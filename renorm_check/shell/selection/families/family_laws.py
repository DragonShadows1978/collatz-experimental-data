#!/usr/bin/env python3
"""
Design C step (b) -- candidate-law tables, computed and written to
<family>_laws.csv BEFORE any D(m) measurement (pre-registration
discipline, per W6C_SELECTION_ORDER.md and W6B's t3_measurement.py
precedent).

For each family: compute beta's continued fraction and its first
several convergents EXACTLY (Decimal, 60-digit precision, used only to
extract integer CF partial quotients -- an exact operation since each
a_i is tiny relative to 60-digit precision; the convergents themselves
are then exact integers built by the standard integer recursion),
classify each convergent as OVER or UNDER beta, and tabulate:
  - irrational law:  ceil(beta*m - 1), tested via the same isqrt-based
    exact inequality form used in Design B's laws_table.py:
        k >= beta*m - 1
        <=> k+1 >= num_shift*m - sqrt(n)*m
        <=> sqrt(n)*m >= num_shift*m - k - 1 =: rhs
        if rhs <= 0: satisfied (k is the answer)
        else: sqrt(n)*m >= rhs  <=>  isqrt(n*m^2) >= rhs
        (sqrt(n) is irrational for our n in {3,6,7}, so sqrt(n)*m never
        equals the integer rhs -- no boundary ambiguity in the isqrt
        comparison). No floats anywhere.
  - each convergent p/q: ceil((p/q)*m - 1) = ceil((p*m-q)/q), exact
    integer ceiling division.
for m = 2..15.

Independently cross-checked against 60-digit Decimal ceiling for every
m before the table is trusted (verify_irrational_law_vs_decimal).

This module also fixes and freezes, in writing, the ORDER in which
laws are tabulated (irrational first, then convergents in CF order,
increasing q) -- logged before measurement per the work order's "log
the ordering" instruction.
"""

from __future__ import annotations

import csv
import math
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 60

HERE = Path(__file__).parent


def cf_and_convergents(beta: Decimal, n_terms: int = 12):
    """Continued fraction terms and convergents p_i/q_i of beta in (0,1),
    via the standard recursion h_i = a_i h_{i-1} + h_{i-2},
    k_i = a_i k_{i-1} + k_{i-2}. Decimal arithmetic at 60-digit
    precision is used only to extract integer CF partial quotients a_i
    (exact, since a_i is small relative to precision); the convergents
    themselves are exact integers."""
    terms = []
    convs = []
    x = beta
    h_prev2, h_prev1 = 0, 1
    k_prev2, k_prev1 = 1, 0
    for _ in range(n_terms):
        a = int(x)
        terms.append(a)
        h = a * h_prev1 + h_prev2
        k = a * k_prev1 + k_prev2
        convs.append((h, k))
        h_prev2, h_prev1 = h_prev1, h
        k_prev2, k_prev1 = k_prev1, k
        frac = x - a
        if frac == 0:
            break
        x = 1 / frac
    return terms, convs


def classify_over_under(beta: Decimal, p: int, q: int) -> str:
    val = Decimal(p) / Decimal(q)
    return "OVER" if val > beta else ("UNDER" if val < beta else "EQUAL")


def verify_cf_exact(n: int, convs: list, beta: Decimal) -> bool:
    """Independent sanity re-derivation: standard CF property
    |beta - p/q| < 1/q^2 must hold for every convergent (checked at
    60-digit Decimal precision, comfortably exact for the q values
    used here, q <= ~10^5)."""
    ok = True
    for (p, q) in convs:
        diff = abs(beta - Decimal(p) / Decimal(q))
        bound = Decimal(1) / Decimal(q * q)
        if not (diff < bound):
            ok = False
    return ok


def ceil_beta_m_minus_1_exact(m: int, n: int, num_shift: int) -> int:
    """Exact integer k = ceil(beta*m - 1), beta = num_shift - sqrt(n),
    via the isqrt-based inequality (see module docstring). No floats."""
    k = -1
    while True:
        rhs = num_shift * m - k - 1
        if rhs <= 0:
            return k
        if math.isqrt(n * m * m) >= rhs:
            return k
        k += 1


