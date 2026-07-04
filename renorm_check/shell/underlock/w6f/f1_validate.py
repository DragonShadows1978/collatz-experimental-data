#!/usr/bin/env python3
"""
W6F-F1 pre-experiment validation (house rule: validate any engine
extension against >=3 ground-truth rows before trusting it).

Cross-checks f1_engine_ext.compute_D_and_optimal_set (forward boolean-
array pass + memoized backward enumeration) against
f1_engine_ext.brute_force_all_chains (fully independent naive scalar
recursive DFS over every starting residue) on BOTH families, m=3,4,5
(6 rows, 2x the minimum family coverage and 2x the row minimum).
Checks BOTH D (matches ground truth) and the SET of distinct optimal
a-sequences (exact match, not just cardinality).
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from f1_engine_ext import compute_D_and_optimal_set, brute_force_all_chains
from underlock_words import credit_golden_per8, credit_sqrt2_per12

HERE = Path(__file__).parent
UNDERLOCK = HERE.parent


def load_ground_truth(paths):
    gt = {}
    for p in paths:
        with open(p, newline="") as f:
            for row in csv.DictReader(f):
                gt[int(row["m"])] = int(row["D"])
    return gt


GT_GOLDEN = load_ground_truth(
    [UNDERLOCK / "D_golden_per8_table.csv", UNDERLOCK / "D_golden_per8_m16.csv"])
GT_SQRT2 = load_ground_truth(
    [UNDERLOCK / "D_sqrt2_per12_table.csv", UNDERLOCK / "D_sqrt2_per12_heavy_table.csv"])


def main():
    C = 12
    all_ok = True
    for fam, credit_fn, gt in [("golden", credit_golden_per8, GT_GOLDEN),
                                ("sqrt2", credit_sqrt2_per12, GT_SQRT2)]:
        for m in [3, 4, 5]:
            D_expected = gt[m]
            D_fast, best_d, seqs_fast = compute_D_and_optimal_set(credit_fn, m, C)
            D_brute, seqs_brute = brute_force_all_chains(credit_fn, m, C)

            ok_gt = (D_fast == D_expected)
            ok_cross_D = (D_fast == D_brute)
            ok_cross_seqs = (seqs_fast == seqs_brute)
            row_ok = ok_gt and ok_cross_D and ok_cross_seqs
            all_ok = all_ok and row_ok
            print(f"{fam} m={m}: D_fast={D_fast} D_ground_truth={D_expected} "
                  f"D_brute={D_brute} | matches_ground_truth={ok_gt} "
                  f"matches_brute_D={ok_cross_D} matches_brute_seqs={ok_cross_seqs} "
                  f"n_seqs={len(seqs_fast)} | {'PASS' if row_ok else 'FAIL'}")
            if not row_ok:
                print(f"    fast seqs: {sorted(seqs_fast)}")
                print(f"    brute seqs: {sorted(seqs_brute)}")

    print()
    if all_ok:
        print("VERDICT: engine extension PASSES validation on 6/6 rows "
              "(both families, m=3,4,5; exceeds the 3-row minimum). "
              "D matches ground truth AND the exact set of optimal "
              "a-sequences matches an independent brute-force "
              "implementation on every row. Proceeding to F1 full census "
              "is justified.")
    else:
        print("VERDICT: engine extension FAILS validation. STOP -- do "
              "not proceed to F1.")
        sys.exit(1)


if __name__ == "__main__":
    main()
