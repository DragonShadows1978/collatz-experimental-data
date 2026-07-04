#!/usr/bin/env python3
"""
W6D-G -- periodic credit words for the under-lock ground-truth order
(shell/W6D_GROUND_TRUTH_ORDER.md).

Three words, all pure integer arithmetic (no floats anywhere):

  golden-per8  : c_k = floor(13(k+1)/8) - floor(13k/8)
                 MECHANICAL WORD of the convergent slope 13/8 (a
                 convergent of alpha=phi; 2-13/8 = 3/8). Period 8,
                 asserted 3 ones + 5 twos per period.

  sqrt2-per12  : c_k = floor(17(k+1)/12) - floor(17k/12)
                 MECHANICAL WORD of the convergent slope 17/12 (a
                 convergent of alpha=sqrt2; 2-17/12 = 7/12). Period 12,
                 asserted 7 ones + 5 twos per period.

  golden-tile8 : the first 8 letters of the TRUE golden Sturmian word
                 [1,2,1,2,2,1,2,1], tiled with period 8. Contrast
                 control ONLY -- the WRONG object per the order's
                 CRITICAL SPEC (tiling the true word's prefix is NOT
                 the same as the mechanical convergent word; this tile
                 carries 4 ones/period, slope 1/2, not 3/8).

Each c_k in {1, 2} for the two mechanical words by construction
(consecutive floor-differences of a slope in (1,2)); golden-tile8 is
built directly from the literal true-word prefix so its per-symbol
values are exactly the listed integers, not re-derived.

All assertions (period, per-period support/drop counts) must run and
PASS before any measurement, per the order's binding CRITICAL SPEC.
"""

from __future__ import annotations

from fractions import Fraction


# ---------------------------------------------------------------------
# golden-per8: mechanical word of convergent 13/8 of alpha=phi
# ---------------------------------------------------------------------

def credit_golden_per8(k: int) -> int:
    """c_k = floor(13(k+1)/8) - floor(13k/8). Pure integer division."""
    return (13 * (k + 1)) // 8 - (13 * k) // 8


PERIOD_GOLDEN_PER8 = 8
ONES_GOLDEN_PER8 = 3   # p = 13 - 2*8 ... see assertion below for the exact count check
TWOS_GOLDEN_PER8 = 5


# ---------------------------------------------------------------------
# sqrt2-per12: mechanical word of convergent 17/12 of alpha=sqrt2
# ---------------------------------------------------------------------

def credit_sqrt2_per12(k: int) -> int:
    """c_k = floor(17(k+1)/12) - floor(17k/12). Pure integer division."""
    return (17 * (k + 1)) // 12 - (17 * k) // 12


PERIOD_SQRT2_PER12 = 12
ONES_SQRT2_PER12 = 7
TWOS_SQRT2_PER12 = 5


# ---------------------------------------------------------------------
# golden-tile8: contrast control -- literal true-word prefix, tiled
# ---------------------------------------------------------------------

_GOLDEN_TRUE_PREFIX8 = (1, 2, 1, 2, 2, 1, 2, 1)  # verbatim from the order


def credit_golden_tile8(k: int) -> int:
    """First 8 letters of the TRUE golden Sturmian word, tiled with
    period 8. Deliberately the WRONG object (tiling vs mechanical-word
    distinction; see module docstring and the work order's CRITICAL SPEC)."""
    return _GOLDEN_TRUE_PREFIX8[k % 8]


PERIOD_GOLDEN_TILE8 = 8
ONES_GOLDEN_TILE8 = 4
TWOS_GOLDEN_TILE8 = 4


# ---------------------------------------------------------------------
# Assertions -- MUST run and pass before any measurement.
# ---------------------------------------------------------------------

