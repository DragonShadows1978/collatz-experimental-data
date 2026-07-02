#!/usr/bin/env python3
"""Attach Lock 3 shadow births to concrete integer witnesses when possible."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


ALPHA = 1.5849625007211563


@dataclass(frozen=True)
class Key:
    deficit: int
    residue: int


@dataclass
class Witness:
    exponents: tuple[int, ...]
    a_sum: int
    b: int
    pow3: int


def credit_at_step(k: int) -> int:
    return int((k + 1) * ALPHA) - int(k * ALPHA)


def residue_modulus(depth: int, residue_mod_power: int) -> int:
    return 3 ** min(depth, residue_mod_power)


def next_terminal_residue(residue: int, exponent: int, modulus: int) -> int:
    if modulus == 1:
        return 0
    return ((3 * residue + 1) * pow(pow(2, exponent, modulus), -1, modulus)) % modulus


def update_witness(witness: Witness, exponent: int) -> Witness:
    return Witness(
        exponents=(*witness.exponents, exponent),
        a_sum=witness.a_sum + exponent,
        b=3 * witness.b + (1 << witness.a_sum),
        pow3=3 * witness.pow3,
    )


def rho_for_witness(witness: Witness) -> tuple[int, int]:
    """Return smallest positive rho and its modulus 2^(A+1)."""
    modulus = 1 << (witness.a_sum + 1)
    target = ((1 << witness.a_sum) - witness.b) % modulus
    rho = (target * pow(witness.pow3 % modulus, -1, modulus)) % modulus
    if rho == 0:
        rho = modulus
    return rho, modulus


def crt_pair(a: int, m: int, b: int, n: int) -> tuple[int, int]:
    """Solve x=a mod m, x=b mod n for coprime m,n."""
    inv_m = pow(m, -1, n)
    t = ((b - a) % n) * inv_m % n
    modulus = m * n
    x = (a + m * t) % modulus
    if x == 0:
        x = modulus
    return x, modulus


def v2(value: int) -> int:
    if value <= 0:
        raise ValueError("v2 expects positive integer")
    return (value & -value).bit_length() - 1


def forward_verify(candidate: int, exponents: tuple[int, ...], residue: int, modulus3: int) -> tuple[bool, str, int]:
    x = candidate
    for idx, exponent in enumerate(exponents, start=1):
        lifted = 3 * x + 1
        actual = v2(lifted)
        if actual != exponent:
            return False, f"valuation_mismatch_at_step_{idx}:expected_{exponent}:actual_{actual}", x
        x = lifted >> exponent
    if x % modulus3 != residue:
        return False, f"terminal_residue_mismatch:expected_{residue}:actual_{x % modulus3}", x
    return True, "integral_witness_verified", x


def reconstruct_witnesses(c: int, residue_mod_power: int, depth: int) -> list[dict[Key, Witness]]:
    by_depth: list[dict[Key, Witness]] = [{Key(0, 0): Witness((), 0, 0, 1)}]
    current = by_depth[0]
    for next_depth in range(1, depth + 1):
        step_credit = credit_at_step(next_depth - 1)
        modulus = residue_modulus(next_depth, residue_mod_power)
        next_map: dict[Key, Witness] = {}
        for key, witness in current.items():
            for d_next in range(0, c + 1):
                exponent = key.deficit + step_credit - d_next
                if exponent < 1:
                    continue
                next_key = Key(d_next, next_terminal_residue(key.residue, exponent, modulus))
                if next_key not in next_map:
                    next_map[next_key] = update_witness(witness, exponent)
        by_depth.append(next_map)
        current = next_map
    return by_depth


def key_from_row(row: dict[str, str]) -> Key:
    return Key(int(row["deficit_state"]), int(row["residue_signature"]))


def parent_key_from_row(row: dict[str, str]) -> Key | None:
    if not row.get("parent_deficit_state") or not row.get("parent_residue_signature"):
        return None
    return Key(int(row["parent_deficit_state"]), int(row["parent_residue_signature"]))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promote Lock 3 shadow births to concrete integer witnesses when integrality verifies."
    )
    parser.add_argument("birth_audit_csv", type=Path)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--out-csv", type=Path)
    args = parser.parse_args()

    with args.birth_audit_csv.open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        print("no birth rows")
        return 0

    c = int(rows[0]["C"])
    m = int(rows[0]["m"])
    max_depth = max(int(row["depth"]) for row in rows[: args.limit])
    witnesses_by_depth = reconstruct_witnesses(c, m, max_depth)

    output_rows = []
    for row in rows[: args.limit]:
        depth = int(row["depth"])
        child_key = key_from_row(row)
        parent_key = parent_key_from_row(row)
        modulus3 = 3**m
        child_witness = witnesses_by_depth[depth].get(child_key)
        parent_witness = witnesses_by_depth[depth - 1].get(parent_key) if parent_key else None
        status = "residue_shadow_only"
        reason = "missing_representative_lineage"
        candidate = None
        terminal_value = None
        rho = None
        rho_modulus = None
        combined_modulus = None
        bit_length = None

        if child_witness is not None:
            rho, rho_modulus = rho_for_witness(child_witness)
            candidate, combined_modulus = crt_pair(rho, rho_modulus, child_key.residue, modulus3)
            ok, reason, terminal_value = forward_verify(
                candidate, child_witness.exponents, child_key.residue, modulus3
            )
            status = "integral_birth" if ok else "residue_shadow_only"
            bit_length = candidate.bit_length()

        output_rows.append(
            {
                "C": c,
                "m": m,
                "depth": depth,
                "status": status,
                "reason": reason,
                "child_deficit": child_key.deficit,
                "child_residue": child_key.residue,
                "parent_deficit": "" if parent_key is None else parent_key.deficit,
                "parent_residue": "" if parent_key is None else parent_key.residue,
                "rho": "" if rho is None else rho,
                "rho_modulus": "" if rho_modulus is None else rho_modulus,
                "candidate_integer": "" if candidate is None else candidate,
                "candidate_bit_length": "" if bit_length is None else bit_length,
                "combined_modulus": "" if combined_modulus is None else combined_modulus,
                "terminal_value_after_prefix": "" if terminal_value is None else terminal_value,
                "exponent_word": "" if child_witness is None else " ".join(map(str, child_witness.exponents)),
                "parent_exponent_word": "" if parent_witness is None else " ".join(map(str, parent_witness.exponents)),
            }
        )

    fieldnames = list(output_rows[0].keys())
    if args.out_csv:
        args.out_csv.parent.mkdir(parents=True, exist_ok=True)
        with args.out_csv.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)
        print(f"wrote {args.out_csv}")

    integral = sum(1 for row in output_rows if row["status"] == "integral_birth")
    print(f"source={args.birth_audit_csv}")
    print(f"C={c} m={m} checked={len(output_rows)} integral_births={integral} residue_shadows={len(output_rows)-integral}")
    for row in output_rows[: min(args.limit, 10)]:
        candidate_text = str(row["candidate_integer"])
        if len(candidate_text) > 80:
            candidate_text = candidate_text[:77] + "..."
        print(
            f"depth={row['depth']} status={row['status']} child=({row['child_deficit']},{row['child_residue']}) "
            f"parent=({row['parent_deficit']},{row['parent_residue']}) bits={row['candidate_bit_length']} "
            f"candidate={candidate_text} reason={row['reason']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
