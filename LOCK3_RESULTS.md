# Lock 3 Results

Run date: 2026-05-22

## Scope

This document tracks Lock 3 only: the bounded-deficit backward solver described
in `lock3_backward_solver_instructions.txt`.

Lock 3 statement under test:

```text
For fixed C, the bounded-deficit inverse tree has no infinite positive-integer
branch except the trivial 1-cycle.
```

The first target is the critical `C=0` Sturmian path where `a_k = c_k`.

## Commands

Critical `C=0` depth-10000 run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m collatz_experimental_data \
  --out-dir data/runs/lock3_C0_N10000 \
  lock3-backward --C 0 --depth 10000
```

## Critical Path: C=0, Depth 10000

Output:

- `data/runs/lock3_C0_N10000/lock3_summary_C0.json`
- `data/runs/lock3_C0_N10000/survivors_by_depth_C0.csv`
- `data/runs/lock3_C0_N10000/valid_backward_paths_C0_N10000.csv`
- `data/runs/lock3_C0_N10000/lock3_residue_lifts_C0.csv`

Result:

- Total paths considered: `10,000`
- Final branch count: `1`
- Valid backward paths from terminal `1`: `0`
- Final residue classes: `1`
- Rho representatives stabilize: `false`
- Rho lift events: `6,399`
- Longest stable plateau: `10`
- Largest rho bit length: `15,849`
- Truncated depths: none
- Near-return depths encountered: `1, 2, 7, 12, 53, 359, 665`

Tail of survivor table:

| C | depth | total paths | valid from 1 | residue classes | branch count | notes |
| ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 0 | 9996 | 1 | 0 | 1 | 1 | ok |
| 0 | 9997 | 1 | 0 | 1 | 1 | ok |
| 0 | 9998 | 1 | 0 | 1 | 1 | ok |
| 0 | 9999 | 1 | 0 | 1 | 1 | ok |
| 0 | 10000 | 1 | 0 | 1 | 1 | ok |

Interpretation:

- The `C=0` bounded-deficit automaton remains a single critical path through
  depth `10000`.
- The representative does not stabilize as an integer candidate; it keeps
  lifting through the run, with `6,399` rho changes.
- No positive odd ancestor maps backward from terminal `1` along the critical
  depth-10000 path.
- This matches the expected Lock 3 failure mode for nontrivial infinite
  candidates: the residue representative keeps lifting instead of settling to a
  finite positive integer.

## Implementation Notes

The Python CLI disables the default Python integer-to-string digit limit for
these runs because the exact residue and modulus outputs intentionally exceed
the interpreter's default safety cap.

The `C=0` path uses incremental affine-state and rho-lift tracking so depth
10000 can be generated without recomputing each prefix from scratch.

## Bounded Paths: C=1, C=2, C=3, Depth 250

These runs were launched in parallel with the default `max_paths=200000`.

Commands:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m collatz_experimental_data \
  --out-dir data/runs/lock3_C1_N250 \
  lock3-backward --C 1 --depth 250

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m collatz_experimental_data \
  --out-dir data/runs/lock3_C2_N250 \
  lock3-backward --C 2 --depth 250

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m collatz_experimental_data \
  --out-dir data/runs/lock3_C3_N250 \
  lock3-backward --C 3 --depth 250
```

Output directories:

- `data/runs/lock3_C1_N250`
- `data/runs/lock3_C2_N250`
- `data/runs/lock3_C3_N250`

Results:

| C | depth | total paths considered | final branch count | valid from 1 | residue classes | rho lift events | longest plateau | largest rho bits | first truncated depth |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 250 | 82,104,127 | 200,000 | 0 | 200,000 | 178 | 12 | 397 | 23 |
| 2 | 250 | 102,880,298 | 200,000 | 0 | 200,000 | 177 | 11 | 397 | 18 |
| 3 | 250 | 113,654,837 | 200,000 | 0 | 200,000 | 177 | 11 | 397 | 17 |

Tail of survivor tables:

| C | depth | total paths | valid from 1 | residue classes | branch count | notes |
| ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 1 | 248 | 400,000 | 0 | 200,000 | 200,000 | truncated_at_max_paths_200000 |
| 1 | 249 | 300,000 | 0 | 200,000 | 200,000 | truncated_at_max_paths_200000 |
| 1 | 250 | 400,000 | 0 | 200,000 | 200,000 | truncated_at_max_paths_200000 |
| 2 | 248 | 517,960 | 0 | 200,000 | 200,000 | truncated_at_max_paths_200000 |
| 2 | 249 | 368,322 | 0 | 200,000 | 200,000 | truncated_at_max_paths_200000 |
| 2 | 250 | 491,398 | 0 | 200,000 | 200,000 | truncated_at_max_paths_200000 |
| 3 | 248 | 574,182 | 0 | 200,000 | 200,000 | truncated_at_max_paths_200000 |
| 3 | 249 | 408,160 | 0 | 200,000 | 200,000 | truncated_at_max_paths_200000 |
| 3 | 250 | 540,115 | 0 | 200,000 | 200,000 | truncated_at_max_paths_200000 |

Interpretation:

- All three C>0 runs hit the `max_paths=200000` cap before depth 250.
- No retained path produced a positive odd ancestor from terminal `1`.
- These are capped search results, not exhaustive C>0 depth-250 proofs.
- Runtime and memory were dominated by retaining long prefix states and exact
  residue-class work for many branches.
- Future C>0 runs should use stderr progress logging and a compact census mode
  that separates branch/residue summary scans from full exact CSV export.

## Critical Path Census: C=0, Depth 1000000

This run used the optimized exact C=0 rho-lift recurrence and skipped terminal
divisibility checks. It also disabled path-row and lift-row CSV emission to
avoid writing enormous exact residue files.

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m collatz_experimental_data \
  --out-dir data/runs/lock3_C0_N1000000 \
  lock3-backward --C 0 --depth 1000000 \
  --max-lift-rows 0 --max-path-rows 0 \
  --skip-terminal-checks --progress-every 100000
