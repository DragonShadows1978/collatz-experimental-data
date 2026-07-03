#!/usr/bin/env python3
"""
W6B T1 -- Port sanity (controls first), per W6B_TOY_WORD_ORDER.md.

Reuses run_heartbeat_generic with the TRUE word (credit_fn = the real
automaton's credit(k), log2(3)-driven) and confirms it reproduces:
  - D(m) for m=2..12 (SYNTHESIS F8 / shell_probe.py P5)
  - the C=1..5 edges (M_edge(C) = 4,7,9,12,14)
bit-for-bit against the known results, using the SAME code path that
will drive the toy-word run (T2/T3) -- only the credit function differs.
Any mismatch = STOP per the work order.

Also cross-checks credit_toy(k) = floor(k*phi) via isqrt against a
60-digit Decimal computation for k=0..100000 (the toy-word analogue of
W1's exact-arithmetic mandate).

Usage: python3 t1_port_sanity.py | tee t1_port_sanity.log
"""

from __future__ import annotations

import math
import sys
from decimal import Decimal, getcontext
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "embedding"))
sys.path.insert(0, str(Path(__file__).parent))

from automaton import credit as credit_true, M_edge
from toy_automaton import run_heartbeat_generic, credit_toy


def t1a_credit_toy_exactness():
    print("T1a  credit_toy(k) exactness: isqrt formula vs 60-digit Decimal, k=0..100000")
    getcontext().prec = 60
    phi = (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)

    def floor_k_phi_decimal(k):
        return int((Decimal(k) * phi).to_integral_value(rounding="ROUND_FLOOR"))

    mismatches = 0
    for k in range(0, 100001):
        a = (k + math.isqrt(5 * k * k)) // 2
        b = floor_k_phi_decimal(k)
        if a != b:
            mismatches += 1
            if mismatches <= 5:
                print(f"    MISMATCH k={k}: isqrt={a} decimal={b}")
    ok = mismatches == 0
    print(f"    checked k=0..100000, mismatches={mismatches}  {'PASS' if ok else 'FAIL'}",
          flush=True)
    assert ok, "credit_toy is not exact -- STOP per work order"
    return ok


def d_rat_true(m):
    return max(0, -((53 - 22 * m) // 53))


def d_irr_true(m):
    k = 0
    while not 3 ** m >= 2 ** max(0, 2 * m - 1 - k):
        k += 1
    return k


def t1b_D_sequence_true_word():
    print("\nT1b  D(m) via run_heartbeat_generic + true word, C=10, m=2..12"
          " (must match shell_probe.py P5 exactly)")
    ok_all = True
    for m in range(2, 13):
        modulus = 3 ** m
        live_by_d, _ = run_heartbeat_generic(10, m, credit_true, steps=53)
        alive_depths = [10 - d for d in range(11) if live_by_d[d][1 % modulus]]
        D_emp = min(alive_depths) if alive_depths else None
        ok = D_emp == d_rat_true(m) == d_irr_true(m)
        ok_all = ok_all and ok
        print(f"    m={m:>2}: D_emp={D_emp} D_rat={d_rat_true(m)} D_irr={d_irr_true(m)}"
              f"  {'MATCH' if ok else 'MISMATCH'}", flush=True)
    assert ok_all, "D(m) port mismatch on the TRUE word -- STOP per work order"
    return ok_all


def t1c_edges_true_word():
    print("\nT1c  Edges via run_heartbeat_generic + true word, C=1..5"
          " (must match automaton.M_edge exactly)")
    ok_all = True
    for C in range(1, 6):
        edge = M_edge(C)
        marker = []
        for m in range(1, edge + 3):
            modulus = 3 ** m
            live_by_d, _ = run_heartbeat_generic(C, m, credit_true, steps=53)
            alive = any(live_by_d[d][1 % modulus] for d in range(C + 1))
            marker.append("L" if alive else ".")
        marker = "".join(marker)
        ok = marker == "L" * edge + ".."
        ok_all = ok_all and ok
        print(f"    C={C} M_edge={edge:>2}: {marker}  {'MATCH' if ok else 'MISMATCH'}",
              flush=True)
    assert ok_all, "Edge port mismatch on the TRUE word -- STOP per work order"
    return ok_all


if __name__ == "__main__":
    a = t1a_credit_toy_exactness()
    b = t1b_D_sequence_true_word()
    c = t1c_edges_true_word()
    print(f"\nT1 verdict: credit_toy exact={a}  D(m) port match={b}  edges port match={c}")
    if a and b and c:
        print("T1 PASSED. Proceeding to T2/T3 with the toy word is justified.")
    else:
        print("T1 FAILED. STOP per work order -- do not proceed to T2/T3.")
        sys.exit(1)
