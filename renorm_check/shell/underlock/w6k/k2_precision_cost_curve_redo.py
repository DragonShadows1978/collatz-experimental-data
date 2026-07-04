#!/usr/bin/env python3
"""
W6K-K2 -- Return-precision cost curve redo (replaces W6J-J2, whose
curve [1,10,2,5,5,16,7,19,19,27] was REJECTED in SYNTHESIS as
logically impossible: nested return precisions require min_cost(t)
nondecreasing in t, and J2's own curve violated this twice), per
W6K_CONVENTION_PINNING_ORDER.md section K2.

THE NESTING ARGUMENT (why min_cost(t) MUST be nondecreasing, restated
precisely): "returns at precision t+1" means rho == 1 (mod 3^(t+1)).
Since 3^t | 3^(t+1), rho==1 (mod 3^(t+1)) ALWAYS implies rho==1
(mod 3^t) -- the set of (t+1)-returning residues is a SUBSET of the
set of t-returning residues (mod 3^(t+1) partitions each residue
class mod 3^t into 3 finer sub-classes; "==1 mod 3^(t+1)" picks out
exactly one of the three sub-classes of "==1 mod 3^t"). Minimizing
cost over a subset of chains can never give a SMALLER minimum than
minimizing over the superset that contains it. Hence
min_cost(t) <= min_cost(t+1) for all t -- REQUIRED, not a conjecture.

--- THE BUG IN J2, root-caused (not merely reported) ---
J2 ran ONE INDEPENDENT layered DP per t, entirely AT modulus 3^t,
reducing every intermediate residue mod 3^t at every step (per its own
"never mix precisions mid-recursion" lesson from an EARLIER false
start). This is subtly wrong in a DIFFERENT way than that earlier false
start: reducing intermediate residues to the SAME modulus as the
target does not just coarsen the TARGET condition, it also coarsens
the STATE SPACE the DP explores at every intermediate step -- two
exact residues that coincide mod 3^t but differ at higher precision
get MERGED into one DP state, and the `backward_predecessor_exact`
division-by-3 (which is representative-dependent, per w6e/engine.py's
own docstring) then commits to whichever specific predecessor integer
happens to be live in that merged bucket, silently discarding the
other. Concretely verified (see ledger W6K-K2): running EXACT
(unreduced) backward-recursion once, at a single fixed HIGH modulus
3^MAX_T (MAX_T=10 here, at or above every t tested), and reading off
min-cost-to-target as the min cost among ALL live high-precision
residues rho with `rho % 3^t == 1` (an entire equivalence CLASS, not
a single merged point) reproduces H1's own t=10 answer (cost 27,
sequence (4,3,8,3,9,8,7,1)) exactly, AND gives a curve that is
nondecreasing in t by construction (formally: since every state alive
at depth d in the mod-3^t readout is literally the mod-3^t projection
of a state alive at the SAME depth d in the single high-precision DP,
and rho%3^(t+1)==1 implies rho%3^t==1 for every one of those states,
the t-readout's candidate set at every depth is a SUPERSET of the
(t+1)-readout's candidate set at that same depth -- the nesting
property is now a structural fact about the shared computation, not
an emergent empirical accident).

--- THE FIX: single high-precision DP, per-t READOUT not per-t DP ---
Run h1/j2's own layered DP ONCE, at modulus 3^MAX_T throughout (never
reduced further mid-recursion -- avoiding BOTH false starts: the
original superset-precision draft's mistake was REPLAYING a chosen
a-sequence's OWN intermediate values across moduli after the fact;
this fix never reduces at all until the final per-t READOUT, which
only ever inspects live states, never feeds a reduced value back into
`backward_predecessor_exact`). For each t=1..MAX_T, the min-cost-to-
precision-t is the min over ALL depths d<=MAX_LEN of (min cost among
states live at depth d with rho % 3^t == 1).

Cross-checks before trusting the curve (house rule):
  1. t=MAX_T readout must exactly reproduce H1's own published answer
     (cost 27, length 8, sequence (4,3,8,3,9,8,7,1)) -- STOP if not.
  2. NESTING ASSERTION (the order's own explicit requirement): the
     resulting curve must be nondecreasing in t -- asserted, not
     merely reported; if it fires, the bug is NOT "expected" and must
     be found before any curve is trusted.
"""
from __future__ import annotations

import csv
import sys
import time
import resource
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "w6e"))
from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
from engine import next_residue  # noqa: E402

MAX_LEN = 10
MAX_T = 10
COST_CAP = 150
HIGH_MOD = 3 ** MAX_T  # single fixed working precision throughout, at/above every t tested


def rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


def backward_step_mod(rho: int, a: int, mod: int) -> int:
    return backward_predecessor_exact(rho, a) % mod


