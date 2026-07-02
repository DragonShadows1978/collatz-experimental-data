# Ghost Geometry
## A Precision-Collapse Framework for the Collatz Conjecture, and Its Measured Transfer to Transformer Attention

**David Perry** — Independent Researcher (no institutional affiliation)
`dave@ai-storyforge.com`

*Release v1.0-rc — 2026-07-02. This document is the citable companion to two
artifacts it summarizes and audits: `COLLATZ_PROOF.md` (the full framework,
2026-05-26) and AtlasForge mission 4482de7b (GHOST_PRECISION, the attention
measurement). It supersedes the May 2026 working note (`collatz-ml-bridge.md`)
wherever numbers differ; all figures below are taken from the final artifact
reports, not from interim summaries. Text licensed CC BY 4.0; the implementations are separately licensed
AGPL-3.0 with commercial licensing available.*

---

## Author's Note and Disclosure

This work is by an independent researcher without academic affiliation, and it
was produced with substantial assistance from AI systems: ChatGPT for
mathematical formalization, Claude for analysis, verification, and
documentation (including this document), Codex for compiled Rust
implementations, and AtlasForge (the author's autonomous research platform,
itself open source — MIT, https://github.com/DragonShadows1978/AI-AtlasForge,
PyPI `ai-atlasforge`; the specific mission workspaces and artifacts cited
below are project-local, not part of that repository)
for the empirical measurement engine. The dimensional-escalation strategy, the
4D coordinate system (odd-step time, total exponent, deficit, residue
precision), the cross-domain hypothesis, and all research direction are the
author's; the author never wrote an equation, and the AI systems never chose
the direction. All computation ran on consumer hardware. The author accepts
full responsibility for the content.

**Status claim, stated plainly:** the Collatz framework below is NOT presented
as an accepted formal proof. It is presented as (i) a novel reformulation with
several independently checkable lemmas, (ii) a set of exhaustive computational
certificates, and (iii) — the claim we do stand behind — the tightest
structural specification of a hypothetical Collatz counterexample known to us.
The document includes its own adversarial gap audit (§4), which enumerates
exactly where the argument falls short of proof. Readers are invited to attack
the gaps; the framework was built to hand off.

---

## 1. The Program in One Page

A study of the Collatz map's precision dynamics produced a structural law:

> In hierarchical computational systems, the precision required per
> interaction decays geometrically, and sustained high-precision operation is
> structurally unsustainable.

In the Collatz setting this law manifests as the incommensurability of base 2
and base 3: an orbit that avoids descent must maintain ever-deeper agreement
between binary and ternary structure, and the capacity for that agreement is
finite at every scale (§2–3).

