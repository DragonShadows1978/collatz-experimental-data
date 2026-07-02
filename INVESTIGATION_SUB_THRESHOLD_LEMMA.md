# Investigation: The Sub-Threshold A-Sequence Lemma

**Priority:** CRITICAL — this is the single remaining gap in the Collatz proof.

**Date:** 2026-05-28

**Data directory:** `/mnt/ForgeRealm/collatz-experimental-data/`

---

## What We Have

A proof of the Collatz conjecture that reduces the entire problem to three cases — cycles, bounded gliders, and unbounded escape — and closes two of them:

1. **Cycles:** Killed by Theorem 3 (Lemma 6 ghost fixed point + Simons-de Weger computational certificate, k < 68 billion). No nontrivial positive cycle exists.

2. **Bounded gliders:** Killed by Theorem 2 + the residue automaton. The automaton at corridor C, precision m > M_edge(C) = ⌊53(C+1)/22⌋, exhaustively enumerates every (deficit, residue mod 3^m) state and finds zero survivors. Verified across C = 1–50 (Certificate 1) and spectral radius locked at ρ = 0.9607 for C = 3, m ≥ 10 through m = 13 on 6.4 million states (Certificate 6).

3. **Unbounded escape:** Partially closed. The automaton forces every orbit to either terminate (reach value 1) or exit the corridor at each precision level. The 2-adic constraint (Part 1) shows sustained consecutive a = 1 requires −1 ∈ ℤ₂, not a positive integer. The Sturmian tilt (Part 2) shows 31 contraction opportunities vs 22 expansion opportunities per heartbeat. But **the composition across corridors does not close the escape case** — the orbit can exit each corridor upward, and per-corridor checks don't compose into a global result.

## What We Don't Have

**The missing lemma, stated precisely by adversarial review (Claude Opus 4.8, 31 turns):**

> For every positive odd integer x₀, the deficit is bounded above along its orbit:
>
> ∀ odd x₀ ∈ ℤ₊, ∃ M(x₀) < ∞ such that ∀ n ≥ 0: d_n ≤ M(x₀)
>
> where d_n = ⌊n·log₂3⌋ − A_n and A_n = a₀ + a₁ + ⋯ + a_{n−1}.

Equivalently: **prove that no positive integer's exponent sequence (a₀, a₁, a₂, ...) can sustain Cesàro mean below log₂3 ≈ 1.585 forever.**

This is equivalent to: no positive integer diverges under Collatz. It IS the conjecture, restated in the proof's coordinates.

### Why the existing machinery doesn't close it

- The **3-adic automaton** (residue mod 3^m) kills confinement exhaustively but can't compose across corridors — an escaping orbit exits each corridor and the automaton correctly files this as "exit," which is permitted.

- The **2-adic constraint** (Part 1) kills consecutive a = 1 (converges to −1), but escape only needs scattered a = 1 with average a < 1.585. Scattered sub-threshold patterns correspond to 2-adic integers that are NOT −1.

- The **Lagarias conjugacy** maps every infinite exponent sequence to a unique 2-adic integer. Sub-threshold sequences are realized by uncountably many 2-adic integers (measure zero but uncountable). Whether any of these are positive integers is the conjecture.

- The **carry-break mechanism** (Section 8.5) shows WHY sub-threshold patterns break on specific orbits: the +1 in 3x+1 accumulates high bits that change the carry structure, producing larger a-values than the low-bit pattern predicts. Verified on orbit 871 (pattern breaks at step 15, predicted a=1 becomes a=4). But this is an observation on specific orbits, not a proof for all.

- **IMPORTANT NEGATIVE RESULT:** The odd Collatz map S is NOT well-defined on residue classes mod 2^k (because S(x) mod 2^k requires x mod 2^{k+a}, depending on the full integer). An attempted lemma claiming "no non-trivial cycles at mod 2^k for k ≥ 13" was WRONG — it traced specific small integers, not residue classes. Do not repeat this error.

