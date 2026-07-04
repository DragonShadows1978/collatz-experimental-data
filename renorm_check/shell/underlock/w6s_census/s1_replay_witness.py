#!/usr/bin/env python3
"""
W6S step 1 -- independent exact-integer replay of W6R's m=29 root-
anchored witness chain (same underlying a-sequence W6Q used for its
839 chain: W6R's r1_root_break_table.csv row m=29 records the IDENTICAL
witness a_seq (4,3,2,1,1,4,2,2,1,6,1,1,1,2,2,2,1,2,1,2,4,1,2,1,1,2,2,1,1)
as W6P-URGENT/W6Q-REALITY's true-word m=29 counterexample chain).

This script:
  (a) reconstructs the chain backward from rho=1 via the exact identity
      rho' = (2^a * rho - 1) / 3, verifying every division is exact,
  (b) forward-replays it as a genuine integer Collatz trajectory,
      checking v2(3x+1) matches the claimed exponent at every one of
      the 29 odd-steps, in FORWARD order,
  (c) reports the key numbers (starting integer, all intermediate
      values, final value) so the replay is independently checkable.

No floats anywhere. Pure Python arbitrary-precision integers.
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).parent

# Witness a-sequence, BACKWARD-CONSUMPTION order (index 0 = nearest
# terminal rho=1), taken verbatim from w6r/r1_root_break_table.csv row
# m=29 (identical to W6P-URGENT/W6Q-REALITY's own 839 chain).
A_BACKWARD = [4, 3, 2, 1, 1, 4, 2, 2, 1, 6, 1, 1, 1, 2, 2, 2, 1, 2, 1, 2, 4, 1, 2, 1, 1, 2, 2, 1, 1]
M = 29
assert len(A_BACKWARD) == M


def backward_predecessor_exact(rho: int, a: int) -> int:
    """rho' = (2^a * rho - 1) / 3; must be an exact integer division."""
    num = (1 << a) * rho - 1
    if num % 3 != 0:
        raise ValueError(f"NOT exactly divisible by 3: rho={rho} a={a} num={num} num%3={num % 3}")
    return num // 3


def v2(n: int) -> int:
    assert n > 0
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v


def collatz_odd_step(x: int):
    assert x % 2 == 1
    y = 3 * x + 1
    a = v2(y)
    return y >> a, a


def main():
    out = []

    def p(s=""):
        print(s)
        out.append(s)

    p("=== W6S step 1: independent exact replay of m=29 witness chain ===\n")
    p(f"a_seq (backward-consumption order, from w6r/r1_root_break_table.csv m=29): {A_BACKWARD}")

    # --- Backward reconstruction ---
    p("\n--- Backward reconstruction rho=1 -> ... -> X, exact integer division at every step ---")
    rho = 1
    rho_trace = [1]
    for i, a in enumerate(A_BACKWARD):
        rho_new = backward_predecessor_exact(rho, a)
        rho_trace.append(rho_new)
        p(f"  backward step {i:2d}: a={a}  rho {rho} -> {rho_new}")
        rho = rho_new
    X = rho
    p(f"\nAll 29 backward divisions exact (zero remainder failures). Final backward value X = {X}")
    p(f"X == 839: {X == 839}")

    # --- Forward replay ---
    A_FORWARD = list(reversed(A_BACKWARD))
    p(f"\n--- Forward replay from X={X}, expected exponent sequence (forward order): {A_FORWARD} ---")
    x = X
    a_realized = []
    x_trace = [X]
    match_all = True
    first_divergence = None
    for step in range(M):
        if x % 2 == 0:
            p(f"*** STEP {step}: x={x} EVEN -- not a valid odd Collatz iterate. HALTING ***")
            first_divergence = step
            match_all = False
            break
        x_next, a_real = collatz_odd_step(x)
        expected = A_FORWARD[step]
        ok = (a_real == expected)
        p(f"  fwd step {step:2d}: x={x:>6}  3x+1={3*x+1:>7}  v2(3x+1)={a_real}  expected={expected}  "
          f"{'OK' if ok else '*** MISMATCH ***'}  -> {x_next}")
        a_realized.append(a_real)
        x_trace.append(x_next)
        if not ok and first_divergence is None:
            first_divergence = step
            match_all = False
        x = x_next

    p(f"\nFinal value after 29 real Collatz odd-steps from X={X}: {x}")
    p(f"Reaches 1: {x == 1}")
    p(f"Realized exponents == expected (forward order): {a_realized == A_FORWARD}")
    p(f"FULL SEQUENCE MATCH: {match_all}")
    if first_divergence is not None:
        p(f"FIRST DIVERGENCE at forward step {first_divergence}")

    with open(HERE / "s1_output.log", "w") as f:
        f.write("\n".join(out) + "\n")
    with open(HERE / "s1_replay_trace.json", "w") as f:
        json.dump({
            "a_backward": A_BACKWARD,
            "a_forward": A_FORWARD,
            "rho_trace_backward": [str(r) for r in rho_trace],
            "X": str(X),
            "x_trace_forward": [str(v) for v in x_trace],
            "a_realized_forward": a_realized,
            "match_all": match_all,
            "first_divergence": first_divergence,
            "reaches_one": x == 1,
        }, f, indent=2)

    return X, A_FORWARD, a_realized, match_all


if __name__ == "__main__":
    main()
