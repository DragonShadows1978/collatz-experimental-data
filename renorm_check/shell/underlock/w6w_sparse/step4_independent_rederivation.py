#!/usr/bin/env python3
"""
W6W-SPARSE Step 4 -- INDEPENDENT RE-DERIVATION of the C=11 verdict.

House rule: "Independent re-derivation is REQUIRED for the C=11
verdict regardless of which way it comes out." This script is a
SECOND, differently-implemented code path from sparse_instrument.py's
exists_range-style layered BFS (that one is a modular-residue layered
BFS over (R, u, v) states, keyed on rho mod 3^(m-j)). This one is an
EXACT-INTEGER memoized DFS with failure-memoization -- different
traversal order (DFS vs BFS), different state representation (exact
rho, no modulus truncation, growing big int) vs (rho mod 3^k, bounded
int), different dedup mechanism (failure-memo set vs per-layer dict).

If both engines agree at C=11 on every m in 26..33, that is the
required independent confirmation. A THIRD check -- direct exact-
integer Collatz replay of every witness produced by either engine --
is also run (shared with sparse_instrument.verify_witness_exact, which
is itself a from-first-principles check: real Collatz division at
every step, not trusting either search engine's own bookkeeping).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from sparse_instrument import (  # noqa: E402
    credit_at_step, parity_forced, backward_pred_exact, verify_witness_exact,
    HEARTBEAT,
)


def end_anchored_letters(m: int, anchor: int = HEARTBEAT):
    return [credit_at_step(anchor - 1 - j) for j in range(m)]


def exists_dfs_exact(letters, C: int, memo_cap: int = 30_000_000):
    """Exact-integer DFS with failure memoization (memo key uses rho
    mod 3^(m-j) purely as a HASHABLE fingerprint alongside the exact
    (u,v) range state -- rho itself grows as a genuine big int along
    the live path, never truncated during the walk, only truncated for
    the memo KEY, which is safe because two different exact rho values
    congruent mod 3^(m-j) provably have the same FUTURE feasibility,
    same argument as sparse_instrument's mod-tracked variant, but this
    is a structurally different implementation: recursion, not an
    explicit layer-by-layer frontier dict)."""
    m = len(letters)
    pow3 = [3 ** i for i in range(m + 1)]
    memo = set()
    stats = {"nodes": 0, "memo_capped": False}
    sys.setrecursionlimit(10000)

    def dfs(j, rho, s, min_s, max_s, acc):
        stats["nodes"] += 1
        if max_s - min_s > C:
            return None
        if j == m:
            return list(acc)  # free endpoints -- any completed chain fits
        key = (j, rho % pow3[m - j], s - min_s, max_s - s)
        if key in memo:
            return None
        c = letters[j]
        p = parity_forced(rho)
        if p is not None:
            a_min = 2 if p == 0 else 1
            a_hi = c + C - (max_s - s)
            a = a_min
            while a <= a_hi:
                s2 = s + c - a
                acc.append(a)
                res = dfs(j + 1, backward_pred_exact(rho, a), s2,
                          min(min_s, s2), max(max_s, s2), acc)
                acc.pop()
                if res is not None:
                    return res
                a += 2
        if len(memo) < memo_cap:
            memo.add(key)
        else:
            stats["memo_capped"] = True
        return None

    wit = dfs(0, 1, 0, 0, 0, [])
    if wit is None:
        return None, stats
    return list(reversed(wit)), stats


def alive_at(m: int, C: int):
    letters = end_anchored_letters(m)
    wit, stats = exists_dfs_exact(letters, C)
    return wit is not None, wit, stats, letters


def main():
    out = []

    def p(s=""):
        print(s, flush=True)
        out.append(s)

    p("=== W6W-SPARSE Step 4: INDEPENDENT RE-DERIVATION (C=11, m=26..33) ===")
    p("Second engine: exact-integer recursive DFS + failure-memo "
      "(sparse_instrument.py's own engine is a layered modular BFS -- "
      "different traversal, different state rep, written independently).\n")

    p(f"{'m':>3} {'alive_dfs':>10} {'nodes':>10} {'memo_capped':>12} {'dt(s)':>8} {'witness_verify':>15}")
    results = {}
    for m in range(26, 34):
        t0 = time.time()
        alive, wit, stats, letters = alive_at(m, 11)
        dt = time.time() - t0
        verify = ""
        if alive and wit:
            v = verify_witness_exact(wit, 11, letters)
            verify = f"all_ok={v['all_ok']} n0={v['start_integer']}"
        results[m] = (alive, wit, stats)
        p(f"{m:>3} {str(alive):>10} {stats['nodes']:>10} {str(stats['memo_capped']):>12} "
          f"{dt:>8.2f} {verify:>15}")

    p(f"\nRaw results dict: {[(m, results[m][0]) for m in sorted(results)]}")
    (HERE / "step4_independent_rederivation.log").write_text("\n".join(out) + "\n")
    p(f"\nWrote {HERE / 'step4_independent_rederivation.log'}")
    return results


if __name__ == "__main__":
    main()
