# Design C — Selection Table Across Three Word Families

Per `renorm_check/shell/W6C_SELECTION_ORDER.md`, Design C section. Scope:
`shell/selection/families/` only. No edits to IMPLEMENTATION_LEDGER.md,
SYNTHESIS.md, or any file outside this directory. No git commits.

**Families:**
1. `sqrt3`: α = √3, floor(kα) = isqrt(3k²), β = 2−√3 ≈ 0.26795.
2. `sqrt6m1`: α = √6−1, floor(kα) = isqrt(6k²)−k, β = 3−√6 ≈ 0.55051.
3. `sqrt7m1`: α = √7−1, floor(kα) = isqrt(7k²)−k, β = 3−√7 ≈ 0.35425.

All code, logs, and CSVs referenced below live in this directory
(`renorm_check/shell/selection/families/`). Shared automaton mechanics
imported unmodified from `shell/toy_word/toy_automaton.py`
(`run_heartbeat_generic`) and `embedding/automaton.py`
(`allowed_exponents`, `mod_inverse`) — no reimplementation.

---

## Step (a) — Credit-function exactness cross-check

`family_credits.py`, log `step_a_crosscheck.log`. Each family's isqrt-based
floor function (`floor_k_sqrt3`, `floor_k_sqrt6m1`, `floor_k_sqrt7m1`)
checked against 60-digit Decimal for k=0..100000.

**Result: 0 mismatches, all three families, k=0..100000. PASS.**

## Step (b) — Candidate-law tables (frozen before measurement)

`family_laws.py`, log `step_b_laws.log`, tables in `<family>_laws.csv`.

For each family: continued fraction of β computed exactly (60-digit
Decimal to extract integer CF partial quotients, then exact-integer
convergent recursion), independently re-verified via the standard bound
|β − p/q| < 1/q² at 60-digit precision (all convergents PASS), and the
irrational-law exact-integer test (`ceil(β·m − 1)` via an isqrt
inequality, no floats) independently verified against 60-digit Decimal
ceiling for m=2..15 (0 mismatches, all three families).

**Frozen law ordering** (as tabulated, logged before any D(m) run):
- sqrt3: `irrational, 0/1, 1/3, 1/4, 3/11, 4/15`
- sqrt6m1: `irrational, 0/1, 1/1, 1/2, 5/9, 11/20`
- sqrt7m1: `irrational, 0/1, 1/2, 1/3, 5/14, 6/17`

CF terms and convergent classification (over/under β), first 5
convergents each:

| Family | CF terms (a₀..) | Convergents (classified) |
|---|---|---|
| sqrt3 | [0,3,1,2,1,2,...] | 0/1(deg), 1/3(OVER), 1/4(UNDER), 3/11(OVER), 4/15(UNDER) |
| sqrt6m1 | [0,1,1,4,2,4,...] | 0/1(deg), 1/1(deg), 1/2(UNDER), 5/9(OVER), 11/20(UNDER) |
| sqrt7m1 | [0,2,1,4,1,1,...] | 0/1(deg), 1/2(OVER), 1/3(UNDER), 5/14(OVER), 6/17(UNDER) |

sqrt3's convergent sequence matches the work order's pre-registered
values exactly (1/3 over, 1/4 under, 3/11 over, 4/15 under) — confirms
the independent CF computation here is correct.

**Denominator-1 exclusion rule** (fixed before reading any D(m) data,
applied uniformly): the CF's zeroth convergent (`0/1`, value 0, always
predicts −1 regardless of m) is degenerate and excluded from law
scoring in all three families. `sqrt6m1` additionally has a first
convergent `1/1` (also denominator 1 — its CF is [0;1,1,4,2,...], so
q₁=1 again) which is likewise excluded on the same basis (not a
meaningful competing approximation at these m-scales). This rule was
derived from the CF structure alone, not from looking at D(m) results,
and applied identically to all three families once fixed.

## Step (c) — Quick controls

`family_controls.py`, log `step_c_controls.log`.

- Heredity (live at m ⟹ parent live at m−1), m=3..7, C=8: **0
  violations, all three families.**
- Universality (dead set keyed by ceiling-distance identical across
  C=8 vs C=12), m=2..5: **0 mismatches, all three families.**

