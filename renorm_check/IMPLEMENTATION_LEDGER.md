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

## W6O — The One-Point Lemma at Scale (work order, Fable, 2026-07-04)

Order: W6O_LEMMA_SCALE_ORDER.md; ledger W6O-O1..O3. Context:
DERIVATION_NOTES §14 — N2's "prefix-alone-suffices" finding
(min over congruence-only k*-prefixes = g_loop(k*) exactly) was
certified on 40 sampled words, m=5..7. This round scales the
empirical base to the domain the proof actually needs: the true
word's own windows (m=2..53), both mechanical families one period
past ground-truth (m=2..2q), and ALL {1,2}^m words exhaustively to
m=12 — plus closes two of N4's tax-curve wall cells. Instrument rule
as W6K/W6L/W6M/W6N: Path C semantics (`w6k/k0_canonical_engine.py`)
+ the W6M exact-bigint ladder only; Path B retired, not used
anywhere. Work under `shell/underlock/w6o/`.

### W6O-O1 — The lemma exhaustively over the real domain (`w6o/o1_lemma_exhaustive_domain.py`) — **BREACH, LEADS THE ROUND**

**THE FROZEN PREDICTION IS FALSIFIED. The one-point lemma (N2's
"prefix congruence alone suffices," DERIVATION_NOTES §14a) BREAKS at
scale — 26 exact, independently-replayed breaches, all in the
long-window regime N2 never tested.**

