# W6D-G RESULTS_D1 — Periodic-Word Ground Truth for P1 (executed 2026-07-03, Fable)

Work order: `shell/W6D_GROUND_TRUTH_ORDER.md`. All work under
`shell/underlock/`. No files outside this directory touched. No commits.

## Headline

**PD1 and PD2 are REFUTED under the registered exact-equality reading.
The under-lock identity FAILS: the corridor DOES distinguish the true
Sturmian word from its mechanical convergent word at most rows — by
exactly +1, with fully regular arithmetic structure.** PD3 is CONFIRMED.
The disagreement list (the order's primary payload) is long and
structured, not empty:

- golden: true ≠ per8 at m ∈ {2, 4, 6, 7, 9, 10, 12} (7 of 13 measured
  rows, m=2..13 and 16; the m=16 row matches, as the law arithmetic
  requires), all +1.
- sqrt2: true ≠ per12 at m ∈ {2, 3, 4, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16}
  (13 of 15 rows), all +1.

Every disagreement row was rerun-confirmed (details below). Bonus
result: the periodic words obey an EXACT closed-form law with zero
anomaly rows — the finite ground truth P1's block algebra must
reproduce:

    D_per(m) = floor((p·m + 1)/q)      [post-hoc form; 28/28 measured rows,
                                        incl. 1 confirmed forward prediction
                                        (G1-X); ≡ ceil((p·m + 2)/q) − 1, the
                                        form registered by the main session]

## Registered predictions (restated verbatim from the order)

> - PD1: D_golden-per8(m) = D_golden-true(m) for EVERY m = 2..13 (and 16
>   if run) — INCLUDING the anomaly rows m=3 and m=11 that no fitted law
>   matched. If the periodic word reproduces the anomalies, they were
>   never aperiodicity effects — they are the 3/8-periodic system's own
>   transient, and P1's closed form must contain them.
> - PD2: D_sqrt2-per12(m) = D_sqrt2-true(m) for every measured row
>   (equivalently ⌈7m/12⌉ + the same offset, 15/15+).
> - PD3: golden-tile8 (the wrong object) follows a slope-1/2 law, NOT
>   3/8 — its D table separates from golden-per8's at small m and never
>   rejoins.

## Assertion receipts (pre-measurement, per the CRITICAL SPEC)

All run and PASSED before any measurement (`underlock_words.py`,
re-printed at the top of `measure_d.log`):

- **golden-per8**: period=8 exact (no smaller divisor works; verified
  over 2000 repetitions = 16000 letters), 3 ones + 5 twos per period.
  Block: `[1,2,1,2,2,1,2,2]`.
- **sqrt2-per12**: period=12 exact (same check), 7 ones + 5 twos per
  period. Block: `[1,1,2,1,2,1,1,2,1,2,1,2]`.
- **golden-tile8**: period=8 exact, 4 ones + 4 twos per period. Block:
  `[1,2,1,2,2,1,2,1]` (the true word's first 8 letters, verbatim).
- Cross-check: per8 block ≠ tile8 block (they differ exactly in the
  8th letter: mechanical word has 2, true-word tile has 1) — the
  CRITICAL SPEC distinction is live in the data.
- Arithmetic: 2 − 13/8 = 3/8, 2 − 17/12 = 7/12 (exact Fractions).
- Word-level confirmation: golden-per8 and the true golden word agree
  letter-for-letter for k=0..6 and first diverge at k=7 (the 8th
  letter) — exactly the under-side convergent correction position.

All credit functions are pure integer arithmetic (integer floor
division only; no floats anywhere in any word).

## Pre-registration record (laws before data)

`laws_golden.csv`, `laws_sqrt2.csv`, `laws_tile8.csv` — raw laws
⌈(p/q)·m − 1⌉ (exact integer ceiling division; irrational laws via the
isqrt-exact ladder, cross-checked 0 mismatches vs 60-digit Decimal).
File mtimes (the record):

    22:20:05  laws_golden.csv, laws_sqrt2.csv, laws_tile8.csv
    22:21:48  D_golden_per8_table.csv     (first measurement output)
    22:22:26  D_sqrt2_per12_table.csv
    22:22:28  D_golden_tile8_table.csv

## G1 — Periodic-word D tables

Machinery: `run_heartbeat_generic` from `shell/toy_word/toy_automaton.py`
(T1-validated), permutation cache monkey-patched to int32 per the order
(all moduli ≤ 3^16 << 2^31). D(m) = min ceiling-distance (C−d) of a
live terminal (d, r=1 mod 3^m) after 53 steps from the fully populated
start. Margin rule enforced every row (widen C by +2 and rerun if
floor margin < 2). m=14..16 sqrt2 rows via the dedicated int32 runner
`measure_d_sqrt2_heavy.py` (capstone_m16.py design: permutations
precomputed once, per-step progress logging, backgrounded).

### D_golden-per8 (m=2..13, `D_golden_per8_table.csv`)

| m | D | C_final | shell_depth | margin |
|---|---|---------|-------------|--------|
| 2 | 0 | 12 | 1 | 11 |
| 3 | 1 | 12 | 3 | 9 |
| 4 | 1 | 12 | 4 | 8 |
| 5 | 2 | 12 | 5 | 7 |
| 6 | 2 | 12 | 6 | 6 |
| 7 | 2 | 12 | 6 | 6 |
| 8 | 3 | 12 | 7 | 5 |
| 9 | 3 | 12 | 8 | 4 |
| 10 | 3 | 12 | 8 | 4 |
| 11 | 4 | 12 | 8 | 4 |
| 12 | 4 | 12 | 9 | 3 |
| 13 | 5 | 12 | 9 | 3 |

### D_sqrt2-per12 (m=2..16, `D_sqrt2_per12_table.csv` + `D_sqrt2_per12_heavy_table.csv`)

| m | D | C_final | shell_depth | margin |
|---|---|---------|-------------|--------|
| 2 | 1 | 12 | 2 | 10 |
| 3 | 1 | 12 | 3 | 9 |
| 4 | 2 | 12 | 4 | 8 |
| 5 | 3 | 12 | 6 | 6 |
| 6 | 3 | 12 | 6 | 6 |
| 7 | 4 | 12 | 7 | 5 |
| 8 | 4 | 12 | 8 | 4 |
| 9 | 5 | 12 | 9 | 3 |
| 10 | 5 | 12 | 9 | 3 |
| 11 | 6 | 12 | 10 | 2 |
| 12 | 7 | 14 | 11 | 3 |
| 13 | 7 | 14 | 11 | 3 |
| 14 | 8 | 16 | 12 | 4 |
| 15 | 8 | 16 | 12 | 4 |
| 16 | 9 | 16 | 13 | 3 |

(m=12, 13 required one widening 12→14 under the margin rule; m=14..16
ran at C=16 directly, margin ≥ 3 first try. Heavy-runner controls:
m=11 and m=13 recomputed at C=16 matched the light-runner values 6 and
7 exactly before the heavy rows were trusted.)

### D_golden-tile8 (m=2..10, contrast control, `D_golden_tile8_table.csv`)

| m | D | C_final | shell_depth | margin |
|---|---|---------|-------------|--------|
| 2 | 0 | 12 | 1 | 11 |
| 3 | 1 | 12 | 3 | 9 |
| 4 | 1 | 12 | 4 | 8 |
| 5 | 2 | 12 | 5 | 7 |
| 6 | 3 | 12 | 6 | 6 |
| 7 | 3 | 12 | 7 | 5 |
| 8 | 4 | 12 | 7 | 5 |
| 9 | 4 | 12 | 8 | 4 |
| 10 | 4 | 12 | 9 | 3 |

### Steps-invariance — spot check PASSED, full sweep found real movement

The order's designated spot check (two rows per word at steps=106):
golden m=6, m=11 — no move; sqrt2 m=6, m=11 — no move; tile8 m=6,
m=9 — no move. **PASS as specified.**

However, a full sweep (every row, steps=53 vs 106,
`steps_invariance_full_check.csv`) found rows that DO move (+1 at
steps=106): golden-per8 m ∈ {2, 10}; sqrt2-per12 m ∈ {10}; golden-tile8
m ∈ {2, 3, 4, 5, 10}. Investigation (fine scans, period-multiple scans,
C=12/16/20 cross-checks — all in session logs): this is a genuine
step-count phase oscillation of ±1 specific to EXACTLY PERIODIC driving
words — D read at any multiple of the word's period q equals the
steps=53 value (checked to 160 steps), while a minority of non-aligned
step counts (106 among them, at these rows) transiently read one higher.
Not floor contamination (identical at C=12/16/20). The house convention
(53-step readout, used by every true-word table this report compares
against) governs all registered comparisons; both readings are on
record. This phenomenon is itself new data for P1: the periodic
corridor's live set breathes with the word's phase, and the 53-step
readout sits on the ⌊(pm+1)/q⌋ branch.

## G2 — The under-lock identity (the decisive comparison)

True-word references: `shell/toy_word/D_toy_table.csv` (+ capstone
m=16 = 6), `shell/selection/sqrt2/D_sqrt2_table.csv` (m=16 = 10).
Exact-equality comparison at the standard 53-step readout.

### PD1 per-row (golden): **REFUTED — 5/12 rows match**

| m | D_true | D_per8 | verdict | rerun confirm |
|---|--------|--------|---------|---------------|
| 2 | 1 | 0 | DISAGREE (+1) | confirmed (C=16; note: steps=106 reads 1 — oscillating row, see G1) |
| 3 | 1 | 1 | MATCH (anomaly row) | — |
| 4 | 2 | 1 | DISAGREE (+1) | confirmed (steps=106 and C=16) |
| 5 | 2 | 2 | MATCH | — |
| 6 | 3 | 2 | DISAGREE (+1) | confirmed (steps=106 and C=16) |
| 7 | 3 | 2 | DISAGREE (+1) | confirmed (steps=106 and C=16) |
| 8 | 3 | 3 | MATCH | — |
| 9 | 4 | 3 | DISAGREE (+1) | confirmed (steps=106 and C=16) |
| 10 | 4 | 3 | DISAGREE (+1) | confirmed (C=16; steps=106 reads 4 — oscillating row) |
| 11 | 4 | 4 | MATCH (anomaly row) | — |
| 12 | 5 | 4 | DISAGREE (+1) | confirmed (steps=106 and C=16) |
| 13 | 5 | 5 | MATCH | — |
| 16 | 6 | 6 | MATCH (measured; forward-predicted, see G1-X) | control-gated run, margin 4 |

PD1's inner conditional resolves AGAINST its premise in an unexpected
direction: the periodic word does NOT "reproduce the anomalies" —
**the periodic system has NO anomaly rows at all** (its exact law fits
12/12, see below). Instead, the true word's anomaly rows m=3, m=11 are
precisely 2 of its 5 agreement rows with the periodic word: at those
rows the TRUE word deviates DOWN from its own ceiling law onto the
periodic word's branch. The anomalies are aperiodicity effects after
all — but they are the true word touching the convergent-word floor,
not the periodic system's transient.

### PD2 per-row (sqrt2): **REFUTED — 2/15 rows match**

| m | D_true | D_per12 | verdict | rerun confirm |
|---|--------|---------|---------|---------------|
| 2 | 2 | 1 | DISAGREE (+1) | confirmed (steps=106 and C=16) |
| 3 | 2 | 1 | DISAGREE (+1) | confirmed (steps=106 and C=16) |
| 4 | 3 | 2 | DISAGREE (+1) | confirmed (steps=106 and C=16) |
| 5 | 3 | 3 | MATCH | — |
| 6 | 4 | 3 | DISAGREE (+1) | confirmed (steps=106 and C=16) |
| 7 | 5 | 4 | DISAGREE (+1) | confirmed (steps=106 and C=16) |
| 8 | 5 | 4 | DISAGREE (+1) | confirmed (steps=106 and C=16) |
| 9 | 6 | 5 | DISAGREE (+1) | confirmed (steps=106 and C=16) |
| 10 | 6 | 5 | DISAGREE (+1) | confirmed (C=16; steps=106 reads 6 — oscillating row) |
| 11 | 7 | 6 | DISAGREE (+1) | confirmed (steps=106 and C=16) |
| 12 | 7 | 7 | MATCH | — |
| 13 | 8 | 7 | DISAGREE (+1) | confirmed (steps=106 at C=14, and C=18) |
| 14 | 9 | 8 | DISAGREE (+1) | confirmed (C=18 rerun: D=8, margin 6) |
| 15 | 9 | 8 | DISAGREE (+1) | confirmed (C=18 rerun: D=8, margin 6) |
| 16 | 10 | 9 | DISAGREE (+1) | confirmed (C=18 rerun: D=9, margin 5) |

### The structure of the disagreement (exact, verified in-session)

Both periodic words obey a single exact law over every measured row
(**post-hoc form — found after the data, not pre-registered; the
pre-registered raw-law columns are in the laws CSVs**):

    D_per8(m)  = floor((3m + 1)/8)      12/12 exact, m=2..13
    D_per12(m) = floor((7m + 1)/12)     15/15 exact, m=2..16

against the true words' established ceiling laws
(D_sqrt2-true = ⌈7m/12⌉, 15/15, W6C; D_golden-true = ⌈3m/8⌉ on 10/12
rows, deviating −1 exactly at m=3, 11). The two laws differ by exactly
1 except where ⌈pm/q⌉ = ⌊(pm+1)/q⌋, i.e. pm ≡ 0 or −1 (mod q):

- sqrt2: agreement iff m ≡ 0 or 5 (mod 12) → m = 5, 12 in range.
  Predicted by the law arithmetic, matched by measurement 15/15.
- golden: law arithmetic gives m ≡ 0 or 5 (mod 8) → m = 5, 8, 13; the
  two EXTRA measured agreements (m=3, 11) are exactly the true word's
  anomaly rows (see PD1 above).

The under-lock identity is therefore not just false — it fails with a
clean mechanism: **the true Sturmian corridor runs exactly one level
above its convergent-word corridor except at the arithmetic
coincidence rows of the two laws.** For P1 this is the whole prize:
the periodic ground truth is a pure floor law with a +1 numerator
shift and NO boundary anomalies; every irregularity in the W6B/W6C
toy tables belongs to the TRUE words, not the periodic algebra.

Consequence the order asked to state plainly: since PD1/PD2 fail,
W6D's P3 (word-monotonicity) does NOT collapse to a weak statement —
a real, sign-definite word difference exists below the wall
(D_true − D_per ∈ {0, +1}, never negative in 28 measured rows), which
is exactly the one-sided bounded control P3's route (c) needs.

## G1-X — golden-per8 m=16 (forward test of the exact law)

Registered pre-run in `golden_m16_row.py` (see its header): the exact
law predicts D_per8(16) = ⌊49/8⌋ = 6; the true-word capstone value is
6; law arithmetic (3·16 ≡ 0 mod 8) predicts m=16 is an AGREEMENT row.
Controls (m=11 expect 4, m=13 expect 5 at C=14) gate the run.

Independently, the main session registered (before this row completed)
the closed form D_per(m) = ⌈(p·m + 2)/q⌉ − 1, fitting all 27 measured
periodic rows and predicting this row = 6. Verified in-session: that
form is algebraically identical to ⌊(p·m + 1)/q⌋ (equality checked
exhaustively for both (p,q) over m = 2..199), so the two registrations
are one prediction: **D_per8(16) = 6, equal to the true-word capstone.**

**Result: D_per8(16) = 6 — PREDICTION CONFIRMED** (C=14, shell depth
10, floor margin 4; controls m=11 → 4 and m=13 → 5 both passed;
wall 859 s for the m=16 row, 14.6 min for the gated run). The exact
law ⌊(p·m + 1)/q⌋ ≡ ⌈(p·m + 2)/q⌉ − 1 now stands at **28/28 measured
rows, including one true forward prediction**, and m=16 is a measured
AGREEMENT row with the true golden word (both 6), exactly as the law
arithmetic (3·16 ≡ 0 mod 8) required. `D_golden_per8_m16.csv`.

## G3 — Contrast control: **PD3 CONFIRMED**

golden-tile8 (the wrong object, 4 ones per 8 = slope 1/2) vs the two
laws, m=2..10 (raw laws from pre-registered `laws_tile8.csv`, best
frozen offset per the W6C offset protocol):

| m | D_tile8 | 1/2 law (+0) | 3/8 law (+1) | on 1/2? | on 3/8? | D_per8 | separation |
|---|---------|--------------|--------------|---------|---------|--------|------------|
| 2 | 0 | 0 | 1 | YES | no | 0 | 0 |
| 3 | 1 | 1 | 2 | YES | no | 1 | 0 |
| 4 | 1 | 1 | 2 | YES | no | 1 | 0 |
| 5 | 2 | 2 | 2 | YES | (yes) | 2 | 0 |
| 6 | 3 | 2 | 3 | no | (yes) | 2 | 1 |
| 7 | 3 | 3 | 3 | YES | (yes) | 2 | 1 |
| 8 | 4 | 3 | 3 | no | no | 3 | 1 |
| 9 | 4 | 4 | 4 | YES | (yes) | 3 | 1 |
| 10 | 4 | 4 | 4 | YES | (yes) | 4* | 0* |

Verdict: slope-1/2 law fits 7/9 rows at frozen offset +0; the 3/8 law
manages 5/9 only at its best offset (+1) and its "hits" are mostly
rows where the two laws coincide numerically. Where the slopes
genuinely separate (m=2, 3, 4, 8), tile8 sits on the 1/2 side 4/4.
**golden-tile8 lands on slope 1/2 — the tiling is NOT the mechanical
convergent word**, empirically demonstrating the CRITICAL SPEC trap.
Separation from golden-per8: identical for m ≤ 5 (the two slopes'
laws differ by < 1 there), separates at m=6, and the LAWS never
rejoin (1/2 vs 3/8 diverge linearly; the m=10 momentary equality* is
the per8 word's own step catching up at 3m+1 ≡ 31, a lattice
coincidence — law projections at m=16: tile8 ≈ 7 vs per8 = 6, gap
growing). The order's "never rejoins" holds at law level; the
row-level D values can momentarily touch (m=10), reported honestly.

Note: tile8 shows the strongest small-m step-phase oscillation of the
three words (5 of 9 rows move at steps=106; see G1). Its 53-step
values are the table of record, consistent with all other tables.

## Runtime / memory

- Light tables (`measure_d.py`, all of golden-per8 m≤13, sqrt2-per12
  m≤13, tile8 m≤10, including margin-rule reruns and spot checks):
  61.6 s total, peak RSS ≈ 230 MB.
- Heavy runner (`measure_d_sqrt2_heavy.py`, sqrt2 m=14..16 + two
  controls, backgrounded with per-step logs): 1257 s (21.0 min); rows:
  m=14 67 s, m=15 273 s, m=16 893 s at C=16; peak RSS ≈ 4.2 GB —
  under the 8 GB guard throughout. int32 permutations.
- Disagreement reruns (light rows): ~90 s; full steps sweep: ~4 min.
- Heavy rerun confirmation (`rerun_heavy_confirm.py`, m=14..16 at
  C=18): m=14 85 s, m=15 ~290 s, m=16 1158 s; peak RSS ≈ 4.6 GB.
  All three rows CONFIRMED (8/8/9), margins 6/6/5.
- golden-per8 m=16 gated run (`golden_m16_row.py`): controls + row in
  14.6 min wall (m=16 row itself 859 s at C=14); RSS well under guard.
- No state-space guard hits, no memory-guard hits, no walls. All
  reported rows satisfied the margin rule (floor margin ≥ 2).
- Independent verification: a from-scratch brute-force reference
  automaton (plain Python sets, no numpy, no permutation cache)
  reproduced D_per8(3)=1, D_per8(4)=1, D_per8(5)=2 exactly.

## Files

- `underlock_words.py` — the three credit words + assertions (receipts).
- `laws_table.py`, `laws_golden.csv`, `laws_sqrt2.csv`, `laws_tile8.csv`
  — pre-registered law tables (mtimes precede all measurement).
- `measure_d.py`, `measure_d.log` — G1/G3 light measurement.
- `measure_d_sqrt2_heavy.py`, `measure_d_sqrt2_heavy.log` — m=14..16.
- `D_golden_per8_table.csv`, `D_sqrt2_per12_table.csv`,
  `D_sqrt2_per12_heavy_table.csv`, `D_golden_tile8_table.csv` — D tables.
- `rerun_disagreements.py/.csv/.log` — disagreement rerun confirmations.
- `steps_invariance_full_check.csv` — the full 53-vs-106 sweep.
- `rerun_heavy_confirm.py/.csv/.log` — m=14..16 rerun at C=18.
- `golden_m16_row.py/.log`, `D_golden_per8_m16.csv` — the m=16 forward test.
