# Renormalization / Corridor-Embedding Conjecture: Test Results

Testing whether A(C+22, m+53) contains an exact self-embedding of A(C, m), per COLLATZ_PROOF.md's residue automaton (Section 4.2-4.3).

## 1. Validation (mandatory pre-check)

- Lemma 3 (22 support / 31 drop in first 53 Sturmian credits): **PASS**
- M_edge(C) formula match (C=1..5): **PASS**
- Zero-birth-edge (Theorem 1 / Certificate 1) reproduced independently for C=3,4,5: **PASS**
- Overall: **PASS**

## 2. Small-side |live(C,m)| table (dense, exact)

| C | m | M_edge(C) | live | possible | live_fraction | terminal_compat | time(s) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 4 | 4 | 6 | 6.666667e-01 | 2 | 0.00 |
| 1 | 2 | 4 | 8 | 18 | 4.444444e-01 | 2 | 0.00 |
| 1 | 3 | 4 | 12 | 54 | 2.222222e-01 | 1 | 0.00 |
| 1 | 4 | 4 | 24 | 162 | 1.481481e-01 | 1 | 0.00 |
| 1 | 5 | 4 | 36 | 486 | 7.407407e-02 | 0 | 0.00 |
| 1 | 6 | 4 | 72 | 1458 | 4.938272e-02 | 0 | 0.00 |
| 2 | 1 | 7 | 6 | 9 | 6.666667e-01 | 3 | 0.00 |
| 2 | 2 | 7 | 14 | 27 | 5.185185e-01 | 3 | 0.00 |
| 2 | 3 | 7 | 27 | 81 | 3.333333e-01 | 2 | 0.00 |
| 2 | 4 | 7 | 64 | 243 | 2.633745e-01 | 2 | 0.00 |
| 2 | 5 | 7 | 123 | 729 | 1.687243e-01 | 1 | 0.00 |
| 2 | 6 | 7 | 282 | 2187 | 1.289438e-01 | 1 | 0.00 |
| 2 | 7 | 7 | 651 | 6561 | 9.922268e-02 | 1 | 0.00 |
| 2 | 8 | 7 | 1364 | 19683 | 6.929838e-02 | 0 | 0.00 |
| 2 | 9 | 7 | 3220 | 59049 | 5.453098e-02 | 0 | 0.01 |
| 3 | 1 | 9 | 8 | 12 | 6.666667e-01 | 4 | 0.00 |
| 3 | 2 | 9 | 21 | 36 | 5.833333e-01 | 4 | 0.00 |
| 3 | 3 | 9 | 46 | 108 | 4.259259e-01 | 3 | 0.00 |
| 3 | 4 | 9 | 118 | 324 | 3.641975e-01 | 3 | 0.00 |
| 3 | 5 | 9 | 262 | 972 | 2.695473e-01 | 2 | 0.00 |
| 3 | 6 | 9 | 641 | 2916 | 2.198217e-01 | 2 | 0.00 |
| 3 | 7 | 9 | 1586 | 8748 | 1.812986e-01 | 2 | 0.00 |
| 3 | 8 | 9 | 3727 | 26244 | 1.420134e-01 | 1 | 0.01 |
| 3 | 9 | 9 | 9405 | 78732 | 1.194559e-01 | 1 | 0.01 |
| 3 | 10 | 9 | 21254 | 236196 | 8.998459e-02 | 0 | 0.04 |
| 3 | 11 | 9 | 52400 | 708588 | 7.394988e-02 | 0 | 0.11 |
| 4 | 1 | 12 | 10 | 15 | 6.666667e-01 | 5 | 0.00 |
| 4 | 2 | 12 | 27 | 45 | 6.000000e-01 | 5 | 0.00 |
| 4 | 3 | 12 | 67 | 135 | 4.962963e-01 | 4 | 0.00 |
| 4 | 4 | 12 | 178 | 405 | 4.395062e-01 | 4 | 0.00 |
| 4 | 5 | 12 | 433 | 1215 | 3.563786e-01 | 3 | 0.00 |
| 4 | 6 | 12 | 1115 | 3645 | 3.058985e-01 | 3 | 0.00 |
| 4 | 7 | 12 | 2907 | 10935 | 2.658436e-01 | 3 | 0.00 |
| 4 | 8 | 12 | 7381 | 32805 | 2.249962e-01 | 2 | 0.01 |
| 4 | 9 | 12 | 19303 | 98415 | 1.961388e-01 | 2 | 0.02 |
| 4 | 10 | 12 | 47276 | 295245 | 1.601246e-01 | 1 | 0.04 |
| 4 | 11 | 12 | 121930 | 885735 | 1.376597e-01 | 1 | 0.12 |
| 4 | 12 | 12 | 317177 | 2657205 | 1.193649e-01 | 1 | 0.51 |
| 4 | 13 | 12 | 799891 | 7971615 | 1.003424e-01 | 0 | 1.66 |
| 4 | 14 | 12 | 2094423 | 23914845 | 8.757836e-02 | 0 | 5.67 |
| 5 | 1 | 14 | 12 | 18 | 6.666667e-01 | 6 | 0.00 |
| 5 | 2 | 14 | 33 | 54 | 6.111111e-01 | 6 | 0.00 |
| 5 | 3 | 14 | 86 | 162 | 5.308642e-01 | 5 | 0.00 |
| 5 | 4 | 14 | 238 | 486 | 4.897119e-01 | 5 | 0.00 |
| 5 | 5 | 14 | 616 | 1458 | 4.224966e-01 | 4 | 0.00 |
| 5 | 6 | 14 | 1653 | 4374 | 3.779150e-01 | 4 | 0.00 |
| 5 | 7 | 14 | 4479 | 13122 | 3.413352e-01 | 4 | 0.00 |
| 5 | 8 | 14 | 11930 | 39366 | 3.030534e-01 | 3 | 0.01 |
| 5 | 9 | 14 | 32313 | 118098 | 2.736117e-01 | 3 | 0.02 |
| 5 | 10 | 14 | 83539 | 354294 | 2.357901e-01 | 2 | 0.05 |
| 5 | 11 | 14 | 223498 | 1062882 | 2.102755e-01 | 2 | 0.16 |
| 5 | 12 | 14 | 602161 | 3188646 | 1.888454e-01 | 2 | 0.66 |
| 5 | 13 | 14 | 1585049 | 9565938 | 1.656972e-01 | 1 | 2.11 |
| 5 | 14 | 14 | 4281077 | 28697814 | 1.491778e-01 | 1 | 7.17 |
| 5 | 15 | 14 | 10947415 | 86093442 | 1.271574e-01 | 0 | 30.02 |
| 5 | 16 | 14 | 29178661 | 258280326 | 1.129728e-01 | 0 | 105.80 |

