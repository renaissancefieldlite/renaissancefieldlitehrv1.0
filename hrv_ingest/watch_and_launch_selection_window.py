#!/usr/bin/env python3
"""Wait for a batch manifest to finish, then launch selection_window_100."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def wait_for_finish(path: Path, poll_seconds: float) -> dict:
    while True:
        if path.exists():
            payload = load_manifest(path)
            if payload.get("finished_at_utc"):
                return payload
        time.sleep(poll_seconds)


def build_launch_command(args: argparse.Namespace) -> list[str]:
    cmd = [
        sys.executable,
        str(Path(__file__).with_name("repeated_capture.py")),
        "--provider",
        "ibm",
        "--backend",
        args.backend,
        "--repeats",
        str(args.repeats),
        "--circuits",
        str(args.circuits),
        "--shots",
        str(args.shots),
        "--label",
        args.label,
        "--condition",
        "selection_window",
        "--session-mode",
        args.session_mode,
        "--session-reference",
        args.session_reference,
        "--selection-window-seconds",
        str(args.selection_window_seconds),
        "--session-notes",
        args.session_notes,
    ]
    if args.scrape_job_ids:
        cmd.append("--scrape-job-ids")
        cmd.extend(["--job-scrape-poll-seconds", str(args.job_scrape_poll_seconds)])
    return cmd


def main() -> None:
    parser = argparse.ArgumentParser(description="Wait for synced_100 to finish, then launch selection_window_100.")
    parser.add_argument("--watch-manifest", required=True)
    parser.add_argument("--backend", default="ibm_fez")
    parser.add_argument("--repeats", type=int, default=100)
    parser.add_argument("--circuits", type=int, default=1)
    parser.add_argument("--shots", type=int, default=32)
    parser.add_argument("--label", default="selection_window_100")
    parser.add_argument("--session-mode", default="timed_window")
    parser.add_argument("--session-reference", default="architect_d_selection_window")
    parser.add_argument("--selection-window-seconds", type=float, default=1.49)
    parser.add_argument(
        "--session-notes",
        default="selection window condition launched automatically after synced_100 completion",
    )
    parser.add_argument("--poll-seconds", type=float, default=30.0)
    parser.add_argument(
        "--scrape-job-ids",
        action="store_true",
        help="Also launch live job-id scraping for the selection-window batch.",
    )
    parser.add_argument(
        "--job-scrape-poll-seconds",
        type=float,
        default=5.0,
        help="Polling interval for the live job-id scraper passed to repeated_capture.py.",
    )
    args = parser.parse_args()

    manifest_path = Path(args.watch_manifest).resolve()
    print(f"[watcher] waiting for {manifest_path}")
    wait_for_finish(manifest_path, args.poll_seconds)
    cmd = build_launch_command(args)
    print(f"[watcher] launching {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
