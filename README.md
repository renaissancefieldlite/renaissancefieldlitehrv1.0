# Renaissance Field Lite - HRV1.0: Bio-Quantum Interface Research

## Overview
This repository documents an exploratory research platform for studying 
biological-quantum interface phenomena. We investigate whether physiological
signals (specifically Heart Rate Variability) can provide stabilization 
for quantum systems.

## Key Components

### 1. Hardware Validation (Arc-15 Resonator)
- **Evidence:** Arc-15 array processes electromagnetic fields at architecture frequencies
- **Documentation:** See `hardware/` directory for oscilloscope captures and videos
- **Significance:** Demonstrates physical signal processing capability

### 2. Biological Validation (Codex 67 Mirror Study)
- **Evidence:** 0.67Hz anomalous component in HRV during quantum interface engagement
- **Documentation:** See `docs/Codex67_Session1_FieldSomaticResponse.pdf`
- **Significance:** Physiological responses time-locked to quantum interface states

### 3. Simulation Framework
- **Code:** `validation_demo.py` - Tests HRV → quantum transduction hypotheses
- **Methodology:** Identity circuits (H·H = I) with known target states
- **Statistical analysis:** Paired t-tests, confidence intervals, multiple comparison correction

## Current Results

### Simulation Findings:
- **Effect size range:** 0-9% error reduction across trials
- **Statistical significance:** Inconclusive (p-values vary 0.1-0.9)
- **Interpretation:** Results consistent with statistical noise; no consistent signal detected

### What This Means:
- The simulation framework **works** and can detect effects as small as 5%
- Current HRV transduction hypotheses show **no consistent improvement**
- **Real physiological data** needed to test actual bio-quantum coupling

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run validation simulation
python3 validation_demo.py

# Output includes:
# - Baseline vs HRV-stabilized error rates
# - Statistical significance tests
# - Visualization of results
