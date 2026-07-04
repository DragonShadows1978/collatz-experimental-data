#!/usr/bin/env python3
"""
W6R-R4 -- Why the end-anchored L predicted M_edge 48/48 (the frame-rule
reconciliation).

Order text (frozen): "The H5 fact: end-anchored L with run ≡ 52 (mod
53) frames matched archived M_edge at C = 3..50, 48/48. Under sec 15a's
hypothesis (extremal corridor windows are frame-aligned), verify
mechanically: for C = 3..10, extract or regenerate the census's actual
edge-achieving data (archived scans, or recompute edges with the
census recursion directly) and measure the phase relationship between
the extremal window and the 53-grid. Frozen: extremal windows sit at
the frame-rule phase (or a fixed offset from it), explaining H5
without coincidence -- 60%."

DATA SOURCE: data/runs/lock3_C{C}_N2000_residue_m1_lineage_cohorts_*/
lock3_census_C{C}.csv (the SAME archive w6h/h5_frame_rule_crosscheck.py
uses for M_edge_archived) -- read directly, not regenerated (the
archived runs already exist and are dense C=1..50; regenerating would
duplicate work for no gain in trust, since these are the SAME files
h5 already cross-validated CSV-vs-summary-JSON).

LINEAGE SEMANTICS (read directly from rust/lock3_census.rs, lines
~2625-2657, not paraphrased): a "lineage" is born at `birth_depth`
when a (deficit,residue) key lacks a live terminal-compatible parent
(no_live_terminal_compatible_parent). Its lifetime AT DEPTH d (while
still alive) is `d - birth_depth + 1`
(current_max_valid1_lineage_lifetime, line 2650-2654); when it DIES
(fails to survive to the next depth), its FINAL lifetime is recorded
into the lifetime histogram as `next_depth.saturating_sub(birth_depth)`
(line 2632, one less than the "while alive" formula since next_depth
is one past the last depth it was actually alive at) and folded into
the running max_valid1_lineage_lifetime_seen (line 2637) -- this
scalar is MONOTONE NONDECREASING over depth (a running max, never
reset), so the FIRST depth at which the CSV's own
`max_valid1_lineage_lifetime` column reaches its final (row -1, i.e.
overall max) value is EXACTLY the depth at which the extremal-lifetime
lineage died -- i.e. the window-END depth. Window START = end - M_edge
+ 1 (from the "while alive" formula, lifetime = d - birth + 1 at the
moment of death is exactly M_edge, since a death-record lifetime of L
via line 2632's next_depth-birth formula equals the "final live depth"
minus birth_depth, i.e. M_edge = (death_event_next_depth) - birth_depth,
and the actual last-alive depth is death_event_next_depth - 1 -- see
`extract_window` below for the exact reconciliation, cross-checked
both ways).

FRAME RULE (H5's own definition, m_irr/run_length reused verbatim):
run(C) = 53*ceil((m_irr(C)+1)/53), window END index === 52 (mod 53)
by construction (a multiple of 53, minus 1). "Frame-aligned" here
means: the extremal window's END DEPTH, reduced mod 53, sits at a
FIXED phase (52, or some other fixed constant -- checked, not assumed)
across all C=3..10, i.e. the corridor's own dynamics naturally produce
windows ending at a constant residue mod 53 regardless of C.
"""
from __future__ import annotations

import csv
import glob
import re
from pathlib import Path

DATA_RUNS = Path("/mnt/ForgeRealm/collatz-experimental-data/data/runs")
HERE = Path(__file__).parent

C_RANGE = list(range(3, 11))  # 3..10, per the order


def find_census_csv(C: int):
    pattern = str(DATA_RUNS / f"lock3_C{C}_N2000_residue_m1_lineage_cohorts_*" / f"lock3_census_C{C}.csv")
    matches = sorted(glob.glob(pattern))
    if not matches:
        return None
    return matches[0]


def extract_window(csv_path: str):
    """Read the census CSV's own max_valid1_lineage_lifetime column
    (monotone nondecreasing running max, per the module docstring's
    citation of the rust source). Returns:
      M_edge         = final (row -1) value of the column
      end_depth      = FIRST depth at which the column reaches M_edge
                        (the extremal lineage's death-record depth,
                        i.e. next_depth in the rust source's own death
                        loop -- the moment AFTER the lineage's last
                        live appearance)
      last_alive_depth = end_depth - 1 (the actual last depth the
                        maximal lineage was observed alive, matching
                        the "while alive" formula lifetime=d-birth+1
                        at d=last_alive_depth giving exactly M_edge)
      birth_depth    = last_alive_depth - M_edge + 1
    Both window-end conventions (end_depth and last_alive_depth) are
    reported and checked against the 53-grid -- the order says
    "measure the phase relationship", not which of two adjacent
    depths is definitionally "the" end, so both candidates are tested
    honestly rather than silently picking one.
    """
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    depths = [int(r["depth"]) for r in rows]
    lifetimes = [int(r["max_valid1_lineage_lifetime"]) for r in rows]
    M_edge = lifetimes[-1]
    end_depth = None
    for d, lt in zip(depths, lifetimes):
        if lt == M_edge:
            end_depth = d
            break
    last_alive_depth = end_depth - 1
    birth_depth = last_alive_depth - M_edge + 1
    return {
        "M_edge": M_edge,
        "end_depth_death_record": end_depth,
        "last_alive_depth": last_alive_depth,
        "birth_depth": birth_depth,
        "n_rows": len(rows),
    }