```

Output:

- `data/runs/lock3_C0_N1000000/lock3_summary_C0.json`
- `data/runs/lock3_C0_N1000000/survivors_by_depth_C0.csv`
- `data/runs/lock3_C0_N1000000/valid_backward_paths_C0_N1000000.csv`
- `data/runs/lock3_C0_N1000000/lock3_residue_lifts_C0.csv`

Result:

- Total paths considered: `1,000,000`
- Final branch count: `1`
- Final residue classes: `1`
- Rho representatives stabilize: `false`
- Rho lift events: `646,205`
- Longest stable plateau: `12`
- Largest rho bit length: `1,584,958`
- Truncated depths: none
- Terminal checks skipped: `true`
- Near-return depths encountered: `1, 2, 7, 12, 53, 359, 665, 16266, 31867, 111202`

Progress checkpoints:

| depth | rho bits | elapsed seconds |
| ---: | ---: | ---: |
| 100,000 | 158,495 | 7.2 |
| 200,000 | 316,992 | 27.8 |
| 300,000 | 475,486 | 61.9 |
| 400,000 | 633,986 | 109.1 |
| 500,000 | 792,478 | 169.8 |
| 600,000 | 950,978 | 243.9 |
| 700,000 | 1,109,474 | 331.5 |
| 800,000 | 1,267,967 | 432.5 |
| 900,000 | 1,426,465 | 547.4 |
| 1,000,000 | 1,584,958 | 677.7 |

Interpretation:

- The C=0 critical path remains a single bounded-deficit branch through depth
  `1,000,000`.
- The rho representative still does not stabilize; it changes `646,205` times.
- This is a census result, not a terminal-backward divisibility run, because
  terminal checks were intentionally skipped for scale.

## C>0 Census Mode: C=1, C=2, C=3, Depth 250

This implements the redesign from `lock3_census_redesign_plan.md`: count
branches by compact deficit state instead of retaining every path.

Command pattern:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m collatz_experimental_data \
  --out-dir data/runs/lock3_C{C}_N250_census \
  lock3-backward --C {C} --depth 250 --mode census --progress-every 50
```

Output directories:

- `data/runs/lock3_C1_N250_census`
- `data/runs/lock3_C2_N250_census`
- `data/runs/lock3_C3_N250_census`

Each directory contains:

- `lock3_summary_C{C}.json`
- `lock3_census_C{C}.csv`
- `lock3_events_C{C}.csv`
- `lock3_witnesses_C{C}.jsonl`

Results:

| C | depth | symbolic branch count | merged states | max branch multiplicity | representative rho lifts | representative longest plateau | max rho bits | events | witnesses |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 250 | 122399332575670000582209165454952445557127439659596140423151616 | 2 | 61199666287835000291104582727476222778563719829798070211575808 | 172 | 4 | 397 | 474 | 14 |
| 2 | 250 | 781816387701927478333413516262892421459298438433175107096335857433169008687590984909 | 3 | 318199902333457131922416104628732444452966133379159052301986805766370232943838726751 | 172 | 4 | 397 | 476 | 18 |
| 3 | 250 | 8673317280575367467735888339610419904648993847781640663519181869570313392357733020537290489856 | 4 | 3211169508436331872705483570276845128287048111817852573141886458418663860569280321934076674048 | 172 | 4 | 397 | 477 | 21 |

Interpretation:

- C=1,2,3 now run through depth `250` without truncation in census mode.
- The branch counts are exact symbolic counts under bounded-deficit transitions.
- The merge strategy is currently deficit-state aggregation, so merged states
  are `C+1`.
- Rho and plateau metrics are tracked on representative witnesses for each
  merged deficit state. They are telemetry, not exhaustive per-branch rho proof.
- Valid-from-1 is not yet tracked in census mode; that requires a symbolic
  backward-integrality gate.

## C>0 Residue-Signature Census: C=1, C=2, C=3, Depth 250

This extends census mode with symbolic terminal-residue compatibility tracking.
The merge key is:

```text
(deficit_state, terminal_residue_signature mod 3^m)
```

For these runs, `m=8`, so the residue modulus is `3^8 = 6561`.

Command pattern:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m collatz_experimental_data \
  --out-dir data/runs/lock3_C{C}_N250_residue_census \
  lock3-backward --C {C} --depth 250 --mode census \
  --residue-mod-power 8 --progress-every 50
```

Output directories:

- `data/runs/lock3_C1_N250_residue_census`
- `data/runs/lock3_C2_N250_residue_census`
- `data/runs/lock3_C3_N250_residue_census`

Results:

| C | depth | residue modulus | symbolic branch count | merged states | valid from 1 mod 6561 | valid residue signatures | representative rho lifts | representative longest plateau | max rho bits |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 250 | 6561 | 122399332575670000582209165454952445557127439659596140423151616 | 216 | 0 | 212 | 177 | 6 | 397 |
| 2 | 250 | 6561 | 781816387701927478333413516262892421459298438433175107096335857433169008687590984909 | 1280 | 0 | 996 | 177 | 6 | 397 |
| 3 | 250 | 6561 | 8673317280575367467735888339610419904648993847781640663519181869570313392357733020537290489856 | 3522 | 405923743889866397297628576490369298473413697273575748129328290527100198126189645991116800 | 2072 | 177 | 6 | 397 |

Interpretation:

- The branch counts remain exact symbolic counts.
- The merged state counts are now residue-aware, not just deficit-state counts.
- `valid from 1` means compatible with terminal value `1` modulo `3^8`; it is
  not yet a full exact terminal-backward proof through depth 250.
- C=1 and C=2 show no terminal-1 compatibility modulo `6561` at depth 250.
- C=3 has terminal-1 compatible residue mass modulo `6561`, so the next useful
  run is C=3 with a larger residue window, or witness inspection for those
  compatible residue signatures.

## C=3 Higher Residue Windows: m=10, 12, 14, 16 at Depth 250

Update date: 2026-05-23

The C=3 residue-signature census was extended beyond `m=8`. The key change is
that terminal-1 compatibility is monotone under increasing residue modulus for a
fixed depth: compatibility modulo `3^16` implies compatibility modulo `3^14`,
`3^12`, etc. The m=10 run already killed terminal-1 compatibility at depth
250; m=12, m=14, and m=16 confirm the lift.

The m=16 run uses the Rust census engine:

```bash
cargo build --release --bin lock3_census --target-dir /tmp/collatz-rust-target

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m collatz_experimental_data \
  --out-dir data/runs/lock3_C3_N250_residue_m16_rust_rho \
  lock3-backward --C 3 --depth 250 --mode census --engine rust \
  --residue-mod-power 16 --progress-every 25 \
  --resume data/runs/lock3_C3_N150_residue_m16_rust_rho/lock3_C3_m16.checkpoint.bin \
  --checkpoint-path data/runs/lock3_C3_N250_residue_m16_rust_rho/lock3_C3_m16.checkpoint.bin \
  --checkpoint-every 25
