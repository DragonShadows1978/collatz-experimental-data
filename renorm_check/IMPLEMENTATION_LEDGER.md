# Renormalization Recon — Implementation Ledger

Tracks execution of the work orders (W1–W4) registered in SYNTHESIS.md.
Per the execution notes: updated after every completed step, commit after
every completed work item.

## Round 2 (Fable, 2026-07-03) — death shell discovered

Attempting the W2 commuting-diagram proof surfaced a sharper object than
the embedding: a universal ceiling-anchored dead set ("death shell")
whose descent with m IS the capacity law. Findings F6–F9 + revised work
orders W2′/W5/W6/W7 registered in SYNTHESIS.md (Execution round 2
section). Artifacts: `shell/shell_probe.py` + `shell/shell_probe.log`
(probes P1–P6, all asserted, all passing): shell existence/growth,
cross-C universality, M_edge reproduced 5/5 densely, edge
steps-invariance, D(m) inverse-law match m=2..12 with first divergence
confirmed at m=359, and trit-locality (k-step liveness reads only the
low k+1 trits) machine-verified. F5 remains OPEN; W7 (shell-guided
witness search) and W6 (shell recursion) are the two live routes.

**W6 first execution (same day, `shell/boundary_probe.py` + log):**
death proven+verified hereditary (shell = monotone 3-adic closed set);
no naive cylinder compression (newly-dead sets read all m trits); but
ceiling subtree-types saturate (19→54, increments dying) and die-rate
tracks the credit word 10/10 — evidence the boundary recursion is a
finite transducer driven by the Sturmian word. Transducer-extraction
work order + frozen validation gates registered in SYNTHESIS.md W6.
This is the current cheapest route to deciding 358 vs 359.

**W6 second execution (2026-07-03, `shell/transducer_extract.py` +
log): preliminary, SUPERSEDED — see the authoritative E1 run below.**
This first re-attempt used a self-invented "ratio < 3x" stabilization
threshold read out of SYNTHESIS.md's prose rather than a written work
order, and only tested ceiling depth (delta=0). It found the same
qualitative signal (h=4 growing, not saturating) but is not the
canonical execution; superseded once `shell/W6_WORK_ORDER.md` (the
precise, authoritative E1-E4 spec, apparently written by whichever
session most recently extended this track) was found on disk.

**W6 authoritative execution (2026-07-03, `shell/e1_stabilization.py`
+ `e1_stabilization.log`, exactly per `shell/W6_WORK_ORDER.md`'s E1):
FAILED, unambiguously — E2/E3/E4 correctly never attempted.** Per the
work order's exact criterion (h=3→h=4 type count UNCHANGED, no
threshold), tested at all 9 required (delta, m0) pairs — delta=0,1,2 x
m0=8,9,10 — plus the fallback h=4→h=5 check at the 3 pairs where h=5
was reachable (m0=8 only; m0=9,10 need dense level 14/15, beyond the
13-level ceiling this repo's 4e8-state guard allows at C=12). **Every
single (delta, m0) pair is unstable, by a wide margin** — h3→h4 counts
roughly double or more everywhere (e.g. delta=2, m0=9: 492→1282;
delta=1, m0=9: 354→815), and the one h4→h5 data point available
(delta=2, m0=8: 767→1174) shows the same continued growth, not a
narrowing gap. This is not a borderline call decided by an arbitrary
threshold — the work order's own hard bar (exact count equality) is
missed by hundreds of states at every test point.

**Per the work order: STOP. E2 (transducer extraction) was correctly
NOT attempted.** The follower set does not stabilize at any reachable
horizon (2 through 5) or corridor depth (0 through 2) under dense
enumeration at C=12, m≤13. This is reported as the work order requires
— plainly, without retrying against a looser bar to manufacture a
pass. **W6's transducer route is a dead end at every scale this repo
can compute densely.** It remains possible (not ruled out) that the
boundary map is sofic in a different coordinate system (the work
order's own suggested fallback: Ostrowski reindexing) or at horizons
beyond what dense enumeration reaches — but that is a materially
different, harder undertaking than what W6 registered, not a next step
already in scope. F5 remains OPEN; W7 (shell-guided witness search) is
now the only registered live route to F5, and it was not run this
round (see W1).

## W6B — Toy-word mechanism experiment (`shell/W6B_TOY_WORD_ORDER.md`)

**Context:** registered as W6's replacement after E1 failed — a direct
mechanism test needing no transducer/extrapolation, on a system whose
own divergence points are densely computable (unlike the real word's
m=359). Same automaton (`shell/toy_word/toy_automaton.py`,
`run_heartbeat_generic`, imports the real `allowed_exponents`/
`mod_inverse` unchanged from `embedding/automaton.py`), driven by
`credit_toy(k) = floor((k+1)φ) − floor(kφ)`, φ = golden ratio, exact
via `(k + isqrt(5k²))//2` — cross-checked against 60-digit `Decimal`
for k=0..100000, zero mismatches.

**T1 (port sanity): PASSED.** `run_heartbeat_generic` + the TRUE word
reproduces D(m) for m=2..12 and all five known edges (C=1..5) bit-for-
bit against `shell_probe.py`'s own results, using the exact same code
path the toy run uses. Confirms the generic automaton is a faithful
port, not a reimplementation with its own bugs.

**T2 (toy shell survey): PASSED, as expected.** Heredity holds exactly
(0 violations, m=3..10, C=12 — the underlying proof is word-
independent, so this is a confirmation not a discovery). Universality
holds across C=8/12/23 at m=2..6. The toy shell grows qualitatively
like the real one (shell-depth 0→9, dead-fraction 2%→17% over m=1..10
at C=23) — a genuine structural analogue, not a degenerate toy.

**T3 (the measurement): D_toy(m) computed, C=23, m=2..13, dense** (raw
data: `shell/toy_word/D_toy_table.csv`). Candidate laws (irrational
β_toy=2−φ; Fibonacci convergents 1/2, 2/5, 3/8, 5/13) tabulated via
exact integer arithmetic (isqrt-based comparison for the irrational
law, exact ceiling division for the rationals — both cross-checked
against 60-digit Decimal before use) BEFORE reading any D_toy value,
per the pre-registration discipline.

**T4 (readout): MIXED RESULT — the work order's own flagged "most
important possible outcome."** The work order's ideal case (one exact
constant offset between D_toy and a law, fit on the agreement region)
did NOT hold: agreement-row offsets are [1,0,1,1] at m=2,3,4,6, not
constant. Reported the honest fallback instead — best-fit constant
offset per law, mismatches counted openly, no cherry-picking:
- irrational (offset +1): 9/12 rows match, misses at m=3,8,11
- **3/8 (offset +1): 10/12 rows match, misses only at m=3,11 — the
  single best-fitting law of the five tested**
- 5/13 (+1): 9/12; 2/5 (+1): 8/12; 1/2 (+0): 7/12 (worst)

Critically, **every row where D_toy disagrees with BOTH the
irrational law and its best convergent (m=3, m=11) is a SHARED
failure** — not evidence for either side, most plausibly a small-m/
small-corridor-width transient (C=23's own boundary effects at low
depth). Where the two candidates genuinely differ (m=8, m=13), the
convergent 3/8 wins both times, and no row favors the irrational law
over 3/8. **Per the work order's pre-declared asymmetry: a convergent-
pinned toy is STRONG evidence against the registered F5 prediction
(359).** This is that outcome, though modest (10/12 vs 9/12, not a
landslide) and partly confounded by the shared-failure rows. Registered
plainly, not softened: **the toy experiment leans AGAINST 359, not
for it.** Per the work order's own framing, this materially weakens
(does not refute) the registered F5 prediction — the real word's α
being arithmetic-native (generated by the same 2 and 3 the corridor
itself is built from) remains a live reason the true system could
still differ from this toy. F5 remains formally OPEN; this is evidence,
not a resolution.

Artifacts: `shell/toy_word/{toy_automaton.py, t1_port_sanity.py,
t2_toy_shell_survey.py, t3_measurement.py, t4_readout.py}` +
`.log` files for each + `D_toy_table.csv`.

**Verification note (Fable, 2026-07-03, post-hoc, independent):** the
D_toy measurements REPRODUCE exactly — an independent from-scratch
implementation (no shared code with `toy_automaton.py`) returns
identical D_toy at m=5,8,11,13, and the values are steps-invariant
(53 vs 106 steps). Two corrections to the readout prose, from the
run's own CSV:
1. **There is ONE genuinely discriminating row, not two.** With the
   fitted +1 offsets, the irrational law and 3/8 differ only at m=8
   (predictions 4 vs 3; D_toy=3, convergent wins). At m=13 both
   predict 5 and both match — m=13 discriminates nothing between
   them. The 10/12-vs-9/12 lead rests entirely on the single m=8 row.
2. **"Small-m transient" mislabels m=11.** The shared-miss rows are
   m=3 AND m=11; the latter is not small-m. Note also every miss is
   D_toy running BELOW the laws (shell lagging), and the real system
   shows NO such transient (D matched exactly from m=2) — the toy's
   D-sequence is qualitatively messier than the real one, which
   weakens toy→real inference in BOTH directions.
Reinterpretation registered pre-capstone: the data pattern (all
misses on the slow side; best-fit line = the slightly-slower
convergent) is equally consistent with (a) genuine convergent
pinning, or (b) an irrational-slope law approached FROM BELOW with a
slowly-decaying transient that the toy's early divergence points sit
inside — a design weakness of W6B (golden's small denominators put
the decisive rows in the transient regime; the real system's m=359
sits far outside it). **Capstone row to discriminate: m=16, the next
irr-vs-3/8 head-to-head (predictions with +1 offsets: irrational 7,
3/8 pins 6; 5/13 also says 7, so m=16 additionally separates "pins
to 3/8 specifically" from "tracks finer convergents"). Dense at
C=14, ~hours, memory-guarded. Registered predictions: pinning ⟹ 6;
Fable ⟹ 7.** Belief update recorded honestly: the registered F5=359
confidence drops (one thin row against, transient-confounded), not
collapses.

**W6B capstone (m=16), executed 2026-07-03
(`shell/toy_word/capstone_m16.{py,log,csv}`): D_toy(16) = 6 —
CONVERGENT PINNING. Fable's registered irrational prediction (7) is
WRONG.** Controls first, both PASS: at C=14, D_toy(11)=4 and
D_toy(13)=5, identical to the prior C=23 run — corridor C=14 is not
floor-contaminated at these precisions; `credit_toy` cross-checked
against `toy_automaton.py`'s for k=0..100000, zero mismatches. The
measured 6 matches the 3/8 convergent's +1-offset prediction
specifically — it excludes BOTH the irrational law AND the finer 5/13
convergent (both predicted 7), answering the verification note's
secondary question: the toy pins to 3/8; it does not track finer
convergents. Shell depth at m=16 is 11, floor margin 3 to the C=14
floor (the death shell is not floor-truncated). Dense, 53 steps from
the fully populated start, 15.2 min total, peak RSS ~3.8GB in-run
(~4.3GB observed externally during permutation precompute), under the
8GB guard. Interpretation, no further: with both head-to-head rows on
record (m=8 and m=16) favoring the 3/8 convergent and none favoring
the golden slope, the transient-from-below alternative registered
pre-capstone is no longer the more economical reading of the toy
data — per the work order's pre-declared asymmetry this is further
evidence AGAINST the registered F5=359 prediction, while the real
word's arithmetic-native α remains the one registered reason the
true system could still differ.

**Capstone VERIFIED + post-capstone assessment (Fable, 2026-07-03):**
independent from-scratch reimplementation (no shared code;
`shell/toy_word/verify_m16.{py,log}`) returns D_toy(16)=6, shell
depth 11, control D_toy(13)=5 at C=14 — exact agreement. The
capstone stands. Assessment, recorded as the program's current best
model (not a resolution — F5 stays OPEN pending the real
measurement):
1. **Mechanism reading:** 53 is the near-identity return time of the
   2-3 rotation (3^53/2^84 ≈ 1.0005) — a convergent denominator IS a
   near-return time. The toy's lock to 3/8 (golden's den-8 return)
   over the finer den-13, with both in dense view, reads as the
   corridor QUANTIZING TO ITS OWN RETURN MAP, visible most strongly
   at the edge where trajectories are forced (F6 steering slack
   vanishes at the ceiling). This coheres with E1's failure: the
   dead SET is not finite-state, but the descent RATE is
   convergent-locked — complexity in the where, rationality in the
   how-fast.
2. **Transfer to the real system:** under either reading (permanent
   lock, or scale-graded upgrade — the toy rejected den-13 at m=16
   despite a full den-13 cycle being in view, suggesting an upgrade
   needs ≳2 full return cycles), the operative convergent at m=359
   is 22/53 (successor 127/306 would need m ≈ 306–612). Current
   best model therefore says **D(359)=149, C=148 edge = 358 — the
   published formula is exact at the decisive point, not a shadow.**
   The registered F5=359 prediction now trails by its own author's
   assessment (~30% from 85% pre-toy). The ~2-cycle upgrade rule is
   a one-data-point conjecture; the toy's next discriminator (m=21,
   3/8 vs 5/13) is dense-walled (3^21).
