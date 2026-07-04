# W6H — The Lemma's Local Core (work order, Fable, 2026-07-04)

Executor: Sonnet agent. House rules as W6E/F/G: frozen gates, result
is the result, ledger-only writes (entries W6H-H1..H5), no edits to
SYNTHESIS/DERIVATION_NOTES/orders, no commits, CPU only,
minutes-scale, work under shell/underlock/w6h/. Reuse validated
machinery (w6e/engine.py, w6f/f1_engine_ext.py, w6g extensions);
validate new code on 3 known rows first.

Context: DERIVATION_NOTES §8. The single remaining lemma: from
anchor ρ_end = 1, the all-2s loop is strictly optimal — every
excursion pays exit ≥ +2 and refunds ≤ +1 net. W6H attacks the
lemma's LOCAL structure and closes W6G's loose threads.

## H1 — Excursion cost spectrum (the lemma's engine room)

Define an excursion: a backward-chain segment that leaves the ρ≡1
ray (first step with a ≠ 2 from a ρ≡1 position) and first returns
to a ρ≡1 position (mod the working precision), or never returns
within length ℓ. Exhaustively enumerate ALL excursion shapes up to
length ℓ ≤ 8 (exponent sequences, residues tracked exactly mod
3^{ℓ+2}): for each, tabulate COST = Σ(a_j − 2) over the excursion
(word-independent!) and whether it returns.

**Registered predictions (Fable):**
- Every returning excursion has COST ≥ +1 (this IS the lemma's local
  form; word-independent because credits cancel in Σ(a−2) framing) —
  75%.
- The minimum COST = +1 exactly, achieved by some shortest returning
  shape; identify it — 65%.
- Non-returning prefixes all have running cost ≥ 0 (you can't even
  temporarily profit while off-ray) — 55% (a dip here would show
  where a lower-bound induction must be careful).
If ANY returning excursion has COST ≤ 0: that is a BREAK of the
lemma — the loop's optimality would then depend on word structure
after all. Dump it verbatim, triple-check it, lead with it.

## H2 — Two-ray decomposition of the anchor sweep

G2 found h(r) < 0 anchors; mechanism hypothesis: the cheap ρ≡−1 ray
(a=1, cost 1/step). Model: D(r, m) = min over rays ρ* ∈ {+1, −1} of
[descent(r → ρ*-ray) + ray-discrepancy(m − descent-length)], where
the −1-ray discrepancy uses Σ(1 − c_j). Fit/validate against the
FULL G2 sweep data (w6g/ anchor tables) and extend the sweep where
needed (mod 81, m to 10).
**Registered prediction: the two-ray model reproduces D(r, m)
exactly for ≥ 90% of anchor keys once descent costs are measured
per-anchor — 55%** (genuinely uncertain; the residual keys' pattern
is the deliverable either way). Also: D(r = 3^m − 1 anchor) = 0
for every word with min letter ≥ 1 (the pure cheap ray) — 80%.

## H3 — Alphabet extension (universality's scope fence)

G1 proved universality on {1,2}^m. Extend: exhaustive word-space
over alphabets {0,1,2}, {1,2,3}, {0,1,2,3} at m ≤ 7 (3^7 = 2187,
4^7 = 16384 words — census each; drop the biggest set honestly if
slow). Note c=0 letters change the kill structure (menu [1, δ]
empty at δ=0 regardless of parity) — the loop remains feasible at
budget L by the conservation identity, but optimality is the
question.
**Registered prediction: D(w) = L(w) = max_k Σ(2 − c_j) and loop
unique for ALL words over ALL tested alphabets — 65%.** Exceptions,
if any: dump verbatim and classify (expect them, if anywhere, at
words with c=0 letters adjacent to high-credit letters).

## H4 — P1b by data-mining (replace the muddled G3 guess)

With universality, every family's ±1 constant is a discrepancy
boundary term. Compute L for the mechanical words of MANY convergents
(all convergents p/q with q ≤ 60 of: log₂3's α, √2's, √3's, golden's,
plus 10 random irrationals' convergent lists), both sides, across
m = 2..4q, under end-anchored windows at every phase offset
0..q−1. Extract the exact empirical rule:
constant(side, phase) = ? (the ⌊(pm+1)/q⌋ vs ⌊(pm−1)/q⌋ selector).
**Registered prediction: the rule is a clean two-case function of
(side, window-end phase mod q), no other dependence — 70%.**

## H5 — Frame rule cross-check (F5's last caveat)

The F5 computation's run-length rule (run = 53·⌈(m+1)/53⌉, window
end ≡ 52 mod 53) is validated at C ≤ 5 and C = 148. Search the repo
for archived corridor step counts at middle C (shell probes, W2
outputs, certs, lock3 outputs — look for (C, steps) pairs). Verify
the rule at every found C. **Registered prediction: holds at all
found C — 70%.** If no archived mid-C step counts exist, SKIP
honestly and say what would be needed to generate one cheaply.

## Output

Ledger entries W6H-H1..H5: scripts, tables (w6h/*.csv), gate
verdicts vs every frozen number, honest walls. Final digest: per
experiment — LEMMA SUPPORTED / BREAK / SKIPPED, decisive
number/table, prediction HIT/MISS.
