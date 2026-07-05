# W6V-MEASURE -- interpretation note (NEW MEASUREMENT, 2026-07-04)

This note clarifies one field in `sweep_new_C.log` that is easy to
misread. It does not add any new numbers -- every number here traces to
`sweep_new_C.log` or `validate_c5.log`, both captured verbatim stdout.

## Validation gate (validate_c5.py / validate_c5.log)

Fresh reproduction of M_edge(1..5) via `automaton.run_heartbeat`,
independent of the pre-existing `shell_probe.log`. Result: **PASS, 5/5**.

| C | measured_edge | known_edge (Tier-1) | formula | match |
|---|---|---|---|---|
| 1 | 4  | 4  | 4  | Y |
| 2 | 7  | 7  | 7  | Y |
| 3 | 9  | 9  | 9  | Y |
| 4 | 12 | 12 | 12 | Y |
| 5 | 14 | 14 | 14 | Y |

Each row's death certificate (first dead m, confirmed to stay dead through
the walked margin) is in `validate_c5.log`.

## Main sweep (sweep_new_C.py / sweep_new_C.log)

### C=6 -- GENUINE, COMPLETE

`measured_edge=16` is a real death edge: m=16 alive (dt=143.23s), m=17
dead (dt=433.10s) -- the death certificate. **Matches formula
floor(53*7/22)=16 exactly.**

### C=7 -- INCONCLUSIVE, NOT a formula deviation

The log's line

```
--- C=7 summary: measured_edge=17 formula=19 match=False ... ---
```

reads, out of context, like a measured mismatch against the formula's
prediction of 19. **It is not.** `measured_edge=17` in this row means
only "the highest m we actually tested was m=17, and it was alive" --
the sweep never reached m=18 or m=19 at all. The wall_hit field says
why:

```
run_heartbeat guard tripped at m=18: state space too large:
C=7, m=18, modulus=3^18=387420489, total_states=3099363912 > guard 2500000000
```

We do not know whether the terminal-compatible set is alive or dead at
m=18 or m=19 for C=7. `match=False` is an artifact of the script
comparing "last m tested" to "formula prediction" -- it is FALSE by
construction whenever the sweep is cut off before reaching the
predicted edge, regardless of what the true edge is. **This is not
evidence against the formula.** C=7 is UNMEASURED at and above m=18.

### Why we did not raise the guard and retry

The naive guard (2.5e9 states, ~1 byte/state as numpy bool) suggested
m=18 for C=7 should need only ~3.1GB. But the actual resource driver is
`automaton.py`'s module-level `_PERM_CACHE`, which stores one `int64`
(8 bytes/element) array of length 3^m per distinct exponent `a` used
across the 53-step heartbeat, and never clears. Cross-checking the two
completed m=17 data points:

- C=6, m=17: naive bytes = 7 * 3^17 = 0.90 GB; observed RSS = 12002.2 MB
  -> observed/naive = 13.28x
- C=7, m=17: naive bytes = 8 * 3^17 = 1.03 GB; observed RSS = 13434.7 MB
  -> observed/naive = 13.00x

This ~13x multiplier is consistent across both data points. Applying it
to C=7, m=18 (naive 3.10 GB) projects an actual RSS of roughly **40 GB**
for a single process on a 62 GB machine -- too close to the physical
ceiling to safely retry, and this is a real, predictable cost driver
(not a fixable guard mis-setting). This is the honest resource wall:
**C=7, m=18, projected ~40GB RSS from a validated ~13x observed/naive
multiplier, is where the automaton.py instrument stops being usable on
this hardware.**

No Rust cross-check was attempted for C=6/C=7 beyond what's already in
this note, since the primary instrument's own guard-tripped wall was
reached within the round's time budget; see the final report for why a
Rust `lock3_census` true per-m sweep was judged likely to hit an
analogous or worse wall (dense per-m residue tracking is not what that
binary's C=6..50 archived runs used -- see SYNTHESIS.md's W6T-PROV entry
-- and building a genuine dense sweep driver for it was out of scope
given the automaton wall was reached first).
