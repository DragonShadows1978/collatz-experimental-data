#!/usr/bin/env python3
"""
W6U-RECON step 4 -- CORRECTED D_recon: census's literal deficit
recursion (w1's validated port, unchanged) PLUS census's literal
residue semantics (newly ported here). Supersedes w1's D_recon
definition (which was diagnosed degenerate); w1-w3 record kept as-is.

=== Residue machinery, verified against rust/lock3_census.rs ===

residue_modulus(depth, residue_mod_power) = 3^min(depth, residue_mod_power)
    (lines 1267-1274).
pow_mod(base, exp, modulus): modular pow; NOTE modulus==1 -> returns 0
    (lines 1276-1290).
mod_inverse(value, modulus): extended Euclid (lines 1292-1313).
next_terminal_residue(residue, exponent, modulus) =
    (3*residue + 1) * mod_inverse(2^exponent mod modulus) mod modulus,
    with modulus==1 -> 0 (lines 1315-1321).
Growth loop applies it with the NEW depth's modulus:
    modulus = residue_modulus(next_depth, config.residue_mod_power)  (line 2082)
    terminal_residue_signature = config.terminal_value % modulus     (line 2083)
    next_key = Key::new(d_next, next_terminal_residue(key.residue(), a, modulus))
                                                          (lines 2113-2114)
Root: Key::new(0, 0) at depth 0, modulus 3^0 = 1, residue trivially 0.
terminal_value default = 1 (parse_args, line 598: `let mut
terminal_value = 1u64;`; CLI override --terminal-value at lines
636-639; oddness/nonzero enforced at lines 570-572).
NOTE ALSO: residue_mod_power CLI default = 8 (line 599: `let mut
residue_mod_power = 8usize;`) -- the census by default tracks residues
only mod 3^min(depth, 8). This matters for G3 variant (iii); the
PRIMARY definition below uses FULL precision (residue_mod_power = m,
i.e. modulus 3^min(depth, m) = 3^depth for depth <= m), with the
capped variant available as a switch.

=== The corrected D_recon(m) ===

D_recon(m) = min C >= 0 such that there EXISTS an a-sequence
(a_i >= 1) with BOTH:
 (1) deficit legality: d_0 = 0, d_{k+1} = d_k + c_k - a_{k+1},
     0 <= d_k <= C for ALL k = 0..m  (d_m FREE in [0,C], not pinned);
 (2) residue legality: r_m == terminal_value (=1) mod 3^m under the
     deterministic forward residue walk r_0 = 0,
     r_{k+1} = (3 r_k + 1) * inv(2^{a_{k+1}}) mod 3^{k+1}.

=== Reduction used by the search (derived, then verified) ===

Backward characterization: multiply the forward recurrence by
2^{a_{k+1}}: r_k = (2^{a_{k+1}} r_{k+1} - 1)/3 mod 3^k, exact
division iff 2^{a_{k+1}} r_{k+1} == 1 mod 3, which forces a's PARITY
from r_{k+1} mod 3 (r==1 mod 3 -> a even; r==2 -> a odd; r==0 ->
dead). Walking backward from an exact-integer rho = 1 with
rho' = (2^a rho - 1)/3 (all divisions exact) enumerates exactly the
residue-legal a-sequences (verified empirically in GATE 0b below by
exhaustive forward-vs-backward agreement on small m).

Deficit bookkeeping in backward order: let s_j = sum over the j
consumed (last) forward steps of (c - a). Then d_{m-j} = d_m - s_j
and d_0 = 0 forces d_m = s_m, so deficit legality for the whole walk
is EXACTLY:
    s_m >= max_{j=0..m} s_j     (all d_k >= 0)
    s_m - min_{j=0..m} s_j <= C (all d_k <= C)
(s_0 = 0 included; d_m in [0,C] falls out via j=0 and j=argmin.)
Equivalently: D_recon(m) = min over residue-legal, floor-legal
(all d_k >= 0) a-sequences of max_k d_k -- the minimal peak deficit
of a root-pinned floor-legal walk. Both search implementations below
verify their bookkeeping against w1's forward port on every witness.

Two independent implementations (cross-checked):
  A. exists_at_C(m, C): memoized backward DFS over EXACT-INTEGER rho,
     existence per fixed C, swept C = 0, 1, 2, ... upward. Memo key
     (j, rho mod 3^{m-j}, s - min_s, max_s - s) -- everything
     future-relevant. Failure states memoized; witness returned on
     success.
  B. exists_at_C_bfs(m, C): layered breadth-first frontier over
     MODULAR residues only (rho tracked mod 3^{m-j} at layer j -- no
     big integers anywhere; transition (2^a*R - 1)/3 mod 3^{m-j-1}
     computed from a representative, well-defined because changing R
     by t*3^{m-j} changes the image by t*2^a*3^{m-j-1}), deduplicated
     per layer on the same future-sufficient key, witness rebuilt via
     parent pointers. Different traversal (BFS vs DFS), different
     number representation (modular vs exact), different dedup
     mechanism (layer dedup vs failure memo).

NOTE on an earlier draft's bug (caught before any results were used):
a branch-and-bound variant seeded with best=10^9 made the per-step
exponent bound effectively unbounded before the first incumbent --
non-terminating. Replaced by implementation B above; additionally a
node-entry range check (max_s - min_s <= C) was added to both
implementations (s can overshoot the corridor by 1 on a c=2, a=1
step before the a-bound at the NEXT step would notice).
"""
from __future__ import annotations

