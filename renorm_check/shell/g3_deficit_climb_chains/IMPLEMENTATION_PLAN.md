# G3 — Deficit-Compatible Climb Chains

**Track:** `renorm_check/shell/g3_deficit_climb_chains/`
**Branch:** `grok/g1-shell-toll-surgery` (folder track; not a new branch)
**Status of this file:** **IMMUTABLE** after freeze.
Receipts → `IMPLEMENTATION_LEDGER.md`. Narrative → `../GROK_SYNTHESIS.md`.

**House Rules:** thresholds pre-registered; honest failure = result; no agent commits.

---

## 0. Why G3 (from G1 + G2)

| Prior result | Implication |
|--------------|-------------|
| G1 P2.2: **a=1 on every upcrossing** | Climbs force expansion exponent |
| G1 P2.1: shell-exit tax **REFUTED** | Don't measure F7 at exits |
| G2 Q2.*: pure a=1 = **x ≡ −1 mod 2^{L+1}**, realizable every finite L | Cylinder emptiness does **not** kill climbs |
| G2 Q3.2: long mixed words still have **small** witnesses | Bare word realizability is too weak for escape |
| G2 synthesis successor | Couple **a-sequence to credit/deficit path** |

**Thesis:** An upcrossing is not free. Deficit updates as
\(d_{k+1} = d_k + c_k - a_k\) with Sturmian credit \(c_k \in \{1,2\}\).
At the running ceiling \(d = C\), an upcrossing needs \(a = 1\) and
\(c - 1 > 0\), i.e. typically a **drop** letter \(c = 2\). Long pure a=1
Mersenne witnesses may realize a-words without producing unbounded corridor
growth. G3 measures that dual constraint.

---

## 1. Non-goals

- F5; F7 shell residual; Lock 1/2; spectral ρ; git commit
- Full Collatz proof
- Re-running G1/G2 tables (read-only reuse OK)

---

## 2. Shared validation V0–V1

| ID | Check | Pass |
|----|-------|------|
| V0 | Exact credit: \(c_k = \lfloor(k+1)\alpha\rfloor-\lfloor k\alpha\rfloor\) via bit_length; matches G2/G1 style | Lemma 3: first 53 have 22 ones |
| V1 | On free orbits, \(d_{k+1} = d_k + c_k - a_k\) holds identically for tracked deficit | 100% on 80049391 for 5000 steps |

---

## 3. E1 — Credit phase of upcrossings

### Object
Free orbits: same family as G2 E1 (HIGH_RESERVE + breach ≤200 + 100 random
seed **20260710**, max_steps 8000). For every upcrossing step k, record
\(c_k\), \(a_k\), \(d_k\), \(C_{\mathrm{run}}\).

### Gates
| ID | Gate |
|----|------|
| E1-G1 | ≥500 upcrossings |
| E1-G2 | a=1 rate on upcrossings ≥ 0.99 |

### Predictions (frozen)
**R1.1** Fraction of upcrossings with \(c_k = 2\) (drop) ≥ **0.90**. Conf **0.70**  
**R1.2** Fraction with \(c_k = 1\) (support) ≤ **0.10**. Conf **0.70**  
**R1.3** When at exact ceiling (\(d_k = C_{\mathrm{run}}\) before step, or
\(d_k = C_{\mathrm{run}}\) after previous), upcrossings with c=1 rate ≤ **0.05**. Conf **0.55**

---

## 4. E2 — Mersenne pure-a=1 witnesses vs deficit growth

### Object
For L = 1..24, let \(x_L = 2^{L+1} - 1\) (G2 min pure a=1 witness).
Run odd-only orbit for **exactly L steps** (the guaranteed a=1 prefix) and
also for min(500, 5L) further steps. Record: number of upcrossings in the
a=1 prefix, max deficit in prefix, max deficit in extended run, whether
prefix is all a=1 (sanity).