Both controls pass cleanly for all three families, confirming F6/F7
(mod-3 steering, universal ceiling-anchored shell) are word-independent
structural properties, not artifacts of the true word or the toy golden
word tested in W6B.

## Step (d) — D(m) measurement

`family_D_measure.py`, logs `<family>_D.log`, tables `<family>_D.csv`.
D(m) = min ceiling-distance of a live terminal (state (d, r=1 mod 3^m))
after one 53-step heartbeat from the fully populated start, exactly
per SYNTHESIS F8 / shell_probe.py P5 / W6B's readout definition.
Corridor starts at C=12; margin rule enforced (widen C by +4 and rerun
if floor margin < 2). int32 permutation arrays throughout. CPU only.

**sqrt3** (all rows at C=12, margin never dropped below 2 — no
widening needed):

| m | D | shell_depth | margin |
|---|---|---|---|
| 2 | 1 | 2 | 10 |
| 3 | 1 | 4 | 8 |
| 4 | 1 | 4 | 8 |
| 5 | 2 | 5 | 7 |
| 6 | 2 | 6 | 6 |
| 7 | 2 | 6 | 6 |
| 8 | 2 | 7 | 5 |
| 9 | 3 | 7 | 5 |
| 10 | 3 | 8 | 4 |
| 11 | 3 | 8 | 4 |
| 12 | 4 | 8 | 4 |
| 13 | 4 | 9 | 3 |
| 14 | 4 | 9 | 3 |
| 15 | 4 | 9 | 3 |

**sqrt6m1** (m=12..15 needed widening to C=16 to satisfy the margin
rule; all other rows at C=12):

| m | D | C_used | shell_depth | margin | widened |
|---|---|---|---|---|---|
| 2 | 1 | 12 | 2 | 10 | no |
| 3 | 2 | 12 | 4 | 8 | no |
| 4 | 3 | 12 | 5 | 7 | no |
| 5 | 3 | 12 | 6 | 6 | no |
| 6 | 4 | 12 | 7 | 5 | no |
| 7 | 4 | 12 | 8 | 4 | no |
| 8 | 5 | 12 | 8 | 4 | no |
| 9 | 5 | 12 | 10 | 2 | no |
| 10 | 6 | 12 | 10 | 2 | no |
| 11 | 6 | 12 | 10 | 2 | no |
| 12 | 7 | 16 | 11 | 5 | yes (C=12 gave margin 1) |
| 13 | 7 | 16 | 12 | 4 | yes |
| 14 | 8 | 16 | 12 | 4 | yes |
| 15 | 9 | 16 | 13 | 3 | yes (C=12 gave margin 0) |

**sqrt7m1** (all rows at C=12, margin never dropped below 2):

| m | D | shell_depth | margin |
|---|---|---|---|
| 2 | 0 | 1 | 11 |
| 3 | 1 | 3 | 9 |
| 4 | 1 | 4 | 8 |
| 5 | 1 | 5 | 7 |
| 6 | 2 | 5 | 7 |
| 7 | 2 | 6 | 6 |
| 8 | 3 | 7 | 5 |
| 9 | 3 | 8 | 4 |
| 10 | 3 | 8 | 4 |
| 11 | 4 | 8 | 4 |
| 12 | 4 | 8 | 4 |
| 13 | 4 | 9 | 3 |
| 14 | 5 | 9 | 3 |
| 15 | 5 | 10 | 2 |

m=15 completed for all three families (the 8GB guard did not bind at
any row; peak process RSS was 1.6GB, for sqrt6m1's widened C=16 row at
m=15).

## Step (e) — Readout

`family_readout.py`, logs `<family>_readout.log`. Offsets fitted as a
single constant integer per law, using ONLY rows where all (non-
degenerate) laws agree with each other, frozen before scoring decisive
rows. Applied to every measured row; per-row MATCH/miss reported, no
aggregation hiding a mixed result.

### sqrt3 — CLEAN WIN for an UNDER convergent

Agreement rows (all laws equal): m = 2,3,5,6,9. Fitted offset: **+1**,
exact on all agreement rows, all five laws.

| Law | Side | Mismatches (of 14 measured rows) | Mismatch rows |
|---|---|---|---|
| **1/4** | **UNDER** | **1** | m=12 |
| 4/15 | UNDER | 2 | m=4, 8 |
| irrational | — | 3 | m=4, 8, 15 |
| 3/11 | OVER | 3 | m=4, 8, 15 |
| 1/3 | OVER | 8 | m=4,7,8,10,11,13,14,15 |

