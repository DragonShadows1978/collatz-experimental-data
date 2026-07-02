# Results

Run date: 2026-05-21

## Machine

- CPU workers used: 11
- System CPU count: 12
- RAM observed: 62 GiB
- GPU present: RTX 3070, not used for this integer scan

## Exhaustive Reserve Scans

All scans covered every odd start in the stated range.

| Limit | Threshold | Hits | Best max reserve | Best start |
| ---: | ---: | ---: | ---: | ---: |
| 1,000,000 | 12 | 44 | 15 | 159487 |
| 25,000,000 | 16 | 58 | 22 | 19638399 |
| 100,000,000 | 22 | 3 | 23 | 80049391 |
| 250,000,000 | 24 | 0 | none | none |
| 250,000,000 | 23 | 6 | 23 | 80049391 |

Top tier through 250M:

| Start | Max reserve | Time of max | Bankruptcy crossing | Growth steps |
| ---: | ---: | ---: | ---: | ---: |
| 80049391 | 23 | 72 | 153 | 53 |
| 120080895 | 23 | 65 | 128 | 48 |
| 210964383 | 23 | 115 | 150 | 56 |
| 219259131 | 23 | 132 | 167 | 64 |
| 222250543 | 23 | 120 | 155 | 58 |
| 246666523 | 23 | 130 | 164 | 61 |

No start below or equal to 250,000,000 reached reserve 24 in this harness.

## Structural Finding

Using strict contiguous reserve-increase segments of length at least 2, every
high-reserve segment observed so far is the exact exponent word `[1, 1]`.

For this word:

```text
S^2(x) = (9x + 5) / 4
gamma = -5 / (9 - 4) = -1
```

So the current "growth segment" definition does not distinguish different
negative ghosts: all detected local corridors are repeated visits to the same
`[1, 1]` expansion away from `-1`.

The next useful test is broader corridor detection: group the full solvent
intervals between major reserve crashes, compute exact affine maps for those
longer words, and then compare their ghosts and fixed-residual valuations.

## Macro-Corridor Pass

Implemented `macro` analysis from `macro-corridor-instructions.md` and ran it
on all six `D=23` starts:

```bash
PYTHONPATH=src python3 -m collatz_experimental_data macro \
  80049391 120080895 210964383 219259131 222250543 246666523
```

Output:

- `data/runs/macro_corridors_20260521T192009Z.csv`

Notable repeated structure:

- `210964383`, `219259131`, and `222250543` share the same high-plateau tail:
  `L=20,A=28`, `L=4,A=4`, `L=5,A=9`, `L=4,A=7`, `L=4,A=8`, `L=9,A=13`.
- The repeated positive-action ghosts in that tail include:
  - `L=20,A=28`: `-15327444431/3218348945`
  - `L=4,A=4`: `-1`
  - `L=9,A=13`: `-33835/11491`
- `80049391` reaches `D=23` earliest and has a different macro profile:
  a large opening corridor `L=74,A=96`, then shorter mixed positive and
  contractive blocks.

## Gap-Kill Pass

Implemented `gap-kill` from `Instructions for Codex.txt`.

Modeling assumption: outside a high-quality corridor, use a losing walk with
`a=2` per step. The credit stream is still the exact Sturmian sequence
`c_k = floor((k+1)log2(3)) - floor(k log2(3))`.

For the concrete `k=53 -> k=359` gap:

- Gap length: `306`
- Phase-specific reserve required from each observed `k=53` exit: `127`
- Worst-phase ladder reserve required: `128`
- Observed reserve at `k=53` exit across all six `D=23` orbits: `20` or `21`
- Result: none are bridgeable.

K=53 exit table:

| Start | k=53 exit step | Exit reserve | Peak reserve | Steps left before bankruptcy | Required reserve | Bridgeable |
| ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 80049391 | 74 | 21 | 23 | 79 | 127 | False |
| 120080895 | 74 | 21 | 23 | 54 | 127 | False |
| 210964383 | 94 | 20 | 22 | 56 | 127 | False |
| 219259131 | 111 | 20 | 22 | 56 | 127 | False |
| 222250543 | 99 | 20 | 22 | 56 | 127 | False |
| 246666523 | 109 | 20 | 22 | 55 | 127 | False |

