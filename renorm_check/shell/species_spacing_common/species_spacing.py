#!/usr/bin/env python3
"""Exact species spacing helpers + prime sieve for G15+ chain."""
from __future__ import annotations
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "descent_rule"))
from descent_common import species_member  # noqa: E402


def x_k(k: int) -> int:
    return species_member(k)


def gap_k(k: int) -> int:
    """x_{k+1} - x_k = 4^k exactly."""
    return 4**k


def verify_gap_identity(k_max: int = 80) -> bool:
    for k in range(1, k_max + 1):
        if x_k(k + 1) - x_k(k) != gap_k(k):
            return False
        if x_k(k + 1) - x_k(k) != 4**k:
            return False
    return True


def count_species_le(X: int) -> int:
    """#{k>=1: x_k <= X}."""
    if X < 1:
        return 0
    # k max: (4^k-1)/3 <= X ⇒ 4^k <= 3X+1
    k = 1
    while x_k(k) <= X:
        k += 1
        if k > 10_000:
            break
    return k - 1


def sieve_primes(limit: int) -> list[int]:
    if limit < 2:
        return []
    n = limit + 1
    is_p = bytearray(b"\x01") * n
    is_p[0:2] = b"\x00\x00"
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            step = i
            start = i * i
            is_p[start:n:step] = b"\x00" * ((n - 1 - start) // step + 1)
    return [i for i in range(2, n) if is_p[i]]


def prime_gaps(primes: list[int]) -> list[int]:
    return [primes[i + 1] - primes[i] for i in range(len(primes) - 1)]


def ln_int(n: int) -> float:
    """Natural log via bit_length + float for large n (display/ratios only)."""
    if n <= 0:
        return float("nan")
    # math.log works for ints until huge; for safety use log2
    return math.log(n) if n.bit_length() < 1000 else n.bit_length() * math.log(2)
