# Macro-Corridor Detection Instructions

## Problem

The current corridor detection is too narrow — it only finds [1,1] micro-bursts. We need macro-corridors that capture the full growth phases.

## New Corridor Definition

For each of the six D=23 orbits, take the full orbit step data (k, x, a, d) and define a corridor as a maximal interval [s, t] where d never drops more than 2 below its running maximum within that interval. When d drops by more than 2 from the local max, that's a corridor boundary.

## For Each Detected Macro-Corridor

1. Extract the full exponent word [a_s, a_{s+1}, ..., a_{t-1}]
2. Compute the affine map using the word: k = t-s, A = sum of exponents, B from the recurrence B = 3*B + 2^A_running
3. If 3^k > 2^A (positive action), compute the ghost: gamma = -B / (3^k - 2^A)
4. Compute the corridor residual: beta = k * log2(3) - A
5. Map beta to the nearest continued-fraction convergent of log2(3) from the known list: k=1,2,7,12,53,359,665,16266,31867,111202
6. Record: corridor index, start step, end step, length L, total division A, beta, mapped convergent, ghost gamma, quality 1/beta, deficit at entry, deficit at exit, deficit at peak

## Run Scope

Run this on all six D=23 orbits:

- 80049391
- 120080895
- 210964383
- 219259131
- 222250543
- 246666523

Output a table for each orbit.

## Existing Code to Reuse

- The `affine_for_word` function from `collatz_spacetime_explore.py` does step 2.
- The continued fraction convergent list and mapping logic from the existing codebase does step 5.
- The orbit simulation and deficit tracking already exist in `ghost_chain_quality_analyzer.py`.
