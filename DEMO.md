# Demonstration Notes

## Two Different Workflows Live Here

This repository has two separate workflows that should not be conflated.

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

- testing the framing
- visualizing the difference between an older HRV-centered story and the current machine-telemetry-centered hypothesis
- showing what the detector will report when the target component is already in the data

What it does **not** prove:

- that a real backend emits an intrinsic 0.67 Hz rhythm
- that the target frequency exists in hardware without being planted
- that simulator success implies physical confirmation

### 2. Raw backend capture

Run locally:

```bash
python3 hrv_ingest/hardware_ingest.py --backend ibmq_qasm_simulator
```

Run against IBM hardware:

```bash
pip install qiskit-ibm-runtime
python3 hrv_ingest/hardware_ingest.py --backend <backend_name>
```

What it does:

- saves raw backend results to `data/raw/`
- preserves the backend output without injecting a target-band sinusoid into the saved JSON
- provides the starting point for real downstream analysis

## Recommended Sequence

### Local baseline

```bash
python3 hrv_ingest/hardware_ingest.py --backend ibmq_qasm_simulator
python3 analysis/summarize_capture.py data/raw/aer_simulator_*.json
```

This confirms that:

- the capture path runs
- the JSON structure is readable
- the local baseline is a simulator artifact, not a hardware finding

### Simulation walkthrough

```bash
python3 validation_demo.py
```

This confirms that:

- the synthetic detector produces the expected target-band peak when one is built into the source data
- the current visualization and reporting stack work

### Hardware step

```bash
pip install qiskit-ibm-runtime
python3 hrv_ingest/hardware_ingest.py --backend <backend_name>
python3 analysis/summarize_capture.py data/raw/ibmq_<backend_name>_*.json
```

This is the earliest stage where the repo moves from concept demonstration toward empirical capture.

## Interpretation Guardrails

- A local Aer result is a software execution artifact.
- A synthetic detector hit is expected if the target band was explicitly present in the synthetic source.
- A hardware claim needs repeated raw captures and separate analysis of non-injected data.
- This repo is strongest when it draws a hard line between concept framing and evidence.

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

## Bottom Line

The repo now has a cleaner split:

- `validation_demo.py` shows how the detector behaves in a synthetic scenario
- `hardware_ingest.py` captures raw backend output
- `analysis/summarize_capture.py` gives a grounded readout of what was actually saved

That is the correct technical reading of the current project.
