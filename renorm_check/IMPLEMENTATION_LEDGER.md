# Renormalization Recon — Implementation Ledger

Tracks execution of the work orders (W1–W4) registered in SYNTHESIS.md.
Per the execution notes: updated after every completed step, commit after
every completed work item.

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
