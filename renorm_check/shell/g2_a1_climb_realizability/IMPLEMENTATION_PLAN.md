# G2 — a=1 Climb Realizability (dual-game pressure)

**Track:** `renorm_check/shell/g2_a1_climb_realizability/`
**Branch:** `grok/g1-shell-toll-surgery` (shared Grok working branch; tracks are folders, not branches)
**Architect:** Grok (xAI), 2026-07-08
**Status of this file:** **IMMUTABLE** after initial freeze.
Do not edit to fit results. Receipts → `IMPLEMENTATION_LEDGER.md` (this track only).
Story → branch-level `../GROK_SYNTHESIS.md` (one synthesis for the whole branch).

**House Rules:** `/mnt/Shared/HOUSE_RULES.md` / repo `AGENTS.md`.
Thresholds pre-registered. Honest failure = deliverable. No agent commits.

---

## 0. Why G2 (from G1, with receipts)

| G1 result | Evidence | Implication for G2 |
|-----------|----------|-------------------|
| **P2.1 REFUTED** | E2: F7 `in_shell_after` at C=5 = 0/107 vs null ~0.30 | Stop “exits land in death shell.” Shell is capacity *inside* corridor, not exit tax. |
| **P2.2 CONFIRMED** | E2: **a=1 on 1195/1195** upcrossings | Every record-setting climb step is forced into the pure expansion exponent. That is a 2-adic constraint on \(x\). |
| **P2.3 CONFIRMED** | interior δ≥3 rate 0 | Climbs are ceiling-local in deficit; the interesting object is *repeated* a=1 at the running max. |
| **P2.4 CONFIRMED** | 100% return ≤200 steps | Free orbits that climb still fall back in sample — but that is not a global bound. |
| P1.1 INCONCLUSIVE | letter 358 real; D blind m≤8 | F5 stays on renorm/underlock; **not G2**. |
| P3.1 INCONCLUSIVE | ΔM staircase real; alignment blind | Optional later; **not G2 primary**. |

**Thesis (to pressure, not prove):**  
An escaping orbit needs unbounded corridor width. G1 says each upcrossing is an **a=1** step. A chain of \(N\) such climbs forces \(x_0\) into a nested family of 2-adic cylinders (each a=1 is \(3x+1 \equiv 0 \pmod{2}\) but \(3x+1 \not\equiv 0 \pmod{4}\) when a exactly 1, i.e. \(x \equiv 1 \pmod{2}\) already odd and \(v_2(3x+1)=1 \Leftrightarrow x \equiv 1 \pmod{2}\) wait — actually for odd x, \(3x+1\) even always; \(v_2=1\) means \(3x+1 \equiv 2 \pmod{4}\) ⇒ \(3x \equiv 1 \pmod{4}\) ⇒ \(x \equiv 3 \pmod{4}\) since 3·3=9≡1).  

Repeated a=1 along a climb itinerary tightens mod \(2^{O(N)}\). The all-a=1 infinite ray is the classic \(-1 \in \mathbb{Z}_2\) obstruction. **G2 asks:** for *finite* climb words matching observed upcrossing patterns, how fast does the modulus grow, do positive odd integers exist in the cylinder at depth \(N\), and does the residual set after \(N\) climbs look empty of “can climb forever” candidates?

This is the dual-game pivot G1 synthesis registered: integer realizability of a=1 ceiling climbs, not more F7 exit histograms.

---

## 1. Non-goals

- F5 (358 vs 359); D(m) letter surgery re-runs
- Death-shell residual membership as exit tax (G1 killed that operationalization)
- Full Collatz proof; Lock 1/2 re-sweeps; spectral ρ
- New C≥32 genuine-death edge sweeps
- Git commit/push unless operator grants

---

## 2. Shared validation (V0)

