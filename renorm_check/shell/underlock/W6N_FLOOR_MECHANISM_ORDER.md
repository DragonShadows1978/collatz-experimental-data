# W6N — Floor Mechanism + Convergence (work order, Fable, 2026-07-04)

Executor: Sonnet agent. House rules as W6M (frozen gates; exact
replay for every witness; independent cross-checks; Path C + the
W6M exact-bigint ladder only; ~8GB RSS; honest walls; work under
shell/underlock/w6n/; ledger entries W6N-N1..N4 to
renorm_check/IMPLEMENTATION_LEDGER.md; no commits; CPU only; verify
background processes are alive before waiting on monitors).

Context: DERIVATION_NOTES §13. The floor-point law (M1, 519/519) is
the global lemma's anchor. This round tests its mechanism, extends
its scope, fingerprints the boundary dips, and closes the curve's
length convergence.

## N1 — Floor-point law at full generality

M1 tested chains within L+1. Extend: ALL admissible chains within
L+3, m = 4..7 (exhaustive, Path C), same 442-word scope trimmed as
needed for runtime (state trims honestly). Test g(k*) ≥ g_loop(k*)
per chain. **Frozen prediction (Fable): exceptionless at every
budget — 75%.** Any violation: exact-replay, dump verbatim, lead
with it (it would relocate the induction's anchor).

## N2 — Is the floor forced by the prefix congruence ALONE?

The mechanism check (13a). For each word in a 40-word sample
(mechanical rows + random, m = 5..7): at the loop's k*, enumerate
ALL residue-feasible prefix states (any chain prefix of length k*,
regardless of suffix feasibility — the mod-3^k* congruence/parity
constraints only) and their minimal partial-sum profiles. Question:
does min over prefix-states-reachable-below-the-floor come out
EMPTY (the congruence alone forbids being cheap at k*), or do
cheap-at-k* prefixes exist that only die by SUFFIX infeasibility?
**Frozen prediction: the congruence alone is NOT enough — cheap
prefixes exist at k* and are killed by the suffix (the floor is a
whole-window fact, matching the L4 coupling picture) — 65%.**
Either answer shapes the proof: prefix-alone ⟹ one-point argument;
suffix-needed ⟹ the induction must carry a forward invariant.

## N3 — Dip fingerprinting (the boundary term's positions)

Take M2's undercut positions (dips to f=1) across all cells; extend
the table to every mechanical-family row m ≤ 9 (Path C, within
L+1). For each dip position j: record the word's local structure
(letter at j, distance to nearest support/correction letter, phase
mod q). **Frozen prediction: dips occur exactly at positions
where the word's suffix from j is a maximal-credit run (the chain
can afford one late unit because the remaining letters over-credit)
— 55%.** Deliverable: the dip catalog + the local-structure
cross-tab, whatever the verdict.

## N4 — Length convergence of the tax curve

With the exact-bigint ladder: t = 10..14, lengths 15, 16, 17, 18
(or to the RSS/time wall, cell by cell, stated). Stop per t when
two consecutive lengths agree. **Frozen prediction: t=11/12
stabilize at 19 by len 16; t=13/14 drop below 31/32 and stabilize
by len 17-18 — 55%.** Deliverable: the converged (or
honestly-still-open) curve of record.

## Output

Ledger entries W6N-N1..N4: scripts, tables (w6n/*.csv), exact-replay
confirmations, gate verdicts vs frozen predictions, honest walls.
Final digest: per experiment — verdict, decisive table, HIT/MISS.
N1 violation or N2 "prefix-alone suffices" would each be
lead-with-it findings.
