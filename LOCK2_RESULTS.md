# Lock 2 Results

Run date: 2026-05-22

## Scope

This document tracks Lock 2 only: the finite-word minimal-residue descent
problem from `lock2_attack_surface.md`.

Lock 2 statement under test:

```text
For every nontrivial contractive exponent word w,
(2^A - 3^k) rho_w - B_w > 0.
```

The all-2 word is the expected equality case.

Lock 4 reserve-tail and k=53/k=359 bridge work remains separate in
`RESULTS.md`.

## Commands

Broad finite-word scan:

```bash
PYTHONPATH=src python3 -m collatz_experimental_data lock2-scan \
  --Amax 20 --top-n 200
```

First-contractivity reduced scan:

```bash
PYTHONPATH=src python3 -m collatz_experimental_data lock2-scan \
  --Amax 28 --top-n 200 --first-contractivity-only
```

## Broad Scan: Amax 20

Output:

- `data/runs/lock2_summary_Amax20_20260522T052451Z.json`
- `data/runs/lock2_near_failures_Amax20_20260522T052451Z.csv`

Result:

- Contractive words scanned: `841,873`
- First-contractivity words within that set: `10,236`
- All-2 zero margins: `10`
- Nontrivial zero margins: `0`
- Negative margins: `0`
- Lock 2 status in scan: holds

Smallest nontrivial raw margin:

| word | A | k | rho | margin | relative gap |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `(3)` | 3 | 1 | 13 | 64 | 0.984615 |

Smallest nontrivial relative gap:

| word | A | k | rho | theta | margin | relative gap |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `(3,2,1,1,1)` | 8 | 5 | 109 | 905/13 | 512 | 0.361327 |

Interpretation:

- The broad surface contains near-failures whose earlier prefixes are already
  contractive.
- Those words validate the inequality, but they are not the cleanest candidates
  for a minimal-counterexample proof.

## First-Contractivity Scan: Amax 20

Output:

- `data/runs/lock2_summary_Amax20_20260522T054440Z.json`
- `data/runs/lock2_near_failures_Amax20_20260522T054440Z.csv`

Result:

- First-contractivity words scanned: `10,236`
- All-2 zero margins: `1`
- Nontrivial zero margins: `0`
- Negative margins: `0`
- Lock 2 status in scan: holds

Closest reduced-surface case:

| word | A | k | rho | margin | relative gap |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `(1,1,2,3)` | 7 | 4 | 7 | 256 | 0.778116 |

## First-Contractivity Scan: Amax 28

Output:

- `data/runs/lock2_summary_Amax28_20260522T060707Z.json`
- `data/runs/lock2_near_failures_Amax28_20260522T060707Z.csv`

Result:

- First-contractivity words scanned: `1,422,567`
- All-2 zero margins: `1`
- Nontrivial zero margins: `0`
- Negative margins: `0`
- Lock 2 status in scan: holds

Closest reduced-surface cases:

| word | A | k | rho | margin | relative gap |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `(1,1,2,3)` | 7 | 4 | 7 | 256 | 0.778116 |
| `(1,1,1,1,4)` | 8 | 5 | 95 | 1024 | 0.829150 |
| `(1,2,2)` | 5 | 3 | 43 | 192 | 0.893023 |
| `(1,2,1,1,3)` | 8 | 5 | 219 | 2560 | 0.899192 |
| `(1,1,1,2,3)` | 8 | 5 | 175 | 2048 | 0.900220 |

Notable new high-A near-row:

| word | A | k | rho | margin | relative gap |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `(1,2,1,1,1,1,1,1,3,1,3,2,1,1,1,3,3)` | 27 | 17 | 795 | 3758096384 | 0.930991 |

Interpretation:

- Pushing the reduced surface from `A=20` to `A=28` does not improve on the
  small early near-failure `(1,1,2,3)`.
- The closest reduced-surface margins are far from zero compared with the broad
  scan's closest relative gap.
- This supports the prefix-reduction idea in `lock2_attack_surface.md`: broad
  near-failures are often not minimal-counterexample candidates.

## Threshold Bucket Attack: Amax 28

The `Amax=28` first-contractivity scan also records exact threshold buckets.
For each word, define:

```text
candidate_odd_count = number of positive odd r with r <= theta_w
```

A Lock 2 failure requires `rho_w <= theta_w`, so it can only occur inside the
word's candidate odd set.

Bucket counts:

| candidate odd residues <= theta | words |
| :--- | ---: |
| 0 | 506268 |
| 1 | 451378 |
| 2 | 86375 |
| 3 | 13766 |
| 4 | 8514 |
| 5 | 12181 |
| 6-10 | 31610 |
| 11-100 | 312475 |

Maximum candidate count:

| word | A | k | rho | candidate odd count |
| :--- | ---: | ---: | ---: | ---: |
| `(1,2,1,2,1,2,2,1,2,1,2,2,1,2,1,2,2)` | 27 | 17 | 96361467 | 54 |

Small-rho counts:

| rho threshold | words |
| :--- | ---: |
| rho <= 3 | 2 |
| rho <= 5 | 3 |
| rho <= 7 | 4 |
| rho <= 15 | 7 |
| rho <= 31 | 10 |
| rho <= 63 | 16 |
| rho <= 127 | 24 |
| rho <= 255 | 40 |
| rho <= 511 | 72 |
| rho <= 1023 | 120 |

Interpretation:

- Across all `1,422,567` reduced-surface words through `A=28`, every real
  attracting fixed point has at most `54` positive odd candidate residues below
  it.
- Therefore any failure in this scan would require `rho <= 107`.
- Only `24` scanned reduced words even have `rho <= 127`, and none fail.
- This makes the threshold-bucket proof path concrete: prove a uniform bound
  on candidate residues, then eliminate finitely many small `rho` orbit
  prefixes.

## Rho Prediction: Amax 28

Rerun with rho-predictor aggregates:

```bash
PYTHONPATH=src python3 -m collatz_experimental_data lock2-scan \
  --Amax 28 --top-n 200 --first-contractivity-only
```

Output:

- `data/runs/lock2_summary_Amax28_20260522T061201Z.json`
- `data/runs/lock2_near_failures_Amax28_20260522T061201Z.csv`

Predictor definitions:

- `theta/rho`: direct threat score; failure requires `theta/rho >= 1`.
- `candidate/rho_rank`: rounded odd-rank version; failure requires this to
  reach at least `1`.
- `rho bit slack`: `(A+1) - bit_length(rho)`, measuring how unusually small
  `rho` is relative to its modulus scale.

Rho bit-slack distribution:

| rho bit slack | words |
| :--- | ---: |
| 0 | 712158 |
| 1 | 354780 |
| 2 | 177843 |
| 3 | 88954 |
| 4 | 44313 |
| 5-8 | 41772 |
| 9-16 | 2740 |
| >16 | 7 |

Small-rho distribution:

| threshold | words |
| :--- | ---: |
| rho <= 3 | 2 |
| rho <= 5 | 3 |
| rho <= 7 | 4 |
| rho <= 15 | 7 |
| rho <= 31 | 10 |
| rho <= 63 | 16 |
| rho <= 127 | 24 |
| rho <= 255 | 40 |
| rho <= 511 | 72 |
| rho <= 1023 | 120 |

Highest nontrivial `theta/rho` threats by `A`:

| A | words | min rho | max theta/rho | max candidate/rho_rank | threat word |
| ---: | ---: | ---: | ---: | ---: | :--- |
| 5 | 4 | 3 | 0.106977 | 0.090909 | `(1,2,2)` |
| 7 | 7 | 7 | 0.221884 | 0.250000 | `(1,1,2,3)` |
| 8 | 14 | 15 | 0.170850 | 0.166667 | `(1,1,1,1,4)` |
| 13 | 141 | 207 | 0.029433 | 0.028846 | `(1,1,1,3,1,1,2,3)` |
| 16 | 790 | 359 | 0.043201 | 0.044444 | `(1,1,2,1,1,1,1,4,2,2)` |
| 24 | 81118 | 743 | 0.014327 | 0.013441 | `(1,1,2,1,1,2,1,1,2,2,1,2,1,2,4)` |
| 27 | 502523 | 795 | 0.069009 | 0.067839 | `(1,2,1,1,1,1,1,1,3,1,3,2,1,1,1,3,3)` |
| 28 | 502523 | 495 | 0.003360 | 0.004032 | `(1,1,1,2,1,1,2,1,1,2,2,1,2,1,2,4,3)` |

What a Lock 2 failure would need to look like:

1. `rho` must be extremely small for its `A` scale.
2. `theta` must be unusually high at the same time.
3. The same word must make `theta/rho >= 1`.

The current reduced scan shows those conditions separating:

- The largest theta bucket has `54` candidate odd residues, but its rho is
  `96361467`, so `theta/rho` is only about `1.12e-6`.
