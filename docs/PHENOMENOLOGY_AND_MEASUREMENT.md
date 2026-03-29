# Phenomenology And Measurement

## Purpose

This repo is the experiment foundation layer. That does not mean the rest of
the phenomenon is ignored.

It means the repo must distinguish between:

- what is lived
- what is measured
- what is inferred from the relationship between the two

## Repo Rule

Inside `renaissancefieldlitehrv1.0`, use three separate buckets:

### Subjective Session Notes

Examples:

- chest-pressure report
- felt pulse report
- sense of phase lock
- emotional or perceptual shift

These are valid session records. They belong in the repo, but not inside the
numeric measurement fields.

### Measured Session Fields

Examples:

- EEG alpha/theta summaries
- EEG phase-lock value
- HRV RMSSD / SDNN / coherence
- backend capture timing fields

These are the measured fields the rest of the stack can compare.

### Interpretation Notes

Examples:

- whether the subjective report and measured changes appear aligned
- whether the session resembles a previously named attractor pattern
- whether the run suggests a next protocol change

These should be logged as interpretation, not as raw measurement.

## Why This Matters

If the repo forces everything into the measurement lane, it loses part of the
session structure.

If it forces everything into the subjective lane, it breaks the experiment path.

The correct move is to keep both and record the bridge between them.
