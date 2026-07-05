#!/usr/bin/env python3
"""
W6V-MEASURE -- validation gate (mandatory, run BEFORE trusting any new C).

Reproduces M_edge(1..5) = 4, 7, 9, 12, 14 FRESH via renorm_check/embedding/
automaton.py's run_heartbeat(C, m) -- the same exact-arithmetic (arbitrary-
precision Python int credit sequence, no float shortcuts) automaton that
shell_probe.py's P3 already validated against the genuine Rust lock3_census
Tier-1 dense per-m sweeps (May 2026). This script does NOT read shell_probe's
old log -- it calls run_heartbeat directly, fresh, right now.

Edge convention (matching the known values, pinned empirically, not by
guesswork): M_edge(C) is the LARGEST m for which some terminal state
(d, r=1 mod 3^m) survives one 53-step heartbeat from the fully-populated
start. Equivalently: walk m = 1, 2, 3, ... ; the marker string is "L" while
terminal-compatible states are alive and "." once they go permanently dead.
M_edge = length of the leading run of "L"s. This matches shell_probe.py's
p3_edge_confirmation() exactly (see renorm_check/shell/shell_probe.py and
shell_probe.log, both pre-existing and already 5/5 against genuine Tier-1
Rust census numbers).

We additionally confirm DEATH IS PERMANENT (not just a single dead m) by
walking a few m past the edge and checking they stay dead -- the "death
certificate" for the digest table.

Usage: python3 validate_c5.py | tee validate_c5.log
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "embedding"))

from automaton import M_edge, run_heartbeat  # noqa: E402

KNOWN_EDGES = {1: 4, 2: 7, 3: 9, 4: 12, 5: 14}


GUARD = 4_000_000_000  # (C+1)*3^m bytes; 47GB box, leave generous headroom


def terminal_alive(C: int, m: int) -> bool:
    modulus = 3 ** m
    live_by_d, _ = run_heartbeat(C, m, max_states_guard=GUARD)
    return any(live_by_d[d][1 % modulus] for d in range(C + 1))


def find_edge(C: int, m_max: int):
    """Walk m=1..m_max, return (edge, marker_list). edge = length of leading
    run of alive m's; also verifies death stays permanent through m_max.
    Stops early (without error) if a given m exceeds GUARD -- the marker
    just ends there and death-permanence is only confirmed up to that m."""
    marker = []
    for m in range(1, m_max + 1):
        try:
            alive = terminal_alive(C, m)
        except ValueError:
            break
        marker.append("L" if alive else ".")
    edge = 0
    for ch in marker:
        if ch == "L":
            edge += 1
        else:
            break
    return edge, marker


def main() -> int:
    print("W6V-MEASURE validation gate -- 2026-07-04")
    print("Reproducing M_edge(1..5) fresh via automaton.run_heartbeat, "
          "independent of shell_probe.log.")
    print("Formula floor(53*(C+1)/22):",
          [M_edge(C) for C in range(1, 6)])
    print()

    all_match = True
    t0 = time.time()
    for C in range(1, 6):
        formula_pred = M_edge(C)
        # Confirm a few extra m stay dead, but stay under GUARD: cost is
        # (C+1)*3^m bytes and grows 3x per unit m, so cap the margin by
        # what the guard allows rather than a flat +3 (C=5 at edge+3=17
        # is 775M states > GUARD; edge+2=16 is ~258M states, fine).
        margin = 3
        while (C + 1) * (3 ** (formula_pred + margin)) > GUARD and margin > 1:
            margin -= 1
        walk_to = formula_pred + margin
        t_c0 = time.time()
        edge, marker = find_edge(C, walk_to)
        dt = time.time() - t_c0
        expected = KNOWN_EDGES[C]
        match = (edge == expected == formula_pred)
        all_match = all_match and match
        marker_str = "".join(marker)
        print(f"C={C}: measured_edge={edge} known_edge={expected} "
              f"formula={formula_pred}  marker(m=1..{walk_to})={marker_str}  "
              f"{'MATCH' if match else 'MISMATCH'}  ({dt:.2f}s)")
        first_dead_m = edge + 1
        stays_dead = all(ch == "." for ch in marker[edge:])
        reached_full_walk = len(marker) == walk_to
        print(f"    death certificate: first dead at m={first_dead_m}, "
              f"stays dead through m={len(marker)} (target was {walk_to}, "
              f"reached={reached_full_walk}): {stays_dead}")
        assert stays_dead, f"death not permanent for C={C}"

    total_dt = time.time() - t0
    print()
    print(f"Total validation time: {total_dt:.2f}s")
    print(f"GATE RESULT: {'PASS -- all 5/5 match' if all_match else 'FAIL'}")
    return 0 if all_match else 1


if __name__ == "__main__":
    raise SystemExit(main())
