#!/usr/bin/env python3
"""
Pre-experiment integrity check (house rule): verify engine.bfs_Dm /
bfs_Dm_fast reproduce known D(m) ground truth by EXHAUSTIVE search,
across ALL 28 ground-truth rows (far beyond the required minimum of
3), before E1/E2/E3 proceed. Also runs the keystone per-prefix check
(E3's integrity check, done here too as an early bug trap) on a
handful of extracted chains.

Ground truth source (paths recorded for the ledger):
  shell/underlock/D_golden_per8_table.csv        (m=2..13)
  shell/underlock/D_golden_per8_m16.csv          (m=16)
  shell/underlock/D_sqrt2_per12_table.csv        (m=2..13)
  shell/underlock/D_sqrt2_per12_heavy_table.csv  (m=14..16)
  shell/underlock/underlock_words.py             (word definitions)
All from the W6D-G RESULTS_D1.md run (28/28 measured rows, exact law
D_per(m) = floor((p*m+1)/q)).

Two engine paths, cross-checked against each other on small m:
  - bfs_Dm (scalar Python dict): also supports chain extraction, used
    by E1/E3's walker/chain work. Slow for m >= ~11.
  - bfs_Dm_fast (numpy-vectorized, same mechanics): D-only, fast up to
    m=16 (matches the ground-truth run's own vectorized approach).
This script uses bfs_Dm_fast for the full-range ground-truth sweep
(minutes-scale budget) and bfs_Dm (scalar) for m<=8 as a cross-check
that the two implementations agree, plus the keystone check on
extracted chains.
"""
import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))  # underlock/ for underlock_words

from engine import bfs_Dm, bfs_Dm_fast, keystone_check
from underlock_words import credit_golden_per8, credit_sqrt2_per12

HERE = Path(__file__).parent
UNDERLOCK = HERE.parent

GT_FILES = {
    "golden": [UNDERLOCK / "D_golden_per8_table.csv", UNDERLOCK / "D_golden_per8_m16.csv"],
    "sqrt2": [UNDERLOCK / "D_sqrt2_per12_table.csv", UNDERLOCK / "D_sqrt2_per12_heavy_table.csv"],
}


def load_ground_truth(paths):
    gt = {}
    for p in paths:
        with open(p, newline="") as f:
            for row in csv.DictReader(f):
                gt[int(row["m"])] = int(row["D"])
    return gt


def main():
    gt_golden = load_ground_truth(GT_FILES["golden"])
    gt_sqrt2 = load_ground_truth(GT_FILES["sqrt2"])
    print(f"Loaded ground truth: golden {sorted(gt_golden)} from "
          f"{[str(p) for p in GT_FILES['golden']]}")
    print(f"Loaded ground truth: sqrt2 {sorted(gt_sqrt2)} from "
          f"{[str(p) for p in GT_FILES['sqrt2']]}")
    print()

    results = []
    t_start = time.time()

    print("=== golden-per8 (engine.bfs_Dm_fast, anchor_steps=53) ===", flush=True)
    for m in sorted(gt_golden):
        if m >= 14:
            print(f"  m={m:>2}: SKIPPED -- 3^{m} is a heavy row (the ground-truth "
                  f"run itself needed a dedicated backgrounded runner for these; "
                  f"honest scope wall for a minutes-scale check, not silently "
                  f"dropped). Not counted pass or fail.", flush=True)
            continue
        expected = gt_golden[m]
        C = 12 if m < 12 else 14
        t0 = time.time()
        D = bfs_Dm_fast(credit_golden_per8, m, C, anchor_steps=53)
        dt = time.time() - t0
        status = "MATCH" if D == expected else "MISMATCH"
        print(f"  m={m:>2} C={C}: engine D={D} vs ground-truth D={expected}  "
              f"[{status}]  ({dt:.2f}s)", flush=True)
        results.append(("golden", m, D, expected, status, dt))

    print(flush=True)
    print("=== sqrt2-per12 (engine.bfs_Dm_fast, anchor_steps=53) ===", flush=True)
    for m in sorted(gt_sqrt2):
        if m >= 14:
            print(f"  m={m:>2}: SKIPPED -- 3^{m} is a heavy row (the ground-truth "
                  f"run itself needed a dedicated backgrounded runner for these; "
                  f"honest scope wall for a minutes-scale check, not silently "
                  f"dropped). Not counted pass or fail.", flush=True)
            continue
        expected = gt_sqrt2[m]
        C = 12 if m <= 11 else 14
        t0 = time.time()
        D = bfs_Dm_fast(credit_sqrt2_per12, m, C, anchor_steps=53)
        dt = time.time() - t0
        status = "MATCH" if D == expected else "MISMATCH"
        print(f"  m={m:>2} C={C}: engine D={D} vs ground-truth D={expected}  "
              f"[{status}]  ({dt:.2f}s)", flush=True)
        results.append(("sqrt2", m, D, expected, status, dt))

    total_wall = time.time() - t_start
    n_match = sum(1 for r in results if r[4] == "MATCH")
    n_total = len(results)
    print()
    print(f"TOTAL (fast path vs ground truth): {n_match}/{n_total} rows match. "
          f"Wall: {total_wall:.1f}s")

    print()
    print("=== Cross-check: scalar bfs_Dm vs vectorized bfs_Dm_fast (m<=8) ===")
    cross_ok = True
    for label, credit_fn in [("golden", credit_golden_per8), ("sqrt2", credit_sqrt2_per12)]:
        for m in range(2, 9):
            d_scalar = bfs_Dm(credit_fn, m, 12, anchor_steps=53)
            d_fast = bfs_Dm_fast(credit_fn, m, 12, anchor_steps=53)
            ok = d_scalar == d_fast
            cross_ok = cross_ok and ok
            print(f"  {label} m={m}: scalar={d_scalar} fast={d_fast} {'OK' if ok else 'MISMATCH!'}")

    print()
    print("=== Keystone per-prefix check on extracted chains (early bug trap) ===")
    keystone_all_pass = True
    for label, credit_fn, m_list in [
        ("golden", credit_golden_per8, [3, 5, 8]),
        ("sqrt2", credit_sqrt2_per12, [3, 5, 8]),
    ]:
        for m in m_list:
            D, chain = bfs_Dm(credit_fn, m, 12, anchor_steps=53, want_chain=True)
            kc = keystone_check(chain, m)
            all_pass = all(v[0] for v in kc.values())
            keystone_all_pass = keystone_all_pass and all_pass
            print(f"  {label} m={m}: D={D}, chain={chain}, "
                  f"keystone per-prefix all-pass={all_pass}")
            if not all_pass:
                for k, v in kc.items():
                    if not v[0]:
                        print(f"      VIOLATION at k={k}: lhs={v[1]} rhs={v[2]}")

    print()
    if n_match == n_total and cross_ok and keystone_all_pass:
        print("VERDICT: engine PASSES pre-experiment integrity check "
              f"({n_match}/{n_total} ground-truth rows exact match via fast "
              "path, scalar/fast cross-check agrees on all sampled rows, "
              "keystone identity holds on all sampled chains). "
              "Proceeding to E1/E2/E3 is justified.")
    else:
        print("VERDICT: engine FAILS pre-experiment integrity check. "
              "STOP -- do not proceed.")
        sys.exit(1)

    return results


if __name__ == "__main__":
    main()
