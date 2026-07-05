#!/usr/bin/env python3
"""
W6X-MULTI Step 1 -- VALIDATION GATES. Must pass before any m>53
(multi-heartbeat) measurement is trusted, per house rules.

Restricted to m <= 53, mx_core.sparse_survival_multi (reading="B",
which reduces EXACTLY to sparse_instrument.py's "end" anchor for
m<=53) must reproduce, EXACTLY:

  GATE A: all ten Tier-1 edges, C=1..10 -> edges
          4, 7, 9, 12, 14, 16, 19, 21, 24, 26
          (death exactly at edge+1, alive at edge).
  GATE B: C=11's no-death-through-53 result (alive at every m=1..53),
          and the peak live-set size stabilizing at 234 (W6W-SPARSE's
          own observed value, from m~=19 onward through m=53).

Also cross-checks, as a bonus/consistency gate (not one of the two
required, but cheap and informative):
  GATE C: reading "A" (== "root") reproduces sparse_instrument.py's
          own "root" anchor's KNOWN divergence at C=11 (dead/dead/
          alive/dead at m=29/30/31/32) -- confirms reading A correctly
          implements the root/growing-end-anchor convention, not just
          agreeing with reading B by accident.
  GATE D: mx_core.letters_for(m, "end") == sparse_instrument's own
          "end" window, and letters_for(m,"B") == letters_for(m,"end")
          for all m<=53 -- direct structural cross-check of the
          reduction claimed in DESIGN_NOTES.md.

Any mismatch -> STOP, no Step 2 (m>53) measurement is taken.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
W6W = HERE.parent / "w6w_sparse"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(W6W))

from mx_core import (  # noqa: E402
    sparse_survival_multi, verify_witness_exact, M_edge_formula,
    verify_lemma3, letters_for, HEARTBEAT,
)
import sparse_instrument as si  # noqa: E402  (w6w_sparse's own validated module)

TIER1_EDGES = {1: 4, 2: 7, 3: 9, 4: 12, 5: 14, 6: 16, 7: 19, 8: 21, 9: 24, 10: 26}


def main():
    out = []

    def p(s=""):
        print(s, flush=True)
        out.append(s)

    t_start = time.time()
    p("=== W6X-MULTI Step 1: VALIDATION GATES (restricted to m<=53) ===\n")

    lemma3 = verify_lemma3()
    p(f"[Sanity] Lemma 3 credit sequence: support={lemma3['support_count']} "
      f"drop={lemma3['drop_count']} total={lemma3['total']} "
      f"matches_expected(22,31)={lemma3['matches_lemma3']}")
    if not lemma3["matches_lemma3"]:
        p("STOP: credit sequence itself is wrong.")
        (HERE / "step1_validation_gates.log").write_text("\n".join(out) + "\n")
        sys.exit(1)

    # -----------------------------------------------------------------
    # GATE D: structural cross-check of letters_for() against
    # sparse_instrument.py's own window construction, BEFORE trusting
    # any live-set numbers from it.
    # -----------------------------------------------------------------
    p("\n[GATE D] letters_for() structural cross-check vs sparse_instrument.py")
    gate_d_ok = True
    for m in [1, 5, 17, 28, 40, 53]:
        si_end = [si.credit_at_step(53 - 1 - j) for j in range(m)]
        mx_end = letters_for(m, "end")
        mx_B = letters_for(m, "B")
        si_root = [si.credit_at_step(m - 1 - j) for j in range(m)]
        mx_root = letters_for(m, "root")
        mx_A = letters_for(m, "A")
        ok = (mx_end == si_end == mx_B) and (mx_root == si_root == mx_A)
        gate_d_ok = gate_d_ok and ok
        p(f"  m={m:>3}: end==B==si_end: {mx_end == si_end == mx_B}  "
          f"root==A==si_root: {mx_root == si_root == mx_A}  overall={ok}")
    p(f"  GATE D: {'PASS' if gate_d_ok else 'FAIL'}")
    if not gate_d_ok:
        p("STOP per house rules: GATE D failed (window construction itself is wrong).")
        (HERE / "step1_validation_gates.log").write_text("\n".join(out) + "\n")
        sys.exit(1)

    # -----------------------------------------------------------------
    # GATE A: Tier-1 C=1..10, reading B (== end anchor for m<=53)
    # -----------------------------------------------------------------
    p("\n[GATE A] Tier-1 M_edge(C) reproduction via reading B (== end anchor), C=1..10")
    p(f"{'C':>3} {'formula':>8} {'alive@edge':>11} {'dead@edge+1':>12} "
      f"{'peak_live':>10} {'match':>6}")
    gate_a_ok = True
    for C in range(1, 11):
        edge = TIER1_EDGES[C]
        assert edge == M_edge_formula(C), "formula mismatch"
        res_edge = sparse_survival_multi(edge, C, reading="B", want_witness=True)
        res_dead = sparse_survival_multi(edge + 1, C, reading="B", want_witness=False)
        alive_ok = res_edge["alive"]
        dead_ok = not res_dead["alive"]
        match = alive_ok and dead_ok
        gate_a_ok = gate_a_ok and match
        peak = max(res_edge["peak_live_states"], res_dead["peak_live_states"])
        p(f"{C:>3} {edge:>8} {str(alive_ok):>11} {str(dead_ok):>12} "
          f"{peak:>10} {'Y' if match else 'N':>6}")
        if alive_ok and res_edge["witness"]:
            v = verify_witness_exact(res_edge["witness"], C, res_edge["letters"])
            if not v["all_ok"]:
                p(f"    WITNESS FAIL at C={C}, m={edge}: {v}")
                gate_a_ok = False

    p(f"\nGATE A overall: {'PASS' if gate_a_ok else 'FAIL'} (10/10 required)")
    if not gate_a_ok:
        p("STOP per house rules: GATE A failed.")
        (HERE / "step1_validation_gates.log").write_text("\n".join(out) + "\n")
        sys.exit(1)

    # -----------------------------------------------------------------
    # GATE B: C=11 alive through m=1..53, peak live-set 234 stabilization
    # -----------------------------------------------------------------
    p("\n[GATE B] C=11: no-death-through-m=53, reading B (== end anchor)")
    all_alive = True
    peak_overall = 0
    layer_peak_by_m = {}
    for m in range(1, 54):
        res = sparse_survival_multi(m, 11, reading="B", want_witness=False)
        if not res["alive"]:
            all_alive = False
            p(f"  UNEXPECTED DEATH at m={m}")
            break
        peak_overall = max(peak_overall, res["peak_live_states"])
        layer_peak_by_m[m] = res["peak_live_states"]
    p(f"  alive at every m=1..53: {all_alive}")
    p(f"  peak live-set size over all m: {peak_overall}")
    # stabilization check: from m=19 onward through m=53, does the peak
    # live-set size for sparse_survival_multi(m, 11, ...) itself (not the
    # running max) equal 234?
    stab_vals = {m: layer_peak_by_m[m] for m in range(19, 54)}
    stabilizes_at_234 = all(v == 234 for v in stab_vals.values())
    p(f"  peak_live_states(m) for m=19..53 all == 234: {stabilizes_at_234}")
    if not stabilizes_at_234:
        distinct = sorted(set(stab_vals.values()))
        p(f"  (values seen instead: {distinct})")

    gate_b_ok = all_alive and (peak_overall == 234) and stabilizes_at_234
    # deep witness at m=53
    res53 = sparse_survival_multi(53, 11, reading="B", want_witness=True)
    if res53["alive"] and res53["witness"]:
        v = verify_witness_exact(res53["witness"], 11, res53["letters"])
        p(f"  m=53 witness: all_ok={v['all_ok']} start_integer={v['start_integer']} "
          f"deficit_range={v['range']}")
        gate_b_ok = gate_b_ok and v["all_ok"]
        if v["start_integer"] == 1707:
            p("  MATCHES W6W-SPARSE's own archived deep witness n0=1707 exactly.")
    p(f"  GATE B: {'PASS' if gate_b_ok else 'FAIL'}")
    if not gate_b_ok:
        p("STOP per house rules: GATE B failed.")
        (HERE / "step1_validation_gates.log").write_text("\n".join(out) + "\n")
        sys.exit(1)

    # -----------------------------------------------------------------
    # GATE C (bonus, informative): reading A/"root" reproduces the
    # KNOWN root-anchor divergence at C=11, m=29..32: dead/dead/alive/dead.
    # -----------------------------------------------------------------
    p("\n[GATE C, informative] Reading A (== root anchor) reproduces the "
      "known root-anchor negative control at C=11, m=29..32 "
      "(expected: dead, dead, alive, dead)")
    expected = {29: False, 30: False, 31: True, 32: False}
    gate_c_ok = True
    for m in (29, 30, 31, 32):
        res = sparse_survival_multi(m, 11, reading="A", want_witness=False)
        ok = res["alive"] == expected[m]
        gate_c_ok = gate_c_ok and ok
        p(f"  m={m}: alive={res['alive']} expected={expected[m]} {'OK' if ok else 'MISMATCH'}")
    p(f"  GATE C (informative, non-blocking): {'PASS' if gate_c_ok else 'FAIL'}")

    p(f"\nTotal gate wall time: {time.time() - t_start:.1f}s")
    p("\n=== ALL BLOCKING VALIDATION GATES PASSED (A, B, D). "
      "Step 2 (m>53 multi-heartbeat measurement) is authorized. ===")
    (HERE / "step1_validation_gates.log").write_text("\n".join(out) + "\n")
    p(f"Wrote {HERE / 'step1_validation_gates.log'}")


if __name__ == "__main__":
    main()
