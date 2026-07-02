# Lock 1 Rotation Reduction Lemma

Date: 2026-05-25

## Claim

Cyclic rotations of an exponent word have the same Lock 1 obstruction status.

Therefore the primitive Lock 1 search space is not raw primitive words. It is
primitive necklaces: primitive words modulo cyclic rotation.

## Split Formula

Let a word split as:

```text
w = uv
```

where `u` has:

```text
length m
total exponent S
offset B_u
```

and `v` has:

```text
length n
total exponent T
offset B_v
```

The full word has:

```text
k = m+n
A = S+T
D = 2^A - 3^k
```

Appending `v` after `u` gives:

```text
B_uv = 3^n B_u + 2^S B_v
```

Rotating gives:

```text
B_vu = 3^m B_v + 2^T B_u
```

## Rotation Congruence

Multiply the rotated offset by `2^S`:

```text
2^S B_vu
= 2^S 3^m B_v + 2^(S+T) B_u
```

Use:

```text
D = 2^(S+T) - 3^(m+n)
```

and:

```text
B_uv = 3^n B_u + 2^S B_v
```

Then:

```text
2^S B_vu
= 3^m B_uv + D B_u
```

So modulo `D`:

```text
2^S B_vu == 3^m B_uv mod D
```

Since `D` is odd:

```text
gcd(2^S,D)=1
gcd(3^m,D)=1
```

Therefore:

```text
D | B_uv iff D | B_vu
```

The same argument holds modulo every prime-power wall `q_i | D`:

```text
q_i | B_uv iff q_i | B_vu
```

Thus every factor-cascade wall is rotation-invariant.

## Consequence

If any cyclic rotation of a primitive word survives every wall, every rotation
has the same obstruction status. A possible loop is a cycle object, not a
chosen starting slot.

So Lock 1 can quotient:

```text
primitive words
```

down to:

```text
primitive necklaces
```

without losing any possible nontrivial loop.

## Implemented Necklace Miner

Implemented:

```text
rust/lock1_primitive_necklace_cascade_miner.rs
```

Current artifact:

```text
data/runs/lock1_primitive_necklace_cascade_k8_t30
```

Summary:

```text
classes=187
classes_with_primitive_necklaces=186
primitive_necklaces=1157937
final_survivor_classes=0
max_final_survivor_necklaces=0
```

For the high-signal class:

```text
k=8,A=30
D = 1073735263 = 107 * 307 * 32687
```

the primitive-necklace cascade is:

```text
mod 107:   195052 -> 1796
mod 307:   1796   -> 2
mod 32687: 2      -> 0
```

The two pre-final primitive necklaces are represented by:

```text
1 2 2 5 12 4 1 3
1 2 2 7 10 3 3 2
```

Both miss the final wall. The closest representative has:

```text
residue mod 32687 = 10658
distance from zero = 10658
```

So the quotient chain for Lock 1 is now:

```text
all words
-> remove repetitions by periodic reduction
-> quotient rotations by rotation reduction
-> prove primitive-necklace cascade empties
```
