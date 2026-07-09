#!/usr/bin/env python3
"""G3 core: credit + deficit dual dynamics for climb compatibility."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Reuse G2 orbit primitives
G2 = Path(__file__).resolve().parents[2] / "g2_a1_climb_realizability" / "scripts"
sys.path.insert(0, str(G2))
from g2_core import (  # noqa: E402
    HIGH_RESERVE,
    floor_k_log2_3,
    load_breach_candidates,
    odd_step,
    v2,
)


def credit(k: int) -> int:
    """Exact Sturmian credit c_k via bit_length (no f64)."""
    if k < 0:
        raise ValueError(k)
    fl = lambda kk: 0 if kk == 0 else (3 ** kk).bit_length() - 1
    return fl(k + 1) - fl(k)


def credit_sequence(n: int) -> tuple[int, ...]:
    return tuple(credit(k) for k in range(n))


def verify_lemma3() -> bool:
    seq = credit_sequence(53)
    return seq.count(1) == 22 and seq.count(2) == 31


def walk_orbit_with_credit(x0: int, max_steps: int = 8000) -> list[dict]:
    """Odd-only orbit with a, c, d, upcrossing, dual-check d_next."""
    x = x0
    if x % 2 == 0:
        while x % 2 == 0 and x > 0:
            x //= 2
    A = 0
    C_run = 0
    d = 0  # before any steps, convention d_0 at k=0 pre-step
    steps = []
    for k in range(max_steps):
        if x == 1:
            break
        c = credit(k)
        nxt, a = odd_step(x)
        A += a
        d_next = floor_k_log2_3(k + 1) - A
        # dual formula from previous d: when k=0, d_prev=0? 
        # d after k steps = floor(k alpha) - A_{k}
        # d_next should equal d + c - a where d is deficit AFTER k steps... 
        # At start of step k, current deficit is d_k = floor(k α) - A_k (A_k sum of first k exponents).
        d_before = floor_k_log2_3(k) - (A - a)  # A already includes a; A_before = A-a
        d_dual = d_before + c - a
        is_up = d_next > C_run
        if is_up:
            C_run = d_next
        steps.append(
            {
                "k": k,
                "x": x,
                "a": a,
                "c": c,
                "d_before": d_before,
                "d_after": d_next,
                "d_dual": d_dual,
                "C_run_after": C_run,
                "upcrossing": is_up,
                "dual_ok": d_dual == d_next,
            }
        )
        x = nxt
    return steps


def dual_a1_path(L: int, k0: int, d0: int) -> dict:
    """Forced a=1 for L steps from phase k0, start deficit d0."""
    d = d0
    C = d0
    min_d = d0
    n_virt_up = 0
    stayed = True
    path = [d0]
    for i in range(L):
        c = credit(k0 + i)
        d = d + c - 1  # a=1
        path.append(d)
        if d < min_d:
            min_d = d
        if d < 0:
            stayed = False
        if d > C:
            n_virt_up += 1
            C = d
    return {
        "L": L,
        "k0": k0,
        "d0": d0,
        "d_final": d,
        "min_d": min_d,
        "n_virt_up": n_virt_up,
        "stayed_nonneg": stayed and min_d >= 0,
        "path_head": path[: min(8, len(path))],
    }


def mersenne_prefix(L: int) -> dict:
    """x = 2^{L+1}-1; first L steps must be a=1; measure ups and max_d."""
    x = (1 << (L + 1)) - 1
    steps = walk_orbit_with_credit(x, max_steps=L + max(500, 5 * L))
    prefix = steps[:L]
    all_a1 = all(s["a"] == 1 for s in prefix) if len(prefix) == L else False
    ups = sum(1 for s in prefix if s["upcrossing"])
    max_d_pref = max((s["d_after"] for s in prefix), default=0)
    max_d_ext = max((s["d_after"] for s in steps), default=0)
    return {
        "L": L,
        "x": x,
        "prefix_all_a1": all_a1,
        "n_upcrossings_prefix": ups,
        "ups_over_L": ups / L if L else 0,
        "max_d_prefix": max_d_pref,
        "max_d_extended": max_d_ext,
        "n_steps_run": len(steps),
    }


def consec_up_streaks(steps: list[dict]) -> list[int]:
    """Lengths of maximal consecutive upcrossing steps."""
    streaks = []
    i = 0
    n = len(steps)
    while i < n:
        if not steps[i]["upcrossing"]:
            i += 1
            continue
        j = i
        while j < n and steps[j]["upcrossing"]:
            j += 1
        streaks.append(j - i)
        i = j
    return streaks
