# collatz-experimental-data

The Collatz research track of an independent research program: a 4D
spacetime reformulation of the Collatz conjecture, a Sturmian
precision-collapse proof framework, exhaustive computational certificates,
and the bridge that carried the program's precision-decay law into
transformer attention (see the companion papers below).

## Read this first

| Document | What it is |
|---|---|
| `GHOST_GEOMETRY_RELEASE.md` | **The citable release document** — program summary, gap audit, relation to known results, and the attention-transfer study (Zenodo record) |
| `COLLATZ_PROOF.md` | The proof framework: residue automaton, 53/22 heartbeat, capacity edge, spectral certificates, product-space automaton — presented as a target claim with enumerated gaps, not an accepted proof |
| `collatz_proof_red_team_problem_list.md` | The framework's own adversarial audit — published deliberately alongside the proof document |
| `collatz-ml-bridge.md` | Historical (May 2026) working note; superseded by the release document where figures differ |
| `LOCK1_*.md`, `LOCK3_RESULTS.md`, `RESULTS.md`, `LOCK2_RESULTS.md`, `collatz-4d-spacetime-attack*.md` | Per-lock theorem write-ups, scan results, and the original spacetime attack notes |

## Companion papers (released together)

1. *Ghost Geometry: A Precision-Collapse Framework for the Collatz
   Conjecture, and Its Measured Transfer to Transformer Attention* (this
   repository's release document).
2. *Selective Attention Is All You Need: Adaptive Precision Attention*
   (Project-Tensor).
3. *Grafted Memory — GRM: A Routed, Tokenless K/V Memory Runtime for Frozen
   Language Models* (GraftRepository).

## Data

The raw certificate data (exhaustive scans to 100B, census outputs,
breach-follow witnesses — ~31 GB) is not tracked in this repository. Every
certificate's summary statistics are recorded in the documents above; raw
data is available on request.

---

# The exact-test harness

Exact-test harness for the Collatz IME / ghost-chain exploration.

This harness is intentionally small and standard-library only. The first
target was to replace rough corridor and ghost proxies with exact odd-only
orbit words, exact affine interval maps, and reproducible CSV/JSON output.

## Run

```bash
PYTHONPATH=src python3 -m collatz_experimental_data orbit 19638399
PYTHONPATH=src python3 -m collatz_experimental_data scan --limit 200000 --min-reserve 12
PYTHONPATH=src python3 -m collatz_experimental_data phase 19638399 --period 53
PYTHONPATH=src python3 -m collatz_experimental_data macro 80049391 120080895
PYTHONPATH=src python3 -m collatz_experimental_data gap-kill 80049391 120080895
PYTHONPATH=src python3 -m collatz_experimental_data post-k53 80049391 120080895
PYTHONPATH=src python3 -m collatz_experimental_data k53-capacity 80049391 120080895
PYTHONPATH=src python3 -m collatz_experimental_data corridor-bound 80049391 120080895
PYTHONPATH=src python3 -m collatz_experimental_data scaling-sweep --samples-per-bit-length 10000
PYTHONPATH=src python3 -m collatz_experimental_data scan-range-fast --start 250000001 --stop 10000000000 --min-reserve 23
PYTHONPATH=src python3 -m collatz_experimental_data macro-summary 319804831 1410123943
PYTHONPATH=src python3 -m collatz_experimental_data tail-law --range 1:250000000:data/runs/scan_limit250000000_D23_20260521T190952Z.csv
PYTHONPATH=src python3 -m collatz_experimental_data lock2-scan --Amax 20
PYTHONPATH=src python3 -m collatz_experimental_data lock2-scan --Amax 20 --first-contractivity-only
PYTHONPATH=src python3 -m collatz_experimental_data lock2-scan --Amax 28 --first-contractivity-only --predict-rho-slack-min 8 --predict-theta-candidates-min 1
cargo build --release --bin lock2_scan --target-dir /tmp/collatz-rust-target
/tmp/collatz-rust-target/release/lock2_scan --Amax 40 --threads 12 --split-depth 8 --predict-rho-slack-min 8 --predict-theta-candidates-min 1
cargo build --release --bin lock2_reverse_barrier --target-dir /tmp/collatz-rust-target
/tmp/collatz-rust-target/release/lock2_reverse_barrier --Amax 77
/tmp/collatz-rust-target/release/lock2_reverse_barrier --Amax 77 --target-num 48215861999407177 --target-den 84244659018371145
/tmp/collatz-rust-target/release/lock2_reverse_barrier --Amax 100 --target-num 48215861999407177 --target-den 84244659018371145 --top-n 100 --progress-every-a 20 --slow-pair-seconds 2
/tmp/collatz-rust-target/release/lock2_reverse_barrier --Amax 100 --target 0.3 --top-n 100 --progress-every-a 20 --slow-pair-seconds 5
```

Outputs are written under `data/runs/` unless `--out-dir` is provided.

## Result Tracks

- `RESULTS.md`: reserve frontier, k=53/k=359 bridge, tail law, and Lock 4
  style search evidence.
- `LOCK2_RESULTS.md`: finite-word minimal-residue descent scans and Lock 2
  proof-surface evidence.

## Current Frontier

The latest exhaustive push scanned every odd start through `100B`.

- First observed `D=23`: `80049391`
- First observed `D=24..D=30`: `319804831`
- First observed `D=31`: `77566362559`
- No observed `D>=32` start below `100B`
- No observed macro-convergent hit at `k=359` or higher below `100B`

See `RESULTS.md` for the full scan tables and output file paths.

## Terms

- Odd-only step: `x -> (3x + 1) / 2^a`, where `a = v2(3x + 1)`.
- Accumulated exponent: `A_k = a_0 + ... + a_{k-1}`.
- Reserve: `d_k = floor(k log2 3) - A_k`.
- Growth step: a step with `d_{k+1} > d_k`.
- Growth segment: a contiguous run of growth steps, default length at least 2.
- Interval affine word: for a segment word `a_i...a_j`,
  `S^L(x) = (3^L x + B) / 2^A`.
- Exact negative ghost: when `3^L > 2^A`,
  `gamma = -B / (3^L - 2^A)`.
- Exact 2-adic proximity proxy:
  `v2((3^L - 2^A) * x_entry + B)`.
- Macro-corridor: a maximal reserve-index interval `[s,t]` where reserve
  stays within 2 of its local running maximum; its affine word is
  `[a_s, ..., a_{t-1}]`.
- Gap-kill bridge cost: under an explicit non-corridor spend model `a=2`,
  the reserve needed for a gap of `G` steps is the maximum prefix loss
  `max_m(2m - floor(m log2 3))`, or the phase-specific equivalent when an
  orbit exit step is known.
- Post-k=53 behavior: exact step-level measurement after the main `k=53`
  macro-corridor, used to compare actual exponent drain against the
  conservative `a=2` bridge model.
- K=53 capacity: combines observed `k=53` macro-corridor gain, deterministic
  high-credit windows, the bit-length corridor estimate `L <= B*53/84`, and
  the martingale bound `mu(H_D) <= 2^-D`.
- Corridor-bound: checks the proposed `L = O(log n)` k=53 corridor bound
  against observed macro-corridors and synthetic large odd starts. Observed
  macro-corridors and strict beta-quality corridors are reported separately.
- Scaling-sweep: random large-integer macro-corridor sweep across bit lengths,
  beta thresholds, and empirical fit models. Uses lightweight aggregate
  corridor metrics rather than exact affine ghosts.
- Scan-range-fast: exhaustive odd-start reserve scan over an inclusive range.
- Macro-summary: compact macro-corridor convergent summary for many starts.
- Tail-law: empirical exponential tail fit for maximum reserve thresholds,
  using completed exhaustive scan CSVs and explicit scanned ranges.
- Lock2-scan: exhaustive finite-word margin scan for the Lock 2
  minimal-residue descent conjecture.

---

## License

Copyright (C) 2026 David Perry.

Code in this repository is licensed under the GNU Affero General Public
License v3.0 — see [LICENSE](LICENSE). Any software derived from this code,
including software served over a network, must be released under the same
terms. **Commercial licensing outside the AGPL terms is available** —
contact `dave@ai-storyforge.com`.

The research documents are licensed CC BY 4.0 via their Zenodo records.

## Citation

Perry, D. (2026). *Ghost Geometry: A Precision-Collapse Framework for the
Collatz Conjecture, and Its Measured Transfer to Transformer Attention.*
Zenodo. (DOI on release.)
