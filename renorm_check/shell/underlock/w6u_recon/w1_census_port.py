#!/usr/bin/env python3
"""
W6U-RECON step 1 -- from-scratch port of the census's LITERAL deficit
recursion (rust/lock3_census.rs), plus the D_recon(m) reconciliation
DP defined in this round's task order. Exact integer arithmetic only.

=== Source citations (verbatim semantics being ported) ===

credit_at_step(k) (rust/lock3_census.rs:1247-1249):
    credit_at_step(k) = floor((k+1)*log2(3)) - floor(k*log2(3))
  computed EXACTLY via bit_length of powers of 3 (never float log2):
    floor(k*log2(3)) = (3**k).bit_length() - 1   for k > 0
                      = 0                          for k == 0
  (ExactFloorCursor.at()/step_credit(), lines 1220-1245, does exactly
  this via incremental BigBits.mul_small(3).)

Growth loop (lines 2080-2081, lean variant 2417-2418):
    for next_depth in (start_depth+1)..=config.depth:
        c = credit_at_step(next_depth - 1)
  Writing k = next_depth - 1 (0-indexed, k=0 = the trajectory's own
  FIRST transition out of the root Key::new(0,0) at depth 0): c_k =
  credit_at_step(k). Root-anchored: k=0 always means "this
  trajectory's first step", never an absolute/external calendar index.

Deficit transition (lines 2093-2116, mirrored 2461+):
    let branch_capacity = deficit_branch_capacity(config.c);   // lines 1251-1257
    if let Some(max_deficit) = max_deficit_for_c(config.c) {   // lines 1259-1265
        for d_next in 0..=max_deficit {        // d_next ranges over [0, C] INCLUSIVE
            let a = key.deficit() + c - d_next; // a DERIVED from d_next
            if a < 1 { continue; }              // legality: a >= 1 required
            // materialize child (d_next, ...) -- only reachable d_next survive
        }
    }
  deficit_branch_capacity(c) = if c<0 {0} else {c+1}
  max_deficit_for_c(c)       = if c<0 {None} else {Some(c)}
  Key::new (lines 268-278) panics if deficit < 0 -- deficit MUST be in
  [0, u32::MAX], and the growth loop's own enumeration additionally
  restricts to [0, config.c]. d_next > C is named an explicit upward
  "breach"/exit event in the code's own comments (~2427-2436), never a
  tracked state. This is a HARD TWO-SIDED WALL: for a FIXED a-sequence
  and FIXED C,
      d_next = d_prev + c_k - a_k
      LEGAL at step k+1 iff a_k >= 1 AND 0 <= d_next <= C
  the first k+1 where this fails is the bankruptcy/breach point.

Root state: Key::new(0, 0) at depth 0 -- deficit d=0.

=== D_recon(m) (this round's task definition) ===

D_recon(m) = the minimum capacity C such that there EXISTS a sequence
of positive integers a_1..a_m for which the root-anchored forward
deficit walk d_0=0, d_{k+1} = d_k + c_k - a_{k+1} (c_k=credit_at_step(k))
satisfies 0 <= d_k <= C for ALL k=0..m, AND d_m = 0 (round-trip to the
root/terminal-compatible state in exactly m steps, staying legal
throughout).

Computed via forward reachable-deficit-set DP: for FIXED C, track the
SET of deficits reachable at [0,C] after k steps (start: {0} at k=0).
Transition from d at step k (credit c_k): for a=1,2,3,... (a>=1), the
successor d' = d + c_k - a ranges over all integers <= d+c_k-1; capped
to the corridor [0,C], EVERY value in [0, min(C, d+c_k-1)] is reachable
by an appropriate a>=1 (choose a = d+c_k-d'). So:
    reach_{k+1} = { d' in [0, C] : d' <= d + c_k - 1 for some d in reach_k }
For fixed C, sweep k=0..m; D_recon(m) = smallest C for which 0 is
reachable in reach_m.

NOTE ON INTERVAL STRUCTURE: reach_k is not assumed to be an interval a
priori; the implementation below tracks the exact SET (as a Python
set of ints, capped at size C+1) rather than assuming contiguity, so
this is a genuine verified DP, not an assumed shortcut. (In practice
it does turn out to always be a contiguous interval [0, R_k] once
non-empty at k>=1, which is reported as an observation, not built in.)
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).parent


# ---------------------------------------------------------------------
# credit_at_step -- exact integer arithmetic, bit_length trick
# ---------------------------------------------------------------------

def floor_k_log2_3(k: int) -> int:
    """floor(k * log2(3)), exact via bit_length of 3**k. k=0 -> 0."""
    if k == 0:
        return 0
    return (3 ** k).bit_length() - 1


def credit_at_step(k: int) -> int:
    """credit_at_step(k) = floor((k+1)log2 3) - floor(k log2 3),
    rust/lock3_census.rs:1247-1249. Root-anchored: k=0 is the
    trajectory's own first transition."""
    return floor_k_log2_3(k + 1) - floor_k_log2_3(k)


