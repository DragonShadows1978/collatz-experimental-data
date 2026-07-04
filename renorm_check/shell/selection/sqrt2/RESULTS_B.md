# W6C Design B — RESULTS (√2 crux experiment)

Executed 2026-07-03 (Fable), per `renorm_check/shell/W6C_SELECTION_ORDER.md`
Design B. All work confined to `renorm_check/shell/selection/sqrt2/` per the
coordination law. No ledger/SYNTHESIS edits, no git commits.

Word slope α = √2 (⌊k√2⌋ = isqrt(2k²), exact integers only, no floats);
β = 2−√2 ≈ 0.58579. Candidate convergents per the work order: 1/2,
3/5 (over), 7/12 (under), 17/29, 41/70.

## 0. Exactness law compliance (pre-measurement record)

- `credit_sqrt2(k) = isqrt(2(k+1)²) − isqrt(2k²)` cross-checked against
  60-digit Decimal for k = 0..100000: **0 mismatches**
  (`crosscheck_credit.log`, written 20:09:39).
- Candidate-law table written to `laws.csv` at 20:09:41 — **before any
  D value was read** (first D readout 20:11+; full sweep started 20:15;
  file mtimes are the record). The irrational law's exact integer test
  was derived as: k ≥ β·m−1 ⟺ √2·m ≥ 2m−k−1 =: rhs; if rhs ≤ 0 true,
  else isqrt(2m²) ≥ rhs (no boundary ambiguity since √2·m is
  irrational). Verified against 60-digit Decimal ceiling for m=2..16:
  0 mismatches (`laws_table.log`).
- Automaton machinery: `run_heartbeat_generic` from
  `shell/toy_word/toy_automaton.py` (T1-validated in W6B), credit
  function swapped to `credit_sqrt2`. No reimplementation of the
  residue map / corridor rules.

## 1. Candidate-law table (laws.csv, frozen pre-measurement)

| m | irrational | 1/2 | 3/5(over) | 7/12(under) | 17/29 | 41/70 |
|---|---|---|---|---|---|---|
| 2 | 1 | 0 | 1 | 1 | 1 | 1 |
| 3 | 1 | 1 | 1 | 1 | 1 | 1 |
| 4 | 2 | 1 | 2 | 2 | 2 | 2 |
| 5 | 2 | 2 | 2 | 2 | 2 | 2 |
| 6 | 3 | 2 | 3 | 3 | 3 | 3 |
| 7 | 4 | 3 | 4 | 4 | 4 | 4 |
| 8 | 4 | 3 | 4 | 4 | 4 | 4 |
| 9 | 5 | 4 | 5 | 5 | 5 | 5 |
| 10 | 5 | 4 | 5 | 5 | 5 | 5 |
| 11 | 6 | 5 | 6 | 6 | 6 | 6 |
| 12 | **7** | 5 | **7** | **6** | 7 | 7 |
| 13 | 7 | 6 | 7 | 7 | 7 | 7 |
| 14 | 8 | 6 | 8 | 8 | 8 | 8 |
| 15 | 8 | 7 | 8 | 8 | 8 | 8 |
| 16 | 9 | 7 | 9 | 9 | 9 | 9 |

m=12 is the unique row in range separating 7/12(under) from
3/5(over)/irrational/17/29/41/70 — exactly as the work order stated.
(1/2 is separated everywhere; it is the degenerate coarse outlier.)

## 2. B1 controls (`b1_controls.log`) — PASS

- **Heredity** (live at m ⟹ parent live at m−1), C=8, m=3..8:
  **0 violations at every m. PASS** (zero violations required — met).
- **Universality** (ceiling-relative dead sets identical across C=8 vs
  C=12), m=2..6: **identical at every m. PASS.**

The √2 system is a faithful structural analogue — same shell
phenomenology as the true word and the golden toy.

## 3. B2 — D_√2(m), m=2..16 (`b2_measurement.log`, `D_sqrt2_table.csv`)

Margin rule per work order: start C=12; require floor margin
(C − shell_depth) ≥ 2; widen C by 2 and rerun the row on violation.
Shell depth and margin reported EVERY row:

| m | D_√2(m) | C_final | shell_depth | margin | attempts | row wall (s) |
|---|---|---|---|---|---|---|
| 2 | 2 | 12 | 3 | 9 | 1 | 0.01 |
| 3 | 2 | 12 | 4 | 8 | 1 | 0.01 |
| 4 | 3 | 12 | 5 | 7 | 1 | 0.01 |
| 5 | 3 | 12 | 7 | 5 | 1 | 0.01 |
| 6 | 4 | 12 | 7 | 5 | 1 | 0.02 |
| 7 | 5 | 12 | 8 | 4 | 1 | 0.03 |
| 8 | 5 | 12 | 9 | 3 | 1 | 0.06 |
| 9 | 6 | 12 | 10 | 2 | 1 | 0.14 |
| 10 | 6 | 12 | 10 | 2 | 1 | 0.36 |
| 11 | 7 | 14 | 11 | 3 | 2 | 3.7 |
| 12 | **7** | 14 | 11 | 3 | 2 | 13.6 |
| 13 | 8 | 14 | 12 | 2 | 2 | 43.3 |
| 14 | 9 | 16 | 13 | 3 | 3 | 246.7 |
| 15 | 9 | 16 | 13 | 3 | 3 | 768.3 |
| 16 | 10 | 16 | 14 | 2 | 3 | 1928.2 |

