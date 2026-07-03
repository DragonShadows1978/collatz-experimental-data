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
