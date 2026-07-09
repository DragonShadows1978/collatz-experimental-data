#!/usr/bin/env python3
"""Shared species+orbit helpers for G10+ chain."""
from __future__ import annotations

import sys
from pathlib import Path

_SHELL = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_SHELL / "descent_rule"))
sys.path.insert(0, str(_SHELL / "g4_drop_gate_streaks" / "scripts"))
sys.path.insert(0, str(_SHELL / "g3_deficit_climb_chains" / "scripts"))
sys.path.insert(0, str(_SHELL / "g2_a1_climb_realizability" / "scripts"))

from descent_common import is_one_step_species, one_odd_step, species_member  # noqa: E402
from g2_core import HIGH_RESERVE, load_breach_candidates, odd_step  # noqa: E402
from g3_core import floor_k_log2_3  # noqa: E402


def steps_to_species(x0: int, max_steps: int = 100000) -> dict:
    """First time is_one_step_species(x) or x==1; count ups/max_d along the path."""
    x = x0
    if x % 2 == 0:
        while x % 2 == 0 and x > 0:
            x //= 2
    n_ups = 0
    max_d = 0
    C = 0
    A = 0

    if x == 1 or is_one_step_species(x)[0]:
        return {
            "hit": True,
            "steps_to_species": 0,
            "n_ups": 0,
            "max_d": 0,
            "species_x": x,
            "hit_1": x == 1,
        }

    for k in range(max_steps):
        if x == 1 or is_one_step_species(x)[0]:
            return {
                "hit": True,
                "steps_to_species": k,
                "n_ups": n_ups,
                "max_d": max_d,
                "species_x": x,
                "hit_1": x == 1,
            }
        nxt, a = odd_step(x)
        A += a
        d = floor_k_log2_3(k + 1) - A
        if d > C:
            n_ups += 1
            C = d
        if d > max_d:
            max_d = d
        x = nxt

    return {
        "hit": False,
        "steps_to_species": None,
        "n_ups": n_ups,
        "max_d": max_d,
        "species_x": None,
        "hit_1": False,
    }


def sample_starts(repo: Path, seed: int = 20260713):
    import random

    rng = random.Random(seed)
    breach = load_breach_candidates(repo / "data" / "runs", 200)
    rnd = [rng.randrange(1, 10**7, 2) for _ in range(100)]
    return (
        [("hr", x) for x in HIGH_RESERVE]
        + [("br", x) for x in breach]
        + [("rnd", x) for x in rnd]
    )