The work order's expectation held: wider corridors were needed at high
m (C=16 by m=14) because β is larger than golden's — the shell
descends faster.

### 3b. The m=16 row

The generic sweep's m=16 attempt hit `run_heartbeat_generic`'s default
`max_states_guard = 400M` states ((C+1)·3^16 = 559.6M at C=12) — a
conservative STATE-COUNT guard, not the 8GB memory guard. A dedicated
runner (`b2b_m16.py`, int32 permutation arrays per the capstone_m16
memory design, per-step progress logging, RSS abort at 7.5GB) ran the
row under the same margin-rule protocol (C=12 → margin 0 → C=14 →
margin 0 → C=16 → margin 2, PASS). **RESULT: D_√2(16) = 10, C=16,
shell_depth=14, margin=2** (32.1 min wall, peak RSS 4.2GB; attempt
detail in `D_sqrt2_m16.csv` / `b2b_m16.log`). D was already 10 at
C=12 and C=14 as well — stable across all three widths. No memory
wall was hit; the 8GB guard never bound.

## 4. B3 — offset fit and per-row matching (`b3_readout.log`)

**Agreement region** (rows where ALL laws in laws.csv agree,
including 1/2): m ∈ {3, 5}. Fitted constant offsets, frozen before
reading any decisive row:

| law | fitted offset | exactly constant on agreement region? |
|---|---|---|
| irrational | +1 | yes |
| 1/2 | +1 | yes |
| 3/5(over) | +1 | yes |
| 7/12(under) | +1 | yes |
| 17/29 | +1 | yes |
| 41/70 | +1 | yes |

(If the agreement region is instead read as "all laws except the
degenerate 1/2" — i.e. every row except m=12 — the fit is unchanged:
D − law = +1 exactly on all 13 such measured rows. The offset is
robust to that ambiguity.)

**Per-row matching at frozen offsets** (T4-style; `*` = match):

| m | D_√2 | irrational+1 | 1/2+1 | 3/5+1 | 7/12+1 | 17/29+1 | 41/70+1 |
|---|---|---|---|---|---|---|---|
| 2 | 2 | 2* | 1 | 2* | 2* | 2* | 2* |
| 3 | 2 | 2* | 2* | 2* | 2* | 2* | 2* |
| 4 | 3 | 3* | 2 | 3* | 3* | 3* | 3* |
| 5 | 3 | 3* | 3* | 3* | 3* | 3* | 3* |
| 6 | 4 | 4* | 3 | 4* | 4* | 4* | 4* |
| 7 | 5 | 5* | 4 | 5* | 5* | 5* | 5* |
| 8 | 5 | 5* | 4 | 5* | 5* | 5* | 5* |
| 9 | 6 | 6* | 5 | 6* | 6* | 6* | 6* |
| 10 | 6 | 6* | 5 | 6* | 6* | 6* | 6* |
| 11 | 7 | 7* | 6 | 7* | 7* | 7* | 7* |
| 12 | **7** | 8 | 6 | 8 | **7*** | 8 | 8 |
| 13 | 8 | 8* | 7 | 8* | 8* | 8* | 8* |
| 14 | 9 | 9* | 7 | 9* | 9* | 9* | 9* |
| 15 | 9 | 9* | 8 | 9* | 9* | 9* | 9* |
| 16 | 10 | 10* | 8 | 10* | 10* | 10* | 10* |

**Match counts (measured rows):**

| law | matches | misses at |
|---|---|---|
| **7/12(under)** | **15/15** | — |
| irrational | 14/15 | m=12 |
| 3/5(over) | 14/15 | m=12 |
| 17/29 | 14/15 | m=12 |
| 41/70 | 14/15 | m=12 |
| 1/2 | 2/15 | everywhere except m=3,5 |

Equivalent closed form of the winning fit: D_√2(m) = ceil(7m/12) for
every measured m (2..16) — the under-convergent law with the +1
offset absorbed (ceil(x·m) = ceil(x·m −1)+1 away from integers; at
m=12 the product 7·12/12 = 7 is an integer, which is exactly where
the under law separates from the pack).

## 5. THE DECISIVE ROW — m=12 verdict

Registered predictions, restated verbatim from W6C_SELECTION_ORDER.md
(frozen there; NOT re-derived or softened here):

> B3. Decisive row m=12 (3^12 dense = trivial): with fitted offsets from
> the agreement region, 7/12 (under) predicts D=6; 3/5 (over) AND
> the irrational law predict D=7.
> - Registered prediction (Fable): **6 — R-under wins.** Stated
>   uncertainty: this is a mechanism hunch from golden's lag-side
>   misses, not a derivation. If 7: R-coarse survives (the slope is
>   already excluded as a standalone law by W6B; transfer inference
>   says 7 → R-coarse). If neither/mixed across rows: the rule is
>   richer than both candidates — report raw, no aggregation.