- The closest nontrivial `theta/rho` threat is still `(1,1,2,3)` at only
  `0.221884`.
- Only `7` of `1,422,567` reduced words have rho bit slack above `16`.

So the current prediction is: a counterexample would not merely be a long word
with a larger theta bucket. It would need a rare small-rho residue event aligned
with a high-theta first-contractivity word. The scan has not shown those two
features aligning.

## Two-Knob Theta/Rho Prediction

Added prediction knobs to `lock2-scan`:

- `--predict-rho-slack-min N`: require unusually small rho, measured by
  `(A+1) - bit_length(rho) >= N`.
- `--predict-theta-candidates-min N`: require at least `N` positive odd
  candidates below theta.
- `--predict-theta-over-rho-min X`: require direct threat score
  `theta/rho >= X`.

These knobs let the scan ask whether small-rho events and high-theta events
overlap.

### Profile 1: Small Rho + Nonempty Theta Bucket

Command:

```bash
PYTHONPATH=src python3 -m collatz_experimental_data lock2-scan \
  --Amax 28 --top-n 50 --first-contractivity-only \
  --predict-rho-slack-min 8 --predict-theta-candidates-min 1 \
  --prediction-top-n 200
```

Output:

- `data/runs/lock2_summary_Amax28_20260522T132649Z.json`
- `data/runs/lock2_predictions_Amax28_20260522T132649Z.csv`

Result:

- Matches: `3,574`
- Strongest overlap by `theta/rho`:

| word | A | k | rho | theta/rho | candidates | rho slack |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `(1,2,1,1,1,1,1,1,3,1,3,2,1,1,1,3,3)` | 27 | 17 | 795 | 0.069009 | 27 | 18 |
| `(1,1,2,1,1,1,1,4,2,2)` | 16 | 10 | 359 | 0.043201 | 8 | 8 |
| `(1,1,1,1,3,1,1,1,4,2)` | 16 | 10 | 479 | 0.029807 | 7 | 8 |

Interpretation:

- Small-rho events with nonempty theta buckets exist, but the best overlap is
  still only `theta/rho ~= 0.069`.
- The main high-A overlap is the `A=27, k=17, rho=795` family.

### Profile 2: Direct High Theta/Rho

Command:

```bash
PYTHONPATH=src python3 -m collatz_experimental_data lock2-scan \
  --Amax 28 --top-n 50 --first-contractivity-only \
  --predict-theta-over-rho-min 0.05 --prediction-top-n 200
```

Output:

- `data/runs/lock2_summary_Amax28_20260522T141423Z.json`
- `data/runs/lock2_near_failures_Amax28_20260522T141423Z.csv`
- `data/runs/lock2_theta_buckets_Amax28_20260522T141423Z.csv`
- `data/runs/lock2_small_rho_Amax28_20260522T141423Z.csv`
- `data/runs/lock2_by_A_threats_Amax28_20260522T141423Z.csv`
- `data/runs/lock2_predictions_Amax28_20260522T141423Z.csv`

Result:

- Matches: `13`
- Nontrivial matches above `theta/rho >= 0.05`:

| word | A | k | rho | theta/rho | candidates | rho slack |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `(1,1,2,3)` | 7 | 4 | 7 | 0.221884 | 1 | 5 |
| `(1,1,1,1,4)` | 8 | 5 | 95 | 0.170850 | 8 | 2 |
| `(1,2,2)` | 5 | 3 | 43 | 0.106977 | 2 | 0 |
| `(1,2,1,1,3)` | 8 | 5 | 219 | 0.100808 | 11 | 1 |
| `(1,1,1,2,3)` | 8 | 5 | 175 | 0.099780 | 9 | 1 |
| `(1,2,1,1,1,1,1,1,3,1,3,2,1,1,1,3,3)` | 27 | 17 | 795 | 0.069009 | 27 | 18 |

Interpretation:

- The high-threat list is tiny: only `13` total matches including the trivial
  all-2 equality word.
- Most direct high-threat words are small `A <= 8` patterns.
- The only large-A direct threat above `0.05` is again the `A=27, k=17,
  rho=795` word.

Current prediction:

```text
Dangerous Lock 2 candidates, if any appear later, should look like:
small rho bit-slack event + nonempty/theta-rich bucket + theta/rho rising
toward 1.
```

Through `A=28`, the strongest nontrivial direct score is only `0.221884`, and
the strongest large-A overlap is only `0.069009`.