```

Output directories:

- `data/runs/lock3_C3_N250_residue_m10`
- `data/runs/lock3_C3_N250_residue_m12`
- `data/runs/lock3_C3_N250_residue_m14`
- `data/runs/lock3_C3_N150_residue_m16_rust_rho`
- `data/runs/lock3_C3_N250_residue_m16_rust_rho`

Final depth-250 results:

| engine | m | residue modulus | symbolic branch count | merged states | valid from 1 | terminal-1 compatible signatures | valid residue signatures | rho lifts | longest plateau | max rho bits |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Python | 10 | 59049 | 8673317280575367467735888339610419904648993847781640663519181869570313392357733020537290489856 | 20566 | 0 | 0 | 13380 | 177 | 7 | 397 |
| Python | 12 | 531441 | 8673317280575367467735888339610419904648993847781640663519181869570313392357733020537290489856 | 117281 | 0 | 0 | 82536 | 177 | 11 | 397 |
| Python | 14 | 4782969 | 8673317280575367467735888339610419904648993847781640663519181869570313392357733020537290489856 | 632638 | 0 | 0 | 479103 | 177 | 11 | 397 |
| Rust | 16 | 43046721 | 8673317280575367467735888339610419904648993847781640663519181869570313392357733020537290489856 | 3775395 | 0 | 0 | 2985549 | 165 | 13 | 397 |

The m=16 run was first pushed to depth 150, then resumed from the depth-150
checkpoint and pushed to depth 250. Final output:

- `data/runs/lock3_C3_N250_residue_m16_rust_rho/lock3_summary_C3.json`
- `data/runs/lock3_C3_N250_residue_m16_rust_rho/lock3_census_C3.csv`
- `data/runs/lock3_C3_N250_residue_m16_rust_rho/lock3_events_C3.csv`
- `data/runs/lock3_C3_N250_residue_m16_rust_rho/lock3_witnesses_C3.jsonl`
- `data/runs/lock3_C3_N250_residue_m16_rust_rho/lock3_C3_m16.checkpoint.bin`

m=16 checkpoint frontier:

| depth | merged states | valid residue signatures | valid from 1 | terminal-1 compatible signatures | rho lifts | longest plateau | max rho bits |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 25 | 3249128 | 2583535 | 0 | 0 | 24 | 12 | 40 |
| 50 | 3775395 | 2985549 | 0 | 0 | 41 | 14 | 80 |
| 75 | 2900630 | 2289099 | 0 | 0 | 59 | 12 | 119 |
| 100 | 3132841 | 2477115 | 0 | 0 | 72 | 14 | 159 |
| 125 | 3963042 | 3086458 | 0 | 0 | 89 | 13 | 199 |
| 150 | 3199775 | 2522983 | 0 | 0 | 103 | 13 | 238 |
| 175 | 3294372 | 2619663 | 0 | 0 | 117 | 14 | 278 |
| 200 | 2913211 | 2289593 | 0 | 0 | 130 | 13 | 317 |
| 225 | 3249128 | 2583535 | 0 | 0 | 149 | 13 | 357 |
| 250 | 3775395 | 2985549 | 0 | 0 | 165 | 13 | 397 |

Interpretation:

- The m=8 C=3 result had nonzero terminal-1-compatible residue mass, but m=10
  kills it at depth 250.
- The terminal-1-compatible signature count remains exactly zero through
  m=10, m=12, m=14, and m=16 at depth 250.
- The symbolic branch mass at depth 250 is astronomically large, but the
  residue-aware merged frontier remains in the low millions at m=16.
- The m=16 merged frontier oscillates. It contracts and expands rather than
  growing monotonically; depths 225 and 250 repeat the merged/residue counts
  from depths 25 and 50.
- The Rust engine restores representative rho diagnostics while avoiding the
  Python object and garbage-collection overhead that crashed the m=16 Python
  run. Full path-heavy witness export remains empty here because there are no
  terminal-1-compatible signatures to witness.

## Rust Census Instrumentation and Extended C=3/C=4 Runs

Update date: 2026-05-23

The Rust census engine now reports terminal-1 compatibility in two distinct
ways:

- `exact_depth_valid1`: per-row exact-depth terminal-1-compatible mass.
- `ever_seen_valid1`: summary/progress boolean showing whether any depth in the
  run ever had nonzero `exact_depth_valid1`.

This matters because exact-depth terminal compatibility is not monotone in
depth. A run can have a transient terminal-1-compatible frontier at an earlier
depth and still end with zero terminal-1-compatible mass at the final depth.

Validation after instrumentation:

```bash
cargo build --release --bin lock3_census --target-dir /tmp/collatz-rust-target

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m collatz_experimental_data \
  --out-dir /tmp/lock3_instrument_check \
  lock3-backward --C 3 --depth 25 --mode census --engine rust \
  --residue-mod-power 10 --progress-every 25

PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_exact.py
```

Test result: `24 passed`. Pytest emitted cache-write warnings only because the
test cache location was read-only in this run environment.

### C=3, m=10, Depth 500 and 1000

Commands:

```bash
/tmp/collatz-rust-target/release/lock3_census \
  --C 3 --depth 500 --residue-mod-power 10 \
  --out-dir data/runs/lock3_C3_N500_residue_m10_rust \
  --progress-every 25 \
  --checkpoint-path data/runs/lock3_C3_N500_residue_m10_rust/lock3_C3_m10.checkpoint.bin \
  --checkpoint-every 50

/tmp/collatz-rust-target/release/lock3_census \
  --C 3 --depth 1000 --residue-mod-power 10 \
  --out-dir data/runs/lock3_C3_N1000_residue_m10_rust \
  --progress-every 50 \
  --resume data/runs/lock3_C3_N500_residue_m10_rust/lock3_C3_m10.checkpoint.bin \
  --checkpoint-path data/runs/lock3_C3_N1000_residue_m10_rust/lock3_C3_m10.checkpoint.bin \
  --checkpoint-every 100
```

Results:

| C | depth | m | residue modulus | merged states | valid from 1 | ever seen valid1 | terminal-1 compatible signatures | valid residue signatures | rho lifts | longest plateau | max rho bits |
| ---: | ---: | ---: | ---: | ---: | ---: | :---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 500 | 10 | 59049 | 18332 | 0 | false | 0 | 11876 | 323 | 8 | 793 |
| 3 | 1000 | 10 | 59049 | 14447 | 0 | false | 0 | 9499 | 664 | 15 | 1585 |

Interpretation:

- C=3 remains terminal-1 clean at `m=10` through depth `1000`.
- `ever_seen_valid1=false` means there were no transient terminal-1-compatible
  depths in either run.
- The depth-1000 run resumed from the depth-500 checkpoint cleanly.

### C=4, Depth 250, m=8/10/12/14 Sweep

Command pattern:

```bash
/tmp/collatz-rust-target/release/lock3_census \
  --C 4 --depth 250 --residue-mod-power {m} \
  --out-dir data/runs/lock3_C4_N250_residue_m{m}_rust \
  --progress-every 25 \
  --checkpoint-path data/runs/lock3_C4_N250_residue_m{m}_rust/lock3_C4_m{m}.checkpoint.bin \
  --checkpoint-every 50
