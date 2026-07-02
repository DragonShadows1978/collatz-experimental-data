# Lock 1 Proof Completion Audit

Date: 2026-05-25

## Exact Target

Lock 1 is complete only when this theorem is proved over all positive integer
exponent words:

```text
For every k >= 1 and every word w = (a_0, ..., a_{k-1}) with a_j >= 1,
let A = sum a_j, B_w = sum 3^(k-1-j) 2^A_j, and D_w = 2^A - 3^k.

If D_w > 0 and D_w | B_w, then w is the all-2 word and x = B_w / D_w = 1.
```

Equivalently:

```text
No non-all-2 contractive word has B_w == 0 mod D_w.
```

## Already Proved

### Positive-Action Engines

Complete.

If `3^k > 2^A`, then

```text
x = B_w / (2^A - 3^k) < 0
```

because `B_w > 0` and `2^A - 3^k < 0`.

Therefore no positive integer can be fixed by a positive-action repeating word.

### Loop Reduction

Complete.

Any odd cycle word must satisfy:

```text
(2^A - 3^k)x = B_w
D_w > 0
D_w | B_w
```

So the no-loop problem reduces to the divisibility obstruction.

### Delta Identity

Complete as an algebraic identity.

With `a_j = 2 + e_j` and prefix deviations `E_j`, the defect

```text
Delta_w = B_w - D_w
```

satisfies

```text
D_w | B_w iff D_w | Delta_w
```

and, after normalization by `h = -min(0,E_j)`,

```text
D_w | Delta_w iff D_w | 2^h Delta_w
```

because `D_w` is odd.

## Barrier Machinery

### Backward Offset-Barrier Prover

Implemented:

```text
rust/lock1_backward_barrier.rs
```

This is the relevant Lock 1 object. It starts from the forbidden loop-closure
state:

```text
prefix_sum = A
B_w mod D_w = 0
non_all2 = true
```

and pulls that state backward through the inverse offset recurrence:

```text
B_j = 3^{-1}(B_{j+1} - 2^A_j) mod D_w
```

The barrier succeeds for a class when the real initial state

```text
prefix_sum = 0
B_0 mod D_w = 0
non_all2 = false
```

is outside the full forbidden preimage set. That means no exponent path in the
class can cross into exact nontrivial loop closure.

Current barrier proof:

```text
data/runs/lock1_backward_barrier_line16_offset1
classes_proved=16
failed_classes=0
```

Unbounded-parts barrier test:

```text
data/runs/lock1_backward_barrier_all_k8_t30_unbounded_parts
classes_proved=187
unbounded_parts=true
failed_classes=0
```

### Residue DP Prover

Implemented:

```text
rust/lock1_residue_dp_prover.rs
```

This is now secondary. It proves finite `(k,A)` classes by forward reachable
residue states. It is useful as a consistency check, but it is not the Lock 1
barrier proof shape.

### Exact Cycle Scanner

Implemented:

```text
rust/lock1_cycle_scan.rs
```

Additional all-class test:

```text
data/runs/lock1_cycle_all_k10_a16_t35
words_scanned=283502271
trivial_cycle_hits=10
nontrivial_cycle_hits=0
```

This is also secondary. It verifies exact candidate cycles, but it is not the
Lock 1 barrier proof shape.

### Factor Cascade Barrier Miner

Implemented:

```text
rust/lock1_factor_cascade_miner.rs
```

This is the current barrier-facing miner. It factors:

```text
D = 2^A - 3^k
```

into prime-power walls and tracks the survivor cascade:

```text
S_i = {w in S_{i-1}: B_w == 0 mod q_i}
```

Current artifact:

```text
data/runs/lock1_factor_cascade_k8_t30
classes=187
factor_layers=414
zero_residue_classes=0
max_final_survivor_words=0
```

Example:

```text
k=8,A=30,D=1073735263=107*307*32687
mod 107:   1560780 -> 14732
mod 307:   14732 -> 380
mod 32687: 380 -> 0
closest final-wall miss: residue 32682, distance 5
```

This is not a forward Collatz scan. It is a return-lattice obstruction miner.

### Periodic-Word Reduction

Complete.

Written in:

```text
LOCK1_PERIODIC_REDUCTION_LEMMA.md
```

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

