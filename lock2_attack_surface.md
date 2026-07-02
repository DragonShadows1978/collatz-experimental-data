# Lock 2 Theoretical Attack Surface
## Contractive Corridor / Minimal-Residue Descent

**Date:** 2026-05-21  
**Context:** Four-lock Collatz tower-spacetime framework  
**Lock:** Lock 2 — finite contractive symbolic corridors

---

## 0. Executive Summary

Lock 2 is the finite-symbolic part of the Collatz decomposition.

It concerns finite odd-only Collatz exponent words

\[
w=(a_0,a_1,\dots,a_{k-1})
\]

with total division

\[
A=\sum_{i=0}^{k-1} a_i.
\]

The \(k\)-step odd-only map has the affine form

\[
S^k(x)=\frac{3^k x+B_w}{2^A}.
\]

When

\[
2^A>3^k,
\]

the word is **contractive** in multiplier.

The descent threshold is

\[
\Theta_w=\frac{B_w}{2^A-3^k}.
\]

Let \(\rho_w\) be the smallest positive odd integer realizing the word \(w\). The Lock 2 conjecture is:

\[
\boxed{
w\ne(2,2,\dots,2),\quad 2^A>3^k
\implies
\rho_w>\Theta_w.
}
\]

Equivalently:

\[
\boxed{
S^k(\rho_w)<\rho_w.
}
\]

Equivalently:

\[
\boxed{
(2^A-3^k)\rho_w>B_w.
}
\]

If Lock 2 is proved, every orbit that ever crosses the contraction line

\[
A_k>k\log_2 3
\]

must descend below its starting value after that finite prefix. That would eliminate all counterexamples that ever become contractive and leave only the bounded/unbounded noncontractive locks.

---

## 1. Background: Odd-Only Collatz Map

Use the odd-only map

\[
S(x)=\frac{3x+1}{2^{v_2(3x+1)}}
\]

on positive odd integers.

For a finite exponent word

\[
w=(a_0,\ldots,a_{k-1}),
\]

the orbit follows

\[
x_{i+1}=\frac{3x_i+1}{2^{a_i}},
\qquad
a_i=v_2(3x_i+1).
\]

Define

\[
A_j=a_0+\cdots+a_{j-1},
\qquad A_0=0,
\]

and

\[
A=A_k.
\]

Then the affine formula is

\[
S^k(x)=\frac{3^k x+B_w}{2^A},
\]

where

\[
B_w=\sum_{j=0}^{k-1}3^{k-1-j}2^{A_j}.
\]

Examples:

- \(w=(2)\):
  \[
  S(x)=\frac{3x+1}{4},\quad B=1,\quad A=2.
  \]

- \(w=(2,2,\dots,2)\):
  \[
  S^k(x)=\frac{3^k x+B}{4^k}.
  \]
  This word is realized by \(x=1\), the trivial odd-only fixed point.

---

## 2. Contractive Words

A word is contractive when

\[
2^A>3^k.
\]

Then

\[
S^k(x)<x
\]

is equivalent to

\[
\frac{3^k x+B_w}{2^A}<x,
\]

so

\[
B_w<(2^A-3^k)x.
\]

Thus descent occurs exactly when

\[
x>\Theta_w,
\]

where

\[
\Theta_w=\frac{B_w}{2^A-3^k}.
\]

So if the smallest positive representative \(\rho_w\) satisfies

\[
\rho_w>\Theta_w,
\]

then every positive integer realizing the word descends, because every such integer is congruent to \(\rho_w\) modulo a positive power of two and is at least \(\rho_w\).

---

## 3. Residue Class of a Word

Every finite exponent word \(w\) corresponds to exactly one odd residue class modulo

\[
2^{A+1}.
\]

Call the smallest positive representative of that class

\[
\rho_w.
\]

Thus every positive odd integer following \(w\) has the form

\[
x=\rho_w+t2^{A+1}
\]

for \(t\ge0\).

The exact congruence for \(\rho_w\) is:

\[
3^k \rho_w+B_w\equiv 2^A \pmod{2^{A+1}}.
\]

Why \(2^A\) rather than \(0\)? Because after dividing by \(2^A\), the resulting value must be odd:

\[
3^k x+B_w = 2^A y,
\qquad y\equiv1\pmod2.
\]

So modulo \(2^{A+1}\),

\[
3^k x+B_w\equiv 2^A.
\]

Since \(3^k\) is invertible modulo \(2^{A+1}\), this uniquely determines \(\rho_w\).

---

## 4. Lock 2 Main Conjecture

### Minimal-Residue Descent Conjecture

For every finite exponent word \(w\) with total division \(A\) and length \(k\),

\[
2^A>3^k,
\]

and \(w\ne(2,2,\dots,2)\), one has

\[
\boxed{
\rho_w>\frac{B_w}{2^A-3^k}.
}
\]

Equivalently,

\[
\boxed{
(2^A-3^k)\rho_w-B_w>0.
}
\]

Define the **Lock 2 margin**

\[
M_w=(2^A-3^k)\rho_w-B_w.
\]

Then the conjecture is:

\[
\boxed{M_w>0}
\]

for all nontrivial contractive words, with

\[
M_w=0
\]

only for the all-\(2\) word.

For \(w=(2,2,\dots,2)\), the trivial fixed point \(x=1\) gives equality:

\[
\rho_w=\Theta_w=1.
\]

---

## 5. Why Lock 2 Matters

Suppose an odd positive integer orbit has prefix word \(w_k\) with

\[
A_k>k\log_2 3.
\]

Then

\[
2^{A_k}>3^k,
\]

so \(w_k\) is contractive.

If Lock 2 holds, then the smallest positive representative of that prefix descends. Therefore every positive integer following that prefix descends below its starting value after \(k\) odd steps.

Thus:

\[
\boxed{
\text{crossing the contraction line forces descent.}
}
\]

This leaves only orbits satisfying

\[
A_k\le k\log_2 3
\]

for all \(k\). Those are precisely the Lock 3 and Lock 4 cases.

---

## 6. Equivalent Forms of Lock 2

### 6.1 Threshold Form

\[
\rho_w>\Theta_w.
\]

### 6.2 Margin Form

\[
M_w=(2^A-3^k)\rho_w-B_w>0.
\]

### 6.3 Descent Form

\[
S^k(\rho_w)<\rho_w.
\]

### 6.4 No Bad Contractive Corridor Form

There is no nontrivial contractive symbolic corridor whose smallest positive representative fails to descend.

### 6.5 Modular Inequality Form

Let \(\rho\) be the unique odd integer satisfying

\[
3^k\rho+B_w\equiv2^A\pmod{2^{A+1}},
\qquad
1\le\rho<2^{A+1}.
\]

Then, except for \(w=(2,\dots,2)\),

\[
(2^A-3^k)\rho>B_w.
\]

This is purely finite arithmetic.

---

## 7. Attack Surface A: Exhaustive Margin Scan

### Goal

Enumerate all exponent words up to a total division bound \(A_{\max}\), compute \(M_w\), and classify near-failures.

### Outputs Needed

For every contractive word:

- word \(w\)
- length \(k\)
- total division \(A\)
- \(B_w\)
- \(\rho_w\)
- \(\Theta_w\)
- margin \(M_w\)
- normalized margin
- distance from all-\(2\) word
- run structure
- prefix/suffix structure
- whether word is primitive or repetition

### Key Diagnostics

1. Is \(M_w=0\) only for \(w=(2,\dots,2)\)?
2. What is the smallest positive margin?
3. Which word families minimize the margin?
4. Do near-failures cluster near all-\(2\) words?
5. Do near-failures correspond to periodic ghost words?
6. Does normalized margin grow with deviation from all-\(2\)?

### Suggested Normalizations

Raw margin:

\[
M_w=(2^A-3^k)\rho_w-B_w.
\]

