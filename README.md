# Renaissance Field Lite HRV 1.0

## Overview

This repository is the experimental layer for the RFL 0.67 Hz hypothesis. It currently contains two different kinds of material:

- a **synthetic demonstration** in [`validation_demo.py`](./validation_demo.py) that shows how a detector behaves when a 0.67 Hz component is present by construction
- a **raw capture utility** in [`hrv_ingest/hardware_ingest.py`](./hrv_ingest/hardware_ingest.py) that saves backend or local Aer results as JSON without injecting a target frequency into the saved data

That distinction matters. The simulation is useful for working out the framing and signal-processing path. It is not empirical proof that a quantum backend has an intrinsic 0.67 Hz pulse.

## Current Status

What this repo can do today:

- generate a synthetic 0.67 Hz demo signal and accompanying visualization
- capture raw JSON from a local `AerSimulator`
- capture raw JSON from an IBM backend if `qiskit-ibm-runtime` is available and the active token has access to a real device
- summarize saved captures with a lightweight inspection script

What this repo does **not** do yet:

- prove that real hardware contains an intrinsic 0.67 Hz rhythm
- ingest Arc-15 or other external biosignal hardware directly
- derive a sub-Hz claim from the local ideal simulator alone

## Evidence Boundary

Use the repo with these guardrails:

1. `validation_demo.py` is a **simulation sketch**. It injects a target-band component and then measures how the synthetic detector responds.
2. `hrv_ingest/hardware_ingest.py` is the **empirical entry path**. It saves raw backend output without planting a 0.67 Hz oscillation into the JSON.
3. Local `AerSimulator` output proves the code path runs. It does **not** adjudicate the physical hypothesis.
4. Any claim about an intrinsic backend rhythm should come from repeated raw captures and separate analysis of non-injected data.

## Repository Layout

```text
.
├── README.md
├── DEMO.md
├── paradimeshift.md
├── requirements.txt
├── validation_demo.py
├── hrv_ingest/
│   └── hardware_ingest.py
├── analysis/
│   └── summarize_capture.py
├── data/
│   └── raw/
└── images/
```

## Quick Start

### 1. Create an environment and install core dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Capture a local simulator baseline

```bash
python3 hrv_ingest/hardware_ingest.py --backend ibmq_qasm_simulator
```

This writes a JSON result into `data/raw/`.

### 3. Inspect the saved capture

```bash
python3 analysis/summarize_capture.py data/raw/aer_simulator_*.json
```

The summary script reports:

- backend name
- number of experiments saved
- shot count
- timing fields present in the file
- whether the file is local simulation or hardware-oriented capture

### 4. Run the synthetic detector demo

```bash
python3 validation_demo.py
```

This generates:

- `paradigm_shift_demonstration.png`
- `quantum_system_validation_metrics.txt`

Those artifacts document the **simulation behavior** of the current detector framing. They are not raw hardware evidence.

## IBM Backend Capture

If you want to hit a real IBM backend, install the runtime client in the same environment:

```bash
pip install qiskit-ibm-runtime
```

Then run:

```bash
python3 hrv_ingest/hardware_ingest.py --backend <backend_name>
```

Example:

```bash
python3 hrv_ingest/hardware_ingest.py --backend ibm_fez
```

Notes:

- backend availability depends on the token and plan attached to your IBM account
- the utility saves the raw result JSON as returned by the backend
- empirical interpretation should be done on repeated captures, not a single idealized run

## Concept Layer

The broader working hypothesis in this repo is:

`candidate substrate rhythm -> detection path -> synchronization hypothesis -> measurable backend change`

That hypothesis motivated the earlier language in this project. The codebase is now separated more cleanly:

- concept notes live in [`paradimeshift.md`](./paradimeshift.md)
- synthetic framing lives in [`validation_demo.py`](./validation_demo.py)
- raw capture lives in [`hrv_ingest/hardware_ingest.py`](./hrv_ingest/hardware_ingest.py)

## Related Files

- [`DEMO.md`](./DEMO.md): technical walkthrough of the current demo and capture paths
- [`paradimeshift.md`](./paradimeshift.md): archived concept note describing the working reframe
- [`Codex67_Session1_FieldSomaticResponse.pdf`](./Codex67_Session1_FieldSomaticResponse.pdf): supporting session document kept in-repo as reference material

## Practical Reading Of This Repo

The clean reading is:

- the synthetic demo shows what the detector is looking for
- the capture utility is the first non-injected data path
- the real question is still downstream of repeated backend capture and honest analysis

That is the point of this repository in its current form.
