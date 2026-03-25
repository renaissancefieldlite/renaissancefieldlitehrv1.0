# ──────────────────────────────────────────────────────────────
# File: hrv_ingest/hardware_ingest.py
# Purpose: grab real error-syndrome timestamps from an IBM cloud back-end
# Requires: pip install qiskit qiskit-ibm-runtime
# ──────────────────────────────────────────────────────────────

from pathlib import Path
import time, json
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService

# ─────────── helper to build a trivial Clifford sampler ───────────
def random_clifford_circuit(qubits: int = 5, depth: int = 5) -> QuantumCircuit:
    """
    Returns a random Clifford circuit of given depth that ends in a full
    measurement. Good enough to stress readout and gate fidelity.
    """
    from qiskit.circuit.library import Clifford
    qc = QuantumCircuit(qubits, qubits)
    for _ in range(depth):
        qc.append(Clifford.random(qubits), range(qubits))
    qc.measure(range(qubits), range(qubits))
    return qc

# ─────────── main capture routine ───────────
def grab_error_timestamps(
        backend_name: str = "ibm_nairobi",  # change if you want a different HW
        circuits: int   = 100,              # how many jobs in one batch
        shots: int      = 1024,             # shots per job
        out_dir: str    = "data/raw"        # where the JSON lands
) -> str:
    """
    Runs <circuits> random Clifford jobs on the specified IBM back-end and
    dumps the full result JSON (real error counts & timestamps) to disk.
    Returns the path for logging.
    """
    svc  = QiskitRuntimeService()           # assumes token already saved
    bk   = svc.backend(backend_name)        # this is REAL hardware, not a sim
    qcs  = [random_clifford_circuit() for _ in range(circuits)]
    job  = bk.run(qcs, shots=shots)
    print(f"[+] submitted job {job.job_id()} to {backend_name}")

    job.wait_for_final_state()
    res  = job.result()                     # ← live qubit data
    ts   = int(time.time())
    out  = Path(out_dir) / f"ibmq_{backend_name}_{ts}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res.to_dict(), indent=2))
    print(f"[+] saved → {out}")
    return str(out)

# ─────────── CLI hook ───────────
if __name__ == "__main__":
    grab_error_timestamps()