# ---------------------------------------------------------------------
# Step 1(b): literal census deficit recursion replay for a FIXED
# a-sequence and FIXED C.
# ---------------------------------------------------------------------

def census_literal_replay(a_forward, C: int):
    """Replay the literal census forward deficit recursion for a fixed
    a-sequence (1-indexed a_1..a_m given as a_forward[0..m-1]) against
    a fixed capacity C. Returns:
        d_sequence   -- [d_0, d_1, ..., d_m] (d_0 = 0 always; if a
                         breach occurs, entries after the breach are
                         still computed as the "would-be" value the
                         recursion produces algebraically, matching
                         the reference script's reporting convention)
        legal        -- True iff every step 1..m is legal (a_k>=1 and
                         0<=d_k<=C)
        breach_index -- 0-indexed forward index i (matching a_forward's
                         indexing) of the FIRST illegal step, or None
        breach_kind  -- "a<1" / "upper (d_next > C)" / "lower (d_next < 0)"
        max_d, min_d -- over the full d_sequence (0..m)
    """
    d = 0
    d_sequence = [d]
    legal = True
    breach_index = None
    breach_kind = None
    for i, a in enumerate(a_forward):
        c_k = credit_at_step(i)  # k = i, root-anchored
        d_next = d + c_k - a
        if a < 1:
            ok = False
            kind = "a<1"
        elif d_next > C:
            ok = False
            kind = "upper (d_next > C)"
        elif d_next < 0:
            ok = False
            kind = "lower (d_next < 0)"
        else:
            ok = True
            kind = None
        if not ok and legal:
            legal = False
            breach_index = i
            breach_kind = kind
        d_sequence.append(d_next)
        d = d_next
    max_d = max(d_sequence)
    min_d = min(d_sequence)
    return d_sequence, legal, breach_index, breach_kind, max_d, min_d


# ---------------------------------------------------------------------
# Step 1(c): D_recon(m) DP
# ---------------------------------------------------------------------

def reachable_deficits_at_C(C: int, m: int):
    """Forward reachable-deficit-SET DP for fixed C, for k=0..m steps.
    reach[k] = set of deficits reachable at step k staying legal
    throughout (0<=d<=C at every intermediate step, a>=1 always
    satisfiable by choice). Returns the list of sets reach[0..m]
    (each a Python set) plus a flag of whether the set was observed
    to be a contiguous [0, R] interval at each k (an observation, not
    an assumption -- the DP itself uses full sets)."""
    reach = [set([0])]  # k=0: only d=0 (Key::new(0,0))
    interval_observation = [True]  # k=0 trivially {0} = [0,0]
    for k in range(m):
        c_k = credit_at_step(k)
        cur = reach[k]
        nxt = set()
        for d in cur:
            hi = d + c_k - 1  # a>=1 => d' <= d + c_k - 1
            if hi < 0:
                continue
            top = min(C, hi)
            for dp in range(0, top + 1):
                nxt.add(dp)
        reach.append(nxt)
        if nxt:
            is_interval = (sorted(nxt) == list(range(min(nxt), max(nxt) + 1)) and min(nxt) == 0)
        else:
            is_interval = True  # vacuously
        interval_observation.append(is_interval)
    return reach, interval_observation


