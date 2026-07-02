# Lock 3 Precision Countdown Grid

Run context: lineage/cohort census, terminal value 1. Most rows are depth
2000; exceptions are noted inline.

## Core Observation

For fixed `C`, the maximum valid1 lineage lifetime behaves like a countdown in residue precision `m`:

```text
max_lineage_lifetime = cutoff(C) - m
```

Each increase in residue precision removes one unit of valid-lineage survival.

## Observed Grid

Values are `max_lifetime_of_valid1_lineage`.

| C \ m | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C3 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 | 0 | 0 | - | - | - | - |
| C4 | 12 | 11 | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 | - | - | - |
| C5 | 14 | 13 | 12 | 11 | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1* | 0** | 0 |

## Countdown Form

| C | Observed countdown | Observed / implied cutoff |
| ---: | --- | ---: |
| C3 | `9,8,7,6,5,4,3,2,1,0` | 10 |
| C4 | `12,11,10,9,8,7,6,5,4,3,2,1,0` | 13 |
| C5 | `14,13,12,11,10,9,8,7,6,5,4,3,2,1,0` | 15 observed |

## Regime Grid

| C \ m | Persistent | Transient terminal-clean | Fully clean |
| ---: | --- | --- | --- |
| C3 | m1-m7 | m8-m9 | m10+ |
| C4 | m1-m9 | m10-m12 | m13+ |
| C5 | m1-m12 | m13-m14 | m15+ |

## C3 Details

```text
m1  -> 9
m2  -> 8
m3  -> 7
m4  -> 6
m5  -> 5
m6  -> 4
m7  -> 3
m8  -> 2
m9  -> 1
m10 -> 0
```

C3 zero point:

```text
m = 10
```

## C4 Details

```text
m1  -> 12
m2  -> 11
m3  -> 10
m4  -> 9
m5  -> 8
m6  -> 7
m7  -> 6
m8  -> 5
m9  -> 4
m10 -> 3
m11 -> 2
m12 -> 1
m13 -> 0
```

C4 zero point:

```text
m = 13
```

## C5 Details

Observed completed N2000 rows:

```text
m1  -> 14
m2  -> 13
m3  -> 12
m4  -> 11
m5  -> 10
m6  -> 9
m7  -> 8
m8  -> 7
m9  -> 6
m10 -> 5
m11 -> 4
m12 -> 3
m13 -> 2
```

Observed boundary probes:

```text
m14 -> 1  (partial depth 1169; killed at user request after live count returned to 0)
m15 -> 0  (depth 50 clean)
m16 -> 0  (depth 250 clean)
```

The C5 m15 depth-50 run wrote:

```text
data/runs/lock3_C5_N50_residue_m15_lineage_cohorts_20260524_005303
```

Result: `ever_seen_valid1=false`, `terminal_1_compatible_signature_count=0`,
`live_valid1_count=0`, `max_lifetime_of_valid1_lineage=0`,
`clean_prefix_depth=50`.

This supports the strict countdown cutoff at `m = 15` for C5. That is not the
same as the earlier `3C + 1` extrapolation, because `3*5 + 1 = 16`.

## Higher-C m1 Probes

Only `m1` has been checked for C6-C50 in this series:

| C | m | observed max lifetime | implied cutoff from m1 | correction vs `3C` |
| ---: | ---: | ---: | ---: | ---: |
| 6 | 1 | 16 | 17 | -1 |
| 7 | 1 | 19 | 20 | -1 |
| 8 | 1 | 21 | 22 | -2 |
| 9 | 1 | 24 | 25 | -2 |
| 10 | 1 | 26 | 27 | -3 |
| 11 | 1 | 28 | 29 | -4 |
| 12 | 1 | 31 | 32 | -4 |
| 13 | 1 | 33 | 34 | -5 |
| 14 | 1 | 36 | 37 | -5 |
| 15 | 1 | 38 | 39 | -6 |
| 16 | 1 | 40 | 41 | -7 |
| 17 | 1 | 43 | 44 | -7 |
| 18 | 1 | 45 | 46 | -8 |
| 19 | 1 | 48 | 49 | -8 |
| 20 | 1 | 50 | 51 | -9 |
| 21 | 1 | 53 | 54 | -9 |
| 22 | 1 | 55 | 56 | -10 |
| 23 | 1 | 57 | 58 | -11 |
| 24 | 1 | 60 | 61 | -11 |
| 25 | 1 | 62 | 63 | -12 |
| 26 | 1 | 65 | 66 | -12 |
| 27 | 1 | 67 | 68 | -13 |
| 28 | 1 | 69 | 70 | -14 |
| 29 | 1 | 72 | 73 | -14 |
| 30 | 1 | 74 | 75 | -15 |
| 31 | 1 | 77 | 78 | -15 |
| 32 | 1 | 79 | 80 | -16 |
| 33 | 1 | 81 | 82 | -17 |
| 34 | 1 | 84 | 85 | -17 |
| 35 | 1 | 86 | 87 | -18 |
| 36 | 1 | 89 | 90 | -18 |
| 37 | 1 | 91 | 92 | -19 |
| 38 | 1 | 93 | 94 | -20 |
| 39 | 1 | 96 | 97 | -20 |
| 40 | 1 | 98 | 99 | -21 |
| 41 | 1 | 101 | 102 | -21 |
| 42 | 1 | 103 | 104 | -22 |
| 43 | 1 | 106 | 107 | -22 |
| 44 | 1 | 108 | 109 | -23 |
| 45 | 1 | 110 | 111 | -24 |
| 46 | 1 | 113 | 114 | -24 |
| 47 | 1 | 115 | 116 | -25 |
| 48 | 1 | 118 | 119 | -25 |
| 49 | 1 | 120 | 121 | -26 |
| 50 | 1 | 122 | 123 | -27 |

The C8-C15 batch was run under:

```text
data/runs/lock3_C8_N2000_residue_m1_lineage_cohorts_20260524_010942
data/runs/lock3_C10_N2000_residue_m1_lineage_cohorts_20260524_011032
data/runs/lock3_C11_N2000_residue_m1_lineage_cohorts_20260524_011032
data/runs/lock3_C12_N2000_residue_m1_lineage_cohorts_20260524_011032
data/runs/lock3_C13_N2000_residue_m1_lineage_cohorts_20260524_011032
data/runs/lock3_C14_N2000_residue_m1_lineage_cohorts_20260524_011032
data/runs/lock3_C15_N2000_residue_m1_lineage_cohorts_20260524_011032
```

The C16-C30 batch was run under:

```text
data/runs/lock3_C16_N2000_residue_m1_lineage_cohorts_20260524_011324
...
data/runs/lock3_C30_N2000_residue_m1_lineage_cohorts_20260524_011324
```

The C31-C50 batch was run under:

```text
data/runs/lock3_C31_N2000_residue_m1_lineage_cohorts_20260524_011632
...
data/runs/lock3_C50_N2000_residue_m1_lineage_cohorts_20260524_011632
```

The C9 row uses the earlier complete run:

```text
data/runs/lock3_C9_N2000_residue_m1_lineage_cohorts_20260523_220055
```

These are not enough to establish the full countdown ladders, but they are
consistent with the same form:

```text
max_lifetime = cutoff(C) - m
```

with a C-dependent cutoff. The cutoff is not simply `3C + 1`; the higher-C m1
probes show a stepped negative correction against `3C`.

## What This Means

The important discovery is not just that compatible states disappear. The important discovery is that they disappear by a linear precision countdown:

```text
increase m by 1 -> max survivable lineage lifetime drops by 1
```

That makes Lock 3 look like a bounded-corridor vertical precision collapse:

```text
bounded width gives a finite survival budget;
residue precision consumes that budget one unit at a time;
at the cutoff, terminal-1 compatibility disappears.
```
