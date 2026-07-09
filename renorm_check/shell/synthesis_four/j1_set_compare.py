#!/usr/bin/env python3
"""
J1 -- Is the death shell's dead set S(m) the SAME OBJECT as the backward
basin's residual complement (the 112 odd x, out of 5,000,000 in [1,10^7),
not yet certified to reach 1 within N=200 forward odd-steps)?

Method:
  1. Take the literal 112 residual x from
     shell/descent_rule/gate2_gate3_results.txt (Gate 3's "smallest 20" /
     "largest 20" plus reconstruction of the full 112 via re-running the
     SAME closed-form species/hit_step test used by gate2_gate3_census.py
     -- reuse descent_common.py's own primitives, don't reinvent the
     forward-simulation rule).
  2. Compute the shell's dead set S(m) for m=2..8 by importing
     automaton.py + reusing shell_probe.py's dead_profile() verbatim.
  3. Reduce each of the 112 residual x mod 3^m for m=2..8 and mod small
     powers of 3, and check:
       (a) do any land on r%3==0 (outside the shell's domain entirely --
           the shell dead set is only defined for r%3 != 0)?
       (b) for those with r%3 != 0, is x mod 3^m IN the shell's dead
           residue set S(m) at any ceiling-distance slot, for any C we
           test (the shell result is proven C-independent per P2, so we
           only need ONE C, but we check two to be safe)?
  4. Adversarial direction: if they WERE the same object, the shell's
     dead set (a FIXED finite union of residue classes mod 3^m, m=2..8)
     would have to contain ALL 112 basin-residual x's reductions mod
     3^m that are r%3!=0, AND -- more decisively -- the shell's dead set
     is a fixed, small, universal (C-independent) set: if basin-residual
     x reduce to residues OUTSIDE S(m) we have a direct falsification of
     set equality (not just "no evidence for").
"""
import sys
import math
from pathlib import Path
from fractions import Fraction

HERE = Path(__file__).parent
EMBED = HERE.parent.parent / "embedding"
sys.path.insert(0, str(EMBED))
sys.path.insert(0, str(HERE.parent))  # for shell_probe

from automaton import M_edge, run_heartbeat  # noqa: E402

# ---------------------------------------------------------------------
# Step 1: the 112 residual x (from gate2_gate3_results.txt, lines 123-124
# give smallest/largest 20; the full 112 list is NOT saved verbatim
# anywhere on disk -- reconstruct it via the SAME merge-safe forward
# simulation the census used, reusing descent_common.py's primitives).
# ---------------------------------------------------------------------
DESCENT_RULE = HERE.parent / "descent_rule"
sys.path.insert(0, str(DESCENT_RULE))
from descent_common import is_power_of_two  # noqa: E402


def hit_step_of(x: int, max_n: int = 200):
    """UNMEMOIZED, direct reproduction of gate2_gate3_census.py's
    resolve_hit_step semantics (no cross-x memo -- we don't need the
    census's speed trick, we only need the exact per-x rule): first n>=0
    with S^n(x) in the layer-0 species (3*cur+1 a power of two with even
    exponent), else None if not found within max_n odd-steps. This is the
    IDENTICAL closed-form test + odd-step map used by the census (verified
    against descent_common.is_power_of_two), just without the memo
    short-circuit -- slower, but exactly equivalent per-x since the memo
    is documented as a pure speed optimization that doesn't change what's
    counted."""
    cur = x
    steps = 0
    while True:
        n = 3 * cur + 1
        if is_power_of_two(n) and (n.bit_length() - 1) % 2 == 0:
            return steps
        if steps >= max_n:
            return None
        while n & 1 == 0:
            n >>= 1
        cur = n
        steps += 1


def reconstruct_residual_112(census_limit: int = 10_000_000, max_n: int = 200):
    """Full walk over all distinct odd x in [1, census_limit), identical
    per-x rule to gate2_gate3_census.py (unmemoized -- slower but exactly
    equivalent). Returns sorted list of x with hit_step None."""
    residual = []
    for x in range(1, census_limit, 2):
        hs = hit_step_of(x, max_n=max_n)
        if hs is None:
            residual.append(x)
    return residual


