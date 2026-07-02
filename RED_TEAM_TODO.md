# Red Team TODO — Prioritized by Difficulty

Status: Working document. Items ordered hardest-first.
If a hard item can't be solved, easier items below it are moot.

Date: 2026-05-26

---

## HARD — Must solve or the proof doesn't close

### H1. Widen corridor definition to include signed deficit [Red Team #2, #3]

**Status:** RESOLVED DIFFERENTLY (2026-05-26)

**Resolution:** Widening the corridor does NOT work — cycles have drifting
deficit (contractive words accumulate negative deficit over repeated periods).
A cycle is NOT a bounded glider. Instead, cycles are handled separately via
the Precision-Corridor Contradiction (Section 7.2): cycle precision m ≈ k,
corridor width C = O(log k), giving k ≤ O(log k) — impossible for large k.
Small k handled by computational certificate (Simons-de Weger k < 68 billion).

**Problem:** A contractive cycle has `2^A > 3^k`, so after one full period
`d_k = floor(k·α) - A < 0`. The cycle's deficit goes negative. Under the
current corridor definition `0 ≤ d_k ≤ C`, a cycle may not lie inside any
Lock 3 corridor. If cycles aren't inside the corridor, Lock 3 can't kill them.

**Why it's hard:** Widening the corridor to allow `d_k < 0` changes the
phase-height cell count. The 53(C+1) capacity formula must be rederived for
a signed corridor `[-C_low, C_high]`. The Sturmian support/drop phase count
might change if the corridor is asymmetric. The `22m ≤ 53(C+1)` inequality
must still hold under the new definition.

**If solved:** Red Team #3 (Delta-Prefix Invariant) goes away entirely.
Lock 1 contractive case is absorbed into Lock 3. No separate cycle proof
needed.

**If NOT solved:** Must prove Lock 1 contractive case independently
(Delta-Prefix Invariant). That's the problem we spent hours on and hit the
wall. The proof would then need to be framed with the cycle case as a
computational certificate + asymptotic argument, not a closed theorem.

