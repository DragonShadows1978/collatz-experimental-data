#!/usr/bin/env python3
"""
W6B T3 -- The measurement, per W6B_TOY_WORD_ORDER.md.

D_toy(m) for m = 2..13 (dense, wide corridor C=23, min ceiling-distance
of a live terminal, exactly as shell_probe.py P5 for the true word).

Candidate laws, tabulated BEFORE reading any D_toy value (frozen here,
same discipline as F5/W1's registered predictions):
  irrational: ceil(beta_toy*m - 1), beta_toy = 2 - phi
  convergent shadows: ceil((p/q)*m - 1) for p/q in {1/2, 2/5, 3/8, 5/13}
All via exact integer arithmetic (isqrt-based comparison for the
irrational law, exact integer ceiling division for the rationals) --
no floats anywhere, mirroring W1's mandate.

Decisive rows = every m <= 13 where any two candidates differ. Per the
work order: small constant offsets between D_toy and a law are
permitted if CONSTANT across the agreement region (fit on agreeing m,
frozen before reading decisive rows) -- the pattern of divergence is
the readout, not the absolute value.

Usage: python3 t3_measurement.py | tee t3_measurement.log
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from toy_automaton import run_heartbeat_generic, credit_toy

C_WIDE = 23
M_MAX = 13

CONVERGENTS = [(1, 2), (2, 5), (3, 8), (5, 13)]


def ceil_beta_toy_m_minus_1(m: int) -> int:
    """Exact: smallest k with k >= (2-phi)*m - 1, via m*sqrt(5) >= 3m-2k-2
    (derived from k+1 >= (2-phi)*m, phi=(1+sqrt5)/2), tested with isqrt-free
    exact integer comparison 5*m^2 >= (3m-2k-2)^2 when RHS > 0."""
    k = -1
    while True:
        rhs = 3 * m - 2 * k - 2
        if rhs <= 0:
            return k
        if 5 * m * m >= rhs * rhs:
            return k
        k += 1


def ceil_conv_m_minus_1(m: int, p: int, q: int) -> int:
    """Exact: ceil((p/q)*m - 1) = ceil((p*m - q)/q), integer ceiling division."""
    num = p * m - q
    return -(-num // q)


def tabulate_candidates():
    print("Candidate law table (frozen BEFORE reading D_toy), m=2..13")
    header = ["m", "irrational"] + [f"{p}/{q}" for p, q in CONVERGENTS]
    print("    " + "  ".join(f"{h:>10}" for h in header))
    table = {}
    for m in range(2, M_MAX + 1):
        row = {"irrational": ceil_beta_toy_m_minus_1(m)}
        for p, q in CONVERGENTS:
            row[f"{p}/{q}"] = ceil_conv_m_minus_1(m, p, q)
        table[m] = row
        print("    " + "  ".join(f"{row.get(h, m) if h != 'm' else m:>10}" for h in header))
    return table


def measure_D_toy():
    print(f"\nMeasuring D_toy(m): min ceiling-distance of a live terminal, "
          f"C={C_WIDE}, m=2..{M_MAX}")
    results = {}
    for m in range(2, M_MAX + 1):
        modulus = 3 ** m
        live_by_d, _ = run_heartbeat_generic(C_WIDE, m, credit_toy, steps=53)
        alive_depths = [C_WIDE - d for d in range(C_WIDE + 1) if live_by_d[d][1 % modulus]]
        D_emp = min(alive_depths) if alive_depths else None
        results[m] = D_emp
        print(f"    m={m:>2}: D_toy={D_emp}", flush=True)
    return results


def main():
    table = tabulate_candidates()
    D_toy = measure_D_toy()

    print("\nT3 readout: D_toy(m) vs each candidate law, m=2..13")
    print("    " + "  ".join(f"{h:>10}" for h in
          ["m", "D_toy", "irrational"] + [f"{p}/{q}" for p, q in CONVERGENTS]))
    decisive_rows = []
    csv_rows = []
    for m in range(2, M_MAX + 1):
        row = table[m]
        d = D_toy[m]
        vals = [row["irrational"]] + [row[f"{p}/{q}"] for p, q in CONVERGENTS]
        all_same = len(set(vals)) == 1
        if not all_same:
            decisive_rows.append(m)
        match_str = "  ".join(f"{v:>10}" for v in vals)
        print(f"    {m:>10}  {d if d is not None else 'None':>10}  {match_str}"
              f"  {'DECISIVE' if not all_same else ''}", flush=True)
        csv_rows.append({"m": m, "D_toy": d, "irrational": row["irrational"],
                          **{f"{p}/{q}": row[f"{p}/{q}"] for p, q in CONVERGENTS}})

    print(f"\nDecisive rows (candidates disagree): {decisive_rows}")

    with open(Path(__file__).parent / "D_toy_table.csv", "w", newline="") as f:
        fieldnames = ["m", "D_toy", "irrational"] + [f"{p}/{q}" for p, q in CONVERGENTS]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in csv_rows:
            w.writerow(r)
    print("Wrote D_toy_table.csv")

    return decisive_rows, D_toy, table


if __name__ == "__main__":
    main()
