# Lock 1 No-Loop Proof

## Status

There are two different statements that have been called "Lock 1" in this folder.

The original Lock 1 statement from `lock1_periodic_engine_proof_and_python.txt` is complete:

```text
No positive-action repeating exponent word can have a positive fixed point.
```

That proof is short and final. If `3^k > 2^A`, then

```text
x = B_w / (2^A - 3^k) < 0
```

because `B_w > 0` and `2^A - 3^k < 0`. Therefore the only affine fixed point of a positive-action word is negative, so no positive integer can be powered forever by that repeating positive-action engine.

The stronger statement in this file is different:

```text
No positive integer cycle exists except the trivial cycle through 1.
```

That stronger statement also has to rule out contractive cycle words with

```text
2^A > 3^k
```

For those words the fixed point denominator is positive, so the negative-ghost argument does not apply. The obstruction must instead prove

```text
D_w ∤ B_w
```

for every non-all-2 exponent word with `D_w = 2^A - 3^k > 0`.

That is why the stronger no-loop proof is not officially closed yet: the generated factor-class certificates prove the obstruction over the scanned surface, but the universal residue lemma must still be written as an algebraic theorem over all words.

## Claim

The Collatz map has no positive integer cycle except the trivial cycle through `1`.

It is enough to prove this for odd cycle members. If a positive even integer belongs to a cycle, repeated division by `2` reaches an odd member of the same cycle. Therefore every positive cycle contains an odd cycle.

## Odd-Only Block

For an odd integer `x`, write one odd-only Collatz step as

```text
x -> (3x + 1) / 2^a
```

where `a = v_2(3x + 1)`.

For a word of exponents

```text
w = (a_0, a_1, ..., a_{k-1})
```

define prefix sums

```text
A_0 = 0
A_j = a_0 + ... + a_{j-1}
A = A_k
```

After `k` odd-only steps, the composed map has the form

```text
F_w(x) = (3^k x + B_w) / 2^A
```

where the accumulated `+1` offset is

```text
B_w = sum_{j=0}^{k-1} 3^(k-1-j) 2^A_j
```

Equivalently, the offset can be computed recursively:

```text
B_0 = 0
B_{j+1} = 3B_j + 2^A_j
```

## Cycle Equation

If the word `w` closes a loop, then

```text
F_w(x) = x
```

so

```text
(3^k x + B_w) / 2^A = x
```

and therefore

```text
(2^A - 3^k)x = B_w
```

Define

```text
D_w = 2^A - 3^k
```

Then a positive loop candidate requires

```text
D_w > 0
D_w | B_w
x = B_w / D_w
```

Thus the loop problem is reduced to the divisibility condition

```text
D_w | B_w
```

## All-2 Heartbeat

The word

```text
w = (2, 2, ..., 2)
```

has

```text
A_j = 2j
A = 2k
```

so

```text
B_w = sum_{j=0}^{k-1} 3^(k-1-j) 4^j
```

This is the finite geometric difference

```text
B_w = 4^k - 3^k
```

and

```text
D_w = 2^(2k) - 3^k = 4^k - 3^k
```

Therefore

```text
B_w = D_w
x = B_w / D_w = 1
```

The all-2 word produces only the trivial loop through `1`.

## Deviation Coordinates

Write every exponent as a deviation from the all-2 heartbeat:

```text
a_j = 2 + e_j
```

Define prefix deviations

```text
E_0 = 0
E_j = e_0 + ... + e_{j-1}
E_k = e_0 + ... + e_{k-1}
```

Then

```text
A_j = 2j + E_j
A = 2k + E_k
```

So

```text
B_w = sum_{j=0}^{k-1} 3^(k-1-j) 4^j 2^E_j
```

and

```text
D_w = 4^k 2^E_k - 3^k
```

Define the offset defect

```text
Delta_w = B_w - D_w
```

Since

```text
B_w = D_w + Delta_w
```

we have the exact equivalence

```text
D_w | B_w
iff
D_w | Delta_w
```

## Delta Identity

Substitute the deviation form into `Delta_w = B_w - D_w`:

