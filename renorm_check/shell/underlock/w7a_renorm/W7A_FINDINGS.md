# W7A — Corridor Edge Law Above C=10: Findings

Data used: C=1..26 measured edges (exact integers, as given in the order
file). w7a_new_edges.txt was checked at three points during this analysis
(start, mid, before finalizing) and contained zero rows each time — the
deep_sweep.py gate step (C=16, 23, 26 cross-check) had not yet completed,
so no C=27..40 cells were available. All results below are N=16
increments (C=11..26). Every number that follows is reproducible by exact
integer arithmetic on the given edge table; irrational constants (beta,
sqrt(2), phi) are used only as comparison targets, never inside the
integer pipeline.

## 0. Raw increments d(C) = M(C) - M(C-1), C=11..26

```
C :  11  12  13  14  15  16  17  18  19  20  21  22  23  24  25  26
d :  31   6   5   3   8  14  15   2  20   2   7  18   6  25   4  13
```

## 1. Increment word / threshold selection

Histogram of the 16 increment values (sorted): 2,2,3,4,5,6,6,7,8,13,14,15,18,20,25,31.

There is one dominant gap: between 8 and 13 (gap = 5). This is confirmed,
not just eyeballed: I ran 1D variance-minimizing splits over all 15
possible cut points. The split {2,2,3,4,5,6,6,7,8} | {13,14,15,18,20,25,31}
(i.e. threshold T in (8,13]) gives within-cluster SSE = 295.3, the global
minimum over all splits (next best neighbors: 307.9 and 397.9). The only
other candidate gap of comparable size, 20|25 (gap=5), sits at SSE=494.4 —
markedly worse. **Threshold selected: T=10** (any T in (8,13] gives the
identical word).

Classifying d(C) > 10 as H, else L, C=11..26:

```
word = H L L L L H H L H L L H L H L H     (C=11 -> C=26, left to right)
        11..............................26
H-positions (C-values): 11, 16, 17, 19, 22, 24, 26   (7 of 16)
```

H count = 7, L count = 9, n = 16. **Density(H) = 7/16 = 0.4375.**

Stability check: this is a single N=16 sample; there is no second window to
test stabilization against. Flagged inconclusive — more cells (the pending
C=27..40 sweep) are required to see whether density drifts. Note the word
is short enough that 7/16 is not distinguishable from many nearby
rationals or irrationals (see §2).

## 2. Sturmian / factor-complexity test

Factor complexity p(n), word = HLLLLHHLHLLHLHLH (n=16 symbols, windows
available = 16-k+1):

| k | p(k) measured | Sturmian target (k+1) | windows available |
|---|---|---|---|
| 1 | 2  | 2 | 16 |
| 2 | 4  | 3 | 15 |
| 3 | 7  | 4 | 14 |
| 4 | 11 | 5 | 13 |
| 5 | 12 | 6 | 12 |

**Verdict: NOT Sturmian.** p(2)=4 already exceeds the Sturmian bound of 3
(all four of HH, HL, LH, LL occur), and the gap widens at k=3 (7 vs 4) and
k=4 (11 vs 5) with ample window count (14 and 13 respectively — not a
small-sample artifact at this k). A Sturmian word by definition has
exactly n+1 factors of length n for every n; this word already violates
that at n=2 with 15 windows to sample from, so the violation is
decisive, not noise. The word looks closer to a high-complexity /
near-random binary sequence at this length than to a low-complexity
(Sturmian/Beatty) code word.

## 3. Density constant vs. algebraic candidates

Full-word density 7/16 = 0.4375 trivially equals itself (7/16) with error
0 — not informative, since any finite rational word matches its own
frequency exactly. Testing against the pre-registered candidates:

| candidate | value | \|err\| vs 7/16 |
|---|---|---|
| 1/2.25 (Beatty k from §4) | 0.4444 | 0.0069 |
| 5/12 | 0.4167 | 0.0208 |
| beta = 2-log2(3) | 0.4150 | 0.0225 |
| sqrt(2)-1 | 0.4142 | 0.0233 |
| 1-beta | 0.5850 | 0.147 |
| 1/phi | 0.6180 | 0.181 |

If the C=11 point is treated as a transient of the break itself (see §4 —
it is the sole outlier in the Beatty fit) and dropped, density over the
remaining 15 points is 6/15 = 0.4000, closest to 2/5 (exact) then
sqrt(2)-1 (err 0.0142) then beta (err 0.0150).

