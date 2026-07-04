#!/usr/bin/env python3
"""
W6N-N4 -- Length convergence of the tax curve, per
W6N_FLOOR_MECHANISM_ORDER.md section N4.

M3 (W6M) built a fresh exact-bigint ladder instrument (no int64
anywhere, no overflow class, gated G1/G2/G3 vs L2e's certified
overlap) and found: t=13 (len<=14) = 31, t=14 (len<=14) = 32 (both
closed, no wall); and a length-stability probe at t=10,11,12 for
len 15,16 showed t=10 STABLE at 16, but t=11 and t=12 BOTH DROP from
21 to 19 at len 15 and hold at 19 through len 16 (shared witness chain
`(4,3,2,5,4,3,1,3,2,2,1,4,9,5,1)` for both). This round: EXTEND every
one of t=10..14 out to len 17, 18 (the order's exact scope), stopping
EACH t as soon as two consecutive lengths agree (early-stop, reported
per t), continuing to the RSS/time wall otherwise, honestly.

INSTRUMENT: the SAME exact-bigint ladder as w6m/m3_ladder_wall_extension
.py (Python bigint arithmetic throughout -- no modular int64, no
overflow risk of any kind at any T0; already gated there: G1 vs an
independent closed-form + lift-invariance at M_exp up to 28, 2520+
samples; G2 vs l2d's brute_force_exact; G3 -- every witness exact-
replays via engine.backward_predecessor_exact, plus overlap agreement
with L2e's certified per-depth tables). This script REUSES that
module's functions directly (imported, not reimplemented) since it is
already independently gated and this round's job is to run it at a
WIDER d_max, not to re-derive the ladder mechanics. The gates are
RE-RUN here too (cheap, <1s) before trusting any production value, per
house rules (never assume a prior gate still holds without re-checking
in a fresh process).

SCOPE (the order's exact text): t=10..14, lengths (d_max) = 15,16,17,18
-- or to the RSS/time wall, cell by cell, stated. Stop per t when two
consecutive lengths' exact_min agree (early termination for that t;
all t's still get every completed cell reported, not just the
stopping one). RSS cap 8GB (binding house rule); a generous per-cell
wall-clock cap is applied (longer than M3's, since len 17/18 are
larger than M3's len 15/16 and this is expected to cost more).

Frozen prediction (Fable, 55%): t=11/12 stabilize at 19 by len 16
(ALREADY OBSERVED in M3 -- this is a re-confirmation opportunity at
len 17/18, not a fresh test); t=13/14 drop below 31/32 and stabilize
by len 17-18.

Deliverable: the converged (or honestly-still-open) curve of record,
t=10..14, with the stopping length noted per t.
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
    gate_G1, gate_G2, rss_gb, RSS_CAP_GB,
)

WALLCLOCK_CAP_PER_CELL_S = 300.0  # generous per-(t,len) budget, len17/18 > M3's len15/16
TOTAL_WALLCLOCK_BUDGET_S = 3000.0  # ~50min overall honest-wall budget for this script

# Starting point per t: M3's own len<=14/len<=16 certified values (the
# curve of record going into this round).
PRIOR_M3 = {
    10: {14: 16, 15: 16, 16: 16},
    11: {14: 21, 15: 19, 16: 19},
    12: {14: 21, 15: 19, 16: 19},
    13: {14: 31},
    14: {14: 32},
}

LENGTHS = [15, 16, 17, 18]

# cap_for: generous margin above the best value seen so far for this t
# (mirrors m3's cap_for(t) = PRIOR_BEST(t)+4 logic, but seeded from
# M3's OWN results here since those supersede the pre-M3 PRIOR_BEST).
def cap_for(t):
    best_known = min(PRIOR_M3.get(t, {}).values(), default=None)
    if best_known is not None:
        return best_known + 4
    return 40


def main():
    t0_all = time.time()
    print("=== W6N-N4: length convergence of the tax curve (bigint ladder, len 15-18) ===\n")
    print("--- Re-running M3's gates fresh (never assume a prior gate still holds "
          "without re-checking in this process) ---")
    gate_G1()
    gate_G2()
    print()

    rows = []
    curve_of_record = {}   # t -> (value, stopping_length, status)
    total_elapsed = 0.0

    for t in range(10, 15):
        print(f"\n=== t={t} ===")
        seen_this_t = dict(PRIOR_M3.get(t, {}))  # len -> exact_min, seed with M3's own values
        stopped_at = None
        stop_value = None

        for d_max in LENGTHS:
            if total_elapsed > TOTAL_WALLCLOCK_BUDGET_S:
                print(f"  *** TOTAL WALLCLOCK BUDGET ({TOTAL_WALLCLOCK_BUDGET_S}s) EXCEEDED -- "
                      f"honest wall, stopping all further cells (t={t}, d_max={d_max} not run) ***")
                rows.append({
                    "t": t, "d_max": d_max, "T0": t + d_max, "cap": cap_for(t),
                    "exact_min": "", "argmin_len": "", "argmin_a_seq": "",
                    "witness_replay": "", "wall": "TOTAL_BUDGET_EXCEEDED_NOT_RUN",
                    "wallclock_s": "", "peak_rss_gb": round(rss_gb(), 3),
                })
                continue

            if d_max in seen_this_t:
                print(f"  d_max={d_max}: already known from M3 = {seen_this_t[d_max]} (reusing, not rerun)")
                continue

            cap = cap_for(t)
            print(f"  [t={t} d_max={d_max} T0={t+d_max} cap={cap}]:")
            t_run0 = time.time()
            res = run_ladder_bigint(t, d_max, cap, wallclock_cap=WALLCLOCK_CAP_PER_CELL_S)
            wit = extract_witness_bigint(res)
            gmin = res["global_min"]
            replay_ok = None
            if wit is None:
                wit_str = "none in scope"
            elif wit[0] == "BACKTRACK_FAIL":
                wit_str = f"BACKTRACK FAIL {wit[1:]}"
                replay_ok = False
            else:
                d, seq = wit
                replay_ok = exact_replay(seq, t) and sum(a - 2 for a in seq) == gmin
                wit_str = f"len={d} a_seq={seq} replay={'PASS' if replay_ok else '*** FAIL ***'}"
            elapsed = time.time() - t_run0
            total_elapsed += elapsed
            wall_note = f" WALL@{res['wall']}" if res["wall"] else ""
            print(f"    RESULT: exact min (len<={d_max}) = {gmin}; {wit_str}; "
                  f"per-depth {res['per_depth_min']}{wall_note}; {elapsed:.1f}s RSS={rss_gb():.2f}GB")

            rows.append({
                "t": t, "d_max": d_max, "T0": t + d_max, "cap": cap,
                "exact_min": gmin,
                "argmin_len": (wit[0] if wit and wit[0] != "BACKTRACK_FAIL" else ""),
                "argmin_a_seq": (",".join(map(str, wit[1])) if wit and wit[0] != "BACKTRACK_FAIL" else ""),
                "witness_replay": replay_ok,
                "per_depth_min": str(res["per_depth_min"]),
                "wall": str(res["wall"]) if res["wall"] else "",
                "wallclock_s": round(elapsed, 1),
                "peak_rss_gb": round(rss_gb(), 3),
            })

            if gmin is not None:
                seen_this_t[d_max] = gmin

            if res["wall"]:
                print(f"    HONEST WALL hit at t={t} d_max={d_max} -- stopping this t's "
                      f"extension here (later lengths not run for this t).")
                break

            if rss_gb() > RSS_CAP_GB:
                print(f"    RSS CAP ({RSS_CAP_GB}GB) hit -- stopping this t's extension.")
                break

        # convergence check: two CONSECUTIVE lengths (in ascending order,
        # over whatever lengths were actually computed for this t,
        # including the M3-seeded ones) agreeing.
        computed_lengths = sorted(seen_this_t.keys())
        for i in range(len(computed_lengths) - 1):
            l1, l2 = computed_lengths[i], computed_lengths[i + 1]
            if l2 == l1 + 1 and seen_this_t[l1] == seen_this_t[l2]:
                stopped_at = l2
                stop_value = seen_this_t[l2]
                break
        if stopped_at is not None:
            status = f"CONVERGED at len {stopped_at-1}->{stopped_at} (value {stop_value})"
        else:
            status = f"NOT CONVERGED within computed lengths {computed_lengths} " \
                     f"(values {[seen_this_t[l] for l in computed_lengths]})"
        curve_of_record[t] = (min(seen_this_t.values()), stopped_at, status, dict(seen_this_t))
        print(f"  >>> t={t} STATUS: {status}")

    out = HERE / "n4_length_convergence.csv"
    with open(out, "w", newline="") as f:
        fieldnames = list(rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nWrote {out.name} ({len(rows)} rows)")

    # -------------------------------------------------------------
    # Frozen prediction verdict + curve of record
    # -------------------------------------------------------------
    print("\n=== CURVE OF RECORD (t=10..14) ===")
    for t in range(10, 15):
        best_val, stopped_at, status, seen = curve_of_record[t]
        print(f"  t={t}: best-known-min={best_val}; {status}; all lengths seen: {seen}")

    print("\n=== FROZEN PREDICTION VERDICT ===")
    print("t=11/12 stabilize at 19 by len 16 (already observed pre-round, "
          "re-confirmation expected); t=13/14 drop below 31/32 and stabilize "
          "by len 17-18 -- 55% predicted\n")

    t11_conv = curve_of_record[11][1] is not None and curve_of_record[11][3].get(curve_of_record[11][1]) == 19
    t12_conv = curve_of_record[12][1] is not None and curve_of_record[12][3].get(curve_of_record[12][1]) == 19
    print(f"t=11 stabilizes at 19: {t11_conv} (status: {curve_of_record[11][2]})")
    print(f"t=12 stabilizes at 19: {t12_conv} (status: {curve_of_record[12][2]})")

    t13_seen = curve_of_record[13][3]
    t14_seen = curve_of_record[14][3]
    t13_drops = any(v < 31 for v in t13_seen.values())
    t14_drops = any(v < 32 for v in t14_seen.values())
    t13_conv = curve_of_record[13][1] is not None
    t14_conv = curve_of_record[14][1] is not None
    print(f"t=13 drops below 31: {t13_drops} (values seen: {t13_seen}); "
          f"stabilizes by len<=18: {t13_conv} (status: {curve_of_record[13][2]})")
    print(f"t=14 drops below 32: {t14_drops} (values seen: {t14_seen}); "
          f"stabilizes by len<=18: {t14_conv} (status: {curve_of_record[14][2]})")

    all_four_conditions = t11_conv and t12_conv and t13_drops and t13_conv and t14_drops and t14_conv
    verdict = "HIT" if all_four_conditions else "MISS"
    print(f"\nVerdict (ALL of: t11@19, t12@19, t13 drops+stabilizes, t14 drops+stabilizes "
          f"required for HIT): {verdict}")

    print(f"\nTotal wall: {time.time()-t0_all:.1f}s, peak RSS: {rss_gb():.3f} GB "
          f"(cap {RSS_CAP_GB}GB)")


if __name__ == "__main__":
    main()