```text
Delta_w =
sum_{j=0}^{k-1} 3^(k-1-j) 4^j (2^E_j - 1)
- 4^k(2^E_k - 1)
```

This identity isolates the only source of nontrivial loop closure: the accumulated `+1` offset must cancel exactly against the denominator defect.

For the all-2 word,

```text
E_0 = E_1 = ... = E_k = 0
```

so every term vanishes:

```text
Delta_w = 0
```

and the loop is `x = 1`.

## Normalized Integer Form

Some prefix deviations `E_j` may be negative. Since `D_w` is odd, multiplying by a power of `2` does not change divisibility by `D_w`.

Let

```text
h = -min(0, E_0, E_1, ..., E_k)
H_j = E_j + h
```

Then every `H_j >= 0`, and

```text
gcd(D_w, 2^h) = 1
```

Therefore

```text
D_w | Delta_w
iff
D_w | 2^h Delta_w
```

The normalized defect is

```text
2^h Delta_w =
sum_{j=0}^{k-1} 3^(k-1-j) 4^j (2^H_j - 2^h)
- 4^k(2^H_k - 2^h)
```

This is the integer-safe form of the Lock 1 obstruction.

## Lock 1 Delta-Prefix Theorem Needed

For every exponent word `w` with `D_w > 0`,

```text
D_w | 2^h Delta_w
```

if and only if

```text
E_0 = E_1 = ... = E_k = 0
```

Equivalently:

```text
2^h Delta_w ≡ 0 mod D_w
```

if and only if the prefix-deviation path is identically zero.

This is the last nontrivial theorem needed by Lock 1. The previous sections reduce no-loop closure to exactly this statement.

In computational certificate form, define

```text
delta_q(w) = D_w / gcd(D_w, 2^h Delta_w)
```

Then the invariant says

```text
delta_q(w) = 1
```

if and only if `w` is the all-2 heartbeat.

## Non-Circular Witness-Prime Form

The theorem should be proved through a prime divisor of `D_w`, but the prime must be selected without already knowing `gcd(D_w, 2^h Delta_w)`.

The correct non-circular statement is:

```text
For every nonzero prefix-deviation path E,
there exists a prime p | D_w
selected from the factor class of D_w
such that
2^h Delta_w not≡ 0 mod p.
```

Then

```text
p | D_w
and
2^h Delta_w not≡ 0 mod p
```

implies

```text
D_w ∤ 2^h Delta_w
```

which proves the delta-prefix theorem.

Modulo such a prime `p`, the condition `p | D_w` gives

```text
2^A ≡ 3^k mod p
```

or, in deviation coordinates,

```text
4^k 2^E_k ≡ 3^k mod p
```

The normalized delta identity becomes a finite-field statement:

```text
2^h Delta_w ≡
sum_{j=0}^{k-1} 3^(k-1-j)4^j(2^(E_j+h)-2^h)
- 4^k(2^(E_k+h)-2^h)
mod p
```

The remaining proof obligation is therefore:

```text
For every nonzero prefix path E, choose a non-circular p | D_w
whose finite-field reduction separates the first nonzero prefix deviation
from all later offset terms.
```

This is the exact written proof still needed for the invariant.

## Conditional Proof Of No Nontrivial Positive Loop

This section shows that the no-loop theorem follows immediately once the Lock 1 Delta-Prefix Theorem is proved.

Assume a positive integer loop exists.

Choose an odd member `x` of the loop and let

```text
w = (a_0, ..., a_{k-1})
```

be the exact valuation word around the loop.

By the odd-only block formula,

```text
F_w(x) = (3^k x + B_w) / 2^A
```

Since the loop closes,

```text
F_w(x) = x
```

so

```text
x = B_w / D_w
```

and therefore

```text
D_w | B_w
```

Because `B_w = D_w + Delta_w`,

```text
D_w | Delta_w
```

Because `D_w` is odd,

```text
D_w | 2^h Delta_w
```

By the Lock 1 Delta-Prefix Theorem, this implies

```text
E_0 = E_1 = ... = E_k = 0
```

Therefore every exponent deviation is zero:

```text
e_j = 0
```

so every exponent is

```text
a_j = 2
```

Thus the word is the all-2 heartbeat.

