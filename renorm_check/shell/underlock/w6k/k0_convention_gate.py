#!/usr/bin/env python3
"""
W6K-K0 -- Asymmetric validation rows + convention gate, per
W6K_CONVENTION_PINNING_ORDER.md section K0.

THE CANONICAL ORDER (architect ruling, binding, restated here verbatim):
letters are consumed in BACKWARD-consumption order -- index 0 = the
letter nearest the terminal -- exactly e1_walkers.backward_letters
semantics, which is what DERIVATION_NOTES.md sec 2's game defines.

Sec 2's game, restated precisely (this is what "canonical order" means
operationally, and the source of the delta-start subtlety e1_walkers.py's
own module docstring already ran into and fixed):

  rho starts at 1 (the terminal, at backward-step j=0, BEFORE the first
  backward step is taken). At each backward step j=0..m-1, consuming
  letter c_j (index 0 = letter nearest the terminal):
    - parity of the exponent a is FORCED by the CURRENT rho:
        rho%3==1 -> a even (a_min=2); rho%3==2 -> a odd (a_min=1);
        rho%3==0 -> DEAD, no legal a at any exponent (parity-kill).
    - given the forced parity, a ranges over ALL a of that parity with
      a>=a_min (ceiling-OFF) or additionally constrained so the running
      sum g(k) = sum_{j<=k}(a_j-c_j) never goes negative at any prefix
      k (ceiling-ON) -- pruned outright the moment a candidate a would
      make g(k)<0 (a "ceiling-kill", tracked and reported separately
      from a genuine parity-kill).
    - rho' = (2^a * rho - 1)/3 (exact integer division, guaranteed exact
      by the parity forcing).
  D(m) = min over admissible exponent processes of max_k g(k) (sec 2's
  conservation identity). Two explicit variants, per the order, NEVER
  silently collapsed to one:
    D_ceil = minimax restricted to processes with g(k)>=0 at every
             prefix k (ceiling-on).
    D_free = minimax with no such restriction (ceiling-off, unbounded
             above -- the walker may go arbitrarily far "above start
             depth" at intermediate prefixes).

Six asymmetric words over {1,2,3}, chosen (per the order) so canonical
and reverse orders give DIFFERENT answers: "13","31","113","311","123","321".
Each word string is read left-to-right as the CONSUMPTION sequence for
its "canonical" listing (c_0 = first char = consumed first = index 0 =
nearest terminal, matching e1_walkers.backward_letters' own indexing
convention applied to whatever finite word is handed to it); "reverse"
is the same tuple reversed.

This script:
  (1) Provides `hand_reference(word, ceiling_on)`: an exhaustive DFS
      directly implementing the canonical-order game as stated above
      (independent from-scratch code, NOT reusing e1_walkers/engine.py),
      used to CROSS-CHECK the hand-derivation transcribed into the
      ledger (which was worked out step-by-step on paper/narrated
      separately -- this function exists so the ledger's hand table can
      be mechanically re-verified, not to replace the hand work).
  (2) Tests THREE engine paths against the 12 (word, order) cases (6
      words x 2 orders), under BOTH ceiling variants where each path
      supports it:
        PATH A: e1_walkers backward-consumption walkers (S0 greedy,
                S1 steering) -- ceiling-OFF only, by construction (the
                order's own e1_walkers.py has no ceiling cap; reported
                as N/A for ceiling-ON, not silently treated as a fail).
                Since S0/S1 are single deterministic STRATEGIES (upper
                bounds on D_free), the gate criterion is: does the
                walker's OWN achieved max-partial-sum equal the true
                minimax D_free for that (word,order)? (a walker
                achieving a value ABOVE true D_free is not itself
                wrong -- it is a suboptimal strategy on a tiny word,
                which is expected on asymmetric words never validated
                before; a walker achieving a value BELOW true D_free
                would be an actual bug, i.e. an infeasible chain
                reported as feasible.)
        PATH B: f1_engine_ext.compute_D_and_optimal_set (the forward
                BFS/enumeration path, ceiling-ON only, by construction
                -- it has a fixed finite ceiling C baked into
                allowed_exponents). Run with the word AS THE WINDOW
                (anchor_steps=m, word_credit_fn(w)[k]=w[k]) in FORWARD
                INDEX ORDER (k=0..m-1 ascending) -- this is the actual,
                unmodified calling convention used throughout
                W6F/W6G/W6H/W6J. Tested against BOTH the canonical-order
                hand answer and the reverse-order hand answer, to see
                which one (if either) it matches -- this is the crux of
                the seam.
        PATH C: this round's own direct canonical-order engine
                (`k0_canonical_engine.py`, new code, written to
                literally implement the boxed definition above) --
                exhaustive minimax DFS, both ceiling variants natively.
  (3) GATE: every path must agree with the hand table under the
      CANONICAL order (reverse-order agreement is recorded for
      diagnostic interest but is NOT the gate condition -- the order
      says "every path must agree with the hand table under the
      canonical order"). Any disagreement -> STOP on that path,
      report exactly where.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).parent
UNDERLOCK = HERE.parent
sys.path.insert(0, str(UNDERLOCK / "w6e"))
sys.path.insert(0, str(UNDERLOCK / "w6f"))
sys.path.insert(0, str(UNDERLOCK))

from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
from e1_walkers import backward_letters, walk_S0, walk_S1  # noqa: E402
from f1_engine_ext import compute_D_and_optimal_set  # noqa: E402

WORDS = {
    "13": (1, 3),
    "31": (3, 1),
    "113": (1, 1, 3),
    "311": (3, 1, 1),
    "123": (1, 2, 3),
    "321": (3, 2, 1),
}


# ---------------------------------------------------------------------
# (1) Independent from-scratch reference implementation of the boxed
#     canonical-order game definition (does NOT import/reuse
#     e1_walkers.py or engine.py's own bfs_Dm -- only the two tiny
#     validated primitives forced_parity_for_backward_step /
#     backward_predecessor_exact, which are pure arithmetic facts about
#     the residue map, not part of what's under test for direction/
#     convention bugs).
# ---------------------------------------------------------------------

def hand_reference(letters, ceiling_on: bool, a_cap: int = 40):
    """Exhaustive DFS, canonical-order game, letters given already in
    CONSUMPTION order (index 0 = first consumed = nearest terminal).
    Returns (D, best_a_seq, n_kill_branches_parity, n_kill_branches_ceiling)."""
    m = len(letters)
    best = {"D": None, "chain": None}
    stats = {"parity_kills": 0, "ceiling_kills": 0}

    def dfs(j, rho, running, max_so_far, a_seq):
        if j == m:
            if best["D"] is None or max_so_far < best["D"]:
                best["D"] = max_so_far
                best["chain"] = tuple(a_seq)
            return
        c = letters[j]
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            stats["parity_kills"] += 1
            return
        a_min = 2 if parity == 0 else 1
        for a in range(a_min, a_min + a_cap, 2):
            running2 = running + (a - c)
            if ceiling_on and running2 < 0:
                stats["ceiling_kills"] += 1
                continue
            rho2 = backward_predecessor_exact(rho, a)
            max2 = max(max_so_far, running2)
            dfs(j + 1, rho2, running2, max2, a_seq + [a])

    dfs(0, 1, 0, 0, [])
    return best["D"], best["chain"], stats["parity_kills"], stats["ceiling_kills"]


# ---------------------------------------------------------------------
# Hand table (from the ledger's W6K-K0 entry, transcribed here so the
# gate can check the engine paths against it programmatically -- the
# ledger entry itself shows the step-by-step menus/kill points; this
# dict is the numeric summary of that work, cross-checked against
# hand_reference() above as an independent from-scratch reproduction).
# ---------------------------------------------------------------------

HAND_TABLE = {
    # (word, order) -> {"D_ceil": int, "D_free": int}
    ("13", "canonical"): {"D_ceil": 1, "D_free": 1},
    ("13", "reverse"):   {"D_ceil": 1, "D_free": 0},
    ("31", "canonical"): {"D_ceil": 1, "D_free": 0},
    ("31", "reverse"):   {"D_ceil": 1, "D_free": 1},
    ("113", "canonical"): {"D_ceil": 2, "D_free": 2},
    ("113", "reverse"):   {"D_ceil": 4, "D_free": 1},
    ("311", "canonical"): {"D_ceil": 4, "D_free": 1},
    ("311", "reverse"):   {"D_ceil": 2, "D_free": 2},
    ("123", "canonical"): {"D_ceil": 1, "D_free": 1},
    ("123", "reverse"):   {"D_ceil": 3, "D_free": 0},
    ("321", "canonical"): {"D_ceil": 3, "D_free": 0},
    ("321", "reverse"):   {"D_ceil": 1, "D_free": 1},
}


def letters_for(word, order):
    canon = WORDS[word]
    return canon if order == "canonical" else tuple(reversed(canon))


# ---------------------------------------------------------------------
# (2) Path checks
# ---------------------------------------------------------------------

def check_hand_reference_reproduces_table():
    print("=== Step 0: independent from-scratch reference vs the hand table ===")
    all_ok = True
    for (word, order), expect in HAND_TABLE.items():
        letters = letters_for(word, order)
        for variant in ("D_ceil", "D_free"):
            ceiling_on = (variant == "D_ceil")
            D, chain, pk, ck = hand_reference(letters, ceiling_on)
            ok = (D == expect[variant])
            all_ok = all_ok and ok
            print(f"  word={word:4} order={order:9} letters={letters} {variant}: "
                  f"hand_reference={D} table={expect[variant]} chain={chain} "
                  f"parity_kills={pk} ceiling_kills={ck} {'OK' if ok else '*** MISMATCH ***'}")
    print(f"  ==> independent reference {'MATCHES' if all_ok else 'DOES NOT MATCH'} the hand table.\n")
    return all_ok


def check_path_A_e1_walkers():
    """PATH A: e1_walkers backward-consumption walkers (ceiling-OFF
    only -- no ceiling cap exists in this code by construction)."""
    print("=== PATH A: e1_walkers.walk_S0 / walk_S1 (backward-consumption, ceiling-OFF only) ===")
    results = []
    for (word, order), expect in HAND_TABLE.items():
        letters = list(letters_for(word, order))
        r0 = walk_S0(letters)
        r1 = walk_S1(letters)
        D_free_true = expect["D_free"]
        for label, r in [("S0", r0), ("S1", r1)]:
            if r["died_at_step"] is not None:
                verdict = f"DIED@{r['died_at_step']} ({r['death_reason']})"
                # a walker death is a bug ONLY if the true D_free run shows
                # a feasible chain exists (i.e. hand_reference found no
                # parity-kill across all its DFS branches would be too
                # strong a claim here -- what matters is: does D_free
                # exist at all for this word/order? HAND_TABLE has a
                # value, so yes, a feasible chain exists; S0/S1 dying
                # while a feasible chain exists is a DIFFERENT kind of
                # miss -- report explicitly, do not paper over.
                bug = True
            else:
                mps = r["max_partial_sum"]
                # Walker achieves an upper bound on D_free; achieving
                # something STRICTLY BELOW the true minimax would mean
                # an infeasible/miscounted chain -- an actual bug.
                # Achieving something AT or ABOVE is a legitimate
                # (possibly suboptimal-strategy) outcome.
                bug = mps < D_free_true
                verdict = f"max_partial_sum={mps} (true D_free={D_free_true}) " \
                          f"{'EXACT MATCH' if mps == D_free_true else ('ABOVE (suboptimal strategy, not a bug)' if mps > D_free_true else 'BELOW TRUE D_free -- BUG')}"
            print(f"  word={word:4} order={order:9} {label}: {verdict}")
            results.append({"word": word, "order": order, "walker": label, "bug": bug})
    any_bug = any(r["bug"] for r in results)
    print(f"  ==> PATH A gate: {'FAIL -- see BUG rows above' if any_bug else 'PASS (no walker reports below true D_free; strategy suboptimality on tiny asymmetric words is expected, not a defect)'}\n")
    return not any_bug, results


def check_path_B_f1_engine_ext():
    """PATH B: f1_engine_ext.compute_D_and_optimal_set -- the forward
    BFS/enumeration path used throughout W6F/W6G/W6H/W6J, called
    EXACTLY as those rounds called it (word-as-window, anchor_steps=m,
    forward index order k=0..m-1). Ceiling-ON only (fixed C baked in).
    Tested against BOTH canonical and reverse hand answers to locate
    which convention it actually implements."""
    print("=== PATH B: f1_engine_ext.compute_D_and_optimal_set (forward-window, ceiling-ON, as called by W6F/H/J) ===")
    C = 18  # matches h3_alphabet_extension.py's own choice, ample margin for these tiny words
    results = []
    for word, canon_letters in WORDS.items():
        m = len(canon_letters)

        def fn(k, w=canon_letters):
            return w[k]

        D_engine, best_d, seqs = compute_D_and_optimal_set(fn, m, C, anchor_steps=m)
        matches_canon = (D_engine == HAND_TABLE[(word, "canonical")]["D_ceil"])
        matches_rev = (D_engine == HAND_TABLE[(word, "reverse")]["D_ceil"])
        print(f"  word={word:4} (letters as stored/consumed forward, index0=window-start): "
              f"engine_D={D_engine} | canonical-order hand D_ceil={HAND_TABLE[(word,'canonical')]['D_ceil']} "
              f"({'MATCH' if matches_canon else 'no match'}) | "
              f"reverse-order hand D_ceil={HAND_TABLE[(word,'reverse')]['D_ceil']} "
              f"({'MATCH' if matches_rev else 'no match'})")
        results.append({"word": word, "engine_D": D_engine,
                         "matches_canonical": matches_canon, "matches_reverse": matches_rev})
    n_match_canon = sum(1 for r in results if r["matches_canonical"])
    n_match_rev = sum(1 for r in results if r["matches_reverse"])
    print(f"\n  Summary: matches canonical-order hand table on {n_match_canon}/6 words; "
          f"matches reverse-order hand table on {n_match_rev}/6 words.")
    gate_pass = (n_match_canon == 6)
    print(f"  ==> PATH B gate (must match CANONICAL order per the order's own binding rule): "
          f"{'PASS' if gate_pass else 'FAIL'}\n")
    return gate_pass, results


def check_path_C_new_canonical_engine():
    """PATH C: this round's own new code, k0_canonical_engine.py --
    a direct, from-scratch (different code path than hand_reference
    above, and than e1_walkers/f1_engine_ext) implementation of the
    canonical-order game, built for K1/K2/K3 reuse. Must pass K0
    natively (both ceiling variants) before being trusted for the
    redos."""
    print("=== PATH C: w6k/k0_canonical_engine.py (new code for this round's K1/K2/K3 use) ===")
    from k0_canonical_engine import canonical_D
    all_ok = True
    for (word, order), expect in HAND_TABLE.items():
        letters = letters_for(word, order)
        for variant in ("D_ceil", "D_free"):
            ceiling_on = (variant == "D_ceil")
            D = canonical_D(letters, ceiling_on)
            ok = (D == expect[variant])
            all_ok = all_ok and ok
            print(f"  word={word:4} order={order:9} {variant}: engine={D} hand={expect[variant]} "
                  f"{'OK' if ok else '*** MISMATCH ***'}")
    print(f"  ==> PATH C gate: {'PASS' if all_ok else 'FAIL'}\n")
    return all_ok


def main():
    ref_ok = check_hand_reference_reproduces_table()
    if not ref_ok:
        print("*** STOP: independent from-scratch reference does not reproduce the "
              "transcribed hand table -- the hand table itself has an arithmetic "
              "error, fix before gating any engine path. ***")
        return

    a_ok, a_results = check_path_A_e1_walkers()
    b_ok, b_results = check_path_B_f1_engine_ext()
    c_ok = check_path_C_new_canonical_engine()

    print("=== K0 FINAL GATE ===")
    print(f"  PATH A (e1_walkers S0/S1, ceiling-OFF strategies): {'PASS' if a_ok else 'FAIL'}")
    print(f"  PATH B (f1_engine_ext.compute_D_and_optimal_set, ceiling-ON): {'PASS' if b_ok else 'FAIL'}")
    print(f"  PATH C (w6k new canonical-order engine): {'PASS' if c_ok else 'FAIL'}")
    if not b_ok:
        print("\n  PATH B FAILS the canonical-order gate. Per house rules: STOP on this "
              "path, do not run K1/K2 through it as-is. Diagnosis:")
        n_rev = sum(1 for r in b_results if r["matches_reverse"])
        print(f"    - It matches the REVERSE-order hand table on {n_rev}/6 words instead.")
        print("    - Root cause: compute_D_and_optimal_set / forward_live_fast consumes "
              "credit_fn(phase+k) for k=0..m-1 in ASCENDING index order relative to the "
              "window's own start (phase=anchor_steps-m), i.e. index 0 = FIRST letter of "
              "the word AS WRITTEN = the window's FAR end (farthest from the terminal at "
              "absolute forward step anchor_steps). The canonical order defines index 0 "
              "as the letter NEAREST the terminal -- the opposite end of the window. For "
              "a general (non-word-as-window) word this is a genuine direction mismatch, "
              "not merely a labeling difference: it is invisible whenever 2-c_j>=0 "
              "everywhere (every row validated through W6G/W6H's {1,2}/{0,1,2} alphabets), "
              "and it is EXACTLY what SYNTHESIS's 'W6J + architect audit' section already "
              "identified for word '13' (D=0 reported by the census, reproduced above).")


if __name__ == "__main__":
    main()
