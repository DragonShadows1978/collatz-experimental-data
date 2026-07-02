# Lock 3 C=5 / m=8 Breakdown

Run date: 2026-05-23

## Scope

This note isolates the C=5, m=8 Lock 3 runs and explains what they show before
the C=5 precision ladder thins out at higher residue precision.

The important comparison ladder is:

```text
m=8  -> persistent low-precision terminal-compatible mass
m=10 -> persistent, thinner terminal-compatible mass
m=12 -> persistent, usually one terminal-compatible signature
m=14 -> isolated one-depth sparks
m=16 -> clean through depth 250
```

## Runs

Depth 250:

```bash
/tmp/collatz-rust-target-lineage/release/lock3_census \
  --C 5 --depth 250 --residue-mod-power 8 \
  --out-dir data/runs/lock3_C5_N250_residue_m8_lineage_lean \
  --progress-every 25 --label lock3 \
  --memory-lean --no-checkpoint \
  --progress-jsonl data/runs/lock3_C5_N250_residue_m8_lineage_lean/live_events.jsonl
```

Depth 2000:

```bash
/tmp/collatz-rust-target-lineage/release/lock3_census \
  --C 5 --depth 2000 --residue-mod-power 8 \
  --out-dir data/runs/lock3_C5_N2000_residue_m8_lineage_lean \
  --progress-every 100 --label lock3 \
  --memory-lean --no-checkpoint \
  --progress-jsonl data/runs/lock3_C5_N2000_residue_m8_lineage_lean/live_events.jsonl
```

## Depth-250 Result

Artifacts:

- `data/runs/lock3_C5_N250_residue_m8_lineage_lean/lock3_summary_C5.json`
- `data/runs/lock3_C5_N250_residue_m8_lineage_lean/lock3_census_C5.csv`
- `data/runs/lock3_C5_N250_residue_m8_lineage_lean/live_events.jsonl`

Summary:

| metric | value |
| --- | ---: |
| first valid1 depth | 14 |
| last valid1 depth | 250 |
| clean prefix depth | 13 |
| dirty depths | 237 |
| dirty gap pattern | all gap 1 after depth 14 |
| final compatible signatures | 3 |
| final live valid1 count | 3 |
| max valid1 shadow lifetime | 7 |
| peak RSS KB | 16004 |

Compatible-signature distribution:

| compatible signatures | depth count |
| ---: | ---: |
| 1 | 2 |
| 2 | 76 |
| 3 | 159 |

## Depth-2000 Result

Artifacts:

- `data/runs/lock3_C5_N2000_residue_m8_lineage_lean/lock3_summary_C5.json`
- `data/runs/lock3_C5_N2000_residue_m8_lineage_lean/lock3_census_C5.csv`
- `data/runs/lock3_C5_N2000_residue_m8_lineage_lean/live_events.jsonl`

Summary:

| metric | value |
| --- | ---: |
| first valid1 depth | 14 |
| last valid1 depth | 2000 |
| clean prefix depth | 13 |
| dirty depths | 1987 |
| dirty gap pattern | all gap 1 after depth 14 |
| final compatible signatures | 2 |
| final live valid1 count | 2 |
| max live valid1 count | 3 |
| max valid1 shadow lifetime | 7 |
| total tracked births | 827 |
| total tracked deaths | 825 |
| persisted rows | 1985 |
| peak RSS KB | 30532 |

Compatible-signature distribution:

| compatible signatures | depth count |
| ---: | ---: |
| 1 | 2 |
| 2 | 637 |
| 3 | 1348 |

## Depth-2000 Resonance Check

The depth-2000 m8 artifact also shows longer block resonance on top of the
period-53 birth/death skeleton.

Checked artifact:

- `data/runs/lock3_C5_N2000_residue_m8_lineage_lean/lock3_census_C5.csv`

### Period 665

`665 mod 53 = 29`.

For the key-level live-compatible fields, blocks 2 and 3 match exactly:

```text
block 1 = depths 1..665
block 2 = depths 666..1330
block 3 = depths 1331..1995
```

