# W7B Findings - High-Capacity Sparse Sweep, C >= 27

Work order: `renorm_check/shell/underlock/w7b_deep/W7B_ORDER.md`.
Evidence artifacts:

- `renorm_check/shell/underlock/w7b_deep/sweep_output.log`
- `renorm_check/shell/underlock/w7b_deep/run_c31_highcap.log`
- `renorm_check/shell/underlock/w7b_deep/sweep_full.json`
- `renorm_check/shell/underlock/w7b_deep/sweep_partial.json`
- `renorm_check/shell/underlock/w7a_renorm/w7a_new_edges.txt`

## Validation Gate

The lean instrument re-ran the frozen validation gate before trusting new
cells:

| C | expected edge | result |
|---:|---:|---|
| 16 | 93 | pass |
| 23 | 163 | pass |
| 26 | 205 | pass |

The C=31 high-cap follow-up re-ran the same gate before the high-cap cell.

## Representation

The original sparse instrument stored survivors as Python objects with a
redundant parent-pointer value. The W7B lean variant stores the frontier as
a bare set of `(rho, u, v)` tuples.

- Profiled checkpoint: about 554 bytes/state before, about 313 bytes/state
  after.
- Full C=26 sweep peak RSS dropped from about 1315.4 MB to about 725.4 MB,
  about 1.81x lower.
- C=31 high-cap run peaked at 73,462,829 live states and about 16,773 MB RSS.

## Validated Edges

Only cells with `wall=None`, real `first_dead`, `genuine_death=True`, and
`M(C) > M(C-1)` were appended to `w7a_new_edges.txt`.

| C | M(C) | first_dead | peak_live | elapsed_sec | source |
|---:|---:|---:|---:|---:|---|
| 27 | 208 | 209 | 4,790,754 | 2,297.6 | `sweep_output.log` |
| 28 | 263 | 264 | 9,489,130 | 4,632.5 | `sweep_output.log` |
| 29 | 265 | 266 | 18,595,538 | 13,768.7 | `sweep_output.log` |
| 30 | 282 | 283 | 36,804,069 | 24,504.6 | `sweep_output.log` |
| 31 | 284 | 285 | 73,462,829 | 48,855.0 | `run_c31_highcap.log` |

Monotonicity held across every trusted new edge:
`208 < 263 < 265 < 282 < 284`.

## Wall Handling

The first C=31 attempt in `sweep_output.log` hit the chosen
`state_cap=64,000,000` at m=48 with `n_exact=69,084,627`. That result was
correctly recorded as a wall, not an edge:

- `first_dead=None`
- `genuine_death=False`
- not appended to `w7a_new_edges.txt`

The high-cap follow-up raised the cap to 120,000,000 states and 28,000 MB
RSS. It cleared the old wall and completed the C=31 cell with a real death
certificate:

- `M(31)=284`
- `first_dead=285`
- `peak_live=73,462,829`
- `wall=None`
- `genuine_death=True`

## Current State

C=31 is resolved. The next unresolved cell is C=32. Pushing farther will
need a fresh run with the same frozen validation gate and likely larger
wall-clock budget; C=31 took about 13.57 hours in the high-cap run, with
memory still under the 28 GB RSS cap.