def D_recon_sweep(m: int, C_max_search: int = 200):
    """D_recon(m) = smallest C such that 0 is reachable in reach_m
    (round-trip 0 -> 0 in exactly m legal steps under two-sided
    ceiling C). Sweep C upward from 0 (monotonicity checked
    separately in the validation gate below, not assumed here --
    this function does a plain linear sweep, stopping at first hit,
    which is correct regardless of monotonicity)."""
    for C in range(0, C_max_search + 1):
        reach, _ = reachable_deficits_at_C(C, m)
        if 0 in reach[m]:
            return C
    return None  # honest wall: not found in range


def D_recon_binary_search(m: int, monotonic_hi: int = 200):
    """Independent re-derivation route: binary search assuming
    monotonicity (more C is weakly easier). Used ONLY after
    monotonicity is verified empirically against the sweep on a range
    of m; kept as a separate code path for the cross-check."""
    lo, hi = 0, monotonic_hi
    # ensure hi actually admits a solution
    reach, _ = reachable_deficits_at_C(hi, m)
    if 0 not in reach[m]:
        return None
    while lo < hi:
        mid = (lo + hi) // 2
        reach, _ = reachable_deficits_at_C(mid, m)
        if 0 in reach[m]:
            hi = mid
        else:
            lo = mid + 1
    return lo


# ---------------------------------------------------------------------
# Validation gates
# ---------------------------------------------------------------------

A_FORWARD_839 = [1, 1, 2, 2, 1, 1, 2, 1, 4, 2, 1, 2, 1, 2, 2, 2, 1, 1, 1, 6, 1, 2, 2, 4, 1, 1, 2, 3, 4]
EXPECTED_LETTERS_839 = [1, 2, 1, 2, 1, 2, 2, 1, 2, 1, 2, 2, 1, 2, 1, 2, 1, 2, 2, 1, 2, 1, 2, 2, 1, 2, 1, 2, 1]
EXPECTED_D_SEQ_C11 = [0, 0, 1, 0, 0, 0, 1, 1, 1, -1, -2, -1, -1, -1, -1, -2, -2, -2, -1, 0,
                      -5, -4, -5, -5, -7, -7, -6, -7, -8, -11]
EXPECTED_BREACH_INDEX = 8
EXPECTED_BREACH_KIND = "lower (d_next < 0)"
EXPECTED_MAX_D = 1
EXPECTED_MIN_D = -11


def gate_credit_letters():
    my_letters = [credit_at_step(k) for k in range(29)]
    ok = (my_letters == EXPECTED_LETTERS_839)
    return ok, my_letters


def gate_839_replay():
    d_seq, legal, breach_i, breach_kind, max_d, min_d = census_literal_replay(A_FORWARD_839, 11)
    ok = (d_seq == EXPECTED_D_SEQ_C11 and legal is False and
          breach_i == EXPECTED_BREACH_INDEX and breach_kind == EXPECTED_BREACH_KIND and
          max_d == EXPECTED_MAX_D and min_d == EXPECTED_MIN_D)
    return ok, d_seq, legal, breach_i, breach_kind, max_d, min_d


def m_edge_formula(C: int) -> int:
    """Published capacity formula: M_edge(C) = floor(53*(C+1)/22)."""
    return (53 * (C + 1)) // 22


