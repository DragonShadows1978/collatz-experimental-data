#!/usr/bin/env python3
"""
W6W-SPARSE Step 4c -- anchor-robustness probes for the C=11 verdict.

(a) Deeper end-anchors: the instrument's default window is the last m
    letters of the 53-step heartbeat. Because the credit word is
    aperiodic (Sturmian), anchoring at 106 or 159 steps selects a
    DIFFERENT m-letter window. shell_probe.py P4 established (dense,
    C=3,4) that the death edge is steps-invariant; here we check the
    C=11 SURVIVAL-past-28 verdict at anchors 106 and 159. Survival at
    all three anchors means the break is not an artifact of one
    window's letters.
    Gate first: at anchors 106/159 the C=3 and C=4 edges must still be
    9 and 12 (P4's own dense steps-invariance fact, reproduced sparse).

(b) Root-anchored negative control: W6U-RECON established (6/6 gates)
    that the ROOT-anchored window FAILS the genuine C<=5 edges (it is
    not the corridor's measurement frame); its C=11 row first fits
    m=29 at C=12 (w5_final_merged_table.csv: D_recon_root_variant=12
    at m=29). Reproducing "root-anchored DIES at m=29, C=11" with this
    round's own engine confirms the instrument distinguishes the two
    frames the same way W6U's engines did.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from sparse_instrument import sparse_survival, verify_witness_exact  # noqa: E402


def main():
    out = []

    def p(s=""):
        print(s, flush=True)
        out.append(s)

    p("=== W6W-SPARSE Step 4c: anchor robustness ===\n")

    # (a) gate: steps-invariance of known edges at deeper anchors
    p("[4c-a gate] C=3 edge=9, C=4 edge=12 must hold at anchors 106, 159:")
    gate_ok = True
    for steps in (106, 159):
        for C, edge in [(3, 9), (4, 12)]:
            r_edge = sparse_survival(edge, C, steps=steps)
            r_past = sparse_survival(edge + 1, C, steps=steps)
            ok = r_edge["alive"] and not r_past["alive"]
            gate_ok = gate_ok and ok
            p(f"  anchor={steps} C={C}: alive@{edge}={r_edge['alive']} "
              f"dead@{edge + 1}={not r_past['alive']} -> {'OK' if ok else 'FAIL'}")
    p(f"  4c-a gate: {'PASS' if gate_ok else 'FAIL'}")
    if not gate_ok:
        p("  STOP: steps-invariance gate failed; deeper-anchor probe untrusted.")
        (HERE / "step4c_anchor_robustness.log").write_text("\n".join(out) + "\n")
        sys.exit(1)

    # (a) the C=11 verdict at deeper anchors
    p("\n[4c-a] C=11 survival at deeper end-anchors:")
    for steps in (53, 106, 159):
        row = []
        for m in (28, 29, 30, 31, 32, 40, 53):
            res = sparse_survival(m, 11, steps=steps)
            row.append(f"m={m}:{'L' if res['alive'] else 'D'}")
        p(f"  anchor={steps}: {'  '.join(row)}")

    # deep witness verification at anchor 106, m=53
    res = sparse_survival(53, 11, steps=106)
    if res["alive"] and res["witness"]:
        v = verify_witness_exact(res["witness"], 11, res["letters"])
        p(f"  anchor=106 m=53 witness: all_ok={v['all_ok']} n0={v['start_integer']} "
          f"range={v['range']}")

    # (b) root-anchored negative control
    p("\n[4c-b] Root-anchored negative control at C=11 (expected: DIES at m=29 "
      "per w6u_recon w5 D_recon_root_variant=12):")
    for m in (28, 29, 30, 31, 32):
        res = sparse_survival(m, 11, anchor="root")
        p(f"  root-anchored m={m}: {'ALIVE' if res['alive'] else 'DEAD'}")
    r29 = sparse_survival(29, 11, anchor="root")["alive"]
    e29 = sparse_survival(29, 11, anchor="end")["alive"]
    p(f"  Frame separation at m=29, C=11: end-anchored={'ALIVE' if e29 else 'DEAD'}, "
      f"root-anchored={'ALIVE' if r29 else 'DEAD'}")

    (HERE / "step4c_anchor_robustness.log").write_text("\n".join(out) + "\n")
    p(f"\nWrote {HERE / 'step4c_anchor_robustness.log'}")


if __name__ == "__main__":
    main()
