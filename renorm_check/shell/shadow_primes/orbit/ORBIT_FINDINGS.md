# ORBIT — Why is prime 19 suppressed? Findings

Executor: cold agent, no prior narrative beyond the given SHADOW_FINDINGS.md
premise. Exact integer arithmetic throughout (Python arbitrary precision,
trial division for v_p / v2). All work in `shell/shadow_primes/orbit/`.
Scripts: `orbit_harness.py`, `orbit_harness2.py`, `invariants.py`,
`invariants2.py`, `correlate.py`, `operator.py` → `operator6.py` (iterative
debugging trail kept for the record — see Task 4 below). Raw data:
`orbit_stationary.json`, `orbit_stationary2.json`, `invariants.json`,
`invariants2.json`, `correlate.json`, `operator_plateau_K16.json`,
`qsd4_p19_K14.json`, `qsd_p19_K14.json`, `operator_p19_K14.json`.

## Sample

- **Main sample**: 20,004 odd starts (20,000 pseudo-random odds in
  [1,10^6), seed 20260705, deterministic, + the 4 named deep starts
  27/703/6171/837799). **All 20,004 converged** (0 failures, step cap
  200,000 never hit). **919,575 total odd-steps** — roughly 3.8x
  SHADOW's original sample (5,204 starts / 239,686 steps).
- Primes tracked: {5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67} — the
  original 7 (for direct SHADOW replication) plus 10 more up to 67 for the
  predictive check.
- Two harness passes: `orbit_harness.py` (pooled counts, fast) and
  `orbit_harness2.py` (same sample, also records **per-trajectory** hit
  rates for a conservative, non-autocorrelated CI — see caveat below).
  Both give identical `hole` values (cross-checked to 1e-9, confirming
  no bug divergence between the two implementations).

## Central identity confirmed (sanity check)

By construction, a "hit" (v_p(3x+1)≥1) occurs **iff** x ≡ h_p ≡ −3⁻¹
(mod p) — the pre-image residue and the hit event are the same fact
viewed two ways. Measured exactly: `hit_density == frac_trig_stationary`
to full float precision for every one of the 17 primes in
`orbit_stationary.json`. This means Task 1's "stationary distribution"
and the original SHADOW "hit density" are **the same measurement**, not
independent evidence of each other — the real independent check is
against SHADOW's own separate sample (see Task 2).

## Honest CI caveat (inherited from SHADOW, reconfirmed here)

Raw pooled-step Wilson-style CIs are misleadingly tight because
consecutive steps within one trajectory are autocorrelated, not iid
draws (SHADOW_FINDINGS.md already flagged this). Redone here with
`orbit_harness2.py` using **per-trajectory hit-rate** as the independent
unit (n=20,004 trajectories, not 919,575 steps): the 95% CI (mean ±
1.96·SE across trajectories) **still excludes 1/p for all 17 primes
tested** — e.g. p=19: traj_mean=0.03974, 95% CI [0.03921, 0.04027],
1/p=0.05263, wide margin. This is a materially stronger result than
SHADOW's (which only had 11, 13, 19 survive the conservative
recount) — with ~4x more independent trajectories, **every tested
prime's deviation from 1/p is statistically robust**, not just the
three SHADOW flagged. This reframes the phenomenon: it is not "3
anomalous primes," it is a **universal, prime-specific bias vs the
naive 1/p model**, of varying sign and magnitude.

---

## Task 1+2: the stationary-hole table and correlation to measured deviation

`hole = 1/p − s_p(h_p)` where `s_p(h_p)` = measured stationary mass
(pre-image residue distribution) at the hit-triggering residue h_p.
Positive hole = suppressed vs uniform; negative = excess.

| p  | h_p | s_p(h_p) | 1/p     | hole     | rel_hole (hole/(1/p)) |
|----|-----|----------|---------|----------|------------------------|
| 5  | 3   | 0.20440  | 0.20000 | −0.00440 | −2.20%                 |
| 7  | 2   | 0.13965  | 0.14286 | +0.00321 | +2.25%                 |
| 11 | 7   | 0.08169  | 0.09091 | +0.00922 | +10.14%                |
| 13 | 4   | 0.09133  | 0.07692 | −0.01441 | −18.73%                |
| 17 | 11  | 0.06295  | 0.05882 | −0.00412 | −7.01%                 |
| 19 | 6   | 0.03803  | 0.05263 | +0.01460 | **+27.74%**             |
| 23 | 15  | 0.04018  | 0.04348 | +0.00329 | +7.58%                 |
| 29 | 19  | 0.03973  | 0.03448 | −0.00525 | −15.23%                |
| 31 | 10  | 0.02867  | 0.03226 | +0.00359 | +11.12%                |
| 37 | 12  | 0.02087  | 0.02703 | +0.00616 | +22.80%                |
| 41 | 27  | 0.01596  | 0.02439 | +0.00843 | **+34.54%**             |
| 43 | 14  | 0.01642  | 0.02326 | +0.00684 | +29.40%                |
| 47 | 31  | 0.01785  | 0.02128 | +0.00342 | +16.09%                |
| 53 | 35  | 0.02109  | 0.01887 | −0.00222 | −11.76%                |
| 59 | 39  | 0.01161  | 0.01695 | +0.00534 | +31.51%                |
| 61 | 20  | 0.01957  | 0.01639 | −0.00317 | −19.35%                |
| 67 | 22  | 0.01049  | 0.01493 | +0.00444 | +29.72%                |

