#!/usr/bin/env python3
"""
W6Z-TAX Steps 2 & 3 -- the tax schedule tau(C) at every level C=1..15,
in every sense the existing instruments support.

REUSES w6w_sparse/sparse_instrument.py's VALIDATED backward layered-BFS
(imported, not reinvented): parity_forced, backward_pred_mod, the (R,u,v)
live-set update with the u<=C / v<=C / u+v<=C corridor legality. The
per-step transition math is already gated exhaustively (W6W-SPARSE gates
A/B, 10 Tier-1 edges). This round adds NO new transition rule; it only
reads out quantities the prior rounds computed but did not tabulate as a
tax-per-level. (Cross-referenced against w6x_multi/step2_measurement.py's
final_live_states readout -- same quantity, one-heartbeat scope here.)

Three tax senses, all end-anchored one-heartbeat frame (the ONLY frame
that reproduces every genuinely measured cell, per W6W-SPARSE / W6U-RECON):

  Step 2 -- POPULATION THINNING.
    Re-run the sparse instrument and record the FINAL-LAYER live-set size
    L(C, m) = number of distinct (R,u,v) states surviving all m residue
    constraints (== the sparse_survival frontier at the last layer; this
    is |live(m)|, the surviving-corridor-state count at precision m).
    Per-level thinning ratio:
        tau_pop(C, m) = L(C, m+1) / L(C, m)        (continuous ratio, float)
    Per-heartbeat thinning (geometric-mean ratio across the alive block).
    NOTE on data detail: the archived w6w/w6x JSON carry only the peak_live
    COUNT per (C,m) (verified: step2_4_climb_full.json rows have no
    per-element deficit detail). So the deficit-DISTRIBUTION drift within
    the live set is NOT recoverable from the archives -- it must be
    re-measured. This script re-runs the instrument and DOES dump the live
    (u,v) deficit-state multiset per (C,m).

  Step 3 -- PER-LEVEL / PER-HEARTBEAT CLIMB CAP under corridor [0,C].
    B1.2-style residue-legal max climb DP (mirrors b1/b2_residue_legal_max_climb
    logic: maximize Sigma(c-a) over residue-legal exponent chains), but with
    the deficit corridor RESTRICTED to [0,C] (the new axis this round adds:
    B1.2 measured the width-unrestricted climb=-6; here we ask how the [0,C]
    bound changes it).

Validation gate (REQUIRED before trusting any new cell): reproduce published
cells -- the ten Tier-1 M_edge values C=1..10 = 4,7,9,12,14,16,19,21,24,26
(w6w LEDGER) from THIS script's live-set walk, and B1.2's climb = -6.
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
W6W = HERE.parent / "w6w_sparse"
sys.path.insert(0, str(W6W))

from sparse_instrument import (  # noqa: E402  (validated instrument)
    credit_at_step, parity_forced, backward_pred_mod, M_edge_formula, HEARTBEAT,
)

LOG = HERE / "step2_3_tax_schedule.log"
_loglines = []


def log(s=""):
    print(s, flush=True)
    _loglines.append(s)
    LOG.write_text("\n".join(_loglines) + "\n")


def survival_final(m: int, C: int, steps: int = HEARTBEAT):
    """Backward layered BFS, end-anchored last-m-letters window. Returns
    (final_live |live(m)|, peak_live, uv_hist of the FINAL live set).
    Exact ints; transition math identical to sparse_instrument.sparse_survival."""
    letters = [credit_at_step(steps - 1 - j) for j in range(m)]
    pow3 = [3 ** i for i in range(m + 1)]
    frontier = {(1 % pow3[m], 0, 0): None}
    peak = 1
    for j in range(m):
        c = letters[j]
        mod_next = pow3[m - j - 1] if (m - j - 1) >= 0 else 1
        nxt = {}
        for (R, u, v), _p in frontier.items():
            p = parity_forced(R % 3)
            if p is None:
                continue
            a_min = 2 if p == 0 else 1
            a_hi = c + C - v
            a = a_min
            while a <= a_hi:
                s_rel = c - a
                new_min_rel = min(-u, s_rel)
                new_max_rel = max(v, s_rel)
                if new_max_rel - new_min_rel <= C:
                    u2 = s_rel - new_min_rel
                    v2 = new_max_rel - s_rel
                    R2 = backward_pred_mod(R, a, mod_next)
                    key2 = (R2, u2, v2)
                    if key2 not in nxt:
                        nxt[key2] = ((R, u, v), a)
                a += 2
        frontier = nxt
        peak = max(peak, len(frontier))
        if not frontier:
            break
    final_live = len(frontier)
    uv_hist = {}
    for (R, u, v) in frontier:
        uv_hist[(u, v)] = uv_hist.get((u, v), 0) + 1
    return final_live, peak, uv_hist


def climb_cap_corridor(C: int, K: int = 1, steps: int = HEARTBEAT):
    """Max residue-legal Sigma(c-a) over one 53-step heartbeat, deficit
    kept in [0,C] every step, from the best starting (d0, rho0). FORWARD
    DP. Parity forced by rho mod 3 (F6): rho==1 mod3 -> a even (a_min=2),
    rho==2 mod3 -> a odd (a_min=1), rho==0 mod3 dead. rho evolves
    rho' = (3*rho+1) * inv(2^a) mod 3^K. Deficit d_{k+1}=d_k+c_k-a_k in [0,C].
    State (d, rho mod 3^K); value = best running climb. Exact ints."""
    mod = 3 ** K
    creds = [credit_at_step(k) for k in range(steps)]

    def inv2a(a):
        return pow(pow(2, a, mod), -1, mod)

    cur = {}
    for d0 in range(C + 1):
        for rho0 in range(mod):
            if rho0 % 3 == 0:
                continue
            cur[(d0, rho0)] = 0
    for k in range(steps):
        c = creds[k]
        nxt = {}
        for (d, rho), val in cur.items():
            cls = rho % 3
            if cls == 0:
                continue
            a_min = 2 if cls == 1 else 1
            a = a_min
            while a <= d + c:
                d2 = d + c - a
                if 0 <= d2 <= C:
                    rho2 = ((3 * rho + 1) * inv2a(a)) % mod
                    nv = val + (c - a)
                    key = (d2, rho2)
                    if key not in nxt or nv > nxt[key]:
                        nxt[key] = nv
                a += 2
        cur = nxt
        if not cur:
            break
    return max(cur.values()) if cur else None


def main():
    t0 = time.time()
    log("=== W6Z-TAX Steps 2 & 3: the tax schedule tau(C), C=1..15 ===\n")

    log("--- Validation gate 1: reproduce Tier-1 M_edge C=1..10 from this "
        "script's own live-set walk (edge = last m with L>0) ---")
    published_edges = {1: 4, 2: 7, 3: 9, 4: 12, 5: 14, 6: 16,
                       7: 19, 8: 21, 9: 24, 10: 26}
    edge_ok = True
    for C in range(1, 11):
        last_alive = 0
        for m in range(1, 40):
            fl, _pk, _h = survival_final(m, C)
            if fl > 0:
                last_alive = m
            else:
                break
        match = (last_alive == published_edges[C])
        edge_ok &= match
        log(f"  C={C:>2}: measured edge={last_alive:>3}  published={published_edges[C]:>3}  "
            f"formula={M_edge_formula(C):>3}  {'OK' if match else '*** MISMATCH ***'}")
    log(f"  Gate 1: {'PASS' if edge_ok else 'FAIL'} (10/10 edges)\n")
    if not edge_ok:
        raise SystemExit("Gate 1 FAILED -- halting.")

    log("--- Validation gate 2: reproduce B1.2 width-unrestricted climb = -6 "
        "per heartbeat, K=1 vs K=3 agree ---")
    climb_K1 = climb_cap_corridor(C=200, K=1)
    climb_K3 = climb_cap_corridor(C=200, K=3)
    log(f"  width-unrestricted (C=200): K=1 -> {climb_K1}, K=3 -> {climb_K3}")
    log(f"  B1.2 published (b2_run_output.log:12): -6 per 53-letter window")
    b12_ok = (climb_K1 == -6)
    log(f"  Gate 2: {'PASS' if b12_ok else 'FAIL'}  "
        f"K-independence: {'OK' if climb_K1 == climb_K3 else 'DIFFERS'}\n")

    log("=== STEP 2: population thinning L(C,m) = |live(m)| (final-layer live set) ===")
    M_MAX = 53
    live = {}
    peak = {}
    uv_hists = {}
    for C in range(1, 16):
        for m in range(1, M_MAX + 1):
            fl, pk, h = survival_final(m, C)
            live[(C, m)] = fl
            peak[(C, m)] = pk
            uv_hists[(C, m)] = h

    try:
        arch = json.load(open(W6W / "step2_4_climb_full.json"))
        arch_peak = {}
        for rec in arch:
            for row in rec["rows"]:
                arch_peak[(row["C"], row["m"])] = row["peak_live_states"]
        mism = checked = 0
        for (C, m), pk in peak.items():
            if (C, m) in arch_peak:
                checked += 1
                if pk != arch_peak[(C, m)]:
                    mism += 1
        log(f"\n  cross-check peak_live vs archived w6w JSON: {checked} cells, "
            f"{mism} mismatches ({'PASS' if mism == 0 else 'FAIL'})")
    except Exception as e:
        log(f"\n  (archived cross-check skipped: {e})")

    log("\n  L(C,m) and per-level ratio tau_pop(C,m)=L(m+1)/L(m):")
    log(f"  {'C':>3} {'edge':>5} {'L(1)':>6} {'L(edge)':>8} {'L(53)':>7} "
        f"{'mean tau_pop pre-edge':>22} {'tau_pop geo/level':>18}")
    step2_rows = []
    for C in range(1, 16):
        edge = max((m for m in range(1, M_MAX + 1) if live[(C, m)] > 0), default=0)
        ratios = []
        for m in range(1, M_MAX):
            a, b = live[(C, m)], live[(C, m + 1)]
            if a > 0:
                ratios.append((m, b / a))
        pre = [r for (m, r) in ratios if m < min(edge, M_MAX)]
        mean_pre = sum(pre) / len(pre) if pre else float("nan")
        top = min(edge, M_MAX)
        if top >= 2 and live[(C, 1)] > 0 and live[(C, top)] > 0:
            geo = (live[(C, top)] / live[(C, 1)]) ** (1.0 / (top - 1))
        else:
            geo = float("nan")
        log(f"  {C:>3} {edge:>5} {live[(C,1)]:>6} {live[(C,edge)] if edge else 0:>8} "
            f"{live[(C,53)]:>7} {mean_pre:>22.5f} {geo:>18.5f}")
        step2_rows.append({
            "C": C, "edge": edge, "L_1": live[(C, 1)],
            "L_edge": live[(C, edge)] if edge else 0, "L_53": live[(C, 53)],
            "mean_tau_pop_pre_edge": mean_pre, "tau_pop_geo_per_level": geo,
        })

    log("\n=== STEP 3: residue-legal climb cap per heartbeat, deficit in [0,C] ===")
    log(f"  {'C':>3} {'climb_cap(C) [0,C]':>18} {'per-letter %':>13} "
        f"{'width-unrestricted':>18}")
    step3_rows = []
    for C in range(1, 16):
        cap = climb_cap_corridor(C, K=1)
        per_letter = (100.0 * cap / HEARTBEAT) if cap is not None else float("nan")
        log(f"  {C:>3} {str(cap):>18} {per_letter:>12.3f}% {'-6 (C=inf)':>18}")
        step3_rows.append({"C": C, "climb_cap_corridor": cap,
                           "per_letter_pct": per_letter})

    with open(HERE / "step2_live_grid.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["C", "m", "L_final_live", "peak_live"])
        for C in range(1, 16):
            for m in range(1, M_MAX + 1):
                w.writerow([C, m, live[(C, m)], peak[(C, m)]])
    log(f"\nWrote {HERE/'step2_live_grid.csv'}")

    with open(HERE / "step2_thinning_ratios.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["C", "m", "L_m", "L_m_plus_1", "tau_pop_ratio"])
        for C in range(1, 16):
            for m in range(1, M_MAX):
                a, b = live[(C, m)], live[(C, m + 1)]
                r = (b / a) if a > 0 else ""
                w.writerow([C, m, a, b, r])
    log(f"Wrote {HERE/'step2_thinning_ratios.csv'}")

    with open(HERE / "step2_deficit_drift.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["C", "m", "u", "v", "count"])
        for C in range(1, 16):
            edge = max((mm for mm in range(1, 54) if live[(C, mm)] > 0), default=1)
            for m in sorted(set([1, 5, 10, 20, min(53, edge)])):
                for (u, v), cnt in sorted(uv_hists[(C, m)].items()):
                    w.writerow([C, m, u, v, cnt])
    log(f"Wrote {HERE/'step2_deficit_drift.csv'}")

    with open(HERE / "step2_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(step2_rows[0].keys()))
        w.writeheader()
        w.writerows(step2_rows)
    with open(HERE / "step3_climb_cap.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(step3_rows[0].keys()))
        w.writeheader()
        w.writerows(step3_rows)
    log(f"Wrote {HERE/'step2_summary.csv'}, {HERE/'step3_climb_cap.csv'}")

    log(f"\nTotal wall: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
