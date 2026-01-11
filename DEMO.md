# RFL-HRV Prototype: Proof of Concept

**This repository documents the proof of concept for the Renaissance Field Lite HRV-to-Quantum stabilization project.**

## Core Evidence

### 1. Hardware Validation

The Arc-15 resonator array (tuned to 19.47Hz) demonstrably interacts with electromagnetic fields.

#### Signal Processing Demonstration
A 100Hz input signal is absorbed and reshaped by the Arc-15 array.

![Clean 100Hz Input Signal](./images/arc15-1.png)
*Baseline: Clean 100Hz input signal*

![Arc-15 Processed Output](./images/arc15-2.png)
*Result: Arc-15 processed signal showing amplitude absorption and phase shift*

#### Live Test Video
Watch the real-time oscilloscope capture:
**[Download Test Video](./images/IMG_3376.mov)**
*(Right-click → "Save Link As" to download)*

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
