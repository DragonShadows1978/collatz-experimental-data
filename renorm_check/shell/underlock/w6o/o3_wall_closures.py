#!/usr/bin/env python3
"""
W6O-O3 -- N4 wall closures (cheap cells only), per
W6O_LEMMA_SCALE_ORDER.md section O3.

BACKGROUND (W6N-N4/N4c, SYNTHESIS.md): the tax-curve of record left
two honest open cells:
  - t=14: nothing <=24 exists at len<=18 (n4c's tight-cap closure,
    cap=24, complete and sound for that cap) -- best witness remains
    32 (len 11, from the static n4 run). True value somewhere in
    [25, 32].
  - t=10: broke a width-4 plateau at len 18 (16->15); true min below
    len-18's 15 is open (len 19+ unprobed).

THIS ROUND (per the order's exact text):
  (i)  t=14: shrink [25, 32] -- run len 15, 16 with the tight-cap
       closure method, bound 25..31 (i.e. cap=31, ONE below the best
       known witness 32, so ANY value found is a strict improvement
       and a sound exact answer for that cap; cap=31 is wide enough to
       admit anything in the open interval [25,31] while still being
       far tighter than n4c's failed cap=24 -- the tight-cap method's
       whole point is that state counts explode roughly exponentially
       in cap, so 24->31 is a real, if partial, re-widening, tried
       here because n4c's cap=24 was certified to find NOTHING, i.e.
       cap=24 was actually too narrow, not too wide -- the direction
       n4c's own docstring did not anticipate). Stop at the RSS/time
       wall; state cells honestly (an honest wall here is NOT a
       failure -- the order says exactly this).
  (ii) t=10: len 19, 20 at tight caps around 15 (best known len-18
       value is 15 exactly; caps are set at 15+margin, tight enough to
       stay fast, wide enough to catch any further drop below 15 or
       confirm stability at 15).

SOUNDNESS OF TIGHT CAPS (restated from n4c, unchanged): the ladder
prunes states with cost > cap + remaining_depth. Any pruned completion
finishes with cost > cap. Therefore IF the run reports a min <= cap,
that min is the TRUE min for the (t, d_max) scope -- nothing cheaper
was ever pruned. A cap can only cause a MISS (no value found), never a
wrong value.

Frozen prediction (Fable, 65%): t=14 settles >= 25 (the cliff is real,
height >= 6, i.e. the true value is NOT close to 19 like the four-trit
plateau's neighbors -- there really is a jump of at least +6 from the
t=13 plateau value of 19).

INSTRUMENT (reused as a module, not reimplemented -- per the order's
own text pointing at "n4c_tight_cap_closure.py (O3's method)"):
w6m/m3_ladder_wall_extension.py's bigint ladder (run_ladder_bigint,
extract_witness_bigint, exact_replay, gate_G1/G2, rss_gb). Gates
re-run fresh in-process before any production value, per the
W6L/W6M/W6N discipline. Same 8GB RSS cap, CPU only.
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

# (t, d_max, cap, per-cell wallclock budget)
CELLS = [
    (14, 15, 31, 300.0),
    (14, 16, 31, 300.0),
    (10, 19, 18, 300.0),
    (10, 20, 18, 300.0),
]


def main():
    t0_all = time.time()
    print("=== W6O-O3: N4 wall closures (t=14 shrink [25,32]; t=10 len 19,20) ===\n")
    print("--- Gates (fresh in-process re-run) ---")
    gate_G1()
    gate_G2()
    print()

    rows = []
    for (t, d_max, cap, wallclock_cap) in CELLS:
        print(f"\n  [t={t} d_max={d_max} T0={t+d_max} cap={cap} (TIGHT, sound), "
              f"wallclock budget={wallclock_cap}s]:")
        t_run0 = time.time()
        res = run_ladder_bigint(t, d_max, cap, wallclock_cap=wallclock_cap)
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

    out = HERE / "o3_wall_closures.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nWrote {out.name} ({len(rows)} rows)")

    # -------------------------------------------------------------
    # Frozen prediction verdict
    # -------------------------------------------------------------
    print("\n=== FROZEN PREDICTION VERDICT ===")
    print("t=14 settles >= 25 (the cliff is real, height >= 6) -- 65% predicted\n")

    t14_rows = [r for r in rows if r["t"] == 14]
    t14_found = [r for r in t14_rows if r["sound_exact"]]
    if t14_found:
        best_t14 = min(r["exact_min"] for r in t14_found)
        print(f"  t=14 cells with an exact value at cap=31: {[(r['d_max'], r['exact_min']) for r in t14_found]}")
        print(f"  Best exact t=14 value found this round: {best_t14}")
        verdict_t14 = "HIT" if best_t14 >= 25 else f"MISS (found {best_t14} < 25, cliff height < 6)"
    else:
        print("  t=14: no cell produced a value <= cap=31 at len 15,16 -- honest wall, "
              "still open; the >=25 claim is UNFALSIFIED but also UNCONFIRMED by a "
              "found value (n4c's own cap=24 exhaustion already implies >=25 for "
              "len<=18, which this round does not overturn -- see honest walls below).")
        verdict_t14 = "WALL (no new value; >=25 stands via n4c's cap=24 exhaustion, not newly confirmed here)"
    print(f"  t=14 verdict: {verdict_t14}")

    t10_rows = [r for r in rows if r["t"] == 10]
    t10_found = [r for r in t10_rows if r["sound_exact"]]
    if t10_found:
        best_t10 = min(r["exact_min"] for r in t10_found)
        print(f"\n  t=10 cells with an exact value at cap=18: {[(r['d_max'], r['exact_min']) for r in t10_found]}")
        print(f"  Best exact t=10 value found this round (len 19,20): {best_t10}")
    else:
        print("\n  t=10: no cell produced a value <= cap=18 at len 19,20 -- honest wall.")

    print(f"\nTotal wall: {time.time()-t0_all:.1f}s, peak RSS: {rss_gb():.3f} GB")


if __name__ == "__main__":
    main()
