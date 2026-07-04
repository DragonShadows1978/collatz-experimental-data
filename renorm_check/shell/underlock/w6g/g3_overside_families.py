#!/usr/bin/env python3
"""
W6G-G3 -- Over-side convergent families (the side-constant law).

Per W6G_BREAK_IT_ORDER.md G3: W6F-F3 concluded the -1 form must come
from the convergent SIDE. Build periodic credit words from OVER-side
convergents of 2-3 irrationals (2 irrationals: phi and sqrt2, the same
two families already established -- "2-3 irrationals" in the order
reads as "two or three", we use the two already-established families
for direct apples-to-apples comparison against their own under-side
siblings) and measure the D law across m=2..12.

Registered prediction: over-side families obey the -1 mirror form
floor((pm-1)/q)-analogue; under-side obey +1 (already measured).
Fable 65%.

--- Convergent-side identification (done here, shown explicitly) ---
The established toy words are MECHANICAL WORDS of slope p/q directly
(c_k = floor(p(k+1)/q) - floor(pk/q), underlock_words.py): golden-per8
uses p/q=13/8 (a convergent of alpha=phi), sqrt2-per12 uses p/q=17/12
(a convergent of alpha=sqrt2). The relevant "beta" for the D-law is
beta = 2 - alpha (golden: 2-phi=0.381966..., sqrt2: 2-sqrt2=0.585786...).
Checking the word's own beta_word = 2 - p/q against beta_true:
  golden: beta_word(13/8) = 0.375 < beta_true = 0.381966 -> UNDER-side.
  sqrt2:  beta_word(17/12) = 0.583333 < beta_true = 0.585786 -> UNDER-side.
Confirms DERIVATION_NOTES 7c's claim ("the toys locked to UNDER-side
[convergents of beta]") directly, not just taken on faith.

Continued-fraction convergents of phi ([1;1,1,1,...]) and sqrt2
([1;2,2,2,...]) ALTERNATE over/under alpha at each step, hence also
alternate over/under beta=2-alpha. The over-side sibling ADJACENT to
each established under-side word (one convergent index over, same
scale of denominator):
  golden: 13/8 (under) -> next convergent 21/13 (over). beta_word =
    2-21/13 = 5/13 = 0.384615 > beta_true=0.381966 -> OVER-side, PASS.
  sqrt2: 17/12 (under) -> next convergent 41/29 (over). beta_word =
    2-41/29 = 17/29 = 0.586207 > beta_true=0.585786 -> OVER-side, PASS.
Both checked arithmetically below (assert_word_receipts-style) before
use, not assumed.

--- Mechanical word construction (per W6D_GROUND_TRUTH_ORDER.md CRITICAL
    SPEC, matching underlock_words.py's own convention exactly: c_k =
    floor(p(k+1)/q) - floor(pk/q) directly on the convergent p/q, NOT
    e2_phase_pinning.py's P=2q-p substitution (that is a DIFFERENT,
    unrelated construction for a different purpose -- confirmed by
    f3_anchoring_map.py's own docstring catching exactly this
    confusion previously; avoided here by using underlock_words.py's
    convention verbatim). ---

Engine: w6e/engine.py's bfs_Dm_fast, validated against 3 ground truth
rows (golden-per8 m=5,9 and sqrt2-per12 m=8) inline before the sweep
(same validation block as G1/G2, reused verbatim for consistency).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from fractions import Fraction

sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
from engine import bfs_Dm_fast, bfs_Dm  # noqa: E402

HERE = Path(__file__).parent
C = 12


# ---------------------------------------------------------------------
# Established (under-side) words, reused verbatim from underlock_words.py
# ---------------------------------------------------------------------

def credit_golden_under_13_8(k: int) -> int:
    return (13 * (k + 1)) // 8 - (13 * k) // 8


def credit_sqrt2_under_17_12(k: int) -> int:
    return (17 * (k + 1)) // 12 - (17 * k) // 12


# ---------------------------------------------------------------------
# New over-side words (adjacent convergents)
# ---------------------------------------------------------------------

def make_mechanical_word(p: int, q: int):
    def fn(k: int, p=p, q=q) -> int:
        return (p * (k + 1)) // q - (p * k) // q
    return fn


GOLDEN_OVER_P, GOLDEN_OVER_Q = 21, 13   # next convergent of phi after 13/8
SQRT2_OVER_P, SQRT2_OVER_Q = 41, 29     # next convergent of sqrt2 after 17/12

credit_golden_over_21_13 = make_mechanical_word(GOLDEN_OVER_P, GOLDEN_OVER_Q)
credit_sqrt2_over_41_29 = make_mechanical_word(SQRT2_OVER_P, SQRT2_OVER_Q)


def assert_side_and_receipts():
    print("=== Convergent-side arithmetic assertions ===")
    # exact side-check via cross-multiplication (no floats)
    def compare_to_phi(p, q):
        # p/q ? phi=(1+sqrt5)/2  <=>  2p/q - 1 ? sqrt5  <=>  2p-q ? sqrt5*q
        lhs = 2 * p - q
        if lhs < 0:
            return -1  # p/q < phi definitely
        rhs2 = 5 * q * q
        lhs2 = lhs * lhs
        if lhs2 < rhs2:
            return -1
        elif lhs2 > rhs2:
            return 1
        else:
            return 0

    def compare_to_sqrt2(p, q):
        # p/q ? sqrt2 <=> p^2 ? 2q^2
        lhs2 = p * p
        rhs2 = 2 * q * q
        return -1 if lhs2 < rhs2 else (1 if lhs2 > rhs2 else 0)

    # beta_word = 2 - p/q is a DECREASING function of p/q:
    #   p/q > alpha  =>  beta_word < beta_true  =>  UNDER-side of beta.
    #   p/q < alpha  =>  beta_word > beta_true  =>  OVER-side of beta.
    c1 = compare_to_phi(13, 8)
    c2 = compare_to_phi(21, 13)
    side1 = "UNDER" if c1 > 0 else "OVER"
    print(f"  13/8 vs phi: {'>' if c1>0 else '<'} phi -> beta_word(13/8) "
          f"{'<' if c1>0 else '>'} beta_true -> {side1}-side (expect UNDER)")
    assert c1 > 0, "13/8 should be > phi (=> under-side beta convention check failed)"
    side2 = "UNDER" if c2 > 0 else "OVER"
    print(f"  21/13 vs phi: {'>' if c2>0 else '<'} phi -> {side2}-side (expect OVER)")
    assert c2 < 0, "21/13 should be < phi (=> over-side beta check failed)"

    c3 = compare_to_sqrt2(17, 12)
    c4 = compare_to_sqrt2(41, 29)
    side3 = "UNDER" if c3 > 0 else "OVER"
    print(f"  17/12 vs sqrt2: {'>' if c3>0 else '<'} sqrt2 -> {side3}-side (expect UNDER)")
    assert c3 > 0, "17/12 should be > sqrt2 (p/q>alpha => beta_word<beta_true => UNDER)"
    side4 = "UNDER" if c4 > 0 else "OVER"
    print(f"  41/29 vs sqrt2: {'>' if c4>0 else '<'} sqrt2 -> {side4}-side (expect OVER)")
    assert c4 < 0, "41/29 should be < sqrt2 (p/q<alpha => beta_word>beta_true => OVER)"
    print("  All side assertions PASS.\n")

    # Period/support receipts (same style as underlock_words.py's own assertions)
    for label, p, q in [("golden-over-21-13", GOLDEN_OVER_P, GOLDEN_OVER_Q),
                         ("sqrt2-over-41-29", SQRT2_OVER_P, SQRT2_OVER_Q)]:
        fn = make_mechanical_word(p, q)
        seq = [fn(k) for k in range(q * 3)]
        for k in range(q * 2):
            assert seq[k] == seq[k + q], f"{label}: not period-{q} at k={k}"
        ones = sum(1 for c in seq[:q] if c == 1)
        twos = sum(1 for c in seq[:q] if c == 2)
        others = [c for c in seq[:q] if c not in (1, 2)]
        assert not others, f"{label}: unexpected symbols {others}"
        assert ones + twos == q
        print(f"  RECEIPT [{label}]: period={q} verified, ones={ones}, twos={twos} "
              f"(p={p}), beta_word=2-{p}/{q}={Fraction(2) - Fraction(p, q)}")
    print()


def validate_engine():
    print("=== Pre-experiment validation (3 ground-truth rows) ===")
    checks = [
        ("golden-under m=5", credit_golden_under_13_8, 5, 2),
        ("golden-under m=9", credit_golden_under_13_8, 9, 3),
        ("sqrt2-under m=8", credit_sqrt2_under_17_12, 8, 4),
    ]
    all_pass = True
    for label, fn, m, expected in checks:
        D = bfs_Dm_fast(fn, m, C, anchor_steps=53)
        ok = (D == expected)
        print(f"  {label}: D={D} expected={expected} {'PASS' if ok else 'FAIL'}")
        all_pass = all_pass and ok
    print(f"=== {'ALL PASS' if all_pass else 'FAILED -- STOP'} ===\n")
    if not all_pass:
        raise SystemExit("Engine validation failed -- refusing to run G3.")


def candidate_forms(p_over, q_over, m):
    """+1 form and -1 mirror using the OVER-side word's BETA fraction
    (p_beta, q) = (2*q_over - p_over, q_over) -- e.g. golden-under's
    established law D_per(m)=floor((3m+1)/8) uses (p,q)=(3,8), the BETA
    of 13/8 (beta=2-13/8=3/8), NOT the word's own slope (13,8) directly.
    So for the over-side word (word-slope p_over/q_over), the matching
    beta fraction is (2*q_over-p_over, q_over) -- SAME (p,q), offset
    only, per the established convention (f3_anchoring_map.py's own
    documented convention: same (p,q) as the LAW's own beta, offset
    only, not a P=2q-p RE-substitution on top of an already-beta p,q --
    caught here: an earlier draft mistakenly passed the word's own
    slope (p_over, q_over) directly into this formula, which silently
    used the wrong fraction; fixed by deriving the beta fraction
    explicitly, matching how (3,8) and (7,12) relate to (13,8) and
    (17,12) in the established golden-per8/sqrt2-per12 laws)."""
    p_beta = 2 * q_over - p_over
    plus1 = (p_beta * m + 1) // q_over
    minus1 = (p_beta * m - 1) // q_over if p_beta * m - 1 >= 0 else None
    return plus1, minus1


def main():
    assert_side_and_receipts()
    validate_engine()

    families = [
        ("golden", credit_golden_under_13_8, credit_golden_over_21_13,
         (13, 8), (GOLDEN_OVER_P, GOLDEN_OVER_Q)),
        ("sqrt2", credit_sqrt2_under_17_12, credit_sqrt2_over_41_29,
         (17, 12), (SQRT2_OVER_P, SQRT2_OVER_Q)),
    ]
    m_scope = list(range(2, 13))  # 2..12 per the order

    results = []
    plus1_hits = 0
    minus1_hits = 0
    n_evaluated = 0

    for family_name, under_fn, over_fn, (p_u, q_u), (p_o, q_o) in families:
        for m in m_scope:
            D_over = bfs_Dm_fast(over_fn, m, C, anchor_steps=53)
            D_under = bfs_Dm_fast(under_fn, m, C, anchor_steps=53)
            plus1, minus1 = candidate_forms(p_o, q_o, m)
            plus1_hit = (D_over == plus1)
            minus1_hit = (D_over == minus1) if minus1 is not None else False
            n_evaluated += 1
            plus1_hits += plus1_hit
            minus1_hits += minus1_hit
            results.append({
                "family": family_name, "m": m,
                "D_over": D_over, "D_under": D_under,
                "p_over": p_o, "q_over": q_o,
                "plus1_form": plus1, "minus1_form": minus1,
                "plus1_hit": plus1_hit, "minus1_hit": minus1_hit,
            })
            p_beta_display = 2 * q_o - p_o
            print(f"{family_name} m={m}: D_over(word={p_o}/{q_o}, "
                  f"beta={p_beta_display}/{q_o})={D_over} "
                  f"D_under(word={p_u}/{q_u})={D_under} "
                  f"+1form={plus1}({'HIT' if plus1_hit else 'miss'}) "
                  f"-1form={minus1}({'HIT' if minus1_hit else 'miss'})")

    out_csv = HERE / "g3_overside_families.csv"
    with open(out_csv, "w", newline="") as f:
        fieldnames = ["family", "m", "D_over", "D_under", "p_over", "q_over",
                      "plus1_form", "minus1_form", "plus1_hit", "minus1_hit"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in results:
            w.writerow(r)
    print(f"\nWrote {out_csv} ({len(results)} rows)")

    print("\n=== GATE VERDICT vs frozen prediction "
          "(over-side obeys -1 mirror form; under-side already measured +1, 65%) ===")
    print(f"+1 form matches D_over: {plus1_hits}/{n_evaluated}")
    print(f"-1 form matches D_over: {minus1_hits}/{n_evaluated}")
    if minus1_hits == n_evaluated and plus1_hits < n_evaluated:
        print("HIT: clean split -- over-side obeys -1 mirror exclusively, "
              "P1b's constant DERIVED empirically.")
    elif plus1_hits == n_evaluated and minus1_hits < n_evaluated:
        print("MISS (inverted): over-side actually obeys +1 form, not -1 mirror -- "
              "opposite of the registered prediction. Report loudly.")
    elif plus1_hits == n_evaluated and minus1_hits == n_evaluated:
        print("MUDDLE: both forms match on every row in scope (they must coincide "
              "arithmetically at these m) -- inconclusive, cannot discriminate; "
              "7c's mechanism claim is untestable at this scope, report honestly.")
    else:
        print(f"MUDDLE: neither form is clean ({plus1_hits}/{n_evaluated} vs "
              f"{minus1_hits}/{n_evaluated}) -- 7c's mechanism claim as stated is WRONG, "
              f"report loudly per the order.")


if __name__ == "__main__":
    main()
