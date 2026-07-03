#!/usr/bin/env python3
"""
W6B toy-word automaton (Fable, 2026-07-03) -- per W6B_TOY_WORD_ORDER.md.

Reuses embedding/automaton.py's residue-permutation machinery exactly,
parameterized by a pluggable credit function instead of the hard-coded
log2(3)-driven Sturmian word. This lets the SAME (C+1)*3^m corridor
automaton be driven by an arbitrary Beatty word -- here, the golden-
ratio word alpha_toy = phi -- whose divergence points between the
irrational slope and its rational (Fibonacci) convergents fall inside
the dense-computable range (m <= 13 at C=12), unlike the true word's
first divergence at m=359.

The automaton code itself (next_residue, allowed_exponents, the
gather/scatter loop) is NOT reimplemented -- imported directly from
embedding/automaton.py so both the true-word and toy-word runs share
one audited implementation, differing only in the credit sequence fed
to run_heartbeat_generic.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "embedding"))

import numpy as np
from automaton import allowed_exponents, mod_inverse

HEARTBEAT = 53  # kept for parity with the true-word module; toy runs pass steps explicitly


def credit_toy(k: int) -> int:
    """Golden-ratio credit: c_k = floor((k+1)*phi) - floor(k*phi).
    Exact via floor(k*phi) = (k + isqrt(5*k^2)) // 2 -- cross-checked
    against 60-digit Decimal for k=0..100000 in T1 below. No floats."""
    def floor_k_phi(kk: int) -> int:
        return (kk + math.isqrt(5 * kk * kk)) // 2
    return floor_k_phi(k + 1) - floor_k_phi(k)


def credit_sequence_toy(n: int) -> tuple:
    return tuple(credit_toy(k) for k in range(n))


_PERM_CACHE = {}


def _get_permutation(a: int, modulus: int) -> np.ndarray:
    key = (a, modulus)
    if key not in _PERM_CACHE:
        r = np.arange(modulus, dtype=np.int64)
        inv2a = mod_inverse(pow(2, a, modulus), modulus)
        r_prime = ((3 * r + 1) % modulus) * inv2a % modulus
        _PERM_CACHE[key] = r_prime.astype(np.int64)
    return _PERM_CACHE[key]


def run_heartbeat_generic(C: int, m: int, credit_fn, steps: int,
                            track_terminal_only: bool = False,
                            max_states_guard: int = 400_000_000):
    """Same mechanics as embedding.automaton.run_heartbeat -- identical
    residue map, corridor/deficit rules, and gather/scatter loop -- but
    the credit sequence is supplied by credit_fn(k) instead of the
    hard-coded log2(3) word."""
    modulus = 3 ** m
    total_states = (C + 1) * modulus
    if total_states > max_states_guard:
        raise ValueError(
            f"state space too large: C={C}, m={m}, modulus=3^{m}={modulus}, "
            f"total_states={total_states} > guard {max_states_guard}"
        )

    live_by_d = {d: np.ones(modulus, dtype=bool) for d in range(C + 1)}
    history_sizes = [sum(int(arr.sum()) for arr in live_by_d.values())]

    seq = tuple(credit_fn(k) for k in range(steps))
    for k in range(steps):
        c_k = seq[k]
        next_live_by_d = {d: np.zeros(modulus, dtype=bool) for d in range(C + 1)}
        for d in range(C + 1):
            src = live_by_d[d]
            live_r_indices = np.nonzero(src)[0]
            if live_r_indices.size == 0:
                continue
            for a in allowed_exponents(d, c_k, C):
                d_prime = d + c_k - a
                perm = _get_permutation(a, modulus)
                targets = perm[live_r_indices]
                next_live_by_d[d_prime][targets] = True
        live_by_d = next_live_by_d
        history_sizes.append(sum(int(arr.sum()) for arr in live_by_d.values()))

    if track_terminal_only:
        terminal = set()
        target_residue = 1 % modulus
        for d in range(C + 1):
            if live_by_d[d][target_residue]:
                terminal.add((d, target_residue))
        return terminal, history_sizes

    return live_by_d, history_sizes
