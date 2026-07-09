# The Backward Basin Certificate — spec & mission (Descent Rule, Layer 2)

**Origin:** David Perry, 2026-07-05. "The second layer: derive a
mathematical rule to ALSO eliminate all odd numbers that END UP at
the terminal species number classification."

**Goal.** Extend the one-step-species certificate (see
DESCENT_RULE_SPEC.md: x reaches 1 in one odd-step iff x=(4^k-1)/3)
BACKWARD: characterize, by closed-form congruence rules and WITHOUT
running any trajectory, every odd x whose Collatz trajectory
eventually lands on the species (hence provably reaches 1). Build the
"certified-convergent basin" as an expanding union of residue classes,
layer by layer, and measure whether it tiles the odd numbers.

Odd-map: S(x) = (3x+1)/2^{v2(3x+1)}. Backward odd-predecessors of an
odd t: all odd x>1 with S(x)=t, i.e. 3x+1 = t*2^j, x=(t*2^j-1)/3,
integer & odd.

---

## Established structure (verified 2026-07-05; verify again as gate 0)
- **LAYER 0** = the species {(4^k-1)/3} = {1,5,21,85,341,...}, all
  ≡ 1 (mod 4). Reach 1 in one odd-step. (Proven, DESCENT_RULE_SPEC.)
- **Predecessor existence is governed by t mod 3:**
  - t ≡ 1 (mod 3): odd predecessors exist at EVEN j (2,4,6,...)
  - t ≡ 2 (mod 3): odd predecessors exist at ODD j (1,3,5,...)
  - t ≡ 0 (mod 3): NO odd predecessors, EVER (multiples of 3 are
    leaves of the backward tree — the "3 is forbidden in 3x+1" fact
    from the shadow-prime work, seen structurally). A ≡0 mod 3 odd
    number can be a START but never a WAYPOINT.
  Reason: x=(t*2^j-1)/3 is an integer iff t*2^j ≡ 1 (mod 3); since
  2 ≡ -1 (mod 3), 2^j ≡ (-1)^j, so t*(-1)^j ≡ 1 (mod 3) fixes the
  j-parity by t mod 3, and is unsolvable when t ≡ 0.

## The recursive certificate (to derive precisely and prove)
- **LAYER n** = odd x such that S(x) ∈ LAYER (n-1). x is
  certified-convergent-in-n-steps.
- Certified basin B_N = LAYER 0 ∪ ... ∪ LAYER N. Every x in B_N
  provably reaches 1 in ≤ N+1 odd-steps, by a certificate of length
  O(N) with NO trajectory simulation of x itself — only the
  congruence membership tests.
- **Certifier is_certified(x, N):** run the DETERMINISTIC forward
  odd-step up to N times; x ∈ B_N iff some iterate is in LAYER 0
  (the species, closed-form testable). NOTE this DOES step forward —
  the scientific goal is the CLOSED-FORM residue description of each
  LAYER so membership becomes a congruence test, not iteration.

---

## MISSION

**Gate 0 — reproduce the structure.** Confirm the mod-3 predecessor
rule and the layer-0 species exactly.

**Gate 1 — closed-form the layers.** For LAYER 1, LAYER 2 (and 3 if
cheap): derive the exact residue-class description. Each layer is a
union of arithmetic progressions (predecessors are x=(t*2^j-1)/3 over
species/prior-layer t and admissible j). Express LAYER n as an
explicit set of congruence classes {x ≡ a_i (mod m_i)} where possible,
with the moduli. Report the classes and the modulus growth per layer.

**Gate 2 — coverage census (THE measurement).** For each N, compute
the DENSITY of odd numbers covered by B_N (fraction of odd x < 10^7,
say, that reach the species within N steps). Report density(N) as N
grows. Does it -> 1 (basin covers almost all odds), plateau, or leave
a positive-density residue uncovered? This is the key number.

**Gate 3 — the uncoverable-class question (THE point).** Is there a
congruence class of odd numbers that B_N can NEVER reach for any N
(structurally excluded from the backward tree)? The ≡0 mod 3 leaves
are excluded as WAYPOINTS but can still be START points that step
INTO the basin — check: does every ≡0 mod 3 odd number's first step
land in the basin? More generally: characterize the complement
(odds not yet certified at layer N) and test whether it shrinks to
measure zero or has a hard residue floor. A hard uncoverable class
is exactly where a counterexample would live — connect to the
death-shell / capacity picture if it appears.

**Gate 4 (optional) — merge-safe density.** WARNING inherited from
SHADOW-HARMONICS: Collatz trajectories MERGE; naive per-start
sampling overcounts shared nodes. Coverage density here is over
DISTINCT odd x (each x tested once for basin membership), so it is
merge-safe by construction — but state this explicitly and confirm
no double-counting.

## Frozen expectations (register before measuring)
- Gate 0/1: exact (theorem-level; a failure = harness bug).
- Gate 2: density(N) -> 1 as N grows (the basin covers almost all
  odds) — CONJECTURED, ~70%. If it plateaus below 1, the residue is
  the finding.
- Gate 3: the complement shrinks toward measure zero with NO hard
  uncoverable residue class — CONJECTURED, ~60% (genuinely open; a
  hard class would be the bigger result).

## Output discipline (MANDATORY — see
renorm_check/shell/LEDGER_SYNTHESIS_POLICY.md)
Write a process LEDGER entry (approaches, abandoned paths + why, bugs
+ how caught, exact artifact paths) to IMPLEMENTATION_LEDGER.md AND a
SYNTHESIS entry to SYNTHESIS.md. Chat summary is courtesy only. Exact
integer arithmetic. Coverage density over DISTINCT x (merge-safe). No
commits. Work under renorm_check/shell/descent_rule/.

Final message: the closed-form layer classes + modulus growth, the
coverage density(N) curve, the uncoverable-class verdict, and
confirmation both LEDGER and SYNTHESIS were written.
