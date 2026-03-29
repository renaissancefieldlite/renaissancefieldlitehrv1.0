"""
Capture raw result JSON from multiple provider paths without injecting a target
frequency into the saved data.

Supported providers:
- aer: local Qiskit Aer simulator
- ibm: IBM Runtime backends
- braket-local: Amazon Braket local simulator
- external-rig: normalized metadata/session logging for external hardware tests

The output schema is normalized so later analysis can distinguish provider,
backend, capture mode, and raw result payload.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit, transpile

DEFAULT_OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


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


def build_capture_path(out_dir: str | Path, stem: str) -> Path:
    timestamp_ns = time.time_ns()
    return Path(out_dir) / f"{stem}_{timestamp_ns}.json"


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
    out_path = build_capture_path(out_dir, "aer_simulator")
    print(f"[local-aer] experiments={circuits} shots={shots}")
    return write_capture_file(payload, out_path)


def capture_ibm(*, backend_name: str, circuits: int, shots: int, out_dir: str) -> str:
    """Run an IBM Runtime capture and save it using the normalized schema."""
    return capture_ibm_with_config(
        backend_name=backend_name,
        circuits=circuits,
        shots=shots,
        out_dir=out_dir,
        channel=None,
        token=None,
        instance=None,
        url=None,
    )


def load_saved_ibm_account() -> dict[str, str] | None:
    """Load the first saved IBM account from ~/.qiskit/qiskit-ibm.json if present."""
    account_path = Path.home() / ".qiskit" / "qiskit-ibm.json"
    if not account_path.exists():
        return None

    data = json.loads(account_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return None

    for value in data.values():
        if isinstance(value, dict) and value.get("token"):
            return {
                "channel": value.get("channel"),
                "token": value.get("token"),
                "instance": value.get("instance"),
                "url": value.get("url"),
            }
    return None


def resolve_ibm_runtime_config(
    *,
    channel: str | None,
    token: str | None,
    instance: str | None,
    url: str | None,
) -> dict[str, str]:
    """Resolve IBM Runtime configuration from args/env with explicit failure."""
    saved_account = load_saved_ibm_account() or {}
    resolved_channel = channel or os.environ.get("QISKIT_IBM_CHANNEL") or saved_account.get("channel") or "ibm_quantum_platform"
    resolved_token = token or os.environ.get("QISKIT_IBM_TOKEN") or os.environ.get("IBM_QUANTUM_TOKEN") or saved_account.get("token")
    resolved_instance = instance or os.environ.get("QISKIT_IBM_INSTANCE") or saved_account.get("instance")
    resolved_url = url or os.environ.get("QISKIT_IBM_URL") or saved_account.get("url")

    if resolved_channel != "local" and not resolved_token:
        raise SystemExit(
            "IBM runtime capture requires qiskit-ibm-runtime plus an IBM token. "
            "Provide --ibm-token, set QISKIT_IBM_TOKEN / IBM_QUANTUM_TOKEN, or save an account in ~/.qiskit/qiskit-ibm.json."
        )

    config = {"channel": resolved_channel}
    if resolved_token:
        config["token"] = resolved_token
    if resolved_instance:
        config["instance"] = resolved_instance
    if resolved_url:
        config["url"] = resolved_url
    return config


def capture_ibm_with_config(
    *,
    backend_name: str,
    circuits: int,
    shots: int,
    out_dir: str,
    channel: str | None,
    token: str | None,
    instance: str | None,
    url: str | None,
) -> str:
    """Run an IBM Runtime capture using explicit runtime configuration."""
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    except ImportError as exc:
        raise SystemExit(
            "IBM backend support requires qiskit-ibm-runtime. "
            "Install it with `pip install qiskit-ibm-runtime`."
        ) from exc

    circuits_list = [build_qiskit_capture_circuit(index) for index in range(circuits)]
    service_config = resolve_ibm_runtime_config(
        channel=channel,
        token=token,
        instance=instance,
        url=url,
    )
    service = QiskitRuntimeService(**service_config)
    backend = service.backend(backend_name)
    isa_circuits = transpile(circuits_list, backend)
    sampler = SamplerV2(mode=backend)
    job = sampler.run(isa_circuits, shots=shots)
    print(f"[ibm:{backend_name}] job submitted → {job.job_id()}")
    result = job.result()

    experiments: list[dict[str, Any]] = []
    for index, pub_result in enumerate(result):
        meas = pub_result.data.meas
        counts = meas.get_counts()
        total_counts = max(sum(counts.values()), 1)
        experiments.append(
            {
                "experiment_index": index,
                "measurement_counts": counts,
                "measurement_probabilities": {
                    bitstring: value / total_counts for bitstring, value in counts.items()
                },
                "sample_bitstrings": meas.get_bitstrings()[: min(10, shots)],
                "pub_metadata": dict(pub_result.metadata),
            }
        )

    payload = normalize_capture(
        provider="ibm",
        backend_name=backend_name,
        capture_mode="cloud_backend",
        circuits=circuits,
        shots=shots,
        raw_result={
            "result_format": "qiskit_sampler_v2",
            "experiments": experiments,
            "result_metadata": {
                "version": result.metadata.get("version"),
                "execution": repr(result.metadata.get("execution")),
            },
        },
        extra={
            "result_format": "qiskit_sampler_v2",
            "job_id": job.job_id(),
            "runtime_config": {
                "channel": service_config.get("channel"),
                "instance": service_config.get("instance"),
                "url": service_config.get("url"),
            },
        },
    )
    out_path = build_capture_path(out_dir, f"ibmq_{backend_name}")
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
    out_path = build_capture_path(out_dir, "braket_local")
    print(f"[braket-local] experiments={circuits} shots={shots}")
    return write_capture_file(payload, out_path)


def capture_external_rig(*, backend_name: str, session_json: str, out_dir: str) -> str:
    """Save an external hardware session using the normalized schema."""
    session_path = Path(session_json)
    if not session_path.exists():
        raise SystemExit(f"External rig session JSON not found: {session_json}")

    session_payload = json.loads(session_path.read_text(encoding="utf-8"))
    payload = normalize_capture(
        provider="external-rig",
        backend_name=backend_name,
        capture_mode="manual_external_session",
        circuits=0,
        shots=0,
        raw_result={"session_record": session_payload},
        extra={"result_format": "external_rig_session_v1"},
    )
    safe_name = backend_name.replace(" ", "_")
    out_path = build_capture_path(out_dir, safe_name)
    print(f"[external-rig:{backend_name}] session={session_path.name}")
    return write_capture_file(payload, out_path)


def infer_provider(provider: str, backend_name: str) -> str:
    """Infer the provider when the user leaves it on auto."""
    if provider != "auto":
        return provider
    if backend_name in {"ibmq_qasm_simulator", "aer_simulator"}:
        return "aer"
    if backend_name.startswith("braket"):
        return "braket-local"
    if backend_name.startswith("arc15") or "fg200" in backend_name.lower():
        return "external-rig"
    return "ibm"


def grab_error_timestamps(
    *,
    provider: str = "auto",
    backend_name: str = "ibm_nairobi",
    circuits: int = 100,
    shots: int = 1024,
    out_dir: str | Path = DEFAULT_OUT_DIR,
    session_json: str | None = None,
    ibm_channel: str | None = None,
    ibm_token: str | None = None,
    ibm_instance: str | None = None,
    ibm_url: str | None = None,
) -> str:
    """Capture backend output and write the normalized result JSON to disk."""
    resolved_provider = infer_provider(provider, backend_name)

    if resolved_provider == "aer":
        return capture_aer(circuits=circuits, shots=shots, out_dir=out_dir)
    if resolved_provider == "ibm":
        return capture_ibm_with_config(
            backend_name=backend_name,
            circuits=circuits,
            shots=shots,
            out_dir=out_dir,
            channel=ibm_channel,
            token=ibm_token,
            instance=ibm_instance,
            url=ibm_url,
        )
    if resolved_provider == "braket-local":
        return capture_braket_local(circuits=circuits, shots=shots, out_dir=out_dir)
    if resolved_provider == "external-rig":
        if not session_json:
            raise SystemExit(
                "External rig capture requires --session-json pointing to a normalized session record."
            )
        return capture_external_rig(
            backend_name=backend_name,
            session_json=session_json,
            out_dir=out_dir,
        )

    raise SystemExit(f"Unsupported provider: {resolved_provider}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--provider",
        default="auto",
        choices=["auto", "aer", "ibm", "braket-local", "external-rig"],
        help="Capture provider. auto preserves backward compatibility.",
    )
    parser.add_argument(
        "--backend",
        default="ibm_nairobi",
        help="Backend name. Use ibmq_qasm_simulator for local Aer, or an IBM backend like ibm_fez.",
    )
    parser.add_argument("--circuits", type=int, default=100)
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--out-dir", "--out_dir", dest="out_dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument(
        "--ibm-channel",
        help="IBM runtime channel, for example ibm_quantum_platform, ibm_cloud, or local.",
    )
    parser.add_argument("--ibm-token", help="IBM runtime token. Falls back to QISKIT_IBM_TOKEN.")
    parser.add_argument("--ibm-instance", help="IBM runtime instance/CRN if required by the account.")
    parser.add_argument("--ibm-url", help="Optional IBM runtime API URL override.")
    parser.add_argument(
        "--session-json",
        help="Path to a normalized external-hardware session record when provider=external-rig.",
    )
    args = parser.parse_args()

    grab_error_timestamps(
        provider=args.provider,
        backend_name=args.backend,
        circuits=args.circuits,
        shots=args.shots,
        out_dir=args.out_dir,
        session_json=args.session_json,
        ibm_channel=args.ibm_channel,
        ibm_token=args.ibm_token,
        ibm_instance=args.ibm_instance,
        ibm_url=args.ibm_url,
    )
