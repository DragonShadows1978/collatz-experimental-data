#!/usr/bin/env python3
"""
Death-shell probe (Fable, 2026-07-03) -- reproduces every measurement behind
SYNTHESIS.md "Execution round 2: the death shell" (F6-F9).

Runs entirely on the existing dense automaton (embedding/automaton.py,
exact-arithmetic credits per W1). No oracle, no census, no witness search.
Total runtime: a few minutes, dominated by the C=5 edge confirmation
(modulus 3^16) and the m-sweep at C=23.

Measurements:
  P1  Liveness after one heartbeat is NOT simply {r % 3 != 0}: a residual
      dead set exists for m >= 2, confined to the top of the corridor
      (the "death shell"), growing in both depth and mass with m.
  P2  Universality: the dead set keyed by ceiling-distance (C - d) is
      IDENTICAL, residue-for-residue, across corridor widths C=8/12/23
      (checked m=2..6). The shell is a single ceiling-anchored object S(m);
      C only decides where the floor truncates it.
  P3  Shell == capacity: some terminal state (d, r=1) survives one
      heartbeat iff m <= M_edge(C). Confirmed exactly for C=1..5
      (edges 4, 7, 9, 12, 14) -- 5/5.
  P4  Steps-invariance: the P3 edge is unchanged at 2 and 3 heartbeats
      (C=3, C=4) -- the edge is not an artifact of exactly-53 steps.
  P5  D(m) = min ceiling-distance of a live terminal (wide corridor)
      matches BOTH inverse capacity laws exactly for m=2..12, and the two
      laws' D-sequences first diverge at m=359 (D_rat=149 vs D_irr=148) --
      the exact inverse of the C=148 divergence. No small-m shortcut.
  P6  Trit-locality: liveness after k steps depends only on r mod 3^(k+1).
      Verified densely (all 3^(m-k-1) top-trit lifts of every low-trit
      class have identical liveness) at four (C, m, steps) combinations.

Usage: python3 shell_probe.py | tee shell_probe.log
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "embedding"))

import numpy as np
from automaton import M_edge, run_heartbeat

BETA = 2 - math.log2(3)  # irrational capacity slope, ~0.4150375


def dead_profile(C: int, m: int):
    """Dead states with r % 3 != 0, keyed by ceiling-distance C - d."""
    live_by_d, _ = run_heartbeat(C, m)
    modulus = 3 ** m
    r = np.arange(modulus)
    nz = r % 3 != 0
    prof = {}
    for d in range(C + 1):
        dead_rs = frozenset(int(x) for x in r[nz & ~live_by_d[d]])
        if dead_rs:
            prof[C - d] = dead_rs
    return prof


def p1_shell_sweep():
    print("P1  Death shell vs m at C=23 (dead = live-excluded states with r%3!=0)")
    print(f"    {'m':>3} {'nz-slots':>9} {'dead':>7} {'frac%':>7} {'shell-depth':>11}")
    for m in range(1, 11):
        prof = dead_profile(23, m)
        dead = sum(len(v) for v in prof.values())
        total_nz = 24 * (3 ** m - 3 ** (m - 1))
        depth = max(prof) if prof else 0
        print(f"    {m:>3} {total_nz:>9} {dead:>7} {100 * dead / total_nz:>7.3f} {depth:>11}",
              flush=True)


def p2_universality():
    print("\nP2  Universality: ceiling-relative dead sets identical across C=8/12/23")
    for m in range(2, 7):
        p8, p12, p23 = dead_profile(8, m), dead_profile(12, m), dead_profile(23, m)
        same = p8 == p12 == p23
        print(f"    m={m}: identical={same}  depths={sorted(p23)}", flush=True)
        assert same, f"UNIVERSALITY VIOLATED at m={m}"


def p3_edge_confirmation():
    print("\nP3  Terminal survival edge == M_edge(C), one heartbeat, C=1..5")
    for C in range(1, 6):
        edge = M_edge(C)
        marker = []
        for m in range(1, edge + 3):
            modulus = 3 ** m
            live_by_d, _ = run_heartbeat(C, m)
            alive = any(live_by_d[d][1 % modulus] for d in range(C + 1))
            marker.append("L" if alive else ".")
        marker = "".join(marker)
        ok = marker == "L" * edge + ".."
        print(f"    C={C} M_edge={edge:>2}: {marker}  {'MATCH' if ok else 'MISMATCH'}",
              flush=True)
        assert ok, f"EDGE MISMATCH at C={C}"


def p4_steps_invariance():
    print("\nP4  Edge invariance under 2 and 3 heartbeats (C=3, C=4)")
    for C in (3, 4):
        edge = M_edge(C)
        for steps in (53, 106, 159):
            stat = []
            for m in (edge, edge + 1):
                modulus = 3 ** m
                live_by_d, _ = run_heartbeat(C, m, steps=steps)
                alive = any(live_by_d[d][1 % modulus] for d in range(C + 1))
                stat.append("L" if alive else ".")
            ok = stat == ["L", "."]
            print(f"    C={C} steps={steps}: m={edge}:{stat[0]} m={edge + 1}:{stat[1]}"
                  f"  {'MATCH' if ok else 'MISMATCH'}", flush=True)
            assert ok


def d_rat(m: int) -> int:
    """ceil((22m - 53)/53), clamped at 0 -- inverse of M_edge(C)=floor(53(C+1)/22)."""
    return max(0, -((53 - 22 * m) // 53))


def d_irr(m: int) -> int:
    """Smallest k with k >= m*(2 - log2 3) - 1, via the EXACT integer test
    3^m >= 2^(2m - 1 - k) (monotone in k; no floats)."""
    k = 0
    while not 3 ** m >= 2 ** max(0, 2 * m - 1 - k):
        k += 1
    return k


def p5_D_sequence():
    print("\nP5  D(m) = min ceiling-distance of a live terminal (C=10, one heartbeat)")
    for m in range(2, 13):
        modulus = 3 ** m
        live_by_d, _ = run_heartbeat(10, m)
        alive_depths = [10 - d for d in range(11) if live_by_d[d][1 % modulus]]
        D_emp = min(alive_depths) if alive_depths else None
        ok = D_emp == d_rat(m) == d_irr(m)
        print(f"    m={m:>2}: D_emp={D_emp} D_rat={d_rat(m)} D_irr={d_irr(m)}"
              f"  {'MATCH' if ok else 'MISMATCH'}", flush=True)
        assert ok
    diffs = [(m, d_rat(m), d_irr(m)) for m in range(1, 1000) if d_rat(m) != d_irr(m)]
    print(f"    first D-divergences (m, D_rat, D_irr): {diffs[:5]}")
    assert diffs[0][0] == 359, "expected first divergence at m=359"


def p6_trit_locality():
    print("\nP6  Trit-locality: k-step liveness depends only on r mod 3^(k+1)")
    for C, m, steps in [(4, 8, 5), (4, 10, 7), (3, 12, 9), (8, 9, 6)]:
        live_by_d, _ = run_heartbeat(C, m, steps=steps)
        ok = True
        for d in range(C + 1):
            arr = live_by_d[d].reshape(3 ** (m - steps - 1), 3 ** (steps + 1))
            if not (arr == arr[0]).all():
                ok = False
        print(f"    C={C} m={m} steps={steps}: lift-independent={ok}", flush=True)
        assert ok, f"TRIT-LOCALITY VIOLATED at C={C} m={m} steps={steps}"


if __name__ == "__main__":
    p1_shell_sweep()
    p2_universality()
    p3_edge_confirmation()
    p4_steps_invariance()
    p5_D_sequence()
    p6_trit_locality()
    print("\nAll probes passed.")
