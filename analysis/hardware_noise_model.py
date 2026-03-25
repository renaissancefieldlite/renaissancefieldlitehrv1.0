"""
Build a hardware-derived noise profile and synthetic decoherence trajectory
from available calibration-style data.

This does not replace real hardware capture. It gives the project a way to:

- anchor simulation parameters to measured/calibration values
- model drift, decoherence, readout error, leakage, and crosstalk locally
- compare synthetic trajectories against later observed captures
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


def load_calibration(path: str) -> dict[str, Any]:
    return json.loads(Path(path).resolve().read_text(encoding="utf-8"))


def extract_noise_parameters(calibration: dict[str, Any]) -> dict[str, float]:
    qubits = calibration.get("qubits", [])
    couplers = calibration.get("couplers", [])

    def mean_or(default: float, values: list[float]) -> float:
        return float(np.mean(values)) if values else default

    t1_values = [float(item.get("t1_us", 0.0)) for item in qubits if item.get("t1_us") is not None]
    t2_values = [float(item.get("t2_us", 0.0)) for item in qubits if item.get("t2_us") is not None]
    readout_values = [float(item.get("readout_error", 0.0)) for item in qubits if item.get("readout_error") is not None]
    gate_values = [float(item.get("single_qubit_gate_error", 0.0)) for item in qubits if item.get("single_qubit_gate_error") is not None]
    freq_values = [float(item.get("frequency_ghz", 0.0)) for item in qubits if item.get("frequency_ghz") is not None]
    anharmonicity_values = [abs(float(item.get("anharmonicity_ghz", 0.0))) for item in qubits if item.get("anharmonicity_ghz") is not None]
    crosstalk_values = [float(item.get("cross_talk", 0.0)) for item in couplers if item.get("cross_talk") is not None]

    params = {
        "mean_t1_us": mean_or(120.0, t1_values),
        "mean_t2_us": mean_or(90.0, t2_values),
        "mean_readout_error": mean_or(0.02, readout_values),
        "mean_gate_error": mean_or(0.001, gate_values),
        "mean_frequency_ghz": mean_or(5.0, freq_values),
        "mean_anharmonicity_ghz": mean_or(0.2, anharmonicity_values),
        "mean_cross_talk": mean_or(0.01, crosstalk_values),
        "qubit_count": len(qubits),
        "coupler_count": len(couplers),
    }
    params["derived_phase_drift_rate"] = float(1.0 / max(params["mean_t2_us"], 1e-9))
    params["derived_amplitude_decay_rate"] = float(1.0 / max(params["mean_t1_us"], 1e-9))
    params["derived_leakage_rate"] = float(params["mean_gate_error"] * (1.0 / max(params["mean_anharmonicity_ghz"], 1e-9)) * 0.01)
    return params


def simulate_noise_trajectory(
    params: dict[str, float],
    duration_seconds: float = 60.0,
    sample_rate_hz: float = 50.0,
    seed: int = 67,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    sample_count = int(duration_seconds * sample_rate_hz)
    time_axis = np.arange(sample_count) / sample_rate_hz

    t1_s = params["mean_t1_us"] * 1e-6
    t2_s = params["mean_t2_us"] * 1e-6
    if t1_s <= 0:
        t1_s = 1e-3
    if t2_s <= 0:
        t2_s = 1e-3

    amplitude_decay = np.exp(-time_axis / t1_s)
    phase_decay = np.exp(-time_axis / t2_s)

    # Slow random-walk drift around the mean frequency.
    drift_noise = rng.normal(0.0, 0.0005, sample_count).cumsum()
    frequency_drift = params["mean_frequency_ghz"] + drift_noise

    depolarization = rng.binomial(1, min(params["mean_gate_error"] * 10.0, 0.25), sample_count)
    readout_flip = rng.binomial(1, min(params["mean_readout_error"], 0.5), sample_count)
    leakage = rng.binomial(1, min(params["derived_leakage_rate"] * 100.0, 0.2), sample_count)
    neighbor_bleed = rng.binomial(1, min(params["mean_cross_talk"] * 5.0, 0.2), sample_count)

    coherence_proxy = amplitude_decay * phase_decay
    coherence_proxy *= (1.0 - 0.15 * depolarization)
    coherence_proxy *= (1.0 - 0.10 * leakage)
    coherence_proxy *= (1.0 - 0.10 * neighbor_bleed)

    report = {
        "schema_version": "rfl.hardware_noise_profile.v1",
        "duration_seconds": duration_seconds,
        "sample_rate_hz": sample_rate_hz,
        "sample_count": sample_count,
        "parameters": params,
        "summary": {
            "mean_coherence_proxy": float(np.mean(coherence_proxy)),
            "min_coherence_proxy": float(np.min(coherence_proxy)),
            "max_coherence_proxy": float(np.max(coherence_proxy)),
            "drift_span_ghz": float(np.max(frequency_drift) - np.min(frequency_drift)),
            "depolarization_events": int(np.sum(depolarization)),
            "readout_flip_events": int(np.sum(readout_flip)),
            "leakage_events": int(np.sum(leakage)),
            "neighbor_bleed_events": int(np.sum(neighbor_bleed)),
        },
        "time_series": {
            "time_s": time_axis.tolist(),
            "coherence_proxy": coherence_proxy.tolist(),
            "frequency_drift_ghz": frequency_drift.tolist(),
            "depolarization_events": depolarization.tolist(),
            "readout_flip_events": readout_flip.tolist(),
            "leakage_events": leakage.tolist(),
            "neighbor_bleed_events": neighbor_bleed.tolist(),
        },
    }
    return report


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Build a hardware-derived local noise/decoherence model.")
    parser.add_argument("calibration_json", help="Path to calibration-style JSON data.")
    parser.add_argument("--duration", type=float, default=60.0, help="Simulation duration in seconds.")
    parser.add_argument("--sample-rate", type=float, default=50.0, help="Simulation sample rate in Hz.")
    parser.add_argument("--seed", type=int, default=67, help="Random seed.")
    parser.add_argument("--output", help="Optional output path for the generated profile JSON.")
    args = parser.parse_args()

    calibration = load_calibration(args.calibration_json)
    params = extract_noise_parameters(calibration)
    report = simulate_noise_trajectory(
        params,
        duration_seconds=args.duration,
        sample_rate_hz=args.sample_rate,
        seed=args.seed,
    )

    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"✓ saved → {output_path}")
    else:
        print(json.dumps(report, indent=2))

    return report


if __name__ == "__main__":
    main()
