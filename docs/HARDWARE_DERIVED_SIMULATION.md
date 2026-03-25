# Hardware-Derived Simulation

If direct IBM Runtime access is unavailable or unreliable, the next best layer is:

1. take calibration-style or telemetry-style data from an available system
2. extract T1, T2, readout error, gate error, frequency drift, anharmonicity, and crosstalk
3. build a local decoherence/noise trajectory from those measured parameters
4. compare later observed captures against that local model

This is still a model layer, not raw hardware proof. But it is materially stronger than an unconstrained synthetic toy signal because the simulator is anchored to measured device characteristics.

The entry point is:

```bash
python3 analysis/hardware_noise_model.py examples/sample_hardware_calibration.json --output data/derived_noise/sample_noise_profile.json
```
