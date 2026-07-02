# Lock 1 Normalized Obstruction Polynomial

Date: 2026-05-25

## Purpose

This is the algebraic object left after the Lock 1 reductions:

```text
raw words
-> periodic reduction
-> rotation quotient
-> primitive necklaces
```

For each prime-power wall `q | D`, loop closure is equivalent to one normalized
polynomial vanishing modulo `q`.

## Definitions

For a word:

```text
w = (a_0, ..., a_{k-1})
```

define prefix sums:

```text
A_j = a_0 + ... + a_{j-1}
A_0 = 0
A = A_k
```

and the Lock 1 offset:

```text
B_w = sum_{j=0}^{k-1} 3^(k-1-j) 2^A_j
```

Let:

```text
D = 2^A - 3^k
```

For any prime-power wall:

```text
q | D
```

we have:

```text
2^A == 3^k mod q
```

and `2` and `3` are units modulo `q`.

## Normalization

Multiply `B_w` by the unit `3^(1-k)` modulo `q`:

```text
B_w == 0 mod q
iff
sum_{j=0}^{k-1} 2^A_j 3^(-j) == 0 mod q
```

Write deviations from the heartbeat as:

```text
e_j = a_j - 2
E_j = A_j - 2j
E = A - 2k
```

Define:

```text
z_q = 4 * 3^(-1) mod q
```

Then:

```text
2^A_j 3^(-j)
= 2^(2j + E_j) 3^(-j)
= 2^E_j (4/3)^j
= 2^E_j z_q^j
```

So the wall obstruction is:

```text
P_w(z_q) = sum_{j=0}^{k-1} 2^E_j z_q^j
```

and:

```text
q | B_w
iff
P_w(z_q) == 0 mod q
```

If some `E_j` are negative, multiply by:

```text
2^h, h = -min_j E_j
```

which is also a unit modulo odd `q`. The integer-coefficient form is:

```text
Q_w(z_q) = sum_{j=0}^{k-1} 2^(E_j+h) z_q^j
```

with:

```text
q | B_w
iff
Q_w(z_q) == 0 mod q
```

## Closure Constraint

Because `q | D`:

```text
2^A == 3^k mod q
```

Using `A = 2k + E`, this becomes:

```text
2^E z_q^k == 1 mod q
```

So a wall is not arbitrary. A primitive necklace must solve:

```text
Q_w(z_q) == 0 mod q
2^E z_q^k == 1 mod q
```

for each prime-power wall `q | D`.

## Rotation Compatibility

The rotation lemma says a cyclic shift multiplies the obstruction by a unit.
In polynomial form, rotation changes the base point of the cyclic prefix path,
but preserves whether:

```text
Q_w(z_q) == 0 mod q
```

Therefore the polynomial is naturally attached to primitive necklaces, not to
raw words.

## Factor Cascade Form

Let:

```text
D = q_1 ... q_r
```

The primitive-necklace cascade is now:

```text
S_0 = primitive non-all-2 necklaces
S_i = { w in S_{i-1} : Q_w(z_{q_i}) == 0 mod q_i }
```

The remaining Lock 1 theorem is:

```text
S_r = empty
```

for every contractive class.

## Concrete Surfaces

### Class `(k=8,A=30)`

```text
D = 1073735263 = 107 * 307 * 32687
E = A - 2k = 14
```

Primitive-necklace cascade:

```text
mod 107:   195052 -> 1796
mod 307:   1796   -> 2
mod 32687: 2      -> 0
```

The two pre-final primitive necklaces are:

```text
1 2 2 5 12 4 1 3
1 2 2 7 10 3 3 2
```

They solve the first two wall polynomials and fail the final wall polynomial.

### Class `(k=8,A=25)`

```text
D = 33547871 = 7 * 4792553
E = A - 2k = 9
```

Primitive-necklace cascade:

```text
mod 7:       43263 -> 6197
mod 4792553: 6197   -> 0
```

The first wall is:

```text
z_7 = 4 * 3^(-1) == -1 mod 7
```

so the first obstruction reduces to the alternating deviation sum:

```text
Q_w(-1) == 0 mod 7
```

The huge final wall kills every primitive necklace that survives that
alternating condition.

## Current Proof Target

The remaining proof is no longer about raw Collatz trajectories.

It is:

```text
For every contractive pair (k,A), no primitive non-all-2 necklace can make
Q_w(z_q) vanish for every prime-power wall q | (2^A - 3^k).
```

That is the normalized primitive-necklace obstruction.

## Verification

The normalized identity:

```text
2^h 3^(1-k) B_w == Q_w(z_q) mod q
```

was checked against the direct offset recurrence over sampled words for:

```text
k <= 8
A <= 30
checked cases = 57067
failures = 0
```
