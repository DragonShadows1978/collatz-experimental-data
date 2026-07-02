# Lock 3 Shadow-Birth Digit Analysis

Status: first direct trigger-residue extraction.

Date: 2026-05-24

## Result

The shadow births are exact modular trigger digits.

For the top-edge birth cases checked so far, the scanner's birth audit reduces
to a simple residue trigger:

```text
child key:    (deficit = 0, residue = 1)
parent key:   (deficit = 0, residue = 3^(m-1) + 1)
exponent:     2
```

In base 3, the parent trigger digit is:

```text
1 00...00 1
```

with width `m`.

Equivalently:

```text
parent_residue = 3^(m-1) + 1
```

## Birth Object

A birth should be treated as one of two objects:

```text
integral birth:        attaches to a specific integer witness
residue-shadow birth:  attaches to a specific residue class not yet proven integral
```

The scanner currently records the residue-shadow object:

```text
(C, m, depth, deficit_state, residue_signature)
```

This means:

```text
x == residue_signature mod 3^m
```

inside the recorded deficit state.

If a concrete witness exists for that residue class and all lineage constraints
are satisfied, the shadow can be promoted to an integral birth:

```text
residue shadow -> specific integer witness
```

If no concrete witness has been attached yet, the birth remains a modular
shadow:

```text
specific trigger address, not yet a specific integer orbit
```

This distinction matters. The birth audit proves the modular trigger obeys the
birth ceiling. A separate integrality/reachability check attaches that trigger
to an actual integer, if such a witness exists.

## Congruence Check

The scanner transition is:

```text
next_residue = ((3r + 1) * inverse(2^a)) mod 3^m
```

For the top-edge births, `a = 2` and `next_residue = 1`, so:

```text
((3r + 1) / 4) == 1 mod 3^m
```

or:

```text
3r + 1 == 4 mod 3^m
3r == 3 mod 3^m
r == 1 mod 3^(m-1)
```

The scanner's reachable top-edge trigger is the middle edge digit:

```text
r = 3^(m-1) + 1
```

## Checked Top-Edge Cases

| C | m | modulus | parent residue | base-3 digit | child residue | exponent | birth rows |
|---:|---:|---:|---:|---|---:|---:|---:|
| 1 | 4 | 81 | 28 | `1001` | 1 | 2 | 84 |
| 2 | 7 | 2187 | 730 | `1000001` | 1 | 2 | 23 |
| 3 | 9 | 19683 | 6562 | `100000001` | 1 | 2 | 62 |
| 4 | 12 | 531441 | 177148 | `100000000001` | 1 | 2 | 4 |
| 5 | 14 | 4782969 | 1594324 | `10000000000001` | 1 | 2 | 43 |

Every checked transition validates directly against the scanner transition
formula.

## Interior Example

The interior `C=5, m=8` run is noisier but still deterministic.

It has:

```text
birth_rows = 1108
unique_parent_triggers = 12
unique_child_keys = 3
transition_validation = PASS
```

The dominant parent trigger residues are:

| parent residue | base-3 digit | count |
|---:|---|---:|
| 2188 | `10000001` | 631 |
| 4375 | `20000001` | 256 |
| 4379 | `20000012` | 159 |
| 2192 | `10000012` | 62 |

This confirms that interior shadow births can use multiple modular trigger
digits, while the top-edge birth is the clean `3^(m-1)+1` trigger.

## Utility

The analyzer is:

```text
scripts/lock3_shadow_birth_digits.py
```

Example:

```text
python3 scripts/lock3_shadow_birth_digits.py \
  Lock3_birth_audit/full_3c_plus_1_n250/c4_m12_n250/lock3_birth_invariant_audit.csv
```

It decodes:

```text
parent trigger residues
base-3 digits
child keys
transition exponent
transition validation
```

## Interpretation

The birth audit is not just counting abstract shadows.

It is exposing exact modular trigger addresses. At the top edge, the address is
the ternary edge digit:

```text
100...001
```

That gives a concrete digit-level object for the proof: the shadow birth is a
specific residue in `mod 3^m`, and the scanner can verify exactly that it maps
to terminal residue `1` under the allowed exponent.
