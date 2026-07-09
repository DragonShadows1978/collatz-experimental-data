# G4 — Drop-Gated Upcrossings & Streak Bounds

**Track:** `renorm_check/shell/g4_drop_gate_streaks/`
**Branch:** `grok/g1-shell-toll-surgery`
**Status:** **IMMUTABLE** after freeze.
Receipts → `IMPLEMENTATION_LEDGER.md`. Narrative → `../GROK_SYNTHESIS.md`.

---

## 0. Why G4 (from G3)

G3 found empirically: **100% of 1217 upcrossings** have \(c=2\) and \(a=1\),
and consecutive-up streaks max out at **2**. Successors were:

1. Prove drop-gating (not just sample).
2. Bound streaks via drop structure of the Sturmian word.
3. Explain support-phase interruption of ceiling residence.

**Algebra (to certify in code + write as lemma):**  
Deficit: \(d_{k+1} = d_k + c_k - a_k\), \(c_k\in\{1,2\}\), \(a_k\ge 1\).  
Running max \(C_k = \max_{j\le k} d_j\) (with \(C_{-1}=0\) or pre-orbit 0).  
Upcrossing at step \(k\): \(d_{k+1} > C_{k-1}\) where \(C_{k-1}\) is max before the step.  
Since \(d_k \le C_{k-1}\), slack \(s = C_{k-1} - d_k \ge 0\). Need
\(c_k - a_k > s\). But \(c_k - a_k \le 2-1 = 1\), so \(s < 1\) ⇒ \(s=0\)
and \(c_k - a_k = 1\) ⇒ **\(a_k=1\) and \(c_k=2\)**, and **\(d_k = C_{k-1}\)** (at ceiling).

Thus every upcrossing is exactly a **drop-phase, a=1, at-ceiling** event.
This is identity-level, not statistical.

Consecutive upcrossings require consecutive steps each with \(c=2,a=1\) at the
moving ceiling — hence a run of **drop letters** in the credit word, each
realized with \(a=1\).

---

## 1. Non-goals

- F5; shell residual; git commit; full Collatz proof
- Replacing G3 sample with larger scans (reuse OK)

---

## 2. V0 — Algebraic gate theorem (machine-checked)

### Object
Formalize and check on large free sample + exhaustive small paths:

**Theorem U (upcrossing form):**  
If step \(k\) is an upcrossing under the dual dynamics, then
\(d_k = C_{k-1}\), \(a_k = 1\), \(c_k = 2\).

### Gates
| ID | Check |
|----|-------|
| V0-G1 | Proof sketch in ledger matching the slack argument above (text) |
| V0-G2 | Zero counterexamples on free sample (same shape as G3 E1: ≥1000 ups) |
| V0-G3 | Zero counterexamples on all odds in 1..10^5 for first 200 steps each (or until 1) |

### Predictions
**S0.1** Zero counterexamples on free sample. Conf **0.95**  
**S0.2** Zero counterexamples on small-odds sweep. Conf **0.90**

---

## 3. E1 — Drop-run structure of the credit word

### Object
Exact credit sequence \(c_k\) for \(k=0..N-1\), \(N \ge 10000\).
Measure maximal consecutive run of \(c=2\) (drop runs); histogram;
runs inside one 53-block and across boundaries.

### Predictions
**S1.1** Global max drop-run length for \(k<10^4\) equals max drop-run inside
one period-53 block of the **true** word (not the 22/53 periodicization
unless identical). Conf **0.60**  
**S1.2** Max drop-run length ≤ **3** for \(k<10^4\). Conf **0.55**  
**S1.3** Mean drop-run length ∈ [1.2, 2.0]. Conf **0.50**

---

## 4. E2 — Streak bound vs drop runs (free orbits)

### Object
On free sample: for each consecutive-upcrossing streak of length \(S\),
verify the \(S\) credit letters are all 2, and \(S \le\) max drop-run in the
ambient credit word. Also: fraction of drop-runs of length \(r\) that are
fully realized as up-streaks of length \(r\) (requires a=1 each step).

