# Lock 1 — Theorem B: Kernel Exclusion

Date: 2026-05-25

## The Kernel

After the rotation-window lemma and Theorem A, the only surviving pre-final
primitive necklaces lie in classes with `excess in {0, 1, 2, 3}`.
These are the "kernel" classes.

**Theorem B:** No primitive non-all-2 kernel necklace satisfies `D | B_w`.
Equivalently: every kernel necklace has `B_w not equiv 0 mod D`.

---

## Part 1: Trailing-2 Recurrence (Proved)

### Setup

For a word `w` with total `A`, length `k`, offset `B_w`, and deficit `D_w = 2^A - 3^k`,
define `w' = w + (2)` (append a single exponent 2). Then:

**Lemma (Trailing-2 Recurrence):**

```text
B_{w'} = 3 * B_w + 2^A
D_{w'} = 3 * D_w + 2^A
```

**Proof of B recurrence:**

```text
B_{w'} = sum_{j=0}^{k} 3^(k-j) * 2^(A_j)
       = 3 * B_w + 2^(A_k) = 3 * B_w + 2^A
```

**Proof of D recurrence (algebraic identity):**

```text
D_{w'} = 2^(A+2) - 3^(k+1) = 4*2^A - 3*3^k
       = 3*(2^A - 3^k) + 2^A = 3*D_w + 2^A
```

☐

### Residue Tripling Theorem

**Theorem:** If `D_w < B_w < 2*D_w` (i.e., `floor(B_w/D_w) = 1`), then:

```text
B_{w'} mod D_{w'} = 3 * (B_w mod D_w)
```

and `D_{w'} < B_{w'} < 2*D_{w'}`.

**Proof:** Let `r = B_w - D_w` (so `r = B_w mod D_w`). Then:

```text
B_{w'} = 3*B_w + 2^A = 3*(D_w + r) + 2^A = 3*D_w + 2^A + 3r = D_{w'} + 3r
```

So `B_{w'} mod D_{w'} = 3r` (since `3r < D_{w'}`: as `r < D_w` gives `3r < 3*D_w < D_{w'} = 3*D_w + 2^A`).

Range: `B_{w'} = D_{w'} + 3r > D_{w'}` and `B_{w'} < 2*D_{w'}` iff `3r < D_{w'}` (proved above). ☐

### Chain Theorem

**Theorem:** Let `w_0` have `D < B_{w_0} < 2D`. Define `w_m = w_0 + (2,...,2)` (m trailing 2s). Then:

```text
B_{w_m} mod D_{w_m} = 3^m * (B_{w_0} mod D_{w_0})
```

and `D_{w_m} < B_{w_m} < 2*D_{w_m}` for all `m >= 0`.

**Proof:** Induction on `m`. ☐

**Non-vanishing:** The residue `3^m * r_0` is never 0 mod `D_{w_m}` because:

1. `gcd(3, D_{w_m}) = 1`: since `D = 2^A - 3^k` and `3 | D` would require `3 | 2^A`, false.
2. `3^m * r_0 < D_{w_m}` (from the range condition).

Therefore `B_{w_m} not equiv 0 mod D_{w_m}` for all `m >= 0`. ☐

### Concrete Chain: `(1,2,1,3,2,...,2)`

Base: `w_0 = (1,2,1,3)`, `k=4`, `A=7`, `D=47`, `r_0 = 38`.

```text
m=0:  k=4,  A=7,   D=47,       r = 38         (excess=0)
m=1:  k=5,  A=9,   D=269,      r = 114        (excess=1)
m=2:  k=6,  A=11,  D=1319,     r = 342        (excess=1)
m=3:  k=7,  A=13,  D=6005,     r = 1026       (excess=1)
m=4:  k=8,  A=15,  D=26207,    r = 3078       (excess=2)
m=5:  k=9,  A=17,  D=111389,   r = 9234       (excess=2)
m=6:  k=10, A=19,  D=465239,   r = 27702      (excess=2)
m=7:  k=11, A=21,  D=1920005,  r = 83106      (excess=2)
```

Residue ratio: exactly 3 at every step. Never zero. ☐

The excess pattern (0,1,1,1,2,2,2,...) is determined by the fractional parts of
`(4+m) * log_2(3)`.

### Coverage

The Chain Theorem provides non-vanishing for the ENTIRE class of words
reachable by trailing-2 extension from any verified base word in `(D, 2D)`.