import sys
import time
import resource
from pathlib import Path

HERE = Path(__file__).parent
UNDERLOCK = HERE.parent
W6E = UNDERLOCK / "w6e"
sys.path.insert(0, str(UNDERLOCK))
sys.path.insert(0, str(W6E))
sys.path.insert(0, str(HERE))

from w1_census_port import credit_at_step, census_literal_replay  # noqa: E402


def rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


# ---------------------------------------------------------------------
# Residue primitives (ported verbatim; exact ints only)
# ---------------------------------------------------------------------

def residue_modulus(depth: int, residue_mod_power: int) -> int:
    """3^min(depth, residue_mod_power) -- lock3_census.rs:1267-1274."""
    return 3 ** min(depth, residue_mod_power)


def next_terminal_residue(residue: int, exponent: int, modulus: int) -> int:
    """(3r+1) * inv(2^a) mod modulus; modulus==1 -> 0.
    lock3_census.rs:1315-1321 (pow_mod 1276-1290, mod_inverse
    1292-1313 -- Python's pow(v, -1, mod) is the same function)."""
    if modulus == 1:
        return 0
    inv = pow(pow(2, exponent, modulus), -1, modulus)
    return ((3 * residue + 1) * inv) % modulus


def forward_residue_walk(a_forward, residue_mod_power=None):
    """The census's own deterministic residue trace for a fixed
    a-sequence: r_0 = 0 (Key::new(0,0)), r at depth k+1 computed with
    the NEW depth's modulus (growth loop lines 2082, 2113-2114).
    residue_mod_power=None means full precision (= len(a_forward))."""
    m = len(a_forward)
    if residue_mod_power is None:
        residue_mod_power = m
    r = 0
    trace = [r]
    for i, a in enumerate(a_forward):
        modulus = residue_modulus(i + 1, residue_mod_power)
        r = next_terminal_residue(r, a, modulus)
        trace.append(r)
    return trace


def residue_legal_forward(a_forward, terminal_value=1, residue_mod_power=None):
    """valid1 at depth m: r_m == terminal_value % modulus (line 2083)."""
    m = len(a_forward)
    if residue_mod_power is None:
        residue_mod_power = m
    trace = forward_residue_walk(a_forward, residue_mod_power)
    modulus = residue_modulus(m, residue_mod_power)
    return trace[-1] == terminal_value % modulus


# ---------------------------------------------------------------------
# Backward-walk primitives (re-derived locally; cross-checked against
# w6e/engine.py's validated pair in GATE 0a)
# ---------------------------------------------------------------------

def parity_forced(rho: int):
    """Parity of a forced by rho mod 3 for the backward step
    rho' = (2^a rho - 1)/3: class 0 -> None (dead), class 1 -> even,
    class 2 -> odd."""
    cls = rho % 3
    if cls == 0:
        return None
    return 0 if cls == 1 else 1


