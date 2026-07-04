#!/usr/bin/env python3
"""
W6K new machinery: a direct, exhaustive engine for the CANONICAL-ORDER
game (architect ruling, DERIVATION_NOTES sec 2), for reuse by K1/K2/K3
once it passes the K0 gate. Independent implementation from
w6e/e1_walkers.py and w6f/f1_engine_ext.py (does not import either) --
only reuses the two tiny validated residue-arithmetic primitives from
w6e/engine.py (forced_parity_for_backward_step, backward_predecessor_exact),
which are pure facts about the residue map, not part of what K0 tests
for direction/convention correctness.

Canonical order: letters consumed backward, index 0 = nearest terminal.
D(m) = min over admissible exponent processes of max_k g(k), g(k) =
sum_{j<=k} (a_j - c_j) -- DERIVATION_NOTES sec 2. Two ceiling variants,
carried explicitly and never collapsed:
  D_ceil: processes restricted to g(k) >= 0 at every prefix k.
  D_free: unrestricted (g(k) may go negative at intermediate prefixes).

Exhaustiveness / correctness argument: at each backward step, the
exponent a is FORCED to one parity by the current (exact-integer,
untruncated) residue rho -- there is no other legal-move restriction
in the canonical order's own definition (no separate fixed ceiling C;
"ceiling-on" is exactly the g(k)>=0 prefix constraint, nothing else).
For finite words (m<=~12, the K1 scope) an exhaustive DFS over ALL
admissible a at ALL steps, with a generous per-step exponent cap
(a_cap), is complete PROVIDED the cap is never actually the binding
constraint on the achieved optimum -- checked mechanically below via
`cap_margin_check` (rerun at a larger cap, confirm the answer is
unchanged) rather than assumed.

NOTE (deliberate near-duplicate, flagged not hidden): this module's
`canonical_D` is intentionally similar in shape to
`k0_convention_gate.hand_reference` -- both implement the exact same
boxed definition above, from scratch, independently, as two separate
files/entry points on purpose (one lives in the gate script as a
throwaway cross-check; this one is the importable module K1/K2/K3
actually call). They are cross-checked against each other in the K0
gate run (PATH C uses THIS module; step 0 uses hand_reference); any
divergence between them would itself be a K0 finding.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402


def canonical_D(letters, ceiling_on: bool, a_cap: int = 40):
    """Exhaustive branch-and-bound DFS, canonical order. Letters given
    in CONSUMPTION order (index 0 = nearest terminal). Prunes branches
    whose running max already exceeds the best complete answer found
    so far (valid: max_so_far is monotone nondecreasing along any DFS
    extension, so such branches can never improve on best)."""
    m = len(letters)
    best = [None]

    def dfs(j, rho, running, max_so_far):
        if best[0] is not None and max_so_far >= best[0]:
            return
        if j == m:
            if best[0] is None or max_so_far < best[0]:
                best[0] = max_so_far
            return
        c = letters[j]
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return
        a_min = 2 if parity == 0 else 1
        for a in range(a_min, a_min + a_cap, 2):
            running2 = running + (a - c)
            if ceiling_on and running2 < 0:
                continue
            rho2 = backward_predecessor_exact(rho, a)
            max2 = max(max_so_far, running2)
            dfs(j + 1, rho2, running2, max2)

    dfs(0, 1, 0, 0)
    return best[0]


def cap_margin_check(letters, ceiling_on: bool, base_cap: int = 40, wider_cap: int = 80):
    """Confirm a_cap is not the binding constraint: rerun at a much
    wider cap and require the same answer."""
    d1 = canonical_D(letters, ceiling_on, a_cap=base_cap)
    d2 = canonical_D(letters, ceiling_on, a_cap=wider_cap)
    return d1 == d2, d1, d2


if __name__ == "__main__":
    WORDS = {
        "13": (1, 3), "31": (3, 1), "113": (1, 1, 3),
        "311": (3, 1, 1), "123": (1, 2, 3), "321": (3, 2, 1),
    }
    for word, canon in WORDS.items():
        for order, letters in [("canonical", canon), ("reverse", tuple(reversed(canon)))]:
            for ceiling_on in (True, False):
                ok, d1, d2 = cap_margin_check(letters, ceiling_on)
                print(f"word={word:4} order={order:9} ceiling_on={ceiling_on!s:5} "
                      f"D={d1} (margin-check {'OK' if ok else f'FAIL d1={d1} d2={d2}'})")
