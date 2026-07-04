#!/usr/bin/env python3
"""
LOCK4-B1.3 prep -- D(m) vs L(m) on the true word, extending the
W6P-URGENT/W6Q-REALITY finding (D<L strictly from m=29 on the true
word's end-anchored game) toward the m=359 scale, to check whether
DERIVATION_NOTES sec 8c's "REQUIRED_SUPPORT = L(359) = 149" is safe to
use as-is or needs an honest caveat.

Uses w6k/k0_canonical_engine.canonical_D (house-gated instrument,
D_ceil variant, ceiling_on=True -- the strict canonical constraint),
NOT reimplemented. Independent of B1.2's own DFS (different objective:
canonical_D MINIMIZES max(a-c); B1.2 MAXIMIZES sum(c-a) -- genuinely
different games, this script does not assume B1.2's results carry
over).

FINDING (load-bearing for B1.3): D(m) is NOT computable at m=358/359
in this session -- canonical_D's own branch-and-bound wall-clock grows
so fast (m=100: 5s; m=110: 9s; m=120: 18s; m=125: 23s; m=130: 30s --
roughly a 1.3x factor per 5 steps) that extrapolating to m=358 would
require astronomically more time. D IS pinned at 11 from m=29 through
m=53 (W6P-URGENT), then grows to 20 by m=130 -- a MUCH slower rate
(~0.12/step average over m=53..130) than L's rate (~0.17/step, the
B1.1 phase-relaxed slope 2*alpha-3). Since D(m) <= L(m) ALWAYS (the
all-2 loop is always one valid candidate for canonical_D's
minimization, so D can never exceed the loop's own value L; strict
inequality is what W6P/W6Q found from m=29 on), L(359)=149 is
mathematically an UPPER BOUND on the true D(359), not a proven exact
value -- and the m=29-130 trend suggests (does NOT prove) the true
D(359) could be materially LOWER. This makes the bridge's
REQUIRED_SUPPORT potentially an OVERESTIMATE, which would make Lock 4's
obstruction argument HARDER to sustain, not easier -- reported
honestly as an open gap, not resolved here.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
W6K = HERE.parent.parent / "underlock" / "w6k"
sys.path.insert(0, str(W6K))
from k0_canonical_engine import canonical_D  # noqa: E402


def floor_k_alpha(k: int) -> int:
    if k == 0:
        return 0
    return (3 ** k).bit_length() - 1


def credit_true(k: int) -> int:
    return floor_k_alpha(k + 1) - floor_k_alpha(k)


def backward_letters(k_end: int, m: int):
    return [credit_true(k_end - 1 - j) for j in range(m)]


def loop_L(letters):
    total = 0
    best = 0
    for c in letters:
        total += (2 - c)
        best = max(best, total)
    return best


def main():
    print("=== LOCK4-B1.3 prep: D(m) vs L(m) trend check (true word, end-anchored game) ===\n")
    rows = []
    time_budget_total = 240
    t_start = time.time()
    test_ms = [53, 60, 70, 80, 90, 100, 110, 115, 120, 125, 130]
    for m in test_ms:
        if time.time() - t_start > time_budget_total:
            print(f"  [time budget exhausted, stopping at m={m}]")
            break
        letters = backward_letters(m, m)
        t0 = time.time()
        D = canonical_D(letters, ceiling_on=True, a_cap=40)
        L = loop_L(letters)
        wall = time.time() - t0
        print(f"  m={m:>4}: D_ceil={D:>3} L={L:>3} D<L={'yes' if D < L else 'no'} time={wall:.2f}s")
        rows.append({"m": m, "D_ceil": D, "L": L, "D_lt_L": D < L, "wall_s": round(wall, 2)})

    out = HERE / "b3_D_vs_L_trend.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["m", "D_ceil", "L", "D_lt_L", "wall_s"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nWrote {out.name} ({len(rows)} rows)")

    if len(rows) >= 2:
        m0, m1 = rows[0]["m"], rows[-1]["m"]
        d0, d1 = rows[0]["D_ceil"], rows[-1]["D_ceil"]
        l0, l1 = rows[0]["L"], rows[-1]["L"]
        d_rate = (d1 - d0) / (m1 - m0)
        l_rate = (l1 - l0) / (m1 - m0)
        print(f"\nD rate over m={m0}..{m1}: {d_rate:.4f}/step  (L rate over same range: {l_rate:.4f}/step)")
        import math
        print(f"L's asymptotic rate (B1.1): {2*math.log2(3)-3:.6f}/step")
        print("\nHONEST CONCLUSION: D(m=358 or 359) is NOT computed here (wall-clock infeasible "
              "at this scale with the exhaustive branch-and-bound instrument -- extrapolated "
              "cost from the measured growth is astronomically beyond this session's budget). "
              "D(m) <= L(m) ALWAYS (loop is always a valid candidate for the minimization); the "
              "measured D-growth rate here is slower than L's, so L(359)=149 (DERIVATION_NOTES "
              "sec 8c) should be read as a MATHEMATICALLY VALID UPPER BOUND on the true "
              "REQUIRED_SUPPORT, not a confirmed exact value -- the true value could be lower, "
              "which would make Lock 4's bridge obstruction HARDER to sustain, not easier. This "
              "is registered as an open gap for B1.3, not resolved.")


if __name__ == "__main__":
    main()