def backward_pred(rho: int, a: int) -> int:
    num = (1 << a) * rho - 1
    assert num % 3 == 0, "parity rule violated"
    return num // 3


def backward_walk_legal(a_forward):
    """Is the a-sequence residue-legal per the BACKWARD
    characterization? Walk from exact rho=1 consuming a in reverse;
    every step's parity must match the forced parity."""
    rho = 1
    for a in reversed(a_forward):
        p = parity_forced(rho)
        if p is None or (a % 2 == 0) != (p == 0):
            return False, None
        rho = backward_pred(rho, a)
    return True, rho


# ---------------------------------------------------------------------
# Implementation A: memoized existence search at fixed (m, C)
# ---------------------------------------------------------------------

def exists_at_C(m: int, C: int, memo_cap: int = 20_000_000):
    """Backward DFS with failure memoization. Returns (witness
    a_forward list or None, stats dict). Letters consumed backward:
    backward step j (1-based) uses credit_at_step(m - j)."""
    letters = [credit_at_step(m - j) for j in range(1, m + 1)]
    pow3 = [3 ** i for i in range(m + 1)]
    memo = set()
    stats = {"nodes": 0, "memo_hits": 0, "memo_capped": False}

    # iterative DFS with explicit stack to allow witness reconstruction
    # (recursive is fine at m<=32; use recursion for clarity)
    sys.setrecursionlimit(10000)

    def dfs(j, rho, s, min_s, max_s, acc):
        """acc: list of a chosen so far (backward order). Returns
        witness (backward-order list) or None."""
        stats["nodes"] += 1
        if max_s - min_s > C:
            return None  # corridor range irrecoverably exceeded
        if j == m:
            if s >= max_s and s - min_s <= C:
                return list(acc)
            return None
        key = (j, rho % pow3[m - j], s - min_s, max_s - s)
        if key in memo:
            stats["memo_hits"] += 1
            return None
        c = letters[j]
        p = parity_forced(rho)
        if p is not None:
            a_min = 2 if p == 0 else 1
            # bound: s' = s + c - a must keep eventual range <= C:
            # s' >= max_s - C  =>  a <= c + C - (max_s - s)
            a_hi = c + C - (max_s - s)
            a = a_min
            while a <= a_hi:
                s2 = s + c - a
                acc.append(a)
                res = dfs(j + 1, backward_pred(rho, a), s2,
                          min(min_s, s2), max(max_s, s2), acc)
                acc.pop()
                if res is not None:
                    return res
                a += 2
        if len(memo) < memo_cap:
            memo.add(key)
        else:
            stats["memo_capped"] = True
        return None

    wit_backward = dfs(0, 1, 0, 0, 0, [])
    if wit_backward is None:
        return None, stats
    # backward-order list: element j-1 is a_{m-j+1}; forward order = reversed
    return list(reversed(wit_backward)), stats


def D_recon_corrected(m: int, C_max: int = 40):
    """Sweep C upward; return (D, witness_forward, per_C_stats)."""
    per_C = []
    for C in range(0, C_max + 1):
        wit, stats = exists_at_C(m, C)
        per_C.append((C, stats["nodes"], stats["memo_hits"], stats["memo_capped"]))
        if wit is not None:
            return C, wit, per_C
    return None, None, per_C


# ---------------------------------------------------------------------
# Implementation B: layered BFS over modular residues (no big ints)
# ---------------------------------------------------------------------