```

Results:

| C | depth | m | residue modulus | merged states | valid from 1 | ever seen valid1 | terminal-1 compatible signatures | valid residue signatures | rho lifts | longest plateau | max rho bits | exact valid1 depths |
| ---: | ---: | ---: | ---: | ---: | ---: | :---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 4 | 250 | 8 | 6561 | 6924 | 101660745172937964280541330302039387234366340167420832905899417564407314797338533725396414770813 | true | 2 | 3139 | 164 | 8 | 397 | 14-250 |
| 4 | 250 | 10 | 59049 | 45670 | 4439897250448957840066415670298717411019167186031688444431405791931970772650136229471068224105 | true | 1 | 23091 | 165 | 8 | 397 | 198 hit depths from 18-250 |
| 4 | 250 | 12 | 531441 | 291952 | 0 | true | 0 | 160981 | 165 | 12 | 397 | 53, 106, 159, 212 |
| 4 | 250 | 14 | 4782969 | 1790110 | 0 | false | 0 | 1068261 | 165 | 12 | 397 | none |

Interpretation:

- C=4 has lower-resolution terminal-1-compatible signatures at `m=8` and
  `m=10`.
- At `m=12`, terminal-1 compatibility appears only at transient exact depths
  `53`, `106`, `159`, and `212`; the final depth-250 frontier has zero
  terminal-1-compatible mass.
- At `m=14`, no terminal-1-compatible mass appears at any depth through 250.
- Compatibility is monotone only in the upward-to-downward direction:
  compatibility modulo `3^14` would imply compatibility modulo `3^12`, but
  compatibility modulo `3^12` does not imply a valid lift modulo `3^14`.
  Therefore the C=4 low-mod hits are coarse residue candidates that fail to
  lift through `m=14` in this model.

Output directories:

- `data/runs/lock3_C3_N500_residue_m10_rust`
- `data/runs/lock3_C3_N1000_residue_m10_rust`
- `data/runs/lock3_C4_N250_residue_m8_rust`
- `data/runs/lock3_C4_N250_residue_m10_rust`
- `data/runs/lock3_C4_N250_residue_m12_rust`
- `data/runs/lock3_C4_N250_residue_m14_rust`

Log files:

- `logs/lock3_C3_N500_residue_m10_rust.log`
- `logs/lock3_C3_N1000_residue_m10_rust.log`
- `logs/lock3_C4_N250_residue_m8_rust.log`
- `logs/lock3_C4_N250_residue_m10_rust.log`
- `logs/lock3_C4_N250_residue_m12_rust.log`
- `logs/lock3_C4_N250_residue_m14_rust.log`

## Collapse-Threshold Curve: C=4 Deep Run, C=5/C=6 Baselines

Update date: 2026-05-23

The current Lock 3 working model is a collapse-threshold curve:

```text
C -> first residue precision m where terminal-1 compatibility disappears
```

Here `m` means compatibility modulo `3^m`. A lower `m` can show false
terminal-1-compatible residue shadows. The meaningful threshold is the first
tested `m` where:

```text
valid_from_1_count = 0
terminal_1_compatible_signature_count = 0
ever_seen_valid1 = false
```

That condition means the run saw no terminal-1-compatible mass at any exact
depth in the tested interval.

### Completed Results

| C | depth | m | residue modulus | final valid1 | ever seen valid1 | compatible signatures | merged states | valid residue signatures | status |
| ---: | ---: | ---: | ---: | ---: | :---: | ---: | ---: | ---: | :--- |
| 3 | 1000 | 10 | 59049 | 0 | false | 0 | 14447 | 9499 | clean through depth 1000 |
| 4 | 250 | 12 | 531441 | 0 | true | 0 | 291952 | 160981 | transient hits only |
| 4 | 250 | 14 | 4782969 | 0 | false | 0 | 1790110 | 1068261 | clean |
| 4 | 500 | 14 | 4782969 | 0 | false | 0 | 1562294 | 942739 | clean through depth 500 |
| 5 | 250 | 10 | 59049 | nonzero | true | 2 | 80334 | 31555 | persistent at low precision |
| 5 | 250 | 12 | 531441 | nonzero | true | 1 | 559285 | 244477 | persistent at low precision |
| 5 | 250 | 14 | 4782969 | 0 | true | 0 | 3756578 | 1806564 | transient hits only |
| 6 | 250 | 10 | 59049 | nonzero | true | 3 | 120600 | 36678 | persistent at low precision |
| 6 | 250 | 12 | 531441 | nonzero | true | 2 | 896828 | 307120 | persistent at low precision |

### C=4, m=14, Depth 500

Command:

```bash
/tmp/collatz-rust-target/release/lock3_census \
  --C 4 --depth 500 --residue-mod-power 14 \
  --out-dir data/runs/lock3_C4_N500_residue_m14_rust \
  --progress-every 25 \
  --checkpoint-path data/runs/lock3_C4_N500_residue_m14_rust/lock3_C4_m14.checkpoint.bin \
  --checkpoint-every 50
```

Final result:

- `valid_from_1_count`: `0`
- `ever_seen_valid1`: `false`
- `terminal_1_compatible_signature_count`: `0`
- `merged_state_count`: `1562294`
- `valid_residue_count`: `942739`
- `rho_lift_count`: `323`
- `longest_plateau`: `13`
- `max_rho_bit_length`: `793`

Interpretation:

- C=4 is clean at `m=14` not only through depth `250`, but through depth `500`.
- The previous C=4/m=12 transient ladder at depths `53`, `106`, `159`, and
  `212` does not reappear at `m=14`.
- This is the current control case for the collapse-threshold curve: after a
  clean precision is found, pushing depth did not recreate compatibility.

### C=5, m=10/12/14

C=5 remains terminal-1-compatible at low precision:

- At `m=10`, final `valid_from_1_count` is nonzero and there are `2`
  terminal-1-compatible signatures at depth `250`.
- At `m=12`, final `valid_from_1_count` is nonzero and there is `1`
  terminal-1-compatible signature at depth `250`.

At `m=14`, C=5 changes character:

- Final `valid_from_1_count`: `0`
- Final `terminal_1_compatible_signature_count`: `0`
- `ever_seen_valid1`: `true`
- `transient_valid1_depths`:
  `24, 31, 36, 43, 48, 53, 55, 60, 65, 72, 77, 84, 89, 96, 101, 106, 108, 113, 118, 125, 130, 137, 142, 149, 154, 159, 161, 166, 171, 178, 183, 190, 195, 202, 207, 212, 214, 219, 224, 231, 236, 243, 248`

Interpretation:

- C=5 is not clean at `m=14`, because `ever_seen_valid1=true`.
- The final frontier is zero, so the m=14 compatibility is transient rather
  than persistent.
- The transient set includes the C=4/m=12 ladder depths `53`, `106`, `159`,
  and `212`, but it is broader than a pure 53-multiple ladder.
- The next required curve point is C=5 at `m=16`. If that is not clean, test
  `m=18`, then `m=20`.

### C=6 Lower-Tier Baseline

C=6 was run at the lower tiers to establish the left side of its threshold
band:

- At `m=10`, final `valid_from_1_count` is nonzero and there are `3`
  terminal-1-compatible signatures.
- At `m=12`, final `valid_from_1_count` is nonzero and there are `2`
  terminal-1-compatible signatures.

Interpretation:

- C=6 is definitely not sieved by `m=10` or `m=12`.
- The useful next C=6 tests are `m=14`, `m=16`, and possibly above, depending
  on where the first clean tier appears.

### Interrupted Next Step

C=5 at `m=16`, depth `250`, was started after C=4 and C=5 m=14 completed:

```bash
/tmp/collatz-rust-target/release/lock3_census \
  --C 5 --depth 250 --residue-mod-power 16 \
  --out-dir data/runs/lock3_C5_N250_residue_m16_rust \
  --progress-every 25 \
  --checkpoint-path data/runs/lock3_C5_N250_residue_m16_rust/lock3_C5_m16.checkpoint.bin \
  --checkpoint-every 50
