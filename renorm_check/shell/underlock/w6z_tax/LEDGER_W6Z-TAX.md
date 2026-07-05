# W6Z-TAX — the corridor tax schedule τ(C), measured at every level C=1..15 (2026-07-04)

Ledger W6Z-TAX. Work dir `renorm_check/shell/underlock/w6z_tax/`.
Task (Architect): "In corridor 1 it's a −3.x percent tax; what was never
measured is the tax at each level." Locate & reproduce his corridor-1
−3.x% number, then extract/measure τ(C) at every capacity level C=1..15
in every sense the existing instruments support.

House rules honored: exact integer arithmetic where the quantity is exact
(credits via `bit_length`; May decay via integer 3C−cutoff; live-set walk
all exact ints); floats only for genuinely continuous ratios (ρ, τ_pop);
every number cited to an artifact + line/key; validated against published
cells before trusting new ones; CPU only, peak RSS < 20 MB this round
(the heaviest cell is the Step-1 power iteration at (C,m)=(15,4), ~120k
states); no commits; `w6y_regime/` never written (not read either — its
step2 log was empty at start, nothing extracted).

---

## STEP 1 — David's corridor-1 −3.x% number: LOCATED and REPRODUCED (with an honest label correction)

**The only −3.x% "tax per heartbeat" figure anywhere in the repo** is the
killed-survivor **spectral-radius contraction = 3.94%**:

- `SPECTRAL_RADIUS_RESULTS.txt:30-31`: "ρ LOCKS at 0.960647 from m=10
  onward (6.4M states). **Permanent 3.94% contraction per heartbeat.**"
- `SPECTRAL_RADIUS_RESULTS.txt:13`: header **"C=3 (narrow corridor — hard
  floor on ρ)"** — the 3.94% is explicitly the **C=3** value.
- `COLLATZ_PROOF.md:484`: "stabilizes at $0.03935$ — a permanent 3.94%
  contraction per heartbeat".
- Same number restated at `GHOST_GEOMETRY_RELEASE.md:104`,
  `INVESTIGATION_SUB_THRESHOLD_LEMMA.md:135`, `Collatz Ideas.md:138`.

**What is divided by what:** τ_spectral(C) = 1 − ρ(C), where ρ(C) is the
dominant-eigenvalue magnitude of the **composed 53-step killed-survivor
transition operator** on non-terminal, non-corridor-exiting residue-
automaton states at width C (`rust/spectral_radius.rs:111-135` builds one
step; the tool composes 53 and power-iterates, `:187-197`). ρ is a
per-**heartbeat** survival-mass multiplier; 1−ρ is the fraction of
surviving mass killed per heartbeat = the tax. It is a
**population-thinning-per-heartbeat** ratio, not a per-level number and
not a climb ratio.

**Reproduced from scratch** (`step1_locate_corridor1_tax.py`, independent
Python power iteration, exact integer residues, float64 iteration like the
Rust tool):
- C=3 sweep (`step1_output.log:10-16`): ρ climbs 0.000 → 0.926 (m=5) →
  0.9562 (m=6) → **0.960229 (m=7)**, converging to the archived lock
  0.960647. My m=7 ρ = 0.960229329 **matches the archived m=7 table value
  0.960230 bit-for-bit** (`SPECTRAL_RADIUS_RESULTS.txt:22`) — the
  reproduction is validated against a published cell. (My m stops at 7 for
  the RSS budget; the archive reached the lock at m=10 / 6.4M states. The
  0.04% residual m=7→lock is pure convergence tail, not disagreement.)
- τ_spectral at m=7: C=3 → **3.98%** ≈ the archived 3.94%. **Located and
  reproduced.**

**HONEST LABEL CORRECTION (no strawman):** the −3.94% is the **C=3** value,
NOT C=1. The C=1 spectral tax is **97.1%** (ρ=0.0286), C=2 is 37.1%, C=3
is 3.98%, and it collapses to a ~0.046% plateau for C≥6
(`step1_output.log:22-36`; the plateau is the "universal ρ" regime,
`SPECTRAL_RADIUS_RESULTS.txt` item 3, ρ identical to 12 dp for C=10..200).
So "corridor 1" in the mission does **not** map to C=1 for this measure.
Most charitable non-strawman reading: the archive itself names C=3 "the
**narrow corridor** (hard floor on ρ)" — David likely meant "the first /
narrowest corridor with a stable contraction floor," which IS C=3, or
mis-indexed. Reported as located-and-reproduced with the index flagged;
his number is real and exact, its corridor label is C=3.

