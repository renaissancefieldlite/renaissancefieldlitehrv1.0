"""
Capture raw result JSON from multiple provider paths without injecting a target
frequency into the saved data.

Supported providers:
- aer: local Qiskit Aer simulator
- ibm: IBM Runtime backends
- braket-local: Amazon Braket local simulator

The output schema is normalized so later analysis can distinguish provider,
backend, capture mode, and raw result payload.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit


def utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def build_qiskit_capture_circuit(index: int) -> QuantumCircuit:
    """Create a small deterministic Qiskit circuit variant for repeated capture."""
    circuit = QuantumCircuit(2)
    circuit.h(0)
    if index % 2 == 0:
        circuit.cx(0, 1)
    else:
        circuit.x(1)
        circuit.cz(0, 1)
    circuit.measure_all()
    return circuit


def build_braket_capture_circuit(index: int):
    """Create a small deterministic Braket circuit variant for repeated capture."""
    from braket.circuits import Circuit

    circuit = Circuit().h(0)
    if index % 2 == 0:
        circuit = circuit.cnot(0, 1)
    else:
        circuit = circuit.x(1).cz(0, 1)
    return circuit


def normalize_capture(
    *,
    provider: str,
    backend_name: str,
    capture_mode: str,
    circuits: int,
    shots: int,
    raw_result: dict[str, Any],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Wrap provider-specific output in a shared capture schema."""
    payload: dict[str, Any] = {
        "schema_version": "rfl.capture.v1",
        "provider": provider,
        "backend_name": backend_name,
        "capture_mode": capture_mode,
        "created_at_utc": utc_now_iso(),
        "circuits_requested": circuits,
        "shots": shots,
        "raw_result": raw_result,
    }
    if extra:
        payload.update(extra)
    return payload


def write_capture_file(payload: dict[str, Any], out_path: Path) -> str:
    """Persist a capture payload to disk."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2))
    print(f"✓ saved → {out_path}")
    return str(out_path)


def capture_aer(*, circuits: int, shots: int, out_dir: str) -> str:
    """Run a local Aer capture and save it using the normalized schema."""
    try:
        from qiskit_aer import AerSimulator
    except ImportError as exc:
        raise SystemExit(
            "Local simulator support requires qiskit-aer. "
            "Install it with `pip install qiskit-aer`."
        ) from exc

    simulator = AerSimulator()
    circuits_list = [build_qiskit_capture_circuit(index) for index in range(circuits)]
    result = simulator.run(circuits_list, shots=shots).result()

    payload = normalize_capture(
        provider="aer",
        backend_name="aer_simulator",
        capture_mode="local_simulator",
        circuits=circuits,
        shots=shots,
        raw_result=result.to_dict(),
        extra={"result_format": "qiskit_result_dict"},
    )
    timestamp = int(time.time())
    out_path = Path(out_dir) / f"aer_simulator_{timestamp}.json"
    print(f"[local-aer] experiments={circuits} shots={shots}")
    return write_capture_file(payload, out_path)


def capture_ibm(*, backend_name: str, circuits: int, shots: int, out_dir: str) -> str:
    """Run an IBM Runtime capture and save it using the normalized schema."""
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
    except ImportError as exc:
        raise SystemExit(
            "IBM backend support requires qiskit-ibm-runtime. "
            "Install it with `pip install qiskit-ibm-runtime`."
        ) from exc

    circuits_list = [build_qiskit_capture_circuit(index) for index in range(circuits)]
    service = QiskitRuntimeService()
    backend = service.backend(backend_name)
    job = backend.run(circuits_list, shots=shots)
    print(f"[ibm:{backend_name}] job submitted → {job.job_id()}")
    job.wait_for_final_state()

    payload = normalize_capture(
        provider="ibm",
        backend_name=backend_name,
        capture_mode="cloud_backend",
        circuits=circuits,
        shots=shots,
        raw_result=job.result().to_dict(),
        extra={
            "result_format": "qiskit_result_dict",
            "job_id": job.job_id(),
        },
    )
    timestamp = int(time.time())
    out_path = Path(out_dir) / f"ibmq_{backend_name}_{timestamp}.json"
    return write_capture_file(payload, out_path)


def capture_braket_local(*, circuits: int, shots: int, out_dir: str) -> str:
    """Run a Braket local simulator capture and save it using the normalized schema."""
    try:
        from braket.devices import LocalSimulator
    except ImportError as exc:
        raise SystemExit(
            "Braket local support requires the Amazon Braket SDK. "
            "Install it with `pip install amazon-braket-sdk`."
        ) from exc

    simulator = LocalSimulator()
    experiments: list[dict[str, Any]] = []

    for index in range(circuits):
        circuit = build_braket_capture_circuit(index)
        task = simulator.run(circuit, shots=shots)
        result = task.result()
        experiments.append(
            {
                "experiment_index": index,
                "measurement_counts": dict(result.measurement_counts),
                "measurement_probabilities": dict(result.measurement_probabilities),
                "measured_qubits": list(result.measured_qubits),
            }
        )

    payload = normalize_capture(
        provider="braket-local",
        backend_name="braket_local_simulator",
        capture_mode="local_simulator",
        circuits=circuits,
        shots=shots,
        raw_result={"experiments": experiments},
        extra={"result_format": "braket_local_result_dict"},
    )
    timestamp = int(time.time())
    out_path = Path(out_dir) / f"braket_local_{timestamp}.json"
    print(f"[braket-local] experiments={circuits} shots={shots}")
    return write_capture_file(payload, out_path)


def infer_provider(provider: str, backend_name: str) -> str:
    """Infer the provider when the user leaves it on auto."""
    if provider != "auto":
        return provider
    if backend_name in {"ibmq_qasm_simulator", "aer_simulator"}:
        return "aer"
    if backend_name.startswith("braket"):
        return "braket-local"
    return "ibm"


def grab_error_timestamps(
    *,
    provider: str = "auto",
    backend_name: str = "ibm_nairobi",
    circuits: int = 100,
    shots: int = 1024,
    out_dir: str = "data/raw",
) -> str:
    """Capture backend output and write the normalized result JSON to disk."""
    resolved_provider = infer_provider(provider, backend_name)

    if resolved_provider == "aer":
        return capture_aer(circuits=circuits, shots=shots, out_dir=out_dir)
    if resolved_provider == "ibm":
        return capture_ibm(
            backend_name=backend_name,
            circuits=circuits,
            shots=shots,
            out_dir=out_dir,
        )
    if resolved_provider == "braket-local":
        return capture_braket_local(circuits=circuits, shots=shots, out_dir=out_dir)

    raise SystemExit(f"Unsupported provider: {resolved_provider}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--provider",
        default="auto",
        choices=["auto", "aer", "ibm", "braket-local"],
        help="Capture provider. auto preserves backward compatibility.",
    )
    parser.add_argument(
        "--backend",
        default="ibm_nairobi",
        help="Backend name. Use ibmq_qasm_simulator for local Aer, or an IBM backend like ibm_fez.",
    )
    parser.add_argument("--circuits", type=int, default=100)
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--out_dir", default="data/raw")
    args = parser.parse_args()

    grab_error_timestamps(
        provider=args.provider,
        backend_name=args.backend,
        circuits=args.circuits,
        shots=args.shots,
        out_dir=args.out_dir,
    )
