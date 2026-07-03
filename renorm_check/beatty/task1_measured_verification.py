#!/usr/bin/env python3
"""
Task 1: locate MEASURED (not formula-derived) capacity values and check them against
floor(53(C+1)/22), plus check exact periodicity M_edge(C+22)-M_edge(C)=53 in the
MEASURED values where both widths exist.

PROVENANCE (see accompanying prose report for full detail):

  - COLLATZ_PROOF.md line ~230 claims: "Verified by Certificate 1: the formula
    matches all 48 independently measured corridor widths (C = 1 through 50)
    without exception."

  - The actual source of the "48" figure is
    /mnt/ForgeRealm/collatz-experimental-data/LOCK3_PRECISION_COUNTDOWN_GRID.md,
    backed by data/runs/lock3_C{3..50}_N2000_residue_m1_lineage_cohorts_* (and
    equivalent) run directories -- 48 distinct C values (C=3..50 inclusive).

  - Of those 48:
      * C = 3, 4, 5 (3 widths) are GENUINE full countdown-ladder measurements:
        m was swept from 1 up through the point where max_lifetime_of_valid1_lineage
        hits 0 (the true zero-birth / desert edge). These are real, independent
        measurements of M_edge(C)+1.
      * C = 6..50 (45 widths) were run at m=1 ONLY. The "cutoff" (zero-birth edge)
        for these was NOT measured -- it was algebraically IMPLIED by adding 1 to
        the single observed m=1 lifetime, under the assumption (proven only at
        C=3,4,5) that max_lifetime(m) = cutoff(C) - m is an exact linear countdown
        with slope -1. No run at C>=6 was ever taken to m > 1, so this assumption
        is untested for 45 of the 48 claimed widths.

  - LOCK3_PRECISION_COUNTDOWN_GRID.md's own text says of the C=6-50 rows: "These
    are not enough to establish the full countdown ladders."

  - COLLATZ_PROOF_backup_v2.md's own Certificate 1 table (a superseded version of
    the polished proof doc) is honest about this: "Domain: C=3,4,5: all m from 1
    to K(C). C=6-50: m=1 only." The current, polished COLLATZ_PROOF.md drops this
    caveat and states "48 independently measured ... without exception," which is
    not an accurate description of what was actually run.

This script re-derives every number above directly from the source files (not by
copy-pasting the table) and writes a flagged JSON/CSV record.
"""
import csv
import json
import re
from pathlib import Path

REPO = Path("/mnt/ForgeRealm/collatz-experimental-data")
OUTDIR = Path(__file__).resolve().parent
GRID_MD = REPO / "LOCK3_PRECISION_COUNTDOWN_GRID.md"
BACKUP_V2 = REPO / "COLLATZ_PROOF_backup_v2.md"
PROOF_MD = REPO / "COLLATZ_PROOF.md"


def M_edge(C: int) -> int:
    return (53 * (C + 1)) // 22


def parse_genuine_ladders(text: str):
    """Parse the zero-birth m for C=3,4,5.

    C3/C4 use a 'C{N} zero point: ```text\\nm = X' block.
    C5 uses different prose: 'strict countdown cutoff at `m = 15` for C5', because its
    m=15 run was a depth-50 probe (not a full depth-2000 sweep) -- see 'Observed boundary
    probes' in the C5 Details section. Both phrasings are parsed explicitly (no blind
    regex fallback) so a missed case fails loudly (via the assert in main) rather than
    silently under-counting.
    """
    out = {}
    for C in (3, 4):
        m = re.search(rf"## C{C} Details.*?zero point:\s*```text\s*m = (\d+)", text, re.S)
        if m:
            out[C] = int(m.group(1))
    m5 = re.search(r"strict countdown cutoff at `m = (\d+)` for C5", text)
    if m5:
        out[5] = int(m5.group(1))
    return out


