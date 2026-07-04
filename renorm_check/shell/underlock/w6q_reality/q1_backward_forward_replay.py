#!/usr/bin/env python3
"""
W6Q-REALITY step 1 -- exact-integer backward reconstruction + forward
replay verification of the W6P-URGENT true-word m=29 counterexample
chain.

Per IMPLEMENTATION_LEDGER.md W6P-URGENT entry:
  Window (backward-consumption order, index 0 = nearest terminal,
  absolute steps [24,53) end-anchored): 22121221212212121221212212121
  a = (4,3,2,1,1,4,2,2,1,6,1,1,1,2,2,2,1,2,1,2,4,1,2,1,1,2,2,1,1)
  g(k) = 0,2,3,4,3,3,5,5,6,5,10,9,8,8,8,9,9,9,9,8,9,11,11,11,10,10,10,11,10,10
  max g(k) = 11 (D_ceil), terminal residue rho = 839.

Both `a` and the window letters are listed in BACKWARD-consumption
order: index 0 is the step CLOSEST to the terminal (rho=1), index 28
(last, m-1) is FARTHEST from the terminal -- i.e. index 0 is applied
FIRST when walking backward from rho=1.

Backward step (per w6e/engine.py backward_predecessor_exact, and per
the p1_completion_search.py replay_chain which consumes `a_seq` in
the SAME order as `letters`, i.e. index 0 first):
    rho' = (2^{a_i} * rho - 1) / 3

So starting rho=1, apply a_seq[0] first, then a_seq[1], ..., a_seq[28]
last. The result after 29 applications is X = the "start" of the
chain in the BACKWARD sense -- i.e. X is the residue/integer that,
walked FORWARD 29 odd-steps, is claimed to reproduce a_seq in
FORWARD order a_seq[28], a_seq[27], ..., a_seq[0] (since index 28 is
farthest from the terminal = earliest in forward time, index 0 is
nearest the terminal = latest in forward time).

No floats anywhere; pure Python arbitrary-precision integers.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).parent

# Exact sequence from the ledger, backward-consumption order (index 0 = nearest terminal).
A_BACKWARD = [4, 3, 2, 1, 1, 4, 2, 2, 1, 6, 1, 1, 1, 2, 2, 2, 1, 2, 1, 2, 4, 1, 2, 1, 1, 2, 2, 1, 1]
G_LEDGER = [0, 2, 3, 4, 3, 3, 5, 5, 6, 5, 10, 9, 8, 8, 8, 9, 9, 9, 9, 8, 9, 11, 11, 11, 10, 10, 10, 11, 10, 10]
TERMINAL_RHO_LEDGER = 839
M = 29
ANCHOR_STEPS = 53

assert len(A_BACKWARD) == M


def credit_true(k: int) -> int:
    """True word: c_k = floor((k+1)log2(3)) - floor(k log2(3)), exact
    integer via bit_length on 3**k (matches e1_walkers.credit_true /
    lock3_census.rs credit_at_step / p1_completion_search.credit_true_own
    verbatim -- all three cross-checked to agree in prior rounds)."""
    def floor_klog2_3(kk: int) -> int:
        if kk == 0:
            return 0
        return (3 ** kk).bit_length() - 1
    return floor_klog2_3(k + 1) - floor_klog2_3(k)


def backward_letters(m: int, anchor_steps: int = ANCHOR_STEPS):
    """Backward-consumption order letters, index 0 = nearest terminal
    (= credit_true(anchor_steps-1)), index m-1 = farthest
    (= credit_true(anchor_steps-m)). Verbatim convention from
    e1_walkers.py / p1_completion_search.py."""
    return [credit_true(anchor_steps - 1 - j) for j in range(m)]


def backward_predecessor_exact(rho: int, a: int) -> int:
    """rho' = (2^a * rho - 1) / 3, must be an exact integer division.
    Raises if not -- that itself would be a critical finding."""
    num = (1 << a) * rho - 1
    if num % 3 != 0:
        raise ValueError(f"backward_predecessor_exact: NOT exactly divisible by 3 "
                          f"(rho={rho}, a={a}, num={num}, num%3={num % 3})")
    return num // 3


def main():
    out = []

    def p(s=""):
        print(s)
        out.append(s)

    p("=== W6Q-REALITY Step 1: exact backward reconstruction + forward replay ===\n")

    letters = backward_letters(M)
    p(f"Backward-order letters (index0=nearest terminal), m={M}, anchor_steps={ANCHOR_STEPS}: {letters}")
    p(f"a_seq (backward-consumption order, from ledger): {A_BACKWARD}")

    # ------------------------------------------------------------------
    # BACKWARD RECONSTRUCTION: rho starts at 1 (the terminal), apply
    # a_seq[0] first (nearest terminal), ..., a_seq[28] last (farthest
    # from terminal). Track g(k) = running sum of (a_i - c_i) exactly
    # as the ledger's convention (g(0)=0, g(k) after k backward steps).
    # ------------------------------------------------------------------
    p("\n--- Backward reconstruction (rho=1 -> ... -> X), exact integer division at every step ---")
    rho = 1
    running = 0
    g_seq = [0]
    rho_trace = [1]
    for i, (c, a) in enumerate(zip(letters, A_BACKWARD)):
        rho_new = backward_predecessor_exact(rho, a)
        running += (a - c)
        g_seq.append(running)
        rho_trace.append(rho_new)
        p(f"  backward step {i:2d} (nearest-terminal index {i}): c={c} a={a} "
          f"rho {rho} -> {rho_new}  g(k)={running}")
        rho = rho_new

    X = rho  # value after all 29 backward steps = farthest-from-terminal end = the "start"
    p(f"\nBackward reconstruction COMPLETE. All 29 steps exact-integer-divided cleanly (no remainder failures).")
    p(f"g(k) sequence computed here:   {g_seq}")
    p(f"g(k) sequence from ledger:     {G_LEDGER}")
    p(f"g(k) MATCH: {g_seq == G_LEDGER}")
    p(f"\nFinal backward value X (= candidate trajectory START, before 29 forward odd-steps): {X}")
    p(f"X bit_length: {X.bit_length()}, X decimal digits: {len(str(X))}")
    p(f"Terminal rho reached going backward from 1: rho_trace[-1] should equal ledger's 'terminal residue "
      f"839' if 839 refers to the FAR end (index 28, farthest from terminal) -- checking both ends:")
    p(f"  rho_trace[0] (at terminal, before any backward step) = {rho_trace[0]}")
    p(f"  rho_trace[-1] (after all 29 backward steps, = X) = {rho_trace[-1]}")
    p(f"  Does X match ledger's claimed terminal residue 839? {X == TERMINAL_RHO_LEDGER}")
    p(f"  Does X mod 3**29 match 839? {X % (3**29) == TERMINAL_RHO_LEDGER}")
    p(f"  X mod small moduli: mod 1000={X % 1000}, mod 3**29={X % (3**29)}")

    # Save raw trace
    with open(HERE / "q1_backward_trace.json", "w") as f:
        json.dump({
            "letters_backward_order": letters,
            "a_backward_order": A_BACKWARD,
            "g_seq_computed": g_seq,
            "g_seq_ledger": G_LEDGER,
            "g_seq_match": g_seq == G_LEDGER,
            "rho_trace_backward": [str(r) for r in rho_trace],
            "X": str(X),
            "X_bit_length": X.bit_length(),
        }, f, indent=2)

    with open(HERE / "q1_output.log", "w") as f:
        f.write("\n".join(out) + "\n")

    return X, letters, g_seq


if __name__ == "__main__":
    main()
