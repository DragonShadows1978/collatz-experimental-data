#!/usr/bin/env python3
"""
W6N-N4b -- Post-hoc convergence verdict correction for N4.

WHY THIS EXISTS (honest, not hidden): n4_length_convergence.py's
in-run STATUS line scans for the FIRST pair of consecutive lengths
that agree, anywhere in the length sequence -- and the t=10 data
immediately exposed that as both a reporting bug AND a substantive
methodological finding: t=10 agrees at len 14=15=16=17 (all 16) and
then DROPS to 15 at len 18. "Two consecutive lengths agree" (the
order's own suggested stopping rule) is therefore demonstrably NOT a
sound convergence criterion on this curve -- a plateau of width 4 can
still break. The order's stopping rule was applied as specified
(well, over-applied: the implementation ran ALL cells rather than
early-stopping, which is precisely what caught the t=10 late drop
that early-stopping would have certified as converged).

This script reads n4_length_convergence.csv + the M3-seeded prior
values, reconstructs the full per-t length series, and reports:
  (i) the honest per-t verdict: value at the longest computed length,
      whether the LAST two computed lengths agree, and whether any
      later length ever broke an earlier agreement (plateau-break
      events, the t=10 phenomenon);
 (ii) the corrected curve of record with per-scope labels.
Every witness cited is exact-replayed here as well (independent
from-scratch replay via engine primitives -- the round's standing
discipline), including a per-t precision check (the exact largest t
each witness serves, catching multi-trit plateau witnesses).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

HERE = Path(__file__).parent
W6E = HERE.parent / "w6e"
sys.path.insert(0, str(W6E))

from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402

PRIOR_M3 = {
    10: {14: 16, 15: 16, 16: 16},
    11: {14: 21, 15: 19, 16: 19},
    12: {14: 21, 15: 19, 16: 19},
    13: {14: 31},
    14: {14: 32},
}


def replay_precision(seq):
    """Exact replay; returns (legal, cost, final_v, max_t_served)."""
    v = 1
    for a in seq:
        p = forced_parity_for_backward_step(v)
        if p is None or (a % 2 == 0) != (p == 0):
            return False, None, None, None
        v = backward_predecessor_exact(v, a)
    cost = sum(a - 2 for a in seq)
    t_max = 0
    while v % (3 ** (t_max + 1)) == 1:
        t_max += 1
    return True, cost, v, t_max


def main():
    rows = []
    with open(HERE / "n4_length_convergence.csv", newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)

    series = {t: dict(PRIOR_M3.get(t, {})) for t in range(10, 15)}
    walled = {}   # (t, d) -> wall string, for cells whose census is INCOMPLETE
    witnesses = {}
    for r in rows:
        if r["exact_min"] == "":
            continue
        t = int(r["t"])
        d = int(r["d_max"])
        if r.get("wall"):
            # A walled cell is NOT a completed length census: its value
            # covers only the depths that finished before the wall, so it
            # is an upper bound for its scope, not the scope's exact min.
            # Exclude from the convergence series; record separately.
            walled[(t, d)] = (int(r["exact_min"]), r["wall"])
            continue
        series[t][d] = int(r["exact_min"])
        if r["argmin_a_seq"]:
            witnesses[(t, d)] = tuple(int(x) for x in r["argmin_a_seq"].split(","))

    # Also fold in n4c tight-cap closure results if present (sound-exact
    # cells only), so the corrected verdict uses the best certified data.
    n4c_path = HERE / "n4c_tight_cap_closure.csv"
    if n4c_path.exists():
        with open(n4c_path, newline="") as f:
            for r in csv.DictReader(f):
                if r["exact_min"] == "" or r.get("wall"):
                    continue
                t = int(r["t"])
                d = int(r["d_max"])
                v = int(r["exact_min"])
                if d not in series[t] or v < series[t][d]:
                    series[t][d] = v
                if r["argmin_a_seq"]:
                    witnesses[(t, d)] = tuple(int(x) for x in r["argmin_a_seq"].split(","))
        print("(n4c tight-cap closure results folded in)\n")

    print("=== W6N-N4b: corrected convergence verdicts ===\n")

    if walled:
        print("--- Walled (INCOMPLETE) cells, excluded from convergence series ---")
        for (t, d), (v, wall) in sorted(walled.items()):
            print(f"  t={t} d_max={d}: reported {v} but WALL={wall} -- value covers "
                  f"only pre-wall depths; upper bound for scope, NOT the scope's min")
        print()

    print("--- Witness exact-replay (independent, incl. max-t-served) ---")
    n_replay_fail = 0
    for (t, d), seq in sorted(witnesses.items()):
        legal, cost, v, t_max = replay_precision(seq)
        claimed = series[t][d]
        ok = legal and cost == claimed and t_max >= t
        if not ok:
            n_replay_fail += 1
        print(f"  t={t} d_max={d}: len={len(seq)} cost={cost} (claimed {claimed}) "
              f"max_t_served={t_max} {'PASS' if ok else '*** FAIL ***'}")
    print(f"  Replay failures: {n_replay_fail}\n")

    print("--- Corrected per-t verdicts ---")
    curve = {}
    for t in range(10, 15):
        s = series[t]
        lens = sorted(s.keys())
        vals = [s[l] for l in lens]
        # last-two-lengths agreement (the only defensible "converged" call)
        last_two_agree = len(lens) >= 2 and lens[-1] == lens[-2] + 1 and s[lens[-1]] == s[lens[-2]]
        # plateau-break events: any l where s[l] < min over shorter lengths
        breaks = []
        best_so_far = None
        for l in lens:
            if best_so_far is not None and s[l] < best_so_far:
                breaks.append((l, best_so_far, s[l]))
            best_so_far = s[l] if best_so_far is None else min(best_so_far, s[l])
        status = "CONVERGED (last two lengths agree)" if last_two_agree else "NOT CONVERGED"
        if breaks:
            status += f"; plateau-break(s) at {breaks} (len, prior best, new)"
        curve[t] = (min(vals), lens[-1], last_two_agree, status)
        print(f"  t={t}: series {dict(sorted(s.items()))}")
        print(f"        best={min(vals)} at longest len {lens[-1]}; {status}")

    print("\n--- CORRECTED CURVE OF RECORD (t=10..14) ---")
    for t in range(10, 15):
        best, longest, conv, status = curve[t]
        label = f"len<={longest}" + (" CONVERGED" if conv else " STILL-OPEN (upper envelope)")
        print(f"  t={t}: {best}  [{label}]")

    print("\n--- Frozen prediction re-verdict on corrected data ---")
    print("(t=11/12 stabilize at 19 by len 16; t=13/14 drop below 31/32 and "
          "stabilize by len 17-18 -- 55%)")
    t11 = curve[11]
    t12 = curve[12]
    t13 = curve[13]
    t14 = curve[14]
    c1 = t11[0] == 19 and t11[2]
    c2 = t12[0] == 19 and t12[2]
    c3 = t13[0] < 31 and t13[2]
    c4 = t14[0] < 32 and t14[2]
    print(f"  t=11 stabilized at 19: {c1}")
    print(f"  t=12 stabilized at 19: {c2}")
    print(f"  t=13 dropped+stabilized: {c3} (best {t13[0]}, converged {t13[2]})")
    print(f"  t=14 dropped+stabilized: {c4} (best {t14[0]}, converged {t14[2]})")
    print(f"  Conjunction verdict: {'HIT' if (c1 and c2 and c3 and c4) else 'MISS'}")
    print(f"  NOTE: t=10 (outside the prediction's own scope) BROKE a width-4 "
          f"plateau at len 18 (16 -> 15) -- the stopping rule itself is refuted "
          f"as a certification criterion regardless of the conjunction verdict.")


if __name__ == "__main__":
    main()
