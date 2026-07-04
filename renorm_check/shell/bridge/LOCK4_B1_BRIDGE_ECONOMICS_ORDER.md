# LOCK4-B1 — Bridge Economics, Measured Exactly (work order, Fable, 2026-07-04)

Executor: Sonnet agent. House rules as the W6 series (frozen gates;
exact replay of every witness; independent cross-checks; canonical
instruments only — w6k/k0_canonical_engine.py conventions and
w6e/e1_walkers.py credit_true; ~8GB RSS; honest walls; verify
background processes alive; work under shell/bridge/b1/; ledger
entries LOCK4-B1.1..B1.4 to renorm_check/IMPLEMENTATION_LEDGER.md;
no commits; CPU only).

Read first: shell/bridge/LOCK4_BRIDGE_NOTES.md (the definitions —
binding), COLLATZ_PROOF.md §5.3 + Theorem 5 Part 1, the red-team
problem list §7 (Lock 4), DERIVATION_NOTES §14 (the one-point
machinery you are mirroring).

## B1.1 — Phase-relaxed climb cap (residue-free upper bound)

For the true word (canonical, exact credits): compute the exact
phase-relaxed max climb over every k-window, k = 1..700 (supports
force a ≥ 2, drops allow a = 1, NO residue tracking): the closed
form should be Σc − k − supports(k); verify against direct DP on
20 windows. Deliverable: the curve, its value at k = 306, and the
law it obeys (test convergent-quantized ⌊·⌋ forms).
**Frozen (Fable): value at k=306 is ≈ 52 and < 149 — 70%; the
curve obeys a floor-form law in k — 60%.**

## B1.2 — Residue-legal max climb (the real usable reserve)

The mirror DP: over the 306-letter first-bridge window (and k = 53,
100, 200 controls), compute max Σ(c − a) over ALL residue-legal
exponent sequences, from every launch class mod 27 (and mod 81 if
cheap), tracking residues exactly (shrinking-modulus ladder if
needed; the W6L/W6N instruments' discipline). Deliverable: max
climb per launch class; the worst (best-for-the-orbit) launch.
**Frozen: residue-legal max climb ≤ phase-relaxed cap (required —
sanity), and the gap between them is ≥ 20% of the cap (residues
bite hard on ascent, as they do on descent) — 60%.**

## B1.3 — The first-bridge inequality, assembled

Combine: worst-launch usable reserve (B1.2) + maximum launch
reserve available at the q = 53 scale (justify the bound you use
from the capacity law — state it explicitly) vs the required
support at arrival (~149; derive the exact number from
M_edge/F5-territory arithmetic and SHOW the derivation).
**Frozen: the inequality HOLDS with slack ≥ 30 — 65%.** If it
fails or is tight (< 10 slack), that is the lead finding — the
bridge argument would need the crash tax to close, which B1.4
measures.

## B1.4 — Crash tax (exploratory, gated lightly)

After a maximal climb segment (take B1.2's argmax witnesses),
measure the forced net descent over the following 20-50 letters
(support forcing + battered residue class). Deliverable: crash-tax
table per witness. **Frozen: crash tax > 0 for every maximal-climb
witness (no soft landings) — 70%.**

## Output

Ledger entries LOCK4-B1.1..B1.4: scripts, tables (b1/*.csv), exact
replays, verdicts vs frozen predictions, honest walls. Final
digest: the assembled first-bridge inequality with every term's
provenance, per-experiment HIT/MISS. A B1.3 failure leads.