Threshold gap:

\[
G_w=\rho_w-\Theta_w.
\]

Relative gap:

\[
R_w=\frac{\rho_w-\Theta_w}{\rho_w}.
\]

Denominator-normalized margin:

\[
\widetilde M_w=\frac{M_w}{2^A-3^k}.
\]

Word-length-normalized log margin:

\[
\log_2(M_w+1)/k.
\]

---

## 8. Attack Surface B: Near-Failure Classification

If Lock 2 is true, the proof likely lives in the near-failure cases.

Near-failure means \(M_w\) is small relative to natural scale.

Possible classifiers:

### 8.1 Distance from All-2 Word

Let

\[
\Delta_2(w)=\sum_i |a_i-2|.
\]

Check whether small margins correspond to small \(\Delta_2\).

### 8.2 Excess Division

Define

\[
E=A-2k.
\]

The all-\(2\) word has \(E=0\).

Words with \(E>0\) are more contractive than all-\(2\).  
Words with \(E<0\) can still be contractive if \(A>k\log_2 3\), but less than \(2k\).

### 8.3 Run Structure

Track:

- number of \(1\)'s
- number of \(2\)'s
- number of \(a_i\ge3\)
- longest run of \(1\)'s
- longest run of \(2\)'s
- longest run of high exponents
- pattern repetitions

### 8.4 Prefix Contractivity

Does the full word become contractive only at the end, or earlier?

Define first contractive prefix:

\[
k_* = \min\{j:A_j>j\log_2 3\}.
\]

Near-failures may correspond to words that barely become contractive.

### 8.5 Primitive Periodic Structure

A word may be a repetition:

\[
w=u^m.
\]

Since periodic positive-action engines have ghost fixed points, repeated patterns may explain small margins.

---

## 9. Attack Surface C: Algebraic Proof via Modular Lift

The unique residue is

\[
\rho_w\equiv
(2^A-B_w)(3^k)^{-1}
\pmod{2^{A+1}}.
\]

The desired inequality is:

\[
(2^A-3^k)\rho_w>B_w.
\]

This suggests an approach through 2-adic expansions:

\[
(3^k)^{-1}\in\mathbb Z_2.
\]

Then \(\rho_w\) is the finite truncation of a 2-adic number modulo \(2^{A+1}\).

A possible proof strategy:

1. Express \(\rho_w\) as a finite binary truncation.
2. Express \(\Theta_w\) as a real threshold.
3. Show the truncation exceeds the threshold unless the 2-adic point is exactly \(1\).

This is a real/2-adic comparison problem.

---

## 10. Attack Surface D: Backward Tree Interpretation

The word \(w\) can be realized by running inverse odd-only Collatz branches.

From

\[
x_{i+1}=\frac{3x_i+1}{2^{a_i}},
\]

we have

\[
x_i=\frac{2^{a_i}x_{i+1}-1}{3}.
\]

A word is valid for a starting integer only if these inverse steps remain integral.

For the smallest residue \(\rho_w\), one can think of choosing the smallest terminal odd value \(y\) such that repeated inverse branches produce a positive integer.

Potential proof idea:

- Contractive words imply the inverse branches expand more slowly than the forward threshold.
- The minimal valid backward lift must overshoot the fixed threshold.
- Equality occurs only when the branch is stationary at \(1\), i.e. all \(a_i=2\).

This may connect to monotonicity of inverse branches.

---

## 11. Attack Surface E: Fixed-Point / Ghost Interpretation

For a contractive word

\[
2^A>3^k,
\]

the affine map

\[
F_w(x)=\frac{3^k x+B_w}{2^A}
\]

has positive fixed point

\[
\Theta_w=\frac{B_w}{2^A-3^k}.
\]

Thus \(\Theta_w\) is the real attracting fixed point of the finite word.

Lock 2 says:

\[
\boxed{
\text{the smallest positive integer in the corridor lies above the attracting fixed point.}
}
\]

So after applying the word, it moves downward.