**Verdict: inconclusive at this N.** Neither reading is close enough
(errors of 1-2%, on a sample of 16-15 points where one unit is already
1/16 ≈ 6%) to claim an algebraic identification over a nearby rational.
The data cannot currently distinguish beta, sqrt(2)-1, 2/5, or 5/12 as the
"true" density. More cells sharpen this directly: each added H/L roughly
halves the denominator granularity of what's distinguishable.

## 4. Positional law (Beatty fit) for H-positions

H occurs at word-index (1-indexed, C=11 -> index 1) n = 1, 6, 7, 9, 12, 14, 16.

Least-squares/grid search over floor(n*k)+c, k step 0.0001, c integer in
[-5,5], minimizing sum of squared residuals over all 7 points:

- Best fit: **k=2.2, c=1**, SSE=5, residuals [+2, -1, 0, 0, 0, 0, 0].
  The only structural miss is the very first point (word-index 1, C=11) —
  the same point that is the single largest increment (d=31) in the whole
  table and immediately adjacent to the base-law breakdown at C=10->11.

- Dropping that one point (treating C=11 as the break's transient, not
  part of the steady-state pattern) and refitting on the remaining six
  H-positions {6,7,9,12,14,16}: **k=2.25 (=9/4 exactly), c=3**, SSE=1,
  residuals [-1, 0, 0, 0, 0, 0] — five of six exact, one off by 1.

**Verdict: strong Beatty fit (k=9/4=2.25, c=3) for the post-transient
H-positions**, with total squared error 1 across 6 points (i.e. one
single-unit miss). This is far tighter than the Sturmian word-complexity
result in §2 — the H-subsequence positions obey a near-exact Beatty rule
even though the full 2-symbol word is too complex to be Sturmian. Density
implied by k=9/4 is 1/k = 4/9 = 0.444, consistent with the full-word
density 7/16 to within 0.007 (see §3) — this is the best interpretation
of the density question available at this N.

## 5. Growth model M(C): power law vs. C*log(C)

Fit over full range C=1..26 (26 points, includes the exact base-law
regime C<=10 which will bias both fits toward the pre-break slope):

- Power law M ~ a*C^p: p=1.3516, a=2.0493. SSE=7040.1, max|residual|=37.7
  (worst at C=24-26, i.e. errors grow with C — bad fit in the regime that
  matters).
- Log-linear M ~ a*C + b*C*log(C): a=-4.464, b=3.744. SSE=1175.6,
  max|residual|=15.6 — three to six times better SSE than the power law,
  residuals do not show the same runaway growth at large C.

Refit on C=11..26 only (16 points, isolating the post-break regime):

- Power law: p=1.5578, a=1.2603, SSE=340.4.
- Log-linear: a=-4.696, b=3.830, SSE=382.6.

**Verdict: mixed / regime-dependent.** Over the full range the log-linear
(C*log C) model is clearly preferred (SSE ~6x lower, no residual blowup
at high C). Restricted to the post-break regime alone, the two models are
statistically close (SSE 340 vs 383, power law marginally better) — 16
points is not enough to separate a p≈1.55 power law from a C*log(C)
term at this precision, since log(C) is nearly linear in C over
C in [11,26]. **Conclusion: the full-range evidence favors the C*log(C)
super-linear model over a pure power law; the post-break-only evidence is
inconclusive between the two.** More cells (C=27..40) would separate
them decisively since log(C) curvature becomes distinguishable from a
fixed power p only over a wider C-range.

## Summary of numbers backing each claim

- Threshold: T in (8,13], selected by global-minimum split-variance
  295.3 (next-best 307.9).
- Word (C=11..26): HLLLLHHLHLLHLHLH, 7H/9L, density 7/16=0.4375.
- Sturmian verdict: FALSE — p(2)=4 (>3), p(3)=7 (>4), p(4)=11 (>5).
- Density best algebraic read: 4/9 (=1/2.25, from the Beatty k), err
  0.0069 against 7/16; no irrational candidate beats this at current N.
- Beatty fit: k=9/4=2.25, c=3, SSE=1 over 6 post-transient H-positions
  {6,7,9,12,14,16} (transient = C=11, the point adjacent to the base-law
  break).
- Growth model: C*log(C) preferred over full range (SSE 1175.6 vs
  7040.1); inconclusive vs. pure power law (p~1.56) restricted to
  C=11..26 alone (SSE 382.6 vs 340.4).

## Note on extended data

w7a_new_edges.txt was empty at all three checks during this run (the
deep_sweep gate had only completed 2 of 3 pre-checks by the last check,
C=16 OK, C=23 OK, C=26 pending). All conclusions above are therefore
based on N=16 increments and should be treated as provisional,
particularly §1 (density stabilization) and §5 (growth-model
discrimination), both of which explicitly need more C-range to resolve.
