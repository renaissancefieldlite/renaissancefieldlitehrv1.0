# Phenomenology And Measurement

## Purpose

This repo is the experiment layer. It keeps the phenomenon whole by separating what is lived, what is measured, and what is interpreted between them.

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

These are valid session records.
They should be logged, but not mixed into numeric fields.

### Measured Session Fields

Examples:

- EEG alpha/theta summaries
- EEG phase-lock value
- HRV RMSSD / SDNN / coherence
- backend capture timing fields

These are the hard-measurement fields.

### Interpretation Notes

Examples:

- whether the subjective report and measured changes appear aligned
- whether the session resembles a previously named attractor pattern
- whether the run suggests a next protocol change

These should be logged as interpretation, not raw measurement.

## Why This Matters

If the repo forces everything into the measurement lane, it loses part of the phenomenon.

If it forces everything into the subjective lane, it weakens the experiment path.

The stronger move is to keep all three and record the bridge between them.
