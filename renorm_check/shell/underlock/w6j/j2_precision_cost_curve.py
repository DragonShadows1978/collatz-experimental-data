#!/usr/bin/env python3
"""
W6J-J2 -- Return-precision cost curve (the lemma's quantitative core),
per W6J_INTERIOR_BOUNDARY_ORDER.md section J2.

Extends W6H-H1's layered DP (w6h/h1_excursion_spectrum.py): H1 fixed
the working precision at mod=3^(ell_max+2)=3^10 for ALL excursion
lengths ell=1..8 and defined "return" as reaching rho==1 in THAT fixed
modulus. J2 asks a genuinely different question: for each precision t
SEPARATELY (t=1..10), define "return" as rho == 1 (mod 3^t) -- i.e.
the excursion only needs to match the target on the LOW t trits, not
the full high-precision residue -- and find min cost over returning
excursions of length <= 10 at that precision. This is the "curve that
interpolates between F2's +1 (low effective precision) and H1's 27
(high)" the order describes: low t is a much WEAKER return condition
(matches 1/3^t of all residues, roughly), so the search space per
depth is effectively restricted to residues satisfying rho==1 mod 3^t,
which is a much bigger reachable set than the single point rho==1 at
full precision -- cheaper returns should exist.

--- FALSE START, reported per house rules (not silently fixed) ---
A first draft tried to run ONE layered DP at a single "superset"
working precision (3^12, above the largest t=10 tested) and read off
all 10 precisions' answers by reducing residues mod 3^t at each depth,
reasoning that mod 3^t is a well-defined function of mod 3^12 (3^t |
3^12) so this would be a strict superset computation. **This is WRONG
and was caught by this script's OWN cross-check against h1's published
answer before being trusted (t=10, length=8 gave cost 38, not h1's own
27 -- a hard mismatch, investigated rather than shrugged off).**
Root cause, confirmed by direct hand-trace: `backward_predecessor_exact`
computes rho' = (2^a * rho - 1)/3 as EXACT integer division on
whatever literal integer is passed in. Two different lifts of the SAME
residue CLASS mod 3^10 (e.g. 32269 vs 504661, both == 32269 mod 3^10)
are NOT interchangeable inputs: replaying h1's own ground-truth
a-sequence (4,3,8,3,9,8,7,1) at mod 3^12 diverges from its mod-3^10
trace starting at step 5 (17684 vs 37367, no longer congruent even mod
3^10) -- continuing the backward recursion at a finer modulus changes
which of the 3 predecessors mod-3 the exact division selects, and that
choice does not commute with later reduction to a coarser modulus. This
is exactly the representative-dependence issue w6e/engine.py's own
module docstring for h1 warns about ("rho must always be pre-reduced");
it was previously worked around by NEVER changing the working modulus
mid-computation. The superset-precision draft violates that invariant.
Confirmed as a genuine mechanism (not a typo) via `backward_predecessor_
exact`'s own assertion: replaying the DP's chosen a=9 edge at step 4
from the mod-3^10-reduced value 32269 raises "not divisible by 3" --
the mod-3^12 canonical representative 504661 IS divisible by 3 at that
same a, but its OWN mod-3^10 reduction is not a valid input for the
same step. The two precisions are simply not interchangeable
mid-recursion.

--- THE METHOD ACTUALLY USED: separate DP per precision t (per the
order's own wording, "for each precision t = 1..10 separately") ---
Run h1's layered DP unchanged, ONCE per t, entirely AT modulus 3^t
throughout (never mixing precisions mid-chain) -- exactly h1's own
mechanics, just parameterized by t instead of hardcoded to 3^(ell_max+2).
This is mechanically IDENTICAL to h1_excursion_spectrum.layered_dp
(same forced_parity_for_backward_step/backward_predecessor_exact calls,
same DAG/negative-edge argument for correctness), reused verbatim
except the working modulus is `3**t` for whichever t is being computed,
not a single fixed value. t=10 is then a LITERAL rerun of h1's own
computation (not merely "should agree") -- the strongest possible
cross-check, done below before trusting t=1..9.
"""
from __future__ import annotations

import csv
import sys
import time
import resource
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
from engine import next_residue  # noqa: E402

HERE = Path(__file__).parent

MAX_LEN = 10          # per the order: excursions of length <= 10
MAX_T = 10             # precisions t = 1..10
COST_CAP = 150  # same cap h1 used at ell_max=8; re-checked for saturation/margin below at length 10


def rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


def backward_step_mod(rho: int, a: int, mod: int) -> int:
    return backward_predecessor_exact(rho, a) % mod