This gives a clean dynamical interpretation:

- Contractive corridors have real attracting fixed points.
- If a positive integer corridor had \(\rho_w\le\Theta_w\), it would start below or at the fixed point.
- The all-\(2\) word has fixed point \(1\), and \(\rho=1\).
- Nontrivial words appear to have their smallest positive representative strictly above the fixed point.

Possible theorem:

> No nontrivial contractive word has a positive integer representative below its real attracting fixed point.

This may be easier to communicate.

---

## 12. Attack Surface F: Prefix Decomposition

Let \(w=uv\), with \(u\) a prefix and \(v\) suffix.

The affine maps compose:

\[
F_w=F_v\circ F_u.
\]

If both \(u\) and \(v\) are contractive, Lock 2 may follow inductively.

But the hard case is when \(w\) is first contractive only at the full length.

Define the first-contractivity index:

\[
k_* = \min\{j:A_j>j\log_2 3\}.
\]

Potential induction:

1. Prove Lock 2 for first-contractivity words.
2. Show any later contractive word inherits descent from the first contractive prefix.

If a prefix is already contractive and descends, the whole word is unnecessary. Therefore the minimal counterexample to Lock 2 must be **first-contractivity**:

\[
A_j\le j\log_2 3\quad\forall j<k,
\]

but

\[
A_k>k\log_2 3.
\]

This is a major reduction.

---

## 13. Attack Surface G: Deficit Bankruptcy Form

Define

\[
d_j=\lfloor j\log_2 3\rfloor-A_j.
\]

A word becomes contractive when

\[
A_j>j\log_2 3.
\]

Lock 2 says:

\[
\boxed{
\text{the first bankruptcy event forces descent below the original integer.}
}
\]

This connects the four-lock framework:

- Lock 3: bounded nonnegative deficit forever.
- Lock 4: unbounded nonnegative deficit forever.
- Lock 2: first deficit bankruptcy forces descent.

Potential theorem:

> If a finite word is solvent for all proper prefixes and bankrupt at the final prefix, then the smallest positive representative descends.

This may be the most natural version for integration with Lock 3/4.

---

## 14. Attack Surface H: Minimal Counterexample to Lock 2

Assume Lock 2 fails.

Then there exists a nontrivial contractive word \(w\) such that

\[
\rho_w\le\Theta_w.
\]

Choose such a word with minimal length \(k\), then minimal total \(A\).

Properties of a minimal counterexample:

1. No proper prefix is contractive and descending.
2. Likely first-contractivity at final step.
3. The word is not all-\(2\).
4. \(\rho_w\) is the smallest residue in its class.
5. \(F_w(\rho_w)\ge\rho_w\), despite \(F_w\) being contractive.
6. Since \(F_w\) is increasing with slope \(3^k/2^A<1\), this implies \(\rho_w\le\Theta_w\).

Because \(F_w\) is contractive, repeated application of \(F_w\) would converge to \(\Theta_w\). But applying the same word repeatedly requires the orbit to remain in the same symbolic corridor, which would imply a periodic or eventually periodic symbolic engine.

This suggests a contradiction with the periodic ghost theorem.

Potential proof sketch:

- If \(\rho_w\le\Theta_w\), then \(F_w(\rho_w)\ge\rho_w\).
- Since \(F_w(\rho_w)\) is an odd integer realizing the shifted state after word \(w\), ask whether it can realize \(w\) again.
- If yes, repeated \(w\) gives a nontrivial cycle/engine.
- If no, the next word changes. Need show that change creates an earlier descent.

This is not complete, but it links Lock 2 failures to periodic/eventual symbolic behavior.

---

## 15. Attack Surface I: All-2 Perturbation

The all-\(2\) word is the equality case:

\[
w_0=(2,2,\dots,2).
\]

It has:

\[
\rho=1,\qquad\Theta=1,\qquad M=0.
\]

Perturb by changing one exponent.

Questions:

1. If one \(2\) becomes \(1\), the word is less contractive. Is it still contractive?
2. If one \(2\) becomes \(3\), the word is more contractive. Does margin become positive immediately?
3. Can any combination of \(1\)'s and \(3\)'s keep margin small?
4. Does the margin decompose into positive contributions from deviations?

For all-\(2\):

\[
A_j=2j,
\]

\[
B_0=\sum_{j=0}^{k-1}3^{k-1-j}4^j
=4^k-3^k.
\]

Then

\[
\Theta_0=\frac{4^k-3^k}{4^k-3^k}=1.
\]

For general \(w\), compare \(B_w\) to \(2^A-3^k\).

The all-\(2\) equality is exactly

\[
B=2^A-3^k.
\]

Since \(\rho_w\) is odd, nontrivial words may have \(\rho_w\ge3\). If one can bound

\[
\Theta_w<3
\]

for a class, Lock 2 follows immediately.

More generally, threshold buckets can reduce the problem to ruling out finitely many small representatives.

---

## 16. Attack Surface J: Threshold Bucket Elimination

Since \(\rho_w\) is a positive odd integer, Lock 2 fails only if

\[
\rho_w\le\Theta_w.
\]

Thus if

\[
2m-1\le\Theta_w<2m+1,
\]

then a failure requires

\[
\rho_w\in\{1,3,\ldots,2m-1\}.
\]

For each small odd candidate \(r\), ask whether \(r\) realizes word \(w\). This is equivalent to checking the exponent sequence of \(r\).

Potential approach:

1. Bound \(\Theta_w\) for most words below a small value.
2. For the remaining small candidates, prove incompatible with the word except all-\(2\).

This may be powerful if empirical near-failures have small thresholds.

---

## 17. Attack Surface K: Candidate Small Representatives

For any word \(w\), a Lock 2 failure requires:

\[
\rho_w\le\Theta_w.
\]

But \(\rho_w\) is the smallest integer realizing \(w\).

So for a fixed small \(r\), the only word \(w\) with \(\rho_w=r\) must be a prefix of the actual Collatz exponent sequence of \(r\).

This suggests a hybrid proof:

1. Show any failure must have \(\rho_w\le R(A,k)\) with modest \(R\).
2. Verify all possible small \(\rho\) cannot produce a failure except \(1\).

This may not close fully but can eliminate large regions.

---

## 18. Attack Surface L: Random / Measure Heuristic

Under the natural 2-adic distribution, exponent words have probability

\[
\Pr(w)=2^{-A}.
\]

There are

\[
\binom{A-1}{k-1}
\]

words of length \(k\) and total \(A\).

For a random word with given \(A,k\), the residue \(\rho_w\) is heuristically uniform among odd residues modulo \(2^{A+1}\).

If so, the probability of failure is roughly

\[
\Pr(\rho_w\le\Theta_w)\approx \frac{\Theta_w}{2^A}.
\]

If typical \(\Theta_w\) is much smaller than \(2^A\), failures are rare.

This is not proof, but it guides computational search: failures should occur only in structured non-random words, likely near all-\(2\).

---

## 19. Attack Surface M: SAT/SMT Encoding

Lock 2 failure can be encoded as finite constraints:

Variables:

- \(a_i\)
- prefix sums \(A_i\)
- \(B_w\)
- \(\rho\)
- integer quotient \(m\) for congruence

Constraints:

\[
A=\sum a_i,
\]

\[
2^A>3^k,
\]

\[
3^k\rho+B_w=2^A+m2^{A+1},
\]

\[
1\le\rho<2^{A+1},
\]

\[
\rho\text{ odd},
\]

\[
(2^A-3^k)\rho\le B_w,
\]

\[
w\ne(2,\dots,2).
\]

For bounded \(A\), use exact integer arithmetic and SMT solving to search for a model.

This can independently validate enumeration.

---

## 20. Attack Surface N: Proof Assistant Target

If a proof emerges, the finite statement is Lean/Coq-friendly.

Definitions:

- finite list of positive integers \(w\)
- prefix sums
- \(B_w\)
- residue \(\rho_w\)
- contractive predicate
- all-\(2\) predicate
- margin

Main theorem shape:

```lean
theorem lock2_minimal_residue_descent
  (w : List Nat)
  (hpos : all entries positive)
  (hcontract : 2^(sum w) > 3^(length w))
  (hnontrivial : w ≠ replicate (length w) 2) :
  margin w > 0
```

The hard proof is mathematical, but the statement is crisp.

---

## 21. Recommended Codex Work Packages

### Package 1: Exhaustive Lock 2 Scan

Script:

```bash
python -m collatz_experimental_data lock2-scan --Amax 40
```

Outputs:

- `lock2_words_Amax40.csv`
- `lock2_near_failures_Amax40.csv`
- `lock2_summary_Amax40.json`

Columns:

- `word`
- `k`
- `A`
- `B`
- `rho`
- `theta_num`
- `theta_den`
- `margin`
- `normalized_margin`
- `is_all_twos`
- `first_contractivity_index`
- `delta_from_all_twos`
- `max_run_1`
- `max_run_2`
- `max_run_ge3`

### Package 2: Near-Failure Classifier

Input:

- near-failures from Package 1.

Outputs:

- family clustering
- repeated patterns
- perturbation distance
- threshold buckets
- representative candidates

### Package 3: First-Contractivity Reduction

Scan only words where:

\[
A_j\le j\log_2 3\quad\forall j<k
\]

and

\[
A_k>k\log_2 3.
\]

Compare margins to all contractive words.

### Package 4: Threshold Bucket Analysis

For each contractive word, compute \(\Theta_w\) and bucket by odd intervals:

\[
[1,3),[3,5),[5,7),\ldots
\]

Find whether failures could only occur with small \(\rho\).

### Package 5: Symbolic Perturbation Around All-2

Generate words of fixed deviation

\[
\Delta_2(w)=r
\]

and fit/prove lower bounds for margin as function of \(r\).

---

## 22. Pseudocode for Exhaustive Scan

```python
from math import log2


def words_with_total_A(A):
    # Generate compositions of A into positive parts.
    def rec(rem, prefix):
        if rem == 0:
            yield tuple(prefix)
            return
        for a in range(1, rem + 1):
            prefix.append(a)
            yield from rec(rem - a, prefix)
            prefix.pop()
    yield from rec(A, [])


def prefix_sums(word):
    out = [0]
    s = 0
    for a in word:
        s += a
        out.append(s)
    return out


def B_of_word(word):
    k = len(word)
    A_prefix = prefix_sums(word)
    B = 0
    for j in range(k):
        B += (3 ** (k - 1 - j)) * (2 ** A_prefix[j])
    return B


def rho_of_word(word):
    k = len(word)
    A = sum(word)
    B = B_of_word(word)
    mod = 2 ** (A + 1)
    inv = pow(3 ** k, -1, mod)
    rho = ((2 ** A - B) * inv) % mod
    if rho == 0:
        rho = mod
    return rho


def is_all_twos(word):
    return all(a == 2 for a in word)


def first_contractivity_index(word):
    A = 0
    alpha = log2(3)
    for i, a in enumerate(word, start=1):
        A += a
        if A > i * alpha:
            return i
    return None


def scan_lock2(Amax):
    rows = []
    for A in range(1, Amax + 1):
        for word in words_with_total_A(A):
            k = len(word)
            if 2 ** A <= 3 ** k:
                continue

            B = B_of_word(word)
            rho = rho_of_word(word)
            den = 2 ** A - 3 ** k
            margin = den * rho - B

            rows.append({
                "word": word,
                "k": k,
                "A": A,
                "B": B,
                "rho": rho,
                "theta_num": B,
                "theta_den": den,
                "margin": margin,
                "is_all_twos": is_all_twos(word),
                "first_contractivity_index": first_contractivity_index(word),
                "delta_from_all_twos": sum(abs(a - 2) for a in word),
            })

    return rows
```