## 3. Explicit embedding-map test (Step 3)

Corridor shift = 22, heartbeat = 53, max elements sampled per pair = 15, oracle call cap = 150000.

### Aggregate totals across all 10 tested (C,m) pairs

| candidate | tested | matched | failed | inconclusive | match rate of decided |
|:---|---:|---:|---:|---:|---:|
| a_identity_no_dshift | 115 | 48 | 0 | 67 | 100% |
| a_identity_dshift22 | 115 | 0 | 49 | 66 | 0% |
| b_mult3pow53_no_dshift | 115 | 0 | 115 | 0 | 0% |
| b_mult3pow53_dshift22 | 115 | 0 | 115 | 0 | 0% |
| c_forward53_a_eq_ck | 115 | 81 | 0 | 34 | 100% |

| C | m | C2 | m2 | candidate | tested | matched | failed | inconclusive | undefined | verdict |
|---:|---:|---:|---:|:---|---:|---:|---:|---:|---:|:---|
| 1 | 1 | 23 | 54 | a_identity_no_dshift | 4 | 3 | 0 | 1 | 0 | CONTAINMENT HOLDS ON DECIDED SUBSET (100% of 3/4; 1 inconclusive) |
| 1 | 1 | 23 | 54 | a_identity_dshift22 | 4 | 0 | 4 | 0 | 0 | DEAD |
| 1 | 1 | 23 | 54 | b_mult3pow53_no_dshift | 4 | 0 | 4 | 0 | 0 | DEAD |
| 1 | 1 | 23 | 54 | b_mult3pow53_dshift22 | 4 | 0 | 4 | 0 | 0 | DEAD |
| 1 | 1 | 23 | 54 | c_forward53_a_eq_ck | 4 | 4 | 0 | 0 | 0 | EXACT CONTAINMENT (fully decided) |
| 1 | 6 | 23 | 59 | a_identity_no_dshift | 15 | 2 | 0 | 13 | 0 | CONTAINMENT HOLDS ON DECIDED SUBSET (100% of 2/15; 13 inconclusive) |
| 1 | 6 | 23 | 59 | a_identity_dshift22 | 15 | 0 | 11 | 4 | 0 | DEAD |
| 1 | 6 | 23 | 59 | b_mult3pow53_no_dshift | 15 | 0 | 15 | 0 | 0 | DEAD |
| 1 | 6 | 23 | 59 | b_mult3pow53_dshift22 | 15 | 0 | 15 | 0 | 0 | DEAD |
| 1 | 6 | 23 | 59 | c_forward53_a_eq_ck | 15 | 0 | 0 | 15 | 0 | ALL INCONCLUSIVE |
| 2 | 1 | 24 | 54 | a_identity_no_dshift | 6 | 5 | 0 | 1 | 0 | CONTAINMENT HOLDS ON DECIDED SUBSET (100% of 5/6; 1 inconclusive) |
| 2 | 1 | 24 | 54 | a_identity_dshift22 | 6 | 0 | 6 | 0 | 0 | DEAD |
| 2 | 1 | 24 | 54 | b_mult3pow53_no_dshift | 6 | 0 | 6 | 0 | 0 | DEAD |
| 2 | 1 | 24 | 54 | b_mult3pow53_dshift22 | 6 | 0 | 6 | 0 | 0 | DEAD |
| 2 | 1 | 24 | 54 | c_forward53_a_eq_ck | 6 | 6 | 0 | 0 | 0 | EXACT CONTAINMENT (fully decided) |
| 2 | 9 | 24 | 62 | a_identity_no_dshift | 15 | 1 | 0 | 14 | 0 | CONTAINMENT HOLDS ON DECIDED SUBSET (100% of 1/15; 14 inconclusive) |
| 2 | 9 | 24 | 62 | a_identity_dshift22 | 15 | 0 | 7 | 8 | 0 | DEAD |
| 2 | 9 | 24 | 62 | b_mult3pow53_no_dshift | 15 | 0 | 15 | 0 | 0 | DEAD |
| 2 | 9 | 24 | 62 | b_mult3pow53_dshift22 | 15 | 0 | 15 | 0 | 0 | DEAD |
| 2 | 9 | 24 | 62 | c_forward53_a_eq_ck | 15 | 15 | 0 | 0 | 0 | EXACT CONTAINMENT (fully decided) |
| 3 | 1 | 25 | 54 | a_identity_no_dshift | 8 | 7 | 0 | 1 | 0 | CONTAINMENT HOLDS ON DECIDED SUBSET (100% of 7/8; 1 inconclusive) |
| 3 | 1 | 25 | 54 | a_identity_dshift22 | 8 | 0 | 7 | 1 | 0 | DEAD |
| 3 | 1 | 25 | 54 | b_mult3pow53_no_dshift | 8 | 0 | 8 | 0 | 0 | DEAD |
| 3 | 1 | 25 | 54 | b_mult3pow53_dshift22 | 8 | 0 | 8 | 0 | 0 | DEAD |
| 3 | 1 | 25 | 54 | c_forward53_a_eq_ck | 8 | 8 | 0 | 0 | 0 | EXACT CONTAINMENT (fully decided) |
| 3 | 11 | 25 | 64 | a_identity_no_dshift | 15 | 2 | 0 | 13 | 0 | CONTAINMENT HOLDS ON DECIDED SUBSET (100% of 2/15; 13 inconclusive) |
| 3 | 11 | 25 | 64 | a_identity_dshift22 | 15 | 0 | 0 | 15 | 0 | ALL INCONCLUSIVE |
| 3 | 11 | 25 | 64 | b_mult3pow53_no_dshift | 15 | 0 | 15 | 0 | 0 | DEAD |
| 3 | 11 | 25 | 64 | b_mult3pow53_dshift22 | 15 | 0 | 15 | 0 | 0 | DEAD |
| 3 | 11 | 25 | 64 | c_forward53_a_eq_ck | 15 | 0 | 0 | 15 | 0 | ALL INCONCLUSIVE |
| 4 | 1 | 26 | 54 | a_identity_no_dshift | 10 | 9 | 0 | 1 | 0 | CONTAINMENT HOLDS ON DECIDED SUBSET (100% of 9/10; 1 inconclusive) |
| 4 | 1 | 26 | 54 | a_identity_dshift22 | 10 | 0 | 7 | 3 | 0 | DEAD |
| 4 | 1 | 26 | 54 | b_mult3pow53_no_dshift | 10 | 0 | 10 | 0 | 0 | DEAD |
| 4 | 1 | 26 | 54 | b_mult3pow53_dshift22 | 10 | 0 | 10 | 0 | 0 | DEAD |
| 4 | 1 | 26 | 54 | c_forward53_a_eq_ck | 10 | 10 | 0 | 0 | 0 | EXACT CONTAINMENT (fully decided) |
| 4 | 14 | 26 | 67 | a_identity_no_dshift | 15 | 5 | 0 | 10 | 0 | CONTAINMENT HOLDS ON DECIDED SUBSET (100% of 5/15; 10 inconclusive) |
| 4 | 14 | 26 | 67 | a_identity_dshift22 | 15 | 0 | 0 | 15 | 0 | ALL INCONCLUSIVE |
| 4 | 14 | 26 | 67 | b_mult3pow53_no_dshift | 15 | 0 | 15 | 0 | 0 | DEAD |
| 4 | 14 | 26 | 67 | b_mult3pow53_dshift22 | 15 | 0 | 15 | 0 | 0 | DEAD |
| 4 | 14 | 26 | 67 | c_forward53_a_eq_ck | 15 | 15 | 0 | 0 | 0 | EXACT CONTAINMENT (fully decided) |
| 5 | 1 | 27 | 54 | a_identity_no_dshift | 12 | 11 | 0 | 1 | 0 | CONTAINMENT HOLDS ON DECIDED SUBSET (100% of 11/12; 1 inconclusive) |
| 5 | 1 | 27 | 54 | a_identity_dshift22 | 12 | 0 | 7 | 5 | 0 | DEAD |
| 5 | 1 | 27 | 54 | b_mult3pow53_no_dshift | 12 | 0 | 12 | 0 | 0 | DEAD |
| 5 | 1 | 27 | 54 | b_mult3pow53_dshift22 | 12 | 0 | 12 | 0 | 0 | DEAD |
| 5 | 1 | 27 | 54 | c_forward53_a_eq_ck | 12 | 12 | 0 | 0 | 0 | EXACT CONTAINMENT (fully decided) |
| 5 | 16 | 27 | 69 | a_identity_no_dshift | 15 | 3 | 0 | 12 | 0 | CONTAINMENT HOLDS ON DECIDED SUBSET (100% of 3/15; 12 inconclusive) |
| 5 | 16 | 27 | 69 | a_identity_dshift22 | 15 | 0 | 0 | 15 | 0 | ALL INCONCLUSIVE |
| 5 | 16 | 27 | 69 | b_mult3pow53_no_dshift | 15 | 0 | 15 | 0 | 0 | DEAD |
| 5 | 16 | 27 | 69 | b_mult3pow53_dshift22 | 15 | 0 | 15 | 0 | 0 | DEAD |
| 5 | 16 | 27 | 69 | c_forward53_a_eq_ck | 15 | 11 | 0 | 4 | 0 | CONTAINMENT HOLDS ON DECIDED SUBSET (100% of 11/15; 4 inconclusive) |