But the all-2 heartbeat gives

```text
B_w = D_w
x = 1
```

Therefore the assumed loop is the trivial loop through `1`.

So, conditional on the Lock 1 Delta-Prefix Theorem, no nontrivial positive integer loop exists.

## Machine Verification Surface

The Lock 1 implementation now has two proof surfaces:

1. `lock1_delta_lemma_miner.rs` verifies the normalized delta identity and records witness factors.
2. `lock1_residue_dp_prover.rs` proves whole finite `(k,A)` classes by residue reachability, without forward-enumerating starting integers.

The DP prover is the direct implementation of the divisibility obstruction. For fixed `k` and `A`, it computes every reachable state

```text
(position, prefix_sum, B_w mod D_w, non_all2)
```

under the recurrence

```text
B_{j+1} = 3B_j + 2^A_j mod D_w
```

where

```text
D_w = 2^A - 3^k
```

At the final layer it checks whether any state exists with

```text
prefix_sum = A
B_w mod D_w = 0
non_all2 = true
```

If no such state is reachable, then that whole `(k,A)` class has no nontrivial loop word.

Current DP class-proof run:

```text
data/runs/lock1_residue_dp_line16_offset1
```

Summary:

```text
classes_proved=16
D_le_zero_skips=0
words_covered=4813823
failed_classes=0
max_layer_states=3203847
claim_status_for_scanned_classes=dp_proved_no_nontrivial_zero_residue
```

Class table:

```text
data/runs/lock1_residue_dp_line16_offset1/lock1_residue_dp_classes.csv
```

The DP run proves the same 4,813,823-word line-16 surface at the class level:

```text
k,A,D,words_covered,zero_all2_words,zero_nontrivial_words,verdict
1,2,1,1,1,0,proved_no_nontrivial_zero_residue
2,4,7,3,1,0,proved_no_nontrivial_zero_residue
3,5,5,6,0,0,proved_no_nontrivial_zero_residue
4,7,47,20,0,0,proved_no_nontrivial_zero_residue
5,8,13,35,0,0,proved_no_nontrivial_zero_residue
6,10,295,126,0,0,proved_no_nontrivial_zero_residue
7,12,1909,462,0,0,proved_no_nontrivial_zero_residue
8,13,1631,792,0,0,proved_no_nontrivial_zero_residue
9,15,13085,3003,0,0,proved_no_nontrivial_zero_residue
10,16,6487,5005,0,0,proved_no_nontrivial_zero_residue
11,18,84997,19448,0,0,proved_no_nontrivial_zero_residue
12,20,517135,75582,0,0,proved_no_nontrivial_zero_residue
13,21,502829,125970,0,0,proved_no_nontrivial_zero_residue
14,23,3605639,497420,0,0,proved_no_nontrivial_zero_residue
15,24,2428309,817190,0,0,proved_no_nontrivial_zero_residue
16,26,24062143,3268760,0,0,proved_no_nontrivial_zero_residue
```

The remaining infinite step is to express this DP reachability obstruction as a closed-form theorem over all `(k,A)` classes.

The Lock 1 delta lemma miner verifies the normalized delta identity and searches for counterexamples to the invariant.

Current in-project run:

```text
data/runs/lock1_delta_lemma_line16_offset1_factor_rules
```

Summary:

```text
words_scanned=4813823
D_le_zero_rejects=0
overflow_rejects=0
identity_failures=0
all_zero_prefix_paths=2
nonzero_prefix_paths=4813821
normalized_residue_zero=2
nontrivial_normalized_residue_zero=0
family_groups=1796
factor_class_groups=16
claim_status_for_scanned_words=delta_identity_clean_no_nontrivial_zero_residue
```

The danger rows are exactly the all-2 heartbeat rows seen in the positive-side scan:

```text
2
2 2
```

The scanner did not find a nonzero prefix-deviation path satisfying

```text
2^h Delta_w ≡ 0 mod D_w
```

This matches the Lock 1 Delta-Prefix Theorem.

Updated non-circular factor-class witness run:

```text
data/runs/lock1_delta_lemma_line16_offset1_factor_rules
```

