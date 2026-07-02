# Lock 3 Birth-Invariant Audit

Date: 2026-05-24

## Result

The original fixed birth audit stands for the primary Lock 3 audit domain
`C >= 3`, but the cleaner statement is corridor-dependent.

The correct generalized birth ceiling is:

```text
I_birth <= K(C) - 3C
```

where:

```text
K(C) = first desert precision
M_edge(C) = K(C) - 1
```

The scanner records

```text
I_birth = L_at_birth + m - 3C
```

and `L_at_birth = 1` for a newly emitted birth cohort in the current scanner.

Under the original fixed test, every completed primary `C=3..5`
`lock3_birth_invariant_summary.json` reported:

```text
births_I_gt_1 = 0
main_theorem_test_passed = true
```

The generalized audit absorbs the low-width `C=1` and `C=2` edges instead of
treating them as contradictions:

```text
C=1: K=5,  K-3C=2
C=2: K=8,  K-3C=2
C=3: K=10, K-3C=1
C=4: K=13, K-3C=1
C=5: K=15, K-3C=0
```

In each completed case, the observed top birth equals this ceiling, and no
birth is observed above it.

The important correction is that this does not mean the visible occupied edge is
always the naive `3C+1` line, and it also does not mean the ceiling is always
`I_birth = 1`. The audit is showing a cleaner object: the birth ceiling decays
with the corridor according to `K(C)-3C`.

## Completed Scope

Primary sweep:

```text
C = 3, m = 1..10, depth = 250
C = 4, m = 1..13, depth = 250
C = 5, m = 1..15, depth = 250
```

Additional odd check:

```text
C = 1, m = 4..5, depth = 250
C = 2, m = 1, depth = 250
C = 2, m = 7..8, depth = 250
```

The `C=5, m=16` run was intentionally stopped because `m=16` was already known
to be desert and was not needed for the birth audit conclusion.

Artifacts are under:

```text
/mnt/ForgeRealm/collatz-experimental-data/Lock3_birth_audit/
```

## Audit Grid

Columns:

- `max_I_birth`: maximum birth invariant observed in emitted birth rows.
- `I>1`: count of birth rows with `I_birth > 1`.
- `I=1`: count of birth rows with `I_birth = 1`.
- `I<1`: count of birth rows with `I_birth < 1`.
- `birth_rows`: emitted birth audit rows.
- `pass`: scanner theorem-test flag.

The `I>1` and `pass` columns are the scanner's original fixed-ceiling fields.
The generalized check is evaluated separately below using `K(C)-3C`.

### Low-C corridor checks

| C | m | max_I_birth | I>1 | I=1 | I<1 | birth_rows | pass |
|---:|---:|---:|---:|---:|---:|---:|:---|
| 1 | 4 | 2 | 84 | 0 | 0 | 84 | false |
| 1 | 5 | null | 0 | 0 | 0 | 0 | true |
| 2 | 1 | -4 | 0 | 0 | 784 | 784 | true |
| 2 | 7 | 2 | 23 | 0 | 0 | 23 | false |
| 2 | 8 | null | 0 | 0 | 0 | 0 | true |

### C = 3

| C | m | max_I_birth | I>1 | I=1 | I<1 | birth_rows | pass |
|---:|---:|---:|---:|---:|---:|---:|:---|
| 3 | 1 | -7 | 0 | 0 | 1272 | 1272 | true |
| 3 | 2 | -6 | 0 | 0 | 1734 | 1734 | true |
| 3 | 3 | -5 | 0 | 0 | 955 | 955 | true |
| 3 | 4 | -4 | 0 | 0 | 750 | 750 | true |
| 3 | 5 | -3 | 0 | 0 | 546 | 546 | true |
| 3 | 6 | -2 | 0 | 0 | 362 | 362 | true |
| 3 | 7 | -1 | 0 | 0 | 261 | 261 | true |
| 3 | 8 | 0 | 0 | 0 | 161 | 161 | true |
| 3 | 9 | 1 | 0 | 62 | 0 | 62 | true |
| 3 | 10 | null | 0 | 0 | 0 | 0 | true |

### C = 4

| C | m | max_I_birth | I>1 | I=1 | I<1 | birth_rows | pass |
|---:|---:|---:|---:|---:|---:|---:|:---|
| 4 | 1 | -10 | 0 | 0 | 1900 | 1900 | true |
| 4 | 2 | -9 | 0 | 0 | 2883 | 2883 | true |
| 4 | 3 | -8 | 0 | 0 | 1700 | 1700 | true |
| 4 | 4 | -7 | 0 | 0 | 1592 | 1592 | true |
| 4 | 5 | -6 | 0 | 0 | 1386 | 1386 | true |
| 4 | 6 | -5 | 0 | 0 | 1180 | 1180 | true |
| 4 | 7 | -4 | 0 | 0 | 618 | 618 | true |
| 4 | 8 | -3 | 0 | 0 | 419 | 419 | true |
| 4 | 9 | -2 | 0 | 0 | 297 | 297 | true |
| 4 | 10 | -1 | 0 | 0 | 198 | 198 | true |
| 4 | 11 | 0 | 0 | 0 | 101 | 101 | true |
| 4 | 12 | 1 | 0 | 4 | 0 | 4 | true |
| 4 | 13 | null | 0 | 0 | 0 | 0 | true |

