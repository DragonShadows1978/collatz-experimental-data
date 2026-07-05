#!/usr/bin/env python3
"""
W6W-SPARSE Step 1 -- VALIDATION GATES, v2. Must pass before any new
measurement (Step 2+) is trusted, per the round's house rules.

VALIDATION BASIS (recorded explicitly, per the course correction):
dense re-enumeration is only used where it fits the ~8GB house cap.
A v1 of this script tried a FRESH dense check at C=6, m=17; its worker
reached VmPeak 13.4 GiB (peer-measured) against a 7500 MB cap that v1
only reported, never enforced, and was externally killed. That fresh
dense run is recorded as an honest RSS wall and is NOT retried --
because a GENUINE archived dense death certificate for that exact cell
already exists: w6v_measure/sweep_new_C.log (W6V-MEASURE, 2026-07-04)
C=6: m=16 alive (dt=143.23s), m=17 dead (dt=433.10s), measured_edge=16,
death_confirmed_at_m=17, match=True. Citing the archive is strictly
better evidence than re-running the same dense instrument on the same
machine.

GATE A: the sparse instrument must reproduce Tier-1 M_edge(C), C=1..6
  = 4, 7, 9, 12, 14, 16 (mapping read from automaton.M_edge / the
  W6T-PROV provenance table / w6v README -- NOT assumed from the task
  brief), with:
  - C=1..5: fresh dense-oracle cross-check IN-PROCESS (cheap; the
    heaviest cell, C=5/m=15, is ~86M states, well under the library
    guard and the RSS cap), alive-at-edge AND dead-past-edge.
  - C=6: fresh dense alive-at-16 via the capped subprocess worker
    (observed ~4.9GB in v1's completed first call -- fits the cap);
    dead-at-17 cited from the ARCHIVED dense certificate above.
GATE B: sparse must confirm C=7 alive at m=17 (the dense sweep's own
  partial fact, w6v_measure/sweep_new_C_v2.log m=17 alive=True).

Any mismatch -> STOP, no Step 2/3/4 measurement is taken.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
EMBEDDING = HERE.parent.parent.parent / "embedding"
sys.path.insert(0, str(EMBEDDING))
sys.path.insert(0, str(HERE))

from sparse_instrument import (  # noqa: E402
    sparse_survival, verify_witness_exact, M_edge_formula, verify_lemma3,
)

# Dense oracle -- imported READ-ONLY, never modified, exactly as
# shell_probe.py itself imports it. In-process calls stay at C<=5
# (small state spaces); the single C=6 call goes through the capped
# subprocess worker.
from automaton import M_edge as dense_M_edge_formula, run_heartbeat  # noqa: E402

DENSE_WORKER = HERE / "dense_oracle_worker.py"

# Archived dense certificate for C=6 (W6V-MEASURE sweep_new_C.log,
# quoted verbatim in the docstring above): m=16 alive, m=17 dead.
ARCHIVED_C6 = {"edge": 16, "alive_at_16": True, "dead_at_17": True,
               "source": "shell/underlock/w6v_measure/sweep_new_C.log "
                         "(C=6 summary: measured_edge=16 formula=16 match=True "
                         "death_confirmed_at_m=17)"}


def dense_alive_inprocess(C: int, m: int) -> bool:
    """In-process dense check -- only used at C<=5 where the state
    space is small (<=6*3^15 = 86M states)."""
    modulus = 3 ** m
    live_by_d, _ = run_heartbeat(C, m)
    return any(live_by_d[d][1 % modulus] for d in range(C + 1))


def dense_alive_subprocess(C: int, m: int, rss_cap_mb: float = 7000.0):
    """Capped subprocess dense check (watchdog-enforced VmRSS cap)."""
    proc = subprocess.run(
        [sys.executable, str(DENSE_WORKER), str(C), str(m), str(rss_cap_mb)],
        capture_output=True, text=True, timeout=1800,
    )
    line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "{}"
    try:
        info = json.loads(line)
    except json.JSONDecodeError:
        info = {"error": f"unparseable: {proc.stdout!r} {proc.stderr[-300:]!r}"}
    return info.get("alive"), info


def main():
    out = []

    def p(s=""):
        print(s, flush=True)
        out.append(s)

    t_start = time.time()
    p("=== W6W-SPARSE Step 1: VALIDATION GATES (v2) ===\n")

    lemma3 = verify_lemma3()
    p(f"[Sanity] Lemma 3 credit sequence (independent re-derivation): "
      f"support={lemma3['support_count']} drop={lemma3['drop_count']} "
      f"total={lemma3['total']} matches_expected(22,31)={lemma3['matches_lemma3']}")
    if not lemma3["matches_lemma3"]:
        p("STOP: credit sequence itself is wrong.")
        (HERE / "step1_output.log").write_text("\n".join(out) + "\n")
        sys.exit(1)

    # -----------------------------------------------------------------
    # GATE A
    # -----------------------------------------------------------------
    p("\n[GATE A] Tier-1 M_edge(C) reproduction, C=1..6")
    p(f"{'C':>3} {'formula':>8} {'dense_check':>40} {'sparse_edge':>12} "
      f"{'peak_live':>10} {'match':>6}")
    gate_a_ok = True
    gate_a_rows = []
    for C in range(1, 7):
        formula_edge = M_edge_formula(C)
        assert formula_edge == dense_M_edge_formula(C), "formula impl disagreement"

        # --- dense side ---
        if C <= 5:
            alive_at_edge = dense_alive_inprocess(C, formula_edge)
            alive_past = dense_alive_inprocess(C, formula_edge + 1)
            dense_ok = alive_at_edge and not alive_past
            dense_note = f"fresh in-proc L@{formula_edge}/D@{formula_edge+1}: {dense_ok}"
        else:  # C == 6
            alive16, info16 = dense_alive_subprocess(6, 16, rss_cap_mb=7000.0)
            fresh16_ok = (alive16 is True)
            dense_ok = fresh16_ok and ARCHIVED_C6["dead_at_17"]
            dense_note = (f"fresh L@16:{fresh16_ok} "
                          f"({info16.get('peak_rss_mb', -1):.0f}MB)+archived D@17")
            if info16.get("error"):
                p(f"  [C=6 dense worker note] {info16['error']}")

        # --- sparse side: full sweep to edge+2 ---
        peak_live = 0
        sparse_edge = None
        for m in range(1, formula_edge + 3):
            res = sparse_survival(m, C, rss_cap_mb=7000.0)
            peak_live = max(peak_live, res["peak_live_states"])
            if not res["alive"]:
                sparse_edge = m - 1
                break
        else:
            sparse_edge = -1  # still alive past window -- treated as mismatch

        match = (sparse_edge == formula_edge) and dense_ok
        gate_a_ok = gate_a_ok and match
        gate_a_rows.append((C, formula_edge, sparse_edge, dense_note, peak_live, match))
        p(f"{C:>3} {formula_edge:>8} {dense_note:>40} {sparse_edge:>12} "
          f"{peak_live:>10} {'Y' if match else 'N':>6}")

    p(f"\nGATE A overall: {'PASS' if gate_a_ok else 'FAIL'} (6/6 required)")
    if not gate_a_ok:
        p("STOP per house rules: GATE A failed.")
        for row in gate_a_rows:
            if not row[5]:
                p(f"  MISMATCH detail: {row}")
        (HERE / "step1_output.log").write_text("\n".join(out) + "\n")
        sys.exit(1)

    # -----------------------------------------------------------------
    # GATE B: C=7 alive at m=17 (dense partial fact)
    # -----------------------------------------------------------------
    p("\n[GATE B] C=7 dense-sweep partial fact: alive at m=17 "
      "(w6v_measure/sweep_new_C_v2.log)")
    res17 = sparse_survival(17, 7, rss_cap_mb=7000.0)
    p(f"  sparse_survival(m=17, C=7): alive={res17['alive']} "
      f"peak_live_states={res17['peak_live_states']} "
      f"peak_rss_mb={res17['peak_rss_mb']:.1f} elapsed={res17['elapsed_sec']:.3f}s "
      f"wall={res17['wall']}")
    gate_b_ok = res17["alive"] and res17["wall"] is None

    if gate_b_ok and res17["witness"]:
        v = verify_witness_exact(res17["witness"], 7, res17["letters"])
        p(f"  Witness exact-integer certification: all_ok={v['all_ok']} "
          f"start_integer={v['start_integer']} "
          f"collatz_replay_ok={v['collatz_replay_ok']} "
          f"deficit_range={v['range']} (<= C=7: {v['deficit_ok']})")
        gate_b_ok = gate_b_ok and v["all_ok"]
    p(f"  GATE B: {'PASS' if gate_b_ok else 'FAIL'}")

    if not gate_b_ok:
        p("STOP per house rules: GATE B failed.")
        (HERE / "step1_output.log").write_text("\n".join(out) + "\n")
        sys.exit(1)

    p(f"\nTotal gate wall time: {time.time() - t_start:.1f}s")
    p("\n=== ALL VALIDATION GATES PASSED. Step 2+ is authorized. ===")
    (HERE / "step1_output.log").write_text("\n".join(out) + "\n")
    p(f"Wrote {HERE / 'step1_output.log'}")


if __name__ == "__main__":
    main()
