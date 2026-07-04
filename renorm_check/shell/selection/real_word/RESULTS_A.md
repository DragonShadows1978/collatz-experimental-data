# Design A Results — Does the real word's aperiodicity bite at all?

Per `renorm_check/shell/W6C_SELECTION_ORDER.md`, Design A section (dir:
`shell/selection/real_word/`). Executed 2026-07-03. Runner:
`run_design_a.py` (this directory); raw logs `run_design_a.log` /
`progress_a.log`; raw data `a1_results.json` / `a2_results.json`.

No git commits made. No files outside this directory touched.

## Executive summary

- **A1** (m=2..13, steps 106 & 159, true vs 53-periodicized word):
  24/24 rows show identical D(m), matching the registered prediction
  on its face. **But the true word and the periodicized tiling are
  letter-for-letter identical for k=0..357** (first divergence at
  k=358 — the same point already on record as the m=359 divergence
  in `shell_probe.log`/SYNTHESIS F8). Since steps=106 and steps=159
  only ever read credits k=0..158, **A1 as specified could not have
  produced a differing row regardless of the mechanism in question** —
  the comparison is a valid, correctly-executed sanity check (and a
  useful one, extending the steps=53 identity control to 2–3
  heartbeats), but it does not test whether the corridor sees
  aperiodicity, because no aperiodicity was present in the inputs at
  these step counts. This is the single most important finding of
  Design A and is reported prominently per the honest-reporting law.
- **A2** (window slide, m ∈ {8,10}, steps 53..106): confirms the
  registered prediction — variation exactly 1 at both m, positive
  correlation with window support-count (r ≈ 0.37–0.42), no drift.
- No margin-<2 rows anywhere; no reruns needed; runtime 407.7s,
  peak RSS ~284MB, both far inside budget.

## Machinery and exactness

- True word: `automaton.credit` from `renorm_check/embedding/automaton.py`
  — exact via `bit_length` on Python bigints (`floor(k*log2(3)) =
  (3**k).bit_length() - 1`), no floats. Reused directly, not
  reimplemented.
- Periodicized word: the true word's first 53 credits `c_0..c_52`
  (computed once via `automaton.credit`), tiled cyclically —
  `credit_periodic(k) = tile[k % 53]`.
- Own int32-array vectorized heartbeat runner (`run_heartbeat` in
  `run_design_a.py`), same residue-permutation mechanics as
  `toy_automaton.run_heartbeat_generic` (gather/scatter over boolean
  liveness arrays per deficit level), parameterized by a credit
  function. Permutation arrays cast to `int32` per the work order's
  memory-guard instruction (all values < 3^13, well inside int32 range).
- D(m) readout: `D = C − d` for the largest live deficit `d` with a
  live terminal (r ≡ 1 mod 3^m) — i.e. min ceiling-distance of a live
  terminal, matching `shell_probe.py`'s P5 definition exactly. Margin
  reported = that terminal's distance from the corridor floor (`d`
  itself); the work order's "widen C and rerun if margin < 2" rule
  reads off this number. **C = 12 fixed throughout, as specified.**
  No row anywhere had margin < 2 (see tables below) — no rerun at wider
  C was needed.

## Sanity checks (both passed cleanly, logged in `run_design_a.log`)

1. **P5 reproduction** — true word, C=10, steps=53, m=2..12: all 11 rows
   matched `shell_probe.log`'s P5 table exactly
   (D = 0,1,1,2,2,2,3,3,4,4,4).
2. **True ≡ periodicized at steps=53** — checked C=12, m=2..13: full
   boolean state-array identity (`live_by_d[d]` equal for every
   d=0..12, not just the D readout) confirmed for every m. This is the
   required code-sanity control (identical by construction); it held
   with no exceptions.

## A1 — True word vs 53-periodicized word, m=2..13, steps=106 and 159

Registered prediction (Fable, not ours): **identical D(m) everywhere**
— the corridor cannot see aperiodicity at these scales.

