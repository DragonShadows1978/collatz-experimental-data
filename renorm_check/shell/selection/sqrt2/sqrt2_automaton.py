#!/usr/bin/env python3
"""
W6C Design B -- sqrt(2) credit word + automaton wiring.

Reuses embedding/automaton.py's residue-permutation machinery (via
shell/toy_word/toy_automaton.py's run_heartbeat_generic, T1-validated
in W6B) exactly, parameterized by the sqrt(2) Beatty word instead of
the golden-ratio toy word or the true log2(3) word.

Exactness law (W6C work order, binding): credit words only from
quadratic surds so floors are exact integer arithmetic --
floor(k*sqrt2) = isqrt(2*k^2), no floats anywhere. Cross-checked
against 60-digit Decimal for k=0..100000 in cross_check_credit_sqrt2()
below -- must be run and must PASS before any measurement (see
run_crosscheck.py).

alpha = sqrt(2). beta = 2 - sqrt(2) ~= 0.585786.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "toy_word"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "embedding"))

from toy_automaton import run_heartbeat_generic  # noqa: F401  (re-exported for callers)


def floor_k_sqrt2(k: int) -> int:
    """floor(k*sqrt(2)), exact: isqrt(2*k^2). No floats."""
    return math.isqrt(2 * k * k)


def credit_sqrt2(k: int) -> int:
    """sqrt(2) credit: c_k = floor((k+1)*sqrt2) - floor(k*sqrt2).
    Exact via floor_k_sqrt2. c_k in {1, 2} (Beatty word, slope in (1,2))."""
    return floor_k_sqrt2(k + 1) - floor_k_sqrt2(k)


def credit_sequence_sqrt2(n: int) -> tuple:
    return tuple(credit_sqrt2(k) for k in range(n))


def cross_check_credit_sqrt2(n: int = 100_000) -> int:
    """Cross-check floor_k_sqrt2 against 60-digit Decimal for k=0..n.
    Returns mismatch count (must be 0 before any measurement, per the
    W6C exactness law)."""
    from decimal import Decimal, getcontext
    getcontext().prec = 60
    sqrt2_dec = Decimal(2).sqrt()

    def floor_k_sqrt2_decimal(k: int) -> int:
        return int((Decimal(k) * sqrt2_dec).to_integral_value(rounding="ROUND_FLOOR"))

    mismatches = 0
    for k in range(0, n + 1):
        a = floor_k_sqrt2(k)
        b = floor_k_sqrt2_decimal(k)
        if a != b:
            mismatches += 1
    return mismatches