def gate_D_recon_edges():
    """D_recon(9)=3, D_recon(12)=4, D_recon(14)=5 -- the genuine
    C=3,4,5 edge data (M_edge(3)=9, M_edge(4)=12, M_edge(5)=14), per
    the inversion D_recon(m) = min{C : M_edge(C) >= m}."""
    targets = {9: 3, 12: 4, 14: 5}
    results = {}
    all_ok = True
    for m, expected_C in targets.items():
        got = D_recon_sweep(m, C_max_search=50)
        results[m] = got
        if got != expected_C:
            all_ok = False
    return all_ok, results, targets


def diagnose_degeneracy():
    """DIAGNOSIS (run when gate_D_recon_edges fails): the literal
    task definition of D_recon(m) -- min C admitting a legal 0->0
    round trip of length m under the two-sided ceiling -- is
    DEGENERATE. Proof by construction: credit_at_step(k) in {1,2} for
    ALL k (never 0, checked exhaustively for k=0..999 below), so the
    "identity path" a_k = c_k for every k satisfies d_{k+1} = d_k +
    c_k - a_k = d_k for all k, staying at d=0 throughout, for ANY C>=0
    (since a_k = c_k in {1,2} >= 1 is always legal). Hence 0 is
    reachable at step m for EVERY m at C=0 already -- D_recon(m)=0 for
    all m under the literal definition, contradicting the expected
    genuine edge data (3,4,5). This is verified directly, not
    inferred: the DP's own reach_fullpop-at-C=0 trace never empties.

    ROOT CAUSE: the census's real corridor (M_edge) obstruction is
    NOT encoded in the deficit recursion alone -- it lives entirely in
    the RESIDUE/ARITHMETIC constraint (rust/lock3_census.rs's
    next_terminal_residue / terminal_residue_signature machinery,
    embedding/automaton.py's r==1 mod 3^m terminal test). The deficit
    recursion by itself (no residue tracking) is a free walk with no
    non-trivial obstruction: the corridor [0,C] is always inhabitable
    forever via the constant-c path, for every C>=0, including C=0.
    The task's instruction that residue-tracking is unnecessary and
    that "the root itself IS the terminal-compatible state ... the
    terminal value's residue is 0 mod anything at depth 0" describes
    depth 0 correctly (trivially true there, modulus 3^0=1) but does
    NOT generalize to "d=0 at any later depth k>0 is ALSO
    terminal-compatible" -- that stronger claim is false in the
    census's own semantics (residue compatibility at depth k requires
    matching mod 3^k, which shrinks the compatible set geometrically,
    not merely returning the deficit bookkeeping to 0). Returning to
    d=0 is necessary but nowhere near sufficient for valid1 status at
    depth k>0.

    Exploratory (reported, not adopted -- uses residue tracking the
    task said was unnecessary, and does not hit the target exactly
    either): re-adding the actual Collatz residue constraint (forced
    parity via forced_parity_for_backward_step/backward_predecessor_exact,
    root-anchored word, backward DFS) with a two-sided ceiling [0,C]
    added to the game's existing one-sided (>=0) ceiling gives min C =
    4, 5, 6 for m=9, 12, 14 respectively -- consistently ONE HIGHER
    than the genuine 3, 4, 5. This is closer than the degenerate pure-
    deficit walk but still does not reproduce the genuine edge data
    exactly, and it required exactly the residue machinery the task
    said to avoid. Neither of the two constructions tried reproduces
    the genuine M_edge inversion exactly without residue arithmetic.
    """
    letters_sample = [credit_at_step(k) for k in range(1000)]
    never_zero = 0 not in set(letters_sample)
    reach0, _ = reachable_deficits_at_C(0, 60)
    stays_alive_at_C0 = all(len(r) > 0 for r in reach0)
    zero_always_reachable_at_C0 = all(0 in r for r in reach0[1:])
    return {
        "credit_letters_never_zero_k0_999": never_zero,
        "C0_walk_never_dies_through_m60": stays_alive_at_C0,
        "C0_zero_reachable_every_step": zero_always_reachable_at_C0,
    }


