#!/usr/bin/env python3
"""Decode Lock 3 shadow-birth trigger residues from a birth audit CSV."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


ALPHA = 1.5849625007211563


def credit_at_step(k: int) -> int:
    return int((k + 1) * ALPHA) - int(k * ALPHA)


def unpack_key(key: int) -> tuple[int, int]:
    return key >> 32, key & 0xFFFFFFFF


def to_base3(value: int, width: int) -> str:
    digits = []
    n = value
    if n == 0:
        digits.append("0")
    while n:
        digits.append(str(n % 3))
        n //= 3
    out = "".join(reversed(digits))
    return out.rjust(width, "0")


def pow_mod(base: int, exponent: int, modulus: int) -> int:
    return pow(base, exponent, modulus)


def next_terminal_residue(residue: int, exponent: int, modulus: int) -> int:
    if modulus == 1:
        return 0
    inv = pow(pow_mod(2, exponent, modulus), -1, modulus)
    return ((3 * residue + 1) * inv) % modulus


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Decode exact modular trigger digits for Lock 3 shadow births."
    )
    parser.add_argument("birth_audit_csv", type=Path)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    rows = []
    with args.birth_audit_csv.open(newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append(row)

    if not rows:
        print("no birth rows")
        return 0

    c = int(rows[0]["C"])
    m = int(rows[0]["m"])
    modulus = 3**m
    terminal = 1 % modulus
    parent_counter: Counter[tuple[int, int, int, int]] = Counter()
    child_counter: Counter[tuple[int, int]] = Counter()
    bad = []

    for row in rows:
        depth = int(row["depth"])
        parent_key_text = row["parent_key"]
        if parent_key_text == "":
            continue
        parent_deficit = int(row["parent_deficit_state"])
        parent_residue = int(row["parent_residue_signature"])
        child_deficit = int(row["deficit_state"])
        child_residue = int(row["residue_signature"])
        exponent = parent_deficit + credit_at_step(depth - 1) - child_deficit
        predicted = next_terminal_residue(parent_residue, exponent, modulus)
        if predicted != child_residue:
            bad.append((depth, parent_deficit, parent_residue, child_deficit, child_residue, exponent, predicted))
        parent_counter[(parent_deficit, parent_residue, child_deficit, exponent)] += 1
        child_counter[(child_deficit, child_residue)] += 1

    print(f"source={args.birth_audit_csv}")
    print(f"C={c} m={m} modulus=3^{m}={modulus} terminal={terminal}")
    print(f"birth_rows={len(rows)} unique_parent_triggers={len(parent_counter)} unique_child_keys={len(child_counter)}")
    print(f"transition_validation={'PASS' if not bad else 'FAIL'}")
    if bad:
        print("first_bad=", bad[0])

    print("\nchild keys:")
    for (child_deficit, child_residue), count in child_counter.most_common(args.limit):
        print(
            f"  count={count} child_deficit={child_deficit} child_residue={child_residue} "
            f"child_base3={to_base3(child_residue, m)}"
        )

    by_parent_residue = defaultdict(int)
    for (_parent_deficit, parent_residue, _child_deficit, _exponent), count in parent_counter.items():
        by_parent_residue[parent_residue] += count

    print("\nparent trigger residues:")
    for parent_residue, count in sorted(
        by_parent_residue.items(), key=lambda item: (-item[1], item[0])
    )[: args.limit]:
        edge_offset = parent_residue - 3 ** (m - 1)
        print(
            f"  count={count} residue={parent_residue} base3={to_base3(parent_residue, m)} "
            f"offset_from_3^(m-1)={edge_offset} "
            f"residue_class='x = {parent_residue} + k*{modulus}'"
        )

    print("\nparent trigger transitions:")
    for (parent_deficit, parent_residue, child_deficit, exponent), count in parent_counter.most_common(args.limit):
        print(
            f"  count={count} parent_deficit={parent_deficit} residue={parent_residue} "
            f"base3={to_base3(parent_residue, m)} exponent={exponent} "
            f"child_deficit={child_deficit}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