The excess-1 and excess-2 kernel necklaces that have `B in (D, 2D)` are
covered by these chains (one chain per kernel class per excess value).

---

## Part 2: Excess-0 Kernel (Partial)

### Setup

For excess-0 classes: `A = ceil(k*log_2(3)) < 2k`, so the all-2 word does
not exist in this class. Every word is non-all-2. Also `B_floor = 3^k - 2^k >= D`
(Theorem A), so all words have `B >= D`. The kernel is the entire class.

### Algebraic Identity

**Lemma:** `B_{all-1} mod D = 2^k * (2^(A-k) - 1) mod D`.

**Proof:**

```text
B_{all-1} = 3^k - 2^k
          = (2^A - D) - 2^k    [since 3^k = 2^A - D]
          = 2^A - 2^k - D
          ≡ 2^A - 2^k = 2^k*(2^(A-k) - 1) mod D
```

☐

### Non-vanishing for Excess-0 (Computational)

Verified for `k = 3..20`: no word of length `k`, total `A = ceil(k*log_2(3))`,
has `B_w ≡ 0 mod D`.

Equivalently: no odd Collatz cycle exists with word length `k` and minimal
contractive total `A`.

### Why the Excess-0 Proof Is Hard

The excess-0 question is: can `sum_j 3^(k-1-j) * 2^(A_j) ≡ 0 mod (2^A - 3^k)`?

If it could: `x = B_w / D` would be a positive integer, giving an odd Collatz cycle.
Since no all-2 word exists in this class (A < 2k), any such cycle would have `x != 1`.

This is equivalent to asking whether any Collatz orbit is periodic with minimal
contractive word length `k`. The computational evidence says no, but this is
essentially the Collatz conjecture restricted to minimal-exponent orbits.

### Baker's Theorem Connection (Conjectured Route)

For a cycle value `x = B_w/D >= 2` to exist:

```text
D | B_w  and  B_w >= 2*D
```

Using `B_w <= k * 3^(k-1) * 2^A` (rough bound) and Baker's lower bound
`D >= C * 3^k / k^kappa`:

```text
2*D <= B_w <= k * 3^(k-1) * 2^A
=> 2*C * 3^k / k^kappa <= k * 3^(k-1) * 2^A
=> 6C / k^(kappa+1) <= 2^A / 3 <= 2 * 3^(k-1) / 3 = 2^(k-1)*(3/2)^(k-1)
```

This does NOT give a contradiction (the right side grows exponentially).

Baker's theorem alone does not rule out large-x cycles. The excess-0 kernel
exclusion is likely equivalent to a new result, not a corollary of Baker.

### Status

```text
Excess-0 kernel: non-vanishing VERIFIED for k=3..20.
                 Formal proof: OPEN.
                 Known equivalent: no Collatz cycle with word
                 of length k and total A = ceil(k*log_2(3)).
```

---

## Part 3: Excess-1, 2, 3 Kernel — Summary

For excess `e in {1, 2, 3}`:

- Most kernel necklaces have `B in (D, 2D)` and are covered by chain families
  (Trailing-2 Recurrence).
- The heartbeat word (all-2) appears at excess=2 when `A = 2k`; it is excluded
  from the no-loop theorem by hypothesis.
- Remaining kernel necklaces at excess=3 are small in number (verified empty
  for `k <= 7`) and require case analysis.

For chains starting at `B in (D, 2D)`:

```text
Non-vanishing: PROVED by Trailing-2 Recurrence + gcd(3, D) = 1.
```

For excess-1 kernel necklaces with `B >= 2D`:

```text
These exist for large k (e.g., k=9, excess=1 has necklaces with B/D up to 3.1).
The Chain Theorem does not directly apply.
Handling: factor-cascade data shows zero_final_residues=0 for all tested classes.
Formal proof: OPEN for the non-chain kernel necklaces.
```

---

## Combined Status

```text
Theorem B — proved components:
  1. Trailing-2 Recurrence closes all chain families (excess 0,1,2,3).
  2. gcd(3, D) = 1 ensures residue 3^m * r_0 is never 0.

Theorem B — open components:
  1. Excess-0 kernel: no formal proof of non-vanishing.
  2. Excess-1,2,3 non-chain kernel necklaces: factor-cascade data is clean
     but symbolic proof not found.

The missing formal proof for both components is:
  "No primitive non-all-2 word can satisfy Q_w(z_D) = 0 mod q for
   every prime-power wall q of D."
```
