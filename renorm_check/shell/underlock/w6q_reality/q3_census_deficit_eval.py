#!/usr/bin/env python3
"""
W6Q-REALITY step 2 (CORRECTED) -- evaluate the verified forward
trajectory (X=839, 29 real Collatz odd-steps, exponent sequence a
forward-order = reverse of ledger's backward-consumption a, terminal
value 1) under the CENSUS's own credit/deficit/anchor convention, as
coded in rust/lock3_census.rs -- NOT the game's end-anchored-at-53
convention (w6e/engine.py, e1_walkers.py, p1_completion_search.py).

BUG FIX FROM FIRST DRAFT: an earlier version of this script tried to
"read the census deficit backward" by applying the d'=d+c-a recursion
while stepping through backward-consumption index order. That is NOT
valid: deficit is a FORWARD-ONLY recursion (d_{i+1} depends on d_i,
not the reverse), so it cannot be re-derived by walking the same
recursion in the opposite index direction and expecting the same
number sequence, reversed, to fall out. This corrected version
computes the census's deficit the ONLY way it is actually defined:
forward, from i=0 (this trajectory's own start, X=839) to i=28 (last
step before reaching 1), using credit_at_step(i) at forward step i --
exactly matching run_census's `c = credit_at_step(next_depth - 1)`
with next_depth = i+1, i.e. k = i, counting from the CENSUS's own
root (depth 0), which is where a genuine, self-contained 29-step
trajectory naturally sits if evaluated on its own terms (it has no
"24 steps of prior history" — nothing in the source code assigns it
one; that number came only from the GAME's choice of anchor_steps=53).

Both quantities (game g and census d) obey the IDENTICAL recursion
step-to-step (g' = g + (a-c), d' = d + c - a = d - (a-c), i.e.
d is simply the negative of g's recursion, both starting at 0) --
the entire question is which credit letter c is assigned to which
step of THIS SPECIFIC trajectory, i.e. which value of k indexes
credit_at_step(k) at the trajectory's i-th real Collatz step.
Because credit_true is nearly-but-not-exactly periodic (period ~12,
governed by log2(3)), the two anchoring choices assign ALMOST the
same c-letters to each step -- this script quantifies exactly how
much they diverge and what it does to the running extremum.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).parent

A_BACKWARD = [4, 3, 2, 1, 1, 4, 2, 2, 1, 6, 1, 1, 1, 2, 2, 2, 1, 2, 1, 2, 4, 1, 2, 1, 1, 2, 2, 1, 1]
A_FORWARD = list(reversed(A_BACKWARD))
M = 29


def credit_true(k: int) -> int:
    def floor_klog2_3(kk: int) -> int:
        if kk == 0:
            return 0
        return (3 ** kk).bit_length() - 1
    return floor_klog2_3(k + 1) - floor_klog2_3(k)


def game_g_sequence(m: int, anchor_steps: int = 53):
    """GAME convention: end-anchored window, backward-consumption order,
    index0=nearest terminal. Absolute credit indices used: k=anchor_steps-1
    down to anchor_steps-m (52 down to 24 for m=29, anchor_steps=53)."""
    letters = [credit_true(anchor_steps - 1 - j) for j in range(m)]
    running = 0
    g = [0]
    for c, a in zip(letters, A_BACKWARD):
        running += (a - c)
        g.append(running)
    return letters, g


def census_d_sequence_forward(a_forward, start_k: int = 0):
    """CENSUS convention: forward recursion d' = d + c - a, credit
    indexed by k = start_k, start_k+1, ..., start_k+m-1 (own trajectory
    step count from wherever this trajectory's root sits in the
    census's tree). start_k=0 is the natural placement for a genuine,
    self-contained trajectory with no assumed prior history."""
    d = 0
    seq = [d]
    letters = []
    for i, a in enumerate(a_forward):
        k = start_k + i
        c = credit_true(k)
        letters.append(c)
        d = d + c - a
        seq.append(d)
    return letters, seq


def main():
    out = []

    def p(s=""):
        print(s)
        out.append(s)

    p("=== W6Q-REALITY Step 2 (corrected): census-own-convention deficit evaluation ===\n")

    game_letters, game_g = game_g_sequence(M, anchor_steps=53)
    p("GAME convention: end-anchored window, absolute credit indices k=24..52 (backward order).")
    p(f"  game letters (backward order, idx0=nearest terminal): {game_letters}")
    p(f"  game g(k), k=0..29 (backward-consumption running sum): {game_g}")
    p(f"  game max g(k) = {max(game_g)}  (claimed D_ceil = 11, matches: {max(game_g) == 11})")

    # CENSUS convention: the ONLY well-defined computation is the forward
    # recursion. start_k=0 -- this trajectory's own natural root position,
    # since nothing establishes it as 24+ steps deep into any prior census
    # growth (that assumption belongs to the GAME's fixed anchor_steps=53
    # choice, not to the census's own indexing rule).
    census_letters_fwd, census_d_fwd = census_d_sequence_forward(A_FORWARD, start_k=0)
    p(f"\nCENSUS convention (forward recursion, root-anchored at k=0):")
    p(f"  census letters (forward order, k=0..28): {census_letters_fwd}")
    p(f"  census deficit d(i), i=0..29 (forward, i=0 is trajectory start X=839, i=29 is terminal=1): {census_d_fwd}")
    p(f"  census max d = {max(census_d_fwd)}, min d = {min(census_d_fwd)}")

    # Fair, apples-to-apples comparison table: put BOTH sequences in
    # FORWARD time order (step 0 = first real Collatz step from X=839,
    # step 28 = last, arriving at 1). The game's g(k) is defined in
    # backward-consumption order; convert it to forward-time order by
    # reversing the INCREMENTS (not the values -- g is a running sum,
    # so "forward view of the same recursion" means reading off the
    # negated increments in forward order): actually the cleanest
    # correct statement is: g and d are the SAME recursion run in
    # OPPOSITE time directions on the SAME physical step sequence, so
    # they are not directly comparable value-for-value at "the same
    # index" unless we fix a single shared time axis. We use FORWARD
    # time (i=0..28, matching the verified Collatz replay) as that
    # shared axis for both quantities below, computing each one's own
    # recursion natively in that direction using ITS OWN credit convention.
    p("\n--- Step-by-step comparison table, FORWARD time order (i=0 = first step from X=839) ---")
    p(f"{'i':>3} {'a_i':>4} {'game_k':>7} {'game_c':>7} {'census_k':>9} {'census_c':>9} "
      f"{'c_match':>8} {'census_d(after)':>16}")

    # game's credit at forward step i corresponds to backward index (M-1-i)
    n_c_mismatch = 0
    first_c_mismatch = None
    for i in range(M):
        a_i = A_FORWARD[i]
        game_k = 52 - (M - 1 - i)  # = 24+i
        gc = credit_true(game_k)
        census_k = i
        cc = credit_true(census_k)
        match = (gc == cc)
        if not match and first_c_mismatch is None:
            first_c_mismatch = i
        if not match:
            n_c_mismatch += 1
        p(f"{i:>3} {a_i:>4} {game_k:>7} {gc:>7} {census_k:>9} {cc:>9} "
          f"{str(match):>8} {census_d_fwd[i+1]:>16}")

    p(f"\nTotal credit-letter mismatches between GAME's k=24+i indexing and CENSUS's k=i indexing: "
      f"{n_c_mismatch}/{M}")
    p(f"First mismatch at forward step i={first_c_mismatch} "
      f"(game uses credit_true({24+first_c_mismatch if first_c_mismatch is not None else '-'})="
      f"{credit_true(24+first_c_mismatch) if first_c_mismatch is not None else '-'}, "
      f"census uses credit_true({first_c_mismatch})="
      f"{credit_true(first_c_mismatch) if first_c_mismatch is not None else '-'})")

    p(f"\nCENSUS's own forward deficit sequence (root-anchored at k=0): max={max(census_d_fwd)}, "
      f"min={min(census_d_fwd)}")
    p(f"Does census deficit stay within [0, 11] (D_ceil-legal AND <=11) throughout: "
      f"{all(0 <= v <= 11 for v in census_d_fwd)}")
    p(f"Does census deficit ever exceed 11: {max(census_d_fwd) > 11}")
    p(f"Does census deficit ever go negative: {min(census_d_fwd) < 0}")
    neg_indices = [i for i, v in enumerate(census_d_fwd) if v < 0]
    p(f"Negative-deficit indices (forward i, d value): "
      f"{[(i, census_d_fwd[i]) for i in neg_indices[:5]]}{'...' if len(neg_indices) > 5 else ''} "
      f"({len(neg_indices)} total)")

    p(f"\nGAME's own reported max g(k) = {max(game_g)} (this is what the ledger calls D_ceil=11).")
    p(f"CENSUS's own reported max d = {max(census_d_fwd)}, min d = {min(census_d_fwd)}.")
    p(f"These are DIFFERENT quantities computed under DIFFERENT anchoring conventions on the SAME "
      f"physical trajectory -- the comparison itself IS the finding (see verdict in ledger).")

    with open(HERE / "q3_step_by_step_table.json", "w") as f:
        json.dump({
            "a_forward": A_FORWARD,
            "game_letters_backward_order": game_letters,
            "game_g_backward_order": game_g,
            "census_letters_forward_root_anchored": census_letters_fwd,
            "census_d_forward_root_anchored": census_d_fwd,
            "n_credit_letter_mismatches_game_vs_census_indexing": n_c_mismatch,
            "first_mismatch_forward_step": first_c_mismatch,
            "census_max_deficit": max(census_d_fwd),
            "census_min_deficit": min(census_d_fwd),
            "game_max_g": max(game_g),
        }, f, indent=2)

    with open(HERE / "q3_output.log", "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