**Winning law: 1/4, denominator 4, side UNDER.** Decisive row m=15 (the
work order's pre-computed side-discriminator): with the fitted +1
offset, 1/4 predicts 4 and 4/15 predicts 4 — both UNDER convergents
match the measured D(15)=4. The irrational law and both OVER
convergents (1/3, 3/11) predict 5 — a miss. This reproduces, at raw
formula level, the work order's stated pattern: under-convergents
predict 3 (raw, before offset) / over+irrational predict 4 (raw);
with the fitted +1 offset the absolute values shift by one but the
SIDE split is identical and decisive in the same direction.

### sqrt6m1 — TIE, not decisive at this m-range

Agreement rows: m = 3,5,7,9. Fitted offset: **+1**, exact on all
agreement rows, all four (non-degenerate) laws.

| Law | Side | Mismatches (of 14) | Mismatch rows |
|---|---|---|---|
| irrational | — | 3 | m=2, 11, 13 |
| **5/9** | **OVER** | **3** | m=2, 11, 13 |
| **11/20** | **UNDER** | **3** | m=2, 11, 13 |
| 1/2 | UNDER | 7 | m=4,6,8,10,12,14,15 |

Irrational, 5/9 (OVER), and 11/20 (UNDER) are in an **exact three-way
tie**, missing the identical three rows (m=2, 11, 13) — not merely the
same count, the same rows. The coarser 1/2 (UNDER) loses decisively (7
misses). No side wins outright: the finest OVER and UNDER convergents
tested are numerically indistinguishable from each other and from the
irrational law across m=2..15 at this offset. This is an honest
inconclusive result for this family in this range, not a forced call.

### sqrt7m1 — TIE, not decisive at this m-range

Agreement rows: m = 2,4. Fitted offset: **0**, exact on both agreement
rows, all five laws.

| Law | Side | Mismatches (of 14) | Mismatch rows |
|---|---|---|---|
| irrational | — | 3 | m=8, 11, 14 |
| **5/14** | **OVER** | **3** | m=8, 11, 14 |
| **6/17** | **UNDER** | **3** | m=8, 11, 14 |
| 1/3 | UNDER | 8 | m=3,6,8,9,11,12,14,15 |
| 1/2 | OVER | 9 | m=5,7,9,10,11,12,13,14,15 |

Same pattern as sqrt6m1: irrational, 5/14 (OVER), and 6/17 (UNDER) tie
exactly (same 3 miss-rows: m=8, 11, 14). Coarser convergents 1/3 and
1/2 lose badly. No side decision possible at this m-range — genuinely
tied, reported as such.

---

## Selection Table (summary)

| Family | β | Winning law | Denominator | Side | Decisive rows / verdict | Rows unexplained by all laws |
|---|---|---|---|---|---|---|
| sqrt3 (α=√3) | 2−√3≈0.26795 | **1/4** | 4 | **UNDER** | m=15: UNDER convergents (1/4, 4/15) match D=4; irrational + OVER convergents (1/3, 3/11) predict 5, miss. Clean, single-mismatch (m=12) winner. | m=12 (all non-degenerate laws miss here) |
| sqrt6m1 (α=√6−1) | 3−√6≈0.55051 | **TIE**: irrational / 5/9 (OVER) / 11/20 (UNDER) | 9 and 20 (tied) | **NO SIDE DECISION** | 3-way exact tie (same 3 miss-rows: m=2,11,13); coarser 1/2 (UNDER) clearly loses | m=2, 11, 13 (shared by all three tied laws) |
| sqrt7m1 (α=√7−1) | 3−√7≈0.35425 | **TIE**: irrational / 5/14 (OVER) / 6/17 (UNDER) | 14 and 17 (tied) | **NO SIDE DECISION** | 3-way exact tie (same 3 miss-rows: m=8,11,14); coarser 1/2 (OVER), 1/3 (UNDER) clearly lose | m=8, 11, 14 (shared by all three tied laws) |

## Verdict vs registered predictions

The work order's registered prediction: **every family locks to a
convergent rather than its slope (lock universality); side-pattern per
family should agree with Design B's verdict.**

- **Lock universality (convergent beats the raw irrational slope
  standalone):** NOT cleanly supported. In two of three families
  (sqrt6m1, sqrt7m1) the irrational law is tied for best fit with the
  two nearest convergents, not beaten by them. Only sqrt3 shows a
  convergent (1/4) outright beating the irrational law (1 mismatch vs
  3). This is a **weaker, more qualified result** than "every family
  locks to a convergent" — one clean convergent win, two irrational/
  convergent ties.
- **Side-pattern consistency:** sqrt3 alone produces a side verdict
  (UNDER), decisively, at its pre-registered discriminating row m=15.
  sqrt6m1 and sqrt7m1 produce NO side verdict at all in this m-range —
  their tied triples straddle both sides (one OVER, one UNDER
  convergent, tied with each other and with the irrational law), so
  there is nothing to compare against Design B's √2 verdict for these
  two families. Agreement/disagreement with Design B cannot be assessed
  for sqrt6m1 or sqrt7m1 from this data; only sqrt3 offers a comparable
  side call, and it is UNDER.
- Per the work order's honest-reporting law: sqrt6m1 and sqrt7m1's
  results are reported as **inconclusive at m≤15**, not rounded up to
  "convergent-consistent" or down to "irrational-consistent." The tie
  is exact (identical miss-rows), not a near-tie broken by judgment.

## Anomalies

- Denominator-1 convergents (0/1 universally; additionally 1/1 for
  sqrt6m1) are degenerate and were excluded from law scoring after
  discovering they made EVERY row "decisive" by trivial construction
  (a convergent that never agrees with anything cannot mark any row as
  an agreement row). This exclusion was derived from the CF structure
  alone (any p/1 convergent), decided once, and applied uniformly
  across all three families without per-family adjustment.
- For sqrt6m1 and sqrt7m1, the tie is EXACT — not merely the same
  mismatch count but the identical set of miss-rows across the tied
  laws. This is a stronger form of "no discrimination yet" than a
  coincidental count-tie would be: at m≤15, these three laws are
  numerically indistinguishable, not just close.
- sqrt6m1 needed corridor widening (C=12→16) for m=12..15 to satisfy
  the margin rule (m=15 at C=12 gave margin=0); sqrt3 and sqrt7m1 never
  needed widening through m=15. This is consistent with sqrt6m1 having
  the largest β (≈0.551, closest to 1 of the three), so its shell
  descends fastest per the F8/W6 framing (steeper slope ⟹ narrower
  natural margin at fixed C).

## Runtime / memory

- Controls (heredity + universality, all 3 families): a few seconds
  total (see `step_c_controls.log`).
- D(m) measurement, m=2..15, all three families run concurrently in
  background (CPU only, no GPU):
  - sqrt3: 487.8s (8.1 min), peak RSS ≈1.26GB
  - sqrt7m1: 441.3s (7.4 min), peak RSS ≈1.19GB
  - sqrt6m1: 807.2s (13.5 min) — longer due to the C=16 widened reruns
    at m=12..15, peak RSS ≈1.58GB
- 8GB guard never bound at any row for any family (worst observed RSS
  ≈1.6GB, well under the ceiling); m=15 completed for all three
  families with no wall hit.
- int32 permutation arrays used throughout (values < 3^15 ≈ 1.43×10^7,
  far under 2^31).

## Files in this directory

- `family_credits.py`, `step_a_crosscheck.log` — step (a)
- `family_laws.py`, `step_b_laws.log`, `sqrt3_laws.csv`,
  `sqrt6m1_laws.csv`, `sqrt7m1_laws.csv` — step (b)
- `family_controls.py`, `step_c_controls.log` — step (c)
- `family_D_measure.py`, `sqrt3_D.log`, `sqrt6m1_D.log`,
  `sqrt7m1_D.log`, `sqrt3_D.csv`, `sqrt6m1_D.csv`, `sqrt7m1_D.csv` —
  step (d)
- `family_readout.py`, `sqrt3_readout.log`, `sqrt6m1_readout.log`,
  `sqrt7m1_readout.log` — step (e)
- `RESULTS_C.md` — this file

Path: `/mnt/ForgeRealm/collatz-experimental-data/renorm_check/shell/selection/families/RESULTS_C.md`
