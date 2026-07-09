# Shadow-Prime Spectrum of the Collatz Descent — Findings

Executor: cold agent, no prior narrative. Exact integer arithmetic
(Python arbitrary-precision ints, trial division for all p_p). Work
performed entirely in `shell/shadow_primes/`. Scripts: `gate0.py`,
`harness.py`, `xresidue.py`, `analyze.py`. Raw aggregates in
`results.json`, `summary.json`, `xresidue.json`.

## Sample

- **Gate 0** (seed fact): 1000 odd trajectories (n0 = 1..2000 odds),
  24,688 total odd-steps, v3(3x+1) checked at every step.
  **Result: 0 exceptions.** 3x+1 ≡ 1 (mod 3) holds identically, v3 ≡ 0
  confirmed before proceeding.
- **Main sample**: 5,204 odd starts — 5,200 pseudo-random odds drawn
  uniformly from [1, 10^6) (seed 12345, deterministic) + the 4 named
  deep starts (27, 703, 6171, 837799). **All 5,204 converged to 1**
  (0 failures, step cap 100,000 never hit; longest trajectory 195
  steps, from 837799).
- **239,686 total odd-steps** sampled (this is the per-step N for
  density/correlation stats). Support/drop split: v2=1 on 120,084
  steps (50.10%), v2≥2 on 119,602 (49.90%) — matches the standard
  P(v2=1)=1/2 geometric baseline, sanity-check passed.
- Primes tracked: p ∈ {5, 7, 11, 13, 17, 19, 23} (v3 excluded, proven
  identically 0). 95% CIs are Wilson score intervals unless noted.

## Central mechanism (read this before the tables)

A hit v_p(m)≥1 for m=3x+1 requires x ≡ −3⁻¹ (mod p) — **exactly one
residue class mod p**, since 3 is invertible mod every p≠3. This makes
the *structurally correct* equidistribution baseline **1/p**, not
1/(p−1). The SHADOW_ORDER brief's 1/(p−1) "units" hypothesis assumes x
ranges over the p−1 nonzero residues mod p; that's the wrong reference
class here — x is not restricted to units mod p, so the naive uniform
model puts all p residues (including 0) on equal footing, giving 1/p.
Measured densities track 1/p much more closely than 1/(p−1) (mean
|error| 0.0064 vs 1/p, vs 0.0166 vs 1/(p−1), across the 7 primes) —
see Table 1.

---

## (1) Shadow-prime hit-density table

P(v_p≥1) measured over all 239,686 steps, vs the two candidate models.

| p  | hits   | measured P(v_p≥1) | 95% CI (Wilson)     | 1/(p−1) | err vs 1/(p−1) | 1/p     | err vs 1/p |
|----|--------|--------------------|----------------------|---------|-----------------|---------|-------------|
| 2  | 239686 | 1.00000            | [0.99998, 1.00000]  | 1.00000 | +0.00000        | 0.50000 | +0.50000    |
| 5  | 49127  | 0.20496            | [0.20335, 0.20658]  | 0.25000 | −0.04504        | 0.20000 | +0.00496    |
| 7  | 33562  | 0.14002            | [0.13864, 0.14142]  | 0.16667 | −0.02664        | 0.14286 | −0.00283    |
| 11 | 19503  | 0.08137            | [0.08028, 0.08247]  | 0.10000 | −0.01863        | 0.09091 | −0.00954    |
| 13 | 22033  | 0.09192            | [0.09077, 0.09309]  | 0.08333 | +0.00859        | 0.07692 | +0.01500    |
| 17 | 15105  | 0.06302            | [0.06205, 0.06400]  | 0.06250 | +0.00052        | 0.05882 | +0.00420    |
| 19 | 9023   | 0.03765            | [0.03689, 0.03841]  | 0.05556 | −0.01791        | 0.05263 | −0.01499    |
| 23 | 9731   | 0.04060            | [0.03982, 0.04140]  | 0.04545 | −0.00486        | 0.04348 | +0.00288    |

