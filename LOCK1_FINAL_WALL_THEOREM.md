# Lock 1 Final Wall Theorem

Date: 2026-05-25

## Theorem Target

Let:

```text
w = (a_0, ..., a_{k-1})
a_i >= 1
A = sum a_i
B_w = sum_{j=0}^{k-1} 3^(k-1-j) 2^A_j
D = 2^A - 3^k
```

Assume:

```text
D > 0
w is primitive
w is not the all-2 heartbeat
w is taken modulo cyclic rotation
```

Factor:

```text
D = q_1 q_2 ... q_r
```

where each `q_i` is a pairwise coprime prime power.

Define:

```text
M = q_1 q_2 ... q_(r-1)
q = q_r
```

The final wall theorem is:

```text
If M | B_w, then q does not divide B_w / M.
```

Equivalently:

```text
No primitive non-all-2 necklace can survive every prime-power wall of D.
```

This is exactly:

```text
D does not divide B_w
```

for every primitive non-all-2 necklace.

## Completed Reductions

### 1. Loop Equation

Any odd cycle word must satisfy:

```text
3^k x + B_w = 2^A x
```

so:

```text
D x = B_w
D = 2^A - 3^k
```

Thus a nontrivial positive loop requires:

```text
D > 0
D | B_w
x = B_w / D > 1
```

### 2. Positive-Action Words

If:

```text
D < 0
```

then:

```text
x = B_w / D < 0
```

because `B_w > 0`. So positive-action words cannot close a positive loop.

### 3. Periodic Reduction

If:

```text
w = v^r
```

then:

```text
B_w = B_v R
D_w = D_v R
```

so:

```text
D_w | B_w iff D_v | B_v
```

Therefore an imprimitive word cannot be the first nontrivial loop.

Reference:

```text
LOCK1_PERIODIC_REDUCTION_LEMMA.md
```

### 4. Rotation Reduction

If:

```text
w = uv
```

and `vu` is the cyclic rotation, then:

```text
2^S B_vu == 3^m B_uv mod D
```

Since every wall `q_i | D` is odd:

```text
q_i | B_uv iff q_i | B_vu
```

Therefore factor-cascade survival is invariant under cyclic rotation.

Reference:

```text
LOCK1_ROTATION_REDUCTION_LEMMA.md
```

### 5. Normalized Wall Polynomial

For each wall:

```text
q | D
```

define:

```text
z_q = 4 * 3^(-1) mod q
E_j = A_j - 2j
```

After clearing negative deviations by a unit power of `2`:

```text
q | B_w iff Q_w(z_q) == 0 mod q
```

where:

```text
Q_w(z_q) = sum_j 2^(E_j+h) z_q^j
```

Reference:

```text
LOCK1_NORMALIZED_OBSTRUCTION_POLYNOMIAL.md
```

## Final Quotient Form

Once the first `r-1` walls are passed:

```text
M | B_w
```

so define the final quotient:

```text
C_w = B_w / M
```

Then:

```text
D | B_w
iff
q | C_w
```

because:

```text
D = Mq
```

The remaining nonvanishing lemma is:

```text
C_w is never 0 mod q
```

for primitive non-all-2 necklaces.

That is the final Lock 1 wall.

## Implemented Final-Wall Miner

Implemented:

```text
rust/lock1_final_wall_quotient_miner.rs
```

Current artifact:

```text
data/runs/lock1_final_wall_quotient_k8_t30
```

Summary:

```text
classes=186
pre_final_classes=121
final_hit_classes=0
max_pre_final_necklaces=6197
max_quotient_windows=10
```

The quotient window count means that, among all checked classes, the pre-final
quotients `C_w` occupy at most 10 integer intervals of length `q`. None lands
on a multiple of `q`.

## Concrete Surfaces

### `(k=8,A=30)`

```text
D = 1073735263 = 107 * 307 * 32687
M = 107 * 307 = 32849
q = 32687
```

Primitive-necklace cascade:

```text
mod 107:   195052 -> 1796
mod 307:   1796   -> 2
mod 32687: 2      -> 0
```

Final quotient surface:

```text
primitive_necklaces=195052
pre_final_necklaces=2
final_hits=0
C_min=11365
C_max=12389
quotient_windows=1
closest_final_distance=11365
```

So both final candidates lie inside one `q`-window and neither is zero.

### `(k=8,A=25)`

```text
D = 33547871 = 7 * 4792553
M = 7
q = 4792553
```

Primitive-necklace cascade:

```text
mod 7:       43263 -> 6197
mod 4792553: 6197 -> 0
```

Final quotient surface:

```text
primitive_necklaces=43263
pre_final_necklaces=6197
final_hits=0
C_min=919
C_max=7125359
quotient_windows=2
closest_final_distance=919
```

So the largest checked pre-final primitive-necklace class spans only two
`q`-windows and still misses every multiple of `q`.

## Proof Form To Complete

The full Lock 1 proof is now equivalent to this final nonvanishing theorem:

```text
For every contractive pair (k,A), every primitive non-all-2 necklace w,
and q the final prime-power wall of D=2^A-3^k:

if (D/q) | B_w, then B_w/(D/q) is not 0 mod q.
```

In normalized-polynomial language:

```text
Q_w(z_{q_i}) == 0 mod q_i for i < r
implies
Q_w(z_q) != 0 mod q.
```

This is the final algebraic theorem Lock 1 needs.

## Rotation-Window Lemma

Completed lemma:

```text
LOCK1_ROTATION_WINDOW_LEMMA.md
```

If a pre-final survivor has a cyclic rotation with:

```text
0 < B_rho(w) < D
```

then final closure is impossible because the rotated loop value would satisfy:

```text
0 < B_rho(w) / D < 1
```

In final-quotient form:

```text
0 < C_rho < q
```

Current measurement:

```text
rotation_window_proved_necklaces=28145
rotation_window_unresolved_necklaces=64
rotation_window_unresolved_classes=9
```

So the current final-wall theorem has split into:

```text
1. General rotation-window kill.
2. Small-wall kernel exclusion.
```

## Bounded-Excess Kernel

The expanded run:

```text
data/runs/lock1_final_wall_quotient_k10_t30
```

initially suggested that the unresolved kernel occurred only in:

```text
A = ceil(k log2 3)
A = ceil(k log2 3) + 1
```

on the checked surface.

Reference:

```text
LOCK1_CRITICAL_BAND_KERNEL.md
```

Current expanded summary:

```text
classes=217
final_hit_classes=0
rotation_window_proved_necklaces=64726
rotation_window_unresolved_necklaces=645
rotation_window_unresolved_classes=13
```

However, the bounded corrective run:

```text
data/runs/lock1_final_wall_quotient_k12_t22
```

found unresolved kernels at:

```text
k=11,A=20, excess=2
k=11,A=21, excess=3
```

with:

```text
final_hit_classes=0
```

So the final proof target is now:

```text
1. Prove the correct rotation-window threshold.
2. Prove C_w != 0 mod q for the remaining bounded-excess kernel.
```