```

The weaker system crashed before the first progress checkpoint. The output
directory exists, but no summary JSON and no checkpoint were written.

A bounded probe was then run locally to measure the early growth curve:

```bash
/tmp/collatz-rust-target/release/lock3_census \
  --C 5 --depth 20 --residue-mod-power 16 \
  --out-dir data/runs/lock3_C5_N20_residue_m16_probe \
  --progress-every 1 \
  --checkpoint-path data/runs/lock3_C5_N20_residue_m16_probe/lock3_C5_m16_N20.checkpoint.bin \
  --checkpoint-every 5
```

Probe result:

| C | depth | m | valid1 | ever_seen_valid1 | compatible signatures | merged states | valid residues | checkpoint |
| ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| 5 | 20 | 16 | 0 | false | 0 | 5,256,767 | 3,443,705 | 572,989,900 bytes |

The probe is clean, but it is not a threshold result because it only reaches
depth `20`. It explains the crash: even before depth `25`, the m=16 frontier
already has more than `5.2M` merged states and a `547 MiB` checkpoint.

Conclusion:

- Do not treat C=5/m16 as solved from the depth-20 probe.
- Do not restart full C=5/N250/m16 blindly on a weaker machine.
- The next full C=5/m16 attempt should either run on the larger-memory system
  with explicit monitoring, or use a more memory-lean census representation.

### C=5, m=16 Memory-Lean Rust Probes

The Rust census engine now has a memory-lean mode for this attack surface:

- `--memory-lean` uses count-only frontier states and does not retain witness
  paths or representative rho data.
- `--no-checkpoint` disables the large checkpoint file.
- count-only lean checkpoints can be written/resumed without witness data.
- `--memory-cap-mb` aborts if peak RSS crosses the configured cap.
- census rows and summaries now record `current_rss_kb` and `peak_rss_kb`.
- summaries record `checkpoint_size_bytes`.
- keys are packed into one `u64` as `(deficit, residue)` instead of storing a
  wider struct.

Verification build:

```bash
cargo build --release --bin lock3_census --target-dir /tmp/collatz-rust-target
```

Checkpoint/resume smoke test:

```bash
/tmp/collatz-rust-target/release/lock3_census \
  --C 5 --depth 8 --residue-mod-power 16 \
  --out-dir data/runs/lock3_C5_checkpoint_smoke_part1 \
  --progress-every 4 --label lock3 \
  --memory-lean \
  --checkpoint-path data/runs/lock3_C5_checkpoint_smoke/lock3_C5_m16_lean.checkpoint.bin \
  --checkpoint-every 4 --memory-cap-mb 1000

/tmp/collatz-rust-target/release/lock3_census \
  --C 5 --depth 10 --residue-mod-power 16 \
  --out-dir data/runs/lock3_C5_checkpoint_smoke_resume \
  --progress-every 1 --label lock3 \
  --memory-lean \
  --checkpoint-path data/runs/lock3_C5_checkpoint_smoke/lock3_C5_m16_lean.checkpoint.bin \
  --checkpoint-every 2 \
  --resume data/runs/lock3_C5_checkpoint_smoke/lock3_C5_m16_lean.checkpoint.bin \
  --memory-cap-mb 1000
```

The resumed run reached depth `10` with the expected direct-probe counts:
`merged_state_count=961`, `valid_residue_count=768`, `exact_depth_valid1=0`.

The old C=5/m16 depth-20 probe had a `572,989,900` byte checkpoint. The
memory-lean packed probe has no checkpoint and reproduces the exact same
frontier counts:

| C | depth | m | valid1 | ever_seen_valid1 | compatible signatures | merged states | valid residues | peak RSS |
| ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| 5 | 20 | 16 | 0 | false | 0 | 5,256,767 | 3,443,705 | 1,897,840 KiB |
| 5 | 21 | 16 | 0 | false | 0 | 9,382,677 | 5,766,632 | 3,703,936 KiB |
| 5 | 22 | 16 | 0 | false | 0 | 11,319,221 | 6,659,427 | 4,974,648 KiB |
| 5 | 25 | 16 | 0 | false | 0 | 23,093,475 | 12,069,875 | 14,447,624 KiB |

Depth `25` is the important recovered boundary: the weaker machine crashed
before this point with checkpointed witness retention. The memory-lean packed
run reaches it cleanly and still has `exact_depth_valid1=0`.

Current depth-25 outputs:

- `data/runs/lock3_C5_N25_residue_m16_lean_packed_probe/lock3_summary_C5.json`
- `data/runs/lock3_C5_N25_residue_m16_lean_packed_probe/lock3_census_C5.csv`
- `data/runs/lock3_C5_N25_residue_m16_lean_packed_probe/lock3_events_C5.csv`
- `data/runs/lock3_C5_N25_residue_m16_lean_packed_probe/lock3_witnesses_C5.jsonl`

This is still not the full C=5/m16 proof point, because the target remains
depth `250`. It does show that the crash mode was largely representation and
checkpoint pressure, not an immediate mathematical explosion at m=16.

### C=5, m=16 Full Depth-250 Attempt

The full run was started as a user systemd transient service so it survives the
Codex shell lifecycle:

```bash
systemd-run --user --unit=lock3-c5-m16-lean --collect \
  --property=WorkingDirectory=/mnt/ForgeRealm/collatz-experimental-data \
  --property=StandardOutput=append:/mnt/ForgeRealm/collatz-experimental-data/logs/lock3_C5_N250_m16_lean_packed_20260523.log \
  --property=StandardError=append:/mnt/ForgeRealm/collatz-experimental-data/logs/lock3_C5_N250_m16_lean_packed_20260523.log \
  /tmp/collatz-rust-target/release/lock3_census \
    --C 5 --depth 250 --residue-mod-power 16 \
    --out-dir data/runs/lock3_C5_N250_residue_m16_lean_packed \
    --progress-every 1 --label lock3 \
    --memory-lean \
    --checkpoint-path data/runs/lock3_C5_N250_residue_m16_lean_packed/lock3_C5_m16_lean.checkpoint.bin \
    --checkpoint-every 5 \
    --resume data/runs/lock3_C5_N250_residue_m16_lean_packed/lock3_C5_m16_lean.checkpoint.bin \
    --memory-cap-mb 30000