### Predictions
**S2.1** Every up-streak length \(S\) satisfies \(S \le R_{\max}\) (max drop-run
in credit over the scanned k-range of the sample). Conf **0.85**  
**S2.2** Max up-streak in sample ≤ max drop-run in first 53 credits. Conf **0.70**  
**S2.3** Fraction of length-2 drop pairs (c=2,c=2) that become up-streaks of 2
is ≤ **0.50** (a=1 not always available). Conf **0.55**

---

## 5. E3 — Support-phase interruption

### Object
After each upcrossing, inspect the **next** step: \((c,a,\Delta d)\).
Classify: support (c=1) vs drop (c=2); whether another up occurs;
deficit change.

### Predictions
**S3.1** ≥ **50%** of steps immediately after an upcrossing have \(c=1\). Conf **0.45**  
**S3.2** Rate of immediate second upcrossing (streak≥2 start) ≤ **0.35**. Conf **0.55**  
**S3.3** When post-up step has \(c=1\), second up rate = **0** (corollary of Theorem U). Conf **0.90**

---

## 6. E4 — Heartbeat packing bound (synthetic)

### Object
In one 53-step heartbeat of true credit, max number of upcrossings achievable
under dual dynamics if every drop with ceiling access and free choice of
a∈{1,…} to maximize ups?  

Constrained model: agent may choose a=1 whenever at ceiling and c=2; else
must pick a to stay in corridor or any a≥1. **Upper bound:** number of
isolated drop letters that are not part of… actually simple bound:
**at most one up per drop letter**, and only when at ceiling — max ups per
heartbeat ≤ number of drops = 31, trivial. Tighter: after an up, C increases
by 1; next up needs another drop at new ceiling. Max ups in 53 steps ≤
max number of times we can hit (c=2 at ceiling).  

**Compute:** greedy dual walker: always a=1 when c=2 and at ceiling (force up);
when c=2 not at ceiling, a=1 if d+c-1 stays… simpler **greedy up:**
whenever c=2 and d=C, set a=1 (up); otherwise set a=2 if c=2 else a=1
(try stay/level). Start d0=0..10, k0=0..52, count ups over 53 and 106 steps.

### Predictions
**S4.1** Max ups over any 53 consecutive credits in greedy model (d0≤10) ≤ **15**. Conf **0.50**  
**S4.2** Max ups over 106 steps ≤ **30**. Conf **0.50**  
**S4.3** Greedy max streak ≤ max drop-run (S1). Conf **0.80**

---

## 7. Execution order

V0 → E1 → E2 → E3 → E4 → ledger + GROK_SYNTHESIS.

---

## 8. Scoreboard

| ID | Claim | Conf | Outcome |
|----|-------|------|---------|
| S0.1 | Thm U: 0 counterex free sample | 0.95 | — |
| S0.2 | Thm U: 0 counterex small odds | 0.90 | — |
| S1.1 | max drop-run = block max | 0.60 | — |
| S1.2 | max drop-run ≤ 3 on 10k | 0.55 | — |
| S1.3 | mean drop-run in [1.2,2.0] | 0.50 | — |
| S2.1 | up-streak ≤ R_max credit | 0.85 | — |
| S2.2 | max up-streak ≤ max drop in 53 | 0.70 | — |
| S2.3 | ≤50% of drop-pairs are up-streaks | 0.55 | — |
| S3.1 | ≥50% post-up are support | 0.45 | — |
| S3.2 | second-up rate ≤0.35 | 0.55 | — |
| S3.3 | post-up c=1 ⇒ no second up | 0.90 | — |
| S4.1 | greedy ups/53 ≤15 | 0.50 | — |
| S4.2 | greedy ups/106 ≤30 | 0.50 | — |
| S4.3 | greedy streak ≤ R_max | 0.80 | — |

---

## 9. Freeze

Frozen 2026-07-08 with G3 successors as scope.