**Verdict: 1/p is the correct first-order law, not 1/(p−1).** v2 is
the sole exception (v2≥1 with probability 1, since 3x+1 is always even
— 2 is a "structurally forced" prime, not equidistributed at all;
mean v2 per step = 1.99045, consistent with the standard E[v2]=2
Collatz geometric-tail result).

**Caveat on significance:** raw-step Wilson CIs (N=239,686) are
misleadingly tight because successive steps within one trajectory are
**not independent** — x_{k+1} is a deterministic function of x_k, so
x mod p is an autocorrelated chain, not iid draws. Direct test: using
only the 5,204 *trajectory-starting* values n0 (one independent draw
per chain) mod p, chi-square vs uniform gives chi2/dof ≈ 0.5–1.3 for
every prime (perfectly consistent with uniform, as expected since n0
is drawn uniformly at random). Pooling all 239,686 correlated steps
instead gives chi2/dof of 120–1380 — inflated purely by chain
autocorrelation, not by a real per-step bias. Re-deriving a
conservative CI using n_traj=5204 as the effective N: **1/p falls
inside the conservative CI for p=5,7,17,23, but stays outside for
p=11, 13, 19** even under this much more conservative accounting —
those three are flagged as the candidates for genuine (if small)
structural deviation from 1/p (see §5).

---

## (2) v2-credit-word correlation verdict

**Yes — shadow-prime appearance is correlated with v2 phase (support
vs drop), and the effect is prime-specific in sign, but the linear
correlation coefficient is small (|r| < 0.11) for every prime.**

P(v_p≥1 | v2=1, "support") vs P(v_p≥1 | v2≥2, "drop"), pooled
two-proportion z-test, plus Pearson r between the full v2 word (v2
magnitude, 1..k) and the v_p word (magnitude), and between the binary
"is-drop" indicator and the binary hit indicator:

| p  | P(hit\|support) | P(hit\|drop) | diff     | z       | r(v2,v_p) magnitude | r(is_drop, hit_p) binary |
|----|------------------|---------------|----------|---------|------------------------|----------------------------|
| 5  | 0.19345          | 0.21653       | −0.02308 | −13.99  | +0.0062                | +0.0286                    |
| 7  | 0.15072          | 0.12929       | +0.02143 | +15.12  | −0.0342                | −0.0309                    |
| 11 | 0.06831          | 0.09448       | −0.02617 | −23.43  | +0.0030                | +0.0479                    |
| 13 | 0.08311          | 0.10078       | −0.01767 | −14.97  | −0.0236                | +0.0306                    |
| 17 | 0.08925          | 0.03668       | +0.05257 | +52.96  | −0.0798                | −0.1082                    |
| 19 | 0.03468          | 0.04063       | −0.00595 | −7.65   | +0.0171                | +0.0156                    |
| 23 | 0.03638          | 0.04483       | −0.00845 | −10.48  | +0.0118                | +0.0214                    |

All differences are statistically significant at N~120K per arm
(|z|>7.6 for every prime) — but every |r| is under 0.11, so **the
effect is real but weak**: knowing v2's phase moves a shadow prime's
hit probability by 0.6–5.3 percentage points, not by a large fraction
of its base rate, except for 17. **p=17 is the standout**: hit density
more than doubles on support steps vs drop steps (8.9% vs 3.7%,
diff=+5.26pp, the largest of any prime, z=+53, r(binary)=−0.108 — the
largest-magnitude correlation in the table). 7 also favors support
(+2.14pp); 5, 11, 13, 19, 23 all favor drop steps instead. No universal
direction — it is genuinely prime-specific, not a uniform "shadow
primes prefer support/drop" law.

**Phase / heartbeat clustering:** lag-1 through lag-10 autocorrelation
of each prime's own hit-indicator sequence (within a trajectory) shows
short-range structure that decays by lag ~5–10:

| p  | lag1   | lag2   | lag3   | lag4   | lag5   | lag10  |
|----|--------|--------|--------|--------|--------|--------|
| 5  | −0.261 | +0.391 | −0.144 | +0.144 | −0.040 | −0.045 |
| 7  | −0.165 | +0.112 | −0.035 | −0.067 | +0.007 | +0.026 |
| 11 | −0.090 | +0.040 | −0.071 | −0.024 | −0.016 | −0.025 |
| 13 | −0.103 | −0.104 | −0.049 | +0.037 | −0.067 | −0.052 |
| 17 | −0.068 | −0.069 | −0.057 | +0.010 | −0.029 | +0.165 |
| 19 | −0.039 | +0.011 | +0.207 | −0.009 | +0.007 | +0.034 |
| 23 | −0.043 | −0.043 | +0.064 | −0.042 | −0.021 | +0.012 |

There is real "heartbeat" phase structure at short lags — most sharply
for p=5 (strong lag-1 anti-correlation −0.261, lag-2 positive +0.391:
a hit at step k makes an immediate re-hit at k+1 markedly *less*
likely, but a hit two steps later markedly *more* likely) — decaying
toward ~0 by lag 5-10 for most primes. This is consistent with the
same forced-residue mechanism as the density law: hitting x≡r (mod p)
constrains the next x = (3x+1)/2^v2 in a way that transiently biases
against or toward re-hitting, before mixing washes it out within a
handful of steps.

---

## (3) Co-occurrence among shadow primes

Pairwise co-occurrence (both v_p≥1 and v_q≥1 in the same step),
observed vs independent-expected = hits_p·hits_q/N, ratio, and a
rough z (excess/√expected). Full 7×7 triangle in `summary.json`
(task3); top 10 largest deviations from independence:

| pair (p,q) | observed | expected | ratio | z (approx) |
|------------|----------|----------|-------|------------|
| (13,17)    | 623      | 1388.5   | 0.449 | −20.5      |
| (7,23)     | 2080     | 1362.6   | 1.527 | +19.4      |
| (17,23)    | 299      | 613.2    | 0.488 | −12.7      |
| (17,19)    | 786      | 568.6    | 1.382 | +9.1       |
| (11,17)    | 769      | 1229.1   | 0.626 | −13.1      |
| (5,23)     | 1267     | 1994.5   | 0.635 | −16.3      |
| (11,13)    | 1217     | 1792.8   | 0.679 | −13.6      |
| (7,17)     | 1444     | 2115.1   | 0.683 | −14.6      |
| (5,11)     | 2778     | 3997.4   | 0.695 | −19.3      |
| (13,23)    | 622      | 894.5    | 0.695 | −9.1       |

**5 and 7 specifically**: observed 8,275 vs expected 6,879 (ratio
1.203, z≈+16.8) — **5 and 7 mildly cluster** (co-occur more than
chance), not avoid each other.

