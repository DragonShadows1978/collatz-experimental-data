#!/usr/bin/env python3
"""Convert Lock 3 JSONL progress events into live CSV and latest-status JSON."""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path


FIELDS = [
    "event",
    "engine",
    "C",
    "residue_mod_power",
    "target_depth",
    "depth",
    "completed_depth",
    "merged_state_count",
    "valid_residue_count",
    "valid_from_1_count",
    "exact_depth_valid1",
    "terminal_1_compatible_signature_count",
    "live_valid1_count",
    "valid1_shadow_birth_count",
    "valid1_shadow_death_count",
    "max_valid1_shadow_lifetime",
    "valid1_shadow_persisted_from_previous",
    "live_valid1_lineage_count",
    "valid1_lineage_birth_count",
    "valid1_lineage_death_count",
    "max_valid1_lineage_lifetime",
    "lineage_lifetime_histogram",
    "ever_seen_valid1",
    "first_valid1_depth",
    "final_live_valid1_count",
    "final_live_valid1_lineage_count",
    "final_valid_from_1_count",
    "final_compatible_signatures",
    "checkpoint_path",
    "checkpoint_size_bytes",
    "current_rss_kb",
    "peak_rss_kb",
    "elapsed_sec",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--latest", required=True, type=Path)
    parser.add_argument("--follow", action="store_true")
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    return parser.parse_args()


def normalize(event: dict) -> dict:
    return {field: event.get(field, "") for field in FIELDS}


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def append_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    ensure_parent(path)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        for row in rows:
            writer.writerow(normalize(row))


def write_latest(path: Path, event: dict) -> None:
    ensure_parent(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(event, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def process_available(handle, csv_path: Path, latest_path: Path) -> bool:
    rows = []
    latest = None
    while True:
        line = handle.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        event = json.loads(line)
        rows.append(event)
        latest = event
    append_csv(csv_path, rows)
    if latest is not None:
        write_latest(latest_path, latest)
    return bool(rows)


def main() -> int:
    args = parse_args()
    while args.follow and not args.input.exists():
        time.sleep(args.poll_seconds)
    with args.input.open("r", encoding="utf-8") as handle:
        while True:
            changed = process_available(handle, args.csv, args.latest)
            if not args.follow:
                break
            if not changed:
                time.sleep(args.poll_seconds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
