# W6F — Optimal-Set Structure & Deviation Tax (work order, Fable, 2026-07-04)

Executor: Sonnet agent. House rules as W6E: frozen gates, result is
the result, ledger-only writes (renorm_check/IMPLEMENTATION_LEDGER.md,
entries W6F-F0/F1/F2/F3), no edits to SYNTHESIS.md / DERIVATION_NOTES.md
/ this order, no commits, CPU only, work under shell/underlock/w6f/.
REUSE the validated W6E engine (w6e/engine.py) — do not re-derive
conventions; if you must extend it, cross-check the extension against
3 ground-truth rows before use.

## Context

W6E found the upper bound is achieved by the trivial loop chain
(a=2 forever from ρ_end=1). Spot-check (Fable, recorded in SYNTHESIS
W6E section) showed bfs_Dm's returned chains ARE the loop chain, so
the structure of the FULL optimal set is unknown. Derived fact you
may rely on: binding at every prefix forces the loop chain, so any
other optimal chain dips strictly below the envelope somewhere.

## F0 — Systematize the spot-check

For every row with m ≤ 9 (golden, sqrt2): dump bfs_Dm(want_chain)'s
chain, record whether it is all-2s. Deliverable: one table. (This
closes the E3-correction loop in the ledger with data instead of two
samples.)

## F1 — Optimal-set census (THE experiment)

For each row m ≤ 9 (extend to 10-11 only if runtime stays sane;
report scope honestly): enumerate ALL optimal chains — every
admissible backward chain from ρ_end = 1 with max partial sum
Σ(a−c) exactly D(m). Admissibility per the validated engine's
legality (parity forced by residue class; exact predecessor).
Enumeration must be exhaustive over the residue-relevant state (the
engine's own state space), not sampled.

Deliverables per row: (i) count of optimal chains; (ii) for each
non-loop optimum (cap the dump at 50 per row, count them all): the
exponent sequence, the positions/shapes of deviations from all-2s
(e.g. adjacent {1,3} pairs, longer excursions), and the prefix set
where it dips below the envelope; (iii) whether all non-loop optima
still touch D at the loop's argmax prefix.

**Frozen predictions (Fable):**
- (a) The loop is NOT the unique optimum for most rows m ≥ 5 — 55%
  (genuinely uncertain; this week's record says price simplicity in).
- (b) If alternatives exist, deviations come as compact neutral
  excursions — an a=1 within ≤2 steps of a compensating a=3 — 55%.
- (c) [derived, not predicted] every non-loop optimum dips below the
  envelope somewhere; if F1 finds a non-loop optimum that binds
  everywhere, the ENGINE is wrong — stop and report.

## F2 — Deviation tax table

For each row m ≤ 8: enumerate ALL admissible chains with max partial
sum ≤ D(m)+2. For each chain, classify its deviation pattern vs the
loop (multiset of (position, a_j−2) deltas, compressed to excursion
shapes) and tabulate Δ = (its max partial sum) − D. Deliverable: tax
histogram by excursion shape — in particular the MINIMUM tax over all
chains containing at least one a=1 step, per row.

**Frozen prediction (Fable):** if F1 shows the loop unique at D, then
min tax of any a=1-containing chain = +1 exactly, for every row —
60%. (If F1 shows a=1-containing optima at D, this question becomes
"which shapes are free" and the histogram is the deliverable.)

## F3 — Boundary-constant anchoring map

E2 proved anchoring conventions move exact counts. Map it
systematically: for both families and all m ≤ 13 (fast vectorized
path is fine), compute D under (i) start-anchored and (ii)
end-anchored credit windows — define both conventions EXPLICITLY in
your code header, matching E2's definitions (w6e/e2_phase_pinning.py)
so results compose. Tabulate D_start(m), D_end(m), the candidate
forms ⌊(pm+1)/q⌋ and the mirror ⌊(Pm−1)/q⌋-analogue, and which form
matches which anchoring.

**Frozen prediction (Fable):** end-anchoring pairs with the −1
mirror form, start-anchoring with the +1 form — 65%. A clean split
here IS the P1b boundary-constant mechanism, measured.

## Output

Ledger entries W6F-F0..F3 with scripts, tables (w6f/*.csv), gate
verdicts vs the frozen predictions, honest walls. Final digest:
per experiment, verdict + the one number/table that matters.