**Finding 1 (confirms the hole-IS-the-deviation mechanism):** cross-checked
against SHADOW_FINDINGS.md Table 1's **independent** sample (different
seed 12345, 5,204 starts, 239,686 steps — genuinely separate data from
this round's seed 20260705 / 20,004 starts) for the 7 shared primes:

| p  | orbit hole (this round) | −(SHADOW err vs 1/p) | diff     |
|----|--------------------------|------------------------|----------|
| 5  | −0.00440                | −0.00496               | +0.00056 |
| 7  | +0.00321                | +0.00283               | +0.00038 |
| 11 | +0.00922                | +0.00954               | −0.00032 |
| 13 | −0.01441                | −0.01500               | +0.00059 |
| 17 | −0.00412                | −0.00420               | +0.00008 |
| 19 | +0.01460                | +0.01499               | −0.00039 |
| 23 | +0.00329                | −0.00288               | +0.00617 |

**Pearson r = 0.9729, sign agreement 6/7** (only p=23 flips, and both
values are small/near-noise-level in both samples: +0.0033 vs −0.0029).
Two independent samples (different seeds, different code paths, ~4x
different N) agree tightly on hole depth and sign for 6/7 primes. **This
is strong evidence the "stationary hole at h_p" and "measured hit-density
deviation" are the same real phenomenon, not sample noise** — the
hypothesis in ORBIT_ORDER.md is confirmed as a description (the hole
*is* the deviation, tautologically and empirically), though as noted
above this is expected given hit-density and stationary mass at h_p are
the same measured quantity by construction; the real test was
cross-sample reproducibility, which passed decisively.

**Finding 2 (breaks the "19 is uniquely extreme" framing):** extending
beyond SHADOW's original 7 primes to 17 primes up to 67, **19 is no
longer the standout**. Ranked by relative hole (most suppressed first):
41 (+34.5%), 59 (+31.5%), 67 (+29.7%), 43 (+29.4%), **19 (+27.7%)**, 37
(+22.8%) — 19 is now 5th, not 1st. The largest-magnitude *excess*
(negative hole) is 13 (−18.7%) then 61 (−19.4%), 29 (−15.2%). **19's
extremeness in SHADOW_FINDINGS.md was an artifact of the small (7-prime)
comparison set**, not a genuine outlier property once more primes are
measured.

---

## Task 3: invariant search for hole-depth — NONE FOUND

First pass (`invariants.py`/`correlate.py`) flagged
`dlogh_minus_dlog2_mod(p-1)` at r=+0.71 — but this is a **basis-dependent
artifact**: discrete logs depend on the arbitrary choice of primitive
root g, and directly verified (p=19, all 6 primitive roots mod 19) the
normalized `dlogh−dlog2` value ranges from 0.056 to 0.944 depending on
which g is picked — i.e. it is not a well-defined invariant at all.
Discarded, along with all other dlog-based features (dlog2/(p−1),
dlog3/(p−1), dlogh/(p−1), dlogh_even) for the same reason.

**Corrected pass (`invariants2.py`), basis-independent invariants only:**
ord(2 mod p), ord(3 mod p), ord(h_p mod p), whether 2 is a primitive
root, whether 3 is, whether h_p is, whether 2 and 3 have the same
order, Legendre/Jacobi symbol (QR-ness) of h_p/2/3, gcd(ord2,ord3), and
p itself. **None reaches statistical significance** (Pearson/Spearman,
n=17 primes):

| invariant             | Pearson r | p-value | Spearman ρ | p-value |
|-----------------------|-----------|---------|-------------|---------|
| ord(2)                | +0.094    | 0.72    | +0.191      | 0.46    |
| ord(3)                | +0.142    | 0.59    | +0.291      | 0.26    |
| ord(h_p)              | +0.095    | 0.72    | +0.190      | 0.47    |
| ord2/ord3              | −0.240    | —       | —           | —       |
| same_order(2,3)       | −0.205    | —       | —           | —       |
| prim2 / prim3 / primh | −0.22/−0.23/−0.26 | — | —      | —       |
| is_QR(h_p)            | +0.097    | —       | —           | —       |
| gcd(ord2,ord3)        | −0.001    | 1.00    | +0.202      | 0.44    |
| p (raw size)          | +0.296    | 0.25    | +0.333      | 0.19    |

