#!/usr/bin/env python3
"""Shared basin/shell helpers for G25+ chain. Exact-int load-bearing paths."""
from __future__ import annotations
import sys
from pathlib import Path

_SHELL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_SHELL / "descent_rule"))
sys.path.insert(0, str(_SHELL / "g10_species_vs_climb" / "scripts"))
sys.path.insert(0, str(_SHELL / "species_spacing_common"))

from descent_common import is_one_step_species, one_odd_step, species_member  # noqa: E402
from species_orbit import steps_to_species, sample_starts  # noqa: E402
from species_spacing import x_k, gap_k, count_species_le, sieve_primes  # noqa: E402


def is_species_or_one(x: int) -> bool:
    if x == 1:
        return True
    return is_one_step_species(x)[0]


def in_immediate_shell(y: int) -> bool:
    """True if odd y is species, or one odd-step lands on species/1."""
    if y % 2 == 0:
        raise ValueError("y must be odd")
    if is_species_or_one(y):
        return True
    return is_species_or_one(one_odd_step(y))


def count_immediate_shell_odds(X: int) -> tuple[int, int]:
    """Return (n_in_shell, n_odds) for odds in 1..X."""
    n_odds = (X + 1) // 2
    n = 0
    for y in range(1, X + 1, 2):
        if in_immediate_shell(y):
            n += 1
    return n, n_odds


def layered_basin_fractions(X: int, max_steps: int, layers: list[int]) -> dict:
    """Among odds ≤ X, fraction with steps_to_species ≤ L for each L in layers."""
    n_odds = (X + 1) // 2
    counts = {L: 0 for L in layers}
    steps_list = []
    for y in range(1, X + 1, 2):
        r = steps_to_species(y, max_steps)
        s = r["steps_to_species"] if r["hit"] else None
        steps_list.append(s)
        if s is not None:
            for L in layers:
                if s <= L:
                    counts[L] += 1
    return {
        "n_odds": n_odds,
        "frac": {str(L): counts[L] / n_odds for L in layers},
        "counts": {str(L): counts[L] for L in layers},
        "n_hit": sum(1 for s in steps_list if s is not None),
        "steps_sample": steps_list,
    }


def last_a_into_species(x0: int, max_steps: int = 5000) -> int | None:
    """Valuation a of the last odd-step that lands on species (or None)."""
    sys.path.insert(0, str(_SHELL / "g2_a1_climb_realizability" / "scripts"))
    from g2_core import odd_step  # local import

    x = x0
    if x % 2 == 0:
        while x % 2 == 0 and x > 0:
            x //= 2
    if is_species_or_one(x):
        return 0  # already there
    last_a = None
    for _ in range(max_steps):
        nxt, a = odd_step(x)
        if is_species_or_one(nxt):
            return a
        x = nxt
    return None


def reverse_preimage_candidates(x: int) -> list[int]:
    """Odd y such that S(y)=x: y = (2^a * x - 1)/3 odd integer for a≥1 when exact."""
    out = []
    for a in range(1, 40):
        num = (1 << a) * x - 1
        if num % 3 == 0:
            y = num // 3
            if y > 0 and y % 2 == 1:
                # verify
                if one_odd_step(y) == x:
                    out.append(y)
    return out
