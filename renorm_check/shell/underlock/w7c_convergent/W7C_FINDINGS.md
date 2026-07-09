# W7C — Convergent-Scheme Test: Spectral Exponent vs Edge-Jump Rate

Executor: cold agent, no prior narrative. All numbers below are computed in
this session with `fractions.Fraction` (exact rationals) and `mpmath`
(mp.dps=50) for irrational CF expansions. Scripts left in this directory:
`w7c_analysis.py` (task 1), `w7c_task2_b_v2.py` + `w7c_task2_exponent6.py`
(task 2; `w7c_task2_b.py` is a superseded first pass that used the wrong
curve — see note below), `w7c_task3_94.py` (task 3), `w7c_task4_jumprate.py`
+ `w7c_task4b_recheck.py` (task 4), `w7c_verdict.py` (residual summary).

No new edges beyond C=28 were present in `w7a_new_edges.txt` at start or at
finalization; it contains only C=27→208, C=28→263, both already in the order
file. No C≥29 data was available this session.

## 1. CF spine table

CF of log2(3) (a0..a8): `[1,1,1,2,2,3,1,5,2,...]`. beta=2−log2(3), 1/beta, and
log2(3)−1 all share the **same partial-quotient tail** (they are integer/
reciprocal transforms of log2(3)), so their convergents are trivially related.