| m  | steps | D_true | D_periodicized | equal? | margin (true / periodic) |
|----|-------|--------|-----------------|--------|---------------------------|
| 2  | 106   | 0      | 0               | YES    | 12 / 12 |
| 3  | 106   | 1      | 1               | YES    | 11 / 11 |
| 4  | 106   | 1      | 1               | YES    | 11 / 11 |
| 5  | 106   | 2      | 2               | YES    | 10 / 10 |
| 6  | 106   | 2      | 2               | YES    | 10 / 10 |
| 7  | 106   | 2      | 2               | YES    | 10 / 10 |
| 8  | 106   | 3      | 3               | YES    | 9 / 9 |
| 9  | 106   | 3      | 3               | YES    | 9 / 9 |
| 10 | 106   | 4      | 4               | YES    | 8 / 8 |
| 11 | 106   | 4      | 4               | YES    | 8 / 8 |
| 12 | 106   | 4      | 4               | YES    | 8 / 8 |
| 13 | 106   | 5      | 5               | YES    | 7 / 7 |
| 2  | 159   | 0      | 0               | YES    | 12 / 12 |
| 3  | 159   | 1      | 1               | YES    | 11 / 11 |
| 4  | 159   | 1      | 1               | YES    | 11 / 11 |
| 5  | 159   | 2      | 2               | YES    | 10 / 10 |
| 6  | 159   | 2      | 2               | YES    | 10 / 10 |
| 7  | 159   | 2      | 2               | YES    | 10 / 10 |
| 8  | 159   | 3      | 3               | YES    | 9 / 9 |
| 9  | 159   | 3      | 3               | YES    | 9 / 9 |
| 10 | 159   | 4      | 4               | YES    | 8 / 8 |
| 11 | 159   | 4      | 4               | YES    | 8 / 8 |
| 12 | 159   | 4      | 4               | YES    | 8 / 8 |
| 13 | 159   | 5      | 5               | YES    | 7 / 7 |

**Result: 24/24 rows identical. Zero disagreements between the true
word and its 53-periodicized tiling, at both steps=106 and steps=159,
across the full m=2..13 range. No row triggered the "differs — report
loudly" branch; none needed the double-check rerun (the runner logs a
rerun automatically on any mismatch — the branch was never entered).**

**Verdict: matches the registered prediction's LETTER (identical D(m)
everywhere), but the intended TEST did not actually run — and this
must be reported loudly rather than glossed over.**

Direct check (added after seeing the 24/24 match, to understand why
it was so clean): the true word `credit_true(k)` and the periodicized
tiling `credit_periodic(k) = tile[k % 53]` are **letter-for-letter
IDENTICAL for all k = 0..357**. Their first divergence is at
**k = 358** (`credit_true(358) = 2`; `358 % 53 = 40`,
`credit_periodic(358) = tile[40] = 1`, and these differ) — not a
coincidence:
this is exactly the m=359 first-divergence point already on record
in `shell_probe.log` P5 (`first D-divergences (m, D_rat, D_irr):
[(359, 149, 148), (412, 171, 170), (465, ...), ...]`) and in
`SYNTHESIS.md` F8. Checking further out, the next divergences are at
k = 359, 411, 412, 464, 465, 517, 518, 570, 571, ... — the same
family of points, off by one index convention from the m-values
above.

**Consequence: steps=106 and steps=159 only ever consume credits
k=0..105 and k=0..158 respectively — both entirely inside the
k=0..357 range where the true and periodicized words are exactly the
same sequence.** A1 as specified (steps 106, 159) therefore could not
possibly have produced a differing row: `credit_true` and
`credit_periodic` are the same function of k over the entire domain
either run touches. The 24/24 agreement is real and correctly
measured, but it is a confirmation that the runner and D-readout are
correct (a stronger sanity check than the steps=53 control, extended
to 2–3 heartbeats), not evidence that the corridor is blind to
aperiodicity that was actually present in the input. The work order's
question — "does the real word's aperiodicity bite at these
scales?" — is **not yet answered by A1's steps=106/159 rows**,
because no aperiodicity was present in the compared inputs at those
step counts. Answering it would require steps ≥ 359 (crossing the
first true divergence point), which is far outside this design's
specified step counts (106, 159) and reaches into the same regime as
the unresolved F5 witness search. This is not a Design A failure —
steps=106/159 are exactly what the work order specified — but the
"aperiodicity does or doesn't bite" question the design frames itself
around is, on this evidence, undecidable within the steps range
tested, because the two words being compared are provably identical
there. **Flagging this prominently per the honest-reporting law: the
match is genuine but the comparison was vacuous by construction of
the step counts relative to the word's own period-53 structure,
which itself only breaks at k=358.**

## A2 — Window slide, m ∈ {8, 10}, true word, steps 53..106

