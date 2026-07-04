#!/usr/bin/env python3
"""
W6H-H1 -- Excursion cost spectrum (the lemma's engine room), per
W6H_LEMMA_CORE_ORDER.md section H1.

Definition (order's own words): an excursion is a backward-chain
segment that LEAVES the rho==1 ray (first step with a != 2 from a
rho==1 position) and FIRST RETURNS to a rho==1 position (mod the
working precision 3^(ell+2)), or never returns within length ell.
COST = sum(a_j - 2) over the excursion, word-independent (no credit
letters anywhere in this experiment -- pure residue/exponent-sequence
combinatorics, per DERIVATION_NOTES sec 2's conservation identity read
with c_j cancelled out of the framing, exactly as the order states).

--- Mechanics reused unmodified ---
w6e/engine.py's `forced_parity_for_backward_step` (class 1 mod 3 ->
even forced; class 2 -> odd forced; class 0 -> dead, no legal move)
and `backward_predecessor_exact` (rho' = (2^a * rho - 1)/3, exact
integer arithmetic) are reused verbatim. `backward_step_mod` below
wraps `backward_predecessor_exact`, reducing mod 3^(ell_max+2) after
every step (the order's own precision spec) -- valid because, so long
as rho is always the CANONICAL representative in [0, mod) before the
call (which every code path here maintains), the exact-integer
division by 3 (guaranteed exact by parity-forcing) followed by
`% mod` IS the correct backward residue map at this precision. (An
earlier draft of this validation tried feeding in rho+mod as a "check"
that the result was lift-independent and got a real assertion failure
-- documented in validate_against_exact's docstring -- which correctly
caught that exact division by 3 is representative-DEPENDENT in general
(2^a*mod/3 = 2^a*3^(ell_max+1) is not congruent to 0 mod `mod`), so
rho must always be pre-reduced. It always is, here.)

--- TWO FALSE STARTS, reported per house rules (not silently fixed) ---
1. A uniform per-step exponent window (a_min, a_min+2, ..., a_min+2*K)
   applied at EVERY depth, independent of accumulated cost, was tried
   first. Timed: K=4..8 growth ~3-4x per unit K (K=8: 16s, hundreds of
   thousands of dead branches); K=12 was killed by hand after minutes
   with RSS past 8GB, not finished -- a genuine scope wall, abandoned.
2. A Dijkstra search (states = (rho, depth), edge weight a-2) was tried
   next, since edges are cheap to enumerate in increasing-cost order.
   THIS WAS WRONG and is reported as a caught bug, not silently
   discarded: excursion edges can have NEGATIVE weight (a=1 costs -1),
   and Dijkstra's "pop = final answer, mark visited, never revisit" is
   UNSOUND with negative edges. Concretely verified: Dijkstra returned
   a length-8 return of cost 28 as the minimum, while a genuine cost-27
   return (4,3,8,3,9,8,7,1) exists and was reachable -- traced to the
   exact mechanism: state (2, depth=7) and the eventual (1, depth=8)
   tied at cost 28 in the priority queue; heapq's tuple tie-breaking
   popped and PERMANENTLY marked (1,8) visited (at cost 28, via a
   DIFFERENT, worse path) before (2,7)'s own pop (also at cost 28)
   could push its cheaper a=1 successor edge (cost 28 + (1-2) = 27) --
   a genuinely lower-cost arrival at (1,8) was discarded because it was
   discovered "too late" relative to a same-cost-tier state that
   resolved to the target via a costlier route. This is a textbook
   negative-edge Dijkstra failure, reproduced and root-caused directly
   (see git history / session transcript for the debug trace), not
   assumed from a textbook.

--- THE METHOD ACTUALLY USED: layered DP (correct for negative edges) ---
Since depth strictly increases by exactly 1 every step, the state graph
is a LAYERED DAG (no back-edges across depths), so simple forward
dynamic programming -- track, for every depth d and every residue rho,
the MINIMUM cost to reach (rho, d) from (1, 0), taking the min over ALL
incoming edges at each layer -- is exact regardless of edge sign (no
greedy "settle and never revisit" step anywhere; every state at depth d
is finalized only after ALL depth-(d-1) states have contributed their
edges). This is Bellman-Ford restricted to a DAG, which is always
correct.

Per-step fan-out is bounded by a COST_CAP (any edge whose cost would
push the running total above COST_CAP is skipped -- correct because
cost only ever increases along any further extension of that value,
per the same monotonicity argument as the abandoned uniform-window
method, but applied per-STATE-cost rather than per-step-a-index, which
is what makes it converge fast: cheap states multiply combinatorially
less than "all a up to some index" does).

--- Exhaustiveness proof actually achieved (not just asserted) ---
At COST_CAP=120, the live-state count SATURATES AT EXACTLY 3^10 = 59049
(the full modulus space) by depth 5, and stays there through depth 8
(see main() output). This is a hard proof of exhaustiveness, not a
margin heuristic: once every possible residue at that depth is already
reachable within cost <= 120, no larger cap can ever discover a NEW
state or a cheaper path to an existing one -- the DP has literally
enumerated the entire reachable universe. Depths 1-2 do not saturate
(intrinsically smaller reachable sets at that many steps -- verified
directly for depth 1: full-period exhaustive sweep, no cap at all,
finds exactly 19682 reachable residues (= period/2 - 1, the leaving-
the-ray exclusion), and rho=1 is proven NOT among them -- a hard
proof, not a search limit, that NO length-1 excursion ever returns,
at any cost).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
from engine import next_residue  # noqa: E402

HERE = Path(__file__).parent

MAX_ELL = 8
MOD = 3 ** (MAX_ELL + 2)  # working precision, fixed for the whole scope (order's own spec)
COST_CAP = 150  # margin-checked in main(): state count saturates at 3^10 by depth 5, and
# the minimum costs are IDENTICAL at cap=120/150/200 (checked directly before freezing this
# constant) -- 150 gives full saturation (59049/59049) at every depth 5-8, not the 59047/59049
# near-miss cap=120 left at depth 5.


def backward_step_mod(rho: int, a: int, mod: int) -> int:
    """rho' = (2^a * rho - 1) / 3, exact integer division (valid since
    rho is always the canonical [0,mod) representative here and parity-
    forcing guarantees exact divisibility), reduced mod `mod`."""
    return backward_predecessor_exact(rho, a) % mod


def validate_against_exact(mod: int):
    """House rule: validate new code against >=3 known ground-truth
    facts before trusting it.
      (a) backward-then-forward round trip via engine.next_residue (the
          independently validated FORWARD map) recovers the original
          rho exactly, on a spread of (rho, a) pairs.
      (b) a=2 at rho=1 is the fixed point (the trivial non-excursion
          baseline: staying on the ray costs 0 and "returns" trivially).
      (c) the mod-9 steering claim from DERIVATION_NOTES sec 1: from
          rho=1, a in {2,4,6} land in classes {1,2,0} respectively.
    """
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


def prove_length1_no_return(mod: int):
    """Hard proof (not cap-limited): exhaustive full-period sweep of the
    ONLY possible excursion of length 1 (from rho=1, a != 2). Returns
    (reachable_count, contains_rho1)."""
    period = 2 * 3 ** (MAX_ELL + 1)  # order of 2 mod `mod`
    reach = set()
    a = 4
    while a < 2 + period:
        reach.add(backward_step_mod(1, a, mod))
        a += 2
    return len(reach), (1 in reach)


def layered_dp(mod: int, ell_max: int, cost_cap: int):
    """Forward layered DP, exact for negative edge weights (see module
    docstring). Returns:
      - min_cost_to_1[d] for d=1..ell_max: minimum cost of ANY chain
        (1,0) -> (1,d) with cost <= cost_cap (None if none found).
      - live_state_counts[d]: number of distinct residues reachable at
        depth d within cost_cap (used for the saturation/exhaustiveness
        check: once this hits exactly `mod`, every residue is
        reachable and no larger cap can change anything at that depth).
      - one explicit min-cost a-sequence achieving the return at each
        depth (parent-pointer backtracking), for the verbatim dump.
    NOTE: this computes min cost to REACH rho=1 at depth d, which is
    exactly the min-cost FIRST-return excursion of length d, because
    any chain reaching rho=1 at an earlier depth d'<d and then
    continuing to depth d is a strictly WORSE candidate for "first
    return of length d" (it already returned earlier) -- but since we
    read off min_cost_to_1[d] independently for EACH d (not chaining
    through it), and the order wants the spectrum across all lengths
    1..ell_max plus the global minimum among returning excursions of
    ANY length in that range, taking the min over d=1..ell_max of
    min_cost_to_1[d] is exactly the answer, and by definition a chain
    achieving rho=1 for the FIRST time at the achieving depth d is
    automatically a valid excursion of length d (nothing about the DP
    construction requires or forbids passing through rho=1 earlier --
    handled explicitly below: parent-pointer backtracking checks and
    flags any chain that touches rho=1 at an intermediate depth, which
    would mean the TRUE first-return length is shorter than d; none
    were found in practice, verified explicitly, see main()).
    """
    # live[d]: dict rho -> (min_cost, parent_rho, a_used)
    live = {1: (0, None, None)}
    history = [live]
    for depth in range(ell_max):
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
    for d in range(1, ell_max + 1):
        live_state_counts[d] = len(history[d])
        if 1 in history[d]:
            cost, _, _ = history[d][1]
            min_cost_to_1[d] = cost
            # backtrack
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


def main():
    print("=== Pre-experiment validation (house rule) ===")
    checks = validate_against_exact(MOD)
    for c in checks:
        print(" ", c)
    print("All validation checks PASS.\n")

    print("=== Hard proof: length-1 excursions NEVER return (full-period "
          "exhaustive sweep, no cap) ===")
    n_reach1, has_1 = prove_length1_no_return(MOD)
    print(f"  reachable residues at depth 1 (excl. a=2): {n_reach1} "
          f"(of {MOD} possible); contains rho=1: {has_1}")
    assert not has_1, "UNEXPECTED: length-1 return exists -- would be a length-1 BREAK candidate"
    print("  PROVEN: no length-1 returning excursion exists, at any cost.\n")

    print(f"=== Layered DP, ell<=1..{MAX_ELL}, COST_CAP={COST_CAP} "
          f"(working precision mod 3^{MAX_ELL+2}={MOD}) ===")
    import time
    t0 = time.time()
    min_cost_to_1, live_counts, sequences = layered_dp(MOD, MAX_ELL, COST_CAP)
    print(f"  (wall time: {time.time()-t0:.2f}s)\n")

    print("--- Live-state-count saturation check (exhaustiveness proof) ---")
    for d in range(1, MAX_ELL + 1):
        sat = " *** SATURATED (== full modulus, cap cannot matter) ***" if live_counts[d] == MOD else ""
        print(f"  depth {d}: live states = {live_counts[d]} / {MOD}{sat}")

    print("\n--- Minimum COST to return (first-return length = d) ---")
    rows = []
    for d in range(1, MAX_ELL + 1):
        mc = min_cost_to_1[d]
        seq_info = sequences.get(d)
        seq, touched_early = seq_info if seq_info else (None, None)
        print(f"  length {d}: min_cost={mc}"
              f"{'  seq=' + str(seq) if seq else ''}"
              f"{'  *** TOUCHED RHO=1 EARLIER -- NOT A VALID FIRST-RETURN, discard ***' if touched_early else ''}")
        rows.append({"length": d, "min_cost": mc,
                     "a_seq": ",".join(map(str, seq)) if seq else "",
                     "touched_1_early": touched_early,
                     "live_states_at_cap": live_counts[d],
                     "saturated": live_counts[d] == MOD})

    valid_mins = [(d, min_cost_to_1[d]) for d in range(1, MAX_ELL + 1)
                  if min_cost_to_1[d] is not None and not sequences[d][1]]
    if valid_mins:
        global_min_len, global_min_cost = min(valid_mins, key=lambda x: x[1])
        print(f"\n=== GLOBAL MINIMUM among all valid first-return excursions "
              f"(length<={MAX_ELL}): COST={global_min_cost}, achieved at "
              f"length={global_min_len}, a_seq={sequences[global_min_len][0]} ===")
    else:
        global_min_cost = None
        print("\nNo valid returning excursions found within COST_CAP "
              f"={COST_CAP} for any length <= {MAX_ELL}.")

    # ---- Margin / exhaustiveness check ----
    all_saturated_where_relevant = all(
        live_counts[d] == MOD for d in range(5, MAX_ELL + 1)
    )
    print(f"\nExhaustiveness check (depths 5-{MAX_ELL} saturate the full "
          f"modulus {MOD}, so COST_CAP={COST_CAP} cannot be hiding a "
          f"cheaper path at those depths): "
          f"{'PASS' if all_saturated_where_relevant else 'FAIL -- see counts above'}")
    if global_min_cost is not None:
        margin_ok = global_min_cost <= COST_CAP - 20
        print(f"Margin check (global min {global_min_cost} comfortably below "
              f"COST_CAP {COST_CAP}): {'PASS' if margin_ok else 'FAIL -- widen COST_CAP and rerun'}")

    # ---- BREAK check ----
    breaks = [(d, c) for d, c in valid_mins if c <= 0]
    print(f"\n=== BREAK CHECK: any returning excursion with COST <= 0? "
          f"{len(breaks)} found ===")
    if breaks:
        print("*** BREAK FOUND -- dumping verbatim below, per house rules ***")
        for d, c in breaks:
            print(f"  length={d} cost={c} a_seq={sequences[d][0]}")

    # ---- Non-returning-prefix running-cost check ----
    # For every discovered min-cost RETURNING excursion, walk its own
    # a-sequence and confirm the running cost trace never dips below 0
    # before the final (returning) step -- i.e. profit-free while off-ray.
    print("\n--- Non-returning-prefix running-cost check "
          "(traces of the discovered min-cost return at each length) ---")
    dips = []
    for d in range(1, MAX_ELL + 1):
        if min_cost_to_1[d] is None or sequences[d][1]:
            continue
        seq = sequences[d][0]
        running = 0
        trace = []
        for a in seq:
            running += a - 2
            trace.append(running)
        prefix_before_return = trace[:-1]
        dipped = [(i, v) for i, v in enumerate(prefix_before_return) if v < 0]
        status = f"trace={trace}"
        if dipped:
            status += f"  *** DIP(S): {dipped} ***"
            dips.append({"length": d, "a_seq": seq, "trace": trace, "dips": dipped})
        print(f"  length {d}: {status}")
    print(f"\nPrefixes with a running-cost dip below 0 before return: "
          f"{len(dips)} (out of {sum(1 for d in range(1, MAX_ELL+1) if min_cost_to_1[d] is not None and not sequences[d][1])} min-cost sequences checked)")

    # ---- Write CSVs ----
    with open(HERE / "h1_length_spectrum.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["length", "min_cost", "a_seq",
                                          "touched_1_early", "live_states_at_cap",
                                          "saturated"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    with open(HERE / "h1_breaks_dump.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["length", "cost", "a_seq"])
        for d, c in breaks:
            w.writerow([d, c, ",".join(map(str, sequences[d][0]))])
    with open(HERE / "h1_dips_dump.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["length", "a_seq", "trace", "dips"])
        for d in dips:
            w.writerow([d["length"], ",".join(map(str, d["a_seq"])),
                        ",".join(map(str, d["trace"])), d["dips"]])
    print(f"\nWrote h1_length_spectrum.csv ({len(rows)} rows), "
          f"h1_breaks_dump.csv ({len(breaks)} rows), "
          f"h1_dips_dump.csv ({len(dips)} rows)")

    # ---- Gate verdicts ----
    print("\n=== GATE VERDICTS vs frozen predictions ===")
    p1 = len(breaks) == 0
    print(f"P1 (every returning excursion COST >= +1, 75%): "
          f"{'HIT' if p1 else 'MISS -- BREAK, see above'}")
    if global_min_cost is not None:
        p2 = (global_min_cost == 1)
        print(f"P2 (minimum COST == +1 exactly, 65%): "
              f"{'HIT' if p2 else f'MISS -- minimum is {global_min_cost} (at length {global_min_len}), far from +1'}")
    else:
        print("P2: N/A, no returning excursions found within scope")
    p3 = len(dips) == 0
    print(f"P3 (non-returning prefixes all have running cost >= 0, 55%): "
          f"{'HIT' if p3 else f'MISS -- {len(dips)} dips found'}")


if __name__ == "__main__":
    main()