## What Needs to Be Proved

**The sub-threshold a-sequence lemma:** No positive integer produces an exponent sequence with sustained sub-threshold average.

Formally, one of these equivalent statements:

**(A)** For every positive odd x₀, there exists N such that A_N ≥ ⌊N·log₂3⌋ (the accumulated halvings catch the credit line).

**(B)** For every positive odd x₀, sup_n d_n < ∞ (the deficit is bounded above).

**(C)** The set of 2-adic integers whose Collatz exponent sequence has limsup of the Cesàro mean below log₂3 contains no positive integers.

**(D)** For every positive odd x₀, there exists n with x_n < x₀ (finite stopping time — the classical form).

## Key Constraints on Any Attack

1. **Cannot use averages/measure theory.** E[a] = 2 > log₂3 shows TYPICAL orbits descend. That's Tao 2019 (almost all). We need ALL, not almost all. The exceptional set is measure zero but potentially non-empty among positive integers.

2. **Cannot use the 3-adic automaton for escape.** It kills confinement but the escaper exits every corridor. Per-corridor emptiness confirms the exit, it doesn't prevent it.

3. **Cannot assume the map is well-defined on mod 2^k residue classes.** It isn't. S(x) mod 2^k depends on x mod 2^{k+a}.

4. **Must work with individual orbits, not ensembles.** The spectral radius controls mass decay of a weighted operator, not individual orbit fate (weighted ρ < 1 is a measure statement). Need a pointwise bound.

5. **The Sturmian credit is exact (not heuristic).** ⌊53·log₂3⌋ = 84 is a theorem, not an average. The 22/31 split is algebraic. What's NOT controlled is the realized exponent sequence a_k of any specific orbit.

## Existing Tools and Data

**Computational infrastructure:**
- `rust/spectral_radius_sparse.rs` — sparse iterative spectral radius computation, handles 6.4M states
- `rust/lock3_census.rs` — full residue automaton with breach-follow, CRT reconstruction
- `rust/spectral_radius.rs` — dense matrix version for smaller state spaces
- All tools compile under Cargo, see `Cargo.toml`

**Key data files:**
- `data/runs/lock3_C3_N2000_residue_m10_lineage_cohorts_20260523/` — C=3, m=10 census (desert: zero valid_from_1 at all 2000 depths)
- `data/runs/lock3_C3_m9_breach_follow/` — breach follow data, 50/50 collapse to 1
- `SPECTRAL_RADIUS_RESULTS.txt` — full spectral radius data with ASCII plots
- `COLLATZ_PROOF.md` — current proof document (891 lines)
- `COLLATZ_PROOF_FIXES.md` — status of all expositional fixes

**Key verified facts:**
- Desert edge exact at M_edge(C) = ⌊53(C+1)/22⌋ for C = 1–50
- Spectral radius locks at 0.9607 for C = 3, m ≥ 10 (through m = 13)
- 250/250 breach witnesses collapse to 1 across C = 1–5
- 10^11 integers scanned, max deficit 31 vs 149 required for first bridge
- Carry-break verified on 871: pattern [1,1,2,1,1,1] holds 12 steps, breaks at step 15

---

## Recommended Attack Vectors

### Attack 1: The Joint 2-adic × 3-adic Automaton

**Idea:** Build an automaton that tracks states in the product space (deficit, residue mod 3^m, residue mod 2^j) simultaneously. The 3-adic automaton branches over all a because a is 2-adically determined. If you ADD the 2-adic coordinate, the branching becomes constrained: at state (d, r₃, r₂) where r₃ = x mod 3^m and r₂ = x mod 2^j, the exponent a = v₂(3x+1) is determined by r₂ (when a < j). So the product-space automaton has NO free branching for a < j — each state has a unique successor.

**Why it might work:** The 3-adic automaton's weakness is that it branches over all a, which is why the escaper can "choose" exit. In the product space, a is pinned by the 2-adic coordinate. The escaper can't choose — its a-value is determined. If the product-space automaton at sufficient (m, j) has all orbits reaching terminal, that's a pointwise result, not a measure result, because there's no branching.