def validate_against_exact(mod: int):
    """Same house-rule validation as h1/j2 (roundtrip via the
    independently-validated forward map, fixed point, mod-9 steering),
    run once at HIGH_MOD before trusting the shared DP."""
    checks = []
    samples = [(1, 2), (1, 4), (1, 6), (1, 8), (2, 1), (2, 3), (4, 2), (5, 1),
               (7, 2), (8, 1), (44287 % mod, 6)]
    for rho, a in samples:
        pred = backward_step_mod(rho, a, mod)
        fwd = next_residue(pred, a, mod)
        ok = fwd == rho % mod
        checks.append(("roundtrip_via_next_residue", rho, a, pred, fwd, ok))
        assert ok, f"ROUNDTRIP FAIL rho={rho} a={a}: pred={pred} fwd_back={fwd}"
    fp = backward_step_mod(1, 2, mod)
    checks.append(("fixed_point", 1, 2, 1, fp, fp == 1))
    assert fp == 1, f"a=2 from rho=1 must be the fixed point, got {fp}"
    classes = [backward_step_mod(1, a, mod) % 3 for a in (2, 4, 6)]
    checks.append(("mod9_steering", classes, [1, 2, 0], classes == [1, 2, 0]))
    assert classes == [1, 2, 0], f"mod-9 steering claim failed: got {classes}"
    return checks


def shared_layered_dp(mod: int, max_len: int, cost_cap: int):
    """h1/j2's layered_dp mechanics, run ONCE at a single high modulus
    for the WHOLE curve (the fix: no per-t re-derivation)."""
    live = {1: (0, None, None)}
    history = [live]
    for depth in range(max_len):
        new_live = {}
        is_first = (depth == 0)
        for rho, (cost, _, _) in live.items():
            parity = forced_parity_for_backward_step(rho)
            if parity is None:
                continue
            a_min = 2 if parity == 0 else 1
            i = 0
            while True:
                a = a_min + 2 * i
                step_cost = a - 2
                newcost = cost + step_cost
                if newcost > cost_cap:
                    break
                i += 1
                if is_first and a == 2:
                    continue
                rho2 = backward_step_mod(rho, a, mod)
                if rho2 not in new_live or newcost < new_live[rho2][0]:
                    new_live[rho2] = (newcost, rho, a)
        live = new_live
        history.append(live)
    return history


def per_t_readout(history, t: int, max_len: int):
    """Min cost to reach the residue CLASS {rho : rho % 3^t == 1}, at
    each depth d, from the SHARED high-precision history -- this is
    the fix's core operation (a readout over live high-precision
    states, never a separate low-precision DP)."""
    modt = 3 ** t
    min_cost_by_depth = {}
    example_by_depth = {}
    for d in range(1, max_len + 1):
        cands = [(cost, rho) for rho, (cost, _, _) in history[d].items() if rho % modt == 1]
        if not cands:
            min_cost_by_depth[d] = None
            continue
        cost, rho = min(cands)
        min_cost_by_depth[d] = cost
        seq = []
        node = rho
        depth = d
        touched_early = False
        while depth > 0:
            c, parent, a = history[depth][node]
            seq.append(a)
            node = parent
            depth -= 1
            if depth > 0 and node % modt == 1:
                touched_early = True
        seq.reverse()
        example_by_depth[d] = (tuple(seq), touched_early)
    return min_cost_by_depth, example_by_depth