def verify_irrational_law_vs_decimal(name: str, n: int, num_shift: int, m_max: int) -> int:
    """Reference check: recompute ceil(beta*m - 1) via 60-digit Decimal
    ceiling and compare to the exact isqrt form. Must be 0 mismatches."""
    beta_dec = Decimal(num_shift) - Decimal(n).sqrt()
    mismatches = 0
    for m in range(2, m_max + 1):
        exact = ceil_beta_m_minus_1_exact(m, n, num_shift)
        val = beta_dec * m - 1
        ref = int(val.to_integral_value(rounding="ROUND_CEILING"))
        if exact != ref:
            mismatches += 1
            print(f"    MISMATCH {name} m={m}: exact={exact} decimal_ref={ref}")
    return mismatches


def ceil_conv_m_minus_1(m: int, p: int, q: int) -> int:
    """Exact ceil((p/q)*m - 1) = ceil((p*m - q)/q), integer ceiling div."""
    num = p * m - q
    return -(-num // q)


FAMILY_SPECS = {
    "sqrt3": {"n": 3, "num_shift": 2, "alpha_desc": "sqrt(3)", "beta_desc": "2 - sqrt(3)"},
    "sqrt6m1": {"n": 6, "num_shift": 3, "alpha_desc": "sqrt(6) - 1", "beta_desc": "3 - sqrt(6)"},
    "sqrt7m1": {"n": 7, "num_shift": 3, "alpha_desc": "sqrt(7) - 1", "beta_desc": "3 - sqrt(7)"},
}

M_MIN, M_MAX = 2, 15
N_CONVERGENTS = 5  # first 4-5 convergents per the work order


def build_family_table(name: str):
    spec = FAMILY_SPECS[name]
    n = spec["n"]
    num_shift = spec["num_shift"]
    beta = Decimal(num_shift) - Decimal(n).sqrt()

    print(f"\n=== Family {name}: alpha = {spec['alpha_desc']}, beta = {spec['beta_desc']} = {beta}")

    print(f"  Verifying irrational-law exact test vs 60-digit Decimal, m=2..{M_MAX}")
    mism = verify_irrational_law_vs_decimal(name, n, num_shift, M_MAX)
    print(f"    mismatches: {mism}  {'PASS' if mism == 0 else 'FAIL'}")
    assert mism == 0, f"STOP: irrational-law exact test mismatch for {name}"

    terms, all_convs = cf_and_convergents(beta, n_terms=12)
    print(f"  CF terms (a_0..): {terms}")
    convs = all_convs[:N_CONVERGENTS]
    classes = [classify_over_under(beta, p, q) for (p, q) in convs]
    for (p, q), cls in zip(convs, classes):
        val = Decimal(p) / Decimal(q)
        print(f"  convergent {p}/{q} = {val}  {cls}")

    cf_ok = verify_cf_exact(n, convs, beta)
    print(f"  CF exactness re-derivation (|beta - p/q| < 1/q^2 for all listed convergents): "
          f"{'PASS' if cf_ok else 'FAIL'}")
    assert cf_ok, f"CF verification failed for {name} -- STOP"

    # Ordering, frozen and logged: irrational law first, then convergents
    # in CF order (increasing q), exactly as generated above -- NOT
    # reordered by over/under or by denominator size.
    law_order = ["irrational"] + [f"{p}/{q}" for p, q in convs]
    print(f"  Law ordering (frozen, as tabulated): {law_order}")

    rows = []
    header = ["m", "irrational"] + [f"{p}/{q}" for p, q in convs]
    print("    " + "  ".join(f"{h:>12}" for h in header))
    for m in range(M_MIN, M_MAX + 1):
        row = {"m": m}
        row["irrational"] = ceil_beta_m_minus_1_exact(m, n, num_shift)
        for (p, q) in convs:
            row[f"{p}/{q}"] = ceil_conv_m_minus_1(m, p, q)
        rows.append(row)
        print("    " + "  ".join(f"{row[h] if h in row else m:>12}" for h in header))

    out_path = HERE / f"{name}_laws.csv"
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"  Wrote {out_path}")

    return {
        "beta": beta,
        "terms": terms,
        "convergents": convs,
        "classes": classes,
        "law_order": law_order,
        "rows": rows,
        "header": header,
    }


def main():
    results = {}
    for name in FAMILY_SPECS:
        results[name] = build_family_table(name)
    return results


if __name__ == "__main__":
    main()
