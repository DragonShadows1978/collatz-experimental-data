# W6E — Bound-Pair Mechanical Phase (work order, Fable, 2026-07-04)

Executor: Sonnet agent. House rules apply: gates are FROZEN before
execution; the result is the result; inconclusive is a result; report
failures unvarnished; append everything to
renorm_check/IMPLEMENTATION_LEDGER.md (do NOT edit SYNTHESIS.md — that
is the architect's post-verification job). All scripts + outputs live
under shell/underlock/w6e/.

## Context (read first)

- shell/underlock/DERIVATION_NOTES.md — especially §1 (game), §2
  (conservation identity D(m) = min max partial sum Σ(a−c)), §5
  (keystone identity, bound-pair program).
- Ground truth: the 28/28 periodic-law rows and the real system's
  11/11 mirror rows from the W6D ground-truth run (tables under
  shell/underlock/; locate the actual files, list them in the ledger
  entry so the record shows what was used).
- The game, operationally (backward chain from terminal ρ = 1):
  state = (residue ρ, depth-from-ceiling δ); at each backward step
  the credit letter c comes from the word; exponent menu
  a ∈ [1, δ+c]; parity of a is FORCED by ρ's class mod 3 (class 1 ⟹
  a even, class 2 ⟹ a odd, class 0 ⟹ no legal move); predecessor
  ρ' = (2^a·ρ − 1)/3 must be integral (that's what the parity/class
  condition encodes — verify your implementation reproduces it
  rather than assuming); δ' = δ + c − a. Feasible chain: δ_k ≥ 0
  always. D(m) for a word = the minimax of §2. Lifts: the residue is
  tracked mod 3^m (trit-locality); a "lift choice" is the freedom in
  ρ above the constrained trits.

## E1 — Explicit-strategy upper bound (the constructive object)

Implement two cheap explicit walker strategies and measure the max
partial sum each achieves on every ground-truth row:

- **S0 greedy:** always the smallest legal exponent of the forced
  parity.
- **S1 one-step steering:** among the three cheapest same-parity menu
  entries {a, a+2, a+4} (cost 0/2/4 above parity-minimal), pick the
  cheapest whose successor residue class avoids (i) class 0 next step
  and (ii) a next-step forced-even with empty menu (the kill shape).
  Tie → cheapest.

Run both on all 28 periodic rows (and the 11 real-system mirror rows
as a bonus census, clearly separated). For each row report: achieved
max partial sum vs ground-truth D; match/exceed; if exceed, the first
prefix where the strategy's running sum leaves the optimal envelope.

**Gate (frozen):** a strategy QUALIFIES as the constructive
upper-bound object iff it matches D exactly on ALL rows in scope.
Partial match is not failure of the experiment — the failure PATTERN
(which families, which m, which phase the divergence starts at) is
the deliverable.

**Registered predictions (Fable, frozen before execution):**
S0 fails somewhere (75%) — class-0 traps / forced-even runs punish
greed. S1 matches golden and √2 families (65%) but full 28/28 only
45% — the §5a lift-cascade suggests one-step lookahead may be too
shallow on some rows. If BOTH fail: the upper bound needs deeper lift
pre-commitment, and the failure phases tell us the horizon.

## E2 — Phase pinning for F5 (end-anchored recount)

The W6D-M exact-counting argument (149 true supports vs 150 periodic
→ D=148 → F5=359, conditional) was computed on the 0..358 window.
The real m=359 measurement runs 371 = 7·53 steps with the constrained
window END-ANCHORED (letters ≈ 12..370). Redo the support census on
the end-anchored window under BOTH phase conventions (start-anchored
0..358 as control; end-anchored 12..370), for the true word and the
periodic comparison word (periodic word = mechanical word of the
convergent per W6D_GROUND_TRUTH_ORDER.md spec — c_k = ⌊P(k+1)/q⌋ −
⌊Pk/q⌋, P = 2q−p; NOT first-q tiling).

**Gate (frozen):** deterministic arithmetic; deliverable = the four
counts (true/periodic × two anchorings) and whether the 149-vs-150
differential survives end-anchoring. Registered prediction (Fable):
differential SURVIVES (70%); if it flips, the conditional F5 flips to
358 and that gets reported exactly as loudly.

## E3 — Prefix-tightness census (targets the LOWER bound)

For each ground-truth row where an optimal chain is recorded (if not
stored, regenerate by search for rows with m small enough to be
cheap; skip and say so otherwise): tabulate the running sum
g(k) = Σ_{j≤k}(a_j − c_j) against the candidate prefix bound
⌊(pk+1)/q⌋ (mirror form for the real system). Report where equality
holds (the BINDING prefixes) and the distribution of binding-k
residues mod q.

Also verify the keystone identity per-prefix on every chain used:
2^{Σa over last k steps} ≡ S_k (mod 3^k) for all k (S_k = the
composition sum of DERIVATION_NOTES §5b restricted to the suffix).
Any violation = implementation bug, fix before trusting anything.

**Gate (frozen):** deliverable = binding-phase histogram. Registered
prediction (Fable): binding prefixes cluster at a fixed phase mod q
(75%) — the Raney/cycle-lemma worst peak. Uniform scatter would
weaken the P1b route and that is a result.

## Output

One ledger entry per experiment (E1/E2/E3), each with: scripts used,
ground-truth files used (paths), raw tables, gate verdict vs the
frozen predictions above, and honest walls hit. No synthesis, no
narrative promotion — the architect reads the tables.
