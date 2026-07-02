# Red-Team Review Paper: Collatz Proof Draft via Sturmian Precision Collapse

**Reviewed manuscript:** `COLLATZ_PROOF.md`  
**Review mode:** realistic computer-assisted proof standard  
**Purpose:** identify what must be clarified, certified, or strengthened before broad circulation as a claimed proof.

---

## 1. Review Standard

This review does **not** demand a fully formalized proof-assistant-level development.

A historically realistic computer-assisted proof may rely on computation when the computational component is:

1. precisely specified,
2. reproducible,
3. independently checkable,
4. finite or reduced to a finite certificate,
5. clearly separated from heuristic interpretation.

Accordingly, this review classifies issues as:

- **Hand-proof issue**
- **Computational-certificate issue**
- **Finite-reduction issue**
- **Presentation issue**
- **Heuristic/interpretive issue**

The goal is not to reject the manuscript. The goal is to prevent a reviewer from finding an avoidable weak point.

---

## 2. Executive Assessment

The manuscript has a serious proof architecture.

Its strongest components are:

- the odd-only affine formulation;
- the deficit/corridor coordinate system;
- the \(q=53\) Sturmian heartbeat;
- the \(22/53\) support-phase structure;
- the edge formula

\[
M_{\mathrm{edge}}(C)=\left\lfloor\frac{53(C+1)}{22}\right\rfloor;
\]

- the computational census and support-cell audits;
- the separation of cycles, bounded gliders, and unbounded escape.

The central contribution is the proposed **Sturmian precision-collapse mechanism**: a fixed corridor width \(C\) supports only finite residue precision \(m\), so no bounded non-descending positive-integer glider can persist forever.

The draft is now a serious manuscript. The remaining issues are mostly about proof/certificate boundaries and several load-bearing lemmas that must be stated more carefully.

---

## 3. Major Issue 1: Lemma 5a / 5b Must Use the Full State

### Current vulnerable point

The manuscript argues that for a lift

\[
r' = r+d3^m,
\]

the condition