F5 implications, restated verbatim from the work order preamble:

> - **R-coarse:** the lock is the coarsest scale-appropriate convergent;
>   upgrades need ≳2 full return cycles. → real system at m=359 uses
>   22/53 → D(359)=149 → C=148 edge = **358**.
> - **R-under:** the lock is the under-side convergent (shell quantizes
>   toward LESS death — consistent with every golden miss-row lagging the
>   laws). → real system at m=359 could use 127/306 (under, den 306 ≤ 359)
>   → D(359)=148 → C=148 edge = **359**.

**MEASURED: D_√2(12) = 7.** Corridor-independence triple-checked:
identical D=7, shell_depth=11 at C=14 (margin 3), C=16 (margin 5),
C=18 (margin 7) — `b3_decisive_row_confirm.log`.

### The two readings (both reported in full; the conflict is the finding)

1. **Raw-value mapping as registered** (6 → R-under; 7 → R-coarse;
   other → neither): measured 7 → **R-coarse**.

2. **The work order's own frozen-offset protocol**: the fitted offsets
   on the agreement region are **+1 for every law, exactly constant**
   — not 0. At those frozen offsets the m=12 predictions are:
   7/12(under) → 7 (**MATCH**); 3/5(over) → 8 (miss);
   irrational → 8 (miss). The under-side law is the UNIQUE match at
   the decisive row and matches **15/15** measured rows overall;
   every over-side/irrational candidate misses exactly and only at
   m=12. Under the offset protocol: **R-under**.

**These two readings CONFLICT, and the conflict is reported loudly,
not resolved here.** The registered mapping's stated premise — "with
fitted offsets from the agreement region, 7/12 predicts D=6; 3/5 and
the irrational law predict D=7" — presupposed that the fitted offsets
would be zero. The measurement refutes that premise: the offsets are
+1 (exactly constant, no fitting freedom was exercised — a single
integer shared by every law). With the actually-fitted offsets, the
work order's own protocol assigns the measured 7 to the UNDER law,
and 8 (not 7) to over/irrational. The raw value 7 is simultaneously
(a) the registered "R-coarse" number and (b) the under-law's
offset-adjusted prediction.

What is NOT ambiguous, at any offset convention: **the measured D_√2
sequence has the under-convergent's SHAPE** — flat step at m=11→12
(7,7), rise at m=13 (8) — which is 7/12's signature and is
incompatible with the over/irrational shape (rise at m=12 to 8 at the
fitted offset; no candidate matches the data at offset 0 anywhere).
The shell tracked the under-side convergent of its word's slope at
the one scale where the candidates separate, and lagged the
irrational slope on the less-death side — the same lag-side behavior
as every golden miss-row in W6B.

Per instruction, the verdict mapping is left exactly as frozen;
whether the F5 transfer inference should consume reading (1) or
reading (2) is an integration decision outside this design's scope.
This file records both readings and the raw data. If forced to one
line: **raw D_√2(12) = 7; the offset-corrected law selection is
R-under (7/12, under side), 15/15 rows; the registered raw-value
mapping would call 7 R-coarse, but its zero-offset premise is
empirically false in this system.**

## 6. Runtime / memory

- All CPU, single process, no GPU. numpy bool occupancy arrays;
  permutations int64 (toy_automaton cache, m ≤ 15) / int32 (dedicated
  m=16 runner).
- laws + credit cross-check: ~5 s total.
- B1 controls: ~15 s.
- B2 sweep m=2..15: 1076 s wall (17.9 min), peak observed RSS 2.0 GB
  (m=15, C=16). Per-row walls in §3 table.
- Decisive-row confirmation (m=12 at C=16, C=18): 7.5 s + 8.9 s.
- m=16 dedicated runner: 1928 s wall (32.1 min) across the three
  margin-rule attempts (C=12/14/16), per-step logging throughout,
  peak observed RSS 4.2 GB (abort ceiling 7.5 GB, never approached).
- 8GB guard: never exceeded; highest observed RSS 4.2 GB.
- Total Design B wall time ≈ 55 min of computation.

## 7. Files

- `sqrt2_automaton.py` — credit word + wiring (exactness cross-check)
- `laws_table.py` / `laws.csv` / `laws_table.log` — pre-registered laws
- `crosscheck_credit.log` — Decimal cross-check record
- `b1_controls.py` / `b1_controls.log` — heredity + universality
- `b2_measurement.py` / `b2_measurement.log` / `D_sqrt2_table.csv` — D sweep
- `b2b_m16.py` / `b2b_m16.log` / `D_sqrt2_m16.csv` — dedicated m=16 row
- `b3_decisive_row_confirm.log` — m=12 at C=16/C=18
- `b3_readout.py` / `b3_readout.log` — offsets, per-row matching, verdict
