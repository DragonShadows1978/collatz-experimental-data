#!/usr/bin/env python3
"""G1 shared instrument — reuses embedding/automaton + toy generic heartbeat.

Exact credits only (W1). No f64 floors for credit letters.
"""
from __future__ import annotations

import math
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # renorm_check/
sys.path.insert(0, str(ROOT / "embedding"))
sys.path.insert(0, str(ROOT / "shell" / "toy_word"))

from automaton import (  # noqa: E402
    M_edge,
    credit as credit_true,
    credit_sequence,
    verify_lemma3,
)
from toy_automaton import run_heartbeat_generic  # noqa: E402

HEARTBEAT = 53
SUPPORT = 22


def d_rat(m: int) -> int:
    """Inverse of M_edge: max(0, ceil((22m-53)/53)) via shell_probe form."""
    return max(0, -((53 - 22 * m) // 53))


def d_real_mirror(m: int) -> int:
    """SYNTHESIS D_real(m) = floor((22m-1)/53)."""
    return (22 * m - 1) // 53 if m >= 1 else 0


def d_irr(m: int) -> int:
    """shell_probe irrational inverse via exact integer test."""
    k = 0
    while not 3 ** m >= 2 ** max(0, 2 * m - 1 - k):
        k += 1
    return k


def make_mechanical_2253():
    """22/53 mechanical word: c_k = floor(P(k+1)/q)-floor(Pk/q), P=2q-p=84.

    Source convention: renorm_check/shell/underlock/w6e/e2_phase_pinning.py
    make_mechanical_word(22, 53).
    """
    p, q = 22, 53
    P = 2 * q - p  # 84

    def credit_fn(k: int, P=P, q=q) -> int:
        return (P * (k + 1)) // q - (P * k) // q

    return credit_fn, P, p, q


def make_hybrid(credit_a, credit_b, N: int | None):
    """Forward hybrid: a for k < N, b for k >= N. N=None => pure a forever."""

    def credit_fn(k: int, N=N) -> int:
        if N is None or k < N:
            return credit_a(k)
        return credit_b(k)

    return credit_fn


def make_reverse_hybrid(credit_a, credit_b, N: int | None):
    """Reverse: b for k < N, a for k >= N (periodic first if a=true, b=period)."""

    def credit_fn(k: int, N=N) -> int:
        if N is None or k < N:
            return credit_b(k)
        return credit_a(k)

    return credit_fn


def D_emp(C: int, m: int, credit_fn, steps: int = HEARTBEAT) -> int | None:
    """Min ceiling-distance of a live terminal after `steps` (shell_probe P5)."""
    live_by_d, _ = run_heartbeat_generic(C, m, credit_fn, steps=steps)
    modulus = 3 ** m
    target = 1 % modulus
    alive_depths = [C - d for d in range(C + 1) if live_by_d[d][target]]
    return min(alive_depths) if alive_depths else None


def terminal_survives(C: int, m: int, credit_fn, steps: int = HEARTBEAT) -> bool:
    live_by_d, _ = run_heartbeat_generic(C, m, credit_fn, steps=steps)
    modulus = 3 ** m
    return any(bool(live_by_d[d][1 % modulus]) for d in range(C + 1))


def edge_marker(C: int, credit_fn, edge: int, steps: int = HEARTBEAT) -> str:
    marks = []
    for m in range(1, edge + 3):
        marks.append("L" if terminal_survives(C, m, credit_fn, steps=steps) else ".")
    return "".join(marks)


def support_count(credit_fn, k_lo: int, k_hi_inclusive: int) -> dict:
    ones = twos = 0
    for k in range(k_lo, k_hi_inclusive + 1):
        c = credit_fn(k)
        if c == 1:
            ones += 1
        elif c == 2:
            twos += 1
        else:
            raise ValueError(f"unexpected credit {c} at k={k}")
    return {"supports": ones, "drops": twos, "length": k_hi_inclusive - k_lo + 1}


def first_true_vs_period_divergence(limit: int = 500) -> int | None:
    credit_per, *_ = make_mechanical_2253()
    for k in range(limit):
        if credit_true(k) != credit_per(k):
            return k
    return None


@lru_cache(maxsize=None)
def shell_dead_by_delta(C: int, m: int) -> dict[int, frozenset]:
    """F7 dead profile: ceiling-distance -> dead residues (r%3!=0, not live).

    Uses TRUE credit word, one heartbeat (shell_probe dead_profile).
    """
    live_by_d, _ = run_heartbeat_generic(C, m, credit_true, steps=HEARTBEAT)
    modulus = 3 ** m
    prof: dict[int, frozenset] = {}
    for d in range(C + 1):
        dead = []
        arr = live_by_d[d]
        for r in range(modulus):
            if r % 3 != 0 and not arr[r]:
                dead.append(r)
        if dead:
            prof[C - d] = frozenset(dead)
    return prof


def in_shell(C: int, m: int, d: int, r: int) -> bool:
    """True if (d, r mod 3^m) is in F7 residual dead set at this C,m."""
    if d < 0 or d > C:
        return False
    modulus = 3 ** m
    r = r % modulus
    if r % 3 == 0:
        return False  # trivial kill class, not "shell residual"
    prof = shell_dead_by_delta(C, m)
    delta = C - d
    return r in prof.get(delta, frozenset())


# ---------------------------------------------------------------------------
# Odd-only Collatz orbit helpers (exact ints)
# ---------------------------------------------------------------------------

def v2(n: int) -> int:
    if n == 0:
        raise ValueError("v2(0)")
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c


def odd_step(x: int) -> tuple[int, int]:
    """Return (next_odd, a) for odd x: a = v2(3x+1), next = (3x+1)/2^a."""
    assert x % 2 == 1
    y = 3 * x + 1
    a = v2(y)
    return y >> a, a


def floor_k_log2_3(k: int) -> int:
    if k == 0:
        return 0
    return (3 ** k).bit_length() - 1


def orbit_upcrossings(
    x0: int,
    max_steps: int = 5000,
    m_track: int = 6,
) -> list[dict]:
    """Track deficit along odd-only orbit; emit events when d sets new max > 0.

    deficit d_k after k steps: floor(k*alpha) - A_k, A_k = sum a_0..a_{k-1}.
    Upcrossing: d_k > C_run where C_run is prior max d (corridor width so far).
    """
    x = x0
    if x % 2 == 0:
        while x % 2 == 0:
            x //= 2
    A = 0
    C_run = 0
    events = []
    history = []  # (step, x, a, d, C_run)
    for k in range(max_steps):
        if x == 1:
            break
        nxt, a = odd_step(x)
        A += a
        d = floor_k_log2_3(k + 1) - A
        c_k = credit_true(k)
        prev_C = C_run
        if d > C_run:
            # upward exit of corridor prev_C into d (new width)
            r = x % (3 ** m_track)
            r_next = nxt % (3 ** m_track)
            events.append(
                {
                    "start_n": x0,
                    "step_k": k,
                    "C_before": prev_C,
                    "C_after": d,
                    "d_before": history[-1][3] if history else 0,
                    "d_after": d,
                    "a_k": a,
                    "c_k": c_k,
                    "x_entry": x,
                    "x_exit": nxt,
                    "residue_mod": r,
                    "residue_next_mod": r_next,
                    "m_used": m_track,
                }
            )
            C_run = d
        history.append((k, x, a, d, C_run))
        x = nxt
    return events, x == 1, len(history)
