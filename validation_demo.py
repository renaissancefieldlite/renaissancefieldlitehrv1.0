#!/usr/bin/env python3
# RFL-HRV1.0 Validation Demo - Proof of Concept for Unitary Fund Grant

# 1. SETUP: Show you're using standard tools
import numpy as np
import qiskit
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
print("Qiskit version:", qiskit.__version__)

# 2. DEFINE TEST CIRCUIT: Standard benchmarking
def create_test_circuit(num_qubits=3, depth=10):
    """Create a simple, standard test circuit"""
    from qiskit import QuantumCircuit
    from qiskit.circuit.random import random_circuit
    circuit = random_circuit(num_qubits, depth, measure=True)
    return circuit

# 3. YOUR HRV-STABILIZATION FUNCTION: The core innovation
def apply_hrv_stabilization(circuit, hrv_phase_data):
    """
    This is your secret sauce.
    Takes HRV phase data (from your sensor) and applies gentle rotations.
    """
    stabilized = circuit.copy()
    
    # Example: Map HRV phase to small Z-rotations on each qubit
    for i, qubit in enumerate(circuit.qubits):
        if i < len(hrv_phase_data):
            # Convert HRV phase to rotation angle (small, ±π/16 max)
            angle = hrv_phase_data[i] * (np.pi / 16)
            stabilized.rz(angle, qubit)
    
    return stabilized

# 4. GENERATE MOCK HRV DATA: Show you understand the input
def generate_mock_hrv(n_samples=1000):
    """Generate realistic HRV phase data with 0.67Hz component"""
    t = np.linspace(0, 10, n_samples)
    # Core 0.67Hz rhythm + some noise
    base_signal = np.sin(2 * np.pi * 0.67 * t)
    noise = 0.3 * np.random.randn(n_samples)
    return base_signal + noise

# 5. RUN THE COMPARISON: The key experiment
def compare_error_rates(n_trials=100):
    """Run multiple trials to compare baseline vs stabilized"""
    
    baseline_errors = []
    stabilized_errors = []
    
    for trial in range(n_trials):
        # Create test circuit
        circuit = create_test_circuit(num_qubits=3, depth=5)
        
        # Generate fresh HRV data for this trial
        hrv_data = generate_mock_hrv(n_samples=len(circuit.qubits))
        
        # Create stabilized version
        stabilized_circuit = apply_hrv_stabilization(circuit, hrv_data)
        
        # Simulate both
        simulator = AerSimulator()
        
        # Baseline result
        baseline_result = simulator.run(circuit, shots=1024).result()
        baseline_counts = baseline_result.get_counts()
        
        # Stabilized result
        stabilized_result = simulator.run(stabilized_circuit, shots=1024).result()
        stabilized_counts = stabilized_result.get_counts()
        
        # Calculate error metric (simplified - can use more sophisticated metrics)
        baseline_error = 1 - max(baseline_counts.values()) / 1024 if baseline_counts else 1
        stabilized_error = 1 - max(stabilized_counts.values()) / 1024 if stabilized_counts else 1
        
        baseline_errors.append(baseline_error)
        stabilized_errors.append(stabilized_error)
    
    return np.array(baseline_errors), np.array(stabilized_errors)

# 6. EXECUTE AND DISPLAY RESULTS
print("Running 100 trials of baseline vs HRV-stabilized circuits...")
baseline, stabilized = compare_error_rates(n_trials=100)

# Calculate improvement
improvement = (baseline.mean() - stabilized.mean()) / baseline.mean() * 100

print(f"\n=== RESULTS ===")
print(f"Baseline error rate: {baseline.mean():.3f} ± {baseline.std():.3f}")
print(f"Stabilized error rate: {stabilized.mean():.3f} ± {stabilized.std():.3f}")
print(f"Improvement: {improvement:.1f}% reduction in error rate")

# 7. VISUALIZATION: Critical for understanding
plt.figure(figsize=(10, 4))

plt.subplot(121)
plt.plot(baseline[:20], 'r-', label='Baseline', alpha=0.7)
plt.plot(stabilized[:20], 'b-', label='HRV-Stabilized', alpha=0.7)
plt.xlabel('Trial Number')
plt.ylabel('Error Rate')
plt.title('Trial-by-Trial Comparison')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(122)
labels = ['Baseline', 'HRV-Stabilized']
means = [baseline.mean(), stabilized.mean()]
stds = [baseline.std(), stabilized.std()]
plt.bar(labels, means, yerr=stds, capsize=10, 
        color=['red', 'blue'], alpha=0.7)
plt.ylabel('Mean Error Rate')
plt.title(f'Mean Improvement: {improvement:.1f}%')
plt.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('validation_results.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\nChart saved as 'validation_results.png'")
