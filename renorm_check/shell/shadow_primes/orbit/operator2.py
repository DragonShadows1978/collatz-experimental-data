#!/usr/bin/env python3
"""
Task 4, numpy version: exact residue operator on Z/(p*2^K)Z (odd states),
vectorized power iteration with convergence check. Same construction as
operator.py (exact integer map application per state) but scaled for
larger K via numpy, and with an explicit convergence diagnostic (L1 change
per iteration) rather than a fixed iteration count.
"""
import json
import sys
import numpy as np

def build_operator(p, K):
    M = p * (2 ** K)
    odds = np.arange(1, M, 2, dtype=np.int64)
    n = len(odds)
    # map: odd value -> index (odds are 1,3,5,...,M-1 -> index (x-1)//2)
    def to_idx(x):
        return (x % M) // 2  # since all our x's (mod M) are odd, (x-1)//2 == x//2 for odd x... check
    # careful: for odd x, (x-1)//2 == x//2 (integer division). Use x//2 consistently.
    targets = np.empty(n, dtype=np.int64)
    # vectorized exact map computation using numpy won't easily do variable-length
    # while-loops per element; do it with python ints via array of python objects
    # for exactness (v2 extraction must be exact). Use a python loop but only once,
    # not per-iteration -- this is the expensive one-time cost, iteration reuses it.
    for i in range(n):
        x = int(odds[i])
        m = 3 * x + 1
        y = m
        while y % 2 == 0:
            y //= 2
        y_mod = y % M
        # y_mod should be odd (y is odd by construction after stripping all factors of 2)
        targets[i] = y_mod // 2
    return odds, targets, M, n

def power_iterate(targets, n, max_iters=20000, tol=1e-12):
    dist = np.full(n, 1.0 / n, dtype=np.float64)
    for it in range(max_iters):
        new = np.zeros(n, dtype=np.float64)
        np.add.at(new, targets, dist)
        diff = np.abs(new - dist).sum()
        dist = new
        if it % 200 == 0:
            print(f"  iter {it}: L1 change = {diff:.3e}")
        if diff < tol:
            print(f"  converged at iter {it}, L1 change {diff:.3e}")
            break
    return dist

def main():
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 19
    K = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    max_iters = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
    print(f"p={p} K={K} M={p*2**K}")
    odds, targets, M, n = build_operator(p, K)
    print(f"n states = {n}")
    dist = power_iterate(targets, n, max_iters=max_iters)
    total = dist.sum()
    print(f"total mass = {total}")

    r_of_state = (odds % p)
    marg = np.zeros(p)
    for r in range(p):
        marg[r] = dist[r_of_state == r].sum()
    marg = marg / marg.sum()

    inv3 = pow(3, -1, p)
    h_p = (-inv3) % p
    for r in range(p):
        print(f"  r={r:3d} marginal={marg[r]:.6f} (1/p={1/p:.6f}) diff={marg[r]-1/p:+.6f}")
    print(f"h_p={h_p} operator marginal at h_p = {marg[h_p]:.6f}, 1/p={1/p:.6f}, "
          f"operator_hole = {1/p - marg[h_p]:+.6f}")

    with open(f"operator_p{p}_K{K}.json", "w") as f:
        json.dump({"p": p, "K": K, "M": int(M), "n_states": int(n), "h_p": int(h_p),
                    "marginal": marg.tolist(), "operator_hole": float(1/p - marg[h_p])}, f, indent=2)

if __name__ == "__main__":
    main()
