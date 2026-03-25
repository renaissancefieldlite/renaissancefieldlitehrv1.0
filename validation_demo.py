#!/usr/bin/env python3
"""
Synthetic 0.67 Hz detector sketch for the RFL-HRV1.0 repo.

This script generates synthetic signals with an explicit target-band
component near 0.67 Hz and then demonstrates how the current detection
and visualization stack responds. It is useful for concept development
and detector behavior checks. It is not empirical proof of an intrinsic
hardware rhythm.
"""
import numpy as np
from scipy import signal, stats
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def demonstrate_paradigm_shift():
    """Show the conceptual difference between the two framings."""
    
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                     SYNTHETIC DETECTOR FRAMING WALKTHROUGH                   ║")
    print("╠══════════════════════════════════════════════════════════════════════════════╣")
    print("║                                                                              ║")
    print("║  WHAT WE PREVIOUSLY THOUGHT (WRONG):                                         ║")
    print("║  Human HRV → contains 0.67Hz → controls quantum computers                    ║")
    print("║                                                                              ║")
    print("║  CURRENT WORKING HYPOTHESIS:                                                  ║")
    print("║  Candidate machine rhythm near 0.67Hz may be detectable in telemetry         ║")
    print("║  Synthetic demo here shows detector behavior when that band is present        ║")
    print("║                                                                              ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print()

def create_comparison_visualization():
    """Create a side-by-side synthetic comparison of the two framings."""
    
    # Time array
    t = np.linspace(0, 30, 3000)
    
    # LEFT: old framing
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    
    # 1. Human HRV signal (biological)
    human_hrv = 0.5 * np.sin(2 * np.pi * 0.1 * t)  # Normal HRV ~0.1Hz
    human_hrv += 0.1 * np.sin(2 * np.pi * 0.67 * t)  # Small 0.67Hz component
    human_hrv += 0.2 * np.random.randn(len(t))  # Biological noise
    
    axes[0, 0].plot(t[:500], human_hrv[:500], 'g-', linewidth=1.5, alpha=0.7)
    axes[0, 0].set_title('OLD: Human HRV Signal\n(Normal ~0.1Hz + small 0.67Hz)')
    axes[0, 0].set_xlabel('Time (s)')
    axes[0, 0].set_ylabel('Amplitude')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Human HRV spectrum
    freqs_h, power_h = signal.welch(human_hrv, fs=100, nperseg=1024)
    axes[0, 1].plot(freqs_h, power_h, 'g-', linewidth=1.5, alpha=0.7)
    axes[0, 1].axvline(0.1, color='darkgreen', linestyle='--', alpha=0.5, label='Normal HRV')
    axes[0, 1].axvline(0.67, color='red', linestyle='--', alpha=0.5, label='Anomalous 0.67Hz')
    axes[0, 1].set_title('Human HRV Frequency Spectrum')
    axes[0, 1].set_xlabel('Frequency (Hz)')
    axes[0, 1].set_ylabel('Power')
    axes[0, 1].legend(fontsize=8)
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Old paradigm diagram
    axes[0, 2].text(0.5, 0.7, 'OLD PARADIGM:\nHuman → Quantum', 
                   ha='center', fontsize=12, fontweight='bold', color='red')
    axes[0, 2].text(0.5, 0.5, 'Human HRV\n(0.67Hz)', 
                   ha='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
    axes[0, 2].arrow(0.5, 0.45, 0, -0.1, head_width=0.05, head_length=0.05, fc='red', ec='red')
    axes[0, 2].text(0.5, 0.3, 'Quantum\nComputer', 
                   ha='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
    axes[0, 2].text(0.5, 0.1, 'Assumption: Human controls\nquantum with biology', 
                   ha='center', fontsize=9, style='italic', color='gray')
    axes[0, 2].axis('off')
    
    # RIGHT: current working hypothesis
    
    # 1. Quantum system telemetry
    quantum_pulse = 0.8 * np.sin(2 * np.pi * 0.67 * t)  # Strong 0.67Hz pulse
    quantum_harmonic = 0.3 * np.sin(2 * np.pi * 1.34 * t)  # First harmonic
    quantum_noise = 0.2 * np.random.randn(len(t))  # Quantum noise (different character)
    
    quantum_signal = quantum_pulse + quantum_harmonic + quantum_noise
    
    axes[1, 0].plot(t[:500], quantum_signal[:500], 'b-', linewidth=1.5, alpha=0.7)
    axes[1, 0].set_title('NEW: Synthetic Machine Telemetry\n(Injected target-band 0.67Hz component)')
    axes[1, 0].set_xlabel('Time (s)')
    axes[1, 0].set_ylabel('Coherence')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 2. Quantum system spectrum
    freqs_q, power_q = signal.welch(quantum_signal, fs=100, nperseg=1024)
    axes[1, 1].plot(freqs_q, power_q, 'b-', linewidth=1.5, alpha=0.7)
    axes[1, 1].axvline(0.67, color='blue', linestyle='--', alpha=0.7, label='Quantum pulse')
    axes[1, 1].axvline(1.34, color='purple', linestyle=':', alpha=0.5, label='Harmonic')
    axes[1, 1].set_title('Quantum System Frequency Spectrum')
    axes[1, 1].set_xlabel('Frequency (Hz)')
    axes[1, 1].set_ylabel('Power')
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].grid(True, alpha=0.3)
    
    # 3. New paradigm diagram
    axes[1, 2].text(0.5, 0.8, 'CURRENT HYPOTHESIS:\nMachine Telemetry First', 
                   ha='center', fontsize=12, fontweight='bold', color='blue')
    axes[1, 2].text(0.5, 0.6, 'Synthetic Telemetry\nTarget Band Near 0.67Hz', 
                   ha='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
    axes[1, 2].arrow(0.5, 0.55, 0, -0.1, head_width=0.05, head_length=0.05, fc='blue', ec='blue')
    axes[1, 2].text(0.5, 0.4, 'Human Detector\n(Bio-Resonance)', 
                   ha='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
    axes[1, 2].arrow(0.5, 0.35, 0, -0.1, head_width=0.05, head_length=0.05, fc='green', ec='green')
    axes[1, 2].text(0.5, 0.2, 'Detector Response\nand Hypothesis Refinement', 
                   ha='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="gold", alpha=0.7))
    axes[1, 2].text(0.5, 0.05, 'This figure is synthetic.\nRaw backend capture is a separate step.', 
                   ha='center', fontsize=9, style='italic', color='darkblue')
    axes[1, 2].axis('off')
    
    plt.suptitle('PARADIGM SHIFT: From Human-Control Story To Machine-Telemetry Hypothesis', 
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('paradigm_shift_demonstration.png', dpi=120, bbox_inches='tight')
    
    return fig

def run_quantum_system_validation():
    """Run synthetic tests on the detector pipeline."""
    
    print("\n" + "="*70)
    print("SYNTHETIC 0.67 HZ DETECTOR TESTS")
    print("="*70)
    
    # Generate test data
    np.random.seed(42)  # For reproducibility
    t = np.linspace(0, 600, 60000)  # 10 minutes of data
    
    # Create synthetic machine-side signals
    quantum_signals = []
    results = []
    
    for i in range(5):  # Test 5 different quantum system "states"
        # Base synthetic target-band pulse
        pulse_freq = np.random.normal(0.67, 0.01)  # Slight variation around 0.67Hz
        pulse_amp = np.random.uniform(0.4, 0.9)  # Varying coherence strength
        
        quantum_pulse = pulse_amp * np.sin(2 * np.pi * pulse_freq * t)
        
        # Add harmonics and noise to vary the synthetic examples
        harmonics = 0.2 * np.sin(2 * np.pi * pulse_freq * 2 * t)  # Harmonics
        quantum_breathing = 0.1 * np.sin(2 * np.pi * 0.15 * t)  # Slow "breathing"
        quantum_noise = 0.3 * np.random.randn(len(t)) * (1 + 0.5 * np.sin(2 * np.pi * 0.01 * t))
        
        sig_data = quantum_pulse + harmonics + quantum_breathing * quantum_pulse + quantum_noise
        quantum_signals.append(sig_data)
        
        # Analyze using signal.welch
        freqs, power = signal.welch(sig_data, fs=100, nperseg=4096)
        target_mask = (freqs >= 0.65) & (freqs <= 0.69)
        
        if np.any(target_mask):
            peak_idx = np.argmax(power[target_mask])
            peak_freq = freqs[target_mask][peak_idx]
            peak_power = power[target_mask][peak_idx]
            
            # Calculate metrics
            baseline = np.median(power[(freqs > 1) & (freqs < 10)])
            snr = peak_power / baseline if baseline > 0 else 0
            
            # Determine if the target band is detected
            pulse_detected = (abs(peak_freq - 0.67) < 0.015 and snr > 2.0)
            
            results.append({
                'test': i + 1,
                'detected_freq': peak_freq,
                'deviation': abs(peak_freq - 0.67),
                'snr': snr,
                'pulse_detected': pulse_detected,
                'health': 'HEALTHY' if pulse_detected and snr > 3 else 'STABLE' if pulse_detected else 'WEAK'
            })
    
    # Print results
    print("\nVALIDATION RESULTS:")
    print("-" * 70)
    print(f"{'Test':<6} {'Frequency':<12} {'Deviation':<12} {'SNR':<10} {'Detected':<10} {'Health':<10}")
    print("-" * 70)
    
    detected_count = 0
    for r in results:
        print(f"{r['test']:<6} {r['detected_freq']:.4f} Hz {'':<2} ±{r['deviation']:.4f} Hz {'':<2} "
              f"{r['snr']:.1f}{'':<4} {r['pulse_detected']!s:<10} {r['health']:<10}")
        if r['pulse_detected']:
            detected_count += 1
    
    print("-" * 70)
    detection_rate = detected_count / len(results) * 100
    print(f"Detection Rate: {detection_rate:.1f}% ({detected_count}/{len(results)} synthetic systems)")
    
    # Statistical analysis
    freqs_list = [r['detected_freq'] for r in results]
    mean_freq = np.mean(freqs_list)
    std_freq = np.std(freqs_list)
    
    print(f"\nSTATISTICAL ANALYSIS:")
    print(f"• Mean frequency: {mean_freq:.4f} Hz")
    print(f"• Standard deviation: {std_freq:.4f} Hz")
    print(f"• 95% confidence interval: [{mean_freq - 1.96*std_freq:.4f}, {mean_freq + 1.96*std_freq:.4f}] Hz")
    
    # T-test against 0.67Hz
    t_stat, p_value = stats.ttest_1samp(freqs_list, 0.67)
    print(f"• T-test against 0.67Hz: t = {t_stat:.3f}, p = {p_value:.4f}")
    
    if p_value > 0.05:
        print("  → Synthetic detections cluster around 0.67Hz, as expected from the generated inputs")
    else:
        print("  → Synthetic detections drift from the seeded target band; adjust the demo generator")
    
    return results, detection_rate

def main():
    """Main synthetic demonstration function."""
    
    # Show paradigm shift
    demonstrate_paradigm_shift()
    
    # Run validation tests
    results, detection_rate = run_quantum_system_validation()
    
    # Create visualization
    print("\n" + "="*70)
    print("CREATING SYNTHETIC PARADIGM VISUALIZATION...")
    fig = create_comparison_visualization()
    
    print("\n" + "="*70)
    print("CONCLUSIONS:")
    print("="*70)
    
    print("1. WHAT THIS SCRIPT SHOWS:")
    print("   • The current detector pipeline responds to a synthetic target band near 0.67Hz")
    print("   • The visualization cleanly separates the older HRV-control story from the telemetry-first framing")
    print("   • The demo is useful for concept iteration and detector checks")
    
    print("\n2. HOW TO READ THE RESULTS:")
    print(f"   • Detection rate: {detection_rate:.1f}%")
    print("   • The reported p-value applies to synthetic data generated inside this script")
    print("   • It should not be read as hardware proof")
    
    print("\n3. WHAT THE REPO STILL NEEDS:")
    print("   • Repeated raw backend capture")
    print("   • Analysis on non-injected data")
    print("   • Clear separation between simulator artifacts and empirical claims")
    
    print("\n4. NEXT STEPS:")
    print("   • Use hrv_ingest/hardware_ingest.py for local or IBM backend capture")
    print("   • Inspect saved JSON with analysis/summarize_capture.py")
    print("   • Reserve physical claims for repeated hardware-backed results")
    
    print("\n" + "="*70)
    print("FINAL STATEMENT:")
    print("This file is a synthetic sketch of the detector path.")
    print("It helps define the search target.")
    print("Raw backend capture is the empirical step.")
    print("="*70)
    
    print(f"\n📊 Visualization saved: paradigm_shift_demonstration.png")
    print("   This shows the critical difference between old and new understanding.")
    
    # Additional metrics file
    with open('quantum_system_validation_metrics.txt', 'w') as f:
        f.write("SYNTHETIC DETECTOR METRICS\n")
        f.write("="*50 + "\n")
        f.write(f"Detection Rate: {detection_rate:.1f}%\n")
        f.write(f"Mean Frequency: {np.mean([r['detected_freq'] for r in results]):.4f} Hz\n")
        f.write(f"Standard Deviation: {np.std([r['detected_freq'] for r in results]):.4f} Hz\n")
        f.write("\nINDIVIDUAL SYNTHETIC SYSTEM RESULTS:\n")
        for r in results:
            f.write(f"Synthetic system {r['test']}: {r['detected_freq']:.4f} Hz, "
                   f"SNR: {r['snr']:.1f}, Detected: {r['pulse_detected']}\n")
    
    print(f"📄 Metrics saved: quantum_system_validation_metrics.txt")

if __name__ == "__main__":
    main()