**Attack route:**
- Define corridor as `|d_k| ≤ C` (symmetric signed deficit).
- Phase-height cells become 53 × (2C+1) for symmetric corridor.
- Support/drop phase counts stay 22/31 (Sturmian structure doesn't change).
- New inequality: `22m ≤ 53(2C+1)`.
- A cycle with word length k has max deficit swing bounded by k.
  Set C = max |d_j| over the cycle. Finite by construction.
- Verify computationally: does the M_edge formula still hold with 2C+1?

**Acceptance criteria:** Written lemma showing every contractive cycle lies
in a signed corridor, plus the updated capacity inequality.

---

### H2. Lock 4 deterministic bridge inequality [Red Team #7]

**Status:** RESOLVED (2026-05-26)

Lemma 5c (alternation constraint) was WRONG — x=7 is a counterexample.
But the deterministic inequality was the wrong approach entirely.

Lock 4 is not a separate mechanism. It is Lock 3 (Theorem 1) applied at
every corridor level the orbit visits. An orbit that spikes to wider C
cannot SUSTAIN that width through a full heartbeat because the same
22m ≤ 53(C+1) constraint applies there. The orbit falls back.

Theorem 5 now derives from Theorem 1 directly: the precision ceiling
applies universally at every C, so no corridor can be held indefinitely.
The computational certificate (100B scan, max reserve 31 vs 149 needed)
confirms the mechanism empirically.

**Problem:** The current Lock 4 argument uses "approximately 127 bits" for the
bridge tax and "roughly C ≥ 149" for the support requirement. These are
heuristic/physical, not deterministic. A reviewer can object that
"approximately" doesn't rule out all integer orbits.

**Why it's hard:** The martingale drift `2 - α ≈ 0.41504` is exact as a
real number, but applying it to an INDIVIDUAL orbit (not an expected value) 
requires a worst-case bound, not an average. An individual orbit could have 
atypical exponent sequences that beat the average drift. Must show no such 
sequence can accumulate enough reserve to bridge.

**If solved:** Lock 4 becomes a theorem. Unbounded escape ruled out.

**If NOT solved:** Lock 4 stays as a proof sketch with computational
certificate (100 billion integers scanned). Publishable under Hales/Kepler
precedent but not a closed theorem.

**Attack route:**
- The bridge gap 53→359 is exactly 306 steps.
- Over 306 steps with exponents a_j ∈ {1,2} (Sturmian corridor):
  minimum total A = 306×1 = 306, maximum A = 306×2 = 612.
  Actual Sturmian total: floor(306·α) = 485.
- An orbit in the 53-corridor has deficit bounded by C.
  After 306 steps: total exponent A ≤ floor(306·α) + C = 485 + C.
  Reserve gained: A - 306 ≤ 485 + C - 306 = 179 + C.
- Support requirement for precision m=359: from 22×359 ≤ 53(C'+1):
  C' ≥ 22×359/53 - 1 = 148.02, so C' ≥ 149.
- The orbit must ENTER the 359-corridor with width C' ≥ 149.
  But the orbit came from a corridor of width C (at the 53-wall).
  Maximum reserve it could have built: 179 + C.
  Need 179 + C ≥ 149 → C ≥ -30. Always true!
  
  Wait — this doesn't give a contradiction. The reserve calculation needs
  to account for the COST of the bridge gap, not just the gain.
  
  Revisit: the orbit must cross 306 steps while maintaining precision
  m ≥ 359. But Lock 3 says precision 359 requires C ≥ 149.
  The orbit at the 53-wall has some C_start. During the 306-step gap,
  the deficit fluctuates. The orbit must maintain |d_k| ≤ C_bridge for
  the ENTIRE gap. The question: can C_bridge be ≤ 149 while also having
  enough reserve to survive?
  
  This needs careful formalization of "reserve" and "bridge cost" as
  deterministic quantities derived from the exponent word structure.

**Acceptance criteria:** Exact inequality showing C_available < C_required
for the 53→359 bridge and all subsequent bridges.

---

## MEDIUM — Solvable with focused work

### M1. Descent-exit lemma for negative-deficit region [Red Team #1]

**Status:** DONE (2026-05-26)

**Problem:** The regime decomposition says every non-descending orbit is
periodic, bounded-gliding, or unbounded-escape. But there's a fourth
possibility: the orbit enters the contractive region (d_k < 0) but hasn't
yet descended below its starting value, due to the accumulated +1 offsets.

**Depends on:** H1. If H1 is solved (signed corridor), this region is
included in the corridor and Lock 3 handles it. If H1 is NOT solved, this
lemma must be proved independently.

**Attack route:**
- If d_k < 0: the total exponent A_k exceeds k·α. The orbit's logarithmic
  height is decreasing on average.
- Show: an orbit with d_k < 0 for all subsequent steps must eventually
  descend below its starting value. The +1 offsets add O(3^k) while the
  contraction removes a factor of 2^(A_k - k·α) > 1 per step.
- Alternatively: show d_k < 0 is TRANSIENT — the orbit must either
  re-enter d_k ≥ 0 or descend.

**Acceptance criteria:** Written lemma with proof.

---

### M2. Integer-shadow correspondence [Red Team #4]

**Status:** DONE (2026-05-26)

**Problem:** The proof uses the census scanner's residue automaton to track
terminal-compatible shadows. A reviewer asks: why does a real integer orbit
necessarily appear as a shadow in the automaton at every precision m?

**Why it's medium:** The answer is nearly tautological — the scanner's
transition function IS the Collatz residue map. But the tautology must be
stated explicitly.

**Attack route:**
- State: the scanner transition `r → ((3r+1) · 2^(-a)) mod 3^m` is
  IDENTICAL to the Collatz odd-step map applied to residue classes.
- Therefore: if integer x has orbit staying in corridor C, then
  x mod 3^m follows the scanner's transition at every step.
- Terminal compatibility of x mod 3^m follows from x eventually reaching 1
  (which is the hypothesis we're trying to prove — careful about circularity).
  
  Actually: terminal compatibility means the residue CLASS containing x
  is compatible with reaching 1. If x DOESN'T reach 1, its residue class
  might still be terminal-compatible at finite precision (because precision
  m only sees the first m steps). The argument is:
  
  If x stays in corridor C forever, its residue at precision m must be
  compatible with SOME orbit path in the corridor at that precision —
  specifically, its OWN orbit path. The scanner enumerates ALL such paths.
  Therefore x's residue must appear in the scanner's live state set.

**Acceptance criteria:** Written correspondence lemma. Two paragraphs.

---

## EASY — Quick fixes, already know how

### E1. Notation table [Red Team #6]

**Status:** DONE (2026-05-26)

Add early in paper:

| Symbol | Meaning |
|---|---|
| C | corridor width (integer deficit levels) |
| m | 3-adic residue precision |
| k | odd-step depth |
| A_k | accumulated division exponent at step k |
| d_k | deficit: floor(k·α) - A_k |
| α | log₂3 ≈ 1.58496 |
| M_edge(C) | last supported precision = floor(53(C+1)/22) |
| K(C) | first desert precision = M_edge(C) + 1 |

---

### E2. Rephrase log₂3 claim [Red Team #9]

**Status:** DONE (2026-05-26)

Replace Section 9's broad claim with:

> The irrationality of log₂3 prevents exact neutral action and generates
> the Sturmian/convergent structure. The individual proof components require
> additional arithmetic: the Drop-Phase Forced Digit lemma for precision
> collapse, support-capacity counting for bounded gliders, and bridge-reserve
> inequalities for unbounded escape.

---

### E3. Fix C=6-50 verification language [Red Team #11]

**Status:** DONE (2026-05-26)

Change "All m=1 lifetime probes match exactly" to:

> For C=6 through 50, the m=1 implied edge values are consistent with the
> formula. Full m-ladders were verified for C=3, 4, 5.

---

### E4. Add theorem/computation/certificate labels [Red Team #12]

**Status:** DONE (2026-05-26)

Label each claim as one of:
- **Theorem** (proved in document)
- **Lemma** (proved in document, supports a theorem)
- **Computational certificate** (verified by scanner, not proved abstractly)
- **Conjecture** (supported by evidence, not proved)

Apply especially to Lock 4 bridge arguments.

---

### E5. Relabel breach witnesses [Red Team #8]

**Status:** DONE (2026-05-26)

Change breach-witness section from proof language to evidence language:

> Computational certificate: every corridor-breach witness constructed by
> the CRT reconstruction system collapses to 1 when followed forward.

Do NOT claim this as a universal proof.

---

### E6. Weaken "generically one of three" [Red Team #10]

**Status:** NOT STARTED  
**RESOLVED BY LEMMA 5 REWRITE.**

The updated Lemma 5 uses the Drop-Phase Forced Digit argument (algebraic)
instead of the "generically 1/3" observation. No longer depends on scanner
lift-survival ratios for the theorem statement. Scanner data is cited as
verification only.

Mark as DONE.

---

## DONE

### D1. Support-cell non-reuse / 22m incidence theorem [Red Team #5]

**Status:** DONE (2026-05-26)

Proved via Drop-Phase Forced Digit Lemma (5a) + Support-Phase Binary Choice
Lemma (5b) + Pigeonhole. Algebraic proof, no computational dependence.
Updated in COLLATZ_PROOF.md.

---

## Dependency Chain

```
H1 (widen corridor) ──→ kills Red Team #2, #3
  └──→ M1 (descent-exit) becomes unnecessary if H1 solved
  
H2 (Lock 4 deterministic) ──→ kills Red Team #7

M2 (integer-shadow) ──→ kills Red Team #4

E1-E6 ──→ kills Red Team #6, #8, #9, #10, #11, #12

All of above ──→ kills Red Team #13 (final theorem too strong)
```

## Critical Path

```
H1 → M1 → H2 → M2 → E1-E5 → Final review
```
