# W6X-MULTI — the two-heartbeat window kills C=11..15; both anchor readings agree death arrives, and Reading B fits a clean generalized law (2026-07-04)

Ledger W6X-MULTI. Work dir `renorm_check/shell/underlock/w6x_multi/`.
Task: extend `w6w_sparse/sparse_instrument.py`'s backward live-set
walk past the one-heartbeat construction boundary (m=53) into
multi-heartbeat windows (m=54..106), to test whether C=11 (and
C=12..15), which survive the ENTIRE one-heartbeat window with no
death, die somewhere past the second heartbeat's boundary or continue
to saturate forever.

**Headline result: they die. Both of the two independently-implemented
anchor conventions ("Reading A"/growing-end == root, and "Reading
B"/heartbeat-periodic re-anchoring) show genuine death for every C in
11..15, all within m=54..106 — the frozen "saturation continues"
prediction (60% favored) did NOT happen; the "death arrives in 54..106"
prediction (40%) HIT.**

## The instrument (`mx_core.py`)

Mechanically identical to `w6w_sparse/sparse_instrument.py`'s layered
modular backward BFS (same per-layer transition math: `parity_forced`,
`backward_pred_exact`/`backward_pred_mod`, the (R, u, v) live-set
update with u<=C, v<=C, u+v<=C legality) — reused, not reinvented, per
the mission brief (this round is about the WINDOW/anchor construction
past m=53, not the per-step transition rule, which w6w_sparse already
gated exhaustively). The ONLY new code is `letters_for(m, reading)`,
which builds the m-letter backward-consumption window for m>53, and
the multi-heartbeat plumbing around it. No state reset at k=53
anywhere: extending m past 53 is mechanically just running the SAME
loop for more layers on a longer `letters` list.

## Both anchor readings, implemented and reported, never silently picked

- **Reading A** ("growing end-anchor"): window = absolute indices
  `[0, m)` for any m. Identical in structure to
  `sparse_instrument.py`'s own `"root"` anchor for ALL m (flagged
  explicitly, per house rules) — for m<=53 this is NOT the
  gate-validated "end" anchor; it only coincides with it at m=53
  exactly.
- **Reading B** ("heartbeat-periodic re-anchoring"): anchor_end(m) =
  `53*ceil(m/53)`; window = last m letters ending at anchor_end(m).
  Reduces EXACTLY to the original gate-validated "end" anchor for
  m<=53 (anchor_end=53 always in that range).
- **Textual-evidence call, made BEFORE measuring** (see
  `DESIGN_NOTES.md`): automaton.py's Theorem 1 / shell_probe.py's P4
  (steps-invariance, tested at steps=53/106/159, always a WHOLE
  number of heartbeats) both frame the construction as "the last m
  letters of a run that is a whole number of heartbeats long" —
  Reading B is the direct generalization of that; Reading A has no
  such grounding for m>53 (it is literally the already-known-bad
  root-anchor frame, which W6W-SPARSE's own negative control showed
  diverges from corridor truth by m=29 at C=11). **The measurement
  confirms this a priori call**: Reading B is a clean monotone
  edge for all 5 C values; Reading A is intermittent (revives after
  its first "death" at 4 of 5 C values) — structurally the
  qualitatively worse-behaved object, exactly as expected going in.

### Surprise finding, reported honestly (not suppressed)

