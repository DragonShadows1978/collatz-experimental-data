#!/usr/bin/env python3
"""
W6L-L4 -- Excursion-tax composability, per
W6L_CANONICAL_CONSOLIDATION_ORDER.md section L4 (registered ideation
idea #5, now on certified instruments).

INSTRUMENT: Path C semantics. D(w) and all constrained variants are
computed by the SAME exhaustive branch-and-bound DFS as
k0_canonical_engine.canonical_D (canonical backward-consumption
order, D_free/ceiling-off -- the certified universality object),
extended with FORCED exponent positions: at window step j in a
forced block, the exponent menu is exactly {shape value} (still
subject to parity legality -- a forced value that violates the
parity forced by the current exact residue kills the branch; if no
completion exists at all, the embedding is INFEASIBLE, reported as
data). Everything else identical to Path C.

GATES:
  G1: no-constraint variant == k0_canonical_engine.canonical_D on
      every window used (values must be identical).
  G2: fully-forced chains == direct arithmetic evaluation (max
      partial sum computed independently by replay), incl. the all-2s
      loop giving exactly L(w).
  G3: parity-impossible embedding detected as INFEASIBLE (forcing
      odd a at the terminal's class-1 first step).

DESIGN: shapes from the L2d/L2e EXACT catalog (every one
exact-replay-verified):
    s1 = (4,3,2,1,1)    excursion cost 1  (t=1 argmin)
    s2 = (4,3,2,1,3,1)  excursion cost 2  (t=2 argmin)
    s3 = (4,5,1,1,5,1)  excursion cost 5  (t=4 argmin)
Windows: golden-per8 / sqrt2-per12 / real word, m = 14,15,16
(canonical windows, anchor_steps=53, backward_letters convention).
Embeddings: ordered pairs (sA @ pA, sB @ pB), pA in {0,1}, gap =
pB - (pA + len(sA)) in {0..4} where the pair fits. THREE-shape
embeddings do not fit: min shape length is 5, so three shapes at
gap>=2 need >= 19 > 16 positions -- the order's "2-3 shapes" scope
is honestly reduced to pairs (stated, not hidden).

MEASUREMENT: tax(X) = D(w | X forced) - D(w).
    delta = tax(sA@pA AND sB@pB) - tax(sA@pA) - tax(sB@pB).
Frozen predictions: exact additivity (delta == 0) for gap >= 2 --
70%; interference (delta != 0) at gap <= 1 -- 55%.
"""
from __future__ import annotations

import csv
import sys
import time
import resource
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
W6K = HERE.parent / "w6k"
W6E = HERE.parent / "w6e"
UNDERLOCK = HERE.parent
sys.path.insert(0, str(W6K))
sys.path.insert(0, str(W6E))
sys.path.insert(0, str(UNDERLOCK))

from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
from k0_canonical_engine import canonical_D  # noqa: E402
from underlock_words import credit_golden_per8, credit_sqrt2_per12  # noqa: E402
from e1_walkers import backward_letters, credit_true  # noqa: E402

A_CAP = 40

SHAPES = {
    "s1": (4, 3, 2, 1, 1),        # exact t=1 argmin, excursion cost 1
    "s2": (4, 3, 2, 1, 3, 1),     # exact t=2 argmin, excursion cost 2
    "s3": (4, 5, 1, 1, 5, 1),     # exact t=4 argmin, excursion cost 5
}


def rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


def constrained_D(letters, forced: dict, a_cap: int = A_CAP):
    """Path-C DFS with forced exponents at given window steps.
    forced: {step_index: forced_a}. Returns min max-partial-sum or
    None (infeasible). Identical mechanics to canonical_D otherwise."""
    m = len(letters)
    best = [None]

    def dfs(j, rho, running, max_so_far):
        if best[0] is not None and max_so_far >= best[0]:
            return
        if j == m:
            if best[0] is None or max_so_far < best[0]:
                best[0] = max_so_far
            return
        c = letters[j]
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return
        a_min = 2 if parity == 0 else 1
        if j in forced:
            a = forced[j]
            if (a % 2 == 0) != (parity == 0) or a < 1:
                return  # forced value parity-illegal here -> dead branch
            menu = (a,)
        else:
            menu = range(a_min, a_min + a_cap, 2)
        for a in menu:
            running2 = running + (a - c)
            rho2 = backward_predecessor_exact(rho, a)
            max2 = max(max_so_far, running2)
            dfs(j + 1, rho2, running2, max2)

    dfs(0, 1, 0, 0)
    return best[0]


def direct_eval(letters, a_seq):
    """Independent full-chain evaluation: legality + max partial sum by
    plain replay (no DFS)."""
    v = 1
    running = 0
    mx = 0
    for c, a in zip(letters, a_seq):
        p = forced_parity_for_backward_step(v)
        if p is None or (a % 2 == 0) != (p == 0):
            return None
        v = backward_predecessor_exact(v, a)
        running += a - c
        mx = max(mx, running)
    return mx


def windows():
    out = {}
    for fam, fn in [("golden-per8", credit_golden_per8),
                    ("sqrt2-per12", credit_sqrt2_per12),
                    ("real-word", credit_true)]:
        for m in (14, 15, 16):
            out[(fam, m)] = backward_letters(fn, m, anchor_steps=53)
    return out


