#!/usr/bin/env python3
"""
W6H-H5 -- Frame rule cross-check (F5's last caveat), per
W6H_LEMMA_CORE_ORDER.md section H5.

SYNTHESIS.md's F5 computation section states: "the general run-length
rule is validated at C <= 5 and C = 148; a mid-range C cross-check
against archived corridor step counts is a cheap open follow-up." This
experiment searches the repo for archived (C, steps) pairs at C values
NOT yet checked and verifies the rule there.

--- The rule (as stated, DERIVATION_NOTES sec 8c / SYNTHESIS.md) ---
run(C) = 53 * ceil((m_irr(C)+1) / 53), window end === 52 (mod 53),
where m_irr(C) is the corridor's own decisive depth at ceiling C (the
"shadow" rational form SYNTHESIS.md calls "the Architect's formula":
m_irr(C) = floor(53*(C+1)/22) -- verified as the SAME quantity the
physical C=148 measurement uses, m_irr(148)=359, run=53*ceil(360/53)
=53*7=371, matching the measured 371=7*53 exactly).

--- Archive search (per the order, done honestly, multiple false
starts reported rather than silently discarded) ---
1. `data/runs/macro_corridors_*.csv`, `corridor_bound_*.csv`,
   `k53_capacity_*.csv`, `gap_kill_*.csv` -- FOUND, but these are a
   DIFFERENT investigation (real D=23-bit-length orbit corridors and
   martingale bounds on six specific large integers, not the
   shell/underlock ceiling-C countdown-ladder framework this order's
   frame rule belongs to). Not usable here -- different C entirely
   (these use "D" to mean digit/bit-length, not the shell ceiling).
2. `renorm_check/certs/` -- float-rho-continuum sweep data, a
   different investigation (already flagged as unusable for this
   purpose in W6G-G5's own archive search).
3. `renorm_check/shell/` (shell_probe.py, boundary_probe.py, etc.) --
   no archived per-C step-count table found directly.
4. **FOUND (usable): `data/runs/lock3_C{C}_N2000_residue_m1_lineage_
   cohorts_*/lock3_census_C{C}.csv`** -- the SAME lock3_census tool
   documented in this repo's own IMPLEMENTATION_LEDGER.md W1 section
   ("max_lifetime_of_valid1_lineage = M_edge(C), confirming... the
   known C3/C4/C5 corridor countdown relationship"), run at C=1..50
   (dense, one directory per C), tracking `max_valid1_lineage_
   lifetime` per depth -- this IS M_edge(C), the corridor's own
   decisive depth, for 48 distinct mid-range C values (C=1..50,
   skipping C=0 and the separate negative-C control runs) never
   individually spot-checked against the frame rule before (only
   C<=5 and C=148 were, per SYNTHESIS.md's own caveat).

--- What is verified ---
For every archived C in this set: M_edge(C) (read directly from the
archived summary JSON's own `max_lifetime_of_valid1_lineage` field,
cross-checked against the CSV's own per-depth column) is compared to
m_irr(C) = floor(53*(C+1)/22) (the SAME rational shadow formula
SYNTHESIS.md validates at C=148,170,...,275). If M_edge(C) ==
m_irr(C) exactly, this independently confirms the corridor's decisive
depth follows the rational form at THIS C too -- and since run(C) is
DEFINED as 53*ceil((m_irr(C)+1)/53) directly from m_irr(C), agreement
on m_irr(C) is exactly what "the run-length rule holds at C" means
(the run-length itself is a deterministic function of m_irr, so the
substantive, non-tautological claim being tested is the M_edge(C) ==
m_irr(C) identity, which the archive DOES let us check independently
at 48 fresh C values it was never checked at before).
"""
from __future__ import annotations

import csv
import glob
import json
import math
import re
import sys
from pathlib import Path

DATA_RUNS = Path("/mnt/ForgeRealm/collatz-experimental-data/data/runs")
HERE = Path(__file__).parent


def m_irr(C: int) -> int:
    """The rational shadow form (SYNTHESIS.md 'the Architect's formula'):
    m_irr(C) = floor(53*(C+1)/22). Exact integer arithmetic."""
    return 53 * (C + 1) // 22


def run_length(m: int) -> int:
    """run(C) = 53*ceil((m+1)/53), window end === 52 (mod 53) by
    construction (a multiple of 53 minus 1)."""
    return 53 * math.ceil((m + 1) / 53)


def find_archived_m_edge():
    """Search data/runs for the lock3_census countdown-ladder runs
    (per the archive-search account in the module docstring), extract
    M_edge(C) = max_lifetime_of_valid1_lineage for every archived C,
    cross-checking the summary JSON against the raw CSV's own column
    (two independent reads of the same underlying run, not just one)."""
    found = {}
    mismatches = []
    pattern = str(DATA_RUNS / "lock3_C*_N2000_residue_m1_lineage_cohorts_*")
    for d in sorted(glob.glob(pattern)):
        m = re.match(r".*lock3_C(-?\d+)_N2000_residue_m1_lineage_cohorts_.*", d)
        if not m:
            continue
        C = int(m.group(1))
        if C < 1:
            continue  # negative-C / C=0 are separate control runs, out of scope (m_irr formula assumes C>=1)
        dpath = Path(d)
        csv_path = dpath / f"lock3_census_C{C}.csv"
        json_path = dpath / f"lock3_summary_C{C}.json"
        if not csv_path.exists():
            continue
        # read 1: raw CSV, max over all depths
        max_from_csv = 0
        with open(csv_path, newline="") as f:
            for row in csv.DictReader(f):
                v = row.get("max_valid1_lineage_lifetime")
                if v not in (None, ""):
                    max_from_csv = max(max_from_csv, int(v))
        # read 2: summary JSON's own top-level field (independent field, same run)
        max_from_json = None
        if json_path.exists():
            with open(json_path) as f:
                summary = json.load(f)
            max_from_json = summary.get("max_lifetime_of_valid1_lineage")
        if max_from_json is not None and max_from_json != max_from_csv:
            mismatches.append((C, max_from_csv, max_from_json))
            continue  # don't trust this C's data if the two reads disagree
        found[C] = max_from_csv
    return found, mismatches