Convergent ladder under this model:

| n | k | Gap | Observed max reserve | Required reserve | Bridgeable |
| ---: | ---: | ---: | ---: | ---: | :--- |
| 0 | 1 | 1 | 17 | 1 | True |
| 1 | 2 | 5 | 23 | 3 | True |
| 2 | 7 | 5 | 22 | 3 | True |
| 3 | 12 | 41 | 23 | 18 | True |
| 4 | 53 | 306 | 23 | 128 | False |
| 5 | 359 | 306 | n/a | 128 | n/a |
| 6 | 665 | 15601 | n/a | 6476 | n/a |
| 7 | 16266 | 15601 | n/a | 6476 | n/a |
| 8 | 31867 | 79335 | n/a | 32928 | n/a |

## Important Output Files

- `data/runs/scan_limit250000000_D23_20260521T190952Z.csv`
- `data/runs/scan_limit250000000_D24_20260521T190900Z.csv`
- `data/runs/orbit_80049391_20260521T190754Z.summary.json`
- `data/runs/orbit_80049391_20260521T190754Z.segments.csv`
- `data/runs/orbit_80049391_20260521T190754Z.seams.csv`
- `data/runs/macro_corridors_20260521T192009Z.csv`
- `data/runs/gap_kill_k53_exits_20260521T192732Z.csv`
- `data/runs/gap_kill_ladder_20260521T192732Z.csv`

## Actual Post-K=53 Behavior

Implemented `post-k53` from the updated `Instructions for Codex.txt`.

Output:

- `data/runs/post_k53_stats_20260521T193111Z.csv`
- `data/runs/post_k53_steps_20260521T193111Z.csv`

Summary across the six `D=23` starts:

- Mean actual drain per step after exiting the `k=53` macro-corridor: `-0.383`
- Conservative `a=2` drain model: `log2(3)-2 = -0.415`
- Mean observed-exponent bridge reserve for 306 steps: `117.8`
- Conservative bridge reserve for 306 steps: `128`
- Observed exit reserve remains only `20` or `21`, so no orbit is bridgeable
  even under the optimistic observed-exponent model.

Per-orbit optimistic bridge requirements:

| Start | Exit step | Post steps | frac a=1 | frac a=2 | frac a>=3 | avg a | drain/step | Required for 306 | Bridgeable |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 80049391 | 74 | 79 | 0.506 | 0.253 | 0.241 | 1.861 | -0.278 | 85 | False |
| 120080895 | 74 | 54 | 0.481 | 0.241 | 0.278 | 1.981 | -0.407 | 122 | False |
| 210964383 | 94 | 56 | 0.536 | 0.179 | 0.286 | 2.000 | -0.411 | 128 | False |
| 219259131 | 111 | 56 | 0.536 | 0.179 | 0.286 | 2.000 | -0.411 | 128 | False |
| 222250543 | 99 | 56 | 0.536 | 0.179 | 0.286 | 2.000 | -0.411 | 128 | False |
| 246666523 | 109 | 55 | 0.545 | 0.182 | 0.273 | 1.964 | -0.382 | 116 | False |

## K=53 Capacity

Implemented `k53-capacity` from the latest `Instructions for Codex.txt`.

Output:

- `data/runs/k53_capacity_observed_20260521T194035Z.csv`
- `data/runs/k53_capacity_requirements_20260521T194035Z.csv`

Observed main `k=53` macro-corridors:

| Start | Steps | L | Actual gain to peak | c=2 in window | Best c=2 same L | Entry bits | Max bits in corridor |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 80049391 | 0-74 | 74 | 23 | 43 | 44 | 27 | 50 |
| 120080895 | 0-74 | 74 | 23 | 43 | 44 | 27 | 50 |
| 210964383 | 0-94 | 94 | 22 | 54 | 55 | 28 | 51 |
| 219259131 | 13-111 | 98 | 22 | 57 | 58 | 29 | 51 |
| 222250543 | 0-99 | 99 | 22 | 57 | 58 | 28 | 51 |
| 246666523 | 22-109 | 87 | 22 | 51 | 51 | 29 | 51 |

