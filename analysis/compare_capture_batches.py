#!/usr/bin/env python3
"""Compare repeated capture artifacts against the hardware-derived model."""

from __future__ import annotations

import argparse
import glob
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats


TARGET_ZERO_KEYS = {"00", "0x0"}
TARGET_THREE_KEYS = {"11", "0x3"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_manifest_capture_paths(path: Path) -> list[Path]:
    payload = load_json(path)
    if payload.get("schema_version") != "rfl.capture_batch.v2":
        return []
    return [Path(item).resolve() for item in payload.get("capture_files", [])]


def collect_capture_paths(patterns: list[str]) -> list[Path]:
    found: list[Path] = []
    for pattern in patterns:
        for match in glob.glob(pattern):
            p = Path(match)
            if p.is_file():
                manifest_paths = extract_manifest_capture_paths(p)
                if manifest_paths:
                    found.extend(manifest_paths)
                else:
                    found.append(p)
    deduped = sorted({path.resolve() for path in found})
    return deduped


def extract_counts(capture: dict[str, Any]) -> dict[str, int]:
    raw_result = capture.get("raw_result", capture)
    if raw_result.get("results"):
        first = raw_result["results"][0]
        return dict(first.get("data", {}).get("counts", {}))
    if raw_result.get("experiments"):
        first = raw_result["experiments"][0]
        return dict(first.get("measurement_counts", {}))
    return {}


def compute_capture_metrics(path: Path) -> dict[str, Any]:
    capture = load_json(path)
    provider = capture.get("provider")
    backend_name = capture.get("backend_name", "unknown")
    if not provider:
        provider = "aer" if backend_name == "aer_simulator" else "ibm-or-legacy"
    counts = extract_counts(capture)
    total = int(sum(counts.values()))
    if total <= 0:
        raise ValueError(f"{path} has no measurable counts.")

    zero_prob = sum(counts.get(key, 0) for key in TARGET_ZERO_KEYS) / total
    three_prob = sum(counts.get(key, 0) for key in TARGET_THREE_KEYS) / total
    target_subspace_probability = zero_prob + three_prob
    off_target_probability = max(0.0, 1.0 - target_subspace_probability)
    bell_imbalance = abs(zero_prob - three_prob)

    return {
        "path": str(path),
        "provider": provider,
        "backend_name": backend_name,
        "created_at_utc": capture.get("created_at_utc"),
        "job_id": capture.get("job_id"),
        "shots": total,
        "zero_probability": zero_prob,
        "three_probability": three_prob,
        "target_subspace_probability": target_subspace_probability,
        "off_target_probability": off_target_probability,
        "bell_imbalance": bell_imbalance,
        "counts": counts,
    }


def summarize_group(items: list[dict[str, Any]], step2_proxy: float) -> dict[str, Any]:
    target_probs = np.array([item["target_subspace_probability"] for item in items], dtype=float)
    off_target_probs = np.array([item["off_target_probability"] for item in items], dtype=float)
    imbalances = np.array([item["bell_imbalance"] for item in items], dtype=float)

    return {
        "count": int(len(items)),
        "mean_target_subspace_probability": float(np.mean(target_probs)),
        "std_target_subspace_probability": float(np.std(target_probs)),
        "mean_off_target_probability": float(np.mean(off_target_probs)),
        "mean_bell_imbalance": float(np.mean(imbalances)),
        "delta_vs_step2_proxy": float(np.mean(target_probs) - step2_proxy),
        "captures": items,
    }


def _compare_metric(
    a_name: str,
    a: list[dict[str, Any]],
    b_name: str,
    b: list[dict[str, Any]],
    metric: str,
) -> dict[str, Any] | None:
    if len(a) < 2 or len(b) < 2:
        return None

    a_values = np.array([item[metric] for item in a], dtype=float)
    b_values = np.array([item[metric] for item in b], dtype=float)
    t_stat, p_value = stats.ttest_ind(a_values, b_values, equal_var=False)

    pooled_var = ((np.var(a_values, ddof=1) + np.var(b_values, ddof=1)) / 2.0)
    if pooled_var <= 0:
        effect_size = 0.0
    else:
        effect_size = float((np.mean(a_values) - np.mean(b_values)) / np.sqrt(pooled_var))

    return {
        "metric": metric,
        "group_a": a_name,
        "group_b": b_name,
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "effect_size": effect_size,
        "delta_mean": float(np.mean(a_values) - np.mean(b_values)),
    }


def build_report(capture_paths: list[Path], hardware_profile: Path) -> dict[str, Any]:
    profile = load_json(hardware_profile)
    step2_proxy = float(profile["summary"]["mean_coherence_proxy"])
    step2_short_window = float(profile["summary"]["mean_short_window_coherence"])
    step2_session_stability = float(profile["summary"]["mean_session_stability"])

    metrics = [compute_capture_metrics(path) for path in capture_paths]
    by_provider: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in metrics:
        by_provider[item["provider"]].append(item)

    provider_summaries = {
        provider: summarize_group(items, step2_proxy)
        for provider, items in sorted(by_provider.items())
    }

    comparisons: list[dict[str, Any]] = []
    providers = sorted(by_provider)
    for idx, provider_a in enumerate(providers):
        for provider_b in providers[idx + 1:]:
            for metric in ("target_subspace_probability", "off_target_probability", "bell_imbalance"):
                comparison = _compare_metric(
                    provider_a,
                    by_provider[provider_a],
                    provider_b,
                    by_provider[provider_b],
                    metric,
                )
                if comparison:
                    comparisons.append(comparison)

    return {
        "schema_version": "rfl.capture_comparison.v1",
        "hardware_profile": str(hardware_profile),
        "step2_reference": {
            "mean_coherence_proxy": step2_proxy,
            "mean_short_window_coherence": step2_short_window,
            "mean_session_stability": step2_session_stability,
        },
        "capture_count": len(metrics),
        "providers": provider_summaries,
        "comparisons": comparisons,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare capture batches against the HRV1.0 hardware-derived model.")
    parser.add_argument(
        "--captures",
        nargs="+",
        required=True,
        help="Capture file globs to include in the comparison.",
    )
    parser.add_argument(
        "--hardware-profile",
        default="/Users/renaissancefieldlite1.0/Documents/Playground/renaissancefieldlitehrv1.0/data/derived_noise/sample_noise_profile.json",
    )
    parser.add_argument("--output")
    args = parser.parse_args()

    capture_paths = collect_capture_paths(args.captures)
    if not capture_paths:
        raise SystemExit("No capture files matched the provided patterns.")

    report = build_report(capture_paths, Path(args.hardware_profile))

    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"✓ saved → {output_path}")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
