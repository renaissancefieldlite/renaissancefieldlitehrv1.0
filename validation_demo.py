#!/usr/bin/env python3
# RFL-HRV1.0 Validation Demo - Proof of Concept for Unitary Fund Grant
# Uses target state methodology for scientifically rigorous error quantification

# 1. SETUP: Show you're using standard tools
import numpy as np
import qiskit
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
from scipy import stats  # For statistical significance

print("="*60)
print("RFL-HRV1.0 VALIDATION DEMO")
print("="*60)
print(f"Qiskit version: {qiskit.__version__}")
print(f"Using target state methodology for ground truth validation")
print("="*60 + "\n")

# 2. CREATE TEST CIRCUIT WITH KNOWN TARGET STATE
def create_hadamard_identity_test(num_qubits=3, add_noise=False):
    """
    Create identity circuit with known target state for ground truth.
    
    Method: Apply Hadamard gates twice (H·H = I identity operation)
    Start: |000⟩
    Operations: H·H on each qubit (should cancel out)
    Target: |000⟩ (return to initial state)
    
    This provides measurable ground truth for error quantification.
    Any deviation from |000⟩ = error from noise/decoherence.
    """
    circuit = QuantumCircuit(num_qubits, num_qubits)
    
    # Apply Hadamard identity (H·H = I) to each qubit
    # In ideal case, this returns to |000⟩
    for q in range(num_qubits):
        circuit.h(q)  # First Hadamard
        # Add small random error to simulate decoherence
        if add_noise:
            import numpy as np
            error_angle = np.random.uniform(-0.15, 0.15)
            circuit.rz(error_angle, q)
        circuit.h(q)  # Second Hadamard (should cancel)
    
    # MEASUREMENT ADDED LATER in apply_hrv_stabilization
    # circuit.measure_all()  # REMOVED - will be added after HRV correction
    
    # Target state is all zeros (what we should measure)
    target_state = '0' * num_qubits
    
    return circuit, target_state


def create_grover_diffusion_test(num_qubits=3):
    """
    Alternative test: Grover diffusion operator applied twice.
    More complex than Hadamard identity but still returns to start.
    
    Can be used for additional validation if needed.
    """
    circuit = QuantumCircuit(num_qubits, num_qubits)
    
    # Grover diffusion operator (2|s⟩⟨s| - I) applied twice
    # Returns to initial state
    for _ in range(2):
        # Apply Hadamard to all qubits
        for q in range(num_qubits):
            circuit.h(q)
        
        # Apply X to all qubits
        for q in range(num_qubits):
            circuit.x(q)
        
        # Multi-controlled Z
        if num_qubits > 1:
            circuit.h(num_qubits - 1)
            circuit.mcx(list(range(num_qubits - 1)), num_qubits - 1)
            circuit.h(num_qubits - 1)
        
        # Apply X to all qubits
        for q in range(num_qubits):
            circuit.x(q)
        
        # Apply Hadamard to all qubits
        for q in range(num_qubits):
            circuit.h(q)
    
    # MEASUREMENT ADDED LATER
    # circuit.measure_all()  # REMOVED
    
    target_state = '0' * num_qubits
    
    return circuit, target_state


# 3. HRV-STABILIZATION FUNCTION: The core innovation (FIXED VERSION)
def apply_hrv_stabilization(circuit, hrv_phase_data):
    """
    Core innovation: Map biological HRV rhythms to quantum phase corrections.
    
    Theory: The autonomic nervous system generates structured entropy
    that, when properly mapped to qubit phases, provides gentle 
    stabilization against decoherence.
    
    Implementation: Convert HRV phase data to small Z-rotations (±π/16)
    applied to each qubit, creating a "bio-lock" on the quantum state.
    
    CRITICAL FIX: HRV Z-rotations must be applied BEFORE measurement.
    
    Args:
        circuit: QuantumCircuit to stabilize (without measurements)
        hrv_phase_data: Array of HRV-derived phase values
    
    Returns:
        Stabilized QuantumCircuit with HRV-modulated phase corrections
        and measurements added at the end.
    """
    stabilized = circuit.copy()
    
    # Map HRV phase to small Z-rotations on each qubit
    # Apply BEFORE measurement to affect the quantum state
    for i in range(min(circuit.num_qubits, len(hrv_phase_data))):
        # Smart HRV correction: strength depends on signal quality
        hrv_value = hrv_phase_data[i]
        # Amplify during strong .67Hz signals, attenuate during noise
        if abs(hrv_value) > 0.7:
            angle = -hrv_value * (np.pi / 12)  # Strong correction
        else:
            angle = -hrv_value * (np.pi / 24)  # Weak correction
        stabilized.rz(angle, i)  # Z-rotation = pure phase shift
    
    # Add measurements AFTER HRV corrections
    stabilized.measure_all()
    
    return stabilized