```

Live status commands:

```bash
systemctl --user status lock3-c5-m16-lean.service --no-pager
tail -n 40 logs/lock3_C5_N250_m16_lean_packed_20260523.log
```

The first `nohup` attempt was killed by the launch context after depth `15`.
The systemd run resumed from the depth-10 lean checkpoint and is the durable
attempt to follow.

Latest observed live progress:

| depth | valid1 | compatible signatures | merged states | valid residues | peak RSS | checkpoint |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 25 | 0 | 0 | 23,093,475 | 12,069,875 | 14,447,576 KiB | 441 MiB |

### Collapse-Curve Artifacts

The curve table and SVG were generated with:

```bash
python3 scripts/lock3_curve_analysis.py
```

Outputs:

- `data/runs/lock3_curve/lock3_collapse_curve_runs.csv`
- `data/runs/lock3_curve/lock3_collapse_thresholds.csv`
- `data/runs/lock3_curve/lock3_collapse_curve.svg`
- `data/runs/lock3_curve/lock3_collapse_curve.md`

Current corrected threshold table, excluding low-depth probes:

| C | first clean m | first clean depth | max dirty m | max completed m | status |
| ---: | ---: | ---: | ---: | ---: | :--- |
| 1 | 8 | 250 |  | 8 | clean-only |
| 2 | 8 | 250 |  | 8 | clean-only |
| 3 | 10 | 250 | 8 | 16 | bracketed |
| 4 | 14 | 250 | 12 | 14 | bracketed |
| 5 |  |  | 14 | 14 | open |
| 6 |  |  | 12 | 12 | open |

Low-depth probes excluded from threshold calls:

| C | probe |
| ---: | :--- |
| 3 | m16/N150/clean |
| 5 | m16/N20/clean |

### Curve Interpretation

The first-blush curve is:

| C | current threshold bracket |
| ---: | :--- |
| 3 | clean by `m=10` |
| 4 | dirty/transient at `m=12`, clean at `m=14` |
| 5 | persistent at `m=10/12`, transient at `m=14`, threshold is `>14` |
| 6 | persistent at `m=10/12`, threshold is `>12` |

This is evidence for a widening-strip collapse curve. As the allowed deficit
width `C` increases, false terminal-compatible shadows survive to higher
precision, but the completed C=3 and C=4 tests show that sharpened residue
precision can still erase them. The next task is to locate the clean bands for
C=5, C=6, and then use those bands to predict targeted tests for C=7 and C=8.

This is the opposite computational role from Lock 4. Lock 4 exposes persistent
frontier structure; Lock 3 is measuring how residue precision collapses bounded
gliding candidates.

## Transient Shadow Lifecycle Heatmap: C=1..4

Update date: 2026-05-23

The scanner was extended with transient-shadow lifecycle fields in the
`--memory-lean` path:

- `live_valid1_count`
- `valid1_shadow_birth_count`
- `valid1_shadow_death_count`
- `max_valid1_shadow_lifetime`
- `valid1_shadow_persisted_from_previous`
- `first_valid1_depth`
- `last_valid1_depth`
- `clean_prefix_depth`

The purpose is to build a heatmap/surface over `(C, m)` rather than a single
threshold line. Each cell records whether terminal-1 shadows are never born,
born transiently, or live at final depth, and when they first/last appear.

Operational refinement rule:

```text
If m is dirty, run the next unresolved adjacent m.
If m is clean but the previous tested m is dirty, run the in-between m.
```

This avoids blind odd-m sweeps while still resolving the transition bands.

Lifecycle audit command pattern:

```bash
/tmp/collatz-rust-target/release/lock3_census \
  --C {C} --depth 250 --residue-mod-power {m} \
  --out-dir data/runs/lock3_C{C}_N250_residue_m{m}_lifecycle_lean \
  --progress-every 50 \
  --memory-lean --no-checkpoint
```

Dense midpoint runs used suffix `lifecycle_dense` for m=10 and m=11.

### Heatmap Cells

| C | m | state | first valid1 depth | last valid1 depth | clean prefix | max shadow lifetime | live at final | final valid1 |
| ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| 1 | 8 | clean | - | - | 250 | 0 | 0 | 0 |
| 1 | 10 | clean | - | - | 250 | 0 | 0 | 0 |
| 1 | 11 | clean | - | - | 250 | 0 | 0 | 0 |
| 1 | 12 | clean | - | - | 250 | 0 | 0 | 0 |
| 1 | 14 | clean | - | - | 250 | 0 | 0 | 0 |
| 2 | 8 | clean | - | - | 250 | 0 | 0 | 0 |
| 2 | 10 | clean | - | - | 250 | 0 | 0 | 0 |
| 2 | 11 | clean | - | - | 250 | 0 | 0 | 0 |
| 2 | 12 | clean | - | - | 250 | 0 | 0 | 0 |
| 2 | 14 | clean | - | - | 250 | 0 | 0 | 0 |
| 3 | 8 | final-live | 14 | 250 | 13 | 2 | 1 | nonzero |
| 3 | 10 | clean | - | - | 250 | 0 | 0 | 0 |
| 3 | 11 | clean | - | - | 250 | 0 | 0 | 0 |
| 3 | 12 | clean | - | - | 250 | 0 | 0 | 0 |
| 3 | 14 | clean | - | - | 250 | 0 | 0 | 0 |
| 4 | 8 | final-live | 14 | 250 | 13 | 5 | 2 | nonzero |
| 4 | 10 | final-live | 18 | 250 | 17 | 3 | 1 | nonzero |
| 4 | 11 | final-live | 19 | 250 | 18 | 2 | 1 | nonzero |
| 4 | 12 | transient-only | 53 | 212 | 52 | 1 | 0 | 0 |
| 4 | 13 | clean | - | - | 250 | 0 | 0 | 0 |
| 4 | 14 | clean | - | - | 250 | 0 | 0 | 0 |

### C=4 Transition Shape

C=4 now shows a clear thinning sequence:

- `m=8`: dirty from depth 14 through final depth, max lifetime 5.
- `m=10`: dirty from depth 18 through final depth, max lifetime 3.
- `m=11`: dirty from depth 19 through final depth, max lifetime 2.
- `m=12`: transient-only single-depth flashes at depths `53`, `106`, `159`,
  and `212`, max lifetime 1.
- `m=13`: clean through depth 250, no valid1 births.
- `m=14`: clean through depth 250, no valid1 births.

Therefore the C=4 collapse is not a binary cliff; it is a visible lifecycle
surface. The valid1 shadows thin out, become isolated 53-ladder flashes, and
then disappear completely.

C=4 collapse wall:

```text
dirty at m=12, clean at m=13
```

The in-between rule moved the first clean C=4 precision down from the earlier
coarse result `m=14` to `m=13`.

## C=4 Long-Depth Lift Profile: m=8 -> m=11

Update date: 2026-05-23

The Rust scanner was extended with lift-profile export:

```bash
--lift-profile-base-m {m-1}
```

For a run at residue precision `m`, this records how terminal-compatible
signatures at base precision `m-1` lift into the sharper precision `m`.
The profile is intentionally lineage/lightweight: it tracks whether each of the
three residue lifts exists and whether the terminal-compatible lift survives.

Command pattern:

```bash
/tmp/collatz-rust-target/release/lock3_census \
  --C 4 --depth 2000 --residue-mod-power {m} \
  --out-dir data/runs/lock3_C4_N2000_m{m-1}_to_m{m}_lift_profile_20260523 \
  --progress-every 100 \
  --memory-lean --no-checkpoint \
  --lift-profile-base-m {m-1} \
  --progress-jsonl data/runs/lock3_C4_N2000_m{m-1}_to_m{m}_lift_profile_20260523/live_events.jsonl
