# W6M — Global-Lemma Empirical Map (work order, Fable, 2026-07-04)

Executor: Sonnet agent. House rules as W6K/W6L: frozen gates, result
is the result, work under shell/underlock/w6m/, ledger entries
W6M-M1..M3 to renorm_check/IMPLEMENTATION_LEDGER.md, no edits to
SYNTHESIS/DERIVATION_NOTES/orders, no commits, CPU only, ~8GB RSS.
INSTRUMENT RULE: Path C (w6k/k0_canonical_engine.py) and the W6L
exact ladder DP (w6l/l2_*) only, for anything order- or
representative-sensitive. Every reported witness must pass
exact-integer replay (the W6L lesson: representatives fabricate;
cross-checks must be INDEPENDENT of the artifact they check).

Context: DERIVATION_NOTES §12 — the proof obligation is now ONE
global lemma: for every word w, every admissible chain from
ρ_end = 1 has max_k Σ(a_j − c_j) ≥ L(w), equality iff the loop.
This round builds the empirical maps the global argument will be
written against.

## M1 — Where the +1 bites (the strictness map)

For m = 4..8, words: the mechanical-family rows + 200 random {1,2}
words per m (canonical order): enumerate ALL chains with max
partial sum ≤ L(w) + 1 (Path C). For each non-loop chain: record
(i) the prefix k where its max is attained vs the loop's argmax
k* = argmax g_loop; (ii) its residue class mod 3, 9, 27 at k*;
(iii) g(k*) − g_loop(k*).
**Frozen predictions (Fable): (a) every non-loop chain's max is
attained at a prefix where its residue has left the 1-ray at the
relevant precision — 65%; (b) g(k*) ≥ g_loop(k*) for all non-loop
chains (the loop's binding prefix is a universal floor point) —
55% (genuinely unsure; a violation would locate exactly where the
global argument must NOT anchor).**

## M2 — Congruence-class cost floors (the lemma's empirical form)

For m = 5..8, the mechanical-family words: for every admissible
chain within L + 2 (Path C), compute its per-prefix residue classes
r_k mod 3^min(k, 6). Group chains by the class trajectory truncated
at depth 3 (r_k mod 27 for each k). Per group: min max-partial-sum.
**Frozen prediction: the cost floor is determined by the FIRST
prefix at which the trajectory leaves the 1-ray class — a clean
"departure time → floor" law: floor(departure at prefix j) =
L + f(j) with f ≥ 1 nonincreasing in j (leaving late is cheaper —
the window-end boundary effect seen from inside) — 60%.**
Deliverable either way: the (departure prefix → min cost) table —
this IS the shape of the global induction.

## M3 — Ladder walls extension (close L2's honest gaps)

Extend the W6L exact ladder: t = 13, 14 at len ≤ 14 if the int64/
RSS budget allows (the T0 ≤ 24 bound and ~8GB cap rule); and
length-stability probe at t = 10..12 (len 15, 16 — does the curve
drop further?). **Frozen prediction: curve values stable at len
15-16 for t ≤ 12 — 60%.** Honest walls welcome; state exactly
which (t, len) cells ran.

## Output

Ledger entries W6M-M1..M3: scripts, tables (w6m/*.csv), gate
verdicts vs frozen predictions, exact-replay confirmation for every
cited witness, honest walls. Final digest: per experiment —
verdict, decisive table, HIT/MISS.
