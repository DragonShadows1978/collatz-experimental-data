# W6L — Canonical Consolidation (work order, Fable, 2026-07-04)

Executor: Sonnet agent. House rules as W6K: frozen gates, result is
the result, work under shell/underlock/w6l/, ledger entries
W6L-L1..L4 to renorm_check/IMPLEMENTATION_LEDGER.md, no edits to
SYNTHESIS/DERIVATION_NOTES/orders, no commits, CPU only, ~8GB RSS.
INSTRUMENT RULE (from W6K): all order-sensitive computation goes
through w6k/k0_canonical_engine.py (Path C, hand-gated) or
w6e/e1_walkers.py (Path A, canonical-verified). Path B
(f1_engine_ext/bfs_Dm) is RETIRED for order-sensitive work — you
may use it only where order-immunity is proven, and must say so.

Context: SYNTHESIS W6K section; DERIVATION_NOTES §11. Universality
is total on certified instruments. This round consolidates the
canonical foundation and attacks the two remaining quantitative
gaps (per-trit tax law, J4 residual).

## L1 — Canonical uniqueness re-census (hygiene, closes the Path-B annotation)

Re-run the loop-uniqueness census under Path C, canonical order:
{1,2}^m exhaustive for m ≤ 10, plus the 28 periodic-family rows and
the 11 real-word rows (canonical windows). Deliverable: n_optimal
per row. **Frozen prediction (Fable): loop strictly unique on ALL
of it — 85%.** Any tie or non-loop optimum: dump verbatim, verify
by hand-traceable DFS, lead with it (it would be the first crack in
total rigidity ever seen on certified instruments).

## L2 — Per-trit tax decomposition (P-II's empirical law)

For each t = 1..10, dump ALL argmin excursions (not just one) from
K2's corrected DP: exponent shapes, lengths, and the residue path.
Deliverables: (i) the argmin catalog; (ii) increment analysis — for
each t→t+1 jump, WHAT changed (longer excursion forced? different
shape class? steering cost step?); (iii) test the plateau
hypothesis: plateaus (5,5 at t=3,4; 7,7 at t=5,6) occur because one
shape satisfies two consecutive precisions (mod-9 steering
granularity — one steering choice fixes two trits). **Frozen
predictions: (a) plateau shapes are literally identical chains
serving both t values — 70%; (b) every jump t→t+1 coincides with
minimum excursion LENGTH increasing — 55%; (c) extrapolation: the
t=11..14 curve (extend the DP if RSS allows; honest wall otherwise)
continues at ~2.5-3/trit with width-≤2 plateaus — 60%.**

## L3 — J4 residual structure (the third-structure hunt)

Take J4's 73.4% mismatch dump (w6j/), all order-immune inputs.
Classify residual anchors: cluster by (r mod 9, r mod 27, distance
patterns to BOTH rays, over/under-prediction sign and magnitude).
The model overpredicted 95.7% — something makes real chains CHEAPER
than ray-descent + ray-riding. Hypothesis menu to test mechanically
(pick cheapest-first): (i) mixed itineraries (ride +1 ray, hop to
−1 ray mid-window when a credit run makes the hop free); (ii)
entry-segment credits (the window's actual letters during descent
are cheaper than ray-rate — J4's own root-cause note); (iii) a
genuine third invariant ray/cycle shadow at higher modulus (search:
fixed points of two-step maps a=(1,3),(3,1),(2,2) etc. mod 27/81).
**Frozen prediction: (ii) + (i) explain ≥ 90% of residuals; no
third ray exists — 65%.** Finding a third invariant structure
would be bigger than fixing the model — check (iii) honestly, not
perfunctorily.

## L4 — Excursion-tax composability (the lemma's assembly step)

Idea #5 from the registered ideation list, now on certified
instruments: embed 2-3 known excursion shapes (from L2's catalog)
at disjoint positions into length-14..16 canonical windows over
{1,2} words; measure whether total max-partial-sum penalty = sum of
individual taxes (within the boundary-term ±1). **Frozen
prediction: exact additivity for gap ≥ 2 separations — 70%;
interference (super- or sub-additive) at gap ≤ 1 — 55%.**
Additivity is what lets P-II compose into the global lower bound.

## Output

Ledger entries W6L-L1..L4: scripts, tables (w6l/*.csv), gate
verdicts vs frozen predictions, honest walls. Final digest: per
experiment — verdict, decisive table, HIT/MISS. If L1 finds a
crack or L3 finds a third structure, that leads.
