#!/usr/bin/env python3
"""
W6F-F0 -- systematize the W6E spot-check, per W6F_OPTIMAL_SET_ORDER.md
section F0.

For every row m<=9 (golden-per8, sqrt2-per12): run the validated
engine.bfs_Dm(..., want_chain=True) (REUSED unmodified from w6e/), dump
the single chain it returns, and record whether that chain is the
trivial all-2s loop (a_j == 2 for every step). Deliverable: one table
closing the E3-correction loop with data across all in-scope rows
instead of the two samples in SYNTHESIS's W6E spot-check.

C values match e3_prefix_tightness.py's choice (12 for all m<=9, both
families -- verified sufficient by W6E, no widening needed at this
scope).
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import bfs_Dm
from underlock_words import credit_golden_per8, credit_sqrt2_per12

HERE = Path(__file__).parent
UNDERLOCK = HERE.parent

C_DEFAULT = 12


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
    rows_out = []
    for fam, credit_fn, gt in [("golden", credit_golden_per8, GT_GOLDEN),
                                ("sqrt2", credit_sqrt2_per12, GT_SQRT2)]:
        print(f"\n=== {fam}-per{'8' if fam=='golden' else '12'} (m<=9) ===")
        for m in sorted(k for k in gt if k <= 9):
            D_expected = gt[m]
            D, chain = bfs_Dm(credit_fn, m, C_DEFAULT, anchor_steps=53,
                               want_chain=True)
            assert D == D_expected, (
                f"{fam} m={m}: engine D={D} != ground-truth {D_expected} "
                f"at C={C_DEFAULT} -- integrity failure, stop")
            a_list = [a for (c, a) in chain]
            is_all2 = all(a == 2 for a in a_list)
            print(f"  m={m}: D={D}  a-sequence={a_list}  all_2s={is_all2}")
            rows_out.append({
                "family": fam, "m": m, "D": D,
                "a_sequence": " ".join(str(a) for a in a_list),
                "is_all_2s": is_all2,
            })

    n_all2 = sum(1 for r in rows_out if r["is_all_2s"])
    n_total = len(rows_out)
    print(f"\n=== SUMMARY ===")
    print(f"{n_all2}/{n_total} rows: bfs_Dm's returned chain IS the "
          f"all-2s loop chain.")
    if n_all2 == n_total:
        print("CONFIRMS the W6E spot-check (2/2 samples) at full scope "
              "(all m<=9, both families): bfs_Dm's single returned chain "
              "is always the trivial loop. This says NOTHING yet about "
              "the SIZE of the full optimal set (that is F1) -- it only "
              "confirms which chain the first-parent-wins BFS happens "
              "to return.")
    else:
        non2 = [r for r in rows_out if not r["is_all_2s"]]
        print(f"CONTRADICTS the W6E spot-check: {len(non2)} row(s) returned "
              f"a non-all-2s chain from bfs_Dm: {non2}")

    with open(HERE / "f0_spotcheck.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["family", "m", "D", "a_sequence", "is_all_2s"])
        w.writeheader()
        for r in rows_out:
            w.writerow(r)
    print(f"\nWrote f0_spotcheck.csv ({n_total} rows)")


if __name__ == "__main__":
    main()