def monotonicity_check(m_range):
    """Verify D_recon(m) is monotone non-decreasing in m (more steps
    require >= capacity) -- checked empirically, not assumed."""
    vals = {m: D_recon_sweep(m, C_max_search=100) for m in m_range}
    violations = []
    prev_m, prev_v = None, None
    for m in sorted(vals):
        v = vals[m]
        if prev_v is not None and v is not None and v < prev_v:
            violations.append((prev_m, prev_v, m, v))
        prev_m, prev_v = m, v
    return len(violations) == 0, vals, violations


def main():
    out_lines = []

    def p(s=""):
        print(s)
        out_lines.append(s)

    p("=== W6U-RECON W1: census port + validation gates ===\n")

    # Gate 0: credit letters
    ok0, my_letters = gate_credit_letters()
    p(f"[GATE 0] credit_at_step(k) for k=0..28 matches s2_output.log's printed letters: "
      f"{'PASS' if ok0 else 'FAIL'}")
    p(f"  mine:     {my_letters}")
    p(f"  expected: {EXPECTED_LETTERS_839}")
    if not ok0:
        p("STOP: credit_at_step diverges from the reference. Diagnosing required before proceeding.")
        with open(HERE / "w1_output.log", "w") as f:
            f.write("\n".join(out_lines) + "\n")
        sys.exit(1)

    # Gate 1: 839-chain replay at C=11
    ok1, d_seq, legal, breach_i, breach_kind, max_d, min_d = gate_839_replay()
    p(f"\n[GATE 1] 839-chain (m=29) literal census replay at C=11 matches s2_output.log EXACTLY: "
      f"{'PASS' if ok1 else 'FAIL'}")
    p(f"  d_sequence (mine): {d_seq}")
    p(f"  d_sequence (ref) : {EXPECTED_D_SEQ_C11}")
    p(f"  legal={legal} (expected False), breach_index={breach_i} (expected {EXPECTED_BREACH_INDEX}), "
      f"breach_kind={breach_kind!r} (expected {EXPECTED_BREACH_KIND!r})")
    p(f"  max_d={max_d} (expected {EXPECTED_MAX_D}), min_d={min_d} (expected {EXPECTED_MIN_D})")
    if not ok1:
        p("STOP: 839-chain replay diverges from the reference oracle. Diagnosing required before proceeding.")
        with open(HERE / "w1_output.log", "w") as f:
            f.write("\n".join(out_lines) + "\n")
        sys.exit(1)

    # Gate 2: D_recon at the genuine C=3,4,5 edges
    ok2, results, targets = gate_D_recon_edges()
    p(f"\n[GATE 2] D_recon(m) matches genuine C=3,4,5 edge data (D_recon(9)=3, D_recon(12)=4, "
      f"D_recon(14)=5): {'PASS' if ok2 else 'FAIL'}")
    for m in sorted(targets):
        p(f"  D_recon({m}) = {results[m]}  (expected {targets[m]}, "
          f"{'MATCH' if results[m] == targets[m] else 'MISMATCH'})")

    if not ok2:
        p("\n*** STOP-AND-DIAGNOSE (house rule): D_recon DP diverges from genuine edge data. ***")
        diag = diagnose_degeneracy()
        p("\n[DIAGNOSIS] The literal task definition of D_recon(m) (min C admitting a legal")
        p("0->0 round trip of length m under the two-sided ceiling ALONE, no residue check)")
        p("is DEGENERATE -- it evaluates to 0 for every m, not the genuine 3/4/5.")
        p(f"  credit_at_step(k) in {{1,2}} for k=0..999 (never 0): {diag['credit_letters_never_zero_k0_999']}")
        p(f"  At C=0, the walk never dies through m=60 steps: {diag['C0_walk_never_dies_through_m60']}")
        p(f"  At C=0, d=0 is reachable at EVERY step (identity path a_k=c_k always legal): "
          f"{diag['C0_zero_reachable_every_step']}")
        p("  ROOT CAUSE: credit letters are always in {1,2} (>=1), so the identity path")
        p("  a_k = c_k keeps d_k = 0 for all k, which is legal at ANY C >= 0. The census's")
        p("  real obstruction (M_edge's eventual death) lives ENTIRELY in the residue/")
        p("  arithmetic terminal-compatibility check (r == 1 mod 3^m), NOT in the deficit")
        p("  recursion's bookkeeping alone. 'd returns to 0' is necessary but nowhere near")
        p("  sufficient for valid1 status at depth k>0 in the census's own semantics --")
        p("  the task's stated shortcut ('root itself IS terminal-compatible ... residue")
        p("  is 0 mod anything at depth 0') is true only AT depth 0 and does not generalize")
        p("  to d=0 at later depths, which is what the degenerate identity path exploits.")
        p("  Exploratory (NOT adopted, uses residue tracking the task said to skip, and")
        p("  still off by +1): re-adding the real Collatz residue constraint (forced")
        p("  parity, root-anchored backward DFS) with a two-sided ceiling added gives")
        p("  min C = 4, 5, 6 for m=9, 12, 14 -- consistently ONE HIGHER than genuine 3,4,5,")
        p("  so this is not the fix either; reported for completeness, not used below.")
        p("\nThis is reported HONESTLY as a wall, per house rules, rather than papered over.")
        p("D_recon(m) as literally specified cannot be trusted as a comparison column; it")
        p("is reported below (all zeros) for completeness, but the round's real comparison")
        p("columns are the mirror-law formula and the two well-defined game-D variants,")
        p("which do not depend on resolving this degeneracy.")

    # Gate 3: monotonicity (checked, not assumed) -- run regardless, for the record
    ok3, vals, violations = monotonicity_check(range(0, 33))
    p(f"\n[GATE 3] D_recon(m) monotone non-decreasing in m, m=0..32 (for the record; "
      f"D_recon itself is degenerate per GATE 2): {'PASS' if ok3 else 'FAIL'}")
    p(f"  D_recon(m) for m=0..32: {vals}")
    if violations:
        p(f"  VIOLATIONS: {violations}")

    # Gate 4: sweep vs binary-search cross-check (independent derivation route)
    p(f"\n[GATE 4] sweep vs binary-search cross-check, m=0..32 (both implementations of the")
    p(f"same degenerate DP -- confirms the degeneracy is not a sweep/search bug):")
    all_match = True
    for m in range(0, 33):
        sw = D_recon_sweep(m, C_max_search=100)
        bs = D_recon_binary_search(m, monotonic_hi=100)
        match = (sw == bs)
        all_match = all_match and match
        if not match:
            p(f"  m={m}: sweep={sw} binary_search={bs}  MISMATCH")
    p(f"  {'ALL MATCH (both = 0 for all m, confirming degeneracy is structural, not a DP bug)' if all_match else 'MISMATCHES FOUND (see above)'}")

    p(f"\n=== GATE SUMMARY: gate0={ok0} gate1={ok1} gate2(D_recon edges)={ok2} "
      f"gate3(monotonicity)={ok3} gate4(cross-check)={all_match} ===")
    p("D_recon(m) itself FAILED validation (GATE 2) -- this is reported as the round's")
    p("central honest wall, not silently proceeded past. Step 2 below still builds the")
    p("well-defined comparison columns (mirror-law, game-D root/end-anchored) and reports")
    p("D_recon's degenerate value alongside them for transparency.")

    with open(HERE / "w1_output.log", "w") as f:
        f.write("\n".join(out_lines) + "\n")
    p(f"\nWrote {HERE / 'w1_output.log'}")


if __name__ == "__main__":
    main()
