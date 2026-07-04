#!/usr/bin/env python3
"""
W6H-H2 -- Two-ray decomposition of the anchor sweep, per
W6H_LEMMA_CORE_ORDER.md section H2.

G2 (w6g/g2_anchor_sweep.py) found h(r) = D(r,m) - D(1,m) < 0 on 80/144
keys -- the original "D(r,m) = L(m) + h(r), h(r)>=0 m-independent"
conjecture BROKE. Mechanism hypothesis (DERIVATION_NOTES sec 8b): a
SECOND fixed ray exists, rho===-1 (a=1 forever, cost 1/step, the
"cheap ray" -- the OTHER trivial cycle of 3x+1 on Z, unreachable-
without-overpaying from the real problem's rho=1 anchor, but directly
reachable/cheap when the anchor sweep points at some OTHER residue).

Model: D(r,m) = min over rays rho* in {+1,-1} of
  [descent(r -> rho*-ray) + ray-discrepancy(m - descent-length)]
where the -1-ray discrepancy uses Sum(1 - c_j) (the cheap ray's own
per-step cost, DERIVATION_NOTES 8b: a=1 forever costs 1/step against
credit c, so per-step contribution is 1-c, vs the +1-ray's 2-c).

--- How this is computed here (reusing/extending validated machinery) ---
`bfs_Dm_target_chain_with_residues` below is a direct, thin, target-
parameterized extension of w6e/engine.py's bfs_Dm(want_chain=True) --
IDENTICAL mechanics (same allowed_exponents/next_residue calls, same
parent-pointer backtracking), only the final survivor-selection target
is parameterized (target_r instead of hardcoded 1) and the residue at
EVERY step is captured directly from the (d,r) parent-pointer nodes
during backtracking (no re-derivation needed). This is the same kind
of extension w6g/g2_anchor_sweep.py's own bfs_Dm_fast_target already
validated for the D-only (fast, no-chain) case. Validated below
against the SAME 3 ground-truth rows G2 used, PLUS a direct cross-
check against G2's own already-computed D_r values on a sample of
anchors (this script's chain-extracting version must reproduce the
EXACT SAME D(r,m) numbers G2 already measured with its D-only fast
path -- any mismatch means this new code is wrong, not that G2 was).

For each extracted optimal chain, the DESCENT to each ray is read
directly off the chain's own recovered residue trajectory: scan for
the FIRST step (earliest, closest to the window start) whose residue
equals 1 or 3^m-1. descent-length = that step's index (0 = anchor
itself already on that ray); the descent's own cost is read directly
from the chain's actual (c,a) pairs up to that point (not assumed);
the ray-discrepancy of the remaining suffix is independently
recomputed via the stated formula (max partial sum of (2-c) or (1-c))
and compared against the model's predicted total vs the chain's
ACTUAL D(r,m) (already cross-validated against G2's own numbers above).

--- Extension per the order: mod 81, m to 10 ---
G2 swept mod 27/81 at m=2..8. This extends m to 10 (3^9=19683,
3^10=59049 working moduli -- same machinery, larger m, timed below).
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
from engine import allowed_exponents, next_residue, bfs_Dm_fast  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent.parent / "w6f"))
from f1_engine_ext import forward_live_fast, backward_predecessors_of_r  # noqa: E402

HERE = Path(__file__).parent
W6G = HERE.parent / "w6g"
C = 12


def credit_golden_per8(k: int) -> int:
    return (13 * (k + 1)) // 8 - (13 * k) // 8


def credit_sqrt2_per12(k: int) -> int:
    return (17 * (k + 1)) // 12 - (17 * k) // 12


FAMILIES = {
    "golden-per8": credit_golden_per8,
    "sqrt2-per12": credit_sqrt2_per12,
}


_FORWARD_LIVE_CACHE = {}


def _get_forward_live(credit_fn, family_name, m, C, anchor_steps=53):
    """Cache forward_live_fast's (letters, history) per (family, m) --
    it does NOT depend on target_r, so computing it once per (family,m)
    and reusing it across every swept target residue is a huge speedup
    (the forward pass, not the backward single-chain extraction, is the
    expensive part). Keyed by family_name (a label, not the function
    object) + m + C + anchor_steps."""
    key = (family_name, m, C, anchor_steps)
    if key not in _FORWARD_LIVE_CACHE:
        _FORWARD_LIVE_CACHE[key] = forward_live_fast(credit_fn, m, C, anchor_steps=anchor_steps)
    return _FORWARD_LIVE_CACHE[key]


def extract_one_chain_with_residues(letters, history, m, C, modulus, terminal_d, target_r):
    """Single-chain backward extraction, reusing f1_engine_ext's
    validated `backward_predecessors_of_r` (the exact modular inverse
    construction distinct_optimal_a_sequences itself uses) and the
    SAME `history` boolean-live-array structure -- just picks the FIRST
    legal, live predecessor at each step (one representative chain, not
    the full optimal set) and records the residue at every step
    directly (no separate re-derivation, no representative-dependence
    issue: history[step-1][d0][r0] is checked for liveness at the EXACT
    r0 backward_predecessors_of_r returns, which is intrinsically the
    canonical [0,modulus) representative)."""
    node_d, node_r = terminal_d, target_r % modulus
    chain = []
    residues = [node_r]
    for step in range(m, 0, -1):
        c = letters[step - 1]
        live_prev = history[step - 1]
        found = None
        for d0 in range(C + 1):
            a = d0 + c - node_d
            if a < 1:
                continue
            lo = max(1, d0 + c - C)
            hi = d0 + c
            if not (lo <= a <= hi):
                continue
            for r0 in backward_predecessors_of_r(node_r, a, modulus):
                if live_prev[d0][r0]:
                    found = (d0, r0, a)
                    break
            if found:
                break
        if found is None:
            raise AssertionError(
                f"extract_one_chain_with_residues: no legal live predecessor "
                f"at step {step} for (d={node_d}, r={node_r}) -- should be "
                f"impossible if terminal_d/target_r came from a genuine "
                f"survivor in this SAME history")
        d0, r0, a = found
        chain.append((c, a))
        residues.append(r0)
        node_d, node_r = d0, r0
    chain.reverse()
    residues.reverse()
    return chain, residues


def bfs_Dm_target_chain_with_residues(credit_fn, m: int, C: int, target_r: int,
                                       anchor_steps: int = 53, family_name: str = None):
    """FAST path: reuses the cached vectorized forward_live_fast pass
    (family_name used as the cache key -- pass it whenever available;
    falls back to id(credit_fn) if not given, still correct, just
    without cross-call cache reuse) plus extract_one_chain_with_residues
    for the backward single-chain extraction. Returns (D, chain,
    residues) with the SAME schema/semantics as the (now-removed) slow
    scalar bfs_Dm-based version this replaced (timed: m=9 scalar took
    25.6s per chain; this version, after the one-time cached forward
    pass, extracts a chain in under a millisecond -- verified to
    reproduce IDENTICAL D values against both the scalar version and
    G2's own independently-computed D_r on a sample before being
    trusted, see validate_extension())."""
    cache_key = family_name if family_name is not None else id(credit_fn)
    letters, history = _get_forward_live(credit_fn, cache_key, m, C, anchor_steps=anchor_steps)
    modulus = 3 ** m
    tr = target_r % modulus
    final_live = history[m]
    survivors = [d for d in range(C + 1) if final_live[d][tr]]
    if not survivors:
        return None, None, None
    best_d = max(survivors)
    D = C - best_d
    chain, residues = extract_one_chain_with_residues(letters, history, m, C, modulus, best_d, tr)
    return D, chain, residues


def validate_extension():
    print("=== Pre-experiment validation (house rule) ===")
    checks = [
        ("golden-per8 m=5", credit_golden_per8, 5, 2),
        ("golden-per8 m=9", credit_golden_per8, 9, 3),
        ("sqrt2-per12 m=8", credit_sqrt2_per12, 8, 4),
    ]
    all_pass = True
    for label, fn, m, expected in checks:
        D_fast = bfs_Dm_fast(fn, m, C, anchor_steps=53)
        fam_label = label.split()[0]
        D_chain, chain, res = bfs_Dm_target_chain_with_residues(
            fn, m, C, target_r=1, anchor_steps=53, family_name=fam_label)
        ok = (D_fast == expected == D_chain)
        print(f"  {label}: D_fast={D_fast} D_chain_ext={D_chain} expected={expected} "
              f"{'PASS' if ok else 'FAIL'}")
        all_pass = all_pass and ok

    print("\n=== Cross-check vs G2's own g2_anchor_sweep.csv (sample of 20 keys) ===")
    g2_csv = W6G / "g2_anchor_sweep.csv"
    sample_checked = 0
    sample_pass = 0
    if g2_csv.exists():
        with open(g2_csv, newline="") as f:
            rows = list(csv.DictReader(f))
        seen_keys = set()
        for row in rows:
            key = (row["family"], row["m"], row["effective_target_mod_3m"])
            if key in seen_keys:
                continue
            seen_keys.add(key)
            if sample_checked >= 20:
                break
            fam, m_s, tgt_s = row["family"], int(row["m"]), int(row["effective_target_mod_3m"])
            if row["D_r"] == "":
                continue
            D_expected = int(row["D_r"])
            fn = FAMILIES[fam]
            D_got, _, _ = bfs_Dm_target_chain_with_residues(
                fn, m_s, C, target_r=tgt_s, anchor_steps=53, family_name=fam)
            ok = (D_got == D_expected)
            sample_checked += 1
            sample_pass += ok
            if not ok:
                print(f"  MISMATCH: {fam} m={m_s} target={tgt_s}: "
                      f"G2 D_r={D_expected} vs this script D={D_got}")
        print(f"  {sample_pass}/{sample_checked} sampled (family,m,target) keys match G2's own D_r exactly")
        all_pass = all_pass and (sample_pass == sample_checked)
    else:
        print(f"  G2 CSV not found at {g2_csv} -- skipping cross-check (unexpected)")

    print(f"\n=== Validation: {'ALL PASS' if all_pass else 'SOME FAILED -- STOP'} ===\n")
    if not all_pass:
        raise SystemExit("Extension validation failed -- refusing to run H2.")


def ray_discrepancy_plus1(letters):
    """L(m) for the +1 ray: max_k sum_{j<=k}(2-c_j)."""
    running = 0
    best = 0
    for c in letters:
        running += (2 - c)
        best = max(best, running)
    return best


def ray_discrepancy_minus1(letters):
    """The -1 ray's own discrepancy law: max_k sum_{j<=k}(1-c_j), per
    DERIVATION_NOTES 8b (a=1 forever, cost 1/step against credit c)."""
    running = 0
    best = 0
    for c in letters:
        running += (1 - c)
        best = max(best, running)
    return best


def fit_two_ray_model(fn, m, C, target_r, anchor_steps=53, family_name=None):
    """Extract the actual optimal chain to target_r, find the descent
    to EACH ray (first touch point in the chain's own trajectory, read
    directly -- not assumed), and compute the two-ray model's
    prediction for comparison against the chain's own (already cross-
    validated) D(r,m)."""
    D_actual, chain, residues = bfs_Dm_target_chain_with_residues(
        fn, m, C, target_r, anchor_steps=anchor_steps, family_name=family_name)
    if D_actual is None:
        return None
    mod = 3 ** m
    neg1 = mod - 1
    letters = [c for (c, a) in chain]

    descent_plus1 = None
    descent_minus1 = None
    for idx, r in enumerate(residues):
        if descent_plus1 is None and r == 1 % mod:
            descent_plus1 = idx
        if descent_minus1 is None and r == neg1:
            descent_minus1 = idx
    model_candidates = []
    if descent_plus1 is not None:
        desc_cost = sum(a - 2 for (c, a) in chain[:descent_plus1]) if descent_plus1 else 0
        ray_cost = ray_discrepancy_plus1(letters[descent_plus1:])
        model_candidates.append(("+1", descent_plus1, desc_cost, ray_cost, desc_cost + ray_cost))
    if descent_minus1 is not None:
        desc_cost = sum(a - 2 for (c, a) in chain[:descent_minus1]) if descent_minus1 else 0
        ray_cost = ray_discrepancy_minus1(letters[descent_minus1:])
        model_candidates.append(("-1", descent_minus1, desc_cost, ray_cost, desc_cost + ray_cost))

    if not model_candidates:
        return {"D_actual": D_actual, "model_prediction": None, "candidates": [],
                "chain": chain, "residues": residues}

    best_candidate = min(model_candidates, key=lambda x: x[4])
    return {
        "D_actual": D_actual, "model_prediction": best_candidate[4],
        "candidates": model_candidates, "chain": chain, "residues": residues,
        "best_ray": best_candidate[0], "best_descent_len": best_candidate[1],
    }


def main():
    validate_extension()

    print("=== Extending G2 sweep: mod 27/81, m up to 10, two-ray model fit ===")
    t0 = time.time()
    m_scope = list(range(2, 11))  # extend to 10 per the order
    mod_targets = [27, 81]

    fit_rows = []
    for family_name, fn in FAMILIES.items():
        for m in m_scope:
            modulus = 3 ** m
            for mod_target in mod_targets:
                classes = [r0 for r0 in range(mod_target) if r0 % 3 != 0]
                seen_targets = set()
                for r0 in classes:
                    tr = r0 % modulus
                    if tr in seen_targets:
                        continue
                    seen_targets.add(tr)
                    fit = fit_two_ray_model(fn, m, C, tr, anchor_steps=53, family_name=family_name)
                    if fit is None:
                        fit_rows.append({
                            "family": family_name, "m": m, "mod_target": mod_target,
                            "target_r": tr, "D_actual": "", "model_prediction": "",
                            "match": "", "best_ray": "", "note": "NO_SURVIVOR",
                        })
                        continue
                    match = (fit["model_prediction"] == fit["D_actual"]) if fit["model_prediction"] is not None else None
                    fit_rows.append({
                        "family": family_name, "m": m, "mod_target": mod_target,
                        "target_r": tr, "D_actual": fit["D_actual"],
                        "model_prediction": fit["model_prediction"] if fit["model_prediction"] is not None else "",
                        "match": match if match is not None else "NO_RAY_TOUCHED",
                        "best_ray": fit.get("best_ray", ""),
                        "note": "",
                    })
            elapsed = time.time() - t0
        print(f"  {family_name}: m up to {m_scope[-1]} done, elapsed {elapsed:.1f}s")

    total_wall = time.time() - t0
    print(f"Total wall: {total_wall:.1f}s, {len(fit_rows)} (family,m,target) rows fitted")

    with open(HERE / "h2_two_ray_fit.csv", "w", newline="") as f:
        fieldnames = ["family", "m", "mod_target", "target_r", "D_actual",
                      "model_prediction", "match", "best_ray", "note"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in fit_rows:
            w.writerow(r)
    print(f"Wrote h2_two_ray_fit.csv ({len(fit_rows)} rows)")

    evaluable = [r for r in fit_rows if r["D_actual"] != "" and r["model_prediction"] != ""]
    matches = [r for r in evaluable if r["match"] is True]
    no_ray_touched = [r for r in evaluable if r["match"] == "NO_RAY_TOUCHED"]
    mismatches = [r for r in evaluable if r["match"] is False]
    n_eval = len(evaluable)
    n_match = len(matches)
    frac = n_match / n_eval if n_eval else 0.0
    print("\n=== GATE 1: two-ray model exact match rate ===")
    print(f"Evaluable keys: {n_eval}, matches: {n_match} ({frac*100:.1f}%), "
          f"no-ray-touched (model undefined): {len(no_ray_touched)}, "
          f"mismatches: {len(mismatches)}")
    gate1_hit = frac >= 0.90
    print(f"Registered prediction (>=90% match, 55%): {'HIT' if gate1_hit else 'MISS'}")

    if mismatches:
        with open(HERE / "h2_mismatches_dump.csv", "w", newline="") as f:
            fieldnames = ["family", "m", "mod_target", "target_r", "D_actual", "model_prediction", "best_ray"]
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in mismatches:
                w.writerow({k: r[k] for k in fieldnames})
        print(f"Wrote h2_mismatches_dump.csv ({len(mismatches)} rows) -- residual keys where the model misses")

    if no_ray_touched:
        with open(HERE / "h2_no_ray_touched_dump.csv", "w", newline="") as f:
            fieldnames = ["family", "m", "mod_target", "target_r", "D_actual"]
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in no_ray_touched:
                w.writerow({k: r[k] for k in fieldnames})
        print(f"Wrote h2_no_ray_touched_dump.csv ({len(no_ray_touched)} rows) -- "
              f"chains that touch NEITHER ray within the window (model undefined for these)")

    print("\n=== GATE 2: D(r = 3^m - 1) = 0 for every word (min letter >= 1) ===")
    gate2_rows = []
    for family_name, fn in FAMILIES.items():
        min_letter = min(fn(k) for k in range(200))
        for m in m_scope:
            modulus = 3 ** m
            target = modulus - 1
            D, chain, residues = bfs_Dm_target_chain_with_residues(
                fn, m, C, target, anchor_steps=53, family_name=family_name)
            gate2_rows.append({"family": family_name, "m": m, "min_letter": min_letter,
                                "target_r": target, "D": D})
            print(f"  {family_name} m={m} (min_letter={min_letter}): D(r=3^{m}-1)={D}")
    with open(HERE / "h2_gate2_pure_cheap_ray.csv", "w", newline="") as f:
        fieldnames = ["family", "m", "min_letter", "target_r", "D"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in gate2_rows:
            w.writerow(r)
    n_gate2_total = len(gate2_rows)
    n_gate2_zero = sum(1 for r in gate2_rows if r["D"] == 0)
    print(f"\n{n_gate2_zero}/{n_gate2_total} rows have D=0 exactly.")
    gate2_hit = (n_gate2_zero == n_gate2_total)
    print(f"Registered prediction (D=0 for every word with min letter>=1, 80%): "
          f"{'HIT' if gate2_hit else 'MISS'}")
    print(f"Wrote h2_gate2_pure_cheap_ray.csv ({len(gate2_rows)} rows)")


if __name__ == "__main__":
    main()