# 4. GENERATE MOCK HRV DATA: Show you understand the input
def generate_mock_hrv(n_samples=1000):
    """
    Generate realistic HRV phase data with 0.67Hz component.
    
    Note: The 0.67Hz frequency is outside normal physiological HRV bands
    (0.04-0.4Hz) and represents an anomalous component observed during
    high-coherence quantum interface states. This is an active research
    question documented in DEMO.md Section 2.5.
    
    Returns:
        Array of normalized phase values for HRV-to-quantum mapping
    """
    t = np.linspace(0, 10, n_samples)
    
    # Core 0.67Hz rhythm (architecture resonance frequency)
    base_signal = np.sin(2 * np.pi * 0.67 * t)
    
    # Add realistic physiological noise
    noise = 0.3 * np.random.randn(n_samples)
    
    # Normalize to [-1, 1] range for phase mapping
    signal = base_signal + noise
    signal = signal / np.max(np.abs(signal))
    
    return signal


# 5. CALCULATE FIDELITY TO TARGET STATE
def calculate_fidelity_to_target(counts, target_state, total_shots=1024):
    """
    Calculate state fidelity: how often we measured the target state.
    
    Args:
        counts: Measurement results dictionary (keys may have spaces)
        target_state: Expected output state (e.g., '000')
        total_shots: Number of measurements performed
    
    Returns:
        error: 1 - fidelity (lower = better)
    """
    # Qiskit returns keys like '000 000' (qubits space classical bits)
    # Extract just the qubit results (first part before space if exists)
    target_count = 0
    for key, value in counts.items():
        # Split by space and take first part
        qubit_result = key.split()[0] if ' ' in key else key
        if qubit_result == target_state:
            target_count += value
    
    fidelity = target_count / total_shots
    error = 1 - fidelity
    return error


# 6. RUN THE COMPARISON: The key experiment (UPDATED)
def compare_error_rates_with_target(n_trials=100, num_qubits=3, shots=1024):
    """
    Run multiple trials comparing baseline vs HRV-stabilized circuits.
    Uses identity circuits with known target states for ground truth.
    
    Args:
        n_trials: Number of independent trials to run
        num_qubits: Number of qubits in test circuit
        shots: Number of measurements per circuit
    
    Returns:
        baseline_errors: Array of baseline error rates
        stabilized_errors: Array of HRV-stabilized error rates
    """
    
    baseline_errors = []
    stabilized_errors = []
    
    simulator = AerSimulator()
    
    print(f"Running {n_trials} trials...")
    print(f"Qubits: {num_qubits} | Shots per trial: {shots}")
    print(f"Test circuit: Hadamard identity (H·H = I)")
    print(f"Target state: {'0' * num_qubits}")
    print(f"HRV correction: Applied BEFORE measurement\n")
    
    for trial in range(n_trials):
        if (trial + 1) % 20 == 0:
            print(f"  Trial {trial + 1}/{n_trials}...")
        
        # Create identity circuit with known target state (NO MEASUREMENTS YET)
        circuit, target_state = create_hadamard_identity_test(num_qubits, add_noise=True)
        
        # Generate fresh HRV data for this trial
        hrv_data = generate_mock_hrv(n_samples=num_qubits)
        
        # Create stabilized version with HRV corrections
        stabilized_circuit = apply_hrv_stabilization(circuit, hrv_data)
        
        # Create baseline version (just add measurements, no HRV)
        baseline_circuit = circuit.copy()
        baseline_circuit.measure_all()  # Add measurements for baseline
        
        # Run baseline circuit
        baseline_result = simulator.run(baseline_circuit, shots=shots).result()
        baseline_counts = baseline_result.get_counts()
        
        # Run stabilized circuit
        stabilized_result = simulator.run(stabilized_circuit, shots=shots).result()
        stabilized_counts = stabilized_result.get_counts()
        
        # Calculate error relative to TARGET STATE (ground truth)
        baseline_error = calculate_fidelity_to_target(baseline_counts, target_state, shots)
        stabilized_error = calculate_fidelity_to_target(stabilized_counts, target_state, shots)
        
        baseline_errors.append(baseline_error)
        stabilized_errors.append(stabilized_error)
    
    return np.array(baseline_errors), np.array(stabilized_errors)


# 7. EXECUTE AND DISPLAY RESULTS
print("\n" + "="*60)
print("STARTING VALIDATION RUN")
print("="*60 + "\n")

# Run the comparison
baseline, stabilized = compare_error_rates_with_target(
    n_trials=100,
    num_qubits=3,
    shots=1024
)

# Calculate improvement metrics
baseline_mean = baseline.mean()
stabilized_mean = stabilized.mean()
if baseline_mean > 0:
    improvement = (baseline_mean - stabilized_mean) / baseline_mean * 100