**State space:** (C+1) × 3^m × 2^{j-1} states (odd residues only mod 2^j). At C = 3, m = 5, j = 10: 4 × 243 × 512 = 497,664 states. Feasible with the sparse engine.

**Key question:** Does the product-space survivor graph empty at feasible (m, j)? If so, it's the per-orbit kill the proof needs.

**Risk:** State space grows as 3^m × 2^j, so large (m, j) may be intractable. The coupling between coordinates might not simplify enough.

### Attack 2: The Carry-Propagation Bound

**Idea:** Formalize the carry-break mechanism. When an orbit follows a sub-threshold exponent pattern for N steps, the value grows by factor (3/2^ā)^N where ā < log₂3. This growth adds ⌈N(log₂3 − ā)⌉ bits above the initial bit-length. The +1 carry in 3x+1 propagates through consecutive 1-bits in the binary expansion. Prove that the accumulated high bits must eventually create a carry that reaches a position where it changes v₂(3x+1), producing a larger a-value than the sub-threshold pattern requires.

**Why it might work:** The carry-break is observed on every tested orbit (871 breaks at step 15, every breach witness collapses). The +1 is deterministic, not statistical. The carry propagation depends on the binary structure of the specific integer, which is finite (positive integers have finitely many bits). A sub-threshold pattern that sustains growth keeps adding bits that the carry chain eventually hits.

**Formal approach:** Model the binary expansion of x_k as a random-looking string (justified by the mixing properties of 3x+1). The expected carry distance from +1 is 2 bits (geometric distribution of consecutive 1-bits). After the orbit adds B new bits above position k, the probability that no carry reaches those bits in B/2 steps is (1/2)^{B/2} → 0. Convert this probabilistic argument to a deterministic one using the structure of 3x+1 (the carry always propagates upward, never skips).

**Key question:** Can the carry-propagation be bounded deterministically (not just in expectation)? The worst case is an integer with all 0-bits above its initial length — but the 3x+1 operation creates 1-bits, so the binary expansion can't stay all-0 above any fixed position.

**Risk:** Converting the probabilistic carry argument to a deterministic bound is hard. The binary expansion of x_k is not truly random — it carries correlations from the +1 offsets. The worst-case carry distance could be larger than expected.

### Attack 3: The Finite-Precision Descent Certificate

**Idea:** For each positive integer x₀ < 2^B (B-bit numbers), compute the maximum number of steps before the orbit MUST descend below x₀, using the joint (3-adic × 2-adic) structure at precision sufficient to resolve x₀ completely.

**Why it might work:** A positive integer x₀ with B bits is completely determined by its residue mod 2^B and mod 3^m for m = ⌈B/log₂3⌉. At these precisions, the automaton can track x₀'s exact residue class with no ambiguity. If the automaton at (C, m, j) = (B, ⌈B/α⌉, B) shows x₀'s class terminates within some depth D(B), then x₀ must descend within D(B) steps.

**The induction:** If every B-bit integer descends within D(B) steps, it reaches a value below 2^B. That smaller value is a B'-bit integer with B' < B. By induction on bit-length: every integer eventually reaches 1. The base cases (small integers) are verified by the 10^11 scan.

**Formal approach:** Show that D(B) exists for every B (the automaton terminates at finite depth for every finite precision). This follows from the desert edge: at m > M_edge(C), the automaton is empty. For B-bit integers in corridor C ≈ B: M_edge(B) ≈ 2.41B, and the automaton at precision m = 2.41B resolves the integer completely (Precision Ratio: 3.82×). The descent must occur within the heartbeat at that precision.

**Key question:** Does the descent at the heartbeat level at precision 2.41B actually give a SMALLER integer, or could it descend to something only slightly smaller (still B bits)? Need to show the descent is by at least 1 bit, establishing the induction.