| field | block 1 sum | block 2 sum | block 3 sum | b1 vs b2 mismatches | b2 vs b3 mismatches |
| --- | ---: | ---: | ---: | ---: | ---: |
| live_valid1_count | 1743 | 1782 | 1782 | 16 / 665 | 0 / 665 |
| terminal_1_compatible_signature_count | 1743 | 1782 | 1782 | 16 / 665 | 0 / 665 |
| valid1_shadow_birth_count | 273 | 276 | 276 | 9 / 665 | 0 / 665 |
| valid1_shadow_death_count | 270 | 276 | 276 | 6 / 665 | 0 / 665 |

Block distributions:

| field | block 1 distribution | block 2 distribution | block 3 distribution |
| --- | --- | --- | --- |
| live_valid1_count | `{0:13, 1:2, 2:209, 3:441}` | `{2:213, 3:452}` | `{2:213, 3:452}` |
| terminal_1_compatible_signature_count | `{0:13, 1:2, 2:209, 3:441}` | `{2:213, 3:452}` | `{2:213, 3:452}` |
| valid1_shadow_birth_count | `{0:392, 1:273}` | `{0:389, 1:276}` | `{0:389, 1:276}` |
| valid1_shadow_death_count | `{0:395, 1:270}` | `{0:389, 1:276}` | `{0:389, 1:276}` |

Interpretation:

```text
665 is a clean post-startup resonance in this artifact.
The first block carries startup defects.
The next two full 665-blocks match exactly at key level.
```

### Period 359

`359 mod 53 = 41`.

The period-359 signal is also strong, but it has small phase defects after the
startup transient.

```text
block 1 = depths 1..359
block 2 = depths 360..718
block 3 = depths 719..1077
block 4 = depths 1078..1436
block 5 = depths 1437..1795
```

For `live_valid1_count` and `terminal_1_compatible_signature_count`:

| comparison | mismatches |
| --- | ---: |
| block 1 vs block 2 | 18 / 359 |
| block 2 vs block 3 | 0 / 359 |
| block 2 vs block 4 | 2 / 359 |
| block 3 vs block 4 | 2 / 359 |
| block 4 vs block 5 | 0 / 359 |

For key-level births:

| comparison | mismatches |
| --- | ---: |
| block 1 vs block 2 | 11 / 359 |
| block 2 vs block 3 | 0 / 359 |
| block 2 vs block 4 | 2 / 359 |
| block 4 vs block 5 | 0 / 359 |

For key-level deaths:

| comparison | mismatches |
| --- | ---: |
| block 1 vs block 2 | 8 / 359 |
| block 2 vs block 3 | 0 / 359 |
| block 2 vs block 4 | 2 / 359 |
| block 4 vs block 5 | 0 / 359 |

Post-startup `d` vs `d + 359` defects are sparse:

| field | post-startup mismatch depths |
| --- | --- |
| live_valid1_count | `971`, `979`, `1636` |
| terminal_1_compatible_signature_count | `971`, `979`, `1636` |
| valid1_shadow_birth_count | `979`, `980` |
| valid1_shadow_death_count | `971`, `972`, `1636`, `1637` |

Interpretation:

```text
359 is not noise.
Blocks 2 and 3 match exactly.
Blocks 4 and 5 match exactly.
The only post-startup failures are tiny phase defects.
```

### Resonance Read

Current read from the depth-2000 m8 file:

```text
53  = local key-level birth/death clock
359 = strong longer envelope with sparse phase defects
665 = cleaner post-startup block repeat in this run
```

So the m8 behavior is not just "dirty forever." It has a stable binary
skeleton, plus longer resonant block structure. The next useful check is to run
the resonance scan against the cohort-tracked m8 output, so the same periods can
be compared against lineage mass instead of only key-level events.

## Interpretation

C=5/m8 is not transient. It becomes terminal-compatible at depth 14 and then
stays dirty at every depth tested through depth 2000.

The live shadow layer is small and stable:

```text
live valid1 count cycles between 2 and 3
max lifetime remains 7
birth/death churn continues
the system never clears
```

This is the low-precision saturated regime. It is the opposite end of the C=5
ladder from m=16:

```text
C=5/m8  : persistent, cycling, final-live
C=5/m10 : persistent, usually 2 compatible signatures
C=5/m12 : persistent, usually 1 compatible signature
C=5/m14 : isolated one-depth sparks
C=5/m16 : no valid1 mass through depth 250
```

