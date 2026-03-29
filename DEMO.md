# Demonstration Notes

## Two Different Workflows Live Here

HRV1.0 contains two core workflows that the later experiment stack depends on.
They do different jobs and need to stay distinct.

### 1. Synthetic detector sketch

Run:

```bash
python3 validation_demo.py
```

What it does:

- constructs synthetic signals with a target-band component near 0.67 Hz
- runs Welch-based detection over those synthetic signals
- writes a visualization and a text summary

What it is for:

- working out the detector path
- visualizing the shift from the older HRV-control story to the
  machine-telemetry-first framing
- showing what the detector stack reports when the target component is already
  in the source data

### 2. Raw backend capture

Run locally:

```bash
python3 hrv_ingest/hardware_ingest.py --provider aer --backend ibmq_qasm_simulator
```

Run against IBM hardware:

```bash
pip install qiskit-ibm-runtime
python3 hrv_ingest/hardware_ingest.py --provider ibm --backend <backend_name>
```

What it does:

- saves raw backend results to `data/raw/`
- preserves the backend output without injecting a target-band sinusoid into the saved JSON
- wraps new captures in a shared schema so provider-specific payloads are easier to compare later
- provides the raw capture lane the rest of the stack builds on

Optional Braket local run:

```bash
pip install amazon-braket-sdk
python3 hrv_ingest/hardware_ingest.py --provider braket-local --backend braket_local
```

## Recommended Sequence

### Local baseline

```bash
python3 hrv_ingest/hardware_ingest.py --provider aer --backend ibmq_qasm_simulator
python3 analysis/summarize_capture.py data/raw/aer_simulator_*.json
```

This confirms that:

- the capture path runs
- the JSON structure is readable
- the local baseline is a simulator artifact, not a hardware finding

### Simulation walkthrough

```bash
MPLBACKEND=Agg MPLCONFIGDIR=/tmp/mpl python3 validation_demo.py
```

This confirms that:

- the synthetic detector produces the expected target-band peak when one is built into the source data
- the current visualization and reporting stack work

### Hardware step

```bash
pip install qiskit-ibm-runtime
python3 hrv_ingest/hardware_ingest.py --provider ibm --backend <backend_name>
python3 analysis/summarize_capture.py data/raw/ibmq_<backend_name>_*.json
```

This is the point where the repo moves from detector framing into actual backend
capture.

## How To Read The Workflows

- the detector workflow defines what the search target looks like
- the raw capture workflow saves backend output without planting that target in
  the saved file
- both workflows are part of the foundation layer, but they are doing different
  jobs

## Files Produced

### `validation_demo.py`

Produces:

- `paradigm_shift_demonstration.png`
- `quantum_system_validation_metrics.txt`

Interpret as:

- simulation outputs
- concept support
- detector-behavior reference

### `hardware_ingest.py`

Produces:

- `data/raw/aer_simulator_<timestamp>.json` for local Aer
- `data/raw/ibmq_<backend>_<timestamp>.json` for IBM Runtime captures

Interpret as:

- raw capture artifacts
- candidate inputs for later, non-injected analysis

### `repeated_capture.py`

Produces:

- `data/batches/<provider>_<backend>_<label>_<timestamp>.json`
- optional sidecar scrape report
  `data/batches/<provider>_<backend>_<label>_<timestamp>_job_ids.json`

Interpret as:

- repeated-batch manifests
- the clean handoff into comparison reports
- live job-id tracking while backend runs are still in flight

## Repeated Batch Workflow

Run:

```bash
python3 hrv_ingest/repeated_capture.py \
  --provider ibm \
  --backend ibm_fez \
  --repeats 10 \
  --circuits 1 \
  --shots 32 \
  --label baseline_10 \
  --condition baseline \
  --scrape-job-ids
```

Then compare:

```bash
python3 analysis/compare_capture_batches.py \
  --captures "data/batches/aer_ibmq_qasm_simulator_baseline_*.json" "data/batches/ibm_ibm_fez_baseline_*.json" \
  --output data/derived_noise/experiment_baseline_comparison.json
```

This is the publishable bridge between the Step 2 proxy and the later
experiment repos.

## Bottom Line

HRV1.0 matters because both workflows are foundational:

- `validation_demo.py` defines the detector path
- `hardware_ingest.py` defines the backend capture path
- `analysis/summarize_capture.py` reads back what was actually saved

That is the groundwork the later experiment stack expands from.
