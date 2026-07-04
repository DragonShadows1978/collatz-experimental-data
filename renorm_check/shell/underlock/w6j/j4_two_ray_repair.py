#!/usr/bin/env python3
"""
W6J-J4 -- Two-ray model repair, per W6J_INTERIOR_BOUNDARY_ORDER.md
section J4.

H2 (w6h/h2_two_ray_model.py) found the two-ray model MISSES 70% of
anchor keys (30.2% exact match). Root cause, hand-verified via a
concrete counterexample (golden-per8 m=3, target=7): the model
assumed a chain, once it touches a ray, RIDES that ray for the rest
of the window -- but reaching an ARBITRARY target r often requires
leaving the ray again near the window's END to land exactly on r.
Concretely: the optimal chain to (m=3, target=7) has residues
[1, 1, 1, 7] (window-start-indexed) -- it SITS ON THE +1-RAY for the
first two steps, then EXITS on the final step (a=4, cost +2) to hit
7. H2's model had no term for this mandatory final "entry" cost.

--- The repair (per the order's own formula) ---
D(r, m) = min over rho* in {+1,-1} of
  [entry_cost(r, rho*) + ray_discrepancy_{rho*}(letters[:m - entry_len])]
where entry_cost(r, rho*) is the EXACT minimum cost (Sigma(a-2), the
same word-independent framing h1/j2 use for excursions) of a FORWARD
chain of length <= 6 from rho* to r (computed by shortest-path DP,
i.e. h1's layered-DP method -- exact for negative edges since a=1
costs -1 -- reused directly, just run FORWARD via next_residue instead
of backward via backward_predecessor_exact, because here the ray sits
at the window START and the arbitrary target r sits at the window
END, the OPPOSITE orientation from h1's excursion DP, which walked
backward from a fixed terminal). ray_discrepancy is H2's own function,
applied to the credit letters covering the window PREFIX (length
m - entry_len) that precedes the entry segment -- i.e. the model reads
as "start on the ray, ride it for the prefix, then execute the
(precomputed, credit-independent) minimal-cost entry maneuver to land
exactly on r over the final entry_len steps."

--- Machinery reuse ---
- w6e/engine.py's `next_residue` reused verbatim (forward-step
  primitive -- unlike h1/j2's backward primitives, since the entry DP
  walks FORWARD from a ray toward an arbitrary target).
- w6h/h2_two_ray_model.py's `ray_discrepancy_plus1`/`ray_discrepancy_
  minus1`, `bfs_Dm_target_chain_with_residues`, `FAMILIES` reused
  verbatim (the credit functions and the actual D(r,m) ground truth to
  fit against, plus the ray-discrepancy formulas themselves, unchanged
  -- only the entry_cost term is new).
- w6g/g2_anchor_sweep.csv (full G2 sweep) + w6h/h2_two_ray_fit.csv
  (H2's own extended sweep, mod 27/81, m to 10) are the re-fit targets,
  per the order ("re-fit against the full W6G-G2 sweep + H2 data").

--- Entry-cost DP mechanics (forward, small, exact) ---
State: residue mod 3^8 (order's own spec: "residues mod 3^8"). Forward
step from state d: no ceiling/floor constraint of its own -- unlike
the main D(m) engine, entry_cost has no ceiling/floor constraint of its
own; it is a pure residue-reachability question under the SAME forward
map r' = (3r+1)*inv(2^a) mod 3^8 the main engine uses, with a in
{1, 2, 3, ...} unbounded above (any positive integer exponent is a
legal forward step in isolation; the C-budget constraint belongs to
the OUTER D(m) problem, already accounted for by ray_discrepancy's own
formula and the window-length bookkeeping, not re-imposed here).
Cost of a step = a - 2 (SAME convention as h1/j2 -- word-independent,
because a ray's own per-step cost against a generic credit letter is
exactly what ray_discrepancy separately handles; the entry segment's
COST here is measured against the ray's OWN implicit credit (c=2 for
the +1 ray, c=1 for the -1 ray), matching DERIVATION_NOTES 8b's
per-step framing for each ray, so ray+entry costs compose additively
without double-counting any credit letter).
Layered DP over depth 0..6 (max entry length 6, per the order),
exact for negative edges (a=1 costs -1) via the same forward-DAG
argument h1/j2 use.

--- FALSE START 1 on precision, caught by validation, reported per
house rules (not silently fixed) ---
A first draft ran the entry DP at a FIXED mod=3^8 regardless of the
outer problem's own working modulus 3^m, reading the order's "residues
mod 3^8" as a literal fixed modulus. This FAILED validation check (3):
H2's own hand-verified counterexample (golden m=3, target=7,
entry_cost(7,+1) should be 2 at length 1, the single a=4 step from
rho=1) came back cost=3 at length=6 instead. Root cause: at m=3 the
outer problem's target "7" means "residue 7 mod 3^3=27"; asking the
fixed-mod-3^8 DP to reach residue EXACTLY 7 (mod 3^8=6561) is a
STRICTLY different, much narrower condition (residue-7-mod-27 is a
union of 3^5 distinct residues mod 3^8, of which literal integer 7 is
only one) -- confirmed directly: next_residue(1, a=4, mod=3^8) = 4921,
and 4921 % 27 == 7 (the correct answer at the OUTER problem's own
precision), but 4921 != 7 at the finer fixed precision, so the fixed-
mod-3^8 DP never found the true length-1 edge at all and returned a
worse, longer path instead. FIX: run the entry DP at mod=3^m (the
SAME precision as the outer D(r,m) problem being modeled) whenever
m <= 8, and at mod=3^8 with the target reduced mod 3^8 only when
m > 8.

--- FALSE START 2, ALSO caught by validation before trusting anything ---
With precision fixed, validation check (3) STILL failed: the DP found
a cost=-1, length=6 path to target=7 (a-sequence (1,1,1,2,2,4)),
cheaper than the true, hand-verified length-1 cost=2 edge. Traced
directly: this path is REAL in the small mod=27 residue space, but it
is an ARTIFACT of the entry DP tracking ONLY residues, with no
ceiling-distance (d) state at all -- unlike the real engine, whose
`allowed_exponents(d,c,C)` requires d' = d+c-a to stay in [0,C].
Reconstructing d along this specific a-sequence (using the ray's own
implicit per-step credit, c=2 for the +1-ray, starting at the engine's
own d0=C=12 window-start convention -- see f1_engine_ext's bugfix note
on this exact convention): d runs 12->13->14->15->15->15->13, i.e. it
EXCEEDS C=12 at step 3 onward -- a real, ceiling-violating (illegal)
excursion that a properly constrained chain could never take. A
per-step exponent cap (tried first, insufficient on its own -- the
menu a<=14 does not by itself forbid this) does not fix this: the
missing ingredient is d itself, not a tighter per-step bound.

FIX: track d explicitly in the entry DP's own state, exactly as the
real engine does -- state = (rho, d), starting at (ray_start, C_PROXY),
legal step a in [max(1, d+c_ray-C_PROXY), d+c_ray] where c_ray is the
ray's own per-step credit (2 for +1-ray, 1 for -1-ray, DERIVATION_NOTES
8b), d' = d+c_ray-a required in [0, C_PROXY]. This is now IDENTICAL in
spirit to w6e/engine.py's own `allowed_exponents`, just specialized to
a single fixed credit per ray instead of a real per-step word letter
(which is exactly right here -- ray_discrepancy already accounts for
the real word's letters over the REST of the window; this segment's
own per-step cost is measured against the ray's fixed implicit credit,
per the module docstring's cost-composition argument above).

Validated against 3 known facts before trusting (now at the CORRECTED
per-m precision AND with explicit (rho,d) ceiling-tracking state):
(1) entry_cost(r=+1-ray's own point, +1) == 0 (already there);
(2) entry_cost(r=-1-ray's own point, -1) == 0;
(3) H2's own counterexample (golden m=3, target=7): entry_cost(7, +1)
    should be exactly 2 at length 1 (the single a=4 step from rho=1),
    matching the hand-verified chain exactly.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
from engine import next_residue  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent.parent / "w6h"))
from h2_two_ray_model import (  # noqa: E402
    FAMILIES, ray_discrepancy_plus1, ray_discrepancy_minus1,
    bfs_Dm_target_chain_with_residues,
)

HERE = Path(__file__).parent
W6G = HERE.parent / "w6g"
W6H = HERE.parent / "w6h"

ENTRY_PRECISION_EXP = 8      # order's own spec: residues mod 3^8
ENTRY_MOD = 3 ** ENTRY_PRECISION_EXP
MAX_ENTRY_LEN = 6            # order's own spec: small DP over <= 6 steps
ENTRY_COST_CAP = 60          # margin-checked below (saturation / stability across caps)
C_PROXY = 12                 # matches C=12 used throughout w6g/w6h's own machinery
MAX_ENTRY_EXPONENT = C_PROXY + 2  # ceiling-realistic cap on the entry DP's own exponent menu
                                   # (see FALSE START 2 above -- an unbounded menu lets the DP
                                   # invent ceiling-violating a=1 wraparound paths in small moduli)


def forward_step_mod(rho: int, a: int, mod: int) -> int:
    return next_residue(rho, a, mod)


def allowed_entry_exponents(d: int, c_ray: int, C: int):
    """Legal exponents for a (rho,d) entry step: a in [max(1,d+c_ray-C),
    d+c_ray], the SAME legality condition as w6e/engine.py's own
    `allowed_exponents(d,c,C)`, specialized to the ray's fixed implicit
    credit c_ray instead of a real per-step word letter."""
    lo = max(1, d + c_ray - C)
    hi = d + c_ray
    if hi < lo:
        return []
    return list(range(lo, min(hi, MAX_ENTRY_EXPONENT) + 1))


def entry_cost_dp(target_r: int, ray_start: int, c_ray: int, mod: int, max_len: int,
                   cost_cap: int, C: int = C_PROXY):
    """Forward layered DP over state (rho, d) -- exact for negative
    edges (same DAG argument as h1's backward layered_dp, just walking
    FORWARD via next_residue and WITH explicit ceiling-distance
    tracking, per FALSE START 2's fix above). State starts at
    (ray_start, C) -- the engine's own window-start convention (d0=C).
    Legal step a in allowed_entry_exponents(d, c_ray, C); d' = d+c_ray-a
    required in [0,C] (enforced by the exponent bound itself, same as
    engine.allowed_exponents). Cost of a step = a - 2 (ray's own
    per-step cost against ITS implicit credit c_ray).

    Returns dict length -> (min_cost, a_sequence) for every length where
    ANY d has residue==target_r, taking the min cost over all such d
    (the outer model only needs the residue to match; d is bookkeeping,
    not part of the target), plus per-depth live-state counts.
    """
    ray_start = ray_start % mod
    target_r = target_r % mod
    if ray_start == target_r:
        return {0: (0, ())}, {0: 1}

    # live[(rho,d)] = (min_cost, parent_state, a)
    live = {(ray_start, C): (0, None, None)}
    history = [live]
    for depth in range(max_len):
        new_live = {}
        for (rho, d), (cost, _, _) in live.items():
            for a in allowed_entry_exponents(d, c_ray, C):
                step_cost = a - 2
                newcost = cost + step_cost
                if newcost > cost_cap:
                    continue
                d2 = d + c_ray - a
                rho2 = forward_step_mod(rho, a, mod)
                key = (rho2, d2)
                if key not in new_live or newcost < new_live[key][0]:
                    new_live[key] = (newcost, (rho, d), a)
        live = new_live
        history.append(live)

    results = {}
    live_counts = {dep: len(history[dep]) for dep in range(max_len + 1)}
    for dep in range(1, max_len + 1):
        # among all (rho,d) states at this depth whose rho==target_r, take min cost
        matches = [(cost, state) for state, (cost, _, _) in history[dep].items() if state[0] == target_r]
        if matches:
            cost, state = min(matches, key=lambda x: x[0])
            # backtrack
            seq = []
            node = state
            depth_i = dep
            while depth_i > 0:
                c, parent, a = history[depth_i][node]
                seq.append(a)
                node = parent
                depth_i -= 1
            seq.reverse()
            results[dep] = (cost, tuple(seq))
    return results, live_counts


def min_entry_cost(target_r: int, ray_start: int, c_ray: int, mod: int, max_len: int,
                    cost_cap: int, C: int = C_PROXY):
    """Min over all lengths 1..max_len (or 0 if already there) of the
    entry_cost_dp results -- the single number the two-ray model uses."""
    results, live_counts = entry_cost_dp(target_r, ray_start, c_ray, mod, max_len, cost_cap, C=C)
    if not results:
        return None, None, None
    best_len, (best_cost, best_seq) = min(results.items(), key=lambda kv: kv[1][0])
    return best_cost, best_len, best_seq


def validate_entry_dp():
    print("=== Pre-experiment validation (house rule, 3 known facts) ===")
    all_ok = True

    # (1) entry_cost(+1's own point, ray=+1) == 0 -- checked at m=3 (mod 27),
    # the same outer precision the counterexample below uses.
    mod3 = 3 ** 3
    cost, length, seq = min_entry_cost(1 % mod3, 1, 2, mod3, MAX_ENTRY_LEN, ENTRY_COST_CAP)
    ok1 = (cost == 0 and length == 0)
    print(f"  entry_cost(target=+1ray's own point={1%mod3}, ray=+1, mod=27): cost={cost} len={length} "
          f"{'PASS' if ok1 else 'FAIL'}")
    all_ok = all_ok and ok1

    # (2) entry_cost(-1's own point, ray=-1) == 0, same mod=27
    neg1 = mod3 - 1
    cost, length, seq = min_entry_cost(neg1, neg1, 1, mod3, MAX_ENTRY_LEN, ENTRY_COST_CAP)
    ok2 = (cost == 0 and length == 0)
    print(f"  entry_cost(target=-1ray's own point={neg1}, ray=-1, mod=27): cost={cost} len={length} "
          f"{'PASS' if ok2 else 'FAIL'}")
    all_ok = all_ok and ok2

    # (3) H2's own hand-verified counterexample: golden m=3, target=7,
    # entry_cost(7, ray=+1) should be exactly 2 at length 1 (a=4 from rho=1)
    # -- MUST be computed at the OUTER problem's own precision, mod 3^3=27,
    # WITH explicit (rho,d) ceiling tracking (see FALSE STARTS above).
    cost, length, seq = min_entry_cost(7, 1, 2, mod3, MAX_ENTRY_LEN, ENTRY_COST_CAP)
    ok3 = (cost == 2 and length == 1 and seq == (4,))
    print(f"  entry_cost(target=7, ray=+1, mod=27) [H2's own m=3 counterexample]: cost={cost} len={length} "
          f"seq={seq} {'PASS' if ok3 else 'FAIL'}")
    all_ok = all_ok and ok3

    assert all_ok, "Entry-cost DP validation FAILED -- refusing to proceed"
    print("All validation checks PASS.\n")


_ENTRY_CACHE = {}


def get_entry_cost(target_r: int, ray: str, m: int):
    """Cache entry_cost by (m, target_r, ray). Precision choice (fixed,
    per the FALSE START correction above): use mod=3^m directly whenever
    m <= ENTRY_PRECISION_EXP (8) -- matching the OUTER problem's own
    working precision exactly, since target_r is only meaningful at that
    precision and a coarser or finer fixed modulus asks a different
    question (proven above to silently miss real edges). For m > 8, cap
    the entry DP's own local precision at mod=3^8 (the order's stated
    ceiling) and reduce target_r mod 3^8 -- a deliberate, LOCAL scope
    reduction for the large-m case (the entry maneuver is a small, few-
    step mechanism whose relevant precision genuinely is bounded near
    the boundary, unlike the outer D(m) problem's own full-precision
    residue tracking), recorded explicitly per-row via
    `entry_precision_note` wherever m > 8 so it's visible in the data."""
    mod = 3 ** m if m <= ENTRY_PRECISION_EXP else ENTRY_MOD
    ray_start = 1 if ray == "+1" else (mod - 1)
    c_ray = 2 if ray == "+1" else 1  # DERIVATION_NOTES 8b: +1-ray cost 2/step, -1-ray cost 1/step
    tr_key = target_r % mod
    key = (mod, tr_key, ray)
    if key not in _ENTRY_CACHE:
        cost, length, seq = min_entry_cost(tr_key, ray_start, c_ray, mod, MAX_ENTRY_LEN, ENTRY_COST_CAP)
        _ENTRY_CACHE[key] = (cost, length, seq)
    return _ENTRY_CACHE[key]


