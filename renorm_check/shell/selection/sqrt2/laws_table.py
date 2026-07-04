#!/usr/bin/env python3
"""
W6C Design B -- candidate-law table, frozen BEFORE any D_sqrt2(m) value
is read (house pre-registration discipline, per W6C_SELECTION_ORDER.md
and the exactness law).

alpha = sqrt(2), beta = 2 - sqrt(2) ~= 0.585786.
Convergents of sqrt(2)'s continued fraction [1;2,2,2,...]: 1/1, 3/2,
7/5, 17/12, 41/29, 99/70, ... The work order names beta's convergents
(beta = 2-sqrt2, continued fraction [0;1,1,2,2,2,...] with alternating
correspondence to sqrt2's own convergents): 1/2, 3/5 (over), 7/12
(under), 17/29, 41/70. These are exactly p/q for p/q in
{1/2, 3/5, 7/12, 17/29, 41/70} as named in the work order -- used
directly, not re-derived from sqrt(2)'s own convergent list.

Irrational law: ceil(beta*m - 1), exact integer test derived and
verified below (isqrt-based inequality, no floats):

    k >= beta*m - 1
    <=> k+1 >= 2m - sqrt2*m
    <=> sqrt2*m >= 2m - k - 1  =: rhs
    if rhs <= 0: always true (k satisfies the bound)
    else (rhs > 0, both sides of sqrt2*m >= rhs positive):
         sqrt2*m >= rhs  <=>  isqrt(2*m^2) >= rhs
         (equivalent to 2*m^2 >= rhs^2 since sqrt2*m is irrational,
         never equals the integer rhs, so the floor/isqrt comparison
         carries no boundary ambiguity)

Verified against a float/Decimal reference below for m=2..16 before
being trusted (report of the check is printed, not hidden).

Convergent law: ceil((p/q)*m - 1) = ceil((p*m - q)/q), exact integer
ceiling division -- same form as W6B's t3_measurement.py.

Usage: python3 laws_table.py | tee laws_table.log
Writes: laws.csv
"""

from __future__ import annotations

import csv
import math
from decimal import Decimal, getcontext
from pathlib import Path

M_MIN, M_MAX = 2, 16

CONVERGENTS = [(1, 2), (3, 5), (7, 12), (17, 29), (41, 70)]
CONVERGENT_LABELS = {
    (1, 2): "1/2",
    (3, 5): "3/5(over)",
    (7, 12): "7/12(under)",
    (17, 29): "17/29",
    (41, 70): "41/70",
}


def ceil_beta_m_minus_1_exact(m: int) -> int:
    """Exact integer k = ceil(beta*m - 1), beta = 2-sqrt(2), via the
    isqrt inequality derived in the module docstring. No floats."""
    k = -1
    while True:
        rhs = 2 * m - k - 1
        if rhs <= 0:
            return k
        if math.isqrt(2 * m * m) >= rhs:
            return k
        k += 1


def ceil_conv_m_minus_1(m: int, p: int, q: int) -> int:
    """Exact: ceil((p/q)*m - 1) = ceil((p*m - q)/q), integer ceiling division."""
    num = p * m - q
    return -(-num // q)


def verify_irrational_law_vs_decimal(m_max: int = 16) -> int:
    """Reference check: recompute ceil(beta*m - 1) via 60-digit Decimal
    ceiling and compare to the exact isqrt form. Must be 0 mismatches."""
    getcontext().prec = 60
    beta_dec = 2 - Decimal(2).sqrt()
    mismatches = 0
    for m in range(M_MIN, m_max + 1):
        exact = ceil_beta_m_minus_1_exact(m)
        val = beta_dec * m - 1
        ref = int(val.to_integral_value(rounding="ROUND_CEILING"))
        if exact != ref:
            mismatches += 1
            print(f"    MISMATCH m={m}: exact={exact} decimal_ref={ref}")
    return mismatches


def main():
    print("W6C Design B -- laws.csv table, frozen BEFORE any D_sqrt2(m) "
          "measurement (this file is written first; the log timestamp "
          "and this notice are the pre-registration record).")

    print("\nStep 1: verify the exact isqrt-based irrational-law test against "
          "60-digit Decimal ceiling, m=2..16")
    mism = verify_irrational_law_vs_decimal(M_MAX)
    print(f"    mismatches: {mism}  {'PASS' if mism == 0 else 'FAIL'}")
    if mism != 0:
        raise SystemExit("STOP: irrational-law exact test does not match Decimal reference.")

    print("\nStep 2: tabulate candidate laws, m=2..16 (irrational law = "
          "ceil(beta*m-1), beta=2-sqrt2; convergents 1/2, 3/5(over), "
          "7/12(under), 17/29, 41/70, each ceil((p/q)*m-1))")
    header = ["m", "irrational"] + [CONVERGENT_LABELS[c] for c in CONVERGENTS]
    print("    " + "  ".join(f"{h:>12}" for h in header))

    rows = []
    for m in range(M_MIN, M_MAX + 1):
        row = {"m": m, "irrational": ceil_beta_m_minus_1_exact(m)}
        for p, q in CONVERGENTS:
            row[CONVERGENT_LABELS[(p, q)]] = ceil_conv_m_minus_1(m, p, q)
        rows.append(row)
        print("    " + "  ".join(f"{row[h] if h != 'm' else m:>12}" for h in header))

    csv_path = Path(__file__).parent / "laws.csv"
    with open(csv_path, "w", newline="") as f:
        fieldnames = ["m", "irrational"] + [CONVERGENT_LABELS[c] for c in CONVERGENTS]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nWrote {csv_path}")
    print("\nThis table is now FROZEN. No D_sqrt2(m) value has been read yet "
          "(B1/B2/B3 run afterward, in separate scripts).")

    print("\nDecisive-row scan (any two candidates disagree):")
    for r in rows:
        vals = [r["irrational"]] + [r[CONVERGENT_LABELS[c]] for c in CONVERGENTS]
        decisive = len(set(vals)) > 1
        if decisive:
            print(f"    m={r['m']:>3}: {dict((h, r[h]) for h in header if h != 'm')}  DECISIVE")


if __name__ == "__main__":
    main()
