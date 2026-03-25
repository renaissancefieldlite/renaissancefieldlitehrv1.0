# Paradigm Shift Note

This file preserves the working reframe that motivated the repository. Treat it as a concept note, not as standalone validation.

## Earlier Framing

```text
Human HRV -> contains 0.67 Hz -> controls quantum computers
```

## Current Working Hypothesis

```text
Candidate substrate rhythm -> machine telemetry shows structure near 0.67 Hz -> operator detects/syncs to that rhythm -> backend behavior may change
```

## What Changed

- the project focus moved away from "human HRV controls quantum hardware"
- the candidate signal under test became a machine-side rhythm hypothesis
- the repo now distinguishes between synthetic illustration and raw capture

## What The Repo Actually Supports

- `validation_demo.py`:
  synthetic illustration of detector behavior when the target band is present
- `hrv_ingest/hardware_ingest.py`:
  raw capture utility for local Aer or IBM Runtime backends
- `analysis/summarize_capture.py`:
  quick inspection of saved capture files

## What Still Needs To Happen

- repeated non-injected backend capture
- analysis over raw results
- explicit separation between simulator artifacts and hardware evidence

## Plain Reading

The 0.67 Hz idea remains the working frequency under test in this repo.

The simulation path helps define the detector.

The capture path is where empirical work starts.
