#!/usr/bin/env python3
"""
W6U-RECON step 3/4 -- independent re-derivation of game-D (root- and
end-anchored) at m=29..32, via a SECOND, structurally different
method: breadth-first value-iteration over (rho, running-sum) states,
rather than the DFS branch-and-bound of
w6k/k0_canonical_engine.canonical_D (reused, unmodified, in
w2_comparison_table.py) or w2's own second DFS
(independent_game_D_check). This is a THIRD independent instrument for
the m=29..32 headline cells, cross-checked against the other two.

Method: track the exact set of (rho, running_sum) pairs reachable at
each backward step j=0..m (rho tracked as an exact Python int -- no
modular reduction needed since we only ever apply
backward_predecessor_exact, which requires exact integer division by
3 each step and asserts exactness; rho stays a genuine, if enormous,
integer, but m<=45 keeps it small: rho < 2^(2*45) at worst). For a
target ceiling C, prune any state with running_sum outside [0, C]
(this is literally the ceiling_on branch-and-bound's pruning
condition, but implemented as full breadth-first frontier tracking
instead of backtracking recursion -- a different traversal shape,
verifying the DFS's pruning didn't accidentally discard a valid
witness).

We sweep C using "does ANY state survive to j=m" as the survival
predicate (same predicate as canonical_D, re-derived independently
here).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).parent
UNDERLOCK = HERE.parent
W6E = UNDERLOCK / "w6e"
W6K = UNDERLOCK / "w6k"
sys.path.insert(0, str(UNDERLOCK))
sys.path.insert(0, str(W6E))
sys.path.insert(0, str(W6K))
sys.path.insert(0, str(HERE))

from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
from k0_canonical_engine import canonical_D  # noqa: E402
from w1_census_port import credit_at_step  # noqa: E402
from w2_comparison_table import independent_game_D_check  # noqa: E402


def root_anchored_word(m: int):
    return [credit_at_step(m - 1 - j) for j in range(m)]


def end_anchored_word(m: int, anchor_steps: int = 53):
    return [credit_at_step(anchor_steps - 1 - j) for j in range(m)]


def survives_at_C(letters, C: int, a_cap: int = 80):
    """Breadth-first frontier over (rho, running) pairs, ceiling_on
    semantics (running must stay in [0, C] at every prefix -- matches
    canonical_D(ceiling_on=True): `if ceiling_on and running2 < 0:
    continue` PLUS the additional upper cap C we are testing).
    Returns True iff at least one state survives all m steps.
    De-duplicates states with the SAME (rho, running) pair (collapsing
    the frontier -- valid because future legality/survival depends
    only on (rho, running), not on path history)."""
    m = len(letters)
    frontier = {(1, 0)}  # (rho, running)
    for j in range(m):
        c = letters[j]
        next_frontier = set()
        for (rho, running) in frontier:
            parity = forced_parity_for_backward_step(rho)
            if parity is None:
                continue
            a_min = 2 if parity == 0 else 1
            a = a_min
            while a < a_min + a_cap:
                running2 = running + (a - c)
                if 0 <= running2 <= C:
                    rho2 = backward_predecessor_exact(rho, a)
                    next_frontier.add((rho2, running2))
                a += 2
        frontier = next_frontier
        if not frontier:
            return False
    return len(frontier) > 0


def game_D_bfs(letters, C_search_max: int = 60, a_cap: int = 80):
    """Sweep C upward (linear, cheap at this scale) to find the
    minimum C for which the word survives all m steps under
    ceiling_on=True semantics -- this IS canonical_D(letters,
    ceiling_on=True)'s definition, re-derived via a structurally
    different (BFS frontier, not DFS-with-pruning) algorithm."""
    for C in range(0, C_search_max + 1):
        if survives_at_C(letters, C, a_cap=a_cap):
            return C
    return None


def main():
    out_lines = []

    def p(s=""):
        print(s)
        out_lines.append(s)

    p("=== W6U-RECON W3: independent BFS-frontier re-derivation, m=29..32 ===\n")
    p("(third independent instrument: BFS frontier over (rho,running) pairs,")
    p(" vs w6k.canonical_D's DFS branch-and-bound, vs w2's second DFS)\n")

    p(f"{'m':>3} {'root_DFS(canonical_D)':>22} {'root_DFS2':>10} {'root_BFS':>9} "
      f"{'end_DFS(canonical_D)':>21} {'end_DFS2':>9} {'end_BFS':>8} {'ALL_AGREE':>10}")

    all_ok = True
    rows = []
    for m in range(29, 33):
        rw = root_anchored_word(m)
        ew = end_anchored_word(m)

        root_dfs1 = canonical_D(rw, ceiling_on=True, a_cap=60)
        root_dfs2 = independent_game_D_check(rw, a_cap=60)
        root_bfs = game_D_bfs(rw, C_search_max=30, a_cap=60)

        end_dfs1 = canonical_D(ew, ceiling_on=True, a_cap=60)
        end_dfs2 = independent_game_D_check(ew, a_cap=60)
        end_bfs = game_D_bfs(ew, C_search_max=30, a_cap=60)

        agree = (root_dfs1 == root_dfs2 == root_bfs) and (end_dfs1 == end_dfs2 == end_bfs)
        all_ok = all_ok and agree
        rows.append((m, root_dfs1, root_dfs2, root_bfs, end_dfs1, end_dfs2, end_bfs, agree))
        p(f"{m:>3} {root_dfs1:>22} {root_dfs2:>10} {root_bfs:>9} "
          f"{end_dfs1:>21} {end_dfs2:>9} {end_bfs:>8} {str(agree):>10}")

    p(f"\n=== ALL THREE INDEPENDENT INSTRUMENTS AGREE AT m=29..32: {all_ok} ===")

    p("\nComparison vs mirror-law formula D_per(m) = floor((22m-1)/53):")
    for (m, root_dfs1, root_dfs2, root_bfs, end_dfs1, end_dfs2, end_bfs, agree) in rows:
        mirror = (22 * m - 1) // 53
        p(f"  m={m}: mirror={mirror}  root_game_D={root_dfs1} (diff {root_dfs1-mirror:+d})  "
          f"end_game_D={end_dfs1} (diff {end_dfs1-mirror:+d})")

    with open(HERE / "w3_output.log", "w") as f:
        f.write("\n".join(out_lines) + "\n")
    p(f"\nWrote {HERE / 'w3_output.log'}")


if __name__ == "__main__":
    main()
