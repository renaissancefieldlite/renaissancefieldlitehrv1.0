#!/usr/bin/env python3
"""Summarize a saved capture JSON from this repository."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_capture(path: Path) -> dict:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise SystemExit(f"{path} does not contain a single result dictionary.")
    return data


def unwrap_capture(data: dict) -> tuple[str, str, str | None, dict]:
    """Normalize legacy and v1 capture payloads into a common view."""
    if "schema_version" in data and "raw_result" in data:
        provider = data.get("provider", "unknown")
        backend_name = data.get("backend_name", "unknown")
        capture_mode = data.get("capture_mode")
        return provider, backend_name, capture_mode, data["raw_result"]

    backend_name = data.get("backend_name", "unknown")
    provider = "aer" if backend_name == "aer_simulator" else "ibm-or-legacy"
    return provider, backend_name, None, data


def summarize_qiskit_result(raw_result: dict) -> None:
    """Print summary details for a qiskit Result-style dictionary."""
    success = raw_result.get("success")
    results = raw_result.get("results", [])

    print(f"top-level success: {success}")
    print(f"experiments saved: {len(results)}")

    shot_values = [entry.get("shots") for entry in results if isinstance(entry, dict)]
    time_values = [
        entry.get("time_taken")
        for entry in results
        if isinstance(entry, dict) and entry.get("time_taken") is not None
    ]

    if shot_values:
        print(f"shots per experiment: min={min(shot_values)} max={max(shot_values)}")
    else:
        print("shots per experiment: unavailable")

    if time_values:
        print(f"time_taken fields: {len(time_values)} present")
        print(f"time_taken range: {min(time_values):.6f}s .. {max(time_values):.6f}s")
    else:
        print("time_taken fields: unavailable")

    if results:
        first = results[0]
        counts = first.get("data", {}).get("counts", {})
        if counts:
            preview = list(counts.items())[:5]
            print(f"first experiment counts preview: {preview}")
        else:
            print("first experiment counts preview: unavailable")


def summarize_braket_local_result(raw_result: dict) -> None:
    """Print summary details for a Braket local result wrapper."""
    experiments = raw_result.get("experiments", [])
    print("top-level success: unavailable")
    print(f"experiments saved: {len(experiments)}")

    if not experiments:
        print("shots per experiment: unavailable")
        print("time_taken fields: unavailable")
        print("first experiment counts preview: unavailable")
        return

    first_counts = experiments[0].get("measurement_counts", {})
    first_shots = sum(first_counts.values()) if first_counts else 0
    print(f"shots per experiment: min={first_shots} max={first_shots}")
    print("time_taken fields: unavailable")
    preview = list(first_counts.items())[:5] if first_counts else []
    if preview:
        print(f"first experiment counts preview: {preview}")
    else:
        print("first experiment counts preview: unavailable")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 analysis/summarize_capture.py <capture.json>")

    path = Path(sys.argv[1])
    data = load_capture(path)
    provider, backend_name, capture_mode, raw_result = unwrap_capture(data)

    print(f"file: {path}")
    print(f"provider: {provider}")
    print(f"backend: {backend_name}")
    if capture_mode:
        print(f"capture_mode: {capture_mode}")

    if raw_result.get("results") is not None:
        summarize_qiskit_result(raw_result)
    elif raw_result.get("experiments") is not None:
        summarize_braket_local_result(raw_result)
    else:
        print("top-level success: unavailable")
        print("experiments saved: unavailable")
        print("shots per experiment: unavailable")
        print("time_taken fields: unavailable")
        print("first experiment counts preview: unavailable")

    if provider == "aer":
        print("classification: local simulator artifact")
        print("note: useful for pipeline checks, not enough on its own for a physical 0.67 Hz claim")
    elif provider == "braket-local":
        print("classification: local simulator artifact")
        print("note: useful for cross-provider tooling checks, not enough on its own for a physical 0.67 Hz claim")
    else:
        print("classification: backend capture")
        print("note: still requires repeated collection and separate non-injected analysis")


if __name__ == "__main__":
    main()