| k | log2(3) p/q | beta p/q | 1/beta p/q | log2(3)−1 p/q |
|---|---|---|---|---|
| 0 | 1/1 | 0/1 | 2/1 | 0/1 |
| 1 | 2/1 | 1/2 | 5/2 | 1/1 |
| 2 | 3/2 | 2/5 | 12/5 | 1/2 |
| 3 | 8/5 | 5/12 | 41/17 | 3/5 |
| 4 | **19/12** | **17/41** | **53/22** | 7/12 |
| 5 | 65/41 | **22/53** | 306/127 | 24/41 |
| 6 | **84/53** | 127/306 | 665/276 | **31/53** |
| 7 | **485/306** | **276/665** | 15601/6475 | **179/306** |
| 8 | 1054/**665** | 6475/15601 | 31867/13226 | 389/**665** |

Exact hits for the target set {53,84,22,306,665}:

- **53**: q of log2(3) k=6 (84/53); q of beta k=5 (22/53); p of 1/beta k=4 (53/22); q of log2(3)−1 k=6 (31/53)
- **84**: p of log2(3) k=6
- **22**: p of beta k=5; q of 1/beta k=4
- **306**: q of log2(3) k=7; q of beta k=6; p of 1/beta k=5; q of log2(3)−1 k=7
- **665**: q of log2(3) k=8; q of beta k=7; p of 1/beta k=6; q of log2(3)−1 k=8

All exact (residual 0) — these are definitionally the same CF tail viewed
through four linear transforms of log2(3), not four independent numbers.

## 2. Exponent 6 — re-derived b and best (convergent, exponent) fit

**Correction caught mid-task**: the published b=0.063099 fit is explicitly
from the **C=10 "universal" curve**, regressed over **m=7..12** (proof text,
`COLLATZ_PROOF.md:499-505`) — NOT the C=3 "locked" curve. My first pass
(`w7c_task2_b.py`) mistakenly used the C=3 table, whose gap *saturates* to a
constant (0.039353, m≥9) rather than decaying to zero — not a b^m regime at
all, and unusable for this fit. Redone correctly on C=10, m=7..12 from
`SPECTRAL_RADIUS_RESULTS.txt`:

- Regression: `ln(gap) = -2.76305*m + intercept` → **b_fit = 0.0630991**
- vs. published 0.063099: relative error **1.3×10⁻⁶** (rounding-limited by
  the 2-sig-fig table; this is an exact reproduction within data precision).
- R² = 0.9986 on 6 points (residuals visibly correlated/oscillating, not
  pure noise — consistent with a second small eigenvalue mode still present).
- Consecutive-ratio check gap(m+1)/gap(m) is **still drifting** at m=11→12
  (0.0522, 0.0500) — the m=7..12 window has not fully settled to a single b;
  the regression is a best-fit over a still-converging tail, not a plateau.

**Convergent/exponent scan**, (q/p)^k for k=1..10 over all log2(3) convergents:

| convergent (p,q) | best k | (q/p)^k | err vs regression | err vs published |
|---|---|---|---|---|
| **84/53 (k_idx=6)** | **6** | **0.0630928** | **9.9×10⁻⁵ (0.0099%)** | **9.9×10⁻⁵** |
| 1054/665 (k_idx=8) | 6 | 0.0630792 | 3.15×10⁻⁴ | 3.14×10⁻⁴ |
| 485/306 (k_idx=7) | 6 | 0.0630780 | 3.34×10⁻⁴ | 3.32×10⁻⁴ |
| 65/41 (k_idx=5) | 6 | 0.0629830 | 1.84×10⁻³ | 1.84×10⁻³ |
| 19/12 (k_idx=4) | 6 | 0.0634696 | 5.87×10⁻³ | 5.87×10⁻³ |

**84/53 at k=6 is the best fit by ~30× over its nearest rivals.**

**Is 6 special or coincidental?** Computed the *continuous* best-fit exponent
k\* = ln(b_fit)/ln(q/p) for each convergent:

| convergent | k\* |
|---|---|
| 65/41 | 5.9960 |
| **84/53** | **5.99978** |
| 485/306 | 5.99928 |
| 1054/665 | 5.99932 |

84/53's k\* misses integer 6 by only 2.2×10⁻⁴ — tighter than any neighbor.
That is a genuine, non-trivial near-integer coincidence. However, checked
independently whether "6" is *derivable* from CF invariants of that
convergent: partial quotients a0..a6 = [1,1,1,2,2,3,1], sum = 11 (not 6);
a6 itself = 1 (not 6); convergent index is 6 only because we picked that
convergent (circular — 53 was chosen as the heartbeat length externally, not
derived from index 6). **No independent CF formula produces 6.** Verdict:
the exponent-6 match is a real, tight (2×10⁻⁴-level) empirical coincidence
tied specifically to the 84/53 convergent, not an explained structural
derivation.

## 3. Does 9/4 appear in the convergent/mediant/semiconvergent structure?

**Not found**, in any of: convergents of log2(3), beta, 1/beta, log2(3)−1
(15 CF terms each, denominators to 10-digit scale); semiconvergents
(Stern–Brocot intermediates) of all four; mediants of adjacent log2(3)
convergents k=0..11.

Closest hits (all far outside convergent-quality tolerance, which is
typically ≪1% for genuine convergents of an irrational with these partial
quotients):

- Semiconvergent **7/3** of 1/beta: |7/3 − 9/4| = 0.0833, relative error **3.7%**
- Convergent **53/22** (1/beta, k=4) itself: |53/22 − 9/4| = 0.159, relative error **7.07%**
- Convergent **12/5** (1/beta, k=2): relative error 6.67%

For comparison, true CF convergents of log2(3)/beta/1/beta match to
10⁻³–10⁻¹⁰ relative error in this range (see table 1). A 3.7-7% miss is not
a convergent-scale match — **9/4 is not a convergent, semiconvergent, or
mediant of any of these four quantities to any meaningful precision.**

## 4. Jump-rate drift verdict

Full edge table C=1..28 confirmed (C=27→208, C=28→263 match `w7a_new_edges.txt`
exactly; no C≥29 data available). Deltas M(C)−M(C−1) for C=11..28 (word-index
n=C−10):

```
n:     1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18
delta: 31  6   5   3   8  14  15   2  20   2   7  18   6  25   4  13   3  55
```

**First check — order file's own claim.** The order file states the claimed
jump set {4,5,6,8,11,13,15,17} fits `floor(9n/4)+2` to **±1**. Testing
literally: k=1,2 fit within ±1 (diff 0,1), but **k=3..8 do NOT** (diffs of
2, 3, 2, 2, 2, 3). The ±1 claim as stated does not hold past k=2.

**Rate from the order file's own claimed set**, n_k/k for k=1..8:
`4.0, 2.5, 2.0, 2.0, 2.2, 2.167, 2.143, 2.125`. Post-transient (k=5..8) this
is **monotonically decreasing**: 2.2 → 2.167 → 2.143 → 2.125 — moving *away*
from both 9/4=2.25 and 53/22=2.409, settling below 9/4. Linear-regression
slope over all 8 anchors: **1.964** (below both candidate rates).

**Bias check — empirical top-delta jump set** (unbiased: take the 8 largest
deltas among n=2..18, dropping boundary n=1): {5,6,7,9,12,14,16,18}, giving
n_k/k = `5.0, 3.0, 2.333, 2.25, 2.4, 2.333, 2.286, 2.25`. This oscillates in
the 2.25–2.4 band without settling cleanly on either candidate. Notably, the
single **largest delta in the entire table (55, at n=18/C=28)** was *excluded*
from the order file's claimed jump set even though it exceeds every claimed
jump's delta — that exclusion is unexplained and worth flagging.

**Verdict: no clean convergence to 53/22=2.409.** The order-file-claimed-set
rate trends *down*, settling near/below 9/4, not up toward 53/22. The
unbiased empirical set oscillates without a clear monotonic trend either
way. With only 8-18 data points and no C≥29 data, this is **not resolvable**
at this sample size — "stable-near-9/4" is mildly favored by the claimed-set
trend, "drift toward 53/22" is not supported by either construction.

## 5. Final verdict: **(B) related but distinct convergents of the same number** — with a caveat on 9/4

- Task 1: FACT 1's 53/84 and FACT 2's beta/1-beta framework are literally the
  same CF tail of log2(3) — exact, zero residual. Unified in that sense.
- Task 2: exponent 6 binds tightly and specifically to convergent 84/53
  (k\*=5.9998, next-best convergent is 15× worse), a real if unexplained
  coincidence — supports a common convergent-quantization origin for FACT 1.
- Task 3: **9/4 itself is not a convergent/semiconvergent/mediant of log2(3),
  beta, 1/beta, or log2(3)−1 at any meaningful precision** (best hit 3.7%
  error, an order of magnitude worse than genuine convergent matches). If
  9/4 is a real structural constant of FACT 2, it is **not explained by the
  same log2(3)-convergent machinery** that explains 84/53 and exponent 6.
- Task 4: the jump-rate does not show convergence toward the log2(3)
  convergent 53/22; if anything it trends toward/below 9/4, and the
  order file's own ±1 fit for the jump positions breaks down for k≥3.

**Net call**: FACT 1 (heartbeat 53, convergent 84/53, exponent 6) is
solidly inside log2(3)'s convergent structure, with real if unproven
sub-structure (the exponent-6 near-integer coincidence). FACT 2's 9/4 rate
does **not** land inside that same convergent structure by any test run
here — it is closer to (C) "genuinely outside" than to (A) "unified," but
I'm calling it **(B)** rather than (C) only because the underlying jump-rate
*data itself is noisy and small-sample* (18 deltas, ±1 claim already broken,
no C≥29 confirmation) — a cleaner/longer edge series could still move this
verdict either direction. The one thing this session rules out with
confidence: **9/4 is not sitting on the CF convergent lattice of log2(3) in
any of the forms tested.** That part of a unified-scheme hypothesis is
refuted at the precision checked here.