**Risk:** The descent might not reduce the bit-length — the orbit could descend below x₀ to a value x₀ − 1 (same bit-length). The induction needs descent in BIT-LENGTH, not just value. May need to combine with the spectral radius showing 3.94% contraction per heartbeat.

### Attack 4: The Sturmian Pigeonhole on Exponent Words

**Idea:** The Sturmian heartbeat has period 53 with credit 84. Over any 53-step window, the credit is exactly 84 (by the convergent property). For the deficit to increase over a 53-step window: the orbit needs A₅₃ < 84, i.e., the exponent sum must be less than 84. The total number of possible exponent words (a₁,...,a₅₃) with sum < 84 and each aᵢ ≥ 1 is finite. For each such word, the automaton can check whether ANY residue class mod 3^m is compatible with that word at sufficient precision.

**Why it might work:** Instead of branching over all a at each step (the automaton's current approach), fix the ENTIRE 53-step exponent word and check compatibility. The number of sub-threshold words is finite (bounded by the number of compositions of 83 into 53 parts). For each word, the 3-adic dynamics are fully determined — no branching, no free variable. If every sub-threshold word's residue orbit hits terminal at sufficient precision, escape is dead.

**Formal approach:** Enumerate all exponent words w = (a₁,...,a₅₃) with sum(w) < 84 and each aᵢ ≥ 1. For each word, compose the 53 transition matrices T_{a₁} ∘ ... ∘ T_{a₅₃} at precision m. Check whether the composed map has any fixed points or cycles that avoid the terminal residue. If none do at m > M_edge: no sub-threshold word can sustain an orbit.

**State space per word:** 3^m residues (no deficit needed since the word fixes the deficit trajectory). At m = 10: 59,049 states. Feasible. Number of words: compositions of ≤83 into 53 parts with each part ≥1 — this is C(82, 52) ≈ 10^14, which is too many to enumerate exhaustively. But the Sturmian structure constrains which words are actually accessible (the deficit must stay non-negative), drastically reducing the count.

**Key question:** Can the accessible sub-threshold words be enumerated tractably? The deficit constraint (d_k ≥ 0 at every step) filters most words. The surviving words are those compatible with corridor [0, C] for some C. The automaton already handles this — the question is whether fixing the word (rather than branching) gives a stronger result.

**Risk:** The word count may still be intractable. And a single 53-step word doesn't capture the full escape — the escaper uses DIFFERENT words in successive heartbeats. Would need to show no SEQUENCE of sub-threshold words sustains escape, which is the composition problem again.

---

## Success Criteria

The investigation succeeds if it produces ANY of:

1. A proof that the product-space (2-adic × 3-adic) automaton has zero survivors at feasible precision — killing escape pointwise, not in measure.

2. A deterministic carry-propagation bound showing the +1 offset forces every sub-threshold pattern to break within bounded steps — closing the observation into a lemma.

3. A finite-precision descent certificate with induction on bit-length — reducing Collatz to a verified base case.

4. A Sturmian word enumeration showing no accessible sub-threshold word sustains terminal-avoidance at sufficient 3-adic precision.

5. Any other mechanism that establishes: ∀ odd x₀ ∈ ℤ₊, sup_n d_n < ∞.

---

## What NOT to Do

- Do not claim the 3-adic automaton alone closes escape. It doesn't — the escaper exits.
- Do not assume S is well-defined on residue classes mod 2^k. It isn't.
- Do not use weighted spectral radius as a pointwise argument. It's a measure statement.
- Do not assert the carry-break as a lemma without proving it for all orbits.
- Do not conflate the credit line (⌊kα⌋ = exact) with the expected halving count (E[a]·k = statistical).
- Do not treat the Lagarias 2-adic conjugacy as excluding positive integers from the sub-threshold set — it doesn't, because positive integers are a countable dense subset of ℤ₂.

---

*Prepared from 31 turns of adversarial review with Claude Opus 4.8, May 2026.*
*Every attack vector above was informed by a specific objection that survived scrutiny.*
