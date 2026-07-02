#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


RUN_RE = re.compile(r"lock3_C(?P<C>\d+)_N(?P<N>\d+)_(?P<kind>.+)")


def load_json(path: Path) -> dict[str, Any]:
    with path.open() as handle:
        return json.load(handle)


def checkpoint_size(run_dir: Path) -> int:
    sizes = [path.stat().st_size for path in run_dir.glob("*.checkpoint.bin")]
    return max(sizes, default=0)


def final_csv_row(run_dir: Path, c: int) -> dict[str, str]:
    path = run_dir / f"lock3_census_C{c}.csv"
    if not path.exists():
        return {}
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    return rows[-1] if rows else {}


def classify(summary: dict[str, Any]) -> str:
    final_valid = int(summary.get("valid_from_1_count", 0))
    ever = bool(summary.get("ever_seen_valid1", False))
    compatible = int(summary.get("terminal_1_compatible_signature_count", 0))
    if final_valid == 0 and compatible == 0 and not ever:
        return "clean"
    if final_valid == 0 and ever:
        return "transient"
    return "persistent"


def row_for_run(run_dir: Path) -> dict[str, Any] | None:
    match = RUN_RE.match(run_dir.name)
    if not match:
        return None
    summary_paths = sorted(run_dir.glob("lock3_summary_C*.json"))
    if not summary_paths:
        return None
    summary = load_json(summary_paths[-1])
    c = int(summary.get("C", match.group("C")))
    final_row = final_csv_row(run_dir, c)
    transients = summary.get("transient_valid1_depths", [])
    alignment = summary.get("valid1_convergent_alignment", [])
    multiples_53 = sum(1 for item in alignment if item.get("is_multiple_of_53"))
    return {
        "run_dir": str(run_dir),
        "C": c,
        "depth": int(summary.get("max_depth", match.group("N"))),
        "m": int(summary.get("residue_mod_power", 0)),
        "residue_modulus": int(summary.get("residue_modulus", 1)),
        "classification": classify(summary),
        "valid_from_1_count": int(summary.get("valid_from_1_count", 0)),
        "ever_seen_valid1": bool(summary.get("ever_seen_valid1", False)),
        "terminal_1_compatible_signature_count": int(
            summary.get("terminal_1_compatible_signature_count", 0)
        ),
        "merged_state_count": int(summary.get("merged_state_count", 0)),
        "valid_residue_count": int(summary.get("valid_residue_count", 0)),
        "rho_lift_count": int(summary.get("rho_lift_count", 0)),
        "longest_plateau": int(summary.get("longest_plateau", 0)),
        "max_rho_bit_length": int(summary.get("max_rho_bit_length", 0)),
        "transient_depth_count": len(transients),
        "transient_depths": ";".join(str(depth) for depth in transients),
        "transient_multiples_of_53": multiples_53,
        "checkpoint_bytes": checkpoint_size(run_dir),
        "census_rows": final_row.get("depth", ""),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "run_dir",
        "C",
        "depth",
        "m",
        "classification",
        "valid_from_1_count",
        "ever_seen_valid1",
        "terminal_1_compatible_signature_count",
        "merged_state_count",
        "valid_residue_count",
        "rho_lift_count",
        "longest_plateau",
        "max_rho_bit_length",
        "transient_depth_count",
        "transient_multiples_of_53",
        "checkpoint_bytes",
        "residue_modulus",
        "transient_depths",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def threshold_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[int(row["C"])].append(row)
    out = []
    for c, c_rows in sorted(grouped.items()):
        full_rows = [row for row in c_rows if row["m"] > 0 and row["depth"] >= 250]
        clean = sorted(
            (row for row in full_rows if row["classification"] == "clean"),
            key=lambda r: (r["m"], r["depth"]),
        )
        dirty = sorted(
            (row for row in full_rows if row["classification"] != "clean"),
            key=lambda r: (r["m"], r["depth"]),
        )
        probes = sorted(
            (row for row in c_rows if row["m"] > 0 and row["depth"] < 250),
            key=lambda r: (r["m"], r["depth"]),
        )
        probe_text = ";".join(
            f"m{row['m']}/N{row['depth']}/{row['classification']}" for row in probes
        )
        out.append(
            {
                "C": c,
                "first_clean_m": clean[0]["m"] if clean else "",
                "first_clean_depth": clean[0]["depth"] if clean else "",
                "max_dirty_m": max((row["m"] for row in dirty), default=""),
                "max_completed_m": max((row["m"] for row in full_rows), default=""),
                "runs": len(full_rows),
                "probes": probe_text,
                "status": "bracketed" if clean and dirty else ("clean-only" if clean else "open"),
            }
        )
    return out


def write_threshold_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "C",
        "first_clean_m",
        "first_clean_depth",
        "max_dirty_m",
        "max_completed_m",
        "runs",
        "status",
        "probes",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_svg(path: Path, rows: list[dict[str, Any]]) -> None:
    points = [row for row in rows if row["m"] > 0 and row["depth"] >= 20]
    width = 1000
    height = 620
    margin = 70
    max_c = max((row["C"] for row in points), default=8)
    max_m = max((row["m"] for row in points), default=20)
    min_m = min((row["m"] for row in points), default=8)
    colors = {"clean": "#147d3f", "transient": "#d18f00", "persistent": "#b3261e"}

    def x_for(c: int) -> float:
        return margin + (c / max(1, max_c)) * (width - 2 * margin)

    def y_for(m: int) -> float:
        span = max(1, max_m - min_m)
        return height - margin - ((m - min_m) / span) * (height - 2 * margin)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="50" y="36" font-family="sans-serif" font-size="24" fill="#111">Lock 3 Collapse Threshold Runs</text>',
        f'<line x1="{margin}" y1="{height-margin}" x2="{width-margin}" y2="{height-margin}" stroke="#333"/>',
        f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height-margin}" stroke="#333"/>',
    ]
    for c in range(0, max_c + 1):
        x = x_for(c)
        parts.append(f'<line x1="{x:.1f}" y1="{height-margin}" x2="{x:.1f}" y2="{height-margin+6}" stroke="#333"/>')
        parts.append(f'<text x="{x:.1f}" y="{height-margin+28}" text-anchor="middle" font-family="sans-serif" font-size="13">C={c}</text>')
    for m in range(min_m, max_m + 1, 2):
        y = y_for(m)
        parts.append(f'<line x1="{margin-6}" y1="{y:.1f}" x2="{margin}" y2="{y:.1f}" stroke="#333"/>')
        parts.append(f'<text x="{margin-12}" y="{y+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="13">m={m}</text>')
        parts.append(f'<line x1="{margin}" y1="{y:.1f}" x2="{width-margin}" y2="{y:.1f}" stroke="#eee"/>')
    jitter: dict[tuple[int, int], int] = defaultdict(int)
    for row in sorted(points, key=lambda r: (r["C"], r["m"], r["depth"])):
        key = (row["C"], row["m"])
        offset = (jitter[key] - 1) * 9
        jitter[key] += 1
        x = x_for(row["C"]) + offset
        y = y_for(row["m"])
        color = colors[row["classification"]]
        radius = 7 if row["depth"] >= 250 else 4
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{color}" opacity="0.88"/>')
        parts.append(
            f'<title>C={row["C"]} m={row["m"]} depth={row["depth"]} {row["classification"]} merged={row["merged_state_count"]}</title>'
        )
    legend_y = 70
    for idx, (label, color) in enumerate(colors.items()):
        x = width - 240
        y = legend_y + idx * 24
        parts.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{color}"/>')
        parts.append(f'<text x="{x+16}" y="{y+5}" font-family="sans-serif" font-size="14">{label}</text>')
    parts.append('</svg>')
    path.write_text("\n".join(parts) + "\n")