def m_irr(C: int) -> int:
    return 53 * (C + 1) // 22


def run_length(m: int) -> int:
    import math
    return 53 * math.ceil((m + 1) / 53)


def main():
    print("=== W6R-R4: frame-rule reconciliation, C=3..10 ===\n")
    print("Reading archived lock3_census_C{C}.csv (same archive as w6h/h5), extracting")
    print("the extremal-lineage window's phase relative to the 53-grid.\n")

    rows = []
    honest_walls = []

    for C in C_RANGE:
        csv_path = find_census_csv(C)
        if csv_path is None:
            honest_walls.append((C, "no archived census CSV found"))
            print(f"  C={C}: *** NO ARCHIVE FOUND ***")
            continue
        info = extract_window(csv_path)
        m_irr_val = m_irr(C)
        run_val = run_length(m_irr_val)

        phase_death = info["end_depth_death_record"] % 53
        phase_alive = info["last_alive_depth"] % 53
        phase_birth = info["birth_depth"] % 53
        run_expected_phase = (run_val - 1) % 53  # window end index === run-1 (mod 53) by H5's own def

        rows.append({
            "C": C, "M_edge": info["M_edge"], "m_irr": m_irr_val, "run_predicted": run_val,
            "M_edge_matches_m_irr": info["M_edge"] == m_irr_val,
            "birth_depth": info["birth_depth"],
            "last_alive_depth": info["last_alive_depth"],
            "end_depth_death_record": info["end_depth_death_record"],
            "phase_last_alive_mod53": phase_alive,
            "phase_death_record_mod53": phase_death,
            "phase_birth_mod53": phase_birth,
            "run_expected_phase_mod53": run_expected_phase,
            "last_alive_matches_frame_phase": phase_alive == run_expected_phase,
        })
        print(f"  C={C:>2}: M_edge={info['M_edge']:>3} (m_irr={m_irr_val}, match={info['M_edge']==m_irr_val}) "
              f"birth={info['birth_depth']:>4} last_alive={info['last_alive_depth']:>4} "
              f"death_rec={info['end_depth_death_record']:>4} | "
              f"phase(last_alive mod53)={phase_alive:>2} phase(death_rec mod53)={phase_death:>2} "
              f"expected_frame_phase={run_expected_phase:>2} "
              f"{'ALIGNED' if phase_alive==run_expected_phase else 'OFFSET'}")

    out = HERE / "r4_frame_phase_table.csv"
    if rows:
        with open(out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for r in rows:
                w.writerow(r)
        print(f"\nWrote {out.name} ({len(rows)} rows)")

    # Phase analysis: is there a FIXED offset (constant across all C),
    # even if not exactly the frame-rule's own phase?
    print("\n--- Phase analysis (is there ANY fixed offset across C=3..10?) ---")
    offsets_alive = [(r["phase_last_alive_mod53"] - r["run_expected_phase_mod53"]) % 53 for r in rows]
    offsets_death = [(r["phase_death_record_mod53"] - r["run_expected_phase_mod53"]) % 53 for r in rows]
    print(f"  last_alive_depth offsets from expected frame phase (mod 53): {offsets_alive}")
    print(f"  death_record_depth offsets from expected frame phase (mod 53): {offsets_death}")
    fixed_offset_alive = len(set(offsets_alive)) == 1
    fixed_offset_death = len(set(offsets_death)) == 1
    print(f"  fixed offset (last_alive): {fixed_offset_alive} "
          f"({'value='+str(offsets_alive[0]) if fixed_offset_alive else 'VARIES'})")
    print(f"  fixed offset (death_record): {fixed_offset_death} "
          f"({'value='+str(offsets_death[0]) if fixed_offset_death else 'VARIES'})")

    n_exact_aligned = sum(1 for r in rows if r["last_alive_matches_frame_phase"])
    n_total = len(rows)

    print(f"\n=== FROZEN PREDICTION VERDICT ===")
    print(f"Extremal windows sit at the frame-rule phase (or a fixed offset from it) "
          f"-- 60% predicted\n")
    print(f"Exact frame-phase alignment (last_alive_depth === expected mod 53): {n_exact_aligned}/{n_total}")
    print(f"Fixed offset exists (last_alive convention): {fixed_offset_alive}")
    print(f"Fixed offset exists (death_record convention): {fixed_offset_death}")

    exact_hit = (n_exact_aligned == n_total)
    fixed_offset_hit = fixed_offset_alive or fixed_offset_death
    if exact_hit:
        verdict = "HIT (exact frame-phase alignment on every C)"
    elif fixed_offset_hit:
        verdict = "HIT (fixed, non-zero offset from frame-rule phase on every C)"
    else:
        verdict = "MISS -- no fixed phase relationship found across C=3..10"
    print(f"Verdict: {verdict}")

    if honest_walls:
        print(f"\nHonest walls: {honest_walls}")
    else:
        print(f"\nNo honest walls: archived census CSV found and read for every C=3..10.")


if __name__ == "__main__":
    main()
