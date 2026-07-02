# Lock 1 Offset Barrier

## Barrier Equation

A loop is not merely a path returning to a previous value. Algebraically, after
`k` odd steps it requires:

```text
3^k x + B_w = 2^A x
```

Therefore:

```text
B_w = (2^A - 3^k)x
```

Define:

```text
D_w = 2^A - 3^k
```

The nontrivial loop condition is exactly:

```text
D_w > 0
D_w | B_w
x = B_w / D_w > 1
```

So the Lock 1 blocker is the offset barrier:

```text
B_w cannot enter the exact return lattice D_w * Z
```

except for the all-2 heartbeat, where:

```text
B_w = D_w
x = 1
```

## Backward Barrier Object

The correct proof object is the forbidden preimage set, not forward
enumeration.

For fixed `k,A,D`, define:

```text
Forbidden_j(k,A,D)
```

as the set of states at layer `j` that can still reach the forbidden final
condition:

```text
prefix_sum = A
B_w mod D = 0
non_all2 = true
```

The backward recurrence is:

```text
B_j = 3^{-1}(B_{j+1} - 2^A_j) mod D
```

because:

```text
B_{j+1} = 3B_j + 2^A_j mod D
```

The barrier proof must show:

```text
(prefix_sum=0, B_0=0, non_all2=false) not in Forbidden_0(k,A,D)
```

for every contractive class:

```text
D = 2^A - 3^k > 0
```

except the all-2 heartbeat.

## Suffix-Preimage Formula

The backward barrier has a closed layer description.

Fix a class `(k,A)` with:

```text
D = 2^A - 3^k > 0
```

At layer `j`, let:

```text
s = A_j
n = k - j
T = A - s
```

Let `v = (b_0, ..., b_{n-1})` be a suffix word of length `n` and total `T`.
Define its local offset:

```text
C_v = sum_{i=0}^{n-1} 3^(n-1-i) 2^(b_0 + ... + b_{i-1})
```

Then appending this suffix to a layer-`j` state gives:

```text
B_k = 3^n B_j + 2^s C_v
```

Therefore the suffix reaches the forbidden return lattice `B_k == 0 mod D`
exactly when:

```text
B_j == -3^(-n) 2^s C_v mod D
```

So the forbidden layer is:

```text
Forbidden_j(k,A,D)
= {
    (s, -3^(-n) 2^s C_v mod D, u)
    where v has length n and total A-s,
    and u is compatible with whether the prefix or suffix is non-all2
  }
```

The boolean rule is:

```text
if suffix v is non-all2:
    u can be false or true
if suffix v is all2:
    u must be true
```

because the final forbidden state requires the whole word to be non-all2.

Thus the formal Lock 1 blocker reduces to the layer-0 specialization:

```text
Forbidden_0(k,A,D)
= {
    (0, -3^(-k) C_w mod D, false)
    for non-all2 full words w of length k and total A
  }
```

The true initial state is forbidden exactly when:

```text
-3^(-k) C_w == 0 mod D
```

Since `gcd(3,D)=1`, this is equivalent to:

```text
C_w == 0 mod D
```

and `C_w` is exactly `B_w`. Therefore:

```text
initial state in Forbidden_0
iff
D | B_w for some non-all2 word w
```

This gives the exact barrier formulation with no forward orbit enumeration.

## Implemented Barrier Probe

Implemented:

```text
rust/lock1_backward_barrier.rs
```

The probe computes `Forbidden_j` backward for finite classes and checks whether
the real initial state lies outside the forbidden preimage.

Current line proof surface:

```text
data/runs/lock1_backward_barrier_line16_offset1
classes_proved=16
failed_classes=0
```

Unbounded-parts proof surface:

```text
data/runs/lock1_backward_barrier_all_k8_t30_unbounded_parts
classes_proved=187
unbounded_parts=true
failed_classes=0
```

Formula check:

```text
data/runs/lock1_barrier_formula_check_k7_t24
classes=127
layers=590
mismatched_layers=0
```

The formula checker compares the recursive backward barrier against the closed
suffix-preimage formula above.

Factor cascade:

```text
rust/lock1_factor_cascade_miner.rs
data/runs/lock1_factor_cascade_k8_t30
classes=187
factor_layers=414
zero_residue_classes=0
max_final_survivor_words=0
```

This treats each prime-power factor of:

```text
D = 2^A - 3^k
```

as a required return-lattice wall. A nontrivial loop survives exactly when a
non-all-2 word survives every wall. In the current run, every tested cascade
empties by the final wall.

## Remaining Formal Step

The finite barrier probe and formula checker are not the final proof. They
expose and validate the proof object.

The remaining theorem is now sharper:

```text
For every non-all2 full word w of length k and total A,
B_w is nonzero modulo D = 2^A - 3^k.
```

Equivalently, prove that the layer-0 suffix-preimage formula never contains
`(0,0,false)` except for the all-2 heartbeat.

The active sharpening is now the factor-cascade form:

```text
If D = q_1 ... q_r is the prime-power factorization of D, and
S_i = {w in S_{i-1}: B_w == 0 mod q_i}, then S_r is empty for every primitive
non-all-2 contractive class.
```

Periodic words are already reduced by:

```text
LOCK1_PERIODIC_REDUCTION_LEMMA.md
```

Rotations are already quotiented by:

```text
LOCK1_ROTATION_REDUCTION_LEMMA.md
```

The wall obstruction is normalized by:

```text
LOCK1_NORMALIZED_OBSTRUCTION_POLYNOMIAL.md
```

The final wall is isolated by:

```text
LOCK1_FINAL_WALL_THEOREM.md
```

The final wall is mostly killed by:

```text
LOCK1_ROTATION_WINDOW_LEMMA.md
```

The remaining kernel is localized by:

```text
LOCK1_CRITICAL_BAND_KERNEL.md
```

That is the Lock 1 barrier theorem.
