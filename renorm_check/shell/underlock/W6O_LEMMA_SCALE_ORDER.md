# W6O — One-Point Lemma at Scale (work order, Fable, 2026-07-04)

Executor: Sonnet agent. House rules as W6N (frozen gates; exact
replay; independent cross-checks; Path C + W6N instruments; ~8GB
RSS; honest walls; verify background processes alive before
waiting; work under shell/underlock/w6o/; ledger entries W6O-O1..O3
to renorm_check/IMPLEMENTATION_LEDGER.md; no commits; CPU only).

Context: DERIVATION_NOTES §14. The one-point lemma is the program's
single remaining proof target, currently certified on 40 sampled
words + N1's exhaustive floor. This round scales the lemma's
empirical base to the domain that matters and closes N4's honest
walls where cheap.

## O1 — The lemma exhaustively over the real domain

The lemma's statement depends only on the k*-prefix of the word.
Enumerate the ACTUAL prefixes that arise: (i) every binding prefix
of the true word's windows (canonical, end-anchored) for m = 2..53;
(ii) every binding prefix of both mechanical families m = 2..2q;
(iii) ALL {1,2} words of length ≤ 12 played AS their own k*-prefix
(exhaustive — this subsumes sampling). For each: branch-and-bound
minimum of g(k*) over all parity-legal k*-walks from ρ = 1
(reuse/extend w6n/n2 machinery; cap-margin checks as there).
**Frozen prediction (Fable): min = g_loop(k*) on 100% — 85%.**
Any breach: exact-replay, dump, lead (it would falsify the lemma
BEFORE proof effort is spent — the entire point of this round).

## O2 — Support-adjacency biconditional (N3's law, tested properly)

N3 found 9/9 dips support-adjacent. Test the BICONDITIONAL on a
real sample: all mechanical rows m ≤ 11 both families + true-word
windows m ≤ 11, band L+1: is every dip support-adjacent AND every
support-adjacent position (within the relevant range) a dip?
**Frozen prediction: forward direction survives (dips ⟹
support-adjacent) — 70%; reverse fails (adjacency is necessary,
not sufficient) — 70%.** Deliverable: the 2×2 table + the exact
extra condition that separates dip from non-dip among
support-adjacent positions, if visible.

## O3 — N4 wall closures (cheap cells only)

(i) t=14: shrink [25, 32] — run len 15, 16 with the tight-cap
closure method (bound 25..31); stop at the RSS/time wall, state
cells. (ii) t=10: len 19, 20 at tight caps around 15.
**Frozen prediction: t=14 settles ≥ 25 (the cliff is real, height
≥ 6) — 65%.** If a cell is infeasible under the cap, honest wall —
the curve's open cells are acceptable; fabricated closure is not.

## Output

Ledger entries W6O-O1..O3: scripts, tables (w6o/*.csv), replay
confirmations, verdicts vs frozen predictions, honest walls. Final
digest: per experiment — verdict, decisive number/table, HIT/MISS.
An O1 breach leads over everything.
