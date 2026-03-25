"""
hardware_ingest.py
────────────────────────────────────────────────────────
Fetch timestamped error data from an IBM Quantum backend
OR (if you pass --backend ibmq_qasm_simulator) fall back
to a local Aer simulator so the rest of the pipeline
can run without cloud access.
────────────────────────────────────────────────────────
Usage examples
──────────────
# local simulator (no IBM token needed)
python hrv_ingest/hardware_ingest.py --backend ibmq_qasm_simulator

# real cloud device once your token has hardware access
python hrv_ingest/hardware_ingest.py --backend ibmq_oslo
"""

import argparse, json, time
from pathlib import Path
from qiskit import QuantumCircuit

# ────────────────────────────────────────────────────────────
# grab_error_timestamps
# ────────────────────────────────────────────────────────────
def grab_error_timestamps(
    backend_name: str = "ibm_nairobi",
    circuits: int = 100,
    shots: int = 1024,
    out_dir: str = "data/raw",
) -> str:
    """
    Run <circuits> shallow Clifford jobs on the specified backend
    and dump the full Result JSON to <out_dir>. Works with either
    a cloud device *or* a local Aer simulator.
    Returns the path to the saved file.
    """

    # ----- LOCAL SIMULATOR SHORT-CIRCUIT --------------------
    if backend_name == "ibmq_qasm_simulator":
        from qiskit_aer import AerSimulator

        sim = AerSimulator()
        qc = QuantumCircuit(2)
        qc.measure_all()
        result = sim.run(qc, shots=shots).result()

        ts = int(time.time())
        out_path = Path(out_dir) / f"aer_simulator_{ts}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result.to_dict(), indent=2))
        print(f"✓ saved → {out_path}")
        return str(out_path)
    # ----- END LOCAL SIMULATOR SHORT-CIRCUIT ---------------

    # Cloud back-end path (IBM Runtime)
    from qiskit_ibm_runtime import QiskitRuntimeService

    svc = QiskitRuntimeService()
    backend = svc.backend(backend_name)

    # simple Clifford sampler
    circuits_list = []
    for _ in range(circuits):
        c = QuantumCircuit(5)
        c.h(0)
        c.cx(0, 1)
        c.measure_all()
        circuits_list.append(c)

    job = backend.run(circuits_list, shots=shots)
    print(f"[{backend_name}] job submitted → {job.job_id()}")
    job.wait_for_final_state()

    ts = int(time.time())
    out_path = Path(out_dir) / f"ibmq_{backend_name}_{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(job.result().to_dict(), indent=2))
    print(f"✓ saved → {out_path}")
    return str(out_path)


# ────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="ibm_nairobi",
                        help="Backend name or ibmq_qasm_simulator for local run")
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