Reserve requirement scale:

| Required reserve | Direct density L | Instruction-style L | Minimum bits | Approx log10(n) | log10 martingale bound | log10 expected starts |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 85 | 146 | 250 | 397 | 119.5 | -25.59 | 25.59 |
| 128 | 219 | 375 | 595 | 179.1 | -38.53 | 38.53 |

Interpretation:

- The observed `D=23` paths get only 22-23 reserve out of their main `k=53`
  corridor.
- Best possible high-credit placement over the same lengths improves the raw
  `c=2` count by at most one step.
- The instruction-style estimate puts the optimistic bridge-reserve case
  (`D=85`) around `10^119.5`, and the conservative case (`D=128`) around
  `10^179.1`.
- The martingale barrier gives `mu(H_128) <= 2^-128`, i.e. about `10^-38.5`.

## Corridor-Length Bound Check

Implemented `corridor-bound` from the latest `Instructions for Codex.txt`.

Output:

- `data/runs/corridor_bound_observed_20260521T194439Z.csv`
- `data/runs/corridor_bound_synthetic_20260521T194439Z.csv`
- `data/runs/corridor_bound_ceiling_20260521T194439Z.csv`

Important result: the proposed bound `L <= 0.631 * bit_length(n)` is not
empirically supported for the earlier broad macro-corridor definition. The six
observed main macro-corridors have `L / bit_length(n)` between `2.741` and
`3.536`, and the orbit value bit-length increases during the corridor rather
than being consumed.

Observed broad macro-corridor ratios:

| Start | bits(n) | L | L/bits(n) | entry bits | exit bits | bits consumed per step | peak D |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 80049391 | 27 | 74 | 2.741 | 27 | 48 | -0.284 | 23 |
| 120080895 | 27 | 74 | 2.741 | 27 | 49 | -0.297 | 23 |
| 210964383 | 28 | 94 | 3.357 | 28 | 49 | -0.223 | 22 |
| 219259131 | 28 | 98 | 3.500 | 29 | 49 | -0.204 | 22 |
| 222250543 | 28 | 99 | 3.536 | 28 | 49 | -0.212 | 22 |
| 246666523 | 28 | 87 | 3.107 | 29 | 49 | -0.230 | 22 |

Synthetic strict beta-quality test:

| bits | samples | entered beta-quality corridor | max L | max D |
| ---: | ---: | ---: | ---: | ---: |
| 50 | 100 | 0 | 0 | 4 |
| 100 | 100 | 0 | 0 | 6 |
| 200 | 100 | 0 | 0 | 5 |
| 500 | 100 | 0 | 0 | 5 |
| 1000 | 100 | 0 | 0 | 4 |

Formal ceiling table under the assumed bound:

| bits | max L=floor(B*53/84) | max reserve=floor((log2(3)-1)L) | bridge 85 | bridge 128 |
| ---: | ---: | ---: | :--- | :--- |
| 50 | 31 | 18 | False | False |
| 100 | 63 | 36 | False | False |
| 200 | 126 | 73 | False | False |
| 500 | 315 | 184 | True | True |
| 1000 | 630 | 368 | True | True |

Interpretation:

- If the `0.631 * bit_length` bound were valid for the relevant corridor
  notion, 500-bit starts would have enough single-corridor reserve capacity to
  bridge both the optimistic and conservative k=53-to-k=359 gaps.
- The observed broad macro-corridors do not satisfy that bound, so this is not
  yet a formal absolute ceiling.
- The stricter beta-quality definition appears extremely rare in random large
  starts: zero hits in 500 samples.
- The remaining theoretical gap is now sharper: define the exact k=53-quality
  object whose length is precision-limited, then prove a bit-length bound for
  that object rather than for broad reserve macro-corridors.

## Scaling Sweep

Implemented `scaling-sweep` from the latest `Instructions for Codex.txt`.

Full run:

```bash
PYTHONPATH=src python3 -m collatz_experimental_data scaling-sweep \
  --samples-per-bit-length 10000 --max-steps 50000 --workers 11 --chunk-size 100
```