```

Runs:

- `data/runs/lock3_C4_N2000_m8_to_m9_lift_profile_20260523`
- `data/runs/lock3_C4_N2000_m9_to_m10_lift_profile_20260523`
- `data/runs/lock3_C4_N2000_m10_to_m11_lift_profile_20260523`
- `data/runs/lock3_C4_N2000_m11_to_m12_lift_profile_20260523`

### Long-Depth Lifecycle

| C | m | depth | final state | first valid1 depth | last valid1 depth | clean prefix | max shadow lifetime | final live | final compatible signatures | peak RSS KB |
| ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 9 | 2000 | final-live | 16 | 2000 | 15 | 4 | 1 | 1 | 31396 |
| 4 | 10 | 2000 | transient/spiky | 18 | 1999 | 17 | 3 | 0 | 0 | 81088 |
| 4 | 11 | 2000 | transient/spiky | 19 | 1999 | 18 | 2 | 0 | 0 | 197764 |
| 4 | 12 | 2000 | transient/spiky | 53 | 1995 | 52 | 1 | 0 | 0 | 418108 |

### Lift Survival

| C | base m | lift m | base-live rows | possible lifts | terminal lifts surviving | survival ratio | deaths before lift | max lift count |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 8 | 9 | 3336 | 10008 | 2510 | 0.250799360512 | 826 | 3 |
| 4 | 9 | 10 | 2510 | 7530 | 1685 | 0.223771580345 | 825 | 2 |
| 4 | 10 | 11 | 1685 | 5055 | 862 | 0.170524233432 | 823 | 2 |
| 4 | 11 | 12 | 862 | 2586 | 39 | 0.015081206497 | 823 | 2 |

### m=12 Spike Structure to Depth 2000

The C=4/m=12 depth-2000 run stays final-clean, but terminal-compatible shadows
reappear as single-depth spikes through the run.

Summary:

- Final `valid_from_1_count`: `0`
- `ever_seen_valid1`: `true`
- First valid1 depth: `53`
- Last valid1 depth: `1995`
- Max shadow lifetime: `1`
- Dirty depth count: `39`
- Gap values: `41`, `53`
- Gap frequencies: `41` appears `6` times; `53` appears `32` times.
- Gap word: `BBBBBABBBBBABBBBBBABBBBBABBBBBBABBBBBA`, where `A=41`
  and `B=53`.
- Shortest exact gap-word period: `13`

Dirty depths:

```text
53, 106, 159, 212, 265, 318, 359, 412, 465, 518,
571, 624, 665, 718, 771, 824, 877, 930, 983, 1024,
1077, 1130, 1183, 1236, 1289, 1330, 1383, 1436,
1489, 1542, 1595, 1648, 1689, 1742, 1795, 1848,
1901, 1954, 1995
```

The first six hits are exact multiples of `53`:

```text
53, 106, 159, 212, 265, 318
```

After that the sequence phase-shifts. Consecutive dirty-depth gaps are mostly
`53`, interrupted by recurring `41` jumps:

```text
53, 53, 53, 53, 53, 41, 53, 53, 53, 53, 53, 41, ...
```

The exact period over the 38 observed gaps is 13:

```text
B B B B B A B B B B B B A
```

equivalently:

```text
53, 53, 53, 53, 53, 41, 53, 53, 53, 53, 53, 53, 41
```

This 13-gap period contains ten `53` gaps and two `41` gaps:

```text
10*53 + 2*41 = 530 + 82 = 612
```

The same number is twice the gap between consecutive continued-fraction
near-return denominators `53` and `359`:

```text
612 = 2*(359 - 53) = 2*306
```

Thus the m=12 C=4 spark train is not merely "near the 53 ladder"; it encodes a
double bridge-gap rhythm from the `53 -> 359` corridor transition.

Interpretation: m=12 is not random transient noise. It is a highly structured
single-depth spike train. The initial 53-ladder seen in the depth-250 run
continues, but the full depth-2000 run shows phase shifts tied to the same
near-return geometry rather than a pure `53k` law through the entire interval.

Gap-analysis outputs:

- `data/runs/lock3_C4_N2000_m11_to_m12_lift_profile_20260523/lock3_C4_m12_gap_word.csv`
- `data/runs/lock3_C4_N2000_m11_to_m12_lift_profile_20260523/lock3_C4_m12_gap_word.txt`
- `data/runs/lock3_C4_N2000_m11_to_m12_lift_profile_20260523/lock3_C4_m12_gap_analysis.json`

### m=11 Gap Structure

The C=4/m=11 per-depth lifecycle is also periodic, but much denser than m=12.
This was checked against both the new depth-2000 lift-profile run and the older
depth-5000 lifecycle run:

- `data/runs/lock3_C4_N2000_m10_to_m11_lift_profile_20260523/lock3_census_C4.csv`
- `data/runs/lock3_C4_N5000_residue_m11_lifecycle_lean_fresh/lock3_census_C4.csv`

Both runs give the same exact gap period.

Summary from the depth-5000 run:

- Dirty depth count: `2165`
- Gap values: `1`, `2`, `3`
- Gap frequencies: `1` appears `97` times; `2` appears `1318` times; `3`
  appears `749` times.
- Shortest exact gap period: `289` gaps.
- One period has gap counts `{1: 13, 2: 176, 3: 100}`.
- One period spans exactly:

```text
13*1 + 176*2 + 100*3 = 665
```

Thus m=11 encodes a full `665` near-return/corridor denominator in its dirty
gap word. This is the next Lock 4 corridor gap/near-return denominator after
`359`, so the m=11 vertical spark word is landing directly on the next
horizontal corridor marker. The m=12 spark train then thins the same underlying
structure into a single-depth spike pattern with period span
`612 = 2*(359 - 53)`, the double bridge gap from `53` to `359`.

### Lock 3 / Lock 4 Bridge Hypothesis

Working interpretation:

```text
Lock 3: vertical precision collapse inside a bounded corridor.
Lock 4: horizontal corridor exhaustion across unbounded reserve corridors.
```

A Collatz escape would need a glide that can do both:

1. lift high enough in residue precision, and
2. persist long enough in accelerated time to cross into the next corridor.

Lock 3 attacks the first requirement. Inside a fixed bounded-deficit corridor,
terminal-compatible residue shadows thin under increasing `m`, then collapse
into single-depth spark trains.

Lock 4 attacks the second requirement. Even when unbounded reserve corridors
are allowed, the horizontal corridor structure exhausts the available glide
before it can persist across the next corridor boundary.

The C=4/m=12 gap word is the current bridge between the two locks. Its
single-depth spark train is not random: the gaps are organized by the same
continued-fraction near-return/corridor geometry that appears in the Lock 4
horizontal exhaustion analysis. Thus Lock 3's vertical residue-collapse pattern
and Lock 4's horizontal corridor-exhaustion pattern appear to be two projections
of the same underlying orbit geometry.

### Reproduction Check Against Earlier m=11 Run

The new scanner reproduces the earlier C=4/m=11 depth-5000 lifecycle run around
the known dirty band at depth `1250`.

Rows from the new C=4/m=11 depth-2000 run:

| depth | state | births | deaths | live |
| ---: | :--- | ---: | ---: | ---: |
| 1245 | dirty | 1 | 0 | 1 |
| 1246 | clean | 0 | 1 | 0 |
| 1247 | clean | 0 | 0 | 0 |
| 1248 | dirty | 1 | 0 | 1 |
| 1249 | clean | 0 | 1 | 0 |
| 1250 | dirty | 1 | 0 | 1 |
| 1251 | clean | 0 | 1 | 0 |
| 1252 | dirty | 1 | 0 | 1 |
| 1253 | clean | 0 | 1 | 0 |
| 1254 | clean | 0 | 0 | 0 |
| 1255 | dirty | 1 | 0 | 1 |

The same rows match exactly in:

```text
data/runs/lock3_C4_N5000_residue_m11_lifecycle_lean_fresh/lock3_census_C4.csv
```

Interpretation:

- `m=9` remains live through depth `2000` after turning on at depth `16`.
- `m=10` is no longer final-live at depth `2000`; it is spiky, with final depth
  clean but dirty depths continuing through `1999`.
- `m=11` is also spiky. It is checkpoint-clean at many 100-depth progress
  prints, but per-depth CSV rows show recurrent dirty bands, including the
  expected `1250` band and a later reappearance at depth `1900`.
- The 100-depth progress output is therefore not sufficient to judge whether a
  run is clean; the per-depth census and lifecycle event rows are the source of
  truth for transient bands.
- Lift survival decays as precision sharpens from `m=9` to `m=11`, but it does
  not vanish monotonically by depth alone. Dirty bands can reappear at later
  depths within the same `m`.

### Even-m Dirty-start Auto Prior-odd Rule

The Rust census now supports:

```bash
--auto-prior-odd-on-even-dirty
```

Scope of the rule:

- Only even `m` can trigger it.
- It only triggers if the first computed row, depth `1`, is already dirty.
- Later valid1 births do not stop the run. They are measured by the lineage
  fields instead.
- If triggered, the run writes its partial output, then runs `m-1` into a
  sibling output directory ending in `_auto_prior_m{m-1}`.

Smoke test:

```bash
/tmp/collatz-rust-target-lineage/release/lock3_census \
  --C 3 --depth 20 --residue-mod-power 8 \
  --out-dir data/runs/lock3_auto_prior_smoke_C3_m8_N20 \
  --progress-every 20 --label lock3 \
  --memory-lean --no-checkpoint --memory-cap-mb 1000 \
  --auto-prior-odd-on-even-dirty