def validate_against_exact(mod: int):
    """Same validation as h1 (house rule): confirm the mechanics hold
    AT THIS PARTICULAR modulus before trusting a DP run there (each
    call site below passes its own t's modulus 3^t -- validated fresh
    per modulus, not assumed to carry over, since the false start above
    is a direct demonstration that different moduli are NOT
    interchangeable for this exact-arithmetic machinery)."""
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


def layered_dp(mod: int, max_len: int, cost_cap: int):
    """h1's layered_dp, REUSED VERBATIM (identical body to
    w6h/h1_excursion_spectrum.layered_dp) -- forward DP over depth,
    exact for negative edges since the graph is a depth-layered DAG,
    working ENTIRELY at the single modulus `mod` passed in (never
    mixed with any other precision mid-recursion, per the false-start
    lesson above). Returns min_cost_to_1[d], live_state_counts[d],
    and one explicit min-cost a-sequence per depth (parent-pointer
    backtracking), exactly h1's own return shape."""
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

    min_cost_to_1 = {}
    live_state_counts = {}
    sequences = {}
    for d in range(1, max_len + 1):
        live_state_counts[d] = len(history[d])
        if 1 in history[d]:
            cost, _, _ = history[d][1]
            min_cost_to_1[d] = cost
            seq = []
            node = 1
            depth = d
            touched_1_early = False
            while depth > 0:
                c, parent, a = history[depth][node]
                seq.append(a)
                node = parent
                depth -= 1
                if depth > 0 and node == 1:
                    touched_1_early = True
            seq.reverse()
            sequences[d] = (tuple(seq), touched_1_early)
        else:
            min_cost_to_1[d] = None
    return min_cost_to_1, live_state_counts, sequences


def run_all_precisions(ts: list[int], max_len: int, cost_cap: int):
    """Run layered_dp ONCE PER t, entirely at modulus 3^t (the method
    actually used, per the order's own "for each precision t separately"
    wording and the false-start lesson above). Returns the same-shaped
    per-t dicts the (superseded) multi-t draft aimed for, but each
    computed by a genuinely independent, self-consistent DP run."""
    min_cost_by_t_len = {}
    live_counts_by_t = {}
    sequences_by_t = {}
    for t in ts:
        mod = 3 ** t
        validate_against_exact(mod)
        min_cost_to_1, live_counts, sequences = layered_dp(mod, max_len, cost_cap)
        min_cost_by_t_len[t] = min_cost_to_1
        live_counts_by_t[t] = live_counts
        sequences_by_t[t] = sequences
    return min_cost_by_t_len, live_counts_by_t, sequences_by_t


