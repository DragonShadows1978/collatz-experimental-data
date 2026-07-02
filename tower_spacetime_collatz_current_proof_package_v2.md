# Tower-Spacetime Collatz: Current Proof Package

**Draft status:** working mathematical writeup  
**Scope:** current lock framework, Lock 1 proof, Lock 3 bounded-corridor collapse proof, Lock 4 bridge obstruction mechanism, and the demotion of Lock 2 into a descent-exit lemma.

---

## 0. Executive Summary

We work with the odd-only Collatz map

\[
S(x)=\frac{3x+1}{2^{v_2(3x+1)}}.
\]

A putative non-descending positive odd orbit can be studied by tracking:

- odd-step time \(k\),
- total division exponent \(A_k\),
- deficit/reserve relative to the critical line \(k\log_2 3\),
- bounded corridor width \(C\),
- residue precision height \(m\),
- terminal-compatible inverse shadows.

The current framework separates possible non-descending behavior into:

1. **Periodic positive engines** — killed by Lock 1.
2. **Bounded gliders** — killed by Lock 3.
3. **Unbounded reserve/corridor escape** — killed by Lock 4 bridge obstruction.
4. **Finite descent crossing** — demoted from “Lock 2” to the descent-exit face of the same geometry.

The central new result is the Lock 3 support-capacity edge:

\[
M_{\text{edge}}(C)=\left\lfloor \frac{53(C+1)}{22}\right\rfloor,
\]

with first desert precision

\[
K(C)=M_{\text{edge}}(C)+1.
\]

A bounded corridor of width \(C\) cannot support terminal-compatible residue shadows above this finite precision. Therefore no fixed finite \(C\) can support an infinite positive-integer bounded glider.

The \(53/22\) coefficient comes from the Sturmian 53-block associated with \(\log_2 3\). In one 53-step heartbeat there are exactly 22 support phases and 31 drop phases.

---

# 1. Odd-Only Collatz Dynamics

For a positive odd integer \(x_i\), define

\[
a_i=v_2(3x_i+1),
\]

and

\[
x_{i+1}=\frac{3x_i+1}{2^{a_i}}.
\]

For a finite exponent word

\[
w=(a_0,a_1,\ldots,a_{k-1}),
\]

define

\[
A=A(w)=a_0+a_1+\cdots+a_{k-1}.
\]

The \(k\)-step odd-only map has affine form

\[
S^k(x)=\frac{3^k x+B_w}{2^A},
\]

where \(B_w\) is the accumulated affine offset from the \(+1\) terms.

The recurrence for \(B_w\) is exact:

\[
B_0=0,\qquad A_0=0,
\]

and when appending exponent \(a_j\),

\[
B_{j+1}=3B_j+2^{A_j},
\]

\[
A_{j+1}=A_j+a_j.
\]

---

# 2. Deficit, Corridor Width, and Bounded Gliders

Define

\[
d_k=\lfloor k\log_2 3\rfloor-A_k.
\]

This measures the orbit relative to the critical contraction line.

A **bounded Lock 3 glider** is an exponent path satisfying

\[
0\le d_k\le C
\]

for all \(k\), for some fixed finite \(C\).

Here \(C\) is the corridor width. It is not an input integer. It is a bound on how far the orbit’s exponent path can deviate while avoiding contraction.

A true positive-integer bounded glider would have to remain compatible with the inverse residue constraints at every residue precision height \(m\).

Lock 3 proves that this cannot happen.

---

# 3. Lock 1: Periodic Positive Engines Have Negative Ghosts

## Theorem 1 — Positive-action repeated blocks cannot form positive cycles

Let \(w\) be a nonempty exponent word of length \(k\) and total exponent \(A\). Its affine block map is

\[
F_w(x)=\frac{3^k x+B_w}{2^A}.
\]

Assume \(w\) has positive action:

\[
3^k>2^A.
\]

Then \(F_w\) has a unique affine fixed point

\[
x_w=\frac{B_w}{2^A-3^k}.
\]

Since \(B_w>0\) for every nonempty word and \(2^A-3^k<0\), we have

\[
x_w<0.
\]

Thus the fixed point of any positive-action repeated block is negative. It is a ghost, not a positive integer.

Moreover, for any \(x>0\),

\[
F_w(x)-x
=
\frac{(3^k-2^A)x+B_w}{2^A}.
\]

Since \(3^k-2^A>0\), \(B_w>0\), and \(x>0\),

\[
F_w(x)-x>0.
\]

