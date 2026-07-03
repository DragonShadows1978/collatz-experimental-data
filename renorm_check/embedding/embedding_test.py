"""
Step 3: test the corridor-embedding ("renormalization") conjecture.

For each small-side (C, m) pair with a persisted live-set (from
small_side_sweep.py), test whether candidate maps phi: live(C,m) ->
(C+22, m+53) land inside live(C+22, m+53), using the backward-reachability
oracle (oracle.py) as the big-side membership tester.

Candidates tested, in the order specified by the mission:
  (a) identity-shift: phi(d, r) = (d, r), where r (an integer < 3^m) is
      reinterpreted as an element of Z/3^(m+53)Z (well-defined since
      3^m < 3^(m+53)). Deficit d is UNCHANGED (natural since [0,C] is a
      sub-range of [0,C+22]).
  (a') identity-shift with deficit offset: phi(d, r) = (d + 22, r), for
       comparison, since "shifted by +53 precision levels" in the mission
       description could plausibly pair with a deficit shift too. Both
       variants of (a) are reported.
  (b) multiplication map: phi(d, r) = (d, r * 3^53 mod 3^(m+53)).
  (b') multiplication map with deficit offset: phi(d, r) = (d + 22,
       r * 3^53 mod 3^(m+53)).
  (c) phase-shift / Sturmian-heartbeat-aligned map: phi(d, r) = (d, r')
      where r' is obtained by applying 53 forward automaton steps to r
      as if continuing the SAME corridor C (not C+22) -- i.e. testing
      whether "one more heartbeat forward, re-embedded" lands correctly.
      This uses the forward transition rule directly (deterministic once
      an exponent-choice policy is fixed; we test the a=c_k policy, which
      keeps the deficit exactly fixed throughout).

For each candidate and each tested (C,m) pair, we report:
  - exact containment: counts of matched / failed / inconclusive (oracle
    capped) among all elements of live(C,m).
  - surjectivity: NOT directly testable (would require enumerating
    live(C+22,m+53), which is exactly what's infeasible) -- reported as
    "not testable" rather than guessed.
  - the raw per-state results, so the JSON is self-auditing.

HONESTY NOTE: because oracle queries can be inconclusive (compute-capped),
the "verdict" logic distinguishes:
  - CONFIRMED CONTAINMENT: live=True for all tested elements, 0 failures,
    0 inconclusive.
  - CONFIRMED FAILURE (dead): live=False for a nontrivial fraction, with
    the fraction reported exactly.
  - INCONCLUSIVE: enough oracle calls hit the cap that we cannot honestly
    render a verdict either way; reported with the exact inconclusive
    fraction, never silently folded into "partial" or "exact".
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from automaton import M_edge, run_heartbeat, credit_sequence, allowed_exponents, next_residue
from oracle import query_membership

OUT_DIR = Path(__file__).parent
LIVE_SETS_DIR = OUT_DIR / "small_side_live_sets"
RESULTS_PATH = OUT_DIR / "embedding_test_results.json"

HEARTBEAT = 53
CORRIDOR_SHIFT = 22

# Testing EVERY element of a live set against the big-side oracle is not
# feasible when live sets have hundreds of thousands of elements (each
# oracle query costs up to the call cap). We test up to
# MAX_ELEMENTS_PER_PAIR elements per (C,m,candidate) triple, chosen
# deterministically (sorted, evenly spaced) so results are reproducible,
# and report the exact sample size used alongside results -- this is a
# SAMPLE of the containment test, not exhaustive, and is labeled as such
# throughout the JSON output.
#
# NOTE ON BUDGET TUNING: an initial run with MAX_ELEMENTS_PER_PAIR=40 and
# ORACLE_CALL_CAP=800_000 was interrupted after ~2 pairs (C=1, m=1 and
# m=4) took ~100s combined and showed the oracle's inconclusive rate
# climbing sharply with m even at fixed C=1 (2/24 decided at m=4, vs 3/4
# decided at m=1) -- consistent with the tractability finding in
# oracle.py's docstring. Continuing at that budget would not have
# finished the C=2..5 pairs (wider corridors, more oracle load) in
# reasonable time. Budgets below were reduced accordingly: this trades
# per-pair sample depth for broader C coverage, which is more informative
# for testing whether the conjecture holds ACROSS corridor widths.
MAX_ELEMENTS_PER_PAIR = 15
ORACLE_CALL_CAP = 150_000
PAIR_TIME_BUDGET_SEC = 90  # wall-clock budget per (C,m) pair across all candidates combined


def load_small_side_live_set(C, m):
    fname = LIVE_SETS_DIR / f"C{C}_m{m}.npz"
    if not fname.exists():
        return None
    data = np.load(fname)
    live = {}
    for key in data.files:
        d = int(key[1:])
        live[d] = data[key]
    return live


def enumerate_sample(live_by_d, max_elements):
    """Deterministic evenly-spaced sample of (d, r) pairs from a live set."""
    all_states = []
    for d in sorted(live_by_d.keys()):
        for r in live_by_d[d]:
            all_states.append((d, int(r)))
    all_states.sort()
    n = len(all_states)
    if n <= max_elements:
        return all_states, n, False  # not actually sampled -- full set
    idx = np.linspace(0, n - 1, max_elements, dtype=int)
    sample = [all_states[i] for i in idx]
    return sample, n, True


def candidate_a(d, r, C, m, C2, m2, shift_deficit=False):
    """Identity on residue value, reinterpreted at higher modulus."""
    d2 = d + CORRIDOR_SHIFT if shift_deficit else d
    return d2, r  # r < 3^m < 3^m2, well-defined as element of Z/3^m2 Z


def candidate_b(d, r, C, m, C2, m2, shift_deficit=False):
    """Multiplication by 3^53 mod 3^(m+53)."""
    d2 = d + CORRIDOR_SHIFT if shift_deficit else d
    modulus2 = 3 ** m2
    factor = pow(3, HEARTBEAT, modulus2)
    r2 = (r * factor) % modulus2
    return d2, r2


def candidate_c_forward53(d, r, C, m, C2, m2, exponent_policy="a_eq_ck"):
    """
    Phase-shift: apply 53 forward automaton steps to (d, r) WITHIN the
    small corridor C's transition rule (same C, since we're asking "what
    does one more heartbeat do to this state"), using a FIXED exponent
    policy a = c_k at every step (the raw automaton branches over all
    allowed a's, which is not a function, so we must fix a policy to get
    a well-defined map). With a=c_k, the deficit recurrence
    d' = d + c_k - a = d is invariant, so the deficit stays fixed at d
    throughout, and only the residue evolves. The resulting (d, r_final)
    is then embedded into (C2, m2) via the identity-shift residue
    embedding (candidate a's core idea), since r_final < 3^m < 3^m2.
    """
    seq = credit_sequence(HEARTBEAT)
    modulus_small = 3 ** m
    dd, rr = d, r
    for k in range(HEARTBEAT):
        c_k = seq[k]
        a = c_k
        lo = max(1, dd + c_k - C)
        hi = dd + c_k
        if not (lo <= a <= hi):
            return None  # policy invalid at this state -- can't apply uniformly
        dd = dd + c_k - a  # = dd since a=c_k
        rr = next_residue(rr, a, modulus_small)
    return dd, rr


CANDIDATES = {
    "a_identity_no_dshift": lambda d, r, C, m, C2, m2: candidate_a(d, r, C, m, C2, m2, shift_deficit=False),
    "a_identity_dshift22": lambda d, r, C, m, C2, m2: candidate_a(d, r, C, m, C2, m2, shift_deficit=True),
    "b_mult3pow53_no_dshift": lambda d, r, C, m, C2, m2: candidate_b(d, r, C, m, C2, m2, shift_deficit=False),
    "b_mult3pow53_dshift22": lambda d, r, C, m, C2, m2: candidate_b(d, r, C, m, C2, m2, shift_deficit=True),
    "c_forward53_a_eq_ck": lambda d, r, C, m, C2, m2: candidate_c_forward53(d, r, C, m, C2, m2),
}


def test_pair(C, m, candidate_names=None):
    C2 = C + CORRIDOR_SHIFT
    m2 = m + HEARTBEAT

    live_by_d = load_small_side_live_set(C, m)
    if live_by_d is None:
        return None

    sample, total_live, was_sampled = enumerate_sample(live_by_d, MAX_ELEMENTS_PER_PAIR)

    candidates_to_run = candidate_names or list(CANDIDATES.keys())
    pair_result = {
        "C": C, "m": m, "C2": C2, "m2": m2,
        "total_live_small": total_live,
        "sample_size": len(sample),
        "was_sampled": was_sampled,
        "candidates": {},
    }

    shared_memo = {}  # reuse across candidates/elements for this (C2,m2)
    pair_start = time.time()
    pair_time_exceeded = False

    for cname in candidates_to_run:
        cfunc = CANDIDATES[cname]
        matched = 0
        failed = 0
        inconclusive = 0
        undefined = 0  # candidate map itself not defined at this element (e.g. policy violated)
        skipped_time_budget = 0
        per_element = []
        t0 = time.time()
        for (d, r) in sample:
            if time.time() - pair_start > PAIR_TIME_BUDGET_SEC:
                pair_time_exceeded = True
                skipped_time_budget += 1
                per_element.append({"d": d, "r": r, "status": "skipped_time_budget"})
                continue
            mapped = cfunc(d, r, C, m, C2, m2)
            if mapped is None:
                undefined += 1
                per_element.append({"d": d, "r": r, "status": "map_undefined"})
                continue
            d2, r2 = mapped
            if d2 < 0 or d2 > C2:
                failed += 1
                per_element.append({"d": d, "r": r, "d2": d2, "r2": r2, "status": "out_of_corridor"})
                continue
            res = query_membership(C2, m2, d2, r2, steps=HEARTBEAT,
                                    call_cap=ORACLE_CALL_CAP, shared_memo=shared_memo)
            if res.inconclusive:
                inconclusive += 1
                status = "inconclusive"
            elif res.live:
                matched += 1
                status = "matched"
            else:
                failed += 1
                status = "failed"
            per_element.append({
                "d": d, "r": r, "d2": d2, "r2": r2, "status": status,
                "oracle_calls": res.calls, "oracle_time_sec": res.elapsed_sec,
            })
        elapsed = time.time() - t0

        n_tested = len(sample)
        pair_result["candidates"][cname] = {
            "n_tested": n_tested,
            "matched": matched,
            "failed": failed,
            "inconclusive": inconclusive,
            "undefined": undefined,
            "skipped_time_budget": skipped_time_budget,
            "matched_fraction_of_decided": (matched / (matched + failed)) if (matched + failed) > 0 else None,
            "elapsed_sec": elapsed,
            "shared_memo_final_size": len(shared_memo),
            "per_element": per_element,
        }
        print(f"  [{cname}] C={C} m={m}: tested={n_tested} matched={matched} "
              f"failed={failed} inconclusive={inconclusive} undefined={undefined} "
              f"skipped_time_budget={skipped_time_budget} time={elapsed:.1f}s")

    pair_result["pair_time_budget_exceeded"] = pair_time_exceeded
    return pair_result


def select_pairs(available, max_per_C=2):
    """
    Prioritize breadth across corridor widths C over depth within a single
    C: for each C, test the LOWEST persisted m (cheapest, cleanest signal)
    and the HIGHEST persisted m (closest to the proof's M_edge(C)+2 target
    precision), skipping intermediate m values. This was adopted after an
    initial run at full (C,m) coverage with a larger budget showed the
    oracle's cost growing fast enough with m (even at fixed small C) that
    exhaustive m-coverage per C would not finish in reasonable time -- see
    the NOTE ON BUDGET TUNING comment above MAX_ELEMENTS_PER_PAIR.
    """
    by_C = {}
    for (C, m) in available:
        by_C.setdefault(C, []).append(m)
    selected = []
    for C, ms in sorted(by_C.items()):
        ms = sorted(ms)
        if len(ms) <= max_per_C:
            selected.extend((C, m) for m in ms)
        else:
            selected.append((C, ms[0]))
            selected.append((C, ms[-1]))
    return selected


def main():
    print("=" * 70)
    print("EMBEDDING TEST: candidate maps phi: live(C,m) -> live(C+22, m+53)")
    print("=" * 70)

    available = []
    for f in sorted(LIVE_SETS_DIR.glob("C*_m*.npz")):
        name = f.stem
        c_part, m_part = name.split("_")
        C = int(c_part[1:])
        m = int(m_part[1:])
        available.append((C, m))
    available.sort()
    print(f"Found {len(available)} persisted small-side live sets: {available}")

    pairs_to_test = select_pairs(available)
    print(f"Selected {len(pairs_to_test)} pairs to test (breadth-first across C): {pairs_to_test}")

    all_results = []
    for (C, m) in pairs_to_test:
        print(f"\n--- Testing C={C} m={m} (C2={C+CORRIDOR_SHIFT} m2={m+HEARTBEAT}) ---")
        result = test_pair(C, m)
        if result:
            all_results.append(result)
            RESULTS_PATH.write_text(json.dumps({
                "description": "Embedding test: candidate maps phi tested against "
                                "big-side membership oracle (backward reachability, "
                                "compute-capped). See oracle.py docstring for the "
                                "honest tractability limitations. Pair selection is "
                                "BREADTH-FIRST across C (lowest+highest persisted m "
                                "per C), not exhaustive -- see select_pairs().",
                "corridor_shift": CORRIDOR_SHIFT,
                "heartbeat": HEARTBEAT,
                "max_elements_per_pair": MAX_ELEMENTS_PER_PAIR,
                "oracle_call_cap": ORACLE_CALL_CAP,
                "pair_time_budget_sec": PAIR_TIME_BUDGET_SEC,
                "pairs_available": available,
                "pairs_selected": pairs_to_test,
                "pairs": all_results,
            }, indent=2))

    print(f"\nWrote results for {len(all_results)} pairs to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