| ID | Check | Pass |
|----|-------|------|
| V0 | Reuse G1 orbit helper semantics: odd-only step, deficit \(d_k=\lfloor k\alpha\rfloor-A_k\), upcrossing = new max \(d\) | Spot-check on start `80049391`: at least one upcrossing with a=1; matches G1 CSV row if present |
| V1 | Exact a=1 residue lemma: odd \(x\), \(v_2(3x+1)=1\) iff \(x \equiv 3 \pmod{4}\) | Exhaustive check mod 4 (and spot mod 8/16 consistency) |
| V2 | Cylinder lift: given \(x \bmod 2^j\) with forced a-sequence prefix, next modulus is well-defined | Unit test on 20 random odd starts: predicted a from residue matches actual a while a < j |

**If V1–V2 fail:** stop; fix number theory / code before E experiments.

---

## 3. E1 — Climb word census (empirical object)

### 3.1 Object

From free orbits (same start families as G1 E2: high-reserve list, breach candidates cap 200, 100 random odds seed **20260709**, max_steps 8000), extract **climb episodes**:

- A climb episode is a maximal run of consecutive steps where each step is an upcrossing (new max deficit) **or** a contiguous block of a=1 steps while at the running ceiling (define precisely in code; ledger the definition used).

**Primary definition (frozen):**  
`climb_run` = maximal consecutive sequence of steps with `a_k = 1` that includes at least one upcrossing (new max d). Record length L, starting x, deficit before/after, number of upcrossings in the run.

### 3.2 Deliverables

- `artifacts/e1_climb_runs.csv`
- `artifacts/e1_summary.json` — histogram of L, max L, rate of L≥k

### 3.3 Gates

| ID | Gate |
|----|------|
| E1-G1 | ≥100 climb runs |
| E1-G2 | 100% of upcrossings have a=1 (reconfirm G1 P2.2 on this sample; if <0.99, halt and diagnose) |

### 3.4 Predictions (frozen 2026-07-08, pre-data)

**Q1.1** Max climb-run length L in this sample is **finite and small** (≤ 20). **Confidence: 0.70**  
If any L ≥ 40 → flag as “long climb witness” for E2.

**Q1.2** Histogram of L is **geometric-like** (mode at L=1, strictly decreasing counts for L=1,2,3 at least). **Confidence: 0.55**

**Q1.3** Mean number of upcrossings per start is **≥ 1** on high-reserve starts and **< 5** on random odds. **Confidence: 0.60**

---

## 4. E2 — 2-adic cylinder for pure a=1 prefixes

### 4.1 Object

For the pure word \(w_L = (1,1,\ldots,1)\) of length L:

- Affine map: \(S^{L}(x) = (3^L x + B_L)/2^{A}\) with \(A=L\) if all a=1.
- Solvable in positive odds iff congruence conditions hold.
- Exact: starting odd x with a_0=…=a_{L-1}=1 means a nested system  
  \(x \equiv c_L \pmod{2^{m(L)}}\) for an explicit residue \(c_L\) and modulus growth \(m(L)\).

**Implement** (exact ints):

1. Compute the unique residue class mod \(2^{L+1}\) (or whatever the sharp modulus is) of odd positives that realize \(w_L\), or prove empty.
2. Table L=1..L_max (L_max ≥ 24, raise if cheap): modulus bit-length, representative, whether class nonempty in odds, smallest positive odd in class if any (search bound 2^{m+2} or CRT constructive).

### 4.2 Gates

| ID | Gate |
|----|------|
| E2-G1 | L=1 class = {x odd : x ≡ 3 mod 4} — match V1 |
| E2-G2 | For each L, either constructive representative or proof of empty class |
| E2-G3 | Modulus bit-length is **nondecreasing** in L |

### 4.3 Predictions (frozen)

**Q2.1** The pure a=1 word of length L is realizable by some positive odd for **all L ≤ 24** (cylinders nonempty). **Confidence: 0.65**  
(If empty at some L* ≤ 24 → strong obstruction; ledger L*.)

**Q2.2** Modulus bit-length \(m(L)\) satisfies \(m(L) \ge L\) (at least one new 2-power per step). **Confidence: 0.75**

**Q2.3** Smallest positive odd realizing \(w_L\) grows at least exponentially in L (fit log2(min_x) ≥ c·L − O(1) with c ≥ 0.5 on L=1..16). **Confidence: 0.50**

