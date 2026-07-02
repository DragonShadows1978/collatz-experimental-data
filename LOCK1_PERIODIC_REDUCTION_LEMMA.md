# Lock 1 Periodic Reduction Lemma

Date: 2026-05-25

## Claim

No imprimitive exponent word can be the first nontrivial Lock 1 loop.

If a loop word is a repetition:

```text
w = v^r
```

then the loop equation for `w` reduces exactly to the loop equation for `v`.

Therefore the Lock 1 no-loop theorem only has to rule out primitive exponent
words.

## Definitions

Let `v` have:

```text
length m
total exponent S
offset B_v
denominator F = 2^S - 3^m
```

Let:

```text
w = v^r
```

Then `w` has:

```text
length k = rm
total exponent A = rS
denominator D = 2^A - 3^k = 2^(rS) - 3^(rm)
```

Define the repetition cofactor:

```text
R = sum_{t=0}^{r-1} 3^(m(r-1-t)) 2^(St)
```

Equivalently:

```text
R = ((2^S)^r - (3^m)^r) / (2^S - 3^m)
```

so:

```text
D = F R
```

## Offset Factorization

Appending a copy of `v` multiplies the existing offset by `3^m` and adds the
new copy shifted by the previous total exponent.

For `w = v^r`, this gives:

```text
B_w = B_v R
```

with the same cofactor:

```text
R = sum_{t=0}^{r-1} 3^(m(r-1-t)) 2^(St)
```

## Divisibility Reduction

A loop for `w` requires:

```text
D | B_w
```

Substitute the factorizations:

```text
F R | B_v R
```

Cancel the positive integer `R`:

```text
F | B_v
```

Therefore:

```text
D_w | B_w
iff
D_v | B_v
```

and the returned value is identical:

```text
B_w / D_w = B_v / D_v
```

So an imprimitive loop word is never new. It is only the same loop repeated.

## Consequence

The all-2 heartbeat:

```text
v = (2)
```

can repeat forever, but every repeat still reduces to:

```text
x = 1
```

Any nontrivial loop must have a primitive exponent word.

Thus the remaining Lock 1 barrier theorem becomes:

```text
For every primitive non-all-2 positive exponent word w,
D_w does not divide B_w.
```

## Connection To Factor Cascade Data

The survivor dump for:

```text
k=8,A=30
D = 2^30 - 3^8 = 1073735263
D = 107 * 307 * 32687
```

shows:

```text
pre_final_candidates=380
period_counts=4:364;8:16
zero_final_residue=0
```

The 364 period-4 candidates are explained by this lemma. If:

```text
w = v^2
length(v)=4
total(v)=15
```

then:

```text
D_w = 2^30 - 3^8
    = (2^15 - 3^4)(2^15 + 3^4)
    = 32687 * 32849
    = 32687 * 107 * 307
```

and:

```text
B_w = B_v(2^15 + 3^4)
```

So those candidates automatically survive the `107` and `307` walls. The final
wall is the primitive-root denominator:

```text
2^15 - 3^4 = 32687
```

The closest final-wall miss in the current dump is:

```text
word = 2 7 1 5 2 7 1 5
residue mod 32687 = 32682
distance from zero = 5
```

It misses because its primitive root:

```text
v = 2 7 1 5
```

is not a loop word.
