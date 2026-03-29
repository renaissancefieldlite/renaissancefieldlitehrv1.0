#!/usr/bin/env python3
"""Run repeated capture batches for local or backend comparison."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hardware_ingest import DEFAULT_OUT_DIR, grab_error_timestamps


DEFAULT_BATCH_DIR = Path(__file__).resolve().parents[1] / "data" / "batches"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_manifest(manifest_path: Path, payload: dict[str, Any]) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def launch_job_scraper(
    *,
    manifest_path: Path,
    batch_dir: Path,
    output_path: str | None,
    poll_seconds: float,
) -> subprocess.Popen[str]:
    scraper_script = Path(__file__).with_name("watch_batch_job_ids.py")
    resolved_output = (
        Path(output_path).resolve()
        if output_path
        else (batch_dir / f"{manifest_path.stem}_job_ids.json").resolve()
    )
    cmd = [
        sys.executable,
        str(scraper_script),
        "--watch-manifest",
        str(manifest_path.resolve()),
        "--output",
        str(resolved_output),
        "--poll-seconds",
        str(poll_seconds),
    ]
    print(f"[batch] launching job scraper → {' '.join(cmd)}")
    return subprocess.Popen(cmd, text=True)


def run_batch(
    *,
    provider: str,
    backend: str,
    repeats: int,
    circuits: int,
    shots: int,
    out_dir: Path,
    batch_dir: Path,
    pause_seconds: float,
    ibm_channel: str | None,
    ibm_token: str | None,
    ibm_instance: str | None,
    ibm_url: str | None,
    label: str | None,
    condition: str | None,
    session_mode: str | None,
    session_reference: str | None,
    selection_window_seconds: float | None,
    session_notes: str | None,
    scrape_job_ids: bool,
    job_scrape_output: str | None,
    job_scrape_poll_seconds: float,
) -> dict[str, Any]:
    capture_files: list[str] = []
    started_at = utc_now_iso()
    timestamp = int(time.time())
    safe_label = None
    if label:
        safe_label = label.lower().replace(" ", "_")

    manifest_name = f"{provider}_{backend}_{timestamp}.json"
    if safe_label:
        manifest_name = f"{provider}_{backend}_{safe_label}_{timestamp}.json"
    manifest_path = batch_dir / manifest_name

    payload = {
        "schema_version": "rfl.capture_batch.v2",
        "provider": provider,
        "backend_name": backend,
        "label": label,
        "condition": condition,
        "session_mode": session_mode,
        "session_reference": session_reference,
        "selection_window_seconds": selection_window_seconds,
        "session_notes": session_notes,
        "repeats": repeats,
        "circuits": circuits,
        "shots": shots,
        "started_at_utc": started_at,
        "updated_at_utc": started_at,
        "finished_at_utc": None,
        "completed_repeats": 0,
        "capture_files": capture_files,
    }
    write_manifest(manifest_path, payload)
    scraper_process: subprocess.Popen[str] | None = None
    if scrape_job_ids:
        scraper_process = launch_job_scraper(
            manifest_path=manifest_path,
            batch_dir=batch_dir,
            output_path=job_scrape_output,
            poll_seconds=job_scrape_poll_seconds,
        )

    try:
        for index in range(repeats):
            capture_path = grab_error_timestamps(
                provider=provider,
                backend_name=backend,
                circuits=circuits,
                shots=shots,
                out_dir=out_dir,
                ibm_channel=ibm_channel,
                ibm_token=ibm_token,
                ibm_instance=ibm_instance,
                ibm_url=ibm_url,
            )
            capture_files.append(capture_path)
            payload["completed_repeats"] = len(capture_files)
            payload["updated_at_utc"] = utc_now_iso()
            write_manifest(manifest_path, payload)
            if index < repeats - 1 and pause_seconds > 0:
                time.sleep(pause_seconds)
    finally:
        finished_at = utc_now_iso()
        payload["updated_at_utc"] = finished_at
        payload["finished_at_utc"] = finished_at
        write_manifest(manifest_path, payload)
        if scraper_process:
            try:
                scraper_process.wait(timeout=max(10.0, job_scrape_poll_seconds * 3.0))
            except subprocess.TimeoutExpired:
                scraper_process.terminate()
        print(f"✓ batch manifest → {manifest_path}")

    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run repeated capture batches for HRV1.0.")
    parser.add_argument("--provider", required=True, choices=["aer", "ibm", "braket-local", "external-rig"])
    parser.add_argument("--backend", required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--circuits", type=int, default=1)
    parser.add_argument("--shots", type=int, default=32)
    parser.add_argument("--pause-seconds", type=float, default=0.0)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--batch-dir", default=str(DEFAULT_BATCH_DIR))
    parser.add_argument("--ibm-channel")
    parser.add_argument("--ibm-token")
    parser.add_argument("--ibm-instance")
    parser.add_argument("--ibm-url")
    parser.add_argument("--label")
    parser.add_argument("--condition")
    parser.add_argument("--session-mode")
    parser.add_argument("--session-reference")
    parser.add_argument("--selection-window-seconds", type=float)
    parser.add_argument("--session-notes")
    parser.add_argument(
        "--scrape-job-ids",
        action="store_true",
        help="Launch a watcher that scrapes capture/job IDs into a sidecar report while the batch is running.",
    )
    parser.add_argument(
        "--job-scrape-output",
        help="Optional output path for the sidecar job-id scrape report.",
    )
    parser.add_argument(
        "--job-scrape-poll-seconds",
        type=float,
        default=5.0,
        help="Polling interval for the live job-id scraper.",
    )
    args = parser.parse_args()

    run_batch(
        provider=args.provider,
        backend=args.backend,
        repeats=args.repeats,
        circuits=args.circuits,
        shots=args.shots,
        out_dir=Path(args.out_dir),
        batch_dir=Path(args.batch_dir),
        pause_seconds=args.pause_seconds,
        ibm_channel=args.ibm_channel,
        ibm_token=args.ibm_token,
        ibm_instance=args.ibm_instance,
        ibm_url=args.ibm_url,
        label=args.label,
        condition=args.condition,
        session_mode=args.session_mode,
        session_reference=args.session_reference,
        selection_window_seconds=args.selection_window_seconds,
        session_notes=args.session_notes,
        scrape_job_ids=args.scrape_job_ids,
        job_scrape_output=args.job_scrape_output,
        job_scrape_poll_seconds=args.job_scrape_poll_seconds,
    )


if __name__ == "__main__":
    main()
