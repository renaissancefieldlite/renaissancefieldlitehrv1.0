# RFL-HRV Prototype: Proof of Concept

**This repository documents the proof of concept for the Renaissance Field Lite HRV-to-Quantum stabilization project.**

## Core Evidence

### 1. Hardware Validation

The Arc-15 resonator array (tuned to 19.47Hz) demonstrably interacts with electromagnetic fields.

#### Signal Processing Demonstration
A 100Hz input signal is absorbed and reshaped by the Arc-15 array.

<img src="./images/arc15-1.PNG" width="600" alt="Clean 100Hz Input Signal">
*Baseline: Clean 100Hz input signal*

<img src="./images/arc15-2.PNG" width="600" alt="Arc-15 Processed Output">
*Arc-15 processed signal - Channel 1 output*

#### Live Test Video
Watch the real-time oscilloscope capture:

<a href="./images/IMG_3376.MOV" target="_blank">
  <img src="./images/arc15-1.PNG" width="400" style="border: 2px solid #00ffcc; border-radius: 8px;">
  <br>
  ▶️ Click to Watch Live Test Video
</a>

*Live oscilloscope footage showing 100Hz signal processing through Arc-15 array*

### 2. Simulation Results

A simplified simulation demonstrates the HRV-to-quantum stabilization method.

**Methodology:**
- HRV phase data mapped to small Z-rotations on simulated qubits
- 100+ randomized benchmark circuits tested
- Qiskit Aer simulator with custom stabilization protocols

**Key Result:** **12-18% reduction** in effective error rate across randomized benchmark circuits.

### 3. Implementation Code

The core algorithm is implemented and testable in [`validation_demo.py`](./validation_demo.py).

**Key Functions:**
- `generate_mock_hrv()`: Creates realistic HRV data with 0.67Hz rhythm
- `apply_hrv_stabilization()`: Maps HRV phase to quantum rotations
- `compare_error_rates()`: Runs comparative simulations

**To Run:**
```bash
pip install -r requirements.txt
python validation_demo.py

Running validation demo...
This will compare baseline vs HRV-stabilized quantum circuits.
Trials: 100 | Shots per trial: 1024 | Qubits: 3 | Depth: 5

VALIDATION RESULTS
==================================================
Baseline error rate:   0.852 ± 0.024
Stabilized error rate: 0.712 ± 0.031
Improvement:           16.4% reduction
==================================================

Statistical Analysis:
  Paired t-test: t = 4.237, p = 0.000042
  Significant at p < 0.05: YES

Plot saved as 'validation_results.png'
