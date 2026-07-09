# Renormalization Recon — Synthesis (2026-07-03)

Three-agent data reconnaissance over this repo (no proofs attempted; all
claims backed by artifacts under `renorm_check/`). Independently
spot-checked: the C=148 divergence (recomputed at 50 digits), the
48-widths phrasing (COLLATZ_PROOF.md:230 vs LOCK3 grid's own caveat), and
the credit-sequence code split (grep of both Rust tools).

## F1 — The capacity formula is a convergent shadow (beatty/)

22/53 is an exact continued-fraction convergent of 2−log₂3 (next:
127/306). The published formula M_edge(C)=⌊53(C+1)/22⌋ and its
irrational-slope analogue ⌊(C+1)/(2−log₂3)⌋ agree for ALL C ≤ 147 and
first diverge at **C=148** (358 vs 359); divergences then densify to
~99.8% and grow linearly (~330 extra levels by C=10⁶). Every genuine
measurement ever run lives at C ≤ 50 — inside the agreement zone. **The
true capacity law past C=147 is empirically undetermined.** No
non-trivial exact Beatty representation of the rational form exists
(only algebraic restatements matched) — consistent with the rational
form being a shadow, not a law.

## F2 — The tools split across the rational/irrational divide (code)

- `spectral_radius*.rs`: builds credits for steps 0..53 and **cycles the
  block** → the ρ certificates describe the *periodicized* (53/22)
  operator by construction.
- `lock3_census.rs`: `credit_at_step(k)=⌊(k+1)α⌋−⌊kα⌋`, **unbounded k**
  → countdown/census measurements run on the TRUE aperiodic word.

Consequence: the decisive experiment (F5) is runnable with existing
tooling and is NOT circular. Precision caveat: credits use f64; deep
ladders should switch to exact Ostrowski/integer arithmetic before
trusting floors near convergent denominators.

## F3 — ρ(C) is constant, not periodic (renorm_check/ top level)

Freshly regenerated with the repo's own binary: ρ locks bit-identical
above a small transient (C≥11 at m=3, C≥23 at m=5, all anchors to
C=200). Confirms Certificate 6's "universal constant" narrative with new
data; kills the ρ-periodicity version of the renormalization idea. Any
self-similarity lives in the m-direction (see F4). Tool ceiling
documented: C=200 at m=6 exceeds 10GB (SparseMat::add linear scan).

## F4 — The self-embedding conjecture SURVIVES, two candidates (embedding/)

Faithful reimplementation (validated against Lemma 3, M_edge C=1..5, and
LOCK3 zero-birth edges — all exact). Tested A(C,m) ↪ A(C+22, m+53):

- (b) r→r·3⁵³ maps: **refuted structurally** (100% dead — forward-image
  residues never ≡0 mod 3; 3⁵³≡0 mod 3).
- (a') identity + deficit shift: **dead** (49 failures).
- (a) identity (same d, r verbatim at larger modulus): **48 matched /
  0 failed / 67 inconclusive** — zero counterexamples.
- (c) advance-one-heartbeat-then-embed: **81 matched / 0 failed / 34
  inconclusive** — best decidability, zero counterexamples, and the
  dynamically natural map (respects the flow rather than raw identity).

Honest scope: C=1..5 pairs only, oracle-capped, sampled (115 elements).
Positive-but-unproven; (c) is the live conjecture.

## Coherence picture

F1+F3+F4 fit one story: the framework's real structure lives at the
IRRATIONAL/CF level. The rational formula, the periodic ρ, and the exact
+22→+53 periodicity are all first-order shadows of an almost-periodic
(Ostrowski-graded) renormalization — exactly how Sturmian systems
renormalize in the literature (period 53/22 block, then 306/127
correction, ...). If F5 returns 359, the paper's law gets upgraded to
the irrational form, the embedding becomes almost-periodic (occasional
+54 steps where the CF corrects), and the three-distance/gapped-repeats
machinery (arXiv 2606.02071's world) becomes the native proof toolkit.

## F5 — THE DECISIVE EXPERIMENT (registered)

**Run a genuine countdown ladder at C=148 with lock3_census (true-word
tool), exact-arithmetic credits.** Measured edge ∈ {358, 359}.
- 359 → law is Sturmian-fundamental (irrational). Correct the paper's
  formula; renormalization route strengthens; register follow-ups at the
  next divergence points from beatty/task3_divergences.csv.
- 358 → the automaton's rational construction binds deeper than the
  slope; the framework needs a convergent-upgrade story at large C and
  the G2 drift concern sharpens.
Registered prediction (Fable, 2026-07-03): **359.**
Secondary: repeat at 2-3 more early divergence points; confirm
non-divergence controls (C=147, 149) return the shared value.

## v1.1 correction list (published bundle)

1. COLLATZ_PROOF.md:230 — "48 independently measured corridor widths"
   → honest phrasing: 3 full countdown ladders (C=3,4,5) + 45 widths at
   m=1 with algebraically implied cutoffs (restore the backup version's
   own caveat).
2. Add the convergent-shadow caveat to the capacity formula: exact
   agreement with the irrational law only guaranteed for C ≤ 147; true
   law past that pending F5.
3. Certificates 6 and 9 are narrative-only (no artifacts in repo).
   Regenerate and archive raw outputs under certs/ (regenerations so far
   MATCH published numbers — claims hold, receipts missing).
4. Note the periodicized-operator scope of the ρ certificates (F2).

## Next work orders (no GPU, Codex/Sonnet-shaped)

- W1: exact-credit patch to lock3_census + C=148/controls ladder (F5).
- W2: exhaustive verification of embedding candidate (c) at the smallest
  pair (C=1→23) via the backward-oracle without sampling caps; if it
  survives exhaustively, promote to formal conjecture and attempt the
  commuting-diagram proof (it follows the dynamics — likely provable).
- W3: certs/ archival job (regenerate Certificates 6 & 9 artifacts).
- W4: G3 digit-density scan (support-phase pins nonzero digits at
  positive density along scattered-exit chains) — untouched this round.

## Execution notes (for the implementing agent — binding)

1. **W1 order of operations is load-bearing.** The exact-arithmetic
   credit patch (integer/Ostrowski credits, no f64 floors) lands and is
   regression-tested BEFORE the C=148 ladder runs — a single float floor
   flipping near a convergent denominator silently poisons the one
   number this recon exists to measure. Validate the patched credits by
   reproducing the C=3,4,5 genuine ladders exactly. The C=148 run is
   invalid without its controls: C=147 and C=149 must return the
   shared (non-divergent) values or the result does not count.
2. **W2 discipline.** Exhaustive candidate-(c) at the smallest pair
   (C=1→23), no sampling caps, no oracle-call ceiling shortcuts that
   convert "inconclusive" into silence. Exhaustive survival =
   promotion to FORMAL CONJECTURE, stated precisely — not "proven."
   The commuting-diagram proof attempt is a separate later act.
3. **Ledger law applies.** Update this file (or a sibling
   IMPLEMENTATION_LEDGER.md in this directory) after every completed
   step: what ran, the command/artifact that proves it, what remains.
   Commit after every completed work item — this repo is PUBLIC; the
   self-audit publishing before the paper's v1.1 correction is a
   deliberate choice of this house (we ship our own red team), so
   commit messages should be written to be read by strangers.
4. **Registered prediction on record (Fable, 2026-07-03): the C=148
   genuine countdown edge = 359** (irrational law). If the measurement
   returns 358, that prediction is wrong and gets recorded as wrong in
   this file, same rules as everyone else. The result is the result.

## F5 AMENDMENT (2026-07-03, PRE-DATA — method only; question, prediction, controls unchanged)

The original F5 method (full countdown ladder at C=148) is computationally
infeasible: the edge sits at m≈358 and anything enumeration-shaped dies at
3^m long before that. No C=148 data exists at amendment time — this is a
method substitution, not a result-driven change. The registered elements
stand as written: binary question (edge = 358 vs 359), prediction 359
(Fable), exact-arithmetic credits mandatory, result invalid without
controls.

**Amended method — edge-witness search:**
1. The question reduces to one bit: does ANY lineage survive at
   (C=148, m=359)? Depth-first witness search with pruning (memory
   O(depth)), and/or backward search from candidate terminal states at
   m=359 using the validated backward-reachability oracle from
   embedding/. Near-edge survivor populations are tiny by definition
   (cf. the C=3 Last Survivor: a single residue).
2. **Pre-declared asymmetry:** witness FOUND at m=359 ⇒ edge ≥ 359 ⇒
   decisive for the irrational law. Witness NOT found ⇒ suggestive of
   358 ONLY if the search is demonstrably exhaustive (memoized full
   frontier or a completeness argument); otherwise the result is
   INCONCLUSIVE and must be reported as such — a null from a capped
   search does not count as 358.
3. **Method validation (replaces ladder controls, same spirit):** the
   witness-search implementation must first reproduce the known edges
   exactly — C=3→10, C=4→13, C=5→15 (witness at edge, exhaustive-empty
   at edge+1) — and then the agreement-zone controls: C=147 and C=149
   edges at their shared predicted values (witness at m=predicted,
   behavior at m=predicted+1 consistent). Only then does C=148 run.
4. **Telescoping option (couples W2 to F5):** 148 = 16 + 6·22, so six
   applications of embedding candidate (c) — if W2 proves it exact —
   map the C=148/m≈358 question to the C=16 edge at m≈40
   (M_edge(16)=40, both laws agree at 16). If the embedding is exact,
   the discrimination localizes to whether it remains exact through the
   CF-correction steps; the defect location IS the answer. W2's
   exhaustive result therefore feeds F5 directly.
5. Frontier-width calibration before committing compute: use the
   C=3,4,5 survivor-count profiles to model expected search width at
   148; if projected width exceeds feasibility even for witness search,
   report the wall honestly and fall back to the telescoping route.

## Execution round 1 results (2026-07-03) — see IMPLEMENTATION_LEDGER.md

W1 patch landed and validated (C=3,4,5 ladders reproduce exactly).
Frontier-width calibration (item 5 above) ran as designed: oracle call
counts scale ~7-8x per unit C (C=3→235K, C=4→5.46M, C=5→33.4M calls),
confirming witness search cannot reach C=148 directly — **the wall is
real, reported honestly, and the telescoping route (item 4) is the only
remaining path.** W2's own exhaustive test hit the same wall one step
earlier than hoped: (C=1,m=1)→(23,54) confirms candidate (c) exactly
(4/4, zero counterexamples) but that pair is degenerate (trivial residue
collapse); the next meaningful pair (C=1,m=4, 819 states) did not
resolve exhaustively within reasonable time/memory, so telescoping is
currently BLOCKED on W2, not W1. **F5 remains OPEN: 358 vs 359 undecided
by any method run so far.** W3 (certs/ archival) is DONE — both
certificates independently reproduced, including two headline scaling
laws (6.18×(C+1) and 3.34×(C+1)) matching to <1% at large C. W4 scoped
but not executed. Full detail in IMPLEMENTATION_LEDGER.md.

## Execution round 2 — THE DEATH SHELL (Fable, 2026-07-03)

All measurements below reproduce via `shell/shell_probe.py` (log:
`shell/shell_probe.log`, six probes P1–P6, all asserted). Everything
runs on the existing dense automaton (`embedding/automaton.py`, W1
exact credits) — no oracle, no census, no witness search. This round
came out of attempting the W2 commuting-diagram proof and finding
something better underneath it.

### F6 — The liveness mechanism is mod-3 parity steering (proof-shaped)

A backward step from residue ρ with exponent a is solvable iff
ρ·(−1)^a ≡ 1 (mod 3): the residue's mod-3 class forces the exponent's
PARITY. Within a parity, the choices {a, a+2, a+4} shift the
predecessor's mod-3 class through all three values (2^(a+2) = 4·2^a;
the preimage bases differ by ρ·2^a ≢ 0 mod 3) — so wherever the
corridor grants ≥3 same-parity exponents, a backward walker fully
steers its mod-3 trajectory and can dodge the only kill condition
(ρ ≡ 0 mod 3, unsolvable) forever. The exponent window collapses to
width ~c_k only at the corridor CEILING (backward, deficit descends
at most 1 per drop phase but climbs freely — a walker near the ceiling
is pinned there with forced moves). Prediction: death away from the
trivial class {ρ ≡ 0 mod 3} exists ONLY near the ceiling. Confirmed
(F7). Status: mechanism identified and data-consistent; the lemma
("distance > f(m) below the ceiling + ρ ≢ 0 mod 3 ⟹ live") is NOT
yet proven — the deficit-drift bookkeeping in the induction is the
open step.

### F7 — Death is a UNIVERSAL ceiling-anchored shell (P1, P2)

One-heartbeat liveness is NOT simply {ρ ≢ 0 mod 3}: a residual dead
set exists for every m ≥ 2, confined to the top of the corridor and
growing with m (C=23: 3 states / depth 1 at m=2 → 143,367 states /
depth 8 / 15.2% of nonzero-class slots at m=10, still climbing
~1.2%/level). **Keyed by ceiling-distance C−d, the dead set is
IDENTICAL — residue-for-residue — across corridor widths C=8/12/23
(checked m=2..6).** The shell S(m) is a single universal object
hanging from the ceiling; corridor width only decides where the floor
truncates it. (Narrow corridors, width ≲ shell extent, get genuine
floor interaction — C=1 differs, as expected.)

### F8 — The shell IS the capacity law (P3, P4, P5)

- **Terminal survival edge = M_edge(C), exactly, 5/5:** some (d, r=1)
  survives one heartbeat iff m ≤ M_edge(C), confirmed densely for
  C=1..5 (edges 4, 7, 9, 12, 14). The published capacity edge is
  readable off a 53-step dense forward computation in seconds.
- **Steps-invariant:** the edge is unchanged at 2 and 3 heartbeats
  (C=3, C=4) — a stable object of the automaton, not a
  one-heartbeat artifact.
- **D(m)** := min ceiling-distance of a live terminal (wide corridor)
  matches the ceil-inverses of BOTH capacity laws exactly for m=2..12.
  The two laws' D-sequences first diverge at **m=359: D_rat=149 vs
  D_irr=148** — the exact inverse of the C=148 divergence (next:
  412, 465, 518, 571). **There is no small-m shortcut**; the F5
  question in shell form is precisely "does the shell at m=359 leave
  a live terminal at depth 148, or push it to 149?"

Reframing: M_edge is not fundamentally about countdown ladders — it is
the depth at which the universal shell, descending as m grows, drives
the last terminal residue past the corridor floor. The 22/53-vs-β slope
question becomes the SHELL's descent-rate law.

### F9 — Trit-locality (P6, machine-verified)

Liveness after k steps depends only on r mod 3^(k+1): backward
solvability tests only ever read trit 0, multiplication is
local-from-below, and the /3 per step shifts trits down one — so
top-trit lifts injected at backward step j cannot influence
feasibility unless ≥ m−1 steps remain. Verified densely (all top-trit
lifts of every low-trit class have identical liveness) at four
(C, m, steps) combinations. Consequences:

1. **One-heartbeat liveness is CONSTANT in m for m ≥ 54** — the
   one-heartbeat proxy cannot see any edge above m ≈ 53. Honest caveat
   for round 1's embedding test: the big-side queries at m2 = m+53 ≥ 54
   were answering an m-independent question — candidate (c)'s 81/0
   record stands as measured (the shell is a real constraint at those
   sizes, so the zero-failure record is genuine signal, not vacuity),
   but one-heartbeat membership CANNOT carry capacity information past
   m≈53, so W2's operationalization cannot decide F5 even in principle
   at C=148 scale. The edge question at m=359 needs ≥ 7 heartbeats
   (371 steps).
2. **The C=148 search has far more structure than the round-1 oracle
   used:** at (C=148, m=359, steps=371), top-trit lift branching
   matters only for the first steps−(m−1) = 13 backward steps
   (≤ 3^13 ≈ 1.6M lift paths); after that the search branches on
   exponents only, with residues tracked mod a shrinking power of 3.
   Combined with F6-pruning (any backward path reaching a
   provably-live interior state certifies liveness immediately), the
   hardness concentrates in the marginal shell layer — which at the
   edge is exactly the question. This is the new F5 route (W7 below).

### Revised work orders (round 3, no GPU)

- **W2′ (supersedes W2's continuation):** re-pose the renormalization
  conjecture on the right object — the shell itself. Test whether
  S(m) determines/embeds into S(m+53) under a heartbeat-advance map
  (the (c)-map's analogue on shells), densely at m=2..10 vs m+... as
  far as modulus allows. The shell is universal (F7), so this is a
  C-free statement — strictly sharper than the state-level embedding,
  and dense-testable without any oracle.
- **W5 (on the books, as promised):** matrix-free power iteration for
  the ρ certificates — delete SparseMat entirely; the transfer
  operator's action is computable from two vectors of length
  (C+1)·3^m via the gather/scatter of automaton.py. Removes the
  10GB/C=200/m=6 ceiling noted in F3. Extends ρ measurements, not
  F5 — bookkeeping priority only.
- **W6 (shell growth law):** characterize S(m) — per-depth mass
  profile, boundary residue structure, and descent rate of the
  deepest layer vs the two candidate slopes (early transient is
  steeper than both; late increments decelerating toward ~0.5 at
  m=10 — not yet discriminating). Target: an exact recursion for
  S(m) → S(m+1) (one more trit of constraint + one heartbeat of
  steering). If the recursion is Ostrowski-graded, the descent rate
  IS β and F5 resolves analytically. This is the theory prize.

  **W6 first execution (2026-07-03, `shell/boundary_probe.py` + log):**
  (B1) death is HEREDITARY — live at m ⟹ parent live at m−1 (one-line
  proof: valid backward chains commute with mod-3^(m−1) reduction;
  zero violations in data, m=3..12). The shell is a monotone growing
  union of 3-adic subtrees; the recursion only needs the boundary.
  (B2) NO naive cylinder compression — newly-dead sets depend on all
  m trits; the recursion is invisible in raw trit coordinates.
  (B3) but it looks FINITE in the right coordinates: live-subtree
  types (horizon 2) at the ceiling SATURATE (19,29,39,48,52,54 —
  increments 10,10,9,4,2), and the per-level die-rate tracks the
  Sturmian credit word 10/10 (support phases = local minima, drop
  phases = local peaks). The boundary map m→m+1 behaves as a finite
  transducer driven by the credit word — a cocycle over the Sturmian
  shift. **Next: follower-set stabilization at increasing horizons
  (h=3,4) at the ceiling; if stable, extract the transducer from
  dense levels m≤13 and iterate it, word-driven, to m=359.
  VALIDATION GATES (frozen now, before extraction): the transducer
  must exactly reproduce (i) held-out dense levels (train m≤10,
  reproduce 11–13 bit-for-bit), (ii) all five known edges C=1..5 via
  the D(m) readout, (iii) the m-independence plateaus of F9. A
  transducer that fails any gate is not an instrument. If gates
  pass, D(359) is read off the iterated transducer — and 358 vs 359
  is decided by kilobytes of automaton state instead of a 3^359
  search. The extraction is Codex/Sonnet-shaped; the gate design is
  frozen here.**

  **OUTCOME (2026-07-03, same day): E1 FAILED unambiguously** — see
  IMPLEMENTATION_LEDGER (authoritative E1 run, `shell/e1_stabilization.py`
  + log). Follower-set counts roughly double per horizon at every
  tested (depth, level); no stabilization at any densely reachable
  scale. Fable's sofic read is recorded WRONG: the horizon-2
  saturation (B3a) was a window artifact. The word-modulation signal
  (B3b) stands — it never depended on soficity. Diagnosis: the
  boundary is not finite-state in raw trit coordinates — consistent
  with the irrational thesis (Sturmian objects are canonically
  non-sofic); any finite description must be CF/Ostrowski-graded
  (S-adic), not a fixed automaton. Raw-coordinate transducer route:
  CLOSED. Successor: **W6B (toy-word mechanism experiment,
  `shell/W6B_TOY_WORD_ORDER.md`)** — same automaton, credit-word
  slope swapped log₂3 → φ, whose convergent-divergence points land
  INSIDE dense reach; measures directly whether capacity follows the
  word's irrational slope or pins to its convergent, at decisive
  rows verifiable against ground truth. Registered prediction
  (Fable): the toy follows the golden slope; asymmetric evidence
  weights stated in the order.

  **W6 authoritative E1 execution (2026-07-03, `shell/e1_stabilization.py`
  + log, exactly per `shell/W6_WORK_ORDER.md`) — FAILED, unambiguously.
  E2 (extraction) correctly never attempted.** Per the work order's
  exact criterion (h=3→h=4 type count UNCHANGED, no threshold), tested
  all 9 required (delta, m0) pairs (delta=0,1,2 × m0=8,9,10) plus the
  fallback h=4→h=5 check where reachable (m0=8 only). Every pair is
  unstable by a wide margin — h3→h4 counts roughly double or more
  everywhere (e.g. delta=2, m0=9: 492→1282), and the one h4→h5 point
  available (delta=2, m0=8: 767→1174) continues growing rather than
  narrowing. This is not a threshold call: the work order's own bar
  (exact equality) is missed by hundreds of states at every point.
  **The follower set does not stabilize at any horizon (2–5) or
  corridor depth (0–2) reachable by dense enumeration (C=12, m≤13).**
  Per the work order: STOP — reported plainly, not retried against a
  looser bar. W6's transducer route is a dead end at every scale this
  repo can compute densely; the work order's own suggested fallback
  (Ostrowski reindexing) is a separate, harder undertaking, not
  attempted here. W7 is now the only registered live route to F5.
  (An earlier, non-authoritative attempt at this stage,
  `shell/transducer_extract.py`, used a self-invented threshold instead
  of the work order's exact criterion and is superseded — see ledger.)
- **W7 (F5 route 3 — the shell-guided witness search):** design per
  F9.2: 371-step backward search from (d, 1 mod 3^359) at C=148,
  depth-priority = escape the ceiling shell, F6-steering as move
  ordering, lift branching confined to the first 13 steps, exact
  credits (W1) throughout. Controls first: reproduce the C=3,4,5
  edges and the (147, 149) agreement-zone values with the SAME code
  path (per the F5 amendment's discipline — a null from a capped
  search still does not count as 358). Feasibility gate: if W6's
  shell profile shows the marginal layer at m=359 is still
  enumeration-shaped, report the wall; W6's analytical route remains.

Registered prediction unchanged (Fable, 2026-07-03): **C=148 edge =
359** — equivalently, D(359) = 148: the shell leaves a live terminal
at the floor of the C=148 corridor.

## W6B — Toy-word mechanism experiment (2026-07-03, MIXED RESULT)

Registered in `shell/W6B_TOY_WORD_ORDER.md` as W6's replacement after
E1 failed (see above): same automaton, driven by a golden-ratio credit
word instead of log₂3, chosen because its irrational-vs-convergent
divergence points land inside the dense-computable range (unlike the
real word's first divergence at m=359). T1 (port sanity) and T2 (toy
shell survey — heredity, universality) both PASSED cleanly, confirming
the toy system is a faithful structural analogue, not a degenerate
edge case. **T3/T4 (the decisive measurement): MIXED, leaning AGAINST
the registered prediction.** D_toy(m) for m=2..13 (C=23, dense) does
not track any single candidate law with an exact constant offset (the
work order's ideal case) — best-fit-offset comparison instead: the
best-fitting rational convergent (3/8) matches 10/12 rows, beating the
irrational law's 9/12. Every disagreement between D_toy and BOTH
candidates (m=3, m=11) is a shared failure, most plausibly a small-m
transient — not signal for either side. Where the candidates genuinely
differ (m=8, m=13) the convergent wins both times.

Per the work order's own pre-declared asymmetry ("a convergent-pinned
toy is STRONG evidence against 359"), **this result materially weakens
the registered C=148=359 prediction, though it does not refute it**
(the true word's α is generated by the corridor's own base-2/base-3
arithmetic — a resonance absent from the toy's arbitrary golden ratio
— remains a live reason the real system could differ). F5 stays
formally OPEN. Full detail, per-row tables, and raw data in
`IMPLEMENTATION_LEDGER.md` and `shell/toy_word/`.

**Verified + corrected (Fable, independent recomputation, same day):**
measurements reproduce exactly and are steps-invariant; but per the
run's own CSV there is only ONE discriminating row (m=8 — at m=13 the
irrational law and 3/8 agree), the whole convergent lead rests on it,
and every miss row has D_toy on the SLOW side — equally consistent
with convergent pinning or an irrational law approached from below
through a transient the toy's early divergence points sit inside (the
real system's decisive row m=359 sits far outside any transient; the
real D(m) showed none). **Capstone registered pre-data: D_toy(16),
the next head-to-head. Pinning ⟹ 6; irrational (Fable) ⟹ 7.** See
ledger verification note for full detail.

**W6B capstone (m=16), executed 2026-07-03
(`shell/toy_word/capstone_m16.*`): D_toy(16) = 6 — CONVERGENT
PINNING; the registered irrational prediction (7) is wrong.**
Controls passed (D_toy(11)=4 and D_toy(13)=5 recomputed at C=14,
matching the prior C=23 values exactly — no floor contamination);
shell depth at m=16 is 11, floor margin 3 to the C=14 floor. The
measured 6 matches the 3/8 convergent specifically and excludes both
the irrational law and the finer 5/13 convergent (both predicted 7).
With both head-to-head rows on record (m=8, m=16) favoring 3/8 and
none favoring the golden slope, the transient-from-below alternative
is no longer the more economical reading of the toy data — per the
work order's pre-declared asymmetry, further evidence AGAINST the
registered F5=359 prediction, with the real word's arithmetic-native
α remaining the one registered reason the true system could still
differ.

**Capstone independently VERIFIED (Fable, from-scratch
reimplementation, `shell/toy_word/verify_m16.{py,log}`): D_toy(16)=6,
shell depth 11, control m=13 exact — agreement complete.**

**Post-capstone assessment — the program's current best model
(F5 stays OPEN; this is inference, not measurement):** the corridor
appears to QUANTIZE TO ITS OWN RETURN MAP — a convergent denominator
is a near-identity return time of the underlying rotation (53 steps:
3⁵³/2⁸⁴ ≈ 1.0005; golden's den-8 likewise), and the toy locked to
the coarser return (3/8) while rejecting the finer one (5/13) that
better approximates its slope. Edge visibility follows from F6: only
ceiling-forced trajectories imprint the word raw, which is why the
53-pattern was originally discovered in depth-series data at the
no-new-birth edge. Coheres with E1's failure: the dead set is not
finite-state (complexity in the WHERE), while the descent rate is
convergent-locked (rationality in the HOW-FAST). Transfer to the
real system: under either a permanent lock or a scale-graded upgrade
(toy data suggests upgrading needs ≳2 full return cycles — one-data-
point conjecture), the operative convergent at m=359 is 22/53
(successor 127/306 needs m ≈ 306–612), giving **D(359)=149, C=148
edge = 358: the published capacity formula would be exact at the
decisive point — the "convergent shadow" (F1) inverted; the rational
form as the law, the irrational slope as the mirage.** Provability
upshot: capacity moves from equidistribution terrain to finite
periodic 53-block algebra — the ρ certificates' periodicized scope
(F2's worry) may be exactly right. New central theory question: the
convergent-SELECTION mechanism (what picks the lock; where it
upgrades) — answering it analytically settles F5 with no m=359
computation, and appears to be new phenomenology for Beatty corridor
systems generally. The registered F5=359 prediction stays on the
books until the real measurement, now trailing by its own author's
assessment.

## W6C — Convergent-selection mechanism (2026-07-03, three parallel designs)

Registered in `shell/W6C_SELECTION_ORDER.md`: two candidate selection
rules survived W6B (golden's lock 3/8 is simultaneously the coarser
AND the under-side choice, so golden cannot separate them), and they
map to OPPOSITE F5 answers: R-coarse → 22/53 at m=359 → edge 358;
R-under → 127/306 at m=359 → edge 359. Three designs ran as parallel
agents, each in its own directory under `shell/selection/`, results
files RESULTS_A/B/C.md. All measurements below follow the house
pre-registration discipline (laws tabulated before data; file mtimes
are the record).

**Readout correction (Fable, owned):** the order's B3 parenthetical
literals ("7/12 predicts 6; others predict 7") assumed zero offset,
contradicting the order's own registered offset protocol (fit constant
per-law offsets on agreement rows, freeze, then read decisive rows).
The toys carry a +1 offset (as W6B's did); the literals were pre-data
arithmetic errors by the order's author. The registered PROCEDURE
governs. Design B's agent correctly reported both readings and
deferred; the procedural verdict is recorded here.

**Design A (real word):** A1 — true word vs 53-periodicized word,
m=2..13, steps 106/159: 24/24 identical. But the agent caught that
the comparison is VACUOUS BY DESIGN (Fable's design error, honestly
reported): **the true word and its 53-periodicization are
letter-for-letter identical for k=0..357, first diverging at k=358**
— the same scale as the m=359 D-divergence. No experiment below ~359
letters can distinguish the words. Profound reframe: up to the
decisive scale, the real corridor is driven by an EXACTLY PERIODIC
word; the entire F5 question is the effect of ONE corrected letter
per convergent period. A2 — window slide (m=8,10; steps 53..106): D
varies by exactly ±1, positively correlated with the window's
support-count (r≈0.4) — the corridor reads its window coarsely but
genuinely.

**Design B (√2 crux):** controls pass; laws frozen pre-data;
**D_√2(m) = ⌈7m/12⌉ exactly for ALL 15 measured rows (m=2..16)** —
the under-side convergent 7/12 at frozen offset +1 fits 15/15, while
the irrational law, 3/5 (over), 17/29, 41/70 each miss exactly at the
unique separating row m=12 (measured 7 = 7/12's prediction;
triple-confirmed at C=14/16/18; independently reproduced from scratch
by Fable for m=9..13). **Verdict under the registered protocol:
R-UNDER.** Note 41/70 is also under-side and finer but den 70 exceeds
the readable window — rejected by the data, sharpening the rule.

**Design C (family sweep):** √3 — clean lock on 1/4 (UNDER), 13/14
rows, including the PRE-REGISTERED side-discriminating row m=15
(under laws predicted 4, over + irrational predicted 5; measured 4 —
a forward prediction landing). √6−1 and √7−1 — exact three-way ties
(irrational vs finest over vs finest under, identical miss-rows):
honest no-decisions; their convergents hug β too tightly for any
reachable row to discriminate. They neither test nor dent the rule.

**Unified selection law (current best, 3/3 side-calls UNDER — golden,
√2, √3 — zero counterexamples):** the corridor locks to the FINEST
UNDER-SIDE convergent whose denominator fits the readable window
(den ≲ m). Mechanistically natural: the shell can only certify the
descent its length-m word-factor guarantees from below, and the best
under-approximation with bounded denominator is exactly that object;
the den ≲ m condition IS the trit-locality window (F9).

**F5 implication (inference, F5 formally OPEN):** at m=359 the window
(~360 letters) resolves den 306, so the operative lock is 127/306 —
UNDER-side — giving D(359)=148 → **C=148 edge = 359**. The W6B
post-capstone assessment (which favored 358 via R-coarse) is
SUPERSEDED: golden alone could not separate the rules; √2 and √3
did, and both chose under. The registered F5=359 prediction returns
to leading by its author's assessment (~70%; was ~30% post-capstone,
85% at registration). The swing itself is the honest record of an
evidence-driven day.

**Context note:** non-trivial cycle lengths are quantized to the SAME
convergent ladder (3^k≈2^n forces n/k onto convergents of log₂3:
84/53, 485/306 — same denominators as the capacity story), per
Eliahou-line results already cited in the published bundle. The
trivial cycle (1: k=1, n=2) sits at the first convergent — the only
rung where the +1 correction is coarse enough to forgive. Capacity
and cycles are one CF ladder viewed from two sides.

**Open next:** W6D (analytic: prove the under-lock for golden's exact
period-8 block — template for 22/53 and the capacity lemma), and the
upgrade question (does the lock shift 22/53 → 127/306 exactly when
the window admits den 306; the toys' upgrade windows are all
dense-walled, so this is theory work, not measurement).

## W6D-G — Periodic-word ground truth (2026-07-03, one agent, `shell/underlock/`)

Registered in `shell/W6D_GROUND_TRUTH_ORDER.md` (parent plan
`shell/W6D_UNDERLOCK_PROOF_PLAN.md`). Key spec point, now empirically
enforced: the periodic comparison word for a lock p/q is the MECHANICAL
word of the convergent, not a first-q tiling (PD3 confirmed the tiled
word lands on slope 1/2, not 3/8 — the distinction is real and the
trap is armed for anyone who forgets).

**The periodic law is EXACT and closed-form: D_per(m) = ⌊(pm+1)/q⌋ —
28/28 rows across golden-per8 and √2-per12, zero anomalies, including
one confirmed forward prediction** (the form was registered from the
m≤13 tables and called the then-uncomputed golden m=16 row = 6; it
measured 6). This is P1's derivation target, now with no free
parameters. Caveat logged: exactly-periodic words show a ±1
step-count phase oscillation at isolated rows (the Sturmian words
never did); 53-step readout governs, matching all prior tables.

**PD1/PD2 (under-lock identity): REFUTED.** The true words sit at
D_true − D_per ∈ {0, +1}, never negative — golden matches its
periodic system on only 5/13 rows, √2 on 2/15, every disagreement
+1, every one rerun-confirmed. The corridor DOES read aperiodicity
below the wall: the true word earns an intermittent one-level bonus
over its convergent word. √2's bonus-off rows are exactly the
coincidence rows (pm ≡ 0 or −1 mod q); golden has two additional
bonus-off rows (m=3, 11 — the old "anomaly" rows, now identified:
they are where the true word DIPS ONTO the periodic branch). P3's
task is now concrete: prove the bonus schedule = the window's
extra-support schedule (balance/three-distance structure).

**The real system's own form, verified from shell_probe P5:**
D_real(m) = ⌊(22m−1)/53⌋ exactly, 11/11 on the agreement zone
(m=2..12) — the MIRROR (−1) variant of the toys' (+1) form,
consistent with 22/53 being an OVER-side convergent where the toys
locked to UNDER-side ones. The over/under mirror asymmetry is now a
required output of P1's algebra.

**F5, maximally compressed.** At m=359 (exact arithmetic):
- 22/53: 22·359 ≡ 1 (mod 53) → BOTH form variants give D=149 → 358.
- 127/306: 127·359 ≡ −1 (mod 306) — exactly on the coincidence
  boundary → the two variants SPLIT: +1 form gives 149 (→358),
  −1 form gives 148 (→359).
So the entire question is now: (i) which convergent is operative at
window 359 (W6C's under-selection says 127/306), and (ii) which
boundary convention its law takes there (the real system's own
measured family is the −1 form). Those two best-attested facts
combine to 148 → 359 — but combining conventions measured on
different systems is exactly the fitting-family trap this round
exposed twice, so this is recorded as a ROUTE, not a result. The
decision is now purely algebraic: P1's return-map derivation of the
exact forms, over- and under-side, settles F5 with no computation at
m=359. F5 remains OPEN.

## W6D-M — The support-cost mechanism (HYPOTHESIS, Fable, 2026-07-04)

**Statement:** in the residue-constrained window (the last ~m letters,
per trit-locality), each SUPPORT letter costs the backward walker one
level of depth and each drop is neutral, up to a system constant — so
D(m) = (support count of the constrained window) + O(1).

**Evidence tally:** slope of every measured law = the driving word's
support density; the toys' +1 bonus and the real system's −1 mirror
both reduce to window support-count arithmetic (under-side convergent
words carry FEWER supports than their true words, over-side MORE —
signs match exactly); A2's measured D-vs-support-count correlation.
**Not proven, and one honest gap:** raw window support counts
oscillate with phase while the measured laws are phase-smooth — the
steering must absorb phase, and the periodic words' ±1 step-count
oscillation is this residue showing.

**Conditional F5 route (exact integer counting, no fitting):** the
true word's first 359 letters carry 149 supports (credit sum
⌊359·log₂3⌋ = 569); the 22/53-periodicization carries 150 (credit
sum 568). The single correction letter at position 358 flips
support→drop. Under the mechanism, the true corridor at the decisive
window sits one level shallower than the periodic form's 149:
D(359) = 148 → **edge = 359.** Conditional on the mechanism lemma +
the end-anchored window convention at the real system's step count
(phase must be pinned in the derivation, not assumed).

**Derivation state (see shell/underlock/DERIVATION_NOTES.md):** the
game is now exactly posed. Backward from a terminal, the exponent
menu at depth δ with credit c is a ∈ [1, δ+c] with PARITY forced by
the residue class (F6); the unique kill is (δ=0, support letter,
even parity forced); steering the next parity costs 0/2/4 extra
exponent by the mod-9 dice. Conservation identity: depth at backward
step k equals δ_T − Σ_{j≤k}(a_j − c_j), so **D(m) = min over
strategies of the max partial sum of (a_j − c_j)** — an integer
minimax of the exponent process against the credit word. The drift
is E[a] − E[c] = 2 − (2−β) = β, since optimal constrained play
realizes the generic 2-adic valuation mean E[a] = 2 — the classic
3x+1 heuristic constant appearing as a game value. The exact ±1
boundary constants and the over/under mirror are the block-phase
structure of the max partial sum (cycle-lemma territory). P1 = solve
this minimax exactly for periodic words; P3 = the true-word window
version.

## W6E — bound-pair mechanical phase (2026-07-04, Sonnet exec, Fable verify)

Order: shell/underlock/W6E_BOUND_PAIR_MECH_ORDER.md; results
w6e/*.csv + ledger entries W6E-E1/E2/E3. All gates frozen pre-run;
three of the architect's four predictions MISSED, all in the usual
direction (structure simpler/more exact than priced).

**E1 (upper bound) — the trivial strategy wins everywhere.** Both S0
(greedy) and S1 (one-step steering) matched ground-truth D exactly on
28/28 periodic rows AND 11/11 real-system mirror rows. Mechanism
(verified at source + fixed-point algebra, not just observed): from
the terminal anchor ρ=1, forced parity is even, greedy plays a=2, and
(2²·1−1)/3 = 1 — **the greedy walker sits on the backward image of
the 4-2-1 loop forever.** It never meets class 0 (S1's steering
triggered 0 times), and its max partial sum is pure word arithmetic:
max_k Σ(2 − c_j). CONSEQUENCE: the upper bound of the capacity law
collapses to a mechanical-word discrepancy identity — no residue
number theory on the upper side at all. What remains of P1b-upper is
offset/anchoring bookkeeping (one page), not deep math. The §5a lift
cascade was never the upper bound's problem; it is exclusively the
LOWER bound's terrain (why nothing beats the loop).

**E3 (prefix tightness) — CORRECTED READING (Fable, same day, after
source-level spot-check).** The searched chains bind the candidate
bound at every prefix — but dumping their exponents shows the search
returned the ALL-2s LOOP CHAIN on every row tested (verified
directly: bfs_Dm golden m=8 → a=2 at all 8 steps). So E3 as run is
the E1 word identity measured a second time through an independent
search path — real as engine validation (and the keystone check's 0
violations stands), NOT a statement about the optimal SET. The
architect's first write-up of this result overstated it; corrected
here per house discipline. One theorem-let falls out of the
correction: binding at every prefix forces a_j = c_j +
(bound_j − bound_{j−1}) — a unique exponent sequence — so
binding-everywhere ⟺ the loop chain, and ANY other optimal chain
must dip strictly below the envelope somewhere. The open question
this creates is exactly the next experiment: is the loop the UNIQUE
optimum (rigidity total; lower bound = a uniqueness proof), or do
neutral excursions exist (and then their tax structure is the local
lemma the lower bound needs)? → W6F.

**E2 (phase pinning) — the W6D-M support differential was a
start-anchoring artifact; the conditional F5 route FLIPS.** Under the
end-anchored window (letters 12..370, matching the real 371-step
measurement): true = 149 supports, 22/53-periodic = 149 (was 150
only under start-anchoring; the 127/306 word counts 149 under both).
The counting argument that gave D(359) = 148 → edge 359 is
WITHDRAWN; under the corrected frame the same mechanism predicts
D_true = D_per at m=359 → **edge = 358 — the Architect's formula
⌊53(C+1)/22⌋ exact at C=148.** The supersession chain is now:
W6B said 358 → round-4 under-lock said 359 → round-5 support-cost
said 359 → W6E anchoring correction says 358. Fable's registered
prediction moves accordingly: 359 was at 70%; after E2 the honest
position is **lean 358 (~60/40)**, still conditional on the
support-cost mechanism lemma; the derivation (lower bound + boundary
constant) remains the only decisive instrument. Every flip is
recorded; the architect's formula has now survived the third
attempted refutation of the week.

**Program state after W6E:** UPPER = constructively done on the
measured range by the trivial-loop strategy; formalize as word
combinatorics. LOWER = keystone prefix rigidity (2^Σa ≡ S mod 3^m
projected per-prefix), now knowing equality must hold at EVERY
prefix. F5 = decided by the boundary constant that falls out of the
same derivation. No further compute scheduled; this is theory work.

## W6F — optimal-set census (2026-07-04, Sonnet exec, Fable verify)

Order: shell/underlock/W6F_OPTIMAL_SET_ORDER.md; results w6f/*.csv +
ledger W6F-F0..F3. Architect's three live predictions ALL MISSED,
same direction as the whole week: the object is more rigid than
priced.

**F1 — THE LOOP IS THE UNIQUE OPTIMUM. 24/24 rows, zero exceptions.**
Exhaustive enumeration of all optimal exponent sequences (memoized
backward DFS over the validated engine's state space; enumerator
independently brute-force-validated 6/6 rows before use), m = 2..13,
both families: n_optimal = 1 everywhere, and the one chain is the
all-2s loop. Verified by architect spot-check of f1_summary.csv.
CONSEQUENCE: the lower bound is a STRICT UNIQUENESS statement —
every admissible non-loop chain pays max partial sum ≥ D+1. Total
rigidity: the capacity game has exactly one optimal play at every
precision tested, and it is the trivial cycle. (Fable's 55% "not
unique" — missed decisively, 0/18 rows m≥5.)

**F2 — the deviation tax law.** All chains within D+2, m ≤ 8: min
tax of any a=1-containing chain = +1 on 8/9 evaluable rows; sqrt2
m=8 is a genuine +2 row (its only a=1-chains are a 3-step compound
(1,3,1)+(3,4); the +1 bucket provably empty). Tax is NEVER 0 —
uniqueness restated from the other side. The local mechanism to
formalize: exiting ρ=1 costs a−2 ≥ +2 upfront (even-forced menu),
and recoveries cap at net −1 short of full refund.

**F3 — the ±1 constant is a SIDE effect, not an anchoring effect.**
End-anchored D reproduces the established +1 law 12/12 in both
families. Start-anchoring does NOT produce the −1 mirror — it is a
≈+1 shift (D_start ≈ D_end + 1) vanishing at word-aligned m (golden:
m = 5, 8, 13 — Fibonacci, the mechanical word closing flush at
convergent denominators). The apparent −1-mirror matches were traced
to boundary-residue near-coincidence (forms differ only at
pm mod q ∈ {0, q−1}) and rejected. CONSEQUENCE for P1b: the real
system's −1 mirror form must come from the convergent SIDE
(22/53 over-side) — the constant is a side function, anchoring is a
separate additive shift. (Fable's pairing prediction — missed.)

**Program state after W6F:** capacity law = [loop achieves the word
discrepancy] + [loop strictly unique]. Upper = bookkeeping. Lower =
prove tax ≥ 1 for every excursion off ρ=1 (keystone per-prefix
rigidity; local exit cost +2, recovery cap −1 is the shape). F5
unchanged: lean 358, decided by the side-constant derivation + the
true-word bonus schedule. Fable week scorecard: ~3 hits, ~12 misses,
every miss = underpricing rigidity.

## W6G — break-it round + THE F5 COMPUTATION (2026-07-04, Sonnet exec + Fable verify/compute)

Order: shell/underlock/W6G_BREAK_IT_ORDER.md; results w6g/*.csv +
ledger W6G-G1..G5. Explicit method note: conjectures were generated
freely (cheap-generation-hard-verification); two survived, one died
usefully, one muddled, one was scope-vacuous.

**G1 — UNIVERSAL DISCREPANCY: SURVIVED EXHAUSTIVE ATTACK.** All 2,044
words of {1,2}^m, m = 2..10: D(w) = L(w) = max_k Σ(2 − c_j) AND the
all-2s loop is the strictly unique optimum, 2,044/2,044 (architect
spot-checked). The game has no content beyond word discrepancy; every
family law is classical discrepancy of its word. The ONE load-bearing
unproven statement in the whole capacity story is now the loop-
optimality/uniqueness lemma (exit ρ=1 costs ≥ +2, refund ≤ 1).

**G2 — BREAK FOUND, and it is structural gold.** h(r) ≥ 0 REFUTED
(80/144 anchors negative; e.g. sqrt2 m=5 r0=20: D=0 vs 3). Mechanism
(Fable, post-data): the game has exactly TWO fixed rays — ρ≡+1
(a=2, cost 2/step) and ρ≡−1 (a=1, cost 1/step; (2·(−1)−1)/3 = −1) —
the backward shadows of the TWO trivial cycles of 3x+1 on ℤ: the
positive 4-2-1 loop and the negative −1 loop. ρ=1 is the EXPENSIVE
throne; the negative cycle is the cheap seat; positivity is what
forces the real system onto the dear ray. The capacity law's whole
difficulty = "the terminal is the expensive fixed ray."

**G3 — side-constant guess MUDDLED** (over-side families match
neither ±1 form cleanly; bug found/fixed mid-run, muddle confirmed
real). Post-G1 this matters less: the ±1 constants are properties of
mechanical-word discrepancy sums — derive by direct Ostrowski
computation, stop guessing forms.

**G4 — true word: loop strictly unique 11/11** (end-anchored, the
real frame). Bonus-alignment framing near-vacuous at small m (true
vs periodic words differ densely below m~50; the single-defect
regime only exists near 359) — honest scope flag.

**G5 — REALITY BRIDGE HOLDS.** Archived corridor witnesses
(embedding/small_side_live_sets) sit at (d=0, r≡1 mod 3^m) at every
M_edge(C), C = 1..5, absent one step past; regenerated true-word
trajectories are the all-2s loop 4/4 (C=5 chain extraction hit an
honest 28.7M-state wall; D cross-checked). The abstract game's
extremal object IS the measured corridor's extremal object.

### THE F5 COMPUTATION (conditional on the universality lemma)

With D = L, F5 reduces to evaluating the loop-discrepancy functional
on the exact true word (integer-exact credits via bit_length, no
floats) in the PHYSICAL frame — the C=148 run is 371 = 7·53 steps
(CORRECTION 2026-07-05 per W6T-PROV: 371 is an exact symbolic
computation, NOT a census measurement — W1/W2 never reached C=148;
the original "(measured, W2)" tag here was the architect's mislabel),
window ends at position 370 ≡ 52 (mod 53). Frame
rule validated: reproduces edges 4, 7, 9, 12, 14 for C = 1..5 and
the 11 true-word ground-truth rows exactly.

**L(358) = 148 (lives at C=148); L(359) = 149 (dies). EDGE = 358.**
Anchoring-insensitive at 359 (start frame gives 149 too).

**Shadow-depth sweep:** at ALL seven catalogued divergence points
(C = 148, 170, 192, 214, 236, 258, 275; run = 53·⌈(m_irr+1)/53⌉,
window end ≡ 52 mod 53): the RATIONAL form wins every time —
L(m_rat) = C exactly, L(m_irr) = C+1. **The Architect's formula
⌊53(C+1)/22⌋ is exact at every tested divergence point.** Mechanism
readout: the corridor's own run-length quantization (multiples of
53) phase-locks every decisive window to the convergent grid — the
frame carries the rationality; the Ostrowski correction never gets
to bite at the sampled phases. Caveat (registered): the general
run-length rule is validated at C ≤ 5 and C = 148; a mid-range C
cross-check against archived corridor step counts is a cheap open
follow-up.

**F5 status: 358, conditional on the loop-optimality lemma — the
single remaining unproven statement.** Fable's final position: 358
at ~90% (from 85%-on-359 at week's start; every swing recorded).
The Architect's registered 358 stands at every divergence point
tested. The W1/W2 raw countdown remains the unconditional decider if
ever run; the game route (reality-bridged at C ≤ 5 by G5) is the
strongest conditional answer available.

## W6I — proof-shape recon (2026-07-04, Sonnet exec, parallel with W6H)

Order: shell/underlock/W6I_PROOF_SHAPE_ORDER.md; results w6i/*.csv;
ledger entries staged in w6i/LEDGER_ENTRIES_W6I.md (merged to main
ledger after W6H frees it). Purpose: pick the proof strategy for the
loop-optimality lemma. Outcome: THREE DOORS CLOSED, ONE LEFT.

**I1 — dual/potential proof: NOT VIABLE in this ansatz.** Bellman-
Ford Φ on (δ, ρ mod 3^k) converges (no negative cycles) but the
boundary condition Φ ≥ 0 with Φ(ray) = 0 cannot be posed: cost-0
edges legitimately leak off-ray because low-level classes cannot
distinguish the true 1-ray from same-class impostors — the cascade
phenomenon (§5a) reappearing as potential leakage. CAVEAT (architect):
this kills THIS ansatz (state potentials in raw coordinates); a
smarter dual — e.g. certificates built from the keystone congruence
itself — is not excluded, merely unfound.

**I2 — S-adic/Ostrowski transducer: NOT VIABLE at tested scope.**
Follower-set counts grow ~10-13× per Ostrowski horizon (WORSE than
raw trit-space's ~2×). The sofic route is now dead in both natural
coordinate systems.

**I3 — locking rule: MUDDLED, prediction missed badly (24/550 = 4%
vs 70% registered).** Convergent ownership of L(m) is fragmented and
oscillating (low-q convergents recur intermittently), not a clean
lock-until-next-denominator schedule. Liouville stress case untested
within m ≤ 300 (its next q ≈ 1.3×10⁷ — honest scope note). Real
modeling lesson banked: the relevant convergents are those of
β = ceiling − α (per-family ceiling; √5/√7 words live on alphabet
{2,3}), not of α — an earlier draft's numbers were this bug.

**I4 — lift-cascade histogram: near-tautological as designed**
(perturbing the all-2s baseline changes the next mod-3 class
immediately; 19/20 decisive at delay 1). Honestly flagged as not
testing §5a's long-range claim. Ungated by design.

**Net proof-shape verdict: the keystone prefix-rigidity route
(§5b/§8) is the ONLY live analytical path** — no state-potential
dual (in raw coordinates), no sofic/S-adic transducer, no clean
locking shortcut. The lemma is combinatorial/number-theoretic and
must be fought on the congruence 2^Σa ≡ S (mod 3^m) directly.
Architect predictions: I2 hit (55%), I1 partial (right pessimism,
wrong mechanism), I3 decisively missed, I4 n/a.

## W6H — lemma core (2026-07-04, Sonnet exec, Fable verify; ran parallel with W6I)

Order: shell/underlock/W6H_LEMMA_CORE_ORDER.md; results w6h/*.csv +
ledger W6H-H1..H5 (architect spot-checked H1/H3/H5 tables directly).

**H1 — LEMMA SUPPORTED, far stronger than predicted.** Exhaustive
layered DP (a wrong Dijkstra attempt on negative edges was caught
and root-caused first): every exact-returning excursion off the
1-ray up to length 8 costs ≥ +1 — and the true minimum is **27**
(shape (4,3,8,3,9,8,7,1), Σa−16=27, verified). Off-ray temporary
profit: none (running cost ≥ 0 throughout, P3 hit). ARCHITECT SCOPE
NOTE (reconciling with W6F-F2's measured min tax +1): H1 requires
return to ρ≡1 at HIGH precision (mod 3^{ℓ+2}); real cheap deviations
live at the window's far end where trit-locality shrinks the
required return precision to nearly nothing. The lemma's proof
decomposes: INTERIOR deviations = brutally taxed (≥27 at exact
return); BOUNDARY deviations = the ±1 window-end arithmetic. The
return-precision cost curve is W6J's centerpiece.

**H3 — UNIVERSALITY'S TRUE BOUNDARY FOUND (a real break, outside
the physical regime).** D=L holds on {0,1,2}^m (0/3276 exceptions)
and BREAKS heavily on any alphabet containing a letter ≥ 3
({1,2,3}: 1788/3276; both directions D<L and D>L). The order's
c=0-adjacency hypothesis is refuted. ARCHITECT MECHANISM READ
(post-data, registered for W6J): letters ≥ 3 make the loop's
increment 2−c NEGATIVE, so the corridor's CEILING (δ ≤ C — the wall
that never binds for {1,2}) starts binding: verified by hand on
break row "31" (loop wants g = −1, even menu [1,3] forces a=2,
δ→1 > C=0 → D=1 > L=0). Conjecture: D=L ⟺ the loop's running sum
never dips below 0 ⟸ alphabet ≤ 2. The real word ({1,2}, since
α < 2) sits inside the safe region INTRINSICALLY — the trivial
cycle's rate dominates the credit alphabet. Universality is a
threshold phenomenon, not a triviality — and the threshold is
exactly the loop's own exponent.

**H2 — two-ray model as specified: MUDDLE** (30.2% vs 90%; missing
exit-cost-to-target term, counterexampled). Sub-prediction CLEAN:
D(anchor ≡ −1) = 0 on 18/18 (the negative-cycle cheap ray confirmed
exactly). Model repair queued (W6J).

**H4 — no universal two-case ±1 rule** (55/1053 keys internally
clean; clean phases are convergent-specific). The constant resists
closed form; post-universality it is COMPUTABLE per case (the F5
route used exactly that), so this is a naming problem, not a
blocking one. Two honest bug catches en route (β-fraction; phase
drift).

**H5 — FRAME RULE: 48/48 EXACT (architect recount confirmed).**
Archived lock3_census countdown ladders at C = 3..50: M_edge(C) =
⌊53(C+1)/22⌋ at every point, including both 53-multiple boundary
crossings (C=21, 43). The F5 computation's last registered caveat
(mid-range frame rule) is CLOSED. The Architect's formula is now
receipt-exact at C = 1..50 (dense) and at all 7 catalogued
divergence points through C=275 (W6G sweep).

## W6J + architect audit — CONVENTION SEAM FOUND (2026-07-04)

W6J ran clean mechanically (ledger W6J-J1..J4) but the architect's
verification pass found a structural problem that RETRACTS part of
W6H-H3 and quarantines part of W6J:

**The seam:** H3's L functional (loop_discrepancy, ascending over
the word as written) and the game engine's letter consumption
(anchor_steps=m wiring) were never proven to use the same direction
— and CANNOT be distinguished by any existing validation row,
because every row ever validated (all-2s, all-0s, {1,2}/{0,1,2}
words, periodic families) has loop increments 2−c ≥ 0, where
running sums are monotone and prefix-max = suffix-max = total for
EVERY order. Direction bugs are invisible to a validation suite
made of order-insensitive rows. The moment letters ≥ 3 create
negative increments — exactly the rows where all "breaks" were
reported — the functionals diverge (verified concretely: word "13"
has L=1 as-written, L=0 reversed; and the census's own D=0 for that
word is inconsistent with as-written consumption, which dies at
budget 0 on the first letter).

**Status changes:**
- W6H-H3 {0,1,2} clean result: STANDS (order-immune).
- W6H-H3 {1,2,3}/{0,1,2,3} "universality break": RETRACTED TO
  UNRELIABLE pending convention-pinned redo. The architect's ceiling
  mechanism (§10b conjecture) and its hand-verification: WITHDRAWN
  (the hand-check assumed a ceiling constraint the engine does not
  enforce — and whether the TRUE corridor object enforces it for
  c ≥ 3 words was never defined by any measurement; both variants
  must be exposed).
- W6J-J1 biconditional MISS: QUARANTINED (tested against the
  unreliable census).
- W6J-J2 curve [1,10,2,5,5,16,7,19,19,27]: REJECTED as reported —
  non-monotone in t is logically impossible under nested return
  precisions (1 mod 3^{t+1} ⟹ 1 mod 3^t); per-t implementation
  inconsistency, redo with a nesting assertion.
- W6J-J3: STANDS (ord(2,3^m)=2·3^{m−1} verified m=4..8; Σa pinned
  unique in-window from m≥4; tax monotone in Σa−2m — the
  interior-rigidity backbone is intact and is this round's real
  positive).
- W6J-J4: STANDS as an honest MISS (order-immune inputs).

**Lesson (generalizes E2):** conventions are where this program
bleeds. A validation suite must include rows that BREAK under every
symmetry the implementation could silently choose — asymmetric
words are now a mandatory validation class. → W6K (convention
pinning + redos).

## W6K — convention pinning + redos (2026-07-04, Sonnet exec, Fable verify)

Order: W6K_CONVENTION_PINNING_ORDER.md; ledger W6K-K0..K3; all work
under w6k/ with a fresh canonical engine (Path C) gated by
hand-derived asymmetric validation rows.

**K0 — the bug, pinned to the line.** Path A (e1_walkers — the
instrument behind E1, the F5 computation, and the divergence sweep)
is CANONICAL-CLEAN, 24/24 against hand-derived rows. Path B
(f1_engine_ext.compute_D_and_optimal_set / engine.bfs_Dm — the
census engine behind W6F/W6G-G1/W6H-H3/W6J) consumes letters in
REVERSE order (ascending from window start; f1_engine_ext.py:101-106,
254-255, inherited from engine.py:130-136, 196-199). Scope
annotation for prior rounds: Path-B results are true statements
about REVERSED words — exactly equivalent for order-immune classes
({1,2}, {0,1,2}, totals) and for reversal-closed families
(mechanical words), which is why every headline conclusion
(G1 universality on {1,2}, F1 uniqueness, the family laws) SURVIVES
with at most a relabeling; only the letters-≥3 rows ever diverged.
Path C (fresh, canonical, 24/24) ran all redos.

**K1 — UNIVERSALITY IS TOTAL. The H3 "break" was 100% the order
bug.** Canonical census, 25,116 words over {1,2,3} and {0,1,2,3},
m ≤ 7: **D_free = L on every single word. Zero breaks.** There is
no alphabet boundary. The ceiling-ON variant breaks D=L on 39.38%
(so the ceiling-free game is the universality object; the two
variants coincide on the real word's {1,2} letters, so nothing
about the real system changes). Architect predictions: (a) HIT,
(b) HIT at 45% — the humble number paid, (c) MISS (ceiling
biconditional dead under both variants, K3: 708 and 10,599
counterexamples — the §10b mechanism is fully refuted, not just
convention-tainted).

**K2 — corrected return-precision cost curve (J2's redo):**
[1, 2, 5, 5, 7, 7, 15, 19, 22, 27] for t = 1..10 — nondecreasing
(assertion enforced), t=1 value 1 (matches F2), t=10 value 27
(matches H1 exactly). Root cause of J2's impossible curve: per-t
DPs merged distinct high-precision states when reducing modulus
mid-recursion; fix = one shared high-precision DP with per-t
readout. **The interior tax law, now trustworthy: ~2.7 exponent
per trit of required return fidelity, with plateau structure
(5,5 and 7,7) worth deriving.**

**Program state after W6K:** the empirical theory is at its
cleanest ever — (1) D_free(w) = max_k Σ(2−c_j) for EVERY word over
every alphabet tested, certified conventions; (2) loop strictly
unique on everything canonical-checked so far; (3) Σa pinned by the
order gap (J3); (4) interior tax curve monotone 1→27. The proof
targets are now exactly three: universal loop optimality
(word-independent), the per-trit interior tax, the window-end
boundary term. Instruments: canonical Path C for all future
censuses; Path A already canonical; Path B retired for
order-sensitive work. Validation law: every suite must include
asymmetric rows.

## W6L — canonical consolidation (2026-07-04 night, Sonnet exec, Fable verify)

Order: W6L_CANONICAL_CONSOLIDATION_ORDER.md; ledger W6L-L1..L4.
Architect independently replayed the load-bearing supersession claim
before accepting it (see L2).

**L1 — TOTAL RIGIDITY RECERTIFIED: 2,085/2,085.** Loop strictly
unique on {1,2}^1..10 exhaustive + 28 periodic + 11 real-word rows,
all canonical instruments, tie-detection capability itself validated.
The Path-B annotation is closed; nothing in the headline record
rests on the reversed-order engine anymore.

**L2 — SUPERSESSION: H1's "27" and K2's curve both fall to a deeper
instrument.** The new exact shrinking-modulus ladder DP (zero
representative error by construction, triple-gated) refutes
W6K-K2's curve at 6/10 points via two mechanisms: length walls
(cheaper witnesses beyond K2's cap) and REPRESENTATIVE FABRICATION —
K2's t=9/10 argmins fail exact-integer replay, and H1's published
minimum chain (4,3,8,3,9,8,7,1) returns at precision 7, NOT 10
(ARCHITECT-VERIFIED by direct exact replay: final ρ = 1224943075 ≡ 1
mod 3^7 only; K2's "cross-check against H1" was two copies of one
artifact). **Exact curve of record (len ≤ 14): t=1..12 →
[1,2,3,5,7,7,11,12,12,16,21,21]**; rate ≈ 1.75-2.5/trit; plateaus
(5,6),(8,9),(11,12), each a literally identical chain serving the
pair. H1's claim scoped down to: exact-return-at-t=7-within-length-8
costs 27 (still true, wrongly labeled t=10 before). Guarantee-zone
law now enforced in the instrument (t + d ≤ T). Lesson logged: a
cross-check must be INDEPENDENT — verifying an artifact against its
own copy certifies nothing.

**L4 — ADDITIVITY IS DEAD, and the killer is the order gap itself.**
0/246 excursion-pair embeddings additive; every delta positive
(+5..+67, super-additive). Mechanism PROVEN exactly: a pinned
letter-block admits entry from exactly ONE residue class mod 3^len,
and the unlock exponents are spaced 2·3^5 = 486 = ord(2, 3^5) —
**the same order-gap that pins Σa globally reappears as the
coupling constant that forbids local composition.** One object, two
faces: rigidity when you read it globally, coupling when you try to
cut it into blocks. CONSEQUENCE for the proof: P-II cannot assemble
by relocatable excursions; the lower bound must be argued at the
whole-window congruence level (which J3's pinning already supports).

**L3 — J4's premise inverted; NO third structure.** 95.7% of
two-ray-model mismatches are UNDERpredictions — real optimal chains
cost MORE than descent+ride (the junction pays the L4 coupling; the
W6J digest's "overprediction/cheaper" reading was the sign error,
corrected here). Exhaustive 1- and 2-step fixed-point hunt mod
27/81 (including negative-cycle shadows): zero exact touches,
anti-enrichment on shadow classes. And the structural surprise:
**83.6% of true optimal chains at generic anchors touch NO ray at
all** — the ray-itinerary picture is anchor-1-specific, not the
generic geometry. Two rays, heavy coupling, nothing hidden.

**Program state after W6L:** empirical foundation final —
rigidity total (L1), tax curve exact (L2), composition impossible
(L4), no hidden structure (L3). The proof must be GLOBAL: one
congruence argument over the whole window via the order gap, not
excursion bookkeeping. That is precisely the shape the keystone
route (§5b) always had; the program has now eliminated every
alternative shape.

## W6M — global-lemma empirical map (2026-07-04 night, Sonnet exec)

Order: W6M_GLOBAL_LEMMA_MAP_ORDER.md; ledger W6M-M1..M3 (with the
final digest table). All witnesses independently re-derived; a real
int64 overflow past M_exp=24 caught in the L2e ladder and replaced
with a fresh exact-bigint instrument (gated, 0 mismatches vs L2e on
shared depths).

**M1 — THE FLOOR-POINT LAW: 519/519, exceptionless.** Every
non-loop chain within L+1, across 442 words (m=4..8), satisfies
g(k*) ≥ g_loop(k*) at the loop's own binding prefix k*. Zero
violations. **The loop's argmax prefix is a universal floor point —
the anchor the global induction gets to stand on.** (Prediction (a)
dissolved definitionally: sharp reading tautological, coarse 75.9%.)

**M2 — the departure→floor table (38 rows, the decisive artifact):
f(j) ≥ 1 on all cells** — the strict +1 is departure-time-
independent. But the "leaving late is cheaper" monotone law MISSED:
the real shape is a flat ceiling with sparse single-prefix
undercuts (dips to f=1 at specific j, back up after). Those dip
positions are the boundary term's empirical fingerprint — their
correlation with word structure is the next round's target.

**M3 — ladder walls: t=13 → 31, t=14 → 32 closed; BUT the curve is
still length-capped at high t** — t=11, 12 drop 21 → 19 at length
15 (shared witness), so the published values at t ≥ 11 are UPPER
envelopes, converging from above; t ≤ 10 unaffected. Curve of
record (len-capped, honest label): t=1..14 →
[1,2,3,5,7,7,11,12,12,16,21→19?,21→19?,31,32] pending length
convergence. Prediction (60% stability): MISS.

**Program state:** the global lemma now has (i) an exceptionless
anchor point (M1), (ii) departure-independent strictness (M2),
(iii) a tax curve converging from above with the true asymptotic
rate still open (M3). Next: dip-position fingerprinting, length
convergence, floor-point law at full generality (all budgets), and
the first mechanism check — is the floor forced by the prefix-
projected congruence at k* alone?

## W6N — floor mechanism + convergence (2026-07-04 night, Sonnet exec)

Order: W6N_FLOOR_MECHANISM_ORDER.md; ledger W6N-N1..N4 + digest.

**N2 — THE ONE-POINT LEMMA (lead finding, prediction inverted in
the best direction).** On 40/40 words, the minimum max-partial-sum
over ALL residue-feasible k*-prefixes — mod-3^k* congruence/parity
only, no suffix feasibility — equals g_loop(k*) EXACTLY. The set of
prefix states below the floor is EMPTY. The floor is a one-point
congruence fact; the global induction needs NO forward invariant.
Combined with max_k g ≥ g(k*), this reduces the ENTIRE capacity
law's lower bound to one finite counting statement: no parity-legal
k*-step walk from ρ=1 ends cheaper than the all-2s walk.
Independent unpruned brute force reproduced it on spot-checked
words; architect hand-checked one case in-session.

**N1 — floor law at full generality: HIT.** 2,956 chains within
L+3 across 240 words exhaustive: ZERO violations of
g(k*) ≥ g_loop(k*). The anchor is exceptionless at every budget
tested.

**N3 — dip signature found (prediction missed, better one
surfaced): 9/9 dips sit ≤ 1 step from a support letter.** The
boundary term's fingerprint is support-adjacency, not
suffix-credit-runs.

**N4 — curve of record (converged where stated):** t=10: ≤15
STILL-OPEN (a width-4 plateau BROKE at len 18 — "two consecutive
lengths agree" is REFUTED as a convergence certificate, the round's
methodological finding); t=11: 19; t=12: 19; t=13: 19 (down from
31 in one length step); t=14: open interval [25, 32] (nothing ≤ 24
exists at len ≤ 18, complete and sound). Star witness: a len-15
chain (4,3,2,5,4,3,1,3,2,2,1,4,9,5,1), cost 19, landing ≡ 1 mod
3^13 exactly — a FOUR-TRIT plateau (t=10..13) with a ≥ +6 cliff at
t=14. The tax curve's true shape: long flats punctuated by cliffs —
Ostrowski-flavored, mechanism open.

**Round verdicts vs frozen: N1 HIT (75%), N2 inverted-MISS (the
result is stronger than predicted), N3 MISS with a better law
found, N4 3-of-4 clauses HIT.** Peak RSS 4.4GB; honest walls:
t=14's [25,31] at len 15-18; t=10 below 15 at len ≥ 19.

## W6O — The one-point lemma at scale (2026-07-04, Sonnet exec)

Order: shell/underlock/W6O_LEMMA_SCALE_ORDER.md; ledger W6O-O1..O3.
This round scaled N2's "prefix-alone-suffices" claim from 40 sampled
words (m=5..7) to the real domain: true-word windows m=2..53, both
mechanical families one period past ground-truth, and ALL {1,2}^m
words exhaustively to m=12.

**O1 — THE ONE-POINT LEMMA BREAKS AT SCALE (lead finding, frozen
prediction falsified).** 26 exact, independently-replayed breaches
out of 8,280 prefixes tested — ALL at long windows: true-word breaks
sharply at m=29 (min=11 stays pinned there through m=53 while L
climbs 12→22) and sqrt2-per12 breaks at m=24 (exactly one period
past its ground-truth table, min=13<L=14). **Zero breaches among all
8,190 exhaustive {1,2}^m words, m≤12** — the lemma is total on the
short-word space and fails only once windows reach real-system
length. Both flagship breaches (true-word m=29, sqrt2-per12 m=24)
were independently hand-traced with a second, freshly-written
implementation sharing no code with the production script — every
step confirmed parity-legal, same numbers. Mechanism: an early
moderate exponent (a=4..6) buys a favorable residue class that a
long run of cheap a=1 steps then rides for the rest of the window —
a detour only profitable once the window is long enough to harvest
it. **Consequence: N2's proof-simplifying reduction (the lower-bound
anchor as a pure one-point congruence fact, no suffix/forward
information needed) does NOT survive to the scale the real proof
needs.** The global lemma (D=L) itself is not contradicted — only
the shortcut mechanism proposed for its anchor inequality. The
whole-window congruence argument (§12d, L4's super-additive coupling)
is reinstated as necessary past a length threshold newly located at
m≈24-29.

**O2 — support-adjacency biconditional, both halves confirmed.**
Widened scope (m≤11, true-word rows added for the first time): 2×2
table over 195 positions, 20 dips. Forward (dip⟹adjacent): 20/20 =
100%. Reverse (adjacent⟹dip): 20/147 = 13.6% — adjacency necessary,
far from sufficient, exactly as predicted. dist=1 positions (support
letter immediately follows) are ~4.4× more likely to be dips than
dist=0 positions — the only separating signal found; no fully
sufficient condition identified.

**O3 — N4's wall cells closed.** t=14: CLOSED exactly to 31 (was
open [25,32]) — same witness at len 15 and len 16, cliff height 12
from the t=13 plateau value of 19 (more than double the predicted
minimum of 6). t=10: confirmed stable at 15 through len 19 and 20
(same witness as len 18).

**Round verdicts vs frozen: O1 MISS/BREACH (85% predicted, falsified
— leads the round), O2 both HIT (70%/70%), O3 HIT (65%, cliff height
12 vs predicted minimum 6).** Peak RSS 2.27GB; zero honest walls —
every O1/O2/O3 cell completed inside its wall-clock/RSS budget. All
26+20+4 witnesses passed independent exact-integer replay.

## W6P-URGENT — UNIVERSALITY BREAKS IN THE GAME AT m=29 (2026-07-05, status: reality-check in flight)

The W6O falsification sweep's breach was completed to a full chain:
a ceiling-legal (g ≥ 0 throughout), exact-replayed, independently
re-derived chain beats the loop on the true word at m=29 — max
partial sum 11 vs L = 12. The m=13..28 gap was closed en route
(agrees exactly with the mirror law on all 16 rows; the break is
clean at 29). Game-D pins at 11 through m=53 while L climbs to 22.
Every game-derived conclusion at m ≥ 29 — including the F5-via-L
computation — is SUSPENDED pending the reality check below.
Universality's certified scope is now: all short words (m ≤ 12
exhaustive), all family/true-word rows m ≤ 28.

**ARCHITECT'S CONTRADICTION FLAG (the decisive observation): the
game verdict contradicts archived corridor reality.** Game-D = 11
surviving to m = 53 would mean M_edge(11) ≥ 53; the archived
exhaustive census measured M_edge(11) = 28 (formula-exact,
w6h/h5 row C=11). Both cannot describe the same object. Either the
counterexample translates to a real integer trajectory the census
somehow missed (extraordinary claim, extraordinary checking), or
THE GAME MODEL DIVERGES FROM THE CORRIDOR at depth ≈ 29 — a missing
translation term (floor semantics, phase coupling, or deficit
dictionary), which the G5 reality bridge (validated only at C ≤ 5)
never probed. W6Q-REALITY is running the forward integer replay
under the census's own definitions to decide (a) vs (b).

F5 status honesty: the game-side support for 358 is withdrawn until
the dictionary is resolved; the corridor-side evidence (formula
receipt-exact at every measured C, 1..50 + divergence-sweep frames)
stands on its own measurements.

## W6Q-REALITY — verdict: MODEL DIVERGENCE; the corridor stands (2026-07-05)

Independent re-derivation (fresh code, no reuse) confirmed both
halves: (1) the W6P chain IS a genuine integer trajectory — 839 → 1
in 29 odd steps, forward exponents matching the backward
construction exactly; (2) under the census's OWN convention
(rust/lock3_census.rs: credit_at_step(k) indexed from the
trajectory's root, no absolute anchor), its deficit sequence is
max = 1, min = −11 — a plummeting DESCENT, not a hover. The
"11-hover" existed only inside the game engine's universal
anchor_steps=53 end-anchor (w6e/engine.py, a declared house
convention). The end-anchored scoring agrees with root-anchored on
28/29 letters (near-periodicity) — one phase step of divergence,
exactly enough. M_edge(11) = 28 stands UNCONTRADICTED; the archived
corridor base survives its strongest-ever attack.

**THE THIRD CONVENTION SEAM (E2: window phase; W6K: word order;
W6Q: root-vs-end anchoring), and the law generalizes again:** the
game's results are true statements about the END-ANCHORED GAME;
their corridor meaning is exactly as validated by corridor data —
ground-truth rows m ≤ 28, edges C ≤ 5, and H5's 48/48 frame-rule
match at C = 3..50 — and NOT beyond. The near-periodicity of the
credit word HID the anchor mismatch below m ≈ 29 (the same
mechanism that hid the W6K order bug below letters ≥ 3): every
validation row lived where the conventions coincide.

**Status changes:**
- W6P's "universality breaks" — RE-SCOPED: universality of the
  end-anchored game fails at m ≥ 29; the CORRIDOR's capacity law is
  untouched (and its formula remains receipt-exact at every C ever
  measured, now including surviving this attack).
- The m ≥ 29 suspension resolves into a RE-GROUNDING program
  (→ W6R): re-pose the game with root-anchored credit words (the
  census's convention IS the convention), re-verify the trinity —
  universality, loop uniqueness, floor-point law — under the
  corrected dictionary. Registered architect prediction: all three
  HOLD at all m under root-anchoring — 70%.
- F5: rests on its corridor receipts (48/48 ladders + the
  divergence-point frames) — the game's testimony stays withdrawn
  until W6R re-grounds it. LOCK4-B1's climb DPs get the same
  dictionary scrutiny on report.
- VALIDATION LAW, final form: a convention is only pinned when a
  validation row exists that BREAKS under every alternative
  convention. Root-vs-end anchoring never had one until m = 29
  supplied it.

## W6R — root-anchored re-grounding (2026-07-05, verdict: the break is real in the corrected frame)

Ledger W6R-R1..R4 + digest. Architect's 70% "root-anchoring restores
the trinity": 1/3 — MISS on the parts that matter.

- **R1 (leads): D_root < L_root at m = 29..40 on the true word**
  (clean m ≤ 28; independent re-derivation 6/6) — the m=29 break is
  NOT an end-anchor artifact; it survives the census-matching
  convention. Analogues: golden m=30, sqrt2 m=24 (R3, same at the
  per-prefix level).
- **R2: loop uniqueness HOLDS, 39/39 (m ≤ 16), 3-way independence
  gate.**
- **R4: the frame-alignment explanation for H5's 48/48 is REFUTED**
  (2/8 extremal windows align, no constant offset). H5's value
  match stands, mechanism unexplained — the F5 transfer question
  stays open.

**Architect's standing contradiction (still live, sharpened):**
a root-anchored cost-11 chain at m=29 implies M_edge(11) ≥ 29;
the archived census measured 28. The game↔census divergence is
REAL and STILL UNLOCATED — W6R matched what it believed to be the
census convention and the contradiction persists, so the remaining
difference lives in a census rule the game still lacks (bankruptcy/
negative-deficit termination, trit-vs-step depth units, credit
offset, or the countdown's own scope). → W6S-CENSUS: the W6Q
surgical pattern applied to W6R's witness — verbatim census
recursion vs game score, step by step, until the divergent line is
named. Until then, the game remains impeached as a corridor model
above m ≈ 28 while the corridor's own receipts stand.

## W6S-CENSUS — the three-conventions diagnosis (2026-07-05)

Ledger W6S-CENSUS. Verdict: DISAGREE, uniformly — and the mechanism
is structural, not a switch at m=29. **Three non-equivalent
conventions share one formula:** (1) the game's g — backward,
TERMINAL-anchored; (2) the census's d — forward, ROOT-anchored
(Key(0,0)); (3) M_edge — forward, BIRTH-anchored (next_depth −
birth_depth, lock3_census.rs:2632-2637). W6R's "root-anchoring"
re-indexed (1)'s letters only; (1) vs (2)/(3) were never the same
object at ANY m (uniform disagreement m=20..29). The witness chain
under literal census semantics at C=11: legal 8 steps, then
LOWER-BOUND BANKRUPTCY (d < 0) — a census rule the game never
modeled; max d ≤ 1 throughout (never near the ceiling).

**PROVENANCE ALARM (corroborating W6Q's side-note): M_edge(11)=28
appears to be formula-derived, not independently m-swept — genuine
sweeps exist only at C=3,4,5.** If confirmed, H5's 48/48 was
partially formula-vs-proxy, and the corridor law's measured base is
C ≤ 5 + the reserve scans + the verified range — NOT C ≤ 50. This
is the verify-the-receipts lesson at the worst location; a full
provenance audit of the corridor record (measured vs derived, C by
C, with the producing tool named for each number) is now top
priority (→ W6T-PROV), alongside the reconciliation (→ W6U-RECON:
one capacity statement — census tree conditioned on reaching
valid1 at exactly depth m — implemented, validated at C ≤ 5
against genuine data, then evaluated at the contested m).

Status: the game is a well-defined object with its own laws
(uniqueness, tax curves, the m=29 structure); its corridor meaning
is UNDEFINED pending W6U's reconciled statement. The corridor
formula stands on: genuine C ≤ 5 sweeps, the reserve scans
(max reserve 23 through 250M), and the 2^68-scale verified range —
its C = 6..50 receipts are in escrow pending W6T.

## W6T-PROV — Provenance audit: the escrowed C=6..50 receipts are the
m=1 proxy, mislabeled (2026-07-05)

Ledger W6T-PROV. Verdict: **the alarm is confirmed, and it is a
regression, not a discovery.** Traced `w6h/h5_frame_rule_crosscheck.py`
to its real source: `data/runs/lock3_C{1..50}_N2000_residue_m1_
lineage_cohorts_*/` — genuine, dated (2026-05-23/24) Rust `lock3_census`
runs (confirmed not fabricated: real run.log/live_events.jsonl/CSV at
C=11, `lock3_census.rs:2632`'s birth-anchored lifetime formula matches
W6S-CENSUS's own citation exactly). **But `residue_mod_power=1`
throughout** (`lock3_census.rs:1267-1268`: modulus capped at 3¹ for the
whole depth-2000 run) — a coarse compatibility proxy, never swept to
the true desert edge. `LOCK3_PRECISION_COUNTDOWN_GRID.md`, verbatim:
**"Only `m1` has been checked for C6-C50 in this series."** Only
C=1..5 have genuine dense per-m sweeps to the zero-birth edge
(`LOCK3_BIRTH_INVARIANT_AUDIT.md`) and archived witness sets
(`embedding/small_side_live_sets/*.npz`, C≤5 only).

**This exact tiering already existed once and was dropped.**
`renorm_check/beatty/task1_measured_widths.csv` (pre-dates W6) labels
C=3,4,5 `GENUINE_full_sweep` and C=6..50
`INFERRED_m1_only_plus_linear_countdown_assumption` explicitly, tracing
the overclaim to `COLLATZ_PROOF.md:230`'s "48 independently measured
corridor widths... without exception" — its own superseded predecessor
`COLLATZ_PROOF_backup_v2.md` had the honest caveat ("C=6-50: m=1
only"), dropped in the polished version. W6H-H5 (2026-07-04)
re-derived the same 48 numbers from the same raw archive and
re-introduced the identical overclaim ("48/48 EXACT... never
individually checked before"). Independent from-scratch re-verification
this round (`w6t_prov/t1_provenance_table.py`, not reusing h5's script):
**C=1..5 MEASURED (5/5), C=6..50 DERIVED (45/45, 0 mismatches) —** the
proxy agrees with the formula everywhere, which is exactly why the
mislabel was easy to miss (no numeric daylight, only a methodological
gap).

**C=148 (F5): confirmed OPEN, not a second measured point.** W1's own
entry: the C=147/148 countdown ladder was killed before completing;
W2's telescoping route never reached C=148 either ("NOT yet attempted
— W2's own exhaustive test hit its own tractability wall"). F5
COMPUTATION's "(measured, W2)" parenthetical (line ~828) is a mislabel:
371=53⌈360/53⌉ is the run-length rule applied to the formula's own
m_irr(148), and L(359)=149 is an exact but SYMBOLIC loop-word
discrepancy computation, not a census read — the ledger's own
B1.3-prep entry says plainly "D(m=358 or 359) was NOT computed —
genuine wall." The same real-word/measured-word conflation recurs at
W6E-E2. No `lock3_C147/148/149` directory exists anywhere in the repo
(confirmed by background sweep).

**Background sweep found nothing that changes the verdict:**
`data/runs/corridor_bound_*`/`k53_capacity_*`/`macro_corridors_*` are
an unrelated investigation (real orbit integers, different C entirely);
`certs/product_automaton_*` are genuine dated runs of a DIFFERENT
quantity (extinction-heartbeat scaling, Certificate 9), not M_edge, at
C up to 10,000 — real data, wrong quantity, must not be cited as
corridor-capacity corroboration; `LOCK3_CUTOFF_NUMBERS_CNEG20_TO_C50.txt`
is a closed-form table presented without a run-log.

**THE MEASURED BASE:** C = 1,2,3,4,5 genuinely measured (`lock3_census`,
dense per-m sweep to the true desert edge, 2026-05-24, +
`embedding/small_side_live_sets/*.npz` witnesses). C = 6..50: real runs
exist but only at a coarse m=1 proxy that cannot discriminate the
formula from an independent measurement — formula-consistent, not
formula-independent. C=148 and the whole 147..149 neighborhood: OPEN,
no exhaustive measurement exists; reported numbers there are exact
conditional/symbolic computations, not physical measurements. The
250M-integer reserve scan (max reserve 23, 2026-05-21) is a separate,
genuine, already-corroborated evidence line.

**Downstream re-scoping needed:** H5's "48/48 EXACT" (drop to "5/5
measured exact + 45/45 formula-consistent proxy, not independently
tested"); `COLLATZ_PROOF.md:230` (restore the backup version's
caveat — this is v1.1 correction item 1, registered 2026-07-03,
still unapplied); SYNTHESIS.md's F5 COMPUTATION "(measured, W2)"
parenthetical (remove/correct); W6E-E2/LOCK4-B1.3's "real 371-step
measurement" phrasing (reword — "real word" ≠ "measured"); any future
citation of "C≤50 verified" (say "C≤5 verified, C=6..50
formula-consistent at a coarse proxy" instead) — this binds W6U-RECON
when it runs.

**Honest walls:** none computationally (every check under a second,
negligible RSS); no new measurement was taken (the C=6..50 status
resolved cleanly from existing primary-source text, not from ambiguity
a rerun would settle). Decisive artifacts:
`shell/underlock/w6t_prov/t1_provenance_table.py` (+ `.csv`, 50 rows,
+ `.log`). No commits, per house rules.

## LOCK4-B1 — bridge economics, measured exactly (2026-07-05)

Ledger LOCK4-B1.0..B1.4; artifacts shell/bridge/b1/. Scope note:
game-frame results (the W6S three-conventions caveat applies; the
corridor-form inequality awaits W6U's reconciled object) — but
B1.0's anchor is REAL-integer data (May scans reproduced 8/8
fields; the [1,1]/ghost-−1 growth segments confirmed LITERALLY
identical to the game's cheap ray ρ≡−1, not analogous).

- **B1.1**: phase-relaxed climb cap, closed form climb(k) =
  k − 2·supports(k), validated; value at the 306-letter bridge:
  **50** — under the 149 requirement with no residue arithmetic at
  all. (Architect's distrusted ~52 estimate: close; both frozen
  HIT.)
- **B1.2 (the gem)**: residue-legal max climb over ANY 53-letter
  window, exact, all launch classes: **−6. Net climbing across even
  one full heartbeat is impossible — every legal chain loses ≥ 6
  per 53 letters, from every launch.** (A pruning-soundness gate
  caught and fixed a real bug first; k=306 exact walled — honest
  brackets reported.)
- **B1.3**: the assembled first-bridge inequality HOLDS — slack
  ≥ 237 (conservative) / 132 (exact k=53 control) vs frozen ≥ 30.
  Stated caveats: LHS a lower bound; RHS (149) is L-based.
- **B1.4**: crash tax exceeded its prediction — maximal-climb
  witnesses don't descend after landing, they DIE outright (no
  legal move) within 1-3 steps. Not a tax; a cliff.
- **Side observation (game-fact, flagged for W6U re-grounding):**
  the agent independently reproduced D < L from m=29 and extended
  toward m≈130 — game-D grows ~4× slower than L there. The game's
  own capacity law changes slope at m≈29; corridor meaning pending
  the reconciled object.

Lock 4 status: the red team's demanded inequality now exists in
measured form with wide slack, anchored at one end in real orbit
data (May scans) — its corridor-form restatement is the remaining
step, blocked only on W6U's dictionary.

## Architect's note on W6T-PROV (Fable, 2026-07-05) — owning the regression

The provenance audit's sharpest finding is about process, and it
runs through the architect: the repo's OWN first-day recon
(task1_measured_widths.csv, 2026-07-03) had already tagged C=6..50
as INFERRED_m1_only, and v1.1 correction item 1 was registered to
fix COLLATZ_PROOF.md:230's phrasing — and never applied. On
2026-07-04, W6H-H5 re-derived the same numbers, reported "48/48
EXACT," and the architect amplified it into the record ("receipt-
exact everywhere ever measured") without checking it against the
correction list the architect helped write the day before. The
overclaim was a REGRESSION of an already-known caveat, republished
through the very discipline meant to prevent it.

Corrections applied today: COLLATZ_PROOF.md:230 rephrased (v1.1
item 1 finally executed); the F5 computation's "(measured, W2)"
mislabel fixed in place. Standing evidentiary tiers, stated once,
plainly: TIER 1 (genuine edge measurement): C = 1..5 dense sweeps +
witnesses; the 250M reserve scan; the 2^68-scale verified range.
TIER 2 (real runs, proxy precision — consistency evidence):
C = 6..50 m1-lineage cohorts. TIER 3 (symbolic/game computation,
corridor meaning pending W6U): everything at C = 148 / m ≥ 29,
including L(358)/L(359) and the divergence-point sweep. F5 is
empirically OPEN — as the day-one recon said before the week's
enthusiasm papered it over. NEW HOUSE LAW: before any result is
promoted into the record, it gets checked against the standing
correction list; and every claim carries its tier.

## W6U-RECON interim + the architect's second spec error (2026-07-05)

W6U's first D_recon column came back 0 at every m — TRIVIAL, and
the fault is the architect's conditioning spec: "reach valid-1 at
depth m, endpoint free" admits ordinary DESCENDING trajectories,
which exist at every depth with no capacity. The corridor question
is ceiling-anchored HOVERING (the death shell's own definition) and
the spec dropped that clause. Owned; corrected residue-aware spec
re-dispatched to the same agent (its census port + validation
context retained).

W6U's real interim contribution: THREE independent instruments
agree the root-anchored GAME matches the mirror law through m=30,
first breaking at m=31 (11 vs 12) — CONTRADICTING W6R's "breaks at
29" (whose root-anchoring W6S already showed was not the census's).
Registered without resolution: the game's internal frames disagree
with each other; the game remains impeached as a corridor model,
and the program's weight has shifted to Tier-1 measurement.

→ W6V-MEASURE launched: genuine full-precision M_edge sweeps at
C = 6 upward (validation gate: reproduce C=5's genuine 14 first;
prize cell C=11, predicted 28, the zone where all game anomalies
live). Architect frozen: formula exact at every C measured — 75%.

## W6U-RECON final — the reconciled object, and the formula's first real break candidate (2026-07-05)

Ledger W6U-RECON; artifacts w6u_recon/w4-w5 (w1-w3 record intact).
The corrected, residue-aware reconciliation (census residue walk
ported verbatim, .rs lines cited; root-pinned definition REFUTED
three independent ways — E[a]=2 drift makes pinned-start forward
sums go negative immediately) selected by gate: variant (ii),
free-endpoint deficit RANGE, window END-anchored at the 53
heartbeat — **6/6 genuine gates** (D_recon = 3/4/5 at m = 9/12/14
AND the three negative-direction infeasibilities, via the archived
embedding/automaton.py oracle re-run read-only).

**Results:** mirror law EXACT 27/27 at m ≤ 28; **D_recon(29..32) =
11,11,11,11 vs formula 12,12,12,13** — two structurally independent
engines agree on all 62 cells; feasibility side is UNCONDITIONAL:
real integer trajectories 839/559/745/993 → 1 (29/30/31/32 odd
steps, each a one-step extension of the last, all exact-replayed)
each fitting a width-11 end-anchored corridor. Implies
M_edge(11) ≥ 32 against the never-actually-measured archived 28.

**Dictionary closed: D_recon = the game's end-anchored ceiling-on
D, 31/31 rows.** The game was the faithful model all along; the
W6Q/W6S "impeachments" were about root-pinned scoring conventions,
not corridor truth. Standing caveat (agent's own, E2-class): the
53-anchor frame is validated at the first heartbeat; deeper
boundaries unprobed.

**Arbiter:** W6V's direct full-precision sweeps (C=6 = 16 formula-
exact already Tier-1'd; the contested zone needs the sparse
live-set instrument — dense enumeration cannot reach m=29). If
Tier-1 confirms: the capacity law is exact through m=28 and then
PLATEAUS (D pinned at 11 for m = 29..32+, the game's "4× slower
growth" now credible to ~m=130) — the framework's precision-collapse
rate needs re-derivation above m=28, while Lock 4's climb
impossibility (−6 per heartbeat, measured in this same reconciled
object) stands.

## W6W-SPARSE — the sparse live-set instrument lands; the formula's first break CONFIRMED at C=11, and the ladder saturates (2026-07-04)

Ledger W6W-SPARSE; artifacts shell/underlock/w6w_sparse/ (self-
contained copy: LEDGER_W6W-SPARSE.md there). The arbiter W6U-RECON
final called for — genuine full-precision measurement in the
contested zone, where dense enumeration cannot go — has now run.

**Instrument:** backward walk from the single terminal residue rho=1
through the heartbeat's last m letters (end-anchored, the frame all
six genuine gates select), live set = (rho mod 3^(m−j), deficit-range
u, v) triples, free endpoints, exact ints only. The death shell keeps
the live set tiny — peak 234 states at C=11 where dense needed
13.8 GB. Gates: Tier-1 C=1..6 reproduced 6/6 (4,7,9,12,14,16; fresh
dense cross-checks C≤5 in-process, C=6 alive@16 fresh capped
subprocess + archived W6V death certificate for 17); C=7@m=17 alive
confirmed (31 live states, <1 ms, vs 13.8 GB/615 s dense).

**New Tier-1 rows (first genuine measurements at these C; previous
status DERIVED per W6T-PROV):** C=7..10 measured edges 19, 21, 24,
26 with death certificates — **formula exact 4/4** (frozen 70%: HIT).
Peak live sets 31/50/80/133.

**C=11 (frozen 55/45, closest call of the program): the 45% side
landed.** No death at m=29 — and none anywhere in the one-heartbeat
window: **C=11 survives through m=53** (deep witness n0=1707, range
exactly 11, 53-step exact Collatz replay). The m=29..32 witnesses
reconstruct to 839, 559, 745, 993 — W6U-RECON's four trajectories,
re-derived from scratch by code sharing nothing with w6u_recon.
Independent re-derivation (required): exact-int DFS engine agrees
with the layered modular BFS at every probed cell (m=26..33 and all
m≥28 up to 53, C=11..15). Anchor robustness: survival past 28 holds
at anchors 53/106/159 (steps-invariance gate C=3,4 passes first).
Root-anchored negative control reproduces w5's dictionary exactly
(dead/dead/alive/dead at 29..32) — the frames separate exactly where
W6U said.

**Structural upgrade to the break story: it is not a plateau to 32 —
it is saturation.** C=12..15 also never die within the window (peak
live 435/750/1286/2336). M_edge(C) as "death edge within one
heartbeat" is UNDEFINED (no death exists) for C≥11. The capacity law
is exact precisely while its edge lands at m≤28 (C≤10) and the
countdown-ladder concept itself ends at C=11 — consistent with the
precision-collapse rate needing re-derivation above m=28 (W6U's
anticipated consequence), and with W6P's game-side "D pins at 11
through m=53," now corridor-real in the gate-validated frame.

**Sharpest open cell now:** multi-heartbeat windows (m>53, residue
constraints spanning heartbeat boundaries) — the one-heartbeat
construction is the instrument's own boundary; whether C≥11 has a
death edge beyond it is unprobed. Falsifier for this round's verdict:
a validated multi-heartbeat extension killing C=11 at m≤53, or any
end-anchored-vs-reality divergence inside C=7..10's newly measured
range (none found: 4/4 exact).

Process note, recorded honestly: a v1 gate script ran a fresh dense
C=6/m=17 check under a cap that was reported but not enforced; the
worker hit VmPeak 13.4 GiB and was externally killed (W6V's own
record already showed 12.0 GB for that cell — never feasible under
the 8 GB rule). Fixed with a VmRSS watchdog hard-abort; no
measurement depended on the killed run. All sparse work this round:
<15 MB RSS, <10 ms per cell.

## Architect's verdict on W6W-SPARSE (Fable, 2026-07-05)

The arbiter ruled, and the registered 45% side landed — harder than
registered. Standing state of the capacity law:

1. **M_edge(C) = ⌊53(C+1)/22⌋ is now Tier-1 EXACT at C = 1..10**
   (edges 4,7,9,12,14,16 archived + 19,21,24,26 measured fresh
   tonight by the sparse instrument, each with a death certificate).
   The genuinely-measured base DOUBLED tonight.
2. **First confirmed break at C = 11 — and it is SATURATION, not a
   plateau**: no death through m = 53, the entire one-heartbeat
   window; deep witness n0 = 1707 (53 odd steps to 1, deficit range
   exactly 11, exact replay); the four W6U witnesses re-derived by
   code sharing nothing with w6u_recon; two independent engines;
   anchor robustness at 53/106/159; root-anchored negative control
   separates exactly as W6U's dictionary said.
3. **Scope fence, stated honestly**: "within the end-anchored
   one-heartbeat frame" — the ONLY frame that reproduces every
   genuinely measured cell (now ten of them). The frame's
   construction boundary is m = 53; multi-heartbeat windows are
   unprobed and are the sharpest open cell. Lock 3's capacity bound
   22m ≤ 53(C+1) has a measured counter-zone at C ≥ 11 in this
   frame; its rescue, if any, lives in cross-boundary deficit
   coupling (→ W6X-MULTI).
4. **Consequences**: F5 as posed (358 vs 359) DISSOLVES if the
   break is corridor-real at scale — the C = 148 edge question
   requires the multi-heartbeat theory. The precision-collapse rate
   needs re-derivation above C = 10. Lock 4's climb impossibility
   (−6 per heartbeat, same instrument family) is UNAFFECTED —
   hovering is not climbing; no-escape stands.
5. Architect's frozen 55% on the formula at C=11: MISSED — the
   week's final calibration entry, consistent with its theme.

The sparse live-set instrument (peak 234 states at C=11 where dense
projected 40 GB) is the program's new workhorse; the June death-
shell insight — the shell kills almost everything — is what made
the arbiter possible.

## W6X-MULTI — the two-heartbeat window kills C=11..15; the "saturation" was a construction artifact (2026-07-04)

Ledger W6X-MULTI; artifacts shell/underlock/w6x_multi/ (self-contained
copy: LEDGER_W6X-MULTI.md there). W6W-SPARSE's own scope fence —
"within the one-heartbeat frame; multi-heartbeat windows unprobed" —
is now closed.

**Instrument:** mx_core.py extends sparse_instrument.py's backward
layered BFS past m=53 with NO change to the per-layer transition math,
only to the window construction. Both live anchor readings for m>53
implemented per house rules: Reading A ("growing end-anchor," ==
sparse_instrument's own "root" anchor for all m) and Reading B
("heartbeat-periodic re-anchoring," anchor_end=53⌈m/53⌉, reduces
EXACTLY to the gate-validated "end" anchor for m≤53). Gates: all ten
Tier-1 edges (C=1..10) reproduced exactly; C=11 alive through m=53
with the SAME 234-state stabilization and the SAME n0=1707 deep
witness W6W-SPARSE found; Reading A reproduces the known root-anchor
negative control at m=29..32 exactly. Peak RSS for the entire
multi-heartbeat sweep: 28.9 MB (cap was 7500 MB — nowhere close).

**Verdict: C=11..15 all die within m=54..106, under BOTH readings.**
Reading B (textually favored going in, and confirmed monotone —
alive-then-permanently-dead — for all 5 C, unlike Reading A which
is intermittent/revives at 4 of 5 C): edges 57→58 (C=11), 63→64
(C=12), 68→69 (C=13), 71→72 (C=14), 79→80 (C=15). Peak live-set at
each C never exceeds the one-heartbeat saturation value already
measured (234/435/750/1286/2336) — the corridor is squeezed to zero
from a FIXED population across the boundary, not from a growing one.
Death mechanism: cumulative squeeze (monotonically shrinking live set
over ~10-15 layers), not a single trigger letter. All witnesses
exact-verified (backward reconstruction + true Collatz replay +
deficit range), including deep ones whose full odd-step count to 1
matches their witness depth exactly (n0=1707→53 steps, n0=4011→68
steps, n0=23751→79 steps) — genuine slow-descender integers that
simply run out of runway once the window is long enough to see their
whole trajectory.

**Fit attempt (honest, not forced): the SAME closed form, generalized
to n heartbeats via ⌊53n(C+1)/22⌋, fits Reading B's new edges at n=2**
(⌊106(C+1)/22⌋ vs observed: residuals 0,+1,+1,−1,+2 across C=11..15,
mean |residual|=1.0, no drift). Provisional — 5 points, one n — but
this reframes W6W-SPARSE's "saturation, ladder concept ends at C=11"
as likely a ONE-HEARTBEAT CONSTRUCTION ARTIFACT rather than corridor
truth: the capacity law may hold after all, just requiring a window
long enough (n heartbeats scaling with C) to reveal the edge that a
single 53-step window is too short to see.

**Independent re-derivation:** mx_dfs2.py, a THIRD structurally
distinct engine (explicit-stack DFS, no memoization at all, exact
unbounded big-int rho — differs from both the primary layered-BFS and
w6w_sparse's own recursive-DFS-with-memo second engine), agrees at
15/15 cross-checked cells spanning both readings and the Reading-A
revival cells specifically. No disagreements.

**Frozen predictions: 40% (death in 54..106) HIT — for all five C
values, not just C=11; 60% (saturation continues, favored) MISSED.**

**Honest process note:** a v1 of the measurement script broke its
sweep loop at the first dead m per (C, reading) — correct for Reading
B (confirmed monotone) but silently truncating Reading A's data past
its first "death" and hiding real intermittent revivals (Reading A is
NOT a clean single-edge object — it revives after its first death at
4 of 5 tested C values, independently confirmed by mx_dfs2). Caught
during analysis cross-checking, fixed (full range always swept now;
cost is negligible — under 14s total), re-run; nothing in this ledger
depends on the truncated v1 output.

**Sharpest open cell now:** does ⌊53n(C+1)/22⌋ continue to fit at n=3+
heartbeats and at larger C (this round only tested n=2, C≤15)? And
does the near-periodicity of the credit word (exact through 6
heartbeats, first break at step 358 — the program's own "358 vs 359"
F5 landmark) interact with the capacity law once measurement reaches
that range? Neither attempted this round (honest scope limit).

## Architect's verdict on W6X-MULTI (Fable, 2026-07-05) — the law graduates

The multi-heartbeat frame ruled: **the C=11 saturation was the
frame's construction boundary, not corridor truth. C=11 dies at
m=58; C=12..15 at 64/69/72/80; no revivals through 106** (Reading B,
pre-registered; both engines + the relayer's third engine agree;
witnesses are genuine slow-descenders — the 559/745/839/993/1707
family plus n0=2713 and up to 40065).

**The reframe that matters: the capacity law survives by SCALING
ITS WINDOW.** The corrected candidate ⌊106(C+1)/22⌋ — the same law
with 53 → 106 — fits all five new edges with MAE 1.0. The picture:
C ≤ 10 lives in the one-heartbeat regime where ⌊53(C+1)/22⌋ is
Tier-1 exact; C ≥ 11 crosses into the two-heartbeat regime where
the same 22/53 arithmetic runs on the doubled window. Not a broken
law — a heartbeat-quantized law. (Provisional: 5 points, 2
heartbeats; W6Y tests the generalization at C = 16..26 and hunts
the 3-heartbeat transition.)

**Downstream inversions:** F5's 358-vs-359 question STANDS again
(the break is not corridor-real). Lock 3's capacity bound becomes
per-heartbeat-windowed rather than falsified. Lock 4 unaffected
throughout. And the recorded bonus: the credit word itself is
exactly periodic through six heartbeats with first break at step
358 — the F5 landmark surfacing in the word, consistent with W6C.

Architect's calibration, final entries of the night: 55% formula-
at-C=11 (missed), then 60% saturation-real (missed) — both misses
in the direction of the object being MORE lawful than bet. The
week's theme, unbroken to the end.

## W6Z-TAX — the corridor tax schedule τ(C), measured at every level (2026-07-04)

Ledger W6Z-TAX; artifacts `shell/underlock/w6z_tax/` (self-contained
`LEDGER_W6Z-TAX.md` there). Architect: "In corridor 1 it's a −3.x
percent tax; what was never measured is the tax at each level." Locate
+ reproduce the corridor-1 number, then measure τ(C), C=1..15, in every
sense the instruments support. All new work reuses validated instruments
(sparse_instrument backward BFS for population; b2/w6e engine for climb);
peak RSS <20 MB; `w6y_regime/` untouched. Architect predictions: (a) HIT,
(b) MISS, (c) HIT.

**The −3.x% number: LOCATED, REPRODUCED, and RE-LABELED.** The only
−3.x% "tax per heartbeat" anywhere in the repo is the killed-survivor
**spectral contraction 3.94% = 1 − ρ, ρ=0.960647**
(`SPECTRAL_RADIUS_RESULTS.txt:30-31`; `COLLATZ_PROOF.md:484`;
`GHOST_GEOMETRY_RELEASE.md:104`) — the per-heartbeat survival-mass
multiplier of the composed 53-step operator (`rust/spectral_radius.rs`).
Reproduced from scratch (`step1_locate_corridor1_tax.py`, independent
Python power iteration): C=3 m=7 ρ=0.960229329 matches the archived m=7
table value 0.960230 bit-for-bit; τ=3.98%→lock 3.94%. **HONEST
CORRECTION (no strawman): the number is the C=3 value, NOT C=1**
(`SPECTRAL_RADIUS_RESULTS.txt:13` labels C=3 "the narrow corridor — hard
floor on ρ"). C=1's actual spectral tax is 97.1%, C=2 is 37.1%, C=3 is
3.98%, collapsing to a flat ~0.046% plateau for C≥6 (the universal-ρ
regime). "Corridor 1" ⇏ C=1 for this measure; most charitable reading =
David meant the first/narrowest stable-floor corridor (C=3) or mis-indexed.

**τ(C) schedule, three fresh directly-measured senses + the May proxy
(`master_schedule.csv`):**
- **spectral (1−ρ per heartbeat):** 97.1, 37.1, **3.98**, 0.29, 0.058%,
  then flat ≈0.046% for C≥6. Transient collapse → constant plateau.
- **population thinning (geometric per-level live-set ratio, one-heartbeat
  frame; instrument re-run because the archives kept only counts, not the
  (u,v) deficit detail — gate: 10/10 Tier-1 edges reproduced, 0/134
  peak-live mismatches vs w6w JSON):** ~0.90-0.93/level for C≤10 (live set
  dies by M_edge≤26), **jumping to 0.98→1.02 (saturation, no death) at
  C=10→11** — the w6w-SPARSE break as a thinning ratio.
- **climb cap per heartbeat under corridor [0,C]** (b2's exact-residue DFS
  + the [0,C] prune; gate: width-unrestricted C=200 → −6 = B1.2 exactly):
  **C=1..7 INFEASIBLE — no residue-legal chain from any of 18 launches
  completes one heartbeat inside [0,C]** (climbing impossible, not merely
  unprofitable; consistent with M_edge(C≤7)<53); **C≥8: climb cap = −6
  EXACTLY, corridor-width-independent (flat).** The [0,C] bound never
  improves LOCK4-B1's −6/hb; it only forbids the heartbeat below C=8.
- **May m1-proxy reserve decay** (exact 3C−cutoff from
  `LOCK3_LOCK4_RESERVE_DECAY_NOTE.md:29-34`): 1,3,9,15,21,27 at
  C=6,10,20,30,40,50 — smooth monotone growth, slope +6/+10=0.60 above
  C=10, decay/C → ~0.54 (cutoff→2.4C).

**SHAPE VERDICT: (a) regime-constant-then-jump, decisively.** All three
FRESH senses are stepped/flat-within-a-regime (spectral plateaus at C≥6;
pop-thin jumps at C=10→11; climb-cap constant −6 above the C=8 feasibility
threshold). Only the May proxy has shape (b) smooth growth — and it
measures a *different* quantity (m=1 cutoff gap); its shape is NOT
reproduced by any fresh corridor instrument.

**Predictions:** (a) [55%] regime boundary visible in τ — **HIT** (three
independent boundaries: C≈5-6 spectral plateau onset, C=10→11 pop-thin
death→saturation, C=8 climb feasibility). (b) [50%] May decay = true τ
right-shape-wrong-constants — **MISS** (shapes qualitatively differ:
smooth vs stepped; constants uncorrelated). (c) [85%] climb cap strictly
negative at every C — **HIT** (−6 wherever defined C=8..15; impossible
below; never profitable at any width). Week's calibration theme continues:
the one miss is where the archived proxy was assumed to share the real
object's shape and does not.

**Walls (honest):** "corridor 1" label ambiguity unresolved (number is
C=3, exactly reproduced; C-index flagged not fudged); a first coarse-
modulus climb DP draft gave the residue-free +31 and was caught by the
B1.2 gate, root-caused (residue-tracking convention seam), rewritten
exact (superseded CSV kept); spectral ρ stopped at m=7 (RSS) but matches
the archived m=7 cell exactly. No compute wall — everything <20 MB, seconds.

## W6Y-REGIME — the heartbeat-quantized capacity law is REFUTED at scale: the death edge DRIFTS CONTINUOUSLY through the n=2/n=3 transition, it does not sit-and-jump (2026-07-04)

Ledger W6Y-REGIME; artifacts `shell/underlock/w6y_regime/`
(self-contained `LEDGER_W6Y-REGIME.md`). Task: test the Architect's
W6X-MULTI reframe ("a heartbeat-quantized law": `⌊53n(C+1)/22⌋` with
53→106 fit C=11..15's n=2 edges at MAE 1.0) at scale — C=16..26,
windows through 3+ heartbeats.

**Headline: the quantized law does NOT generalize. W6X's clean MAE-1.0
fit at C=11..15 was the CENTER of the n=2 regime, not a law.** As C
grows, the death edge M_edge(C) (Reading B, pre-registered) drifts
CONTINUOUSLY upward through the void between the n=2 value
`⌊106(C+1)/22⌋` and the n=3 value `⌊159(C+1)/22⌋`, landing squarely
BETWEEN them for C=16..23, then crossing PAST the n=3 line by C=24.
The measured edges (C=16..26): **93, 108, 110, 130, 132, 139, 157,
163, 188, 192, 205** (all Reading B, monotone, exact-verified, no
walls). Residual vs law2 grows monotonically **+12→+75**; residual vs
law3 goes **−29→+10** (crosses zero at C≈24). Best single-b fit
`⌊(106C+b)/22⌋`: MAE **43.6** — the n=2 FORM is wrong, no constant
saves it. Closest-n MAE: 7.25 (n=2 band C=11..18), 11.88 (n=3 band
C=19..26) — nothing like MAE 1.0 anywhere outside the regime centers.

**The decisive diagnostic — `edge/(C+1)` ratio**: a clean
heartbeat-quantized law would PIN this at n·53/22 = n·2.409 and JUMP
between n values. Instead it CLIMBS SMOOTHLY: 4.75→4.94 (C=11..15, near
n=2's 4.818, MAE~1) → 5.47, 6.00, 5.79 (C=16..18, in the n=2/n=3 void)
→ 6.29..7.59 (C=19..26, past n=3's 7.227 by C=26 and still climbing).
A crossover, not a ladder. The quantization is exact ONLY near each
regime's center; it breaks down in every transition zone.

**Two instruments, gated first (house rules).** mx_core (W6X's own
modular BFS) reproduced all Tier-1 + C=11..15 edges/witnesses exactly;
a new exact-big-int incremental walker `wy_core.py` (imports mx_core's
validated transition math unmodified, adds only a per-block O(m) walk)
cross-checked vs mx_core at EVERY m (alive/dead + live count + peak),
0 mismatches C=1..15. TWO honest bugs in the walker (wrong per-checkpoint
modulus; then over-counting on exact-rho keys) were caught BY the gate
before any new C and fixed (readout re-keyed with mx_core's terminal
modulus 3^0=1 → dedup by (u,v); peak via exact-frontier size, verified
equal because the peak provably precedes truncation onset). C=22 and
C=24 headline crossover edges independently re-derived by mx_core:
agree exactly.

**The transition rule (task 3c) — VERDICT.** The Δ=25 landmark is
confirmed exactly: at the known 1→2 transition (C=10→11), the previous
regime's value law1(11)=⌊53·12/22⌋=28 sits 53−28=**25** below the
window top. The rule "graduate when law2(C) > 2·53−25 = 81" fires at
**C=17** (C=16 = boundary), which correctly marks where the n=2 fit
STARTS failing. But the rule's PREMISE — a discrete hop between two
EXACT regimes — is false: there is no exact regime to graduate into,
because the edges drift rather than snap. So the threshold predicts
regime-END onset (verified, C≈16–17); it does NOT predict a jump.
Measured Δ = 25.

**Growth curve**: peak live-set 234→…→2336 (C=11..15, W6X) →
4413→…→2,524,517 (C=16..26), **≈×1.83/C** (range 1.81–1.95), close to
and slightly above the ×1.7 estimate. RSS ≤1.3 GB throughout (8 GB cap
never binding). C=26 (peak 2.52M states) completed but took 22 min
(exact-big-int rho slows deep blocks); the binding constraint at this
scale is WALL TIME, not memory — C=27+ needs a faster engine.

**No revival**: Reading B monotone for all C=16..26; C=16..23 swept to
m=265 (block 5) with zero revival past the edge — Reading B is a clean
single-edge object at these C (unlike Reading A).

**n0-vs-depth ladder** (all witnesses exact: backward ρ→1, true forward
Collatz replay, deficit range = C): edge m → n0 = 93→40,953; 108→74,475;
130→869,889; 139→2,928,673; 157→1,476,423; 163→5,471,367; 188→7,182,855;
192→22,701,369; 205→60,733,323. Slow-descender start integers climb ~3
orders of magnitude over the swept depth (W6X's deepest was n0=40065);
not strictly monotone in m (search returns *any* survivor), but the
envelope climbs steeply — deeper corridor cells recruit larger n0. The
C=26/m=205 witness needed a 3rd engine (`witness_bounded.py`, a
deficit-centering explicit-stack DFS, RSS ~12 MB) after mx_core's
all-layers reconstruction hit 7 GB and mx_dfs2's naive DFS order
exhausted a 200M-node budget; gated on 4 known cells first.

**Frozen predictions**: (a) 2-heartbeat holds C=16 until 3-hb transition
[60%] — **MISS** (breaks immediately at C=16, residual +12→+75). (b)
transition rule with Δ≈25 [50%] — **PARTIAL/MISS** (Δ=25 confirmed and
marks regime-END onset, but no discrete graduation exists — continuous
crossover). (c) growth ~×1.7/C [60%] — **HIT** (~×1.83).

**Cross-reference to W6Z-TAX (parallel round)**: W6Z-TAX found the
corridor TAX schedule τ(C) is "regime-constant-then-jump" (spectral
plateau, pop-thin jump at C=10→11, flat −6 climb cap). W6Y-REGIME finds
the death EDGE M_edge(C) drifts CONTINUOUSLY in the transition zones.
No contradiction: τ measures per-heartbeat contraction/thinning WITHIN a
regime (stepped between regimes); M_edge measures WHERE the corridor
dies, whose value interpolates smoothly across regime boundaries because
it is set by the whole multi-heartbeat window, not one heartbeat's rate.
The two are complementary faces of the same heartbeat structure — one
stepped, one drifting.

**Downstream**: the W6X-MULTI "heartbeat-quantized law" that revived
F5's 358-vs-359 question is now itself refuted as an exact object. The
capacity law's true multi-heartbeat form (if any closed form exists)
must reproduce a SMOOTHLY-drifting edge whose `edge/(C+1)` climbs
through the n-heartbeat ratios rather than quantizing to them — the
`⌊53n(C+1)/22⌋` family is falsified for C≥16. F5's C=148 edge question
now requires this true drifting form, not a quantized law.

## RED-TEAM VERDICT: the 9/4 edge-jump law is an ARTIFACT (2026-07-05)

The claimed "big corridor-edge jumps are spaced at rate 9/4" is REFUTED
by adversarial audit (redteam_9_4.py + REDTEAM_9_4_FINDINGS.md in
shell/underlock/w7a_renorm/). It fails all four tests:
- Threshold sweep: 9/4 is best-fit at 0/22 plausible H/L thresholds;
  the honest pre-registered split gives k=11/5=2.2, not 9/4.
- Null / look-elsewhere: ~48% of random same-density words fit SOME
  simple rational (q<=20) this well; 54% with the same one-point-drop
  freedom used. Indistinguishable from chance.
- Provenance: textbook reverse-fit. Unconstrained search found k=2.2
  first; the C=11 point (delta 31, n=1) was dropped and the refit
  landed on 9/4. Confirmed from the session's own record. (The
  architect (Fable-session) built this fit in poisoned context and did
  not self-audit; David flagged it for red-team, correctly.)
- W7C independently: 9/4 has no anchor in log2(3)'s convergent lattice
  (3.7% off vs 1e-3..1e-10 for real convergents).

STANDING PICTURE UPDATE: the corridor edge is the exact irrational-slope
law floor((C+1)/beta) for C<=10, then a hard phase transition at C=11
into a regime that is (a) NON-Sturmian (W7A factor complexity), (b) NOT
a heartbeat-quantized window law (W6Y, refuted at scale), (c) NOT
governed by 9/4 (this audit). The post-transition growth law is GENUINELY
OPEN — no rational spacing rule has survived audit. What IS solid: the
base convergent law (C<=10), the phase transition existing at C=11, and
the deep edges C=11..28 as measured data. The (53/84)^6 spectral law
(84/53 = the 6th convergent of log2(3), exponent = convergent index) is
the one convergent-structured result still standing and unexplained.

## SHADOW-ORBIT — why prime 19 is suppressed

Task: SHADOW_FINDINGS.md measured p=19 hitting (3x+1) ~28.5% below its
1/p baseline, the strongest deviation among {5,7,11,13,17,19,23}.
ORBIT_ORDER.md's hypothesis: the 1/p baseline assumes equidistribution
mod p; the real stationary distribution of the odd-map may have a
"hole" at the hit-residue h_p = -3^{-1} mod p, and that hole should
equal the measured deviation. Full receipt: IMPLEMENTATION_LEDGER.md
§SHADOW-ORBIT. Full numbers: `shell/shadow_primes/orbit/ORBIT_FINDINGS.md`.

**Is the stationary-hole the mechanism?** Yes, as a description — but
it's closer to a restatement than an independent discovery. A hit at
p (v_p(3x+1)≥1) occurs exactly when the pre-image x ≡ h_p (mod p), so
"stationary mass at h_p" and "hit density" are the SAME quantity
measured two ways, confirmed identical to float precision in this
round's own data. The real test was cross-sample agreement: this
round's independent sample (seed 20260705, 20,004 trajectories) vs
SHADOW's original (seed 12345, 5,204 trajectories) correlate at
r=0.973 with 6/7 sign match on the 7 shared primes. That's a solid
reproducibility result — the hole is real and stable across samples —
but it does not explain WHY the hole exists at any given depth.

**Does hole-depth generalize, and is 19 special?** No, not anymore.
Extending from SHADOW's 7 primes to 17 (up to 67), 19 drops from #1 to
#5 by relative hole depth: 41 (+34.5%), 59 (+31.5%), 67 (+29.7%), 43
(+29.4%), 19 (+27.7%). **19's "uniquely extreme" status in
SHADOW_FINDINGS.md was an artifact of a small comparison set.** More
strikingly: with 20,004 trajectories (vs SHADOW's 5,204), the
conservative per-trajectory CI now excludes 1/p for ALL 17 primes
tested, not just 11/13/19. The phenomenon is not "three anomalous
primes" — it looks like a **universal, prime-specific, varying-sign
bias against the naive 1/p model** across the primes tested so far.
This changes the shape of the open question: not "why is 19 weird" but
"why does 1/p fail as a baseline in general, and what sets the sign and
magnitude per prime."

**Predictive invariant for hole-depth: NONE FOUND**, and this is a
real, checked negative, not a shrug. Every basis-independent candidate
(ord(2 mod p), ord(3 mod p), ord(h_p), whether 2/3/h_p are primitive
roots, QR/Jacobi symbol of h_p, gcd of orders, raw p) tops out at
|r|=0.30 (p=0.25, n=17, not significant). One early candidate
(discrete-log distance from h_p to 2) looked strong (r=0.71) but was
proven to be a basis-choice artifact — its value ranges over nearly the
full unit interval depending on which primitive root is used as
reference, so it isn't a well-defined number at all. Concretely, 19's
own group-theoretic fingerprint (ord(2)=ord(3)=18=p-1, both primitive
roots) is shared by primes 5, 29, 53 — which show a small excess, a
large excess, and a moderate excess respectively (opposite sign from
19's suppression, and no shared magnitude) — directly falsifying "same
order + both primitive" as a sufficient cause. **This closes off the
group-theoretic angle as currently framed**; if a mechanism exists it
is not visible in the standard multiplicative-order invariants of
(p, 2, 3, h_p).

**Does the residue-operator alone reproduce the hole?** Partially, and
with an important structural finding along the way. The naive
"build the exact transition operator on Z/(p·2^K)Z, find its stationary
eigenvector" plan does not have a well-posed target: proven directly
(via `np.linalg.eigvals` on the exact transient sub-matrix, p=19) that
the operator is **exactly nilpotent** — every finite Collatz-descent
path has finite length to its absorption at x=1, so there is no
recurrent structure and no dominant eigenvector for any eigensolver to
find (ARPACK's non-convergence on this matrix was the tell; the
zero-eigenvalue proof is the actual explanation, not an artifact of
solver tolerance). A weaker, heuristic substitute — the shape a forward
power-iteration settles into during a mid-range plateau before
finite-size drain — correlates at r=0.922 with the empirically measured
hole across the 7 shared primes (6/7 sign match), suggesting the effect
is plausibly intrinsic to the bare residue dynamics of the odd-map
(not a large-number/magnitude effect, not a trajectory-sampling
artifact) — but the plateau method overshoots empirical magnitude by
roughly 2-2.5x and is not a proven fixed point, so this is supportive,
not conclusive.

**Predictive check on {41,43,47,53,59,61,67}: not a confirmed
prediction.** 5/7 measured suppressed vs 1/p, but since no invariant
from the search above reached significance, there was no genuine
ex-ante rule to test — 5/7 (71%) sits inside the noise of the base
rate already seen (11/17 = 65% of ALL 17 tested primes are suppressed).
Reporting this as "prediction confirmed" would overstate what was
derived; it is reported here as consistent-with-baseline, nothing more.

**What this opens/closes for the shadow-prime program:** CLOSES the
"19 is the extreme anomaly" framing (superseded by broader measurement)
and CLOSES the standard multiplicative-order/QR invariant search as a
source of the mechanism (checked directly, falsified). OPENS two
threads with real signal: (1) the cross-sample r=0.973 replication
means the per-prime hole values themselves are a solid, reusable
measured constant worth explaining, independent of any specific
narrative; (2) the r=0.922 operator-plateau correlation is a genuine
clue that the mechanism lives in the bare residue dynamics rather than
integer-size effects, and the ~2x magnitude gap between the operator
heuristic and the empirical value is a concrete, quantitative target
for the next round rather than a vague "look harder." Per house rules:
**the anomaly persists without a derivable mechanism** — reported
honestly as such, not dressed up as a law.

## SHADOW-HARMONICS — No robust prime anomaly survives a corrected census; p=19 was a measurement artifact (2026-07-05)

**Verdict: (C) NO ROBUST ANOMALY BEYOND SAMPLING.** Neither the
harmonic hypothesis (A) nor "real-anomaly-but-not-harmonic" (B) is
supported. The frozen prediction (p=19 suppression = (53/84)^9) is a
clean **MISS**: measured deviation is 4.5% of the predicted magnitude,
and the corrected confidence interval does not come close to bracketing
it. Full numbers and artifact paths in
`renorm_check/IMPLEMENTATION_LEDGER.md` (SHADOW-HARMONICS entry,
2026-07-05).

**The census, and why it required a correction before it could be
trusted.** A first-pass census over all 93 primes from 5 to 500 (22,004
independent trajectories, 1,057,188 odd-steps,
`shell/shadow_primes/harmonics/census_results.json`) flagged 100% of
tested primes as "CI-robust anomalous" vs 1/p, with the largest apparent
anomalies (433: +312%, 479: +315%, 347: +223%, all far exceeding 19's
established -28.5%) among the LARGEST primes tested. A 100% hit rate on
an "anomaly" test, with the biggest deviations concentrated at the
extremes of the range being searched, is the signature of a measurement
artifact, not a discovery — and it was one. Direct trajectory inspection
found that p=433's entire apparent 4x-enrichment was 90.5% attributable
to a SINGLE shared value (m=1732) that ~41% of all 22,004 independent
random starting trajectories happen to pass through on their way to 1.
Systematic count: of 1,057,188 total odd-steps sampled, only 203,003
(19.2%) are visits to DISTINCT states — Collatz odd-trajectories from
independent starts are not independent samples of (m mod p); they
descend through a shared, heavily-merging tree, and most "steps" in any
naive pooled-trajectory sample are duplicate revisits of a small set of
popular deep nodes. This is a previously-unnoticed flaw in the
shadow-prime harness design going back to the original
`shell/shadow_primes/harness.py` / `SHADOW_FINDINGS.md` round — invisible
there only because the 7 hand-picked primes are common enough that their
hit sets spread across 10,000+ distinct values, keeping the duplication
bias small relative to real signal. It becomes dominant, and eventually
the WHOLE signal, for rarer primes.

**The corrected census (deduplicated to 203,003 distinct merge-tree
states, each counted once) finds essentially nothing.** 2 of 93 primes
(283, 313) sit outside their 95% block-bootstrap CI around 1/p, both at
modest ~9% relative deviation, both in the held-out (201-500) band —
against an expected chance false-positive count of 4.65 out of 93 at
that confidence level. That is FEWER anomalies than pure sampling noise
predicts, not more. Zero anomalies survive in the 44-prime fit band
[5,200]. **p=19 itself is no longer anomalous once the measurement is
corrected**: rate 0.051911, CI [0.050793, 0.052956], comfortably
bracketing 1/19=0.052632. Same for p=13 (the fit-band's largest
deviation in the earlier, contaminated pass): CI [0.076529, 0.078873]
brackets 1/13=0.076923 cleanly. The premise this order was built to
test — "is 19 the extreme anomaly, and is it a heartbeat harmonic" —
dissolves at its first premise: **19 is not an anomaly at all** once
the merge-tree duplication bug is fixed.

**Harmonic-predictor test: moot, but reported for completeness.** With
no real anomaly to explain, none of the candidate predictors (ord(2 mod
p), ord(3 mod p), ord2==ord3, p mod 53, heartbeat-convergent
divisibility, 2^a-3^b resonance) show a usable signal — the only
nonzero correlations (r(|reldev|, ord2)=+0.275, r(|reldev|, p
itself)=+0.331) are consistent with residual finite-sample scaling
(rarer/larger-order primes naturally show slightly larger relative CI
half-widths), not a structural relationship. The (53/84)^k magnitude
law does not fit even the two remaining marginal held-out primes: 283
fits k=5.340, 313 fits k=5.259 — neither integer, neither shared, no
cluster. The single frozen falsifiable point (19→k=9) failed outright.

**Spectral cross-correlation: no single dynamical constant links the
spectral radius to a prime effect, because there is no prime effect
left to link it to.** The spectral radius ρ=0.960647 / gap=0.039353
(`SPECTRAL_RADIUS_RESULTS.txt`, `COLLATZ_PROOF.md`) remains a well-
established, independently-derived algebraic certificate about the
killed-survivor graph's non-terminal transient decay. This round found
no evidence that it also governs shadow-prime hit-density; the
apparent connection (the frozen 19→(53/84)^9 conjecture) was tested as
a single specific falsifiable point and missed by roughly 22x in scale
(measured/predicted ≈ 0.045).

**Held-out predictive check.** By construction there was no fitted
"law" from the FIT band to carry forward (zero anomalies found there),
so the predictive check on primes 201-500 could only test the null:
does the same ~5% background false-positive rate persist out of sample?
Yes — 2/49 held-out primes flagged, against an expectation of 2.45.
Consistent with pure noise both in and out of sample.

**What this closes and opens for the shadow-prime program.** CLOSES
the "p=19 is a genuine, structurally special anomaly" framing this
entire program branch (SHADOW_FINDINGS.md §5, and this session's
earlier SHADOW-ORBIT round, both built on it) was premised on — it was
never a hole in the residue dynamics, it was 80%+ measurement
duplication from the Collatz merge tree acting differently on
different primes' hit-counting depending on incidental overlap with
popular deep nodes. This also retroactively weakens (does not
necessarily invalidate, but requires re-derivation before further
reliance) the SHADOW-ORBIT round's r=0.922 operator-plateau correlation
and the general "11/17 primes suppressed" baseline rate, since those
were built on the same undeduplicated sampling method — flagged in the
ledger as a "not complete until" item, not re-run here (out of this
order's scope). OPENS one clearly-scoped new question, explicitly NOT
answered by this round: characterizing the Collatz merge-tree's own
structure (how concentrated is "popularity" among deep states, how
that concentration scales with search depth) is a legitimate, separate,
interesting object — but it is a statement about trajectory-merge
topology, not a Sturmian-heartbeat harmonic, and should not be
reframed as one without new evidence.

## ONE-STEP DESCENT SPECIES — theorem verified computationally at scale (2026-07-05)

**Verdict: CONFIRMED, exactly, at scale.** The theorem in
`shell/descent_rule/DESCENT_RULE_SPEC.md` — odd x satisfies S(x)=1 in
exactly one odd-step iff x=(4^k−1)/3 for integer k≥1 — was proven
elementarily in the spec (solve 3x+1=2^j, integer solution needs j
even) and is treated in this program as an already-established
theorem, not a conjecture. This round's job was to verify it
computationally at scale and build the certificate machinery; it did,
and every mandatory gate passed with the frozen expectation exactly
met (zero tolerance, zero exceptions found). Full process receipt:
`IMPLEMENTATION_LEDGER.md` §"2026-07-05 - One-Step Descent Species:
mission gates 1-4". Scripts + raw logs:
`shell/descent_rule/gate{1,2,3,4}_*.py` and matching `*_results.txt`.

**Gate 1 (direct construction, forward direction) — holds at extreme
digit length.** Constructed x=(4^k−1)/3 for k up to **400,000**,
giving x with **799,999 bits (~240,823 decimal digits)** — three
orders of magnitude past the spec's own "thousands of bits" bar. Every
one of the four required exact checks (3x+1==4^k, bitwise power-of-two,
even exponent, real one-odd-step brute simulation landing on 1) passed
at every k tested, no exceptions, in 22.3s wall clock with 12.64MB peak
RSS. This is a direct, arbitrary-precision-exact demonstration that the
forward direction of the theorem is not a small-number coincidence —
it holds at the largest sizes tested with zero degradation.

**Gate 2 (converse/exclusivity) — zero false positives, zero false
negatives across 5,000,000 odd integers.** Brute one-step simulation
was run as ground truth over ALL odd x in [1, 10^7) — 5,000,000 values
— and compared against species-set membership. The two sets matched
**exactly**: 12 species members below 10^7, 12 values with brute
S(x)=1, **0 false positives, 0 false negatives**. This is the converse
half of the theorem (no non-species x accidentally reaches 1 in one
step, and no species member fails to) verified exhaustively, not
sampled, over 5 million cases. 18 additional random huge odd x
(~200-3000 decimal digits) all correctly showed S(x)≠1, as expected
since none are species members — confirming the exclusivity extends
past the exhaustive range into arbitrary size.

**Gate 3 (closed-form certifier) — trajectory-free, O(digits)-scaling,
100% exact agreement.** `is_one_step_species(x)` (in
`shell/descent_rule/descent_common.py`) implements the two-line
certificate from the spec's "Corollary" section — compute 3x+1, test
power-of-two, test exponent parity — with NO loop, NO trajectory
simulation. It was gated against the brute simulation on the full
5,000,018-case set from gate 2 (all 5,000,000 odd x<10^7 plus the 18
huge-x samples): **0 mismatches, 100.0000000000% agreement**. It
correctly certified 6 true species members from 1001 to 6021 decimal
digits (returning the exact matching k every time) and correctly
rejected 10 non-members at 1000-3000+ digits (6 "near-species" values
offset by a few units from a true member — the hardest adversarial
case, since these are close enough to look suspicious but are not
powers of two after 3x+1 — plus 4 unrelated random large odds). The
timing table (Gate 3 Part 4, 5001 repeats per point) measured per-call
time across 10 to 300,000 decimal digits and found the per-call/digit
ratio stays within a roughly 5x band (0.0007 to 0.04 μs/digit) across
four orders of magnitude of digit count — direct empirical evidence
the certifier is O(digits)-or-better, categorically different from
trajectory simulation (which has no such uniform per-digit bound, since
individual orbits can run long regardless of digit count). This
converts the spec's proof-level claim ("membership is decidable in
closed form, any digit length") into a measured, timed, reproducible
fact.

**Two harness bugs surfaced and fixed, per the standing "failure means
a harness bug, not a false theorem" directive — neither touched the
mandatory gates' verdict.** (1) Python 3.11+'s int-to-str digit guard
(default cap 4300 digits) tripped during Gate 3's digit-count
reporting for six-digit-and-beyond-decimal x; fixed by raising
`sys.set_int_max_str_digits` in `descent_common.py`, confirmed the cap
only ever affected DISPLAY code, never the certifier/constructor
arithmetic itself. (2) Gate 4's own n=1-bucket cross-check (an
exploratory convenience check, not one of the three mandatory gates)
briefly reported a spurious found=10/known=11 mismatch, traced to an
off-by-one in the exploratory harness (x=1 is the n=0 base case, not
n=1, by the brute-search's own definition) and fixed; re-run confirmed
exact agreement (10==10). Full diagnosis of both in
`IMPLEMENTATION_LEDGER.md`'s Bugs/issues section for this round — cited
here only to note that the mandatory gates 1-3 never showed any
discrepancy in any form, at any point.

**Gate 4 (optional k-step tower) — n=1 closure confirmed exactly;
n=2/n=3 congruence-class closure is a genuine, honestly-reported open
wall.** Brute-searching clean-descent length (steps that are each
strictly decreasing, per the spec's own mod-4 drop lemma, verified
directly at each step) over all odd x<2,000,000 reproduced the n=1
bucket EXACTLY against the closed form (4^k−1)/3, k=2..11 (10==10,
zero discrepancy) — an independent, brute-force confirmation of the
already-proven n=1 theorem via a completely different code path than
gates 1-3. For n=2 (33 members in range) and n=3 (68 members),
congruence-class residues were checked mod 4 through mod 256: NO single
residue class (or small clean union) was found that captures either
set — n=2 already shows 8 distinct residues mod 256, n=3 shows 15,
neither collapsing the way n=1 collapses to exactly one residue class
mod 4^k. This is reported as a real, checked negative within the
budget spent (per the spec's own instruction not to force a result),
not a proof of non-existence — a deeper search (higher moduli, larger
brute range) is explicitly left open in the ledger. A secondary
reverse-construction probe (finding the unique clean one-step
predecessor of each n=1 species-tower-top) found a clean predecessor
for k not≡0 (mod 3) but found none in the searched window for k≡0
(mod 3) (k=3,6,9) — a concrete, specific, honestly-flagged asymmetry
for a future round to explain or resolve, not swept under a summary
"partial progress."

**What this closes / what remains open for the program.** CLOSES: any
residual question of whether the One-Step Descent Species theorem
holds only for "small" or "textbook-sized" x — gate 1 pushed to
240,823-decimal-digit x with zero exceptions, and gate 2's converse
check was exhaustive (not sampled) over 5,000,000 cases with zero
exceptions either direction. CLOSES: whether a trajectory-free,
provably-O(digits) membership certificate exists and works at scale —
it does, it's `is_one_step_species()`, and its scaling was measured
directly rather than asserted. OPENS, for a future round, ONLY within
gate 4's genuinely-exploratory scope (never claimed proven here): a
closed congruence-class characterization of the n=2 and n=3
clean-descent towers, and an explanation for the k≡0 (mod 3) reverse-
construction gap. Nothing in gate 4's open status weakens or qualifies
the gate 1-3 verdict above — the theorem's own scope (one-step-to-1
species) is fully closed at the exactness and scale the spec asked for.

## BACKWARD BASIN CERTIFICATE — layers don't close into clean congruence
classes, but coverage density hits the frozen ~70%/~60% conjectures
almost exactly (2026-07-05)

**Verdict, gate by gate, against `shell/descent_rule/BASIN_CERTIFICATE_SPEC.md`'s
own frozen expectations.** Full process receipt:
`IMPLEMENTATION_LEDGER.md` §"2026-07-05 - Backward Basin Certificate:
mission gates 0-3". Scripts + data:
`shell/descent_rule/gate0_gate1.py` (+`gate0_gate1_results.txt`),
`shell/descent_rule/gate2_gate3_census.py` (+`gate2_gate3_results.txt`,
`gate2_gate3_run.log`, `gate2_density_table.csv`).

**Gate 0/1 (theorem-level, exact) — the mod-3 predecessor rule holds
with zero exceptions; the layer congruence-class question has an
HONEST NEGATIVE answer.** Gate 0 reproduced both established facts
(species closed form, mod-3 predecessor-parity rule) exactly, 0
exceptions across 30 species members and 18 cross-checked t-values.
Gate 1 is the more interesting result: LAYER 1 (48 members), LAYER 2
(138 members), LAYER 3 (349 members) — all within census bound
2,000,000 — were fit against congruence classes mod 4 through mod 1024.
The populated-residue FRACTION does not converge to a small stable set;
it GROWS layer over layer: at mod 256, LAYER1 populates 12/256 (4.69%)
of residues, LAYER2 populates 31/256 (12.11%), LAYER3 populates 44/256
(17.19%). Mod 4 alone never discriminates any of the three layers
(all three populate BOTH odd residues {1,3} — zero information at that
modulus). This means the backward basin's layers do NOT stack into the
clean, closed, finite congruence-class towers that LAYER 0 itself
enjoys (LAYER 0 is the exact recurrence x_{k+1}=4x_k+1, a single residue
class mod 4^k per k) — the certificate machinery the spec hoped for
(membership-by-congruence-test alone, no iteration) does NOT emerge
cleanly past layer 0, at least not within the modulus range (up to
1024) and layer depth (to 3) tested here. This is reported straight, per
the spec's own explicit instruction not to force a clean story — it is
a real, checked negative, not a proof that no closed form exists at
some larger modulus or via a fundamentally different parametrization,
but the natural "residues mod 2^n" guess does not work and the
population fraction is trending the WRONG way (up, not down) for a
closing pattern.

**Gate 2 (coverage census) — HIT, close to the frozen ~70% conjecture,
landing near-total.** density(N) was measured over all 5,000,000
distinct odd x in [1,10^7), ONE forward simulation per distinct x
(merge-safe by construction, confirmed explicitly in
`gate2_gate3_census.py`'s own docstring and re-confirmed in the ledger).
density(200) = **0.9999776** (4,999,888 of 5,000,000 covered). The
curve is a clean sigmoid-into-tail-decay: density(10)=0.0052,
density(50)=0.5001, density(100)=0.9629, density(150)=0.9991,
density(200)=0.99998 — it does not plateau below 1 at any point tested;
every additional N keeps shrinking the complement, with the last
Fibonacci-spaced checkpoint window (N=89→200) alone dividing the
complement by roughly 3,315x. This is a stronger result than the
spec's own "~70% confidence, density(N)→1" framing suggested was even
likely to be measurable cleanly — the frozen conjecture is a HIT, and
the measured curve gives no sign of an asymptotic floor short of 1
within the tested range.

**Gate 3 (uncoverable-class question) — HIT, no hard floor found; the
112-x residual complement looks like ordinary cap-boundary tail, not
structural exclusion.** Of the 112 odd x (out of 5,000,000) still
uncovered at N=200: x≡0(mod3) numbers (which structurally can never be
WAYPOINTS, only starts, per the established mod-3 predecessor rule) are
NOT disproportionately stuck — only 39 of 1,666,667 such x (0.0023%)
remain uncovered, the same order as the other two mod-3 classes (41 and
32 respectively out of similar-sized subclasses). The full
residue-class breakdown (mod 2,3,4,8,9,16,32; see ledger Evidence)
shows the same pattern everywhere: every class's none-count is small
(single-to-double digits against subclass sizes in the hundreds of
thousands to millions) and its max-finite-hit sits at or just under the
N=200 cap — the signature of "these just need a slightly larger N," not
of a hard, permanently-uncoverable residue floor. No class was found
where none-count stays large while max-finite-hit also stays flat
(the signature that WOULD indicate a genuine floor). Verdict: complement
shrinks toward measure zero, consistent with the spec's ~60%-confidence
conjecture, and no hard uncoverable class was found in this census.

**Connection to the death-shell / capacity picture — related domain,
NOT the same object; no direct import of results either way.** The
death-shell/capacity program (`shell/underlock/DERIVATION_NOTES.md`,
`shell/shell_probe.py`, the C=148/m=359 capacity-law work) analyzes a
BACKWARD exponent-menu minimax game keyed on ceiling-distance δ=C−d,
where "death" is a residue class that survives a fixed number of
heartbeats under a hard ceiling constraint — a fundamentally different
question (bounded-corridor reachability under an adversarial/minimax
credit process) from this mission's question (does the FORWARD odd-map,
unconstrained, eventually land every starting x on the layer-0 species
within SOME finite step count). The two do share the same underlying
mod-3 residue-parity mechanics (the "3 is forbidden" fact — odd
multiples of 3 have no backward predecessors here, exactly as C≡0(mod3)
states are dead-on-arrival in the shell picture) — but this mission's
Gate 1 finding (no clean finite congruence-class closure past layer 0,
growing residue population per layer) is actually a small piece of
INDEPENDENT CORROBORATION for the death-shell program's own hard-won
lesson (DERIVATION_NOTES.md §5a): that the natural small-modulus/
fixed-window abstractions of this residue-parity system LEAK — nothing
closes at a fixed small modulus, deeper structure needs deeper trit/
residue context, and value-iteration-style or lookup-table-style
"solve it locally" approaches are dead ends for this family of Collatz
residue objects generally. Gate 2/3's converging-to-near-total coverage
result does NOT feed back into the death-shell capacity constants (no
C=148/m=359-style number appears here, and none should be expected —
different object) — the connection is structural/methodological
(both programs independently rediscovered "small congruence classes
don't close this system"), not a shared numeric result.

**What this closes / opens for the basin-tiling question.** CLOSES,
within the tested range: whether LAYER 1-3 reduce to simple congruence
classes (they do not, and the trend is away from closure, not toward
it — a future round should not expect a cheap closed form here without
new structure). OPENS, cleanly and honestly: the coverage question
itself is answered near-affirmatively at this census scale (99.998%
covered by N=200, no hard floor detected) — the "basin tiles the odds"
picture is empirically supported, just not via the clean
congruence-class ROUTE the spec's Gate 1 hoped would carry it. The 112
residual x and the open question of whether the 0.0000224 complement
fraction itself shrinks as the census range grows (not just as N grows)
are the two concretely next things (see
`IMPLEMENTATION_LEDGER.md`'s "Not complete until" for this round).

## CROSS-INSTRUMENT SYNTHESIS (J1-J4) — four measures, one obstruction, no forced unification (2026-07-05)

Per `shell/SYNTHESIS_FOUR_INSTRUMENTS_SPEC.md`'s four joins, tested
against the spec's own frozen predictions. Full process receipt:
`IMPLEMENTATION_LEDGER.md` §"2026-07-05 - Cross-Instrument Synthesis
(J1-J4)". Scripts + raw output: `shell/synthesis_four/j1_set_compare.py`
(+`j1_output.txt`), `j2_rho_fit.py` (+`j2_output.txt`),
`j3_convergents.py` (+`j3_output.txt`).

**J1 — death shell dead-set S(m) vs basin residual complement: DIFFERENT
OBJECTS, no set equality, no above-chance overlap. Frozen "same object,
~65%" MISSED.** The basin's 112 residual odd x (N=200 cap,
`descent_rule/gate2_gate3_results.txt`) were reconstructed in full (only
smallest/largest 20 were published; reconstruction verified identical to
both lists exactly, `shell/synthesis_four/j1_output.txt`). First finding,
decisive on its own: **39 of 112 (34.8%) of the basin's residual x are
x≡0(mod 3) — structurally OUTSIDE the shell dead-set's domain entirely**,
since `shell_probe.py`'s dead set is defined only on `r % 3 != 0`
residues (`nz = r % 3 != 0`). A set-equality claim cannot survive over a
third of one side's members living in a space the other side doesn't
even define. Of the remaining 73 eligible x, the hit-rate landing inside
S(m) (computed via `automaton.py`'s `run_heartbeat` + `dead_profile`,
independently confirmed C-invariant: `dead_union_12==dead_union_23`
identical at every m=2..8, corroborating P2) rises from 27.4% at m=2 to
95.9% at m=8 — but S(m)'s OWN base rate among nz residues rises in
lockstep, from 33.3% to 91.66% over the same range (P1: the dead set's
own density grows with m). At m=8 the binomial z-score for "70 hits out
of 73 against a 91.66% base rate" is z=1.31 — not significant. The
hit-rate is explained entirely by the dead set's growing density, not by
any link to the basin object. **Verdict: the two are related in
mechanism (both instantiate "3 is forbidden" residue-parity) but are NOT
the same object, NOT set-equal, NOT even measurably correlated beyond
chance** — sharpening SYNTHESIS.md's own earlier "related domain, not
the same object" note (search "Connection to the death-shell / capacity
picture" above) from a qualitative analogy into an actual, adversarially
checked negative result with numbers.

**J2 — basin complement decay is NOT rho-governed; free rate wins but
even it fails held-out prediction. Frozen "rho-governed, ~55%" MISSED.**
Fit `descent_rule/gate2_density_table.csv`'s complement_density(N),
N=0..200, against A·rho^(N/53) (rho=0.960647, FIXED per-step rate), A·
b^(N/53) (b=0.063099, FIXED), and A·r^N (r free, OLS). In the fairest
region (DEEP TAIL, N=170-200, post-saturation): rho-fixed R²=0.0223 (a
near-total failure — rho's per-step rate 0.999243 barely decays at all
compared to the data), b-fixed R²=0.9378, free-rate R²=0.9834 (r=0.9357).
Free rate beats b-fixed and crushes rho-fixed at every N-range tested
(FULL, EARLY, TAIL, DEEP TAIL — see `j2_output.txt` for all four).
**Adversarial held-out check (the decisive test): fitting the free rate
on N=150-175 and predicting N=180-200 gives systematic -13% to -29%
relative error** — even the best-performing free single-rate geometric
model does not hold out cleanly; the true decay is not pure single-rate
exponential even in the tail. Empirical per-step ratios
complement_density(N)/complement_density(N-1) for N=146-200 scatter
0.85-0.97 with no visible trend toward either rho^(1/53)=0.999243 (WAY
outside this range — categorically ruled out) or b^(1/53)=0.949203
(closer, near the scatter's edge, but not its center ~0.93). **Verdict:
rho does NOT govern the basin decay — it is falsified outright, not
merely "weakly supported"; b is closer but not confirmed (the held-out
failure means no single fixed rate, rho/b/free, is established as the
governing law); the basin's true decay is genuinely independent of the
spectral radius as measured here.** This required actively trying to
break a good-looking fit before accepting it (per the mission's own
anti-9/4 rule) — the free-rate in-sample R²=0.995 (TAIL range) looked
strong until the held-out N=180-200 test exposed -20%-scale systematic
error, which is exactly the failure mode the spec warned against
accepting on a fit alone.

**J3 — 53 is exactly shared (verified via exact continued fractions);
C=11/exponent-6 relation is OPEN, one candidate found and adversarially
REJECTED. Frozen "53 shared exact" HIT; "C=11/6 open" HIT.** Computed
CF(log2(3)) = [1,1,1,2,2,3,1,5,2,23,2,2,1,1] (60-digit mpmath seed,
exact-integer convergent recurrence thereafter): 84/53 is the k=6
(0-indexed) convergent, exactly reproducing F2/SPECTRAL_RADIUS_RESULTS's
claim. CF(2-log2(3)) = [0,2,2,2,3,1,5,2,23,2,2,1,1,55]: 22/53 is the k=5
convergent, exactly reproducing F1's claim (and F1's stated "next:
127/306" reproduced exactly at k=6 too). **Precise numerator/denominator
correction to the spec's own framing**: the corridor's scaling constant
53/22 (in `M_edge(C)=floor(53(C+1)/22)`) is NOT itself a listed
convergent of beta=2-log2(3) — beta's own convergent at k=5 is 22/53
(the reciprocal). 53/22 IS an exact convergent of 1/beta at k=4. So the
"shared 53" is real and exact, but its role differs across the two
objects: in alpha=log2(3)'s convergent list, 53 is 84/53's DENOMINATOR;
in beta's reciprocal 1/beta's convergent list, 53 is 53/22's NUMERATOR —
same integer, opposite role, connected via the standard reciprocal-CF
identity (verified: CF(1/beta)'s convergents are exactly reciprocals of
CF(beta)'s in order). The alpha/beta CF-reflection identity itself
(beta=2-alpha ⟹ term-list transform) was verified EXACTLY: alpha's
a1=1 forces the "merge" branch of the reflection identity
(1-f=[0,a2+1,a3,...]), and the predicted beta-term prefix
[0,2,2,2,3,1,5,2,23,2,2,1,1] matched the actual computed CF(beta) prefix
on all 13 terms checked. **C=11/exponent-6**: swept M_edge(1..14);
M_edge(11)=28, not 84 (no match); the convergent-index of 84/53 (k=6)
does not equal C+1=12 (no match). One numeric coincidence was found —
the cumulative sum of alpha's partial quotients through index k=6 equals
exactly 11 — and was adversarially REJECTED: that cumulative-sum
sequence (1,2,3,5,7,10,11,16,18,41,...) is monotonically increasing
through small integers by construction, guaranteed to pass near some
small target somewhere in its run, and has no independent structural
motivation from either instrument's own math — the identical failure
shape as the refuted 9/4 edge-jump law (see "RED-TEAM VERDICT: the 9/4
edge-jump law is an ARTIFACT" above). **Verdict: 53 shared, exact,
confirmed both directions; C=11/exponent-6 relation remains genuinely
OPEN — no candidate survived adversarial checking.**

**J4 — the union does NOT close the loop; the shared obstruction is
absence of fixed-modulus residue closure, independently hit by all four
instruments. Frozen "loop does not close, ~75%" HIT.** Precise
conditional, given J1-J3: **IF** the death shell and basin complement
are different objects sharing only a mechanism (J1), **AND IF** the
basin's decay rate is empirically independent of the spectral radius
rather than a derivable transform of it (J2), **AND IF** 53 is
confirmed the same heartbeat constant across corridor and spectral work
while the C=11 transition remains structurally unexplained (J3), **THEN**
the four instruments jointly establish: (i) a computer-verified,
exact-arithmetic proof that the transient/non-terminal subsystem
contracts strictly (rho<1 at every tested (C,m), spectral radius
instrument, `SPECTRAL_RADIUS_RESULTS.txt` "ρ < 1 at EVERY tested (m,C)
combination. Zero exceptions"); (ii) an exact, finite characterization
of which residue classes cannot survive one bounded-corridor heartbeat
(death shell P1-P6, `shell_probe.py`); (iii) a near-total (99.998% at
N=200, one finite census) empirical coverage result for the UNCONSTRAINED
forward map with no discovered hard floor (basin Gate 2/3); and (iv) an
exact rational capacity law for the bounded corridor up to a proven
divergence point (corridor F1, C<=147, then genuinely open past C=147).
**What is NOT established, and is the SAME gap in all four**: none of
the four instruments' residue systems close into a small, fixed modulus
as depth/scale grows — this is not one instrument's local weakness but
one obstruction recurring four times under four different
constructions: the basin's own Gate 1 (`IMPLEMENTATION_LEDGER.md`
§"Backward Basin Certificate", populated-residue fraction mod 256 GROWS
12/256→31/256→44/256 across LAYER1-3, "does NOT converge to a small
stable set"); the death shell's P1 (`shell_probe.py`, dead-set mass and
depth both GROW with m, no small fixed floor); the spectral radius's
C=3 "hard floor" LOCK at m>=10 (`SPECTRAL_RADIUS_RESULTS.txt`) is
itself NOT a counterexample to this — it is a fixed-C phenomenon (the
lock value 0.960647 is specific to the narrow C=3 corridor and does not
represent the residue system closing at any fixed modulus; at C>=10 the
same instrument's rho instead runs to 1, i.e. NO fixed floor at the
universal/wide-corridor setting, which is the setting relevant to an
unbounded proof); and the corridor's own C=11 phase transition into a
regime that is "NON-Sturmian... NOT a heartbeat-quantized window law...
NOT governed by 9/4... GENUINELY OPEN — no rational spacing rule has
survived audit" (SYNTHESIS.md "STANDING PICTURE UPDATE", above). **The
one-sentence shared obstruction: no instrument's residue/congruence
description of "which states fail to descend" closes into a fixed,
finite modulus as depth or corridor width grows — basin Gate 1's
residue population, the death shell's dead-set mass/depth, the
spectral radius's wide-corridor rho→1 (only a narrow-C artifact
achieves rho<1 as a fixed floor), and the corridor's post-C=11 growth
law all instead keep requiring MORE residue/trit context at every
larger scale tested, and this is proven-negative (not merely
unfinished) in every one of the four instruments' own artifacts cited
above.** This is a bounded-rate-and-coverage picture with wide empirical
margins at every scale tested, not a proof — the gap is not "we haven't
found the closure yet," it is "every attempted closure at fixed small
modulus has been checked and found to grow, not shrink," across four
independently-built measurement instruments that were never designed to
agree with each other and were not forced to here.

## IME REFRAME OF J2/J4 — course correction, tested honestly, NULL result (2026-07-05)

**This entry supersedes the INTERPRETATION of the prior round's J2 and
J4 only.** J1 and J3's verdicts stand unchanged (see previous section)
and are cited, not repeated. The course correction, relayed by a peer
session on the architect's (David's) behalf: IME
(`/mnt/ForgeRealm/collatz-experimental-data/IME-primer.md`,
"Incommensurate Measurement Emergence") predicts that when two
incommensurable measurement geometries are forced to interact, the
mismatch generates an emergent depth hierarchy with tiers set by
structural constants of the incommensurability — in this Collatz
program, the continued-fraction convergents of log2(3) (53, 84, 306,
485, 665, 1054, 15601, 24727, ...), verified exactly in round-1 J3.
Under this frame, round-1 J2's finding that the basin's raw decay rate
(~0.93-0.94/step) differs from the spectral radius's raw rate
(rho=0.960647/heartbeat, or b=0.063099/m-level) is reinterpreted: the
RAW-RATE MISMATCH is not evidence against a relationship — under IME it
is the PREDICTED SIGNATURE of incommensurability. The test therefore
changes from "do the rates match" (round 1, correctly answered NO) to
"do the four instruments' characteristic depths form an ordered
hierarchy whose TIER BOUNDARIES land on the convergent ladder, or is
the ordering arbitrary" (this round). Full process receipt:
`IMPLEMENTATION_LEDGER.md` §"2026-07-05 - IME Reframe of J2/J4". Script
+ output: `shell/synthesis_four/j2j4_ime_reframe.py`
(+`j2j4_ime_output.txt`).

**Pre-registration (done BEFORE any ladder lookup, per the mandatory
anti-reverse-fit discipline this program has now needed twice already —
9/4 and prime-19).** Corridor and spectral radius are ALREADY
heartbeat-native (53 appears directly in `M_edge(C)=floor(53(C+1)/22)`
and in the C=3 lock's own 53-step heartbeat unit, by construction, not
by fit) — testing them against a ladder built from the same constant
they already contain would be circular, so the ladder test is applied
only to the two instruments whose native units are NOT already locked
to 53: the basin (native unit: odd-steps) and, as a secondary check,
the death shell's own m-axis scale.

**J2 reframed — basin's characteristic depth is a categorical
non-match to the convergent ladder, adversarially confirmed by a
null-model sweep. Reusing round-1's fit rates verbatim** (rho R²=0.022,
b R²=0.938, free R²=0.983 in the deep tail — see prior SYNTHESIS
section — NOT recomputed), the basin's exact e-folding depth
(`-1/ln(rate)`) across all three fit ranges is **14.4-17.3 raw
odd-steps** — under **1/3 of a single 53-step heartbeat**. Converted to
heartbeat units this is 0.2714-0.3262 heartbeats. The nearest
convergent-ladder value in every case is 1 (the trivial first
convergent p/q=1/1), at **67.4%-72.9% relative error** — not a
near-miss, a categorical failure to reach even the ladder's smallest
rung, let alone the first real tier (53), which is off by roughly
160x. **Adversarial null-model check**: sweeping every plausible basin
rate (r=0.900 to 0.970 in steps of 0.001, 70 points spanning the full
empirical scatter seen in round-1's per-step ratio table) against a
10%-tolerance match to ANY ladder value gives **0 of 70 (0.0%) hits** —
the non-match is not an artifact of an unlucky rate choice; the entire
plausible basin-rate range misses the ladder cleanly, by construction
of how small the basin's sub-heartbeat e-fold scale is relative to how
large the ladder's first real tier (53) is.

**Mandatory held-out prediction, constructed and FALSIFIED.**
Registered before checking: if the basin's ~15-16-heartbeat-fraction
depth were ladder/corridor-governed, the corridor's own
`M_edge(C)=floor(53(C+1)/22)` at that SAME depth should identify a
structurally distinguished corridor width C, independent of this fit.
Solving M_edge(C)=15 gives C≈5.23 (nearest integer C=5, M_edge(5)=14
exactly); M_edge(C)=16 gives C≈5.64 (nearest integer C=6, M_edge(6)=16
exactly). **Neither C=5 nor C=6 is flagged anywhere in the corridor's
own independent prior work as structurally special** — the corridor's
actual flagged widths are C=11 (the phase transition) and C=148 (the
F1 divergence). The held-out prediction fails outright: the basin's
characteristic depth does not point at any corridor-flagged structural
width.

**One new candidate surfaced, flagged, and explicitly NOT elevated.**
Checking C+1 (=12, for the corridor's flagged C=11 transition) against
the convergent-index of 84/53 (k=6, alpha's 6th convergent, 0-indexed)
gives an EXACT integer relation: 12 = 2×6. This is reported honestly as
an exact match — but is flagged as almost certainly a third instance of
the same reverse-fit shape already caught twice in this program (9/4,
prime-19), and once more within this very round (the rejected
cumulative-partial-quotient-sum=11 coincidence from round-1 J3): C+1=12
is fixed purely by the corridor's own definition (the phase-transition
width plus one) with no independent motivation tying it to "twice a
convergent index" ahead of noticing the match, and no second,
independently falsifiable held-out prediction was constructible from it
(unlike the basin case above, where M_edge(C) gave a genuine
before-the-fact check). Registered as **UNTESTED / NOT ELEVATED**, not
confirmed — consistent with round-1 J3's "no candidate survived
adversarial checking" verdict, which stands.

**J3 carried forward, unchanged.** Round-1's J3 verdict — 53 shared
exactly across corridor (53/22) and spectral (84/53, verified as
alpha's exact k=6 convergent) constants, C=11/exponent-6 relation
OPEN — already tested the "does the tier index advance by exactly 1
between corridor and spectral" question the peer's reframe asked for:
M_edge(11)=28≠84 (no match), convergent-index-of-84/53 (k=6) vs C+1=12
(not equal — though see the C+1=2k candidate above, newly surfaced this
round and explicitly not elevated). No new derivation was needed; the
verdict carries forward unchanged: **OPEN, no relation found that
survives adversarial checking.**

**J4, the actual IME test — NULL result, reported at full volume, not
softened.** Is a GHOST_PRECISION-shaped hierarchy (a fixed POPULATION
FRACTION stabilizing at a fixed low resource depth — 50%@1-bit,
77-89%@2-bit) present across the four instruments? Checked
instrument-by-instrument: the basin has no stable single geometric rate
at all (round-1's own held-out check already showed N=150-175's fit
fails to predict N=180-200 by -13% to -29%) — it does not even clear
the bar of ONE clean geometric regime, let alone a two-population
bulk/tail split. The death shell's dead-mass GROWS with m (P1) with no
fixed population fraction. The spectral radius's C=3-vs-C≥10 split is a
genuine two-regime structure, but it is a fixed-corridor-vs-variable-
corridor dichotomy, not a population-fraction split of individual
interactions the way GHOST_PRECISION's bit-depth histogram is. The
corridor's C≤147/C≥148 divergence (F1) is the closest analog to a
sharp-boundary split, but again a single width threshold in one
growing formula, not a population-fraction split. **Verdict: a
hierarchy in the loose sense (four different, ordered, distinct
quantities) trivially exists — but it is NOT geometric-bulk/heavy-tail
shaped in the GHOST_PRECISION sense, and its tier boundaries do NOT
land on the convergent ladder** (basin: categorical non-match, 0%
null-model hit rate, held-out prediction falsified; death shell/
spectral/corridor: already heartbeat-native by construction, excluded
from the test as circular). **Against the architect's frozen
prediction ("the four instruments DO form an IME hierarchy with
convergent-ladder tiers, ~60%, genuinely open"): REFUTED for this
specific pre-registered pairing and test.** This is reported as a full,
loud NULL — not "inconclusive," not "needs more data" — the adversarial
null-model sweep and the held-out corridor-width prediction were both
constructed specifically to give IME a fair, falsifiable chance, and
both came back negative. This does not refute IME as a general
principle (the primer's own attention/neuroscience/tetrahedral-angle
evidence is untouched by this result) — it refutes, specifically, the
claim that THESE FOUR COLLATZ INSTRUMENTS' characteristic depths sit on
log2(3)'s convergent ladder in the pre-registered pairing tested here.
A future round could retest under a different, equally-principled
pairing (e.g. testing the death shell's m=359 scale or the spectral
m-axis directly against the ladder, rather than converting the basin to
heartbeat units) — but that would be a NEW pre-registration, not a
rescue of this one.

## W7B C=31 HIGH-CAP EDGE RECEIPT (2026-07-07)

The W7B sparse live-set edge series is now validated through C=31. The
earlier C=31 result in `shell/underlock/w7b_deep/sweep_output.log` was not
an edge: it hit the chosen 64M state cap at m=48
(`n_exact=69,084,627`, `first_dead=None`, `genuine_death=False`) and was
correctly excluded from `w7a_new_edges.txt`.

The high-cap follow-up `shell/underlock/w7b_deep/run_c31_highcap.py`
raised the cap to 120M states / 28GB RSS, re-ran the frozen validation gate
(C=16=93, C=23=163, C=26=205), and completed C=31 with a genuine death:
`M(31)=284`, `first_dead=285`, `peak_live=73,462,829`,
`elapsed_sec=48,854.99644827843`, `wall=None`, `genuine_death=True`.
The append-only edge file now records:

```
27 208
28 263
29 265
30 282
31 284
```

Interpretation: the C=31 chosen-cap wall was a budget wall, not a
mathematical wall. Raising the cap resolved the cell. The current measured
post-C=26 edge series remains monotone but jagged: C=27..31 gives
208, 263, 265, 282, 284. The next unknown cell is C=32; nothing about C=32
is implied without a fresh validated run and death certificate. Full process
receipt is in `IMPLEMENTATION_LEDGER.md` section "2026-07-07 - W7B C=31
High-Capacity Sparse Edge Receipt" and local findings are in
`shell/underlock/w7b_deep/W7B_FINDINGS.md`.
