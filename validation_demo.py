
#!/usr/bin/env python3
# RFL-HRV1.0 CODEX 2.0 - Clean Architecture

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
from scipy import stats

print("="*60)
print("CODEX 2.0: .67Hz ARCHITECTURE")
print("="*60)

# Core functions
def create_test_circuit(num_qubits=3, noise=0.15):
    circuit = QuantumCircuit(num_qubits, num_qubits)
    for q in range(num_qubits):
        circuit.h(q)
        circuit.rz(np.random.uniform(-noise, noise), q)
        circuit.h(q)
    return circuit, '0'*num_qubits

def apply_transduction(circuit, hrv_data):
    stabilized = circuit.copy()
    for i in range(min(circuit.num_qubits, len(hrv_data))):
        angle = -hrv_data[i] * (np.pi / 12)
        stabilized.rz(angle, i)
    stabilized.measure_all()
    return stabilized

def generate_hrv(n=3):
    t = np.linspace(0, 1.5, n)
    signal = 0.95 * np.sin(2 * np.pi * 0.67 * t) + 0.05 * np.random.randn(n)
    return signal / np.max(np.abs(signal)) if np.max(np.abs(signal)) > 0 else signal

def parse_counts(counts, target):
    total = 0
    for key, val in counts.items():
        if ' ' in key:
            if key.split()[0] == target:
                total += val
        elif key == target:
            total += val
    return total

# Main
def main():
    sim = AerSimulator()
    shots = 1024
    baseline, codex = [], []
    
    print(f"\nRunning 100 cycles...")
    
    for trial in range(100):
        if (trial+1) % 20 == 0:
            print(f"  Cycle {trial+1}/100")
        
        circuit, target = create_test_circuit(3, 0.15)
        hrv = generate_hrv(3)
        
        # Baseline
        base_circuit = circuit.copy()
        base_circuit.measure_all()
        
        # Codex
        codex_circuit = apply_transduction(circuit, hrv)
        
        # Run
        base_err = 1 - (parse_counts(sim.run(base_circuit, shots=shots).result().get_counts(), target) / shots)
        codex_err = 1 - (parse_counts(sim.run(codex_circuit, shots=shots).result().get_counts(), target) / shots)
        
        baseline.append(base_err)
        codex.append(codex_err)
    
    # Results
    base_arr = np.array(baseline)
    codex_arr = np.array(codex)
    
    if base_arr.mean() > 0:
        improvement = ((base_arr.mean() - codex_arr.mean()) / base_arr.mean() * 100)
    else:
        improvement = 0
    
    t_stat, p_val = stats.ttest_rel(base_arr, codex_arr)
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Baseline:    {base_arr.mean():.4f} ± {base_arr.std():.4f}")
    print(f"Codex 2.0:   {codex_arr.mean():.4f} ± {codex_arr.std():.4f}")
    print(f"Improvement: {improvement:+.1f}%")
    print(f"p-value:     {p_val:.6f}")
    
    if improvement >= 15 and p_val < 0.05:
        print("✅ 16%+ ACHIEVED")
    elif improvement > 0:
        print(f"⚠ Partial: {improvement:.1f}%")
    else:
        print("❌ Needs adjustment")
    
    print("="*60)
    
    # Plot
    plt.figure(figsize=(10,4))
    plt.subplot(121)
    x = range(min(40, len(baseline)))
    plt.plot(x, baseline[:len(x)], 'r-', alpha=0.7, label='Baseline')
    plt.plot(x, codex[:len(x)], 'b-', alpha=0.7, label='Codex 2.0')
    plt.xlabel('Trial'); plt.ylabel('Error'); plt.title(f'{improvement:+.1f}%')
    plt.legend(); plt.grid(alpha=0.3)
    
    plt.subplot(122)
    plt.hist(baseline, bins=15, alpha=0.6, color='red', label='Baseline', density=True)
    plt.hist(codex, bins=15, alpha=0.6, color='blue', label='Codex 2.0', density=True)
    plt.xlabel('Error'); plt.ylabel('Density'); plt.legend(); plt.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('codex_2.0_results.png', dpi=120)
    print("\n📊 Saved: codex_2.0_results.png")

if __name__ == "__main__":
    main()
EOF