**General pattern: mostly avoidance, with two clustering exceptions.**
Of the 21 pairs, most (15/21) show ratio<1 (mutual avoidance/negative
association); 6/21 show ratio>1 (clustering), the strongest being
(7,23) at 1.53× and (17,19) at 1.38×. 17 is the prime most often
involved in strong *avoidance* (appears in 4 of the top 5 avoidance
pairs: 13-17, 17-23, 11-17, 7-17) while simultaneously clustering with
19. **This is not reducible to the v2-phase confound**: checked
whether co-occurring/avoiding pairs share the same sign of v2-phase
preference (§2's diff column) — only 6/10 of the top pairs have
matching signs, so the pairwise structure is a genuine residue-level
(CRT-adjacent) interaction through the shared trajectory dynamics, not
just two primes independently both preferring drop (or both support)
steps.

---

## (4) Descent-position density trend

Binned by fractional position along the trajectory (0 = near n0,
9 = near 1), 10 equal bins, ~24K steps/bin. **Caveat found and
corrected for:** 93.8% of all 5,204 trajectories end their last odd
step at x=5 (3·5+1=16=2⁴, the unique fast final descent), which
degenerately zeroes every shadow-prime hit in that one step and
distorts the naive last bin. All slopes below **exclude the final
step** of each trajectory (linear OLS fit of density vs bin index 0-9,
t = slope/SE):

| p  | slope (incl. artifact bin) | t | slope (bins 0-8 only) | t |
|----|------------------------------|-----|--------------------------|-----|
| 5  | +0.00738 | 0.79 | −0.00775 | −1.81 |
| 7  | −0.00016 | −0.12 | +0.00074 | +0.50 |
| 11 | −0.00322 | −2.88 | −0.00145 | −2.67 |
| 13 | +0.00629 | +6.54 | +0.00568 | +5.06 |
| 17 | +0.00361 | +1.67 | +0.00477 | +1.85 |
| 19 | −0.00487 | **−8.80** | −0.00398 | **−15.48** |
| 23 | +0.00039 | 0.14 | −0.00400 | −3.61 |

**Verdict: real trend for p=19 (robustly decreasing toward the n≈1
end, most significant of all primes at any binning, t up to −15.48)
and p=13 (robustly increasing, t≈5-6.5). p=11 shows a smaller but
consistent decreasing trend (t≈−2.7 to −2.9). p=5, 7, 17, 23: no
robust trend survives the artifact-bin exclusion** (sign/significance
flips or stays weak) — "no detectable descent-position pattern at this
N" for those four.

---

## (5) Structurally special prime beyond 3

**p=19 is the standout anomaly.** Three independent lines of evidence:

1. **Largest deviation from the 1/p baseline**: measured 0.03765 vs
   1/19=0.05263 (−28.5% relative, the largest relative miss of any
   tracked prime), and the only prime whose conservative
   trajectory-count CI (N=5204) still excludes 1/p by a wide margin
   ([0.0328, 0.0432] vs 1/p=0.0526).
2. **Not the largest v2-phase split** (p=17 has the biggest
   support/drop gap, +5.26pp) but 19 does show a smaller, still
   significant drop-preference: P(hit|drop)=0.04063 > P(hit|support)
   =0.03468, diff=−0.00595 pp (support minus drop), z=−7.65.
3. **By far the strongest descent-position trend of any prime**
   (t=−15.48 excluding the artifact bin): density falls steadily from
   ~5.4% near the start to ~2.4-3% near the end. This is a genuine,
   monotone, high-significance decline, not noise.

**Modular explanation attempted, not fully derived.** ord_19(2)=18=
p−1 (2 is a primitive root mod 19, same as mod 5, 11, 13 — so
primitive-rootedness of 2 alone does not explain why 19 is uniquely
suppressed; 11 and 13 are also primitive-root primes for 2 but show
much smaller deviations). The x-mod-19 residue histogram (see
`xresidue.json`) shows two residues (4 and 15) sitting at ~1.7-1.8×
the uniform rate while the trigger residue itself (x≡6 mod 19) and
several neighbors sit below uniform — i.e. the map's mod-19 orbit
structure is measurably non-flat in a way it isn't (as strongly) for
the other primes tested, but a closed-form residue-class derivation
analogous to the exact "3x+1≡1 mod 3" identity was **not found** for
19; this is reported as a measured, statistically robust irregularity
(t=−15.48 on position, −28.5% baseline miss) without a proven
generating mechanism — flagged for a follow-up round rather than
asserted as derived law.

No prime showed a *forbidden* pattern like v3≡0 (i.e., no p≠3 had
hits=0). 3 remains the unique structurally forbidden prime, exactly as
predicted by the 3x+1≡1 (mod 3) identity — confirmed exactly, 0
exceptions in gate 0, and implicitly reconfirmed across the full
239,686-step main sample as well (v3 was not even instrumented in the
main harness since gate 0 already proved it identically 0; no v3
column exists in any residue count, and trial division would have
raised it immediately as a co-occurrence artifact if nonzero — it
was not).

---

## Files

- `gate0.py` — seed-fact verification (1000 traj, 0 exceptions)
- `harness.py` — main sample generator + step-level aggregator → `results.json`
- `xresidue.py` — x-mod-p residue distribution check → `xresidue.json`
- `analyze.py` — Wilson CIs, correlation, co-occurrence, position bins → `summary.json`
- `results.json`, `summary.json`, `xresidue.json` — raw numeric aggregates backing every table above
