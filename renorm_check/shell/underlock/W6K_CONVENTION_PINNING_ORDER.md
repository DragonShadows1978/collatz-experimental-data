# W6K — Convention Pinning + Redos (work order, Fable, 2026-07-04)

Executor: Sonnet agent. House rules as prior rounds: frozen gates,
result is the result, work under shell/underlock/w6k/, ledger
entries W6K-K1..K3 appended to renorm_check/IMPLEMENTATION_LEDGER.md
(you own the ledger), no edits to SYNTHESIS/DERIVATION_NOTES/orders,
no commits, CPU only, ~8GB RSS discipline.

Context: SYNTHESIS "W6J + architect audit" section. A direction/
convention seam invalidated the W6H-H3 alphabet-break results and
W6J-J1/J2. This round pins conventions and redoes the invalidated
work. THE CANONICAL ORDER (architect ruling, binding): letters are
consumed in BACKWARD-consumption order — index 0 = the letter
nearest the terminal — exactly e1_walkers.backward_letters
semantics, which is what §2's game defines and what E1 validated
11/11 against real ground truth.

## K0 — Asymmetric validation rows (do this FIRST, gate everything on it)

Build the missing validation class: hand-compute (on paper, in the
ledger entry, showing work) D and L for 6 asymmetric words over
{1,2,3} at m = 2,3 under the canonical order AND its reverse —
words chosen so the two orders give DIFFERENT answers (e.g. "13",
"31", "113", "311", "123", "321"). Hand-derivation must state, per
word: legal menus at each step, kill points, the feasible budget.
THEN run every engine path that will be used in K1/K2
(e1-walker functional, f1 enumerator via compute_D_and_optimal_set,
any new code) against these 12 (word, order) cases. Every path must
agree with the hand table under the canonical order. Any
disagreement: STOP, report which engine path deviates and where —
that diagnosis outranks the redos.

ALSO pin the ceiling question explicitly: does the game permit
negative running sums (walker above start depth)? Hand-derive both
variants for the 6 words (ceiling-on: g(k) ≥ 0 required;
ceiling-off: unbounded above). Report both columns; the architect
decides which matches corridor semantics after seeing the table —
DO NOT silently choose one.

## K1 — Alphabet-extension redo (replaces W6H-H3's {1,2,3} results)

Re-run the exhaustive word-space census on {1,2,3}^m and
{0,1,2,3}^m (m ≤ 7, drop the 4-letter set honestly if slow) under
the canonical order, with BOTH ceiling variants as separate columns
(D_ceil, D_free), and L computed over the SAME canonical order.
Deliverables: break counts per (alphabet, ceiling-variant);
break dumps; and the cross-tab against min_k g_loop(k) < 0 (the
architect's ceiling conjecture, retried on trustworthy data).
**Frozen predictions (Fable, re-registered on clean instruments):
(a) under ceiling-ON, D_ceil = max(L, 0) fails somewhere — 50%
(genuinely uncertain now); (b) under ceiling-OFF, D_free = L
everywhere on ALL alphabets (universality is order-artifact-free
and total once the direction is consistent) — 45%; (c) the ceiling
conjecture biconditional (breaks ⟺ min g_loop < 0) holds under
exactly one of the two variants — 60%.**

## K2 — Return-precision cost curve redo (replaces W6J-J2)

One DP per t as before, but with the nesting law enforced as an
assertion: a chain counted as returning at precision t+1 MUST also
be counted at t (1 mod 3^{t+1} ⟹ 1 mod 3^t); therefore
min_cost(t) must be nondecreasing — assert it inside the run, and
if the assertion fires, the bug is in that t's DP: find it, fix it,
document it. Deliverable: the corrected (t, min_cost, argmin shape)
curve, t = 1..10, length ≤ 10, cross-checked against H1's t=10
value (27) and F2's t≈1 value (+1).
**Frozen predictions: (a) corrected curve is nondecreasing —
REQUIRED (assertion); (b) t=1 value = 1 — 80%; (c) the curve's
big jumps align with t crossing excursion-length thresholds
(cost jumps when longer excursions become mandatory) — 55%.**

## K3 — J1 biconditional retest

Re-run the ceiling-mechanism cross-tab (J1) against K1's clean
census (both ceiling variants). Report per-variant verdicts vs the
architect's conjecture. No new prediction — K1(c) covers it.

## Output

Ledger entries W6K-K0..K3 (K0's hand table verbatim in the ledger).
Final digest: K0 pass/fail per engine path; per experiment —
verdict, decisive table, predictions HIT/MISS, honest walls.