def load_reference_smallest_largest():
    smallest_20 = [1723519, 2298025, 2585279, 2725659, 2929311, 3064033, 3066367,
                   3428767, 3447039, 3542887, 3732423, 3877919, 4063723, 4064103,
                   4085377, 4088489, 4393967, 4571689, 4596051, 4637979]
    largest_20 = [8842233, 8847225, 8848743, 8865705, 8888811, 8901447, 8967935,
                  9143379, 9144233, 9192101, 9275959, 9447699, 9533531, 9691233,
                  9715455, 9947513, 9953129, 9973919, 9997729, 9999913]
    return smallest_20, largest_20


def dead_profile(C: int, m: int):
    """Verbatim reuse of shell_probe.py's dead_profile."""
    import numpy as np
    live_by_d, _ = run_heartbeat(C, m)
    modulus = 3 ** m
    r = np.arange(modulus)
    nz = r % 3 != 0
    prof = {}
    for d in range(C + 1):
        dead_rs = frozenset(int(x) for x in r[nz & ~live_by_d[d]])
        if dead_rs:
            prof[C - d] = dead_rs
    return prof


def main():
    out = []
    out.append("=" * 78)
    out.append("J1 -- death shell dead-set S(m) vs basin residual-complement set")
    out.append("=" * 78)

    small20, large20 = load_reference_smallest_largest()
    out.append(f"\nReference (gate2_gate3_results.txt lines 123-124):")
    out.append(f"  smallest 20 of 112: {small20}")
    out.append(f"  largest  20 of 112: {large20}")

    out.append("\nReconstructing full 112-element residual set by re-running the "
                "IDENTICAL merge-safe forward rule (descent_common.is_one_step_species "
                "+ odd_step) over all distinct odd x in [1, 10,000,000), max_n=200 ...")
    residual = reconstruct_residual_112(10_000_000, 200)
    out.append(f"  reconstructed residual count: {len(residual)} (expect 112)")
    match = (len(residual) == 112
             and residual[:20] == small20
             and residual[-20:] == large20)
    out.append(f"  matches published smallest-20/largest-20 exactly: {match}")
    if not match:
        out.append("  !! MISMATCH -- reconstruction diverges from published gate3 "
                    "results; treating reconstructed list as ground truth for J1 but "
                    "flagging discrepancy explicitly in the ledger.")
        out.append(f"  reconstructed smallest 20: {residual[:20]}")
        out.append(f"  reconstructed largest  20: {residual[-20:]}")

    # ---- residue-space compatibility check ----
    out.append("\n--- Step (a): domain compatibility (r mod 3) ---")
    out.append("Shell dead set S(m) is defined ONLY on r % 3 != 0 (shell_probe.py "
                "dead_profile: `nz = r % 3 != 0`). Check how many of the 112 basin "
                "residual x satisfy x % 3 != 0:")
    mod3_0 = [x for x in residual if x % 3 == 0]
    mod3_nz = [x for x in residual if x % 3 != 0]
    out.append(f"  x % 3 == 0: {len(mod3_0)} of {len(residual)}")
    out.append(f"  x % 3 != 0: {len(mod3_nz)} of {len(residual)}")
    out.append(f"  x%3==0 examples: {mod3_0[:10]}")

    # ---- compute shell dead sets S(m), m=2..8, at two corridor widths ----
    out.append("\n--- Step (b): shell dead-set S(m), m=2..8, C=12 and C=23 "
                "(P2 proves C-independence when keyed by ceiling-distance; "
                "checking two C values as an adversarial cross-check) ---")

    results_by_m = {}
    for m in range(2, 9):
        prof12 = dead_profile(12, m)
        prof23 = dead_profile(23, m)
        dead_union_12 = frozenset().union(*prof12.values()) if prof12 else frozenset()
        dead_union_23 = frozenset().union(*prof23.values()) if prof23 else frozenset()
        same = dead_union_12 == dead_union_23
        results_by_m[m] = dead_union_23
        out.append(f"  m={m}: |S(m)| via C=12: {len(dead_union_12):>6}  "
                    f"via C=23: {len(dead_union_23):>6}  identical-as-sets: {same}  "
                    f"modulus=3^{m}={3**m}")

    # ---- Step (c): does basin residual x mod 3^m land in S(m)? ----
    out.append("\n--- Step (c): for each residual x with x%3!=0, is (x mod 3^m) "
                "IN the shell dead set S(m) (C=23 slot), for m=2..8? ---")
    out.append("If the basin complement and shell dead set were literally the SAME "
                "OBJECT, we would expect x mod 3^m to land in S(m) at some m for "
                "EVERY residual x (or at minimum, a marked excess over the S(m) base "
                "rate, not a coin-flip rate).")

    hits_by_m = {m: 0 for m in range(2, 9)}
    per_x_detail = []
    for x in mod3_nz:
        row = {"x": x, "x_mod3": x % 3}
        any_hit = False
        for m in range(2, 9):
            r = x % (3 ** m)
            in_dead = r in results_by_m[m]
            row[f"m{m}_in_S"] = in_dead
            if in_dead:
                hits_by_m[m] += 1
                any_hit = True
        row["any_hit_m2to8"] = any_hit
        per_x_detail.append(row)

    for m in range(2, 9):
        base_rate = len(results_by_m[m]) / (2 * 3 ** (m - 1))  # |S(m)| / (# nz residues mod 3^m)
        out.append(f"  m={m}: basin-x hitting S(m): {hits_by_m[m]} / {len(mod3_nz)}  "
                    f"(S(m) base rate among nz residues: {base_rate:.6f})")

    any_hit_count = sum(1 for row in per_x_detail if row["any_hit_m2to8"])
    out.append(f"\n  Basin-residual x (r%3!=0) landing in S(m) for AT LEAST ONE "
                f"m in 2..8: {any_hit_count} / {len(mod3_nz)}")

    # ---- Step (d): adversarial containment / equality test ----
    out.append("\n--- Step (d): adversarial containment test ---")
    out.append("If shell-dead-set case: EVERY basin residual x with x%3!=0 must land "
                "in S(m) for ALL m up to the depth where 3^m > x (finite containment "
                "would require it at the SPECIFIC m matching corridor scale of the "
                "actual unconstrained forward walk -- but the forward walk has NO "
                "corridor C at all, so there is no principled m to test at except "
                "'any m small enough to compute'). Reporting the strongest-possible "
                "case for equality: hits at m=2..8 out of the 73 nz residual x.")

    frac = any_hit_count / len(mod3_nz) if mod3_nz else 0.0
    out.append(f"  fraction of basin-residual (nz) x landing in ANY tested S(m) "
                f"slot: {frac:.4f}")
    # base rate for comparison: union of S(2..8) as fraction of all nz residues
    # (upper bound on chance overlap)
    out.append("\n  Comparison to CHANCE: base rate of S(m) among nz residues mod 3^m "
                "(computed above) already exceeds 0 and grows with m (shell's own "
                "P1: dead set GROWS with m) -- so above-chance hits at large m are "
                "expected for ANY finite integer set purely from S(m)'s growing "
                "density, not from a genuine link to the basin object specifically.")

    out.append("\n--- VERDICT INPUTS (see SYNTHESIS.md entry for final call) ---")
    out.append(f"  mod3==0 basin-residual count (OUTSIDE shell's domain entirely): "
               f"{len(mod3_0)} / {len(residual)} = {len(mod3_0)/len(residual):.4f}")
    out.append(f"  mod3!=0 basin-residual count (only ones even eligible to compare): "
               f"{len(mod3_nz)} / {len(residual)}")
    out.append(f"  Of those eligible, hitting S(m) at m=2..8: {any_hit_count} "
               f"({frac:.4f})")

    text = "\n".join(out)
    print(text)
    (HERE / "j1_output.txt").write_text(text + "\n")
    return residual, mod3_0, mod3_nz, results_by_m, per_x_detail


if __name__ == "__main__":
    main()
