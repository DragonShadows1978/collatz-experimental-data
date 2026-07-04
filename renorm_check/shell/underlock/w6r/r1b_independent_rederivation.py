#!/usr/bin/env python3
"""
W6R-R1b -- Independent re-derivation of R1's lead finding (house rule:
"independent re-derivation for any lead finding"). R1's central claim
is that universality D_root=L_root BREAKS at m=29 under root anchoring
(D_root=12 < L_root=13), the SAME break location as the end-anchored
game, just with different numbers. This script re-derives the m=29
(and m=24, m=28 as clean-zone sanity anchors) cells with a COMPLETELY
FRESH implementation: no import of root_anchor.py, k0_canonical_engine,
or engine.py -- its own residue arithmetic, its own DFS, its own credit
function, written from scratch.
"""
from __future__ import annotations


def credit_true_fresh(k: int) -> int:
    """Independent re-derivation of c_k = floor((k+1)log2 3) - floor(k log2 3),
    using Python's arbitrary-precision integer log via bit_length on 3**k
    (same mathematical fact, re-typed, not copy-pasted)."""
    def flog(n):
        if n == 0:
            return 0
        return (3 ** n).bit_length() - 1
    return flog(k + 1) - flog(k)


def root_word_fresh(m: int):
    """Root-anchored word, backward-consumption order, built directly:
    index 0 (nearest terminal) = credit_true_fresh(m-1), ...,
    index m-1 (window start) = credit_true_fresh(0)."""
    return [credit_true_fresh(m - 1 - j) for j in range(m)]


def parity_needed(rho: int):
    """Fresh re-derivation: predecessor rho' = (2^a rho - 1)/3 must be
    integer -> 2^a*rho == 1 (mod 3). rho%3==0 -> impossible ever.
    rho%3==1 -> need 2^a%3==1 -> a even. rho%3==2 -> need 2^a%3==2 -> a odd."""
    r = rho % 3
    if r == 0:
        return None
    if r == 1:
        return "even"
    return "odd"


def predecessor(rho: int, a: int) -> int:
    num = (1 << a) * rho - 1
    if num % 3 != 0:
        raise ValueError(f"not divisible by 3: rho={rho} a={a}")
    return num // 3


def exhaustive_min_max_partial_sum(letters, a_cap=40):
    """Fresh branch-and-bound DFS (ceiling-on: running partial sum
    a_j - c_j must stay >= 0 at every prefix -- the D_ceil constraint),
    minimizing the max partial sum over all admissible chains. Written
    independently: recursion structured as an explicit stack-free
    recursive function with its own pruning, not modeled on
    k0_canonical_engine.canonical_D's code shape beyond the shared
    mathematical definition (both must implement the same spec, but
    the code below was typed fresh)."""
    m = len(letters)
    best = {"val": None}

    def go(idx, rho, running_sum, worst_so_far):
        if best["val"] is not None and worst_so_far >= best["val"]:
            return
        if idx == m:
            if best["val"] is None or worst_so_far < best["val"]:
                best["val"] = worst_so_far
            return
        need = parity_needed(rho)
        if need is None:
            return
        start_a = 1 if need == "odd" else 2
        c = letters[idx]
        a = start_a
        while a < start_a + a_cap:
            new_sum = running_sum + (a - c)
            if new_sum >= 0:
                new_worst = worst_so_far if worst_so_far > new_sum else new_sum
                new_rho = predecessor(rho, a)
                go(idx + 1, new_rho, new_sum, new_worst)
            a += 2

    go(0, 1, 0, 0)
    return best["val"]


def loop_value_fresh(letters):
    total = 0
    peak = 0
    for c in letters:
        total += (2 - c)
        if total > peak:
            peak = total
    return peak


def main():
    print("=== W6R-R1b: independent re-derivation (fresh code, no shared imports) ===\n")
    targets = [24, 28, 29, 30, 31, 32]
    results = []
    for m in targets:
        word = root_word_fresh(m)
        D = exhaustive_min_max_partial_sum(word, a_cap=40)
        D_wide = exhaustive_min_max_partial_sum(word, a_cap=80)
        L = loop_value_fresh(word)
        margin_ok = (D == D_wide)
        results.append((m, D, D_wide, L, margin_ok))
        print(f"  m={m:>3}: D_root(fresh)={D} (wide-cap check: {D_wide}, "
              f"{'OK' if margin_ok else 'MISMATCH'})  L_root(fresh)={L}  "
              f"{'MATCH' if D == L else 'BREACH'}")

    print("\n--- Cross-check against R1's production numbers ---")
    production = {24: (10, 10), 28: (12, 12), 29: (12, 13), 30: (12, 13),
                  31: (11, 13), 32: (12, 14)}
    all_agree = True
    for (m, D, D_wide, L, margin_ok) in results:
        prod_D, prod_L = production[m]
        agree = (D == prod_D and L == prod_L)
        all_agree = all_agree and agree
        print(f"  m={m}: fresh(D={D},L={L}) vs production(D={prod_D},L={prod_L}) "
              f"{'AGREE' if agree else '*** DISAGREE ***'}")

    print(f"\n=== VERDICT: independent re-derivation {'CONFIRMS' if all_agree else 'CONTRADICTS'} "
          f"R1's production run ===")
    assert all_agree, "Independent re-derivation DISAGREES with production R1 numbers"


if __name__ == "__main__":
    main()
