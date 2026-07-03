#!/usr/bin/env python3
"""
Shell-boundary structure probe (Fable, 2026-07-03) -- W6 first execution.
Follows shell_probe.py (F6-F9). Three measurements on the shell's m-growth,
all dense, C=12, m=2..12:

  B1  Heredity: live at m  =>  parent live at m-1 (proof: a valid backward
      chain mod 3^m reduces to one mod 3^(m-1); all maps commute with
      reduction, deficits unchanged). Data: ZERO violations, all levels.
      Consequence: the shell is a MONOTONE growing union of 3-adic subtrees;
      once a class dies its whole subtree is dead. All action is at the
      boundary (live nodes with dying children).
  B2  NO naive cylinder compression: the newly-dead set at level m depends
      on ALL m trits (minimal cylinder depth k = m at every level, every
      corridor depth). The recursion, if finite, is NOT visible in raw
      trit coordinates.
  B3  Structure hints that it IS finite in the right coordinates:
      (a) sofic signal -- distinct live-subtree types (horizon 2) at the
          ceiling saturate: 19, 29, 39, 48, 52, 54 over levels m0=5..10
          (increments 10,10,9,4,2). Deeper corridor depths are noisier
          (finite-size / floor-truncation effects at C=12).
      (b) word-modulation -- per-level die fraction of live-parent children
          tracks the Sturmian credit word: support phases (c_m=1) are local
          minima, drop phases (c_m=2) local peaks, 10/10 levels consistent
          (superimposed on a slow overall decay).
      Together: the level-m -> level-(m+1) boundary map looks like a
      finite transducer DRIVEN BY THE CREDIT WORD (a cocycle over the
      Sturmian shift) -- the renormalization structure, on the right object.

Caveats (binding): horizon-2 type saturation is EVIDENCE of soficity, not
proof -- follower-set stabilization must be checked at increasing horizons
before any transducer is trusted. A learned transducer counts as an
instrument ONLY after passing the validation gates registered in
SYNTHESIS.md W6 (reproduce held-out dense levels + all five known edges).

Usage: python3 boundary_probe.py | tee boundary_probe.log
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "embedding"))

import numpy as np
from automaton import credit, run_heartbeat

C = 12
M_MAX = 12


def load_levels():
    L = {}
    for m in range(2, M_MAX + 1):
        live_by_d, _ = run_heartbeat(C, m)
        L[m] = live_by_d
    return L


def b1_b2_heredity_and_cylinders(L):
    print("B1/B2  Heredity violations + minimal cylinder depth of newly-dead sets")
    print(f"    {'m':>3} {'hered-viol':>10} {'new-dead':>9} {'die-frac%':>9} {'min-k':>6}")
    for m in range(3, M_MAX + 1):
        modulus = 3 ** m
        r = np.arange(modulus)
        nz = r % 3 != 0
        viol = 0
        new_dead_total = 0
        live_parent_children = 0
        min_k = 0
        for d in range(C + 1):
            parent_live = L[m - 1][d][r % (modulus // 3)]
            child_live = L[m][d]
            viol += int((child_live & ~parent_live & nz).sum())
            newly_dead = parent_live & ~child_live & nz
            n_new = int(newly_dead.sum())
            new_dead_total += n_new
            live_parent_children += int((parent_live & nz).sum())
            if n_new:
                for k in range(1, m + 1):
                    blk = 3 ** k
                    arr = newly_dead.reshape(modulus // blk, blk)
                    if (arr == arr[0]).all():
                        break
                min_k = max(min_k, k)
        frac = 100 * new_dead_total / max(1, live_parent_children)
        print(f"    {m:>3} {viol:>10} {new_dead_total:>9} {frac:>9.3f} {min_k:>6}"
              f"   c_{m}={credit(m)}", flush=True)
        assert viol == 0, f"HEREDITY VIOLATED at m={m}"


def b3_sofic_types(L):
    print("\nB3a  Distinct live-subtree types (horizon 2) per level")
    for delta in (0, 2, 4):
        d = C - delta
        counts = []
        for m0 in range(5, M_MAX - 1):
            n = 3 ** m0
            r = np.arange(n)
            own = L[m0][d]
            kids = np.stack([L[m0 + 1][d][r + t * n] for t in range(3)], axis=1)
            gk = np.stack([L[m0 + 2][d][(r + t * n) + s * (3 * n)]
                           for t in range(3) for s in range(3)], axis=1)
            types = np.concatenate([own[:, None], kids, gk], axis=1)
            counts.append(len(np.unique(types[own], axis=0)))
        print(f"    depth {delta}: {counts}  (levels m0=5..{M_MAX - 2})", flush=True)


if __name__ == "__main__":
    levels = load_levels()
    b1_b2_heredity_and_cylinders(levels)
    b3_sofic_types(levels)
    print("\nDone. See SYNTHESIS.md W6 for the transducer-extraction gates.")
