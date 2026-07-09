#!/usr/bin/env python3
"""G4: Theorem U (upcrossing form) + drop runs + streak / support analysis."""
from __future__ import annotations

import sys
from pathlib import Path

G3 = Path(__file__).resolve().parents[2] / "g3_deficit_climb_chains" / "scripts"
G2 = Path(__file__).resolve().parents[2] / "g2_a1_climb_realizability" / "scripts"
sys.path.insert(0, str(G3))
sys.path.insert(0, str(G2))

from g2_core import HIGH_RESERVE, load_breach_candidates  # noqa: E402
from g3_core import credit, walk_orbit_with_credit  # noqa: E402


def theorem_U_holds(step: dict, C_before: int) -> bool:
    """Check Theorem U on one step known to be an upcrossing.

    Requires: d_before == C_before, a==1, c==2.
    """
    return (
        step["upcrossing"]
        and step["d_before"] == C_before
        and step["a"] == 1
        and step["c"] == 2
    )


def slack_argument_impossible(s: int, c: int, a: int) -> bool:
    """Return True if (c,a) cannot upcross with slack s = C - d_before ≥ 0."""
    return not (c - a > s)


def prove_U_cases() -> dict:
    """Exhaustive small check: for s=0..5, c=1..2, a=1..6, upcross possible iff s=0,c=2,a=1."""
    rows = []
    for s in range(0, 6):
        for c in (1, 2):
            for a in range(1, 7):
                can = c - a > s
                expected = s == 0 and c == 2 and a == 1
                rows.append(
                    {
                        "s": s,
                        "c": c,
                        "a": a,
                        "can_upcross": can,
                        "matches_thm_U_only": can == expected,
                    }
                )
    all_ok = all(r["matches_thm_U_only"] for r in rows)
    return {"all_ok": all_ok, "n": len(rows), "rows_fail": [r for r in rows if not r["matches_thm_U_only"]]}


def drop_runs(seq: list[int]) -> list[int]:
    """Lengths of maximal consecutive 2's in credit sequence."""
    out = []
    i = 0
    n = len(seq)
    while i < n:
        if seq[i] != 2:
            i += 1
            continue
        j = i
        while j < n and seq[j] == 2:
            j += 1
        out.append(j - i)
        i = j
    return out


def walk_with_C_before(x0: int, max_steps: int = 8000) -> list[dict]:
    steps = walk_orbit_with_credit(x0, max_steps)
    C = 0
    out = []
    for s in steps:
        C_before = C
        rec = dict(s)
        rec["C_before"] = C_before
        rec["slack"] = C_before - s["d_before"]
        if s["upcrossing"]:
            rec["thm_U"] = theorem_U_holds(s, C_before)
            C = s["d_after"]
        else:
            rec["thm_U"] = None
            C = max(C, s["d_after"])
        out.append(rec)
    return out


def up_streaks_detailed(steps: list[dict]) -> list[dict]:
    """Consecutive upcrossing streaks with credit letters."""
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
        seg = steps[i:j]
        credits = [s["c"] for s in seg]
        asas = [s["a"] for s in seg]
        streaks.append(
            {
                "S": j - i,
                "credits": credits,
                "as": asas,
                "all_c2": all(c == 2 for c in credits),
                "all_a1": all(a == 1 for a in asas),
                "k0": seg[0]["k"],
            }
        )
        i = j
    return streaks


def greedy_up_walker(k0: int, d0: int, n_steps: int) -> dict:
    """Dual greedy: if c==2 and d==C, take a=1 (up); elif c==2: a=2; else a=1."""
    d = d0
    C = d0
    ups = 0
    streak = 0
    max_streak = 0
    for i in range(n_steps):
        c = credit(k0 + i)
        if c == 2 and d == C:
            a = 1
        elif c == 2:
            a = 2
        else:
            a = 1
        d = d + c - a
        if d > C:
            ups += 1
            streak += 1
            max_streak = max(max_streak, streak)
            C = d
        else:
            streak = 0
            if d > C:
                C = d
            C = max(C, d)
    return {"k0": k0, "d0": d0, "n_steps": n_steps, "ups": ups, "max_streak": max_streak}
