# EEG + HRV Protocol

## Purpose

This protocol adds EEG as a measured biosignal lane alongside HRV inside the HRV experiment repo.

The goal is not to collapse everything into HRV. The goal is to let the repo handle a combined session where:

- EEG captures phase-lock or coherence changes
- HRV captures autonomic rhythm/coherence changes
- external front-end hardware such as Arc15 can be logged as a separate rig lane
- subjective field notes remain logged, but separate from measured channels

## Why EEG Fits

EEG is a physical measurement path.

That matters because:

- alpha/theta shifts are not just symbolic language
- phase-lock and coherence metrics are measurable
- the repo can store them as session artifacts instead of only discussing them in prose

## Minimal Hardware

- 1 EEG headset with raw export if possible
- 1 HRV source
  - chest strap, ECG capture, or existing HRV path
- 1 machine running the capture scripts
- synchronized timestamps across channels
- optional external-rig lane:
  - Arc15 / FG200.67 or similar front-end hardware
  - oscilloscope or waveform export path if available

## Minimum Session Structure

### Phase 1: Baseline

- 2 minutes eyes closed or fixed-rest state
- no external entrainment pulse
- collect EEG + HRV simultaneously

### Phase 2: Entrainment

- introduce the session condition
- examples:
  - audio pulse
  - visual flicker
  - experimental 0.67 Hz timing cue
- collect EEG + HRV continuously

### Phase 3: Post Window

- 2 to 5 minutes recovery window
- continue collecting EEG + HRV
- store subjective notes separately

## Suggested Fields To Save

### EEG

- session id
- sample rate
- channels recorded
- alpha power summary
- theta power summary
- phase-lock metric if available
- coherence metric if available

### HRV

- session id
- source type
- RR count or beat count
- RMSSD
- SDNN
- coherence score if used
- respiration note if available

### Shared Session Fields

- condition label
- baseline duration
- entrainment duration
- post duration
- timestamp source
- operator notes
- external rig id if used
- external rig drive frequencies if used

## Interpretation Guardrails

- EEG changes are physical measurements.
- HRV changes are physical measurements.
- subjective reports can be important, but they should be stored in a separate field from the measured metrics.
- one combined session does not prove the entire theory.
- repeated sessions with consistent logging are the path to stronger claims.
- if Arc15 or another front-end rig is used, keep its hardware/session fields
  separate from EEG and HRV numeric summaries unless direct synchronization is
  demonstrated.

## Recommended Repo Position

Inside this repo family:

- `Source-code-layer` names deep primitives
- `Codex-67-white-paper-` carries the document framing
- `Codex-67-white-paper-code-layers` carries the ontology and architecture bridge
- `renaissancefieldlitehrv1.0` is the right home for EEG+HRV session capture and summary