## 4. Size comparison smoke test (Step 4, NOT proof of embedding)

### Small-side structural (exact)

| C | m | live | possible | live_fraction |
|---:|---:|---:|---:|---:|
| 1 | 1 | 4 | 6 | 6.666667e-01 |
| 1 | 2 | 8 | 18 | 4.444444e-01 |
| 1 | 3 | 12 | 54 | 2.222222e-01 |
| 1 | 4 | 24 | 162 | 1.481481e-01 |
| 1 | 5 | 36 | 486 | 7.407407e-02 |
| 1 | 6 | 72 | 1458 | 4.938272e-02 |
| 2 | 1 | 6 | 9 | 6.666667e-01 |
| 2 | 2 | 14 | 27 | 5.185185e-01 |
| 2 | 3 | 27 | 81 | 3.333333e-01 |
| 2 | 4 | 64 | 243 | 2.633745e-01 |
| 2 | 5 | 123 | 729 | 1.687243e-01 |
| 2 | 6 | 282 | 2187 | 1.289438e-01 |
| 2 | 7 | 651 | 6561 | 9.922268e-02 |
| 2 | 8 | 1364 | 19683 | 6.929838e-02 |
| 2 | 9 | 3220 | 59049 | 5.453098e-02 |
| 3 | 1 | 8 | 12 | 6.666667e-01 |
| 3 | 2 | 21 | 36 | 5.833333e-01 |
| 3 | 3 | 46 | 108 | 4.259259e-01 |
| 3 | 4 | 118 | 324 | 3.641975e-01 |
| 3 | 5 | 262 | 972 | 2.695473e-01 |
| 3 | 6 | 641 | 2916 | 2.198217e-01 |
| 3 | 7 | 1586 | 8748 | 1.812986e-01 |
| 3 | 8 | 3727 | 26244 | 1.420134e-01 |
| 3 | 9 | 9405 | 78732 | 1.194559e-01 |
| 3 | 10 | 21254 | 236196 | 8.998459e-02 |
| 3 | 11 | 52400 | 708588 | 7.394988e-02 |
| 4 | 1 | 10 | 15 | 6.666667e-01 |
| 4 | 2 | 27 | 45 | 6.000000e-01 |
| 4 | 3 | 67 | 135 | 4.962963e-01 |
| 4 | 4 | 178 | 405 | 4.395062e-01 |
| 4 | 5 | 433 | 1215 | 3.563786e-01 |
| 4 | 6 | 1115 | 3645 | 3.058985e-01 |
| 4 | 7 | 2907 | 10935 | 2.658436e-01 |
| 4 | 8 | 7381 | 32805 | 2.249962e-01 |
| 4 | 9 | 19303 | 98415 | 1.961388e-01 |
| 4 | 10 | 47276 | 295245 | 1.601246e-01 |
| 4 | 11 | 121930 | 885735 | 1.376597e-01 |
| 4 | 12 | 317177 | 2657205 | 1.193649e-01 |
| 4 | 13 | 799891 | 7971615 | 1.003424e-01 |
| 4 | 14 | 2094423 | 23914845 | 8.757836e-02 |
| 5 | 1 | 12 | 18 | 6.666667e-01 |
| 5 | 2 | 33 | 54 | 6.111111e-01 |
| 5 | 3 | 86 | 162 | 5.308642e-01 |
| 5 | 4 | 238 | 486 | 4.897119e-01 |
| 5 | 5 | 616 | 1458 | 4.224966e-01 |
| 5 | 6 | 1653 | 4374 | 3.779150e-01 |
| 5 | 7 | 4479 | 13122 | 3.413352e-01 |
| 5 | 8 | 11930 | 39366 | 3.030534e-01 |
| 5 | 9 | 32313 | 118098 | 2.736117e-01 |
| 5 | 10 | 83539 | 354294 | 2.357901e-01 |
| 5 | 11 | 223498 | 1062882 | 2.102755e-01 |
| 5 | 12 | 602161 | 3188646 | 1.888454e-01 |
| 5 | 13 | 1585049 | 9565938 | 1.656972e-01 |
| 5 | 14 | 4281077 | 28697814 | 1.491778e-01 |
| 5 | 15 | 10947415 | 86093442 | 1.271574e-01 |
| 5 | 16 | 29178661 | 258280326 | 1.129728e-01 |