The mission brief expected the credit word to be non-periodic across
the m=54..106 test range ("steps 53..105 are NOT a repeat of steps
0..52"). Empirically (`step0_periodicity_check.py`), the credit word
IS exactly periodic with period 53 through the first SIX heartbeats
(absolute steps 0..317) — the first genuine divergence is at absolute
step 358, matching the repo's own already-known "358 vs 359" F5
landmark (a convergent-driven correction to 53/22 ≈ log2(3), not a
bug). Since this round's m=54..106 range sits entirely inside the
exactly-periodic-so-far zone, any Reading-A-vs-B difference observed
below comes purely from the anchor/window construction, not from any
drift in the underlying Sturmian word — a cleaner separation of
variables than expected, and explicitly noted as contradicting the
brief's a priori (though ultimately immaterial to the verdict).

## Validation gates (`step1_validation_gates.py` / .log) — ALL PASS

Restricted to m<=53, via Reading B (== original "end" anchor for
m<=53):

- **GATE D** (structural): `letters_for()` byte-identical to
  `sparse_instrument.py`'s own window construction at both anchor
  conventions, m ∈ {1,5,17,28,40,53}. PASS.
- **GATE A**: all ten Tier-1 edges, C=1..10 → 4, 7, 9, 12, 14, 16, 19,
  21, 24, 26 — alive-at-edge AND dead-at-edge+1, all ten, with
  exact-verified witnesses. **10/10 PASS.**
- **GATE B**: C=11 alive at every m=1..53 (no death anywhere in the
  one-heartbeat window); peak live-set size stabilizes at exactly
  **234** from m=19 through m=53 (reproduces W6W-SPARSE's own
  observation exactly); m=53 deep witness **n0=1707**, exact Collatz
  replay, deficit range exactly 11 — matches W6W-SPARSE's own archived
  deep witness exactly. **PASS.**
- **GATE C** (informative, non-blocking): Reading A reproduces the
  KNOWN root-anchor negative control at C=11, m=29..32: dead, dead,
  ALIVE, dead — exactly as W6W-SPARSE's own dictionary records.
  **PASS.**

No mismatches; no diagnosis needed; Step 2 authorized.

## The measurement (`step2_measurement.py`, `step3_analysis.py`)

C=11..15, full sweep m=54..106, BOTH readings, RSS/time watchdog.
**Peak RSS observed across the ENTIRE run: 28.9 MB** (cap 7500 MB —
nowhere close; the sparse live-set stays tiny even across a heartbeat
boundary). Total wall time for the full 2×5×53-cell sweep: 13.8s.

### Survival map, Reading B (the textually-favored, confirmed-monotone reading)

| C | last alive m | first (permanent) dead m | peak live-set | witness at edge (n0) |
|---|---|---|---|---|
| 11 | **57** | **58** | 234 | 2713 |
| 12 | **63** | **64** | 435 | 1071 |
| 13 | **68** | **69** | 750 | 4011 |
| 14 | **71** | **72** | 1286 | 4011 |
| 15 | **79** | **80** | 2336 | 23751 |

Reading B is **confirmed monotone** for all 5 C: once dead, stays dead
through m=106 (explicit check in `step3_analysis.py` §1b — no revival
for any C anywhere in the swept range). The peak live-set size at
each C matches the ONE-HEARTBEAT saturation value exactly (234,
435, 750, 1286, 2336 — i.e. the same numbers W6W-SPARSE already
measured at m=53); it never grows past that ceiling across the
heartbeat boundary — the corridor is squeezed to zero from a fixed
population, not from a growing one.

Sample of the survival grid (L=alive, .=dead; full grid in
`step2_measurement_table.csv`):

```
m:       54  58  62  66  70  74  78  82  86  90  94  98 102 106
C=11:    L   .   .   .   .   .   .   .   .   .   .   .   .   .
C=12:    L   L   L   .   .   .   .   .   .   .   .   .   .   .
C=13:    L   L   L   L   .   .   .   .   .   .   .   .   .   .
C=14:    L   L   L   L   L   .   .   .   .   .   .   .   .   .
C=15:    L   L   L   L   L   L   L   .   .   .   .   .   .   .
```

A clean staircase — later C dies later, monotonically, no plateau.

### Survival map, Reading A (growing-end/root anchor — expected worse-behaved)

| C | first "death" | true last-alive m (54..106) | monotone? | notes |
|---|---|---|---|---|
| 11 | 54 | 55 | **No** | revives once (m=55) then permanently dead |
| 12 | 58 | 62 | **No** | revives at 59,60,61,62 |
| 13 | 66 | 67 | **No** | revives once (m=67) |
| 14 | 70 | 69 | **Yes** | only C where Reading A happens to be clean |
| 15 | 73 | 79 | **No** | revives at 74, 77, 79 |

Reading A is genuinely intermittent — confirmed both by the primary
engine and independently by `mx_dfs2.py` (the second, structurally
different engine; see below). This matches its pre-registered
expectation as the worse-behaved / non-physical frame.

### C=11 death mechanism (Reading B, m=58)

Live-set size shrinks monotonically approaching death (layer sizes,
last 8 of 58: `[11, 11, 8, 4, 6, 4, 2, 0]`) — the corridor is
progressively squeezed by the cumulative deficit walk, not killed by
one exceptional letter. The live set empties at the FINAL backward
layer (j=57 of 58, consuming the last credit letter, c=1) — i.e. the
58th residue-constraint is exactly the one no surviving (R,u,v) state
can satisfy. No single "special" letter identified in the last-6
pre-death letters across C=11..15 (`[1,2,2,1,2,1]`, `[2,2,1,2,1,2]`,
`[2,2,1,2,1,2]`, `[2,1,2,1,2,2]`, `[1,2,2,1,2,1]`) — this is a
cumulative-squeeze death, not a trigger-letter death.

### Fit attempt (Step 4 of the mission)

Does a corrected law fit Reading B's new edges? Tested the direct
two-heartbeat analog of the original closed form — literally the same
`⌊53(C+1)/22⌋`, with 53 replaced by 106 (steps doubled to match two
heartbeats): `⌊106(C+1)/22⌋`.

| C | observed edge (B) | ⌊106(C+1)/22⌋ | residual |
|---|---|---|---|
| 11 | 57 | 57 | 0 |
| 12 | 63 | 62 | +1 |
| 13 | 68 | 67 | +1 |
| 14 | 71 | 72 | −1 |
| 15 | 79 | 77 | +2 |

Mean absolute residual **1.0**, no systematic drift (residuals
−1..+2, not monotonically growing) — an honest, non-forced fit. This
is a genuinely encouraging finding: **the SAME closed-form law,
literally generalized to `steps` heartbeats via `⌊53n(C+1)/22⌋` for n
heartbeats, may be the right multi-heartbeat capacity law after all**
— the one-heartbeat "saturation" at C≥11 was an artifact of the
one-heartbeat window being too short to see the death, not evidence
the countdown-ladder concept itself ends at C=11. (5 points is not
enough to be certain this holds at n=3+ heartbeats or larger C — flagged
as an open follow-on, not claimed as proven.)

For Reading A, no simple law fits (nor would fitting one be
meaningful — Reading A is not a clean single-edge object to begin
with; see intermittency above).

## Witness verification (all exact, per house rules)

Every alive cell's witness (both readings, entire swept range) was
exact-integer certified via `verify_witness_exact`: backward exact-rho
reconstruction from ρ=1, TRUE forward Collatz replay (odd steps, exact
division at every step, arbitrary precision), and deficit-range check
against C. **All witnesses in the full sweep: `all_ok=True`, zero
exceptions.**

Trajectory-length characterization (`step3_analysis.py` §3): for
several witnesses, the FULL Collatz odd-step-count to 1 equals (or is
very close to) the m at which that integer surfaced as a witness — for
example n0=1707 needs exactly 53 odd steps (surfaces as witness at
m=53); n0=4011 needs 68 (surfaces at the C=13 Reading-B edge, m=68);
n0=23751 needs 79 (surfaces at the C=15 Reading-B edge, m=79 exactly).
These are genuine slow-descender integers whose entire forward
trajectory length matches the corridor window depth — not partial-
window artifacts. Only **n0=1707** from W6W-SPARSE's specific
previously-named family (839, 559, 745, 993, 1707) reappears verbatim
in this round's witness set (at the Gate B check, m=53); the other
four don't resurface as THE witness returned at these particular new
cells (a different, but structurally analogous, integer is returned
at each — the search returns "any" surviving state, not all of them,
so non-recurrence of a specific integer is not itself evidence against
the slow-descender-family picture).

## Independent re-derivation (`mx_dfs2.py` / `step5_independent_engine.log`)

Second engine, genuinely different in kind from BOTH prior engines
(not a rename of w6w_sparse's own DFS, per the mission's explicit
instruction):

- Primary (`mx_core.sparse_survival_multi`): iterative layered BFS,
  dict-per-layer, state key `(R mod 3^(m-j), u, v)`.
- w6w_sparse's own second engine (not reused): recursive DFS +
  failure-memo keyed on `(j, rho mod 3^(m-j), u, v)`.
- **mx_dfs2 (this round's second engine)**: EXPLICIT STACK (no Python
  recursion at all), **NO memoization whatsoever** (a genuinely
  different, weaker-cache traversal — relies purely on the corridor
  prune + depth-first early exit), and rho carried as an EXACT,
  UNBOUNDED big int throughout (never truncated to a residue at all,
  unlike the primary engine) until the final witness check.

Cross-checked at 15 cells spanning both readings, both the clean
Reading-B edges and the Reading-A intermittency/"revival" cells found
during analysis. **15/15 agreement, zero disagreements**, all
witnesses re-verified exact. The revival phenomenon under Reading A
(e.g. C=11 dead at m=54, alive again at m=55) is independently
confirmed by this structurally unrelated engine — not a BFS-specific
bug.

## Frozen predictions — HIT/MISS, stated plainly

- **"C=11 death arrives in 54..106" (40%): HIT.** Not just C=11 —
  ALL of C=11..15 die within this window, under BOTH anchor readings.
- **"Saturation continues through 106" (60%, favored, with a specific
  lean toward n0=1707-class survivors being real slow-descenders and
  the one-heartbeat result being corridor truth): MISS.** The
  one-heartbeat "no death" result was an artifact of the one-heartbeat
  construction boundary, exactly the (a)-vs-(b) ambiguity the
  Architect's verdict flagged going in — outcome (b) (construction
  artifact) is what happened, not (a) (corridor truth). The
  n0=1707-class integers ARE real slow-descenders (verified again this
  round), but they run out of runway once the window is long enough to
  see their full trajectory length — which is exactly what a corridor
  window is supposed to detect, once it's long enough.