The law then made a falsifiable prediction in an unrelated domain: the
per-interaction precision depth of transformer attention should be
geometrically distributed — most query–key products should resolve at 1–2
bits, with a thin high-precision tail. This was measured directly
(GHOST_PRECISION, §5) across four models including a 7B-parameter model, and
the prediction held in shape (geometric bulk, heavy tail) while failing in
constant (attention's decay rates are 2–10× the Collatz constant). The
measured two-regime structure — cheap bulk plus expensive rare tail — became
the design specification for Adaptive Precision Attention (APA), documented
separately [APA paper, ref. 10].

The chain number theory → structural law → registered prediction → independent
measurement → working kernel is the contribution this document exists to
timestamp.

---

## 2. The Collatz Framework (Summary)

Full statements and proofs are in `COLLATZ_PROOF.md`; this section is a map.

**The object.** For odd `x`, the odd-only map `S(x) = (3x+1)/2^{v₂(3x+1)}`.
Deficit `d_k = ⌊kα⌋ − A_k` with `α = log₂3`; a non-descending orbit must keep
`d_k ≥ 0` infinitely often, and splits into three regimes: cycle, bounded
glider (deficit in a corridor `[0, C]`), or unbounded escape.

**The instrument.** A deterministic residue automaton `A(C, m)` tracks every
(deficit, residue mod 3^m) state a non-descending orbit in corridor `C` could
occupy, under the exact Collatz transition `r → (3r+1)·(2^a)⁻¹ mod 3^m`. It
does not sample or approximate. When its survivor set empties, no residue
class — hence no integer with that residue — can continue in that corridor at
that precision.

**The heartbeat.** The Sturmian word of `α` has, per 53-step block (the 84/53
convergent), exactly 22 support phases — where the terminal residue moves
(`4·2⁻¹ = 2 mod 3^m`) and states are eliminated — and 31 drop phases — where
it is fixed (`4·4⁻¹ = 1`). These are two-line identities, independently
checkable.

**The measured laws.**
- *Capacity edge:* the automaton's survivor set empties at precision
  `m = ⌊53(C+1)/22⌋ + 1`. Verified with full precision-countdown ladders
  (exact at every rung) at C = 3, 4, 5; for C = 6–50 the m = 1 lifetime
  probes are consistent with the formula (48 widths total). Zero exceptions.
- *Spectral certificates:* the killed survivor graph's heartbeat operator has
  spectral radius ρ < 1 at every tested (C, m), C ≤ 200, m ≤ 13; at C = 3 it
  locks at ρ = 0.9607 for all m ≥ 10 (a permanent 3.94% contraction per
  heartbeat). The gap decays as b^m with fitted b = 0.0631, matching (53/84)⁶
  to 0.01% — a structural observation, not a load-bearing step.
- *Product-space extinction:* the strongest object in the framework. A
  product automaton tracks (deficit, residue mod 3^m, odd residue mod 2^j)
  with the exponent **pinned by the 2-adic coordinate** — each state has at
  most one successor; there is no branching, no weighting, no measure theory.
  Its survivor set empties at every tested configuration: C = 1 through
  10,000, m ≤ 8, j ≤ 14, up to 215 million states. Zero exceptions. This is a
  pointwise statement, built specifically to answer the standard objection
  that measure-zero bounds cannot exclude integers.
- *Exhaustive scans:* all odd integers to 10^11: maximum deficit reserve
  observed 31 bits at the q = 53 convergent, versus ~149 required to bridge
  to the next convergent (k = 359). Every reconstructed "last survivor"
  residue witness collapsed to 1 when followed forward (max excursion:
  corridor 9, 157 steps).

**What this buys.** A hypothetical counterexample must simultaneously: exceed
the ~2^71 verification frontier; thread residue classes through automata whose
survivor sets empty at capacity-formula precision at every corridor it visits;
satisfy 2-adic congruences that compound toward a 2-adic limit shown to be
non-integer in the consecutive case; and climb a convergent ladder of log₂3
whose measured gaps exceed measured maximum reserves by a factor of ~3–4×,
inside a landscape contracting at a computed ρ < 1 per heartbeat. We know of
no published characterization of a Collatz counterexample this constrained
(see §3 for how this relates to known results).

---

## 3. Relation to Known Results

- **Tao (2019)** [1] proves that almost all Collatz orbits attain almost
  bounded values — the strongest known theorem, and a *density* statement:
  counterexamples are logarithmically rare. The present framework is on a
  different axis: it is a *pointwise structural specification* of what any
  individual counterexample must be. The two are complementary; neither
  implies the other.
- **Cycle bounds** (Simons & de Weger [2], building on Eliahou's
  continued-fraction method) exclude m-cycles using the convergents of log₂3
  — the same skeleton as this framework's convergent ladder and heartbeat.
  Our cycle exclusion (Theorem 3 of `COLLATZ_PROOF.md`) explicitly
  incorporates their certificate and inherits its finite bound; see gap G6.
- **Computational verification** (Barina [3]) has checked convergence for all
  starting values into the ~2^71 range; the framework's exhaustive scans
  (10^11) are much smaller in raw range but measure different observables
  (deficit reserves, corridor breaches, witness follow-through) that raw
  convergence checking does not record.
- The framework's spiritual kin is the study of the Diophantine properties of
  log₂3: every lock bottoms out in the irrationality and continued fraction
  of that single constant. We believe the right specialists for the remaining
  gaps are in Diophantine approximation, and this document is written to be
  handed to them.

---

## 4. The Gap Audit (What Is NOT Proven)

This section is the document's spine. It merges the project's internal
red-team review (`collatz_proof_red_team_problem_list.md`, thirteen
problems — items #1–#6 map into G1–G7 below; the remainder are
presentation-level or scoping items adopted directly into the current
`COLLATZ_PROOF.md`) with two further gaps found in a July 2026
external-style review. A reader who
wants to attack the framework should start here.

- **G1 — The capacity lemma's counting argument (red team #5; the central
  gap).** Theorem 1's proof asserts that 22m constraint events "consume"
  53(C+1) phase-height cells, each cell absorbing at most one constraint. No
  injection from constraint events to cells has been constructed; as written
  this is an accounting metaphor, not a pigeonhole proof. The formula it
  predicts is exact on every full ladder tested (C = 3, 4, 5) and consistent
  with the m = 1 probes at C = 6–50 — strong evidence the *formula* is
  true, no substitute for a proof of it.
