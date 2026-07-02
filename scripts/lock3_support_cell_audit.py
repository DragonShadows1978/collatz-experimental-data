#!/usr/bin/env python3
import csv
import json
from pathlib import Path


ROOT = Path("/mnt/ForgeRealm/collatz-experimental-data")
RUNS = ROOT / "data" / "runs"
OUT_DIR = ROOT / "Lock3_support_cell_audit"

GRID = [
    (3, 8),
    (3, 9),
    (3, 10),
    (4, 11),
    (4, 12),
    (4, 13),
    (5, 13),
    (5, 14),
    (5, 15),
]

THIN_PHASES = [
    0,
    2,
    4,
    7,
    9,
    12,
    14,
    16,
    19,
    21,
    24,
    26,
    28,
    31,
    33,
    36,
    38,
    40,
    43,
    45,
    48,
    50,
]


def choose_summary(c: int, m: int) -> Path:
    paths = sorted(
        RUNS.glob(f"lock3_C{c}_N*_residue_m{m}*/lock3_summary_C{c}.json"),
        key=lambda p: (
            json.loads(p.read_text()).get("completed_depth")
            or json.loads(p.read_text()).get("max_depth")
            or 0,
            p.stat().st_mtime,
        ),
        reverse=True,
    )
    if not paths:
        raise FileNotFoundError(f"missing summary for C={c} m={m}")
    return paths[0]


def formula(c: int, value: int) -> str:
    correction = value - 3 * c
    if correction == 0:
        return "3C"
    if correction > 0:
        return f"3C+{correction}"
    return f"3C{correction}"


def support_cells(c: int, m: int):
    cells = []
    for layer in range(1, m + 1):
        for thin_idx, thin_phase in enumerate(THIN_PHASES):
            support_index = (layer - 1) * len(THIN_PHASES) + thin_idx
            cells.append(
                {
                    "precision_layer": layer,
                    "thin_slot_index": thin_idx,
                    "thin_phase_mod_53": thin_phase,
                    "phase_mod_53": support_index % 53,
                    "deficit": support_index // 53,
                }
            )
    return cells


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    audit_path = OUT_DIR / "lock3_support_cell_audit.csv"
    detail_path = OUT_DIR / "lock3_support_cell_detail.csv"
    summary_path = OUT_DIR / "lock3_support_cell_summary.json"

    audit_rows = []
    detail_rows = []
    failures = []

    for c, m in GRID:
        summary_file = choose_summary(c, m)
        summary = json.loads(summary_file.read_text())
        depth = summary.get("completed_depth") or summary.get("max_depth")
        observed_terminal_compatible = bool(summary.get("ever_seen_valid1"))
        expected_min = 22 * m
        capacity = 53 * (c + 1)
        cells = support_cells(c, m)
        unique_cells = {(cell["phase_mod_53"], cell["deficit"]) for cell in cells}
        support_cell_count = len(cells)
        unique_support_cell_count = len(unique_cells)
        forbidden_reuse_count = support_cell_count - unique_support_cell_count
        exceeds_capacity = expected_min > capacity
        capacity_condition_pass = unique_support_cell_count <= capacity
        no_forbidden_reuse = forbidden_reuse_count == 0
        theorem_observation_pass = (
            not observed_terminal_compatible if exceeds_capacity else observed_terminal_compatible
        )
        support_cell_count_pass = support_cell_count >= expected_min
        audit_pass = (
            theorem_observation_pass
            and support_cell_count_pass
            and no_forbidden_reuse
            and (exceeds_capacity or capacity_condition_pass)
        )
        lineage = (
            "none"
            if not observed_terminal_compatible
            else "aggregate_terminal_compatible_support"
        )
        row = {
            "C": c,
            "m": m,
            "depth": depth,
            "lineage_cohort": lineage,
            "support_cell_count": support_cell_count,
            "unique_support_cell_count": unique_support_cell_count,
            "expected_min": expected_min,
            "capacity": capacity,
            "cutoff_floor": capacity // 22,
            "cutoff_formula": formula(c, capacity // 22),
            "observed_terminal_compatible": observed_terminal_compatible,
            "expected_desert": exceeds_capacity,
            "support_cell_count_pass": support_cell_count_pass,
            "capacity_condition_pass": capacity_condition_pass,
            "observation_condition_pass": theorem_observation_pass,
            "forbidden_reuse_count": forbidden_reuse_count,
            "source_summary": str(summary_file.relative_to(ROOT)),
            "pass_fail": "PASS" if audit_pass else "FAIL",
        }
        audit_rows.append(row)
        if row["pass_fail"] != "PASS":
            failures.append(row)

        for cell in cells:
            detail_rows.append(
                {
                    "C": c,
                    "m": m,
                    "depth": depth,
                    "lineage_cohort": lineage,
                    **cell,
                }
            )

    with audit_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(audit_rows[0].keys()))
        writer.writeheader()
        writer.writerows(audit_rows)

    with detail_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(detail_rows[0].keys()))
        writer.writeheader()
        writer.writerows(detail_rows)

    summary = {
        "thin_phase_count": len(THIN_PHASES),
        "thin_phases_mod_53": THIN_PHASES,
        "capacity_formula": "53(C+1)",
        "expected_min_formula": "22m",
        "critical_theorem_test": "If 22m > 53(C+1), no terminal-compatible lineage should exist.",
        "rows": len(audit_rows),
        "passes": sum(1 for row in audit_rows if row["pass_fail"] == "PASS"),
        "failures": len(failures),
        "failure_rows": failures,
        "audit_csv": str(audit_path.relative_to(ROOT)),
        "detail_csv": str(detail_path.relative_to(ROOT)),
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(audit_path)
    print(summary_path)


if __name__ == "__main__":
    main()
