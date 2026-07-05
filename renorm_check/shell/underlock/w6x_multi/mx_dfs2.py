#!/usr/bin/env python3
"""
W6X-MULTI Step 5 -- INDEPENDENT SECOND ENGINE, structurally different
from mx_core.py's layered modular BFS (and ALSO structurally different
from w6w_sparse/step4_independent_rederivation.py's DFS -- per the
mission brief's explicit instruction not to just reuse that file's
approach and call it independent).

Differences from BOTH prior engines:
  - mx_core.sparse_survival_multi: iterative layered BFS, dict-per-
    layer, state key (R mod 3^(m-j), u, v), deduplicated by dict
    insertion, R tracked as a bounded modular residue throughout.
  - w6w_sparse's DFS: Python-recursive DFS with failure-memo keyed on
    (j, rho mod 3^(m-j), u, v), rho as an EXACT growing big int, memo
    implemented as a set add/lookup, recursion for traversal, depth-
    first choice order low-a-first with early return on first success.
  - mx_dfs2 (THIS file): EXPLICIT STACK (no Python recursion at all --
    iterative DFS via a manual stack of frames), and NO memoization at
    all (a genuinely different, brute-force-with-pruning-only
    traversal), relying entirely on the (u<=C, v<=C, u+v<=C) prune and
    the depth-first "first success wins" early exit. This is slower in
    the worst case (no dedup) but is a legitimately different
    computational path: no shared dedup logic, no shared recursion
    mechanism, no shared state key with either prior engine. Confirms
    the ALIVE/DEAD calls agree without sharing any traversal-
    engineering trick.

  Because full DFS-without-memo can blow up if the search is deep and
  branchy, mx_dfs2 also carries an explicit node-count budget and
  reports honestly if it cannot complete (does not fabricate an
  answer under budget exhaustion).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from mx_core import (  # noqa: E402
    letters_for, parity_forced, backward_pred_exact, verify_witness_exact,
)


def exists_dfs_stack_nomemo(letters, C: int, node_budget: int = 20_000_000):
    """Iterative (explicit stack) exact-integer DFS, NO memoization
    (deliberately different dedup strategy from both prior engines --
    here there IS no dedup, just pruning). rho carried as an exact,
    unbounded-growth big int throughout (never truncated mod anything,
    unlike mx_core's R which is always a bounded residue) -- so this
    also differs in STATE REPRESENTATION, not just traversal order.

    Returns (alive: bool, witness_forward_or_None, stats: dict).
    stats includes 'nodes' and 'budget_exceeded' (True if we could not
    finish -- an honest wall, not a fabricated answer).
    """
    m = len(letters)
    stats = {"nodes": 0, "budget_exceeded": False}
    acc = []

    def push_choices(j, rho, s, min_s, max_s):
        """Return (a_min, a_hi) or None (dead) or 'DONE' (goal reached)."""
        if max_s - min_s > C:
            return None
        if j == m:
            return "DONE"
        p = parity_forced(rho)
        if p is None:
            return None
        a_min = 2 if p == 0 else 1
        c = letters[j]
        a_hi = c + C - (max_s - s)
        if a_hi < a_min:
            return None
        return (a_min, a_hi)

    stack = []
    j0, rho0, s0, min0, max0 = 0, 1, 0, 0, 0
    res0 = push_choices(j0, rho0, s0, min0, max0)
    if res0 == "DONE":
        return True, [], stats  # m==0 edge case
    if res0 is None:
        return False, None, stats
    a_min, a_hi = res0
    stack.append([j0, rho0, s0, min0, max0, a_min, a_hi])

    while stack:
        stats["nodes"] += 1
        if stats["nodes"] > node_budget:
            stats["budget_exceeded"] = True
            return None, None, stats

        frame = stack[-1]
        j, rho, s, min_s, max_s, a, a_hi = frame
        if a > a_hi:
            stack.pop()
            if acc:
                acc.pop()
            continue

        frame[5] = a + 2
        c = letters[j]
        s2 = s + c - a
        min2 = min(min_s, s2)
        max2 = max(max_s, s2)
        if max2 - min2 > C:
            continue
        rho2 = backward_pred_exact(rho, a)
        acc.append(a)
        nxt = push_choices(j + 1, rho2, s2, min2, max2)
        if nxt == "DONE":
            witness = list(reversed(acc))
            return True, witness, stats
        if nxt is None:
            acc.pop()
            continue
        a_min2, a_hi2 = nxt
        stack.append([j + 1, rho2, s2, min2, max2, a_min2, a_hi2])

    return False, None, stats


def alive_at_dfs2(m: int, C: int, reading: str, node_budget: int = 20_000_000):
    letters = letters_for(m, reading)
    alive, witness, stats = exists_dfs_stack_nomemo(letters, C, node_budget=node_budget)
    return alive, witness, stats, letters


def main():
    out = []

    def p(s=""):
        print(s, flush=True)
        out.append(s)

    p("=== W6X-MULTI Step 5: mx_dfs2 (explicit-stack, no-memo, exact-big-int) ===")
    p("Independent re-derivation of the C=11 headline cells "
      "(both readings), vs mx_core's layered modular BFS.\n")

    cells = [
        ("B", 11, 54), ("B", 11, 57), ("B", 11, 58), ("B", 11, 60),
        ("A", 11, 53), ("A", 11, 54),
        ("B", 12, 63), ("B", 12, 64),
        ("B", 15, 79), ("B", 15, 80),
        # Reading A intermittency ("revival") cells -- found in step2's
        # full sweep (a monotone-death assumption bug in step2 v1 had
        # hidden these; fixed, and cross-checked here with the fully
        # independent engine to confirm the revivals are real, not a
        # bug in either engine):
        ("A", 11, 55), ("A", 12, 58), ("A", 12, 59), ("A", 13, 66), ("A", 13, 67),
    ]

    agreements = 0
    disagreements = []
    p(f"{'reading':>7} {'C':>3} {'m':>4} {'dfs2_alive':>11} {'nodes':>9} "
      f"{'budget_exceeded':>15} {'dt(s)':>8} {'witness_check':>18}")
    for reading, C, m in cells:
        t0 = time.time()
        alive, wit, stats, letters = alive_at_dfs2(m, C, reading, node_budget=20_000_000)
        dt = time.time() - t0
        wcheck = ""
        if alive and wit is not None:
            v = verify_witness_exact(wit, C, letters)
            wcheck = f"all_ok={v['all_ok']} n0={v['start_integer']}"
        p(f"{reading:>7} {C:>3} {m:>4} {str(alive):>11} {stats['nodes']:>9} "
          f"{str(stats['budget_exceeded']):>15} {dt:>8.3f} {wcheck:>18}")

    p("\n--- Cross-check vs mx_core.sparse_survival_multi ---")
    from mx_core import sparse_survival_multi  # noqa: E402
    p(f"{'reading':>7} {'C':>3} {'m':>4} {'dfs2':>6} {'bfs':>6} {'agree':>6}")
    for reading, C, m in cells:
        alive_dfs2, _, stats, _ = alive_at_dfs2(m, C, reading, node_budget=20_000_000)
        res_bfs = sparse_survival_multi(m, C, reading=reading, want_witness=False)
        alive_bfs = res_bfs["alive"]
        agree = (alive_dfs2 == alive_bfs)
        agreements += int(agree)
        if not agree:
            disagreements.append((reading, C, m, alive_dfs2, alive_bfs))
        p(f"{reading:>7} {C:>3} {m:>4} {str(alive_dfs2):>6} {str(alive_bfs):>6} "
          f"{'Y' if agree else 'N':>6}")

    p(f"\nTotal cells cross-checked: {len(cells)}, agreements: {agreements}")
    if disagreements:
        p(f"DISAGREEMENTS ({len(disagreements)}): {disagreements}")
    else:
        p("NO DISAGREEMENTS -- independent re-derivation CONFIRMS the primary engine.")

    (HERE / "step5_independent_engine.log").write_text("\n".join(out) + "\n")
    p(f"\nWrote {HERE / 'step5_independent_engine.log'}")


if __name__ == "__main__":
    main()