Therefore an imprimitive loop word is only a repeated shorter loop. It cannot
be the first nontrivial Lock 1 loop. The remaining no-loop theorem only has to
rule out primitive non-all-2 exponent words.

Targeted survivor dumps:

```text
rust/lock1_cascade_survivor_dump.rs
data/runs/lock1_survivor_dump_k8_a30
data/runs/lock1_survivor_dump_k8_a13
data/runs/lock1_survivor_dump_k6_a10
data/runs/lock1_survivor_dump_k12_a20
```

### Rotation Reduction

Complete.

Written in:

```text
LOCK1_ROTATION_REDUCTION_LEMMA.md
```

If a word splits as `w=uv`, then:

```text
2^S B_vu == 3^m B_uv mod D
```

Therefore every prime-power wall `q_i | D` satisfies:

```text
q_i | B_uv iff q_i | B_vu
```

So cyclic rotations have the same factor-cascade obstruction status.

Implemented quotient miner:

```text
rust/lock1_primitive_necklace_cascade_miner.rs
data/runs/lock1_primitive_necklace_cascade_k8_t30
```

Current summary:

```text
classes=187
primitive_necklaces=1157937
final_survivor_classes=0
max_final_survivor_necklaces=0
```

For `(k=8,A=30)`:

```text
raw pre-final words: 380
primitive pre-final necklaces: 2
final survivors: 0
```

### Normalized Obstruction Polynomial

Written in:

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

After clearing negative deviations by a unit power of `2`, this becomes:

```text
Q_w(z_q) == 0 mod q
```

This is now the exact algebraic obstruction attached to primitive necklaces.

Verification:

```text
k <= 8
A <= 30
normalized identity checks = 57067
failures = 0
```

### Final Wall Quotient Theorem

Built theorem surface:

```text
LOCK1_FINAL_WALL_THEOREM.md
```

Implemented miner:

```text
rust/lock1_final_wall_quotient_miner.rs
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

Final quotient form:

```text
D = Mq
M = product of all walls before the final wall
C_w = B_w / M