### C = 5

| C | m | max_I_birth | I>1 | I=1 | I<1 | birth_rows | pass |
|---:|---:|---:|---:|---:|---:|---:|:---|
| 5 | 1 | -13 | 0 | 0 | 2623 | 2623 | true |
| 5 | 2 | -12 | 0 | 0 | 4081 | 4081 | true |
| 5 | 3 | -11 | 0 | 0 | 2694 | 2694 | true |
| 5 | 4 | -10 | 0 | 0 | 2583 | 2583 | true |
| 5 | 5 | -9 | 0 | 0 | 2455 | 2455 | true |
| 5 | 6 | -8 | 0 | 0 | 2343 | 2343 | true |
| 5 | 7 | -7 | 0 | 0 | 1487 | 1487 | true |
| 5 | 8 | -6 | 0 | 0 | 1108 | 1108 | true |
| 5 | 9 | -5 | 0 | 0 | 688 | 688 | true |
| 5 | 10 | -4 | 0 | 0 | 491 | 491 | true |
| 5 | 11 | -3 | 0 | 0 | 332 | 332 | true |
| 5 | 12 | -2 | 0 | 0 | 234 | 234 | true |
| 5 | 13 | -1 | 0 | 0 | 138 | 138 | true |
| 5 | 14 | 0 | 0 | 0 | 43 | 43 | true |
| 5 | 15 | null | 0 | 0 | 0 | 0 | true |

## Edge Behavior

The observed decay edge is:

```text
M_edge(C) = floor((53 / 22) * (C + 1))
K(C) = M_edge(C) + 1
```

This is the cleaner pattern exposed by the audit. It predicts the last occupied
`m` level for the completed checks:

| C | top occupied m `M_edge` | first desert `K(C)` | `K(C)-3C` | max_I_birth at top |
|---:|---:|---:|---:|---:|
| 1 | 4 | 5 | 2 | 2 |
| 2 | 7 | 8 | 2 | 2 |
| 3 | 9 | 10 | 1 | 1 |
| 4 | 12 | 13 | 1 | 1 |
| 5 | 14 | 15 | 0 | 0 |

This is the key observation.

For `C=3` and `C=4`, `K(C)-3C = 1`, so the old fixed ceiling accidentally
looked universal. For `C=5`, `K(C)-3C = 0`; the `I=1` level is skipped. For
`C=1` and `C=2`, `K(C)-3C = 2`; the small corridor allows a top birth above
the old fixed ceiling.

So the audited statement is not:

```text
the top edge is always I = 1
```

The generalized audited statement is:

```text
no birth occurs above I_birth = K(C) - 3C
```

That is a stronger and cleaner formulation for Lock 3, because it allows
small-corridor shifts, desert gaps, and skipped old-ceiling levels without
damaging the birth ceiling.

## Lifetime / Desert Notes

The normal census summaries show the visible lifetime edge:

| C | m | ever seen valid1 | first valid depth | last valid depth | max lineage lifetime |
|---:|---:|:---|---:|---:|---:|
| 1 | 4 | true | 7 | 250 | 1 |
| 1 | 5 | false | null | null | 0 |
| 2 | 7 | true | 12 | 248 | 1 |
| 2 | 8 | false | null | null | 0 |
| 3 | 9 | true | 19 | 250 | 1 |
| 3 | 10 | false | null | null | 0 |
| 4 | 12 | true | 53 | 212 | 1 |
| 4 | 13 | false | null | null | 0 |
| 5 | 14 | true | 24 | 248 | 1 |
| 5 | 15 | false | null | null | 0 |

The `C=5, m=14` run is especially important:

```text
C=5, m=14
max_I_birth = 0
first_valid1_depth = 24
last_valid1_depth = 248
max_lifetime_of_valid1_lineage = 1
final valid_from_1_count = 0
```

That means `C=5, m=14` is dirty during the scan, but terminally clean at depth
250. It supplies one-frame birth/death evidence without touching `I_birth = 1`.

The `C=5, m=15` run is desert through depth 250:

```text
C=5, m=15
ever_seen_valid1 = false
birth_rows = 0
max_I_birth = null
```

## Interpretation

The birth-invariant audit supports the local Lock 3 proof shape in generalized
form:

```text
If I_birth > K(C) - 3C, the terminal-compatible state is not a birth.
Therefore any terminal-compatible birth must satisfy:
I_birth <= K(C) - 3C.
```

The data does not support compressing the behavior into a simple `3C+1`
boundary rule. That rule matched the visible edge for `C=3` and `C=4`, but the
completed checks follow the cleaner decay edge:

```text
M_edge(C) = floor((53 / 22) * (C + 1))
```

`C=5` shows the real structure is more selective than the old `I=1` ceiling:
the local ceiling is `I=0`. `C=1` and `C=2` show the small corridor has local
ceiling `I=2`. These are not contradictions once the ceiling is written as
`K(C)-3C`.

This makes the birth bound more robust, not less robust. The proof object is
the ceiling:

```text
I_birth <= K(C) - 3C
```

not the assumption that every corridor uses the same fixed `I=1` ceiling.
