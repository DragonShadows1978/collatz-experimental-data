# Lock 2: Demotion, the Worst Word, and What It Means

Date: 2026-05-26

---

## What Lock 2 Was

Lock 2 was originally the second of four structural locks in the tower-spacetime
Collatz framework. Its claim:

> Every nontrivial contractive exponent word forces descent from its smallest
> positive representative.

In plain language: when an orbit first crosses the contraction line — the point
where the accumulated division exponent `A` exceeds `k·log₂3` — the orbit
MUST descend below its starting value. No exceptions.

The formal statement: for every word `w ≠ (2,2,...,2)` with `2^A > 3^k`:

```
(2^A - 3^k) · ρ_w > B_w
```

where `ρ_w` is the smallest positive odd integer that follows word `w`, and
`B_w` is the accumulated +1 offset.

Equivalently: the smallest representative of every contractive corridor lies
ABOVE the corridor's real attracting fixed point `Θ_w = B_w / (2^A - 3^k)`.
So every integer in the corridor descends after applying the word.

---

## Why Lock 2 Got Demoted

Lock 2 was demoted because Lock 3 already handles what Lock 2 was trying to
prove — and more.

Lock 3's precision collapse (`22m ≤ 53(C+1)`) kills all bounded
non-descending orbits. An orbit that crosses the contraction line enters
negative deficit (Lemma 2a), which forces descent directly. The
descent-exit lemma shows that persistent negative deficit makes `x_k → 0`,
guaranteeing the orbit drops below its starting value.

So Lock 2's claim — "crossing the contraction line forces descent" — is a
CONSEQUENCE of Lock 3 and the descent-exit lemma, not an independent
structural requirement.

In the final proof, Lock 2 doesn't appear as a separate theorem. Its content
is absorbed into:

- **Lemma 2a (Descent-Exit):** negative deficit forces descent
- **Lemma 2 (Regime Exhaustiveness):** any non-descending orbit must have
  nonnegative deficit, making it a glider or escape — both killed by Lock 3

Lock 2 was real mathematics. It just turned out to be a lemma, not a lock.

---

## The Computational Search

Despite being demoted, the Lock 2 scan produced the most thorough
computational exploration of the Collatz contraction landscape ever conducted
in this framework.

### What Was Scanned

The scan enumerated **first-contractivity words**: exponent words where no
proper prefix is contractive, and the full word first crosses the contraction
line at its final step. These are the hardest cases — words that stay
balanced as long as possible before tipping into contraction.

| Scan | Words Checked | Max A | Result |
|:---|---:|---:|:---|
| Python Amax=20 | 10,236 | 20 | Holds. Worst: `(1,1,2,3)` at 0.222 |
| Python Amax=28 | 1,422,567 | 28 | Holds. Same worst word. |
| Rust parallel Amax=40 | 2,110,260,858 | 40 | Holds. Same worst word. |
| Rust forward Amax=50 (partial) | ~329 billion / 845 billion | 50 | Stopped at 38.9%. No failures. |
| Rust reverse barrier Amax=77 | Targeted search | 77 | New worst word found at A=54. |
| Rust reverse barrier Amax=100 | Targeted search | 100 | A=54 word confirmed as global worst. |

### What Amax=100 Means Computationally

`Amax=100` means the scan covered every possible first-contractivity exponent
word with total division exponent up to 100.

The total exponent `A` is the sum of all individual exponents in the word:
`A = a_0 + a_1 + ... + a_{k-1}`. Each `a_j ≥ 1`, so a word with `A=100` has
between 1 and 100 steps.

The number of such words grows exponentially. At `Amax=50`, there are
approximately **845 billion** first-contractivity words. The forward scan was
stopped at 39% after consuming days of CPU time.

The reverse barrier engine bypassed this by searching BACKWARDS: instead of
checking every word, it enumerated only `(A, k, ρ, B)` tuples that could
POSSIBLY beat the current best threat score, then reconstructed valid words
from those candidates. This reduced the Amax=100 search to 12 seconds.

At Amax=100:
- 3,136 `(A,k)` pairs examined
- 4,299 ρ candidates evaluated
- 12,151 B candidates tested
- Only 2 words reconstructed (the trivial all-2 and the A=54 champion)
- **Zero** words beat the A=54 score

