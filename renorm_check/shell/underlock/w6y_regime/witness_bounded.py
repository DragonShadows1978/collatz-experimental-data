#!/usr/bin/env python3
"""
Memory-bounded witness extractor for deep cells (C=26/m=205), where
mx_core._reconstruct_witness (retains all m frontier-layers) blows past
8 GB and mx_dfs2's naive depth-first order exhausts a 200M-node budget.

Approach: a backward DFS from rho=1 with an explicit stack (no
recursion, no full-layer retention) and a DEFICIT-CENTERING heuristic:
at each layer try the `a` value whose resulting (u,v) is most balanced
first. Most cells have astronomically many witnesses, so centering the
deficit walk finds a completing path with negligible backtracking.

Exact (integer rho throughout; verified by mx_core.verify_witness_exact)
and memory-light (single path + small per-frame option lists). NOT a new
survival oracle -- alive/dead is already decided by the gated BFS; this
only EXTRACTS a certificate for a cell already known alive.
"""
from __future__ import annotations
import sys
import resource
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6x_multi"))
import mx_core as mx  # noqa: E402


def _legal_as(rho, u, v, c, C):
    p = mx.parity_forced(rho % 3)
    if p is None:
        return []
    a_min = 2 if p == 0 else 1
    a_hi = c + C - v
    opts = []
    a = a_min
    while a <= a_hi:
        s_rel = c - a
        new_min_rel = min(-u, s_rel)
        new_max_rel = max(v, s_rel)
        if new_max_rel - new_min_rel <= C:
            u2 = s_rel - new_min_rel
            v2 = new_max_rel - s_rel
            opts.append((abs(u2 - v2), a, u2, v2))  # most-centered first
        a += 2
    opts.sort()
    return opts


def find_witness_bounded(m, C, reading="B", max_backtracks=200_000_000):
    letters = mx.letters_for(m, reading)
    opts0 = _legal_as(1, 0, 0, letters[0], C)
    stack = [[0, 1, 0, 0, opts0, 0]]  # j, rho, u, v, options, idx
    path_a = []
    backtracks = 0
    while stack:
        frame = stack[-1]
        j, rho, u, v, opts, idx = frame
        if idx >= len(opts):
            stack.pop()
            if path_a:
                path_a.pop()
            backtracks += 1
            if backtracks > max_backtracks:
                return None, backtracks
            continue
        frame[5] = idx + 1
        _score, a, u2, v2 = opts[idx]
        rho2 = mx.backward_pred_exact(rho, a)
        if j + 1 == m:
            path_a.append(a)
            return list(reversed(path_a)), backtracks
        opts_next = _legal_as(rho2, u2, v2, letters[j + 1], C)
        if not opts_next:
            backtracks += 1
            if backtracks > max_backtracks:
                return None, backtracks
            continue
        path_a.append(a)
        stack.append([j + 1, rho2, u2, v2, opts_next, 0])
    return None, backtracks


def main():
    C = int(sys.argv[1]) if len(sys.argv) > 1 else 26
    m = int(sys.argv[2]) if len(sys.argv) > 2 else 205
    wit, bt = find_witness_bounded(m, C, "B")
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    if wit is None:
        print(f"C={C} m={m} NO witness within backtrack budget (bt={bt}) rss={rss:.1f}MB", flush=True)
        return
    letters = mx.letters_for(m, "B")
    v = mx.verify_witness_exact(wit, C, letters)
    print(f"C={C} m={m} n0={v['start_integer']} collatz_ok={v['collatz_replay_ok']} "
          f"range={v['range']} all_ok={v['all_ok']} backtracks={bt} rss={rss:.1f}MB", flush=True)


if __name__ == "__main__":
    main()