def main():
    print(f"=== Shared high-precision DP: mod=3^{MAX_T}={HIGH_MOD}, "
          f"max_len={MAX_LEN}, COST_CAP={COST_CAP} ===")
    print("Pre-run validation (house rule):")
    checks = validate_against_exact(HIGH_MOD)
    for c in checks:
        print(" ", c)
    print("All validation checks PASS.\n")

    t0 = time.time()
    history = shared_layered_dp(HIGH_MOD, MAX_LEN, COST_CAP)
    dt = time.time() - t0
    print(f"Shared DP wall time: {dt:.2f}s, peak RSS: {rss_gb():.3f} GB")
    if rss_gb() > 8:
        print("*** RSS EXCEEDED 8GB -- HONEST WALL, KILLING PER HOUSE RULES ***")
        raise SystemExit(137)

    print("\n--- Live-state-count per depth (saturation context, vs full HIGH_MOD) ---")
    for d in range(1, MAX_LEN + 1):
        print(f"  depth {d}: live states = {len(history[d])} / {HIGH_MOD}")

    print(f"\n--- Cross-check 1: t={MAX_T} readout must reproduce H1's own "
          f"length-8 answer (cost 27, seq (4,3,8,3,9,8,7,1)) exactly ---")
    min_cost_maxT, example_maxT = per_t_readout(history, MAX_T, MAX_LEN)
    len8_cost = min_cost_maxT.get(8)
    len8_seq = example_maxT.get(8, (None, None))[0]
    h1_match = (len8_cost == 27) and (len8_seq == (4, 3, 8, 3, 9, 8, 7, 1))
    print(f"  t={MAX_T}, length=8: cost={len8_cost} seq={len8_seq} "
          f"{'PASS -- EXACT MATCH to H1' if h1_match else 'FAIL -- MISMATCH, investigate'}")
    if not h1_match:
        raise SystemExit("STOP: t=MAX_T cross-check against H1's own published answer "
                          "FAILED -- refusing to trust the rest of the curve.")

    print("\n--- The (t, min_cost, argmin length, argmin shape) table, GLOBAL MIN over "
          "all depths 1..MAX_LEN, per t ---")
    out_rows = []
    curve = []
    for t in range(1, MAX_T + 1):
        min_cost_by_depth, example_by_depth = per_t_readout(history, t, MAX_LEN)
        valid = [(d, c) for d, c in min_cost_by_depth.items() if c is not None]
        if valid:
            best_len, best_cost = min(valid, key=lambda x: x[1])
            best_seq, best_touched = example_by_depth[best_len]
        else:
            best_len, best_cost, best_seq, best_touched = None, None, None, None
        print(f"  t={t:>2} (mod 3^{t}): global_min_cost={best_cost} "
              f"achieved_at_length={best_len} a_seq={best_seq} "
              f"touched_target_early={best_touched}")
        out_rows.append({
            "t": t, "min_cost": best_cost, "argmin_length": best_len,
            "argmin_a_seq": ",".join(map(str, best_seq)) if best_seq else "",
            "touched_target_early": best_touched,
        })
        curve.append((t, best_cost))

    out_csv = HERE / "k2_precision_cost_curve.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["t", "min_cost", "argmin_length",
                                          "argmin_a_seq", "touched_target_early"])
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print(f"\nWrote {out_csv.name} ({len(out_rows)} rows)")

    print(f"\nCurve (t, min_cost): {curve}")

    print("\n=== NESTING ASSERTION (REQUIRED, not a frozen-% prediction) ===")
    violations = [(curve[i], curve[i + 1]) for i in range(len(curve) - 1)
                  if curve[i][1] is not None and curve[i + 1][1] is not None
                  and curve[i][1] > curve[i + 1][1]]
    if violations:
        print(f"*** ASSERTION WOULD FIRE: {len(violations)} non-monotone step(s): "
              f"{violations} ***")
        raise AssertionError(
            f"min_cost(t) is NOT nondecreasing -- violations: {violations}. "
            f"Per the order: this means a NEW bug exists in the shared-DP fix "
            f"itself (the nesting argument is a structural guarantee of this "
            f"construction, not empirical), and must be found before reporting "
            f"any curve."
        )
    print("PASS -- min_cost(t) is nondecreasing in t across all 10 points, "
          "exactly as the nesting argument requires by construction.")

    print("\n=== GATE VERDICTS vs frozen predictions ===")
    print("(a) corrected curve is nondecreasing -- REQUIRED (assertion): HIT "
          "(assertion did not fire, see above)")

    t1_cost = curve[0][1]
    b_hit = (t1_cost == 1)
    print(f"(b) min_cost at t=1 is exactly +1 (80%): global min at t=1 is {t1_cost} -- "
          f"{'HIT' if b_hit else 'MISS'}")

    print(f"\n(c) curve's big jumps align with t crossing excursion-length thresholds "
          f"(55%): examining per-t argmin lengths for jump correlation --")
    diffs = [curve[i + 1][1] - curve[i][1] for i in range(len(curve) - 1)]
    argmin_lens = [r["argmin_length"] for r in out_rows]
    print(f"    first differences (jump sizes): {diffs}")
    print(f"    argmin lengths per t:           {argmin_lens}")
    big_jump_idx = [i for i, d in enumerate(diffs) if d is not None and d >= 3]
    print(f"    'big jumps' (diff>=3) occur between t={[curve[i][0] for i in big_jump_idx]} "
          f"-> t={[curve[i+1][0] for i in big_jump_idx]}")
    len_changes_at_jumps = []
    for i in big_jump_idx:
        len_before, len_after = argmin_lens[i], argmin_lens[i + 1]
        len_changes_at_jumps.append((curve[i][0], len_before, len_after, len_before != len_after))
    print(f"    argmin-length change at each big jump (t, len_before, len_after, changed?): "
          f"{len_changes_at_jumps}")
    c_hit = len(big_jump_idx) > 0 and all(x[3] for x in len_changes_at_jumps)
    print(f"    verdict: {'HIT' if c_hit else 'MISS'} -- "
          f"{'every big jump coincides with an argmin-length change' if c_hit else 'not all big jumps coincide with an argmin-length change (or no big jumps at all)'}")


if __name__ == "__main__":
    main()
