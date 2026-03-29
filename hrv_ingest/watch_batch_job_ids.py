#!/usr/bin/env python3
"""Watch a batch manifest and scrape capture/job identifiers as files appear."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_capture_job_entry(capture_path: Path) -> dict[str, Any]:
    payload = load_json(capture_path)
    return {
        "capture_path": str(capture_path),
        "provider": payload.get("provider"),
        "backend_name": payload.get("backend_name"),
        "created_at_utc": payload.get("created_at_utc"),
        "job_id": payload.get("job_id"),
        "shots": payload.get("shots"),
        "capture_mode": payload.get("capture_mode"),
    }


def write_report(
    *,
    output_path: Path,
    manifest_path: Path,
    manifest_payload: dict[str, Any],
    jobs: list[dict[str, Any]],
) -> None:
    report = {
        "schema_version": "rfl.batch_job_scrape.v1",
        "manifest_path": str(manifest_path),
        "provider": manifest_payload.get("provider"),
        "backend_name": manifest_payload.get("backend_name"),
        "label": manifest_payload.get("label"),
        "condition": manifest_payload.get("condition"),
        "started_at_utc": manifest_payload.get("started_at_utc"),
        "updated_at_utc": manifest_payload.get("updated_at_utc"),
        "finished_at_utc": manifest_payload.get("finished_at_utc"),
        "completed_repeats": manifest_payload.get("completed_repeats"),
        "jobs": jobs,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def watch_manifest(manifest_path: Path, output_path: Path, poll_seconds: float) -> None:
    seen_capture_paths: set[str] = set()
    jobs: list[dict[str, Any]] = []

    while True:
        if not manifest_path.exists():
            time.sleep(poll_seconds)
            continue

        manifest_payload = load_json(manifest_path)
        capture_files = manifest_payload.get("capture_files", [])
        for capture_file in capture_files:
            if capture_file in seen_capture_paths:
                continue

            capture_path = Path(capture_file).resolve()
            if not capture_path.exists():
                continue

            entry = extract_capture_job_entry(capture_path)
            jobs.append(entry)
            seen_capture_paths.add(capture_file)
            job_id = entry.get("job_id") or "no-job-id"
            print(f"[job-scrape] {job_id} ← {capture_path.name}")

        write_report(
            output_path=output_path,
            manifest_path=manifest_path,
            manifest_payload=manifest_payload,
            jobs=jobs,
        )

        if manifest_payload.get("finished_at_utc"):
            break

        time.sleep(poll_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="Watch a batch manifest and scrape live capture/job identifiers.")
    parser.add_argument("--watch-manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    args = parser.parse_args()

    watch_manifest(
        manifest_path=Path(args.watch_manifest).resolve(),
        output_path=Path(args.output).resolve(),
        poll_seconds=args.poll_seconds,
    )


if __name__ == "__main__":
    main()
