# Lock 3 C>0 Solver Redesign Plan

## Purpose

The C=1, C=2, and C=3 Lock 3 backward-solver proof-of-concept showed that the current exact path-retention implementation is not the right architecture for bounded-buffer cases.

C=0 is a single critical Sturmian path, so exact path tracking works.

C>0 creates a branching finite-buffer automaton. Retaining full path objects causes rapid explosion:
- C=1 truncates around depth 23 at the 200,000 branch cap.
- C=2 truncates around depth 18.
- C=3 truncates around depth 17.

This is not a mathematical failure. It is an implementation-design signal.

The next solver should switch from "retain every path" to "census and merge states."

---

## Core Interpretation

Lock 3 asks whether a positive integer orbit can remain forever in a bounded deficit strip:

    0 <= d_k <= C

where:

    d_k = floor(k * log2(3)) - A_k
    A_k = a_0 + a_1 + ... + a_{k-1}
    a_i = v2(3*x_i + 1)

For C=0, the exponent word is unique.

For C>0, the bounded deficit state:

    d_k in {0, 1, ..., C}

creates multiple possible transitions at every depth.

The solver must stop treating those transitions as independent full paths and instead compress equivalent branches.

---

## New Architecture

Implement two modes:

1. Exact Mode
2. Census Mode

### Exact Mode

Use exact mode only when branch count is small.

Good for:
- C=0
- debugging C=1 at shallow depth
- exporting witness paths
- verifying recurrence logic

Exact mode keeps:
- full deficit path
- full exponent word
- rho trajectory
- branch-local values
- exact ancestor if available

### Census Mode

Use census mode for C>=1 at meaningful depths.

Census mode should:
- aggregate branches by compact state
- count branches instead of storing them individually
- export only summaries and record witnesses
- merge states that are equivalent for future evolution

This is the primary path for C=1,2,3 and beyond.

---

## State Representation for Census Mode

At minimum, a state should include:

    depth k
    deficit d_k
    A_k
    affine state if needed
    residue/integrality signature
    rho stability signature

Candidate compact state:

    (k, d, A_mod_window, residue_mod_3_power, rho_mod_window, stabilization_status)

The exact choice should be refined empirically.

Do not store the entire path unless the branch sets a new record or survives an interesting filter.

---

## Required Metrics Per Depth

For each C and depth k, write one row to:

    lock3_census_C{C}.csv

Columns:

    C
    depth
    symbolic_branch_count
    merged_state_count
    valid_from_1_count
    residue_class_count
    rho_stable_count
    rho_lift_count
    longest_plateau
    max_rho_bit_length
    max_branch_multiplicity
    truncated
    notes

Important derived ratios:

    compression_ratio = symbolic_branch_count / merged_state_count
    valid_fraction = valid_from_1_count / symbolic_branch_count
    stable_fraction = rho_stable_count / merged_state_count

---

## Event Logging

Write sparse event logs, not full path dumps.

### Record Events

Emit to STDERR and to a CSV when:

- new max branch count
- new max merged state count
- new longest rho plateau
- new max rho bit length
- first valid-from-1 branch at a depth
- possible stabilization candidate appears
- residue class count collapses unexpectedly
- branch count explodes past configured warning threshold

Suggested event CSV:

    lock3_events_C{C}.csv

Columns:

    C
    depth
    event_type
    value
    branch_id_or_state_id
    deficit_state
    exponent
    summary

---

## Witness Export

Export full path details only for selected witnesses.

Witness criteria:

1. Longest rho plateau
2. Smallest rho at depth
3. Largest rho bit length
4. Valid-from-1 branch if any
5. Candidate branch with no rho lift for unusually long interval
6. Near-return depth branch
7. Any branch flagged as possible stabilization

Suggested file:

    lock3_witnesses_C{C}.jsonl

Each line should contain:

    C
    depth
    witness_type
    deficit_path
    exponent_word
    A_k
    rho_k
    modulus_bits
    lift_count
    plateau_length
    notes

---

## Backward Integrality Gate

Backward odd-only inverse step:

    x_i = (2^a * x_{i+1} - 1) / 3

Valid only when:

    2^a * x_{i+1} ≡ 1 mod 3

Since:

    2^a ≡ 1 mod 3 if a is even
    2^a ≡ 2 mod 3 if a is odd

the local gate is:

    if a even: x_{i+1} ≡ 1 mod 3
    if a odd:  x_{i+1} ≡ 2 mod 3

Census mode should track these constraints symbolically instead of keeping every terminal value.

---

## Forward Residue Stabilization Test

For each exponent prefix, the smallest positive representative is:

    rho_k ≡ (2^A_k - B_k) * (3^k)^(-1) mod 2^(A_k+1)

A positive integer candidate must eventually stabilize:

    rho_k = N

once:

    2^(A_k+1) > N

Therefore a Lock 3 infinite positive integer branch would need eventual zero-lift behavior.

Track:
- rho_changed
- lift_amount
- plateau length
- max plateau length
- cumulative lift events