def exists_at_C_bfs(m: int, C: int, state_cap: int = 20_000_000):
    """Layered breadth-first existence search at fixed (m, C).
    State at layer j: (R, u, v) with R = rho mod 3^{m-j},
    u = s - min_s, v = max_s - s (both in [0, C]). Parent pointers
    for witness reconstruction. Transition: parity forced by R mod 3
    (well-defined: m-j >= 1 while j < m); successor residue
    (2^a * R - 1)/3 mod 3^{m-j-1} via any representative (image
    well-defined mod 3^{m-j-1}). Acceptance at layer m: s >= max_s
    (v == 0 tracked exactly: v = max_s - s) and s - min_s <= C
    (u <= C, maintained by construction).
    Returns (witness_forward or None, stats)."""
    letters = [credit_at_step(m - j) for j in range(1, m + 1)]
    pow3 = [3 ** i for i in range(m + 1)]
    stats = {"layer_sizes": [], "state_capped": False}

    # layer 0: rho = 1 mod 3^m, s = min_s = max_s = 0
    start = (1 % pow3[m], 0, 0)
    frontier = {start: None}  # state -> (parent_state, a)
    layers = [frontier]
    for j in range(m):
        c = letters[j]
        mod_next = pow3[m - j - 1]
        nxt = {}
        for (R, u, v), _parent in frontier.items():
            # u = s - min_s, v = max_s - s
            p = parity_forced(R % 3)
            if p is None:
                continue
            a_min = 2 if p == 0 else 1
            # s' = s + c - a; require eventual range <= C:
            # s' >= max_s - C  =>  a <= c + C - v
            a_hi = c + C - v
            a = a_min
            while a <= a_hi:
                delta = c - a  # s' - s
                # new u' = s' - min(min_s, s') ; new v' = max(max_s, s') - s'
                s_rel = delta  # s' relative to s
                new_min_rel = min(-u, s_rel)   # min_s' relative to s
                new_max_rel = max(v, s_rel)    # max_s' relative to s
                u2 = s_rel - new_min_rel
                v2 = new_max_rel - s_rel
                if u2 <= C and v2 <= C and (new_max_rel - new_min_rel) <= C:
                    R2 = ((R * (1 << a)) - 1) // 3 % mod_next if mod_next > 1 else 0
                    # exact division check on the representative:
                    assert (R * (1 << a) - 1) % 3 == 0, "parity bookkeeping bug"
                    key2 = (R2, u2, v2)
                    if key2 not in nxt:
                        nxt[key2] = ((R, u, v), a)
                a += 2
            if len(nxt) > state_cap:
                stats["state_capped"] = True
                return None, stats
        frontier = nxt
        layers.append(frontier)
        stats["layer_sizes"].append(len(frontier))
        if not frontier:
            return None, stats

    # acceptance: v == 0 (s >= max_s) -- u <= C guaranteed by construction
    goal = None
    for (R, u, v) in frontier:
        if v == 0:
            goal = (R, u, v)
            break
    if goal is None:
        return None, stats

    # witness reconstruction (backward order), then reverse
    a_backward = []
    cur = goal
    for j in range(m, 0, -1):
        parent, a = layers[j][cur]
        a_backward.append(a)
        cur = parent
    a_backward.reverse()  # now in backward-consumption order j=1..m
    return list(reversed(a_backward)), stats


def D_recon_corrected_bfs(m: int, C_max: int = 40):
    """Independent sweep using implementation B."""
    for C in range(0, C_max + 1):
        wit, stats = exists_at_C_bfs(m, C)
        if stats.get("state_capped"):
            return None, None, "state_capped"
        if wit is not None:
            return C, wit, None
    return None, None, None


# ---------------------------------------------------------------------
# Witness verification (G4 machinery)
# ---------------------------------------------------------------------

def verify_witness(a_forward, C):
    """Full exact-integer verification of a witness at capacity C:
    (i) deficit legality via w1's validated forward port;
    (ii) residue legality via the census's own forward walk;
    (iii) backward rho reconstruction from 1 -> real odd integer n;
    (iv) TRUE forward Collatz replay from n: n -> (3n+1)/2^a must be
         an exact odd integer at every step, landing on 1 (this also
         certifies a_k = v2(3n_k+1) exactly, since the quotient is odd).
    Returns dict of results."""
    m = len(a_forward)
    d_seq, legal, breach_i, breach_kind, max_d, min_d = census_literal_replay(a_forward, C)
    deficit_ok = legal and d_seq[0] == 0 and all(0 <= d <= C for d in d_seq)

    residue_ok = residue_legal_forward(a_forward)

    bk_ok, n0 = backward_walk_legal(a_forward)

    collatz_ok = False
    if bk_ok:
        cur = n0
        ok = True
        for a in a_forward:
            if cur % 2 != 1:
                ok = False
                break
            t = 3 * cur + 1
            if t % (2 ** a) != 0:
                ok = False
                break
            cur = t // (2 ** a)
        collatz_ok = ok and cur == 1
    return {
        "deficit_ok": deficit_ok, "residue_ok": residue_ok,
        "backward_ok": bk_ok, "start_integer": n0,
        "collatz_replay_ok": collatz_ok,
        "d_seq": d_seq, "max_d": max_d, "min_d": min_d,
        "all_ok": deficit_ok and residue_ok and bk_ok and collatz_ok,
    }


