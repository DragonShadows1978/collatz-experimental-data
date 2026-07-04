#!/usr/bin/env python3
"""
W6C Design B, B1 -- controls, per W6C_SELECTION_ORDER.md.

Heredity: live at m => parent live at m-1, m=3..8, C=8 (zero violations
required). Universality: ceiling-relative dead sets identical across
C=8 vs C=12, m=2..6. Mirrors W6B's T2a/T2b exactly, credit_sqrt2
substituted for credit_toy.

Usage: python3 b1_controls.py | tee b1_controls.log
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from sqrt2_automaton import run_heartbeat_generic, credit_sqrt2

M_HEREDITY_MAX = 8
C_HEREDITY = 8


def dead_profile(C: int, m: int):
    """Dead states with r % 3 != 0, keyed by ceiling-distance C - d."""
    live_by_d, _ = run_heartbeat_generic(C, m, credit_sqrt2, steps=53)
    modulus = 3 ** m
    r = np.arange(modulus)
    nz = r % 3 != 0
    prof = {}
    for d in range(C + 1):
        dead_rs = frozenset(int(x) for x in r[nz & ~live_by_d[d]])
        if dead_rs:
            prof[C - d] = dead_rs
    return prof


def b1a_heredity():
    print(f"B1a  Heredity (sqrt2 word): live at m => parent live at m-1, "
          f"C={C_HEREDITY}, m=3..{M_HEREDITY_MAX}")
    levels = {}
    for m in range(1, M_HEREDITY_MAX + 1):
        live_by_d, _ = run_heartbeat_generic(C_HEREDITY, m, credit_sqrt2, steps=53)
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


def b1b_universality():
    print("\nB1b  Universality (sqrt2 word): dead sets identical across "
          "C=8 vs C=12, m=2..6")
    ok_all = True
    for m in range(2, 7):
        p8, p12 = dead_profile(8, m), dead_profile(12, m)
        same = p8 == p12
        ok_all = ok_all and same
        print(f"    m={m}: identical={same}  depths(C=12)={sorted(p12)}", flush=True)
    if not ok_all:
        print("    NOTE: universality does NOT hold for the sqrt2 word -- "
              "reported as a finding in its own right, not glossed over.")
    return ok_all


if __name__ == "__main__":
    heredity_ok = b1a_heredity()
    universality_ok = b1b_universality()
    print(f"\nB1 verdict: heredity={heredity_ok}  universality={universality_ok}")
    if not (heredity_ok and universality_ok):
        print("At least one B1 control FAILED -- reported plainly. Per the "
              "work order, B1 is a control check; a failure here would be "
              "itself a finding but does not by construction block B2/B3 "
              "(which target the independent D_sqrt2(m) measurement) -- "
              "however any failure will be surfaced prominently in RESULTS_B.md.")
