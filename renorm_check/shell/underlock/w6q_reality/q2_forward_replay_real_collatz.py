#!/usr/bin/env python3
"""
W6Q-REALITY step 1b -- forward replay of X=839 under the REAL Collatz
odd-step map, checking whether it reproduces the exact exponent
sequence a = [4,3,2,1,1,4,2,2,1,6,1,1,1,2,2,2,1,2,1,2,4,1,2,1,1,2,2,1,1]
(backward-consumption order; FORWARD order is the reverse of this,
since index 0 = nearest terminal = LAST in forward time, index 28 =
farthest from terminal = FIRST in forward time).

Real Collatz odd-step map: given odd x, compute y = 3x+1, then divide
out all factors of 2: y = 2^v * y', v = v2(3x+1), y' odd. Record v.
Next odd iterate is y'.

Exact Python integers throughout, no floats.
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).parent

A_BACKWARD = [4, 3, 2, 1, 1, 4, 2, 2, 1, 6, 1, 1, 1, 2, 2, 2, 1, 2, 1, 2, 4, 1, 2, 1, 1, 2, 2, 1, 1]
# Forward-time order = reverse of backward-consumption order (index 28 first, index 0 last)
A_FORWARD_EXPECTED = list(reversed(A_BACKWARD))

X_START = 839


def v2(n: int) -> int:
    """Exact 2-adic valuation of positive integer n."""
    assert n > 0
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v


def collatz_odd_step(x: int):
    """One odd Collatz step: x odd -> 3x+1 -> strip all factors of 2.
    Returns (next_odd, exponent_realized)."""
    assert x % 2 == 1, f"collatz_odd_step called on even x={x}"
    y = 3 * x + 1
    a = v2(y)
    y_odd = y >> a
    return y_odd, a


def main():
    out = []

    def p(s=""):
        print(s)
        out.append(s)

    p("=== W6Q-REALITY Step 1b: forward Collatz replay from X=839 ===\n")
    p(f"Expected forward-time exponent sequence (reverse of ledger's backward-order a): {A_FORWARD_EXPECTED}")
    p(f"Starting integer X = {X_START} (odd: {X_START % 2 == 1})\n")

    x = X_START
    trace = []
    a_realized = []
    match_all = True
    first_divergence = None

    for step in range(29):
        if x % 2 == 0:
            p(f"*** STEP {step}: x={x} is EVEN -- not a valid odd Collatz iterate. HALTING. ***")
            first_divergence = step
            match_all = False
            break
        x_next, a_real = collatz_odd_step(x)
        expected_a = A_FORWARD_EXPECTED[step]
        ok = (a_real == expected_a)
        trace.append({"step": step, "x_odd": x, "3x+1": 3 * x + 1, "a_realized": a_real,
                      "a_expected": expected_a, "match": ok, "x_next": x_next})
        p(f"  fwd step {step:2d}: x={x:>6}  3x+1={3*x+1:>7}  v2={a_real}  "
          f"(expected a={expected_a})  {'OK' if ok else '*** MISMATCH ***'}  -> x_next={x_next}")
        a_realized.append(a_real)
        if not ok and first_divergence is None:
            first_divergence = step
            match_all = False
        x = x_next

    p(f"\nFinal odd iterate after 29 steps: {x}")
    p(f"Realized exponent sequence (forward time): {a_realized}")
    p(f"Expected exponent sequence (forward time): {A_FORWARD_EXPECTED}")
    p(f"FULL SEQUENCE MATCH: {a_realized == A_FORWARD_EXPECTED}")
    if first_divergence is not None:
        p(f"FIRST DIVERGENCE at forward step {first_divergence}")
    p(f"\nTerminal odd value after 29 real Collatz steps starting from 839: {x}")
    p(f"(compare to ledger's 'terminal residue 839' -- note: 839 was the START here, "
      f"not necessarily the same slot as this end value)")

    # Extra: also try walking MANY more steps to see long-run behavior / sanity.
    p(f"\n--- Sanity: continue the true Collatz trajectory from 839 a further 20 steps ---")
    x2 = x
    for extra in range(20):
        if x2 == 1:
            p(f"  reached 1 after this many extra odd-steps: {extra}")
            break
        if x2 % 2 == 0:
            p(f"  hit even value unexpectedly: {x2}")
            break
        x2n, a2 = collatz_odd_step(x2)
        p(f"  extra step {extra}: x={x2} -> 3x+1={3*x2+1} v2={a2} -> {x2n}")
        x2 = x2n

    with open(HERE / "q2_output.log", "w") as f:
        f.write("\n".join(out) + "\n")

    return a_realized, A_FORWARD_EXPECTED, match_all, first_divergence, trace


if __name__ == "__main__":
    main()
