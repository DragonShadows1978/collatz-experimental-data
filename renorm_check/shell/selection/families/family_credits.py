#!/usr/bin/env python3
"""
Design C -- exact credit functions for the three word families, per
W6C_SELECTION_ORDER.md's exactness law: floors are exact integer
arithmetic (isqrt-based), no floats anywhere. Cross-checked against
60-digit Decimal for k=0..100000 before any measurement (function
`cross_check_all` below; also run standalone as a script).

Family 1: alpha = sqrt(3).       floor(k*alpha) = isqrt(3*k^2).
          beta = 2 - sqrt(3) ~= 0.26794919...
Family 2: alpha = sqrt(6) - 1.   floor(k*alpha) = isqrt(6*k^2) - k.
          beta = 3 - sqrt(6) ~= 0.55051025...
Family 3: alpha = sqrt(7) - 1.   floor(k*alpha) = isqrt(7*k^2) - k.
          beta = 3 - sqrt(7) ~= 0.35424868...

Credit c_k = floor((k+1)*alpha) - floor(k*alpha), matching the
Sturmian/Beatty-word convention used throughout shell/toy_word/.
"""

from __future__ import annotations

import math
from decimal import Decimal, getcontext


def floor_k_sqrt3(k: int) -> int:
    return math.isqrt(3 * k * k)


def floor_k_sqrt6m1(k: int) -> int:
    return math.isqrt(6 * k * k) - k


def floor_k_sqrt7m1(k: int) -> int:
    return math.isqrt(7 * k * k) - k


def credit_sqrt3(k: int) -> int:
    return floor_k_sqrt3(k + 1) - floor_k_sqrt3(k)


def credit_sqrt6m1(k: int) -> int:
    return floor_k_sqrt6m1(k + 1) - floor_k_sqrt6m1(k)


def credit_sqrt7m1(k: int) -> int:
    return floor_k_sqrt7m1(k + 1) - floor_k_sqrt7m1(k)


FAMILIES = {
    "sqrt3": {
        "alpha_desc": "sqrt(3)",
        "floor_fn": floor_k_sqrt3,
        "credit_fn": credit_sqrt3,
        "beta_desc": "2 - sqrt(3)",
    },
    "sqrt6m1": {
        "alpha_desc": "sqrt(6) - 1",
        "floor_fn": floor_k_sqrt6m1,
        "credit_fn": credit_sqrt6m1,
        "beta_desc": "3 - sqrt(6)",
    },
    "sqrt7m1": {
        "alpha_desc": "sqrt(7) - 1",
        "floor_fn": floor_k_sqrt7m1,
        "credit_fn": credit_sqrt7m1,
        "beta_desc": "3 - sqrt(7)",
    },
}


def _decimal_floor_k_alpha(k: int, n: int, shift: int, prec: int = 60) -> int:
    """floor(k*alpha) via 60-digit Decimal, alpha = sqrt(n) - shift."""
    getcontext().prec = prec
    alpha = Decimal(n).sqrt() - Decimal(shift)
    return int((Decimal(k) * alpha).to_integral_value(rounding="ROUND_FLOOR"))


def cross_check_family(name: str, kmax: int = 100_000) -> int:
    """Cross-check the isqrt-based floor function against 60-digit Decimal
    for k=0..kmax. Returns mismatch count (must be 0 before any use)."""
    if name == "sqrt3":
        floor_fn = floor_k_sqrt3
        n, shift = 3, 0
    elif name == "sqrt6m1":
        floor_fn = floor_k_sqrt6m1
        n, shift = 6, 1
    elif name == "sqrt7m1":
        floor_fn = floor_k_sqrt7m1
        n, shift = 7, 1
    else:
        raise ValueError(name)

    mismatches = 0
    for k in range(kmax + 1):
        a = floor_fn(k)
        b = _decimal_floor_k_alpha(k, n, shift)
        if a != b:
            mismatches += 1
            if mismatches <= 5:
                print(f"    MISMATCH {name} k={k}: isqrt={a} decimal={b}")
    return mismatches


def cross_check_all(kmax: int = 100_000) -> dict:
    results = {}
    for name in FAMILIES:
        print(f"Cross-check {name}: isqrt floor vs 60-digit Decimal, k=0..{kmax}", flush=True)
        mism = cross_check_family(name, kmax)
        print(f"  {name}: mismatches={mism}  {'PASS' if mism == 0 else 'FAIL'}", flush=True)
        results[name] = mism
    return results


if __name__ == "__main__":
    res = cross_check_all(100_000)
    print("\nSummary:", res)
    if all(v == 0 for v in res.values()):
        print("ALL FAMILIES PASS (0 mismatches, k=0..100000).")
    else:
        print("STOP: at least one family FAILED exactness cross-check.")
        raise SystemExit(1)
