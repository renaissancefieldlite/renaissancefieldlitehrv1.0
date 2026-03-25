"""
Capture raw result JSON from either a local Aer simulator or an IBM backend.

The goal of this utility is simple: save backend output without injecting a
target frequency into the saved data. Interpretation happens later.
"""

import argparse
import json
import time
from pathlib import Path

from qiskit import QuantumCircuit

def build_capture_circuit(index: int) -> QuantumCircuit:
    """Create a small deterministic circuit variant for repeated capture."""
    circuit = QuantumCircuit(2)
    circuit.h(0)
    if index % 2 == 0:
        circuit.cx(0, 1)
    else:
        circuit.x(1)
        circuit.cz(0, 1)
    circuit.measure_all()
    return circuit


def grab_error_timestamps(
    backend_name: str = "ibm_nairobi",
    circuits: int = 100,
    shots: int = 1024,
    out_dir: str = "data/raw",
) -> str:
    """Capture backend output and write the raw result JSON to disk."""

    circuits_list = [build_capture_circuit(index) for index in range(circuits)]

    if backend_name == "ibmq_qasm_simulator":
        try:
            from qiskit_aer import AerSimulator
        except ImportError as exc:
            raise SystemExit(
                "Local simulator support requires qiskit-aer. "
                "Install it with `pip install qiskit-aer`."
            ) from exc

        sim = AerSimulator()
        result = sim.run(circuits_list, shots=shots).result()

        ts = int(time.time())
        out_path = Path(out_dir) / f"aer_simulator_{ts}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result.to_dict(), indent=2))
        print(f"[local-sim] experiments={circuits} shots={shots}")
        print(f"✓ saved → {out_path}")
        return str(out_path)

    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
    except ImportError as exc:
        raise SystemExit(
            "IBM backend support requires qiskit-ibm-runtime. "
            "Install it with `pip install qiskit-ibm-runtime`."
        ) from exc

    svc = QiskitRuntimeService()
    backend = svc.backend(backend_name)

    job = backend.run(circuits_list, shots=shots)
    print(f"[{backend_name}] job submitted → {job.job_id()}")
    job.wait_for_final_state()

    ts = int(time.time())
    out_path = Path(out_dir) / f"ibmq_{backend_name}_{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(job.result().to_dict(), indent=2))
    print(f"✓ saved → {out_path}")
    return str(out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend",
        default="ibm_nairobi",
        help="Backend name or ibmq_qasm_simulator for a local Aer run",
    )
    parser.add_argument("--circuits", type=int, default=100)
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--out_dir", default="data/raw")
    args = parser.parse_args()

    grab_error_timestamps(
        backend_name=args.backend,
        circuits=args.circuits,
        shots=args.shots,
        out_dir=args.out_dir,
    )
