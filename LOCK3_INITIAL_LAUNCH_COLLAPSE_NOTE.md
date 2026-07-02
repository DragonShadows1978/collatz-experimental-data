# Lock 3 Initial-Launch Collapse Mechanism

Status: working proof-mechanism note.

Date: 2026-05-24

## Proof Position

This is not a brute-force search argument.

The goal is not to say:

```text
we have not searched far enough to find a counterexample
```

The goal is to identify the mathematical principle that explains why collapse
happens:

```text
forced division by 2 always dominates the apparent gain from 3x + 1
```

in the corridor reserve accounting.

The proof target is therefore structural:

```text
show why the launch gain cannot become durable reserve
```

instead of computational:

```text
search larger and larger number space
```

## Core Claim

In the Lock 3 corridor model, entry into the next corridor can only occur at
the initial launch.

The launch map is:

```text
L(x) = 3x + 1
```

This is a corridor-entry probe. It is not the ordinary step ordering of the
standard Collatz iteration, where an even integer would normally divide by 2
first. In this model, the question is whether the initial launch carrier can
immediately satisfy the next-corridor bridge condition.

If it cannot, the candidate collapses back into the controlled lower corridor.

## Even Carrier

The launched carrier is:

```text
E = 3x + 1
```

For ordinary odd Collatz inputs, `E` is even. In the corridor model, the
important object is this step-1 carrier, because it is the value that must
already have enough scale and residue compatibility to enter the next reserve
corridor.

The next-corridor condition is not just size. It is:

```text
E has enough magnitude
E has the correct residue/signature alignment
E survives the forced division tax
```

Equivalently, after normalization:

```text
E = 2^a y
```

the reduced value `y` must still lie inside the target corridor.

## Collapse Dichotomy

Every launch has two possible outcomes:

```text
L(x) satisfies the next-corridor bridge condition -> advance test continues
L(x) fails the bridge condition -> immediate collapse to lower controlled basin
```

The key Lock 3 claim is stronger:

```text
Even when L(x) appears to breach the corridor, the forced division tax strips
the launched carrier before it can become durable reserve.
```

So the launch must satisfy two constraints at once:

```text
1. Cross the next bridge threshold.
2. Remain above the corridor floor after mandatory /2 normalization.
```

Lock 3 says bounded corridor support cannot satisfy both requirements.

## Division-Tax Lemma

The tax mechanism is stronger than a local failed launch.

No matter how far the launch moves upward, the forced divide-by-2 loss is
larger than the multiply-by-3 gain in the corridor accounting.

In ordinary arithmetic, the odd lift creates:

```text
3x + 1
```

but the Collatz structure immediately forces:

```text
3x + 1 = 2^a y
```

for some `a >= 1`.

The Lock 3 tax claim is:

```text
division loss > launch gain
```

in the relevant corridor reserve metric.

So even a successful-looking upward launch does not create durable reserve. It
creates a carrier that must pay the division tax immediately, and that payment
drops the candidate below the level needed to persist in the next corridor.

This is why raw upward scale is not enough. The launched value must be high
enough to cross the bridge and still remain high enough after the mandatory
halving sequence. Lock 3 says the second requirement always fails for bounded
corridor support.

## Small Launch Examples

The small cases show the accounting rule clearly.

Starting from `7`:

```text
7 -> 22 -> 11
```

The raw launch appears to gain from `7` to `22`, but the forced division tax
immediately reduces the durable value to `11`.

So the effective gain is only:

```text
11 - 7 = 4
```

Starting from `6` under the forced-launch probe:

```text
6 -> 19 -> 58 -> 29 -> 88 -> 11
```

Step-by-step:

```text
3*6 + 1  = 19
3*19 + 1 = 58
58 / 2   = 29
3*29 + 1 = 88
88 / 8   = 11
```

The launches look large:

```text
6 -> 19
19 -> 58
29 -> 88
```

but the tax sequence collapses the carrier back to `11`.

So the net durable gain from the starting value is only:

```text
11 - 6 = 5
```

This illustrates the reserve-decay mechanism. Apparent launch height is not
the same as durable corridor support. The meaningful value is what survives
after the forced division tax.

The next chain from the surviving value `11` is dead-end behavior, not durable
reserve growth:

```text
11 -> 34 -> 17 -> 52 -> 13 -> 40 -> 5 -> 16 -> 1
```

The `6` forced-launch probe therefore does not create an escape route. It
lands at `11`, and `11` immediately belongs to a collapsing chain.

## Bridge Threshold

Let:

```text
B(q_i, q_{i+1})
```

be the minimum bridge threshold required to move from corridor `q_i` to the
next reserve corridor `q_{i+1}`.

Then the necessary condition for advancement is:

```text
3x + 1 >= B(q_i, q_{i+1})
```

but this is not sufficient. The normalized value must also survive:

```text
(3x + 1) / 2^a >= floor(q_{i+1})
```

with the correct residue/signature compatibility.

If either condition fails, the launch is transient and the orbit collapses back
under the active corridor floor.

## Corridor Scale Examples

The current corridor interpretation is:

```text
53 corridor      first reserve gate
359 corridor     requires roughly c=127 support, about 10^38-scale entry
665 corridor     requires at least about 10^83-scale entry
16266 corridor   requires about 10^1949-scale entry
```

These sizes are not being used as a brute-force argument. They are evidence of
the bridge-support explosion:

```text
next corridor requires vastly more support
forced division tax strips support immediately
bounded corridor lifetime decays before support can become durable
```

## Lock 3 / Lock 4 Link

Lock 4 describes the horizontal reserve-corridor ladder:

```text
53 -> 359 -> 665 -> 16266 -> ...
```

Lock 3 describes the vertical precision/lifetime collapse inside a bounded
corridor.

The combined obstruction is:

```text
To escape, an orbit must lift high enough to enter the next corridor and
persist long enough to bridge the next gap.

The only possible entry point is the initial launch.

But the initial launch immediately triggers the division tax.

That tax collapses bounded support before the next corridor can become durable.
```

## Compact Statement

A bounded-corridor escape requires a launched value that both crosses the next
bridge threshold and remains above that threshold after mandatory normalization.

Lock 3 asserts that no bounded support class can do this:

```text
launch below bridge -> immediate failure
launch across bridge -> division tax strips carrier below durable corridor floor
```

Therefore a bounded glide cannot become an infinite corridor escape.

## Formal Proof Obligations

The note above becomes a proof only after the following objects are formalized:

1. Define the corridor floor and bridge threshold `B(q_i, q_{i+1})`.
2. Prove that next-corridor entry can occur only through the initial launch
   carrier in the Lock 3 model.
3. Prove that failure of the bridge condition forces collapse into a controlled
   lower basin.
4. Prove the division-tax inequality:

```text
(3x + 1) / 2^a < durable floor(q_{i+1})
```

for every bounded support class that appears below the bridge threshold.

5. Connect the measured birth/decay cutoff:

```text
M_edge(C) = floor((53 / 22) * (C + 1))
```

to the bridge threshold inequality.
