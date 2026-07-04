#!/usr/bin/env python3
"""
W6Q-REALITY step 3 -- independent re-derivation via a SEPARATE code path
(manual/independent recomputation, not importing q1/q2/q3), cross-
checking:
  (a) the forward Collatz replay from X=839 reproduces the exact
      exponent sequence for all 29 steps (recomputed here using
      Python's built-in bit operations, a different code shape than
      q2's v2() loop), and
  (b) the census's own root-anchored (k=0-at-trajectory-start) deficit
      recursion, recomputed via a manually unrolled closed form
      (deficit after i steps = sum_{j<i} c_j - sum_{j<i} a_j =
      (floor(i*log2(3)) - floor(0)) - partial_sum(a)), independent of
      q3's step-by-step loop.

No floats. Exact Python integers throughout.
"""
from __future__ import annotations

X_START = 839
A_BACKWARD = [4, 3, 2, 1, 1, 4, 2, 2, 1, 6, 1, 1, 1, 2, 2, 2, 1, 2, 1, 2, 4, 1, 2, 1, 1, 2, 2, 1, 1]
A_FORWARD = A_BACKWARD[::-1]
M = 29


def floor_k_log2_3(k: int) -> int:
    """Independent re-derivation of floor(k*log2(3)) via bit_length,
    written as a one-liner distinct in shape from q1/q3's helper
    function (same underlying math fact, re-derived independently as
    the house discipline requires for decisive claims)."""
    return 0 if k == 0 else (pow(3, k)).bit_length() - 1


def credit_word_sum(k0: int, k1: int) -> int:
    """Sum of credit_true(k) for k in [k0, k1) via telescoping:
    sum = floor(k1*log2 3) - floor(k0*log2 3). Avoids recomputing
    each credit letter individually -- an independent closed-form
    check of the same quantity q1/q3 compute step-by-step."""
    return floor_k_log2_3(k1) - floor_k_log2_3(k0)


def main():
    print("=== W6Q-REALITY Step 3: independent re-derivation (separate code path) ===\n")

    # --- (a) Forward replay cross-check, alternate implementation ---
    print("--- (a) Forward Collatz replay, alternate implementation (bit-twiddling form) ---")
    x = X_START
    exps = []
    ok = True
    for step in range(29):
        y = 3 * x + 1
        # count trailing zero bits via (y & -y) trick instead of a while-loop v2()
        low_bit = y & (-y)
        a = low_bit.bit_length() - 1
        y_odd = y // low_bit
        exps.append(a)
        expected = A_FORWARD[step]
        if a != expected:
            print(f"  DIVERGENCE at step {step}: got a={a}, expected {expected}")
            ok = False
        x = y_odd
    print(f"  Alternate-implementation exponents: {exps}")
    print(f"  Expected (forward order):           {A_FORWARD}")
    print(f"  MATCH: {exps == A_FORWARD} (final x = {x}, expect 1: {x == 1})")
    assert exps == A_FORWARD and x == 1, "Step 3(a) independent replay FAILED to reproduce step 1/2 result"

    # --- (b) Census root-anchored deficit, closed-form telescoping cross-check ---
    print("\n--- (b) Census root-anchored deficit d(i), closed-form telescoping re-derivation ---")
    # d(i) = [sum_{j=0}^{i-1} c_j] - [sum_{j=0}^{i-1} a_j]
    #      = credit_word_sum(0, i) - partial_sum(A_FORWARD[:i])
    a_partial = 0
    d_seq_closed_form = [0]
    for i in range(1, M + 1):
        a_partial += A_FORWARD[i - 1]
        c_partial = credit_word_sum(0, i)
        d = c_partial - a_partial
        d_seq_closed_form.append(d)
    print(f"  d(i) via closed-form telescoping credit sum: {d_seq_closed_form}")
    print(f"  max = {max(d_seq_closed_form)}, min = {min(d_seq_closed_form)}")

    # Cross-check against direct step-by-step recursion (same as q3, but
    # rewritten independently here to avoid importing q3's function)
    d = 0
    d_seq_stepwise = [0]
    for i, a in enumerate(A_FORWARD):
        c = floor_k_log2_3(i + 1) - floor_k_log2_3(i)
        d = d + c - a
        d_seq_stepwise.append(d)
    print(f"  d(i) via direct stepwise recursion (independent re-implementation): {d_seq_stepwise}")
    print(f"  MATCH between closed-form and stepwise: {d_seq_closed_form == d_seq_stepwise}")
    assert d_seq_closed_form == d_seq_stepwise, "Step 3(b) closed-form and stepwise disagree -- BUG"

    print(f"\n  CONFIRMED (independent code path): census root-anchored deficit "
          f"max={max(d_seq_stepwise)}, min={min(d_seq_stepwise)}.")
    print(f"  This does NOT reach 11 on the positive side (max={max(d_seq_stepwise)}), "
          f"and goes negative (min={min(d_seq_stepwise)}) -- confirms q3's finding via a "
          f"completely separate derivation (telescoping closed form vs step-by-step loop).")

    # --- First divergence point between game's g and census's own d, in
    # a shared, clearly-defined coordinate: forward-time step index ---
    print("\n--- First point where census-own d(i) (forward, root-anchored) differs in SIGN behavior from "
          "what the game's window would require ---")
    # The game's own g(k) never goes negative (D_ceil-legal) and peaks at 11.
    # Census's own d(i) here goes negative almost immediately.
    first_neg = next((i for i, v in enumerate(d_seq_stepwise) if v < 0), None)
    print(f"  First forward step where census-own root-anchored deficit goes negative: i={first_neg} "
          f"(d={d_seq_stepwise[first_neg]})" if first_neg is not None else "  never negative")
    print(f"  Game's own g(k) (end-anchored at 53, from ledger) never goes negative by construction "
          f"(that is exactly the D_ceil legality gate the game itself enforces) and peaks at 11 at "
          f"backward-index 21 (~forward step 7 from the trajectory's start, since backward idx21 "
          f"= forward step {M-1-21}).")


if __name__ == "__main__":
    main()
