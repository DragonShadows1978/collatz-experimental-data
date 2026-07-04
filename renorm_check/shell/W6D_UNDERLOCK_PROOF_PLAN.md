# W6D — Analytic Under-Lock Proof Plan (registered 2026-07-03, Fable)

**Goal:** prove the occupancy rule measured in W6B/W6C — a Sturmian-driven
corridor's capacity law is the finest under-side rational certificate its
readable window affords — as a theorem, first for toy words, then for
22/53 → 127/306 on the real word. This is the analytic route to F5 (no
m=359 computation) and the template for the published framework's
capacity lemma (its central gap).

**Status: ATTACK PLAN — proof obligations registered, none discharged.**

## Proof obligations

**P1 — Periodic-word exact law (finite algebra).** For the automaton
driven by the EXACTLY p/q-periodic word (q-letter block, p supports),
derive D_per(m) in closed form via the q-step return map. The block
composition is a finite object (golden: 8 letters, 3 supports; the real
analogue: the 53-block with 22 supports — the published heartbeat
lemmas' home). Strategy: the q-step return map on (deficit, residue mod
3^j) is an explicit affine-ish correspondence; the shell's per-period
descent should fall out as exactly p levels per q letters plus a
boundary constant. Expected result: D_per(m) = ⌈(p/q)·m⌉ + c_word with
c_word computable from the block. Validation: must reproduce the
measured golden-periodic and √2-periodic dense tables exactly (cheap
dense runs with tiled words — NOT yet run; run them first as ground
truth; note the true-vs-periodic comparison is only meaningful past the
agreement window, cf. P3 caveat).

**P2 — Balance lemma (imported, known).** Sturmian words are 1-balanced:
every length-ℓ factor has support count ⌊ℓβ⌋ or ⌈ℓβ⌉. No work — cite.
This is what makes "the window's guaranteed support count" = ⌊ℓβ⌋, the
under-count, and is the origin of one-sidedness.

**P3 — Word-monotonicity lemma (THE new mathematical content).** Needed:
if two driving words agree except one position where word A has a
support (c=1) and word B a drop (c=2), then the terminal-liveness depth
D under A vs B differs by a bounded, sign-controlled amount. Evidence:
W6C Design A2 measured D varying by exactly ±1 with window support
count (r≈0.4 correlation, no drift). DANGER: this is NOT obviously
monotone — a support-vs-drop letter changes exponent windows at one
step, which changes the live set non-locally. Candidate techniques:
(a) coupling/injection between the two automata's backward chains;
(b) the F6 steering algebra — quantify how one credit letter alters
the forced region near the ceiling; (c) restrict the claim to what's
actually needed: worst-case-factor lower bound (D ≥ the value driven
by the minimal-support factor), which is one-sided and may dodge full
monotonicity. If (c) suffices, P3 shrinks to a comparison against the
extremal factor only.

**P4 — Assembly + the semiconvergent check.** P1 (exact law per rational
certificate) + P2 (window guarantees the under-count) + P3 (D controlled
by window support count) ⟹ D_true(m) = the law of the best rational
LOWER bound of β with denominator ≤ window(m). CARE: best one-sided
approximations are in general SEMICONVERGENTS, not only convergents.
Checked for the F5 stakes (2026-07-03, exact arithmetic to recheck in
execution): between 22/53 (over) and 127/306 (under), the under-side
semiconvergent chain marches toward 127/306; the best under-bound with
den ≤ 359 is 127/306 itself (the mediant 149/359 = 0.4150417… sits
ABOVE β = 0.4150375…, hence over-side, hence unavailable) — so the
semiconvergent refinement does NOT change the F5 implication:
window(359) ⟹ operative law 127/306 ⟹ D(359)=148 ⟹ edge 359.
It DOES change intermediate-scale predictions for words with partial
quotients > 1 (√2: 24/41 operative at windows 41..69 — dense-walled,
noted as untestable).

## Order of battle

1. Dense ground truth for P1: golden-8-periodic and √2-12-periodic
   tiled-word D tables, m=2..13 (hours, Sonnet-shaped, same pipeline as
   W6C — a small work order when a slot opens).
2. P1 derivation against that ground truth (Fable, paper-and-pencil on
   the 8-block; the 8-block has 3 supports / 5 drops — small enough to
   enumerate the return map's deficit action exactly).
3. P3 attempt via route (c) worst-case-factor first — it is the weakest
   claim that still assembles, and A2's data says the dependence on the
   window is tame (±1).
4. P4 assembly; then port the P1 algebra to the 53-block (the published
   heartbeat lemmas already contain the drop-phase/support-phase exact
   identities — they are the 53-block return-map algebra in embryo).

## Honest stakes

If P1–P4 discharge: the capacity law of the real system is THEOREM-level
"finest under-certificate of the window," F5 resolves analytically to
359 via 127/306 at window ≥ 306, the published formula's caveat becomes
a precise statement (22/53 exact for windows < 306), and the framework's
capacity lemma moves from empirical to proven on its rational core. If
P3 fails (word-monotonicity is false in general), the occupancy rule is
an empirical regularity with an unknown mechanism — report that too;
the W6C data stands either way.
