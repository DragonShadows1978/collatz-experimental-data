#!/usr/bin/env python3
"""
W6B T2 -- Toy shell survey, per W6B_TOY_WORD_ORDER.md.

With credit_toy (golden-ratio word): heredity check (must hold -- the
one-line proof is word-independent, so this is a sanity re-confirmation
not a discovery), universality check across C in {8, 12, 23} at
m = 2..6 (expected to hold; report if not -- that would itself be a
finding), and the dead-shell profile vs m at C=12 (mirrors shell_probe.py
P1/P2 exactly, credit_toy substituted for the true word).

Usage: python3 t2_toy_shell_survey.py | tee t2_toy_shell_survey.log
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from toy_automaton import run_heartbeat_generic, credit_toy

M_HEREDITY_MAX = 10
C_HEREDITY = 12


def dead_profile(C: int, m: int):
    """Dead states with r % 3 != 0, keyed by ceiling-distance C - d (toy word)."""
    live_by_d, _ = run_heartbeat_generic(C, m, credit_toy, steps=53)
    modulus = 3 ** m
    r = np.arange(modulus)
    nz = r % 3 != 0
    prof = {}
    for d in range(C + 1):
        dead_rs = frozenset(int(x) for x in r[nz & ~live_by_d[d]])
        if dead_rs:
            prof[C - d] = dead_rs
    return prof


def t2a_heredity():
    print(f"T2a  Heredity (toy word): live at m => parent live at m-1, C={C_HEREDITY}, "
          f"m=3..{M_HEREDITY_MAX}")
    levels = {}
    for m in range(1, M_HEREDITY_MAX + 1):
        live_by_d, _ = run_heartbeat_generic(C_HEREDITY, m, credit_toy, steps=53)
        levels[m] = live_by_d
    ok_all = True
    for m in range(3, M_HEREDITY_MAX + 1):
        modulus = 3 ** m
        r = np.arange(modulus)
        nz = r % 3 != 0
        viol = 0
        for d in range(C_HEREDITY + 1):
            parent_live = levels[m - 1][d][r % (modulus // 3)]
            child_live = levels[m][d]
            viol += int((child_live & ~parent_live & nz).sum())
        ok = viol == 0
        ok_all = ok_all and ok
        print(f"    m={m}: heredity violations={viol}  {'PASS' if ok else 'FAIL'}", flush=True)
    return ok_all


def t2b_universality():
    print("\nT2b  Universality (toy word): dead sets identical across C=8/12/23, m=2..6")
    ok_all = True
    for m in range(2, 7):
        p8, p12, p23 = dead_profile(8, m), dead_profile(12, m), dead_profile(23, m)
        same = p8 == p12 == p23
        ok_all = ok_all and same
        print(f"    m={m}: identical={same}  depths={sorted(p23)}", flush=True)
    if not ok_all:
        print("    NOTE: universality does NOT hold for the toy word -- reported as "
              "a finding in its own right, not glossed over.")
    return ok_all


def t2c_shell_sweep():
    print("\nT2c  Toy dead-shell profile vs m at C=23 (mirrors shell_probe.py P1)")
    print(f"    {'m':>3} {'nz-slots':>9} {'dead':>7} {'frac%':>7} {'shell-depth':>11}")
    for m in range(1, 11):
        prof = dead_profile(23, m)
        dead = sum(len(v) for v in prof.values())
        total_nz = 24 * (3 ** m - 3 ** (m - 1))
        depth = max(prof) if prof else 0
        print(f"    {m:>3} {total_nz:>9} {dead:>7} {100 * dead / total_nz:>7.3f} {depth:>11}",
              flush=True)


if __name__ == "__main__":
    heredity_ok = t2a_heredity()
    universality_ok = t2b_universality()
    t2c_shell_sweep()
    print(f"\nT2 verdict: heredity={heredity_ok}  universality={universality_ok}")
    if not (heredity_ok and universality_ok):
        print("At least one T2 expectation FAILED -- reported plainly. Per the work "
              "order, T2 findings (pass or fail) are informative either way; T3 "
              "proceeds regardless since it targets a different, independent "
              "measurement (D_toy(m)).")
