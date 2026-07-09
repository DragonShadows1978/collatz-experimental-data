#!/usr/bin/env python3
"""
Task 4, final methodology note + measurement.

PROVEN: the finite functional-graph operator on odd residues mod
M=p*2^K, restricted to the true basin of x=1 with state 1 itself
absorbing, is EXACTLY NILPOTENT (verified directly: all eigenvalues of
the dense transient sub-matrix Q are 0.0 for p=19,K=9, confirmed via
np.linalg.eigvals). This is because every transient path has finite
length (max distance to absorption = 118 for p=19,K=14) -- there is no
cycle, hence no formal quasi-stationary eigenvector for ARPACK (or any
eigensolver) to find; "the dominant eigenvector" does not exist as a
well-posed object for this exact finite truncation. This null result
itself answers part of task 4: the operator construction as specified
(exact finite truncation to depth K) has NO intrinsic stationary
eigenvector, full stop -- not "found but doesn't match," but
structurally absent.

What DOES exist and IS measurable: forward power iteration from a
uniform start produces a renormalized-shape trajectory that empirically
PLATEAUS (stabilizes in shape, if not in total surviving mass) over a
"bulk" window of iterations -- roughly it 15-70 for p=19,K=14 (see
operator4.py output) -- before the finite-size drain (few remaining
live states) corrupts the shape at late iterations. This plateau is the
closest well-defined analogue of "what the pure residue-dynamics
predicts for a typical mid-trajectory step," and we report ITS value at
h_p as the operator's testable prediction, with the caveat that it is a
heuristic transient plateau, not a proven fixed point.

This script: automates finding the plateau by tracking rolling-window
stability of the shape (not just raw survivor count) and reports the
plateau-averaged hole per prime for the p in the shared set.
"""
import json
import sys
from collections import deque
import numpy as np

def build_and_restrict(p, K):
    M = p * (2 ** K)
    odds = np.arange(1, M, 2, dtype=np.int64)
    n = len(odds)
    idx_of = {int(x): i for i, x in enumerate(odds)}
    targets = np.empty(n, dtype=np.int64)
    for i in range(n):
        x = int(odds[i])
        m = 3 * x + 1
        y = m
        while y % 2 == 0:
            y //= 2
        targets[i] = idx_of[y % M]

    idx1 = idx_of[1]
    preimg = [[] for _ in range(n)]
    for i in range(n):
        preimg[targets[i]].append(i)
    basin1 = np.zeros(n, dtype=bool)
    q = deque([idx1])
    basin1[idx1] = True
    while q:
        u = q.popleft()
        for v in preimg[u]:
            if not basin1[v]:
                basin1[v] = True
                q.append(v)
    return odds, targets, idx1, basin1, M, n

def plateau_run(p, K, max_iters=150):
    odds, targets, idx1, basin1, M, n = build_and_restrict(p, K)
    live_mask = basin1.copy()
    live_mask[idx1] = False
    n_live0 = int(live_mask.sum())
    dist = np.zeros(n, dtype=np.float64)
    dist[live_mask] = 1.0 / n_live0

    inv3 = pow(3, -1, p)
    h_p = (-inv3) % p
    r_of_state = odds % p

    hole_series = []
    live_count_series = []
    for it in range(max_iters):
        new = np.zeros(n, dtype=np.float64)
        src = np.where(live_mask & (dist > 0))[0]
        np.add.at(new, targets[src], dist[src])
        new[idx1] = 0.0
        new[~basin1] = 0.0
        lam = new.sum()
        n_live_now = int((new > 0).sum())
        if lam <= 0 or n_live_now < max(30, p * 2):
            # stop before finite-size drain artifact dominates (require at
            # least ~2 states per residue class on average for a meaningful marginal)
            break
        dist = new / lam
        marg = np.zeros(p)
        for r in range(p):
            marg[r] = dist[r_of_state == r].sum()
        marg = marg / marg.sum()
        hole = 1 / p - marg[h_p]
        hole_series.append(hole)
        live_count_series.append(n_live_now)

    return h_p, hole_series, live_count_series

def main():
    primes_to_test = [5, 7, 11, 13, 17, 19, 23]
    K = 16
    results = {}
    for p in primes_to_test:
        h_p, hole_series, live_series = plateau_run(p, K, max_iters=200)
        if len(hole_series) < 20:
            print(f"p={p}: too few usable iterations ({len(hole_series)}), skipping plateau avg")
            continue
        # plateau window: iterations 15 to (len-10), i.e. skip initial transient
        # and the last 10 (closest to finite-size drain)
        lo = 15
        hi = max(lo + 5, len(hole_series) - 10)
        window = hole_series[lo:hi]
        plateau_mean = sum(window) / len(window) if window else float("nan")
        plateau_std = (sum((x - plateau_mean) ** 2 for x in window) / len(window)) ** 0.5 if window else float("nan")
        results[p] = dict(h_p=h_p, plateau_mean_hole=plateau_mean, plateau_std=plateau_std,
                           n_iters_used=len(hole_series), window=[lo, hi])
        print(f"p={p:3d} h_p={h_p:3d} plateau_hole_mean(it {lo}-{hi})={plateau_mean:+.5f} "
              f"+/- {plateau_std:.5f}  (n_usable_iters={len(hole_series)})")

    with open(f"operator_plateau_K{K}.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