---

## 23. Pseudocode for Near-Failure Report

```python
def near_failure_report(rows, top_n=100):
    nontrivial = [r for r in rows if not r["is_all_twos"]]
    nontrivial.sort(key=lambda r: r["margin"])

    print("Top near-failures:")
    for r in nontrivial[:top_n]:
        print({
            "word": r["word"],
            "k": r["k"],
            "A": r["A"],
            "rho": r["rho"],
            "margin": r["margin"],
            "theta": r["theta_num"] / r["theta_den"],
            "delta_from_all_twos": r["delta_from_all_twos"],
            "first_contractivity_index": r["first_contractivity_index"],
        })

    zeros = [r for r in rows if r["margin"] == 0]
    print("zero margins:", zeros)

    negatives = [r for r in rows if r["margin"] < 0]
    print("negative margins:", negatives)
```

---

## 24. Expected Outcomes

### If Lock 2 is true

Expected scan results:

- no negative margins;
- zero margins only for all-\(2\);
- near-failures clustered around all-\(2\);
- first-contractivity cases contain the hardest examples;
- normalized margin has simple lower bound in terms of deviation from all-\(2\).

### If Lock 2 is false

A counterexample word gives a finite obstruction.

Then:

- compute its smallest representative \(\rho\);
- verify actual orbit;
- inspect whether it creates a nontrivial cycle or non-descending contractive prefix;
- this would significantly alter the four-lock decomposition.

Either way, Lock 2 is productive.

---

## 25. Main Theorem Candidates

### Theorem Candidate 1: Minimal-Residue Descent

\[
w\ne(2,\dots,2),\quad2^A>3^k
\implies
(2^A-3^k)\rho_w>B_w.
\]

### Theorem Candidate 2: First-Contractivity Descent

If \(w\) first becomes contractive at its final step, then

\[
M_w>0
\]

except all-\(2\).

Then general Lock 2 follows by prefix reduction.

### Theorem Candidate 3: Threshold Bucket Bound

For every nontrivial contractive word,

\[
\Theta_w<\rho_w.
\]

Prove by showing \(\Theta_w\) lies below the first possible odd residue in its residue class.

### Theorem Candidate 4: All-2 Stability

The all-\(2\) word is the unique equality case, and any finite perturbation creates strictly positive margin.

### Theorem Candidate 5: No Contractive Corridor Below Fixed Point

No nontrivial contractive symbolic corridor contains a positive integer at or below its real attracting fixed point.

---

## 26. Relationship to Other Locks

- Lock 1 / periodic ghost theorem handles periodic positive-action engines.
- Lock 2 handles first contraction-line crossing.
- Lock 3 handles bounded nonnegative deficit forever.
- Lock 4 handles unbounded nonnegative deficit forever.

If Lock 2 is proven, then any counterexample must never cross the contraction line.

So Lock 2 is the gate that converts a symbolic crossing into actual descent.

---

## 27. Recommended Next Step

Start with computation, not proof.

Run exhaustive Lock 2 scans with:

\[
A_{\max}=30,40,50
\]

if feasible.

Then inspect:

1. smallest nontrivial margins;
2. zero margins;
3. near-failure families;
4. first-contractivity subset;
5. threshold bucket distribution.

The proof should be guided by the shape of the near-failures.

The likely path is:

\[
\boxed{
\text{enumeration}
\to
\text{near-failure classification}
\to
\text{all-2 perturbation lemma}
\to
\text{first-contractivity reduction}
\to
\text{Lock 2 proof.}
}
\]

---

## 28. Short Version

Lock 2 is the finite theorem:

\[
\boxed{
\text{Every nontrivial contractive exponent word forces descent from its smallest positive representative.}
}
\]

It is equivalent to the modular inequality:

\[
\boxed{
(2^A-3^k)\rho_w>B_w.
}
\]

This is finite, exact, computable, and probably the best next proof target.
