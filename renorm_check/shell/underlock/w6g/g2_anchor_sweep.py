#!/usr/bin/env python3
"""
W6G-G2 -- Anchor sweep (is the loop's throne anchored to rho=1?).

Per W6G_BREAK_IT_ORDER.md G2: sweep the terminal anchor rho_end over
ALL admissible residues mod 27 and mod 81 (classes 1 and 2 mod 3 only;
class 0 has no legal backward step per w6e/engine.py's
forced_parity_for_backward_step), small m (2..8), golden + sqrt2 words:
measure D(r, m) by census.

Registered conjecture: D(r, m) = L(m) + h(r), h(r) >= 0 an
m-independent "descent cost to the 1-ray", stabilizing once m exceeds
a small threshold. Fable 60%.

--- Engine extension ---
w6e/engine.py's bfs_Dm / bfs_Dm_fast hardcode target_r = 1 % mod. This
experiment needs an arbitrary target residue. Extension `bfs_Dm_fast_
target` below is a thin wrapper reusing engine.py's OWN primitives
(allowed_exponents, _get_permutation) verbatim -- no new mechanics,
only the final survivor-selection target is parameterized. Validated
below: target_r=1 exactly reproduces 3 ground-truth rows (golden m=5,
m=9; sqrt2 m=8) before trusting any r!=1 result.

Note on "mod 27 / mod 81" vs the engine's own working modulus 3^m: for
small m (2..8), 3^m ranges 9..6561. Sweeping target residues mod 27 or
mod 81 while the working modulus is 3^m requires m >= 3 (mod 27) or
m >= 4 (mod 81) for the target residue class to be meaningfully
distinct mod the working modulus; for m < that threshold the "mod 27"
or "mod 81" target collapses/repeats mod 3^m (e.g. m=2, modulus=9: a
residue mod 27 folds onto residues mod 9 many-to-one). Handled
explicitly: for each m, target residues are enumerated mod
gcd-compatible scale = min(27 or 81, 3^m) via r_target = r0 % (3**m)
for r0 in the admissible mod-27/81 class list, and duplicate targets
(same r0 % 3**m) are recorded but only measured once (deduplicated,
not silently dropped -- the mapping is logged).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
from engine import allowed_exponents, _get_permutation, bfs_Dm_fast  # noqa: E402

HERE = Path(__file__).parent
C = 12


def credit_golden_per8(k: int) -> int:
    return (13 * (k + 1)) // 8 - (13 * k) // 8


def credit_sqrt2_per12(k: int) -> int:
    return (17 * (k + 1)) // 12 - (17 * k) // 12


def bfs_Dm_fast_target(credit_fn, m: int, C: int, target_r: int, anchor_steps: int = 53):
    """Same mechanics as engine.bfs_Dm_fast, target residue parameterized
    instead of hardcoded to 1. Reuses engine.allowed_exponents and
    engine._get_permutation verbatim (no new transition logic)."""
    modulus = 3 ** m
    phase = anchor_steps - m
    live_by_d = {d: np.ones(modulus, dtype=bool) for d in range(C + 1)}
    for k in range(m):
        c = credit_fn(phase + k)
        next_live_by_d = {d: np.zeros(modulus, dtype=bool) for d in range(C + 1)}
        for d in range(C + 1):
            src = live_by_d[d]
            live_r_indices = np.nonzero(src)[0]
            if live_r_indices.size == 0:
                continue
            for a in allowed_exponents(d, c, C):
                d_prime = d + c - a
                perm = _get_permutation(a, modulus)
                targets = perm[live_r_indices]
                next_live_by_d[d_prime][targets] = True
        live_by_d = next_live_by_d
    tr = target_r % modulus
    alive_d = [d for d in range(C + 1) if live_by_d[d][tr]]
    if not alive_d:
        return None
    return C - max(alive_d)


def validate_extension():
    print("=== Pre-experiment validation: bfs_Dm_fast_target(target_r=1) "
          "vs 3 ground-truth rows ===")
    checks = [
        ("golden-per8 m=5", credit_golden_per8, 5, 2),
        ("golden-per8 m=9", credit_golden_per8, 9, 3),
        ("sqrt2-per12 m=8", credit_sqrt2_per12, 8, 4),
    ]
    all_pass = True
    for label, fn, m, expected in checks:
        D_orig = bfs_Dm_fast(fn, m, C, anchor_steps=53)
        D_ext = bfs_Dm_fast_target(fn, m, C, target_r=1, anchor_steps=53)
        ok = (D_ext == expected == D_orig)
        print(f"  {label}: original_engine={D_orig} extension(target_r=1)={D_ext} "
              f"expected={expected} {'PASS' if ok else 'FAIL'}")
        all_pass = all_pass and ok
    print(f"=== Validation: {'ALL PASS' if all_pass else 'SOME FAILED -- STOP'} ===\n")
    if not all_pass:
        raise SystemExit("Extension validation failed -- refusing to run G2 sweep.")


def admissible_classes(mod_target: int):
    """All r0 in [0, mod_target) with r0 % 3 in {1, 2} (class 0 excluded,
    no legal backward step ever, per engine.forced_parity_for_backward_step)."""
    return [r0 for r0 in range(mod_target) if r0 % 3 != 0]


def main():
    validate_extension()

    families = [
        ("golden-per8", credit_golden_per8),
        ("sqrt2-per12", credit_sqrt2_per12),
    ]
    m_scope = list(range(2, 9))  # 2..8 per the order
    mod_targets = [27, 81]

    results = []
    dedup_log = []

    for family_name, fn in families:
        for m in m_scope:
            modulus = 3 ** m
            D_at_1 = bfs_Dm_fast_target(fn, m, C, target_r=1, anchor_steps=53)
            for mod_target in mod_targets:
                classes = admissible_classes(mod_target)
                seen_targets = {}
                for r0 in classes:
                    tr = r0 % modulus
                    if tr in seen_targets:
                        dedup_log.append({
                            "family": family_name, "m": m, "mod_target": mod_target,
                            "r0": r0, "folds_onto_r0": seen_targets[tr],
                            "effective_target": tr,
                        })
                        D = seen_targets[tr][1]
                    else:
                        D = bfs_Dm_fast_target(fn, m, C, target_r=r0, anchor_steps=53)
                        seen_targets[tr] = (r0, D)
                    h_r = None
                    if D is not None and D_at_1 is not None:
                        h_r = D - D_at_1
                    results.append({
                        "family": family_name, "m": m, "mod_target": mod_target,
                        "r0": r0, "r0_mod3": r0 % 3, "effective_target_mod_3m": tr,
                        "D_r": D, "D_at_r1": D_at_1, "h_r": h_r,
                    })
            print(f"{family_name} m={m}: D(r=1)={D_at_1}, "
                  f"{len(classes)} classes swept per modulus (27, 81)")

    out_csv = HERE / "g2_anchor_sweep.csv"
    with open(out_csv, "w", newline="") as f:
        fieldnames = ["family", "m", "mod_target", "r0", "r0_mod3",
                      "effective_target_mod_3m", "D_r", "D_at_r1", "h_r"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in results:
            w.writerow(r)
    print(f"\nWrote {out_csv} ({len(results)} rows)")

    dedup_csv = HERE / "g2_dedup_log.csv"
    with open(dedup_csv, "w", newline="") as f:
        fieldnames = ["family", "m", "mod_target", "r0", "folds_onto_r0", "effective_target"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in dedup_log:
            w.writerow(r)
    print(f"Wrote {dedup_csv} ({len(dedup_log)} rows) -- residues that folded together mod 3^m < mod_target")

    # Analyze: for each (family, mod_target, r0), does h(r) stabilize across m
    # (m-independent once m exceeds a small threshold)? And is h(r) >= 0 always?
    print("\n=== Analysis: h(r) non-negativity and m-stability ===")
    from collections import defaultdict
    by_key = defaultdict(dict)  # (family, mod_target, r0) -> {m: h_r}
    for r in results:
        if r["h_r"] is not None:
            by_key[(r["family"], r["mod_target"], r["r0"])][r["m"]] = r["h_r"]

    n_negative = 0
    negative_dump = []
    n_stable = 0
    n_total_keys = 0
    instability_dump = []
    for key, m_to_h in by_key.items():
        n_total_keys += 1
        ms_sorted = sorted(m_to_h.keys())
        vals = [m_to_h[m] for m in ms_sorted]
        if any(v < 0 for v in vals):
            n_negative += 1
            negative_dump.append({"key": key, "m_to_h": dict(zip(ms_sorted, vals))})
        # stability: values for m >= some small threshold (say m>=5) all equal
        tail_vals = [m_to_h[m] for m in ms_sorted if m >= 5]
        if tail_vals and len(set(tail_vals)) == 1:
            n_stable += 1
        elif tail_vals:
            instability_dump.append({"key": key, "m_to_h_tail": dict(zip([m for m in ms_sorted if m>=5], tail_vals))})

    print(f"Total (family,mod_target,r0) keys analyzed: {n_total_keys}")
    print(f"h(r) < 0 somewhere (conjecture requires h(r)>=0 always): "
          f"{n_negative}/{n_total_keys} keys have a violation "
          f"{'(NONE -- clean)' if n_negative == 0 else '-- BREAK'}")
    print(f"h(r) stabilizes for m>=5 (constant tail): {n_stable}/{n_total_keys}")

    neg_csv = HERE / "g2_negative_h_dump.csv"
    with open(neg_csv, "w", newline="") as f:
        f.write("family,mod_target,r0,m_to_h\n")
        for row in negative_dump:
            fam, modt, r0 = row["key"]
            f.write(f"{fam},{modt},{r0},\"{row['m_to_h']}\"\n")
    print(f"Wrote {neg_csv} ({len(negative_dump)} rows) -- h(r)<0 counterexamples, should be empty if conjecture holds")

    instab_csv = HERE / "g2_instability_dump.csv"
    with open(instab_csv, "w", newline="") as f:
        f.write("family,mod_target,r0,m_to_h_tail\n")
        for row in instability_dump:
            fam, modt, r0 = row["key"]
            f.write(f"{fam},{modt},{r0},\"{row['m_to_h_tail']}\"\n")
    print(f"Wrote {instab_csv} ({len(instability_dump)} rows) -- non-stabilizing h(r) rows")

    print("\n=== GATE VERDICT vs frozen prediction "
          "(D(r,m) = L(m) + h(r), h(r)>=0 m-independent for m>=threshold, 60%) ===")
    if n_negative == 0 and n_stable == n_total_keys:
        print("HIT: h(r) >= 0 everywhere AND stabilizes for all keys by m=5.")
    elif n_negative == 0:
        print(f"PARTIAL: h(r) >= 0 holds everywhere (no negative h), but stabilization "
              f"is NOT universal ({n_stable}/{n_total_keys} keys stabilize by m=5) -- "
              f"MISS on the full conjecture as stated (both non-negativity AND "
              f"m-independence required).")
    else:
        print(f"MISS (BREAK): h(r) < 0 found on {n_negative}/{n_total_keys} keys -- "
              f"see g2_negative_h_dump.csv for exact counterexamples.")


if __name__ == "__main__":
    main()