The C=5 decay is therefore not depth decay at fixed low precision. It is
precision decay. Increasing `m` strips away terminal-compatible mass.

## Current Birth-Tracking Limitation

The current lean scanner tracks live valid1 shadows as:

```text
HashMap<Key, birth_depth>
```

where `Key = (deficit_state, terminal_residue_signature)`.

That is efficient and good for the first lifecycle pass, but it collapses
multiple histories that land on the same key. Consequences:

- `live_valid1_count` means live compatible keys, not live compatible histories.
- `valid1_shadow_birth_count` means new compatible keys born at a depth, not all
  compatible branch births.
- If two parents create the same compatible child key, the current tracker keeps
  the earliest birth depth and drops the other lineage identity.
- `max_valid1_shadow_lifetime` is a key-level lifetime, not a full path-lineage
  lifetime.

So the m8 result proves persistent key-level terminal compatibility. It does not
yet measure all individual birth histories inside the merged compatible mass.

## Multiple-Birth Tracking Options

### Option A: Birth-Depth Histogram Per Key

Replace:

```text
HashMap<Key, birth_depth>
```

with:

```text
HashMap<Key, BTreeMap<birth_depth, lineage_count>>
```

Behavior:

- A key can hold multiple birth cohorts.
- If two histories merge into the same key, both cohorts remain counted.
- Birth count becomes the sum of new cohort counts.
- Death count becomes the sum of cohort counts that fail to propagate.
- Lifetime distribution becomes measurable.

Pros:

- Still merged and memory-bounded compared to full paths.
- Gives real multiple-birth counts.
- Can output histograms: lifetime 1, lifetime 2, ..., lifetime max.

Cons:

- More memory than the current single birth-depth map.
- Counts may become huge, so `lineage_count` should probably use `Big`.

Recommended first implementation.

### Option B: Aggregate Lifetime Histogram Only

Keep the current key-level live map, but add global counters:

```text
births_by_depth
deaths_by_depth
deaths_by_lifetime
survivors_by_lifetime
```

This does not preserve all cohorts per key. It only records aggregate lifecycle
statistics as shadows are born and die.

Pros:

- Very cheap.
- Good for curves and heatmaps.
- Minimal risk to the fast scanner.

Cons:

- Still cannot distinguish multiple births that merge into one key.
- Not enough if we need lineage-level proof objects.

Useful as a quick telemetry layer, but not enough as the final answer.

### Option C: Parent Transition Multiplicity

Track transitions into terminal-compatible keys:

```text
parent_key -> child_key -> multiplicity
```

Only record transitions where `child_key` is terminal-compatible.

Pros:

- Directly answers how many parent channels feed each live shadow.
- Excellent for diagnosing why m8/m10 are persistent and why m14 sparks die.
- Can pair with lift-profile output.

Cons:

- Potentially large if enabled globally.
- Should be gated behind a flag and probably sampled by depth range.

Useful for targeted studies around transition bands.

### Option D: Top-K Lineage Witnesses Plus Aggregate Counts

Store full lineage/witness data only for a bounded top K per compatible key,
while keeping aggregate counts for everything else.

Pros:

- Produces inspectable examples.
- Avoids full witness explosion.
- Good for debugging suspected families or periodic bands.

Cons:

- Not exhaustive.
- Needs careful labeling so examples are not mistaken for total counts.

Useful for explanation and verification, not as the primary counting engine.

## Recommendation

Implement Option A first:

```text
HashMap<Key, BTreeMap<birth_depth, Big lineage_count>>
```

Then add these output fields:

```text
live_valid1_key_count
live_valid1_lineage_count
valid1_key_birth_count
valid1_lineage_birth_count
valid1_key_death_count
valid1_lineage_death_count
max_key_lifetime
max_lineage_lifetime
lineage_lifetime_histogram
```

This keeps the current key-level lifecycle metrics, while adding the missing
multiple-birth accounting needed to separate "one compatible key persists" from
"many compatible histories keep being reborn into the same key."

The m8 result is exactly where this matters: the key-level live count stays tiny
while the compatible mass is enormous. That gap is the signal that multiple
births and merged lineages need their own counters.

## Cohort Tracker Implementation

Implemented on 2026-05-23 in the Rust lean scanner.