def gates(wins):
    print("--- G1: unconstrained == canonical_D (Path C) on all windows ---")
    for (fam, m), letters in sorted(wins.items()):
        d1 = constrained_D(letters, {})
        d2 = canonical_D(letters, False, a_cap=A_CAP)
        assert d1 == d2, f"G1 FAIL {fam} m={m}: {d1} != {d2}"
        print(f"  {fam} m={m}: D={d1} == canonical_D -- OK")
    print("--- G2: fully-forced == direct evaluation ---")
    letters = wins[("golden-per8", 14)]
    d_loop = constrained_D(letters, {j: 2 for j in range(14)})
    L = 0
    running = 0
    for c in letters:
        running += 2 - c
        L = max(L, running)
    de = direct_eval(letters, [2] * 14)
    assert d_loop == L == de, f"G2 FAIL loop: {d_loop} vs L={L} vs direct={de}"
    print(f"  all-2s loop on golden m=14: constrained={d_loop} == L(w)={L} == direct={de} -- OK")
    chain = [4, 3, 2, 1, 1] + [2] * 9  # s1 at 0 then a=2 padding (legality decided by replay)
    de2 = direct_eval(letters, chain)
    d2f = constrained_D(letters, dict(enumerate(chain)))
    assert de2 == d2f, f"G2 FAIL forced chain: direct={de2} vs constrained={d2f}"
    print(f"  s1+2s full chain: constrained={d2f} == direct={de2} -- OK")
    print("--- G3: parity-impossible embedding detected ---")
    bad = constrained_D(letters, {0: 1})  # terminal class 1 forces even first a
    assert bad is None, f"G3 FAIL: expected None, got {bad}"
    print("  forcing a=1 at step 0 (class-1 terminal): INFEASIBLE as required -- OK\n")


def main():
    t0 = time.time()
    wins = windows()
    gates(wins)

    rows = []
    print("--- Composability sweep ---")
    for (fam, m), letters in sorted(wins.items()):
        D0 = constrained_D(letters, {})
        for nA, sA in SHAPES.items():
            for nB, sB in SHAPES.items():
                for pA in (0, 1):
                    for gap in (0, 1, 2, 3, 4):
                        pB = pA + len(sA) + gap
                        if pB + len(sB) > m:
                            continue
                        fA = {pA + i: a for i, a in enumerate(sA)}
                        fB = {pB + i: a for i, a in enumerate(sB)}
                        dA = constrained_D(letters, fA)
                        dB = constrained_D(letters, fB)
                        dAB = constrained_D(letters, {**fA, **fB})
                        taxA = None if dA is None else dA - D0
                        taxB = None if dB is None else dB - D0
                        taxAB = None if dAB is None else dAB - D0
                        if None in (taxA, taxB):
                            status = "SINGLE_INFEASIBLE"
                            delta = None
                        elif taxAB is None:
                            status = "JOINT_INFEASIBLE"
                            delta = None
                        else:
                            delta = taxAB - taxA - taxB
                            status = "OK"
                        rows.append({
                            "family": fam, "m": m, "D0": D0,
                            "shapeA": nA, "pA": pA, "shapeB": nB, "pB": pB, "gap": gap,
                            "taxA": taxA, "taxB": taxB, "tax_joint": taxAB,
                            "delta": delta, "status": status,
                        })
    out = HERE / "l4_composability.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {out.name} ({len(rows)} rows), wall {time.time()-t0:.1f}s, RSS {rss_gb():.2f}GB\n")

    evals = [r for r in rows if r["status"] == "OK"]
    inf_single = [r for r in rows if r["status"] == "SINGLE_INFEASIBLE"]
    inf_joint = [r for r in rows if r["status"] == "JOINT_INFEASIBLE"]
    print(f"Rows: {len(rows)} total; evaluable {len(evals)}; single-infeasible {len(inf_single)}; "
          f"joint-infeasible {len(inf_joint)}")

    print("\n=== delta = tax(A+B) - tax(A) - tax(B), by gap ===")
    print(f"{'gap':>4} {'n':>5} {'delta==0':>9} {'|delta|<=1':>10}  delta distribution")
    for g in (0, 1, 2, 3, 4):
        sub = [r for r in evals if r["gap"] == g]
        if not sub:
            continue
        dist = Counter(r["delta"] for r in sub)
        n0 = sum(1 for r in sub if r["delta"] == 0)
        n1 = sum(1 for r in sub if abs(r["delta"]) <= 1)
        print(f"{g:>4} {len(sub):>5} {n0:>9} {n1:>10}  {dict(sorted(dist.items()))}")

    big = [r for r in evals if r["gap"] >= 2]
    n0_big = sum(1 for r in big if r["delta"] == 0)
    a_hit = len(big) > 0 and n0_big == len(big)
    print(f"\nFrozen (a) [70%] EXACT additivity (delta==0) for ALL gap>=2 rows: "
          f"{'HIT' if a_hit else 'MISS'} ({n0_big}/{len(big)} exact; "
          f"{sum(1 for r in big if abs(r['delta'])<=1)}/{len(big)} within +-1)")
    if not a_hit and big:
        viol = [r for r in big if r["delta"] != 0][:12]
        print("  gap>=2 violations (first 12):")
        for r in viol:
            print(f"    {r['family']} m={r['m']} {r['shapeA']}@{r['pA']}+{r['shapeB']}@{r['pB']} "
                  f"gap={r['gap']}: taxA={r['taxA']} taxB={r['taxB']} joint={r['tax_joint']} "
                  f"delta={r['delta']}")

    small = [r for r in evals if r["gap"] <= 1]
    n_int = sum(1 for r in small if r["delta"] != 0)
    b_hit = len(small) > 0 and n_int > 0
    print(f"Frozen (b) [55%] interference (delta!=0) exists at gap<=1: "
          f"{'HIT' if b_hit else 'MISS'} ({n_int}/{len(small)} rows with delta!=0)")

    print(f"\nPeak RSS: {rss_gb():.3f} GB")


if __name__ == "__main__":
    main()