## Implementation Notes

The first-contractivity generator now avoids enumerating all impossible
composition branches. It now builds each solvent prefix once and closes that
prefix to every final `A` that crosses contractivity, instead of rebuilding the
same prefix tree once per total `A`.

It tracks exact solvent-prefix limits using:

```text
A_j <= floor(log2(3^j))
```

and only closes a word when the final exponent produces:

```text
2^A > 3^k.
```

The `lock2_small_rho` CSV includes extra invariant columns for every
`rho <= 1023` row:

- actual exponent prefix from `rho`
- whether `rho` follows the word
- congruence validity
- image at `rho`
- odd-image check
- descent check

The Python implementation reaches the reduced `A=28` surface in under a minute
on this machine and writes all five research tables. The current Rust core is
the preferred scanner for larger first-contractivity surfaces.

## Rust Parallel Amax40 Scan

Command:

```bash
/tmp/collatz-rust-target/release/lock2_scan \
  --Amax 40 --threads 12 --split-depth 8 \
  --top-n 200 --prediction-top-n 200 \
  --out-dir data/runs \
  --stamp 20260522T_lock2_rust_parallel_Amax40 \
  --progress-every 50000000 \
  --predict-rho-slack-min 8 --predict-theta-candidates-min 1
```

Output:

- `data/runs/lock2_summary_Amax40_20260522T_lock2_rust_parallel_Amax40.json`
- `data/runs/lock2_near_failures_Amax40_20260522T_lock2_rust_parallel_Amax40.csv`
- `data/runs/lock2_theta_buckets_Amax40_20260522T_lock2_rust_parallel_Amax40.csv`
- `data/runs/lock2_small_rho_Amax40_20260522T_lock2_rust_parallel_Amax40.csv`
- `data/runs/lock2_by_A_threats_Amax40_20260522T_lock2_rust_parallel_Amax40.csv`
- `data/runs/lock2_predictions_Amax40_20260522T_lock2_rust_parallel_Amax40.csv`

Result:

- Exact first-contractivity rows: `2,110,260,858`
- Runtime: `678.16s` with `12` CPU threads and split depth `8`
- All-twos zero margins: `1`
- Nontrivial zero margins: `0`
- Negative margins: `0`
- Lock 2 holds in scan: `true`
- Prediction matches for `rho_slack >= 8` and nonempty theta bucket:
  `5,506,399`

The worst nontrivial word is unchanged:

| word | A | k | rho | theta/rho | margin |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `(1,1,2,3)` | 7 | 4 | 7 | 0.221884498480 | 256 |

The maximum theta candidate count is also unchanged from `Amax=28`:

| word | A | k | rho | odd theta candidates |
| :--- | ---: | ---: | ---: | ---: |
| `(1,2,1,2,1,2,2,1,2,1,2,2,1,2,1,2,2)` | 27 | 17 | 96361467 | 54 |

Theta candidate bucket distribution:

| odd candidate bucket | words |
| :--- | ---: |
| `0` | 700,986,328 |
| `1` | 379,496,618 |
| `2` | 160,333,550 |
| `3` | 239,114,785 |
| `4` | 272,575,962 |
| `5` | 195,015,293 |
| `6-10` | 134,738,465 |
| `11-100` | 27,999,857 |

Small-rho audit:

- Rows with `rho <= 1023`: `127`
- Nontrivial rows with `rho <= 1023`: `126`
- Nontrivial invariant failures: `0`
- The only non-descent small-rho row is the trivial all-twos equality word
  `(2)` at `rho=1`.

Scale estimates from the Rust `--count-only` path:

| Amax | first-contractivity rows |
| ---: | ---: |
| 40 | 2,110,260,858 |
| 50 | 845,112,617,459 |
| 60 | 491,178,407,520,346 |

Interpretation:

- Pushing from `A=28` to `A=40` did not create a new high-theta or small-rho
  threat.
- The global observed worst by `theta/rho` remains the tiny word `(1,1,2,3)`.
- The high-A search surface grows extremely fast. `Amax=50` is plausible only
  as a long parallel CPU job or after more pruning/load balancing.

A short `Amax=50` probe with `--threads 12 --split-depth 10 --top-n 0` used
`961` tasks and measured about `4.08M` rows/sec. At that rate, the exact
`Amax=50` surface is roughly a `57.5` hour count-only run before CSV/top-N
overhead and tail imbalance.

## Reverse Barrier Pivot