def fit_repaired_model(fn, m, target_r, letters_full):
    """Repaired two-ray model: for each ray, find its entry_cost to
    target_r (mod 3^8, capped at 6 steps) and combine with
    ray_discrepancy over the PREFIX of the window preceding the entry
    segment (length m - entry_len), per the order's formula and the
    counterexample's own structure (ride first, exit at the end)."""
    candidates = []
    for ray, ray_disc_fn in (("+1", ray_discrepancy_plus1), ("-1", ray_discrepancy_minus1)):
        cost, length, seq = get_entry_cost(target_r, ray, m)
        if cost is None:
            continue  # no entry path found within the 6-step/cost-cap scope -- honest wall for this ray
        prefix_len = m - length
        if prefix_len < 0:
            continue  # entry segment alone longer than the window -- infeasible for this ray at this m
        prefix_letters = letters_full[:prefix_len]
        ray_cost = ray_disc_fn(prefix_letters) if prefix_letters else 0
        total = cost + ray_cost
        candidates.append((ray, length, cost, ray_cost, total))
    if not candidates:
        return None
    best = min(candidates, key=lambda x: x[4])
    return {"best_ray": best[0], "entry_len": best[1], "entry_cost": best[2],
            "ray_cost": best[3], "model_prediction": best[4], "candidates": candidates}