**Q2.4 (link to −1):** The inverse limit of the a=1 cylinders is exactly the 2-adic class of **−1** (or a finite union including −1). Check: representatives mod 2^m approach −1 for large m. **Confidence: 0.55**

---

## 5. E3 — Mixed climb words from E1 (not only pure a=1)

### 5.1 Object

G1 upcrossings are a=1, but between upcrossings the orbit may insert other a. Take the **top 20** distinct climb-adjacent exponent words from E1 (by frequency), length ≤ 12.

For each word w: decide realizability by positive odd x (same cylinder method generalized to variable a — product of local conditions; pin a by 2-adic when a is determined).

### 5.2 Gates

| ID | Gate |
|----|------|
| E3-G1 | ≥10 distinct words analyzed |
| E3-G2 | Each word: nonempty/empty + modulus bits + min witness or empty proof |

### 5.3 Predictions (frozen)

**Q3.1** Every frequent short climb word from E1 is realizable (nonempty cylinder). **Confidence: 0.60**

**Q3.2** No frequent word of length ≥ 8 has a positive odd witness below 10^6. **Confidence: 0.45** (escape needs large x if any)

**Q3.3** Words that include an upcrossing pattern (deficit-increasing under true credit) are **stricter** (larger modulus) than pure a=1 of same length. **Confidence: 0.50**

---

## 6. E4 — Stretch: return vs climb capacity (optional)

Only if E1–E3 complete with budget.

**Object:** Among E1 starts, max deficit M vs number of a=1 upcrossings U.  
**Prediction Q4.1:** U ≤ f(M) with f linear-ish (e.g. U ≤ M+1) always in sample. **Confidence: 0.55**

Does **not** prove bounded deficit; only shapes the dual-game state space.

---

## 7. Execution order

1. Scaffold (this freeze) — plan / ledger / synthesis.  
2. V0–V2.  
3. E1 climb census.  
4. E2 pure a=1 cylinders.  
5. E3 mixed words from E1.  
6. E4 optional.  
7. Update branch `../GROK_SYNTHESIS.md` after each experiment (not a new synthesis file).

---

## 8. Layout

```
renorm_check/shell/g2_a1_climb_realizability/
  IMPLEMENTATION_PLAN.md   # THIS FILE — immutable
  IMPLEMENTATION_LEDGER.md # this track only
  README.md
  scripts/
  artifacts/
```

Branch narrative (shared): `renorm_check/shell/GROK_SYNTHESIS.md`  
Parent G1 track (read-only inputs): `renorm_check/shell/g1_shell_toll_surgery/artifacts/`

---

## 9. Prediction scoreboard (fill only in this ledger + branch GROK_SYNTHESIS)

| ID | Claim (short) | Conf | Outcome |
|----|---------------|------|---------|
| Q1.1 | Max climb-run L ≤ 20 in sample | 0.70 | — |
| Q1.2 | L histogram geometric-like | 0.55 | — |
| Q1.3 | Upcrossings: high-reserve ≥1, random <5 mean | 0.60 | — |
| Q2.1 | Pure a=1 realizable all L≤24 | 0.65 | — |
| Q2.2 | m(L) ≥ L | 0.75 | — |
| Q2.3 | min witness grows ≥ 2^{0.5 L} | 0.50 | — |
| Q2.4 | Inverse limit → −1 in ℤ₂ | 0.55 | — |
| Q3.1 | Frequent mixed words realizable | 0.60 | — |
| Q3.2 | Long frequent words: no witness <1e6 | 0.45 | — |
| Q3.3 | Upcrossing words stricter than pure a=1 | 0.50 | — |
| Q4.1 | U ≤ M+1 in sample (stretch) | 0.55 | — |

---

## 10. Plan freeze

Frozen at first write on branch `grok/g1-shell-toll-surgery`.
Execution does not renegotiate gates or predictions.
Method bugs may be fixed; gates may not be loosened after seeing data.
