#!/usr/bin/env python3
"""
W6L-L4b -- Exponent-cap margin check for the L4 composability sweep.

The D_free game has NO exponent cap; L4's DFS searched a ~80-wide
menu (A_CAP=40 -> a in {a_min, a_min+2, ..., a_min+78}). Two risks:
  (1) evaluable joint minima could DROP with a wider menu (steering
      via one huge exponent instead of several) -- deltas overstated;
  (2) "JOINT_INFEASIBLE" rows may really be "feasible only with
      a > ~80" -- with unbounded exponents, one free step from class
      r can reach 3^(K-1) distinct classes mod 3^K (4 generates the
      index-2 subgroup), so feasibility at big exponents is expected
      generically; the honest claim is then "joint tax exceeds X",
      not "infeasible".

Check 1: rerun EVERY evaluable (status OK) row's dA, dB, dAB at
a_cap=80 (menu width ~160); values must be identical to the a_cap=40
sweep. Any change -> the L4 numbers are cap-limited; widen and rerun.

Check 2: take gap<=1 rows (all JOINT_INFEASIBLE at a_cap=40) on a
representative subsample and search at a_cap=110 then 250; report
which become feasible and their joint taxes.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from l4_composability import constrained_D, windows, SHAPES  # noqa: E402


def main():
    wins = windows()
    rows = list(csv.DictReader(open(HERE / "l4_composability.csv")))

    # --- Check 1: evaluable rows at a_cap=80 ---
    print("=== Check 1: all evaluable rows re-run at a_cap=80 ===")
    t0 = time.time()
    n_same = n_diff = 0
    diffs = []
    for r in rows:
        if r["status"] != "OK":
            continue
        letters = wins[(r["family"], int(r["m"]))]
        sA, sB = SHAPES[r["shapeA"]], SHAPES[r["shapeB"]]
        pA, pB = int(r["pA"]), int(r["pB"])
        fA = {pA + i: a for i, a in enumerate(sA)}
        fB = {pB + i: a for i, a in enumerate(sB)}
        dA = constrained_D(letters, fA, a_cap=80)
        dB = constrained_D(letters, fB, a_cap=80)
        dAB = constrained_D(letters, {**fA, **fB}, a_cap=80)
        D0 = int(r["D0"])
        old = (int(r["taxA"]), int(r["taxB"]), int(r["tax_joint"]))
        new = (dA - D0 if dA is not None else None,
               dB - D0 if dB is not None else None,
               dAB - D0 if dAB is not None else None)
        if old == new:
            n_same += 1
        else:
            n_diff += 1
            diffs.append((r["family"], r["m"], r["shapeA"], pA, r["shapeB"], pB, old, new))
    print(f"  {n_same} identical, {n_diff} CHANGED at a_cap=80 ({time.time()-t0:.1f}s)")
    if diffs:
        print("  CHANGED rows (cap=40 sweep is cap-limited -- values below supersede):")
        for d in diffs[:20]:
            print(f"    {d}")

    # --- Check 2: gap<=1 subsample at bigger caps ---
    print("\n=== Check 2: gap<=1 (all 'infeasible' at cap 40) at a_cap=110 and 250 ===")
    sub = [r for r in rows if r["status"] == "JOINT_INFEASIBLE" and int(r["gap"]) <= 1
           and r["family"] == "golden-per8" and r["m"] == "16" and r["pA"] == "0"]
    print(f"  subsample: {len(sub)} rows (golden-per8 m=16, pA=0, gap<=1)")
    for r in sub:
        letters = wins[(r["family"], int(r["m"]))]
        sA, sB = SHAPES[r["shapeA"]], SHAPES[r["shapeB"]]
        pA, pB = int(r["pA"]), int(r["pB"])
        fAB = {pA + i: a for i, a in enumerate(sA)}
        fAB.update({pB + i: a for i, a in enumerate(sB)})
        results = {}
        for cap in (110, 250):
            t1 = time.time()
            d = constrained_D(letters, fAB, a_cap=cap)
            results[cap] = (d, time.time() - t1)
        D0 = int(r["D0"])
        msg = ", ".join(f"cap={c}: {'INFEASIBLE' if v is None else f'joint_tax={v - D0}'} ({dt:.1f}s)"
                        for c, (v, dt) in results.items())
        print(f"  {r['shapeA']}@{pA}+{r['shapeB']}@{pB} gap={r['gap']}: {msg}")

    print("\nInterpretation: if Check 1 shows zero changes, the L4 deltas stand at menu "
          "width ~160. Check 2 reclassifies 'infeasible' as either genuinely dead (parity "
          "trap at every exponent) or 'tax above the cap-40 search horizon' -- the honest "
          "wording for the ledger.")


if __name__ == "__main__":
    main()