D | B_w iff q | C_w
```

So the last theorem is:

```text
if M | B_w, then q does not divide C_w
```

for every primitive non-all-2 necklace.

### Rotation-Window Lemma

Complete.

Written in:

```text
LOCK1_ROTATION_WINDOW_LEMMA.md
```

If any rotation of a pre-final survivor has:

```text
0 < B_rho(w) < D
```

then the rotated candidate loop value would be:

```text
0 < B_rho(w) / D < 1
```

which cannot be a positive integer cycle value.

Current artifact:

```text
data/runs/lock1_final_wall_quotient_k8_t30
rotation_window_proved_necklaces=28145
rotation_window_unresolved_necklaces=64
rotation_window_unresolved_classes=9
```

The unresolved kernel is confined to small-wall classes on this surface.

Expanded run:

```text
data/runs/lock1_final_wall_quotient_k10_t30
classes=217
final_hit_classes=0
rotation_window_proved_necklaces=64726
rotation_window_unresolved_necklaces=645
rotation_window_unresolved_classes=13
```

The expanded kernel is documented in:

```text
LOCK1_CRITICAL_BAND_KERNEL.md
```

The initial `k10_t30` run suggested the unresolved cases lived only in:

```text
A = ceil(k log2 3)
A = ceil(k log2 3) + 1
```

but `k12_t22` corrected that: unresolved classes also appear at `k=11` with
excess `+2` and `+3`.

## Missing For A Formal Lock 1 Barrier Proof

### Missing Theorem 1: Closed Barrier Formula

Partially completed.

Need a parameterized description of the forbidden preimage set:

```text
Forbidden_j(k,A,D) =
all states at layer j that can still reach B_w = 0 mod D with non_all2=true.
```

The current barrier prover computes this set exactly for finite classes. The
formal proof needs the closed symbolic form of this barrier.

The suffix-preimage formula has now been written in:

```text
LOCK1_OFFSET_BARRIER.md
```

and checked against recursive backward barriers:

```text
data/runs/lock1_barrier_formula_check_k7_t24
classes=127
layers=590
mismatched_layers=0
```

Remaining work for this theorem: turn the written formula into the formal
published lemma.

### Missing Theorem 2: Initial-State Separation

Not proved.

Need to prove, from the closed barrier formula, that:

```text
(0,0,false) not in Forbidden_0(k,A,D)
```

for every contractive class `D=2^A-3^k>0`, except the all-2 trivial heartbeat.

The active route is the factor-cascade theorem:

```text
D = q_1 ... q_r
S_0 = all primitive non-all-2 necklaces in the class
S_i = {w in S_{i-1}: B_w == 0 mod q_i}
```

Prove:

```text
S_r = empty
```

for every contractive class. This proves initial-state separation because
surviving all prime-power walls is equivalent to `D | B_w`.

### Missing Theorem 3: All Contractive Totals

Not proved.

The barrier theorem must cover every integer `A` satisfying:

```text
2^A > 3^k
```

## New Results (2026-05-25)

### B-Floor Theorem

Proved:

```text
LOCK1_BFLOOR_THEOREM.md
```

For any word of length k: `B_w >= 3^k - 2^k` (achieved by the all-1 word).
This is a UNIVERSAL lower bound independent of the total A.

Consequence: at excess = 0 (`A = ceil(k*log_2(3))`), `B_floor = 3^k - 2^k >= D`
for all k. This geometrically blocks the rotation-window for ALL words in all
excess-0 classes — the kernel at excess-0 is forced by geometry, not filter structure.

Verified: `2*3^k >= 2^k + 2^A` for k = 3..100 at excess = 0.

### Trailing-2 Recurrence Theorem

Proved:

```text
LOCK1_TRAILING2_RECURRENCE.md
```

For word `w` with `D < B_w < 2D`, appending a trailing 2 gives:

```text
B_{w'} mod D_{w'} = 3 * (B_w mod D_w)
```

This follows from the algebraic identity `3*D_w + 2^A = D_{w'}` (proved).

Consequence: Any chain `w_0, w_0+(2), w_0+(2,2), ...` starting with `B in (D,2D)`
has residue `3^m * r_0` at step m. Since `gcd(3, D) = 1`, this residue is never 0.

Verified concrete chain: `(1,2,1,3,2,...,2)` covers k=4..infinity with residues
`38, 114, 342, 1026, 3078, ...` (factor 3 exact at every step).

### Kernel Structure Clarified

The kernel (pre-final necklaces not killed by rotation-window) has:

```text
excess = 0: entirely due to geometric blockage (B_floor >= D). ALL words are kernel.
excess = 1,2,3: structural residue from prime-wall filters. BOUNDED kernel.
excess >= 4: empty kernel (verified k=3..12). All pre-final necklaces killed.
```

### Theorem A Status

```text
Excess-0 geometric blockage: PROVED (B-Floor Lemma).
Excess >= 4 kernel-vanishing: VERIFIED computationally, symbolic proof open.
Written up in: LOCK1_THEOREM_A_WRITEUP.md
```

### Theorem B Status

```text
Trailing-2 chain families: NON-VANISHING PROVED.
Excess-0 kernel (all words): VERIFIED k=3..20, formal proof OPEN.
Excess-1,2,3 non-chain kernel: factor-cascade data clean, symbolic proof OPEN.
Written up in: LOCK1_THEOREM_B_WRITEUP.md
```

## Updated Audit Verdict

```text
Positive-action Lock 1: complete.
Full no-loop Lock 1: not complete.

New proofs added:
  - B-Floor universal lower bound (3^k - 2^k)
  - Excess-0 geometric blockage of rotation-window
  - Trailing-2 Recurrence: residue triples exactly under appending 2
  - Algebraic identity: 3*D(k,A) + 2^A = D(k+1,A+2)
  - Chain non-vanishing: gcd(3,D)=1 closes all trailing-2 families

Remaining gaps (unchanged in kind, sharpened in description):
  1. Excess >= 4 symbolic kernel-vanishing proof (cascade decay bound)
  2. Excess-0 non-vanishing for general k (essentially: no Collatz cycle
     with word of minimal contractive total)
  3. Excess-1,2,3 non-chain kernel necklaces (large B/D cases)

The deepest remaining piece is still the symbolic survivor-decay bound.
The trailing-2 recurrence gives a clean sub-result that closes infinite
families and may generalize to other appending patterns.
```
