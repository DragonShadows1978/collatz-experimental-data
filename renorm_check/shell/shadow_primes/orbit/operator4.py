#!/usr/bin/env python3
"""
Task 4, final corrected version.

Diagnosis of prior bugs (operator2.py, operator3.py):
  - operator2.py: plain power iteration on the full functional graph on
    Z/(p*2^K)Z converges to the TRUE fixed point x=1 with ~100% mass
    (correct in principle, but degenerate/uninformative -- that's not
    the "distribution along a live trajectory," it's just "eventually
    every state maps to 1").
  - operator3.py: tried to build a quasi-stationary distribution (QSD)
    by treating direct-predecessors-of-1 as absorbing and renormalizing
    survivor mass each iteration. Found survival eigenvalue = 1.000000
    (no decay) because power iteration got trapped in a SPURIOUS
    3-cycle at large residues near M (verified: representative integers
    131071, 196607, 294911 for p=19,K=14,M=311296 -- an artifact of
    modular wraparound, basin size 12/155648 states, NOT part of any
    real Collatz trajectory, which would pass through such a residue
    only transiently for one specific huge starting integer and then
    continue, never staying trapped).

Fix: restrict to the BASIN OF THE TRUE FIXED POINT x=1 (found via exact
backward BFS on the functional graph -- 155636/155648 = 99.992% of
states for p=19,K=14), discard the ~12 states in the spurious-cycle
basin entirely, THEN compute the QSD (dominant eigenvector of the
substochastic sub-matrix with state 1 itself absorbing/removed) via
power iteration on that restricted, verified-non-degenerate transient set.
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
    n_basin = int(basin1.sum())
    n_excluded = n - n_basin
    return odds, targets, idx1, basin1, M, n, n_basin, n_excluded

def qsd_power_iteration(targets, idx1, basin1, n, max_iters=20000, tol=1e-14):
    """
    Restrict to states in basin1 (guaranteed to reach x=1, no spurious
    trap). Mark idx1 itself as absorbing (mass reaching it leaves the
    transient system -- this is the analogue of a live trajectory
    TERMINATING, matching what SHADOW/ORBIT measure: statistics over
    steps BEFORE termination). Iterate v <- Q^T v, renormalize each
    step (standard QSD power method); dominant eigenvalue = survival
    probability per step, dominant eigenvector = QSD.
    """
    live_mask = basin1.copy()
    live_mask[idx1] = False  # idx1 is absorbing, remove from transient set
    n_live = int(live_mask.sum())
    print(f"  transient (live, non-absorbed, in true basin) states = {n_live}")

    dist = np.zeros(n, dtype=np.float64)
    dist[live_mask] = 1.0 / n_live

    lam = None
    shape_history = []
    for it in range(max_iters):
        new = np.zeros(n, dtype=np.float64)
        # only propagate mass FROM live states; mass landing on idx1 (or outside
        # basin1, which shouldn't happen since basin1 is forward-closed under
        # dynamics restricted to itself) is dropped
        src = np.where(live_mask & (dist > 0))[0]
        np.add.at(new, targets[src], dist[src])
        new[idx1] = 0.0  # absorbed mass discarded (idx1 does not re-emit)
        new[~basin1] = 0.0  # safety: should be zero anyway (basin1 forward-closed minus idx1 sink)
        raw_survivors = int((new > 0).sum())
        lam = new.sum()
        if lam <= 0:
            print(f"  iter {it}: chain fully drained (finite-diameter DAG, no true stationary "
                  f"support past this point) -- using last nonzero shape")
            break
        new_shape = new / lam  # renormalized shape (this is what we track for convergence)
        diff = np.abs(new_shape - dist).sum()
        dist = new_shape
        if it % 10 == 0 or it < 5:
            print(f"  iter {it}: survival lambda={lam:.10f} L1 shape-change={diff:.3e} "
                  f"live_states={raw_survivors}")
        shape_history.append(dist.copy())
        if diff < tol and it > 60:
            print(f"  CONVERGED (shape stable) iter {it}: survival eigenvalue lambda={lam:.10f}")
            break
    return dist, lam, shape_history

def main():
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 19
    K = int(sys.argv[2]) if len(sys.argv) > 2 else 14
    max_iters = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
    print(f"=== p={p} K={K} M={p*2**K} ===")
    odds, targets, idx1, basin1, M, n, n_basin, n_excluded = build_and_restrict(p, K)
    print(f"total states={n}, basin-of-1={n_basin} ({n_basin/n*100:.4f}%), excluded (spurious traps)={n_excluded}")

    dist, lam, shape_history = qsd_power_iteration(targets, idx1, basin1, n, max_iters=max_iters)

    r_of_state = (odds % p)
    inv3 = pow(3, -1, p)
    h_p = (-inv3) % p

    # report marginal shape at several checkpoints to show convergence-then-drain behavior
    checkpoints = [10, 20, 30, 40, 50, 60, 70, 80, min(90, len(shape_history)-1)]
    checkpoints = sorted(set(c for c in checkpoints if 0 <= c < len(shape_history)))
    print("\n  Shape checkpoints (marginal at h_p over iteration index):")
    for c in checkpoints:
        d = shape_history[c]
        marg_c = np.zeros(p)
        for r in range(p):
            marg_c[r] = d[r_of_state == r].sum()
        s = marg_c.sum()
        if s > 0:
            marg_c = marg_c / s
            print(f"    it={c:3d}  marginal[h_p={h_p}]={marg_c[h_p]:.6f}  hole={1/p-marg_c[h_p]:+.6f}")

    # final usable shape = last entry in shape_history (before/at drain)
    dist_final = shape_history[-1] if shape_history else dist
    marg = np.zeros(p)
    for r in range(p):
        marg[r] = dist_final[r_of_state == r].sum()
    s = marg.sum()
    marg = marg / s

    for r in range(p):
        print(f"  r={r:3d} QSD_marginal={marg[r]:.6f} (1/p={1/p:.6f}) diff={marg[r]-1/p:+.6f}")
    hole = 1 / p - marg[h_p]
    print(f"h_p={h_p}  QSD marginal at h_p={marg[h_p]:.6f}  1/p={1/p:.6f}  "
          f"operator_hole={hole:+.6f}  survival_eigenvalue(last)={lam:.10f}")

    with open(f"qsd4_p{p}_K{K}.json", "w") as f:
        json.dump({"p": p, "K": K, "M": int(M), "n_states_total": int(n),
                    "n_basin": int(n_basin), "n_excluded_spurious": int(n_excluded),
                    "h_p": int(h_p), "marginal": marg.tolist(),
                    "operator_hole": float(hole), "survival_eigenvalue": float(lam)}, f, indent=2)

if __name__ == "__main__":
    main()
