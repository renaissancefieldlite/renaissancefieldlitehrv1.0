# Hardware-Derived Simulation

The hardware-derived lane is the bridge between the synthetic detector path and
the real backend timestamp / capture path.

It uses calibration-style inputs such as:

- `T1`
- `T2`
- readout error
- single-qubit gate error
- frequency drift
- anharmonicity
- crosstalk

to build a local model that behaves more like repeated backend execution than a
free synthetic toy signal.

## Current Model

The current model in
[`analysis/hardware_noise_model.py`](../analysis/hardware_noise_model.py)
separates two layers that were previously collapsed together:

1. fast short-window decoherence during a backend-style prepare/evolve/measure cycle
2. slower session drift across repeated batches

That matters because the older model treated the device as if one qubit state
were left alive across a long continuous window. The updated model instead
simulates repeated short shots under a slower session envelope, which is much
closer to what the backend lane is actually doing.

## Current Derived Artifact

Current example output:

- [`data/derived_noise/sample_noise_profile.json`](../data/derived_noise/sample_noise_profile.json)
- `schema_version = rfl.hardware_noise_profile.v2`
- `shots_per_batch = 32`
- `effective_circuit_duration_us = 0.9065`
- `mean_short_window_coherence = 0.9823794452339145`
- `mean_session_stability = 0.976366014174089`
- `mean_coherence_proxy = 0.9553175210847371`
- `drift_span_ghz = 0.001604963857123387`

## Why This Lane Exists

This lane is not raw hardware proof, but it is materially stronger than an
unconstrained synthetic placeholder because it is anchored to measured device
characteristics and shaped to resemble repeated backend execution.

The point is not to claim the model is final. The point is to create a local
bridge that can be compared honestly against the backend lane instead of
pretending the only options are ideal simulation or direct hardware access.

## Entry Point

```bash
python3 analysis/hardware_noise_model.py \
  examples/sample_hardware_calibration.json \
  --output data/derived_noise/sample_noise_profile.json
```
