# Lock 1 — Trailing-2 Recurrence

Date: 2026-05-25

## Purpose

This document establishes an exact recurrence for `B_w mod D` when a word `w`
is extended by appending a single exponent `a = 2`. It shows that the residue
triples exactly under this operation, and derives its consequences for the
bounded-excess kernel.

## Setup

For a word `w = (a_0, ..., a_{k-1})` with total `A` and length `k`, define:

```text
B_w = sum_{j=0}^{k-1} 3^(k-1-j) * 2^(A_j)
D_w = 2^A - 3^k
```

Let `w' = (a_0, ..., a_{k-1}, 2)` be the word with a trailing 2 appended.
Then `k' = k+1` and `A' = A+2`.

## Recurrence for B

The offset recurrence gives:

```text
B_{w'} = 3 * B_w + 2^A
```

Proof: The new sum adds one term at position `j = k` and shifts the 3-powers:

```text
B_{w'} = sum_{j=0}^{k} 3^(k-j) * 2^(A_j)
       = 3 * sum_{j=0}^{k-1} 3^(k-1-j) * 2^(A_j) + 3^0 * 2^(A_k)
       = 3 * B_w + 2^A
```

## Recurrence for D

```text
D_{w'} = 2^(A+2) - 3^(k+1) = 4 * 2^A - 3 * 3^k
```

Using `D_w = 2^A - 3^k`:

```text
D_{w'} = 4 * (D_w + 3^k) - 3 * 3^k = 4 * D_w + 3^k
```

**Algebraic identity:**

```text
D_{w'} = 3 * D_w + 2^A
```

Proof: `3 * D_w + 2^A = 3 * (2^A - 3^k) + 2^A = 4 * 2^A - 3^{k+1} = D_{w'}`. ☐

This identity is verified for all `(k, A)` with `D > 0`.

## Residue Tripling Theorem

**Theorem:** If `D_w < B_w < 2 * D_w` (i.e., `floor(B_w / D_w) = 1`), then:

```text
B_{w'} mod D_{w'} = 3 * (B_w mod D_w)
```

and `D_{w'} < B_{w'} < 2 * D_{w'}`.

**Proof:**

Let `r = B_w mod D_w = B_w - D_w` (since `floor = 1`). Then:

```text
B_{w'} = 3 * B_w + 2^A
       = 3 * (D_w + r) + 2^A
       = 3 * D_w + 2^A + 3r
       = D_{w'} + 3r
```

using the algebraic identity `3 * D_w + 2^A = D_{w'}`.

Therefore `B_{w'} = D_{w'} + 3r`, and since `r < D_w`:

```text
B_{w'} mod D_{w'} = 3r = 3 * (B_w mod D_w)
```

For the range condition:

- Lower: `B_{w'} = D_{w'} + 3r > D_{w'}` since `r > 0`. ✓
- Upper: Need `3r < D_{w'} = 4 * D_w + 3^k`. Since `r < D_w`, we have `3r < 3 * D_w < 4 * D_w < D_{w'}`. ✓

Therefore `D_{w'} < B_{w'} < 2 * D_{w'}`. ☐

## Chain Theorem

**Theorem:** Let `w_0` be any word with `D_{w_0} < B_{w_0} < 2 * D_{w_0}`.
Define `w_m = w_0 + (2, 2, ..., 2)` with `m` trailing 2s appended.
Then for all `m >= 0`:

```text
B_{w_m} mod D_{w_m} = 3^m * (B_{w_0} mod D_{w_0})
```

and `D_{w_m} < B_{w_m} < 2 * D_{w_m}`.

**Proof:** Induction on `m`, using the Residue Tripling Theorem. ☐

**Consequence:** The residue `3^m * r_0` is never 0 modulo `D_{w_m}` because:

1. `gcd(3, D_{w_m}) = 1`: since `D = 2^A - 3^k` and `3 | 2^A - 3^k` would require
   `3 | 2^A`, which is false.

2. `3^m * r_0 < D_{w_m}`: established above.

Therefore `B_{w_m} not equiv 0 mod D_{w_m}` for all `m >= 0`. ☐

## Concrete Chain: Starting at `(1, 2, 1, 3)`

The base word `w_0 = (1, 2, 1, 3)` has `k=4`, `A=7`, `D=47`, `B=85`, `r_0=38`.

Extended chain `w_m = (1, 2, 1, 3, 2, ..., 2)` with `m` trailing 2s:

```text
m=0:  k=4,  A=7,   D=47,       r=38
m=1:  k=5,  A=9,   D=269,      r=114
m=2:  k=6,  A=11,  D=1319,     r=342
m=3:  k=7,  A=13,  D=6005,     r=1026
m=4:  k=8,  A=15,  D=26207,    r=3078
m=5:  k=9,  A=17,  D=111389,   r=9234
m=6:  k=10, A=19,  D=465239,   r=27702
m=7:  k=11, A=21,  D=1920005,  r=83106
m=8:  k=12, A=23,  D=7857167,  r=249318
```

Residues: `38, 114, 342, 1026, 3078, 9234, 27702, 83106, 249318, ...`
Ratio: exactly 3 each step. None is 0 mod the corresponding `D`.

This chain covers one kernel necklace per class `(k=4+m, A=7+2m)` at
`excess = (7+2m) - ceil((4+m)*log_2(3))`. These classes fall in `excess ∈ {0,1,2}`
depending on the fractional part of `(4+m) * log_2(3)`.

## Significance

The Chain Theorem closes Theorem B for all word families reachable by
trailing-2 extension from a verified base word.

The remaining open question for Theorem B is whether ALL kernel necklaces
(for all `(k, excess)` classes) fall into finitely many such chains from
finitely many base words, or whether a separate argument is needed for the
excess-0 kernel where `B >> D`.
