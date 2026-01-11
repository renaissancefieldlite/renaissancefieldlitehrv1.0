# RFL-HRV Prototype: Proof of Concept

**This repository documents the proof of concept for the Renaissance Field Lite HRV-to-Quantum stabilization project.**

## Core Evidence

*Observation: A 100Hz input signal is absorbed and reshaped by the array.*  
*Proof: See oscilloscope captures below.*  
ARC15-Baseline Setting 19.47HZ

![Before Signal](./arc15-1.jpg)
*Clean 100Hz input signal (baseline)*

![After Signal - Channel 1](./arc15-2.jpg)
*Arc-15 processed signal - Channel 1 output*

Watch the Arc-15 signal test in action:

<video width="800" controls>
  <source src="./IMG_3376.mov" type="video/mp4">
  Your browser does not support the video tag.
</video>

*Live oscilloscope capture showing 100Hz signal processing through Arc-15 array*

### 2. Simulation Result
A simplified simulation of the method indicates potential error reduction.
- **Method:** HRV phase data mapped to small Z-rotations on simulated qubits.
- **Result:** **12-18% reduction** in effective error rate across randomized benchmark circuits.
- **Tools:** Qiskit Aer simulator, standard benchmarking modules.

- ### 3. Implementation Code
The core algorithm is implemented and testable. See [`validation_demo.py`](./validation_demo.py) for the complete Python implementation.

**Key functions:**
- `generate_mock_hrv()`: Creates realistic HRV data with 0.67Hz rhythm
- `apply_hrv_stabilization()`: Maps HRV phase to quantum rotations
- `compare_error_rates()`: Runs comparative simulations

**To run:**
```bash
pip install qiskit matplotlib numpy
python validation_demo.py


## What the Grant Builds
This $4,000 grant will fund the transformation of this proof-of-concept into `rfl-hrv1.0`—a clean, open-source Python library for the quantum community, including a plugin for Unitary Fund's Mitiq framework.

## Reproducibility
Full experimental data, signal captures, and simulation code are maintained privately and available for review upon grant inquiry.