The forward `Amax=50` Rust scan was stopped at:

```text
329,000,000,000 / 845,112,617,459 rows
38.930%
```

No final CSV/JSON outputs were written by that forward run. The last sampled
rows had effectively zero `theta/rho` and large positive margins, but the scan
was too expensive for interactive use.

The replacement Rust engine is `lock2_reverse_barrier`. It does not enumerate
all words. For a target score `73/329`, it enumerates only `(A,k,rho,B)` tuples
that can satisfy:

```text
B / ((2^A - 3^k) rho) >= 73 / 329
```

then reconstructs valid first-contractivity exponent words backwards from the
candidate `B`.

Commands:

```bash
cargo build --release --bin lock2_reverse_barrier --target-dir /tmp/collatz-rust-target

/tmp/collatz-rust-target/release/lock2_reverse_barrier \
  --Amax 77 \
  --out-dir data/runs \
  --stamp 20260523T_lock2_reverse_barrier_Amax77
```

Output:

- `data/runs/lock2_reverse_barrier_summary_Amax77_20260523T_lock2_reverse_barrier_Amax77.json`
- `data/runs/lock2_reverse_barrier_hits_Amax77_20260523T_lock2_reverse_barrier_Amax77.csv`

Result:

| Amax | `(A,k)` pairs | rho candidates | B candidates | reconstructed words | hits |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 40 | 497 | 1,332 | 1,414 | 2 | 2 |
| 50 | 779 | 2,611 | 4,046 | 2 | 2 |
| 60 | 1,124 | 3,429 | 5,735 | 4 | 4 |
| 70 | 1,533 | 6,895 | 16,586 | 4 | 4 |
| 77 | 1,856 | 7,755 | 19,110 | 4 | 4 |

Hits through `Amax=77`:

| comparison | word | A | k | rho | score |
| :--- | :--- | ---: | ---: | ---: | ---: |
| above | `(2)` | 2 | 1 | 1 | 1.000000000000 |
| above | `(1,1,1,1,1,4,1,2,1,1,2,1,1,1,2,3,1,1,2,1,2,1,1,1,1,1,3,1,1,1,4,2,2,4)` | 54 | 34 | 63 | 0.572331380544 |
| above | `(1,2,1,1,1,1,2,2,1,2,1,1,2,1,1,1,2,3,1,1,2,1,2,1,1,1,1,1,3,1,1,1,4,2,2,4,3)` | 59 | 37 | 27 | 0.323159554530 |
| equal | `(1,1,2,3)` | 7 | 4 | 7 | 0.221884498480 |

Exact verification of the two nontrivial above-barrier words:

- `rho` follows the word exactly.
- The image at `rho` is odd and below `rho`.
- `first_contractivity_index == k`.
- Margins are positive.

Interpretation:

- The old hypothesis "`(1,1,2,3)` is the global worst by `theta/rho`" is false
  once the search reaches `A=54`.
- This is not a Lock 2 counterexample. The new above-barrier words still
  descend at their minimal residue.
- The correct next reverse target is the new nontrivial maximum:

```text
48215861999407177 / 84244659018371145
```

from the `A=54, k=34, rho=63` word.

The reverse engine now accepts arbitrary rational targets:

```bash
/tmp/collatz-rust-target/release/lock2_reverse_barrier \
  --Amax 77 \
  --target-num 48215861999407177 \
  --target-den 84244659018371145 \
  --out-dir data/runs \
  --stamp 20260523T_lock2_reverse_barrier_newtop_Amax77
```

Output:

- `data/runs/lock2_reverse_barrier_summary_Amax77_20260523T_lock2_reverse_barrier_newtop_Amax77.json`
- `data/runs/lock2_reverse_barrier_hits_Amax77_20260523T_lock2_reverse_barrier_newtop_Amax77.csv`

Result:

- rho candidates: `2,624`
- B candidates: `6,420`
- reconstructed words: `2`
- hits: `(2)` and the `A=54` word exactly
- no nontrivial word above the `A=54` score through `Amax=77`

## Big-Integer Reverse Barrier: Amax 100

The reverse engine was extended past the earlier fixed-width ceiling with a
hand-rolled unsigned big integer backend for the exact powers, rational
comparisons, and residue arithmetic. It now writes:

- summary JSON
- hits CSV
- top score CSV
- top rho-slack CSV
- top theta-candidate CSV
- top margin-proximity CSV

Current-top command:

```bash
/tmp/collatz-rust-target/release/lock2_reverse_barrier \
  --Amax 100 \
  --target-num 48215861999407177 \
  --target-den 84244659018371145 \
  --out-dir data/runs \
  --stamp 20260523T_lock2_reverse_big_default_Amax100 \
  --top-n 100 \
  --progress-every-a 20 \
  --slow-pair-seconds 2
```

Output:

- `data/runs/lock2_reverse_barrier_summary_Amax100_20260523T_lock2_reverse_big_default_Amax100.json`
- `data/runs/lock2_reverse_barrier_hits_Amax100_20260523T_lock2_reverse_big_default_Amax100.csv`

Result:

| Amax | target | `(A,k)` pairs | rho candidates | B candidates | reconstructed words | hits | critical failures | runtime |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | A54 current top | 3,136 | 4,299 | 12,151 | 2 | 2 | 0 | 11.626s |

Hits:

| comparison | word | A | k | rho | score |
| :--- | :--- | ---: | ---: | ---: | ---: |
| above | `(2)` | 2 | 1 | 1 | 1.000000000000 |
| equal | `(1,1,1,1,1,4,1,2,1,1,2,1,1,1,2,3,1,1,2,1,2,1,1,1,1,1,3,1,1,1,4,2,2,4)` | 54 | 34 | 63 | 0.572331380544 |

No nontrivial word exceeds the A54 score through `Amax=100`.

## Reverse Barrier Target Ladder: Amax 100

Target-ladder commands used the same binary and `--Amax 100`, changing only the
target and stamp. The current-top target is the A54 exact rational.

| target | stamp suffix | rho candidates | B candidates | reconstructed words | hits | critical failures | runtime | nontrivial words found |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| `0.9` | `t09` | 2,726 | 8,170 | 1 | 1 | 0 | 9.600s | none |
| `0.75` | `t075` | 3,275 | 9,402 | 1 | 1 | 0 | 9.731s | none |
| `48215861999407177/84244659018371145` | `default_Amax100` | 4,299 | 12,151 | 2 | 2 | 0 | 11.626s | A54 exact |
| `0.5` | `t05` | 4,931 | 13,879 | 2 | 2 | 0 | 13.377s | A54 |
| `0.4` | `t04` | 6,164 | 17,294 | 2 | 2 | 0 | 16.788s | A54 |
| `0.3` | `t03` | 8,229 | 22,997 | 3 | 3 | 0 | 22.249s | A54, A59 |
| `73/329` | `t73_329` | 11,135 | 31,099 | 4 | 4 | 0 | 29.675s | A54, A59, `(1,1,2,3)` |

Target-ladder interpretation:

- A54 remains isolated at the current-top threshold through `Amax=100`.
- No ridge appears above `0.5`; the only nontrivial reconstructed word there is
  A54 itself.
- The A59 word appears once the target falls to `0.3`, below A54 and above the
  old `(1,1,2,3)` score.
- The old `(1,1,2,3)` word appears exactly at the `73/329` threshold.
- Every ladder hit verified exactly: the orbit follows the word, the image is
  odd and below `rho`, `first_contractivity_index == k`, the margin is positive
  for nontrivial words, and there were zero critical failures.

## A54/A59 Family Analysis

Priority-1 family analysis was generated by:

```bash
PYTHONPATH=src python3 scripts/lock2_family_analysis.py \
  --out-dir data/runs \
  --hits data/runs/lock2_reverse_barrier_hits_Amax100_20260523T_lock2_reverse_barrier_family_search_Amax100.csv
```

Required outputs:

- `data/runs/lock2_prefix_analysis_A54.csv`
- `data/runs/lock2_prefix_analysis_A59.csv`
- `data/runs/lock2_family_alignment.md`

Common-structure result:

- Exact longest common prefix length: `1`, prefix `(1)`.
- Exact longest common suffix length: `0`, because A59 has an extra terminal
  `3`.
- Longest common contiguous core length: `28`.
- Shared core starts at A54 offset `6` and A59 offset `8`:

```text
(1,2,1,1,2,1,1,1,2,3,1,1,2,1,2,1,1,1,1,1,3,1,1,1,4,2,2,4)
```

Relationship result:

- A59 is not a prepend of A54.
- A59 is not an append of A54.
- A54 is not a contiguous subsequence of A59.
- A54 is not a subsequence of A59.
- A59 is not a rotation/permutation variant of A54.
- The relationship is a shared suffix/core family: different heads, same long
  internal core, and A59 appends one final `3` after the A54-family suffix
  `(4,2,2,4)`.