def write_markdown(path: Path, rows: list[dict[str, Any]], thresholds: list[dict[str, Any]]) -> None:
    lines = [
        "# Lock 3 Collapse Curve",
        "",
        "Generated from completed `lock3_summary_C*.json` files.",
        "",
        "## Threshold Summary",
        "",
        "| C | first clean m | first clean depth | max dirty m | max completed m | status |",
        "| ---: | ---: | ---: | ---: | ---: | :--- |",
    ]
    for row in thresholds:
        lines.append(
            f"| {row['C']} | {row['first_clean_m']} | {row['first_clean_depth']} | {row['max_dirty_m']} | {row['max_completed_m']} | {row['status']} |"
        )
    lines.extend(
        [
            "",
            "Low-depth probes are excluded from threshold calls:",
            "",
            "| C | probes |",
            "| ---: | :--- |",
        ]
    )
    for row in thresholds:
        if row.get("probes"):
            lines.append(f"| {row['C']} | {row['probes']} |")
    lines.extend(
        [
            "",
            "## Completed Runs",
            "",
            "| C | depth | m | class | final valid1 | ever seen | compatible signatures | merged states | transient depths | checkpoint |",
            "| ---: | ---: | ---: | :--- | ---: | :--- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in sorted(rows, key=lambda r: (r["C"], r["m"], r["depth"])):
        lines.append(
            f"| {row['C']} | {row['depth']} | {row['m']} | {row['classification']} | {row['valid_from_1_count']} | {row['ever_seen_valid1']} | {row['terminal_1_compatible_signature_count']} | {row['merged_state_count']} | {row['transient_depth_count']} | {row['checkpoint_bytes']} |"
        )
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    root = Path("data/runs")
    out_dir = root / "lock3_curve"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for run_dir in root.glob("lock3_C*_N*"):
        if run_dir.is_dir():
            row = row_for_run(run_dir)
            if row is not None:
                rows.append(row)
    rows.sort(key=lambda row: (row["C"], row["m"], row["depth"], row["run_dir"]))
    thresholds = threshold_rows(rows)
    write_csv(out_dir / "lock3_collapse_curve_runs.csv", rows)
    write_threshold_csv(out_dir / "lock3_collapse_thresholds.csv", thresholds)
    write_svg(out_dir / "lock3_collapse_curve.svg", rows)
    write_markdown(out_dir / "lock3_collapse_curve.md", rows, thresholds)
    print(f"wrote {out_dir / 'lock3_collapse_curve_runs.csv'}")
    print(f"wrote {out_dir / 'lock3_collapse_thresholds.csv'}")
    print(f"wrote {out_dir / 'lock3_collapse_curve.svg'}")
    print(f"wrote {out_dir / 'lock3_collapse_curve.md'}")


if __name__ == "__main__":
    main()