The lean path now tracks:

```text
HashMap<Key, BTreeMap<birth_depth, Big lineage_count>>
```

The original key-level lifecycle fields remain:

```text
live_valid1_count
valid1_shadow_birth_count
valid1_shadow_death_count
max_valid1_shadow_lifetime
```

New lineage-level fields were added:

```text
live_valid1_lineage_count
valid1_lineage_birth_count
valid1_lineage_death_count
max_valid1_lineage_lifetime
lineage_lifetime_histogram
```

Smoke output verified:

- CSV header contains the new lineage columns.
- JSONL progress and final events contain the new lineage fields.
- Summary JSON contains cumulative lineage births, deaths, and lifetime
  histogram.

### C=5/m8 Cohort Rerun, Depth 250

Command:

```bash
/tmp/collatz-rust-target-lineage/release/lock3_census \
  --C 5 --depth 250 --residue-mod-power 8 \
  --out-dir data/runs/lock3_C5_N250_residue_m8_lineage_cohorts \
  --progress-every 50 --label lock3 \
  --memory-lean --no-checkpoint \
  --progress-jsonl data/runs/lock3_C5_N250_residue_m8_lineage_cohorts/live_events.jsonl
```

Artifacts:

- `data/runs/lock3_C5_N250_residue_m8_lineage_cohorts/lock3_summary_C5.json`
- `data/runs/lock3_C5_N250_residue_m8_lineage_cohorts/lock3_census_C5.csv`
- `data/runs/lock3_C5_N250_residue_m8_lineage_cohorts/live_events.jsonl`

Key result:

| metric | value |
| --- | ---: |
| final live key count | 3 |
| final live lineage count | 302236783354729162265282871981034548351626274923866698666013090627639373707917270717178460470269393 |
| cumulative lineage births | 352853615552555238833741683381535082019837987205426579816429448746804001231395203822918143177437446 |
| cumulative lineage deaths | 50616832197826076568458811400500533668211712281559881150416358119164627523477933105739682707168053 |
| max lineage lifetime | 7 |

Interpretation:

```text
key-level view: 3 live compatible keys
lineage-level view: enormous compatible mass flowing through those keys
```

This confirms the original concern: at low precision, a tiny number of merged
keys can represent an enormous number of live terminal-compatible histories.
The cohort tracker now exposes that hidden multiplicity directly.

## Binary Event Pattern

The key-level birth/death layer is binary:

```text
valid1_shadow_birth_count is always 0 or 1
valid1_shadow_death_count is always 0 or 1
```

For the C=5/m8/N250 cohort run:

| field | 0 rows | 1 rows |
| --- | ---: | ---: |
| valid1_shadow_birth_count | 149 | 101 |
| valid1_shadow_death_count | 152 | 98 |

This is only the key-level skeleton. The lineage-level birth/death fields are
large `Big` counts and are not binary.

### Period-53 Masks

After the startup transient, the key-level event masks are period-53.

Death-event mask:

```text
01010010100101010010100101010010100101001010100101001
```

Birth-event mask, after its startup offset:

```text
10010101001010010101001010010101001010010100101010010
```

These masks have:

```text
period length = 53
ones = 22
zeros = 31
```

The death mask as a binary integer:

```text
binary = 01010010100101010010100101010010100101001010100101001
hex    = 0xa52a52a529529
```

The birth mask as a binary integer:

```text
binary = 10010101001010010101001010010101001010010100101010010
hex    = 0x12a52a52a52952
```

### ASCII Check

Interpreting the 53-bit masks as raw 8-bit ASCII does not produce readable text.
Different byte offsets produce fragments such as:

```text
R.)R..
.*R.)R
JT.JR.
```

So the binary word should not be read as a hidden message. It is a structured
event mask.

### Interpretation

The meaningful signal is:

```text
binary skeleton = period 53
lineage mass    = enormous Big-count flow through that skeleton
```

That is exactly the kind of structure Lock 3 has been exposing elsewhere. The
period is not arbitrary: `53` is one of the known near-return/corridor
denominators already appearing in the Lock 3 and Lock 4 bridge analysis.

In plain terms:

```text
m8 does not just stay dirty.
m8 stays dirty by cycling through a period-53 key-level birth/death rhythm.
```