## Honest walls

- **None hit.** RSS peaked at 28.9 MB (cap 7500 MB) across the entire
  measurement; every cell ran in well under a second; no state-cap or
  time-cap triggered anywhere in m=54..106 for C=11..15.
- **Process bug found and fixed IN-ROUND, recorded honestly**: v1 of
  `step2_measurement.py` broke its per-(C,reading) m-loop at the FIRST
  dead cell, which is correct for Reading B (confirmed monotone) but
  silently truncated Reading A's data past its first death — hiding
  the intermittent revivals entirely. Caught during `step3_analysis.py`
  cross-checking (C=13 Reading A showed alive at m=67 in a manual
  probe but was absent from the recorded sweep), fixed by removing the
  early break (sweep is cheap enough — <14s total — that there is no
  cost to always completing the full range), and the full sweep was
  re-run. No measurement in this ledger depends on the buggy v1 output;
  all numbers above are from the corrected re-run.
- **Scope limit, not a wall**: the credit-word periodicity check
  (`step0_periodicity_check.py`) only searched out to block 299
  (~step 15,900) for the first post-317 divergence claim's block
  number; the actual first divergence (step 358, block 6) was found
  well within that search, so this is not a limiting factor for
  anything measured this round, but is noted as a bounded search, not
  an exhaustive proof of no-earlier-divergence beyond what was swept.