Actual orbit result:

| rho | target word | agreement | image after word | descends after word |
| ---: | :--- | ---: | ---: | :--- |
| 63 | A54 | 34/34 | 61 | yes |
| 27 | A59 | 37/37 | 23 | yes |

The first post-word values:

- rho `63`: `61, 23, 35, 53, 5, 1, 1`
- rho `27`: `23, 35, 53, 5, 1, 1, 1`

Neither `27` appears in the sampled rho `63` orbit prefix nor `63` in the
sampled rho `27` orbit prefix. They are not immediate predecessor/successor
pairs in the measured odd-only direction.

### Family Search Above 0.2

Requested command:

```bash
/tmp/collatz-rust-target/release/lock2_reverse_barrier \
  --Amax 100 \
  --target-num 1 --target-den 5 \
  --out-dir data/runs \
  --stamp 20260523T_lock2_reverse_barrier_family_search_Amax100 \
  --top-n 500 \
  --progress-every-a 20 \
  --slow-pair-seconds 5
```

Output:

- `data/runs/lock2_reverse_barrier_summary_Amax100_20260523T_lock2_reverse_barrier_family_search_Amax100.json`
- `data/runs/lock2_reverse_barrier_hits_Amax100_20260523T_lock2_reverse_barrier_family_search_Amax100.csv`

Result:

| Amax | target | `(A,k)` pairs | rho candidates | B candidates | reconstructed words | hits | critical failures | runtime |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | `1/5` | 3,136 | 12,354 | 34,498 | 5 | 5 | 0 | 33.652s |

Hits above `0.2`:

| word | A | k | rho | score | note |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `(2)` | 2 | 1 | 1 | 1.000000000000 | trivial |
| A54 | 54 | 34 | 63 | 0.572331380544 | current top |
| A59 | 59 | 37 | 27 | 0.323159554530 | shares A54 core |
| `(1,1,2,3)` | 7 | 4 | 7 | 0.221884498480 | old top |
| `(1,1,2,2,1,2,1,1,2,1,1,1,2,3,1,1,2,1,2,1,1,1,1,1,3,1,1,1,4,2,2,4)` | 51 | 32 | 71 | 0.204686288903 | new low member |

Grouping:

- By rho: every hit has a distinct rho: `1`, `7`, `27`, `63`, `71`.
- By suffix4: A51 and A54 end in `(4,2,2,4)`; A59 ends in `(2,2,4,3)`,
  i.e. it extends the A54-family suffix by a terminal `3`.
- Score histogram: `[0.75,1.0]`: 1, `[0.5,0.75)`: 1, `[0.3,0.4)`: 1,
  `[0.2,0.25)`: 2.

Interpretation:

- The above-0.2 family through `Amax=100` is small.
- A54 does not look like the first element of a monotone score-rising chain:
  A51 scores `0.204686`, A54 scores `0.572331`, and A59 scores `0.323160`.
- The most concrete family marker is suffix/core structure, especially the
  `(4,2,2,4)` terminal block.

## Amax 150 Attempt

A current-top `Amax=150` run was attempted with progress logging:

```bash
/tmp/collatz-rust-target/release/lock2_reverse_barrier \
  --Amax 150 \
  --target-num 48215861999407177 \
  --target-den 84244659018371145 \
  --out-dir data/runs \
  --stamp 20260523T_lock2_reverse_big_default_Amax150 \
  --top-n 100 \
  --progress-every-a 10 \
  --slow-pair-seconds 5
```

The run was interrupted after passing `A=130` because it had already consumed
more than nine minutes and was spending long intervals inside individual
zero-reconstruction `(A,k)` pairs.

Observed slow pairs before interruption:

| A | k | elapsed | rho delta | B delta | reconstructed delta |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 111 | 70 | 67.0s | 549 | 3,094 | 0 |
| 119 | 75 | 81.2s | 236 | 1,353 | 0 |
| 124 | 78 | 51.8s | 77 | 387 | 0 |
| 127 | 80 | 161.8s | 154 | 894 | 0 |

State at `A=120`:

- `(A,k)` pairs: `4,520`
- rho candidates: `5,842`
- B candidates: `19,180`
- reconstructed words: `2`
- hits: `2`
- critical failures: `0`

No new word appeared before the interruption. The bottleneck is now recursive
word reconstruction for rare expensive `(A,k)` pairs, not candidate generation.