def assert_period_and_counts(credit_fn, period: int, expected_ones: int,
                              expected_twos: int, label: str,
                              n_periods_check: int = 2000) -> str:
    """Assert credit_fn has exactly `period` and exactly expected_ones/
    expected_twos per period, checked over n_periods_check repetitions
    (pure integer arithmetic, exact by construction). Returns a receipt
    string; raises AssertionError on any violation."""
    # 1. Check period: c_k == c_{k+period} for a long stretch.
    n_check = period * n_periods_check
    seq = [credit_fn(k) for k in range(n_check + period)]
    for k in range(n_check):
        if seq[k] != seq[k + period]:
            raise AssertionError(
                f"{label}: NOT period-{period} at k={k}: "
                f"c_k={seq[k]} != c_(k+{period})={seq[k+period]}"
            )
    # 2. Check no smaller period divides it falsely (period is exact,
    #    not just a multiple of the true period) -- verify no proper
    #    divisor of `period` also works.
    for d in range(1, period):
        if period % d != 0:
            continue
        if all(seq[k] == seq[k + d] for k in range(n_check - d)):
            raise AssertionError(
                f"{label}: period is NOT exactly {period} -- "
                f"smaller period {d} also satisfies periodicity"
            )
    # 3. Check per-period support (c=1) and drop (c=2) counts, and that
    #    no other symbol values occur.
    one_period = seq[:period]
    ones = sum(1 for c in one_period if c == 1)
    twos = sum(1 for c in one_period if c == 2)
    others = [c for c in one_period if c not in (1, 2)]
    if others:
        raise AssertionError(f"{label}: unexpected symbol values {others}")
    if ones != expected_ones:
        raise AssertionError(
            f"{label}: expected {expected_ones} ones/period, got {ones} "
            f"(period-block={one_period})"
        )
    if twos != expected_twos:
        raise AssertionError(
            f"{label}: expected {expected_twos} twos/period, got {twos} "
            f"(period-block={one_period})"
        )
    if ones + twos != period:
        raise AssertionError(
            f"{label}: ones+twos={ones+twos} != period={period}"
        )
    receipt = (
        f"{label}: PASS -- period={period} (verified exact, no smaller "
        f"divisor works, over {n_periods_check} repetitions = {n_check} "
        f"letters), ones={ones}, twos={twos} per period, block={one_period}"
    )
    return receipt


def run_all_assertions() -> list:
    receipts = []
    receipts.append(assert_period_and_counts(
        credit_golden_per8, PERIOD_GOLDEN_PER8, ONES_GOLDEN_PER8,
        TWOS_GOLDEN_PER8, "golden-per8"))
    receipts.append(assert_period_and_counts(
        credit_sqrt2_per12, PERIOD_SQRT2_PER12, ONES_SQRT2_PER12,
        TWOS_SQRT2_PER12, "sqrt2-per12"))
    receipts.append(assert_period_and_counts(
        credit_golden_tile8, PERIOD_GOLDEN_TILE8, ONES_GOLDEN_TILE8,
        TWOS_GOLDEN_TILE8, "golden-tile8"))
    # Cross-check: golden-per8's block is NOT golden-tile8's block (the
    # whole point of the CRITICAL SPEC distinction) -- assert they differ.
    block_per8 = tuple(credit_golden_per8(k) for k in range(8))
    block_tile8 = tuple(credit_golden_tile8(k) for k in range(8))
    if block_per8 == block_tile8:
        raise AssertionError(
            "golden-per8 and golden-tile8 blocks are IDENTICAL -- "
            "this would invalidate the contrast control; spec says "
            "they must differ (3/8 mechanical vs 1/2 tiled)"
        )
    receipts.append(
        f"cross-check: golden-per8 block={block_per8} != "
        f"golden-tile8 block={block_tile8} -- CONFIRMED DISTINCT (PASS)"
    )
    # Sanity: convergent fractions match the order's arithmetic.
    beta_golden = 2 - Fraction(13, 8)
    if beta_golden != Fraction(3, 8):
        raise AssertionError(f"golden-per8: 2-13/8={beta_golden} != 3/8")
    beta_sqrt2 = 2 - Fraction(17, 12)
    if beta_sqrt2 != Fraction(7, 12):
        raise AssertionError(f"sqrt2-per12: 2-17/12={beta_sqrt2} != 7/12")
    receipts.append(
        "arithmetic check: 2-13/8=3/8 (PASS), 2-17/12=7/12 (PASS)"
    )
    return receipts


if __name__ == "__main__":
    for r in run_all_assertions():
        print(r)
