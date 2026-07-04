# W6D-G Work Order — Periodic-Word Ground Truth for P1 (registered 2026-07-03, Fable)

**Parent:** `shell/W6D_UNDERLOCK_PROOF_PLAN.md`, order-of-battle item 1.
**Purpose:** measure the EXACT capacity law of corridors driven by
purely periodic convergent words — the ground truth P1's block algebra
must reproduce — and test the under-lock identity: that the true
Sturmian corridor is indistinguishable from its convergent-word
corridor at every measurable row.

**CRITICAL SPEC (do not substitute):** the periodic comparison word for
a convergent lock p/q of β = 2−α is the MECHANICAL WORD OF THE
CONVERGENT SLOPE, c_k = ⌊P(k+1)/q⌋ − ⌊Pk/q⌋ with P/q the corresponding
convergent of α (NOT of β), i.e. P = 2q − p. It has period q and
exactly p ones per period. Tiling the first q letters of the true word
is NOT the same object for under-side convergents (the golden word's
first 8 letters carry FOUR ones, slope 1/2, not 3/8) — that tiling is
measured here only as a deliberate contrast control (G3).

Words under test (all pure integer arithmetic, exact by construction;
assert period and per-period support counts before measuring):
- **golden-per8:** c_k = ⌊13(k+1)/8⌋ − ⌊13k/8⌋. Period 8, 3 ones + 5
  twos per period. (13/8 = convergent of φ; 2 − 13/8 = 3/8.)
- **sqrt2-per12:** c_k = ⌊17(k+1)/12⌋ − ⌊17k/12⌋. Period 12, 7 ones +
  5 twos per period. (17/12 = convergent of √2; 2 − 17/12 = 7/12.)
- **golden-tile8 (contrast control):** the first 8 letters of the TRUE
  golden word [1,2,1,2,2,1,2,1], tiled. Period 8, 4 ones. This is the
  WRONG object on purpose.

**Shared machinery:** `shell/toy_word/toy_automaton.py`
`run_heartbeat_generic` (T1-validated), D(m) readout exactly as W6B/W6C
(min ceiling-distance of a live terminal, 53 steps from fully populated
start, margin rule: report shell depth + floor margin every row, widen
C and rerun if margin < 2). 8GB memory guard, int32 permutation arrays,
long runs backgrounded with progress logs. Work ONLY under
`shell/underlock/` (create it); results to `RESULTS_D1.md` there. No
edits to IMPLEMENTATION_LEDGER.md / SYNTHESIS.md / anything outside
your directory. No git commits.

## G1 — Periodic-word D tables

D(m), m = 2..13, for golden-per8 and sqrt2-per12 (extend sqrt2 to m=16
if the guard allows — the true-word W6C table reaches 16). Before
reading any D value, write the candidate law tables (⌈(p/q)·m − 1⌉ raw,
per W6C convention) to laws CSVs — mtimes are the pre-registration
record. Steps-invariance spot check: rerun two rows per word at
steps=106; values must not move.

## G2 — The under-lock identity (the decisive comparison)

Row-by-row comparison against the TRUE-word D tables already on disk
(golden: `shell/toy_word/D_toy_table.csv` + capstone m=16=6; sqrt2:
`shell/selection/sqrt2/D_sqrt2_table.csv` + m=16=10).

**Registered predictions (Fable, frozen here, pre-data):**
- PD1: D_golden-per8(m) = D_golden-true(m) for EVERY m = 2..13 (and 16
  if run) — INCLUDING the anomaly rows m=3 and m=11 that no fitted law
  matched. If the periodic word reproduces the anomalies, they were
  never aperiodicity effects — they are the 3/8-periodic system's own
  transient, and P1's closed form must contain them.
- PD2: D_sqrt2-per12(m) = D_sqrt2-true(m) for every measured row
  (equivalently ⌈7m/12⌉ + the same offset, 15/15+).
- PD3: golden-tile8 (the wrong object) follows a slope-1/2 law, NOT
  3/8 — its D table separates from golden-per8's at small m and never
  rejoins.

Report each prediction's outcome per-row, no aggregation that hides a
mixed result. If PD1/PD2 hold exactly, say so plainly: it means the
corridor CANNOT DISTINGUISH its true word from the convergent word at
these scales — the under-lock identity — and W6D's P3
(word-monotonicity) collapses to a much weaker statement. If any row
differs, that row is a direct measurement of aperiodicity biting below
the wall: report it loudly with a rerun confirmation, exactly as
Design A's discipline would.

## G3 — Contrast control

golden-tile8 D(m), m=2..10 suffices. Purpose: demonstrate empirically
that the tiling-vs-mechanical distinction is real (protects all future
work from the spec trap named above). Compare against slope-1/2 and
slope-3/8 laws; report which side it lands.

## Reporting

RESULTS_D1.md: assertion receipts (periods/counts), laws CSVs, three D
tables with shell depths/margins, per-row PD1/PD2/PD3 verdicts,
runtime/memory, walls (inconclusive is a result). Final message back:
the three verdicts and any row where a periodic word and its true word
disagree — that list, empty or not, is the payload P1 needs.