### Gates
| ID | Gate |
|----|------|
| E2-G1 | All L=1..24 realize a=1 for first L steps |
| E2-G2 | Table written for all L |

### Predictions (frozen)
**R2.1** In the pure a=1 prefix of length L, number of upcrossings ≤ **L**
(always true) and **mean** upcrossings/L over L=1..24 ≤ **0.50**. Conf **0.50**  
**R2.2** max deficit in the a=1 prefix for each L is ≤ **L**. Conf **0.60**  
**R2.3** max deficit after extended run for \(x_L\) is **not monotone** in L
(not a smooth escape ladder). Conf **0.55**

---

## 5. E3 — Dual walk: prescribed a=1 vs credit-forced deficit

### Object
Simulate **synthetic** deficit path with forced a≡1 for L steps starting at
phase k0 ∈ {0..52}, d0 ∈ {0..10}:
\(d \leftarrow d + c_{k} - 1\), k = k0..k0+L-1.
Record: final d, min d, number of “virtual upcrossings” (d exceeds running max),
whether d stays ≥ 0 for all steps.

No integer x required — pure dual-game bookkeeping (legal deficit trajectories
under a=1).

### Gates
| ID | Gate |
|----|------|
| E3-G1 | Full grid L∈{1,2,4,8,12,16,20,24} × k0=0..52 × d0=0..10 evaluated |
| E3-G2 | For each (L,k0,d0): fields min_d, n_virt_up, stayed_nonneg |

### Predictions (frozen)
**R3.1** Fraction of grid cells with stayed_nonneg for L=24 is ≤ **0.25**. Conf **0.55**  
**R3.2** Among cells with d0=0, L=24, fraction stayed_nonneg ≤ **0.10**. Conf **0.60**  
**R3.3** Mean virtual upcrossings for L=24, d0=0 is ≤ **8**. Conf **0.50**

---

## 6. E4 — Consecutive upcrossing streaks (free orbits)

### Object
On E1 sample orbits: maximal run of **consecutive steps that are each
upcrossings**. (Stricter than G2 climb_run which allowed a=1 without each
step upcrossing.)

### Predictions (frozen)
**R4.1** Max consecutive-upcrossing streak ≤ **5** in sample. Conf **0.65**  
**R4.2** ≥ **80%** of upcrossings are isolated (streak length 1). Conf **0.55**

---

## 7. Execution order

1. Freeze this plan + ledger scaffold  
2. V0–V1  
3. E1  
4. E2  
5. E3  
6. E4  
7. Update `../GROK_SYNTHESIS.md` + close ledger  

---

## 8. Layout

```
g3_deficit_climb_chains/
  IMPLEMENTATION_PLAN.md
  IMPLEMENTATION_LEDGER.md
  README.md
  scripts/
  artifacts/
```

---

## 9. Scoreboard (fill in ledger/synthesis only)

| ID | Claim | Conf | Outcome |
|----|-------|------|---------|
| R1.1 | ≥90% ups at c=2 | 0.70 | — |
| R1.2 | ≤10% ups at c=1 | 0.70 | — |
| R1.3 | Ceiling ups almost never c=1 | 0.55 | — |
| R2.1 | Mersenne prefix ups/L mean ≤0.50 | 0.50 | — |
| R2.2 | Mersenne prefix max_d ≤ L | 0.60 | — |
| R2.3 | Extended max_d not monotone in L | 0.55 | — |
| R3.1 | L=24 stayed_nonneg ≤25% of grid | 0.55 | — |
| R3.2 | d0=0 L=24 stayed_nonneg ≤10% | 0.60 | — |
| R3.3 | mean virt ups L=24 d0=0 ≤8 | 0.50 | — |
| R4.1 | max consec ups streak ≤5 | 0.65 | — |
| R4.2 | ≥80% ups isolated | 0.55 | — |

---

## 10. Plan freeze

Frozen 2026-07-08. Do not edit predictions after data.
