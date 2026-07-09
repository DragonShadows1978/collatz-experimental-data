#!/usr/bin/env python3
"""
Task 4, corrected: the naive finite functional-graph operator on
Z/(p*2^K)Z collapses almost all mass onto the absorbing fixed point
x=1 (3*1+1=4=2^2, y=1) under plain power iteration -- because that
graph has no "restart," unlike real Collatz trajectories which begin
fresh at a new n0 each time and only terminate at 1. That degenerate
result (operator2.py) is NOT what SHADOW/ORBIT measure; it is an
artifact of treating the transient chain as if it were ergodic.

Correct construction: QUASI-STATIONARY DISTRIBUTION of the sub-stochastic
chain with state x=1 (and its pre-images that immediately re-enter 1,
i.e. the whole {1}-cycle) made ABSORBING/REMOVED. This is the standard
object for "distribution conditional on not yet having died," which is
exactly what a live, unterminated Collatz trajectory's residue is at a
uniformly random step. Concretely:
  - Build the same transition graph, but delete state x=1 (remove the
    row/col for r-class of the absorbing state) -- any transition INTO
    x=1 is treated as absorption (leaves the transient system).
  - Take the principal left eigenvector of the resulting SUBSTOCHASTIC
    matrix Q (restricted to transient states) with the LARGEST
    eigenvalue lambda < 1 (Perron-Frobenius for substochastic
    irreducible-on-transient-support matrices). That eigenvector,
    normalized to sum 1, is the quasi-stationary distribution: the
    distribution of x mod (p*2^K) conditional on survival, in the
    long-run limit. This is the correct finite-state analogue of the
    empirical "stationary distribution along the descent."
"""
import json
import sys
import numpy as np

def build_transient_operator(p, K):
    M = p * (2 ** K)
    odds = np.arange(1, M, 2, dtype=np.int64)
    n = len(odds)
    targets = np.empty(n, dtype=np.int64)
    absorbed = np.zeros(n, dtype=bool)
    idx_of = {int(x): i for i, x in enumerate(odds)}
    for i in range(n):
        x = int(odds[i])
        m = 3 * x + 1
        y = m
        while y % 2 == 0:
            y //= 2
        y_mod = y % M
        if y_mod == 1:
            absorbed[i] = True
            targets[i] = idx_of[1]  # self-loop-ish, but we'll mask it out of the transient matrix
        else:
            targets[i] = idx_of.get(y_mod, idx_of[1])
    return odds, targets, absorbed, M, n

def quasi_stationary(targets, absorbed, n, max_iters=20000, tol=1e-13):
    """
    Power-iterate the SUBSTOCHASTIC transient operator: mass flowing into
    an absorbed state is REMOVED (not redeposited), then renormalize each
    iteration to isolate the quasi-stationary distribution direction
    (standard method: iterate v <- Q^T v / ||Q^T v||_1, converges to the
    dominant eigenvector of Q since Q is substochastic + irreducible on
    the transient class).
    """
    dist = np.full(n, 1.0 / n, dtype=np.float64)
    # zero out the absorbed state's own initial mass contribution over time by just
    # removing mass that maps to it each step (it's absorbed -> leaves the system)
    prev_lambda = None
    for it in range(max_iters):
        new = np.zeros(n, dtype=np.float64)
        live = ~absorbed
        np.add.at(new, targets[live], dist[live])
        lam = new.sum()  # the surviving fraction = quasi-stationary decay eigenvalue estimate
        if lam <= 0:
            raise RuntimeError("all mass absorbed, chain died out completely")
        new_normalized = new / lam
        diff = np.abs(new_normalized - dist).sum()
        dist = new_normalized
        if it % 200 == 0:
            print(f"  iter {it}: lambda={lam:.8f} L1 change={diff:.3e}")
        if diff < tol:
            print(f"  converged at iter {it}: lambda(survival eigenvalue)={lam:.8f}")
            break
    return dist, lam

def main():
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 19
    K = int(sys.argv[2]) if len(sys.argv) > 2 else 14
    max_iters = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
    print(f"p={p} K={K} M={p*2**K}")
    odds, targets, absorbed, M, n = build_transient_operator(p, K)
    print(f"n states = {n}, absorbed (map directly to 1) = {absorbed.sum()}")
    dist, lam = quasi_stationary(targets, absorbed, n, max_iters=max_iters)

    r_of_state = (odds % p)
    marg = np.zeros(p)
    for r in range(p):
        marg[r] = dist[r_of_state == r].sum()
    marg = marg / marg.sum()

    inv3 = pow(3, -1, p)
    h_p = (-inv3) % p
    for r in range(p):
        print(f"  r={r:3d} marginal={marg[r]:.6f} (1/p={1/p:.6f}) diff={marg[r]-1/p:+.6f}")
    hole = 1/p - marg[h_p]
    print(f"h_p={h_p} operator(quasi-stationary) marginal at h_p = {marg[h_p]:.6f}, "
          f"1/p={1/p:.6f}, operator_hole = {hole:+.6f}, survival_eigenvalue={lam:.8f}")

    with open(f"qsd_p{p}_K{K}.json", "w") as f:
        json.dump({"p": p, "K": K, "M": int(M), "n_states": int(n), "h_p": int(h_p),
                    "marginal": marg.tolist(), "operator_hole": float(hole),
                    "survival_eigenvalue": float(lam)}, f, indent=2)

if __name__ == "__main__":
    main()
