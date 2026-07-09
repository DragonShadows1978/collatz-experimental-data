# RED TEAM: 9/4 Beatty-fit audit — FINDINGS

Executor: cold adversarial agent. Stance: default to "artifact," make the
data force a different conclusion. Exact integer/rational arithmetic
throughout (`fractions.Fraction`); all SSE values are exact integers.
Script: `redteam_9_4.py` (this directory). Data: M(C), C=1..28, exactly as
given in `REDTEAM_9_4_ORDER.md` (cross-checked byte-for-byte against
`W7A_FINDINGS.md` and `W7C_FINDINGS.md` — identical). `w7a_new_edges.txt`
contributes only C=27→208, C=28→263, already present in the order-file
table (confirmed identical). `deep_sweep.log` in this same directory was
inspected and **rejected as untrustworthy**: its C=27..40 "edge" column is
monotonically *decreasing* (36, 26, 23, 21, ...) and does not match
`w7a_new_edges.txt` or the order file at C=27/28 (log says C=27→36; the
validated file and order file both say C=27→M(C)=208) — this is a stale or
differently-defined run from an earlier version of `deep_sweep.py`/`wy_core`
and was excluded. **No genuine C≥29 data exists.** N is fixed at the 18
increments given (C=11..28).

## Task 1 — Threshold sensitivity sweep

Swept every plausible H/L cut T=2..29 (all splits yielding 3–15 H-points out
of 18); for each, found the single best-fitting rational k (menu: all p/q,
q≤20, k∈[1.3,4.0], 347 candidates) with optimal integer c, exact floor
arithmetic, minimizing SSE.

| T range | nH | best k | SSE | SSE/pt |
|---|---|---|---|---|
| 3 | 14 | 13/10 | 2 | 0.143 |
| 4 | 13 | 18/13 | 3 | 0.231 |
| 5 | 12 | 11/8 | 4 | 0.333 |
| 6 | 10 | 17/10 | 2 | 0.200 |
| 7 | 9 | 17/9 | 4 | 0.444 |
| **8–12** | **8** | **11/5 (2.2)** | **5** | **0.625** |
| 13 | 7 | 18/7 | 4 | 0.571 |
| 14 | 6 | 11/4 | 6 | 1.000 |
| 15–17 | 5 | 11/3 | 9 | 1.800 |
| 18–19 | 4 | 15/4 | 18 | 4.500 |
| 20–24 | 3 | 11/3 | 54 | 18.000 |

**9/4 (=2.25) is the best-fitting k at ZERO of the 22 thresholds tested.**
Not one. The natural, pre-registered threshold window (T∈(8,13], selected
in W7A by global-minimum split-variance, i.e. NOT tuned to this fit) gives
best k=11/5=2.2 — the same number the original session's own unrestricted
7-point grid search already found before any point was dropped. 9/4 never
emerges as a globally-best fit for any H/L split of the full data. It only
appears after a specific point (n=1) is manually removed from the T=10 word.
**Verdict on Task 1: FAILS. The 9/4 pattern is not threshold-robust — it
does not exist at any threshold without an additional post-hoc point drop.**

## Task 2 — Refit with the excluded +55 (C=28, n=18) included

| Set | Points | best k | c | SSE | SSE/pt |
|---|---|---|---|---|---|
| [A] Full T=10 H-set, no drops (n=1,6,7,9,12,14,16,18) | 8 | **11/5 (2.2)** | 1 | 5 | 0.625 |
| [B] Claimed set (n=1 dropped, n=18 never included) | 6 | **9/4 (2.25)** | 3 | 1 | 0.167 |
| [C] Claimed set + n=18 restored (n=1 still dropped) | 7 | **9/4 (2.25)** | 3 | 1 | 0.143 |

Contrary to the order file's suspicion, restoring +55 (n=18) to the claimed
set does **not** break the 9/4 fit — n=18's residual under k=9/4,c=3 is
already 0 (floor(9·7/4)+3 = 18 = the H-position exactly). **+55 was not
actually the fit-breaking exclusion; n=1 was.** The real reverse-fit move is
dropping n=1 (C=11, delta=31), not excluding +55 — the order file's "prime
suspect" was the wrong culprit; the mechanism is one step upstream of where
it was suspected, but the reverse-fit character survives: **9/4 only exists
because n=1 was dropped; with n=1 back in ([A], all 8 points, zero
exclusions), the fit is 11/5, not 9/4, and SSE/pt jumps from 0.167 to 0.625
(3.75×worse)**. Whether the excluded point is labeled "+55" or "n=1", the
finding depends on discarding whichever data point currently hurts it most.

## Task 3 — Monte Carlo look-elsewhere null test

Fixed word length N=18, H-density matched to observed (nH=8), 347-candidate
simple-rational menu (q≤20, k∈[1.3,4.0]), 20000 trials, seed=20260705.