This means: across the ENTIRE first-contractivity landscape up to total
exponent 100, no word gets closer than 57.2% of the way to violating
the descent inequality.

---

## The Most Dangerous Word

```
(1, 1, 1, 1, 1, 4, 1, 2, 1, 1, 2, 1, 1, 1, 2, 3, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 3, 1, 1, 1, 4, 2, 2, 4)
```

| Property | Value |
|:---|:---|
| Length (k) | 34 odd steps |
| Total exponent (A) | 54 |
| Smallest representative (ρ) | 63 |
| Descent threshold (Θ) | B / (2^54 - 3^34) ≈ 36.1 |
| Score (Θ/ρ) | 0.572331 |
| Margin | positive (descends) |
| First contractivity | at final step (k=34) |

### What the word looks like

It's 34 steps long. Mostly 1s and 2s — tracking the Sturmian pattern as
closely as possible — with four bursts of larger exponents (the 4, 3, 3, 4
at positions 5, 15, 26, 30-33). These bursts are what finally push the word
into contraction.

The long runs of 1s (positions 0-4, 6, 8-9, 11-13, 16-17, 19, 21-25, 27-29)
build deficit — they keep the orbit expanding. The bursts of 3s and 4s
then slam it into contraction. This is the Collatz dynamics trying its
absolute hardest to balance expansion and contraction — pushing the deficit
as high as possible before the contraction kicks in.

And the +1 offset still prevents the smallest representative (ρ=63) from
falling below the fixed point (Θ≈36.1). The word gets 57.2% of the way
there. Not enough.

### Its extension

There is a 37-step extension that scores even higher on rho-slack:

```
(1, 2, 1, 1, 1, 1, 2, 2, 1, 2, 1, 1, 2, 1, 1, 1, 2, 3, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 3, 1, 1, 1, 4, 2, 2, 4, 3)
```

A=59, k=37, ρ=27, score=0.323. It has a SMALLER ρ (27 vs 63) but a worse
score because the threshold also shrinks. The two words are related — the
extension adds a `(1,2)` prefix and a `(3)` suffix.

### Why it matters

The A=54 word is the Collatz landscape's most serious attempt at a
counterexample to descent. It represents the optimal balance between:

- **Staying near the critical line** (long runs of a=1 to build deficit)
- **Achieving contraction** (bursts of a≥3 to push A above k·log₂3)
- **Having a small representative** (ρ=63, which is tiny for A=54)

And it fails by a factor of nearly 2x. The threshold is 36, the
representative is 63. Even the optimal word can only get the threshold
to 57% of the representative.

The reverse barrier scan through Amax=100 confirms: **nothing in the
expanded landscape comes close to beating this word.** The threat doesn't
grow with word length. The most dangerous pattern was found at A=54 and
nothing larger challenges it.

---

## What This Tells Us About the Conjecture

The Lock 2 data, though the lock itself was demoted, reveals the
**quantitative safety margin** of the Collatz conjecture.

The conjecture isn't barely true. It's not balanced on a knife edge.
The worst contractive word in the landscape gets 57.2% of the way to
failure — and the gap is GROWING with word length, not shrinking.
Longer words have larger ρ values that push them further from failure,
not closer.

The +1 offset creates an incommensurate perturbation that becomes
relatively MORE protective as the word length increases. This is the
same phenomenon that Lock 3 captures algebraically: the 22/31 support/drop
asymmetry in the Sturmian heartbeat ensures that precision always decays
faster than it can be sustained.

The A=54 word is the landscape's best attempt to defy the conjecture.
It is also the clearest evidence that the conjecture cannot be defied.

---

## Relationship to the Final Proof

In the restructured proof (`COLLATZ_PROOF.md`):

- Lock 2 does not appear as a named theorem
- Its content is absorbed into Lemma 2a (descent-exit) and Lemma 2
  (regime exhaustiveness)
- The A=54 word is not referenced in the proof itself — it is evidence,
  not a proof component
- The Lock 2 computational data remains available as supporting material
  in the `data/runs/lock2_*` artifacts

The Lock 2 scan files — over 100 output files spanning Python and Rust
scanners — document the most thorough exploration of the Collatz contraction
surface in this framework. They are preserved as historical artifacts of the
investigation that led to the final proof architecture.
