# The One-Step Descent Species — specification & mission brief

**Origin:** David Perry, 2026-07-05. Question that seeded it:
"Is there a rule on the descent — a number that when divided by 2
always gets to 1?"

**Convention.** Collatz odd-map: S(x) = (3x+1) / 2^{v2(3x+1)}, where
v2(n) = the number of factors of 2 in n, and x ranges over odd
positive integers. One "odd-step" applies S once.

---

## The claim (to be proven, then mission-verified at scale)

**THEOREM (One-Step Descent Species).**
An odd integer x reaches 1 in exactly ONE odd-step — i.e. S(x) = 1 —
if and only if
        x = (4^k − 1) / 3   for some integer k ≥ 1.
Equivalently: x ∈ {1, 5, 21, 85, 341, 1365, 5461, 21845, ...},
the numbers whose binary form is a block of k ones times... i.e.
x = (4^k−1)/3 = 0b01010...1 (k ones in the odd positions).

For these and ONLY these odd x, 3x+1 is a pure power of two (2^{2k}),
so the single division by 2^{2k} lands exactly on 1.

**Corollary (membership is decidable in closed form, any digit
length).** Given any odd x — of arbitrary size — one can PROVE
whether it is in the species WITHOUT running its trajectory:
x is in the species  ⟺  3x+1 is a power of 2  ⟺  3x+1 = 2^j with
j even. This is a two-line certificate: compute 3x+1, test if it is
a power of two (single bitwise op: n & (n−1) == 0), and if so check
the exponent is even. O(digits) work, no trajectory simulation.

---

## Proof (elementary, complete)

S(x) = 1 means (3x+1)/2^{v2(3x+1)} = 1, i.e. 3x+1 = 2^j for some
j ≥ 1 (the full 2-power is divided out to reach the odd number 1).

Solve 3x + 1 = 2^j for a positive integer x:
    x = (2^j − 1) / 3.
This is an integer iff 2^j ≡ 1 (mod 3). Since 2 ≡ −1 (mod 3),
2^j ≡ (−1)^j (mod 3), which equals 1 iff j is EVEN. Write j = 2k:
    x = (2^{2k} − 1)/3 = (4^k − 1)/3.
For k ≥ 1 this is a positive odd integer, and 3x+1 = 4^k = 2^{2k}
is a pure power of two, so S(x) = 1. Conversely any one-step-to-1
odd x forces 3x+1 = 2^{even}, hence x = (4^k−1)/3. ∎

**Also provable, size-independent (the mod-4 drop rule, a lemma the
species sits inside):** an odd x DECREASES on its next odd-step
(S(x) < x) iff v2(3x+1) ≥ 2 iff 3x+1 ≡ 0 (mod 4) iff x ≡ 1 (mod 4).
Every species member is ≡ 1 (mod 4): (4^k−1)/3 ≡ 1 (mod 4) for all
k ≥ 1 (each term = 4·previous + 1). So the species is a subset of
the one-step droppers — it is the extreme sub-case where the drop
goes all the way to 1.

Recurrence form: x_{k+1} = 4·x_k + 1, x_1 = 1. Binary: x_k is the
k-bit alternating pattern 0101...01 (value (4^k−1)/3).

---

## What is PROVEN vs what remains the Collatz problem (state honestly)

- PROVEN, any digit length: membership in the species (closed-form
  certificate), the one-step-to-1 behavior, the mod-4 drop rule.
- NOT claimed here, and NOT implied: that arbitrary x reaches 1.
  That is the open Collatz conjecture. This species is exactly the
  set with a *trivial* one-step certificate; the hard numbers are
  everything else. The spec proves a clean sub-structure, not the
  conjecture.

---

## MISSION (for the executor)

Verify the theorem at scale and produce the certificate machinery.

1. **Direct construction gate.** For k = 1 .. K_large (push K into the
   thousands of BITS — i.e. x with thousands of digits): construct
   x = (4^k−1)/3, confirm exact-integer that 3x+1 = 2^{2k} (bitwise
   power-of-two test), and confirm S(x) = 1 by one exact odd-step.
   Report the largest k reached and wall/RSS. This proves the forward
   direction holds at arbitrary digit length.
2. **Converse / exclusivity gate.** Over a large exhaustive range of
   odd x (e.g. all odd x < 10^7, plus random huge x), confirm that
   S(x) = 1 in one step happens for EXACTLY the (4^k−1)/3 values and
   no others. Zero false positives, zero false negatives, against a
   brute one-step simulation as ground truth.
3. **The closed-form certifier.** Implement is_one_step_species(x)
   returning (bool, k or None) using ONLY the 3x+1 / power-of-two /
   even-exponent test — no trajectory run. Gate it: it must agree with
   brute one-step simulation on every x in gate 2, and must certify a
   handful of thousand-digit species members and reject thousand-digit
   non-members, each in O(digits) time. Report timing vs digit length
   to show it is trajectory-free.
4. **(Optional extension) the k-step clean-descent tower.** The
   one-step species is the k=1 floor of a larger structure: odd x that
   descend to 1 in n clean drops with no rise. Characterize the n=2, 3
   species (stacked congruences mod 4, 16, 64 ...) if cheap; report the
   closed forms or an honest wall.

**Output discipline (mandatory, see
renorm_check/shell/LEDGER_SYNTHESIS_POLICY.md):** write a process
LEDGER entry (paths tried/abandoned + why, bugs + how caught, exact
artifact paths) to IMPLEMENTATION_LEDGER.md AND a SYNTHESIS entry to
SYNTHESIS.md. The chat summary is a courtesy only. Exact integer
arithmetic throughout. No commits. Work under
renorm_check/shell/descent_rule/.

**Frozen expectation:** all three gates pass exactly (this is a
theorem, not a conjecture — a failure means a BUG in the harness, so
stop and diagnose rather than doubt the math). Gate-4 tower is
genuine open exploration; no prediction frozen there.
