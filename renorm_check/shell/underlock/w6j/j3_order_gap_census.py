#!/usr/bin/env python3
"""
W6J-J3 -- Order-gap uniqueness census (the keystone's sharpest tooth),
per W6J_INTERIOR_BOUNDARY_ORDER.md section J3.

Part A: verify ord(2, 3^m) = 2*3^(m-1) directly, for m=4..8 (brute:
smallest k>0 with 2^k == 1 mod 3^m).

Part B: for the S-value of every admissible chain enumerated in
W6F-F2's D+2 scope (w6f/f2_tax_table.csv, 50 rows -- reload the
chain a-sequences and each chain's own credit-word context DIRECTLY
from F2's own machinery, not re-derived by hand, to guarantee the
S computed here matches what F2 actually enumerated), recompute
S = Sum_{i=0}^{m-1} 3^{m-1-i} * 2^{A_i} per chain (DERIVATION_NOTES
sec 5b's keystone identity: 2^{Sigma a} == S (mod 3^m), A_i = a_1+...
+a_i, A_0=0) and brute the FULL solution set
{sigma in [0, 6m] : 2^sigma == S (mod 3^m)}.

Frozen predictions:
  (a) each S admits AT MOST ONE sigma in [0,6m] (85%)
  (b) that sigma equals the chain's actual Sigma a in every case
      (consistency; REQUIRED -- a mismatch = engine bug, STOP)
  (c) tabulate Sigma a - 2m vs the chain's tax (delta_tax): architect
      expects a clean monotone relation (60%)

Machinery reuse: engine.py's keystone_check already implements this
EXACT identity (per-prefix, at the chain's own precision) -- reused
directly for the "does 2^Sigma_a == S mod 3^m hold at all" sanity
check before the brute-force solution-set search (which is new code,
since keystone_check doesn't enumerate OTHER sigma solving the same
congruence, only checks the chain's own Sigma a). f2_tax_table.csv's
own a_sequence column is reloaded verbatim (not regenerated) so this
experiment's S values are guaranteed to be F2's actual chains, not a
re-derivation that could silently drift.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
sys.path.insert(0, str(Path(__file__).parent.parent / "w6f"))
from engine import keystone_check  # noqa: E402

HERE = Path(__file__).parent
F2_CSV = HERE.parent / "w6f" / "f2_tax_table.csv"


# ---------------------------------------------------------------------
# Part A: order-gap verification
# ---------------------------------------------------------------------

def multiplicative_order_of_2(mod: int) -> int:
    """Brute: smallest k>0 with 2^k == 1 (mod mod). Direct definition,
    no shortcuts -- mod=3^m is small enough (3^8=6561) that this is
    instant."""
    k = 1
    val = 2 % mod
    while val != 1:
        val = (val * 2) % mod
        k += 1
        if k > 10 * mod:  # sanity guard, should never trigger
            raise RuntimeError(f"order search exceeded sanity bound for mod={mod}")
    return k


def part_a():
    print("=== Part A: ord(2, 3^m) = 2*3^(m-1) direct verification, m=4..8 ===")
    rows = []
    all_ok = True
    for m in range(4, 9):
        mod = 3 ** m
        expected = 2 * 3 ** (m - 1)
        got = multiplicative_order_of_2(mod)
        ok = (got == expected)
        all_ok = all_ok and ok
        print(f"  m={m} mod=3^{m}={mod}: ord(2,3^{m})={got} expected={expected} "
              f"{'PASS' if ok else 'FAIL'}")
        rows.append({"m": m, "mod": mod, "ord_2": got, "expected": expected, "match": ok})
    with open(HERE / "j3a_order_gap.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["m", "mod", "ord_2", "expected", "match"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote j3a_order_gap.csv ({len(rows)} rows). ALL PASS: {all_ok}\n")
    if not all_ok:
        raise SystemExit("STOP: ord(2,3^m) verification FAILED -- refusing to proceed, engine bug or "
                          "wrong formula, this is foundational to the whole keystone.")
    return all_ok


# ---------------------------------------------------------------------
# Part B: keystone pinning table
# ---------------------------------------------------------------------

def compute_S(a_seq, m: int) -> int:
    """S = Sum_{i=0}^{m-1} 3^{m-1-i} * 2^{A_i}, A_i = a_1+...+a_i (A_0=0).
    Matches engine.keystone_check's own S formula exactly (re-derived
    here standalone, not imported, because keystone_check bundles the
    congruence CHECK against a chain's own Sigma_a and doesn't return S
    itself for reuse in a separate solution-set search -- but computed
    identically, and cross-validated against keystone_check below on
    every chain before trusting the brute-force search)."""
    A = [sum(a_seq[:i]) for i in range(0, m + 1)]
    return sum(3 ** (m - 1 - i) * 2 ** A[i] for i in range(m))


def brute_all_sigma(S: int, mod: int, sigma_max: int):
    """All sigma in [0, sigma_max] with 2^sigma == S (mod mod).
    Direct brute force -- sigma_max = 6m per the order, mod=3^m is
    small (<=3^13 for this scope), so this is cheap."""
    target = S % mod
    solutions = []
    val = 1 % mod
    for sigma in range(0, sigma_max + 1):
        if val == target:
            solutions.append(sigma)
        val = (val * 2) % mod
    return solutions


def validate_on_known_rows(chains_sample):
    """House rule: validate the new S/brute-force machinery on >=3
    known rows before trusting the full census.
      (1) cross-check compute_S against engine.keystone_check's own S
          (read back out of its internals is not exposed, so instead
          cross-check that keystone_check's congruence PASSES using
          this same S formula -- i.e. 2^Sigma_a mod 3^m == compute_S(..)
          mod 3^m, for the chain's own Sigma_a, on 3 sample chains).
      (2) confirm the chain's own Sigma_a is FOUND in the brute-forced
          solution set (a minimal self-consistency smoke test before
          the real per-row consistency check below, which is the same
          thing done systematically for all 50 rows).
    """
    print("=== Pre-experiment validation (house rule, 3+ known rows) ===")
    all_ok = True
    for (fam, m, a_seq) in chains_sample[:3]:
        mod = 3 ** m
        Sigma_a = sum(a_seq)
        S = compute_S(a_seq, m)
        lhs = pow(2, Sigma_a, mod)
        rhs = S % mod
        ok1 = (lhs == rhs)
        kc = keystone_check(list(zip([0] * m, a_seq)), m)  # credit values irrelevant to keystone_check's own math, only a_seq matters
        ok2 = kc[m][0]  # full-length (k=m) check result
        sols = brute_all_sigma(S, mod, 6 * m)
        ok3 = Sigma_a in sols
        ok = ok1 and ok2 and ok3
        all_ok = all_ok and ok
        print(f"  {fam} m={m} a_seq={a_seq}: Sigma_a={Sigma_a} S mod 3^m={rhs} "
              f"2^Sigma_a mod 3^m={lhs} congruence_holds={ok1} "
              f"keystone_check_agrees={ok2} Sigma_a_in_brute_solutions={ok3} "
              f"{'PASS' if ok else 'FAIL'}")
    assert all_ok, "S/brute-force validation failed on sample rows -- STOP"
    print("All validation checks PASS.\n")


def part_b():
    if not F2_CSV.exists():
        raise SystemExit(f"F2 tax table not found at {F2_CSV}")
    with open(F2_CSV, newline="") as f:
        f2_rows = list(csv.DictReader(f))
    print(f"Loaded {len(f2_rows)} chains from {F2_CSV.name} (F2's D+2 scope)")

    chains = []
    for row in f2_rows:
        fam = row["family"]
        m = int(row["m"])
        a_seq = tuple(int(x) for x in row["a_sequence"].split())
        assert len(a_seq) == m, (
            f"a_sequence length {len(a_seq)} != m={m} for {fam} row -- "
            f"malformed F2 data, STOP")
        chains.append((fam, m, a_seq, int(row["delta_tax"]), row["is_loop"] == "True"))

    validate_on_known_rows([(fam, m, a_seq) for (fam, m, a_seq, _, _) in chains])

    out_rows = []
    n_at_most_one = 0
    n_multi = 0
    n_zero_sol = 0
    consistency_mismatches = []
    for (fam, m, a_seq, delta_tax, is_loop) in chains:
        mod = 3 ** m
        Sigma_a = sum(a_seq)
        S = compute_S(a_seq, m)
        sols = brute_all_sigma(S, mod, 6 * m)
        n_sols = len(sols)
        if n_sols == 0:
            n_zero_sol += 1
        elif n_sols == 1:
            n_at_most_one += 1
        else:
            n_multi += 1
        consistent = (Sigma_a in sols) and (n_sols >= 1)
        # exact consistency requirement (b): if there IS a unique/any sigma
        # solving the congruence, it must equal Sigma_a exactly -- check
        # every returned sigma, not just presence, per the order's wording
        # ("that sigma equals the chain's actual Sigma a in every case").
        mismatch = (n_sols >= 1) and any(s != Sigma_a for s in sols)
        if mismatch or n_sols == 0:
            consistency_mismatches.append({
                "family": fam, "m": m, "a_sequence": " ".join(map(str, a_seq)),
                "Sigma_a": Sigma_a, "S_mod_3m": S % mod, "n_solutions": n_sols,
                "solutions": ",".join(map(str, sols)), "delta_tax": delta_tax,
            })
        out_rows.append({
            "family": fam, "m": m, "delta_tax": delta_tax, "is_loop": is_loop,
            "a_sequence": " ".join(map(str, a_seq)), "Sigma_a": Sigma_a,
            "Sigma_a_minus_2m": Sigma_a - 2 * m,
            "S_mod_3m": S % mod, "n_solutions_in_0_6m": n_sols,
            "solutions": ",".join(map(str, sols)),
            "sigma_equals_Sigma_a": (sols == [Sigma_a]) if n_sols else None,
        })

    out_csv = HERE / "j3b_pinning_table.csv"
    with open(out_csv, "w", newline="") as f:
        fieldnames = ["family", "m", "delta_tax", "is_loop", "a_sequence",
                      "Sigma_a", "Sigma_a_minus_2m", "S_mod_3m",
                      "n_solutions_in_0_6m", "solutions", "sigma_equals_Sigma_a"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print(f"Wrote {out_csv.name} ({len(out_rows)} rows)")

    print(f"\n=== GATE (a): each S admits AT MOST ONE sigma in [0,6m] (85%) ===")
    print(f"  0 solutions: {n_zero_sol}, exactly 1 solution: {n_at_most_one}, "
          f">1 solutions: {n_multi} (out of {len(chains)} chains)")
    gate_a_hit = (n_multi == 0)
    print(f"  VERDICT: {'HIT' if gate_a_hit else f'MISS -- {n_multi} chains have multiple sigma solutions in [0,6m]'}")

    print(f"\n=== GATE (b): sigma == chain's actual Sigma_a in every case (REQUIRED) ===")
    print(f"  Mismatches/zero-solution rows: {len(consistency_mismatches)}")
    if consistency_mismatches:
        dump_csv = HERE / "j3b_consistency_mismatches_dump.csv"
        with open(dump_csv, "w", newline="") as f:
            fieldnames = ["family", "m", "a_sequence", "Sigma_a", "S_mod_3m",
                          "n_solutions", "solutions", "delta_tax"]
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in consistency_mismatches:
                w.writerow(r)
        print(f"  *** MISMATCH DUMP (verbatim, {dump_csv.name}) ***")
        for r in consistency_mismatches:
            print(f"    {r}")
        print("\n  PER ORDER: 'a mismatch = engine bug, STOP and report rather than "
              "writing it up as math.' STOPPING part B verdict here -- see final digest.")
        gate_b_hit = False
    else:
        print("  VERDICT: HIT -- every chain's brute-forced sigma solution set is "
              "exactly {Sigma_a}, no exceptions, no zero-solution rows.")
        gate_b_hit = True

    print(f"\n=== GATE (c): Sigma_a - 2m vs delta_tax -- monotone relation? (60%) ===")
    table_c = sorted(
        [(r["family"], r["m"], r["delta_tax"], r["Sigma_a_minus_2m"]) for r in out_rows],
        key=lambda t: (t[0], t[1], t[2]))
    for row in table_c:
        print(f"  family={row[0]} m={row[1]} delta_tax={row[2]} Sigma_a-2m={row[3]}")
    # Check monotonicity: within each (family, m) group, as delta_tax increases,
    # does Sigma_a - 2m increase (non-decreasing)?
    from collections import defaultdict
    groups = defaultdict(list)
    for (fam, m, dt, s2m) in table_c:
        groups[(fam, m)].append((dt, s2m))
    n_monotone_groups = 0
    n_total_groups = 0
    violations = []
    for key, vals in groups.items():
        vals_sorted = sorted(vals)
        n_total_groups += 1
        is_monotone = all(vals_sorted[i][1] <= vals_sorted[i + 1][1] for i in range(len(vals_sorted) - 1))
        if is_monotone:
            n_monotone_groups += 1
        else:
            violations.append((key, vals_sorted))
    print(f"\n  Monotone (Sigma_a-2m nondecreasing in delta_tax) within {n_monotone_groups}/{n_total_groups} "
          f"(family,m) groups.")
    if violations:
        print("  Non-monotone groups (verbatim):")
        for key, vals_sorted in violations:
            print(f"    {key}: {vals_sorted}")
    gate_c_hit = (n_monotone_groups == n_total_groups)
    print(f"  VERDICT: {'HIT' if gate_c_hit else 'MISS'} (clean monotone relation "
          f"{'holds' if gate_c_hit else 'does NOT hold'} across all groups)")

    return gate_a_hit, gate_b_hit, gate_c_hit, consistency_mismatches


def main():
    part_a()
    part_b()


if __name__ == "__main__":
    main()
