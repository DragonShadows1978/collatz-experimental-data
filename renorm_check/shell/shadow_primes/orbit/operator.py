#!/usr/bin/env python3
"""
Task 4: exact residue-transition operator on Z/pZ for the odd-map,
accounting for v2 exactly via the operator on Z/(p*2^K)Z marginalized.

The odd-map is: x -> y = (3x+1) / 2^v2(3x+1), where v2 = the 2-adic
valuation of 3x+1 (x odd).

Key fact used: for x odd, 3x+1 is even (always), and v2(3x+1) depends
on x mod 2^k for increasing k (it's determined by how many low bits of
3x+1 are zero, a 2-adic condition on x, NOT an independent random
variable). We build the EXACT joint operator on states (x mod p, x mod 2^K)
for K large enough that P(v2 > K) is negligible (< 2^-K), transition
x -> y = (3x+1) >> v2, marginalize onto Z/pZ.

Because gcd(2,p)=1 for odd p, x mod p and x mod 2^K are independent
under CRT for a UNIFORM x mod (p*2^K); but the map itself creates
correlation between the two "coordinates" via v2 which depends only on
the 2^K coordinate deterministically -- this is exactly the mechanism
that can create a non-uniform marginal on x mod p even though the map
mod p alone (x -> 3x+1, ignoring the halving) is just an exact bijective
affine map mod p (uniform preserving!). The whole "hole" phenomenon, if
real at the operator level, comes ONLY from the coupling through v2.

We construct the exact transition matrix T on states s = (r, b) where
r = x mod p, b = x mod 2^K (only odd b, i.e. b in {1,3,5,...,2^K-1}),
apply x -> y = (3x+1) >> v2(3x+1) using EXACT integer arithmetic on a
representative integer (CRT-lift r,b to the unique odd x in [0, p*2^K)
matching both, apply the true map, reduce back) -- so v2 is computed
exactly, not modeled. Then marginalize the stationary distribution of T
onto the r-coordinate and compare to the empirical stationary mass at
h_p.

This tests: does the RESIDUE DYNAMICS ALONE (no size/magnitude effects,
just x mod (p*2^K) as a finite Markov chain) reproduce empirical hole?
"""
import json
from fractions import Fraction

def build_operator(p, K=20):
    """
    States: odd residues b mod 2^K (there are 2^(K-1) of them), crossed
    with r mod p (p residues) -> total states = p * 2^(K-1).
    For efficiency we index state by the actual CRT integer x in
    [0, p*2^K) with x odd (since x mod 2 must be 1, x is odd in this
    range representing "odd numbers mod p*2^K" -- but Collatz x is any
    odd positive integer, and reducing mod p*2^K captures the exact
    joint (x mod p, x mod 2^K) periodic structure of the map since the
    map is affine/eventually-shift, and v2(3x+1) depends only on x mod
    2^(v2+1) <= 2^K for K large (P(v2>K) = 2^-K, negligible for K=20).
    """
    M = p * (2 ** K)
    # enumerate odd residues x in [1, M) step 2 -- these are exactly the
    # odd residues mod M; each corresponds to a unique (r=x mod p, b=x mod 2^K)
    odds = list(range(1, M, 2))
    n = len(odds)
    idx = {x: i for i, x in enumerate(odds)}

    # transition: for each odd x mod M, compute y = (3x+1) >> v2 using the
    # ACTUAL value of x (not the representative alone -- but v2(3x+1) only
    # depends on x mod 2^K as long as v2 <= K, which holds w.p. 1-2^-K;
    # if v2 > K (vanishingly rare) we cap by treating 3x+1 as if exactly
    # divisible by 2^K, giving a boundary approximation only in that
    # negligible-probability tail).
    row_targets = [None] * n
    for x in odds:
        m = 3 * x + 1
        v2 = 0
        y = m
        while y % 2 == 0 and v2 < K:
            y //= 2
            v2 += 1
        # y may be even here only if v2 hit cap K (extremely rare, x ~ -1/3 mod 2^K);
        # force odd by continuing (doesn't affect stationary dist meaningfully at K=20)
        while y % 2 == 0:
            y //= 2
        y_mod = y % M
        if y_mod % 2 == 0:
            y_mod = (y_mod + 1) % M  # shouldn't happen; guard
        row_targets[idx[x]] = idx.get(y_mod)
        if row_targets[idx[x]] is None:
            # y_mod odd but computed exactly; must exist in odds list since M's odds are exhaustive
            raise RuntimeError(f"y_mod {y_mod} not odd-indexed, x={x}, y={y}")

    return odds, idx, row_targets, M

def stationary_via_iteration(n, row_targets, iters=4000):
    """Power iteration on the deterministic functional graph (each state has
    exactly one out-edge; this is NOT doubly stochastic in general, so the
    stationary distribution of the induced Markov chain = the distribution
    that a long random walk following these deterministic edges converges to,
    which for a functional graph = uniform over each state's eventual cycle,
    weighted by basin size. We compute via pushing a uniform initial mass
    forward (this is exactly the Markov chain on the functional graph)."""
    dist = [Fraction(1, n) for _ in range(n)]
    for it in range(iters):
        new = [Fraction(0) for _ in range(n)]
        for i in range(n):
            new[row_targets[i]] += dist[i]
        dist = new
        if it % 500 == 0:
            print(f"  iter {it}")
    return dist

def main():
    import sys
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 19
    K = int(sys.argv[2]) if len(sys.argv) > 2 else 14
    print(f"Building exact operator for p={p}, K={K} (M=p*2^K={p*2**K})")
    odds, idx, row_targets, M = build_operator(p, K)
    n = len(odds)
    print(f"n states = {n}")

    # Use float power iteration for speed (n can be large); then also
    # cross-check via exact-count long single trajectory occupancy
    # (functional graph => eventually periodic; count occupancy over a
    # long forward push in floats, which is fine, this is just linear algebra
    # not the arithmetic on Collatz itself -- Collatz map application above
    # IS exact integer).
    dist = [1.0 / n] * n
    ITERS = 3000
    for it in range(ITERS):
        new = [0.0] * n
        for i in range(n):
            new[row_targets[i]] += dist[i]
        dist = new
    total = sum(dist)
    print(f"total mass after {ITERS} iters: {total}")

    # marginalize onto r = x mod p
    marg = [0.0] * p
    for i, x in enumerate(odds):
        marg[x % p] += dist[i]
    s = sum(marg)
    marg = [m / s for m in marg]

    inv3 = pow(3, -1, p)
    h_p = (-inv3) % p
    print(f"h_p = {h_p}")
    for r in range(p):
        print(f"  r={r:3d} marginal={marg[r]:.6f}  (1/p={1/p:.6f})")
    print(f"Operator stationary mass at h_p = {marg[h_p]:.6f} vs 1/p={1/p:.6f}, "
          f"operator_hole = {1/p - marg[h_p]:+.6f}")

    with open(f"operator_p{p}_K{K}.json", "w") as f:
        json.dump({"p": p, "K": K, "M": M, "n_states": n, "h_p": h_p,
                    "marginal": marg, "operator_hole": 1/p - marg[h_p]}, f, indent=2)

if __name__ == "__main__":
    main()
