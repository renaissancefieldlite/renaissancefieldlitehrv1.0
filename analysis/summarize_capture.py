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


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 analysis/summarize_capture.py <capture.json>")

    path = Path(sys.argv[1])
    data = load_capture(path)
    results = data.get("results", [])
    backend_name = data.get("backend_name", "unknown")
    success = data.get("success")

    print(f"file: {path}")
    print(f"backend: {backend_name}")
    print(f"top-level success: {success}")
    print(f"experiments saved: {len(results)}")

    shot_values = [entry.get("shots") for entry in results if isinstance(entry, dict)]
    time_values = [entry.get("time_taken") for entry in results if isinstance(entry, dict) and entry.get("time_taken") is not None]

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

    if backend_name == "aer_simulator":
        print("classification: local simulator artifact")
        print("note: useful for pipeline checks, not enough on its own for a physical 0.67 Hz claim")
    else:
        print("classification: backend capture")
        print("note: still requires repeated collection and separate non-injected analysis")


if __name__ == "__main__":
    main()
