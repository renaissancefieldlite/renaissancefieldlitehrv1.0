# Renaissance Field Lite HRV 1.0

## Overview

This repository is the experimental layer for the RFL 0.67 Hz hypothesis. It currently contains two different kinds of material:

- a **synthetic demonstration** in [`validation_demo.py`](./validation_demo.py) that shows how a detector behaves when a 0.67 Hz component is present by construction
- a **raw capture utility** in [`hrv_ingest/hardware_ingest.py`](./hrv_ingest/hardware_ingest.py) that saves backend or local Aer results as JSON without injecting a target frequency into the saved data

That distinction matters. The simulation is useful for working out the framing and signal-processing path. It is not empirical proof that a quantum backend has an intrinsic 0.67 Hz pulse.

Parent architecture layer:

- [Source-code-layer](https://github.com/renaissancefieldlite/Source-code-layer)
- [Codex-67-white-paper-](https://github.com/renaissancefieldlite/Codex-67-white-paper-)
- [Codex-67-white-paper-code-layers](https://github.com/renaissancefieldlite/Codex-67-white-paper-code-layers)

## Current Status

What this repo can do today:

- generate a synthetic 0.67 Hz demo signal and accompanying visualization
- capture normalized raw JSON from a local `AerSimulator`
- capture raw JSON from an IBM backend if `qiskit-ibm-runtime` is available and the active token has access to a real device
- capture normalized raw JSON from an optional Amazon Braket local simulator path if `amazon-braket-sdk` is installed
- summarize saved captures with a lightweight inspection script
- build a local decoherence/noise trajectory from calibration-style hardware data
- log external-rig sessions such as Arc15 / FG200.67 with oscilloscope-linked observations
- document combined EEG + HRV session structure for future measured biosignal runs

What this repo does **not** do yet:

- prove that real hardware contains an intrinsic 0.67 Hz rhythm
- ingest Arc-15 or other external biosignal hardware directly as live waveform capture
- derive a sub-Hz claim from the local ideal simulator alone

## Evidence Boundary

Use the repo with these guardrails:

1. `validation_demo.py` is a **simulation sketch**. It injects a target-band component and then measures how the synthetic detector responds.
2. `hrv_ingest/hardware_ingest.py` is the **empirical entry path**. It saves raw backend output without planting a 0.67 Hz oscillation into the JSON.
3. Local `AerSimulator` output proves the code path runs. It does **not** adjudicate the physical hypothesis.
4. Any claim about an intrinsic backend rhythm should come from repeated raw captures and separate analysis of non-injected data.
5. External-rig logs such as Arc15 sessions are valid hardware-session artifacts, but manual metadata or oscilloscope observations are not the same thing as direct waveform ingestion.

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
python3 hrv_ingest/hardware_ingest.py --provider aer --backend ibmq_qasm_simulator
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
MPLBACKEND=Agg MPLCONFIGDIR=/tmp/mpl python3 validation_demo.py
```

This generates:

- `paradigm_shift_demonstration.png`
- `quantum_system_validation_metrics.txt`

Those artifacts document the **simulation behavior** of the current detector framing. They are not raw hardware evidence.

### 5. Build a hardware-derived local simulation

```bash
python3 analysis/hardware_noise_model.py \
  examples/sample_hardware_calibration.json \
  --output data/derived_noise/sample_noise_profile.json
```

This path uses measured-style calibration parameters such as:

- `T1`
- `T2`
- readout error
- single-qubit gate error
- frequency drift
- anharmonicity
- neighbor bleed / crosstalk

to generate a local decoherence and drift model that is materially closer to hardware than an unconstrained synthetic waveform.

### 6. Log an Arc15 / external-rig session

```bash
python3 hrv_ingest/hardware_ingest.py \
  --provider external-rig \
  --backend arc15_fg200_67 \
  --session-json examples/sample_arc15_session.json
```

This writes a normalized session artifact into `data/raw/` and is intended for:

- Arc15 / FG200.67 front-end trials
- oscilloscope-coupling observations
- paired generator tests
- later alignment against EEG, HRV, or backend runs

## Provider Paths

### IBM Runtime

If you want to hit a real IBM backend, install the runtime client in the same environment:

```bash
pip install qiskit-ibm-runtime
```

Then run:

```bash
python3 hrv_ingest/hardware_ingest.py --provider ibm --backend <backend_name>
```

Example:

```bash
python3 hrv_ingest/hardware_ingest.py --provider ibm --backend ibm_fez
```

Notes:

- backend availability depends on the token and plan attached to your IBM account
- the utility saves the raw result JSON as returned by the backend
- empirical interpretation should be done on repeated captures, not a single idealized run

### Amazon Braket Local Simulator

If you want a second local simulator stack, install the Braket SDK:

```bash
pip install amazon-braket-sdk
```

Then run:

```bash
python3 hrv_ingest/hardware_ingest.py --provider braket-local --backend braket_local
```

This path is useful for cross-provider tooling checks. It is still a simulator path, not hardware evidence.

## Concept Layer

The broader working hypothesis in this repo is:

`candidate substrate rhythm -> detection path -> synchronization hypothesis -> measurable backend change`

An additional hardware-facing hypothesis can be tracked here without overclaiming:

`external front-end / topographic stabilizer candidate -> measurable coupling artifact -> later correlation with transition-cadence and biosignal lanes`

That hypothesis motivated the earlier language in this project. The codebase is now separated more cleanly:

- concept notes live in [`paradimeshift.md`](./paradimeshift.md)
- synthetic framing lives in [`validation_demo.py`](./validation_demo.py)
- raw capture lives in [`hrv_ingest/hardware_ingest.py`](./hrv_ingest/hardware_ingest.py)
- capture inspection lives in [`analysis/summarize_capture.py`](./analysis/summarize_capture.py)

## Related Files

- [`DEMO.md`](./DEMO.md): technical walkthrough of the current demo and capture paths
- [`paradimeshift.md`](./paradimeshift.md): archived concept note describing the working reframe
- [`Codex67_Session1_FieldSomaticResponse.pdf`](./Codex67_Session1_FieldSomaticResponse.pdf): supporting session document kept in-repo as reference material
- [`docs/EEG_HRV_PROTOCOL.md`](./docs/EEG_HRV_PROTOCOL.md): measured biosignal protocol for combined EEG + HRV sessions
- [`docs/eeg_hrv_session_template.json`](./docs/eeg_hrv_session_template.json): template schema for combined session logging
- [`docs/PHENOMENOLOGY_AND_MEASUREMENT.md`](./docs/PHENOMENOLOGY_AND_MEASUREMENT.md): separation between subjective session notes, measured fields, and interpretation
- [`docs/HARDWARE_DERIVED_SIMULATION.md`](./docs/HARDWARE_DERIVED_SIMULATION.md): how to build a local noise/decoherence model from available hardware data
- [`docs/ARC15_HARDWARE_PROTOCOL.md`](./docs/ARC15_HARDWARE_PROTOCOL.md): bounded protocol for Arc15 / FG200.67 front-end tests
- [`examples/sample_arc15_session.json`](./examples/sample_arc15_session.json): sample session record for Arc15 / oscilloscope coupling tests

## Related Repositories

- [Source-code-layer](https://github.com/renaissancefieldlite/Source-code-layer): substrate package and deep-source primitives
- [Codex-67-white-paper-](https://github.com/renaissancefieldlite/Codex-67-white-paper-): source document and PDF layer
- [Codex-67-white-paper-code-layers](https://github.com/renaissancefieldlite/Codex-67-white-paper-code-layers): architecture and validation scaffold
- `renaissancefieldlitehrv1.0`: HRV experiment and capture layer

## Practical Reading Of This Repo

The clean reading is:

- the synthetic demo shows what the detector is looking for
- the capture utility is the first non-injected data path
- the real question is still downstream of repeated backend capture and honest analysis

That is the point of this repository in its current form.