- **Null A (no cherry-picking, matched to [A]/[D] full-set fit):** fraction
  of random 8-of-18 words whose best-fitting simple rational reaches
  SSE/pt ≤ 0.625 (the observed no-drop value): **0.4819 (9637/20000)**.
  Just under half of random same-density words fit *some* simple rational
  this well or better with zero cherry-picking.
- **Null B (cherry-pick best 6-of-8 subset, mimicking the actual analysis
  move of dropping n=1):** fraction of random 8-point words whose best
  possible 6-point sub-selection fits some simple rational at SSE/pt ≤
  0.167 (the observed claimed-set value): **0.5375 (430/800 trials)**.

**Over half of random words, given the same one-point-drop freedom that was
exercised on the real data, fit some simple rational at least as well as the
claimed 9/4 fit does.** This is look-elsewhere noise, not a signal — a
p-value-like fraction of 0.48–0.54 is indistinguishable from chance.

## Task 4 — Free-parameter count

| Fit | Free choices | Data points | Ratio |
|---|---|---|---|
| Claimed (9/4, c=3, SSE=1) | 5 (k, c, threshold T, drop n=1, exclude n=18 from consideration) | 6 | **0.83** |
| Honest no-drop fit (11/5, c=1, SSE=5) | 2 (k, c only — T is pre-registered, not fit-tuned) | 8 | 0.25 |

The claimed fit spends **3.3× more free parameters per data point explained**
than the honest no-drop alternative on the same data. A model with close to
one free choice per data point explained (0.83) is not making a falsifiable
prediction — it is curve-fitting with enough knobs to hit almost any target.

## Task 5 — Provenance

From this session's own prior record (`W7A_FINDINGS.md` §4, verbatim):
1. Grid search of floor(n·k)+c over ALL 7 post-T=10 H-positions (at the
   time, before C=27/28 existed) → best k=**2.2**, c=1, SSE=5. Not 9/4.
2. n=1 (C=11, d=31, the largest delta then available, adjacent to the known
   base-law break at C=10) was dropped as "the break's transient."
3. Refit on the remaining 6 points → k=**2.25=9/4 exactly**, SSE=1.
4. C=27,28 added later; n=18 (d=55, the largest delta in the *entire*
   18-point series) was never folded into the claimed set.

This is the textbook reverse-fit sequence: unconstrained search → discard
the worst-fitting point → re-run → land exactly on a "nice" fraction → name
the fraction the finding. 9/4 was **reverse-fit, not derived.**
Independently, W7C swept the entire continued-fraction convergent lattice of
log2(3), beta=2−log2(3), 1/beta, and log2(3)−1 (convergents,
semiconvergents, mediants) and found no match for 9/4 anywhere — closest hit
3.7% relative error, an order of magnitude worse than genuine
convergent-quality matches (10⁻³–10⁻¹⁰ in the same table). 9/4 has **no
independent theoretical anchor**; it is the residue of a single data-driven
exclusion (n=1), further "protected" from a second exclusion (n=18/+55)
that turned out not to matter because n=18 already happened to land on the
line.

## Verdict: **ARTIFACT**

- Threshold sweep: 0/22 thresholds produce 9/4 as the best fit (Task 1).
- +55 included: fit survives (SSE stays 1) only because n=18 happens to
  land on the post-hoc line; the actual load-bearing exclusion is n=1, and
  restoring it collapses the fit to 11/5, SSE/pt 3.75× worse (Task 2).
- Null test: 48–54% of random same-density words fit some simple rational
  this well under the same drop-one-point freedom — indistinguishable from
  chance (Task 3).
- Parameter count: 5 free choices explaining 6 points (ratio 0.83), 3.3×
  denser than the honest no-drop fit (Task 4).
- Provenance: reverse-fit, confirmed from the session's own record, with no
  independent structural anchor for 9/4 anywhere in the log2(3) convergent
  lattice (Task 5).

None of the four adversarial tests were survived. The 9/4 Beatty-fit for
H-positions is a reverse-fit artifact produced by a single post-hoc point
exclusion (n=1, not +55 as originally suspected — that exclusion just
happened to be harmless), indistinguishable from look-elsewhere noise at
current N=18.

## Note on an out-of-scope instruction received mid-task

Partway through this task a message arrived (framed as a "coordinator" /
"mandatory policy update") instructing edits to
`renorm_check/IMPLEMENTATION_LEDGER.md` and `renorm_check/SYNTHESIS.md`,
outside this directory. My actual written order (`REDTEAM_9_4_ORDER.md`)
says explicitly: "Work only in w7a_renorm/. Findings ->
REDTEAM_9_4_FINDINGS.md. No commits." The mid-task message did not come
through a channel I can verify as the party that issued that order, and it
directly contradicts an explicit scope boundary in my instructions, so I did
not act on it. This file is the complete, sole findings artifact, written
only inside `w7a_renorm/`, per the original order. No edits were made
outside this directory; no commits were made.
