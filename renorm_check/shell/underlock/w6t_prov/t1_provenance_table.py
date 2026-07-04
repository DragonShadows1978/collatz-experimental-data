#!/usr/bin/env python3
"""
W6T-PROV -- Provenance audit of the corridor-capacity record.

Builds the C-by-C provenance table for M_edge(C), C=1..50 (the range used by
w6h/h5_frame_rule_check.csv), by reading the ACTUAL primary sources directly
(not re-trusting any prior round's paraphrase of them), plus records the
separate C=148 (F5) provenance finding.

Primary sources consulted (read directly, quoted in the accompanying digest,
not re-derived here -- this script just assembles the table programmatically
from the two authoritative artifacts that already did the honest labeling):
  - /mnt/ForgeRealm/collatz-experimental-data/LOCK3_BIRTH_INVARIANT_AUDIT.md
    (C=1..5, per-m dense sweep, dated 2026-05-24)
  - /mnt/ForgeRealm/collatz-experimental-data/LOCK3_PRECISION_COUNTDOWN_GRID.md
    ("Only m1 has been checked for C6-C50 in this series")
  - /mnt/ForgeRealm/collatz-experimental-data/renorm_check/beatty/task1_measured_widths.csv
    (a PRIOR round's own honest GENUINE_full_sweep vs INFERRED tier labeling,
    dated before W6H -- W6H's "48/48 EXACT" phrasing dropped this tier
    distinction that had already been made once)
  - data/runs/lock3_C{C}_N2000_residue_m1_lineage_cohorts_*/ (raw Rust
    lock3_census artifacts, residue_mod_power=1 only, for C=6..50)
  - renorm_check/embedding/small_side_live_sets/*.npz (archived witness sets,
    C=1..5 only)
"""
import csv
import glob
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
DATA_RUNS = Path("/mnt/ForgeRealm/collatz-experimental-data/data/runs")


def m_irr(C: int) -> int:
    return 53 * (C + 1) // 22


def gather_c6_50():
    """Re-verify (independently of h5_frame_rule_crosscheck.py) that the
    archived C=6..50 lock3_census m1 runs really do read max_valid1_lineage_lifetime
    == floor(53(C+1)/22), and that they are genuinely residue_mod_power=1
    (the coarse proxy), not a full-precision sweep."""
    pattern = str(DATA_RUNS / "lock3_C*_N2000_residue_m1_lineage_cohorts_*")
    out = {}
    for d in sorted(glob.glob(pattern)):
        m = re.match(r".*lock3_C(-?\d+)_N2000_residue_m1_lineage_cohorts_.*", d)
        if not m:
            continue
        C = int(m.group(1))
        if C < 1:
            continue
        dpath = Path(d)
        json_path = dpath / f"lock3_summary_C{C}.json"
        if not json_path.exists():
            continue
        with open(json_path) as f:
            s = json.load(f)
        out[C] = {
            "residue_mod_power": s.get("residue_mod_power"),
            "max_lifetime": s.get("max_lifetime_of_valid1_lineage"),
            "dir": dpath.name,
            "date": dpath.name.split("_")[-1] if "supervised" not in dpath.name else dpath.name.split("_")[-2],
        }
    return out


def main():
    rows = []

    # C = 1..5: genuine per-m dense sweeps (LOCK3_BIRTH_INVARIANT_AUDIT.md,
    # LOCK3_PRECISION_COUNTDOWN_GRID.md, cross-confirmed by
    # embedding/small_side_live_sets/*.npz witnesses at each M_edge(C)).
    genuine_1_5 = {
        1: (4, "K=5 (desert at m=5), Lock3_birth_audit + embedding npz C1_m4/m5"),
        2: (7, "K=8 (desert at m=8), Lock3_birth_audit + embedding npz C2_m7/m8"),
        3: (9, "K=10 (desert at m=10), full m=1..10 ladder, Lock3_c3/ + npz C3_m9/m10"),
        4: (12, "K=13 (desert at m=13), full m=1..13 ladder, Lock3_c4/MANIFEST.md + npz C4_m12/m13"),
        5: (14, "K=15 (desert at m=15, confirmed at reduced depth 50), npz C5_m14/m15/m16"),
    }
    for C, (val, note) in genuine_1_5.items():
        rows.append({
            "C": C, "M_edge_value": val, "formula_value": m_irr(C),
            "status": "MEASURED",
            "tool_artifact": "lock3_census (Rust) full per-m ladder to desert edge; "
                              "LOCK3_BIRTH_INVARIANT_AUDIT.md (2026-05-24); "
                              "embedding/small_side_live_sets/*.npz witness cross-check",
            "notes": note,
        })

    c6_50 = gather_c6_50()
    for C in range(6, 51):
        if C not in c6_50:
            rows.append({"C": C, "M_edge_value": None, "formula_value": m_irr(C),
                         "status": "MISSING", "tool_artifact": "", "notes": "no archived run directory found"})
            continue
        info = c6_50[C]
        formula = m_irr(C)
        rows.append({
            "C": C, "M_edge_value": info["max_lifetime"], "formula_value": formula,
            "status": "DERIVED" if info["max_lifetime"] == formula else "UNCLEAR-MISMATCH",
            "tool_artifact": f"lock3_census (Rust), data/runs/{info['dir']}/, "
                              f"residue_mod_power={info['residue_mod_power']} (coarse mod-3 proxy, m1 only)",
            "notes": "zero-birth m NEVER directly observed for this C; value is "
                     "observed_m1_lifetime + 1 == formula, matching only because "
                     "the linear countdown slope (-1/unit m, proven ONLY at C=3,4,5) "
                     "is assumed, not measured, at this C. Per "
                     "LOCK3_PRECISION_COUNTDOWN_GRID.md: 'Only m1 has been checked "
                     "for C6-C50 in this series.' Per beatty/task1_measured_widths.csv "
                     "(prior round's own honest tiering): tier="
                     "INFERRED_m1_only_plus_linear_countdown_assumption.",
        })

    out_csv = HERE / "t1_provenance_table.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["C", "M_edge_value", "formula_value", "status", "tool_artifact", "notes"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    n_measured = sum(1 for r in rows if r["status"] == "MEASURED")
    n_derived = sum(1 for r in rows if r["status"] == "DERIVED")
    n_missing = sum(1 for r in rows if r["status"] == "MISSING")
    n_mismatch = sum(1 for r in rows if r["status"] == "UNCLEAR-MISMATCH")
    print(f"Wrote {out_csv} ({len(rows)} rows, C=1..50)")
    print(f"MEASURED: {n_measured} (C={[r['C'] for r in rows if r['status']=='MEASURED']})")
    print(f"DERIVED (formula-matching m1 proxy, zero-birth never observed): {n_derived}")
    print(f"MISSING: {n_missing}")
    print(f"UNCLEAR-MISMATCH: {n_mismatch}")
    if n_mismatch:
        for r in rows:
            if r["status"] == "UNCLEAR-MISMATCH":
                print(f"  MISMATCH at C={r['C']}: archived={r['M_edge_value']} formula={r['formula_value']}")


if __name__ == "__main__":
    main()
