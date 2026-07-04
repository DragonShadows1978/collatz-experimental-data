# W6G — Break-It Round (work order, Fable, 2026-07-04)

Executor: Sonnet agent. House rules as W6E/W6F: frozen gates, result
is the result, ledger-only writes (entries W6G-G1..G5), no edits to
SYNTHESIS/DERIVATION_NOTES/orders, no commits, CPU only, minutes-scale
per experiment, work under shell/underlock/w6g/. REUSE w6f/w6e code
(engine.py, f1_engine_ext.py); validate any extension on 3 known rows
first.

Method note (Architect, explicit): the conjectures below are
GENERATED FREELY — some will be wrong; that is the design. Each dies
or survives on the gate. Do not soften a kill.

## G1 — EXHAUSTIVE word-space attack (the universality test)

For EVERY word w ∈ {1,2}^m, m = 2..10 (2^m words per m; reuse the
W6F census machinery per word): compute D(w) by exhaustive census
and compare to the loop discrepancy L(w) = max_k Σ_{j≤k}(2 − c_j).
Also record n_optimal(w) and min-tax where cheap.

**Registered conjecture (UNIVERSAL DISCREPANCY): D(w) = L(w) for ALL
words — the game has no content beyond word discrepancy; every
family law is just classical discrepancy of its word.** Fable: 70%.
Uniqueness for all words: 55% (degenerate words may create ties).
Pattern-mine the exceptions: if D < L anywhere (loop beaten!) that is
a STRUCTURAL BREAK — dump every such word verbatim. If ties appear,
tabulate which word shapes produce them. Bonus mine: which (w, m)
rows have min-tax ≥ 2 (the sqrt2-m8 class) — is there a word-local
signature (e.g. flat runs at the landing zone)? Fable: signature
exists, 60%.

## G2 — Anchor sweep (is the loop's throne anchored to ρ=1?)

All experiments so far anchor the terminal at ρ_end = 1. Sweep the
terminal anchor over all admissible residues mod 27 and mod 81
(classes 1 and 2 only; class 0 has no backward step), small m
(2..8), golden + sqrt2 words: D(r, m) by census.

**Registered conjecture: D(r, m) = L(m) + h(r) where h(r) ≥ 0 is an
m-independent "descent cost to the 1-ray" (stabilizes once m exceeds
a small threshold).** Fable: 60%. Deliverable: the h(r) table if it
exists; the breakage pattern if it does not.

## G3 — Over-side convergent families (the side-constant law)

W6F-F3 concluded the −1 form must come from the convergent SIDE.
Test it: build periodic credit words from OVER-side convergents of
2-3 irrationals (choose convergents p'/q' with p'/q' > the target α
where the measured families used under-side; construct the
mechanical word per the W6D spec with the over-side convergent) and
measure the D law across m = 2..12.

**Registered prediction: over-side families obey the −1 mirror form
⌊(pm−1)/q⌋-analogue; under-side obey +1 (already measured).**
Fable: 65%. A clean split = P1b's constant DERIVED empirically; a
muddle = 7c's mechanism is wrong, report loudly.

## G4 — True-word round: uniqueness + bonus schedule

(i) Optimal-set census on the REAL system's credit word windows
(end-anchored, the real frame; reuse e2's convention), m = 2..12:
is the loop still strictly unique on the aperiodic word? Fable:
holds, 75% (rigidity priced in; a break would likely sit near
correction letters and would be F5-relevant gold).
(ii) Bonus schedule: D_true(m) vs both ±1 forms for every m in
scope; tabulate bonus-on rows; test alignment against the word's
correction-letter positions / Ostrowski markers. Fable: aligned,
60%.

## G5 — Reality bridge (game vs the actual corridor)

The game says the optimal survivor rides the 1-ray (residues ≡ 1
mod 3^k, the backward 4-2-1 shadow). Check the ORIGINAL corridor
data: do the measured M_edge witnesses / deepest corridor survivors
(from the shell probes' archived outputs, if witness residues were
archived — check shell/ and certs/; if not archived, regenerate only
what is cheap, else SKIP honestly) actually sit ≡ 1 mod 3^k at
depth? **Registered prediction: yes — the abstract game's extremal
object is the real corridor's extremal object.** Fable: 65%.
A mismatch here would mean the game abstraction and the corridor
disagree about the extremal structure — the most important possible
break in this whole program. Do not paper over a mismatch.

## Output

Ledger entries W6G-G1..G5: scripts, tables (w6g/*.csv), gate
verdicts vs every frozen number above, honest walls. Final digest:
per experiment — verdict, the one decisive table/number, break
found or rigidity extended.