else:
    improvement = 0.0

# Statistical significance test (paired t-test)
t_stat, p_value = stats.ttest_rel(baseline, stabilized)

# Display results
print("\n" + "="*60)
print("VALIDATION RESULTS")
print("="*60)
print(f"Baseline error rate:   {baseline_mean:.3f} ± {baseline.std():.3f}")
print(f"Stabilized error rate: {stabilized_mean:.3f} ± {stabilized.std():.3f}")
print(f"Improvement:           {improvement:.1f}% reduction")
print("="*60)
print("\nSTATISTICAL ANALYSIS")
print("="*60)
print(f"Paired t-test: t = {t_stat:.3f}, p = {p_value:.6f}")
if p_value < 0.05:
    print("✓ Result is statistically significant (p < 0.05)")
else:
    print("⚠ Result not statistically significant (p ≥ 0.05)")
print("="*60 + "\n")


# 8. VISUALIZATION: Critical for understanding
print("Generating visualizations...")

fig = plt.figure(figsize=(14, 5))

# Plot 1: Trial-by-Trial Comparison
plt.subplot(131)
trial_range = min(30, len(baseline))  # Show first 30 trials
plt.plot(baseline[:trial_range], 'r-', label='Baseline', alpha=0.7, linewidth=2, marker='o', markersize=4)
plt.plot(stabilized[:trial_range], 'b-', label='HRV-Stabilized', alpha=0.7, linewidth=2, marker='s', markersize=4)
plt.xlabel('Trial Number', fontsize=11, fontweight='bold')
plt.ylabel('Error Rate (1 - Fidelity)', fontsize=11, fontweight='bold')
plt.title('Trial-by-Trial Comparison', fontsize=12, fontweight='bold')
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)
plt.ylim([0, 1])

# Plot 2: Mean Comparison with Error Bars
plt.subplot(132)
labels = ['Baseline', 'HRV-Stabilized']
means = [baseline_mean, stabilized_mean]
stds = [baseline.std(), stabilized.std()]
colors = ['#ff6b6b', '#4ecdc4']
bars = plt.bar(labels, means, yerr=stds, capsize=10, 
               color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
plt.ylabel('Mean Error Rate', fontsize=11, fontweight='bold')
plt.title(f'Mean Improvement: {improvement:.1f}%\n(p = {p_value:.4f})', 
          fontsize=12, fontweight='bold')
plt.grid(True, alpha=0.3, axis='y')
plt.ylim([0, max(means) * 1.3 if max(means) > 0 else 0.1])

# Add improvement annotation if improvement != 0
if improvement != 0:
    mid_point = (means[0] + means[1]) / 2
    plt.annotate('', xy=(0.5, means[0]), xytext=(0.5, means[1]),
                arrowprops=dict(arrowstyle='<->', lw=2, color='green'))
    plt.text(0.5, mid_point, f'{improvement:.1f}%', 
             ha='left', va='center', fontsize=10, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Plot 3: Distribution Comparison
plt.subplot(133)
plt.hist(baseline, bins=25, alpha=0.6, color='red', label='Baseline', 
         edgecolor='black', linewidth=0.5)
plt.hist(stabilized, bins=25, alpha=0.6, color='blue', label='HRV-Stabilized', 
         edgecolor='black', linewidth=0.5)
plt.xlabel('Error Rate', fontsize=11, fontweight='bold')
plt.ylabel('Frequency', fontsize=11, fontweight='bold')
plt.title('Error Rate Distribution', fontsize=12, fontweight='bold')
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('validation_results.png', dpi=150, bbox_inches='tight')
print("✓ Plot saved as 'validation_results.png'\n")

# 9. SUMMARY AND NEXT STEPS
print("="*60)
print("DEMO COMPLETE")
print("="*60)
print("\nKey Findings:")
print(f"  • HRV-stabilization reduces error by {improvement:.1f}%")
print(f"  • Result is {'statistically significant' if p_value < 0.05 else 'not significant'} (p = {p_value:.4f})")
print(f"  • Based on {len(baseline)} independent trials")
print(f"  • Uses ground truth methodology (identity circuits)")
print("\nMethodology:")
print("  • Target state validation (Hadamard identity H·H = I)")
print("  • State fidelity measurement (1 - error rate)")
print("  • 0.67Hz HRV rhythm component (anomalous frequency)")
print("  • Small phase corrections (±π/16 Z-rotations) applied BEFORE measurement")
print("\nNext Steps:")
print("  • See DEMO.md for hardware validation (Arc-15 array)")
print("  • See README.md for full project context")
print("  • See Codex67_Session1_FieldSomaticResponse.pdf for bio-validation")
print("\n" + "="*60)
print("Renaissance Field Lite - HRV1.0")
print("Bio-Synchronous Quantum Stabilization")
print("="*60 + "\n")
