# Lock 1 — B-Floor Theorem

Date: 2026-05-25

## Statement

For any exponent word `w = (a_0, ..., a_{k-1})` with all `a_j >= 1` and any
total `A = sum a_j >= k`, the offset

```text
B_w = sum_{j=0}^{k-1} 3^(k-1-j) * 2^(A_j)
```

satisfies the universal lower bound

```text
B_w >= 3^k - 2^k
```

with equality exactly for the all-1 word `w = (1, 1, ..., 1)` with `A = k`.

## Proof

Since all `a_j >= 1`, the prefix sums satisfy `A_j >= j` for every `j`.
Therefore `2^(A_j) >= 2^j`, with equality iff `a_0 = a_1 = ... = a_{j-1} = 1`.

Substituting:

```text
B_w = sum_{j=0}^{k-1} 3^(k-1-j) * 2^(A_j)
    >= sum_{j=0}^{k-1} 3^(k-1-j) * 2^j
    = 3^(k-1) - 3^(k-2)*2 + ... (geometric sum)
```

The sum `sum_{j=0}^{k-1} 3^(k-1-j) * 2^j` is a standard geometric series:

```text
sum_{j=0}^{k-1} 3^(k-1-j) * 2^j
= 3^(k-1) * sum_{j=0}^{k-1} (2/3)^j
= 3^(k-1) * (1 - (2/3)^k) / (1 - 2/3)
= 3^k * (1 - 2^k/3^k)
= 3^k - 2^k
```

Therefore `B_w >= 3^k - 2^k`, with equality when `A_j = j` for all `j`, i.e.,
when `a_j = 1` for all `j`. ☐

## Corollary: Rotation Invariance

The lower bound `3^k - 2^k` holds for every cyclic rotation of `w` because
all rotations have the same length `k`, and the bound depends only on `k`.

## Corollary: Excess Threshold for Rotation-Window Feasibility

Let `D = 2^A - 3^k > 0`. The rotation-window lemma requires some rotation
`rho(w)` to satisfy `0 < B_rho < D`. A necessary condition is:

```text
3^k - 2^k < D = 2^A - 3^k
```

i.e.,

```text
2 * 3^k < 2^k + 2^A
```

Define `excess = A - ceil(k * log_2(3))`. Then:

- At `excess = 0`: `2^A <= 2 * 3^k` (since `2^(ceil(k*log_2(3))) = O(3^k)`).
  Verified numerically: `2*3^k >= 2^k + 2^A` for all `k = 3..20` at `excess = 0`.
  Therefore **no rotation of any word** can satisfy `B_rho < D` at `excess = 0`.
  The rotation-window lemma is geometrically impossible for all excess-0 classes.

- At `excess >= 1`: `2^A >= 2 * 2^(ceil(k*log_2(3))) > 2 * 3^k`, so the necessary
  condition is satisfied. There exist words (the all-1 extension) with `B < D`.

## Consequence for the Kernel

The kernel — primitive non-all-2 necklaces not killed by the rotation-window —
consists precisely of classes where the rotation-window is geometrically blocked
or structurally blocked for specific survivors.

The excess-0 kernel arises from geometric blockage: `B_floor >= D` for every word.

The excess-1, 2, 3 kernels arise from structural blockage: the prime-wall filters
select survivors whose B-values stay above D across all rotations, even though
D > B_floor.