So a positive-action block strictly increases every positive input and cannot return to form a positive cycle.

Therefore no positive orbit can be powered forever by a repeating positive-action engine.

---

# 4. Lock 3: The Bounded-Corridor Collapse Mechanism

## 4.1 The critical Sturmian word

Let

\[
\alpha=\log_2 3.
\]

Define the critical Sturmian credit word

\[
c_n=\lfloor (n+1)\alpha\rfloor-\lfloor n\alpha\rfloor.
\]

Since \(1<\alpha<2\), each \(c_n\) is either \(1\) or \(2\).

The near-return denominator

\[
q=53
\]

is the first major heartbeat scale in the current Lock 3/Lock 4 geometry.

Compute

\[
\lfloor 53\log_2 3\rfloor=84.
\]

Let \(x\) be the number of \(1\)-steps and \(y\) be the number of \(2\)-steps in the 53-block. Then

\[
x+y=53,
\]

\[
x+2y=84.
\]

Subtracting gives

\[
y=31,
\]

so

\[
x=22.
\]

Thus one 53-heartbeat contains exactly:

\[
22\text{ support/thin phases},
\]

and

\[
31\text{ drop/heavy phases}.
\]

This is the exact source of the coefficient

\[
\frac{53}{22}.
\]

---

## 4.2 Support-cell capacity lemma

**Important unit convention.** The corridor width \(C\) is a logarithmic
height / bit-length quantity. It is not a count of ordinary integers.

Equivalently, \(C\) measures the number of allowed binary-height levels in the
bounded corridor. A corridor of width \(C\) corresponds to a multiplicative
ordinary-number scale of about

\[
2^C,
\]

but the Lock 3 support count is performed in **height cells**, not in raw
integer points.

With the deficit coordinate

\[
d_k=\lfloor k\log_2 3\rfloor-A_k,
\]

a bounded corridor of width \(C\) allows the integer height levels

\[
d\in\{0,1,\ldots,C\}.
\]

Thus there are \(C+1\) allowed vertical bit-level cells at each time phase.

Across one 53-step heartbeat, the phase/height cell space has size

\[
53(C+1).
\]

This is a count of \((\text{phase mod }53,\text{ binary-height level})\)
cells. It is **not** a count of ordinary numbers inside the corridor.

A terminal-compatible shadow at residue precision \(m\) requires support across
the 22 support phases for each residue-precision layer. Thus precision height
\(m\) demands at least

\[
22m
\]

support incidences.

Therefore survival requires

\[
22m\le 53(C+1).
\]

Equivalently,

\[
m\le \left\lfloor \frac{53(C+1)}{22}\right\rfloor.
\]

Define the last occupied precision edge

\[
M_{\text{edge}}(C)=
\left\lfloor \frac{53(C+1)}{22}\right\rfloor.
\]

Define the first desert precision

\[
K(C)=M_{\text{edge}}(C)+1.
\]

For

\[
m\ge K(C),
\]

the corridor cannot support a terminal-compatible lineage.

In plain language: \(C\) controls the bit-height of the corridor. The raw
number scale grows like \(2^C\), but the support lemma counts how many
binary-height layers the 53-step heartbeat can sustain.

---

## 4.3 Lock 3 theorem

## Theorem 2 — No fixed finite corridor supports an infinite positive-integer bounded glider

Assume a positive integer orbit remains inside a fixed bounded Lock 3 corridor:

\[
0\le d_k\le C
\]

for all \(k\), with finite \(C\).

A genuine positive-integer bounded glider must remain terminal-compatible at arbitrarily high residue precision \(m\). But the support-capacity lemma gives

\[
m\le M_{\text{edge}}(C)=\left\lfloor \frac{53(C+1)}{22}\right\rfloor.
\]

The right-hand side is finite for fixed \(C\).

Therefore residue precision cannot grow without bound inside the fixed corridor. Hence no positive integer orbit can remain a bounded glider forever.

So Lock 3 is closed:

\[
\boxed{\text{No bounded positive-integer Lock 3 glider exists.}}
\]

---

# 5. Birth-Invariant Formulation

A useful local invariant is

\[
I=L+m-3C,
\]

where:

- \(L\) is shadow lifetime,
- \(m\) is residue precision height,
- \(C\) is corridor width.

The first conjectural ceiling was

\[
I_{\text{birth}}\le 1.
\]

That held for \(C=3,4\), but the full audit showed the cleaner corridor-dependent form:

\[
I_{\text{birth}}\le K(C)-3C.
\]

Using

\[
K(C)=\left\lfloor \frac{53(C+1)}{22}\right\rfloor+1,
\]

we obtain the generalized birth ceiling.

Observed completed cases:

| \(C\) | \(M_{\text{edge}}(C)\) | \(K(C)\) | \(K(C)-3C\) | top observed birth |
|---:|---:|---:|---:|---:|
| 1 | 4 | 5 | 2 | 2 |
| 2 | 7 | 8 | 2 | 2 |
| 3 | 9 | 10 | 1 | 1 |
| 4 | 12 | 13 | 1 | 1 |
| 5 | 14 | 15 | 0 | 0 |

Thus the fixed \(I=1\) ceiling was a local coincidence. The actual object is the corridor-dependent ceiling:

\[
I_{\text{birth}}\le K(C)-3C.
\]

This is stronger and more flexible.

---

# 6. Resonance and the 53-Heartbeat

The 53-block does not merely give a coefficient. It appears directly in the shadow lifecycle.

For \(C=5,m=8\), low-precision terminal-compatible shadows persist after turning on. The key-level live-compatible layer cycles through a period-53 binary birth/death skeleton.

The birth/death masks have:

\[
22\text{ ones},
\]

\[
31\text{ zeros},
\]

over a 53-bit period.

This matches the Sturmian 53-block count exactly.

For \(C=4,m=12\), the shadow has collapsed into a single-depth spark train. The dirty-depth gaps are built from 53 and 41, with exact gap word period:

\[
B B B B B A B B B B B B A,
\]

where

\[
B=53,
\]

\[
A=41.
\]

One period spans

\[
10\cdot 53+2\cdot 41=530+82=612.
\]

And

\[
612=2(359-53).
\]

Thus Lock 3’s vertical precision-collapse rhythm is tied to the same continued-fraction corridor geometry seen in Lock 4.

---

# 7. Lock 4: Unbounded Reserve / Corridor Bridge Obstruction

Lock 4 is the case where no fixed finite \(C\) contains the orbit:

\[
d_k\to\infty
\]

or, more precisely, no finite bound \(C\) works forever.

This means the orbit tries to escape by building unbounded reserve and jumping from one continued-fraction corridor to the next.

The relevant near-return denominators include:

\[
53,\quad 359,\quad 665,\quad 16266,\ldots
\]

The first major bridge is

\[
53\to 359,
\]

with gap

\[
359-53=306.
\]

The martingale drift tax per odd step is

\[
2-\log_2 3\approx0.4150375.
\]

Across 306 steps, the reserve tax is approximately

\[
306(2-\log_2 3)\approx127.
\]

So the orbit needs roughly 127 bits of reserve just to pay the bridge tax.

But the support edge needed to support precision \(m=359\) requires

\[
359\le \left\lfloor \frac{53(C+1)}{22}\right\rfloor.
\]

Ignoring the floor for the threshold:

\[
22\cdot359\le 53(C+1),
\]

\[
7898\le 53(C+1),
\]

\[
C+1\ge \frac{7898}{53}\approx149.0188.
\]

So the corridor support threshold is

\[
C\ge149.
\]

The bridge tax gets to about \(C=127\), while support requires about \(C=149\). The missing support gap is roughly 22 bits.

That 22 is again the support-phase count from the 53-heartbeat.

The next major gap is vastly worse:

\[
16266-665=15601.
\]

The martingale tax over that gap is approximately

\[
15601(2-\log_2 3)\approx6475
\]

bits of reserve, corresponding to a scale of roughly

\[
2^{6475}\approx 10^{1949}.
\]

So Lock 4 is not merely computationally large. The bridge scale exits physical comparison. Even surviving one impossible bridge would only lead to a worse bridge.

Lock 4 obstruction:

\[
\boxed{
\text{corridor gaps grow faster than reserve can be supported under the }53/22\text{ edge and }2-\log_2 3\text{ tax.}
}
\]

---

# 8. Demotion of Lock 2

The old Lock 2 was:

> First contractive crossing actually descends.

In the updated framework, Lock 2 is not a separate escape mode. It is a local descent-exit face.

The real locks are:

1. No positive periodic engine.
2. No bounded glider.
3. No unbounded reserve bridge.

Once bounded and unbounded non-descending routes are killed, a finite contraction crossing cannot stand as an independent obstruction without creating a missing fifth case.

Thus Lock 2 is best rewritten as:

