#!/usr/bin/env python3
"""
W6L-L1b -- Instrument validation addendum for L1's optimal-set
collector: prove the collector CAN detect ties / non-loop optima
(SYNTHESIS validation law: every suite must include rows that BREAK
under whatever blindness the implementation could silently have).
A collector that always returns n_optimal=1 would fake-pass L1.

Method: run the L1 collector over all {1,2,3}^m words for m=2..4
(canonical order, D_free). Words with c=3 letters admit equal-cost
alternatives (the loop's slack lets a larger exponent ride for free),
so ties are plausible there. Requirements to PASS:
  (1) at least one word shows n_optimal > 1 (tie detection works);
  (2) [STRUCTURALLY VACUOUS -- recorded, not required] a word where
      the loop is NOT optimal cannot exist under D_free: K1 certified
      D_free = L on every word over every alphabet tested, and the
      all-a=2 loop achieves exactly L(w) by definition, so the loop
      is always IN the optimal set. The meaningful blindness check is
      (1): can the collector see when the loop is NOT ALONE. (2) is
      reported for the record but cannot gate.
  (3) the tie word hand-verified by the independent hand_trace_dfs
      (structurally different full enumeration, no branch-and-bound).
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from l1_uniqueness_recensus import canonical_D_and_optimal_set, hand_trace_dfs  # noqa: E402


def main():
    found_tie = None
    found_nonloop = None
    n_words = 0
    for m in (2, 3, 4):
        for w in itertools.product((1, 2, 3), repeat=m):
            n_words += 1
            D, optima, is_loop_opt, is_loop_uniq, trunc = canonical_D_and_optimal_set(w, False)
            if D is None:
                continue
            if len(optima) > 1 and found_tie is None:
                found_tie = (w, D, optima)
            if not is_loop_opt and found_nonloop is None:
                found_nonloop = (w, D, optima)
            if found_tie and found_nonloop:
                break
        if found_tie and found_nonloop:
            break

    print(f"Scanned {n_words} {{1,2,3}} words (m=2..4)")
    ok1 = found_tie is not None
    ok2 = found_nonloop is not None
    if ok1:
        w, D, optima = found_tie
        print(f"(1) TIE DETECTED: word={w} D={D} n_optimal={len(optima)} optima={optima[:6]} -- PASS")
    else:
        print("(1) NO tie found anywhere -- collector tie-detection UNPROVEN on this scope")
    if ok2:
        w, D, optima = found_nonloop
        print(f"(2) NON-LOOP OPTIMUM DETECTED: word={w} D={D} optima={optima[:6]} "
              f"-- would CONTRADICT K1 universality (D_free=L, loop achieves L); investigate")
    else:
        print("(2) no loop-non-optimal word found -- CONSISTENT with K1 universality "
              "(structurally required: loop always achieves L=D_free; vacuous check, does not gate)")

    ok3 = False
    if found_tie:
        w, D, optima = found_tie
        D2, optima2 = hand_trace_dfs(list(w), False)
        ok3 = (D2 == D) and (sorted(optima2) == sorted(optima))
        print(f"(3) independent hand-trace on {w}: D={D2} n_optimal={len(optima2)} "
              f"{'CONFIRMED -- PASS' if ok3 else '*** DISAGREEMENT ***'}")

    print(f"\nL1b VERDICT: {'PASS (collector demonstrably detects ties; hand-trace confirms; loop-always-optimal is K1-structural)' if (ok1 and ok3) else 'FAIL -- see above'}")


if __name__ == "__main__":
    main()