The scanner now factors `D_w` first, then selects the first prime-power factor `p^r | D_w` for which

```text
2^h Delta_w not≡ 0 mod p^r
```

That means the witness is selected from the factor class of `D_w`, not from `gcd(D_w, 2^h Delta_w)`.

Factor-class rule table:

```text
data/runs/lock1_delta_lemma_line16_offset1_factor_rules/lock1_factor_class_witness_rules.csv
```

Aggregate factor-class check:

```text
factor_classes=16
missing_witness_modulus_total=0
nontrivial_residue_zero_total=0
```

The sixteen scanned factor classes are:

```text
k,A,D,D_factorization,count,nonzero_prefix,nontrivial_residue_zero,missing_witness_modulus,witness_modulus_counts
1,2,1,1,1,0,0,0,1:1
2,4,7,7:7,3,2,0,0,1:1;7:2
3,5,5,5:5,6,6,0,0,5:6
4,7,47,47:47,20,20,0,0,47:20
5,8,13,13:13,35,35,0,0,13:35
6,10,295,5:5;59:59,126,126,0,0,5:90;59:36
7,12,1909,23:23;83:83,462,462,0,0,23:448;83:14
8,13,1631,7:7;233:233,792,792,0,0,7:672;233:120
9,15,13085,5:5;2617:2617,3003,3003,0,0,5:2499;2617:504
10,16,6487,13:13;499:499,5005,5005,0,0,13:4595;499:410
11,18,84997,11:11;7727:7727,19448,19448,0,0,11:17666;7727:1782
12,20,517135,5:5;59:59;1753:1753,75582,75582,0,0,5:59562;59:15720;1753:300
13,21,502829,502829:502829,125970,125970,0,0,502829:125970
14,23,3605639,79:79;45641:45641,497420,497420,0,0,79:491078;45641:6342
15,24,2428309,13:13;186793:186793,817190,817190,0,0,13:754415;186793:62775
16,26,24062143,7:7;233:233;14753:14753,3268760,3268760,0,0,7:2801664;233:464920;14753:2176
```

This verifies the obstruction over the scanned positive-side surface with the witness selected non-circularly from the prime-power factorization of `D_w`. The written universal proof must promote this finite certificate rule into a theorem: select a prime-power factor `p^r | D_w` from the factor class of `D_w`, then prove the normalized residue is nonzero modulo `p^r`.

## Implementation Artifacts

Completion audit:

```text
LOCK1_PROOF_COMPLETION_AUDIT.md
LOCK1_OFFSET_BARRIER.md
```

Primary proof miner:

```text
rust/lock1_delta_lemma_miner.rs
rust/lock1_residue_dp_prover.rs
```

Primary run artifacts:

```text
data/runs/lock1_delta_lemma_line16_offset1_factor_rules/LOCK1_DELTA_LEMMA_NOTES.md
data/runs/lock1_delta_lemma_line16_offset1_factor_rules/lock1_delta_lemma_summary.json
data/runs/lock1_delta_lemma_line16_offset1_factor_rules/lock1_delta_families.csv
data/runs/lock1_delta_lemma_line16_offset1_factor_rules/lock1_delta_danger_rows.csv
data/runs/lock1_delta_lemma_line16_offset1_factor_rules/lock1_delta_samples.csv
data/runs/lock1_delta_lemma_line16_offset1_factor_rules/lock1_factor_class_witness_rules.csv
data/runs/lock1_residue_dp_line16_offset1/lock1_residue_dp_summary.json
data/runs/lock1_residue_dp_line16_offset1/lock1_residue_dp_classes.csv
```

## Final Lock Statement

The `+1` term creates an accumulated offset `B_w`.

The only way that offset lands exactly on the loop denominator

```text
D_w = 2^A - 3^k
```

is the all-2 heartbeat.

Every nonzero deviation from the all-2 heartbeat is expected to create a normalized delta residue that does not vanish modulo `D_w`; the remaining written theorem is the non-circular witness-prime separation lemma above.

Once that witness-prime separation lemma is proved, the `+1` offset prevents exact nontrivial loop closure.

Conditional final Lock 1 statement: no positive integer loop exists except the trivial cycle through `1`.
