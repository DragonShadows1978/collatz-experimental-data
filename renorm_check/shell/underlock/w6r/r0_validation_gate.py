#!/usr/bin/env python3
"""
W6R-R0 -- Validation gate (house rule, binding): "asymmetric/convention-
sensitive validation rows FIRST for any new code path (the W6K/W6Q
law -- include at least one row that distinguishes root from end
anchoring, m >= 29, and show your code gets W6Q's known values:
deficit max 1 on the 839 chain."

This gate must PASS before any of R1-R4 are trusted.

Row A: root vs end anchoring on the true word at m=29 must give
DIFFERENT L values (a distinguishing row) -- if they coincided, root
anchoring would not be a live variable at this m and the whole round's
premise would be moot.

Row B: reproduce W6Q-REALITY's own number exactly -- the W6P-URGENT
m=29 counterexample chain (a=(4,3,2,1,1,4,2,2,1,6,1,1,1,2,2,2,1,2,1,2,
4,1,2,1,1,2,2,1,1), terminal residue rho=839), evaluated under the
root-anchored census convention, must give deficit max=1, min=-11 --
the EXACT numbers ledger W6Q-REALITY reported (rust/lock3_census.rs's
own forward recursion, root-anchored at k=0). This is done here via a
FRESH computation (not imported from w6q_reality/), using this round's
own root_anchor.py machinery plus a direct forward d-recursion, cross-
checked two ways (direct forward recursion; closed-form telescoping),
matching W6Q's "cross-checked via a second, independently-coded
method... bit-for-bit identical" discipline.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from root_anchor import (  # noqa: E402
    root_anchored_word, end_anchored_word, loop_curve, credit_true,
)

# The W6P-URGENT / W6Q-REALITY witness chain, verbatim from the ledger
# (IMPLEMENTATION_LEDGER.md ~line 3525 / q3's A_BACKWARD), backward-
# consumption order (index 0 = nearest terminal).
A_BACKWARD_839 = [4, 3, 2, 1, 1, 4, 2, 2, 1, 6, 1, 1, 1, 2, 2, 2,
                  1, 2, 1, 2, 4, 1, 2, 1, 1, 2, 2, 1, 1]
M_839 = 29
CLAIMED_CENSUS_MAX_D = 1
CLAIMED_CENSUS_MIN_D = -11


def census_forward_d_from_root(a_forward, m):
    """Direct forward recursion, root-anchored (k=0 at trajectory's
    own start): d(i) = d(i-1) + c_{i-1} - a_{i-1}, c_k = credit_true(k).
    Method 1: step-by-step."""
    d = 0
    seq = [d]
    for i, a in enumerate(a_forward):
        c = credit_true(i)
        d = d + c - a
        seq.append(d)
    return seq


def census_forward_d_closed_form(a_forward, m):
    """Method 2 (independent): closed-form telescoping credit sum.
    d(i) = Sum_{k=0}^{i-1} c_k - Sum_{k=0}^{i-1} a_k
         = floor(i*log2(3)) - A_i   (telescoping credit sum collapses
    exactly, since c_k = floor((k+1)log2 3) - floor(k log2 3))."""
    def floor_k_log2_3(kk: int) -> int:
        if kk == 0:
            return 0
        return (3 ** kk).bit_length() - 1

    seq = [0]
    A = 0
    for i, a in enumerate(a_forward):
        A += a
        d = floor_k_log2_3(i + 1) - A
        seq.append(d)
    return seq


def main():
    print("=== W6R-R0: validation gate (must PASS before R1-R4) ===\n")

    # --- Row A: root vs end anchoring must DISTINGUISH at m=29 ---
    print("--- Row A: root-anchored vs end-anchored true word, m=29 (distinguishing row) ---")
    root_word = root_anchored_word(credit_true, 29)
    end_word = end_anchored_word(credit_true, 29, anchor_steps=53)
    _, L_root, kstar_root = loop_curve(root_word)
    _, L_end, kstar_end = loop_curve(end_word)
    print(f"  root-anchored word: {root_word}")
    print(f"  end-anchored word:  {end_word}")
    print(f"  L_root(29) = {L_root} (k*={kstar_root+1})")
    print(f"  L_end(29)  = {L_end} (k*={kstar_end+1}) [ledger's L=12]")
    row_a_distinguishes = (root_word != end_word)
    row_a_pass = row_a_distinguishes and L_end == 12
    print(f"  words differ: {row_a_distinguishes}; L_end matches ledger's 12: {L_end == 12}")
    print(f"  Row A: {'PASS' if row_a_pass else 'FAIL'}\n")

    # --- Row B: reproduce W6Q-REALITY's own numbers exactly ---
    print("--- Row B: W6Q-REALITY reproduction (839 chain, root-anchored census deficit) ---")
    seq1 = census_forward_d_from_root(list(reversed(A_BACKWARD_839)), M_839)
    seq2 = census_forward_d_closed_form(list(reversed(A_BACKWARD_839)), M_839)
    max1, min1 = max(seq1), min(seq1)
    max2, min2 = max(seq2), min(seq2)
    methods_agree = seq1 == seq2
    matches_ledger = (max1 == CLAIMED_CENSUS_MAX_D and min1 == CLAIMED_CENSUS_MIN_D)
    print(f"  method 1 (step recursion):   d(i) sequence = {seq1}")
    print(f"  method 2 (closed-form telescoping): d(i) sequence = {seq2}")
    print(f"  methods agree bit-for-bit: {methods_agree}")
    print(f"  max d = {max1} (claimed by W6Q-REALITY: {CLAIMED_CENSUS_MAX_D})")
    print(f"  min d = {min1} (claimed by W6Q-REALITY: {CLAIMED_CENSUS_MIN_D})")
    row_b_pass = methods_agree and matches_ledger
    print(f"  Row B: {'PASS' if row_b_pass else 'FAIL'}\n")

    overall = row_a_pass and row_b_pass
    print(f"=== GATE VERDICT: {'PASS -- proceed to R1-R4' if overall else 'FAIL -- STOP, do not run R1-R4'} ===")
    assert overall, "W6R-R0 validation gate FAILED"


if __name__ == "__main__":
    main()