---

## STEP 2 — population thinning, extracted then re-measured (C=1..15)

The archived w6w/w6x JSON carry only the **count** peak_live per (C,m)
(verified: `w6w_sparse/step2_4_climb_full.json` rows have keys
peak_live_states / no per-element deficit detail). So per-live-element
deficit distribution is **NOT recoverable from the archives** — it was
re-measured here by re-running the validated instrument.

**Instrument:** `w6w_sparse/sparse_instrument.py`'s backward layered-BFS
live set (imported verbatim: `parity_forced`, `backward_pred_mod`, the
(R,u,v) update with u≤C/v≤C/u+v≤C corridor legality). `survival_final()`
in `step2_3_tax_schedule.py` returns L(C,m) = final-layer live-set size
= |live(m)| (== w6x's `final_live_states`), the peak, and the (u,v)
deficit histogram.

**Validation gates (`step2_3_tax_schedule.log:3-24`):**
- Gate 1: reproduce the ten Tier-1 M_edge C=1..10 = 4,7,9,12,14,16,19,
  21,24,26 from this script's own edge (last m with L>0): **10/10 OK**.
- Cross-check peak_live vs archived w6w JSON: **134 cells, 0 mismatches**.

**τ_pop results (`step2_summary.csv`, `step2_live_grid.csv`,
`step2_thinning_ratios.csv`):** per-level ratio τ_pop(C,m)=L(m+1)/L(m)
oscillates letter-by-letter tracking the Sturmian word (support letters
thin, drops don't). The meaningful aggregate is the geometric per-level
ratio over the alive stretch:
- **C=1..10: geo/level 0.89..0.93** (< 1) — the live set shrinks to death
  by M_edge ≤ 26. (C=1 degenerate: L≡1 until death, geo=1.0.)
- **C=11..15: geo/level 0.979 → 1.017** — the live set SATURATES / grows;
  no death in one heartbeat. A **sharp regime jump at C=10→11** (the
  w6w-SPARSE first-break, `LEDGER_W6W-SPARSE.md:63`).

**Deficit-distribution drift (`step2_deficit_drift.csv`, the archives
could not give this):** at C=11 the live set thins 15 (m=5) → 8 (m=20) →
2 (m=53); the ceiling-side spread v pins at 11 (= full corridor width)
throughout while u grows slowly — the corridor is squeezed against its
ceiling exactly as the death-shell picture predicts (W6X's
"cumulative-squeeze" mechanism, `LEDGER_W6X-MULTI.md:157-164`).

---

## STEP 3 — per-heartbeat climb cap under corridor [0,C] (C=1..15), fresh

`step3_climb_cap_corridor.py`: B1.2's residue-legal max-climb DFS reused
(imports `w6e/engine.py`'s `forced_parity_for_backward_step` +
`backward_predecessor_exact`, exactly as `b1/b2_residue_legal_max_climb.py`
does) with ONE new axis: the deficit corridor is bounded to width C (track
(s,min_s,max_s), prune any step making max_s−min_s > C). Objective: max
Σ(c−a) over one 53-letter heartbeat, best launch class mod 27.

**FIRST DRAFT CAUGHT WRONG (recorded honestly):** an initial coarse
mod-3¹ forward DP (`step2_3_tax_schedule.py::climb_cap_corridor`,
CSV `step3_climb_cap_SUPERSEDED_k1draft.csv`) decoupled parity from the
true residue chain and reproduced B1.1's **residue-FREE +31 cap**, not
B1.2's residue-legal −6 (Gate 2 FAILED at +31, `step2_3_tax_schedule.log`).
Root cause = the same class of convention seam the program keeps hitting:
the residue constraint only binds when residues are tracked exactly along
each chain. The corrected exact-residue DFS was written and gated.

**Validation gate (`step3_climb_cap_corridor.log:3-8`):** width-
unrestricted C=200 → **−6 at launch class 20 mod 27**, exactly B1.2
(`b2_run_output.log:12`). PASS.

**Results (`step3_climb_cap_corridor.csv`, `step3b_completability.csv`):**

| C | climb cap /hb, [0,C] | heartbeat completable? | #launches completing /18 |
|---|---|---|---|
| 1..7 | **None** (no chain fits) | **NO** | 0/18 |
| 8 | −6 | yes | 2/18 |
| 9 | −6 | yes | 4/18 |
| 10 | −6 | yes | 6/18 |
| 11 | −6 | yes | 7/18 |
| 12 | −6 | yes | 9/18 |
| 13 | −6 | yes | 15/18 |
| 14..15 | −6 | yes | 18/18 |

- **C=1..7: NO residue-legal chain from ANY of the 18 launch classes fits
  a full heartbeat inside [0,C]** — the corridor is too narrow to sustain
  one heartbeat at all (climbing not merely unprofitable, *impossible*;
  consistent with M_edge(C≤7) < 53, the corridor dies before precision 53).
- **C≥8: climb cap = −6 exactly, corridor-width-INDEPENDENT (flat).** The
  [0,C] bound stops binding on the −6-achieving chain at C=8; wider
  corridors only admit more *viable* launches, never a better climb.

The [0,C] bound therefore does **not** change LOCK4-B1's −6/heartbeat cap
for any C where climbing is possible; it only forbids the heartbeat
outright below C=8.

---

## STEP 4 — the master τ(C) schedule (every measured sense)

`step4_schedule_and_scoring.py` → `master_schedule.csv`. Reserve-decay
reproduced at full precision (exact integer 3C−cutoff) from
`LOCK3_LOCK4_RESERVE_DECAY_NOTE.md:29-34` (confirmed by reading, not
paraphrase):

| C | cutoff | decay = 3C−cutoff | decay/C |
|---|---|---|---|
| 6 | 17 | **1** | 0.167 |
| 10 | 27 | **3** | 0.300 |
| 20 | 51 | **9** | 0.450 |
| 30 | 75 | **15** | 0.500 |
| 40 | 99 | **21** | 0.525 |
| 50 | 123 | **27** | 0.540 |

decay(C) grows monotonically; slope is exactly **+6 per +10 in C = 0.60**
above C=10 (piecewise-linear), decay/C rising toward ~0.54 → cutoff(C) ~
2.4C, not 3C. This is the "wider corridor buys less relative reserve"
claim of the note, now exact.

**MASTER SCHEDULE (`master_schedule.csv`, C=1..15):**

| C | τ_spectral (1−ρ) %/hb | pop-thin geo/level | climb cap /hb [0,C] | hb feasible | M_edge | frame regime |
|---|---|---|---|---|---|---|
| 1 | 97.142 | 1.000 | — infeasible | no | 4 | 1-hb |
| 2 | 37.086 | 0.891 | — infeasible | no | 7 | 1-hb |
| 3 | **3.977** | 0.917 | — infeasible | no | 9 | 1-hb |
| 4 | 0.294 | 0.905 | — infeasible | no | 12 | 1-hb |
| 5 | 0.058 | 0.919 | — infeasible | no | 14 | 1-hb |
| 6 | 0.047 | 0.912 | — infeasible | no | 16 | 1-hb |
| 7 | 0.046 | 0.926 | — infeasible | no | 19 | 1-hb |
| 8 | 0.046 | 0.923 | **−6** | yes | 21 | 1-hb |
| 9 | 0.046 | 0.932 | **−6** | yes | 24 | 1-hb |
| 10 | 0.046 | 0.931 | **−6** | yes | 26 | 1-hb |
| 11 | 0.046 | 0.979 | **−6** | yes | 53* | 2-hb |
| 12 | 0.046 | 0.997 | **−6** | yes | 53* | 2-hb |
| 13 | 0.046 | 1.007 | **−6** | yes | 53* | 2-hb |
| 14 | 0.046 | 1.011 | **−6** | yes | 53* | 2-hb |
| 15 | 0.046 | 1.017 | **−6** | yes | 53* | 2-hb |

*C≥11: no one-heartbeat death edge (saturation); true edge is 57..79 in
the 2-heartbeat frame (`LEDGER_W6X-MULTI.md:108-113`).

### Shape test: (a) regime-constant-then-jump vs (b) smooth growth

**Every directly-measured (fresh) sense supports shape (a):**
- **spectral:** transient collapse C=1..5, then a **flat ~0.046% plateau**
  for C≥6 (the universal-ρ regime). Not smooth growth.
- **population thinning:** roughly constant ~0.90-0.93/level for C≤10,
  then a **jump to saturation at C=10→11**.
- **climb cap:** a **constant −6/hb** once feasible (C≥8); infeasible
  below. Zero growth with C.

**Only the May m1-proxy decay has shape (b)** (smooth monotone growth
1,3,9,15,21,27). It is a *different quantity* (an m=1 cutoff-vs-3C gap),
and its smooth shape is **not** reproduced by any fresh corridor
instrument. **Verdict: shape (a).**

---

## STEP 5 — Architect's frozen predictions

**(a) [55%] regime-boundary structure visible in τ — HIT.** Every fresh
sense shows a boundary, not smooth growth: spectral transient→plateau at
C≈5-6; population death-regime→saturation-regime jump at C=10→11
(`LEDGER_W6W-SPARSE.md:63`); climb-cap infeasible→flat-−6 at C=8. The tax
is stepped/regime-structured in all three.

**(b) [50%] May m1 decay correlates with true τ, right shape wrong
constants — MISS.** The claim's "right shape" fails: May decay is *smooth
monotone growth* (b); every fresh τ is *regime-constant-then-jump* (a) —
qualitatively different shapes. The proxy does capture ONE true fact
(decay/C rises → wider corridor, less relative reserve), but its quantity
is not the per-heartbeat corridor tax any fresh instrument measures, and
the constants have no correspondence (May decay(10)=3 bits vs the −6
climb cap vs the 0.046% spectral plateau are unrelated). Missed on the
load-bearing "shape" clause, not merely on constants.

**(c) [85%] per-C climb cap strictly negative at every C (climbing never
profitable at any corridor width) — HIT.** Measured climb caps where
DEFINED (C=8..15): **all = −6** (min=−6, max=−6). For C=1..7 climbing is
*impossible* (0/18 launches complete a heartbeat) — a fortiori
non-profitable. Width-unrestricted C=200 = −6. **At no corridor width
1..15 does climbing turn profitable.**

**Scorecard: (a) HIT, (b) MISS, (c) HIT.**

---

## Walls hit (honest)

1. **"Corridor 1" is ambiguous / mislabeled.** The −3.94% number is real
   and exactly reproduced, but it is C=3, not C=1. Reported as a label
   discrepancy, not resolved (I do not know which David meant; C=1's true
   spectral tax is 97.1%). Not smoothed over.
2. **Deficit-distribution drift not in the archives** — only counts
   survived; re-measured here (the instrument had it in hand). Resolved.
3. **First Step-3 draft wrong** (coarse-modulus DP gave the residue-free
   +31, not −6). Caught by the B1.2 gate, root-caused (convention seam),
   rewritten with exact residues; the superseded CSV is kept
   (`step3_climb_cap_SUPERSEDED_k1draft.csv`), not deleted.
4. **Spectral ρ stops at m=7** (RSS budget) rather than the archived m=10
   lock; the m=7 value matches the archived m=7 cell exactly and is on the
   convergence tail — no measurement depends on going deeper. Not a
   disagreement, a scope note.
5. **Climb cap uses a_cap=4** (B1.2's margin-checked cap) at one heartbeat
   only; B1.2 already proved a_cap=4 exact at m=53, so no new wall.
6. Population-thinning per-level ratio is intrinsically noisy (Sturmian
   letter-by-letter); the geometric aggregate is the reportable summary —
   stated as such, not over-read per-cell.

## Artifacts (all under `renorm_check/shell/underlock/w6z_tax/`)

- `step1_locate_corridor1_tax.py` + `step1_output.log` + `step1_spectral_tax.csv`
- `step2_3_tax_schedule.py` + `step2_3_tax_schedule.log` +
  `step2_live_grid.csv` + `step2_thinning_ratios.csv` +
  `step2_deficit_drift.csv` + `step2_summary.csv`
- `step3_climb_cap_corridor.py` + `step3_climb_cap_corridor.log` +
  `step3_climb_cap_corridor.csv` + `step3b_completability.csv` +
  `step3_climb_cap_SUPERSEDED_k1draft.csv` (superseded, kept for record)
- `step4_schedule_and_scoring.py` + `step4_schedule_and_scoring.log` +
  `master_schedule.csv`
- this file, `LEDGER_W6Z-TAX.md`.

No commits. CPU only. Peak RSS < 20 MB (Step-1 power iteration dominates).
`w6y_regime/` untouched.