- **G2 — Terminal-residue coincidence at large x₀.** The emptiness argument
  treats states reaching `r ≡ 1 mod 3^m` as terminated, and argues the
  modulus dwarfs orbit values so `r ≡ 1` means value 1. That holds only for
  x₀ small relative to 3^{M_edge}; for sufficiently large integers a
  "terminal" state is a residue coincidence, not a termination, and automaton
  emptiness no longer contradicts the orbit's existence. The Precision Ratio
  Lemma (automaton reach = 3.82× the integer's ternary precision) points at
  the quantity a repair needs, but the argument as written does not close it.
  A July 2026 verification pass found the same hole from the other side:
  the Precision Ratio Lemma's derivation drops the log₃(n₀) term (its ratio
  table reports the n₀-free component), and for counterexample-scale starts
  (n₀ > 2^71, log₃ n₀ ≈ 45) that term dominates every corridor row with
  C ≲ 70 — the 3.82× tracking margin is asymptotic in corridor width, not
  uniform. (Overlaps red team #4, Lemma 4 under-proving.)
- **G3 — The scattered-exit case of escape (Theorem 5, Part 1).** Consecutive
  ceiling exits force x₀ = −1 ∈ ℤ₂ (proven). Scattered exits compound to
  *some* 2-adic limit, and the argument that this limit cannot be a positive
  integer leans on interior emptiness (Door 1) — which carries gap G2. The
  interlock is genuinely suggestive; it is not yet a chain of implications.
- **G4 — Spectral and extinction certificates are finite.** ρ < 1 is verified
  on a finite grid (C ≤ 200, m ≤ 13) and extrapolated via the fitted b^m gap
  law; product-space extinction is verified to C = 10,000 at bounded (m, j).
  "At every (C, m)" is an inference from zero exceptions, not a theorem. The
  qualitative argument (31 killing phases vs 22 preserving phases) is a
  heuristic, not an eigenvalue bound.
- **G5 — Regime decomposition and corridor bookkeeping (red team #1, #2,
  #6).** The cycle/glider/escape trichotomy and the consistency of the
  corridor width C across sections need tightening; cycles are not "bounded
  gliders" under the current corridor definition.
- **G6 — Cycle exclusion is certificate-bounded.** Theorem 3 rests on the
  Simons–de Weger certificate, which is finite (no nontrivial m-cycles for
  m ≤ 68, extended to m ≤ 91 by Hercher [2]); unconditional cycle exclusion
  is not known — here or
  anywhere. (An earlier mis-citation of this result in `COLLATZ_PROOF.md`
  was found and corrected during release review.)
- **G7 — Lock 1 provenance (red team #3).** The periodic-engine impossibility
  argument was produced by an AI collaborator and has not been independently
  verified; its dependence on the Delta-Prefix Invariant is scanned, not
  proven.

We note what the audit does *not* contain: no gap has been found in the
heartbeat identities (Lemmas 3, 5a, 5b), the ghost fixed-point lemma, the
automaton's transition fidelity (Lemma 4a), or the computational certificates
as computations. The gaps are in the glue, not the bricks.

---

## 5. The Attention Transfer: GHOST_PRECISION

### 5.1 Hypothesis

If the precision-decay law is structural rather than Collatz-specific, then
transformer attention — a hierarchical accumulation of query–key interactions
— should exhibit geometrically distributed per-interaction precision depth:
most dot products resolvable at very low bit-width, deep precision
exponentially rare. The distribution-family claim was registered before measurement (the
mission specification's hypothesis is that depth "follows a geometric
distribution"); whether the Collatz constant (0.079) itself transferred was
left as an open question and answered in the negative by the measurement
(Q2, §5.3).

### 5.2 Instrument

AtlasForge mission 4482de7b (`ghost_precision/` package: `core/depth_engine.py`,
`core/statistical_analysis.py`, model/corpus adapters, orchestration). For
each attention head:

1. Extract full-precision (float32) Q and K; compute reference weights
   `softmax(QKᵀ/√d_k)`.
2. For bit-depths b ∈ {1, 2, 3, 4, 6, 8, 12, 16}: fake-quantize Q and K
   (asymmetric per-tensor min–max affine quantization — qmin = 0,
   qmax = 2^b − 1, clamp–round–dequantize) and recompute the weights.
3. The **interaction depth** δ(i,j) is the smallest b at which
   `|w_b − w_full| / |w_full| < ε`; pairs that never stabilize are assigned
   the full-precision depth.
4. Fit geometric, power-law, and exponential distributions to the depth
   histogram by maximum likelihood; compare by AIC/BIC and Vuong's
   closeness test; χ² goodness-of-fit with standard low-expectation bin
   merging. Detect "ghosts" (high-depth, low-weight pairs) and "phantoms"
   (high-weight pairs resolvable at 1–2 bits).

Inputs span eight text categories (code, conversational, paragraph, and
structured among them); sequence lengths 128 and 512; tolerances
ε ∈ {0.01, 0.001, 0.0001}. Test sensitivity was audited by mutation testing
(see mission artifacts).

A note on why these figures deserve trust: the measurement methodology is
itself inspectable software rather than prose. AtlasForge missions run a
stage-gated loop in which artifacts are adversarially reviewed,
health-checked, and mutation-tested each cycle, and results are regenerated
only after found defects are fixed — falsification is platform
architecture, not authorial discipline. The adversarial stages deliberately
exploit the generative model's bias toward confabulation, aiming it at
failure hypotheses — concrete inputs and states under which an artifact
*could* break — which are then mechanically tested against the real code
and data: hallucination repurposed as hypothesis generation, with the
verification gate as the only arbiter of which conjectures were real. The GHOST_PRECISION artifacts
preserve this history in full (four cycle health reports, a bug-fix plan
that caught a NaN-silent ghost detector and a stabilization boundary bug,
and the post-fix re-run that produced every figure used here), and the
platform code implementing the loop is public (MIT). This document's own
correction of the May working note (§5.3) is that machinery working as
designed.

### 5.3 Results (final artifact report; supersedes the May note's figures)

Four models: GPT-2 124M, TinyLlama-1.1B, Qwen2.5-1.5B, and Mistral-7B-v0.1
(70.6M measured interactions per configuration at 7B — the scale question the
May note listed as open, answered here).

| Model | Mean decay rate (± sd) | vs Collatz 0.079 | ε=0.01 preferred fit | Ghosts | Phantoms |
|---|---|---|---|---|---|
| GPT-2 124M | 0.430 ± 0.184 | 5.4× | geometric (both seq) | 0 | ~500 (cap) |
| TinyLlama-1.1B | 0.310 ± 0.159 | 3.9× | geometric @128 / power-law @512 | 0 | ~500 |
| Qwen2.5-1.5B | 0.282 ± 0.134 | 3.6× | power-law (all configs) | 0 | ~500 |
| Mistral-7B | 0.288 ± 0.122 | 3.6× | geometric (Z = 646.5) | 0 | ~500 |

Findings, stated with the final report's numbers:

- **The two-regime structure is universal.** Roughly half of all
  interactions resolve at 1 bit in every configuration (49.6–60.9%),
  exceeding 50% on every model at working tolerance ε = 0.01 (e.g.
  Mistral-7B: 51.2%; GPT-2: 50.5%) and dipping to 49.6–51.4% at ε ≤ 0.001,
  always with a heavy high-precision tail. At tight tolerance the tail's
  power-law character dominates the fit on all models.
- **The exact bulk family is tolerance- and model-dependent.** At loose
  tolerance (ε = 0.01), geometric is Vuong-preferred on GPT-2, TinyLlama
  (seq 128), and Mistral-7B — decisively at 7B as well (Z = 646.5, p ≈ 0;
  the study's largest geometric statistic is GPT-2 at seq 512, Z = 1579.6)
  — while Qwen2.5 prefers power-law at every tested tolerance, and the
  largest-magnitude statistics overall favor power-law at tight tolerance.
  The May working note's blanket claim ("geometric wins at ε = 0.01 across
  all models") was an interim-cycle result and is corrected here.
- **Scale does not break the law.** Mistral-7B's mean decay (0.288) is
  indistinguishable from Qwen2.5-1.5B's (0.282): decay slows from GPT-2 to
  modern architectures but plateaus rather than vanishing with scale.
- **Ghosts do not exist; phantoms do.** Zero high-depth/low-weight patterns
  in any configuration; hundreds of high-weight pairs resolvable at 1–2 bits
  in all of them. The tail that a precision-allocating method rounds is
  genuinely low-mass.
- **The Collatz constant does not transfer; the shape does.** Measured decay
  rates run 2–10× the number-theoretic constant. The hypothesis was
  structural and survives; a numerical transfer would have been suspicious.

### 5.4 What the measurement fed

The measured structure — cheap bulk plus rare expensive tail, with the tail
low-mass by the phantom/ghost census — is implemented directly as Adaptive
Precision Attention: a low-bit bulk pass over all keys, full-precision
refinement of the softmax-dominant fraction, exact denominator. APA's own
validation (seven models across four attention families plus MoE, retrofit
and trained-from-birth) is documented in the companion paper [10].

---

## 6. Falsifiers

The program makes commitments that future work can break:

1. A constructed injection failing for the capacity lemma at some corridor
   width (G1), or a corridor width where the M_edge formula misses.
2. A product-space configuration whose survivor set does not empty.
3. A model family whose attention shows no low-bit bulk (e.g. <20% of
   interactions resolving at ≤2 bits at ε = 0.01) — this would break the
   structural law where it is cheapest to test.
4. An orbit exceeding the k = 53 reserve wall (deficit reserve > ~40 within
   reach of scanning) — the convergent-ladder mechanism predicts this will
   not occur below reserves of ~85.

---

## 7. Artifact Index

- `COLLATZ_PROOF.md` — the full framework (theorems, lemmas, certificates).
- `collatz_proof_red_team_problem_list.md` — internal adversarial review
  (source of G1, G5, G7; published with this release).
- Rust engines: backward solver, `spectral_radius_sparse`,
  `product_automaton` (this repository).
- GHOST_PRECISION: AtlasForge mission 4482de7b — `ghost_precision/` package,
  `artifacts/report.md` (final numbers), `artifacts/results/`
  (per-configuration distributions, layer-decay and heatmap figures,
  `experiment_results.json`, `mistral_results.json`), mutation-testing
  reports.
- `collatz-ml-bridge.md` — the May 2026 working note (historical; superseded
  by this document where figures differ).

## References

1. Tao, T. *Almost all orbits of the Collatz map attain almost bounded
   values.* Forum of Mathematics, Pi, 2022. arXiv:1909.03562.
2. Simons, J., de Weger, B. *Theoretical and computational bounds for
   m-cycles of the 3n+1-problem.* Acta Arithmetica 117(1), 51–70, 2005.
   (No nontrivial m-cycles for m ≤ 68; extended to m ≤ 91 by Hercher, C.,
   *There are no Collatz m-cycles with m ≤ 91*, J. Integer Sequences 26(3),
   Article 23.3.5, 2023, arXiv:2201.00406.)
3. Barina, D. *Convergence verification of the Collatz problem.* J.
   Supercomputing 77(3), 2021 (online 2020); and *Improved verification limit for the convergence
   of the Collatz conjecture.* J. Supercomputing 81:810, 2025 (frontier 2^71).
4. Lagarias, J. C. *The 3x+1 problem: an annotated bibliography.* arXiv:
   math/0309224 (and *The Ultimate Challenge: The 3x+1 Problem*, AMS 2010).
5. Vuong, Q. H. *Likelihood ratio tests for model selection and non-nested
   hypotheses.* Econometrica, 1989.
6. Vaswani, A., et al. *Attention Is All You Need.* NeurIPS 2017.
   arXiv:1706.03762.
7. Radford, A., et al. *Language Models are Unsupervised Multitask Learners.*
   OpenAI, 2019. (GPT-2)
8. Zhang, P., et al. *TinyLlama.* 2024. arXiv:2401.02385. — and Qwen Team,
   *Qwen2.5 Technical Report*, arXiv:2412.15115; Jiang, A. Q., et al.,
   *Mistral 7B*, 2023, arXiv:2310.06825.
9. Tishby, N., Zaslavsky, N. *Deep learning and the information bottleneck
   principle.* 2015. arXiv:1503.02406.
10. Perry, D. *Selective Attention Is All You Need: Adaptive Precision
    Attention.* Companion paper, 2026 (released alongside this note).

---

## Suggested Citation

Perry, D. (2026). *Ghost Geometry: A Precision-Collapse Framework for the
Collatz Conjecture, and Its Measured Transfer to Transformer Attention.*
Zenodo. `[DOI on release]`