def main():
    print(f"=== Layered DP, length<=1..{MAX_LEN}, precisions t=1..{MAX_T}, "
          f"COST_CAP={COST_CAP}, ONE INDEPENDENT DP RUN PER t (mod 3^t each) ===")
    t0 = time.time()
    ts = list(range(1, MAX_T + 1))
    min_cost_by_t_len, live_counts_by_t, example_seqs = run_all_precisions(ts, MAX_LEN, COST_CAP)
    dt = time.time() - t0
    print(f"  (wall time: {dt:.2f}s, peak RSS: {rss_gb():.3f} GB)\n")
    if rss_gb() > 8:
        print("*** RSS EXCEEDED 8GB -- HONEST WALL, KILLING PER HOUSE RULES ***")
        raise SystemExit(137)

    print("--- Live-state-count saturation check per t (each vs its own full modulus 3^t) ---")
    for t in ts:
        mod_t = 3 ** t
        print(f"  t={t} (mod 3^{t}={mod_t}):")
        for d in range(1, MAX_LEN + 1):
            cnt = live_counts_by_t[t][d]
            sat = " *** SATURATED ***" if cnt == mod_t else ""
            print(f"    depth {d}: live states = {cnt} / {mod_t}{sat}")

    print("\n--- Cross-check: t=10 must reproduce h1's own length-8 answer (cost 27) exactly ---")
    h1_csv = HERE.parent / "w6h" / "h1_length_spectrum.csv"
    cross_check_ok = None
    if h1_csv.exists():
        with open(h1_csv, newline="") as f:
            h1_rows = {int(r["length"]): r for r in csv.DictReader(f)}
        h1_len8 = h1_rows.get(8)
        this_t10_len8 = min_cost_by_t_len[10].get(8)
        if h1_len8 is not None and h1_len8["min_cost"] not in ("", None):
            h1_val = int(h1_len8["min_cost"])
            cross_check_ok = (this_t10_len8 == h1_val)
            print(f"  h1 length=8 min_cost={h1_val}; this script's t=10,length=8 min_cost={this_t10_len8} "
                  f"{'PASS -- MATCHES' if cross_check_ok else 'FAIL -- MISMATCH, investigate before trusting curve'}")
        else:
            print("  h1 length=8 row missing/empty -- cannot cross-check")
    else:
        print(f"  h1_length_spectrum.csv not found at {h1_csv} -- cannot cross-check")
    if cross_check_ok is False:
        raise SystemExit("STOP: t=10 cross-check against h1's own published answer FAILED -- "
                          "engine/precision-matching bug, refusing to trust the rest of the curve.")

    print("\n--- The (t, min_cost, argmin length, argmin shape) table ---")
    out_rows = []
    for t in ts:
        # global min over all lengths 1..MAX_LEN for this t (excluding any
        # chain flagged as touching the target earlier -- same "valid
        # first return" discipline as h1)
        valid = [(d, min_cost_by_t_len[t][d]) for d in range(1, MAX_LEN + 1)
                 if min_cost_by_t_len[t][d] is not None
                 and not example_seqs[t].get(d, (None, False))[1]]
        if valid:
            best_len, best_cost = min(valid, key=lambda x: x[1])
            best_seq = example_seqs[t][best_len][0]
        else:
            best_len, best_cost, best_seq = None, None, None
        print(f"  t={t:>2} (mod 3^{t}): global_min_cost={best_cost} "
              f"achieved_at_length={best_len} a_seq={best_seq}")
        out_rows.append({
            "t": t, "min_cost": best_cost, "argmin_length": best_len,
            "argmin_a_seq": ",".join(map(str, best_seq)) if best_seq else "",
        })

    out_csv = HERE / "j2_precision_cost_curve.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["t", "min_cost", "argmin_length", "argmin_a_seq"])
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print(f"\nWrote {out_csv.name} ({len(out_rows)} rows)")

    # full per-(t,length) table too, for completeness/audit
    full_csv = HERE / "j2_precision_length_full.csv"
    with open(full_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "length", "min_cost", "a_seq", "touched_early"])
        for t in ts:
            for d in range(1, MAX_LEN + 1):
                mc = min_cost_by_t_len[t][d]
                seq_info = example_seqs[t].get(d)
                seq, touched = seq_info if seq_info else (None, None)
                w.writerow([t, d, mc, ",".join(map(str, seq)) if seq else "", touched])
    print(f"Wrote {full_csv.name} (full (t,length) grid, {MAX_T * MAX_LEN} rows)")

    # ---- Gate verdicts ----
    print("\n=== GATE VERDICTS vs frozen predictions ===")
    curve = [(r["t"], r["min_cost"]) for r in out_rows if r["min_cost"] is not None]
    print(f"Curve (t, min_cost): {curve}")

    # (a) min_cost nondecreasing in t
    nondecreasing = all(curve[i][1] <= curve[i + 1][1] for i in range(len(curve) - 1))
    print(f"\n(a) min_cost is nondecreasing in t (85%): {'HIT' if nondecreasing else 'MISS'}")
    if not nondecreasing:
        violations = [(curve[i], curve[i + 1]) for i in range(len(curve) - 1) if curve[i][1] > curve[i + 1][1]]
        print(f"    Violations (verbatim): {violations}")

    # (b) min_cost at t=1 is exactly +1
    t1_cost = min_cost_by_t_len[1]
    t1_valid = [(d, t1_cost[d]) for d in range(1, MAX_LEN + 1)
                if t1_cost[d] is not None and not example_seqs[1].get(d, (None, False))[1]]
    if t1_valid:
        t1_best_len, t1_best_cost = min(t1_valid, key=lambda x: x[1])
        b_hit = (t1_best_cost == 1)
        print(f"\n(b) min_cost at t=1 is exactly +1 (70%): global min at t=1 is {t1_best_cost} "
              f"(length {t1_best_len}) -- {'HIT' if b_hit else 'MISS'}")
    else:
        print("\n(b) min_cost at t=1: NO valid returning excursion found within scope -- N/A")

    # (c) curve is convex-ish/superlinear in t
    diffs = [curve[i + 1][1] - curve[i][1] for i in range(len(curve) - 1)]
    print(f"\n(c) curve convex-ish/superlinear in t (55%): first differences = {diffs}")
    convexish = all(diffs[i] <= diffs[i + 1] for i in range(len(diffs) - 1))
    print(f"    Nondecreasing first-differences (discrete convexity): "
          f"{'HIT' if convexish else 'MISS'}")


if __name__ == "__main__":
    main()
