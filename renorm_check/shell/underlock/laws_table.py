#!/usr/bin/env python3
"""
W6D-G -- candidate law tables, written BEFORE any D measurement (the
mtime of the CSVs this script produces is the pre-registration record,
per the order and per W6C convention).

Raw law, per W6C convention (reused verbatim from
shell/selection/families/family_laws.py, which this file imports):
  law(m) = ceil(beta*m - 1) for a rational law beta=p/q via exact
  integer ceiling division, and via the isqrt-based exact inequality
  ceil_beta_m_minus_1_exact() for irrational betas of the quadratic-
  surd form beta = num_shift - sqrt(n) -- no floats anywhere in the
  law itself (Decimal is used only as an independent cross-check,
  exactly as family_laws.py does).

Covers, per m=2..16:
  - golden-per8's own law family: irrational (beta=2-phi=(3-sqrt5)/2),
    1/2, 2/5, 3/8, 5/13 -- for cross-reference against the TRUE golden
    word's established table (shell/toy_word/D_toy_table.csv).
  - sqrt2-per12's own law family: irrational (beta=2-sqrt2), 1/2,
    3/5, 7/12, 17/29, 41/70 -- for cross-reference against the TRUE
    sqrt2 word's established table
    (shell/selection/sqrt2/D_sqrt2_table.csv).
  - golden-tile8 (contrast control): slope-1/2 and slope-3/8 laws,
    the two candidates G3 must discriminate between.

This is the FROZEN, pre-data prediction surface. Offset-fitting (on
agreement rows, after measurement, per the registered protocol) is
applied separately in RESULTS_D1.md, not here.
"""

from __future__ import annotations

import csv
import math
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "selection" / "families"))
from family_laws import (  # noqa: E402
    ceil_beta_m_minus_1_exact,
    ceil_conv_m_minus_1,
)

M_MIN, M_MAX = 2, 16

# golden: beta = 2 - phi = (3 - sqrt(5)) / 2 -- NOT of the num_shift-sqrt(n)
# form directly (there's a /2), so we derive an isqrt-exact form specific
# to this beta rather than reusing ceil_beta_m_minus_1_exact's n/num_shift
# signature verbatim.
GOLDEN_RATIONAL_LAWS = [("1/2", 1, 2), ("2/5", 2, 5), ("3/8", 3, 8), ("5/13", 5, 13)]
SQRT2_RATIONAL_LAWS = [("1/2", 1, 2), ("3/5", 3, 5), ("7/12", 7, 12),
                        ("17/29", 17, 29), ("41/70", 41, 70)]
TILE8_RATIONAL_LAWS = [("1/2", 1, 2), ("3/8", 3, 8)]


def ceil_golden_beta_m_minus_1_exact(m: int) -> int:
    """Exact integer ceil(beta*m - 1), beta = (3-sqrt5)/2 = 2-phi.
    beta*m - 1 = (3m - 2)/2 - sqrt(5)*m/2 = (3m - 2 - m*sqrt5)/2.
    We want smallest k with k >= (3m-2-m*sqrt5)/2, i.e.
    2k >= 3m - 2 - m*sqrt5, i.e. m*sqrt5 >= 3m - 2 - 2k, i.e.
    (for the RHS positive) isqrt(5*m*m) >= 3m - 2 - 2k.
    Same isqrt-inequality-ladder approach as family_laws.py's
    ceil_beta_m_minus_1_exact, adapted for the /2 in this beta."""
    k = -1
    while True:
        rhs = 3 * m - 2 - 2 * k
        if rhs <= 0:
            return k
        if math.isqrt(5 * m * m) >= rhs:
            return k
        k += 1


def verify_golden_irrational_vs_decimal(m_max: int) -> int:
    from decimal import getcontext
    getcontext().prec = 60
    beta_dec = (Decimal(3) - Decimal(5).sqrt()) / 2
    mismatches = 0
    for m in range(2, m_max + 1):
        exact = ceil_golden_beta_m_minus_1_exact(m)
        val = beta_dec * m - 1
        ref = int(val.to_integral_value(rounding="ROUND_CEILING"))
        if exact != ref:
            mismatches += 1
            print(f"    MISMATCH golden-irrational m={m}: exact={exact} decimal_ref={ref}")
    return mismatches


def write_golden_laws(path: Path):
    mism = verify_golden_irrational_vs_decimal(M_MAX)
    assert mism == 0, "golden irrational-law exact-vs-Decimal cross-check FAILED"
    print(f"  golden irrational-law cross-check: 0 mismatches over m=2..{M_MAX} (PASS)")

    rows = []
    for m in range(M_MIN, M_MAX + 1):
        row = {"m": m, "irrational": ceil_golden_beta_m_minus_1_exact(m)}
        for label, p, q in GOLDEN_RATIONAL_LAWS:
            row[label] = ceil_conv_m_minus_1(m, p, q)
        rows.append(row)
    fieldnames = ["m", "irrational"] + [lbl for lbl, _, _ in GOLDEN_RATIONAL_LAWS]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return rows


def write_sqrt2_laws(path: Path):
    # beta = 2 - sqrt2 is exactly family_laws.py's num_shift-sqrt(n) form
    # with n=2, num_shift=2 -- reuse ceil_beta_m_minus_1_exact directly.
    from family_laws import verify_irrational_law_vs_decimal
    mism = verify_irrational_law_vs_decimal("sqrt2", 2, 2, M_MAX)
    assert mism == 0, "sqrt2 irrational-law exact-vs-Decimal cross-check FAILED"
    print(f"  sqrt2 irrational-law cross-check: 0 mismatches over m=2..{M_MAX} (PASS)")

    rows = []
    for m in range(M_MIN, M_MAX + 1):
        row = {"m": m, "irrational": ceil_beta_m_minus_1_exact(m, 2, 2)}
        for label, p, q in SQRT2_RATIONAL_LAWS:
            row[label] = ceil_conv_m_minus_1(m, p, q)
        rows.append(row)
    fieldnames = ["m", "irrational"] + [lbl for lbl, _, _ in SQRT2_RATIONAL_LAWS]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return rows


def write_tile8_laws(path: Path):
    rows = []
    for m in range(M_MIN, M_MAX + 1):
        row = {"m": m}
        for label, p, q in TILE8_RATIONAL_LAWS:
            row[label] = ceil_conv_m_minus_1(m, p, q)
        rows.append(row)
    fieldnames = ["m"] + [lbl for lbl, _, _ in TILE8_RATIONAL_LAWS]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return rows


def main():
    here = Path(__file__).parent
    g_path = here / "laws_golden.csv"
    s_path = here / "laws_sqrt2.csv"
    t_path = here / "laws_tile8.csv"
    print("=== golden-per8 law family ===")
    write_golden_laws(g_path)
    print("=== sqrt2-per12 law family ===")
    write_sqrt2_laws(s_path)
    print("=== golden-tile8 law family (contrast control) ===")
    write_tile8_laws(t_path)
    print(f"\nWrote {g_path}")
    print(f"Wrote {s_path}")
    print(f"Wrote {t_path}")
    print("Pre-registration record: these mtimes precede any D measurement.")


if __name__ == "__main__":
    main()
