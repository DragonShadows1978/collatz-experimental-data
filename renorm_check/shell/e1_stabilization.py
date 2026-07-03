#!/usr/bin/env python3
"""
W6 E1 -- Follower-set stabilization (per W6_WORK_ORDER.md, exact spec).

At depths delta = 0, 1, 2, levels m0 = 8, 9, 10: compute type counts at
horizons h = 2, 3, 4. STABLE = the h=3 -> h=4 refinement splits no type
(count unchanged) at every tested (delta, m0). If unstable at h=4, try
h=5 once before stopping.

C=12 (per the work order's definitions section; shell depth stays well
under corridor width at m<=13 per F7 universality).

Usage: python3 e1_stabilization.py | tee e1_stabilization.log
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "embedding"))

import numpy as np
from automaton import run_heartbeat

C = 12
M_DENSE_MAX = 13  # hard ceiling: (C+1)*3^14 exceeds the 4e8-state guard


def load_levels(m_max):
    L = {}
    for m in range(1, m_max + 1):
        live_by_d, _ = run_heartbeat(C, m)
        L[m] = live_by_d
    return L


def horizon_type(L, m0, d, h):
    """Type of every node at level m0, deficit d, horizon h: own liveness
    plus all descendants down to depth h. Shape (3**m0, 1+3+...+3^h)."""
    n = 3 ** m0
    r = np.arange(n)
    cols = [L[m0][d][r][:, None]]
    for depth in range(1, h + 1):
        width = 3 ** depth
        block = np.stack([L[m0 + depth][d][r + t * n] for t in range(width)], axis=1)
        cols.append(block)
    return np.concatenate(cols, axis=1).astype(np.uint8)


def type_count(L, delta, m0, h):
    d = C - delta
    if m0 + h > M_DENSE_MAX:
        return None  # out of reach of dense computation at this ceiling
    types = horizon_type(L, m0, d, h)
    own = L[m0][d]
    if not own.any():
        return 0
    return len(np.unique(types[own], axis=0))


def main():
    print(f"Loading dense levels m=1..{M_DENSE_MAX} at C={C} ...", flush=True)
    L = load_levels(M_DENSE_MAX)

    print("\nE1  Follower-set stabilization: type counts at horizons 2,3,4,(5)")
    print("    stable at (delta, m0) iff h=3->h=4 count is UNCHANGED (exact, no threshold)")

    table = {}
    all_stable = True
    for delta in (0, 1, 2):
        for m0 in (8, 9, 10):
            counts = {}
            for h in (2, 3, 4):
                counts[h] = type_count(L, delta, m0, h)
            row_str = "  ".join(f"h{h}={counts[h]}" for h in (2, 3, 4))
            stable_34 = (counts[3] is not None and counts[4] is not None
                         and counts[3] == counts[4])
            print(f"    delta={delta} m0={m0:>2}: {row_str}"
                  f"  h3->h4 stable={stable_34}", flush=True)
            table[(delta, m0)] = counts
            if counts[4] is None:
                print(f"      (h=4 out of reach: m0+4={m0+4} > {M_DENSE_MAX})")
                all_stable = False
                continue
            if not stable_34:
                all_stable = False

    print(f"\nE1 verdict (h3->h4 exact-match at every tested (delta,m0)): "
          f"{'STABLE' if all_stable else 'UNSTABLE'}")

    if not all_stable:
        print("\nTrying h=5 once at the (delta, m0) pairs where h=4 was reachable, "
              "per the work order's fallback instruction.")
        any_h5 = False
        for (delta, m0), counts in table.items():
            if m0 + 5 > M_DENSE_MAX:
                print(f"    delta={delta} m0={m0}: h=5 needs level {m0+5} > "
                      f"{M_DENSE_MAX} (dense ceiling) -- CANNOT TEST h=5 here.")
                continue
            any_h5 = True
            c5 = type_count(L, delta, m0, 5)
            stable_45 = (counts[4] is not None and c5 == counts[4])
            print(f"    delta={delta} m0={m0}: h4={counts[4]} h5={c5}"
                  f"  h4->h5 stable={stable_45}", flush=True)
        if not any_h5:
            print("\nh=5 is out of reach for EVERY tested (delta, m0) under the "
                  "current dense-computation ceiling (M_DENSE_MAX=13, since "
                  "m0>=8 was required by the work order and m0+5>=13 already "
                  "exceeds it for all m0>=8). Per the work order: STOP and "
                  "report -- not demonstrably sofic at accessible horizons in "
                  "raw coordinates. Ostrowski reindexing is a separate order, "
                  "not attempted here.")
        print("\nE1 FAILED. Per W6_WORK_ORDER.md: STOP. E2 (transducer "
              "extraction) is NOT attempted on an unstable follower set.")
        return False

    print("\nE1 PASSED. Proceeding to E2 would be justified.")
    return True


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
