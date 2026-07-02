# Lock 1 Critical Band Kernel

Date: 2026-05-25

## Result

The rotation-window lemma does not leave a random residue problem, but the
first `k<=10` critical-band interpretation was too narrow.

The initial expanded quotient surface:

```text
k <= 10
A <= 30
```

had every unresolved primitive necklace in the near-critical band:

```text
A = ceil(k log2 3)
```

or:

```text
A = ceil(k log2 3) + 1
```

But a later bounded run:

```text
k <= 12
A <= 22
```

found additional unresolved classes at excess `+2` and `+3`.

Therefore the live theorem is not "critical band only." The live theorem is:

```text
Prove a structural bound showing exactly when rotation-window kill must occur,
and prove final-residue exclusion for the remaining bounded-excess kernel.
```

## Current Artifact

```text
data/runs/lock1_final_wall_quotient_k10_t30
```

Summary:

```text
classes=217
pre_final_classes=151
final_hit_classes=0
rotation_window_unresolved_classes=13
rotation_window_proved_necklaces=64726
rotation_window_unresolved_necklaces=645
max_pre_final_necklaces=16796
max_quotient_windows=25
```

The unresolved kernel file is:

```text
data/runs/lock1_final_wall_quotient_k10_t30/lock1_rotation_window_unresolved_kernel.csv
```

It contains:

```text
kernel rows = 645
zero final residues = 0
```

## Kernel Classes In `k10_t30`

```text
k=3,  A=5,  excess=0, q=5,     unresolved=2
k=4,  A=7,  excess=0, q=47,    unresolved=5
k=5,  A=8,  excess=0, q=13,    unresolved=7
k=5,  A=9,  excess=1, q=269,   unresolved=10
k=6,  A=10, excess=0, q=59,    unresolved=6
k=6,  A=11, excess=1, q=1319,  unresolved=14
k=7,  A=12, excess=0, q=83,    unresolved=2
k=7,  A=13, excess=1, q=1201,  unresolved=3
k=8,  A=13, excess=0, q=233,   unresolved=15
k=9,  A=15, excess=0, q=2617,  unresolved=56
k=9,  A=16, excess=1, q=45853, unresolved=325
k=10, A=16, excess=0, q=499,   unresolved=41
k=10, A=17, excess=1, q=10289, unresolved=159
```

## Corrective Run

Artifact:

```text
data/runs/lock1_final_wall_quotient_k12_t22
```

Summary:

```text
classes=145
pre_final_classes=109
final_hit_classes=0
rotation_window_unresolved_classes=19
rotation_window_proved_necklaces=41796
rotation_window_unresolved_necklaces=3846
```

New kernel classes beyond the original critical bands:

```text
k=11, A=20, excess=2, q=67033,  unresolved=59
k=11, A=21, excess=3, q=384001, unresolved=3
```

So the previous `excess <= 1` statement is false as a general claim.

## Interpretation

The final Lock 1 proof is now split into two theorems:

### Theorem A: Rotation-Window Kill

Find and prove the correct threshold under which every primitive non-all-2
necklace has:

```text
0 < B_rho(w) < D
```

for some cyclic rotation `rho`.

The `k10_t30` data suggested this might begin at excess `+2`, but `k12_t22`
disproved that.

### Theorem B: Kernel Exclusion

For every survivor not killed by rotation-window, prove:

```text
C_w != 0 mod q
```

The current kernel remains residue-clean:

```text
final_hit_classes=0
```

## Current Status

This is not a completed proof yet.

The final missing step is not vague:

```text
Prove bounded-excess kernel exclusion, with the correct rotation-window
threshold.
```

Everything else has been reduced to that statement.