Registered prediction (Fable): variation ≤ 1, correlated with window
support-count, no drift.

Full per-step table in `a2_results.json` (108 rows: 54 steps values ×
2 m values). Summary:

### m = 8 (window = final 9 credits)

- D range: **{3, 4}** — variation of exactly 1, matching the
  prediction's ceiling.
- Support-count range: {3, 4} (out of 9-letter window).
- Cross-tab (support_count, D) → count: (3,3)×15, (4,3)×22, (4,4)×17.
- Pearson r(D, support_count) = **0.420**.
- No drift: D does not trend up or down monotonically over
  steps=53..106; it oscillates between 3 and 4 tracking the window
  content, consistent with "no drift."
- No margin < 2 at any of the 54 steps values (margins 8 or 9
  throughout).

### m = 10 (window = final 11 credits)

- D range: **{4, 5}** — variation of exactly 1.
- Support-count range: {4, 5} (out of 11-letter window).
- Cross-tab (support_count, D) → count: (4,4)×24, (4,5)×22, (5,5)×8.
- Pearson r(D, support_count) = **0.373**.
- No drift, same oscillating pattern as m=8.
- No margin < 2 at any of the 54 steps values (margins 7 or 8
  throughout).

**Verdict: CONFIRMS the registered prediction.** Variation is exactly
1 (not more) at both tested m, and D correlates positively with the
window's support-count at both m (r ≈ 0.37–0.42 — positive and
non-trivial, though moderate rather than tight; the (4,3) and (4,4)
/ (4,4) and (4,5) cells overlapping in the cross-tabs show D is not a
deterministic function of support-count alone, some additional
structure — e.g. which positions within the window carry the 1-credits,
not just the count — plays a role). No drift observed over the full
53-step sweep at either m. No anomaly.

## Runtime and memory

- Total wall-clock: **407.7 s (6.80 min)**, CPU-only, single process,
  logged by the runner itself.
- Heaviest rows (as anticipated by the work order): m=13 at steps=106
  (78.22 s) and m=13 at steps=159 (137.15 s, ≈1.75× the steps=106 cost
  for that row — in the ballpark of, if a bit under, the work order's
  "~3x" estimate, likely because the vectorized gather/scatter cost is
  dominated by `3^13` array operations rather than step count alone
  once m is large).
- Peak RSS observed via `ps` snapshots during the run: **~284 MB**,
  far under the 8GB guard (`max_states_guard` in the runner is set to
  400,000,000 states; the largest state space actually touched was
  C=12, m=13 → 13 × 3^13 ≈ 20.7M states).
- int32 permutation arrays used throughout (values bounded by
  3^13 ≪ 2^31, no overflow risk).
- No walls hit; no runs were capped, retried for resource reasons, or
  left inconclusive.

## Anomalies

No row disagreed and no margin dropped below 2 anywhere — by the
work order's own rerun criterion, nothing required a rerun. But the
finding that matters is not an anomaly in the data; it is a scope
limit in the design as specified, surfaced above and repeated here:
**A1's steps=106/159 comparison is provably vacuous** — `credit_true`
and `credit_periodic` are the identical function of k over the entire
range either run consumes (k=0..357 is where they agree; the runs
only reach k=158). The 24/24 match confirms the runner and D-readout
are correct, extends the steps=53 identity control through 2–3
heartbeats, and is consistent with (but cannot itself demonstrate)
the registered "corridor can't see aperiodicity at these scales"
claim. A1 at step counts that actually cross k=358 (i.e. steps ≥ 359)
would be the real test, and reaches the same m≈359-scale territory as
the unresolved F5 witness search — outside this design's specified
range. A2's results carry no such caveat: the window-slide runs at
steps=53..106 only ever use the true word, so no vacuity issue
applies there, and its confirmation of the registered prediction
(variation ≤ 1, positive support-count correlation, no drift) stands
as a genuine positive result.

## File manifest

- `run_design_a.py` — the runner (self-contained; imports only
  `automaton.credit`, `mod_inverse`, `allowed_exponents` from
  `renorm_check/embedding/automaton.py`).
- `run_design_a.log` / `progress_a.log` — identical full run logs
  (per-row progress, sanity checks, timing).
- `a1_results.json` — 24 raw A1 rows.
- `a2_results.json` — 108 raw A2 rows.
- `RESULTS_A.md` — this file.