19's own profile is not distinctive: ord(2)=ord(3)=18 (both primitive
roots — "same_order" and both-primitive is shared with 5, 29, 53, none
of which show comparable hole magnitude: 5 at −2.2%, 29 at −15.2%, 53
at −11.8%, vs 19 at +27.7% — **same qualitative invariant profile,
opposite-sign and wildly different-magnitude outcome**, which by itself
falsifies "same_order + both primitive roots" as a sufficient
explanation). **Verdict: no invariant tested predicts hole-depth across
all 17 primes. This is reported as an honest negative result, not
papered over.**

---

## Task 4: exact residue-transition operator

**Construction attempted:** exact finite operator on odd residues mod
M=p·2^K (K deep enough that P(v2>K)=2^-K is negligible), built via
exact integer application of the true map (not an approximated/averaged
v2) to every state, so v2 is exact per state, not modeled.

**Bug trail (kept for the record, each diagnosed exactly):**
1. `operator2.py` — naive power iteration converges to ~100% mass on
   the true fixed point x=1 (correct but degenerate/uninformative:
   that's just "the map converges," not a residue-hole measurement).
2. `operator3.py` — tried a quasi-stationary distribution (QSD) by
   making direct predecessors of 1 absorbing. Found survival eigenvalue
   locked at exactly 1.000000 — **traced to a genuine bug**: power
   iteration got trapped in a **spurious 3-cycle** at large residues
   near M (verified for p=19,K=14,M=311296: representative integers
   131071, 196607, 294911 — a modular-wraparound artifact, basin size
   12 states out of 155,648, that does not correspond to any real
   Collatz behavior — a real trajectory only visits such a residue
   transiently for one specific huge integer, then moves on).
3. `operator4.py` — excluded the spurious cycle's basin via exact
   backward BFS (basin of true fixed point = 155,636/155,648 =
   99.9923% of states for p=19,K=14). Re-ran power iteration: this is a
   **finite-diameter DAG** (max distance to absorption = 118 steps,
   verified exactly), so it necessarily drains to zero live states —
   there is no true recurrence to converge to. The renormalized shape
   does show a plateau at intermediate iterations (~15-70) before
   finite-size collapse in the tail.
4. `operator5.py` — tried to find the QSD as a formal dominant
   eigenvector via sparse ARPACK. **ARPACK fails to converge**
   (`ArpackNoConvergence`, 0/1 eigenvectors after 5000 iterations).
   Root cause found and proven directly: `np.linalg.eigvals` on the
   dense transient sub-matrix for p=19,K=9 gives **all eigenvalues
   exactly 0.0** — the matrix is **nilpotent**. This is an exact,
   structural fact (finite DAG ⟹ nilpotent adjacency operator), not a
   numerical failure: **there is no dominant eigenvector for this
   construction to find.** Task 4's original framing ("compute its
   stationary eigenvector") does not apply to this finite truncation —
   the object doesn't exist.

**What is measurable instead (`operator6.py`):** the transient
power-iteration shape does stabilize over a mid-range iteration window
before finite-size drain. Reporting the plateau-window mean hole
(iterations 15 through len−10, K=16) as the operator's best empirical
prediction, explicitly flagged as a heuristic (not a proven fixed
point):

| p  | empirical hole | operator plateau hole | same sign |
|----|-----------------|--------------------------|-----------|
| 5  | −0.00440        | −0.02026 ± 0.0219        | yes       |
| 7  | +0.00321        | +0.00893 ± 0.0085        | yes       |
| 11 | +0.00922        | +0.03541 ± 0.0203        | yes       |
| 13 | −0.01441        | −0.02308 ± 0.0066        | yes       |
| 17 | −0.00412        | −0.00880 ± 0.0044        | yes       |
| 19 | +0.01460        | +0.03110 ± 0.0097        | yes       |
| 23 | +0.00329        | −0.00143 ± 0.0094        | **no**    |

**Pearson r = 0.922** across these 7 primes between empirical hole and
operator-plateau hole. 6/7 sign matches (23 flips, but both values are
small and within 1 SD of zero in the operator estimate — consistent
with noise at that prime specifically). The operator plateau
**systematically overshoots** empirical hole magnitude by roughly
2-2.5x for most primes (e.g. 19: 0.0311 operator vs 0.0146 empirical).

**Verdict: partial confirmation.** The pure residue dynamics (v2
computed exactly from the true map, no magnitude/size effects, no
random restarts) DOES reproduce the qualitative hole structure for 19
and correlates strongly (r=0.92) with the empirically measured hole
across primes — so the mechanism is plausibly intrinsic to the residue
dynamics of the odd-map itself, not an artifact of the specific
finite-sample trajectory statistics. However: (a) the formal "stationary
eigenvector" this task asked for does not exist for the exact finite
truncation (proven nilpotent); (b) the heuristic plateau substitute
over-predicts magnitude by ~2x; (c) one prime (23) disagrees in sign,
though at low-confidence magnitude in both measurements. This is
reported as "mechanism substantially supported at the residue-dynamics
level, but not cleanly derived/proven, with a quantitative gap."

---

## Task 5: predictive check on new primes

Since **Task 3 found no invariant reaching significance**, there is no
independently-derived predictor to test — using "prime is suppressed"
(positive hole) as the only available (weak, r=0.30, p=0.25, NOT
significant) trend, extrapolating to larger p:

Measured (`orbit_harness2.py`, same 20,004-trajectory sample,
per-trajectory CI):

| p  | traj_mean_hit_rate | 1/p     | 95% CI (traj-level)      | suppressed (hit&lt;1/p)? |
|----|----------------------|---------|----------------------------|--------------------------|
| 41 | 0.01686              | 0.02439 | [0.01654, 0.01718]        | **yes**                  |
| 43 | 0.01651              | 0.02326 | [0.01622, 0.01679]        | **yes**                  |
| 47 | 0.01690              | 0.02128 | [0.01663, 0.01717]        | **yes**                  |
| 53 | 0.02108              | 0.01887 | [0.02079, 0.02138]        | no (excess)              |
| 59 | 0.01142              | 0.01695 | [0.01118, 0.01166]        | **yes**                  |
| 61 | 0.01855              | 0.01639 | [0.01830, 0.01880]        | no (excess)              |
| 67 | 0.01149              | 0.01493 | [0.01123, 0.01174]        | **yes**                  |

5/7 suppressed. But 11/17 primes in the FULL tested set (65%) are
suppressed overall — so 5/7 (71%) is not distinguishable from the base
rate at this n. **Honest verdict: no real prediction was made (no
invariant survived task 3), so this is not a hit/miss on a genuine
prediction — it is simply "most primes in this range are suppressed,
consistent with the same un-explained base rate seen across the whole
17-prime set."** Framing this as a successful prediction would overstate
what was actually derived.

---

## Summary verdict

1. **Stationary-hole table**: computed for 17 primes (table above);
   hole ranges from −18.7% (p=13) to +34.5% (p=41) relative to 1/p.
2. **Correlation to measured deviation**: r=0.973 (6/7 sign match)
   between this round's independent sample and SHADOW's original
   sample — the phenomenon replicates tightly across independent
   samples. Note this is a tautological identity (hit density ≡
   stationary mass at h_p), so this confirms *reproducibility*, not an
   independent causal test.
3. **Predictive invariant for hole-depth**: **NONE FOUND.** Every
   basis-independent group-theoretic candidate tested (ord(2), ord(3),
   ord(h_p), primitivity of 2/3/h_p, QR-ness, gcd of orders, raw p) has
   |r| < 0.30 and p > 0.19, not significant at n=17. 19's own invariant
   profile (ord2=ord3=18=p−1) is shared by 5, 29, 53 which show
   opposite-sign and very different-magnitude holes — directly
   falsifying that profile as a sufficient explanation.
4. **Residue-operator eigenvector for p=19**: **does not exist** — the
   exact finite-truncation transient operator is provably nilpotent
   (all eigenvalues 0). A heuristic plateau substitute correlates at
   r=0.92 with the empirical hole across 7 primes (qualitatively
   supportive of "residue dynamics alone drives this"), but
   systematically overshoots magnitude ~2x and disagrees in sign for
   1/7 primes (23, low-confidence in both measurements).
5. **Predictive check on {41,43,47,53,59,61,67}**: 5/7 measured
   suppressed, but this is not distinguishable from the un-derived base
   rate (11/17 = 65% of all tested primes are suppressed) since no
   invariant from Task 3 reached significance to make a genuine
   ex-ante prediction. **No confirmed predictive law.**

**Overall: the anomaly is real, reproducible, and appears general (not
unique to 19) — but it persists without a derivable mechanism or
predictive invariant.** The residue-operator work shows the effect is
plausibly intrinsic to the odd-map's pure residue dynamics (not a
sampling artifact), which narrows the search space for a future round,
but this is short of proof and short of a formula. Per the task's own
stated rule: "anomaly persists without a derivable mechanism" is
reported here as the honest verdict, not papered over with a
manufactured law.