The expected Lock 3 failure mode is:

    bounded-deficit branches require infinitely many rho lifts,
    preventing stabilization to a positive integer.

---

## Phase Plan

### Phase 1 — Preserve Current Exact C=0 Path

Keep exact mode for C=0.

Run:

    lock3-backward --C 0 --depth 1000000 --mode exact

Outputs:
- rho lift curve
- plateau curve
- near-return ghost table
- bit length growth
- stabilization flag

Goal:
Confirm the C=0 critical path continues non-stabilizing at much larger depth.

---

### Phase 2 — Implement C>0 Census Mode

Add:

    --mode census

Run:

    lock3-backward --C 1 --depth 250 --mode census
    lock3-backward --C 2 --depth 250 --mode census
    lock3-backward --C 3 --depth 250 --mode census

Goal:
Replace branch truncation with meaningful census data.

Success:
- no path cap needed for summary mode
- branch/state counts recorded through depth 250
- witness export stays bounded

---

### Phase 3 — Residue-Class Merging

If branch counts still explode, merge by symbolic equivalence.

Possible merge keys:
- deficit state d
- depth k
- A_k modulo a selected window
- residue condition modulo 3^m
- rho modulo a selected 2-power window
- lift/stability status class

Test multiple merge strategies:
- conservative merge: fewer false equivalences
- aggressive merge: faster census
- exact residue merge where feasible

Outputs should compare:
- raw branch count estimate
- merged state count
- compression ratio
- lost witness risk

---

### Phase 4 — Deeper C=1,2,3 Runs

After census mode is stable:

    C=1 depth 1000
    C=2 depth 1000
    C=3 depth 1000

Then increase if manageable.

Track:
- stabilization candidates
- long plateau branches
- near-return behavior
- residue-class growth or collapse

---

### Phase 5 — Rust Port If Needed

If Python census becomes too slow:
- port time-indexed bounded-buffer automaton to Rust
- keep Python as report aggregator
- use compact state structs
- use hash maps for state counts
- write CSV/JSONL outputs incrementally

Rust CLI target:

    lock3_census --C 3 --depth 10000 --merge conservative

---

## STDERR Logging

For long runs, print progress every configurable depth interval.

Suggested format:

    [lock3] C=2 depth=175 branches=123456789 merged=54321 valid1=0 lifts=98765 longest_plateau=12 max_bits=314 rate=... mem=...

Record events:

    [record plateau] C=2 depth=181 plateau=19 witness=...
    [record max_bits] C=3 depth=220 bits=...
    [valid-from-1] C=1 depth=... count=...
    [possible-stabilization] C=2 depth=... plateau=...

---

## Validation Tests

Add tests for:

1. Deficit transition:
       d_next = d + c_k - a

2. Exponent reconstruction:
       a = d + c_k - d_next

3. Valid transition:
       a >= 1

4. Inverse step:
       x_prev = (2^a * x_next - 1) / 3

5. Mod 3 gate:
       if a even, x_next ≡ 1 mod 3
       if a odd, x_next ≡ 2 mod 3

6. C=0 word:
       a_k = floor((k+1)log2(3)) - floor(k log2(3))

7. Rho recurrence:
       3^k * rho + B_k ≡ 2^A mod 2^(A+1)

8. Positive integer stabilization:
       for a known positive start, rho stabilizes once modulus exceeds start

9. Trivial 1-cycle:
       all-2 word corresponds to rho=1

---

## Immediate Codex Task

Implement Lock 3 census mode.

Do not try to retain all paths for C>0.

Command target:

    lock3-backward --C 1 --depth 250 --mode census
    lock3-backward --C 2 --depth 250 --mode census
    lock3-backward --C 3 --depth 250 --mode census

Minimum deliverables:
- lock3_census_C1.csv
- lock3_census_C2.csv
- lock3_census_C3.csv
- lock3_events_C1.csv
- lock3_events_C2.csv
- lock3_events_C3.csv
- lock3_summary_C1.json
- lock3_summary_C2.json
- lock3_summary_C3.json

Do not output every path.
Do output records and witnesses.

---

## Success Criteria

Minimum:
- C=1,2,3 run to depth 250 without truncation in census mode.
- Branch counts and merged-state counts are recorded.
- Rho lift and plateau statistics are recorded.
- No full-path explosion in output files.

Good:
- C=1,2,3 run to depth 1000.
- Residue-class merging shows useful compression.
- Longest plateau witnesses are exported.

Strong:
- Evidence that C>0 bounded-buffer branches also keep lifting rather than stabilizing.
- No eventually-zero-lift branch appears.
- Branch/residue structure suggests a theorem for bounded-deficit non-stabilization.

---

## Plain English Summary

C=0 worked because there is one critical path.

C>0 branches too fast for full path retention.

The next solver must count and merge states instead of storing every branch.

The goal is not to prove Lock 3 immediately.
The goal is to identify whether bounded-buffer paths behave like C=0:
they may survive symbolically, but their rho representatives keep lifting instead of stabilizing to a positive integer.

That is the Lock 3 mechanism to measure.
