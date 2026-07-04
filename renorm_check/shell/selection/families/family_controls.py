#!/usr/bin/env python3
"""
Design C step (c) -- quick controls, per W6C_SELECTION_ORDER.md's
shared-machinery clause (same checks as W6B T2 / shell_probe.py P1-P2):

  - Heredity: live at m ==> parent live at m-1 (zero violations expected),
    m=3..7, C=8.
  - Universality: the dead-set keyed by ceiling-distance (C-d) is
    identical across corridor widths C=8 vs C=12, m=2..5.

Run once per family (three word families share the same automaton
mechanics -- only the credit function differs), using
toy_automaton.run_heartbeat_generic exactly as imported, no
reimplementation of the automaton itself.

Usage: python3 family_controls.py | tee family_controls.log
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "toy_word"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "embedding"))

from toy_automaton import run_heartbeat_generic
from family_credits import FAMILIES

STEPS = 53


def dead_set_by_ceildist(live_by_d: dict, C: int, m: int):
    """Dead residues with r % 3 != 0, keyed by ceiling-distance C-d.
    Returns dict: ceil_dist -> frozenset of residues dead at that depth."""
    modulus = 3 ** m
    out = {}
    for d in range(C + 1):
        arr = live_by_d[d]
        dead_idx = [r for r in range(modulus) if r % 3 != 0 and not arr[r]]
        out[C - d] = frozenset(dead_idx)
    return out


def heredity_check(name: str, credit_fn, m_lo: int, m_hi: int, C: int):
    """Live at m => parent (r mod 3^(m-1)) live at m-1. Zero violations
    expected (word-independent proof, per SYNTHESIS F6/W6 B1)."""
    print(f"  [{name}] Heredity check m={m_lo}..{m_hi}, C={C}")
    violations = 0
    prev_live = None
    prev_m = None
    for m in range(m_lo, m_hi + 1):
        live_by_d, _ = run_heartbeat_generic(C, m, credit_fn, steps=STEPS)
        if prev_live is not None:
            modulus_prev = 3 ** prev_m
            for d in range(C + 1):
                arr = live_by_d[d]
                parr = prev_live[d]
                modulus = 3 ** m
                for r in range(modulus):
                    if arr[r]:
                        parent_r = r % modulus_prev
                        if not parr[parent_r]:
                            violations += 1
        prev_live = live_by_d
        prev_m = m
    print(f"  [{name}] Heredity violations m={m_lo}..{m_hi} @ C={C}: {violations}")
    return violations


def universality_check(name: str, credit_fn, m_lo: int, m_hi: int, C_list):
    """Dead set keyed by ceiling-distance identical across corridor
    widths in C_list, for m=m_lo..m_hi."""
    print(f"  [{name}] Universality check m={m_lo}..{m_hi}, C in {C_list}")
    mismatches = 0
    for m in range(m_lo, m_hi + 1):
        dead_sets = {}
        for C in C_list:
            live_by_d, _ = run_heartbeat_generic(C, m, credit_fn, steps=STEPS)
            dead_sets[C] = dead_set_by_ceildist(live_by_d, C, m)
        base_C = C_list[0]
        base = dead_sets[base_C]
        for C in C_list[1:]:
            other = dead_sets[C]
            common_depths = set(base.keys()) & set(other.keys())
            for depth in common_depths:
                if base[depth] != other[depth]:
                    mismatches += 1
                    print(f"    MISMATCH m={m} depth={depth}: C={base_C} vs C={C} differ")
    print(f"  [{name}] Universality mismatches m={m_lo}..{m_hi}: {mismatches}")
    return mismatches


def run_family_controls(name: str):
    credit_fn = FAMILIES[name]["credit_fn"]
    print(f"\n=== Controls for family {name} ===", flush=True)
    hered_viol = heredity_check(name, credit_fn, m_lo=3, m_hi=7, C=8)
    univ_mis = universality_check(name, credit_fn, m_lo=2, m_hi=5, C_list=[8, 12])
    ok = (hered_viol == 0) and (univ_mis == 0)
    print(f"  [{name}] Controls: heredity={'PASS' if hered_viol==0 else 'FAIL'} "
          f"universality={'PASS' if univ_mis==0 else 'FAIL'}", flush=True)
    return {"heredity_violations": hered_viol, "universality_mismatches": univ_mis, "pass": ok}


def main():
    results = {}
    for name in FAMILIES:
        results[name] = run_family_controls(name)
    print("\n=== Controls summary ===")
    for name, r in results.items():
        print(f"  {name}: {r}")
    all_pass = all(r["pass"] for r in results.values())
    if not all_pass:
        print("STOP: at least one family failed controls.")
        raise SystemExit(1)
    print("ALL FAMILIES PASS quick controls.")


if __name__ == "__main__":
    main()