Output:

- `data/runs/scaling_sweep_summary_20260521T195440Z.csv`
- `data/runs/scaling_sweep_fits_20260521T195440Z.csv`
- `data/runs/scaling_sweep_kill_20260521T195440Z.csv`

Entry frequencies and maxima:

| beta threshold | bits | positive corridor frac | quality corridor frac | max L | L/bits | max gain |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.50 | 50 | 0.2505 | 0.0381 | 28 | 0.560 | 3 |
| 0.50 | 100 | 0.2467 | 0.0423 | 19 | 0.190 | 3 |
| 0.50 | 200 | 0.2571 | 0.0414 | 19 | 0.095 | 3 |
| 0.50 | 500 | 0.2542 | 0.0434 | 24 | 0.048 | 3 |
| 0.50 | 1000 | 0.2478 | 0.0405 | 28 | 0.028 | 3 |
| 0.50 | 2000 | 0.2416 | 0.0414 | 28 | 0.014 | 2 |
| 0.10 | 50 | 0.2505 | 0.0056 | 12 | 0.240 | 2 |
| 0.10 | 100 | 0.2467 | 0.0082 | 12 | 0.120 | 2 |
| 0.10 | 200 | 0.2571 | 0.0076 | 12 | 0.060 | 2 |
| 0.10 | 500 | 0.2542 | 0.0073 | 24 | 0.048 | 3 |
| 0.10 | 1000 | 0.2478 | 0.0064 | 24 | 0.024 | 2 |
| 0.10 | 2000 | 0.2416 | 0.0063 | 12 | 0.006 | 2 |
| 0.05 | 50 | 0.2505 | 0.0014 | 12 | 0.240 | 2 |
| 0.05 | 100 | 0.2467 | 0.0016 | 12 | 0.120 | 2 |
| 0.05 | 200 | 0.2571 | 0.0019 | 12 | 0.060 | 2 |
| 0.05 | 500 | 0.2542 | 0.0018 | 24 | 0.048 | 3 |
| 0.05 | 1000 | 0.2478 | 0.0010 | 24 | 0.024 | 2 |
| 0.05 | 2000 | 0.2416 | 0.0009 | 12 | 0.006 | 2 |

Fit summary:

| beta threshold | best model by R2 | R2 | comment |
| ---: | :--- | ---: | :--- |
| 0.50 | linear | 0.3217 | weak fit; max L does not clearly grow with bits |
| 0.10 | log | 0.1967 | weak fit |
| 0.05 | log | 0.1967 | weak fit |

Interpretation:

- Roughly one quarter of random starts enter some positive-action macro-corridor.
- Quality corridors are much rarer: about `4%` for beta `<0.5`, `0.6-0.8%`
  for beta `<0.1`, and `0.09-0.19%` for beta `<0.05`.
- The longest quality corridors observed in 60,000 random starts are short:
  `L <= 28` for beta `<0.5`, and `L <= 24` for beta `<0.1` or `<0.05`.
- No convincing linear growth of quality-corridor length with bit length appears
  up to 2000-bit starts.
- Under these empirical fits, the required corridor lengths for reserves 85
  and 128 are far beyond the observed frontier. The remaining gap is no longer
  "larger integers may trivially solve it"; it is whether rare tails can produce
  much longer quality corridors than seen in 10,000 samples per bit length.

## Hard Push To 10B

Implemented `scan-range-fast` and `macro-summary`, then ran the requested
exhaustive odd-start scan:

```bash
PYTHONPATH=src python3 -m collatz_experimental_data scan-range-fast \
  --start 250000001 --stop 10000000000 --min-reserve 23 \
  --max-steps 10000 --workers 11 --chunk-odds 500000
```

Output:

- `data/runs/scan_range_250000001_10000000000_D23_20260521T203411Z.csv`
- `data/runs/macro_convergent_summary_20260521T203507Z.csv`

Scan result:

- Range: every odd integer from `250,000,001` through `10,000,000,000`
- Odd starts scanned: `4,875,000,000`
- Hits with `D >= 23`: `209`
- Maximum reserve found: `D=30`
- First observed `D=30` start: `319804831`
- No `D >= 31` start found below `10B`

Hit count by exact maximum reserve:

| max reserve | count |
| ---: | ---: |
| 23 | 115 |
| 24 | 46 |
| 25 | 17 |
| 26 | 8 |
| 27 | 5 |
| 28 | 8 |
| 29 | 7 |
| 30 | 3 |

Updated observed reserve minima:

| threshold D | smallest observed start reaching at least D |
| ---: | ---: |
| 23 | 80049391 |
| 24 | 319804831 |
| 25 | 319804831 |
| 26 | 319804831 |
| 27 | 319804831 |
| 28 | 319804831 |
| 29 | 319804831 |
| 30 | 319804831 |

Top hard-push hits:

| start | max reserve | time max | crossing | growth steps |
| ---: | ---: | ---: | ---: | ---: |
| 319804831 | 30 | 76 | 165 | 65 |
| 1410123943 | 30 | 141 | 228 | 89 |
| 2115185915 | 30 | 142 | 227 | 78 |
| 479707247 | 29 | 74 | 164 | 66 |
| 639609663 | 29 | 76 | 164 | 64 |
| 719560871 | 29 | 74 | 162 | 64 |
| 2379584155 | 29 | 137 | 225 | 81 |
| 2677032175 | 29 | 136 | 222 | 83 |
| 4015548263 | 29 | 137 | 220 | 79 |
| 8528817511 | 29 | 93 | 157 | 57 |

Macro-convergent summary over all 209 hard-push hits:

- `207 / 209` have a positive macro-corridor mapped to `k=53` or higher.
- `0 / 209` have a positive macro-corridor mapped to `k=359` or higher.
- The only two not mapped to `k=53` or higher are `D=23` starts:
  - `1845011903`, max mapped convergent `12`
  - `2287760231`, max mapped convergent `12`

Conclusion: the hard push found much higher reserve bubbles, but no escape to
the `k=359` convergent. The observed high-reserve mechanism is still bounded by
the `k=53` wall under this macro-convergent mapping.

## Hard Push To 100B

Extended the exhaustive odd-start scan from `10B` through `100B`:

```bash
PYTHONPATH=src python3 -m collatz_experimental_data scan-range-fast \
  --start 10000000001 --stop 100000000000 --min-reserve 23 \
  --max-steps 10000 --workers 11 --chunk-odds 500000
```

Output:

- `data/runs/scan_range_10000000001_100000000000_D23_20260522T044115Z.csv`
- `data/runs/macro_convergent_summary_20260522T044134Z.csv`

Scan result:

- Range: every odd integer from `10,000,000,001` through `100,000,000,000`
- Odd starts scanned: `45,000,000,000`
- Hits with `D >= 23`: `2,324`
- Maximum reserve found: `D=31`
- First observed `D=31` start: `77566362559`
- No `D >= 32` start found below `100B`

Hit count by exact maximum reserve in the `10B..100B` range:

| max reserve | count |
| ---: | ---: |
| 23 | 1155 |
| 24 | 570 |
| 25 | 282 |
| 26 | 166 |
| 27 | 82 |
| 28 | 44 |
| 29 | 18 |
| 30 | 5 |
| 31 | 2 |

Range-local reserve minima:

| threshold D | smallest start in this range reaching at least D |
| ---: | ---: |
| 23 | 10031976091 |
| 24 | 10031976091 |
| 25 | 10031976091 |
| 26 | 10031976091 |
| 27 | 10031976091 |
| 28 | 10031976091 |
| 29 | 12327829503 |
| 30 | 59436135663 |
| 31 | 77566362559 |
| 32 | none |

Updated observed reserve minima through `100B`:

| threshold D | smallest observed start reaching at least D |
| ---: | ---: |
| 23 | 80049391 |
| 24 | 319804831 |
| 25 | 319804831 |
| 26 | 319804831 |
| 27 | 319804831 |
| 28 | 319804831 |
| 29 | 319804831 |
| 30 | 319804831 |
| 31 | 77566362559 |
| 32 | none |