\[
2^a\mid (3r'+1)
\]

reduces to

\[
2^a\mid d3^{m+1},
\]

because the parent state already satisfies

\[
2^a\mid (3r+1).
\]

### Problem

A residue \(r \bmod 3^m\) alone does not determine divisibility by \(2^a\). Since \(3^m\) is odd, changing representatives by multiples of \(3^m\) can change parity and 2-adic valuation behavior.

So the proof must not appear to derive a 2-adic divisibility condition from a purely 3-adic residue.

### Required repair

Define the mathematical scanner state as a combined state carrying enough information:

\[
(\text{3-adic residue},\ \text{2-adic representative},\ \text{affine witness data})
\]

or an equivalent CRT-compatible state.

Then restate Lemma 5a / 5b using that full state.

### Acceptable corrected statement

> Let a live state carry both its \(3^m\)-residue and the compatible 2-adic/affine data determining \(a=v_2(3x+1)\). For lifts \(r'=r+d3^m\), the divisibility condition is evaluated in the combined CRT/affine state. Under that state representation, drop phases force \(d=0\), while support phases admit the stated digit choices.

### Classification

**Hand-proof / presentation issue.**

This is the most urgent repair. It may not break the idea, but the current wording is vulnerable.

---

## 4. Major Issue 2: Support-Cell Non-Reuse Needs a Formal Statement or Certificate Boundary

### Current claim

The manuscript claims precision \(m\) requires

\[
22m
\]

support incidences, while the corridor supplies

\[
53(C+1)
\]

phase-height cells.

### Problem

The \(53\)-block count is solid. What needs hardening is the statement that the \(22m\) incidences are independent and cannot reuse the same phase-height support cell.

### Required repair

Add a named lemma or certificate:

**Support-Cell Non-Reuse Lemma.**

Possible form:

> For a terminal-compatible shadow at precision \(m\), the \(m\) independent ternary precision layers impose independent constraints across the 22 support phases of the 53-block. These constraints require at least \(22m\) distinct phase-height support incidences.

### Must clarify

- why each precision layer contributes 22 constraints;
- why a phase-height cell cannot satisfy two different precision-layer constraints;
- why merged states do not hide illegal reuse;
- why terminal compatibility forces those support incidences;
- why the 22 support phases, rather than all 53 phases, are the bottleneck.

### Computer-assisted proof option

This does not necessarily need a long traditional proof if it is certified by an exact checker. If so, state:

- exact input domain,
- exact state definition,
- exact incidence-counting algorithm,
- audit output,
- failure criteria,
- reproducibility command.

### Classification

**Central proof/certificate boundary.**

---

## 5. Major Issue 3: Integer-Shadow Correspondence Needs Sharper Definition

### Current claim

If an actual integer orbit stays inside corridor width \(C\), then its residue class is terminal-compatible at every precision \(m\).

### Problem

The word “terminal-compatible” is potentially ambiguous. A non-descending orbit may never hit terminal value \(1\), so the implication must be stated in automaton terms.

### Required repair

Define \(\mathcal T(C,m)\) exactly as the residue-state set generated by the mathematical automaton, not merely as an observed scanner output.

Then prove:

> If \(x\) is a positive odd integer whose odd-only orbit remains inside corridor width \(C\), then for every \(m\ge1\), the state \(x\bmod 3^m\) belongs to the automaton state set \(\mathcal T(C,m)\).

### Must prove

- the automaton transitions match the odd-only Collatz residue transitions;
- the merged representation does not exclude any real integer orbit;
- terminal/inverse compatibility is exactly the mathematical compatibility needed.

### Classification

**Bridge-theorem issue.**

Likely fixable by definitions and a short proof.

---

## 6. Major Issue 4: Cycle Section Needs Exact Bounds

### Current approach

The draft separates cycles from bounded gliders. That is correct.

But the proposed large-cycle contradiction uses scale statements such as:

\[
m\approx k,
\]

and

\[
C=O(\log k).
\]

### Problem

Those are not enough for a theorem unless made explicit with constants and a threshold.

### Required repair

Replace the asymptotic section with exact inequalities:

\[
m\ge f(k),
\]

\[
C\le g(k),
\]

and prove:

\[
f(k)>\frac{53(g(k)+1)}{22}
\]

for all

\[
k>K_0.
\]

Then show the finite computational certificate covers all

\[
k\le K_0.
\]

### Classification

**Finite-reduction issue.**

This is acceptable for a computer-assisted proof if the threshold and certificate are exact.

---

## 7. Major Issue 5: Lock 4 Still Needs a Deterministic Bridge Inequality

### Current claim

Unbounded escape is impossible because bridge gaps grow too fast and the division tax prevents enough reserve accumulation.

### Problem

The argument currently uses approximate/physical language:

\[
306(2-\log_2 3)\approx127.
\]

This is compelling but not yet a deterministic theorem.

### Required repair

State a bridge inequality:

\[
C_{\mathrm{available}}(q_i,q_{i+1})
<
C_{\mathrm{required}}(q_{i+1}).
\]

Define exactly:

- available reserve,
- usable reserve,
- launch height,
- crash tax,
- bridge gap,
- support requirement,
- sustained corridor breach.

Then prove the inequality, or reduce it to a finite computational certificate.

### Classification

**Major theorem/certificate boundary.**

---

## 8. Major Issue 6: Computational Certificates Must Be Scoped Precisely

### Current issue

The manuscript refers to several computations:

- \(C=1\) through \(50\) cutoff consistency;
- \(10^{11}\) Lock 4 scan;
- breach witnesses;
- lift-profile data;
- birth-invariant audits.

### Problem

These are valuable, but each must say exactly what was certified.

For example:

> \(C=6\) through \(50\) at \(m=1\) is consistent with the edge formula

is not the same as:

> full \(m\)-ladders were verified for \(C=6\) through \(50\).

### Required repair

For each computational result, include:

- input domain,
- algorithm,
- exact arithmetic type,
- stopping condition,
- output files,
- summary counts,
- what theorem/certificate it supports,
- what it does **not** prove.

### Classification

**Presentation/certificate issue.**

---

## 9. Secondary Issue: Avoid Overbroad Philosophical Statements

The statement that all locks are expressions of

\[
2^A\ne3^k
\]

is philosophically useful but too broad as a theorem.

Better wording:

> The irrationality of \(\log_2 3\) generates the Sturmian/convergent structure. The individual proof components require additional arithmetic: affine offset obstruction for cycles, support-capacity collapse for bounded gliders, and bridge-reserve inequalities for unbounded escape.

---

## 10. Secondary Issue: Avoid “Generically”

The manuscript should avoid phrases like:

> generically one lift survives.

If the proof uses it, make it exact or computationally certified.

If the proof does not require it, phrase it as observed scanner behavior.

---

## 11. Recommended Revised Dependency Table

Use a table like this in the manuscript.

| Claim | Type | Status Needed |
|---|---|---|
| Odd-only affine formula | Hand proof | Complete |
| 53-block support/drop count | Hand / finite arithmetic | Complete |
| Full-state lift digit lemma | Hand proof / exact state proof | Needs rewrite |
| Support-cell non-reuse | Hand proof or computational certificate | Needs boundary |
| Edge formula \(M_{\mathrm{edge}}(C)\) | Theorem from support capacity | Depends on non-reuse |
| Integer-shadow correspondence | Bridge theorem | Needs sharper definition |
| No bounded glider | Theorem | Depends on edge + correspondence |
| No cycle | Finite reduction + computation or delta invariant | Needs exact threshold/certificate |
| No unbounded escape | Theorem/certificate | Needs deterministic bridge inequality |
| Collatz conclusion | Theorem | Depends on all above |

---

## 12. Fair Publication Standard

This manuscript should **not** be judged by the standard of a fully mechanized formal proof.

A fair computer-assisted proof standard is:

1. Infinite claims are either hand-proven or reduced to finite computation.
2. Computational claims are precisely specified and reproducible.
3. Heuristics are not used as theorem steps.
4. Every load-bearing computational certificate has clear scope.
5. The final theorem depends only on proven lemmas and certified computations.

Under that standard, the current manuscript is promising but must clarify several certificate boundaries.

---

## 13. Minimal Action List

Before broad circulation, make these repairs.

### Repair 1

Rewrite Lemma 5a / 5b using full CRT/affine state.

### Repair 2

Add a named Non-Reuse Lemma or explicitly label the support-cell audit as a computational certificate.

### Repair 3

Rewrite the cycle section with exact inequalities and an explicit finite threshold.

### Repair 4

Rewrite Lock 4 as a deterministic bridge inequality or clearly label it as a computational certificate.

### Repair 5

Add certificate scopes for every computational claim.

### Repair 6

Add a dependency table showing which claims are hand-proven and which are computationally certified.

---

## 14. Bottom Line

The manuscript has a real mathematical core.

The strongest part is the \(53/22\) Sturmian support edge:

\[
M_{\mathrm{edge}}(C)=\left\lfloor \frac{53(C+1)}{22}\right\rfloor.
\]

The main remaining job is not to invent a new framework. It is to harden the proof/certificate boundaries so that a reviewer cannot say:

> This theorem uses a scanner observation as if it were a hand-proven lemma.

If those boundaries are made explicit, the manuscript becomes much more defensible as a computer-assisted proof attempt.