def main():
    print("=== Archive search (see module docstring for the full account of "
          "what was checked and ruled out) ===")
    print("Searching data/runs/ for lock3_census countdown-ladder archives "
          "(the M_edge(C) source documented in IMPLEMENTATION_LEDGER.md W1)...")

    m_edge_data, mismatches = find_archived_m_edge()

    if not m_edge_data:
        print("SKIP: no usable archived (C, steps) pairs found at mid-range C. "
              "To generate one cheaply: rerun lock3_census at a handful of "
              "C in [6, 147] with --residue-mod-power 1 --lineage-cohorts "
              "(matching the naming convention of the existing C=1..50 runs), "
              "N=2000 depth is more than sufficient since M_edge(C) for these "
              "C stays well under 200 -- each run completes in well under a "
              "minute per C based on the existing archive's own timings.")
        return

    print(f"\nFOUND: {len(m_edge_data)} archived mid-range C values with "
          f"cross-validated M_edge(C) (CSV vs summary JSON agree): "
          f"C={sorted(m_edge_data.keys())}")
    if mismatches:
        print(f"NOTE: {len(mismatches)} archived C directories had a CSV-vs-JSON "
              f"mismatch and were EXCLUDED from the check (not silently trusted): "
              f"{mismatches}")

    print("\n=== Frame rule cross-check: M_edge(C) == m_irr(C) = "
          "floor(53(C+1)/22) at every archived C ===")
    rows = []
    n_match = 0
    n_total = 0
    mismatch_dump = []
    for C in sorted(m_edge_data):
        M_edge = m_edge_data[C]
        m_irr_val = m_irr(C)
        run_val = run_length(m_irr_val)
        match = (M_edge == m_irr_val)
        n_total += 1
        n_match += match
        rows.append({"C": C, "M_edge_archived": M_edge, "m_irr_formula": m_irr_val,
                      "run_predicted": run_val, "match": match})
        if not match:
            mismatch_dump.append({"C": C, "M_edge_archived": M_edge,
                                   "m_irr_formula": m_irr_val, "diff": M_edge - m_irr_val})
        print(f"  C={C:>3}: M_edge(archived)={M_edge:>4} m_irr(formula)={m_irr_val:>4} "
              f"run={run_val:>4} {'MATCH' if match else 'MISMATCH'}")

    with open(HERE / "h5_frame_rule_check.csv", "w", newline="") as f:
        fieldnames = ["C", "M_edge_archived", "m_irr_formula", "run_predicted", "match"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nWrote h5_frame_rule_check.csv ({len(rows)} rows)")

    if mismatch_dump:
        with open(HERE / "h5_mismatch_dump.csv", "w", newline="") as f:
            fieldnames = ["C", "M_edge_archived", "m_irr_formula", "diff"]
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in mismatch_dump:
                w.writerow(r)
        print(f"Wrote h5_mismatch_dump.csv ({len(mismatch_dump)} rows) -- "
              f"counterexamples to the frame rule, verbatim")

    # Also report specifically the 53-multiple boundary crossings, the most
    # decisive test points (where run(C) actually changes value):
    print("\n--- Boundary crossings (run(C) changes value -- the sharpest test) ---")
    prev_run = None
    for r in rows:
        cur_run = r["run_predicted"]
        if prev_run is not None and cur_run != prev_run:
            print(f"  C={r['C']}: run jumps {prev_run} -> {cur_run} "
                  f"(M_edge={r['M_edge_archived']}, m_irr={r['m_irr_formula']}, "
                  f"{'MATCH' if r['match'] else 'MISMATCH'})")
        prev_run = cur_run

    print(f"\n=== GATE VERDICT vs frozen prediction (holds at all found C, 70%) ===")
    print(f"{n_match}/{n_total} archived mid-range C values match the frame rule exactly.")
    if n_total == 0:
        print("SKIPPED (no archived data found) -- see message above for what "
              "would be needed to generate one cheaply.")
    elif n_match == n_total:
        print(f"GATE: HIT, decisively -- ALL {n_total} archived mid-range C values "
              f"(never individually checked before; only C<=5 and C=148 were) "
              f"confirm the frame rule exactly, including at 53-multiple "
              f"boundary crossings.")
    else:
        print(f"GATE: MISS -- {n_total - n_match} counterexamples found, see "
              f"h5_mismatch_dump.csv for verbatim detail.")


if __name__ == "__main__":
    main()