3. **Provability upshot:** convergent-locking moves the capacity
   lemma (the published framework's central gap) from irrational
   terrain (equidistribution) to rational terrain (finite periodic
   53-block algebra) — the periodicized scope of the ρ certificates
   (F2's worry) may be exactly right rather than an approximation.
4. **New central theory question:** the convergent-selection
   mechanism — what picks the lock, and where (if ever) it
   upgrades. Answering it analytically settles F5 without any
   m=359 computation. This appears to be new phenomenology for
   Beatty/Sturmian corridor systems generally.

## W6C — Convergent-selection mechanism (`shell/W6C_SELECTION_ORDER.md`)

Three designs, three parallel agents, disjoint directories under
`shell/selection/` (coordination law held: no shared-file edits, no
commits by agents; integration by Fable). Full findings in
SYNTHESIS.md W6C section; execution record:

- **Design A** (`selection/real_word/RESULTS_A.md`): A1 24/24
  identical rows — and the agent caught the comparison was vacuous by
  design (order author's error): the true word ≡ its 53-periodicization
  for k=0..357, first divergence k=358. Reported prominently per the
  honest-reporting law. A2 window slide: D varies ±1 with window
  support-count (r≈0.4). 6.8 min, 284MB peak.
- **Design B** (`selection/sqrt2/RESULTS_B.md`): pre-registration
  mtime-documented; controls pass; **D_√2(m)=⌈7m/12⌉ for all 15 rows**;
  unique separating row m=12 measured 7 (=7/12+1), triple-confirmed
  C=14/16/18, independently reproduced from scratch by Fable
  (m=9..13). Agent correctly surfaced the order's literal-vs-protocol
  conflict and deferred; procedural verdict (integration): **R-UNDER**.
  The order's zero-offset literals recorded as Fable's pre-data
  arithmetic error; the registered offset protocol governs. ~55 min,
  4.2GB peak.
- **Design C** (`selection/families/RESULTS_C.md`): √3 locks 1/4
  (UNDER, 13/14 rows, pre-registered side-row m=15 HIT); √6−1 and
  √7−1 exact three-way ties — honest no-decisions. ~13-27 min/family
  concurrent, 1.6GB peak.

**Integrated verdict: selection rule = finest under-side convergent
within the readable window (den ≲ m). 3/3 side-calls UNDER, zero
counterexamples. F5 inference flips back: 127/306 operative at m=359
→ D(359)=148 → edge 359. The W6B post-capstone 358-leaning assessment
is SUPERSEDED (golden could not separate the rules; √2 and √3 did).**
F5 remains formally OPEN. Next: W6D analytic lock proof (golden
period-8 block), upgrade-scale theory.

## W6D-G — Periodic-word ground truth (`shell/W6D_GROUND_TRUTH_ORDER.md`)

Executed by one agent in `shell/underlock/` (RESULTS_D1.md + CSVs +
laws files, mtime pre-registration held, independent brute-force
cross-check of the vectorized automaton, margin rule satisfied
everywhere, heavy √2 rows to m=16 at C=18 without guard hits).
Findings registered in SYNTHESIS.md W6D-G: exact periodic law
D_per(m)=⌊(pm+1)/q⌋ 28/28 with a confirmed forward prediction
(golden m=16 called =6 pre-computation, measured 6); PD1/PD2
REFUTED — true words carry a sign-definite intermittent +1 bonus
over their convergent words (golden 5/13 rows equal, √2 2/15, all
disagreements +1, rerun-confirmed), so the corridor DOES read
aperiodicity below the wall and P3 does not collapse; PD3 confirmed
(tiling-vs-mechanical trap real); periodic words show a ±1 phase
oscillation in step count (Sturmian words don't); real system's own
agreement-zone form is the mirror variant ⌊(22m−1)/53⌋ 11/11. F5
compressed to pure algebra: at m=359, 22/53 gives 149 (→358) under
both variants, 127/306 sits exactly on its coincidence boundary and
splits (+1→149/358, −1→148/359) — P1's return-map derivation of the
over/under form asymmetry decides. Process note: mid-run, a user
message reached this agent's session asking it to check GEMV router
state; it spawned one read-only Explore child for that lookup (no
writes, no collision with Codex's concurrent GraftRepository work),
reported it under the main session's scope check, and returned to
order. Coordination law otherwise held throughout.

## W1 — Exact-credit patch + F5 decisive experiment

**Patch: DONE.** `rust/lock3_census.rs`'s `credit_at_step` and the three
inline `((depth as f64) * ALPHA).floor()` call sites (in
`try_follow_down_exit_u128`, `try_follow_breach_u128`, and the two
`run_census`/`run_census_lean` per-depth loops) now compute
`floor(k*log2(3))` via `bit_length(3^k) - 1` on an arbitrary-precision
`BigBits` accumulator — no f64 involved. Also patched the analogous
`credit()` in `renorm_check/embedding/automaton.py` (Python arbitrary
precision `(3**k).bit_length()-1`), since the amended F5 method routes
through this module's oracle.

**Validation: PASS.** Rebuilt `lock3_census`, reran the genuine C=3,4,5
countdown ladders (m=1, depth=2000, `--memory-lean --no-checkpoint`) and
diffed against the pre-patch reference runs
(`data/runs/lock3_C{3,4,5}_N2000_residue_m1_lineage_cohorts_*`): every
column identical except `current_rss_kb`/`peak_rss_kb` (memory telemetry,
expected to vary run-to-run). `max_lifetime_of_valid1_lineage` = 9, 12, 14
for C=3,4,5 respectively — exactly `M_edge(C)`, confirming both the patch
and the known C3/C4/C5 corridor countdown relationship survive intact.
Cross-checked `credit_at_step`'s f64 vs exact-arithmetic outputs directly
(Python) for k=0..200,000: zero mismatches — the legacy f64 path was not
actually wrong at the scales previously exercised, but is no longer
trusted-by-luck.

**F5 (original method): INFEASIBLE, confirmed empirically.** Attempted
the full countdown ladder at C=147/148/149 (m=1, depth=2000) with the
patched binary. C=149 completed (`max_lifetime_of_valid1_lineage=361`,
matching `M_edge(149)=361` exactly — but this metric is definitionally
tied to the rational corridor construction the census tool implements,
so it cannot discriminate the 358-vs-359 question; it was not decisive
even though it completed). C=147/148 did not reach the same convergence
within reasonable wall-clock/memory before being killed — consistent
with the SYNTHESIS.md F5 AMENDMENT's own diagnosis that ladder-shaped
enumeration is infeasible near this precision.

**F5 (amended method, edge-witness search): PARTIALLY EXECUTED,
methodology validated, C=148 NOT YET DECIDED.**
- Validated `oracle.query_membership` against the three known edges:
  C=3 m=9 → witness found (235K calls); C=3 m=10 → exhaustive-empty (33K
  calls). C=4 m=12 → witness found (5.46M calls, needed a 20M cap — the
  original 2M cap gave a false "not found" from silently swallowing an
  inconclusive result, corrected per the amendment's own discipline).
  C=5 m=14 → witness found only after raising the cap to 100M (33.4M
  calls, 82s); at 20M cap it was correctly INCONCLUSIVE, not miscounted
  as false. All three edges reproduce their documented cutoffs (10, 13,
  15) via `M_edge(C)+1` exactly.
- Call-count scaling C=3→C=4→C=5 is roughly 7-8x per unit increase in C
  (235K → 5.46M → 33.4M). Extrapolating to C=148 (corridor width 149 vs
  6) is combinatorially infeasible for the plain backward-reachability
  oracle — confirms the amendment's own assessment. **C=148 is NOT
  resolved by this route either.**
- Per the amendment's step 4 (telescoping), the tractable path is: use
  W2's candidate-(c) embedding (if it survives exhaustively) to reduce
  C=148/m≈358 to the C=16/m≈40 question, both within the agreement zone.
  **This is not yet attempted** — W2's own exhaustive test hit its own
  tractability wall before reaching a usable exact-embedding conclusion
  (see W2 below), so telescoping is currently blocked on W2.

**F5 status: OPEN.** Neither the original ladder method nor the amended
witness-search method resolves 358 vs 359 at the scales reachable so
far. This is reported as an honest open blocker, not silently narrowed.
Next step if resumed: either (a) a smarter/bounded backward search
(tighter pruning, Ostrowski-graded state compression) to push the oracle
past C~10-20, or (b) get W2's candidate-(c) exact-survival result at a
size where the telescoping reduction is actually usable.

## W2 — Exhaustive candidate-(c) verification at the smallest pair

**(C=1, m=1) → (C2=23, m2=54): EXHAUSTIVE, CONFIRMED.** This is the
genuinely smallest pair (4 live states total on the small side — already
exhaustive in the prior sampled run, `sample_size == total_live_small`).
Candidate (c) (`c_forward53_a_eq_ck`): **4/4 matched, 0 failed, 0
inconclusive.** Each mapped residue lands on r2=1 (terminal state)
directly, resolving in 1 oracle call each. Zero counterexamples.

**(C=1, m=4) [=M_edge(1), 819 live states]: NOT ACHIEVED — tractability
wall, reported honestly.** Attempted exhaustive coverage of the next
meaningful (non-degenerate) pair. Individual oracle queries at
`(C2=23, m2=57)` for mapped residues took 13s+ each and did not resolve
even at a 5M call cap; pushing to 60M calls consumed >8GB of memoization
before being killed at the 300s mark. Dense forward computation at
(23,57) is also impossible (`3^57 ≈ 2×10^27` states, guard is 4×10^8).
Per W2's explicit discipline ("no oracle-call ceiling shortcuts that
convert inconclusive into silence... otherwise the result does not
count as exhaustive"), this is reported as **NOT tested**, not as a
pass. No promotion to formal conjecture follows from this round.

**Consequence for F5 telescoping:** blocked (see W1 above) — the exact
(C,m) size telescoping needs (C=16, m≈40) is well beyond what the
current oracle resolves exhaustively.

## W3 — Certificate 6 & 9 archival

**DONE.** Created `renorm_check/certs/`. Certificate 6: copied the
already-regenerated F3 sweep data (`rho_sweep_m3_C1_200.csv`,
`rho_m3_analysis_table.csv`/`.json`, `rho_sweep_m5_anchors.csv`,
`rho_m5_anchors_analysis_table.csv`/`.json` — full C=1..200 at m=3,
51-point anchor sweep at m=5, both from `renorm_check/run_rho_sweep.sh` +
`analyze_rho_structure.py` invoking the repo's own unmodified
`spectral_radius_sparse` binary). Certificate 9: fresh regeneration run,
`product_automaton` at C ∈ {3, 10, 50, 200, 1000} × j ∈ {10, 12}, m=4,
with enough heartbeats each to reach genuine extinction (not just a
single truncated heartbeat), plus a bounded C=10,000 m=1 capstone
confirming the "largest corridor" state-space claim (extinguished at
heartbeat 0 — different m than the certificate's own m=8, so not a
scaling-law data point, just a state-space-size sanity check).

**Result: zero exceptions, matches published numbers.** Every tested
(C,j) pair reached `SURVIVOR GRAPH EMPTY`. Scaling-rate check against
the certificate's claims:
- j=10 (claimed ≈6.18×(C+1)): C=1000 observed 6195 vs predicted 6186
  (0.14% off); C=200 observed 1254 vs 1242 (1% off); smaller C show the
  expected transient deviation (documented in the certificate text
  itself as a small-C effect).
- j=12 (claimed ≈3.34×(C+1)): C=1000 observed 3345 vs predicted 3343
  (0.06% off); C=200 observed 671 vs 671.34 (exact); C=50 observed 170
  vs 170.34 (exact).

Both headline scaling laws independently reproduced to within ~1% at
large C. Raw CSV+log pairs for all 11 runs archived under
`renorm_check/certs/`.

## W4 — G3 digit-density scan

**NOT STARTED this round — scoped, not executed.** G3
(COLLATZ_PROOF.md Theorem 5 Part 1, lines 356-367) is the gap between
the consecutive-ceiling-exit case (clean: forces `x0 = -1` in Z_2) and
the scattered-exit case (each ceiling exit still imposes a congruence
`x0 ≡ r_k mod 2^{N_k}` with `N_k → ∞`, but the compounded intersection
is only shown to be "some" 2-adic integer, not provably non-positive-
integer). The synthesis's phrasing ("support-phase pins nonzero digits
at positive density") names the natural empirical angle: if the digits
of `x0`'s 2-adic expansion forced by the scattered congruences are
nonzero at positive density (not just finitely many), that alone would
show the compounded limit isn't a positive integer (finite integers
have finitely many nonzero base-2 digits), independent of Door 1/G2.

This needs real design work before it's a runnable measurement, not
just an existing-tool invocation: (1) extracting actual scattered-exit
witness sequences (existing `corridor_breach_follows`/
`downward_exit_follows` structures in `lock3_census.rs` track `d_k`,
`a_k`, candidate residues post-exit, but not the pre-exit congruence
chain needed here), (2) reconstructing the nested congruence classes
each ceiling exit imposes on `x0`, (3) defining and measuring digit
density in the composed residue as the chain grows. None of this
exists in the repo yet. Deferred rather than rushed under the time
already spent on the W1/W2 tractability investigation above — flagged
here as the next open item, not silently dropped.

## W6E-E1 — Explicit-strategy upper bound (`shell/underlock/w6e/`)

Order: `shell/underlock/W6E_BOUND_PAIR_MECH_ORDER.md`. Ground truth
used (paths): `shell/underlock/D_golden_per8_table.csv` +
`D_golden_per8_m16.csv` (m=2..13,16), `shell/underlock/
D_sqrt2_per12_table.csv` + `D_sqrt2_per12_heavy_table.csv` (m=2..16),
`shell/underlock/underlock_words.py` (golden-per8, sqrt2-per12 credit
functions) — 28/28 rows total, per the order's scope. Bonus census
used the real system's own true word (`c_k =
floor((k+1)log2(3))-floor(k*log2(3))`, exact via bit_length) against
the mirror law `D_real(m)=floor((22m-1)/53)` (SYNTHESIS.md /
IMPLEMENTATION_LEDGER.md W6D-G section, 11/11 agreement zone m=2..12).

**Pre-experiment engine verification (house rule, done before any
result trusted):** `w6e/engine.py` + `w6e/verify_engine.py`. First
implementation attempt used the order's literal backward-chain
description (state=(rho,delta), delta starting at 0 at the terminal,
menu `a in [1,delta+c]` enforced live) — this made EVERY chain on
EVERY ground-truth row infeasible (0 surviving chains via exhaustive
DFS on golden m=2..8, sqrt2 m=2..5). Root-caused by cross-checking
against the validated forward automaton (same mechanics as
`embedding/automaton.py`/`toy_word/toy_automaton.py`, re-derived
scalar-style in `engine.bfs_Dm`): the window START (m steps before the
true 53-step terminal) sits at ceiling-distance 0, and the TERMINAL's
own ceiling-distance EQUALS D(m) itself — not 0. Confirmed by
extracting an explicit optimal forward chain (parent-pointer
backtracking) for golden m=3: delta path 0 -> -1 -> -1 (window start
at 0, if walked forward), i.e. the literal capped-at-0-start backward
model is simply the wrong initial condition for online strategy
evaluation (S0/S1 can't know D(m)=delta_terminal in advance — using
it to seed the cap would be circular). CORRECTED model: legality
during strategy construction is governed ONLY by parity-forced
integrality (`2^a*rho%3==0` iff class 0, else parity forced per the
order's F6 rule) with NO artificial ceiling cap; the strategy's own
running max partial sum is what gets compared post-hoc to
ground-truth D. Verified: uncapped exhaustive DFS full-minimax-search
reproduces ground-truth D(m) exactly on 8/8 sampled rows (golden
m=2..8); scalar (`bfs_Dm`) vs numpy-vectorized (`bfs_Dm_fast`) engine
paths cross-checked and agree on 16/16 sampled rows; fast-path engine
matches ALL 24 ground-truth rows attempted (golden m=2..13, sqrt2
m=2..13 — m=14..16 honestly skipped as a scope wall, heavy rows the
original W6D-G run itself needed a dedicated backgrounded runner for);
keystone identity (`2^Sigma_a == S mod 3^m`) holds on 6/6 sampled
extracted chains. **Engine PASSES the pre-experiment integrity check**
(far exceeds the 3-row minimum). Full account + all commands in
`w6e/engine.py`'s module docstring and `w6e/verify_engine.py`.

**E1 result (`w6e/e1_walkers.py`, `w6e/e1_results_28row.csv`,
`w6e/e1_results_bonus_real.csv`):** S0 (greedy, smallest legal
parity-forced exponent, no cap) and S1 (one-step steering among
{a,a+2,a+4}, avoiding next-step class-0) were run on all 28
ground-truth rows (backward-consumption letter order, anchored at the
true 53-step window per row) plus the 11-row real-system bonus census.

**S0: 28/28 exact match. S1: 28/28 exact match. Both QUALIFY as the
constructive upper-bound object.** Neither died nor exceeded D on any
row in scope (bonus census: also 11/11 for both). Tracing S1's
steering logic: it never actually triggered a non-greedy choice on any
row (`steered_count=0` everywhere checked) — the class-0 successor
trap the steering rule guards against simply never arises for these
periodic 2-symbol (golden-per8, sqrt2-per12) words at these scales, so
S1 degenerates to S0 exactly across the whole scope.

**Frozen predictions vs result:**
- "S0 fails somewhere (75%)" — **MISSED.** S0 matched all 28 rows.
- "S1 matches golden and sqrt2 families (65%) but full 28/28 only 45%"
  — **MISSED in the stronger direction**: S1 matched full 28/28, not
  a partial subset.
- "If BOTH fail, the upper bound needs deeper lift pre-commitment" —
  moot; both qualified outright, no lift-cascade evidence found at
  this scope (m<=16, both toy families).

Table shape: `e1_results_28row.csv` has columns m, D, S0_max_partial_
sum, S0_verdict, S0_died_at, S0_first_exceed_prefix, S1_* (same),
family (golden/sqrt2) — 28 data rows. `e1_results_bonus_real.csv` same
schema, 11 rows (m=2..12, real-system true word vs 22/53 mirror law).

## W6E-E2 — Phase pinning for F5 (`shell/underlock/w6e/e2_phase_pinning.py`)

Pure deterministic integer arithmetic (no automaton). Ground truth /
context: SYNTHESIS.md W6D-M section (`true=149 supports, periodic=150,
diff=-1, D=148, conditional F5=359`, computed on the 0..358 window);
SYNTHESIS.md's under-selection claim (127/306 operative convergent at
m=359, lines ~472/548/567/610-614); `embedding/automaton.py`'s `credit`
for the true word.

**Ambiguity surfaced and resolved by testing both candidates (house
rule: report, don't silently pick):** the order's E2 section doesn't
repeat which convergent (p,q) the "periodic comparison word" is inside
its own text — it just cites the general W6D_GROUND_TRUTH_ORDER.md
mechanical-word spec. SYNTHESIS.md's own W6D-M text says the prior
"150" figure is for "the 22/53-periodicization" (p,q)=(22,53), while
elsewhere SYNTHESIS identifies 127/306 as the operative convergent AT
m=359. Both were computed, start- and end-anchored, and cross-checked
against the prior claim: **only 22/53 reproduces the prior 149-vs-150
figure exactly** (127/306 gives 149-149=0 on the same start-anchored
window — it was never the word behind that specific "150" claim,
regardless of its separate operative-convergent status).

**Result (`e2_support_census.csv`, four/six counts as computed):**

| word | anchoring | k-range | supports |
|---|---|---|---|
| true | start | 0..358 | 149 |
| true | end | 12..370 | 149 |
| periodic 22/53 | start | 0..358 | 150 |
| periodic 22/53 | end | 12..370 | **149** |
| periodic 127/306 | start | 0..358 | 149 |
| periodic 127/306 | end | 12..370 | 149 |

**GATE VERDICT: the 149-vs-150 differential DOES NOT SURVIVE
end-anchoring** (22/53: start diff=-1, end diff=0). Under the
end-anchored window — the one that actually matches the real 371-step
measurement's own phase — true and 22/53-periodic support counts are
EQUAL (149 both). The conditional D(359)=148-\>edge=359 route, as
built on this specific support-count differential, LOSES its
arithmetic support once the correct (end-anchored) phase convention is
used. 127/306 shows zero differential under EITHER anchoring — it was
never evidence for either F5 branch via this mechanism.

**Frozen prediction ("differential SURVIVES", 70%) — MISSED.** Per the
order's own instruction, this is reported exactly as loudly as a HIT
would have been: the F5 conditional route built on the 0..358-window
149-vs-150 count was a **start-anchoring artifact**. This does not by
itself prove F5=358 (the conditional route was never a proof, and this
result only removes one piece of conditional support — see
DERIVATION_NOTES/SYNTHESIS for the other routes still in play), but it
removes the specific arithmetic plank the 359-leaning conditional
route stood on.

## W6E-E3 — Prefix-tightness census (`shell/underlock/w6e/e3_prefix_tightness.py`)

Ground truth / engine: same `w6e/engine.py` (`bfs_Dm(want_chain=True)`)
validated in W6E-E1, one regenerated optimal chain per row via
exhaustive scalar search with parent-pointer backtracking. Candidate
prefix bound: `floor((p*k+1)/q)`, golden-per8 (p,q)=(3,8), sqrt2-per12
(p,q)=(7,12) (the toy laws established in W6D-G RESULTS_D1.md).

**Scope wall (reported honestly, hit twice):** first attempt scoped
chain regeneration through m=13 for both families (matching E1's
scope); this alone exceeded a 280s background budget mid-run (m=10
golden chain extraction was still running after &gt;1 minute of CPU
time, having not yet reached sqrt2 at all) — killed and re-scoped
rather than let it run further, per the house rule ("if something
looks like it needs hours, you've mis-scoped it — stop and report the
wall honestly"). Re-ran capped at **m&lt;=9** (empirically fast: full
run, both families, 47s wall). Rows m=10..16 (golden: 10,11,12,13,16;
sqrt2: 10,11,12,13,14,15,16) were **NOT chain-regenerated** — no
prefix-tightness or keystone data for those rows in this experiment.
This is a real scope reduction versus the order's full 28-row ask, not
a silent one: 16 of 28 rows covered (8 golden m=2..9, 8 sqrt2 m=2..9).

**Keystone integrity check: PASS, 0 violations across all 16 chains
used** (every k=1..m on every chain). Engine integrity reconfirmed
independently of E1/verify_engine's own checks.

**Prefix-tightness result:** on every one of the 16 chains, **every
single prefix k=1..m is binding** (`g(k) == floor((pk+1)/q)` exactly,
for ALL k, not a subset) — see `e3_binding_prefixes.csv` for the full
per-(family,m,k) table. This is itself the headline finding: the
optimal chains are tight everywhere, not just at isolated phases.

**Binding-phase histogram** (`e3_binding_histogram.csv`, k mod q,
pooled across all rows of each family — NOTE: because every prefix
1..m binds on every row, and m varies row to row, the histogram shape
is mechanically dominated by how many rows have m&gt;=phase — this is
flagged explicitly as a likely artifact of "always-binding," not
necessarily evidence of genuine cycle-lemma phase preference):

- golden-per8 (q=8): all 8 phases hit; peak phase=1 (9/44, 20.5%);
  top-2 phases 38.6%.
- sqrt2-per12 (q=12): 9/12 phases hit; peak phase=1 (8/44, 18.2%);
  top-2 phases 36.4%.

**Gate verdict against the frozen prediction ("binding prefixes
cluster at a fixed phase mod q", 75%):** golden-per8 peak (20.5%) is
under the 2x-uniform threshold (25%) — **MISSED**. sqrt2-per12 peak
(18.2%) clears its 2x-uniform threshold (16.7%) — **HIT**, narrowly.
Given the "always-binding" mechanism identified above (the histogram
shape is largely explained by which rows reach which m, not a genuine
worst-phase concentration), this mixed HIT/MISS at scope m&lt;=9 should
be read with that caveat attached rather than as clean confirmation or
refutation of the Raney/cycle-lemma route; a m&gt;9 rerun (with a faster
chain-extraction path than the current scalar dict BFS) would be
needed to separate the two effects, and is NOT attempted here (scope
wall, reported above).
here as the next open item, not silently dropped.

## W6F-F0 — Systematize the W6E spot-check (`shell/underlock/w6f/f0_spotcheck_systematize.py`)

Order: `shell/underlock/W6F_OPTIMAL_SET_ORDER.md` section F0. Reuses
`w6e/engine.py`'s `bfs_Dm(..., want_chain=True)` unmodified. For every
row m<=9 (golden-per8, sqrt2-per12 — 16 rows total), dumps the single
chain `bfs_Dm` returns and records whether it is the all-2s loop.

**Result: 16/16 rows — bfs_Dm's returned chain IS the all-2s loop
chain, on every row, both families** (`f0_spotcheck.csv`). This
confirms the W6E spot-check (2/2 samples, SYNTHESIS.md) at full m<=9
scope, not just two rows. Per the order's own framing, this says
nothing yet about the SIZE of the full optimal set (that is F1) — it
only confirms which chain the first-parent-wins BFS happens to return.

## W6F-F1 — Optimal-set census (`shell/underlock/w6f/f1_engine_ext.py`, `f1_validate.py`, `f1_census.py`)

**Engine extension and why it was needed.** `engine.bfs_Dm`'s forward
BFS keeps exactly ONE parent per `(d,r)` state (`if key not in
new_live`), discarding all other predecessors — sufficient for
computing D(m) or extracting one representative chain, but structurally
unable to answer "how many distinct optimal chains exist." A first
attempt (tested, not shipped) tracked ALL parents forward for every
`(d,r)` state and backtracked every path: this reproduces the correct
COUNT of *residue-tagged* paths but that count is not the deliverable
(distinct exponent sequences), and it is combinatorially wrong for
that purpose — verified directly: golden m=9 returns 19683 = 3^9 raw
parent-paths, ALL carrying the identical a-sequence (all-2s), one path
per surviving starting residue. It also blew memory past several GB
and was killed by hand at m=10-11 during development (storing a
parents-list for every one of `(C+1)*3^m` states, most never used in
any backward path to the terminal).

**Fix (`f1_engine_ext.py`):** (1) forward pass reuses the SAME
boolean-array mechanics as `engine.bfs_Dm_fast` (`allowed_exponents` +
the cached `_get_permutation` trick), storing only which `(d,r)` are
live at each step (cheap, no parent lists) — `forward_live_fast`;
(2) distinct optimal a-SEQUENCES are enumerated by a backward-only,
memoized recursion from the terminal state (`distinct_optimal_a_sequences`),
computing predecessors on demand via the explicit inverse of the
forward residue map (`backward_predecessors_of_r` — solves `3r ==
r_target*2^a - 1 (mod 3^m)`; since `gcd(3,3^m)=3`, this has either 0 or
exactly 3 solutions, confirmed directly: e.g. m=4, the forward map's
image covers only 27 of 81 possible residues, i.e. it is 3-to-1 onto
its image, NOT a bijection — the naive "depth-path determines
feasibility" hypothesis was tested and refuted before adopting this:
depth-legal exponent deviations from the loop at m=5 golden were found
whose residue equation has ZERO solutions despite passing every
ceiling-bound check, so residues are NOT decoupled from the depth walk
and must be tracked exactly, as done here).

**State-space exhaustiveness argument (required by the order, not just
asserted):** the engine's state space is `(d,r)`, `d` in `[0,C]`, `r`
in `Z/3^m` — established in `engine.py`'s own docstring and validated
throughout W6E. `d` is exactly what `allowed_exponents` needs; `r mod
3^m` is exactly what the terminal constraint `r=1 mod 3^m` needs (the
m-step window is the full residue-relevant range per the trit-locality
argument, DERIVATION_NOTES sec 1). The forward transition
`(d,r,a)->(d',r')` is deterministic given the phase-fixed credit letter
and the chosen `a`. `forward_live_fast` evaluates every legal `a` from
every live `(d,r)` at every step (same calls as the validated
`bfs_Dm_fast`), so the recorded live-sets are the complete reachable
state graph; the backward recursion explores every legal predecessor
consistent with those live-sets, restricted (see bug note below) to
starts at exactly `d0=C` (ceiling-distance 0, the engine's validated
window-start convention). Nothing in `[0,C]x[0,3^m)` is skipped and
nothing outside it is relevant — this is the exhaustiveness argument.

**A bug was found and fixed during F2 development, recorded here since
it affects F1's engine (`f1_engine_ext.py`'s own module docstring has
the full account):** the first version of `distinct_optimal_a_sequences`
did not pin the step-0 depth to `d0=C`, only requiring the state to be
"live" (which `forward_live_fast`'s step-0 layer pools across ALL
starting depths, matching `bfs_Dm_fast`'s own convention). This is
harmless when querying the TRUE optimum (`terminal_d=best_d`), because
only a `d0=C` start can ever reach the global max survivor depth for a
fixed a-sequence (`d_k(d0) = d0 + sum(c-a)` is affine in `d0` with unit
slope, so a `d0<C` start can never catch up) — which is exactly what
F1 queries, and why F1's own results (below) are unaffected. It is NOT
harmless for off-optimum queries (F2's `D+1`/`D+2` buckets), where it
silently mixed in shorter-budget chains that only coincide in
a-sequence. Caught by F2's own cross-check (each returned chain's
max-partial-sum, recomputed independently from its a-sequence and
credit word, must equal `C-terminal_d` exactly) before any F2 result
was trusted. Fixed by pinning step 0 to `d==C` exactly. F1 was rerun
after the fix; identical results (as expected, since F1's queries were
never in the affected regime).

**Validation (`f1_validate.py`, house rule: >=3 ground-truth rows
before trust):** cross-checked against a THIRD, fully independent
implementation (`brute_force_all_chains` — naive scalar recursive DFS
over every starting residue explicitly, fixed `d0=C`, no cached
permutations) on BOTH families, m=3,4,5 (6 rows, 2x the family
coverage and 2x the row minimum). D matches ground truth AND the exact
SET of optimal a-sequences matches the brute force on all 6/6 rows —
**PASS**.

**F1 result (`f1_census.py`, `f1_summary.csv`, `f1_nonloop_dump.csv`):**
scope m=2..13 (extended past the required m<=9 since per-row wall time
stayed sane throughout — golden m=13 the slowest single row at 14.7-
18.4s across reruns, sqrt2 m=13 ~13-16s; total wall 48-58s for all 24
rows both families; m=14+ not attempted, a real scope wall since the
underlying state space is 3^m and cost is visibly climbing, reported
honestly rather than pushed further).

**THE LOOP IS THE UNIQUE OPTIMUM ON EVERY SINGLE ROW TESTED: 24/24
rows (m=2..13, golden-per8 AND sqrt2-per12) have exactly ONE optimal
chain, and it is the all-2s loop. Zero non-loop optima found anywhere
in scope.** `f1_nonloop_dump.csv` is empty (0 rows) — there was nothing
to dump.

**Gate verdicts vs frozen predictions:**
- (a) "loop NOT unique optimum for most rows m>=5" (55%) — **MISS**,
  decisively: 0/18 rows m>=5 have a non-unique optimum (0.0%, prediction
  needed >50%).
- (b) "IF alternatives exist, compact {1,3}-excursion" (55%) — **VACUOUS**:
  no alternatives exist anywhere in scope, so there is nothing to
  classify. Not a HIT, not a MISS.
- (c) [derived engine-integrity check] a non-loop optimum binding every
  prefix would mean the engine is wrong — **did not fire** (there are
  no non-loop optima to check in the first place). Consistent with,
  not proof of, engine correctness; F1's own 3-row-minimum validation
  above is the actual integrity evidence.

This is a materially stronger and more surprising finding than the
architect's own 55%-confidence prediction anticipated: uniqueness isn't
just "more likely than not," it is total across every row measured.

## W6F-F2 — Deviation tax table (`shell/underlock/w6f/f2_deviation_tax.py`)

Reuses `f1_engine_ext.forward_live_fast` and
`distinct_optimal_a_sequences` (post-bugfix, see W6F-F1 above)
unchanged — no new engine logic, only a different terminal-depth
argument (`best_d - delta` for `delta` in `{0,1,2}`) to the
already-validated function, exploiting the identity that a chain from
`d0=C` ending at depth `d` has max partial sum EXACTLY `C-d` (the same
identity `engine.bfs_Dm` uses for D itself). Every returned chain's own
max-partial-sum is independently recomputed from its a-sequence and the
credit word and asserted equal to `D+delta` — this is what caught the
F1-engine bug documented above.

Scope: m<=8, both families (per the order), C=12. For each chain in
the union of delta in {0,1,2}, classified deviation pattern vs the
all-2s loop (compressed excursion shapes: contiguous runs of
`(a_j - 2)` deltas) and tabulated Δ = own max-partial-sum − D.

**Result (`f2_tax_table.csv`, 50 rows; `f2_shape_histogram.csv`,
11 distinct (family,delta,shape) buckets; `f2_min_tax_a1.csv`,
14 rows):**

- delta=0 (the optimum itself): exactly 1 chain per row (the loop),
  confirming F1's uniqueness finding again at this narrower scope
  (m<=8) via an independently-triggered code path.
- delta=1: 0-2 chains per row; several rows (golden m=2,4,6,7; sqrt2
  m=3,8) have ZERO chains at delta=1 exactly — the tax spectrum has
  gaps, not a smooth +1,+2,+3... ladder.
- delta=2: 1-5 chains per row.
- Recurring excursion shapes across both families: a lone `a=4` (pure
  cost, no a=1) at delta+1 per unit; a `{1,4}` adjacent pair at
  delta=+1; a `{1,3}`-adjacent-to-`{3,4}` compound shape and a 3-step
  `(1,3,1)`-then-`(3,4)` shape at delta=+2. No shape appears at more
  than one delta value in this data.

**Frozen prediction: IF F1 shows the loop unique at D (it does — 24/24
rows), min tax of any a=1-containing chain = +1 exactly, for every row
(60%).** Evaluable on 9/14 rows (5 rows — golden m=2,4,6,7, sqrt2 m=3 —
hit a genuine scope wall: no a=1-containing chain exists at all within
the delta<=2 window, so the prediction cannot be evaluated for those
rows, which is a wall, not a miss). **Of the 9 evaluable rows, 8 have
min-tax-a1 exactly +1; ONE — sqrt2 m=8 — has min-tax-a1 = +2** (its
only a=1-containing chains are the 3-step `(1,3,1)+(3,4)` compound
shape, both appearing only at delta=2; no a=1-chain exists at delta=1
for that row). **GATE VERDICT: MISS** (prediction required "every row";
8/9 is not every row). Reported exactly as loudly as a clean hit would
have been, per house rules — sqrt2 m=8 is a genuine, small, honest
counterexample to the "+1 exactly, always" claim, not noise: the
delta=1 bucket for that row is provably empty (checked, not just
absent from the dump).

## W6F-F3 — Boundary-constant anchoring map (`shell/underlock/w6f/f3_anchoring_map.py`)

Reuses `engine.bfs_Dm_fast` unmodified — only the `anchor_steps`
argument (`phase = anchor_steps - m`) is varied. Anchoring conventions
defined explicitly (matching `w6e/e2_phase_pinning.py`'s own
start/end-anchored definitions so results compose): start-anchored =
`anchor_steps=m` (phase=0, the word's own k=0 origin); end-anchored =
`anchor_steps=53` (phase=53-m, the established 53-step house
convention the existing ground-truth tables were built under).
Candidate forms use the SAME (p,q) as each family's established law
(golden 3/8, sqrt2 7/12) — "+1 form" `floor((pm+1)/q)`, "-1 mirror"
`floor((pm-1)/q)`, offset only. (A first draft tried a `P=2q-p`
substitution in the mirror form, borrowing `e2_phase_pinning.py`'s
UNRELATED mechanical-word-construction convention; caught by
cross-checking against `e3_prefix_tightness.py`'s and
`e1_walkers.py`'s own actual `mirror` usage — both use the SAME (p,q),
offset only, e.g. the real system's `floor((22m-1)/53)` — before
trusting the result, and corrected.)

**Result (`f3_anchoring_map.csv`, 24 rows, m=2..13 both families):**

| pairing | golden | sqrt2 |
|---|---|---|
| end-anchored vs +1form | 12/12 | 12/12 |
| end-anchored vs -1mirror | 9/12 | 10/12 |
| start-anchored vs +1form | 3/12 | 2/12 |
| start-anchored vs -1mirror | 0/12 | 0/12 |

End-anchored matches the established `+1form` LAW EXACTLY on every row
(expected — this is the same convention the ground-truth tables were
built under). The `-1mirror` "hits" against end-anchored (9/12, 10/12)
are a mechanical near-coincidence, not a real pairing: `floor((pm+1)/q)`
and `floor((pm-1)/q)` differ only when `pm mod q` is `0` or `q-1`
(a boundary residue condition), so the two forms agree at most phases
regardless of which anchoring is correct — this was checked directly
(`D_start - D_end` is 1 at every row except the exact rows where the
two forms coincide: golden m=5,8,13; sqrt2 m=5,12) rather than taken at
face value from the raw match counts.

**Neither candidate form matches start-anchored cleanly (3/12, 2/12
against +1form; 0/12, 0/12 against -1mirror).** The actual pattern:
`D_start(m) = D_end(m) + 1` on every row EXCEPT the boundary-coincidence
rows just listed (where `D_start=D_end`) — i.e. start-anchoring behaves
like a roughly-constant +1 shift on top of the established end-anchored
law, not like either of the order's two literal candidate forms. This
is reported as the honest result rather than forced into either
candidate.

**GATE VERDICT vs frozen prediction ("end-anchoring pairs with -1
mirror, start-anchoring with +1 form", 65%): MISS, both families** (the
order's own verdict logic: neither pairing is clean across all 12 rows
for either family — end-anchored is clean against `+1form`, not
`-1mirror`; start-anchored is clean against neither). The real
boundary-constant story here is "end-anchored = established +1 law,
start-anchored = that same law's value shifted by a roughly-constant
+1" — a real anchoring effect, just not the specific pairing predicted.

## W6G — Break-It Round (`shell/underlock/w6g/`)

Order: `shell/underlock/W6G_BREAK_IT_ORDER.md` (Fable, explicit
break-it round — "conjectures below are GENERATED FREELY — some will
be wrong; that is the design"). All five experiments reuse `w6e/
engine.py` (`bfs_Dm`, `bfs_Dm_fast`, `allowed_exponents`, `next_
residue`) and `w6f/f1_engine_ext.py` (`compute_D_and_optimal_set`,
`forward_live_fast`, `distinct_optimal_a_sequences`) unmodified except
for one documented thin extension (G2's target-residue parameter).
Every script validates against >=3 known ground-truth rows (golden-per8
m=5,9; sqrt2-per12 m=8, D=2,3,4 respectively) before running its own
sweep — all passed on every script, every time. CPU only, no commits,
work under `shell/underlock/w6g/`.

### W6G-G1 — Exhaustive word-space attack (`w6g/g1_exhaustive_wordspace.py`)

**The universality test — the headline.** For EVERY word w in
{1,2}^m, m=2..10 (all 2^m words per m, fully exhaustive, no sampling —
2044 words total, verified count = sum(2^m, m=2..10) exactly), computed
D(w) via `f1_engine_ext.compute_D_and_optimal_set` (word read as its
own m-letter window at phase 0, i.e. `anchor_steps=m` — the only
non-arbitrary convention for a word with no "house phase" of its own;
validated separately from the periodic toy words' house-53-anchored
convention, since the two conventions pick different, non-interchangeable
windows for periodic words — caught explicitly during validation, see
script docstring) and compared to L(w) = max_k sum_{j<=k}(2-c_j) (the
trivial all-2s loop's own max partial sum against w).

**Runtime note (reported honestly):** a first attempt included an
extra "min-tax" bonus mine (cheapest a=1-containing chain's excess cost)
inline for every word at every m; timed and found to cost 3.4x overhead
(m=8: 17.8s with it vs 5.3s without), which would have made m=10 alone
take 10+ minutes — killed and re-scoped. Final run: min-tax computed
only for m<=8 (SKIPPED, not fabricated, for m=9,10 — reported in the
CSV as `"SKIPPED(m>8)"`); D, L, and n_optimal (full uniqueness census)
computed for the FULL m=2..10 scope with no reduction. Total wall
244.8s (m=10 alone: 192.1s, the dominant cost); zero scope dropped.

**RESULT: D(w) = L(w) on ALL 2044/2044 words, and n_optimal(w) = 1
(unique optimum, the all-2s loop) on ALL 2044/2044 words.** Verified
independently of the script's own printed summary by re-reading
`g1_wordspace_census.csv` directly: row counts match 2^m exactly for
every m in 2..10, zero `NO_SURVIVOR_C12` rows, zero `D<L` rows, zero
`n_optimal>1` rows. `g1_breaks_dump.csv` and `g1_ties_dump.csv` are both
empty (header only) — there was nothing to dump.

**GATE VERDICTS vs frozen predictions:**
- Universal discrepancy D(w)=L(w) for ALL words (Fable 70%): **HIT**,
  and not narrowly — 2044/2044, zero exceptions, at every m in the full
  requested range. RIGIDITY EXTENDED, decisively: the game truly has no
  content beyond word discrepancy of the all-2s loop, at least through
  m=10 exhaustively.
- Uniqueness for all words (Fable 55%, "degenerate words may create
  ties"): **HIT**, also decisively — 2044/2044 unique, zero ties found,
  extending W6F-F1's periodic-word-only uniqueness finding (24/24 rows)
  to the FULL word space at this scope.
- Bonus mine ("min-tax>=2 signature exists", Fable 60%): evaluated only
  at m<=8 per the scope cap above (m=9,10 honestly skipped, not
  sampled) — min-tax>=2 counts climb with m (2, 4, 8, 16, 24, 48, 96 at
  m=2..8) but as a roughly constant ~37-38% fraction of words at each m
  (not a rare "signature" class); no distinctive word-local shape was
  separately mined beyond this density observation — INCONCLUSIVE at
  this scope, not a clean HIT or MISS.

**Decisive table:** `g1_wordspace_census.csv` (2044 rows, columns m,
word, D, L, n_optimal, min_tax_a1, note). No counterexample dump needed
(`g1_breaks_dump.csv`, `g1_ties_dump.csv` both empty).

### W6G-G2 — Anchor sweep (`w6g/g2_anchor_sweep.py`)

**Is the loop's throne anchored to rho=1? BREAK FOUND.** Swept the
terminal anchor over all admissible residues (class 1 and 2 mod 3 only
— class 0 has no legal backward step, per `engine.
forced_parity_for_backward_step`) mod 27 and mod 81, m=2..8, golden-per8
and sqrt2-per12 words, via a thin validated extension of `engine.
bfs_Dm_fast` (`bfs_Dm_fast_target`, parameterizing the hardcoded
`target_r=1` — reuses `allowed_exponents`/`_get_permutation` verbatim,
validated to reproduce all 3 ground-truth rows exactly at `target_r=1`
before trusting any `r!=1` result). 144 distinct (family, mod_target,
r0) keys analyzed across 1008 total sweep rows (54 admissible residues
x 2 moduli x 2 families x up to 7 m-values, deduplicated where a mod-27
or mod-81 target folds onto the same residue mod the smaller working
modulus 3^m — 192 such folds logged in `g2_dedup_log.csv`, not silently
merged).

**RESULT: h(r) = D(r,m) - D(1,m) is NEGATIVE on 80/144 keys (55.6%) —
the conjectured "h(r) >= 0" is FALSE, and not by a small margin.**
Decisive counterexample (verified directly against the raw CSV, not
just the script's own summary): **sqrt2-per12, m=5, target residue
r0=20 (mod 27 and mod 81 alike) gives D(r=20, m=5) = 0, while
D(r=1, m=5) = 3 — anchoring the terminal at rho=20 is THREE LEVELS
EASIER than anchoring at the canonical rho=1, at the exact same m.**
Other golden-per8 counterexamples at m=5 reach h(r)=-2 (r0=10, r0=20).
This is not an edge-of-scope artifact: negative h(r) values appear at
m=3 through m=8 for both families (see `g2_negative_h_dump.csv`, 80
rows, full per-m breakdown per key). Additionally, even where h(r)>=0
holds, it does NOT stabilize to an m-independent constant by m=5 on
most keys (only 30/144 keys show a constant tail for m>=5 —
`g2_instability_dump.csv`, 114 rows).

**GATE VERDICT vs frozen prediction (D(r,m) = L(m) + h(r), h(r)>=0
m-independent for m>=threshold, 60%): MISS (BREAK)**, reported at full
volume per house rules — rho=1 is demonstrably NOT the hardest anchor;
several other residues are strictly EASIER to reach, and the excess
cost relative to rho=1 is neither always non-negative nor
m-independent in the measured range. The "descent cost to the 1-ray"
framing in the registered conjecture does not survive contact with the
data.

**Decisive table/counterexample dump:** `g2_negative_h_dump.csv` (80
rows, exact per-m h(r) history per violating key);
`g2_anchor_sweep.csv` (1008 rows, full raw sweep); sharpest single
number: sqrt2-per12 m=5 r0=20, h(r)=-3.

### W6G-G3 — Over-side convergent families (`w6g/g3_overside_families.py`)

**The side-constant law. MUDDLE, reported loudly per the order's own
instruction for this outcome.** Built the over-side sibling convergent
for each established (under-side) toy word: golden-per8's 13/8 (a
convergent of phi; beta_word=2-13/8=3/8, confirmed UNDER-side of
beta=2-phi via exact integer cross-multiplication, not floats) has
over-side sibling 21/13 (next continued-fraction convergent of phi;
beta_word=2-21/13=5/13, confirmed OVER-side); sqrt2-per12's 17/12
(beta_word=7/12, UNDER-side of beta=2-sqrt2) has over-side sibling
41/29 (beta_word=17/29, confirmed OVER-side). Both new words' period/
support-count receipts verified (period 13: 5 ones/8 twos; period 29:
17 ones/12 twos) before measurement, matching `underlock_words.py`'s
own receipt-discipline. Bug caught and fixed during development: an
early draft passed the OVER-side word's own slope (p,q)=(21,13) or
(41,29) directly into the +-1 candidate-form formula, instead of that
word's BETA fraction (2q-p, q) = (5,13) or (17,29) — the established
golden/sqrt2 laws use the BETA fraction (3,8) and (7,12), not the
words' own slopes (13,8)/(17,12), so using the wrong fraction would
have silently tested the wrong candidate; caught by checking against
the established law's own convention before trusting results, fixed,
and the full m=2..12 sweep re-run clean.

**RESULT: neither the +1 form nor the -1 mirror form (using the
over-side word's own correct beta fraction) matches D_over cleanly.**
Golden over-side (beta=5/13): +1 form hits 5/11, -1 form hits 4/11.
Sqrt2 over-side (beta=17/29): +1 form hits 1/11, -1 form hits 1/11.
Combined: +1 form 6/22, -1 form 5/22 — both forms fail on the large
majority of rows, and where they do hit, `+1form` and `-1form` mostly
coincide (they differ only at boundary-residue phases, same mechanism
W6F-F3 already found), so there is no clean split favoring the -1
mirror as predicted.

**GATE VERDICT vs frozen prediction (over-side obeys -1 mirror form
exclusively, under-side already measured +1, 65%): MISS/MUDDLE** — not
a clean inversion (over-side does NOT cleanly obey +1 either), just a
genuine failure of both simple offset forms to describe the over-side
laws at this m<=12 scope. Per the order's own framing: "a muddle means
7c's mechanism is wrong" — reported as such, not softened. The
over-side D-values do NOT reduce to a simple same-(p,q)-offset-only
law the way the under-side toys do; whatever governs the over-side
constant is more structured than a fixed +-1 shift.

**Decisive table:** `g3_overside_families.csv` (22 rows, columns
family, m, D_over, D_under, p_over, q_over, plus1_form, minus1_form,
plus1_hit, minus1_hit).

### W6G-G4 — True-word round (`w6g/g4_true_word_round.py`)

**(i) Uniqueness: RIGIDITY EXTENDED, clean HIT.** Optimal-set census
(`f1_engine_ext.compute_D_and_optimal_set`, unmodified) on the REAL
system's true credit word (embedding/automaton.py's own `credit`,
exact via bit_length), end-anchored at the real house convention
(`anchor_steps=53`, matching `e1_walkers.py`'s own bonus-census
convention and `e2_phase_pinning.py`'s "end-anchored" definition),
m=2..12: **n_optimal=1 (the all-2s loop) on ALL 11/11 rows** —
verified against the established D_real mirror law
(`floor((22m-1)/53)`) at m=5,8,12 before trusting, all 3/3 PASS.
`g4_nonunique_dump.csv` is empty. **GATE: HIT** vs the 75%-confidence
prediction, and decisively (11/11, not a partial majority) — the
aperiodic true word shows the SAME total rigidity W6F-F1 found on the
periodic toy words.

**(ii) Bonus schedule: HIT on the raw numbers, but flagged with an
honest methodological caveat.** D_true(m) matches BOTH the +1 form and
the established -1 mirror form (same (p,q)=(22,53)) on 10/11 rows
(m=2..11; they coincide at every one of these rows), diverging only at
m=12 where D_true=4 matches ONLY the established -1 mirror
(plus1_form=5, minus1_form=4) — consistent with the established law,
not a new finding. Alignment check (does the "bonus" row's window carry
a correction letter — a position where the true word differs from the
22/53-periodic word — at the window's end?): 10/11 raw "aligned" by the
literal test, but **this test is reported as NEAR-VACUOUS at this
scope**: measured directly, the true word and 22/53-periodic word
differ at 30-70% of ALL positions in every m<=12 window (2/2 up to
8/12), not the "single rare correction letter" regime the m=359-scale
prediction was built on (where DERIVATION_NOTES/SYNTHESIS report only
1 of 359 positions differing) — so "a correction letter present at the
window end" is true on 11/11 rows regardless of bonus class, making it
a non-discriminating base rate rather than a genuine alignment signal.
**GATE (ii): PARTIAL on the literal count (10/11), but the "aligned"
framing itself does not transfer to this scope** — reported honestly
per house rules rather than claimed as a clean confirmation.

**Decisive tables:** `g4_true_word_uniqueness.csv` (11 rows),
`g4_bonus_schedule.csv` (11 rows), `g4_correction_letters.csv` (11
rows, showing the 30-70%-differing-positions caveat directly),
`g4_alignment_check.csv` (11 rows).

### W6G-G5 — Reality bridge (`w6g/g5_reality_bridge.py`)

**Game vs the actual corridor. RIGIDITY EXTENDED on the rows fully
evaluated (4/4, C=1..4); one genuine scope wall (C=5) honestly
reported, not papered over.** Archive search (per the order): `certs/`
holds only float-`rho`-continuum sweep data (a different, unrelated
investigation — not usable here); `shell/` holds no archived witness
RESIDUE data either. Found instead: `embedding/small_side_live_sets/
*.npz` — genuine archived witness data (final live-residue-index sets,
NOT boolean masks, keyed by deficit) for C=1..5 at their own M_edge(C)
and M_edge(C)+1. **Part A (direct archive inspection, independent of
shell_probe.py's own code path):** (d=0, r=1 mod 3^m) confirmed as
THE witness at all 5/5 archived edges (C=1..5), and confirmed ABSENT
one step past each edge (5/5) — reproducing P3's own claim via a
completely separate read of the raw archive files.

**Part B (regenerated, since the archive lacks per-step history — cheap
for C=1..4, a genuine wall at C=5):** extracted ONE explicit optimal
backward chain via `engine.bfs_Dm(want_chain=True)` on the REAL true
word (not a toy) at each C's own M_edge(C): **C=1 (m=4), C=2 (m=7),
C=3 (m=9), C=4 (m=12) all give the all-2s loop EXACTLY as the extracted
a-sequence — 4/4 — meaning the actual corridor's deepest survivor rides
rho=1 at EVERY intermediate step, not just the terminal.** C=5 (m=14):
`bfs_Dm`'s scalar dict-based chain extraction starts (C+1)*3^m =
6*4,782,969 ~= 28.7M live states; a first attempt ran >3 CPU-minutes
with RSS climbing past 8GB and still rising (~1.6GB/min, not crashed,
not finished) — killed and honestly scoped out rather than let run
indefinitely, per house discipline. C=5's D-VALUE ALONE was cheaply
cross-checked via the vectorized `bfs_Dm_fast` (D=5, consistent with
Part A's witness finding) but its full chain/trajectory question is
UNRESOLVED, not claimed.

**GATE VERDICT vs frozen prediction (abstract game's extremal object =
real corridor's extremal object, 65%): HIT on all rows where the
question could be fully evaluated (Part A: 5/5; Part B: 4/4 C=1..4)**,
with C=5's full-trajectory question left explicitly OPEN (scope wall,
not silently resolved either way). No mismatch found anywhere in scope
— this is the strongest possible confirmation available within the
CPU/memory budget, reported with its actual boundary intact rather than
extrapolated past it.

**Decisive table:** `g5_true_word_chains.csv` (5 rows: C, m_edge, D,
is_all_2s_loop, a_sequence — 4 rows fully evaluated True/True, 1 row
explicitly marked SKIPPED).

## W6H — The Lemma's Local Core (`shell/underlock/w6h/`)

Order: `shell/underlock/W6H_LEMMA_CORE_ORDER.md`. All five experiments
reuse `w6e/engine.py` and `w6f/f1_engine_ext.py`'s validated primitives
(`forced_parity_for_backward_step`, `backward_predecessor_exact`,
`allowed_exponents`, `next_residue`, `forward_live_fast`,
`backward_predecessors_of_r`, `compute_D_and_optimal_set`,
`bfs_Dm`/`bfs_Dm_fast`) — no changes to any of them. CPU only, no
commits, work under `shell/underlock/w6h/`. Executed in the order's
stated order: H1, H3, H2, H4, H5.

### W6H-H1 — Excursion cost spectrum (`w6h/h1_excursion_spectrum.py`)

**THE LEMMA'S ENGINE ROOM. LEMMA SUPPORTED (P1 HIT), but P2 is a
dramatic MISS in the SAFE direction — the true minimum cost is far
above +1, not equal to it.**

Two false starts, reported per house rules rather than silently fixed:
(1) a uniform per-step exponent window (`a_min, a_min+2, ..., a_min+2K`)
applied at every depth blew up combinatorially (K=8: 16s/hundreds of
thousands of dead branches; K=12 killed by hand after minutes, RSS
past 8GB); (2) a Dijkstra search over states `(rho, depth)` was tried
next and produced a WRONG answer (cost 28 instead of the true 27 at
length 8) — root-caused directly: excursion edges can have NEGATIVE
weight (a=1 costs -1), and Dijkstra's greedy "pop = final, never
revisit" is unsound with negative edges; traced to an exact heapq
tie-break collision between two cost-28 states that blocked a cheaper
successor from ever being pushed. **Fixed with a layered DP** (depth
strictly increases every step, so the state graph is a DAG — forward
dynamic programming taking the min over ALL incoming edges per layer
is exact regardless of edge sign, no greedy step anywhere).

**Exhaustiveness proof (not just asserted):** at `COST_CAP=150`
(working precision `mod=3^10=59049`), the live-state count SATURATES
AT EXACTLY the full modulus (59049/59049) at every depth 5-8 — a hard
proof that no larger cap could ever find a cheaper path at those
depths, since every reachable residue is already accounted for.
Separately, length-1 excursions are proven (not searched) to NEVER
return: a full-period exhaustive sweep (no cap at all) finds exactly
19682 reachable residues excluding the trivial a=2 fixed point, and
rho=1 is proven absent.

**Result (`h1_length_spectrum.csv`):** minimum COST by first-return
length: length 3→109, 4→95, 5→60, 6→33, 7→29, **8→27** (global
minimum across length<=8). Verbatim decisive shape (triple-checked:
engine + independent from-scratch reimplementation both confirm):
**a-sequence (4,3,8,3,9,8,7,1), length 8, COST=27**, trace
`[2,3,9,10,17,23,28,27]` (all non-negative, cost 27 at the end).
Lengths 1-2 have NO return within any economically relevant cost (a
length-2 return does exist somewhere in the far tail, cost ~36,915 —
found and confirmed, but irrelevant to any of the three predictions).

**BREAK CHECK: 0 returning excursions found with COST <= 0** — no
break. **Non-returning-prefix check: 0 dips below 0** in any of the
6 min-cost sequences' own running-cost traces.

**GATE VERDICTS vs frozen predictions:**
- P1 (every returning excursion COST >= +1, 75%): **HIT**, and not
  narrowly — the minimum found (27) is nowhere near the +1 floor.
- P2 (minimum COST == +1 exactly, 65%): **MISS** — minimum is 27
  (length 8), not 1. This is a genuinely surprising result: the
  registered prediction anticipated a tight, nearly-breakable bound;
  the data shows the loop's local rigidity has enormous slack, not a
  hairline margin. Shortest returning excursion is length 6 (cost 33),
  not the "shortest returning shape" near cost 1 the prediction
  anticipated.
- P3 (non-returning prefixes running cost >= 0, 55%): **HIT**.

**Decisive table:** `h1_length_spectrum.csv` (8 rows). No BREAK dump
needed (`h1_breaks_dump.csv` empty). Honest wall: exhaustiveness is
proven via state-count saturation at depths >=5 (hard proof); depths
1-2 are proven via a full-period sweep (hard proof, no return exists
at ANY cost for length 1); depths 3-4 rest on the COST_CAP=150 margin
check (min values stable across cap=120/150/200, comfortably far from
the cap) rather than full saturation, since their state spaces are
intrinsically smaller and didn't reach 3^10 states within the tested
cap — reported as a slightly softer (but still checked, not asserted)
guarantee than depths 5-8's hard saturation proof.

### W6H-H3 — Alphabet extension (`w6h/h3_alphabet_extension.py`)

**BREAK — universality's scope fence is real and sharp.** Extended
G1's exhaustive word-space census ({1,2}^m, 2044/2044 clean) to
{0,1,2}, {1,2,3}, {0,1,2,3} at m=2..7 (full scope completed for all
three alphabets, no wholesale drops needed — {0,1,2,3} at m=7 alone
took 531s, the dominant cost, total wall 594s for that alphabet;
C=18, sized against the all-0s word's own worst-case D=L=2m=14 at
m=7, verified before trusting the sweep).

**Result (`h3_wordspace_census.csv`, 28,392 rows; `h3_breaks_dump.csv`,
12,918 rows; `h3_ties_dump.csv`, 845 rows):**
- **{0,1,2} (3,276 words): 0 D!=L exceptions, 0 uniqueness ties —
  universality extends CLEANLY** to the alphabet containing c=0 but
  not c=3.
- **{1,2,3} (3,276 words): 1,788 D!=L exceptions (54.6%!), 310
  uniqueness ties — BREAKS badly, despite containing ZERO c=0
  letters.** This directly REFUTES the order's own mechanistic
  expectation ("exceptions... expect them, if anywhere, at words with
  c=0 letters adjacent to high-credit letters") — c=0 is not required
  at all; c=3 alone is sufficient and the c0-adjacent-high flag is
  0/1788 (0.0%) among these breaks by construction (no c=0 present).
- **{0,1,2,3} (21,840 words): 11,130 D!=L exceptions, 535 ties.**
  74.1% of these breaks (8,246/11,130) DO involve a c=0 letter
  adjacent to a high-credit (c>=2) letter, but this is a co-occurrence
  statistic, not the causal mechanism (see below) — most words in this
  alphabet contain BOTH c=0 and c=3 letters, and c=3 alone already
  breaks things in the {1,2,3} data above.

**Mechanism (root-caused, not just observed):** the order's own
`L(w) = max_k Sum(2-c_j)` is the WORST INTERMEDIATE DIP of the all-2s
loop's depth trajectory. For the {1,2} alphabet, `2-c_j` is always
>= 0, so the running sum is monotone non-decreasing and its max
EQUALS its final value -- this identity (not a coincidence) is WHY
D(w)=L(w) held universally there. Once c=3 is legal, `2-c_j` can be
NEGATIVE (2-3=-1), so the running sum is no longer monotone: the
worst dip and the final value decouple, and the all-2s chain can
transiently need MORE budget than it ends up needing (or can profit
past its own starting point) in ways `L`'s single max-of-running-sum
formula does not capture. Verified directly on two minimal
counterexamples: word (1,3) at m=2 has D=0 but L=1 (the all-2s chain
IS still optimal here, `L` is just measuring the wrong quantity);
word (3,1) at m=2 has D=1, L=0, and the all-2s chain is NOT even in
the optimal set anymore (`seqs=frozenset()`) -- a genuine, not just
cosmetic, break.

**GATE VERDICT vs frozen prediction (D(w)=L(w) and unique loop for
ALL words over ALL tested alphabets, 65%): MISS**, decisively for two
of the three alphabets, with the mechanism identified precisely (any
c>=3 letter, not c=0-adjacency) rather than left as a mystery.

**Decisive tables:** `h3_wordspace_census.csv`, `h3_breaks_dump.csv`,
`h3_ties_dump.csv`.

### W6H-H2 — Two-ray decomposition of the anchor sweep (`w6h/h2_two_ray_model.py`)

**MUDDLE on the main model (Gate 1 MISS), clean HIT on Gate 2.**

Engine note: chain extraction via the scalar `bfs_Dm`-style dict
approach (as used for the target-chain extension) timed at 25.6s for
a SINGLE m=9 anchor -- far too slow for the required mod-81/m-to-10
sweep (dozens of targets x 2 families x 9 m-values). Replaced with a
fast path reusing `f1_engine_ext.forward_live_fast` (cached per
family/m, vectorized) + a single-chain backward extractor built on
the SAME validated `backward_predecessors_of_r` modular-inverse
construction `distinct_optimal_a_sequences` already uses -- verified
identical D(r,m) values against both the slow scalar version and 20
sampled rows from G2's own already-computed `g2_anchor_sweep.csv`
(20/20 exact match) before trusting it. Full mod-27/81 sweep, m=2..10,
both families: 1.2s total (vs an extrapolated tens-of-minutes for the
scalar path).

**Gate 1 result (`h2_two_ray_fit.csv`, 1,104 rows; 192 evaluable keys
after extending to m=10): 58/192 (30.2%) exact matches -- MISS**
against the 90% threshold. Of the 58 matches, 36 are TRIVIAL (the
swept target r IS one of the two ray points itself, D(r,m) reduces to
the ray's own law tautologically); only 22 are genuine non-trivial
hits. **Mechanism (root-caused via a concrete counterexample, not left
as a mystery):** the model as specified assumes that once a chain
touches a ray it STAYS there for the rest of the window (riding the
ray's own trivial per-step cost for the remaining suffix) -- but
reaching an ARBITRARY target residue r often requires the chain to
LEAVE the ray again near the end to land exactly on r. Verified
directly: golden-per8 m=3, target=7 has actual D=3 with optimal chain
(1,2),(2,2),(2,4) -- riding rho=1 for the first two steps, then
EXITING (a=4, cost +2) on the final step to hit the target -- the
model's "ray-discrepancy(remaining suffix)" formula (`Sum(2-c_j)`,
which implicitly assumes a=2 forever) predicts 1, not 3, because it
has no term for the mandatory final exit cost. This is a genuine gap
in the model's own stated form, not an implementation bug (the
extraction was cross-validated against G2's own numbers first).

**Gate 2 result (`h2_gate2_pure_cheap_ray.csv`, 18 rows, both families
x m=2..10): 18/18 have D(r=3^m-1)=0 exactly -- clean HIT.** The pure
cheap ray (target = the -1-ray's own canonical representative mod
3^m) is reached at zero cost for every tested m and family whose
minimum credit letter is >=1, exactly as predicted.

**GATE VERDICTS vs frozen predictions:**
- Two-ray model >=90% exact match (55%): **MISS** (30.2%), with the
  residual pattern identified precisely: the model needs an explicit
  "final approach/exit cost to the specific target" term, not just
  descent-then-ride.
- D(r=3^m-1)=0 for every word with min letter>=1 (80%): **HIT**, 18/18.

**Decisive tables:** `h2_two_ray_fit.csv` (1,104 rows), `h2_mismatches_
dump.csv` (134 rows, verbatim), `h2_gate2_pure_cheap_ray.csv` (18 rows).

### W6H-H4 — P1b by data-mining (`w6h/h4_p1b_datamining.py`)

**MISS, mechanism-rich muddle -- the phase/side selector is NOT the
clean two-case function the prediction anticipated; a first-draft bug
(caught and fixed, same bug class as W6G-G3) is recorded honestly.**

Convergents (q<=60) computed to 100-digit precision (Python Decimal)
for log2(3) [7 convergents], sqrt(2) [5], sqrt(3) [8], golden [10],
and 10 reproducible random irrationals (sqrt(n/d), seed=42, listed
verbatim in the run log) -- 141,287 total (target,p,q,side,phase,m)
rows across m=2..4q, phase=0..q-1, both CF-alternating sides.

**Two bugs caught and fixed in sequence, both reported (house rule):**
(1) first draft used the word's own slope `p` directly in the +-1
candidate forms instead of its BETA fraction `P=2q-p` -- the EXACT
same bug class W6G-G3's own ledger entry already documents once;
caught immediately because raw L values came out systematically far
smaller than `(p*m+-1)/q` predicted at literally every row (not
organic noise). (2) After fixing (1), still found near-universal
"NEITHER" rows; traced to a phase-anchoring bug: `anchor_steps = m +
phase` makes `(anchor_steps mod q)` DRIFT with m instead of staying
fixed at `phase` -- the window's end-residue mod q was not actually
constant across the m-sweep for a nominally fixed "phase" bucket.
Fixed by setting `anchor_steps = phase` directly (the mechanical word
is exactly periodic for negative k too, verified directly, so this
correctly pins the window end's residue mod q for every m). Cross-
checked post-fix: `anchor_steps=53%8=5` and `anchor_steps=53` give
IDENTICAL L values at every m for golden-per8 -- confirms the fix.

**Result after both fixes (`h4_convergent_word_census.csv`, 141,287
rows):** of 1,053 (target,p,q,side,phase) keys, only **55 are
internally clean** (single form, no NEITHER, across the full m=2..4q
scope) -- all 55 are "+1"-form matches, and NONE of the other 998
keys are clean. The clean phases are NOT a simple function of
`53 mod q` or any other single arithmetic rule checked -- they appear
to be convergent-specific (each (p,q) pair has its own "house" phase,
plausibly tied to the CF's own worst-peak/Raney-cycle-lemma phase per
DERIVATION_NOTES sec 3, not investigated further here). At non-clean
phases, the discrepancy pattern is itself structured (e.g. golden
p=13,q=8,phase=0: NEITHER rows have `L = plus1_form + 1` exactly,
matching only at Fibonacci-spaced m) rather than random noise --
flagged as a concrete, dump-verified pattern for a future session,
not chased to a final rule here.

**GATE VERDICT vs frozen prediction (clean two-case function of side
and phase mod q alone, 70%): MISS** -- only 55/1,053 keys (5.2%) are
even internally clean, let alone matching a shared cross-convergent
rule; the (side,phase) consistency check found 0 shared buckets with
enough clean-key overlap to test cross-convergent generality at all
(every clean key's own (side,phase) turned out to be convergent-
specific in this run, so the "0 inconsistent buckets" figure is
vacuous, not a hidden HIT -- reported plainly rather than spun).

**Decisive tables:** `h4_convergent_word_census.csv` (141,287 rows),
`h4_neither_dump.csv` (943 keys), `h4_dirty_keys_dump.csv` (998 keys).

### W6H-H5 — Frame rule cross-check (`w6h/h5_frame_rule_crosscheck.py`)

**SUPPORTED, clean and decisive HIT.**

Archive search (per the order, false starts reported): `data/runs/
macro_corridors_*.csv`, `corridor_bound_*.csv`, `k53_capacity_*.csv`,
`gap_kill_*.csv` were found first but belong to a DIFFERENT
investigation (real D=23-bit-length orbit corridors and martingale
bounds on six specific large integers -- different "C"/"D" meaning
entirely, not usable). `renorm_check/certs/` is the same unrelated
float-rho-continuum data W6G-G5 already flagged. **Found and used:**
`data/runs/lock3_C{C}_N2000_residue_m1_lineage_cohorts_*/lock3_census_
C{C}.csv` -- the SAME `lock3_census` tool the ledger's own W1 section
already validated (`max_lifetime_of_valid1_lineage = M_edge(C)`), run
densely at C=1..50, never individually spot-checked against the frame
rule before (only C<=5 and C=148 were, per SYNTHESIS.md's own caveat).
Cross-validated each archived C's CSV-derived M_edge(C) against the
run's own summary JSON field before trusting it (0 mismatches, all 48
usable).

**Result (`h5_frame_rule_check.csv`, 48 rows, C=3..50): M_edge(C) ==
floor(53*(C+1)/22) EXACTLY at all 48/48 archived mid-range C values**
-- the SAME rational "Architect's formula" SYNTHESIS.md's shadow-depth
sweep validates at C=148,170,...,275. Boundary crossings (the
sharpest test, where the predicted run actually changes value) both
confirm cleanly: C=21 (run jumps 53->106, M_edge=53=m_irr exactly) and
C=43 (run jumps 106->159, M_edge=106=m_irr exactly).

**GATE VERDICT vs frozen prediction (holds at all found C, 70%): HIT**,
decisively -- 48/48, spanning both 53-multiple boundary crossings in
the tested range, with zero counterexamples.

**Decisive table:** `h5_frame_rule_check.csv` (48 rows).

## W6H Final Digest

| Exp | Verdict | Prediction(s) HIT/MISS | Decisive artifact |
|---|---|---|---|
| H1 | LEMMA SUPPORTED (no break; local bound far looser than expected) | P1 HIT, P2 MISS (min cost 27, not 1), P3 HIT | `h1_length_spectrum.csv`, shape (4,3,8,3,9,8,7,1) cost 27 |
| H3 | BREAK outside {0,1,2}; universality's scope fence found and mechanism identified (any c>=3 letter, not c=0-adjacency) | MISS for {1,2,3} and {0,1,2,3}; HIT for {0,1,2} | `h3_breaks_dump.csv` (12,918 rows) |
| H2 | MUDDLE on the two-ray model (missing exit-cost term); clean SUPPORTED on the pure-cheap-ray gate | Gate1 MISS (30.2%<90%), Gate2 HIT (18/18) | `h2_two_ray_fit.csv`, `h2_mismatches_dump.csv` |
| H4 | MUDDLE — selector is real but convergent-specific, not a clean cross-convergent 2-case rule; two bugs caught+fixed en route (documented) | MISS (55/1053 clean, 5.2%) | `h4_convergent_word_census.csv` |
| H5 | SUPPORTED, clean | HIT (48/48 archived mid-range C) | `h5_frame_rule_check.csv` |

No BREAK of the H1 core lemma was found (COST>=1 holds everywhere
tested, exhaustively/hard-proven at every length 1-8). The three
"muddle" outcomes (H2, H3, H4) each have an identified, verified
mechanism rather than being left as unexplained noise: H3's c>=3
non-monotonicity, H2's missing final-exit-cost term, H4's convergent-
specific (not universal) clean phase. H5 cleanly extends F5's frame
rule to 48 fresh archived C values. No commits made; all work under
`shell/underlock/w6h/`; no edits to SYNTHESIS.md, DERIVATION_NOTES.md,
or any order file.

### W6I-I1 — Potential-function fitting (`w6i/i1_potential_fit.py`)

**Machinery validated first:** `backward_predecessor_mod` (the mod-3^k
3-lift backward residue map, reimplemented locally per the copy-don't-
edit rule) cross-checked against `w6e/engine.backward_predecessor_exact`
(genuine unbounded-integer arithmetic) on 10 explicit steps of a chain
from rho=1 — 10/10 PASS.

**FINDING (more fundamental than the registered prediction): no Phi>=0
with Phi(1-ray)=0 exists on this state graph — a structural non-
existence, not merely a lift-consistency failure.** Built the full
one-step cost graph on (delta, rho mod 3^k), delta<=8, k=4..7, edge
cost=a-2, uncapped backward exponent menu (sensitivity-checked stable
against a much larger cap, 0/2187 states differ at k=5). Bellman-Ford
from the ray (Phi(s) = min cost to reach the ray) converges cleanly (no
negative cycle at any k, 11-12 iterations) but yields Phi(delta,1) =
delta - 8 for delta<8 (i.e. NEGATIVE, not 0) at every k tested —
`ray_phi_all_zero=False`, `phi_nonneg_holds=False`, `loop_equality_ok=
False` uniformly across k=4..7. Mechanism, traced and confirmed: at
fixed k, the mod-3 class alone (which determines forced parity) cannot
distinguish the TRUE ray rho=1 from other residues rho' == 1 (mod 3)
but rho' != 1 (mod 3^k) — a cost-0 (a=2) edge from a ray state (delta,1)
legitimately lands on such an rho' (e.g. k=4: rho=28 is class-1 but
28 != 1 mod 81), and those states are cheaper to reach the BFS
"terminal" from, back-propagating negative values onto the ray itself.
This is precisely the sec 5a lift-cascade phenomenon, but it breaks the
potential-function program at a MORE BASIC level than the registered
prediction anticipated (that prediction assumed a finite Phi>=0 exists
at each fixed k and only asked about lift-consistency across k;
instead, Phi>=0 itself fails to exist, at every k, for the same
underlying reason).

**Bonus (max-Phi / "deepest hole"): STABLE, not growing — but this
finding is now subsumed by the non-existence result above** (max_phi=0
identically at k=4..7, min_phi=-8=-delta_max identically; the "depth"
never grows past the delta_max=8 cap because that cap, not k, sets the
scale here).

**Ironic technical footnote: the k -> k+1 PROJECTION check that the
prediction anchored on (part iii) is trivially, vacuously satisfied**
(0 multi-valued states, 0 mismatches across all three (k,k+1) pairs
tested) — but this is a red herring given (i)/(ii) fail outright; a
projection of an ill-posed Phi being self-consistent does not rescue
the program.

**GATE VERDICT vs registered predictions:**
- "Finite Phi exists at each k but fails lift-consistency" (60%): PARTIAL
  MISS — Phi is finite (as required, no negative cycle) but is NOT >=0
  with Phi(ray)=0, which is a stronger and earlier failure than
  "lift-consistency" addresses; the literal lift-consistency check
  itself came back TRUE (misleadingly), so the registered framing
  doesn't cleanly apply.
- "If lift-consistent, one-page dual proof, report Phi table and stop
  early": the literal lift-consistency numbers say yes, but the
  headline non-existence finding means this branch is a false
  positive, not a real early-stop condition — reported, not acted on.
- "Max-Phi grows with k" (55%): MISS — stable at 0/-8 across k=4..7 (but
  see caveat above: the deepest hole is set by delta_max, not k, here).

**PROOF-SHAPE VERDICT: DUAL-PROOF NOT VIABLE**, and for a more
fundamental reason (Phi>=0 does not exist as specified, not merely
"exists but doesn't project") than the round anticipated.

**Decisive tables:** `w6i/i1_phi_summary.csv` (4 rows, k=4..7),
`w6i/i1_lift_consistency.csv` (3 rows).

---

### W6I-I2 — Ostrowski re-coordinates for the follower-set test (`w6i/i2_ostrowski_follower.py`)

**Machinery validated first:** Ostrowski digit reconstruction
(greedy expansion w.r.t. CF convergent denominators of alpha=log2(3))
hand-checked on 10 explicit n (0,1,2,3,5,12,13,41,53,100) — exact
reconstruction + admissibility bound (d_i <= a_{i+1}) — 10/10 PASS.
**Bug caught and fixed during development:** an early draft seeded the
convergent-denominator recurrence with the NUMERATOR convention
(1,0) instead of the DENOMINATOR convention (0,1), silently computing
the p-sequence (1,2,3,8,19,...) instead of q (1,1,2,5,12,41,53,...) —
caught by cross-checking against SYNTHESIS.md's own stated 22/53
convergent and beatty/continued_fraction_analysis.py's verified
convergents(), fixed before any measurement was trusted.

**FINDING: follower sets FAIL to stabilize in Ostrowski coordinates
either.** Retried the h3->h4-type stabilization test (raw trit-space
version FAILED unambiguously per e1_stabilization.py/ledger) reindexed
via Ostrowski-block horizons (jumps of size q_1=1, q_2=2 trits, the
reachable range within the M_DENSE_MAX=13 ceiling this repo's dense-
enumeration guard allows) instead of unit-trit steps. Same (delta,
rho mod 3^m) automaton, same real Sturmian credit word, same C=12,
delta in {0,1,2}, m0 in {8,9,10} as the raw test, for direct
comparability. Type counts at j1 (levels {m0+1}) vs j2 (levels
{m0+1,m0+2}): grows by roughly 10-13x at every one of the 9 (delta,m0)
points (e.g. delta=2,m0=9: 7->78), qualitatively the SAME failure mode
as raw trit-space's roughly-2x-per-horizon growth (e.g. delta=2,m0=9:
492->1282) — no stabilization signal recovered by the coordinate
change, at this (necessarily narrow, 2-horizon) scope.

**Honest wall:** the order's full scope (m<=13, matching e1_stabilization
.py's own dense-enumeration ceiling) only permits testing 2 Ostrowski
horizons (jump sizes q_1=1, q_2=2) at m0=8,9,10 before hitting the
level-13 ceiling — an initial attempt at M_DENSE_MAX=15 (3 horizons,
jumps 1,2,5) TIMED OUT at 300s wall-clock (RSS stayed safe at ~3GB;
this was a compute-time wall from the naive per-(d,a) Python forward
pass at m=15's 9x-larger state count, not a memory wall) and was
descoped back to M_DENSE_MAX=13 to stay tractable — reported as a
genuine scope constraint, not a silent reduction.

**GATE VERDICT vs registered prediction (follower sets ALSO fail to
stabilize in Ostrowski coordinates, 55% — "the prediction I most want
to lose"): HIT.** Ostrowski re-coordinatization does not rescue the
sofic/transducer route at the tested scope; S-adic viability remains
unconfirmed here (though the 2-horizon scope is admittedly thin
evidence next to the raw test's fuller 2-5 horizon sweep).

**PROOF-SHAPE VERDICT: S-ADIC NOT VIABLE** (at this scope; genuinely
narrower evidence than I'd like, flagged honestly).

**Decisive table:** `w6i/i2_ostrowski_follower_counts.csv` (9 rows).

---

### W6I-I3 — Convergent-locking harness (`w6i/i3_convergent_locking.py`)

**Machinery validated first:** 4 exact-arithmetic strategies (quadratic-
surd isqrt, integer cube-root binary search, log2(3) bit_length exact
method cross-checked against a certified-precision mpmath method, and
a Liouville-ish alpha's exact Fraction-convergent method cross-checked
against a much-higher-index reference convergent) — 14 hand-checked
(alpha, k) cases, 14/14 PASS, including k=300 boundary cases for every
family. **Modeling correction caught before trusting results:** an
early draft computed CF/convergents of alpha itself and used a fixed
ceiling=2 in the L(w)=max sum(2-c_j) discrepancy functional; this is
WRONG for alpha not in (1,2) (sqrt5~2.236 and sqrt7~2.646 have credit
alphabet {2,3}, not {1,2}) and, more importantly, the CORRECT
convergents to test locking against are convergents of beta=ceiling-
alpha, NOT of alpha itself (verified CF(sqrt5)=[2,4,4,...] vs
CF(3-sqrt5)=[0,1,3,4,...] are genuinely different) — both fixed before
trusting any match-rate number (the alpha-CF/ceiling=2 draft gave
near-zero matches, 0-6/299, across the board; the beta-CF/per-family-
ceiling fix raised this to 8-191/299, a large, non-cosmetic effect).

**FINDING: the lock-until-next-denominator rule is a clear MISS.**
For 10 irrationals (log2(3), sqrt2, sqrt3, sqrt5, sqrt7, phi, cbrt(2),
pi-3, e-2, a Liouville-ish alpha with a designed CF entry of 10^6),
computed L(m) of the true word exactly (no floats near any floor) for
m=2..300 and matched against each family's leading beta-convergents'
closed-form laws (+1 form ceil(beta*m-1) and -1 form floor((p*m-1)/q)).
Only **24/550 transfer points** (schedule-segment boundaries, summed
across all 10 families) land within +-1 of a tabulated convergent
denominator — roughly 4%, nowhere near the 70%-confidence prediction.
Per-family match rates against ANY tabulated convergent's law at all
range from 3% (pi-3) to 64% (sqrt3); most families show NOT a clean
"convergent A owns m=[a,b], then convergent B takes over and stays"
handoff but a FRAGMENTED, oscillating pattern — the same low-q
convergent (e.g. phi's 1/2) recurring intermittently across widely
separated, non-contiguous m even after "newer" convergents have
started appearing, rather than being cleanly retired. The Liouville-
ish alpha's huge injected CF term (a_7=10^6, convergent denominator
~1.3e7) never becomes relevant within m<=300 (as expected — that
convergent's denominator dwarfs the tested range) so the "one
convergent owns a huge range" stress test is UNTESTED at this m-scope,
not confirmed or refuted; within reach, its locking behavior looks
like the other small-CF-entry families (fragmented, low-q).

**GATE VERDICT vs registered prediction (lock transfers at exactly
next convergent's denominator, refined by +-1 boundary cases, 70%):
MISS**, clearly and by a wide margin (4% hit rate on transfer points),
across every family, not just the Liouville stress case (which is
inconclusive, not a counterexample, at this m-range).

**PROOF-SHAPE VERDICT: RULE MUDDLED — the simple lock-until-denominator
picture does not describe the data; the true locking structure (to the
extent one exists) is more fragmented than a clean handoff schedule.**

**Decisive tables:** `w6i/i3_locking_summary.csv` (10 rows),
`w6i/i3_locking_<family>.csv` (299 rows each, 10 families).

---

### W6I-I4 — Lift-cascade effective branching (`w6i/i4_lift_cascade.py`, exploratory, UNGATED)

**Machinery validated first:** the "3 same-parity menu offsets give 3
distinct mod-3 successor classes, offset+6 repeats offset+0's class"
claim (DERIVATION_NOTES sec 1's mod-9 steering) hand-checked on 5
explicit steps from rho=1 — 5/5 PASS.

**Result: 19/20 tested single-step lift perturbations (offset+2 vs the
S0-greedy baseline) are "decisive" within the 20-step window, ALL at
delay=1 (the very next step).** Traced, for each backward step j=0..19
from rho==1 (mod 3^8), whether a minimal alternative lift (a_min+2
instead of a_min) at step j — followed by greedy S0 continuation —
changes the forced-parity sequence at some later step, and if so, how
many steps later.

**Honest scope caveat (flagged, not silently reported as a stronger
finding): this near-universal delay=1 is close to a TAUTOLOGY here,
not evidence about sec 5a's actual cascade claim.** The baseline chain
from rho=1 is the trivial all-2s fixed-point loop (never leaves the
ray), so perturbing step j's exponent immediately produces a
generically different residue integer, which generically differs mod
3 (hence forced parity) at the very next step too — this measures "does
perturbing the residue at all change the immediately-following mod-3
class" (near-tautologically yes on a degenerate baseline), NOT sec 5a's
actual claim, which concerns a SPECIFIC high trit (written at step j,
trit m-j-1) taking ~(m-j) further steps before it becomes the low-order
trit governing forced parity. Testing that claim properly needs a
non-degenerate baseline (one that actually visits multiple residue
classes) and tracking one specific trit's delayed influence, not
perturbed-vs-baseline forced-parity divergence on a fixed point.
Reported honestly as a narrower measurement than the order's framing
suggested going in, not reframed as confirming or refuting sec 5a.

**Deliverable (per the order, ungated, no verdict required):**
histogram = {delay=1: 19 occurrences, no-divergence-in-window: 1 (the
final step j=19, which has no room left in the 20-step window to
observe any later step — not a substantive finding)}. Effective
branching at this (degenerate) baseline and offset: 19/20 "decisive,"
1/20 untestable.

**Decisive tables:** `w6i/i4_influence_delays.csv` (20 rows),
`w6i/i4_delay_histogram.csv`.

## W6J — Interior/Boundary Decomposition (work order, Fable, 2026-07-04)

Executor: Sonnet agent. House rules as W6E..W6I: frozen gates, result
is the result, ledger-only writes (entries W6J-J1..J4), no edits to
DERIVATION_NOTES/orders, no commits, CPU only, work under
`shell/underlock/w6j/`. Reused validated machinery (w6e/engine.py,
w6f/f1_engine_ext.py, w6h/h1_excursion_spectrum.py's layered DP,
w6h/h2_two_ray_model.py, w6h/h3_wordspace_census.csv, w6g/
g2_anchor_sweep.csv); validated new code on >=3 known rows before
trusting each experiment. Executed in the order's own sequence:
J1, J3, J2, J4.

### W6J-J1 — Ceiling-mechanism check (`w6j/j1_ceiling_mechanism.py`)

**COUNTEREXAMPLES FOUND — LEADING WITH THIS PER HOUSE RULES. The
architect's registered biconditional (D(w)=L(w) <=> min_k g_loop(k)>=0)
is FALSIFIED in BOTH directions, at scale, on the full W6H-H3 census.**

Computed `min_k g_loop(k) = min_k Sum_{j<=k}(2-c_j)` directly from each
word's own digit string (validated on 3 hand-computed rows — "22"->0,
"31"->-1, "13"->0 — before running the full census) and cross-tabbed
against H3's own `D`/`L` columns across all 28,392 rows (`{0,1,2}`,
`{1,2,3}`, `{0,1,2,3}`, m=2..7 — the FULL H3 census, exactly as named).

**Result (`j1_ceiling_crosstab.csv`, 28,392 rows;
`j1_counterexamples_dump.csv`, 8,063 rows verbatim): biconditional
holds on only 20,329/28,392 (71.60%) — 8,063 (28.40%) counterexamples,
in BOTH directions:**
- 5,191 rows: break (D!=L) but loop-safe (min_k>=0) — e.g. word "13"
  (alphabet `{1,2,3}`, m=2): census says D=0, L=1 (a break); hand-
  independent re-verification via `w6e/engine.bfs_Dm` on this exact
  word confirms D=0, chain=[(1,2),(3,2)], L=1 — genuinely a break —
  while g_loop([1,3]) = [1,0], min=0, never negative.
- 2,872 rows: no break (D=L) but loop-unsafe (min_k<0) — e.g. "23",
  "32", "33" at m=2 (alphabet `{1,2,3}`): D=L=0 exactly, but
  g_loop dips to -1 or -2.

Both directions are large and systematic, not edge-case noise —
concentrated in `{1,2,3}` and `{0,1,2,3}` (which admit c=3, the
ceiling-breaking letter H3 already flagged as a scope fence) but
present at every m in scope, not a rare tail.

**GATE VERDICT vs frozen prediction (biconditional holds exactly, 80%):
MISS — decisively, 28.40% counterexample rate, hand-verified.** The
architect's ceiling-mechanism conjecture as stated does NOT capture
universality's boundary on alphabets including c=3; some additional
or different mechanism governs the D=L boundary once the ceiling
constraint can bind (matching H3's own earlier finding that letters
>=3 "engage the corridor CEILING and break the identity both
directions").

**Decisive tables:** `w6j/j1_ceiling_crosstab.csv` (28,392 rows, full
census), `w6j/j1_counterexamples_dump.csv` (8,063 rows, verbatim, both
directions labeled).

### W6J-J3 — Order-gap uniqueness census (`w6j/j3_order_gap_census.py`)

**Part A (order-gap direct verification): clean HIT, 5/5.** ord(2,3^m)
= 2*3^(m-1) verified by brute-force direct search (smallest k with
2^k==1 mod 3^m) for m=4..8: 54, 162, 486, 1458, 4374 — exact match
to the formula on every row.

**Part B (keystone pinning table): Gate (a) MISS, Gate (b) STOP-AND-
REPORT (not an engine bug — root-caused to a window/order-gap scope
effect at small m), Gate (c) HIT.**

Reloaded all 50 chains from W6F-F2's own `f2_tax_table.csv` (D+2 scope,
m=2..8 both families) verbatim — not regenerated — recomputed
S = Sum 3^(m-1-i)*2^A_i per chain (cross-validated against
`engine.keystone_check`'s own congruence check plus a "chain's own
Sigma_a is in the brute-forced solution set" smoke test, 3/3 sample
chains PASS) and brute-forced the full solution set
{sigma in [0,6m] : 2^sigma == S mod 3^m} for every chain.

**Gate (a) result (`j3b_pinning_table.csv`, 50 rows): 45/50 chains
have exactly 1 solution, 5/50 have MULTIPLE (2 or 3) solutions in
[0,6m] — MISS** against the 85% "at most one" prediction, but a
precisely diagnosed one: **all 5 multi-solution chains are at m=2 or
m=3**, exactly where 6m >= ord(2,3^m) (m=2: window=12 >= ord=6; m=3:
window=18 >= ord=18) — the window is NOT yet strictly dwarfing the
order gap at these small m (the ratio window/ord drops below 1 only
from m=4 onward: 0.444, 0.185, 0.074, 0.029, 0.011 for m=4..8). This
is confirmed as the exact mechanism (not asserted): at m=2, S%9=7 has
solutions {4,10} (spaced exactly 6=ord(2,9) apart, both landing inside
the 2-full-period window [0,12]); at m=2, S%9=1 has {0,6,12} (3 hits,
window straddles a 3rd partial period). Every multi-solution row's
own chain Sigma_a IS among its returned solutions (checked, not
assumed) — the periodicity ADDS spurious extra solutions, it never
removes the true one.

**Gate (b) result: per the order's own binding rule ("a mismatch =
engine bug, STOP and report rather than writing it up as math"), this
is reported as a STOP, not smoothed into gate (a)'s math finding.**
The order's literal test ("that sigma equals the chain's actual
Sigma_a in every case") fails on exactly these same 5 rows (multiple
sigma means "the" sigma is not well-defined) — **but the mechanism is
fully diagnosed and benign, not a bug**: Sigma_a is present in every
returned solution set, every time; the failure is purely "more than
one candidate exists in the window," caused by the window/order-gap
ratio at m<4, not a wrong S, wrong sigma, or wrong Sigma_a anywhere.
Dumped verbatim: `j3b_consistency_mismatches_dump.csv` (5 rows: all
5 are m=2 exactly — golden m=2 (a_seq "2 2" and "4 2"), sqrt2 m=2
(a_seq "2 2", "1 4", and "4 2") — verified directly from the dump).
**Read together, gates (a)/(b) establish exactly what
J3 was testing for: the order gap dwarfing the window is a real,
m-dependent threshold (kicks in at m=4 for this 6m-window convention),
not an unconditional truth at every m — a sharper, quantified version
of "the order gap dwarfs the window" than the frozen prediction
assumed.**

**Gate (c) result: clean HIT, 14/14.** Sigma_a - 2m is nondecreasing
in delta_tax within every one of the 14 (family,m) groups tested (e.g.
golden m=8: delta_tax=0->Sigma_a-2m=0, delta_tax=1->1, delta_tax=2->2
across 5 tied rows) — the clean monotone relation the architect
expected holds exactly, no exceptions.

**GATE VERDICTS vs frozen predictions:**
- (a) each S admits at most one sigma in [0,6m] (85%): **MISS**
  (45/50, with the 5 exceptions fully mechanism-diagnosed as an
  m<4 window/order-gap scope effect, not noise).
- (b) sigma equals chain's actual Sigma_a in every case (REQUIRED):
  **STOP-level finding reported as instructed** — same 5 rows,
  Sigma_a always present among solutions, never absent or wrong;
  the multiplicity itself is the (diagnosed, benign) failure mode.
- (c) Sigma_a-2m vs delta_tax clean monotone relation (60%): **HIT**,
  14/14 groups.

**Decisive tables:** `w6j/j3a_order_gap.csv` (5 rows),
`w6j/j3b_pinning_table.csv` (50 rows, the pinning table proper),
`w6j/j3b_consistency_mismatches_dump.csv` (5 rows, verbatim).

### W6J-J2 — Return-precision cost curve (`w6j/j2_precision_cost_curve.py`)

**Curve computed, CROSS-CHECKED exactly against H1's own published
answer, and it is NON-MONOTONE — a genuine, hand-verified surprise.
Gates (a) and (c) MISS; gate (b) HIT.**

**False start, reported per house rules:** a first draft tried ONE
layered DP at a single superset working precision (3^12) and read off
all 10 precisions t=1..10 by reducing residues mod 3^t at each depth.
This FAILED its own cross-check against H1's published length-8 answer
(got 38, not 27) and was traced to a genuine mechanism, not a typo:
`backward_predecessor_exact`'s exact division by 3 is representative-
dependent (two different lifts of the SAME residue class, e.g. 32269
vs 504661 both ==32269 mod 3^10, are NOT interchangeable inputs to the
backward recursion — replaying H1's own ground-truth a-sequence
(4,3,8,3,9,8,7,1) at mod 3^12 diverges from its mod-3^10 trace
starting at step 5). **Fixed the correct way, per the order's own
wording** ("for each precision t = 1..10 separately"): ran h1's
layered_dp verbatim, once per t, entirely at modulus 3^t throughout
(never mixing precisions mid-chain). t=10 is then a LITERAL rerun of
h1's own computation — confirmed to reproduce h1's published cost=27
at length=8 EXACTLY before trusting t=1..9.

**Result (`j2_precision_cost_curve.csv`, 10 rows; full grid
`j2_precision_length_full.csv`, 100 rows):**

| t | min_cost | argmin length | a_seq |
|---|---|---|---|
| 1 | 1 | 2 | (4,1) |
| 2 | 10 | 3 | (4,11,1) |
| 3 | 2 | 6 | (4,3,2,1,3,1) |
| 4 | 5 | 6 | (4,5,1,1,5,1) |
| 5 | 5 | 6 | (4,5,1,1,5,1) |
| 6 | 16 | 9 | (4,5,7,1,2,1,6,7,1) |
| 7 | 7 | 9 | (4,3,2,1,3,3,5,3,1) |
| 8 | 19 | 6 | (4,5,5,4,12,1) |
| 9 | 19 | 6 | (4,5,5,4,12,1) |
| 10 | 27 | 8 | (4,3,8,3,9,8,7,1) [=H1's own answer] |

Every entry independently hand/spot-verified (t=1, t=2, t=3 all
re-traced by hand outside the DP and confirmed exact; t=2's surprising
min-cost-10 also cross-checked via a wholly independent small-cap
memoized-BFS reimplementation, exact match).

Live-state-count saturation (exhaustiveness proof) achieved at every
t by depth <=5 (full modulus 3^t reached and held through depth 10 in
every case) — a hard proof, not a margin heuristic.

**GATE VERDICTS vs frozen predictions:**
- (a) min_cost nondecreasing in t (85%): **MISS** — two clean
  violations: (t=2,cost=10)->(t=3,cost=2), and (t=6,cost=16)->
  (t=7,cost=7). Coarser precision is NOT uniformly easier to return
  to: t=2's specific target class (rho==1 mod 9) is markedly HARDER
  to hit cheaply than t=3's (rho==1 mod 27), despite mod 9 being a
  strictly coarser condition. Mechanism (not chased further this
  round): parity-forcing is a mod-3 property of the CURRENT full
  residue, so "coarser target" does not simply enlarge the reachable
  set monotonically in a way that helps the SPECIFIC point rho==1;
  it can align badly with the forced-parity dynamics at some t and
  well at others.
- (b) min_cost at t=1 is exactly +1 (70%): **HIT** — global min at
  t=1 is 1, achieved at length 2, a_seq=(4,1) (hand-verified: trace
  1->2->1 mod 3, cost (4-2)+(1-2)=1).
  This is F2's own +1 floor, recovered exactly at the lowest precision.
- (c) curve convex-ish/superlinear in t (55%): **MISS** — first
  differences [9,-8,3,0,11,-9,12,0,8] are not nondecreasing (not even
  close; the curve oscillates rather than smoothly compounding).
  H1's high-precision value (27) IS at the top of the range, and t=1's
  value (1) IS at the bottom, so there is a coarse "low t cheap, high
  t expensive" trend across the extremes, but the interior (t=2..9) is
  genuinely jagged, not a smooth interpolating curve.

**Decisive table:** `w6j/j2_precision_cost_curve.csv` (10 rows, the
(t,min_cost,argmin) table proper). Honest wall: exhaustiveness proven
via saturation at every t; no RSS or time wall hit (peak ~0.1GB,
~17s wall for all 10 DP runs combined).

### W6J-J4 — Two-ray model repair (`w6j/j4_two_ray_repair.py`)

**Repair implemented per the order's exact formula; re-fit result:
MISS on the 90% gate (26.6% exact), with the residual mechanism fully
diagnosed by hand — a real architectural gap in the entry/ray cost
split, not merely "ran out of the 6-step/mod-3^8 scope."**

Two false starts caught by this experiment's OWN pre-trust validation
(house rule: validate on known facts before trusting), reported in
full rather than silently patched:
1. First draft ran the entry-cost DP at a FIXED mod=3^8 regardless of
   the outer problem's own working modulus 3^m. Failed validation
   against H2's own hand-verified counterexample (golden m=3, target=7,
   should be entry_cost=2 at length 1) — traced to target "7" meaning
   "residue 7 mod 27" at the outer m=3 precision, a completely
   different condition from "residue exactly 7 mod 6561." Fixed:
   entry DP runs at mod=3^m whenever m<=8 (matching the outer
   problem's own precision exactly), falling back to mod=3^8 with the
   target reduced only when m>8 (logged per-row via
   `entry_precision_note`, 288/1104 rows).
2. Second draft (correct precision, unbounded exponent menu) STILL
   failed the same validation check: found a cost=-1, length=6 path
   to target=7, cheaper than the true cost=2 length-1 edge. Hand-
   traced: this path drives the ceiling-distance budget d from 12 up
   to 15 (12->13->14->15->15->15->13), EXCEEDING C=12 — a real,
   illegal excursion the true engine could never take, an artifact of
   the entry DP tracking only residues with no (rho,d) ceiling state
   of its own (a per-step exponent cap alone does not fix this — the
   missing ingredient is d itself). Fixed: entry DP now tracks explicit
   (rho,d) state, starting at (ray_start, C=12), legality identical in
   form to `engine.allowed_exponents` (specialized to the ray's own
   fixed implicit credit, 2 for +1-ray / 1 for -1-ray per
   DERIVATION_NOTES 8b). All 3 validation facts (both rays' own fixed
   points at cost 0; H2's m=3/target=7 counterexample at cost 2,
   length 1, seq=(4,)) PASS exactly after this fix.

**Re-fit result (`j4_repaired_fit.csv`, 1,104 rows, full W6G-G2 +
extended H2 sweep; 982 evaluable, 122 NO_MODEL_WITHIN_SCOPE): 261/982
(26.6%) exact matches — MISS**, actually slightly WORSE than H2's own
un-repaired 30.2%.

**Mechanism, root-caused via a concrete hand-verified row (not left as
a mystery):** golden-per8 m=3, target=11: model predicts cost 2
(entry_len=2, entry_cost=1, ray_cost=1) but D_actual=1. The real
optimal chain (independently re-extracted via
`bfs_Dm_target_chain_with_residues`) has (c,a) pairs
[(1,2),(2,1),(2,3)] against the window's REAL credit letters [1,2,2]
— true cost = (2-1)+(1-2)+(3-2) = 1, matching D_actual exactly. The
repaired model's entry segment charges its cost against the RAY'S OWN
fixed implicit credit (2 for the +1-ray) rather than the window's real
credit letters at those specific positions — here the real first
letter is c=1, not 2, so "riding the ray" (a=2) actually costs +1, not
0, and the model's idealized bookkeeping doesn't see this. **This
explains the systematic direction of the miss: 690/721 (95.7%) of all
mismatches are OVERPREDICTIONS** (model cost > actual cost) — entry
segments charged against an idealized credit-2 ray are generically
more expensive than what the real, often credit-1-containing window
actually charges. This is a genuine THIRD finding beyond the two-ray
geometry itself (not a discovery of new structure, but a precise
diagnosis of why the "entry_cost + ray_discrepancy" additive
decomposition, as specified, cannot reach 90% no matter how exactly
entry_cost is computed): entry and ray costs are not actually
separable against different credit bases; the real chain's cost is
one seamless Sum(a_j - c_j) over the REAL window letters throughout,
and any model that computes the exit maneuver's cost against a
different (idealized ray) credit will systematically overpredict
whenever real letters near the boundary are cheaper than the ray's own
implicit rate.

**GATE VERDICT vs frozen prediction (repaired model >=90% exact, 60%):
MISS** (26.6%, and the un-repaired H2 model's 30.2% was already
higher) — reported exactly as measured, not softened.

**Decisive tables:** `w6j/j4_repaired_fit.csv` (1,104 rows),
`w6j/j4_residual_mismatches_dump.csv` (721 rows, verbatim, with
per-(family,m) diff breakdown showing the systematic overprediction
bias growing with m).

### W6J Final Digest

| Experiment | Verdict | Decisive number | Frozen predictions |
|---|---|---|---|
| J1 (ceiling mechanism) | **MISS — counterexamples, both directions** | 8,063/28,392 (28.40%) counterexamples, hand-verified (e.g. word "13" alphabet {1,2,3}: D=0,L=1, min_k_g_loop=0) | biconditional exact (80%): **MISS** |
| J3a (order gap) | HIT | ord(2,3^m)=2*3^(m-1) exact, m=4..8 | (verification, not a frozen-% prediction) HIT 5/5 |
| J3b (keystone pinning) | (a) MISS, (b) STOP-reported/benign, (c) HIT | 45/50 unique sigma; all 5 exceptions at m<4 (window>=order-gap); Sigma_a-2m monotone in 14/14 groups | (a) at-most-one (85%): **MISS**; (b) sigma==Sigma_a (REQUIRED): **mismatch reported per order, mechanism benign**; (c) monotone (60%): **HIT** |
| J2 (precision cost curve) | (a) MISS, (b) HIT, (c) MISS | curve = [1,10,2,5,5,16,7,19,19,27] for t=1..10, cross-checked exact vs H1 at t=10 | (a) nondecreasing (85%): **MISS**; (b) t=1 exactly +1 (70%): **HIT**; (c) convex-ish (55%): **MISS** |
| J4 (two-ray repair) | MISS, mechanism diagnosed | 261/982 (26.6%) exact match, worse than H2's un-repaired 30.2%; 95.7% of misses are overpredictions from idealized ray-credit bookkeeping | repaired model >=90% exact (60%): **MISS** |

**Honest walls:** none forced an incomplete result this round (no RSS
kills, no timeouts) — every experiment ran to completion within
minutes and well under 1GB peak RSS. The walls this round were
methodological, not resource-based: two false starts in J2 (precision-
mixing) and two in J4 (precision mismatch, then missing ceiling state),
each caught by this round's own pre-trust validation discipline before
any result was reported, not discovered after the fact.

**Round-level takeaway:** J1's large-scale counterexamples mean the
architect's ceiling-mechanism conjecture (§10b) does NOT hold as
stated once alphabets admit the ceiling-breaking letter c=3 — a
genuine boundary of universality's own boundary claim. J3 sharpens
"the order gap dwarfs the window" into an m-dependent statement (true
from m=4 on, for the 6m-window convention) rather than an absolute
truth, with the pinning table's monotone tax relation (gate c) holding
cleanly throughout. J2 shows the interior-rigidity induction cannot
assume a smooth precision-cost tradeoff — the true curve is jagged,
not convex, and any proof strategy built on "coarser is monotonically
cheaper" would be built on sand. J4 shows the two-ray decomposition's
failure is not a missing term but a wrong cost basis (ray-implicit
credit vs real window credit) — repairing the missing entry-cost term
exactly, as specified, does not rescue the model, because the
underlying additive separation of entry cost from ray cost is not
faithful to how real chains actually spend their budget.

## W6K — Convention Pinning + Redos (work order, Fable, 2026-07-04)

### W6K-K0 — Asymmetric validation rows + engine-path gate (`w6k/k0_convention_gate.py`, `w6k/k0_canonical_engine.py`)

**Purpose (per the order): build the missing validation class the
SYNTHESIS "W6J + architect audit" section identified — asymmetric
words where canonical-order and reverse-order give DIFFERENT answers
— hand-derive both, hand-derive both ceiling variants, then gate
every engine path this round needs against the hand table under the
CANONICAL order (architect ruling: index 0 = letter nearest the
terminal, exactly `e1_walkers.backward_letters` semantics).

**The canonical-order game, restated precisely (DERIVATION_NOTES sec
2, this is what was hand-computed):** rho starts at 1 (terminal).
Backward step j=0..m-1 consumes letter c_j (index 0 = nearest
terminal). Parity of exponent a is FORCED by the CURRENT rho
(rho%3==1 → a even, a_min=2; rho%3==2 → a odd, a_min=1; rho%3==0 →
PARITY-KILL, no legal move at any exponent). g(k) = running sum of
(a_j − c_j). rho' = (2^a·rho − 1)/3 exact integer division.
**D(m) = min over admissible processes of max_k g(k).** Two ceiling
variants, carried as separate columns, never collapsed:
- **D_ceil**: processes restricted to g(k) ≥ 0 at every prefix
  (a candidate a pruned outright — a "CEILING-KILL" — the instant it
  would drive g(k) negative).
- **D_free**: unrestricted; g(k) may go negative at any intermediate
  prefix (walker excursions "above start depth" allowed).

**Hand table (6 words × 2 orders × 2 ceiling variants = 24 rows),
menus/kill points shown step by step:**

Word "13" canonical (letters consumed in order (1,3)):
- step0: ρ=1, class=1 → even forced, a_min=2, c=1. Menu {2,4,6,...}
  (both ceiling variants identical here — g would be ≥0 for a=2
  regardless). Cheapest a=2: g(0)=2−1=1, ρ'=1.
- step1: ρ=1, class=1 → even forced, a_min=2, c=3. Cheapest a=2:
  g(1)=1+(2−3)=0, ρ'=1. Any larger a only increases max_k g.
- No parity-kill occurs anywhere in this word (ρ stays 1 throughout
  the optimal branch). **D_ceil = D_free = 1**, chain a=(2,2).

Word "13" reverse (letters consumed in order (3,1), = word "31" canonical):
- step0: ρ=1, class=1 → even forced, a_min=2, c=3. Menu {2,4,6,...}.
  a=2 gives g(0)=2−3=−1 — **CEILING-KILL under D_ceil** (pruned,
  g<0 forbidden); legal under D_free. Cheapest surviving a under
  D_ceil is a=4: g(0)=4−3=1, ρ'=(16·1−1)/3=5.
  Under D_free, a=2 stands: g(0)=−1 (max so far 0), ρ'=1.
- step1 (D_ceil branch, ρ=5, class=2 → odd forced, a_min=1, c=1):
  a=1: g(1)=1+(1−1)=1, ρ'=(2·5−1)/3=3. max_k g = max(1,1) = 1.
  **D_ceil = 1**, chain a=(4,1).
- step1 (D_free branch, ρ=1, class=1 → even forced, a_min=2, c=1):
  a=2: g(1)=−1+(2−1)=0, ρ'=1. max_k g = max(0,0) = 0 (the −1 at
  k=0 is allowed to stand under D_free, and 0 ≥ −1 so max is 0).
  **D_free = 0**, chain a=(2,2).
- No parity-kill in this word either. Ceiling-kill count: 1 (the
  a=2 branch at step0 under D_ceil).

Word "31" canonical = word "13" reverse (same letters-consumed tuple
(3,1) by construction — this is a built-in internal cross-check, not
a separate derivation): **D_ceil=1 (chain (4,1)), D_free=0 (chain
(2,2))**, matching above exactly.

Word "31" reverse = word "13" canonical (letters (1,3)): **D_ceil=1,
D_free=1**, chain (2,2) both variants — matches "13" canonical
exactly, as required by construction.

Word "113" canonical (letters (1,1,3)): optimal chain a=(2,2,2)
throughout (ρ stays 1 every step, all three letters ≤ 2's own
even-forced cheapest move stays feasible): g = (1, 2, 2)... precisely:
step0 c=1,a=2→g=1; step1 c=1,a=2→g=2; step2 c=3,a=2→g=1(running
2+(2-3)=1, max stays 2). **D_ceil=D_free=2**. No kill anywhere
(g never negative, so ceiling variant is moot here — identical to
free).

Word "113" reverse (letters (3,1,1), = word "311" canonical):
- step0: ρ=1,class=1,a_min=2,c=3. a=2→g(0)=−1 (CEILING-KILL under
  D_ceil, legal under D_free).
  - D_ceil branch: cheapest legal a=4: g(0)=1, ρ'=5.
    step1: ρ=5,class=2→odd forced,a_min=1,c=1. a=1: g(1)=1+0=1,
    ρ'=3. step2: ρ=3, **class=0 → PARITY-KILL** (no legal move at
    any exponent — a genuine dead end, not a ceiling artifact). Must
    backtrack: step1 try a=3: g(1)=1+2=3,ρ'=(8·5-1)/3=13. step2:
    ρ=13,class=1→even,a_min=2,c=1. a=2: g(2)=3+1=4,ρ'=(4·13-1)/3=17.
    max_k g = max(1,3,4)=4. Checked a=1 at step0's a=4 branch is the
    only viable continuation once a=1's ρ=3 dies; a=3 at step1 is
    the next-cheapest odd option and yields max=4. (Exhaustive DFS
    over wider a confirms no cheaper D_ceil chain exists — see
    engine cross-check below.) **D_ceil=4**, chain (4,3,2).
  - D_free branch: a=2 at step0 stands (g(0)=−1,ρ'=1). step1:
    ρ=1,class=1,a_min=2,c=1. a=2: g(1)=−1+1=0,ρ'=1. step2:
    ρ=1,class=1,a_min=2,c=1. a=2: g(2)=0+1=1,ρ'=1. max_k g=
    max(−1,0,1)=1. **D_free=1**, chain (2,2,2).

Word "311" canonical = word "113" reverse (same tuple (3,1,1)):
**D_ceil=4 (chain (4,3,2)), D_free=1 (chain (2,2,2))** — matches above.

Word "311" reverse = word "113" canonical (tuple (1,1,3)): **D_ceil=
D_free=2**, chain (2,2,2) — matches "113" canonical exactly.

Word "123" canonical (letters (1,2,3)): a=(2,2,2) throughout, ρ
stays 1: g=(1,1,0) running (step0 c=1→g=1; step1 c=2→g=1+0=1; step2
c=3→g=1+(2-3)=0). No kill. **D_ceil=D_free=1**, chain (2,2,2).

Word "123" reverse (letters (3,2,1), = word "321" canonical):
- step0: ρ=1,class=1,a_min=2,c=3. a=2→g(0)=−1 (CEILING-KILL under
  D_ceil).
  - D_ceil: a=4: g(0)=1,ρ'=5. step1: ρ=5,class=2→odd,a_min=1,c=2.
    a=1: g(1)=1+(1−2)=0,ρ'=(2·5−1)/3=3. step2: ρ=3, **class=0 →
    PARITY-KILL**. Backtrack step1: a=3: g(1)=1+1=2,ρ'=(8·5−1)/3=13.
    step2: ρ=13,class=1→even,a_min=2,c=1. a=2: g(2)=2+1=3,ρ'=17.
    max_k g=max(1,2,3)=3. **D_ceil=3**, chain (4,3,2).
  - D_free: a=2 at step0 (g(0)=−1). step1: ρ=1,class=1,a_min=2,c=2.
    a=2: g(1)=−1+0=−1,ρ'=1. step2: ρ=1,class=1,a_min=2,c=1. a=2:
    g(2)=−1+1=0,ρ'=1. max_k g=max(−1,−1,0)=0. **D_free=0**, chain
    (2,2,2).

Word "321" canonical = word "123" reverse: **D_ceil=3 (chain
(4,3,2)), D_free=0 (chain (2,2,2))** — matches above.

Word "321" reverse = word "123" canonical (tuple (1,2,3)): **D_ceil=
D_free=1**, chain (2,2,2) — matches "123" canonical exactly.

**Hand table summary (the 12 distinct (word,order) cases; the
mirrored duplicates above are the internal cross-check):**

| word | order | letters | D_ceil | D_free |
|---|---|---|---|---|
| 13  | canonical | (1,3)   | 1 | 1 |
| 13  | reverse   | (3,1)   | 1 | 0 |
| 31  | canonical | (3,1)   | 1 | 0 |
| 31  | reverse   | (1,3)   | 1 | 1 |
| 113 | canonical | (1,1,3) | 2 | 2 |
| 113 | reverse   | (3,1,1) | 4 | 1 |
| 311 | canonical | (3,1,1) | 4 | 1 |
| 311 | reverse   | (1,1,3) | 2 | 2 |
| 123 | canonical | (1,2,3) | 1 | 1 |
| 123 | reverse   | (3,2,1) | 3 | 0 |
| 321 | canonical | (3,2,1) | 3 | 0 |
| 321 | reverse   | (1,2,3) | 1 | 1 |

Every row shows a genuine order-dependence (canonical ≠ reverse on
D_free for 4/6 words; D_ceil differs canonical-vs-reverse on all 6
except the two that are the OTHER word's mirror — i.e. exactly the
"chosen so the two orders give DIFFERENT answers" property the order
required), and 4/6 words also exercise a genuine PARITY-KILL
backtrack (113/311/123/321's D_ceil branches all hit ρ=3, class 0,
mid-search), so the table exercises both trap types the order names.

**Independent from-scratch re-verification:** `k0_convention_gate.
hand_reference` (exhaustive DFS, written independently of the by-hand
narration above, reusing only the two validated residue-arithmetic
primitives `forced_parity_for_backward_step`/`backward_predecessor_
exact`) reproduces all 24 numbers exactly — 24/24 — with the
parity-kill/ceiling-kill counts consistent with the by-hand trace
(e.g. word "113" reverse D_ceil branch: 1 ceiling-kill logged at
step0, matching the a=2→g=−1 prune identified by hand).

**Engine-path gate (per the order: every path used in K1/K2/K3 must
agree with the hand table under canonical order, or STOP on that path):**

- **PATH A — `e1_walkers.walk_S0`/`walk_S1`** (backward-consumption,
  D_free only — no ceiling cap exists in this code by construction):
  **PASS, 24/24** (12 cases × 2 walkers). Both walkers' own achieved
  max-partial-sum equals the true D_free exactly on every one of the
  12 (word,order) cases — no walker reports a value BELOW the true
  minimax (which would indicate an infeasible/miscounted chain
  reported as feasible, i.e. a real bug); all matches are exact, not
  merely upper bounds, on this small-word scope.
- **PATH B — `f1_engine_ext.compute_D_and_optimal_set`** (the forward
  BFS/enumeration path used unmodified throughout W6F/W6G/W6H/W6J,
  called exactly as those rounds called it: word-as-window,
  `anchor_steps=m`, `credit_fn(k)=w[k]` for ascending k=0..m-1):
  **FAIL — engine_D matches `reverse-order D_free` on 6/6 words
  exactly** (13→0, 31→1, 113→1, 311→2, 123→0, 321→1 — every one of
  the six engine outputs equals the REVERSE-order hand table's D_free
  column, verbatim, no exceptions), and additionally coincides with
  `reverse-order D_ceil` on 3/6 (31, 311, 321 — precisely the words
  where reverse-order's D_ceil and D_free already agree with each
  other, i.e. no ceiling-prune ever binds in that direction). It
  matches the CANONICAL-order hand table (either column) on only the
  same 3/6, and never uniquely. So Path B's fixed-ceiling machinery is
  reproducing the REVERSE-order, CEILING-FREE answer exactly, not any
  ceiling-restricted quantity in either direction — the engine's own
  internal `allowed_exponents(d,c,C)` cap (fixed C=18 here) is wide
  enough on these 2-3 letter words that it never actually binds, so
  what's left to distinguish is pure direction, and Path B's direction
  is confirmed to be the reverse of canonical. Word "13" is the exact
  SYNTHESIS-cited case (engine reports D=0, reverse-order D_free=0).
  **STOP on this path per house rules — diagnosis follows, K1 does
  NOT run through it as-is.**
- **PATH C — `w6k/k0_canonical_engine.canonical_D`** (new code,
  independent exhaustive branch-and-bound DFS implementing the boxed
  canonical-order definition directly, built for K1/K2/K3 reuse,
  cross-checked at 2× the exponent cap to confirm the cap is never
  binding): **PASS, 24/24** exact match on both D_ceil and D_free.

**Diagnosis of the PATH B failure (exact location, per house rules —
lead with this, do not paper over):** `w6f/f1_engine_ext.py`'s
`forward_live_fast` (lines 101–106) computes `phase = anchor_steps -
m` then iterates `for k in range(m): c = credit_fn(phase + k)` —
i.e. **index k=0 is consumed FIRST in the forward pass and corresponds
to the WINDOW'S START** (the end of the window farthest from the
terminal at absolute forward step `anchor_steps`). `brute_force_all_
chains` (lines 254–255) uses the identical `phase+k` ascending
convention. Both are inherited unmodified from `w6e/engine.py`'s
`bfs_Dm` (lines 130,135–136) and `bfs_Dm_fast` (lines 196,198–199).
The CANONICAL order (architect ruling) defines index 0 as the letter
**NEAREST the terminal** — the *opposite* end of the window. For a
general word this is a genuine direction mismatch: it is invisible
whenever `2−c_j ≥ 0` everywhere (every alphabet validated through
W6G/W6H's `{1,2}`/`{0,1,2}` census — running sums monotone, so
prefix-max = suffix-max = total regardless of direction), and it is
exactly the failure mode SYNTHESIS's "W6J + architect audit" section
predicted and the reason this K0 round exists. **This is the SAME
underlying bug for every alphabet-extension/census result that ever
called `compute_D_and_optimal_set` or `bfs_Dm*` on a word with
`c ≥ 3` or `c = 0` letters where the discrepancy is order-sensitive**
(W6H-H3's `{1,2,3}`/`{0,1,2,3}` breaks, W6J-J1's cross-tab, W6J-J2 is
UNAFFECTED — J2/H1 use pure residue/exponent combinatorics with no
credit letters at all, so this direction bug does not reach them).

**K0 GATE VERDICT: PARTIAL PASS.** Path A and Path C pass cleanly
(24/24 each). **Path B fails (1/6)** — per house rules, K1's
alphabet-extension census (which was going to reuse
`compute_D_and_optimal_set` per the order's own text) **must use
Path C (`w6k/k0_canonical_engine.canonical_D`) instead**, not Path B,
for any canonical-order measurement. K1 proceeds on Path C only.

**Ceiling question, pinned per the order's instruction (reported as
two explicit columns throughout, never silently collapsed) — see the
hand table above: both D_ceil and D_free are real, distinct,
well-defined quantities under the canonical order, and they
frequently disagree (8/12 rows). The architect must decide which
matches corridor semantics; this round carries both forward
undecided, as instructed.**

**Decisive artifacts:** `w6k/k0_convention_gate.py`,
`w6k/k0_canonical_engine.py`, `w6k/k0_run_output.log` (full run
transcript, all 24+24+6 checks verbatim).

### W6K-K1 — Alphabet-extension redo (`w6k/k1_alphabet_redo.py`)

**Gated on K0: uses Path C (`w6k/k0_canonical_engine.canonical_D`)
exclusively — Path B (`f1_engine_ext`/`engine.bfs_Dm*`, what W6H-H3
used) failed the K0 canonical-order gate and is not used here.**
Reuses H3's scaffolding (per-alphabet time-budget loop, wholesale-drop
discipline, CSV dump shape) — deliberately not its conventions, per
the order's instruction.

Pre-census validation: `A_CAP=30` margin-checked at 2× on 12 worst-
case-shaped probe words (all-0s, all-3s, both alternating 0/3
patterns, m=5,6,7) × 2 ceiling variants = 24 checks, ALL PASS — the
exponent cap is confirmed non-binding before trusting the full sweep.

**Full scope completed on BOTH alphabets, m=2..7, no drops** (fast:
0.40s for `{1,2,3}` 3,276 words; 7.07s for `{0,1,2,3}` 21,840 words;
peak RSS 39MB — nowhere near the 8GB cap, no honest wall hit).
25,116 words total.

**Decisive result — the direction fix changes everything:**

| alphabet | words | D_ceil != L | D_free != L |
|---|---|---|---|
| {1,2,3}   | 3,276  | 1,871 (57.1%) | 0 (0.00%) |
| {0,1,2,3} | 21,840 | 8,020 (36.7%) | 0 (0.00%)  |
| **OVERALL** | **25,116** | **9,891 (39.38%)** | **0 (0.00%)** |

**D_free = L on EVERY SINGLE WORD tested, both wider alphabets, full
m<=7 scope (25,116/25,116) — universal discrepancy (G1/W6G's {1,2}
result) EXTENDS CLEANLY to {1,2,3} and {0,1,2,3} once the ceiling
constraint is dropped and letters are consumed in the canonical
order.** This directly overturns W6H-H3's retracted finding (which
reported large-scale breaks on these same alphabets) — those breaks
were an artifact of the direction bug compounded with an implicit
finite ceiling, not a real property of the alphabet extension.

**D_ceil != L is common and grows with alphabet width** (57.1% on
{1,2,3}, 36.7% on {0,1,2,3} — note the wider alphabet's rate is LOWER
because it includes many more low-discrepancy words, notably every
word containing enough `c=0` letters stays near-loop; the {1,2,3}-only
subset is uniformly the harder, more break-prone regime). Break sizes
(D_ceil - L, among the 9,891 breaks): 1 (2,489), 2 (5,089), 3 (2,033),
4 (170), 5 (98), 6 (12) — the vast majority are small (+1/+2), a long
thin tail out to +6.

**Ceiling-mechanism cross-tab (architect's conjecture, W6H sec 10b:
D=L <=> min_k g_loop(k) >= 0), both variants, retried on Path C data:**

| variant | TP | TN | FP | FN | accuracy | biconditional exact? |
|---|---|---|---|---|---|---|
| D_ceil (both alphabets combined) | 14,517 | 9,891 | 708 | 0 | 0.9710 | **NO** |
| D_free (both alphabets combined) | 14,517 | 0 | 10,599 | 0 | 0.5781 | **NO** |

(FN=0 in both variants throughout: min_g_loop>=0 NEVER coincides with
a break — the conjecture's "loop stays feasible => discrepancy-free"
direction holds with ZERO exceptions across all 25,116 words, on both
D_ceil and D_free.) The failures are entirely one-sided: **708 words
have min_g_loop<0 (the loop's own running sum dips negative at some
prefix) yet D_ceil still equals L** — the conjecture's "loop dips =>
break" direction fails on these 708/25,116 (2.8%) words specifically.
Spot-checked example: word "133" (alphabet {1,2,3}, m=3): min_g_loop=
-1 (loop dips at the first letter, c=3: 2-3=-1), yet D_ceil=D_free=
L=1 exactly — the optimal chain here evidently finds a cheaper
non-loop route back to feasibility whose OWN max never needs to
exceed L, even though the loop strategy itself would have gone
negative first. Under D_free the conjecture fails far more often
(10,599/25,116, 42.2%) since D_free=L universally (per above) while
min_g_loop<0 on far more than 0% of words — the D_free variant's
cross-tab is dominated by this near-tautological mismatch (L itself
doesn't care whether the loop dipped, since D_free=L always).

**Spot-check (hand, independent of the census script):** word "23"
(alphabet {1,2,3}, m=2), canonical letters (2,3): step0 rho=1,
class=1->even forced,a_min=2,c=2. a=2: g(0)=0, legal both variants,
rho'=1. step1: rho=1,class=1->even,a_min=2,c=3. a=2: g(1)=0+(2-3)=-1
-- CEILING-KILL under D_ceil (pruned), legal under D_free. D_ceil
branch must take a=4: g(1)=0+(4-3)=1,rho'=5; max_k g=max(0,1)=1 =
D_ceil. D_free branch keeps a=2: g(1)=-1; max_k g=max(0,-1)=0=L=
D_free. Matches the census row (`D_ceil=1,D_free=0,L=0,
min_g_loop=-1`) exactly.

**Frozen predictions:**
- (a) ceiling-ON: D_ceil = max(L,0) fails somewhere (50%): **HIT**
  — 9,891/25,116 rows have D_ceil != max(L,0) (D_ceil is not simply
  "L, clipped at 0"; the ceiling constraint genuinely reshapes the
  minimax, not just its floor).
- (b) ceiling-OFF: D_free = L everywhere, ALL alphabets (45%): **HIT**
  — 0 exceptions across both wider alphabets, full m<=7 scope, no
  drops. Universality (D=L, unique-loop-flavor) is confirmed to be
  an order-artifact-free, ceiling-free, and now alphabet-width-free
  property once the canonical order is used correctly.
- (c) ceiling conjecture biconditional holds under EXACTLY ONE of the
  two variants (60%): **MISS** — it holds under NEITHER exactly (708
  FP under D_ceil, 10,599 FP under D_free); the TN/FN=0 asymmetric
  structure (conjecture's forward direction is airtight, reverse
  direction leaks on a real but small 2.8% minority under D_ceil) is
  the actual, more nuanced shape.

**Decisive artifacts:** `w6k/k1_wordspace_census.csv` (25,116 rows),
`w6k/k1_breaks_ceil_dump.csv` (9,891 rows, verbatim), `w6k/
k1_breaks_free_dump.csv` (0 rows — empty by the D_free=L result),
`w6k/k1_run_output.log`.

**Honest walls:** none. Full scope on both alphabets, no time or RSS
wall (peak 39MB, ~8s wall total).

### W6K-K2 — Return-precision cost curve redo (`w6k/k2_precision_cost_curve_redo.py`)

**Not gated by K0 directly** (H1/J2's machinery uses pure residue/
exponent combinatorics, no credit letters, so the direction bug
proven in K0 does not reach it — confirmed in K0's own diagnosis).
K2's own bug is different: J2's curve
`[1,10,2,5,5,16,7,19,19,27]` was REJECTED in SYNTHESIS because
nested return precisions make `min_cost(t)` LOGICALLY REQUIRED to be
nondecreasing (rho==1 mod 3^(t+1) always implies rho==1 mod 3^t,
since 3^t | 3^(t+1) — the set of (t+1)-returning chains is a strict
subset of t-returning chains, so minimizing over the subset can never
beat minimizing over the superset), and J2's own curve violated this
twice: (t=2,cost=10)->(t=3,cost=2) and (t=6,cost=16)->(t=7,cost=7).

**Root cause, found by direct reproduction (not merely asserted):**
J2 ran ONE INDEPENDENT layered DP per `t`, entirely at modulus `3^t`,
reducing every intermediate residue mod `3^t` at every step. This
coarsens not just the TARGET condition but the DP's own INTERMEDIATE
STATE SPACE: two exact residues that coincide mod `3^t` at some step
but differ at higher precision get merged into one DP bucket, and
`backward_predecessor_exact`'s division-by-3 (representative-
dependent, per `engine.py`'s own docstring) then commits to whichever
specific predecessor integer happens to be live in that bucket,
silently discarding the other admissible predecessor. Concretely
demonstrated: the exact (unreduced) integer trajectory for the t=3
argmin sequence `(4,3,2,1,3,1)` — cost 2, reaching rho=19 at depth 6
— reduces to `[1,5,4,8,2,2,1]` mod 9, which DOES return to rho≡1
(mod 9) at the same depth 6 with the same cost 2; but re-running that
literal sequence through backward-arithmetic AT mod-9 precision
throughout (i.e. feeding reduced values back into
`backward_predecessor_exact` at each step, as J2's per-t DP
effectively does via bucket-merging) diverges immediately: step 3
(rho=3 at mod 9) hits `assert num % 3 == 0` failure (`backward_
predecessor_exact: not divisible by 3 (rho=3, a=3)`) — a direct,
mechanical demonstration that low-precision-throughout is NOT
equivalent to high-precision-then-reduce, exactly the "representative
dependence" issue engine.py's own docstring already named, but
manifesting here in a form J2's own false-start fix (never mixing
moduli mid-recursion) did not actually prevent, because "never mixing
moduli" was satisfied WITHIN each per-t run while still discarding
information relative to the true exact recursion.

**The fix:** run the layered DP (h1/j2's own mechanics, unchanged)
ONCE, at a single fixed HIGH modulus `3^MAX_T` (MAX_T=10, at or above
every `t` tested) throughout — never reduced further mid-recursion.
For each `t=1..MAX_T`, read off `min_cost(t)` as the min cost among
ALL live high-precision states at each depth whose residue satisfies
`rho % 3^t == 1` (an entire equivalence CLASS at every depth, not a
single merged point) — then take the global min over depths 1..10.
This makes the nesting property a STRUCTURAL fact about the shared
computation (every state counted at precision t+1 is automatically
also counted at precision t, since they're literally the same live
high-precision state re-filtered by a coarser condition), not an
emergent empirical accident to hope for.

**Validation before trusting the curve:**
1. Same house-rule mechanics validation as H1/J2 (roundtrip via the
   independently-validated forward map, fixed point at rho=1/a=2,
   mod-9 steering table) — re-run at HIGH_MOD=3^10, ALL PASS.
2. **t=MAX_T readout reproduces H1's own published ground truth
   EXACTLY: cost=27, length=8, sequence (4,3,8,3,9,8,7,1)** — the
   strongest available cross-check (a literal, not merely
   "should-agree," match).
3. Live-state-count saturates the full modulus (59,049/59,049) by
   depth 5 and holds through depth 10 — exhaustiveness at the shared
   high precision, same discipline as H1.

Wall time 8.99s, peak RSS 0.086GB — no honest wall hit, nowhere near
the 8GB cap.

**Corrected curve (t, min_cost), t=1..10:**

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| min_cost | 1 | 2 | 5 | 5 | 7 | 7 | 15 | 19 | 22 | 27 |

**NESTING ASSERTION: PASS** — the curve is nondecreasing at every
step (`[1,2,5,5,7,7,15,19,22,27]`, first differences
`[1,3,0,2,0,8,4,3,5]`, all >= 0), exactly as the (now-required, not
hoped-for) nesting argument demands.

**GATE VERDICTS vs frozen predictions:**
- (a) corrected curve is nondecreasing — REQUIRED (assertion): **HIT**
  (assertion did not fire; the fix's construction guarantees this
  structurally, and the guarantee is borne out).
- (b) t=1 value = 1 (80%): **HIT** — global min at t=1 is exactly 1,
  achieved at length 5, a_seq=(4,3,2,1,1) (this chain also touches the
  target class mod 3 at an earlier depth than 5, flagged
  `touched_target_early=True` — harmless at t=1: mod 3 is the
  coarsest possible condition, so early touches are common and do not
  change the fact that cost 1 is genuinely the global minimum, cross-
  checked against every depth 1..10 independently).
- (c) curve's big jumps (diff>=3) align with argmin-length changes
  (55%): **MISS** — 5 big jumps found (t: 2->3, 6->7, 7->8, 8->9,
  9->10), of which only 3/5 coincide with an argmin-length change
  (6->7: len 9->8 changed; 7->8: len 8->6 changed; 8->9: len 6->8
  changed) and 2/5 do NOT (2->3: len stays 6->6; 9->10: len stays
  8->8) — the jump-mechanism correlation is real but not universal;
  the curve is NOT simply "cost jumps exactly when a longer excursion
  becomes newly mandatory," some jumps happen with the SAME argmin
  length getting more expensive at finer precision.

**Cross-check against H1's t=10 value (27) and F2's t~1 value (+1):
both reproduced exactly** — H1's 27 is the shared-DP's own t=10
readout (identical, not merely close), and F2's +1 floor is the t=1
readout.

**Decisive artifacts:** `w6k/k2_precision_cost_curve.csv` (10 rows),
`w6k/k2_run_output.log` (full transcript including the shared-DP
saturation table and per-t argmin sequences).

**Honest walls:** none. Peak RSS 0.086GB, 9s wall total.

### W6K-K3 — J1 biconditional retest (`w6k/k3_j1_retest.py`)

**No new prediction this round** (per the order: K1's frozen
prediction (c) already covers this). Re-derives J1's own 2x2
cross-tab methodology (`min_k_g_loop(word) < 0` vs `D != L`) UNCHANGED
in form, against K1's clean canonical-order census (gated on Path C,
not the retracted H3 census J1 originally ran against), reported per
ceiling variant as two separate columns — this is a dedicated,
independently-runnable K3 artifact reproducing K1's own inline
crosstab exactly (708 and 10,599 counterexamples match K1's numbers
precisely, cross-confirming both scripts).

**2x2 cross-tab, D_ceil vs L (25,116 rows):**

| | min_k_g_loop < 0 | min_k_g_loop >= 0 |
|---|---|---|
| **break (D_ceil != L)** | 9,891 (biconditional holds) | 0 (counterexample dir A) |
| **no break (D_ceil == L)** | 708 (counterexample dir B) | 14,517 (biconditional holds) |

Biconditional holds on 24,408/25,116 (97.18%); 708 counterexamples
(2.82%), ALL in direction B (loop dips negative, yet D_ceil still
equals L — the conjecture's "loop-unsafe implies break" direction is
the one that leaks; "break implies loop-unsafe" holds with ZERO
exceptions, 9,891/9,891). **VERDICT: MISS** (counterexamples exist).

**2x2 cross-tab, D_free vs L (25,116 rows):**

| | min_k_g_loop < 0 | min_k_g_loop >= 0 |
|---|---|---|
| **break (D_free != L)** | 0 | 0 |
| **no break (D_free == L)** | 10,599 (counterexample dir B) | 14,517 (biconditional holds) |

D_free never breaks at all (K1's universal D_free=L result), so this
column is entirely direction-B counterexamples by construction: every
word with a loop-dip (min_k_g_loop<0) is trivially a "counterexample"
to the conjecture under D_free, since D_free=L always regardless of
whether the loop itself stayed feasible. Biconditional holds on
14,517/25,116 (57.80%); 10,599 counterexamples (42.20%). **VERDICT:
MISS.**

**Both variants MISS — the biconditional holds under NEITHER
variant exactly**, confirming K1(c)'s own verdict (MISS: "holds under
exactly one variant" did not obtain; it holds under neither). The
sharper, decisive shape (same as K1): the conjecture's forward
direction (loop-safe => no break) is airtight under D_ceil (0/9,891
exceptions) and vacuous-but-consistent under D_free; its reverse
direction (loop-unsafe => break) is what actually fails, on a small
but real 2.82% minority under D_ceil and a much larger 42.20% under
D_free (structurally, since D_free=L always).

**Decisive artifacts:** `w6k/k3_j1_crosstab_d_ceil.csv` (25,116
rows), `w6k/k3_j1_crosstab_d_free.csv` (25,116 rows), `w6k/
k3_counterexamples_dump_d_ceil.csv` (708 rows, verbatim), `w6k/
k3_counterexamples_dump_d_free.csv` (10,599 rows, verbatim), `w6k/
k3_run_output.log`.

**Honest walls:** none — pure CSV read/derive over an already-computed
census, sub-second.

## W6K Final Digest

**K0 engine-path gate (per-path pass/fail, checked FIRST):**

| Path | What it is | Verdict |
|---|---|---|
| A | `e1_walkers.walk_S0`/`walk_S1` (backward-consumption, ceiling-OFF strategies) | **PASS, 24/24** |
| B | `f1_engine_ext.compute_D_and_optimal_set` / `engine.bfs_Dm*` (forward-window, ceiling-ON, used unmodified by W6F/G/H/J) | **FAIL, 1/6 on canonical D_ceil** |
| C | `w6k/k0_canonical_engine.canonical_D` (new code, this round) | **PASS, 24/24** |

**Path B's exact bug location:** `w6f/f1_engine_ext.py` lines 101–106
(`forward_live_fast`) and 254–255 (`brute_force_all_chains`), inherited
unmodified from `w6e/engine.py` lines 130,135–136 (`bfs_Dm`) and
196,198–199 (`bfs_Dm_fast`) — all four consume `credit_fn(phase+k)`
ascending from the WINDOW START (k=0 = far end from terminal), the
exact opposite of the canonical order's index-0-nearest-terminal
convention. Engine output matches reverse-order D_free on 6/6 test
words. This is the SYNTHESIS-predicted seam, now pinned to its exact
lines, and confirmed to invalidate every alphabet-extension/cross-tab
result (W6H-H3, W6J-J1) that used `c>=3` or `c=0` letters where the
direction is order-sensitive; J2/H1 (no credit letters, pure residue
combinatorics) are unaffected by this specific bug.

**Per-experiment digest:**

| Experiment | Verdict | Decisive number | Predictions |
|---|---|---|---|
| K0 (gate) | PARTIAL PASS — Path B failed, Path A/C passed | 24/24 (A, C) vs 1/6 (B) | n/a (gate) |
| K1 (alphabet redo, Path C only) | D_free universal, D_ceil frequently breaks | D_free!=L: 0/25,116; D_ceil!=L: 9,891/25,116 (39.38%) | (a) HIT, (b) HIT, (c) MISS |
| K2 (precision cost curve redo) | Corrected, nondecreasing curve; cross-checked exact vs H1 | curve=[1,2,5,5,7,7,15,19,22,27], t=10 exact match to H1's 27 | (a) HIT (required), (b) HIT, (c) MISS |
| K3 (J1 retest, no new prediction) | Both variants MISS | 708/25,116 (2.82%) ceil counterexamples; 10,599/25,116 (42.20%) free counterexamples | covered by K1(c): MISS |

**Ceiling question — carried as two explicit variants throughout,
architect must decide (never silently collapsed):** D_ceil and D_free
are both well-defined under the canonical order and frequently
disagree. The K1 census's headline result is that **D_free = L is a
clean, total, universal law across every alphabet tested ({1,2} from
G1, {0,1,2} from H3-stands, {1,2,3} and {0,1,2,3} from K1) once the
direction bug is fixed** — universality is real and total under
ceiling-OFF. D_ceil is a genuinely different, more constrained
quantity that breaks from L on a large minority of words (39.38%
overall) and does NOT reduce to a simple `max(L,0)` clipping.

**Honest walls:** none, anywhere in this round. K0/K1/K2/K3 all
completed at full specified scope with no RSS or time-budget kills
(peak RSS across the whole round: 0.086GB in K2; peak wall: ~10s in
K2). The walls this round were entirely methodological (the K0
direction bug, the K2 nesting bug), both found, root-caused to exact
line numbers, and fixed before any redo result was trusted.

---

### W6L-L1 — Canonical loop-uniqueness re-census (`w6l/l1_uniqueness_recensus.py`, `w6l/l1b_tie_detection_check.py`)

**Instrument:** Path C exclusively. New two-pass optimal-set
collector built on `k0_canonical_engine.canonical_D`'s exact DFS
shape (same residue primitives from `w6e/engine.py`, exact big-int
backward walk): pass 1 finds D (identical pruning to `canonical_D`);
pass 2 re-runs bounded by D and collects EVERY admissible exponent
sequence achieving exactly D. Pre-run cap-margin checks at
A_CAP=40 vs 80 (3 probe words, all OK). Independent hand-traceable
verifier (`hand_trace_dfs`, full enumeration, no branch-and-bound)
stood ready for any crack; none appeared. **Instrument validation
(l1b, the K-round validation law):** the collector demonstrably
DETECTS ties when they exist — word (3,3) over {1,2,3}: D_free=0
with n_optimal=2, optima {(2,2),(2,4)}, independently confirmed by
`hand_trace_dfs` and checkable by hand in four lines. ("Loop
non-optimal" cannot occur under D_free at all: K1's universality
D_free=L plus the loop achieving L structurally puts the loop in
every optimal set — recorded as the reason that check is vacuous,
not skipped.)

**Scope run:** {1,2}^m exhaustive m=1..10 (2,046 words) + the 28
periodic-family rows (golden-per8 m=2..13,16; sqrt2-per12 m=2..16,
canonical 53-anchored windows) + the 11 real-word rows (m=2..12).

**RESULT — RIGIDITY HOLDS, NO CRACK: 2,085/2,085 rows have the
all-2s loop as the STRICTLY UNIQUE optimum** (n_optimal=1 and the
optimum is the loop, every single row). D simultaneously matches
ground truth on 28/28 periodic rows and the 22/53 mirror law on
11/11 real-word rows. The Path-B annotation on W6F/G1 uniqueness is
now CLOSED: uniqueness re-certified end-to-end on canonical
instruments.

**Frozen prediction (loop strictly unique on ALL of it, 85%): HIT.**

**Decisive artifacts:** `w6l/l1_n_optimal_table.csv` (2,085 rows),
`w6l/l1_run_output.log`, `w6l/l1b_run_output.log`.

**Honest walls:** none. Wall ~1s total, peak RSS 0.028 GB.

### W6L-L2 — Per-trit tax decomposition (`w6l/l2_per_trit_tax.py`, `l2c_exact_replay_audit.py`, `l2d_exact_ladder.py`, `l2e_ladder_extension.py`)

**THIS LEADS THE ROUND — A CRACK IN THE CERTIFIED RECORD (not in
L1's rigidity, but in W6K-K2's certified interior tax curve).** The
certified curve [1,2,5,5,7,7,15,19,22,27] is REFUTED at six of ten
points by two distinct mechanisms:

1. **Length wall.** K2 searched excursion lengths <= 10. Extending
   the same DP to length 14 produces cheaper returns at t=3
   (5 -> 3, len-13 witness), t=7 (15 -> 11), t=8 (19 -> 12), t=9
   (22 -> 12) — every one of these witnesses EXACT-REPLAY-VERIFIED
   on big integers (parity-legal chains from v=1 genuinely returning
   to 1 mod 3^t at the claimed cost).

2. **Representative fabrication.** The H1/J2/K2 DP reduces states to
   a fixed modulus 3^T every step; division by 3 loses one trit of
   certainty per step, so a t-readout of a length-d excursion is
   faithful ONLY for t + d <= T (the guarantee zone). K2's certified
   t=9 (cost 22) and t=10 (cost 27) argmins live far outside the
   zone and FAIL exact replay — **H1's published chain
   (4,3,8,3,9,8,7,1) is a legal cost-27 excursion that returns at
   precision t=7, not t=10** (hand-traced verbatim, step by step, in
   `w6l/l2c_hand_trace_h1_chain.log`: final v = 1224943075 == 1 mod
   3^7, == 4375 mod 3^8). K2's "cross-check 1: exact match to H1"
   was two copies of the same representative artifact agreeing with
   each other. Audit totals (`l2c`): K2 CSV argmins 8 verified /
   2 artifacts; the t=10 "cost 23" len-13/14 witnesses from the
   naive length extension are also artifacts (rejected).

**New instrument (fully gated): the EXACT shrinking-modulus ladder**
(`l2d`, two-limb extension `l2e`). State at depth k = v mod
3^(T0-k) from the exact terminal v=1; the one-trit-per-step modulus
decrement is exactly what division by 3 delivers, so every parity
decision and readout is provably exact — no representative error
exists anywhere. Witness extraction via the unique-predecessor
inversion p = (3c+1)*inv(2^a) mod 3^(M+1), every witness
exact-replayed. Gates: G1 vectorized step == big-int reference incl.
lift-invariance (2,263 + 5,589 samples, Mexp <= 24); G2 == structurally
independent brute-force exact-integer DFS on 9 small scopes
(per-depth tables identical); every production witness replays.

**THE EXACT CURVE OF RECORD (len <= 14 exact for t <= 12):**

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|----|----|----|----|----|
| exact min | 1 | 2 | 3 | 5 | 7 | 7 | 11 | 12 | 12 | 16 | 21 | 21 | 32* | <=32 |
| argmin len | 5 | 6 | 13 | 6 | 9 | 9 | 11 | 11 | 11 | 13 | 11 | 11 | 11 | 11 |

(*t=13 exact for len <= 11 only, T0<=24 int64 wall; its witness
returns at precision 14, so t=14 <= 32 by the same verified chain;
t=10's 16 and t=11/12's 21 could in principle drop again at len 15+
— the top of the curve is NOT yet length-stable, stated openly.)

**The tax law changes shape:** ~1.75/trit (21 cost over 12 trits),
not W6K's ~2.7/trit. Plateaus sit at (5,6), (8,9), (11,12) — every
plateau served by a LITERALLY IDENTICAL chain whose exact return
precision equals the pair's UPPER t (verified: the three plateau
witnesses return at precisions 6, 9, 12 exactly —
`w6l/l2f_witness_precisions.log`). The registered plateau instance
(3,4) DISSOLVED (it was a length-wall artifact); (5,6) survived.
Increment structure (t=1..12): +1,+1,+2,+2,0,+4,+1,0,+4,+5,0.

**Frozen predictions:** (a) plateau shapes literally identical
chains serving both t values (70%): **HIT** — 3/3 real plateaus,
mechanism confirmed at exact return-precision level (with the noted
caveat that the registered instance list was partly artifactual).
(b) every jump coincides with min excursion LENGTH increasing (55%):
**MISS** — 5/9 jumps on the exact curve (counterexamples: t=3->4
len 13->6, t=7->8 len 11->11, t=10->11 len 13->11). (c) t=11..14
continues ~2.5-3/trit with width<=2 plateaus (60%): **PARTIAL —
evaluable portion consistent** (t=10->12: +5, 0; avg 2.50/trit, in
range; plateau width 2), t=13..14 UNEVALUABLE at full length scope
(honest wall: T0 = t + d_max <= 24 under int64 two-limb arithmetic).

**Decisive artifacts:** `w6l/l2_argmin_catalog.csv` (rep-DP catalog,
replay-audited), `w6l/l2_increment_analysis.csv`,
`w6l/l2c_run_output.log` (the artifact list), `w6l/
l2c_hand_trace_h1_chain.log` (verbatim hand trace), `w6l/
l2d_exact_curve.csv`, `w6l/l2e_extended_curve.csv`,
`w6l/l2f_witness_precisions.log`, run logs.

**Honest walls:** (1) first L2 attempt ran the dict DP at 3^14
directly and was killed by its own 280s timeout with zero output —
recorded, restructured; (2) t=13 full-length and t=14 values blocked
at T0 <= 24 (int64 two-limb bound); (3) length-stability above
len 14 for t >= 10 open. Peak RSS 0.176 GB (core), 0.158 GB
(ladder); every production run seconds-scale.

**SYNTHESIS impact (for the architect):** 11b's "interior tax curve
(corrected, trustworthy)" must be re-annotated: trustworthy only as
the length-<=10 representative-DP object inside the t+d<=10
guarantee zone; the exact-game curve is the table above. H1's
"exact-return excursions up to length 8 cost >= 27" (10a) is
unsupported at t=10 (its witness returns at t=7; the true len<=8
t=10 exact min is 28, len<=14 min is 16). The 2.7/trit figure in
11b/P-II should read ~1.75/trit (len<=14, still an upper bound on
the asymptotic rate).

### W6L-L4 — Excursion-tax composability (`w6l/l4_composability.py`, `l4b_margin_check.py`, `l4c_gap1_unlock_demo.log`)

**Instrument:** Path-C constrained DFS (identical mechanics to
`canonical_D`, with forced exponent positions; forced value that
violates the residue-forced parity kills the branch). Gates: G1
unconstrained == `canonical_D` on all 9 windows; G2 fully-forced ==
independent direct replay (incl. the all-2s loop == L(w), and a
None==None infeasibility agreement); G3 parity-impossible embedding
correctly reported infeasible. Shapes: the three cheapest
EXACT-VERIFIED L2 argmins s1=(4,3,2,1,1), s2=(4,3,2,1,3,1),
s3=(4,5,1,1,5,1). Windows: golden-per8/sqrt2-per12/real-word,
m=14,15,16 (canonical 53-anchored). Scope note: three-shape
embeddings DO NOT FIT (3x5 + 2x2 gaps = 19 > 16); the order's "2-3
shapes" is honestly pairs-only. Margin checks: all 246 evaluable
rows IDENTICAL at doubled exponent cap (a_cap 40 -> 80).

**RESULT — ADDITIVITY IS NOT MERELY VIOLATED, IT DOES NOT EXIST ON
THIS OPERATIONALIZATION.** Of 651 embedding rows: 246 evaluable, 405
jointly infeasible within the cap-40 search. Among evaluable rows
(all gap 2..4): **0/246 additive; 0/246 even within +-1; every delta
POSITIVE (super-additive), range +5..+67.** All gap<=1 rows are
infeasible at cap 40; at cap 250 still 17/18 sampled infeasible.

**Mechanism, proven exactly:** a fully-forced block's legal-entry
set is EXACTLY ONE residue class mod 3^len(block) (each forced
parity pins one trit, and a matching lift always exists — so entry
is a 3^(-len) coincidence, never robust). One free step with
unbounded exponent reaches ANY class mod 3^(K-1) (2^a sweeps <4> =
the full unit subgroup == 1 mod 3), so gap-1 joints ARE feasible in
the unbounded game — but only at steering exponents of order
2*3^len(B). Demonstrated end-to-end (golden-per8 m=16, s1@0+s1@6):
unlock exponents a5 = 94, 580, 1066, 1552 — spacing exactly
486 = 2*3^5 as predicted — and the minimal-unlock joint tax is
**583 vs additive expectation 5 (delta +578)**, the steering
exponent entering the max partial sum directly. Gap-0 joints have
zero free steps and are deterministically dead unless the first
block's exit class happens to match (none of the sampled 9 did).

**Frozen predictions:** (a) exact additivity for gap>=2 (70%):
**MISS** — 0/246. (b) interference at gap<=1 (55%): **HIT** — total
interference (deterministic infeasibility at gap 0; ~3^len steering
tax at gap 1), far beyond the envisioned magnitude; note the
gap>=2-vs-gap<=1 CONTRAST the prediction pair envisioned does not
exist: interference is universal, catastrophic at small gaps.

**Program consequence:** P-II's assembly step CANNOT treat excursion
shapes as relocatable letter-level blocks — the trit cascade couples
every block to the terminal's residue trajectory. Whatever composes
must be defined at the free-optimization level (D-increments /
return-precision classes), not pinned exponent patterns. This is the
same coupling that breaks J4's model (see L3).

**Decisive artifacts:** `w6l/l4_composability.csv` (651 rows),
`w6l/l4_run_output.log`, `w6l/l4b_run_output.log`,
`w6l/l4c_gap1_unlock_demo.log`.

**Honest walls:** joint minimization at gap<=1 not run at the
~1500-wide menus full feasibility requires (the one computed case,
a5=580 -> joint 583, is exact for its search scope; others reported
as "feasible only above the searched menu"). Peak RSS 0.03 GB.

### W6L-L3 — J4 residual structure / third-structure hunt (`w6l/l3_residual_structure.py`)

**PREMISE CORRECTION (load-bearing, leads this entry).** The order
states "The model overpredicted 95.7% — something makes real chains
CHEAPER than ray-descent + ray-riding." The dump says the opposite:
**95.7% (690/721) of mismatches are model UNDERpredictions
(model_prediction < D_actual) — real chains are MORE EXPENSIVE than
the ray decomposition**; only 4.3% (31/721) are overpredictions. The
order's own number (95.7) matches the dump's negative-diff share
exactly — the direction label in the order is inverted relative to
its own source. Verified three times (independent recomputations
from `w6j/j4_residual_mismatches_dump.csv`, example rows dumped).
Consequence: mechanisms (i) mixed itineraries and (ii) entry-segment
credits are CHEAPENING mechanisms and can only ever address the 4.3%
minority.

**Inputs & instruments:** w6j dumps (order-immune per SYNTHESIS's
W6J-J4 annotation). Chain extraction used
`h2_two_ray_model.bfs_Dm_target_chain_with_residues` — Path-B-derived
machinery, used ONLY on the J4 input class whose order-immunity
SYNTHESIS certifies (declared per the instrument rule's escape
clause), and double-gated: 189/189 extracted chains reproduce the
dump's D_actual exactly; and a Path-C canonical anchored DFS
cross-check at m<=4 reproduces D_actual 21/21 under ceiling-OFF
(18/21 ceiling-on) — **documenting that the G2/H2/J4 ground truth
corresponds to the ceiling-OFF canonical game on this input class.**

**Classification (544 deduped keys vs 178 exact-match controls):**
diff distribution {-5:8, -4:49, -3:164, -2:160, -1:139, +1:15, +2:5,
+3:4}; r mod 9 flat across units for both sets. **3-adic proximity
to cycle shadows: NO enrichment anywhere** — residual vs control
means: +1 ray 0.732 vs 0.708; -1 ray 0.735 vs 0.865; -5/-7 cycle
1.456 vs 1.494; -17 cycle 2.009 vs 2.096. Keys sitting ON a 1/2-step
fixed-point class mod 27: residuals 69.9% vs controls 79.8% (vs 48%
uniform) — the fixed-point classes are ANTI-enriched among
residuals: proximity to ray-like structure makes the model MORE
accurate, exactly as a no-third-ray world predicts.

**(iii) done honestly, not perfunctorily:** full enumeration of
1-step fixed points (one per exponent a: -1/(3-2^a) mod 3^k) and
2-step fixed points ((a1,a2) in 1..4^2, incl. the order's
(1,3),(3,1),(2,2)) mod 27 and mod 81; the (1,2)/(2,1) fixed points
are precisely the -5/-7 negative-cycle shadow. Zero of 189 extracted
optimal chains touch a -5/-7 shadow residue exactly; no residual
clustering near any enumerated class. **NO THIRD STRUCTURE EXISTS in
this data.**

**Mechanism census (189 extracted true optimal chains):**
**83.6% touch NO ray at all** (no step at residue 1 or 3^m-1) — the
two-ray picture (descend, ride, exit) is simply not what optimal
chains to generic targets do; 11.1% ride +1 but cost MORE than the
model's additive decomposition (the L4 composition-coupling
mechanism — ray+entry does not splice at additive cost); 5.3% (all
in the overprediction class) ride +1 cheaper than the model.
Under-prediction keys: 158 no-ray + 21 rides-+1-costlier; zero
explained by cheapening mechanisms.

**Frozen prediction ((i)+(ii) explain >= 90% of residuals; no third
ray — 65%): MISS** — cheapening mechanisms cover 5.3% (structurally
capped by the premise inversion at ~4-5%); the no-third-ray HALF is
SUPPORTED (anti-enrichment + zero shadow touches), but the
conjunction fails.

**The real shape of the J4 residual:** the model's failure is not a
missing structure — it is L4's non-additivity: max-partial-sum games
do not decompose segmentwise, and generic-target optima are
free-form chains, not ray-riders. J4's residual and L4's
interference are one phenomenon.

**Decisive artifacts:** `w6l/l3_residual_classification.csv` (544
rows), `w6l/l3_mechanism_sample.csv` (189 rows),
`w6l/l3_run_output.log`.

**Honest walls:** mechanism census sampled (all m<=6 keys + 6 per
family at m=7,8 = 189 of 544; m=9,10 chains not extracted;
distribution stable across m=3..8). Exact-contact ray classification
is conservative (mod-3^m equality; coarse proximity handled
separately in the classification table). Peak RSS negligible; wall
0.1s.

## W6L Final Digest

| Experiment | Verdict | Decisive number/table | Frozen predictions |
|---|---|---|---|
| L1 (uniqueness re-census) | Rigidity total on canonical instruments; Path-B annotation closed | 2,085/2,085 loop strictly unique; 28/28 + 11/11 ground-truth match | HIT (85%) |
| L2 (per-trit tax) | **K2/H1 certified curve REFUTED at 6/10 points (length wall + representative fabrication; H1's t=10 chain actually returns at t=7)**; exact ladder built+gated; new exact curve [1,2,3,5,7,7,11,12,12,16,21,21], ~1.75/trit, plateaus (5,6),(8,9),(11,12) all identical-chain | t+d<=T guarantee-zone law; every claim now witness-backed | (a) HIT, (b) MISS 5/9, (c) partial-consistent/walled |
| L4 (composability) | Additivity does not exist at pinned-shape level; super-additive +5..+67 everywhere; gap<=1 needs ~2*3^len steering exponents | 0/246 additive; unlock spacing 486=2*3^5 exact; demo joint tax 583 vs additive 5 | (a) MISS 0/246, (b) HIT (total interference) |
| L3 (J4 residual) | Order premise INVERTED vs its own data (95.7% = underprediction); no third structure; 83.6% of true chains touch no ray; residual = L4's coupling | 544 keys: -5/-7 prox 1.456 vs 1.494; fixed-point occupancy 69.9% vs 79.8% (anti-enriched); 21/21 ceiling-OFF convention match | MISS (cheapening covers 5.3%, needed 90%; no-third-ray half supported) |

**Program state after W6L:** (1) rigidity/uniqueness is total and
now certified end-to-end on canonical instruments — the lower-bound
lemma remains a strict statement; (2) the interior tax law must be
rebuilt on the exact ladder curve (~1.75/trit; length-stability
above len 14 open for t>=10; plateau mechanism = one chain owning
both trits, now exact); (3) excursions are NOT composable as
letter-blocks — P-II's assembly and J4's model share one failure
mode (segment coupling through the trit cascade), so the composition
layer of the proof program needs a different object (return-precision
classes / D-increments); (4) no third invariant structure — the
two-trivial-cycle geometry stands. Instruments: exact
shrinking-modulus ladder joins Path A/C as certified; the
representative DP (H1/J2/K2 lineage) is RETIRED outside its
t+d<=T guarantee zone; every excursion claim now requires an
exact-replay witness. Peak RSS this round: 0.176 GB; no run
exceeded 30s except the first (killed, restructured) L2 attempt.

## W6M — Global-Lemma Empirical Map (work order, Fable, 2026-07-04)

Order: W6M_GLOBAL_LEMMA_MAP_ORDER.md; ledger W6M-M1..M3. Context:
DERIVATION_NOTES §12 — the proof obligation collapsed to ONE global
lemma; this round builds the empirical maps the global argument will
be written against. Instrument rule as W6K/W6L: Path C
(w6k/k0_canonical_engine.py semantics) or Path A only; Path B
retired, not used anywhere in M1/M2/M3.

**W6M-M1 — Where the +1 bites (the strictness map).** Scope: m=4..8,
mechanical-family words (golden-per8, sqrt2-per12) + up to 200 random
{1,2}^m words/m (seed 20260704; 442 words total). Exhaustive
branch-and-bound enumeration (canonical order, D_free/ceiling-off) of
every admissible chain with max partial sum ≤ L(w)+1: 961 total
chains in-band, 519 non-loop. Every non-loop chain's own binding
prefix k* and exact residue there were independently re-derived from
scratch (fresh `backward_predecessor_exact` replay, not reused DFS
state) — **519/519 PASS**.

Frozen (a) "left the 1-ray at the relevant precision" (65%):
the SHARP reading (chain's residue at k* differs from the loop's own
exact residue at that same prefix — the loop is a fixed point,
`backward_predecessor_exact(1,2)==1`, so this is well-defined) is
**519/519 = 100%** — but this reading is close to tautological for
any chain that has taken a single non-loop step by k*, so it is
reported honestly as a weak confirmation, not inflated. The COARSE
reading (rho(k*) mod 3 ≠ 1) is a more informative number: **394/519 =
75.9%**. Neither reading sits at the 65% point estimate cleanly
(100% trivially clears it, 75.9% overshoots); **MISS** against the
tight 65% band, reported both ways per the order's own admission that
the phrasing supports two readings.

Frozen (b) g(k*) ≥ g_loop(k*) universally (55%, "genuinely unsure"):
**HIT, cleanly — 519/519 = 100%.** Zero violations found; the loop's
own binding prefix is a universal floor point on every non-loop chain
tested within L+1. No `m1_floor_violations.csv` was written (none
existed). k* distribution is interior-heavy (peaks at k*=5,7,4,6 —
not edge-concentrated).

**Decisive artifacts:** `w6m/m1_strictness_chains.csv` (519 rows),
`w6m/m1_word_summary.csv` (442 rows). Peak wall <1s, RSS negligible.
Cap-margin re-checked at 2x on the widest-band probes (m=4,8 all-1s
words) before trusting the full census — no discrepancy.

**W6M-M2 — Congruence-class cost floors (the lemma's empirical
form).** Scope: m=5..8, the two mechanical-family words. Every
admissible chain (Path C, D_free) within L+2: 48 chains total across
8 (word,m) cells, exact per-prefix residues tracked as genuine Python
integers throughout (no truncation — m≤8 makes this free). Departure
prefix = first j with r_j ≠ 1 (exact integer test; the loop chain is
the unique r_j≡1-forever trajectory). Every chain's max-partial-sum
and residue trajectory independently re-derived from scratch before
being trusted (0 replay failures/48); the departure-floor table was
additionally cross-checked by a second, structurally separate scan
over the materialized per-chain dump rows (0 mismatches/8 cells).

**THE DECISIVE TABLE** (departure prefix j → f(j) = floor−L, all 8
cells in `w6m/m2_departure_floor_table.csv`):
golden-per8 m=5 [(1,2),(2,2),(4,1),(5,2)]; m=6 [(1,2),(2,2),(5,2),(6,2)];
m=7 [(2,2),(6,2),(7,2)]; m=8 [(1,2),(2,2),(3,2),(4,2),(5,2),(7,1),(8,2)];
sqrt2-per12 m=5 [(1,1),(2,2),(4,1),(5,2)]; m=6 [(1,1),(2,2),(5,2),(6,2)];
m=7 [(1,2),(2,1),(3,2),(4,2),(6,1),(7,2)]; m=8 [(1,2),(2,2),(3,2),(4,2),(7,2),(8,2)].

Frozen prediction (60%, clean "leaving late is cheaper" departure→floor
law, f nonincreasing in j): f(j) ≥ 1 holds on **all 8/8 cells**
(the floor lemma's sign is right — departing at all always costs at
least L+1). The **nonincreasing-in-j shape does NOT hold**: 5/8 cells
show f(j) DIP then RECOVER (e.g. golden-per8 m=8: 2,2,2,2,2,**1**,2 —
a single interior j=7 undercuts the floor by exactly 1 trit, then j=8
returns to 2). **MISS.** The real shape is a flat ceiling (mostly
f(j)=L+2, i.e. chains ride the full slack band) with occasional
single-j dips to L+1 at specific residue-class departures, not a
monotone late-is-cheap curve — this non-monotonic dip IS the
departure-time structure the global induction will have to explain,
not a clean boundary law.

**Decisive artifacts:** `w6m/m2_departure_floor_table.csv` (38 rows,
the table above), `w6m/m2_chain_dump.csv` (48 rows, per-chain),
`w6m/m2_trajclass_groups.csv` (26 rows, depth-3 mod-27 trajectory
groups). Peak wall <1s.

**W6M-M3 — Ladder walls extension (close L2's honest gaps).** L2e's
two-limb int64 ladder is documented to M_exp≤24; probed directly
before reuse (throwaway check, not part of the certified record) at
M_exp=26 and found a genuine int64 OVERFLOW in its `P_hi*sub` cross
term (product ~3^42 > 2^63) — confirming L2e's stated ceiling is a
real arithmetic wall, not a conservative round number. Rather than
build an uncertified wider-limb int64 scheme under time pressure,
this round built a FRESH exact-bigint instrument (Python big integers
throughout, no modular int64 anywhere, so this overflow class cannot
recur by construction), gated the same way as L2d/L2e: G1 (bigint
step vs. independent closed-form + lift-invariance, 2520 samples,
M_exp up to 28) PASS; G2 (vs. l2d's own brute_force_exact, reused
unmodified as a structurally independent reference) PASS on 5 small
scopes; G3 — every witness exact-replayed via `engine.py`'s
`backward_predecessor_exact` (519→ all witnesses below PASS), plus an
overlap cross-check: **every per-depth minimum shared with L2e's
certified per-depth tables agrees exactly** (t=10: depths
{10,11,12,13} match; t=11: depths {8,11,12,13} match; t=12: depth
{11} matches — 0 mismatches).

**Part 1 (t=13,14 at len≤14, T0=27,28):** BOTH cells completed, no
wall. **t=13: exact min (len≤14) = 31**, len-14 witness
`(8,2,3,6,2,1,2,2,1,2,5,10,2,13)`, exact-replay PASS. **t=14: exact
min (len≤14) = 32**, len-11 witness `(10,5,2,4,2,1,4,1,1,14,10)`,
exact-replay PASS. This closes both of L2/L2e's open cells (L2e had
no value at all for t=14, and only a len≤11 value of 32 for t=13's
neighbor scope). Curve of record extends to t=1..14 →
[1,2,3,5,7,7,11,12,12,16,21,21,31,32].

**Part 2 (length-stability probe, t=10,11,12 at len 15,16, T0=25-28):**
ALL 6 cells completed, no wall (peak RSS 4.40GB, under the 8GB cap).
**The curve DROPS FURTHER for t=11 and t=12** — contradicting the
frozen prediction:

| t | len≤14 (L2e certified) | len≤15 (this round) | len≤16 (this round) | stable? |
|---|---|---|---|---|
| 10 | 16 | 16 | 16 | YES |
| 11 | 21 | **19** | **19** | NO — drops 2 |
| 12 | 21 | **19** | **19** | NO — drops 2 |

Both t=11 and t=12's new minimum is achieved by the SAME len-15 chain
`(4,3,2,5,4,3,1,3,2,2,1,4,9,5,1)` (exact-replay PASS both times) —
one witness serving two precisions, structurally the same
"plateau = one chain owns both trits" phenomenon L2 already found at
shorter length, just not visible until length 15 was reached. **Frozen
prediction (60%, "stable at len 15-16 for t≤12"): MISS** — 2 of 3
probed t-values are NOT stable; the L2e len≤14 curve was scope-capped,
not converged, exactly the kind of length wall the L2 lesson warned
about.

**Decisive artifact:** `w6m/m3_ladder_extension.csv` (8 rows, both
parts). Total wall 464.5s; peak RSS 4.398GB (under the 8GB cap on
every cell); no honest wall was hit anywhere in this round — all 8
target cells ran to completion.

## W6M Final Digest

| Experiment | Verdict | Decisive number/table | Frozen predictions |
|---|---|---|---|
| M1 (strictness map) | Floor point (b) holds totally; departure reading (a) ambiguous between trivial-100% and informative-75.9% | 519 non-loop chains: (a) 100%/75.9% (two readings), (b) 519/519=100% | (a) MISS (neither reading sits at 65%), (b) HIT (55%) |
| M2 (departure→floor table) | f(j)≥1 always; nonincreasing-in-j law fails — flat ceiling with occasional single-j dips, not monotone | 8 (word,m) cells, table in ledger text; 5/8 show non-monotonic dip-then-recover | MISS (60%) — f≥1 confirmed, shape is dip/recover not nonincreasing |
| M3 (ladder wall extension) | Both L2 gaps closed (t=13→31, t=14→32); length-stability FAILS for t=11,12 (curve drops 21→19 at len 15) | curve t=1..14: [1,2,3,5,7,7,11,12,12,16,21,21,31,32]; t=11,12 new min=19 at len15, shared witness | MISS (60%) — 2/3 probed t-values unstable |

**Program state after W6M:** the empirical maps for the global-lemma
argument are built. (1) The loop's own binding prefix is a genuine,
exceptionless floor (M1-b) — the global argument CAN anchor on it
safely everywhere tested. (2) Departure-time is not a clean monotone
cost law (M2) — the floor is a flat ceiling (chains ride the full
L+2 slack almost everywhere) with sparse single-prefix undercuts, so
the global induction needs to explain DIPS, not fit a smooth
boundary-effect curve. (3) The exact ladder curve is NOT converged at
length 14 (M3) — t=11,12 both drop from 21 to 19 once length 15 is
reached via one shared witness chain, meaning every "exact" curve
value up to this round must be read as "exact for its scope," and
further length extensions remain open (T0>28 needs a wider-than-28
instrument, not attempted here). All three experiments used only
Path C/Path A machinery or freshly-gated independent instruments; the
W6L exact-replay discipline held throughout — every reported witness
across M1/M2/M3 (519+48+8 = 575 witness-bearing rows) passed
independent from-scratch replay, 0 failures. Peak RSS this round:
4.398 GB (M3); M1/M2 negligible (<0.1s each). No honest wall was hit
in any of the three experiments — all target cells specified in the
order ran to completion.

## W6N — Floor Mechanism + Convergence (work order, Fable, 2026-07-04)

Order: W6N_FLOOR_MECHANISM_ORDER.md; ledger W6N-N1..N4. Context:
DERIVATION_NOTES §13 — the floor-point law (M1, 519/519) is the
global lemma's anchor; this round tests its mechanism (N2, the
intellectual center), extends its scope (N1), fingerprints the
boundary dips (N3), and closes the tax curve's length convergence
(N4). Instrument rule as W6K/W6L/W6M: Path C semantics + the W6M
exact-bigint ladder only; Path B retired, not used anywhere.

### W6N-N1 — Floor-point law at full generality (`w6n/n1_floor_generality.py`)

**Scope decision (stated, not silent):** the order says "ALL
admissible chains within L+3, m=4..7 (exhaustive, Path C), same
442-word scope trimmed as needed." M1's 442-word scope was
mechanical rows + random samples; N1's own "exhaustive" upgrade
makes the true exhaustive word space {1,2}^m, m=4..7 = 240 words the
correct object (both mechanical-family words verified to be MEMBERS
of the enumerated set at every m — no separate pass needed, no
random padding that would dilute the exhaustiveness claim).

**Result: 240/240 words, 2,956 admissible chains within L+3, 2,716
non-loop — ZERO violations of g(k*) ≥ g_loop(k*).** No word trimmed
(largest per-word census far under the 5M row cap), no RSS wall
(peak 0.027 GB), wall 0.1s. Cap-margin pre-checked at 40 vs 80 on
the widest-band probes (all-1s words m=4, m=7) — identical counts.
The violation dump/exact-replay path was armed and produced an empty
`n1_violations.csv` (0 rows) — nothing to replay because nothing
violated.

**Frozen prediction (exceptionless at every budget, 75%): HIT.**
The floor-point law survives a 3× budget widening (L+1 → L+3) and
full word-space exhaustion. The anchor holds; nothing outranks
downstream work.

**Decisive artifacts:** `w6n/n1_word_summary.csv` (240 rows),
`w6n/n1_violations.csv` (0 rows), `w6n/n1_run_output.log`.

### W6N-N2 — Is the floor forced by the prefix congruence ALONE? (`w6n/n2_prefix_congruence_mechanism.py`)

**THE ROUND'S LEAD FINDING: PREFIX-ALONE SUFFICES — the frozen
prediction is inverted.** On all 40 sampled words (mechanical rows
golden-per8/sqrt2-per12 at m=5,6,7 + 34 seeded random {1,2}^m words),
the minimum max-partial-sum over ALL residue-feasible prefix states
of length k* (parity/congruence constraints only, NO suffix
feasibility requirement, NO slack-band pruning — true unrestricted
minimum via branch-and-bound) equals g_loop(k*) EXACTLY:
**min_prefix_cost == g_loop(k*) on 40/40 words; zero cheap-at-k*
prefixes exist anywhere.** The set "prefix states reachable below
the floor" is EMPTY — the mod-3^k* congruence alone already forbids
being cheap at k*; the suffix never gets a chance to kill anything
because there is nothing to kill.

**Frozen prediction (cheap prefixes exist, killed by suffix — the
L4 whole-window coupling picture, 65%): MISS, decisively.** The
floor g(k*) ≥ g_loop(k*) is a ONE-POINT congruence fact, not a
whole-window fact. Per the order's own consequence table:
prefix-alone ⟹ the induction gets a ONE-POINT argument at k* (no
forward invariant needs to be carried). This materially simplifies
the proof obligation: the lower-bound lemma's anchor inequality
lives entirely in the prefix-projected keystone at a single index.

**Instrument notes (honest):** the first implementation attempted
FULL enumeration of the unrestricted prefix space — a genuine
combinatorial wall (20 same-parity choices/step at A_CAP=40 ⟹ 20^k*
≈ 1.3e9 states at k*=7; process killed at 3.1GB RSS before any
output). Replaced with (i) branch-and-bound for the true minimum
(same pruning-soundness argument as k0's canonical_D: max is
monotone along extensions) and (ii) threshold-pruned enumeration for
the cheap-state census (only materializes states strictly below
g_loop(k*) — provably complete for the census by the same
monotonicity). Both A_CAP margin-checked at 40 vs 80 per word,
40/40 stable.

**Cross-checks (all passed):** (1) architect-style independent
replay — a from-scratch, unpruned brute force (separate code, cap
30, no branch-and-bound) reproduces min_prefix_cost == g_loop(k*) on
4 spot-checked words including both mechanical rows at m=5; (2) one
word (1122211, m=7, k*=7) re-verified at caps 40/80/160/320 —
minimum stays 4 = g_loop(k*) at every width (not a cap artifact);
(3) the completion/cross-consistency machinery (case (c): a cheap
prefix WITH a legal completion would contradict N1/M1) was armed and
never fired — vacuously consistent with N1's clean 240/240.

**Decisive artifact:** `w6n/n2_prefix_congruence_table.csv` (40
rows: every row min_prefix_cost == g_loop_at_kstar, n_cheap_states=0).
`w6n/n2_run_output.log`. Wall <0.1s after the redesign.

### W6N-N3 — Dip fingerprinting (`w6n/n3_dip_fingerprinting.py`)

**Scope/band note (load-bearing, stated up front):** the order says
"within L+1" — narrower than M2's L+2. At an L+1 band, f(j)=1 is the
ONLY value a departure can appear with (f(j)=2 departures are absent
from the census, not present-with-higher-floor), so "dip catalog" at
this band = "every departure reachable at all within L+1." Continuity
verified exactly: N3's in-band departures reproduce M2's f=1 dip set
on every overlapping cell (7/7 dips at m=5..8), plus two new m=9
rows (sqrt2-per12 j=4, j=8; golden-per8 m=9 has NO in-band departure
at all — the L+1 band is empty of non-loop chains there except the
loop). 9 dip rows total; 0 replay failures (every chain in every
census independently re-derived from scratch).

**THE DIP CATALOG (9 rows, `w6n/n3_dip_catalog.csv`):**
golden-per8: (m=5, j=4, phase 1), (m=8, j=7, phase 6);
sqrt2-per12: (m=5, j=1, phase 4), (m=5, j=4, phase 1),
(m=6, j=1, phase 4), (m=7, j=2, phase 3), (m=7, j=6, phase 11),
(m=9, j=4, phase 1), (m=9, j=8, phase 9).
Local structure: 6/9 dips sit at letter-2 positions exactly one step
before a support letter (dist_to_nearest_support=1); the other 3/9
sit ON a support letter (dist=0). No dip sits ≥2 steps from support.
"Correction letter" distance: N/A for this word class (pure periodic
mechanical words; no true-word deviation exists to measure — the
g4 concept does not apply, reported explicitly rather than
silently dropped).

**Frozen prediction (dips ⟺ suffix-from-j is a maximal-credit run,
55%): MISS.** Operationalized as suffix support-density: strict-max
reading 3/9 = 33.3%; top-quartile reading 3/9 = 33.3%. The
over-credit picture explains the three j=1/j=2 early dips
(suffix = essentially the whole window, trivially max-density) but
NOT the six interior/late dips: five of those sit at LOW suffix
densities (1-2 supports remaining) and one (sqrt2-per12 m=9 j=4)
at 4-of-max-5 — near-max but not max. The consistent local signature is
support-adjacency (dist ≤ 1 in 9/9), not suffix credit mass.

**Decisive artifacts:** `w6n/n3_dip_catalog.csv` (9 rows),
`w6n/n3_chain_dump.csv` (9 rows), `w6n/n3_run_output.log`.
Wall <0.1s.

### W6N-N4 — Length convergence of the tax curve (`w6n/n4_length_convergence.py` + `n4c_tight_cap_closure.py` + `n4b_convergence_verdict.py`)

**Instrument:** the W6M exact-bigint ladder, reused as a module (not
reimplemented); its G1/G2 gates RE-RUN fresh in-process in both the
static-cap and tight-cap runs before any production value (all PASS);
every witness exact-replayed (n4b re-replays all 10 witness cells
independently, including a max-t-served precision readout — 0
failures).

**Three-instrument story (honest):** (1) the static-cap run
(cap = M3_best + 4) completed t=10,11,12 at len 17,18 cleanly but
WALLED mid-sweep (300s/cell budget, ~4.4GB) on t=13 len≥16 and t=14
len≥15 — the caps (35/36) were sized to M3's pre-drop values and the
mid-run t=13 discovery made them obsolete; (2) `n4c` closed the
walled cells with SOUND tightened caps (a found min ≤ cap is exact
for scope; a cap can only miss, never fabricate): t=13 at cap 21 —
len 16/17/18 all = 19 EXACT, seconds each (state counts collapsed
7.1M → 380k); t=14 at cap 24 — len 15/16/17/18 all complete, NO
value ≤ 24 exists; (3) `n4b` recomputes convergence from the union,
excluding walled cells (a walled cell's value covers only pre-wall
depths — upper bound, not the scope's min).

**CORRECTED CURVE OF RECORD (t=10..14):**

| t | series (len: min) | verdict |
|---|---|---|
| 10 | 14:16, 15:16, 16:16, 17:16, **18:15** | **STILL-OPEN at 15** — width-4 plateau BROKE at len 18 |
| 11 | 14:21, 15:19, 16:19, 17:19, 18:19 | CONVERGED at 19 (len≤18) |
| 12 | 14:21, 15:19, 16:19, 17:19, 18:19 | CONVERGED at 19 (len≤18) |
| 13 | 14:31, **15:19**, 16:19, 17:19, 18:19 | CONVERGED at 19 (len≤18) — dropped 12 in one length step |
| 14 | 14:32; len 15-18: nothing ≤ 24 exists (complete, sound) | STILL-OPEN in [25, 32]; 32 = best witness (len 11) |

**THE FOUR-TRIT PLATEAU WITNESS (the round's structural surprise #2):**
one len-15 chain `(4,3,2,5,4,3,1,3,2,2,1,4,9,5,1)`, cost 19, final
v = 35075107 ≡ 1 mod 3^13 EXACTLY (replay-verified, not mod 3^14) —
serves t=10, 11, 12, 13 simultaneously. L2's "plateau = one chain
owns both trits" mechanism now spans FOUR trits. And it hard-stops at
13: t=14 gets nothing ≤ 24 from any chain of length ≤ 18 — the
plateau boundary is a genuine precision cliff (19 → something in
[25,32], a jump of ≥ 6).

**t=10 PLATEAU BREAK (methodological, load-bearing):** t=10 agreed at
16 across len 14,15,16,17 — four consecutive lengths — then dropped
to 15 at len 18 (len-18 witness, replay PASS). **"Two consecutive
lengths agree" (the order's own stopping rule) is REFUTED as a
certification criterion** — the in-run status line that applied it
certified t=10 as converged and was wrong within the same run's own
data. Convergence labels on this curve are henceforth
"exact-for-scope at len≤N", never "converged", until a principled
length bound exists. (The n4 script's status-scan bug — reporting
first-agreement instead of last-two-lengths — is documented in
n4b's docstring and corrected there; the CSV raw data was always
right.)

**Frozen prediction (t=11/12 stabilize at 19 by len 16; t=13/14 drop
below 31/32 and stabilize by len 17-18 — 55%): MISS (3 of 4 clauses
hit).** t=11: HIT. t=12: HIT. t=13: HIT (dropped below 31 and
stabilized — spectacularly, to the shared 19). t=14: MISS (does NOT
drop below 25 at any length ≤ 18; best remains 32). Conjunction
fails on t=14's cliff — which is itself the more informative outcome:
the prediction's implicit model (t=13/14 behave alike) is wrong; 13
is the last trit the cheap witness family reaches.

**Decisive artifacts:** `w6n/n4_length_convergence.csv` (9 rows,
static run), `w6n/n4c_tight_cap_closure.csv` (7 rows, closure),
`w6n/n4b_run_output.log` (corrected verdicts + all replays),
`w6n/n4_run_output.log`, `w6n/n4c_run_output.log`.

**Honest walls:** static run: t=13 d16 and t=14 d15 walled mid-sweep
at ~305s/4.4GB (stated, excluded from convergence series); t=14
len 15-18 in the 25..32 cost range NOT resolved (the tight cap only
certifies "nothing ≤ 24"; resolving 25..31 needs either a longer
wall-clock at cap 33 or a better instrument); t=10's true min below
len-18's 15 is open (plateau just broke; len 19+ unprobed, needs
T0 = 29+ at cap ~17 — cheap, queued for next round). Peak RSS:
4.40GB (static run), 0.98GB (closure) — both under the 8GB cap.

## W6N Final Digest

| Experiment | Verdict | Decisive number/table | Frozen prediction |
|---|---|---|---|
| N1 (floor at L+3, exhaustive m=4..7) | Floor exceptionless at triple budget on the FULL word space | 240/240 words, 2,716 non-loop chains, 0 violations | HIT (75%) |
| N2 (prefix congruence mechanism) | **LEAD FINDING: PREFIX-ALONE SUFFICES — cheap-at-k* prefix set is EMPTY on every word; min over congruence-only prefixes = g_loop(k*) exactly, 40/40** | n2_prefix_congruence_table.csv: min_prefix_cost == g_loop(k*) all rows; independent unpruned replay on 4 words; cap-stable to 320 | **MISS (65% predicted suffix-needed) — inverted, and the inversion simplifies the proof: one-point argument at k*, no forward invariant** |
| N3 (dip fingerprinting, m≤9, L+1) | Dip catalog built (9 rows); M2 continuity exact (7/7 overlap); local signature = support-adjacency (dist≤1 in 9/9), NOT suffix over-credit | strict-max reading 3/9 = 33.3% | MISS (55%) |
| N4 (length convergence, t=10..14, len≤18) | t=11/12/13 converge at 19 (13 via a 12-point one-step drop); t=14 cliffs (nothing ≤24, len≤18); t=10 breaks a width-4 plateau at len 18 (16→15) | corrected curve: [15?, 19, 19, 19, 25..32?]; four-trit plateau witness v=35075107 ≡ 1 mod 3^13 | MISS (55%) — 3/4 clauses hit, t=14 cliff kills conjunction; stopping rule itself refuted |

**Program state after W6N:** (1) The floor-point law is now
exhaustively certified at L+3 over the full {1,2}^m word space m≤7 —
AND (the round's center) it is a PREFIX-CONGRUENCE-ONLY fact: the
global lemma's anchor inequality g(k*) ≥ g_loop(k*) needs no suffix
information, no forward invariant, no whole-window coupling — the
mod-3^k* parity-forcing alone already makes cheaper-than-loop
impossible at k*. The proof obligation at the anchor point reduces to
a one-point statement about the m-step congruence game, exactly the
prefix-projected keystone shape §5b/§12d wanted. (2) The boundary
dips are support-adjacent (≤1 step from a c=1 letter, 9/9) but NOT
explained by suffix over-credit — the boundary term's mechanism
remains open, now with a sharper negative. (3) The tax curve's
plateau structure is deeper than known: one chain owns FOUR trits
(t=10..13 at cost 19), the t=14 side of that plateau is a cliff of
≥ +6, and plateau width is NOT a convergence certificate (t=10's
width-4 plateau broke at len 18). The asymptotic per-trit rate
remains open and now looks genuinely non-monotone in scope. All
witnesses across N1-N4 (2,716 + 40 + 9 + 10 witness-bearing rows)
passed independent exact-integer replay; 0 failures. Peak RSS this
round: 4.40GB; every honest wall stated above.