## Reverse Reconstruction Optimization

The reverse reconstruction engine now includes two exact pruning layers:

- `--memo-exact-k`, default `15`: precomputes exact reachable `B` sets for
  remaining reconstruction lengths up to `k=15`.
- `--residue-mod-power`, default `8`: precomputes reachable residue classes
  modulo `3^8` and applies them inside the recursive reconstruction, not only
  at the root candidate `B`.

Memo statistics were added to summary JSON and console output:

- `memo_hits`
- `memo_misses`
- `memo_entries`
- `pruned_by_memo`
- `deepest_recursion`
- `largest_remaining_a_sum`
- `largest_remaining_b_bits`
- `zero_reconstruction_pairs`
- `slow_pairs`

Amax100 sanity check at the current A54 target:

| Amax | residue mod power | exact memo k | memo entries | memo hits | pruned by memo | deepest recursion | hits | critical failures | runtime |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 8 | 15 | 6,501,370 | 15,214,633 | 15,214,633 | 47 | 2 | 0 | 11.700s |

The Amax100 hit set remained unchanged: `(2)` and A54 exactly.

The requested Amax150 command was attempted with the optimized defaults:

```bash
/tmp/collatz-rust-target/release/lock2_reverse_barrier \
  --Amax 150 \
  --target-num 48215861999407177 \
  --target-den 84244659018371145 \
  --out-dir data/runs \
  --stamp 20260523T_lock2_reverse_memo_Amax150 \
  --top-n 100 \
  --progress-every-a 10 \
  --slow-pair-seconds 5
```

The run reached past `A=130` with no new reconstructed words and no critical
failures, but was interrupted inside the next large slow pair. No final
summary/hits files were written for this interrupted Amax150 run.

Optimized slow-pair profile before interruption:

| A | k | elapsed | rho delta | B delta | reconstructed delta | memo hits | memo misses | deepest recursion |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 108 | 68 | 6.0s | 119 | 580 | 0 | 11,123,183 | 9,555,918 | 52 |
| 111 | 70 | 45.0s | 549 | 3,094 | 0 | 87,819,934 | 74,684,830 | 55 |
| 116 | 73 | 13.0s | 93 | 460 | 0 | 22,843,117 | 19,609,882 | 55 |
| 119 | 75 | 56.7s | 236 | 1,353 | 0 | 105,784,639 | 93,282,205 | 58 |
| 121 | 76 | 12.9s | 48 | 212 | 0 | 23,944,387 | 19,161,708 | 57 |
| 124 | 78 | 35.0s | 77 | 387 | 0 | 67,105,918 | 55,419,620 | 59 |
| 126 | 79 | 10.6s | 32 | 120 | 0 | 13,786,163 | 17,006,892 | 58 |
| 127 | 80 | 119.9s | 154 | 894 | 0 | 207,207,007 | 181,629,164 | 62 |
| 129 | 81 | 30.8s | 44 | 195 | 0 | 57,538,441 | 48,678,953 | 60 |
| 130 | 81 | 10.3s | 11 | 27 | 0 | 29,940,913 | 13,268,436 | 60 |

Comparison to the previous unoptimized profile:

| pair | previous elapsed | optimized elapsed |
| :--- | ---: | ---: |
| A111/k70 | 67.0s | 45.0s |
| A119/k75 | 81.2s | 56.7s |
| A124/k78 | 51.8s | 35.0s |
| A127/k80 | 161.8s | 119.9s |

Interpretation:

- Recursive memo/residue pruning helps, but does not make Amax150 feasible as a
  clean interactive run.
- Candidate generation remains small; the heavy cost is still high-level
  branching inside zero-reconstruction `(A,k)` pairs before the exact memo
  frontier can terminate the subtree.
- Increasing `--memo-exact-k` to `16` raised memo entries to `24,488,475` and
  made the early slow-pair profile worse, so `15` is the better current
  setting.
- The next required optimization is meet-in-the-middle reconstruction: split
  the word at an intermediate prefix length, build reachable forward `B`
  states for one side, and match reverse states against that table instead of
  descending one exponent at a time through high-branching zero subtrees.

## Next Lock 2 Work

1. Replace recursive reconstruction with meet-in-the-middle pruning before
   retrying full `Amax=150`.
2. Cluster the reverse-barrier hit families, with A54/A59 relation first.
3. Separately classify broad near-failures like `(3,2,1,1,1)` as prefix-
   reducible rather than minimal-counterexample candidates.
