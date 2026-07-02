# Lock 1 Factor Cascade Barrier

Date: 2026-05-25

## Purpose

This is the current Lock 1 obstruction surface.

It does not forward-solve Collatz or search for long orbits. It works directly
on the loop-closing equation:

```text
3^k x + B_w = 2^A x
```

so a loop requires:

```text
B_w = (2^A - 3^k)x
```

Define:

```text
D = 2^A - 3^k
```

Then a nontrivial loop exists only if:

```text
D > 0
D | B_w
w is not the all-2 word
```

Therefore every prime-power factor of `D` is a required return-lattice gate.

## Cascade Definition

Let:

```text
D = q_1 q_2 ... q_r
```

where each `q_i` is a prime power and the `q_i` are pairwise coprime.

For fixed `(k,A,D)`, define:

```text
S_0 = all non-all-2 exponent words w of length k and total A
```

and recursively:

```text
S_i = { w in S_{i-1} : B_w == 0 mod q_i }
```

A nontrivial loop word exists exactly when:

```text
S_r is nonempty
```

because the Chinese remainder theorem gives:

```text
B_w == 0 mod D
iff
B_w == 0 mod q_i for every i
```

So the Lock 1 barrier can be stated as:

```text
For every contractive class (k,A), the factor cascade empties before or at
the final prime-power wall:

S_r = empty.
```

The all-2 heartbeat is excluded from `S_0`; it is the trivial `x=1` return.

## Implemented Cascade Miner

Implemented:

```text
rust/lock1_factor_cascade_miner.rs
```

Manifest target:

```text
lock1_factor_cascade_miner
```

Current run:

```text
data/runs/lock1_factor_cascade_k8_t30
```

Summary:

```text
classes=187
factor_layers=414
zero_residue_classes=0
max_final_survivor_words=0
```

This means every tested contractive `(k,A)` class emptied its non-all-2
cascade before surviving the full return lattice.

## Example Cascades

### Class `(k=6,A=10)`

```text
D = 2^10 - 3^6 = 295 = 5 * 59
non_all2_words = 126
```

Cascade:

```text
mod 5:  space=126, blocked=90, survivors=36
mod 59: space=36,  blocked=36, survivors=0
```

### Class `(k=8,A=13)`

```text
D = 2^13 - 3^8 = 1631 = 7 * 233
non_all2_words = 792
```

Cascade:

```text
mod 7:   space=792, blocked=672, survivors=120
mod 233: space=120, blocked=120, survivors=0
```

### Class `(k=8,A=30)`

```text
D = 2^30 - 3^8 = 1073735263 = 107 * 307 * 32687
non_all2_words = 1560780
```

Cascade:

```text
mod 107:   space=1560780, blocked=1546048, survivors=14732
mod 307:   space=14732,   blocked=14352,   survivors=380
mod 32687: space=380,     blocked=380,     survivors=0
```

The closest final-wall miss is:

```text
mod 32687: closest_nonzero_distance=5
closest_nonzero_residue=32682
closest_nonzero_word=2 7 1 5 2 7 1 5
```

The second wall exposes repeated structured survivors such as:

```text
1 1 1 12 1 1 1 12
1 1 2 11 1 1 2 11
1 1 3 10 1 1 3 10
1 1 4 9 1 1 4 9
1 1 5 8 1 1 5 8
```

This is the useful signal: the survivors are not random orbit hits. They are
structured residue survivors inside the return-lattice obstruction.

## Formal Target

The cascade reduces Lock 1 to a sharper theorem:

```text
For every k >= 1 and every A with 2^A > 3^k, if S_0 is the set of primitive
non-all-2 positive exponent words of length k and total A, then the factor
cascade defined by D = 2^A - 3^k satisfies S_r = empty.
```

Equivalently:

```text
No primitive non-all-2 word can satisfy B_w == 0 mod every prime-power factor
of D.
```

The next proof step is not a larger scan. It is a symbolic survivor-bound:

```text
|S_i| decays under the prime-power walls of D until |S_r| = 0.
```

That is the Lock 1 barrier theorem in factor-cascade form.

## Periodic-Word Reduction

Completed lemma:

```text
LOCK1_PERIODIC_REDUCTION_LEMMA.md
```

If a word is a repetition:

```text
w = v^r
```

then:

```text
B_w = B_v R
D_w = D_v R
```

with:

```text
R = sum_{t=0}^{r-1} 3^(m(r-1-t)) 2^(St)
```

where `m` is the length of `v` and `S` is the total exponent of `v`.

Therefore:

```text
D_w | B_w iff D_v | B_v
```

So imprimitive words cannot produce a new loop. They reduce to their primitive
root.

Current survivor dumps:

```text
data/runs/lock1_survivor_dump_k8_a30
pre_final_candidates=380
period_counts=4:364;8:16
rotation_classes=93
zero_final_residue=0
```

The 364 period-4 survivors are explained by the repetition cofactor. The
remaining 16 primitive period-8 survivors form two rotation classes, and still
miss the final wall.

## Rotation Reduction

Completed lemma:

```text
LOCK1_ROTATION_REDUCTION_LEMMA.md
```

If a word splits as `w=uv`, then:

```text
2^S B_vu == 3^m B_uv mod D
```

where `S` and `m` are the total exponent and length of `u`.

Since every prime-power wall `q_i | D` is odd and coprime to `2^S 3^m`:

```text
q_i | B_uv iff q_i | B_vu
```

So factor-cascade survival is invariant under cyclic rotation.

Current primitive-necklace artifact:

```text
data/runs/lock1_primitive_necklace_cascade_k8_t30
classes=187
primitive_necklaces=1157937
final_survivor_classes=0
max_final_survivor_necklaces=0
```

For `(k=8,A=30)`, the quotient cascade is:

```text
mod 107:   195052 -> 1796
mod 307:   1796   -> 2
mod 32687: 2      -> 0
```

Thus the active barrier target is now primitive necklaces, not raw words.

## Normalized Obstruction Polynomial

The active algebraic object is written in:

```text
LOCK1_NORMALIZED_OBSTRUCTION_POLYNOMIAL.md
```

For each wall `q | D`, define:

```text
z_q = 4 * 3^(-1) mod q
E_j = A_j - 2j
```

Then:

```text
q | B_w
iff
sum_j 2^E_j z_q^j == 0 mod q
```

or, after clearing negative deviations by a unit power of `2`:

```text
Q_w(z_q) == 0 mod q
```

The remaining theorem is that no primitive non-all-2 necklace can satisfy this
polynomial obstruction for every prime-power wall of `D`.

## Final Wall Quotient

The final wall theorem surface is written in:

```text
LOCK1_FINAL_WALL_THEOREM.md
```

Let:

```text
D = Mq
```

where `q` is the final prime-power wall and `M` is the product of all previous
walls. If a primitive necklace survives the previous walls, then:

```text
M | B_w
```

so:

```text
C_w = B_w / M
```

The final wall closes a loop exactly when:

```text
q | C_w
```

Current artifact:

```text
data/runs/lock1_final_wall_quotient_k8_t30
final_hit_classes=0
max_pre_final_necklaces=6197
max_quotient_windows=10
```
