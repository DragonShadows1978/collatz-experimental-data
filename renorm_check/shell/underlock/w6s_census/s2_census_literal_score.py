#!/usr/bin/env python3
"""
W6S step 2 -- score the verified 839/m=29 trajectory under the
CENSUS's LITERAL Rust semantics, re-implemented verbatim from
rust/lock3_census.rs (read directly, line numbers cited below), NOT
from the Python k0_canonical_engine.canonical_D reimplementation that
W6R trusted at face value. This is the step W6R skipped: W6R's
canonical_D docstring explicitly asserts "no separate fixed ceiling
C; ceiling-on is exactly the g(k)>=0 prefix constraint, nothing else"
(w6k/k0_canonical_engine.py lines ~18-21) -- this claim is checked
here against the literal .rs source instead of taken on faith.

=== Literal census semantics, read directly from rust/lock3_census.rs ===

1. credit_at_step(k) = floor((k+1)log2 3) - floor(k log2 3)  (line 1247-1249)
   -- IDENTICAL formula to the game's credit_true / k0's credit_true.

2. Growth loop (run_census, line ~2080-2081; identical shape in
   run_census_lean, line ~2417-2418):
       for next_depth in (start_depth+1)..=config.depth:
           c = credit_at_step(next_depth - 1)
   At the transition INTO depth next_depth (producing the next_depth-th
   tree level from the (next_depth-1)-th), the credit letter used is
   credit_at_step(next_depth - 1). Writing k = next_depth - 1 (0-indexed
   step number, k=0 is the FIRST transition, out of the root
   Key::new(0,0) at depth 0): c_k = credit_at_step(k). This is EXACTLY
   the root-anchored (k=0 at trajectory start) indexing W6Q and W6R
   both already established. No new finding here -- W6R's indexing
   convention is confirmed correct against the literal source.

3. THE PART W6R'S PYTHON REIMPLEMENTATION DID NOT INCLUDE -- the
   deficit transition itself (run_census, lines 2093-2103; identical
   shape in run_census_lean, lines 2461+):

       let branch_capacity = deficit_branch_capacity(config.c);
       // config.c = the CLI --C capacity ceiling
       if let Some(max_deficit) = max_deficit_for_c(config.c) {
           // max_deficit_for_c(c) = Some(c) if c>=0 else None
           for d_next in 0..=max_deficit {
               // d_next ranges over [0, C] INCLUSIVE -- HARD UPPER BOUND
               let a = key.deficit() + c - d_next;
               // a is DERIVED from d_next, not the reverse
               if a < 1 { continue; }
               // legality: a must be >= 1 (a=0 illegal -- v2 is always >=1)
               // only d_next in [0,C] with resulting a>=1 produces a child
           }
       }

   deficit_branch_capacity/max_deficit_for_c (lines 1251-1265):
       fn deficit_branch_capacity(c: i64) -> usize { if c<0 {0} else {(c as usize)+1} }
       fn max_deficit_for_c(c: i64) -> Option<i64> { if c<0 {None} else {Some(c)} }
   Key::new (lines 268-273): panics if deficit<0 (or > u32::MAX) -- i.e.
   deficit MUST be in [0, u32::MAX], and the growth loop itself
   additionally restricts the ENUMERATED range to [0, config.c] -- the
   tree NEVER contains a state with deficit > config.c. This is
   independently confirmed by run_census_lean's own inline comments
   (lines ~2427-2436): "exit_up: state has a valid transition to
   d_next > C (breach upward)" -- d_next > C is explicitly named a
   BREACH / EXIT event, not a state the corridor-tracking census ever
   contains going forward.

   For a FIXED, given a-sequence (like our witness), the census's
   legality rule for step k (deficit d_prev -> d_next, credit c_k,
   move a_k) is therefore:
       d_next = d_prev + c_k - a_k
       LEGAL iff  0 <= d_next <= config.c   AND   a_k >= 1
   If a proposed d_next falls outside [0, config.c], the census's
   growth loop's `for d_next in 0..=max_deficit` NEVER PRODUCES that
   child at all -- there is no state to continue from. This is a HARD
   WALL in BOTH directions (upper AND lower), not merely d_next>=0.

   Compare to k0_canonical_engine.canonical_D's ceiling_on=True branch
   (game's own g(k), NEGATIVE of d by the established g/d duality):
       if ceiling_on and running2 < 0: continue   # ONLY a lower bound on g
   There is NO corresponding upper bound on g (no lower bound on d)
   anywhere in canonical_D. This script computes both quantities side
   by side and pinpoints, numerically, exactly where (if anywhere) the
   two-sided rule bites for this specific trajectory.
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).parent

A_BACKWARD = [4, 3, 2, 1, 1, 4, 2, 2, 1, 6, 1, 1, 1, 2, 2, 2, 1, 2, 1, 2, 4, 1, 2, 1, 1, 2, 2, 1, 1]
A_FORWARD = list(reversed(A_BACKWARD))
M = 29


def credit_true(k: int) -> int:
    """credit_at_step(k) verbatim (rust/lock3_census.rs lines 1247-1249):
    floor((k+1)log2 3) - floor(k log2 3), exact via bit_length on 3**k."""
    def floor_klog2_3(kk: int) -> int:
        if kk == 0:
            return 0
        return (3 ** kk).bit_length() - 1
    return floor_klog2_3(k + 1) - floor_klog2_3(k)


def game_g_sequence(anchor_steps: int = 53):
    """GAME convention (existing, end-anchored at 53, ledger's own
    quantity, UNCHANGED -- this is what W6P-URGENT claimed D_ceil=11 for)."""
    letters = [credit_true(anchor_steps - 1 - j) for j in range(M)]
    running = 0
    g = [0]
    for c, a in zip(letters, A_BACKWARD):
        running += (a - c)
        g.append(running)
    return letters, g


def census_literal_forward(a_forward, C: int):
    """Faithful re-implementation of the run_census/run_census_lean
    growth-loop legality rule for a SINGLE fixed a-sequence: at each
    step, d_next = d_prev + c_k - a_k is computed; LEGAL iff
    0 <= d_next <= C and a_k >= 1. Returns the deficit trace and the
    first index (if any) at which the census tree would NOT have
    produced this trajectory as a live state (bankruptcy point)."""
    d = 0
    seq = [d]
    letters = []
    legal = True
    breach_index = None
    breach_kind = None
    for i, a in enumerate(a_forward):
        c_k = credit_true(i)  # k = i, root-anchored, per literal .rs indexing
        letters.append(c_k)
        d_next = d + c_k - a
        if a < 1:
            legal = False
            if breach_index is None:
                breach_index, breach_kind = i, "a<1"
        elif d_next > C:
            legal = False
            if breach_index is None:
                breach_index, breach_kind = i, "upper (d_next > C)"
        elif d_next < 0:
            legal = False
            if breach_index is None:
                breach_index, breach_kind = i, "lower (d_next < 0)"
        seq.append(d_next)
        d = d_next
    return letters, seq, legal, breach_index, breach_kind


def main():
    out = []

    def p(s=""):
        print(s)
        out.append(s)

    p("=== W6S step 2: literal census (.rs-faithful) scoring of the m=29 witness ===\n")

    game_letters, game_g = game_g_sequence(anchor_steps=53)
    p(f"GAME g(k) (end-anchored@53, backward-consumption, ledger's own quantity): {game_g}")
    p(f"  max g = {max(game_g)}  (W6P-URGENT's claimed D_ceil = 11: {max(game_g) == 11})")
    p(f"  min g = {min(game_g)} (never negative -> D_ceil-legal by the GAME's own rule)")

    for C_TEST in (11, 12):
        p(f"\n--- CENSUS literal scoring at capacity C={C_TEST} (root-anchored, forward, hard ceiling [0,{C_TEST}]) ---")
        letters, d_seq, legal, breach_i, breach_kind = census_literal_forward(A_FORWARD, C_TEST)
        p(f"  census letters (k=0..28): {letters}")
        p(f"  census d(i), i=0..29: {d_seq}")
        p(f"  max d = {max(d_seq)}, min d = {min(d_seq)}")
        p(f"  LEGAL under census's literal two-sided ceiling for all 29 steps: {legal}")
        if not legal:
            p(f"  FIRST ILLEGAL STEP (breach/bankruptcy point): forward index i={breach_i}, kind={breach_kind}")
            p(f"    at i={breach_i}: d_prev={d_seq[breach_i]}, c_k={letters[breach_i]}, a={A_FORWARD[breach_i]}, "
              f"d_next(computed, would-be)={d_seq[breach_i+1]}")

    p("\n\n=== FULL STEP-BY-STEP TABLE (forward time order i=0..28, values after step shown as index i+1) ===")
    letters11, d_seq11, legal11, breach_i11, breach_kind11 = census_literal_forward(A_FORWARD, 11)
    p(f"{'i':>3} {'a_fwd_i':>8} {'census_c_k':>11} {'census_d(i+1)':>14} {'legal@C=11':>11}")
    d = 0
    for i, a in enumerate(A_FORWARD):
        c_k = credit_true(i)
        d_next = d + c_k - a
        ok = (0 <= d_next <= 11) and (a >= 1)
        marker = "  <-- FIRST ILLEGAL" if i == breach_i11 else ("  <-- illegal" if not ok else "")
        p(f"{i:>3} {a:>8} {c_k:>11} {d_next:>14} {str(ok):>11}{marker}")
        d = d_next

    p(f"\nVERDICT (literal census, C=11): trajectory {'SURVIVES' if legal11 else 'DOES NOT SURVIVE'} "
      f"all 29 steps inside the census's tracked corridor [0,11].")
    if not legal11:
        p(f"First bankruptcy/breach at forward step i={breach_i11} ({breach_kind11}).")

    with open(HERE / "s2_output.log", "w") as f:
        f.write("\n".join(out) + "\n")
    with open(HERE / "s2_census_literal_table.json", "w") as f:
        json.dump({
            "a_forward": A_FORWARD,
            "game_g": game_g,
            "game_max": max(game_g),
            "census_C11": {"letters": letters11, "d_seq": d_seq11, "legal": legal11,
                           "breach_index": breach_i11, "breach_kind": breach_kind11},
        }, f, indent=2)


if __name__ == "__main__":
    main()
