# W6J — Interior/Boundary Decomposition (work order, Fable, 2026-07-04)

Executor: Sonnet agent. House rules as W6E..W6I: frozen gates,
result is the result, no edits to SYNTHESIS/DERIVATION_NOTES/orders,
no commits, CPU only, work under shell/underlock/w6j/, ledger
entries appended directly to renorm_check/IMPLEMENTATION_LEDGER.md
(entries W6J-J1..J4; no other agent is running — you own the ledger).
Kill any process past ~8GB RSS; report walls honestly. Reuse
validated machinery (w6e/, w6f/, w6g/, w6h/); validate extensions on
3 known rows first.

Context: DERIVATION_NOTES §8-§10. The lemma's proof now decomposes
into INTERIOR rigidity (exact-return excursions cost ≥ 27 at high
precision) and BOUNDARY arithmetic (window-end deviations cost the
measured +1). This round quantifies the decomposition and tests the
architect's two post-data mechanisms.

## J1 — Ceiling-mechanism check (universality's boundary)

Architect conjecture (registered, DERIVATION_NOTES §10b): on any
alphabet, D(w) = L(w) ⟺ the loop's running sum never dips below 0
(min_k g_loop(k) ≥ 0, where g_loop(k) = Σ_{j≤k}(2 − c_j)).
Test on the FULL W6H-H3 census output (w6h/h3_wordspace_census.csv
+ breaks dump): for every word in all three alphabets, compute
min_k g_loop(k) and cross-tabulate against break/no-break.
**Frozen prediction: the biconditional holds exactly — every break
row has min_k g_loop < 0, every non-break row has min_k g_loop ≥ 0
— 80%.** Any counterexample in either direction: dump verbatim,
classify, lead with it.

## J2 — Return-precision cost curve (the lemma's quantitative core)

Extend H1's layered DP: min cost over returning excursions of
length ≤ 10, where "return" = ρ ≡ 1 (mod 3^t), for each precision
t = 1..10 separately. Deliverable: the (t, min_cost, argmin shape,
min length achieving it) table — the curve that interpolates
between F2's +1 (low effective precision) and H1's 27 (high).
**Frozen predictions: (a) min_cost is nondecreasing in t — 85%;
(b) min_cost at t = 1 is exactly +1 — 70%; (c) the curve is
convex-ish/superlinear in t (rigidity compounds) — 55%.**
The shape of this curve dictates how the interior-rigidity
induction must scale its per-trit tax.

## J3 — Order-gap uniqueness census (the keystone's sharpest tooth)

For m = 4..8: verify ord(2, 3^m) = 2·3^{m−1} directly. Then for the
S-value of every admissible chain enumerated in W6F-F2's D+2 scope
(recompute S = Σ 3^{m−1−i} 2^{A_i} per chain), brute the full
solution set {σ ∈ [0, 6m] : 2^σ ≡ S (mod 3^m)}.
**Frozen predictions: (a) each S admits AT MOST ONE σ in [0, 6m]
(the order gap dwarfs the window) — 85%; (b) that σ equals the
chain's actual Σa in every case (consistency; a mismatch = engine
bug, stop and report) — required; (c) tabulate Σa − 2m vs the
chain's tax: architect expects a clean monotone relation (more
excess exponent ⟺ more tax) — 60%.** Deliverable: the pinning
table — this is the empirical backbone of the interior-rigidity
induction.

## J4 — Two-ray model repair

Add the missing term to H2's model: D(r, m) = min over rays
ρ* ∈ {+1, −1} of [entry_cost(r → ρ*-ray, measured per-anchor by
shortest-path DP) + ray discrepancy over remaining letters], where
entry_cost is computed EXACTLY (small DP over ≤ 6 steps, residues
mod 3^8) rather than assumed. Re-fit against the full W6G-G2 sweep
+ H2 data. **Frozen prediction: repaired model ≥ 90% of anchor keys
exact — 60%.** Residual keys: dump and classify (third structure
beyond the two rays would be a discovery, not a failure).

## Output

Ledger entries W6J-J1..J4: scripts, tables (w6j/*.csv), gate
verdicts vs every frozen number, honest walls. Final digest: per
experiment — verdict, decisive table/number, predictions HIT/MISS.
