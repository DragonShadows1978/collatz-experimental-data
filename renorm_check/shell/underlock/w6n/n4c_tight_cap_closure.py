#!/usr/bin/env python3
"""
W6N-N4c -- Tight-cap closure of the N4 cells that the static-cap run
walls on (or leaves slow), using SOUND cap tightening.

CONTEXT: n4_length_convergence.py seeds caps from M3's own values
(cap_for(t) = M3_best + 4), which was correct at design time -- but
the run's OWN mid-flight discovery (t=13 drops 31 -> 19 at len 15 via
the shared four-trit witness (4,3,2,5,4,3,1,3,2,2,1,4,9,5,1), replay-
verified: final v = 35075107 == 1 mod 3^13 exactly) makes cap=35 for
t=13 wastefully wide: state counts blow up ~exponentially in cap, so
the d_max=16,17,18 cells crawl toward the per-cell wall-clock cap.

SOUNDNESS OF TIGHT CAPS (the standard argument, restated): the ladder
prunes states with cost > cap + remaining_depth. Any pruned
completion finishes with cost > cap. Therefore IF the run reports a
min <= cap, that min is the TRUE min for the (t, d_max) scope --
nothing cheaper was ever pruned. A cap can only cause a MISS (no
value found / value > cap reported as none), never a wrong value.
Since a cost-19 witness for t=13 (len 15) and cost-15 witness for
t=10 (len 18) are already exact-replay-certified in this round, caps
of 21 for t=13 comfortably contain the true min for every d_max >= 15
(min is nonincreasing in d_max). For t=14 no better witness than 32
(len<=14) is known yet; we FIRST try cap=24 (a guess informed by the
t=13 collapse; if the true min at len 15..18 is <= 24 this finds it
exactly and fast) and only report "no value at cap 24" -- an honest
partial -- if nothing lands, in which case the static-cap N4 run's
own result (if it completed) stands as the record.

Cells run here: t=13 d_max in (16,17,18) at cap 21;
                t=14 d_max in (15,16,17,18) at cap 24;
                t=10 NOT rerun -- N4's static run already completed
                t=10 cleanly at cap 20 (16,15 at len 17,18).
Same instrument (m3_ladder_wall_extension, gated in-process again),
same replay discipline, same 8GB RSS cap, per-cell wall-clock 300s.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
W6M = HERE.parent / "w6m"
W6L = HERE.parent / "w6l"
W6E = HERE.parent / "w6e"
sys.path.insert(0, str(W6M))
sys.path.insert(0, str(W6L))
sys.path.insert(0, str(W6E))

from m3_ladder_wall_extension import (  # noqa: E402
    run_ladder_bigint, extract_witness_bigint, exact_replay,
    gate_G1, gate_G2, rss_gb,
)

CELLS = [
    (13, 16, 21), (13, 17, 21), (13, 18, 21),
    (14, 15, 24), (14, 16, 24), (14, 17, 24), (14, 18, 24),
]
WALLCLOCK_CAP_PER_CELL_S = 300.0


def main():
    t0_all = time.time()
    print("=== W6N-N4c: tight-cap closure (sound caps; see docstring) ===\n")
    print("--- Gates (fresh in-process re-run) ---")
    gate_G1()
    gate_G2()
    print()

    rows = []
    for (t, d_max, cap) in CELLS:
        print(f"\n  [t={t} d_max={d_max} T0={t+d_max} cap={cap} (TIGHT, sound)]:")
        t_run0 = time.time()
        res = run_ladder_bigint(t, d_max, cap, wallclock_cap=WALLCLOCK_CAP_PER_CELL_S)
        wit = extract_witness_bigint(res)
        gmin = res["global_min"]
        replay_ok = None
        if wit is None:
            wit_str = "none in scope at this cap (honest partial if cap-bound)"
        elif wit[0] == "BACKTRACK_FAIL":
            wit_str = f"BACKTRACK FAIL {wit[1:]}"
            replay_ok = False
        else:
            d, seq = wit
            replay_ok = exact_replay(seq, t) and sum(a - 2 for a in seq) == gmin
            wit_str = f"len={d} a_seq={seq} replay={'PASS' if replay_ok else '*** FAIL ***'}"
        elapsed = time.time() - t_run0
        wall_note = f" WALL@{res['wall']}" if res["wall"] else ""
        sound = (gmin is not None and gmin <= cap)
        print(f"    RESULT: min (len<={d_max}, cap {cap}) = {gmin} "
              f"{'[EXACT for scope: min <= cap]' if sound else '[NO VALUE <= cap -- honest partial]'}; "
              f"{wit_str}; per-depth {res['per_depth_min']}{wall_note}; "
              f"{elapsed:.1f}s RSS={rss_gb():.2f}GB")
        rows.append({
            "t": t, "d_max": d_max, "T0": t + d_max, "cap": cap,
            "exact_min": gmin if sound else "",
            "raw_min_at_cap": gmin,
            "sound_exact": sound,
            "argmin_len": (wit[0] if wit and wit[0] != "BACKTRACK_FAIL" else ""),
            "argmin_a_seq": (",".join(map(str, wit[1])) if wit and wit[0] != "BACKTRACK_FAIL" else ""),
            "witness_replay": replay_ok,
            "per_depth_min": str(res["per_depth_min"]),
            "wall": str(res["wall"]) if res["wall"] else "",
            "wallclock_s": round(elapsed, 1),
            "peak_rss_gb": round(rss_gb(), 3),
        })

    out = HERE / "n4c_tight_cap_closure.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nWrote {out.name} ({len(rows)} rows)")
    print(f"\nTotal wall: {time.time()-t0_all:.1f}s, peak RSS: {rss_gb():.3f} GB")


if __name__ == "__main__":
    main()