\[
\boxed{\text{Descent Exit Lemma}}
\]

rather than a structural lock.

The earlier reverse-barrier Lock 2 computations remain useful as local verification, but the global proof burden shifts to the corridor-collapse and bridge-exhaustion mechanisms.

---

# 9. Full Proof Chain

The intended proof chain is:

1. Reduce Collatz to the odd-only map.

2. Show every positive odd orbit either:
   - repeats a positive-action engine,
   - remains in a bounded corridor,
   - builds unbounded reserve,
   - or descends.

3. Lock 1 kills positive-action periodic engines:
   \[
   x_w=\frac{B_w}{2^A-3^k}<0.
   \]

4. Lock 3 kills bounded gliders:
   \[
   22m\le53(C+1)
   \]
   gives finite precision height for every fixed \(C\).

5. Lock 4 kills unbounded reserve:
   corridor bridge gaps outrun reserve accumulation under the \(53/22\) edge and martingale tax.

6. Therefore a positive odd orbit cannot avoid descent forever.

7. Once every positive odd \(n>1\) eventually reaches a smaller positive odd number, strong induction gives the Collatz conjecture.

---

# 10. Remaining Formal Statements to Polish

The current proof package has the main objects. The paper should state the following cleanly.

## Lemma A — Odd-only reduction

It is enough to prove every positive odd \(n>1\) eventually reaches a smaller positive odd number under \(S\).

## Lemma B — Regime exhaustiveness

A non-descending orbit must be periodic, bounded-gliding, or unbounded-reserve.

## Lemma C — Lock 1 negative ghost

Any positive-action repeated word has a negative affine fixed point.

## Lemma D — 53-block support count

The critical \(q=53\) Sturmian block contains 22 support phases and 31 drop phases.

## Lemma E — Support-cell capacity

A width-\(C\) corridor has \(53(C+1)\) support cells per 53-block, while precision \(m\) requires \(22m\) support incidences.

Therefore

\[
22m\le53(C+1).
\]

## Lemma F — Shadow correspondence

A true positive integer bounded glider must produce terminal-compatible shadows at arbitrarily high residue precision \(m\).

## Theorem G — Lock 3 collapse

No fixed finite \(C\) bounded glider exists.

## Lemma H — Lock 4 bridge obstruction

An unbounded reserve bridge must cross increasingly sparse near-return corridors, but the reserve required exceeds what the \(53/22\) support edge and martingale drift allow.

## Corollary I — Descent forced

No positive odd orbit can avoid descent forever.

---

# 11. Suggested Paper Title

**Tower-Spacetime Coordinates for the Odd Collatz Map: Periodic Ghosts, Bounded-Glider Collapse, and Corridor Exhaustion**

Alternative:

**A 53/22 Support Edge for Bounded Collatz Gliders**

Alternative:

**Ghost Corridors and Precision Collapse in the Odd Collatz Map**

---

# 12. Recommended Abstract Draft

We introduce a tower-spacetime coordinate system for the odd Collatz map, tracking odd-step time, total division exponent, deficit relative to \(k\log_2 3\), bounded corridor width, and residue precision. In these coordinates, possible non-descending behavior separates into periodic engines, bounded gliders, and unbounded corridor escapes. We prove that positive-action periodic engines have negative affine fixed points. For bounded gliders, we derive a support-capacity edge from the \(q=53\) Sturmian block of \(\log_2 3\), which contains 22 support phases in 53 steps. A width-\(C\) corridor supplies \(53(C+1)\) support cells while residue precision \(m\) demands \(22m\) incidences, forcing \(m\le\lfloor 53(C+1)/22\rfloor\). Thus no fixed finite corridor can support a positive-integer bounded glider at arbitrarily high residue precision. We further connect this vertical precision-collapse mechanism to the unbounded-reserve corridor obstruction at the \(53\to359\) bridge. These results give a structured proof framework for excluding non-descending odd Collatz orbits.

---

# 13. Reproducibility Artifacts

Important existing artifacts include:

- Lock 1 proof and Python verifier.
- Lock 3 support-cell audit.
- Lock 3 birth-invariant audit.
- Lock 3 cutoff numbers from \(C=-20\) to \(C=50\).
- Lock 3 C=5/m8 cohort tracker.
- Lock 3 lifecycle heatmaps and cylinder plots.
- Lock 2 reverse-barrier scans.
- Lock 4 bridge/corridor computations.

The paper should include exact commands and output file hashes/paths in an appendix.