Top `100B` hard-push hits:

| start | max reserve | time max | crossing | growth steps |
| ---: | ---: | ---: | ---: | ---: |
| 77566362559 | 31 | 127 | 184 | 77 |
| 89798565535 | 31 | 98 | 217 | 72 |
| 59436135663 | 30 | 166 | 236 | 83 |
| 70141259775 | 30 | 166 | 235 | 88 |
| 77052745407 | 30 | 166 | 236 | 84 |
| 82282399515 | 30 | 166 | 241 | 86 |
| 92567699455 | 30 | 95 | 216 | 73 |

Macro-convergent summary over all 2,324 `10B..100B` hits:

- `2,299 / 2,324` have a positive macro-corridor mapped to `k=53` or higher.
- `0 / 2,324` have a positive macro-corridor mapped to `k=359` or higher.
- The max mapped convergent counts are `25` at `k=12` and `2,299` at `k=53`.

Conclusion: pushing from `10B` to `100B` raises the observed frontier from
`D=30` to `D=31`, but still does not produce anything in the `k=359`
convergent class. The empirical frontier remains pinned below the bridge
reserve predicted by the k=53-to-k=359 gap analysis.

## Empirical Tail Law Through 100B

Implemented `tail-law`, then fit the cumulative maximum-reserve tail from the
completed exhaustive scans through `100B`:

```bash
PYTHONPATH=src python3 -m collatz_experimental_data tail-law \
  --range 1:250000000:data/runs/scan_limit250000000_D23_20260521T190952Z.csv \
  --range 250000001:10000000000:data/runs/scan_range_250000001_10000000000_D23_20260521T203411Z.csv \
  --range 10000000001:100000000000:data/runs/scan_range_10000000001_100000000000_D23_20260522T044115Z.csv \
  --min-threshold 23 \
  --fit-min-threshold 23 --fit-min-threshold 24 --fit-min-threshold 25 \
  --fit-min-threshold 26 --fit-min-threshold 27 --fit-min-threshold 28 \
  --target-reserve 32 --target-reserve 40 --target-reserve 53 \
  --target-reserve 85 --target-reserve 128
```

Output:

- `data/runs/tail_law_thresholds_20260522T045744Z.csv`
- `data/runs/tail_law_fits_20260522T045744Z.csv`
- `data/runs/tail_law_projections_20260522T045744Z.csv`
- `data/runs/tail_law_zero_bound_20260522T045744Z.csv`

Cumulative observed tail:

| threshold D | count reaching at least D | empirical rate per odd start | log10(rate) |
| ---: | ---: | ---: | ---: |
| 23 | 2539 | 5.078e-08 | -7.294 |
| 24 | 1263 | 2.526e-08 | -7.598 |
| 25 | 647 | 1.294e-08 | -7.888 |
| 26 | 348 | 6.960e-09 | -8.157 |
| 27 | 174 | 3.480e-09 | -8.458 |
| 28 | 87 | 1.740e-09 | -8.759 |
| 29 | 35 | 7.000e-10 | -9.155 |
| 30 | 10 | 2.000e-10 | -9.699 |
| 31 | 2 | 4.000e-11 | -10.398 |

Exponential tail fits of `log10(rate) = a + bD`:

| fit window | slope b | per-D factor | R2 | log10 expected odds for D=85 | log10 expected odds for D=128 |
| :--- | ---: | ---: | ---: | ---: | ---: |
| D>=23 | -0.364 | 0.432 | 0.9700 | 29.727 | 45.389 |
| D>=24 | -0.380 | 0.417 | 0.9667 | 30.635 | 46.991 |
| D>=25 | -0.404 | 0.394 | 0.9656 | 31.953 | 49.321 |
| D>=26 | -0.438 | 0.365 | 0.9683 | 33.835 | 52.657 |
| D>=27 | -0.482 | 0.330 | 0.9731 | 36.278 | 56.998 |
| D>=28 | -0.546 | 0.284 | 0.9848 | 39.803 | 63.279 |

Zero-hit check:

- `D>=32`: `0` hits in `50,000,000,000` odd starts.
- Approximate 95% zero-hit upper rate: `6.0e-11`.
- Corresponding lower bound on expected odd starts: `10^10.222`.

Interpretation:

- The full `D>=23` tail fit is already severe: `D=128` extrapolates to about
  `10^45.4` odd starts.
- The high-end `D>=28` fit is much harsher: `D=85` extrapolates to about
  `10^39.8` odd starts, and `D=128` to about `10^63.3` odd starts.
- The observed slope steepens as the low-reserve shoulder is removed, so the
  high-end data supports a stronger wall than the broad-tail average.

## Lock 2 Finite-Word Scan

Implemented `lock2-scan` from `lock2_attack_surface.md`, then ran the first
exact exhaustive finite-word margin scan:

```bash
PYTHONPATH=src python3 -m collatz_experimental_data lock2-scan \
  --Amax 20 --top-n 200
```

Output:

- `data/runs/lock2_summary_Amax20_20260522T052451Z.json`
- `data/runs/lock2_near_failures_Amax20_20260522T052451Z.csv`

Scan result:

- Total contractive words scanned: `841,873`
- First-contractivity words: `10,236`
- All-2 zero margins: `10`
- Nontrivial zero margins: `0`
- Negative margins: `0`
- Result: Lock 2 holds throughout the `A <= 20` exact scan.

Smallest nontrivial raw margin:

| word | A | k | rho | margin | relative gap |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `(3)` | 3 | 1 | 13 | 64 | 0.984615 |

Smallest nontrivial relative gap:

| word | A | k | rho | theta | margin | relative gap |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `(3,2,1,1,1)` | 8 | 5 | 109 | 905/13 | 512 | 0.361327 |

Top near-failure family observed:

| word | A | k | rho | margin | relative gap | delta from all-2 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `(3,2,1,1,1)` | 8 | 5 | 109 | 512 | 0.361327 | 4 |
| `(4,1,1,1,1)` | 8 | 5 | 165 | 1024 | 0.477389 | 6 |
| `(2,1,1,3,1)` | 8 | 5 | 73 | 512 | 0.539515 | 4 |
| `(3,2,1,1,1,1,2,2,1,2)` | 16 | 10 | 109 | 393216 | 0.556110 | 6 |
| `(2,3,2,1,1,1,1,2,2,1)` | 16 | 10 | 145 | 524288 | 0.557389 | 6 |

Interpretation:

- The scan found no Lock 2 counterexample up to `A=20`.
- The all-2 word is the only equality case observed, exactly as predicted.
- The near-failures are not random-looking; they cluster around short
  low-exponent patterns with one high exponent and several `1`s, especially
  the `(3,2,1,1,1)` core and length-10 extensions.
- The current pure-Python exhaustive scan reaches `A=20` comfortably. Pushing
  much past that needs either optimized enumeration or a reduced first-
  contractivity scan because the finite composition count grows exponentially.

### First-Contractivity Reduction

Added `--first-contractivity-only` to scan the reduced surface where the final
step is the first contractive prefix. This matches the minimal-counterexample
reduction proposed in `lock2_attack_surface.md`.

```bash
PYTHONPATH=src python3 -m collatz_experimental_data lock2-scan \
  --Amax 20 --top-n 100 --first-contractivity-only
```

Output:

- `data/runs/lock2_summary_Amax20_20260522T054440Z.json`
- `data/runs/lock2_near_failures_Amax20_20260522T054440Z.csv`

Reduced scan result:

- First-contractivity words scanned: `10,236`
- All-2 zero margins: `1`
- Nontrivial zero margins: `0`
- Negative margins: `0`
- Result: Lock 2 holds on the reduced first-contractivity surface through
  `A <= 20`.

Closest reduced-surface case by relative gap:

| word | A | k | rho | margin | relative gap |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `(1,1,2,3)` | 7 | 4 | 7 | 256 | 0.778116 |

This is much farther from failure than the closest broad-scan near-failure
`(3,2,1,1,1)`, whose earlier prefix is already contractive. That supports the
prefix-reduction idea: many broad near-failures are not minimal-counterexample
candidates.