def parse_m1_probe_table(text: str):
    """Parse the 'Higher-C m1 Probes' markdown table rows: C, m, observed, implied_cutoff, correction."""
    out = {}
    in_table = False
    for line in text.splitlines():
        if "Higher-C m1 Probes" in line:
            in_table = True
            continue
        if in_table:
            if line.strip().startswith("| C | m |"):
                continue
            if line.strip().startswith("| ---"):
                continue
            m = re.match(r"\|\s*(\d+)\s*\|\s*1\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(-?\d+)\s*\|", line)
            if m:
                C, observed, implied_cutoff, correction = (int(x) for x in m.groups())
                out[C] = {
                    "observed_max_lifetime_m1": observed,
                    "implied_cutoff": implied_cutoff,
                    "correction_vs_3C": correction,
                }
            elif line.strip().startswith("## ") and out:
                break
    return out


def main():
    grid_text = GRID_MD.read_text()
    backup_text = BACKUP_V2.read_text()
    proof_text = PROOF_MD.read_text()

    genuine_zero_points = parse_genuine_ladders(grid_text)  # C -> zero_m (= M_edge(C)+1)
    m1_probes = parse_m1_probe_table(grid_text)             # C -> {...} for C=6..50

    assert set(genuine_zero_points.keys()) == {3, 4, 5}, (
        f"expected genuine zero-birth points for exactly C=3,4,5, got {sorted(genuine_zero_points)}"
    )
    assert set(m1_probes.keys()) == set(range(6, 51)), (
        f"expected m1-only probes for exactly C=6..50, got {sorted(m1_probes)} "
        f"(count={len(m1_probes)})"
    )

    # Certificate 1 domain statement, extracted verbatim from the backup file (source of truth
    # for what was actually run, per that file's own text).
    domain_match = re.search(
        r"\*\*Domain\*\*\s*\|\s*(.+?)\s*\|", backup_text
    )
    certificate1_domain_text_in_backup_v2 = domain_match.group(1) if domain_match else None

    claim_match = re.search(
        r"Verified by Certificate 1.{0,400}", proof_text, re.S
    )
    claim_text_in_current_proof = claim_match.group(0)[:300] if claim_match else None

    rows = []

    # Genuine measurements: C=3,4,5
    for C, zero_m in sorted(genuine_zero_points.items()):
        target = M_edge(C) + 1
        note = None
        if C == 5:
            note = ("zero-birth point m=15 was confirmed at DEPTH 50 (not the standard depth "
                     "2000 used for m=1..13), after the depth-1169 m=14 run was manually killed "
                     "once its live count returned to 0; see LOCK3_PRECISION_COUNTDOWN_GRID.md "
                     "'Observed boundary probes'. Still a direct zero-birth observation, just at "
                     "reduced depth budget for the confirming run.")
        rows.append({
            "C": C,
            "measurement_tier": "GENUINE_full_sweep",
            "measured_zero_birth_m": zero_m,
            "formula_M_edge_plus_1": target,
            "matches_formula_exactly": zero_m == target,
            "note": note,
            "source": str(GRID_MD),
        })

    # Inferred: C=6..50
    for C, info in sorted(m1_probes.items()):
        target = M_edge(C) + 1
        rows.append({
            "C": C,
            "measurement_tier": "INFERRED_m1_only_plus_linear_countdown_assumption",
            "measured_zero_birth_m": info["implied_cutoff"],
            "formula_M_edge_plus_1": target,
            "matches_formula_exactly": info["implied_cutoff"] == target,
            "raw_observed_m1_lifetime": info["observed_max_lifetime_m1"],
            "note": "zero-birth m was NEVER DIRECTLY OBSERVED for this C; implied_cutoff = "
                    "observed_m1_lifetime + 1, valid only if the linear countdown slope "
                    "(-1 per unit m), established only at C=3,4,5, also holds here.",
            "source": str(GRID_MD),
        })

    all_exact = all(r["matches_formula_exactly"] for r in rows)
    genuine_rows = [r for r in rows if r["measurement_tier"] == "GENUINE_full_sweep"]
    inferred_rows = [r for r in rows if r["measurement_tier"] != "GENUINE_full_sweep"]

    # --- Periodicity check: M_edge(C+22) - M_edge(C) == 53 in MEASURED values, where BOTH
    #     widths exist in some tier.
    by_C = {r["C"]: r for r in rows}
    periodicity_checks = []
    for C in sorted(by_C):
        if (C + 22) in by_C:
            a, b = by_C[C], by_C[C + 22]
            delta = b["measured_zero_birth_m"] - a["measured_zero_birth_m"]
            periodicity_checks.append({
                "C": C,
                "C_plus_22": C + 22,
                "tier_C": a["measurement_tier"],
                "tier_C_plus_22": b["measurement_tier"],
                "both_genuine": a["measurement_tier"] == "GENUINE_full_sweep"
                                 and b["measurement_tier"] == "GENUINE_full_sweep",
                "delta": delta,
                "matches_53": delta == 53,
            })

    any_both_genuine = any(p["both_genuine"] for p in periodicity_checks)

    summary = {
        "provenance": {
            "claim_source_file": str(PROOF_MD),
            "claim_text_verbatim_excerpt": claim_text_in_current_proof,
            "data_source_file": str(GRID_MD),
            "certificate1_domain_text_in_backup_v2_md": certificate1_domain_text_in_backup_v2,
            "explanation": (
                "The '48' in the COLLATZ_PROOF.md claim = 3 genuine full-sweep widths "
                "(C=3,4,5) + 45 m=1-only widths (C=6..50) whose zero-birth edge was never "
                "directly observed, only algebraically implied. COLLATZ_PROOF_backup_v2.md's "
                "own Certificate 1 table states this domain split honestly ('C=6-50: m=1 "
                "only'); the polished COLLATZ_PROOF.md prose drops the caveat and calls all "
                "48 'independently measured ... without exception', which overstates what was "
                "actually run. LOCK3_PRECISION_COUNTDOWN_GRID.md itself says the C=6-50 probes "
                "'are not enough to establish the full countdown ladders.'"
            ),
        },
        "genuine_full_sweep_widths": sorted(genuine_zero_points.keys()),
        "genuine_count": len(genuine_rows),
        "inferred_m1_only_widths_count": len(inferred_rows),
        "total_widths_in_claim": len(rows),
        "all_48_numerically_consistent_with_formula": all_exact,
        "CAVEAT": (
            "'all_48_numerically_consistent_with_formula' = True is expected and NOT strong "
            "independent evidence for 45 of the 48 rows, because their target value was "
            "computed as observed_m1_lifetime + 1 -- i.e. those rows are consistent with "
            "M_edge(C)+1 by construction (the linear-countdown assumption bakes in a fixed "
            "offset of +1 from a single sample), not because an independent zero-birth point "
            "was measured and found to agree."
        ),
        "periodicity_check": {
            "pairs_checked": len(periodicity_checks),
            "pairs_with_delta_53": sum(1 for p in periodicity_checks if p["matches_53"]),
            "pairs_both_tiers_genuine": sum(1 for p in periodicity_checks if p["both_genuine"]),
            "ANY_PAIR_BOTH_GENUINE": any_both_genuine,
            "HONEST_FLAG": (
                "No (C, C+22) pair exists where BOTH widths are genuine full-sweep "
                "measurements (the only genuine set is {3,4,5}, and {25,26,27} = "
                "{3,4,5}+22 were never independently swept). Therefore the exact "
                "periodicity M_edge(C+22)-M_edge(C)=53 CANNOT be confirmed in the "
                "measured data as currently available -- every one of the pairs "
                "checked below relies on at least one inferred (m=1-only) value, so "
                "periodicity holding there is consistent-by-construction with the "
                "linear-countdown assumption, not independent confirmation."
            ),
        },
    }

    with open(OUTDIR / "task1_measured_verification.json", "w") as f:
        json.dump({"summary": summary, "rows": rows, "periodicity_pairs": periodicity_checks}, f, indent=2)

    fieldnames = ["C", "measurement_tier", "measured_zero_birth_m", "formula_M_edge_plus_1",
                  "matches_formula_exactly", "raw_observed_m1_lifetime", "note", "source"]
    with open(OUTDIR / "task1_measured_widths.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    with open(OUTDIR / "task1_periodicity_pairs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(periodicity_checks[0].keys()))
        w.writeheader()
        for p in periodicity_checks:
            w.writerow(p)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
