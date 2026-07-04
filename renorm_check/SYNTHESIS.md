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