### Big-side Monte Carlo estimate (NOT exact)

| C | m | C2 | m2 | decided/samples | est. live_frac (big) | exact live_frac (small) | ratio |
|---:|---:|---:|---:|:---|---:|---:|---:|
| 1 | 6 | 23 | 59 | 31/60 | 0.0968 | 4.938272e-02 | 1.960 |
| 2 | 9 | 24 | 62 | 25/60 | 0.0400 | 5.453098e-02 | 0.734 |
| 3 | 11 | 25 | 64 | 27/60 | 0.1111 | 7.394988e-02 | 1.503 |
| 4 | 14 | 26 | 67 | 31/60 | 0.0645 | 8.757836e-02 | 0.737 |
| 5 | 16 | 27 | 69 | 35/60 | 0.0571 | 1.129728e-01 | 0.506 |

## 5. Honest limitations (what was NOT tested / could not be tested)

- **Dense enumeration of the big-side automaton A(C+22, m+53) is mathematically impossible on any hardware**: even the smallest required big-side precision (m+53 >= 54) needs 3^54 ~ 5.8e25 residues per deficit level. This is not a compute-budget limitation to be optimized away; it is combinatorial.
- The big-side membership oracle (backward reachability, see oracle.py) is exact where it decides, but its decidability (non-inconclusive) rate DROPS as corridor width and precision grow, even at C+22=23 (the narrowest big-side corridor tested). This means containment claims are demonstrated on a DECREASING fraction of the sampled elements as (C,m) grows -- see the 'inconclusive' column throughout.
- **Surjectivity of any candidate map was NOT tested** -- this would require enumerating live(C+22,m+53) in full, which is exactly the infeasible operation above. All verdicts in Section 3 concern containment (phi(live) subset of live'), not surjectivity.
- Sample sizes per (C,m) pair are capped at 15 elements (40 in an initial, abandoned run at C=1 only -- see embedding_test.py's 'NOTE ON BUDGET TUNING' comment) for compute-time reasons; this is a SAMPLE, not exhaustive coverage, of live(C,m).
- Corridor widths C=6..15 (required by the mission spec's C=1..15 range) were **not reached** on the small side: dense computation at C=6's target precision (m=18) already requires ~2.7 billion states, and C=7+ requires 8e10+ states -- both infeasible in the time available. Only C=1..5 were computed. This is reported here explicitly rather than silently narrowing scope.
- The initial embedding-test run (uncapped, MAX_ELEMENTS_PER_PAIR=40, ORACLE_CALL_CAP=800,000) was killed after ~100s once it became clear it would not finish C=2..5 in reasonable time; it was restarted with tighter budgets (15 elements, 150,000 call cap, 90s per-pair wall-clock budget) that traded per-pair depth for breadth across C. No pair in the final run hit the 90s wall-clock cap (all completed under it), so the reported results are not truncated by that budget -- only by the per-query oracle call cap (visible in the 'inconclusive' counts).
- The Monte Carlo big-side live-fraction estimates (Section 4, Part 2) use only 60 samples per (C,m) pair, of which roughly 25-35 resolved (the rest inconclusive) -- standard error on the resulting fraction is large (~0.06-0.09). The ratios reported (0.5x to 2.0x) show no clean pattern at this sample size and should NOT be read as evidence of (or against) a specific closed-form size relationship.
- Candidate (c)'s exponent policy (a = c_k at every step) is one natural choice among several the raw automaton's branching permits; other fixed policies (e.g. always-maximal-a, or policies tied to a specific target residue's own forward trajectory) were not tested.
