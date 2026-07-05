#!/usr/bin/env python3
"""
W6X-MULTI Step 2 -- THE MEASUREMENT.

C = 11..15, sweep m = 54..106 (two heartbeats) and beyond as the RSS
budget allows, under BOTH anchor readings ("A" and "B", see mx_core.py
/ DESIGN_NOTES.md). For each (C, m, reading): alive/dead, peak
live-set size, peak RSS, elapsed time, and (if alive) an exact-
verified witness.

This intentionally follows the same house log/report style as
w6w_sparse/step2_4_climb.py (this program's own predecessor) -- same
per-cell logging shape, same CSV/JSON dual output, same "record every
row, not just the edge" policy so partial progress survives a wall.

RSS watchdog: mx_core's sparse_survival_multi already hard-checks RSS
after every layer inside a single (C,m) cell; this script additionally
checks RSS BEFORE starting each new cell (covers the case where the
watchdog inside one cell would fire mid-cell but we want to also avoid
even starting an expensive cell close to the cap), and records the
peak RSS observed across the whole run even when comfortably under
budget, per house rules.
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from mx_core import sparse_survival_multi, verify_witness_exact, rss_mb  # noqa: E402

RSS_CAP_MB = 7500.0
C_LIST = [11, 12, 13, 14, 15]
M_RANGE = list(range(54, 107))  # 54..106 inclusive
READINGS = ["A", "B"]


def main():
    out = []

    def p(s=""):
        print(s, flush=True)
        out.append(s)

    t_start = time.time()
    p("=== W6X-MULTI Step 2: MULTI-HEARTBEAT MEASUREMENT ===")
    p(f"C in {C_LIST}, m in {M_RANGE[0]}..{M_RANGE[-1]}, readings={READINGS}")
    p(f"RSS cap: {RSS_CAP_MB} MB\n")

    rows = []
    peak_rss_overall = 0.0
    honest_walls = []

    # IMPORTANT: the full m-range is swept for EVERY (C, reading) cell,
    # WITHOUT stopping at the first dead m. Reading B is empirically
    # monotone (alive-then-permanently-dead, confirmed below and in
    # step3_analysis.py), but reading A ("root"/growing end-anchor) is
    # KNOWN non-monotone (W6W-SPARSE's own root-anchor negative control
    # showed dead/dead/ALIVE/dead at m=29..32) -- an early v1 of this
    # script broke the loop at the first dead m for BOTH readings and
    # silently truncated reading A's data past its first death, hiding
    # later revivals (caught in review before this was reported: C=13
    # reading A revives at m=67 despite "dying" at m=66). Fixed here:
    # no early break on death for either reading, only on an actual
    # wall (RSS cap / instrument-reported wall).
    for reading in READINGS:
        p(f"\n--- Reading {reading} ---")
        for C in C_LIST:
            p(f"\nC={C}, reading={reading}")
            any_dead = False
            first_dead_m = None
            for m in M_RANGE:
                cur_rss = rss_mb()
                peak_rss_overall = max(peak_rss_overall, cur_rss)
                if cur_rss > RSS_CAP_MB:
                    wall = f"pre-cell RSS cap exceeded before C={C} m={m} reading={reading} (rss={cur_rss:.1f}MB)"
                    p(f"  WALL: {wall}")
                    honest_walls.append(wall)
                    break
                res = sparse_survival_multi(m, C, reading=reading,
                                             rss_cap_mb=RSS_CAP_MB, want_witness=True)
                peak_rss_overall = max(peak_rss_overall, res["peak_rss_mb"])
                row = {
                    "reading": reading, "C": C, "m": m,
                    "alive": res["alive"],
                    "peak_live_states": res["peak_live_states"],
                    "final_live_states": res["final_live_states"],
                    "peak_rss_mb": res["peak_rss_mb"],
                    "elapsed_sec": res["elapsed_sec"],
                    "wall": res["wall"],
                    "witness_start_integer": None,
                    "witness_all_ok": None,
                    "witness_range": None,
                }
                if res["wall"]:
                    p(f"  m={m}: WALL {res['wall']}")
                    honest_walls.append(f"C={C} m={m} reading={reading}: {res['wall']}")
                    rows.append(row)
                    break
                if res["alive"]:
                    if res["witness"]:
                        v = verify_witness_exact(res["witness"], C, res["letters"])
                        row["witness_start_integer"] = v["start_integer"]
                        row["witness_all_ok"] = v["all_ok"]
                        row["witness_range"] = v["range"]
                        if not v["all_ok"]:
                            p(f"  m={m}: WITNESS VERIFY FAILED: {v}")
                    rows.append(row)
                    if m % 10 == 0 or m in (54, 106) or any_dead:
                        tag = " (REVIVAL after earlier death)" if any_dead else ""
                        p(f"  m={m}: alive peak_live={res['peak_live_states']} "
                          f"final_live={res['final_live_states']} "
                          f"rss={res['peak_rss_mb']:.1f}MB dt={res['elapsed_sec']:.3f}s "
                          f"witness_ok={row['witness_all_ok']} n0={row['witness_start_integer']}{tag}")
                else:
                    rows.append(row)
                    if not any_dead:
                        first_dead_m = m
                        p(f"  m={m}: DEAD (first death). live-set became empty. "
                          f"peak_live_at_death_layer={res['peak_live_states']} "
                          f"last_alive_m={m - 1}")
                        prev = sparse_survival_multi(m - 1, C, reading=reading,
                                                      rss_cap_mb=RSS_CAP_MB, want_witness=True)
                        if prev["alive"] and prev["witness"]:
                            v = verify_witness_exact(prev["witness"], C, prev["letters"])
                            p(f"    certificate: m={m - 1} alive, witness all_ok={v['all_ok']} "
                              f"n0={v['start_integer']}")
                    any_dead = True
            if first_dead_m is None:
                p(f"  C={C} reading={reading}: ALIVE through m={M_RANGE[-1]} "
                  f"(no death found in swept range)")
            else:
                revived = any(r["alive"] for r in rows
                               if r["reading"] == reading and r["C"] == C and r["m"] > first_dead_m)
                p(f"  C={C} reading={reading}: first_dead_m={first_dead_m}, "
                  f"revives_later_in_range={revived}")

    # -------------------------------------------------------------
    # Write CSV + JSON
    # -------------------------------------------------------------
    csv_path = HERE / "step2_measurement_table.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    p(f"\nWrote {csv_path}")

    json_path = HERE / "step2_measurement_full.json"
    json_path.write_text(json.dumps(rows, indent=2))
    p(f"Wrote {json_path}")

    p(f"\nPeak RSS observed across entire run: {peak_rss_overall:.1f} MB "
      f"(cap {RSS_CAP_MB} MB)")
    if honest_walls:
        p(f"\nHonest walls hit ({len(honest_walls)}):")
        for w in honest_walls:
            p(f"  - {w}")
    else:
        p("\nNo walls hit -- full swept range completed for all (C, reading).")

    p(f"\nTotal wall time: {time.time() - t_start:.1f}s")
    (HERE / "step2_measurement.log").write_text("\n".join(out) + "\n")
    p(f"Wrote {HERE / 'step2_measurement.log'}")


if __name__ == "__main__":
    main()
