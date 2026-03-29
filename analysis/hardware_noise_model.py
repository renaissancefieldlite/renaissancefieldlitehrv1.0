"""
Build a hardware-derived noise profile from available calibration-style data.

This model is intended to sit between the unconstrained detector lane and the
real backend lane. It does that by:

- anchoring local behavior to measured/calibration values
- modeling repeated short circuit executions rather than one impossible long-lived qubit
- separating fast per-shot decoherence from slower session drift
- comparing synthetic backend-style behavior against later observed captures
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


def derive_effective_circuit_duration_us(params: dict[str, float]) -> float:
    """
    Approximate the duration of one backend-style prepare/evolve/measure cycle.

    The current repos mostly use very small 1-2 qubit circuits, so the effective
    duration should stay short relative to T1/T2 while still responding to gate
    error, crosstalk, and circuit size.
    """
    gate_component = 180.0 * params["mean_gate_error"]
    crosstalk_component = 5.0 * params["mean_cross_talk"]
    qubit_component = 0.04 * max(params["qubit_count"] - 1, 0)
    duration_us = 0.55 + gate_component + crosstalk_component + qubit_component
    return float(np.clip(duration_us, 0.35, 2.5))


def _bounded_random_walk(rng: np.random.Generator, count: int, step_sigma: float, max_span: float) -> np.ndarray:
    walk = rng.normal(0.0, step_sigma, count).cumsum()
    walk -= np.mean(walk)
    if count == 0:
        return walk
    current_span = float(np.max(np.abs(walk)))
    if current_span <= 0:
        return walk
    scale = min(1.0, max_span / current_span)
    return walk * scale


def simulate_noise_trajectory(
    params: dict[str, float],
    duration_seconds: float = 60.0,
    sample_rate_hz: float = 50.0,
    shots_per_batch: int = 32,
    seed: int = 67,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    sample_count = max(1, int(duration_seconds * sample_rate_hz))
    time_axis = np.arange(sample_count) / sample_rate_hz

    t1_us = max(params["mean_t1_us"], 1e-9)
    t2_us = max(params["mean_t2_us"], 1e-9)
    effective_circuit_duration_us = derive_effective_circuit_duration_us(params)

    short_window_amplitude = np.exp(-effective_circuit_duration_us / t1_us)
    short_window_phase = np.exp(-effective_circuit_duration_us / t2_us)
    short_window_coherence = float(short_window_amplitude * short_window_phase)

    drift_span_limit = 0.0009 + (params["mean_cross_talk"] * 0.012)
    drift_offset = _bounded_random_walk(
        rng,
        sample_count,
        step_sigma=0.000015,
        max_span=drift_span_limit,
    )
    frequency_drift = params["mean_frequency_ghz"] + drift_offset

    drift_sensitivity = 0.01 + (params["mean_cross_talk"] * 0.1)
    session_stability_envelope = np.exp(-np.abs(drift_offset) / drift_sensitivity)

    depolarization_prob = min(params["mean_gate_error"] * 4.0, 0.05)
    readout_flip_prob = min(params["mean_readout_error"], 0.5)
    leakage_prob = min(params["derived_leakage_rate"] * 20.0, 0.03)
    neighbor_bleed_prob = min(params["mean_cross_talk"] * 1.5, 0.08)

    shot_shape = (sample_count, shots_per_batch)
    depolarization = rng.binomial(1, depolarization_prob, shot_shape)
    readout_flip = rng.binomial(1, readout_flip_prob, shot_shape)
    leakage = rng.binomial(1, leakage_prob, shot_shape)
    neighbor_bleed = rng.binomial(1, neighbor_bleed_prob, shot_shape)

    shot_quality = np.full(shot_shape, short_window_coherence, dtype=float)
    shot_quality *= session_stability_envelope[:, None]
    shot_quality *= (1.0 - 0.18 * depolarization)
    shot_quality *= (1.0 - 0.08 * readout_flip)
    shot_quality *= (1.0 - 0.10 * leakage)
    shot_quality *= (1.0 - 0.06 * neighbor_bleed)
    shot_quality = np.clip(shot_quality, 0.0, 1.0)

    batch_success_rate = np.mean(shot_quality, axis=1)
    batch_error_rate = 1.0 - batch_success_rate
    batch_readout_flip_rate = np.mean(readout_flip, axis=1)
    batch_depolarization_rate = np.mean(depolarization, axis=1)
    batch_leakage_rate = np.mean(leakage, axis=1)
    batch_neighbor_bleed_rate = np.mean(neighbor_bleed, axis=1)

    report = {
        "schema_version": "rfl.hardware_noise_profile.v2",
        "duration_seconds": duration_seconds,
        "sample_rate_hz": sample_rate_hz,
        "sample_count": sample_count,
        "shots_per_batch": shots_per_batch,
        "parameters": params,
        "model": {
            "mode": "repeated_short_window_backend_proxy",
            "effective_circuit_duration_us": effective_circuit_duration_us,
            "short_window_amplitude": float(short_window_amplitude),
            "short_window_phase": float(short_window_phase),
            "short_window_coherence": short_window_coherence,
            "session_drift_sensitivity_ghz": float(drift_sensitivity),
        },
        "summary": {
            "mean_coherence_proxy": float(np.mean(batch_success_rate)),
            "min_coherence_proxy": float(np.min(batch_success_rate)),
            "max_coherence_proxy": float(np.max(batch_success_rate)),
            "mean_short_window_coherence": short_window_coherence,
            "mean_session_stability": float(np.mean(session_stability_envelope)),
            "mean_batch_error_rate": float(np.mean(batch_error_rate)),
            "mean_readout_flip_rate": float(np.mean(batch_readout_flip_rate)),
            "mean_depolarization_rate": float(np.mean(batch_depolarization_rate)),
            "mean_leakage_rate": float(np.mean(batch_leakage_rate)),
            "mean_neighbor_bleed_rate": float(np.mean(batch_neighbor_bleed_rate)),
            "drift_span_ghz": float(np.max(frequency_drift) - np.min(frequency_drift)),
            "depolarization_events": int(np.sum(depolarization)),
            "readout_flip_events": int(np.sum(readout_flip)),
            "leakage_events": int(np.sum(leakage)),
            "neighbor_bleed_events": int(np.sum(neighbor_bleed)),
        },
        "time_series": {
            "time_s": time_axis.tolist(),
            "coherence_proxy": batch_success_rate.tolist(),
            "session_stability_envelope": session_stability_envelope.tolist(),
            "batch_error_rate": batch_error_rate.tolist(),
            "batch_readout_flip_rate": batch_readout_flip_rate.tolist(),
            "batch_depolarization_rate": batch_depolarization_rate.tolist(),
            "batch_leakage_rate": batch_leakage_rate.tolist(),
            "batch_neighbor_bleed_rate": batch_neighbor_bleed_rate.tolist(),
            "frequency_drift_ghz": frequency_drift.tolist(),
        },
    }
    return report


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Build a hardware-derived local noise/decoherence model.")
    parser.add_argument("calibration_json", help="Path to calibration-style JSON data.")
    parser.add_argument("--duration", type=float, default=60.0, help="Simulation duration in seconds.")
    parser.add_argument("--sample-rate", type=float, default=50.0, help="Simulation sample rate in Hz.")
    parser.add_argument("--shots-per-batch", type=int, default=32, help="Repeated backend-style shots per batch.")
    parser.add_argument("--seed", type=int, default=67, help="Random seed.")
    parser.add_argument("--output", help="Optional output path for the generated profile JSON.")
    args = parser.parse_args()

    calibration = load_calibration(args.calibration_json)
    params = extract_noise_parameters(calibration)
    report = simulate_noise_trajectory(
        params,
        duration_seconds=args.duration,
        sample_rate_hz=args.sample_rate,
        shots_per_batch=args.shots_per_batch,
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
