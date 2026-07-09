#!/usr/bin/env python3
"""
Task 4, final: proper QSD via sparse dominant-eigenvector solve.

Diagnosis of operator4.py: naive forward power iteration on the finite
transient DAG (basin of x=1, minus the ~12-state spurious wraparound
cycle) necessarily DRAINS to zero live states because every path has
finite length (max 118 steps for p=19,K=14) -- there is no true
infinite recurrence, so the iteration eventually collapses onto
whichever single straggler path survives longest, which is a finite-
size artifact, NOT the QSD. The genuine QSD is the dominant
LEFT-eigenvector of the substochastic transition matrix Q restricted to
transient states (state 1 removed/absorbing) -- found here directly via
sparse eigenvalue decomposition (ARPACK, which finds the eigenvector
by the matrix's algebraic structure, immune to the finite-drain
artifact that corrupts naive iteration to convergence).
"""
import json
import sys
from collections import deque
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigs

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

def main():
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 19
    K = int(sys.argv[2]) if len(sys.argv) > 2 else 14
    print(f"=== p={p} K={K} M={p*2**K} ===")
    odds, targets, idx1, basin1, M, n, n_basin, n_excluded = build_and_restrict(p, K)
    print(f"total states={n}, basin-of-1={n_basin} ({n_basin/n*100:.4f}%), excluded (spurious traps)={n_excluded}")

    # transient states = basin1 minus idx1 (the absorbing state)
    live_mask = basin1.copy()
    live_mask[idx1] = False
    live_idx = np.where(live_mask)[0]
    n_live = len(live_idx)
    remap = -np.ones(n, dtype=np.int64)
    remap[live_idx] = np.arange(n_live)
    print(f"transient states = {n_live}")

    # build sparse substochastic matrix Q (n_live x n_live): Q[i,j] = 1 if state i -> state j (j also transient)
    rows = []
    cols = []
    for local_i, global_i in enumerate(live_idx):
        tgt = targets[global_i]
        if live_mask[tgt]:
            rows.append(local_i)
            cols.append(remap[tgt])
        # else: transition leads to idx1 (absorption) or (shouldn't happen) outside basin -- dropped, row sums < 1
    data = np.ones(len(rows))
    Q = sp.csr_matrix((data, (rows, cols)), shape=(n_live, n_live))
    row_sums = np.array(Q.sum(axis=1)).flatten()
    print(f"substochastic row-sum stats: min={row_sums.min()}, max={row_sums.max()}, "
          f"n_rows_with_leak(row_sum==0, i.e. direct predecessor of idx1)={int((row_sums==0).sum())}")

    # dominant LEFT eigenvector of Q <=> dominant RIGHT eigenvector of Q^T
    print("solving sparse eigenproblem (ARPACK, largest magnitude eigenvalue)...")
    vals, vecs = eigs(Q.T.tocsr(), k=1, which='LM', maxiter=50000)
    lam = vals[0].real
    v = vecs[:, 0].real
    if v.sum() < 0:
        v = -v
    v = np.clip(v, 0, None)  # Perron eigenvector should be sign-definite; clip tiny numerical negatives
    v = v / v.sum()
    print(f"dominant eigenvalue (survival probability per step) = {lam:.10f}")

    # map back to full state space, then marginalize mod p
    dist_full = np.zeros(n)
    dist_full[live_idx] = v
    r_of_state = (odds % p)
    marg = np.zeros(p)
    for r in range(p):
        marg[r] = dist_full[r_of_state == r].sum()
    s = marg.sum()
    marg = marg / s

    inv3 = pow(3, -1, p)
    h_p = (-inv3) % p
    for r in range(p):
        print(f"  r={r:3d} QSD_marginal={marg[r]:.6f} (1/p={1/p:.6f}) diff={marg[r]-1/p:+.6f}")
    hole = 1 / p - marg[h_p]
    rel_hole = hole / (1 / p)
    print(f"h_p={h_p}  QSD marginal at h_p={marg[h_p]:.6f}  1/p={1/p:.6f}  "
          f"operator_hole={hole:+.6f}  rel_operator_hole={rel_hole:+.4f}  survival_eigenvalue={lam:.10f}")

    with open(f"qsd5_p{p}_K{K}.json", "w") as f:
        json.dump({"p": p, "K": K, "M": int(M), "n_states_total": int(n),
                    "n_basin": int(n_basin), "n_excluded_spurious": int(n_excluded),
                    "n_transient": int(n_live),
                    "h_p": int(h_p), "marginal": marg.tolist(),
                    "operator_hole": float(hole), "rel_operator_hole": float(rel_hole),
                    "survival_eigenvalue": float(lam)}, f, indent=2)

if __name__ == "__main__":
    main()