- No RSS, time, or state-cap wall of any kind was hit anywhere in this
  round's work. This is itself worth flagging as slightly surprising
  given the mission's 8GB budget framing — the sparse instrument's
  death-shell-driven live-set stays tiny (peak 2336 states at C=15)
  even across a heartbeat boundary, so the entire multi-heartbeat
  question turned out to be cheap once the window-construction design
  question was resolved.

## Artifacts (all under `renorm_check/shell/underlock/w6x_multi/`)

- `DESIGN_NOTES.md` — pre-registered design reasoning (both anchor
  readings, textual-evidence call, periodicity note).
- `mx_core.py` — core multi-heartbeat instrument (letters_for, both
  readings, sparse_survival_multi, witness reconstruction/verification).
- `step0_periodicity_check.py` + `.log` — credit-word periodicity
  sanity check (the "surprise finding" above).
- `step1_validation_gates.py` + `.log` — all blocking gates (A, B, D)
  plus informative Gate C, all PASS.
- `step2_measurement.py` + `.log` + `step2_measurement_table.csv` +
  `step2_measurement_full.json` — the full m=54..106 × C=11..15 ×
  {A,B} sweep (corrected version, no early-break bug).
- `step3_analysis.py` + `.log` — exact edges, monotonicity check,
  death-mechanism traces, witness trajectory-length characterization,
  fit attempts.
- `summary_edges_table.csv` — compact per-(C,reading) edge summary.
- `mx_dfs2.py` + `step5_independent_engine.log` — independent second
  engine (explicit-stack, no-memo, exact-big-int) and its 15/15
  agreement cross-check against the primary.
- This file.

No git commits, per house rules. CPU only. Peak RSS this round:
28.9 MB (well under the 8GB / 7500MB cap). Total measurement wall time
across all scripts: well under one minute.