Domain tested, exactly per the order: (i) true-word windows m=2..53
(52 prefixes); (ii) golden-per8 m=2..16 and sqrt2-per12 m=2..24 (38
prefixes, one full period past the 28-row ground-truth table); (iii)
ALL {1,2}^m words, m=1..12, exhaustive (8,190 words, each played as
its own k*-prefix — this alone subsumes N2's 40-word random sample).
8,280 prefixes total, branch-and-bound true minimum (N2's own
pruning argument, extended) at A_CAP=40/80 cap-margin-checked on
every prefix, 60s per-prefix wall-clock budget (never hit).

**Result: 8,254/8,280 = 99.69% hit g_loop(k*) exactly. 26 breaches,
ALL exact-replayed independently (fresh from-scratch
`engine.backward_predecessor_exact` application; `replay_ok=True` on
every one) — genuine, not an instrument artifact. Zero breaches
among all 8,190 exhaustive {1,2}^m words, m≤12 — the lemma is total
on the short-word space.** The breach is a pure LENGTH effect, not a
word-content effect:

- **True word:** clean through m=28 (min=g_loop(k*) exactly on every
  m=2..28). Breaks EXACTLY at m=29 (min=11 < L=12) and stays broken
  through m=53 (min pinned at 11, while L climbs 12→22) — a sharp,
  one-shot phase transition, not a gradual drift.
- **sqrt2-per12:** clean through m=23 (essentially 2 periods), breaks
  at m=24 exactly (min=13 < L=14) — the SAME period-boundary
  mechanism the order's own scoping note ("one full period beyond
  ground-truth, so k* can cross a period boundary") was designed to
  catch.
- **golden-per8:** no breach through m=16 (only 2 periods reached;
  the order's m=2..2q scope for q=8 does not extend far enough to
  force a golden-side breach — an honest scope note, not a
  contradiction).

**Independent reproduction (architect-grade, done in-session):** the
m=29 true-word breach and the sqrt2-per12 m=24 breach were BOTH
hand-traced step-by-step with a completely separate, freshly-written
branch-and-bound implementation (not importing or sharing any code
with the production script) — every step verified parity-legal by
hand, final max-partial-sum = 11 (true-word m=29, vs L=12) and 13
(sqrt2-per12 m=24, vs L=14) confirmed exactly. The breach mechanism,
read off the traced chains: a single moderately large exponent
(a=4..6) taken early, while running-sum slack still exists, buys a
favorable residue class that a long run of cheap (a=1) steps then
rides for the rest of the window — a detour that only pays off once
the window is long enough to harvest it. Short windows (m≤12,
exhaustively checked with zero exceptions) never have room for this;
long windows (real-system scale, m≥24-29) do.

**Frozen prediction (min = g_loop(k*) on 100%, 85%): BREACH
CONFIRMED — MISS, and the most consequential finding of the program
to date.** Per the order's own binding text, this leads over
everything else: **N2's "prefix-alone-suffices" reduction — the
proof-simplifying inversion that let the global lemma's lower bound
rest on a one-point congruence fact with no forward invariant — does
NOT hold at the scale the real system needs (m up to 53).** It holds
on 100% of the short-word space (m≤12, exhaustive) and on both
mechanical families up to roughly 2-3 periods, then fails. The
global lemma itself (D=L, loop optimality) is NOT contradicted by
this — g(k*) is a per-prefix quantity, and N1's floor-point law
(g(k*) ≥ g_loop(k*) at L+3, tested only m≤7) was never tested past
m=7 either; O1 does not re-test the WHOLE-WORD floor claim at long m,
only the prefix-congruence-alone mechanism N2 proposed for it. What
O1 falsifies specifically is the SIMPLIFICATION: the anchor
inequality is NOT purely a one-point congruence fact at real-system
scale; suffix/whole-window information re-enters exactly where L4's
super-additive coupling said it should. The proof program's
"one-point lemma" shortcut is closed; the global-window congruence
argument (§12d/L4's shape) is reinstated as necessary, not optional,
past a length threshold this round newly locates at m≈24-29.

**Decisive artifacts:** `w6o/o1_lemma_scale_domain.csv` (8,280 rows),
`w6o/o1_breaches.csv` (26 rows, all `replay_ok=True`),
`w6o/o1_run_output.log`. No honest walls (0 wallclock caps hit, 0 RSS
cap hit, peak RSS 0.032GB, wall 36.7s).

### W6O-O2 — Support-adjacency biconditional (`w6o/o2_support_adjacency_biconditional.py`)

Scope per the order: mechanical rows m≤11 both families + true-word
windows m≤11 (widening N3's mechanical-only, m≤9 scope), band L+1,
every position j=1..m tested (not just observed dip positions) to
populate the full 2×2 table.

**THE 2×2 TABLE (195 positions total, 20 dips):**

|              | support-adjacent | NOT adjacent | row-total |
|---|---|---|---|
| **dip**      | 20 | 0 | 20 |
| **NOT dip**  | 127 | 48 | 175 |
| **col-total** | 147 | 48 | 195 |

**Forward (dip ⟹ support-adjacent): 20/20 = 100%.** Every dip across
all three word sources (golden-per8, sqrt2-per12, true-word) and the
widened m≤11 scope is support-adjacent — N3's finding holds exactly,
now with true-word rows included for the first time.

**Reverse (support-adjacent ⟹ dip): 20/147 = 13.6%.** Confirmed
FALSE, decisively — adjacency is necessary but nowhere near
sufficient. Breakdown by distance: dist=0 (letter itself is a
support letter) → 4/77 = 5.2% are dips; dist=1 (support letter
immediately follows) → 16/70 = 22.9% are dips. The separating
condition is NOT visible from support-adjacency alone (both
sub-populations are overwhelmingly non-dip); no further structural
feature isolates it in this round's data (dist=1 positions are ~4.4×
more likely to be dips than dist=0, the only signal found).

**Frozen prediction (forward 70%, reverse-fails 70%): BOTH HIT.**
Forward: HIT at 100% (exceeds prediction). Reverse: HIT (13.6% ≪
100%, cleanly confirms "necessary, not sufficient"). 0 replay
failures across all 20 chains dumped.

**Decisive artifacts:** `w6o/o2_position_table.csv` (195 rows),
`w6o/o2_chain_dump.csv` (20 rows), `w6o/o2_run_output.log`. No honest
walls; wall <0.1s.

### W6O-O3 — N4 wall closures (`w6o/o3_wall_closures.py`, reusing `w6m/m3_ladder_wall_extension.py`)

Two cells targeted per the order: (i) t=14 shrink [25,32] at len
15,16, tight cap=31 (one below the best prior witness of 32 — any
value found is both a strict improvement and cap-sound); (ii) t=10
len 19,20 at tight cap=18 (around the len-18 value of 15). Both
gates (G1/G2) re-run fresh in-process before production, both PASS.

**t=14: CLOSED to exactly 31 (down from the open [25,32] interval).**
len=15 and len=16 both give exact_min=31 (sound: 31≤cap), same
witness `a_seq=(10,7,5,1,2,1,4,3,8,4,2,9,1,1,3)` (len 15) both times
— stable across the one-step length extension, replay PASS both
cells. This directly overturns n4c's cap=24 exhaustion in the other
direction from what was expected: n4c proved "nothing ≤24 exists,"
and this round's wider cap=31 finds the true value sits at the very
TOP of the previously-open interval, barely under the old best
witness of 32 (not down near 25).

**t=10: CONFIRMED STABLE at 15 through len 19 and len 20** (same
witness `a_seq=(10,1,3,3,1,2,1,2,6,2,1,4,5,1,1,4,3,1)`, len 18,
replay PASS both cells) — the value that emerged when the width-4
plateau broke at len 18 holds for two further length steps. Per the
program's own N4 lesson ("two consecutive lengths agree" was
refuted as a certificate once already), this is reported as
"stable through len 20," not "converged."

**Frozen prediction (t=14 settles ≥25, cliff height ≥6, 65%): HIT.**
31 ≥ 25; the cliff from the t=13 plateau value of 19 to t=14's 31 is
height 12 — more than double the predicted minimum height of 6.

**Decisive artifacts:** `w6o/o3_wall_closures.csv` (4 rows),
`w6o/o3_run_output.log`. No honest walls (0 wallclock/RSS caps hit
on any of the 4 cells); peak RSS 2.269GB (well under the 8GB cap,
higher than N4c's 0.98GB closure run because cap=31 vs cap=21/24
grows the live-state count substantially — expected and stated, not
a wall).

## W6O Final Digest

| Experiment | Verdict | Decisive number/table | Frozen prediction |
|---|---|---|---|
| O1 (one-point lemma at scale, 8,280 prefixes) | **BREACH — 26 exact-replayed falsifications, all at long windows (true-word m≥29, sqrt2-per12 m≥24); ZERO breaches among 8,190 exhaustive short words m≤12** | 8,254/8,280 = 99.69% hit rate; true-word min pinned at 11 for m=29..53 vs L climbing 12→22 | **MISS (85% predicted 100%) — falsified, leads the round** |
| O2 (support-adjacency biconditional, 195 positions) | Forward 100% HIT, reverse 13.6% HIT (necessary, not sufficient); dist=1 positions ~4.4× more likely to be dips than dist=0 | 2×2 table: dip∩non-adjacent = 0/20 | **BOTH HIT (70%/70%)** |
| O3 (N4 wall closures) | t=14 CLOSED exactly to 31 (was open [25,32]); t=10 confirmed stable at 15 through len 20 | t=14: 31/31 (len 15,16, same witness); t=10: 15/15 (len 19,20, same witness) | HIT (65%) — cliff height 12, more than double the predicted minimum |

**Program state after W6O:** the round's center of gravity is O1's
breach. N2's proof-simplifying claim — that the global lemma's
lower-bound anchor is a ONE-POINT congruence fact needing no suffix
or forward-window information — is FALSIFIED at real-system scale,
even though it holds with zero exceptions on the entire short-word
space (m≤12, 8,190/8,190) and on both mechanical families for
roughly 2-3 periods. The break is sharp (a one-step phase transition
at m=29 for the true word, m=24 for sqrt2-per12, both exact-replayed
by two independent implementations) and mechanistically legible
(an early moderate-exponent detour that only pays off once the
window is long enough to harvest the cheap run it buys). This
reinstates the whole-window congruence argument (§12d, L4's
super-additive coupling) as NECESSARY for the lower-bound proof, not
a fallback — the "one-point lemma" shortcut the proof program was
converging on is closed. Downstream of the breach, the program's two
smaller open questions both resolved cleanly this round: the
support-adjacency law is now a fully-tested, correctly-asymmetric
biconditional (necessary, not sufficient, exactly as N3's fingerprint
suggested), and the tax curve's t=14 cliff is now an exact number
(31, height 12 from the t=13 plateau) rather than an open interval.
All witnesses across O1-O3 (26 breach witnesses + 20 O2 chains + 4
O3 cells) passed independent exact-integer replay; 0 failures. Peak
RSS this round: 2.269GB; zero honest walls hit (every cell in O2/O3
completed inside its wall-clock and RSS budget; O1's per-prefix
budget was never triggered).

## W6P-URGENT — Does D=L survive at true-word m=29 (surgical follow-up to O1's breach)

Order (verbal, urgent): does D=L survive at the true word's own m=29
window, or does universality itself break? Work under
`shell/underlock/w6p_urgent/`, no commits, CPU only, ~8GB RSS,
independent implementation for any lead finding, every witness
exact-replayed.

**Scoping correction made before running anything (load-bearing,
stated explicitly): O1's own DFS, despite its "k*-prefix" framing, is
run with `k = len(letters_prefix)` equal to the FULL window length m
in every one of its three domains — i.e. for every m in the 26
breaches, k* (the loop-curve's own argmax) turns out to occupy
either the tail of the window (k*=m, 5/8 of this round's target
cells: true-word m=29/32/34, sqrt2 m=24) or just short of it (k*=m-1
or m-2, 3/8: true-word m=30/31/33/35) — confirmed by direct
recomputation of the loop curve for every cell (see
`p1_completion_search_results.csv` column `kstar_eq_m`). Either way,
O1 already searched the WHOLE window as one object; there is no
separate "remaining suffix beyond the breach prefix" to complete
within these windows, because D(m) (per DERIVATION_NOTES sec 2) is
itself defined as the minimax over the FULL m-window, not over a
k*-only sub-prefix with a suffix tacked on. So "search for a legal
completion" was operationalized as: **an independent, from-scratch,
FULL-window branch-and-bound true minimum, under the house's own
CANONICAL constraint (`w6k/k0_canonical_engine.py`'s `ceiling_on=True`,
i.e. g(k)>=0 at every prefix k — the "D_ceil" variant), since O1's own
breach-producing search explicitly ran D_free (ceiling-off, no such
constraint) and left D_ceil untested.** This is the correct
reduction of "does a cheap prefix have a legal completion" for cells
where k*=m (there is nothing to complete) and a strict superset check
for cells where k*<m (the full-window D_ceil search subsumes any
shorter-prefix completion question, since it already searches the
entire window exactly).

**Independence gates (both required to pass before trusting anything
downstream, both PASS):**
- Gate 0a: this round's own from-scratch `credit_true`/`backward_letters`
  construction reproduces W6O's `e1_walkers` byte-for-byte on every
  target m (24, 29-35, 53) and reproduces `underlock_words.credit_sqrt2_per12`
  on m=24.
- Gate 0b: this round's own D_ceil branch-and-bound
  (`min_full_window_d_ceil`, independent DFS, does not import
  `o1_lemma_exhaustive_domain.py`) agrees with `w6k/k0_canonical_engine.canonical_D(ceiling_on=True)`
  (the K0-gated house reference) on all 12 tiny-word test cases
  (canonical + reverse order, words 13/31/113/311/123/321).
- Extra ground-truth cross-check (not in the original order, run
  because a live discrepancy demanded it -- see below): the D_ceil
  branch-and-bound was run for EVERY m=13..28 (the gap between the
  original 12-row ground truth and this round's m=29 target) and
  agrees exactly with both `k0.canonical_D` AND the `22/53` mirror
  law `D_real(m)=floor((22m-1)/53)` (previously verified only on its
  original m=2..12 agreement zone) on all 16 additional rows,
  m=13..28, zero discrepancies. This closes the gap cleanly: D_ceil
  true-min tracks the mirror law exactly, in lockstep with L, all the
  way to m=28, then departs from BOTH exactly at m=29.

**VERDICT, per cell (all 8 target cells: the mandatory pair + all
6 extras run) — UNIVERSALITY BREAKS, not "D=L survives":**

| Cell | L (loop) | mirror-law ⌊(22m-1)/53⌋ | D_ceil true min (this round) | k*=m? |
|---|---|---|---|---|
| true-word m=29 | 12 | 12 | **11** | yes |
| true-word m=30 | 12 | 12 | **11** | no (k*=29) |
| true-word m=31 | 12 | 12 | **11** | no (k*=29) |
| true-word m=32 | 13 | 13 | **11** | yes |
| true-word m=33 | 13 | 13 | **11** | no (k*=32) |
| true-word m=34 | 14 | 14 | **11** | yes |
| true-word m=35 | 14 | 14 | **11** | no (k*=34) |
| sqrt2-per12 m=24 | 14 | -- | **13** | yes |
| (sanity) true-word m=13..28 | tracks mirror | tracks mirror | **matches L/mirror exactly, 16/16** | -- |
| (sanity) true-word m=40/45/50/53 | 16/18/20/22 | -- | **11 (pinned)** | -- |

**Every cell: an EXACT, exact-replayed, D_ceil-legal (g(k)>=0 at
every prefix — the strict canonical constraint, not the laxer
D_free O1 used) full-length admissible chain achieves max partial sum
strictly BELOW both the loop value L and the (extrapolated) mirror
law, at every one of the 8 target cells.** The true-word D_ceil
minimum is pinned at exactly 11 from m=29 through at least m=53 (spot
checked m=40,45,50,53, all still 11) while L climbs 12→22 over the
same range — the identical sharp, one-shot phase transition O1
reported under D_free, now independently reproduced under the
strictly stronger D_ceil constraint. sqrt2-per12 m=24 similarly
breaks (13 vs L=14), matching O1 exactly.

**Counterexample chain, true-word m=29, verbatim (independently
re-derived from scratch — separate DFS implementation, separate
replay, agrees with W6O's own witness digit-for-digit as an
additional cross-check, not by construction):**

Window (backward-consumption order, index 0 = nearest terminal,
absolute steps [24,53) end-anchored): `22121221212212121221212212121`

Exponent sequence: `a = (4,3,2,1,1,4,2,2,1,6,1,1,1,2,2,2,1,2,1,2,4,1,2,1,1,2,2,1,1)`

g(k) (running partial sum, k=0..29): `0,2,3,4,3,3,5,5,6,5,10,9,8,8,8,9,9,9,9,8,9,11,11,11,10,10,10,11,10,10`

max g(k) = **11**; min g(k) = 0 (never negative — D_ceil-legal
throughout, not merely D_free-legal); terminal residue rho=839
(exact-integer, replayed independently, matches W6O's own recorded
839). Parity-legality re-verified at every one of the 29 steps by a
freshly written replay function (`replay_chain` in
`p1_completion_search.py`), independent of the generating DFS's own
bookkeeping.

**Upper-bound sanity (required by the order): re-confirmed the loop
achieves exactly L on every cell** — the all-2s chain, replayed
explicitly, stays at the residue fixed point (rho=1 throughout,
2-adically the backward image of the trivial 4-2-1 cycle) and
achieves max g(k)=L exactly, on all 8 cells (own computation, not
assumed). So the verdict is cleanly D_ceil<L, not something muddier.

**Kill mechanism (read off the exact-replayed chain, same shape O1
already identified, now confirmed under the stronger constraint):**
step 9 (0-indexed; the 10th backward step) takes a=6 on a support
letter (c=1) while g is still slack (g(8)=6, six below the eventual
loop ceiling) — a moderately expensive detour (+4 over the loop's own
would-be cost at that step) that buys a favorable residue class the
chain then rides via a long run of a=1 steps (positions 10,11,18,21,
23,24,27,28 all run 1 cheaper than the loop) for the remainder of the
window, capping the running max at 11 instead of tracking the loop's
climb to 12. This is a genuine whole-window effect — no
short-prefix-alone view sees it, and no shorter window has room for
the early investment to pay off (consistent with O1's own m<=12
exhaustive zero-breach finding and the clean m=13..28 agreement this
round adds).

**Honest walls: none.** Cap-margin checks (A_CAP=40 vs 80) agreed on
every one of the 8 cells; no wallclock cap (300s/cell) or RSS cap
(8GB) was ever hit. Peak RSS this round: well under 0.1GB (node
counts topped out at ~200k for m=53); total wall time for the full
script (both gates + 8 cells + all replays): under 2 seconds.

**Conclusion: the one-point lemma's failure at m=29 (W6O-O1) is NOT
an artifact of D_free's laxer semantics — it holds, independently
re-derived and independently replayed, under the house's own
strictest canonical D_ceil convention too, and it is a break in the
actual capacity value D(m) itself (D_ceil now measurably diverges
from the loop AND from the extrapolated mirror law at exactly the
same m=29 boundary), not merely a break in a proof-simplification
shortcut about how to search for it.** This raises the stakes past
O1's own framing: O1 said the one-point *lemma* (a proof-technique
convenience) breaks at scale but explicitly did not claim D itself
breaks from L ("the global lemma... is NOT contradicted by this").
This round's D_ceil result says the actual capacity value D(29) (and
D(30..53) on the true word, D(24) on sqrt2-per12) is strictly LESS
than the loop's L — i.e., **the loop is not optimal past m=29-53 on
the true word (m=24 on sqrt2-per12): a cheaper full admissible chain
exists, exact-replayed, house-canonical-legal.** This is upstream of
and more consequential than O1's lemma-scale finding; it says the
GLOBAL claim D=L (the program's central capacity/loop-optimality
conjecture, DERIVATION_NOTES sec 14a's own "D=L follows... equality
analysis... uniqueness" chain) itself needs re-examination past
m approx 29, not just the one-point-congruence proof shortcut for it.
This does not, by itself, say anything about the ORIGINAL
Collatz-loop uniqueness question at the scales that matter for F5
(m=359) without further work extending this exact check there — it
is reported at exactly the scale tested (m=29-53 true word, m=24
sqrt2-per12), no further extrapolation claimed.

**Decisive artifacts:** `w6p_urgent/p1_completion_search.py` (script,
independent implementation), `w6p_urgent/p1_completion_search_results.csv`
(8 rows, one per cell), `w6p_urgent/p1_run_output.log` (full run
transcript, every replay shown), `w6p_urgent/sanity_depth_relation.py`
(preliminary sanity check validating the forward/backward depth
relation against `bfs_Dm`'s own certified chains on m=5,8, run first,
PASSED). No commits made, per house rules for this round.

## W6Q-REALITY — Does the W6P-URGENT m=29 counterexample survive under the CENSUS's own convention, or only the game's? (Sonnet exec, 2026-07-04)

Order (urgent, verbal): W6P-URGENT's true-word m=29 counterexample
(`a=(4,3,2,1,1,4,2,2,1,6,1,1,1,2,2,2,1,2,1,2,4,1,2,1,1,2,2,1,1)`,
claimed max partial sum 11 < loop L=12, terminal residue 839)
contradicts the archived corridor measurement `M_edge(C=11)=28`
(`shell/w6h/h5_frame_rule_check.csv`, formula `floor(53(C+1)/22)`).
Game says capacity-11 chains survive 29 steps; corridor says only 28.
Determine which world the counterexample actually lives in, with
bulletproof exact-integer verification. Work under
`shell/underlock/w6q_reality/`, no commits, CPU only, well under 8GB
RSS (actual peak ~12MB across all scripts).

**STEP 1 — Backward reconstruction + forward replay: CONFIRMED
EXACTLY, no honest walls.** Exact-integer backward reconstruction from
ρ=1 via ρ' = (2^a·ρ − 1)/3 at all 29 steps: every division exact, zero
remainder failures, reproduces the ledger's own g(k) sequence
digit-for-digit, final backward value **X = 839** (small, no lift
needed — this is a genuine, self-contained, non-degenerate real
Collatz start). Forward replay of the REAL Collatz odd-step map
(3x+1, strip all 2s, record v2) from X=839 reproduces the EXACT
expected 29-exponent sequence at every step, landing on exactly 1.
Re-confirmed via a second, differently-coded replay (bit-isolation
`y & -y` trick vs while-loop v2()) — identical. **This chain is a
real, verified, 29-step Collatz trajectory: 839 → … → 1.** No
divergence anywhere in step 1.

**STEP 2/3 — Evaluated under the CENSUS's own credit/deficit
convention (read directly from `rust/lock3_census.rs`, not
paraphrased): BREAKS DOWN COMPLETELY — the two conventions are
measuring different quantities, and this trajectory does not remotely
approach deficit 11 under the census's own rule.** `run_census`
(~line 2081) grows its tree from `Key::new(0,0)` at depth 0 and uses
`c = credit_at_step(next_depth - 1)` — i.e. credit is indexed
`k=0,1,2,…` **counting from the trajectory's OWN start**, with no
external "absolute step 53" anchor anywhere in the source. The GAME's
own convention (`w6e/engine.py`, `e1_walkers.py`,
`p1_completion_search.py`: `backward_letters(credit_fn, m,
anchor_steps=53)`) instead uses a **fixed, universal end-anchored
window** — for m=29 this is credit indices k=24..52 — regardless of
which specific integer trajectory is being played; `engine.py`'s own
docstring justifies this purely as "the actual 53-step house
convention used to build every ground-truth table" (a modeling
choice for a specific automaton measurement, not a fact about this
trajectory's own history).

Applying the census's own forward recursion `d(i) = d(i−1) + c_{i−1} −
a_{i−1}`, root-anchored at k=0 (this trajectory's natural placement —
nothing in the source assigns it 24 steps of prior history):

```
i:    0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29
d(i): 0  0  1  0  0  0  1  1  1 -1 -2 -1 -1 -1 -1 -2 -2 -2 -1  0 -5 -4 -5 -5 -7 -7 -6 -7 -8 -11
```

**census max d = 1, min d = −11** — cross-checked via a second,
independently-coded method (closed-form telescoping credit sum vs
step-by-step recursion): bit-for-bit identical. Compare to the GAME's
own g(k) (ledger's original quantity): max **g = 11**, min g = 0
(never negative — by construction, since D_ceil-legality is exactly
what the game's own search enforces). The credit LETTERS the two
conventions assign are nearly identical (28/29 positions match,
because `credit_true` is close to periodic-12 over a window this
short — only the very last position, k=52 vs k=28, differs, c=2 vs
c=1); the divergence is entirely in **which endpoint is fixed at zero
and which direction the running sum accumulates** — the game fixes
the deficit at the *terminal* (chain's end) and walks backward across
a *calendar-anchored* window; the census fixes it at the trajectory's
own *start* and walks forward with no calendar anchor at all. Under
the census's own rule, this specific trajectory spends most of the
window strongly negative and never gets within 10 of the claimed
bound of 11.

**Side finding (verified directly, not the main verdict but load-
bearing for trusting the M_edge(11)=28 comparator itself): no genuine
direct m=28-vs-m=29 residue-automaton scan was ever run for C=11.**
The only archived C=11 census run
(`data/runs/lock3_C11_N2000_residue_m1_lineage_cohorts_20260524_011032/`)
was run at `residue_mod_power=1` (memory-lean modular-compatibility-
only mode) — its own summary JSON reports `max_lifetime_of_valid1_lineage
= 28`, a lineage-lifetime PROXY at m=1, not an m=28-occupied/m=29-desert
observation. `LOCK3_PRECISION_COUNTDOWN_GRID.md` says outright: "Only
m1 has been checked for C6-C50 in this series." Only C=1..5 have
genuine exhaustive per-m countdown grids to the desert edge
(`LOCK3_BIRTH_INVARIANT_AUDIT.md`); C=11's `M_edge=28` is the FORMULA
`⌊53(C+1)/22⌋` value, cross-checked only against this proxy (which
happens to agree numerically), not against an independent from-scratch
exhaustive scan at that specific C.

**VERDICT: (b) MODEL DIVERGENCE.** The W6P-URGENT chain is a real,
independently-triple-verified Collatz trajectory (839 → 1 in 29
steps) — step 1 is airtight. But it does NOT sustain census-own
deficit ≤ 11 for 29 steps; under the census's actual root-anchored
credit convention its deficit collapses to strongly negative values
almost immediately and never approaches the claimed ceiling. **The
exact missing translation term is the anchor/calendar convention
itself**: the game's `anchor_steps=53` end-anchoring assigns credit
index k = 53−m+j to backward-position j, a convention justified only
as matching a specific 53-step automaton measurement (`M_edge(C)` per
`COLLATZ_PROOF.md`'s Theorem-1-style automaton, which IS genuinely
end-anchored at a fixed 53-step heartbeat by its own formal
definition) — but `lock3_census.rs`'s own deficit recursion, the tool
that actually grows real backward/forward trees over arbitrary depths
(250, 500, 1000, 2000 in the archived runs), indexes credit from
k=0 at ITS OWN root with no such anchor. **These are two different,
non-interchangeable measurement conventions that happen to share the
same `credit_at_step` formula but disagree on which absolute index k
applies to a given trajectory position** — the W6P-URGENT breach is a
real result about the FIRST convention (the fixed-53-step automaton
game), not evidence against the second (the census's own open-ended
tree). No claim survives that "the corridor's exhaustive scan missed
a real survivor" — under the census's own rule, applied honestly to
this trajectory's own natural (start-anchored) position, there is no
survivor to miss. This does not, by itself, prove `M_edge(C=11)=28`
is correct in the strong sense (the side finding above shows C=11
itself was never exhaustively m-swept, only formula-asserted) — it
shows specifically that the W6P-URGENT chain does not constitute a
counterexample to it.

**Honest walls: none.** All four scripts ran in well under 1 second
each; peak RSS ~12MB (vs the 8GB cap). No wallclock or RSS caps
approached. The one open scope note: the "sqrt2-m24 breach" checked
for per the order is `sqrt2-per12 m=24` from the same W6P-URGENT
round — this is a fully rational, period-12 MECHANICAL toy word
(`credit_sqrt2_per12(k) = ⌊17(k+1)/12⌋ − ⌊17k/12⌋`), not an
irrational-rotation toy and not itself a claim about any specific
integer trajectory; it was not re-examined here since the task at
hand is specifically about the true-word m=29 chain's status as a
REAL Collatz counterexample, and the sqrt2-per12 family was never
presented as one (it is a synthetic word used for testing the game's
combinatorics, with the same anchor-convention caveat applying to it
if anyone later tries to read it as a real-trajectory claim).

**Decisive artifacts:** `w6q_reality/q1_backward_forward_replay.py` +
`q1_backward_trace.json` + `q1_output.log` (step 1a, backward
reconstruction), `w6q_reality/q2_forward_replay_real_collatz.py` +
`q2_output.log` (step 1b, forward Collatz replay, alternate bit-trick
cross-check included in `q4`), `w6q_reality/q3_census_deficit_eval.py`
+ `q3_step_by_step_table.json` + `q3_output.log` (step 2, the
game-vs-census comparison table), `w6q_reality/q4_independent_rederivation.py`
(step 3, fully independent second code path for both the replay and
the deficit recursion), `w6q_reality/q5_final_condensed_table.txt`
(condensed human-readable summary of all of the above). No commits
made, per house rules.

## LOCK4-B1 — Bridge Economics, Measured Exactly (work order, Fable, 2026-07-04; executor: Sonnet agent)

Scope: LOCK4_BRIDGE_NOTES.md's Bridge Obstruction inequality for the
first bridge (the 306-letter q=53 -> m=359 gap). House rules as W6:
frozen gates in the order; exact replay; independent cross-checks;
canonical instruments (w6e/engine.py primitives, w6e/e1_walkers.py
credit_true convention); ~8GB RSS; honest walls; CPU only; no commits.
Work under `shell/bridge/b1/`.

### LOCK4-B1.0 — Audit + reconciliation + spot-reproduction (`b1/b0_audit_reconcile.py`)

**Instrument:** fresh, independent simulation of the true (odd-only)
Collatz map (does NOT import `src/collatz_experimental_data/exact.py`
— the point is an independent spot-check, not a re-run), tracking
exact deficit `d_k = floor(k*alpha) - A_k` via the bit_length trick
(no floating point in the deficit computation), and an independent
re-derivation of the [1,1] word's affine ghost.

**Vocabulary reconciliation (the round's B1.0 job):** LOCK4_RESULTS.md's
"reserve" (from `src/collatz_experimental_data/exact.py`'s
`simulate_orbit`/`reserve_profile`) is reported as `d_before`/`d_after`
directly — the deficit itself, with NO fixed corridor C anywhere in its
formula. This is IDENTICAL to LOCK4_BRIDGE_NOTES.md's deficit `d`, NOT
to the bridge notes' `RESERVE := C - d` (headroom below a *chosen*
ceiling). The old module's "max_reserve=23" means the orbit's deficit
`d_k` peaked at 23 above the `floor(k*alpha)` baseline — equivalently,
pinning the tightest corridor `C=23` that contains this orbit's whole
prefix, `RESERVE = C - d` is exactly 0 at that peak and >= 0 throughout
by construction (verified directly, not asserted: `RESERVE_min_over_
prefix_under_pinned_C = 0`, `RESERVE_at_time_of_max_deficit = 0`, both
computed, both correct). This lineage is the empirical "jump is
impossible" evidence (May 21 exhaustive scan through 250M: max reserve
23, never 24) upgrading into this round's deterministic bridge DPs.

**Spot-reproduction (2 concrete numbers -> 8/8 fields, fresh code):**
orbit 80049391 (max-reserve-23 orbit): max_reserve=23 @ step 72,
crossing_time=153, num_growth_steps=53 — ALL MATCH. Second independent
bankruptcy crossing, orbit 120080895: max_reserve=23 @ step 65,
crossing_time=128, num_growth_steps=48 — ALL MATCH. 8/8 fields exact,
0 mismatches.

**[1,1] / ghost -1 identity with the game's cheap ray (DERIVATION_NOTES
sec 8b):** word [1,1] gives S^2(x) = (9x+5)/4 (re-derived independently
via the affine-word recursion B_{n+1}=3B_n+2^{A_n}), ghost = -B/D =
-5/(9-4) = -1 EXACTLY. Cross-checked two ways: (a) direct algebra on
the word; (b) S(-1) = (3*(-1)+1)/2 = -1, confirming -1 is the unique
fixed point of the real map S(x)=(3x+1)/2 (the a=1-forever ray). This
IS exactly rho=-1 in the residue game (DERIVATION_NOTES 8b's "cheap
ray": a=1 forever, cost 1/step, the -1-loop shadow) — the May scan's
repeated growth-segment word [1,1] is the SAME object as the game's
cheap ray, not merely analogous. Identity confirmed: `True`.

**Verdict: PASS (8/8 spot-reproduced numbers match; vocabulary
reconciliation explicit and verified; ghost/cheap-ray identity
confirmed both algebraically and by direct fixed-point check).**

**Artifact-level corroboration (additional, beyond the fresh-code
spot-check above):** the raw source CSVs referenced by LOCK4_RESULTS.md
still exist and directly corroborate the claimed aggregate counts —
`data/runs/scan_limit250000000_D24_*.csv` is EMPTY (0 data rows,
confirming "0 starts reached reserve 24" through 250M exhaustively);
`data/runs/scan_limit250000000_D23_*.csv` has exactly 6 data rows
(confirming "6 hits, max reserve 23"), including the two rows
(80049391, 120080895) whose fields match the fresh-code reproduction
above verbatim. The full 250M-integer exhaustive scan itself was NOT
re-run this round (infeasible in scope; B1.0's mandate was audit +
spot-reproduction, not re-execution of the whole scan) — this is
inherited empirical evidence, corroborated at the artifact level and
spot-verified at the individual-orbit level, not independently
re-derived at the full-scan level.

**Decisive artifacts:** `b1/b0_audit_reconcile.py`, `b1/b0_audit_results.json`,
`b1/b0_run_output.log`, plus the pre-existing
`data/runs/scan_limit250000000_D23_20260521T190952Z.csv` (7 lines) and
`data/runs/scan_limit250000000_D24_20260521T190900Z.csv` (0 lines, empty)
cross-checked as artifact corroboration. Wall <0.01s, peak RSS negligible.

**Honest walls:** the full 250M exhaustive scan was not re-executed
(inherited, artifact-corroborated, not re-derived from scratch).

### LOCK4-B1.1 — Phase-relaxed climb cap (`b1/b1_phase_relaxed_climb.py`)

**Instrument:** true-word credits via `credit_true` (exact bit_length
convention, matching `w6e/e1_walkers.py` verbatim). Phase-relaxed rule
(the order's own definition, letter-type only, no residue tracking):
support (c=1) forces a>=2, drop (c=2) allows a=1. Since each step is
independent under this rule (no coupling across steps — no residue
state to carry), the per-step-maximizing choice a=a_min at every step
gives the closed form `climb(k) = k - 2*supports(k)`, algebraically
IDENTICAL to the order's suggested form `Sigma(c) - k - supports(k)`
(shown symbolically: Sigma(c) = 2k - supports(k) by telescoping, so
the two forms collapse to the same expression — not a coincidence,
confirmed by direct substitution in the script docstring).

**Validation:** independent per-window brute-force DP (explicit scan
over `a` in `[a_min, a_min+a_cap]`, MAXIMIZING c-a, margin-checked
a_cap=6 vs 20) on 20 windows k=1..700 (Fibonacci-ish spread plus
k=306): **20/20 MATCH**, margin check OK on all 20 — closed form
validated, not merely asserted.

**RESULT:** value at k=306 = **50** (supports=128, drops=178) — inside
10% of the frozen ~52 estimate, and strictly < 149. Floor-form law
test: `climb(k)` vs `floor(k*(2*alpha-3))` (rate 0.169925...) over the
full k=1..700 curve — **max |deviation| = 1** (essentially exact floor
law, not merely "roughly linear").

**Frozen prediction 1 (value at k=306 ~=52 and <149, 70%): HIT**
(actual 50, within 10% of 52, and 50 < 149).
**Frozen prediction 2 (floor-form law in k, 60%): HIT** (max deviation
1 across 700 points — as clean a floor law as the program has
measured anywhere).

**Decisive artifacts:** `b1/b1_phase_relaxed_climb.py`,
`b1/b1_phase_relaxed_curve.csv` (700 rows, k=1..700),
`b1/b1_run_output.log`. Wall 0.36s, peak RSS negligible.

**Honest walls:** none.

## W6R — Root-Anchored Re-Grounding (Sonnet exec, 2026-07-05)

Order (frozen prompt, no separate order file). Context: W6Q-REALITY
established the census's own convention (rust/lock3_census.rs) scores
deficit ROOT-anchored (credit_at_step(k), k=0 at the trajectory's own
start, no external calendar anchor) and CEILING-ON (deficit clamped to
[0,C] — `deficit_branch_capacity`/`max_deficit_for_c`, lines 1251-1265,
c>=0 required; `Key::new` panics on negative deficit, lines 268-271),
whereas the GAME's entire proof program (W6E-W6Q) used an END-anchored
window (`anchor_steps=53`, w6e/engine.py). DERIVATION_NOTES sec 15
registered the architect's prediction that re-grounding the whole
program root-anchored would RESTORE universality/uniqueness/floor at
all m (70%). This round tests that directly. Work under
`shell/underlock/w6r/`, no commits, CPU only, peak RSS ~0.03GB across
every script (well under the 8GB cap), no wallclock cap ever hit.

**Shared instrument (`w6r/root_anchor.py`):** root-anchoring is a
SURGICAL change to the existing, already-validated machinery —
`root_anchored_word(credit_fn, m)` = `backward_letters(credit_fn, m,
anchor_steps=m)` (i.e. the window is [0,m) in the census's own
indexing, instead of the game's fixed [53-m,53)) — verified against a
fresh, independent forward recursion built directly from
`credit_at_step`'s own definition (`verify_root_anchor_equivalence`,
PASS) and against the g/d sign-duality fact stated in
w6q_reality/q3 (`verify_g_d_duality`, PASS, re-derived independently
here). `w6r/r0_validation_gate.py` (binding house rule: asymmetric/
convention-sensitive validation rows FIRST) ran two required rows
before anything else: Row A (root vs end anchoring genuinely
DIFFERENT at true-word m=29 — root word != end word, L_end=12 matches
the archived ledger value — PASS); Row B (this round's OWN fresh code,
two independently-coded methods — step recursion and closed-form
telescoping credit sum — reproduce W6Q-REALITY's own reported numbers
on the 839 chain EXACTLY: max d=1, min d=-11, digit-for-digit matching
the ledger's own table — PASS). Both rows PASS; round proceeded.

### W6R-R1 — Does the m=29 break vanish under the convention of record? (`w6r/r1_root_break_check.py`) — **LEADS THE ROUND, MISS**

Ceiling variant stated explicitly per the order: D_ceil
(`canonical_D(ceiling_on=True)`, g(k)>=0 at every prefix), matching
rust/lock3_census.rs's own deficit recursion at lines 2080-2081
(`credit_at_step(next_depth-1)`, root-anchored at depth 0 per line
2049) combined with the ceiling-on branch capacity at lines 1251-1265
and 268-271 — the SAME variant W6P-URGENT itself used for its
from-scratch D_ceil search.

**THE FROZEN PREDICTION IS FALSIFIED: universality D_root=L_root does
NOT hold at all m under root anchoring. It holds cleanly through
m=24..28 (5/5 clean match, D_root==L_root exactly) and BREAKS at
m=29, staying broken through m=40 (12/17 total MISS, only 5/17 match).**
At m=29, D_root(ceil)=12 while L_root=13 (a strict miss); the break
value pins in a narrow 11-12 band while L_root climbs 13→17 over
m=29..40 — the SAME qualitative shape as the end-anchored break W6O/
W6P found (a cheap "detour" chain beating the loop), just with
different numbers under the corrected anchoring. Every cell's A_CAP
margin check (40 vs 80) passed; a witness was recovered and
independently replayed for all 17 cells (all PASS, 0 replay failures).
`root_anchor.canonical_D` fed the census's own D_ceil semantics with
NO other change to the validated backward-DFS machinery.

**Independent re-derivation (house rule, this is the lead finding):**
`w6r/r1b_independent_rederivation.py`, a COMPLETELY FRESH
implementation (own `credit_true_fresh`, own parity/predecessor
functions, own branch-and-bound DFS, no shared imports with
root_anchor.py or k0_canonical_engine.py) re-derived m=24,28,29,30,31,32
from scratch and agrees EXACTLY with the production run on every cell,
including the m=29 breach (D=12, L=13) and its continuation through
m=32 — 6/6 agreement, 0 discrepancies.

**Decisive artifacts:** `w6r/r1_root_break_table.csv` (17 rows, m=24..40),
`w6r/r1_root_break_check.log`, `w6r/r1b_independent_rederivation.py` +
`.log` (independent re-derivation, 6/6 agreement). No honest walls
(margin checks all OK, every witness recovered and replayed, peak RSS
0.027GB, wall 2.0s).

**Frozen prediction (universality holds at all m under root anchoring,
70%): MISS.** The break is real under BOTH anchoring conventions —
root-anchoring does not restore universality. It relocates the exact
numbers (D_root pins near 11-12 vs the end-anchored D pinning at 11;
L_root climbs to 17 by m=40 vs L_end's climb to different values) but
the qualitative phenomenon — a non-loop chain beating the loop past
m≈29 — survives the correction to the convention of record. This is
the round's central finding: the m=29 anomaly is not an artifact of
the end-anchoring bug: it is a genuine fact about the m-window
minimax game at long m, under either convention.

### W6R-R2 — Loop uniqueness under the convention of record (`w6r/r2_uniqueness_census.py`) — **HIT**

Instrument note (honest wall reported): the order's natural reuse
target, `w6f/f1_engine_ext.py`'s exhaustive (d,r) residue-space
enumerator, scales O(3^m) regardless of chain rarity and timed out
(>4min) at m=15 in this round's first attempt (m=14 alone took ~21s).
PRIMARY instrument became a lighter-weight backward-DFS witness
collector reusing `canonical_D`'s own sound pruning (collects every
a-sequence hitting the known-optimal D_target instead of only
returning the scalar), which scales to m=16 in well under a second —
validated by a 3-way independence gate (this lightweight method vs
`compute_D_and_optimal_set`'s exhaustive residue-BFS vs
`brute_force_all_chains`'s from-scratch residue-iteration, the latter
capped at m<=6 per its own module docstring's validated scope and a
measured >2min wall past that) before trusting the extended range.

**Independence gate: PASS, all three methods agree exactly on every
tested cell (true-word + both mechanical families, m=4..11, brute
force through m=6).** Production census (root-anchored, m=4..16, all
3 word families, both mechanical at their own root phase): **39/39
words have a UNIQUE optimal chain, and it is the all-2s loop, exactly
matching D_root==L_root at every one of these (short) m** — fully
consistent with R1's finding that the short-word regime (m<=~28) is
clean under root anchoring too.

**Decisive artifacts:** `w6r/r2_uniqueness_table.csv` (39 rows),
`w6r/r2_uniqueness_census.log`. No honest walls in the production run
(every margin check OK, no enumeration cap hit, independence gate
passed). Peak RSS 0.117GB, wall 9.1s.

**Frozen prediction (loop strictly unique everywhere, 70%): HIT.**
39/39.

### W6R-R3 — Floor-point + one-point structure, root-anchored (`w6r/r3_floor_onepoint.py`) — **MISS**

Reused N2's own `min_prefix_cost_and_argmin` branch-and-bound
(congruence-only, true minimum over admissible length-k* prefixes,
margin-checked 40 vs 80) unmodified in logic, fed root-anchored words.
Tested m=4..12 + {13,16,20,24,28} + 29..35 mandatory, all 3 word
families (63 rows total).

**Floor law and one-point property hold cleanly through the short/
mid range (all m<=28 for true-word and golden-per8; m<=20 for
sqrt2-per12) but BREAK starting at m=29 for the true word (min
prefix cost=12 < g_loop(k*)=13, a genuine floor violation), m=30 for
golden-per8, and even earlier — m=24 — for sqrt2-per12.** Overall
41/63 hold, 22/63 violate — every violation independently replayed
(0 replay failures) and margin-checked (0 margin failures). The
violations are exactly the R1 breach re-appearing at the per-prefix
level (same mechanism: a cheaper congruence-only prefix exists at k*
than the loop achieves), now shown to set in EARLIER for the
mechanical families (sqrt2-per12 breaks at m=24, matching its own
period-boundary sensitivity noted back in W6O-O1) than for the true
word (m=29).

**Independent re-derivation** of the true-word m=29 cell (fresh
credit function, fresh parity/predecessor code, fresh DFS) reproduces
min=12 < L=13 exactly.

**Decisive artifacts:** `w6r/r3_floor_onepoint_table.csv` (63 rows),
`w6r/r3_floor_onepoint.log`. No honest walls (all margin checks OK,
all replays PASS). Peak RSS 0.026GB, wall 2.4s.

**Frozen prediction (floor law + one-point property hold at every m
tested including 29..35, 55%): MISS.** The order itself flagged this
as the most likely prediction to fail ("the shortcut may genuinely be
small-m-only even in the right frame") — confirmed: root-anchoring
does not extend the shortcut's scope past where W6O/N1/N2 already
found it failing under end-anchoring; if anything the mechanical
families' break points are EARLIER under root-anchoring (sqrt2-per12
at m=24) than the true word's m=29.

### W6R-R4 — Frame-rule reconciliation (`w6r/r4_frame_phase_check.py`) — **MISS**

Data source: the SAME archived `data/runs/lock3_C{C}_N2000_residue_m1_
lineage_cohorts_*/lock3_census_C{C}.csv` files w6h/h5 used (not
regenerated). Lineage-death semantics read directly from
rust/lock3_census.rs (lines ~2625-2657): a lineage's recorded lifetime
at death equals `next_depth - birth_depth`; the CSV's own
`max_valid1_lineage_lifetime` column is a monotone-nondecreasing
running max, so the FIRST depth at which it reaches its final (row-(-1))
value is exactly the death-record depth of the extremal lineage.
Extracted (`extract_window`): birth_depth, last_alive_depth (=
death_record_depth - 1, the "while-alive" convention giving lifetime =
d - birth + 1 = M_edge exactly), for C=3..10.

**No fixed phase relationship found.** Under either window-end
convention tested (last_alive_depth or the raw death-record depth),
only 2/8 archived C values (C=4, C=9) land exactly on the frame rule's
own expected phase (52 mod 53); the other 6/8 sit at varying offsets
(offsets from expected phase: [19, 0, 24, 31, 36, 36, 0, 48] for the
last_alive convention) — no constant shift reconciles them. A
secondary check (residue mod 22, the corridor's other natural modulus)
was also tried as a bonus diagnostic and showed no structure either.
Honest caveat (stated, not hidden): C=3..10 all sit BELOW the frame
rule's own first 53-boundary crossing (C=21, per h5's own table,
where run(C) first jumps from 53 to 106) — this round's C-range may
simply be too small to see whatever alignment mechanism (if any)
operates once the window genuinely wraps past 53; that is a scope
note for a follow-up, not a rescue of this round's own null result.

**Decisive artifacts:** `w6r/r4_frame_phase_table.csv` (8 rows),
`w6r/r4_frame_phase_check.log`. No honest walls (all 8 archived C
values found and read; the h5 archive itself was already cross-
validated CSV-vs-JSON in that round). Wall <1s.

**Frozen prediction (extremal windows sit at the frame-rule phase or a
fixed offset from it, 60%): MISS.** H5's own 48/48 VALUE match
(M_edge(C) == m_irr(C) exactly) stands completely undisturbed by this
result — R4 only shows that the mechanism behind that value-match is
NOT simple frame-phase-alignment of the extremal window against the
53-grid, at least not in the C=3..10 regime tested. H5's fact remains
correct and receipt-exact; its EXPLANATION via sec 15a's phase-
alignment hypothesis is what this round refutes.

## W6R Final Digest

| Experiment | Verdict | Decisive number/table | Frozen prediction |
|---|---|---|---|
| **R1 (m=29 break under root anchoring, LEADS)** | **MISS — universality does NOT hold; breaks exactly at m=29, same as end-anchored, independently re-derived 6/6** | 5/17 match (m=24..28 clean, m=29..40 all miss); m=29: D_root=12 < L_root=13 | **MISS (70% predicted universality holds at all m)** |
| R2 (loop uniqueness, m=4..16, 3 families) | **HIT — loop strictly unique everywhere tested** | 39/39 unique all-2s optimal chain; 3-way independence gate PASS | **HIT (70%)** |
| R3 (floor/one-point, m=4..35 sampled) | **MISS — breaks at m=29 (true word), m=30 (golden), m=24 (sqrt2)** | 41/63 hold; all violations replayed, 0 failures | **MISS (55% predicted holds through 29..35)** |
| R4 (frame-rule phase reconciliation, C=3..10) | **MISS — no fixed phase found under either window-end convention** | 2/8 exact alignment; offsets vary, no constant shift | **MISS (60%)** |

**Program state after W6R:** the architect's root-anchoring hypothesis
(DERIVATION_NOTES sec 15, "all three [universality, uniqueness,
floor] HOLD at all m under root-anchoring — 70%") is **only 1/3
confirmed**. Loop uniqueness (R2) transfers cleanly to the corrected
convention. Universality (R1, the round's lead question) and the
floor/one-point shortcut (R3) do NOT — both break at essentially the
SAME location (m≈24-29) under root-anchoring as they did under the
end-anchored game, independently re-derived and replayed at every
reported cell. **The m=29 phenomenon is therefore not a W6Q-style
convention artifact — root-anchoring was a genuine correction (R0's
validation gate shows the two conventions are materially different
objects, confirmed against W6Q-REALITY's own numbers exactly) but it
does not make the anomaly disappear.** R4 additionally shows the
corridor-side H5 frame-rule fact (M_edge=m_irr, 48/48, still standing,
untouched) is not explained by simple extremal-window phase-alignment
in the C=3..10 range — its mechanism remains open. Net effect: the
proof program's "one-point lemma" shortcut (N2, closed by W6O) and the
global universality claim (W6P/W6Q) both stay closed/suspended past
m≈29 under the corrected convention too; the global-window congruence
argument (DERIVATION_NOTES sec 12d) remains the necessary route, now
confirmed necessary under BOTH anchoring conventions rather than only
the (mistaken) end-anchored one. Uniqueness (R2) is the one piece of
the trinity that generalizes cleanly and can be built on directly.
Peak RSS across the whole round: ~0.12GB (R2's production run); no
wallclock or RSS cap ever approached; zero commits made.

## W6S-CENSUS — Locating the game-vs-census divergence, following the W6Q method exactly (Sonnet exec, 2026-07-05)

Order: apply W6Q-REALITY's own method (backward-reconstruct + forward-
replay a witness chain as genuine integers, then score it under the
census's LITERAL `rust/lock3_census.rs` semantics, read directly, not
paraphrased or reused-via-`k0_canonical_engine.py`) to W6R's m=29
root-anchored witness, to finally locate where the game and the census
part ways — the open question that has survived W6Q and W6R. Work
under `shell/underlock/w6s_census/`, no commits, CPU only, peak RSS
negligible (<50MB across all three scripts, well under the 8GB cap),
wall time <1s per script.

**STEP 1 — Replay: CONFIRMED EXACTLY, no honest walls
(`s1_replay_witness.py`).** W6R's m=29 witness a-sequence
(`4,3,2,1,1,4,2,2,1,6,1,1,1,2,2,2,1,2,1,2,4,1,2,1,1,2,2,1,1`, identical
to W6P-URGENT/W6Q-REALITY's own 839 chain — confirmed byte-for-byte
against `w6r/r1_root_break_table.csv` row m=29) was independently
re-reconstructed backward from ρ=1 (`ρ'=(2^a·ρ-1)/3`, all 29 divisions
exact) and forward-replayed as a real Collatz trajectory
(839→1259→…→1, 29 odd-steps). Every one of the 29 `v2(3x+1)` values
matches the claimed exponent exactly (e.g. step 0: x=839, 3x+1=2518,
v2=1; step 8: x=2693, 3x+1=8080, v2=4; step 28: x=5, 3x+1=16, v2=4→1).
This is a third independent confirmation (after W6Q's and W6R's own)
that 839→1 in exactly 29 steps with this exact exponent sequence is
real.

**STEP 2 — Literal census scoring (`s2_census_literal_score.py`): the
census's actual `.rs` two-sided ceiling rule, never previously
re-implemented from the literal source (W6R used
`k0_canonical_engine.canonical_D`, whose OWN docstring explicitly
states "no separate fixed ceiling C; ceiling-on is exactly the
g(k)>=0 prefix constraint, nothing else" — this claim is checked here
against the `.rs` source directly instead of taken on faith).** Read
`rust/lock3_census.rs` directly: `credit_at_step` (lines 1247-1249,
identical formula to the game's `credit_true`); growth loop
(`run_census` lines 2080-2081 / `run_census_lean` lines 2417-2418,
`c = credit_at_step(next_depth-1)`, root `Key::new(0,0)` at depth 0,
lines 2049/2395 — confirms W6Q/W6R's root-anchored k=0..m-1 indexing
is correct); and the deficit transition itself (`run_census` lines
2093-2103 / `run_census_lean` lines 2461-2472): `for d_next in
0..=max_deficit { let a = key.deficit() + c - d_next; if a < 1 {
continue; } }`, where `max_deficit = config.c` (the CLI `--C` capacity
ceiling, required non-negative, line 751) — i.e. **a child state is
materialized ONLY if `d_next` lands in `[0, config.c]` AND `a>=1`; a
proposed `d_next` outside `[0,C]` produces NO state at all** (`Key::new`,
lines 268-273, panics on negative deficit; `run_census_lean`'s own
inline comments, lines ~2432-2436, explicitly name `d_next > C` a
"breach upward" / exit event). This IS a genuine hard two-sided wall,
confirming `canonical_D`'s docstring claim ("no upper ceiling, only
g>=0") describes a DIFFERENT, laxer rule than the literal `.rs` code.

Scoring the verified 839/m=29 chain under this literal rule (C=11 and
C=12 both tested): **the trajectory is illegal from step i=8 onward**
(`d_prev=1, c_k=2, a=4 → d_next=-1 < 0`) — it goes bankrupt on the
LOWER bound, 20 steps before the window even ends, never once
approaching the upper ceiling (max d = 1 across the whole run). This
is the exact same qualitative result W6Q already found for its own
839-chain-vs-census-own-d comparison (max d=1, min d=-11) — this
round's contribution is confirming it against the LITERAL two-sided
Rust rule (not just the lower-bound-only Python rule), and showing the
upper-ceiling term is not even the operative one here — the lower wall
already kills it.

**STEP 3 — Reconciliation and the actual mechanism
(`s3_reconciliation.py`): DISAGREE, and the mechanism is NOT
"m=29-inert-below/active-at-29"; it is a permanent, uniform structural
gap present at every m tested (20..29), which is itself the finding.**
Per the order's Branch B, the expected shape was "name a census rule
that is inert for m=24..28 and switches on at m=29." That shape does
NOT fit what was found: repeating the exact same game-g-vs-
census-literal-d comparison on the all-2s loop chain (W6R-R2's
independently-verified unique optimal chain for m≤28) at m=20..29
shows **`max(census-literal d)` stays at 0 and `min(census-literal d)`
goes uniformly, monotonically negative (−9 at m=20 down to −13 at
m=29, roughly −m/2) at EVERY m in this range** — there is no m=29
transition in this comparison at all. The game's own `g` (backward-
terminal, W6R's `D_root`) matches the loop's own `L_root` cleanly
through m=28 and breaks at m=29 — but that is an internal, same-
convention comparison (game vs game, both backward-terminal), never a
comparison against the census's literal forward-root `d`. **The
census-literal-vs-game mismatch was never "inert" at m=24..28; it
simply was never the thing W6R's R1 was testing there.**

**Named mechanism: three non-equivalent anchor/boundary conventions,
not one calendar offset.**
1. **Game's g** (DERIVATION_NOTES sec 2, `δ_k = δ_T −
   Σ_{j≤k}(a_j−c_j)`; `k0_canonical_engine.canonical_D`'s DFS starts
   `dfs(0, rho=1, running=0, ...)`): a **backward, TERMINAL-anchored**
   minimax — "how much capacity must be banked in advance for an
   m-step chain ENDING at ρ=1 to never go bankrupt walking backward to
   that terminal." The terminal condition ρ=1 is baked into the DFS's
   own root.
2. **Census's own literal d** (`rust/lock3_census.rs`, `Key::new(0,0)`
   at depth 0, forward growth loop): a **forward, ROOT-anchored**
   recursion with NO constraint that the tree terminate at ρ=1 after
   any particular depth — "valid1" (residue-compatible with terminal)
   is tracked as an emergent event wherever it happens to occur in the
   tree.
3. **M_edge(C)** (the archived comparator, `max_valid1_lineage_lifetime`,
   defined at `rust/lock3_census.rs` lines 2632-2637 as `next_depth −
   birth_depth`): a **forward, BIRTH-anchored** lifetime — relative to
   whichever depth a lineage happens to enter valid1 status, not depth
   0 and not the terminal.
W6Q found (1) vs (2) diverge on the 839 chain. W6R's "root-anchoring
fix" changed WHICH credit letters convention (1) pulls into its
window (re-indexed from k=24..52 to k=0..28) but never changed
convention (1) into (2) or (3) — `D_root`'s own DFS still starts at
ρ=1 and walks backward. That is why W6R's fix relocated the break's
NUMBERS (D_root=12 vs L_root=13, instead of D_end=11 vs the
M_edge-implied L_end=12) without resolving the contradiction: it
corrected the calendar offset within convention (1) but never touched
the boundary-direction mismatch between (1) and (2)/(3), which is
uniform across every m, not something that switches on at 29.

**Verdict: DISAGREE (confirmed), but NOT in the shape the order's
Branch B anticipated.** No single named `.rs` line is "inert through
m=28 and active at m=29" — the census's literal two-sided ceiling
rule (step 2 finding) is real and load-bearing (it IS stricter than
`canonical_D`'s lower-bound-only rule), but it is not what explains
the m=29-specific break, because the game-vs-census-literal
comparison never agreed at any m in the first place (step 3). The
original W6P-URGENT/W6H contradiction (game's D_ceil=11-survives-29
vs archived `M_edge(11)=28`) is therefore not resolvable by finding a
missing translation TERM between the two conventions — they are
different conventions from the ground up (backward/terminal vs
forward/root vs forward/birth), and W6Q's own side-finding stands
independently: `M_edge(11)=28` itself was never produced by a genuine
m=28-vs-m=29 exhaustive scan at C=11 (only the `⌊53(C+1)/22⌋` formula,
cross-checked against a residue_mod_power=1 lineage-lifetime proxy).
**Neither side of the original contradiction is a verified apples-to-
apples measurement of the same object; both W6Q's convention-mismatch
finding and this round's uniform-structural-gap finding stand
together as the located root cause: the "contradiction" was comparing
three different formal quantities that happen to share the same
`credit_at_step` formula, not a bug in any one of them.**

**Honest walls:** none in the computational sense (every script ran in
well under a second, all replays exact, no RSS/wall pressure) — but
the INTERPRETIVE wall from W1/W2 (F5 status OPEN, telescoping blocked
on W2's tractability wall) is unchanged and out of this round's scope.
This round narrows *why* game and census disagree structurally; it
does not newly resolve F5 or produce a corrected capacity-lemma
statement — that remains future work (candidate next step: define
D(m) and the census's tracked corridor as the SAME boundary-value
problem, e.g. by requiring the census tree to be conditioned on
reaching valid1 at exactly depth m, rather than treating valid1-birth
as emergent — untried here, out of scope for this round's order).

**Decisive artifacts:** `shell/underlock/w6s_census/s1_replay_witness.py`
(+ `.log`, `s1_replay_trace.json`), `s2_census_literal_score.py` (+
`.log`, `s2_census_literal_table.json`), `s3_reconciliation.py` (+
`.log`, `s3_uniform_mismatch_table.json`). All under
`shell/underlock/w6s_census/`; `shell/bridge/` untouched; zero commits.

### LOCK4-B1.2 — Residue-legal max climb (`b1/b2_residue_legal_max_climb.py`)

**Instrument:** exhaustive branch-and-bound DFS mirroring
`w6k/k0_canonical_engine.canonical_D`'s exact residue primitives
(`w6e/engine.py`'s `forced_parity_for_backward_step`,
`backward_predecessor_exact`, imported not reimplemented), objective
flipped to MAXIMIZE Sigma(c-a) (usable reserve, per LOCK4_BRIDGE_NOTES
sec 1) instead of minimizing max-prefix. Admissible pruning bound,
18 live launch classes mod 27 (the 9 class-0-mod-3 residues mod 27 are
immediately dead, excluded).

**BUG CAUGHT AND FIXED BY THE PRUNING-SOUNDNESS GATE (load-bearing,
not glossed over):** the first version of this script used B1.1's
phase-relaxed climb cap (support c=1 forces a>=2 blanket, regardless
of actual residue) as the admissible upper bound for pruning. The
gate (`gate_pruning_soundness`: pruned DFS vs unpruned brute force on
m<=12 cells) caught a real mismatch (m=10, launch class 23: pruned=-7,
brute=-6) BEFORE any production numbers were trusted. Root cause:
B1.1's rule and the true residue-legal rule are INCOMPARABLE in
general — which parity is legal at a support/drop letter is decided
by the actual residue class, not the letter type; a witness was found
where a support letter's residue happened to permit a=1 (beating
B1.1's blanket a>=2 assumption there). B1.1's cap is unsound for this
game and was replaced with a genuinely admissible (looser, but
provably valid) per-step bound `c-1` (the best possible (c-a_min)
across BOTH possible parity classes). Gate PASSES with the corrected
bound (15/15 (m,rho0) cells). This is reported explicitly because it
means EVERY earlier fast run under the old bound was WRONG and
discarded — none of its numbers appear below.

**HONEST WALL (measured after the fix, not assumed): only k=53
completes exactly.** With the corrected (sound but looser) bound,
m=53 takes ~2.4-11s/launch (a_cap=4 vs 6 margin-checked stable, 18/18
launches complete in 56.7s total). m=100/200/306 do NOT complete
within a 40s/launch budget (confirmed at 60-110s/launch in dev probes
too — genuinely exponential, not a tuning artifact); these three
scopes are reported as an HONEST LOWER-BOUND BRACKET (best value
found within budget — a real, complete, exact-replayable witness in
every case, never fabricated) alongside the sound admissible upper
bound.

**RESULTS (worst-launch = max over the 18 live classes mod 27):**

| k | usable reserve (worst launch) | status | admissible upper bound | gap |
|---:|---:|---|---:|---:|
| 53 | **-6** (launch class 20) | EXACT | 31 | 119.4% of cap |
| 100 | -25 (launch class 2) | LOWER BOUND | 58 | 143.1% of cap |
| 200 | -70 (launch class 2) | LOWER BOUND | 116 | 160.3% of cap |
| 306 | -111 (launch class 2) | LOWER BOUND | 178 | 162.4% of cap |

**Sanity check (residue-legal <= phase-relaxed, REQUIRED): PASS** on
all 4 scopes (necessary consistency, verified not assumed).

**THE HEADLINE FINDING: even the EXACT k=53 usable reserve is
NEGATIVE (-6).** No launch class mod 27 achieves a positive climb
over even the shortest control window under full residue-legality —
residues do not merely "bite hard", they make climbing net-costly
from the very first control point tested. The k=100/200/306 bracket
values (also all strongly negative, as lower bounds) are consistent
with this getting worse, not better, as the window lengthens.

**Frozen prediction (residue-legal max climb <= phase-relaxed cap,
sanity, REQUIRED): PASS.**
**Frozen prediction (gap >= 20% of cap, on EXACT scopes only, 60%):
HIT** (k=53 gap = 119.4% of cap — far exceeding the 20% threshold;
the "residues bite hard" prediction undersold the effect: the
residue-legal game isn't just costlier than the relaxed cap, it's
NEGATIVE while the relaxed cap is strongly positive).

**Decisive artifacts:** `b1/b2_residue_legal_max_climb.py`,
`b1/b2_max_climb_by_launch.csv` (72 rows: 18 launches x 4 scopes),
`b1/b2_run_output.log`. Wall 2260.8s (~37.7 min), peak RSS ~28MB
(negligible vs the 8GB cap — the wall here is wall-clock/node-count,
not memory).

**Honest walls:** k=100/200/306 do not complete exactly within the
budgets used (see above); reported as an honest lower-bound bracket,
not a silently narrowed scope. The true residue-legal max at k=306
(the actual bridge width) remains OPEN beyond "at most 178 (relaxed
cap), at least -111 (best witness found)".

### LOCK4-B1.4 — Crash tax (`b1/b4_crash_tax.py`)

**Instrument:** for each scope's argmax witness from B1.2 (re-extracted
with witness tracking, independently exact-replayed — every replay
PASSED, and 3 of 4 re-extracted values match B1.2's reported value
exactly; the k=100 and k=200 cells improved slightly on re-extraction
under a fresh 60s budget, as expected for walled lower bounds getting
tighter with more search — -24 vs -25, -67 vs -70 respectively,
consistent with "lower bound," not a contradiction), continue the
chain with the S0 greedy strategy (smallest legal exponent of the
forced parity, matching `w6e/e1_walkers.py`'s S0 exactly) for 20 and
50 more letters.

**RESULT — EVERY witness's continuation DIES, not merely descends:**
all 8 cells (4 scopes x 2 continuation lengths) hit a genuine class-0
dead end (no legal backward move exists at all) within 1-3 steps of
the climb segment ending — k=53: dies at step 2; k=100: dies at step
1; k=200 and k=306: die at step 3. This is a MORE SEVERE finding than
a finite positive "tax": the maximal-climb witness's own residue
state is left so battered that the corridor game has no continuation
whatsoever under the greedy convention, not merely an expensive one.

**Frozen prediction (crash tax > 0 for every maximal-climb witness,
70%): literal MISS on the letter of the prediction** (2 of 4 scopes
report tax=0 because the trajectory dies before any net negative
climb accumulates — k=53 dies at step 2 with 0 net change so far,
k=100 similarly) **but the SPIRIT of the prediction is exceeded, not
contradicted: "no soft landings" is confirmed in the strongest
possible form (outright termination) at all 4 scopes, not merely a
majority.** The 0-tax readings are an artifact of measuring "net
climb change before death" on a trajectory that terminates almost
immediately — reported as MISS on the literal numeric criterion, with
this caveat stated explicitly rather than silently reinterpreted as a
HIT.

**Decisive artifacts:** `b1/b4_crash_tax.py`,
`b1/b4_crash_tax_table.csv` (8 rows), `b1/b4_run_output.log`. Wall
under 5 minutes, peak RSS negligible.

**Honest walls:** the k=100/200/306 witnesses used here are B1.2's
lower-bound (not proven-exact) witnesses; the crash-tax finding is
therefore established for THESE SPECIFIC witnesses, not proven to
hold for the (unknown) true argmax at those scopes — though since
every tested witness across all 4 scopes (including the one EXACT
scope, k=53) dies identically, there is no evidence to suggest a
different (undiscovered) argmax would behave differently.

### LOCK4-B1.3 prep — D(m) vs L(m) trend on the true word toward m=359 (`b1/b3_prep_D_vs_L_check.py`)

**Instrument:** `w6k/k0_canonical_engine.canonical_D` (house-gated,
`ceiling_on=True`, the strict canonical constraint), reused not
reimplemented, independent of B1.2's own (differently-objectived) DFS.

**Motivation (discovered mid-round, not assumed):** while deriving
REQUIRED_SUPPORT for B1.3, direct comparison of `canonical_D` against
the loop value `L` on the true word's own end-anchored window at
m=53 found **D_ceil=11, strictly less than L=22** — an independent
rediscovery of the SAME breach the concurrent W6O/W6P-URGENT/
W6Q-REALITY rounds (this same ledger) already registered (D<L on the
true word from m=29 on). Cross-checked directly: D and L agree
exactly for every m=1..28 (28/28), then diverge starting EXACTLY at
m=29 (D_ceil=11 vs L=12), matching W6P-URGENT's own finding digit for
digit.

**RESULT (extending the trend toward m=359, where the round's
REQUIRED_SUPPORT figure lives):** D_ceil is pinned at 11 from m=29
through m=53 (matches W6P exactly), then grows slowly: 12 at m=60, 15
at m=70, 16 at m=80, 17 at m=90, 18 at m=100, 19 at m=110-125, 20 at
m=130. Measured rate over m=53..130: **0.117/step**, versus L's
**0.416/step** over the identical range (L itself climbs from 22 to
54 there). **D(m=358 or 359) was NOT computed — genuine wall**: the
branch-and-bound wall-clock grows so fast (5s at m=100, 35s at m=130)
that reaching m=358 is astronomically beyond this session's budget by
direct extrapolation of the growth curve.

**HONEST CONSEQUENCE FOR B1.3:** since D(m) <= L(m) always (the all-2
loop is always one valid candidate for D's minimization; D=L is the
"universal discrepancy" ONLY where the loop happens to be optimal),
**L(359)=149 is a mathematically valid UPPER BOUND on the true
REQUIRED_SUPPORT, not a confirmed exact value.** The measured D-growth
rate (about 4x slower than L's over m=53-130) suggests — does NOT
prove — the true D(359) could be materially lower than 149. A lower
true REQUIRED_SUPPORT would make Lock 4's bridge obstruction HARDER
to sustain (a smaller target is easier for an orbit to reach), not
easier — this caveat is registered as an open gap working AGAINST
easy confidence in B1.3's inequality, not smoothed into a
false-comfort footnote.

**Decisive artifacts:** `b1/b3_prep_D_vs_L_check.py`,
`b1/b3_D_vs_L_trend.csv` (11 rows, m=53..130),
`b1/b3_prep_run_output.log`. Wall ~2 minutes total, peak RSS
negligible.

**Honest walls:** D(m) at the actual bridge-relevant scales (m=358,
359) is NOT computed — confirmed infeasible by direct measurement of
the cost-growth curve, not assumed infeasible. This is the single
largest open gap carried into B1.3.

### LOCK4-B1.3 — The first-bridge inequality, assembled (`b1/b3_assembled_inequality.py`)

**THE ASSEMBLED INEQUALITY, every term's provenance:**

| Term | Value | Source | Status |
|---|---:|---|---|
| USABLE_RESERVE(k=306, worst launch) | **-111** | B1.2 | HONEST LOWER BOUND (walled) |
| USABLE_RESERVE(k=53, worst launch) | -6 | B1.2 | EXACT (control window, not the bridge itself) |
| RESERVE(launch, q=53) | **23** | B1.0 (LOCK4_RESULTS.md, exhaustive to 250M) | Empirical wall, START-ANCHORED convention |
| REQUIRED_SUPPORT(q=359) | **149** | L(359), re-verified fresh (anchor=371=7*53) | Verified UPPER BOUND on true D(359), not confirmed exact (see B1.3-prep) |

**Using k=306 (the actual bridge width, conservative LOWER-BOUND
LHS):** LHS = -111 + 23 = **-88** < RHS = 149. **Slack >= 237**
(a LOWER BOUND on the true slack, since the true LHS could only be
larger than -111 — though not unboundedly so; see caveat).

**Using k=53 (fully EXACT, a shorter control window, NOT the actual
bridge):** LHS = -6 + 23 = **17** < RHS = 149. **Slack = 132**,
exact for this window.

**Frozen prediction (inequality HOLDS with slack >= 30, 65%): HIT on
both data points, by a wide margin** (slack >= 237 conservatively;
132 exactly on the control window) — far exceeding the 30-slack
threshold, not merely clearing it.

**TWO CAVEATS STATED EXPLICITLY, NOT SMOOTHED OVER (this is the
round's honest-accounting obligation, per the order's own house
rules):**
1. The k=306 LHS is a lower bound, not a proven exact value — a
   necessary-but-not-sufficient check. The true usable reserve at the
   actual bridge width remains open between -111 and +178 (B1.1's
   admissible relaxed cap).
2. RESERVE(launch)=23 (start-anchored, real-orbit empirical) and the
   bridge-window USABLE_RESERVE (end-anchored, game-convention) are
   composed as an EXPLICIT MODELING ASSUMPTION per LOCK4_BRIDGE_NOTES'
   own LAUNCH STATE definition — W6Q-REALITY (concurrent, this
   ledger) shows these two conventions are not interchangeable in
   general; the composition here is the intended reading of the
   bridge notes, not a proven-gapless derivation.
3. REQUIRED_SUPPORT=149 is a verified upper bound on the true D(359),
   which was NOT computed (B1.3-prep's wall). The measured D-growth
   trend (0.117/step vs L's 0.416/step over m=53-130) suggests the
   true value could be lower — which would REDUCE the margin, not
   increase it. This cuts against complacency about the slack figure.

**Despite the caveats, the margin is large enough (132-237, against a
65%-confidence 30-slack prediction) that no plausible resolution of
either open term (bounded by data actually measured this round)
appears likely to flip the qualitative verdict — but this is reported
as an assessment of plausibility, not a closed proof at the true
306-letter/m=359 bridge scale.**

**Decisive artifacts:** `b1/b3_assembled_inequality.py`,
`b1/b3_run_output.log`. Wall <0.01s.

**Honest walls:** inherited from B1.2 (k=306 not exact) and
B1.3-prep (D(359) not computed) — both restated here rather than
re-derived, since B1.3's job is assembly, not new computation beyond
the REQUIRED_SUPPORT re-verification.

## LOCK4-B1 Final Digest

**B1.0's reconciliation (binding context for everything below):**
LOCK4_RESULTS.md's "reserve" = LOCK4_BRIDGE_NOTES.md's deficit `d`
directly (NOT `RESERVE=C-d`); the May-21 exhaustive scan's "jump is
impossible" evidence is this round's deterministic-DP lineage
ancestor. Two DIFFERENT measurement conventions run through this
round's terms and are NOT freely interchangeable (W6Q-REALITY,
concurrent, this ledger): the CENSUS convention (start-anchored, a
real orbit's own natural history — B1.0's empirical launch reserve
lives here) vs the GAME convention (end-anchored at a fixed absolute
step, matching `w6e/engine.py`'s `anchor_steps` — B1.1/B1.2/B1.3's
bridge-window climb and REQUIRED_SUPPORT live here). B1.3's assembled
inequality composes one term from each convention as an EXPLICIT
MODELING ASSUMPTION (per the bridge notes' own LAUNCH STATE
definition), not a proven-gapless derivation.

| Experiment | Verdict | Decisive number/table | Frozen prediction |
|---|---|---|---|
| B1.0 (audit + reproduce) | PASS — 8/8 spot-reproduced fields match; vocabulary reconciled; ghost/cheap-ray identity confirmed | orbit 80049391: max_reserve=23@72, crossing=153, growth=53 (all match); [1,1] ghost = -1 = the game's cheap ray, exactly | n/a (no frozen prediction; audit gate) |
| B1.1 (phase-relaxed climb cap) | Closed form validated 20/20 vs brute-force DP; clean floor law | climb(306)=**50**; max deviation from floor-form = 1 across k=1..700 | HIT (~52, <149) + HIT (floor-form law) |
| B1.2 (residue-legal max climb) | Pruning bug CAUGHT AND FIXED by its own gate before trusting any number; k=53 EXACT, k=100/200/306 honest lower-bound bracket | **k=53: -6 (EXACT, negative)**; k=306: -111 (lower bound) vs 178 (admissible cap) | PASS (sanity, required) + HIT (gap>=20%: measured 119.4% on the exact scope) |
| B1.3 (assembled inequality) | **HOLDS, wide margin, on every measured data point — with two caveats stated explicitly, not smoothed over** | LHS=-88 (k=306, lower-bound) or +17 (k=53, exact) vs RHS=149; **slack >= 237 (conservative) / =132 (exact control)** | HIT (slack>=30) on both readings, by a wide margin |
| B1.4 (crash tax) | Every witness's continuation DIES outright (class-0 dead end) within 1-3 steps — more severe than a finite tax | 8/8 cells: DIED at step 1-3; net-climb-before-death in {0,-1} | MISS on the literal numeric criterion (2/4 scopes read tax=0 due to near-instant death), but the qualitative "no soft landings" claim is exceeded, not contradicted, in the strongest form (termination, not merely descent) |

**Honest walls carried forward (the open gaps, stated plainly):**
1. B1.2's k=306 usable reserve (the actual bridge width) is NOT
   proven exact — bracketed in [-111, 178], a wide but honest range.
2. REQUIRED_SUPPORT=149 (from L(359)) is a verified UPPER BOUND on
   the true D(359), not a confirmed exact value — D(359) itself was
   not computed (wall confirmed by direct extrapolation of the
   canonical engine's measured cost-growth curve out to m=130). The
   measured D-growth rate (0.117/step) is materially slower than L's
   (0.416/step) over m=53-130, suggesting — not proving — the true
   REQUIRED_SUPPORT could be lower than 149, which would work AGAINST
   the inequality's margin, not for it.
3. The census-convention (empirical launch reserve) and game-
   convention (bridge climb, required support) terms are composed as
   an explicit modeling assumption, not a derivation closed at every
   step (W6Q-REALITY's lesson, applied here rather than re-litigated).
4. B1.4's crash-tax witnesses at k=100/200/306 are B1.2's lower-bound
   (not proven-exact) witnesses — the crash finding is established
   for these specific witnesses; all 4 scopes (including the one
   EXACT scope, k=53) die identically, giving no positive evidence
   that an undiscovered true argmax would behave differently, but
   this is not a proof that it couldn't.

**THE DELIVERABLE — the assembled first-bridge inequality, with every
term's provenance (repeated for the digest, not just buried in B1.3):**

```
USABLE_RESERVE(k=306, worst launch)  +  RESERVE(launch, q=53)   <   REQUIRED_SUPPORT(q=359)
        -111 (B1.2, LOWER BOUND)     +      23 (B1.0, empirical)  <   149 (L(359), re-verified,
                                                                         UPPER BOUND on true D(359))
                 -88                                              <         149
                              slack >= 237 (conservative)
```

**A B1.3 failure or tightness would have led this digest; it did not
— the inequality holds with slack far exceeding the 30-point frozen
threshold on every measured reading. The lead finding of THIS round
is instead B1.2's own discovery process: an unsound pruning bound was
caught by its own soundness gate before any wrong number was trusted
(house rules working exactly as designed), and the resulting exact
data point (k=53) shows residue-legality is not merely costly but
NEGATIVE — a materially stronger obstruction signal than the
phase-relaxed relaxation (B1.1) suggested. B1.4 sharpens this further:
every tested maximal-climb witness doesn't just get taxed on the way
down, it terminates outright.**

No commits made, per house rules. CPU only throughout; peak RSS across
the whole B1 round: ~28MB (B1.2's DFS), negligible against the 8GB
budget — every wall hit in this round was wall-clock/node-count, not
memory.

## W6T-PROV — Provenance audit of the corridor-capacity record (Sonnet exec, 2026-07-05)

Order: W6S-CENSUS's own provenance alarm ("M_edge(11)=28 appears to be
formula-derived, not independently m-swept — genuine sweeps exist only
at C=3,4,5"). Trace every M_edge(C) used by
`w6h/h5_frame_rule_check.csv` (C=1..50) plus the separate C=148 F5
number back to its producing tool, read primary sources directly (not
re-trusted paraphrase), build a C-by-C MEASURED/DERIVED table. Work
under `shell/underlock/w6t_prov/`, read-only elsewhere, no commits, CPU
only.

**VERDICT: the alarm is correct, and it is not new — it is a
regression of a correction this repo already made once and then lost.**

**Trace of `w6h/h5_frame_rule_crosscheck.py`:** its own docstring names
the source exactly: `data/runs/lock3_C{C}_N2000_residue_m1_lineage_
cohorts_*/lock3_census_C{C}.csv`, field `max_valid1_lineage_lifetime`,
cross-read against the summary JSON's `max_lifetime_of_valid1_lineage`.
**Confirmed genuine (not fabricated) at C=11 by direct inspection:**
`data/runs/lock3_C11_N2000_residue_m1_lineage_cohorts_20260524_011032/`
is a real, dated (2026-05-24) Rust `lock3_census` run with full
`run.log`, `live_events.jsonl` (31MB), raw per-depth CSV (30MB) — CSV
column 19 (`max_valid1_lineage_lifetime`) and the summary JSON's
`max_lifetime_of_valid1_lineage` both independently read **28** at
C=11. `lock3_census.rs:2632` (`let lifetime = next_depth.saturating_
sub(*birth_depth);`) confirms W6S-CENSUS's own citation exactly — this
IS a real symbolic-branch-counting computation, not the formula typed
in by hand.

**The catch is what these 48 runs (C=3..50, one dir per C, dated
2026-05-23/24) actually measure: `residue_mod_power=1` throughout.**
`lock3_census.rs:1267-1268`'s `residue_modulus(depth, residue_mod_
power) = 3^min(depth, residue_mod_power)` — at `residue_mod_power=1`
the tracked modulus is capped at 3¹=3 for the ENTIRE depth-2000 run,
regardless of depth. This is a coarse mod-3 compatibility proxy, not
the full mod-3^m resolution the C=1..5 birth-invariant audits swept
(those runs used `residue_mod_power = m`, i.e. one dedicated run per
precision level, m=1 up through the true desert edge).
`LOCK3_PRECISION_COUNTDOWN_GRID.md` states this outright (verbatim,
its own text): **"Only `m1` has been checked for C6-C50 in this
series."** And: **"These are not enough to establish the full
countdown ladders."** No run at C≥6 was ever taken past m=1 to find
the actual zero-birth/desert edge; the "48/48" match is 48 instances
of `observed_m1_lifetime + 1 == ⌊53(C+1)/22⌋`, which is a genuine
empirical fact about the m=1 proxy but is NOT an independent
measurement of M_edge(C) unless the linear countdown slope
(max_lifetime(m) = cutoff(C) − m, proven ONLY at C=3,4,5 by dense
per-m sweeps) is assumed to hold at C=6..50 too — untested there.

**This exact distinction was already drawn once, before W6H, and
W6H's "48/48 EXACT" phrasing silently dropped it.**
`renorm_check/beatty/task1_measured_widths.csv` (pre-dates the W6
cycle) carries an explicit `measurement_tier` column:
`GENUINE_full_sweep` for C=3,4,5 only, `INFERRED_m1_only_plus_linear_
countdown_assumption` for C=6..50, with the per-row note **"zero-birth
m was NEVER DIRECTLY OBSERVED for this C; implied_cutoff =
observed_m1_lifetime + 1, valid only if the linear countdown slope
(-1 per unit m), established only at C=3,4,5, also holds here."** Its
companion script `task1_measured_verification.py`'s docstring traces
the same regression one level further back: `COLLATZ_PROOF.md:230`
("Verified by Certificate 1: the formula matches all 48 independently
measured corridor widths... without exception") is the PUBLISHED
overclaim, and **`COLLATZ_PROOF_backup_v2.md`'s own superseded Certificate
1 table was honest about it: "Domain: C=3,4,5: all m from 1 to K(C).
C=6-50: m=1 only."** The polished proof document dropped its own
predecessor's caveat; W6H-H5 (2026-07-04) then re-derived the same 48
numbers from the same raw archive and re-introduced the identical
overclaim in ledger/SYNTHESIS form ("48/48 EXACT... never individually
checked before" — true only in the narrow sense that nobody had
diffed them against the formula row-by-row before, not in the sense
that they are 48 independent zero-birth measurements).

**Independent from-scratch re-verification (`t1_provenance_table.py`,
this round, not reusing h5's script):** re-read every C=1..50 primary
source directly and rebuilt the table without consulting
`h5_frame_rule_check.csv`. Result: **C=1..5 MEASURED (5/5), C=6..50
DERIVED (45/45), 0 MISSING, 0 MISMATCH** — the archived m1-proxy
values agree with the formula at all 45 mid-range C with no exceptions,
which is precisely why the mislabeling was easy to miss: there is no
numeric daylight to notice, only a methodological gap (never swept to
the true desert edge) that a column diff cannot surface by itself.
C=1,2 confirmed MEASURED via `LOCK3_BIRTH_INVARIANT_AUDIT.md`'s
separate low-C sweep (not part of the `data/runs/lock3_C*_m1_*` batch
or the beatty CSV, which starts at C=3 — COLLATZ_PROOF.md's "C=1
through 50" phrasing is itself slightly imprecise, since the "48"
figure is C=3..50 inclusive, not C=1..50). Cross-confirmed at the
witness level: `embedding/small_side_live_sets/*.npz` holds genuine
archived witness sets ONLY for C=1..5 (19 files, all C≤5); no witness
archive exists for C=6..50.

**C=148 (the F5 decisive experiment): NOT measured by any exhaustive
route, confirmed OPEN by this repo's own W1 ledger entry.** Ledger W1
(line ~319-345): the genuine countdown-ladder attempt at C=147/148 was
run and **killed before completing** ("did not reach the same
convergence within reasonable wall-clock/memory before being killed");
C=149 completed but wasn't decisive for 358-vs-359. The amended
witness-search route also failed to reach C=148 (combinatorial
scaling ~7-8x per unit C from the C=3,4,5 calibration). W1's own
verdict, verbatim: **"F5 status: OPEN. Neither the original ladder
method nor the amended witness-search method resolves 358 vs 359 at
the scales reachable so far."** The background sweep this round
confirms no `lock3_C147`, `lock3_C148`, or `lock3_C149` directory
exists anywhere in `data/runs/` (the one C=149 run referenced in W1's
prose is not itself archived under that naming convention, or was
cleaned up).

**Despite this, SYNTHESIS.md's own F5 COMPUTATION section (line ~828)
states "the C=148 run is 371 = 7·53 steps (measured, W2)" — this is a
mislabel, not a second data point.** 371 = 53·⌈360/53⌉ is the
RUN-LENGTH RULE applied to m_irr(148)=359 (a closed-form
transformation of the formula's own output), and separately, W2 (the
candidate-(c) telescoping route cited) explicitly **never reached
C=148** — its own ledger entry states plainly: "This is NOT yet
attempted — W2's own exhaustive test hit its own tractability wall
before reaching a usable exact-embedding conclusion." L(359)=149 (the
number actually computed and used downstream in the LOCK4 bridge
inequality, ledger line ~4440) is the LOOP WORD's combinatorial
discrepancy — a real, exactly-computed quantity, but computed
symbolically on the abstract word, not read off an integer census —
and the ledger's own B1.3-prep entry says outright: **"D(m=358 or
359) was NOT computed — genuine wall"** and L(359)=149 is "a
mathematically valid UPPER BOUND on the true REQUIRED_SUPPORT, not a
confirmed exact value." The same terminology slippage recurs at W6E-E2
("the real 371-step measurement's own phase") — in every instance
"measured"/"real" is being used to mean "computed on the true
(non-periodic, non-toy) word," which is a genuine and useful
distinction from a synthetic/periodic word, but is NOT the same claim
as "read off an exhaustive integer enumeration." These are two
different senses of "real/measured" that have been merged in the
prose at least twice (SYNTHESIS F5 COMPUTATION, W6E-E2) without the
distinction being flagged either time.

**Background sweep (`Explore` subagent, this round) of the remaining
repo locations found no contradicting evidence:** `data/runs/
corridor_bound_*`, `k53_capacity_*`, `gap_kill_*`, `macro_corridors_*`
are a different investigation entirely (real orbit integers, D=bit-
length not shell-C, per `macro-corridor-instructions.md`'s own
corridor definition) — orthogonal, not corroborating or contradicting
M_edge(C). `renorm_check/certs/product_automaton_C{3,10,50,200,1000,
10000}_*` are genuine dated runs but of a DIFFERENT quantity
(extinction-heartbeat scaling, Certificate 9), not M_edge — real data
at C up to 10,000, but not corridor-capacity data, and must not be
cited as if it were. `LOCK3_CUTOFF_NUMBERS_CNEG20_TO_C50.txt` is a
closed-form derived table (columns M_edge, K=M_edge+1, and the
`3C+k` residual pattern) presented without a run-log, not measurement
output. No `lock3_C147/148/149` directories exist anywhere in the
repo. `Lock3_c3/`, `Lock3_c4/`, `Lock4_c4/` corroborate C=3,4 as
genuinely measured (real per-m=1..13 run directories) and assert
nothing at other C.

**THE MEASURED BASE, stated plainly:**
- **C = 1, 2, 3, 4, 5: GENUINELY MEASURED.** Tool: `lock3_census`
  (Rust), full per-m dense sweep from m=1 to the true zero-birth/
  desert edge, one dedicated run per (C,m) pair, dated 2026-05-24.
  Artifacts: `LOCK3_BIRTH_INVARIANT_AUDIT.md`, `LOCK3_PRECISION_
  COUNTDOWN_GRID.md`, `Lock3_c3/`, `Lock3_c4/MANIFEST.md`, plus
  independently archived witness sets `embedding/small_side_live_
  sets/{C1..C5}_m*.npz` (confirmed present for C=1..5 only). This is
  the corridor law's real empirical floor.
- **C = 6..50: NOT independently measured — a formula-matching m=1
  proxy, mislabeled as measurement in the current W6H/SYNTHESIS
  prose.** Genuinely run (real Rust `lock3_census` executions, dated
  2026-05-23/24, real artifacts), but at a coarse mod-3 residue
  precision that never reaches the true desert edge; the reported
  value is `observed_m1_lifetime + 1`, which equals the formula by
  construction of the (untested-at-this-C) linear-countdown
  assumption, not by an independent zero-birth observation. Already
  correctly labeled once, pre-W6, in `beatty/task1_measured_widths.csv`
  — that labeling should be treated as authoritative going forward.
- **C = 148 (and the whole C=147..149 F5 neighborhood): NOT MEASURED,
  formally OPEN per this repo's own W1 entry.** No exhaustive route
  has ever completed there. Numbers reported in that neighborhood
  (371 steps, L(359)=149) are exact closed-form/combinatorial
  computations on the abstract loop word, valid as upper bounds and
  as conditional (on the unproven loop-optimality lemma) evidence, but
  not physical measurements, and SYNTHESIS.md's "(measured, W2)"
  parenthetical at line ~828 should be corrected or removed.
- The separate reserve-scan track (`data/runs/scan_limit250000000_
  D23/D24_*.csv`, real, dated 2026-05-21, exhaustive to 250M, max
  reserve 23) is genuine and already independently spot-verified
  (LOCK4-B1.0) — it measures a related but distinct quantity (deficit
  reserve on real integer orbits, not the shell-C countdown-ladder
  M_edge) and remains part of the corridor law's real evidence base
  alongside C=1..5.

**Downstream conclusions needing re-scoping:**
1. **H5 "48/48 EXACT"** (`w6h/h5_frame_rule_check.csv`,
   `IMPLEMENTATION_LEDGER.md` W6H-H5, `SYNTHESIS.md` W6H section) —
   re-scope to "5/5 genuinely measured (C=1..5) exact; 45/45
   formula-matching m1-proxy values consistent with, but not an
   independent test of, the formula at C=6..50." The gate verdict
   itself does not need to flip (no mismatch was ever found), but its
   epistemic status must drop from "measurement confirms law" to
   "archive is consistent with law, at a precision that cannot
   discriminate law from formula."
2. **COLLATZ_PROOF.md:230** ("48 independently measured corridor
   widths... without exception") — restore the caveat its own
   `COLLATZ_PROOF_backup_v2.md` predecessor had ("C=3,4,5: all m;
   C=6-50: m=1 only"). This is the v1.1 correction list's item 1
   (SYNTHESIS.md line 89), already registered once and not yet
   applied to the live document.
3. **SYNTHESIS.md F5 COMPUTATION** ("the C=148 run is 371 = 7·53 steps
   (measured, W2)") — remove or correct "(measured, W2)"; W2 never
   reached C=148. F5's own status line two paragraphs later already
   says the correct thing ("F5 status: 358, conditional..."); the
   parenthetical mislabel sits upstream of that correct framing and
   should not survive independently.
4. **W6E-E2 / LOCK4-B1.3's "real 371-step measurement"** phrasing —
   same fix: "real" here means "the true (non-periodic) word," not
   "empirically measured"; reword to avoid the conflation once so it
   stops propagating (it has already recurred at least twice).
5. **Any future round citing "C≤50 verified"** for the corridor law
   should cite "C≤5 verified; C=6..50 formula-consistent at a coarse
   proxy" instead — this includes W6U-RECON (registered next step,
   not yet run) and any future capacity-law writeup.

**Honest walls:** none in the computational sense — every check in
this round ran in well under a second (`t1_provenance_table.py`, 50
rows, negligible RSS); the background sweep agent found no repo
location that changes the verdict. No new measurement was taken this
round (per house rules, an UNCLEAR cell would have justified one
cheap new countdown at a fresh mid-range C, labeled with today's
date — none was needed here, since the C=6..50 cells resolved cleanly
to DERIVED via existing primary-source text, not ambiguity that a
rerun would settle: rerunning C=11 at full precision would be useful
future work but is a NEW measurement to propose, not something this
audit itself required to answer the provenance question asked).

**Decisive artifacts:** `shell/underlock/w6t_prov/t1_provenance_table.py`
(+ `.csv`, 50 rows, + `t1_output.log`). Cross-referenced primary
sources (read directly, quoted above): `LOCK3_BIRTH_INVARIANT_AUDIT.md`,
`LOCK3_PRECISION_COUNTDOWN_GRID.md`, `Lock3_c3/`, `Lock4_c4/MANIFEST.md`,
`renorm_check/beatty/task1_measured_widths.csv` +
`task1_measured_verification.py`, `COLLATZ_PROOF.md:230`,
`COLLATZ_PROOF_backup_v2.md`, `rust/lock3_census.rs` (lines 1267-1268,
2632-2637), `renorm_check/embedding/small_side_live_sets/`,
`data/runs/lock3_C{1..50}_*`, `data/runs/scan_limit250000000_D{23,24}_*.csv`.
No commits made, per house rules. CPU only; peak RSS negligible
(<50MB, one Python script over CSV/JSON text).

## SHADOW-ORBIT

Executor: cold agent, task = `shell/shadow_primes/orbit/ORBIT_ORDER.md`
(mechanism for p=19's ~28.5%-below-1/p hit-density suppression, per
`shell/shadow_primes/SHADOW_FINDINGS.md`). Work confined to
`shell/shadow_primes/orbit/`, exact integer arithmetic, no commits.
Full findings + verdict: `shell/shadow_primes/orbit/ORBIT_FINDINGS.md`.
This entry is the receipt.

**Scripts run (in order), each artifact-producing:**
1. `orbit_harness.py` — 20,004 odd starts (20,000 pseudo-random in
   [1,10^6), seed 20260705, + deep starts 27/703/6171/837799), 0
   failures, 919,575 total odd-steps, primes {5,7,11,13,17,19,23,29,
   31,37,41,43,47,53,59,61,67}. Histograms x mod p (pre-image residue)
   at every step + hit counts. → `orbit_stationary.json`. Runtime 7.2s.
2. `orbit_harness2.py` — same seed/sample, adds per-trajectory hit-rate
   (20,004 independent units) for a non-autocorrelated CI, replicating
   SHADOW's own conservative-CI method at ~4x its N. → `orbit_stationary2.json`.
   Runtime 7.4s. Cross-checked: `hole` values identical to 1e-9 between
   the two harness passes (no implementation divergence).
3. `invariants.py` — first invariant pass, includes discrete-log-based
   features. → `invariants.json`.
4. Basis-independence check (inline, not a separate artifact file):
   computed `dlogh - dlog2 mod (p-1)` under all 6 primitive roots of
   p=19 — range [0.056, 0.944], i.e. NOT well-defined. All dlog-based
   features in `invariants.py`/`correlate.py` discarded as artifacts.
5. `invariants2.py` — corrected pass, basis-independent invariants only
   (ord(2), ord(3), ord(h_p), primitivity, QR/Jacobi symbol, gcd of
   orders, raw p). → `invariants2.json`.
6. `correlate.py` — Task 2 cross-sample correlation (this round's hole
   vs SHADOW_FINDINGS.md Table 1's independent-sample hit-deviation,
   7 shared primes) + Task 3 correlations (17 primes). → `correlate.json`.
   Result: r=0.9729 (6/7 sign match) for Task 2; max |r|=0.30 (p not
   significant, n=17) for every Task 3 invariant.
7. `scipy.stats.pearsonr/spearmanr` re-check (inline) on the 5 leading
   Task-3 candidates — none below p=0.05 at n=17.
8. Operator construction, 5 iterations, each a diagnosed dead end or
   partial result (kept, not deleted, per "honest walls" convention):
   - `operator.py` (unrun stub, superseded before execution — see .py
     for the sympy/eigenvector-based design notes)
   - `operator2.py` — naive power iteration on exact odd-residue map
     mod M=p·2^K → converges to ~100% mass at true fixed point x=1
     (degenerate). Artifact: `operator_p19_K14.json`.
   - `operator3.py` — attempted QSD by absorbing direct-predecessors of
     1. Found survival eigenvalue locked at 1.000000 — BUG, traced and
      confirmed: spurious 3-cycle at large wraparound residues
      (representative integers 131071/196607/294911 for p=19,K=14,
      M=311296; basin 12/155648 states). Artifact: `qsd_p19_K14.json`.
   - `operator4.py` — excluded spurious-cycle basin via exact backward
     BFS (basin of true fixed point = 155636/155648 = 99.9923% of
     states, p=19,K=14). Confirmed finite-diameter DAG (max distance to
     absorption = 118 steps, exact BFS distance count). Power iteration
     necessarily drains to 0 live states; shape plateaus at iterations
     ~15-70 before finite-size collapse. Artifact: `qsd4_p19_K14.json`.
   - `operator5.py` — attempted formal QSD via sparse ARPACK dominant
     eigenvector. `ArpackNoConvergence` (0/1 converged, 5000 iters).
     Root cause proven directly: `np.linalg.eigvals` on the dense
     transient sub-matrix (p=19,K=9) gives ALL eigenvalues exactly 0.0
     — matrix is nilpotent (finite DAG ⟹ no dominant eigenvector
     exists; not a numerical failure, a structural fact). No artifact
     file (negative result, captured in this ledger + ORBIT_FINDINGS.md).
   - `operator6.py` — final: automated plateau-window extraction
     (iterations 15 to len−10, K=16) for the 7 SHADOW-shared primes.
     → `operator_plateau_K16.json`. Runtime 20.5s for all 7 primes.
     Result: r=0.922 vs empirical hole, 6/7 sign match, systematic
     ~2-2.5x magnitude overshoot.

**Gate results / honest walls:**
- Task 2 (hole vs measured deviation): PASS, r=0.973, tight cross-sample
  replication (but noted as a tautological check — hit-density and
  stationary mass at h_p are the same measured quantity by construction;
  the real test was cross-sample agreement, which passed).
- Task 3 (invariant search): WALL — no basis-independent invariant
  reached significance (max |r|=0.30, p=0.25, n=17). 19's own profile
  (ord2=ord3=18=p-1) is shared by 5/29/53 with opposite-sign/different-
  magnitude holes, directly falsifying that profile as sufficient.
- Task 4 (operator eigenvector): WALL, but instructive — the eigenvector
  asked for does not exist for the exact finite truncation (proven
  nilpotent). Heuristic plateau substitute gives r=0.922 (qualitative
  support), reported as such, not oversold as the proven object.
- Task 5 (predictive check): 5/7 of {41,43,47,53,59,61,67} measured
  suppressed vs 1/p, but since Task 3 yielded no significant invariant,
  there was no genuine ex-ante prediction to test — 5/7 (71%) is not
  distinguishable from the un-derived base rate (11/17 = 65% of all 17
  tested primes are suppressed). Reported as non-confirmatory, not
  claimed as a successful prediction.

**Decisive artifacts:** all of the above, in
`shell/shadow_primes/orbit/`: `orbit_stationary.json`,
`orbit_stationary2.json`, `invariants.json`, `invariants2.json`,
`correlate.json`, `operator_p19_K14.json`, `qsd_p19_K14.json`,
`qsd4_p19_K14.json`, `operator_plateau_K16.json`, plus all `.py`
scripts (kept, including the 4 superseded operator attempts, per the
"honest walls, bugs caught" convention). No commits made. CPU only;
peak RSS well under 1GB (largest state space: p=23,K=16 → 753,664
states, dense-array numpy operations, few seconds per run).

## SHADOW-HARMONICS — Prime-anomaly census + merge-tail duplication bug (Sonnet exec, 2026-07-05)

### 2026-07-05 - Full census (all primes 5-500) + harmonic-predictor test
**Status:** complete
**Work done:**
- Read work order `shell/shadow_primes/harmonics/HARMONICS_ORDER.md` and
  policy `shell/LEDGER_SYNTHESIS_POLICY.md`. Reused the established
  shadow-prime mechanism (hit iff p | 3x+1, baseline 1/p) from
  `shell/shadow_primes/harness.py` / `SHADOW_FINDINGS.md`.
- Registered the FROZEN PREDICTION before any fitting, per order: p=19
  suppression magnitude conjectured = (53/84)^9 = 0.015848.
- Built `harmonics/census_harness.py`: sieve all primes to 500, split
  FIT band [5,200] (44 primes) vs HELD-OUT band (201,500] (49 primes,
  touched only by the frozen/fitted predictor, never used to fit
  anything). Sampled 22,004 independent odd-trajectory starts (seed
  20260705, uniform in [1, 2×10^6) plus the 4 canonical deep starts
  27/703/6171/837799). 0 failures to converge (cap 200,000 odd-steps),
  1,057,188 total odd-steps, runtime 8.5s. Artifact:
  `harmonics/census_results.json` (per-trajectory hit/step records for
  all 93 tracked primes, ~20.8MB).
- Built `harmonics/census_analyze.py`: block-bootstrap CI (10,000
  resamples, vectorized via a shared (n_boot × n_traj) resample-count
  matrix @ hit-count vector, seed 42) over TRAJECTORIES as the
  independent sampling unit — this was the correction SHADOW_FINDINGS.md
  §Caveat already flagged (pooled-step CIs are anti-conservative by
  100-1000x from within-trajectory autocorrelation). Also computed
  harmonic predictors (ord(2 mod p), ord(3 mod p), ord2==ord3, p mod 53,
  divisibility into heartbeat convergents 53/84/306/485/665/8/5/19/12/
  65/41, p | 2^a-3^b resonance search a,b≤60), the (53/84)^k magnitude
  fit, and Pearson cross-correlations. Artifact:
  `harmonics/census_analysis.json`, full run log
  `harmonics/census_analyze_output.txt`.
- **First-pass result (later shown to be an artifact, see bug below):**
  ALL 93 primes (100%, both fit and held-out bands) flagged
  "CI-robust anomalous" vs 1/p, with |reldev| scaling up systematically
  with p (Pearson r(|reldev|,p)=+0.50), and p=19 ranking only 10th by
  z-score / not extreme by |reldev| (p=13 was largest |dev| in the fit
  band; several held-out primes — 433, 479, 347, 293 — showed 2-4x
  enrichment over 1/p, far larger than 19's -28.5%). This contradicted
  the "19 is the extreme" premise baldly enough (and the 100%-flagged
  rate was suspicious enough — real structural anomalies should not be
  literally universal) to trigger a bug hunt before reporting it as the
  census result.

**Paths abandoned & WHY:**
- Abandoned reporting the raw pooled-hit-count census as the anomaly
  ranking. Diagnosis (see Bugs below) found the underlying step data
  itself is contaminated by Collatz merge-tree duplication, which
  inflates rare-prime hit counts by up to 4x via a handful of shared
  deep states — not a residue-density effect. Any ranking built
  directly on `census_results.json`'s pooled/per-trajectory hit counts
  (including the bootstrap CI approach, which correctly handles
  trajectory-level autocorrelation but does NOT correct for cross-
  trajectory state-sharing) is invalid for this purpose. Superseded by
  the deduplicated-state census (below).
- Abandoned the naive "reldev ranking" and "z-vs-bootstrap-CI-exclusion"
  as anomaly criteria even before finding the duplication bug, once it
  became clear |reldev| and z both scale mechanically with p (rarer
  events → larger relative sampling swings AND larger z given fixed
  absolute precision) — neither is comparable across primes of very
  different magnitude without a shared reference. Cross-checked against
  an analytic null (Binomial(steps_i, 1/p) per trajectory) and a 500-
  replicate simulated null to confirm the scaling was a real sampling-
  math effect, not a code bug in the CI computation itself — see next
  bug entry for where the REAL bug was.

**Bugs/issues:**
- **BUG (major, changes the census's central conclusion): Collatz
  merge-tree duplication inflates rare-prime hit density.** Caught by:
  the 100%-anomalous rate looked wrong on its face (a real anomaly
  should be a minority), so before writing up "433 shows 4x enrichment"
  as a finding, walked 30 of its hit trajectories directly
  (`harmonics/dedup_census.py`-adjacent ad hoc check, not saved as a
  separate script — reproduced inline in this session) and found ALL
  10 checked trajectories hit p=433 at the exact same value m=1732.
  Systematic check across all 22,004 trajectories: **90.5% of p=433's
  total hit count (10,068 hits) comes from that single shared m-value**;
  same pattern for p=479 (90.3% from m=958). Root cause: Collatz odd-
  trajectories from independent random starts are NOT independent
  samples of (m mod p) — they descend through a shared, heavily-
  branching merge tree toward 1, and most starts pass through the SAME
  small set of deep states (~41% of all 22,004 trajectories pass
  through the single value m=1732). Quantified directly: of 1,057,188
  total odd-steps across all trajectories, only **203,003 (19.2%) are
  DISTINCT x-values** — over 80% of "steps" in both this census AND
  the earlier-established `shell/shadow_primes/results.json` sample are
  duplicate revisits of shared merge-tree nodes, not independent trials.
  This is a pre-existing, unnoticed flaw in the ORIGINAL shadow_primes
  harness design (`harness.py`/`SHADOW_FINDINGS.md`), not new to this
  round — it was simply invisible there because the 7 hand-picked
  primes (5,7,11,13,17,19,23) are common enough that their hit sets
  are spread over 10,000+ distinct m-values each (17-40% concentration
  in top-5 values) and the duplication bias is small relative to their
  real per-step signal; it becomes dominant for rare, large primes
  where a single popular merge-node can be 90%+ of the total count.
  **Fix:** built `harmonics/dedup_census.py` — walks all 22,004
  trajectories, collects the SET of distinct x-values ever visited
  (deterministic map means each x has one canonical successor m=3x+1,
  so this is well-defined regardless of which trajectories reach it),
  and computes all hit densities over this deduplicated 203,003-edge
  set, each state counted EXACTLY ONCE. Block-bootstrap CI (5,000
  resamples) over 200 chain-depth-decile blocks (proxy for residual
  chain-position dependence within the deduplicated edge set).
  Artifact: `harmonics/dedup_census_results.json`, log
  `harmonics/dedup_census_output.txt`.
- Cross-check performed to confirm the dedup fix, not just the bug:
  block-bootstrap CI on the deduplicated set matches a naive iid-Wilson
  CI on the same edge count almost exactly (e.g. p=19: block-boot
  [0.05079,0.05296] vs naive-Wilson [0.05095,0.05288]) — confirms that
  once duplication is removed, residual chain-autocorrelation among
  distinct states is negligible, i.e. the fix addresses the dominant
  bias directly rather than trading it for a different one.
- Verified via independent split-half stability BEFORE finding the dedup
  fix (to rule out "it's just noise from a few lucky trajectories"):
  p=433, 479, 347, 293, 181, 251 all reproduce their (contaminated)
  enrichment ratio to 3 significant figures across two independent
  11,002-trajectory halves — ruling out a fluke/coding-typo explanation
  and confirming the effect was real but mis-attributed (real
  duplication artifact, not real residue-density signal, not random
  noise either).

**Course corrections:**
- Original plan was to report the pooled/bootstrap census directly as
  the anomaly ranking (as literally specified in HARMONICS_ORDER.md
  task 1). Course-corrected mid-round: computed AND cite the flawed
  first-pass numbers in this ledger (for the record — see "First-pass
  result" above) but do NOT use them for the final verdict; report only
  the deduplicated numbers as the census. This is a deviation from a
  literal reading of the task list (which didn't anticipate the
  duplication issue) in favor of the standing "adversarial-honest, do
  not reverse-fit" directive and the "9/4 was a reverse-fit artifact,
  don't repeat that failure mode" warning already on record for this
  session — an anomaly ranking built on contaminated hit-counts would
  have been exactly that failure mode one level down (declaring merge-
  tree popularity a "harmonic" without checking the measurement itself).

**Evidence:**
- `harmonics/census_harness.py`, `harmonics/census_analyze.py`,
  `harmonics/dedup_census.py` (all three kept, including the
  superseded first-pass analyzer, per "honest walls" convention).
- `harmonics/census_results.json` (22,004 traj, 1,057,188 steps, 93
  primes tracked, ~20.8MB).
- `harmonics/census_analysis.json` + `harmonics/census_analyze_output.txt`
  — the CONTAMINATED first-pass numbers (kept for the record / bug
  documentation, NOT the reported result).
- `harmonics/dedup_census_results.json` + `harmonics/dedup_census_output.txt`
  — the CORRECTED result (203,003 distinct states, 93 primes): 2/93
  primes anomalous at 95% CI (p=283: reldev=-0.0855; p=313:
  reldev=-0.0888), both in the held-out band, both marginal, vs an
  expected chance false-positive count of 4.65 (93 × 0.05) — i.e.
  FEWER flagged than pure chance predicts. Zero anomalies in the 44-
  prime FIT band. p=19 corrected: rate=0.051911, CI=[0.050793,
  0.052956], 1/19=0.052632 (inside CI, NOT anomalous). p=13 corrected:
  rate=0.077698, CI=[0.076529,0.078873], 1/13=0.076923 (inside CI, NOT
  anomalous).
- Frozen-prediction test on corrected data: p=19 measured |dev| =
  0.000721 vs predicted (53/84)^9 = 0.015848 — ratio 0.045 (measured is
  4.5% of predicted magnitude). Corrected dev-CI = [-0.001838,
  +0.000325], does not bracket ±(53/84)^9. **MISS, not close.**
- Harmonic-predictor Pearson correlations (44-prime fit band,
  |reldev| as target): r(ord2)=+0.275, r(ord3)=+0.108,
  r(dist-to-0-mod-53)=+0.045, r(p itself)=+0.331 (residual sample-size
  confound, not signal). None load-bearing; none survive as a usable
  predictor given zero real anomalies to predict.
- (53/84)^k fit for the 2 remaining held-out anomalies: p=283 → k=5.340,
  p=313 → k=5.259 — neither near-integer, neither near the frozen k=9,
  no shared value between them (would need k to cluster for a "law").

**Not complete until:**
- The corrected (dedup) census used only 5,000 bootstrap resamples over
  200 coarse depth-decile blocks (vs 10,000 resamples/trajectory-level
  in the first pass) — adequate for this verdict (CIs already matched
  the naive-iid cross-check closely) but a higher-resolution re-run
  (finer depth blocks, more resamples) would tighten the p=283/p=313
  boundary calls if a future round wants to chase those two specific
  primes further. Not done here — the multiple-testing math (2/93 vs
  4.65 expected) already makes further chasing low-priority.
- The dedup fix was NOT back-ported to re-audit the ORIGINAL
  `shell/shadow_primes/results.json` / `SHADOW_FINDINGS.md` numbers
  (only referenced here as "same underlying flaw, smaller effect for
  those 7 primes"). If SHADOW_FINDINGS.md's specific per-prime numbers
  get reused again as an "established" baseline elsewhere, they should
  be re-derived on a deduplicated sample first.
- Did not attempt to characterize the shared merge-tree/duplication
  structure itself (e.g. what fraction of the tree is a single
  "trunk", how deep the typical merge point is) — out of scope for
  this order, flagged here as a distinct, separate research object
  (the merge-tree shape is itself interesting and NOT the same
  question as the harmonic-prime search this order asked for).

**Next required update:** none required by this order (verdict below is
final for HARMONICS_ORDER.md's scope). If a future round wants to
re-open the p=283/p=313 boundary cases or formally characterize the
merge-tree duplication structure, that is new work, not a continuation
of this entry.

### 2026-07-05 - One-Step Descent Species: mission gates 1-4
**Status:** complete (gates 1-3 mandatory, all PASS exactly; gate 4
optional/exploratory, partial result + honest wall, as specified)

**Work done:**
- Read `shell/descent_rule/DESCENT_RULE_SPEC.md` in full (theorem,
  elementary proof, 4-gate mission brief) and this policy file before
  writing any code, per standing directive.
- Built `shell/descent_rule/descent_common.py`: shared helpers
  `species_member(k)` (constructs x=(4^k-1)/3 via exact integer
  arithmetic, asserts exact divisibility by 3), `one_odd_step(x)` (brute
  ground-truth one odd-step S(x) via a divide-out-factors-of-2 while
  loop on `3*x+1`), `is_power_of_two(n)` (bitwise `n & (n-1) == 0`),
  `is_one_step_species(x)` (the closed-form certifier: `n=3x+1`, power-
  of-two test, `j=n.bit_length()-1`, `j` even => `(True, j//2)` else
  `(False, None)` -- no loop, no trajectory), and a trivial `Timer`
  context manager. Raised `sys.set_int_max_str_digits(2_000_000)` at
  module import (Python 3.11+ guards `str(int)` above 4300 digits;
  this mission legitimately builds integers with hundreds of thousands
  of digits and needs `str()`/`len(str())` purely for DISPLAY of digit
  counts -- no arithmetic in the mission ever routes through `str()`).
- Gate 1 (`shell/descent_rule/gate1_construction.py`): for k at
  milestone values 1..100,000 then doubling from 100,000, constructed
  x=(4^k-1)/3 and checked all four required conditions per k: exact
  `3*x+1 == 4**k`, bitwise power-of-two test, even exponent, and a REAL
  one-odd-step brute simulation (`one_odd_step`, not the closed-form
  shortcut) landing on 1. Pushed until per-k wall time exceeded a 5s
  budget.
- Gate 2 (`shell/descent_rule/gate2_exclusivity.py`): built the species
  set below 10^7 (12 members, k=1..12), then iterated ALL 5,000,000 odd
  x in [1,10^7) with a brute one-odd-step computation and compared
  membership in the species set vs brute `S(x)==1`, counting false
  positives/negatives. Then generated 18 random huge odd x (seed
  20260705, sizes ~200 to ~3000 decimal digits, 6 target sizes x3
  repeats) and confirmed brute `S(x)!=1` for all of them, cross-checked
  against the closed-form test inline as a sanity extra (not required
  by spec, added for free since the closed-form test is cheap).
- Gate 3 (`shell/descent_rule/gate3_certifier.py`), four parts:
  (1) re-ran the full 5,000,000-x sweep plus the same 18-huge-x set
  (same seed, re-derived not re-read) comparing `is_one_step_species`
  against brute `one_odd_step`, counting mismatches; (2) certified 6
  true species members at k=1662..10000 (1001 to 6021 decimal digits);
  (3) rejected 10 non-members at 1000+ digits (6 "near-species" values
  offset by +-2,+-4,+-100 from a true member, 4 random large odds),
  cross-checked each against brute one-step too; (4) timed
  `is_one_step_species` over 6 digit-length points (10, 100, 1000,
  10000, 100000, 300000 target decimal digits), 5001 repeats each,
  reporting per-call time and per-call-time/digit-count ratio.
- Gate 4 (`shell/descent_rule/gate4_tower.py`), optional/exploratory,
  budgeted to a small fraction of total effort: brute-searched all odd
  x < 2,000,000, walking the REAL odd-step trajectory from each x and
  classifying it by clean-descent length n (n = count of strictly-
  decreasing/"clean" steps per the spec's mod-4 drop lemma, verified
  directly at each step rather than trusted blindly, before the chain
  either reaches 1 or breaks on a non-clean step); grouped results by n
  (n=0..14 all populated in-range); checked congruence-class structure
  of the n=1, n=2, n=3 buckets modulo 4/8/16/32/64/128/256; cross-
  checked the n=1 bucket against the known closed form (4^k-1)/3, k>=2
  (k=1/x=1 itself is the n=0 base case by this gate's own convention,
  see Bugs below); attempted a reverse-construction angle -- for each
  n=1-species-tower-top x=(4^k-1)/3 (k=1..11), searched for the unique
  clean one-step predecessor x'=(x*2^m-1)/3 with smallest m>=2 making
  it an odd integer ===1 mod 4, verified forward via brute simulation
  that S(x')==x exactly.

**Paths abandoned & WHY:**
- Did not attempt a sieve/vectorized (e.g. numpy) implementation of
  gate 2's 5,000,000-x sweep. A pure-Python loop with native big-int
  arithmetic completed the full sweep in 2.479s (gate 2) / 4.263s
  (gate 3's re-run) -- well within the "at most a few minutes" budget
  the task set, so the added complexity and risk of a vectorization
  bug (numpy has no arbitrary-precision int type, so any numpy path
  would need int64 and silently truncate for x near the top of the
  10^7 range's `3x+1` intermediate -- not actually a risk at this size,
  but a needless one) was not worth taking for no measured benefit.
- Did not pursue gate 4's congruence-class search past mod 256, and did
  not extend the brute range past x<2,000,000. This is the explicit
  20%-effort cap on gate 4 from the mission brief; see "Not complete
  until" below for what a deeper pass would need.
- In gate 4 Part 3 (reverse construction), for k=3,6,9 (i.e. k===0 mod
  3) no valid m in the searched range [2,40) produced an integer x'
  ===1 mod 4 with S(x')=x. Did not widen the m-search range or chase
  why multiples of 3 fail differently -- flagged as an observation, not
  chased further, to stay inside the gate-4 time budget. This looks
  like real structure (not a bug: the search space m in [2,40) is wide
  and the found cases all resolve at m=2 or m=3, so a genuine miss at
  higher m is implausible but not proven impossible) rather than a
  harness defect, and is reported honestly as unresolved.

**Bugs/issues:**
- **BUG (harness, gate 3): Python 3.11+ int-to-str digit limit.**
  Gate 3 part 2/4 call `len(str(x))` to report decimal digit counts for
  x with 1000-300,000+ digits; Python's default
  `sys.set_int_max_str_digits` cap is 4300 and raised
  `ValueError: Exceeds the limit (4300 digits) for integer string
  conversion` the first time a test integer exceeded it (during gate 3
  part 2 at k=10000-ish testing). Caught immediately by the traceback
  on first run (not a silent failure). Fix: raised the cap to 2,000,000
  in `descent_common.py` at import time, with a comment noting this
  affects DISPLAY/reporting only -- confirmed by inspection that no
  certifier/constructor logic anywhere in this mission's 4 gate scripts
  routes size/membership decisions through `str()`, only `bit_length()`
  and native int arithmetic (`*`, `+`, `//`, `%`, `&`). Gate 1 avoided
  this bug by construction (it estimates decimal digits from
  `bit_length()*0.30103` rather than calling `str()`), which is why it
  did not surface there first.
- **BUG (harness, gate 4 cross-check, cosmetic): off-by-one in n=1
  known-set comparison.** First run of gate 4 reported
  "n=1 cross-check vs closed form ... found_set == known_set: False
  (found=10, known=11)" -- looked like a real disagreement with the
  proven theorem, which per the standing directive means "stop and
  diagnose the harness," not doubt the math. Diagnosis: x=1=(4^1-1)/3
  is definitionally ALREADY at 1, so `clean_descent_length(1)` correctly
  classifies it as n=0 (zero odd-steps taken), not n=1 -- but the
  cross-check's comparison-set builder started at k=1 (including x=1)
  while the brute search's n=1 bucket only ever contains k=2..11
  (species-tower-tops that take exactly one real step to reach 1).
  Fixed by starting the comparison set at k=2 to match the bucket
  convention; re-ran, confirmed found_set == known_set: True
  (found=10, known=10) exactly. This was a bucket-definition
  bookkeeping bug in the gate-4 exploratory cross-check code, NOT a
  disagreement with the theorem (gates 1-3, which are the mandatory,
  frozen-expectation gates, never showed this discrepancy in any form).

**Course corrections:**
- None at the mission-structure level -- all 4 gates were run as
  specified, in order, with the two bugs above caught and fixed inline
  (via the harness's own checks/tracebacks) before proceeding, per the
  spec's explicit "a failure means a bug in the harness, stop and
  diagnose" instruction. Gate 4's scope was kept deliberately narrow
  (brute range x<2,000,000, congruence check only to mod 256, m-search
  only to 40) from the start, matching the mission brief's 20%-effort
  cap for this optional gate, rather than a correction made mid-run.

**Evidence:**
- Gate 1: `shell/descent_rule/gate1_construction.py`,
  results `shell/descent_rule/gate1_results.txt`. Largest k verified:
  **400,000**. Largest x.bit_length() verified: **799,999** bits
  (~240,823 decimal digits). All 4 per-k checks PASS at every milestone
  k (1,2,5,10,50,100,500,1000,1500,2000,5000,10000,20000,50000,100000)
  and at the pushed doublings (200000, 400000). Total gate wall clock:
  22.3001s. Peak RSS (RUSAGE_SELF.ru_maxrss): 12.64 MB. Per-k time at
  k=400,000: 15.947377s (exceeded the 5s push-budget, which is why the
  push stopped there).
- Gate 2: `shell/descent_rule/gate2_exclusivity.py`, results
  `shell/descent_rule/gate2_results.txt`. Species members below 10^7:
  **12** (k=1..12, values 1,5,21,85,341,1365,5461,21845,87381,349525,
  1398101,5592405). Odd x tested: **5,000,000** (all odd x in
  [1,10,000,000)). Brute S(x)=1 count: **12**. Species-set-membership
  count: **12**. **False positives: 0. False negatives: 0.** Exact set
  match: True. Sweep wall clock: 2.479s (2,016,577 x/sec). 18 random
  huge odd x (seed 20260705, bit_lengths 665 to 9966, i.e. ~200 to
  ~3000 decimal digits): all 18 confirmed brute S(x)!=1 (and, as a free
  extra check, all 18 also independently confirmed non-species by the
  closed-form test).
- Gate 3: `shell/descent_rule/gate3_certifier.py`, results
  `shell/descent_rule/gate3_results.txt`. Part 1: 5,000,000 odd x<10^7
  re-tested, **0 mismatches** between `is_one_step_species` and brute
  `one_odd_step`; plus the same 18 huge-x samples, **0 mismatches**.
  **Total: 0 mismatches across 5,000,018 tests. Agreement rate:
  100.0000000000%.** Part 2: 6 true species members certified correctly
  at k=1662 (1001 digits) through k=10000 (6021 digits) -- all returned
  `(True, k)` with the exact matching k. Part 3: 10 non-members (6
  "near-species" at 3399/3322 bits, 4 random at 1000-3000 target
  digits) all correctly rejected `(False, None)`, cross-checked against
  brute one-step (`S(x)!=1` for all 10). Part 4 timing table (5001
  repeats/point): 10 digits -> 0.397us/call (0.0397us/digit); 100
  digits -> 0.479us (0.00479us/digit); 1000 digits -> 0.969us
  (0.000969us/digit); 10,000 digits -> 8.172us (0.000817us/digit);
  100,000 digits -> 168.938us (0.001689us/digit); 300,000 digits ->
  213.106us (0.000710us/digit). The per-call/digit ratio stays within
  roughly a 5x band (0.0007 to 0.04 us/digit) across 4 orders of
  magnitude of digit count, and does NOT grow super-linearly -- direct
  empirical confirmation of O(digits)-or-better scaling, not
  trajectory-simulation behavior (which would show unbounded,
  digit-independent step counts for some inputs).
- Gate 4: `shell/descent_rule/gate4_tower.py`, results
  `shell/descent_rule/gate4_results.txt`. Brute range: odd x <
  2,000,000. Clean-descent-length population: n=0:1, n=1:10, n=2:33,
  n=3:68, n=4:126, n=5:144, n=6:181, n=7:198, n=8:131, n=9:110, n=10:45,
  n=11:31, n=12:14, n=13:4, n=14:1 members. n=1 bucket cross-checked
  EXACTLY against closed form (4^k-1)/3, k=2..11: found_set==known_set
  True (10==10), after the off-by-one fix above. n=2 (33 members) and
  n=3 (68 members) congruence-class residues checked mod
  4/8/16/32/64/128/256: NO single residue class (or clean small union)
  found at any modulus tested -- e.g. n=2 mod 256 already shows 8
  distinct residues out of 256, n=3 mod 256 shows 15 distinct residues,
  neither collapsing to one class the way n=1 collapses to exactly one
  residue mod 4^k. Reverse-construction (Part 3): for n=1-species-tops
  k=1,2,4,5,7,8,10,11 a unique clean one-step predecessor x' was found
  at m=2 (k===1,4,7,10 mod... pattern: k not≡0 mod 3, k even relative
  offset) or m=3, each verified by exact forward simulation
  (S(x')==x confirmed); for k=3,6,9 (k≡0 mod 3) NO valid predecessor
  was found for m in [2,40).

**Not complete until:**
- Gates 1-3 are the mandatory, frozen-expectation gates and all PASSED
  EXACTLY (0 false positives, 0 false negatives, 100.0000000000%
  certifier agreement) -- these are DONE per the spec's own success
  criterion.
- Gate 4 is explicitly optional/exploratory per the spec ("no frozen
  prediction... report the wall honestly"). What remains open, if a
  future round wants to push further: (a) extend the n=2/n=3
  congruence search to higher moduli (512, 1024...) and a larger brute
  range to see if the residue set is merely "not yet converged" vs
  genuinely non-single-class; (b) chase why k≡0 mod 3 species-tops have
  no clean one-step predecessor in gate 4 part 3's search window --
  widen the m range past 40 and/or prove no m exists via a closed-form
  argument on 3 | (x*2^m - 1) combined with the ===1 mod 4 constraint;
  (c) attempt an n=2/n=3 analogue of the reverse-recurrence
  x_{k+1}=4x_k+1 that generates the FULL n=1 species, rather than only
  characterizing single tower-tops.
- Gate 1 was pushed to k=400,000 (x at 799,999 bits) using a fixed 5s
  per-k push-budget and a 5,000,000 hard k-cap; neither budget nor cap
  was reached (the 5s budget triggered the stop, well under the
  5,000,000 cap) -- a future round with a larger time budget could push
  further, this was not a hard ceiling of the method, just this run's
  time allocation.

**Next required update:** none required by DESCENT_RULE_SPEC.md's
mandatory scope (gates 1-3 all passed exactly, matching the frozen
expectation). If a future round wants to chase gate 4's open threads
(n=2/n=3 congruence closure, the k≡0 mod 3 predecessor gap, or a
generalized k-step reverse recurrence), that is new work building on
this entry, not a continuation of an unfinished gate.

### 2026-07-05 - Backward Basin Certificate: mission gates 0-3 (BASIN_CERTIFICATE_SPEC.md)
**Status:** complete
**Work done:**
- Gate 0a: reconstructed the layer-0 species (4^k-1)/3, k=1..30, via
  `descent_common.species_member` (already on disk from the prerequisite
  DESCENT_RULE mission), confirmed S(x)=1 in one odd-step AND x≡1(mod4)
  for all 30 members. Script: `shell/descent_rule/gate0_gate1.py`.
- Gate 0b: reproduced the mod-3 predecessor-existence rule by DIRECT
  construction — for 6 odd t values in each of the 3 residue classes mod
  3 (18 t total), computed x=(t*2^j-1)/3 for j=1..20, tested integrality
  and oddness explicitly at every j, and cross-checked every found
  predecessor x by re-applying the forward odd-map and confirming
  S(x)==t exactly. Result: t≡0(mod3) -> 0 predecessors found across the
  full j=1..20 range for all 6 t's tested; t≡1(mod3) -> predecessors at
  EVEN j only (j=2,4,...,20, all 10 present for all 6 t's); t≡2(mod3) ->
  predecessors at ODD j only (j=1,3,...,19, all 10 present for all 6
  t's). Zero exceptions.
- Gate 1: derived LAYER 1/2/3 by TWO independently cross-checked
  methods — (a) backward construction x=(t*2^j-1)/3 over the prior
  layer's t-members and admissible j (by t mod 3), and (b) forward
  ground-truth enumeration (every odd x < BOUND, test whether S^n(x)
  lands in the species via the closed-form `is_one_step_species`
  applied to the n-th iterate). LAYER 1 backward-vs-forward sets matched
  after accounting for the literal-spec definition including any
  layer-0/layer-1 overlap (11 of LAYER 0's own 30 constructed members,
  those with S(x) also landing back in species after one more step,
  fall inside LAYER1's literal membership too — the spec's "LAYER n =
  odd x with S(x) in LAYER(n-1)" does not exclude x already in
  LAYER(n-1) itself). LAYER 2's backward-from-(truncated)-LAYER1 set
  matched its forward-ground-truth set EXACTLY (138==138) once LAYER 1
  was taken as literal-spec (with overlap). Congruence-class fit
  (residues mod 4,8,16,...,1024) computed for LAYER 1, 2, 3 via
  `fit_report()`/`residues_mod()`.
- Gate 2: coverage census over all 5,000,000 distinct odd x in
  [1,10^7), one forward-simulation per distinct x, cap MAX_STEPS=200,
  membership tested at every odd-step via the closed-form
  `is_power_of_two(3*cur+1)` + even-exponent test (no separate
  trajectory-simulation call inside the test itself). density(N)
  computed for N=0..200 (full table, 201 rows) via a difference-array
  cumulative count, written to
  `shell/descent_rule/gate2_density_table.csv`.
- Gate 3: characterized the complement (112 odd x out of 5,000,000
  with hit_step=None at N=200) — checked x≡0(mod3) specifically (can
  never be waypoints, only starts) and a residue-class breakdown mod
  2,3,4,8,9,16,32 for none_count and max_finite_hit per class.
- Script: `shell/descent_rule/gate2_gate3_census.py`. Two full runs:
  first run (`gate2_gate3_run.log` v1, superseded) surfaced the memo
  cap-bypass bug below and was killed mid-way through the (slow,
  unoptimized) residue breakdown before writing final results; second
  run (current `gate2_gate3_run.log`, `gate2_gate3_results.txt`,
  `gate2_density_table.csv`) is the one cited throughout this entry —
  it re-ran the FULL census from scratch (not resumed) after both the
  correctness fix and the residue-breakdown speed fix, so nothing in
  the cited numbers passed through the buggy code path.

**Paths abandoned & WHY:**
- Considered generating LAYER n purely by backward construction alone
  (spec's own suggested method) without a forward ground-truth
  cross-check. Abandoned as the SOLE method: backward construction from
  a necessarily-TRUNCATED prior-layer member list can miss small
  members of the next layer that would only be generated by t-values
  outside the truncation window (observed directly for LAYER 2 when
  cross-checking against a LAYER 1 truncated at t<2*10^6 — matched
  exactly in this run, but the risk is structural, not incidental, so
  the forward pass was kept as the primary ground truth throughout,
  backward construction as the cross-check/cheap-generation tool, not
  the reverse).
- Did NOT attempt to force LAYER 1/2/3 into a "clean" finite union of
  congruence classes once the residue-count-vs-modulus data (see
  Evidence) showed no convergence — per the spec's explicit instruction
  ("don't force a clean story that isn't there"), reported the actual
  observed growth instead (see Evidence / SYNTHESIS.md for the verdict).
- Did not extend Gate 1's census bound past 2,000,000 or push to LAYER
  4+: LAYER 3 already has 349 members inside that bound (vs LAYER 0's
  30, LAYER 1's 48, LAYER 2's 138) and shows no sign of the residue-set
  count leveling off (see Evidence); a LAYER 4 pass would need a
  materially larger bound to be informative and was judged out of scope
  given Gate 1's own honest-negative verdict was already clear by
  LAYER 3.

**Bugs/issues:**
- **BUG (harness, gate 2/3, correctness-critical, CAUGHT AND FIXED
  before any cited numbers were produced).** The memoization shortcut in
  `resolve_hit_step()` originally did `return steps + memo_val, path`
  whenever the walk hit an already-memoized value, with NO check that
  `steps + memo_val` stayed within `max_steps`. Since `memo_val` is the
  exact (unbounded) remaining-steps-to-species from that value's OWN
  orbit — independent of any particular caller's cap — a later start
  whose walk passed through an already-memoized value could get a
  combined total EXCEEDING the nominal 60-step cap used in the smoke
  test. Caught by direct inspection during a small-scale (odd x<200,000,
  MAX_STEPS=60) smoke test BEFORE the full 10,000,000-range run: the
  reported "max observed finite hit_step" was 137, impossible under a
  60-step cap. Traced by hand-tracing x=703 (memo-based walk returned
  hit_step=61) against a fresh, no-memo, no-cap direct simulation
  (confirmed x=703's TRUE first species-hit is at step 61, landing on
  species member 5) — the memo path was silently ignoring the cap
  entirely. Fixed by adding an explicit `if memo_val is None or steps +
  memo_val > max_steps: return None, path` guard before accepting the
  memo shortcut. Re-ran the same smoke test: max observed finite
  hit_step correctly capped at exactly 60, and a fresh no-memo
  resolution of x=703 under the 60-step cap correctly returned None.
  This bug, if uncaught, would have INFLATED density(N) at every N by
  crediting some x with a hit_step it could not have reached within the
  stated cap — exactly the kind of harness bug the mission brief warns
  "failure means a bug" about, except this is Gate 2/3 (genuine
  measurement, not a frozen theorem) so the fix was to the accounting
  machinery, not a reason to doubt any conjecture.
- **Performance issue (not a correctness bug), gate 3 residue-class
  report.** The first version of the per-residue-class breakdown
  (mod 2,3,4,8,9,16,32) re-scanned the FULL 5,000,000-entry hit_steps
  list once per (modulus, residue) pair — 2+3+4+8+9+16+32 = 74 full
  linear passes total. This made the reporting step the dominant cost
  of the whole script (the actual census walk itself took only ~30s;
  the naive residue breakdown was still running several minutes later
  and was killed deliberately, see Work done above). Fixed by bucketing
  ALL residues for a given modulus in a SINGLE pass (accumulate
  count/none_count/max_finite per residue simultaneously), cutting 74
  passes to 7. This is a wall-clock-only fix — the per-distinct-x
  accounting (every x counted in exactly one bucket per modulus, using
  its own already-resolved hit_step) is unchanged; verified by
  comparing bucket totals (sum of per-residue counts = 5,000,000 = the
  full census) after the fix.

**Course corrections:**
- Killed the first full-scale run mid-execution once it became clear
  the (still-correct, post-bugfix) residue-breakdown loop would take
  many more minutes than warranted for a reporting-only step; rewrote
  that section for O(1)-passes-per-modulus instead of O(residues), then
  re-ran the ENTIRE script from scratch (not resumed) so every number
  in this entry comes from one clean, fully-reproducible run.
- Registered the literal-spec ambiguity around whether LAYER n
  "excludes" members already in LAYER(n-1) — the spec's own wording
  ("LAYER n = odd x such that S(x) in LAYER(n-1)") does not exclude
  overlap, so Gate 1 reports BOTH the literal-spec set (with overlap)
  and the overlap-excluded "new members only" set, and used the literal
  set as the one cross-checked against backward construction and
  carried forward into the congruence-fit tables (see Evidence).

**Evidence:**
- Gate 0: `shell/descent_rule/gate0_gate1.py`, full output
  `shell/descent_rule/gate0_gate1_results.txt`. Gate 0a: 30/30 species
  members confirmed S(x)=1 and x≡1(mod4). Gate 0b: 18 t-values (6 per
  residue class mod 3), j=1..20 tested exhaustively per t —
  t≡0(mod3): 0 predecessors found in 6/6 cases; t≡1(mod3): predecessors
  at all 10 even j's (2..20) in 6/6 cases; t≡2(mod3): predecessors at
  all 10 odd j's (1..19) in 6/6 cases. Every found predecessor
  cross-checked S(x)==t exactly, 0 mismatches.
- Gate 1 layer sizes within census bound 2,000,000: LAYER 0 (species,
  first 30 constructed members, smallest 8: 1,5,21,85,341,1365,5461,
  21845) — LAYER 1: 48 members (smallest 15: 1,3,5,13,21,53,85,113,213,
  227,341,453,853,909,1365) — LAYER 2: 138 members (smallest 15: 1,3,5,
  13,17,21,35,53,69,75,85,113,141,151,213), backward-construction count
  EQUALS forward-enumeration count exactly (138==138) — LAYER 3: 349
  members (smallest 15: 1,3,5,11,13,17,21,23,35,45,53,69,75,85,93).
  Congruence-class residue counts (distinct populated residues out of m
  possible), mod 256: LAYER1=12/256 (4.69%), LAYER2=31/256 (12.11%),
  LAYER3=44/256 (17.19%) — growing both in absolute count and as a
  FRACTION of the modulus at each successive layer, i.e. NOT converging
  to a small fixed-size class list. LAYER1 mod4={1,3} (no
  discrimination at mod4 — covers both odd residues), LAYER2 mod4={1,3},
  LAYER3 mod4={1,3} (same, mod4 alone never discriminates any of the
  three layers checked). Full residue tables at every modulus tested
  (4,8,16,32,64,128,256,512,1024) in
  `shell/descent_rule/gate0_gate1_results.txt`.
- Gate 2: `shell/descent_rule/gate2_gate3_census.py`, full log
  `shell/descent_rule/gate2_gate3_run.log`, results
  `shell/descent_rule/gate2_gate3_results.txt`, density table
  `shell/descent_rule/gate2_density_table.csv` (201 rows, N=0..200).
  Census: 5,000,000 distinct odd x in [1,10,000,000), ONE forward
  simulation per x (merge-safe by construction — see METHODOLOGY
  docstring in the script). Wall clock: 30.009s (166,614 x/sec), peak
  RSS 235.62 MB, final memo size 2,499,968. density(0)=0.0000024
  (12/5,000,000, the literal species members themselves), density(10)=
  0.0052352, density(50)=0.5001166, density(100)=0.9628670,
  density(150)=0.9990890, density(200)=**0.9999776**
  (4,999,888/5,000,000 covered). Complement at N=200: exactly 112
  distinct odd x. Complement decay ratios at widening checkpoints
  (Fibonacci-spaced N=1,2,3,5,8,13,21,34,55,89,200): 1.0000, 0.9999,
  0.9997, 0.9982, 0.9883, 0.9391, 0.8030, 0.5736, 0.1741, 0.0003 —
  monotonically shrinking, with the steepest collapse in the tail
  (N=89->200 alone divides the complement by ~3,315x).
- Gate 3: same artifacts as gate 2. Complement (112 x) smallest 20:
  1723519, 2298025, 2585279, ..., 4637979; largest 20: 8842233, ...,
  9999913 — spread across the full census range, not concentrated at
  either end. x≡0(mod3) count 1,666,667 of the census, none-count only
  39 (0.0023% of that subclass) at N=200, max finite hit_step 200 (a
  cap artifact, not a floor). Per-residue-class table (mod
  2,3,4,8,9,16,32): every single residue class shows none_count in the
  single digits to double digits (out of subclass sizes from 165,000 to
  2,500,000) and max_finite_hit clustering at or just under 200 (the
  cap) — NO class shows none_count staying flat/large while max_finite
  also stays flat (which would indicate a hard floor); every class's
  none_count is small and its max_finite is near the cap boundary,
  consistent with "these just need a slightly larger N," not with
  structural exclusion.

**Not complete until:**
- Gates 0/1 are exact/theorem-level per the spec and both PASSED
  (0 exceptions in gate 0; gate 1's cross-checks matched exactly where
  checked). Gate 1's "closed form" question has an HONEST NEGATIVE
  answer within the scope tested (LAYER 1/2/3 do not collapse to a
  small fixed congruence-class list; the populated-residue fraction
  GROWS layer to layer) — this is reported as the actual finding, not
  chased further into LAYER 4+ (see Paths abandoned).
- Gate 2/3 are genuine measurement, not theorems: density(200)=0.9999776
  is exact for the 5,000,000-x census AT CAP N=200. It is NOT a proof
  that density->1 as N->infinity, nor a proof the 112 remaining x would
  resolve at some finite larger N (though the per-residue evidence
  argues strongly against a hard floor). A future round wanting a
  stronger claim would need: (a) push MAX_STEPS well past 200 on just
  the 112 residual x (cheap — 112 individual trajectories) to see if
  they resolve; (b) a LARGER census bound (10^8, 10^9) to test whether
  the 0.0000224 complement fraction itself keeps shrinking as the
  census range grows, not just as N grows within a fixed range.
- This entry's own verdict comparison against the frozen ~70%/~60%
  conjectures, and the connection (or lack thereof) to the death-shell/
  capacity picture, is in `SYNTHESIS.md` (see next section), not
  duplicated here.

**Next required update:** none required by BASIN_CERTIFICATE_SPEC.md's
mandatory gates (0-3 all executed, gate 0/1 exact, gate 2/3 measured
honestly against the frozen expectations). If a future round chases the
open items above (residual-112 individual resolution, larger census
bound, LAYER 4+ congruence growth), that is new work building on this
entry.

### 2026-07-05 - Cross-Instrument Synthesis (J1-J4): basin, shell, spectral, corridor

**Status:** complete

**Work done:**
- Read `renorm_check/shell/SYNTHESIS_FOUR_INSTRUMENTS_SPEC.md` and
  `renorm_check/shell/LEDGER_SYNTHESIS_POLICY.md` in full before starting,
  per mandatory instruction.
- Created `renorm_check/shell/synthesis_four/` and three scripts:
  `j1_set_compare.py`, `j2_rho_fit.py`, `j3_convergents.py`, each writing
  its own `j{1,2,3}_output.txt` alongside stdout.
- **J1**: reconstructed the FULL 112-element basin residual complement
  (gate2_gate3_results.txt only published smallest/largest 20, not the
  full 112) by re-implementing gate2_gate3_census.py's exact per-x rule
  (`descent_common.is_power_of_two` closed-form species test + one-odd-
  step map), UNMEMOIZED (no cross-x memo — a correctness simplification,
  not a rule change, since the memo is documented in the census script as
  a pure speed optimization). Verified the unmemoized reproduction against
  a partial published checkpoint (see Bugs/issues) before trusting it at
  full scale (10,000,000). Then computed the death shell's dead set S(m)
  for m=2..8 at two corridor widths (C=12, C=23) via direct reuse of
  `shell_probe.py`'s `dead_profile()` and `embedding/automaton.py`'s
  `run_heartbeat`, and tested every one of the 112 residual x for (a)
  domain membership (x mod 3 != 0, the shell's domain restriction) and
  (b) landing in S(m) at m=2..8.
- **J2**: fit `gate2_density_table.csv`'s complement_density(N), N=0..200,
  against three forms — (a) A·rho^(N/53) with rho=0.960647 FIXED
  (per-step rate rho^(1/53) held fixed, only amplitude A free), (b)
  A·b^(N/53) with b=0.063099 FIXED similarly, (c) A·r^N with r free via
  ordinary log-linear least squares — over four N-ranges (FULL 0-200,
  EARLY 0-20, TAIL 150-200, DEEP TAIL 170-200), reported R^2 and RSS on
  log-complement for each. Also tabulated empirical per-step ratios
  complement_density(N)/complement_density(N-1) for N=146..200 against
  the two fixed-rate predictions, and ran a held-out adversarial check
  (fit free rate on N=150-175, predict N=180-200, report relative error).
- **J3**: computed continued fractions of log2(3) and 2-log2(3) to 60
  mpmath digits, listed convergents p_k/q_k for k=0..13 for both, located
  the exact index of 84/53 (alpha's convergents) and 22/53 (beta's
  convergents), verified the reciprocal relationship (53/22 is a
  convergent of 1/beta, not of beta itself — beta's own convergent is
  22/53), and verified the exact CF-reflection identity connecting
  alpha's and beta's term lists (beta=2-alpha implies terms
  [0,1,a1-1,a2,a3,...] when alpha=[1,a1,a2,...] with a1>=2; alpha's a1=1
  here so the a1==1 merge branch was used instead — see Evidence). Then
  swept M_edge(C) for C=1..14 and tested exact-match candidates linking
  C=11 (corridor phase-transition width) to the spectral exponent 6 or
  convergent-index 6 (M_edge(11)==84? convergent-index==C+1? 11==2*6-1?
  cumulative partial-quotient sums near index 6? 11 appearing anywhere
  as a p_k/q_k in either convergent list?).
- **J4**: synthesized the J1-J3 verdicts into the precise conditional
  statement (see SYNTHESIS.md entry) naming the one shared obstruction
  (no fixed-modulus residue-system closure) across all four instruments,
  with the specific artifact/passage from each instrument that
  instantiates it.

**Paths abandoned & WHY:**
- Considered reusing `gate2_gate3_census.py`'s memoized `resolve_hit_step`
  verbatim (import it directly) to save runtime on J1's reconstruction.
  Abandoned: the memo dict is a persistent, order-dependent global keyed
  by first-seen value, and importing/reusing it as a library function
  inside a fresh script risks subtly different behavior if imported
  functions were called in a different x-order or with the module-level
  dict pre-populated by prior module import side effects elsewhere in the
  synthesis run. Reimplemented an UNMEMOIZED per-x walker instead (slower:
  ~2m40s vs the original's 30s) using only `descent_common.is_power_of_two`
  (already-shared, gate-0-audited primitive) so correctness rests on the
  smallest possible reused surface, then cross-checked it against a
  published intermediate checkpoint before trusting the full run (see
  Bugs/issues). This trades performance for an independent, from-scratch
  verification path — appropriate for an audit whose entire point is
  cross-checking, not for a production census.
- Considered treating "sum of partial quotients of alpha's CF up to the
  84/53 term equals 11" (matches C=11 exactly) as a candidate positive
  J3 finding. Abandoned after adversarial check: the cumulative-sum
  sequence (1,2,3,5,7,10,11,16,18,41,43,45,46,47) is monotonically
  increasing through small integers by construction and was GUARANTEED
  to pass near any small target somewhere in its run; there is no
  independent motivation (from either instrument's own math) for "sum of
  partial quotients up to a specific convergent index" as a meaningful
  quantity, and the match is a single untested ad hoc statistic with no
  null-model comparison — structurally the same failure mode as the
  refuted 9/4 edge-jump law (see SYNTHESIS.md "RED-TEAM VERDICT: the 9/4
  edge-jump law is an ARTIFACT"). Reported as OPEN/no-relation-found in
  J3, per the spec's explicit instruction not to repeat that failure
  mode.
- Did not attempt to extend J1's residue comparison to m>8 (3^8=6561):
  S(8) already has 4,009 dead residues out of 4,374 nz residues mod 3^8
  (91.66% base rate) — pushing m higher only inflates the base rate
  further (the shell's own P1 result: dead set density grows with m),
  which would make ANY finite integer set's hit-rate approach 100% by
  m's growth alone, not by any genuine link to the basin object. Testing
  further m would not sharpen the J1 verdict, only reproduce the
  already-quantified base-rate-driven ceiling.

**Bugs/issues:**
- First J1 correctness check FAILED: an early version's `hit_step_of`
  reused a `memo` dict across the reconstruction call in a way that
  produced a plain count of 1 residual x under census bound 2,000,000,
  contradicting the published log line `... 2,000,000 distinct odd x
  processed ... none-so-far=12`. Root cause: mismatched units — the
  census log's checkpoint counts DISTINCT ODD x PROCESSED (the k-th odd
  number is 2k-1), not literal x-value bound. Fixed by testing at
  census bound 4,000,000 (= 2*2,000,000-1, the correct x-value bound for
  "2,000,000 distinct odd x processed") — reproduced none-so-far=12
  exactly, THEN ran the full bound-10,000,000 reconstruction. This
  checkpoint cross-check is why the full run was trusted before use;
  without it the 112-list could have silently been wrong at full scale.
- No other bugs; each script's output was sanity-checked against a
  published number before being treated as verdict evidence (J1 against
  the smallest-20/largest-20 list; J3's CF convergents against F1's
  published "22/53 convergent of 2-log2(3), next 127/306" claim — both
  matched exactly, see Evidence).

**Course corrections:**
- Original plan for J1 was to test containment against a single
  corridor width C. Changed to testing TWO widths (C=12, C=23) and
  explicitly confirming `dead_union_12 == dead_union_23` as sets before
  using either, per P2's own universality claim — this was a stronger,
  more adversarial check than the minimum the spec required, added
  because the whole J1 question turns on the dead set being a
  well-defined single object independent of C.
- Original plan for J2's form (b) used b's per-m spectral-precision-level
  rate directly as a per-odd-step rate. Corrected in the write-up (not
  the fit mechanics) to explicitly flag the unit assumption: b is
  measured as a per-increment-of-m (precision level) decay in the
  spectral data, and treating b^(1/53) as a per-ODD-STEP basin rate
  requires assuming m-increments and heartbeats are the same unit, which
  is the SAME assumption already implicit in using rho this way, so both
  (a) and (b) carry an identical unit caveat, stated explicitly rather
  than silently assumed.

**Evidence:**
- `renorm_check/shell/synthesis_four/j1_set_compare.py`,
  `j1_output.txt` (51 lines). Full reconstructed 112-x complement
  verified IDENTICAL to published smallest-20/largest-20
  (`descent_rule/gate2_gate3_results.txt` lines 123-124): exact match,
  `matches published smallest-20/largest-20 exactly: True`. Domain
  split: 39/112 (34.8%) have x%3==0 (OUTSIDE the shell's domain, which
  is defined only on r%3!=0, per `shell_probe.py`'s `nz = r % 3 != 0`);
  73/112 (65.2%) are eligible for comparison. Of those 73: hit rate in
  S(m) rises from 20/73 (27.4%, m=2) to 70/73 (95.9%, m=8), while S(m)'s
  OWN base rate among nz residues mod 3^m rises from 33.3% (m=2) to
  91.66% (m=8) over the same range — i.e. the observed hit rate tracks
  the base rate, not a fixed excess. Binomial z-score at m=8: expected
  hits under the null (each of 73 x independently landing in S(8) at
  its 91.66% base rate) = 66.9, observed = 70, sd = 2.36, z = 1.31 — NOT
  significant (|z|<2). `dead_union_12 == dead_union_23` confirmed
  identical (True) at every m=2..8 tested, confirming P2's
  C-independence claim independently.
- `renorm_check/shell/synthesis_four/j2_rho_fit.py`,
  `j2_output.txt` (100 lines). DEEP TAIL (N=170-200, the fairest
  region): (a) rho-fixed R²=0.0223, RSS=10.89; (b) b-fixed R²=0.9378,
  RSS=0.693; (c) free rate R²=0.9834, RSS=0.185, r=0.9357. Free rate
  beats b-fixed by R² margin +0.046 and beats rho-fixed by +0.961; RSS
  ~3.7x lower than b-fixed and ~59x lower than rho-fixed. rho-fixed is
  a categorical failure at every N-range tested (R²<0.36 everywhere,
  R²=0.022-0.026 in FULL/TAIL/DEEP-TAIL). Held-out adversarial check
  (fit N=150-175, predict N=180-200): systematic -13% to -29% relative
  error, i.e. even the BEST-performing free-rate fit under-predicts the
  deep tail once honestly held out — the decay is NOT clean single-rate
  geometric even in the "fair" tail region. Empirical per-step ratios
  N=146..200 scatter 0.85-0.97 (mean ~0.93, high step-to-step noise from
  small integer counts, e.g. complement_count=112 at N=200) — neither
  rho^(1/53)=0.999243 nor b^(1/53)=0.949203 sits inside that empirical
  scatter's central tendency; b^(1/53) is the closer of the two (0.9492
  vs observed range's rough center ~0.93) but still outside most
  individual-step ratios.
- `renorm_check/shell/synthesis_four/j3_convergents.py`,
  `j3_output.txt` (verified against F1's published claim). CF(log2(3))
  = [1,1,1,2,2,3,1,5,2,23,2,2,1,1]; 84/53 at k=6 exactly. CF(2-log2(3))
  = [0,2,2,2,3,1,5,2,23,2,2,1,1,55]; 22/53 at k=5 exactly (F1's "next:
  127/306" also reproduced exactly at k=6). 53/22 is NOT itself a listed
  convergent of beta=2-log2(3) (only its reciprocal 22/53 is); 53/22
  IS an exact convergent of 1/beta at k=4. Reflection identity
  beta=[0,1,a1-1,a2,...]-vs-merge-branch verified: alpha's a1=1 forces
  the merge branch (1-f=[0,a2+1,a3,...]), predicted prefix
  [0,2,2,2,3,1,5,2,23,2,2,1,1] matches the actual computed beta CF
  prefix EXACTLY (13/13 terms). C=11/exponent-6: M_edge(11)=28!=84;
  convergent-index-of-84/53 (k=6) != C+1=12; the one numeric coincidence
  found (cumulative partial-quotient sum through k=6 equals 11 exactly)
  was adversarially rejected as an artifact of a monotonically-increasing
  small-integer sequence with no independent structural motivation (see
  Paths abandoned) — 11 does not appear as any p_k or q_k in either
  convergent list at all.

**Not complete until:**
- J1's verdict (different objects, no set equality, no above-chance
  overlap) is exact and adversarially checked (two corridor widths,
  binomial null test) within the SCOPE tested (m=2..8, one census bound
  of 10,000,000, N-cap 200). It is not a proof that no relation could
  ever be found between the two objects at larger m or under a different
  residue parametrization — only that the straightforward, most-favorable
  comparison attempted here shows none.
- J2's verdict (basin decay is NOT cleanly rho-governed; free rate wins
  but even the free rate fails held-out prediction) rests on ONE
  complement_density curve (one census, one N-cap). A future round
  wanting a stronger claim would need a second, independent basin census
  at a different bound to check if the "true" per-step rate is stable
  across census scales, and/or a piecewise (not single-rate) fit to the
  tail, since the held-out failure suggests even the tail is not pure
  single-rate geometric decay.
- J3's CF work is exact and fully verified (finite integer arithmetic,
  no floats in the load-bearing convergent computation — mpmath was used
  only to seed the initial high-precision alpha/beta values before
  handing off to exact-integer CF/convergent recurrences). The C=11/
  exponent-6 question is honestly OPEN: no candidate tested here
  produced a non-coincidental match. A future round could try other
  candidates (e.g. relating C=11 to the corridor's OWN internal
  structure rather than to alpha/beta's convergent lattice at all) but
  none is registered here as promising.
- J4's synthesis statement (SYNTHESIS.md) is a synthesis of already-
  measured/proven facts from the four instruments' own prior work plus
  this round's J1-J3 checks; it does not itself run new proofs.

**Next required update:** none required by
SYNTHESIS_FOUR_INSTRUMENTS_SPEC.md's four joins (J1-J4 all addressed
with frozen-prediction comparisons stated in SYNTHESIS.md). A future
round extending J2 (piecewise/second-census fit) or J3 (alternative
C=11 candidates) would build on this entry.

### 2026-07-05 - IME Reframe of J2/J4 (course correction relayed by peer session, per architect/IME-primer.md)

**Status:** complete

**Work done:**
- Read `/mnt/ForgeRealm/collatz-experimental-data/IME-primer.md` in full
  before doing anything else, per the peer session's relayed instruction.
- This round does NOT redo J1 or J3 (both stand as-is per the peer
  message: J1 was already a clean set-comparison, not an agreement test;
  J3's C=11/exponent-6 check already covers the "consecutive tier"
  framing — see Course corrections below for the explicit carry-forward
  statement).
- Built `renorm_check/shell/synthesis_four/j2j4_ime_reframe.py`
  (+`j2j4_ime_output.txt`) to re-interpret round-1's J2 raw fit numbers
  (rho R²=0.022, b R²=0.938, free R²=0.983, held-out -13%..-29% error —
  NOT recomputed, reused verbatim from `j2_output.txt`) under IME's
  actual claim: incommensurable measurement geometries forced to
  interact produce an EMERGENT DEPTH HIERARCHY with tiers set by the
  convergent ladder of log2(3) (53, 84, 306, 485, 665, 1054, 15601,
  24727, ...), not "do the raw rates match."
- Pre-registered (BEFORE any ladder lookup, written into the script's
  own docstring as STEP 0) which instrument-depth maps to which role:
  corridor and spectral are already heartbeat-native (53 built in by
  construction, verified exactly in round-1 J3) so they are NOT tested
  against the ladder they are themselves built from (that would be
  circular); the ladder test is applied to the BASIN's e-folding depth
  (converted from its native odd-step unit to heartbeats) and the death
  shell's own m-axis scale, the two instruments whose native units are
  not already locked to 53.
- Computed basin characteristic (1/e-folding) depth via exact
  `-1/ln(rate)` from round-1's three already-fit rates (DEEP_TAIL,
  TAIL, FULL free-rate fits), converted to heartbeat units (divide by
  53), and located the nearest convergent-ladder value for each.
- Ran an adversarial null-model sweep: r=0.900 to 0.970 in steps of
  0.001 (70 points spanning the full empirically-plausible basin-rate
  range seen across all N-range fits and the per-step ratio scatter),
  checking what fraction land within 10% of ANY ladder value by pure
  construction (not because of any Collatz-specific structure).
- Constructed a genuine held-out prediction per the peer's mandatory
  discipline: IF the basin's heartbeat-depth (~15 heartbeats) were
  ladder-governed, solved M_edge(C)=15..16 for C and checked whether
  that C is independently flagged as structurally special anywhere in
  the corridor's OWN prior measurement work (it solves to C~5-6; the
  corridor's own flagged special widths are C=11 and C=148 — a genuine,
  falsifiable, checkable-before-the-fact prediction that FAILED).
- Assessed whether the four instruments' own native structure actually
  matches GHOST_PRECISION's specific shape (a fixed POPULATION FRACTION
  stabilizing at a fixed low resource level — 50%@1bit, 77-89%@2bit) as
  opposed to merely "some two-regime or growing/decaying structure
  exists somewhere," checked instrument by instrument.

**Paths abandoned & WHY:**
- Considered testing the basin's RAW odd-step e-fold depth (14.4-17.3)
  directly against the ladder without heartbeat conversion. Abandoned:
  the ladder is defined in heartbeat/precision-level units by
  construction (convergents of log2(3), the SAME irrational the 53-step
  heartbeat itself is built from) — comparing a raw odd-step count
  against it with no unit conversion would be comparing incommensurable
  units on their face, which is a worse methodological error than the
  conversion's own caveats. Heartbeat conversion was used, with the
  resulting tiny value (~0.28-0.33 heartbeats) reported honestly rather
  than discarded once it manifestly failed to land near any tier.
- Considered testing the spectral m-axis (b's e-fold depth in
  precision-level units, ~0.36 m-levels) and the death shell's m=359
  scale against the SAME heartbeat ladder used for the basin. Abandoned
  per the pre-registration rule stated in Work done: both spectral and
  corridor are already heartbeat-native BY CONSTRUCTION (53 appears
  directly in their own defining formulas, not as a fitted parameter),
  so testing them against a ladder built from the same constant they
  already contain would not be a test of anything — it would recover
  the already-known, already-verified J3 fact (53 shared exactly) under
  a new name, not a new IME-specific finding.
- Considered accepting the basin's nearest-ladder-value match (heartbeat
  depth ~0.28-0.33, nearest ladder value 1, i.e. the FIRST trivial
  convergent p/q=1/1) as a "match" since it's the smallest available
  ladder entry. Abandoned: the relative error is 67-73% even against
  the loosest, most trivial ladder rung available — this is not a
  near-miss worth registering as suggestive, it is a categorical
  non-match, and reporting it as anything softer would repeat exactly
  the failure mode this program has now caught three times (9/4,
  prime-19, and this).

**Bugs/issues:**
- Caught and fixed a self-authored framing error before finalizing
  output: an early draft of the script's inline commentary described
  "12 (0-indexed convergent denom)" as being outside "our HEARTBEAT-
  relevant subset," a confusing and unnecessary aside given the actual
  arithmetic (basin depth in raw odd-steps, ~14-17, converted correctly
  to ~0.28-0.33 heartbeats by dividing by 53) was already correct and
  did not need defending — the number itself, not the framing, is the
  finding. Rewrote the surrounding prose to state the honest scale
  comparison directly (basin's 1/e-fold happens within under 1/3 of a
  SINGLE heartbeat, nowhere near the ladder's smallest nontrivial tier
  of 53) instead of relitigating which ladder entries "count." No
  arithmetic was wrong; only the explanatory text was confusing and was
  corrected before this entry was finalized.

**Course corrections:**
- The peer message asked explicitly whether the existing C=11/
  exponent-6 check (round-1 J3) "already covers" the reframed
  "consecutive tier index" question. It does: round-1 J3 tested
  M_edge(11) against 84 (no match), the convergent-index of 84/53 (k=6)
  against C+1=12 (no match), and one coincidental cumulative-partial-
  quotient-sum match (=11 at k=6) that was adversarially rejected as a
  guaranteed pass-through artifact. "Does the tier INDEX advance by
  exactly 1 between corridor-C=11 and spectral-exponent-6" is precisely
  the C+1-vs-convergent-index-k check already run (12 vs 6, not equal,
  not off-by-one either — 12 is exactly double 6, which was not flagged
  as a candidate in round 1 and is checked now: see Evidence). No new
  script was needed; the verdict (OPEN, no relation found) is carried
  forward unchanged, per the peer's own instruction not to re-derive.
- The peer's message treated "raw-rate disagreement is the IME-
  predicted signature, not a fit failure" as the operative correction.
  This round's course correction is to make explicit, in both this
  ledger entry and the SYNTHESIS entry, that round-1's J2 NUMBERS are
  unchanged and reused verbatim — only the INTERPRETATION frame changed
  — and that the reframed test (characteristic-depth-hierarchy vs
  convergent ladder, with mandatory pre-registration and held-out
  prediction) is a genuinely NEW and independently falsifiable test,
  not a repackaging of the same negative result under looser standards.
  It returned a NULL result under the new frame too — this is reported
  as a null of the IME-specific claim, not as a re-confirmation of the
  original (already-superseded) "rho does not govern basin" framing.

**Evidence:**
- `renorm_check/shell/synthesis_four/j2j4_ime_reframe.py`,
  `j2j4_ime_output.txt`. Basin characteristic (1/e-fold) depths (exact
  `-1/ln(rate)` from round-1's already-fit rates, reused verbatim):
  DEEP_TAIL (r=0.935710) = 15.049 odd-steps = 0.2839 heartbeats;
  TAIL (r=0.932844) = 14.385 odd-steps = 0.2714 heartbeats;
  FULL (r=0.943803) = 17.290 odd-steps = 0.3262 heartbeats. Nearest
  ladder value in all three cases: 1 (the trivial first convergent),
  at 67.4%-72.9% relative error — a categorical non-match, not a
  near-miss. Adversarial null-model sweep (r=0.900..0.970, step 0.001,
  70 points): 0 of 70 (0.0%) land within 10% of ANY ladder value —
  confirms the non-match is not an artifact of an unlucky choice of
  rate; the entire plausible basin-rate range misses the ladder
  cleanly. Held-out prediction: M_edge(C)=15 heartbeats solves to
  C≈5.23 (nearest integer C=5, M_edge(5)=14 exactly, the closest
  achievable integer-C value); M_edge(C)=16 solves to C≈5.64 (nearest
  integer C=6, M_edge(6)=16 exactly) — neither C=5 nor C=6 is flagged
  anywhere in the corridor's own prior measurement work as structurally
  distinguished (the corridor's own flagged widths are C=11, the
  phase-transition point, per "STANDING PICTURE UPDATE," and C=148, the
  F1 divergence point) — the held-out prediction FAILS cleanly.
  C+1-vs-convergent-index doubling check (new candidate, registered and
  tested in this round): C+1=12 is exactly 2x the convergent index k=6
  of 84/53 — this candidate was tested and IS an exact integer relation
  (12=2*6), but is flagged as almost certainly a second reverse-fit-
  shaped coincidence for the same reason the cumulative-partial-quotient
  match was rejected in round 1: C+1=12 for C=11 is fixed by the
  corridor's own definition regardless of any convergent structure
  (12 is just "the phase-transition width plus one"), and needing a
  factor of exactly 2 between two independently-arbitrary small
  integers (12 and 6) is exactly the kind of small-number coincidence
  the null-model discipline in this same round demonstrates is cheap —
  no independent held-out test was constructed for it (unlike the
  basin case above) because no second, structurally-motivated prediction
  falls out of "C+1 = 2*convergent-index" the way "M_edge(C) at the
  basin's own depth predicts a specific C" did; reported as UNTESTED/
  NOT ELEVATED rather than confirmed, consistent with the "no candidate
  survived adversarial checking" carry-forward verdict from round 1.
  Bulk/tail shape check (instrument-by-instrument, see script output):
  none of the four instruments' native structure reproduces
  GHOST_PRECISION's specific population-fraction-at-fixed-depth shape;
  each has a DIFFERENT kind of two-regime or growing structure (basin:
  no stable single rate at all, not even one bulk/tail split; shell:
  monotonically growing dead-mass, no fixed fraction; spectral:
  fixed-C-vs-variable-C dichotomy, not a population split; corridor:
  single width-threshold divergence, not a population-fraction split).

**Not complete until:**
- This round's NULL verdict (no convergent-ladder alignment, no
  GHOST_PRECISION-shaped hierarchy) is exact and adversarially checked
  within the SCOPE tested: three basin fit-range rates, the ladder
  entries reproduced from round-1 J3, one held-out corridor-width
  prediction, and a instrument-by-instrument bulk/tail shape comparison.
  It is not a proof that NO characteristic-depth hierarchy could ever be
  constructed from these four instruments under some OTHER unit
  convention or pairing — only that the pre-registered, most natural
  pairing attempted here (and the one the peer message's own framing
  pointed at) shows none.
- The untested C+1=2*k candidate (Evidence, above) is flagged but not
  resolved either way — a future round wanting to close it would need
  to construct an independent held-out prediction from it (the way the
  basin case was tested against corridor structure) before it could be
  elevated above "untested coincidence."
- This entry's own verdict comparison against the architect's frozen
  "~60%, genuinely open" IME-hierarchy prediction is stated in
  SYNTHESIS.md (see next section), not duplicated here.

**Next required update:** none required by the peer session's relayed
reframe request (J2/J4 re-interpreted under IME, new adversarial checks
run, NULL verdict reported against the architect's frozen prediction in
SYNTHESIS.md). A future round could pursue the flagged-but-unresolved
C+1=2k candidate, or test IME against a fifth, differently-constructed
Collatz instrument not yet built.

### 2026-07-07 - W7B C=31 High-Capacity Sparse Edge Receipt

**Status:** complete

**Work done:**
- Audited the W7B high-capacity sparse sweep artifacts after the detached
  C=31 follow-up finished.
- Confirmed the main C=27..31 sweep correctly treated the first C=31 result
  as a chosen-cap wall, not an edge: `state_cap=64,000,000` exceeded at
  m=48 with `n_exact=69,084,627`, `first_dead=None`,
  `genuine_death=False`.
- Confirmed `run_c31_highcap.py` re-ran the frozen validation gate
  (C=16=93, C=23=163, C=26=205) and then completed C=31 under raised caps:
  `state_cap=120,000,000`, `rss_cap_mb=28,000`.
- Created the missing local findings file required by the W7B order:
  `renorm_check/shell/underlock/w7b_deep/W7B_FINDINGS.md`.
- Updated the stale `RESUME_STATE.md` block from "C=31 high-cap in progress"
  to "complete"; no C=31 process is running anymore.

**Paths abandoned & WHY:**
- The 64M-cap C=31 result is abandoned as an edge candidate because it ended
  on a resource cap with no observed death. It remains valid as a wall
  receipt and as the reason the high-cap follow-up was launched.
- No attempt was made to infer C=32 from the C=31 high-cap run. W7B gates
  require each new C to carry its own validation/run receipt and death
  certificate.

**Bugs/issues:**
- The high-cap driver had an earlier monotonicity-seed bug recorded in
  `RESUME_STATE.md`: `prev_edge` was hardcoded to 205 instead of seeded from
  M(30)=282. The follow-up run fixed that before trusting C=31.
- `RESUME_STATE.md` had become stale after the detached process finished:
  it still said blocks 3..8 were in progress. This ledger update corrected
  that file and wrote the result into the permanent ledger.

**Course corrections:**
- C=31 changed status from "wall at chosen 64M cap, edge unknown" to
  "validated genuine-death edge" after the 120M-state high-cap follow-up.
- The proper next unresolved cell is now C=32, not C=31.

**Evidence:**
- `renorm_check/shell/underlock/w7b_deep/sweep_output.log`: validated
  C=27=208, C=28=263, C=29=265, C=30=282, then stopped honestly at the
  C=31 64M wall (`state cap 64000000 exceeded at m=48`,
  `n_exact=69084627`, `first_dead=None`, `genuine_death=False`).
- `renorm_check/shell/underlock/w7b_deep/run_c31_highcap.log`: frozen gate
  passed (C=16=93, C=23=163, C=26=205); C=31 completed with
  `M(31)=284`, `first_dead=285`, `peak_live=73,462,829`,
  `wall=None`, `genuine_death=True`, `elapsed_sec=48,854.99644827843`.
- `renorm_check/shell/underlock/w7b_deep/sweep_full.json` and
  `sweep_partial.json`: both contain the final C=31 high-cap receipt:
  `{"C":31,"edge":284,"first_dead":285,"peak_live":73462829,
  "wall":null,"elapsed_sec":48854.99644827843,"blocks_done":8,
  "genuine_death":true}`.
- `renorm_check/shell/underlock/w7a_renorm/w7a_new_edges.txt` now records
  genuine-death edges only:
  C=27 208, C=28 263, C=29 265, C=30 282, C=31 284.
- Representation receipt from `RESUME_STATE.md`: lean frontier storage
  reduced the profiled bytes/state from about 554 to about 313 and reduced
  the full C=26 sweep peak RSS from about 1315.4 MB to about 725.4 MB.
  C=31 high-cap peaked at about 16,773 MB RSS with 73,462,829 live states.

**Not complete until:**
- C=31 itself is complete and ledgered.
- The W7B sweep beyond C=31 is not complete. C=32 requires a fresh run with
  the same frozen validation gate, monotonicity gate, wall-vs-edge
  distinction, and a new death certificate.

**Next required update:** after any C=32+ run completes, append only
genuine-death edges to `w7a_new_edges.txt`, update `W7B_FINDINGS.md`,
and add a new ledger/synthesis entry. If the next run hits a cap, record it
as a wall, not an edge.