```

Result: the run had later lineage births (`first_valid1_depth=14`) and
continued through depth `20`. This verifies the intended behavior: births at
later depths, including around the full-precision boundary, are not treated as
dirty-start failures.

### Live JSONL Telemetry and Sidecar CSV

The Rust census now supports canonical machine-readable live telemetry:

```bash
--progress-jsonl data/runs/<run>/live_events.jsonl
```

When enabled, the engine appends JSONL events as the run proceeds:

- `progress`: one event per completed depth row.
- `checkpoint`: emitted after checkpoint write, including checkpoint size.
- `final`: emitted after normal output write.

The sidecar converter is:

```bash
python3 scripts/lock3_live_daemon.py \
  --input data/runs/<run>/live_events.jsonl \
  --csv data/runs/<run>/live_progress.csv \
  --latest data/runs/<run>/latest_status.json \
  --follow
```

The JSONL is the primary durable telemetry stream. The daemon can run live or
after the fact; it appends normalized CSV rows and atomically refreshes
`latest_status.json`.

Smoke tests:

```bash
/tmp/collatz-rust-target-lineage/release/lock3_census \
  --C 3 --depth 8 --residue-mod-power 8 \
  --out-dir data/runs/lock3_jsonl_smoke \
  --progress-every 4 --label lock3 \
  --memory-lean --no-checkpoint --memory-cap-mb 1000 \
  --progress-jsonl data/runs/lock3_jsonl_smoke/live_events.jsonl

/tmp/collatz-rust-target-lineage/release/lock3_census \
  --C 3 --depth 5 --residue-mod-power 8 \
  --out-dir data/runs/lock3_jsonl_checkpoint_smoke \
  --progress-every 5 --label lock3 \
  --memory-lean \
  --checkpoint-path data/runs/lock3_jsonl_checkpoint_smoke/lock3_C3_m8.checkpoint.bin \
  --checkpoint-every 5 \
  --memory-cap-mb 1000 \
  --progress-jsonl data/runs/lock3_jsonl_checkpoint_smoke/live_events.jsonl
```

Verified event types: `progress`, `checkpoint`, and `final`.