# ---------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------

A_FORWARD_839 = [1, 1, 2, 2, 1, 1, 2, 1, 4, 2, 1, 2, 1, 2, 2, 2, 1, 1, 1, 6,
                 1, 2, 2, 4, 1, 1, 2, 3, 4]


def main():
    out_lines = []

    def p(s=""):
        print(s)
        out_lines.append(s)

    t0 = time.time()
    p("=== W6U-RECON W4: corrected D_recon (deficit + residue semantics) ===\n")

    # -- GATE 0a: local parity/predecessor vs w6e engine's validated pair
    from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
    ok0a = True
    for rho in list(range(1, 200, 2)) + [839, 1259, 2393]:
        if parity_forced(rho) != forced_parity_for_backward_step(rho):
            ok0a = False
        pf = parity_forced(rho)
        if pf is not None:
            a = 2 if pf == 0 else 1
            if backward_pred(rho, a) != backward_predecessor_exact(rho, a):
                ok0a = False
    p(f"[GATE 0a] local parity/predecessor primitives match w6e/engine.py's validated pair: "
      f"{'PASS' if ok0a else 'FAIL'}")

    # -- GATE 0b: forward residue-legality == backward-walk legality
    # (exhaustive over all a-sequences with a in 1..5, m = 2..6)
    ok0b = True
    n_checked = 0
    n_legal = 0
    import itertools
    for m in range(2, 7):
        for combo in itertools.product(range(1, 6), repeat=m):
            fw = residue_legal_forward(list(combo))
            bw, _ = backward_walk_legal(list(combo))
            n_checked += 1
            n_legal += fw
            if fw != bw:
                ok0b = False
                p(f"  DISAGREE at m={m}, a={combo}: forward={fw} backward={bw}")
    p(f"[GATE 0b] forward residue walk (census semantics, r_0=0, modulus 3^(k+1)) == "
      f"backward rho-chain legality: {'PASS' if ok0b else 'FAIL'} "
      f"({n_checked} sequences exhaustively checked, m=2..6, a<=5; {n_legal} legal)")
    if not (ok0a and ok0b):
        p("STOP: primitive gates failed.")
        (HERE / "w4_output.log").write_text("\n".join(out_lines) + "\n")
        sys.exit(1)

    # -- GATE 1: w1's forward-port gates stay green (re-run via import)
    from w1_census_port import gate_credit_letters, gate_839_replay  # noqa: E402
    ok_g1a, _ = gate_credit_letters()
    ok_g1b = gate_839_replay()[0]
    p(f"\n[GATE G1] w1 forward-port gates stay green: credit letters {'PASS' if ok_g1a else 'FAIL'}, "
      f"839-chain replay {'PASS' if ok_g1b else 'FAIL'}")

    # -- GATE 2: 839 chain residue-legal but NEVER deficit-legal
    res839 = residue_legal_forward(A_FORWARD_839)
    bk839, n839 = backward_walk_legal(A_FORWARD_839)
    d_seq, legal839, breach_i, _, max_d839, min_d839 = census_literal_replay(A_FORWARD_839, 11)
    floor_ok_839 = all(d >= 0 for d in d_seq)
    p(f"\n[GATE G2] 839 chain: residue-legal={res839} (backward reconstructs n0={n839}), "
      f"deficit floor-legal={floor_ok_839} (d goes to {min_d839} -- illegal at EVERY C)")
    g2_ok = res839 and bk839 and (n839 == 839) and (not floor_ok_839)
    p(f"  => corrected search can never accept it at ANY C (floor violation is "
      f"C-independent): {'PASS' if g2_ok else 'FAIL'}")

    # -- GATE 3: genuine census edges, positive AND negative directions
    p(f"\n[GATE G3] genuine census edges (M_edge(3)=9, M_edge(4)=12, M_edge(5)=14):")
    g3_ok = True
    g3_rows = []
    for m, expect in [(9, 3), (12, 4), (14, 5)]:
        D, wit, per_C = D_recon_corrected(m)
        hit = (D == expect)
        g3_ok = g3_ok and hit
        g3_rows.append((m, D, expect, wit))
        p(f"  D_recon({m}) = {D}  (expected {expect}, {'MATCH' if hit else 'MISMATCH'})"
          f"  witness a-seq (forward): {wit}")
    p(f"  Negative directions (length just past the edge must NOT fit at the edge C):")
    for m_over, C_edge in [(10, 3), (13, 4), (15, 5)]:
        wit, stats = exists_at_C(m_over, C_edge)
        infeasible = wit is None
        g3_ok = g3_ok and infeasible
        p(f"  length-{m_over} at C={C_edge}: {'INFEASIBLE (correct)' if infeasible else f'FEASIBLE -- GATE FAIL, witness {wit}'}"
          f"  [{stats['nodes']} nodes]")
    p(f"  GATE G3 overall: {'PASS' if g3_ok else 'FAIL'}")

    if not g3_ok:
        p("\n  Plain 'valid1 at depth m' missed -- probing definitional variants per order...")
        # (variants only explored on failure, per the order)

    # -- GATE 4 on the G3 witnesses
    p(f"\n[GATE G4] exact-integer verification of every G3 witness:")
    g4_ok = True
    for (m, D, expect, wit) in g3_rows:
        if wit is None:
            continue
        v = verify_witness(wit, D)
        g4_ok = g4_ok and v["all_ok"]
        p(f"  m={m}, C={D}: deficit_ok={v['deficit_ok']} residue_ok={v['residue_ok']} "
          f"backward_ok={v['backward_ok']} start_integer={v['start_integer']} "
          f"collatz_replay_ok={v['collatz_replay_ok']}  d_seq={v['d_seq']}")
    p(f"  GATE G4: {'PASS' if g4_ok else 'FAIL'}")

    # -- Cross-check A vs B on the gate rows (positive AND negative)
    p(f"\n[Cross-check] implementation B (layered modular BFS) on gate rows:")
    ab_ok = True
    for m, expect in [(9, 3), (12, 4), (14, 5)]:
        D_b, wit_b, wall = D_recon_corrected_bfs(m)
        match = (D_b == expect)
        ab_ok = ab_ok and match
        v_b = verify_witness(wit_b, D_b) if wit_b else {"all_ok": False}
        p(f"  D_recon_bfs({m}) = {D_b} ({'MATCH' if match else 'MISMATCH'}); "
          f"witness verifies: {v_b['all_ok']}")
    for m_over, C_edge in [(10, 3), (13, 4), (15, 5)]:
        wit_b, stats_b = exists_at_C_bfs(m_over, C_edge)
        infeasible = wit_b is None and not stats_b.get("state_capped")
        ab_ok = ab_ok and infeasible
        p(f"  BFS length-{m_over} at C={C_edge}: "
          f"{'INFEASIBLE (correct)' if infeasible else 'FEASIBLE -- MISMATCH WITH A'}")
    p(f"  A-vs-B agreement on gates: {'PASS' if ab_ok else 'FAIL'}")

    p(f"\nWall: {time.time()-t0:.1f}s, peak RSS: {rss_gb():.3f} GB")
    p(f"\n=== GATES: 0a={ok0a} 0b={ok0b} G1={ok_g1a and ok_g1b} G2={g2_ok} "
      f"G3={g3_ok} G4={g4_ok} AvsB={ab_ok} ===")

    (HERE / "w4_output.log").write_text("\n".join(out_lines) + "\n")
    p(f"Wrote {HERE / 'w4_output.log'}")


if __name__ == "__main__":
    main()