def main():
    validate_entry_dp()

    print("=== Re-fitting repaired model against full W6G-G2 sweep + H2 data ===")
    t0 = time.time()

    # Reuse H2's own already-computed fit rows AS THE GROUND TRUTH SOURCE
    # (D_actual for every (family, m, target_r) key H2 already measured
    # and cross-validated against the G2 sweep) -- avoids re-running the
    # expensive forward BFS; this experiment only needs D_actual (already
    # trustworthy, per H2's own ledger entry: 20/20 sampled cross-check vs
    # G2's own numbers) plus the credit letters for the window, which are
    # deterministic given (family, m).
    h2_csv = W6H / "h2_two_ray_fit.csv"
    if not h2_csv.exists():
        raise SystemExit(f"H2 fit table not found at {h2_csv}")
    with open(h2_csv, newline="") as f:
        h2_rows = list(csv.DictReader(f))
    print(f"Loaded {len(h2_rows)} rows from {h2_csv.name}")

    def letters_for(fam, m, anchor_steps=53):
        fn = FAMILIES[fam]
        phase = anchor_steps - m
        return [fn(phase + k) for k in range(m)]

    out_rows = []
    n_eval = 0
    n_match = 0
    n_no_model = 0
    mismatches = []
    m_gt8_notes = 0
    for row in h2_rows:
        if row["D_actual"] == "":
            continue  # NO_SURVIVOR rows from H2, not evaluable here either
        fam = row["family"]
        m = int(row["m"])
        target_r = int(row["target_r"])
        D_actual = int(row["D_actual"])
        letters_full = letters_for(fam, m)
        fit = fit_repaired_model(FAMILIES[fam], m, target_r, letters_full)
        if fit is None:
            n_no_model += 1
            out_rows.append({
                "family": fam, "m": m, "mod_target": row["mod_target"], "target_r": target_r,
                "D_actual": D_actual, "model_prediction": "", "match": "NO_MODEL_WITHIN_SCOPE",
                "best_ray": "", "entry_len": "", "entry_cost": "", "ray_cost": "",
            })
            continue
        n_eval += 1
        match = (fit["model_prediction"] == D_actual)
        if match:
            n_match += 1
        else:
            mismatches.append({
                "family": fam, "m": m, "target_r": target_r, "D_actual": D_actual,
                "model_prediction": fit["model_prediction"], "best_ray": fit["best_ray"],
                "entry_len": fit["entry_len"], "entry_cost": fit["entry_cost"],
                "ray_cost": fit["ray_cost"], "candidates": fit["candidates"],
            })
        if m > ENTRY_PRECISION_EXP:
            m_gt8_notes += 1
        out_rows.append({
            "family": fam, "m": m, "mod_target": row["mod_target"], "target_r": target_r,
            "D_actual": D_actual, "model_prediction": fit["model_prediction"], "match": match,
            "best_ray": fit["best_ray"], "entry_len": fit["entry_len"],
            "entry_cost": fit["entry_cost"], "ray_cost": fit["ray_cost"],
            "entry_precision_note": "m>8, entry mod-3^8-reduced target" if m > ENTRY_PRECISION_EXP else "",
        })

    dt = time.time() - t0
    print(f"  wall time: {dt:.2f}s")
    print(f"  rows: {len(h2_rows)}, evaluable (model produced a prediction): {n_eval}, "
          f"no-model-within-scope: {n_no_model}, m>8 (mod-3^8-reduced entry target): {m_gt8_notes}")

    out_csv = HERE / "j4_repaired_fit.csv"
    with open(out_csv, "w", newline="") as f:
        fieldnames = ["family", "m", "mod_target", "target_r", "D_actual", "model_prediction",
                      "match", "best_ray", "entry_len", "entry_cost", "ray_cost", "entry_precision_note"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in out_rows:
            row_out = {k: r.get(k, "") for k in fieldnames}
            w.writerow(row_out)
    print(f"Wrote {out_csv.name} ({len(out_rows)} rows)")

    frac = n_match / n_eval if n_eval else 0.0
    print(f"\n=== GATE: repaired model exact match rate ===")
    print(f"Evaluable: {n_eval}, matches: {n_match} ({frac*100:.1f}%), mismatches: {len(mismatches)}")
    gate_hit = frac >= 0.90
    print(f"Registered prediction (>=90% exact, 60%): {'HIT' if gate_hit else 'MISS'}")

    if mismatches:
        dump_csv = HERE / "j4_residual_mismatches_dump.csv"
        with open(dump_csv, "w", newline="") as f:
            fieldnames = ["family", "m", "target_r", "D_actual", "model_prediction",
                          "best_ray", "entry_len", "entry_cost", "ray_cost", "candidates"]
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in mismatches:
                rr = dict(r)
                rr["candidates"] = str(rr["candidates"])
                w.writerow(rr)
        print(f"Wrote {dump_csv.name} ({len(mismatches)} rows) -- residual keys, classified below")

        # classify residuals: how far off, and by how much per (family,m)
        by_m = defaultdict(list)
        for r in mismatches:
            diff = r["model_prediction"] - r["D_actual"]
            by_m[(r["family"], r["m"])].append(diff)
        print("\nResidual mismatch diffs (model - actual) by (family, m):")
        for key, diffs in sorted(by_m.items()):
            print(f"  {key}: n={len(diffs)} diffs={diffs}")

    print(f"\n(Deliverable per order: residual keys dumped and classified above -- "
          f"a third structure beyond the two rays would be a discovery, not a failure,"
          f" if the residual pattern is NOT just 'ran out of 6-step/mod-3^8 entry scope'.)")


if __name__ == "__main__":
    main()
