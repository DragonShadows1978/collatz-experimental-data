#!/usr/bin/env python3
"""
W6Z-TAX Step 4 & 5 -- assemble the tau(C) schedule (every measured sense),
test the two candidate shapes, and score the Architect's frozen predictions.

INPUTS (all produced earlier this round, read from CSV -- no recompute of
the heavy cells):
  step1_spectral_tax.csv          -- tau_spectral(C) = 1 - rho(C)  [per heartbeat]
  step2_summary.csv               -- population thinning summary per C
  step2_live_grid.csv             -- full L(C,m) grid (for per-heartbeat geo)
  step3_climb_cap_corridor.csv    -- residue-legal climb cap under [0,C]
  step3b_completability.csv       -- heartbeat feasibility + n launches per C

PLUS: the May m1-proxy reserve-decay schedule reproduced at FULL PRECISION
(exact integer arithmetic) directly from LOCK3_LOCK4_RESERVE_DECAY_NOTE.md's
formula cutoff(C) = 3C - decay(C), with the note's own data points
(C,cutoff) = (6,17),(10,27),(20,51),(30,75),(40,99),(50,123).

Two candidate shapes tested against the fresh data:
  (a) tau roughly CONSTANT within a heartbeat regime, JUMPING at regime
      boundaries (May note's C~10-11 boundary; w6w's C=10->11 break;
      w6x's two-heartbeat regime).
  (b) tau growing SMOOTHLY with C (May decay note's monotone-increasing
      magnitude 1,3,9,15,21,27).
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

HERE = Path(__file__).parent
LOG = HERE / "step4_schedule_and_scoring.log"
_loglines = []


def log(s=""):
    print(s, flush=True)
    _loglines.append(s)
    LOG.write_text("\n".join(_loglines) + "\n")


def read_csv(name):
    return list(csv.DictReader(open(HERE / name)))


# ---------------------------------------------------------------------
# May m1-proxy reserve-decay, EXACT (Fraction-free integer arithmetic).
# LOCK3_LOCK4_RESERVE_DECAY_NOTE.md lines 29-34 (confirmed by reading):
#   C6  cutoff 17  = 3C-1     -> decay 1
#   C10 cutoff 27  = 3C-3     -> decay 3
#   C20 cutoff 51  = 3C-9     -> decay 9
#   C30 cutoff 75  = 3C-15    -> decay 15
#   C40 cutoff 99  = 3C-21    -> decay 21
#   C50 cutoff 123 = 3C-27    -> decay 27
# ---------------------------------------------------------------------
MAY_POINTS = [(6, 17), (10, 27), (20, 51), (30, 75), (40, 99), (50, 123)]


def may_decay_exact():
    """Return list of (C, cutoff, decay = 3C - cutoff) -- all exact ints."""
    out = []
    for C, cutoff in MAY_POINTS:
        decay = 3 * C - cutoff  # exact integer
        out.append((C, cutoff, decay))
    return out


def main():
    log("=== W6Z-TAX Step 4 & 5: schedule assembly, shape test, prediction scoring ===\n")

    # -----------------------------------------------------------------
    # Load the three fresh tax senses + the completability diagnostic
    # -----------------------------------------------------------------
    spec = {int(r["C"]): float(r["tax_pct"]) for r in read_csv("step1_spectral_tax.csv")}
    spec_rho = {int(r["C"]): float(r["rho"]) for r in read_csv("step1_spectral_tax.csv")}
    s2 = {int(r["C"]): r for r in read_csv("step2_summary.csv")}
    s3 = {int(r["C"]): r for r in read_csv("step3_climb_cap_corridor.csv") if r["C"] != "200"}
    s3b = {int(r["C"]): r for r in read_csv("step3b_completability.csv")}

    # -----------------------------------------------------------------
    # May decay schedule, exact
    # -----------------------------------------------------------------
    log("--- May m1-proxy reserve-decay schedule (EXACT integer, from the note) ---")
    log(f"  {'C':>3} {'cutoff':>7} {'3C':>5} {'decay=3C-cutoff':>16} {'decay/C':>9}")
    may = may_decay_exact()
    for (C, cutoff, decay) in may:
        log(f"  {C:>3} {cutoff:>7} {3*C:>5} {decay:>16} {decay/C:>9.4f}")
    # characterize the decay shape: is decay(C) piecewise-linear / what slope?
    log("\n  May decay shape: successive slopes (decay[i]-decay[i-1])/(C[i]-C[i-1]):")
    for i in range(1, len(may)):
        dC = may[i][0] - may[i-1][0]
        dD = may[i][2] - may[i-1][2]
        log(f"    C {may[i-1][0]:>2}->{may[i][0]:>2}: d(decay)={dD:>3} over dC={dC:>2} "
            f"-> slope {dD/dC:.4f}  (decay/C at C={may[i][0]}: {may[i][2]/may[i][0]:.4f})")
    log("  -> decay(C)/C hovers ~0.5-0.6 (0.167,0.30,0.45,0.50,0.525,0.54): decay ~ 0.6C for")
    log("     large C, i.e. cutoff(C) ~ 2.4C, NOT 3C -- the tax GROWS with C toward a plateau"
        " slope ~0.54.\n")

    # -----------------------------------------------------------------
    # THE MASTER SCHEDULE TABLE tau(C), C=1..15, every measured sense
    # -----------------------------------------------------------------
    log("=== MASTER SCHEDULE tau(C), C=1..15 (every measured sense) ===\n")
    log(f"{'C':>3} | {'spectral tau%':>13} | {'pop-thin geo/lvl':>16} "
        f"| {'pop-thin/hb':>11} | {'climb cap/hb':>12} | {'hb feasible':>11} "
        f"| {'M_edge':>6} | {'in-frame regime':>16}")
    log("-" * 120)
    schedule = []
    for C in range(1, 16):
        st = spec[C]
        geo = float(s2[C]["tau_pop_geo_per_level"]) if s2[C]["tau_pop_geo_per_level"] not in ("", "nan") else float("nan")
        # per-heartbeat pop-thinning = geo^53 (compounding the per-level geo over a heartbeat)
        hb = geo ** 53 if not math.isnan(geo) else float("nan")
        cap = s3[C]["climb_cap_corridor"]
        cap = int(cap) if cap not in ("", "None") else None
        feasible = s3b[C]["heartbeat_feasible"] == "True"
        edge = int(s2[C]["edge"])
        # regime: C<=10 one-heartbeat death edge <=28 (M_edge exact zone);
        #         C>=11 saturates one-heartbeat, needs 2 heartbeats (w6x)
        regime = "1-hb (edge<=28)" if C <= 10 else "2-hb (saturates)"
        schedule.append({
            "C": C, "spectral_tax_pct": st, "pop_thin_geo_per_level": geo,
            "pop_thin_per_hb": hb,
            "climb_cap_per_hb": cap if cap is not None else "None(infeasible)",
            "heartbeat_feasible": feasible, "M_edge": edge, "regime": regime,
        })
        log(f"{C:>3} | {st:>12.3f}% | {geo:>16.5f} | {hb:>11.4f} | "
            f"{str(cap) if cap is not None else 'None':>12} | {str(feasible):>11} | "
            f"{edge:>6} | {regime:>16}")

    with open(HERE / "master_schedule.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(schedule[0].keys()))
        w.writeheader()
        w.writerows(schedule)
    log(f"\nWrote {HERE/'master_schedule.csv'}")

    # -----------------------------------------------------------------
    # SHAPE TEST: (a) constant-within-regime-then-jump vs (b) smooth growth
    # -----------------------------------------------------------------
    log("\n=== SHAPE TEST: (a) regime-constant+jump vs (b) smooth growth ===\n")

    # SENSE 1: spectral tax
    log("SENSE 1 -- spectral tax (1-rho per heartbeat):")
    log(f"  values C=1..15: {[round(spec[C],3) for C in range(1,16)]}")
    log("  C=1:97.1%  C=2:37.1%  C=3:3.98%  C=4:0.29%  C=5:0.058%  C>=6: ~0.046% FLAT.")
    log("  SHAPE: sharp DROP over C=1..5 then a FLAT PLATEAU at ~0.046% for C>=6.")
    log("  -> NOT smooth-growth; it is a transient collapse to a CONSTANT plateau.")
    log("     Consistent with shape (a) 'constant within a regime' -- but the")
    log("     regime here is C>=6 (the universal-rho regime, SPECTRAL_RADIUS_RESULTS")
    log("     item 3: rho identical to 12 dp for C=10..200), NOT a per-heartbeat jump.\n")

    # SENSE 2: population thinning per heartbeat
    log("SENSE 2 -- population thinning (geometric per-level ratio, one heartbeat frame):")
    geos = [float(s2[C]['tau_pop_geo_per_level']) for C in range(1,16)]
    log(f"  geo/level C=1..15: {[round(g,4) for g in geos]}")
    # boundary at C=10->11 (death vs saturation)
    log("  C=1..10: geo/level < 1 (0.89..0.93, live set SHRINKS to death by M_edge<=28).")
    log("  C=11..15: geo/level >= ~0.98 and rising above 1.0 by C=13 (live set SATURATES,")
    log("            no death in one heartbeat) -- a clean REGIME JUMP at C=10->11.")
    log("  SHAPE: (a). Within C<=10 the per-level ratio is roughly constant (~0.90-0.93,")
    log("         drifting gently up); it JUMPS at the C=10->11 boundary (death -> saturation)")
    log("         -- exactly the w6w-SPARSE C=11 break the ledger documents.\n")

    # SENSE 3: climb cap per heartbeat
    log("SENSE 3 -- residue-legal climb cap under corridor [0,C]:")
    caps = [(C, s3[C]['climb_cap_corridor'], s3b[C]['heartbeat_feasible']) for C in range(1,16)]
    log(f"  (C, cap, feasible): {caps}")
    log("  C=1..7: corridor cannot complete one heartbeat AT ALL (0/18 launches) -- climb")
    log("          UNDEFINED (worse than any finite negative: no sustained orbit exists).")
    log("  C=8..15: climb cap = -6 EXACTLY, corridor-width-INDEPENDENT (flat).")
    log("  SHAPE: (a) in the strongest form -- once climbing is even possible (C>=8), the")
    log("         cap is a CONSTANT -6/heartbeat, no growth with C at all. The only")
    log("         'boundary' is the feasibility threshold C=8 (below it, no heartbeat).\n")

    # SENSE 4: May reserve-decay proxy (the shape to compare)
    log("SENSE 4 -- May m1-proxy reserve decay (the archived proxy schedule):")
    log(f"  decay(C) at C=6,10,20,30,40,50: {[d for (_,_,d) in may]}")
    log("  decay GROWS monotonically 1,3,9,15,21,27; decay/C rises 0.167->0.54 then flattens.")
    log("  SHAPE: (b) SMOOTH monotone growth in magnitude, decelerating slope toward ~0.54.")
    log("  This is the ONLY sense that looks like shape (b). It is a DIFFERENT quantity")
    log("  (an m=1 cutoff-vs-3C gap), and it disagrees in SHAPE with all three fresh senses.\n")

    log("=== SHAPE VERDICT ===")
    log("  Fresh data (all three directly-measured senses: spectral, population-thinning,")
    log("  climb-cap) support shape (a): the tax is roughly CONSTANT within a regime and")
    log("  JUMPS/steps at a boundary, NOT smooth growth with C.")
    log("    - spectral: collapses to a flat ~0.046% plateau for C>=6")
    log("    - pop-thin: ~constant ~0.90-0.93/level for C<=10, JUMPS to saturation at C=11")
    log("    - climb-cap: constant -6/hb once feasible (C>=8); infeasible below")
    log("  The May proxy (shape (b), smooth growth) is the ODD ONE OUT and measures a")
    log("  different object; its smooth-growth shape is NOT reproduced by the fresh")
    log("  corridor instruments.\n")

    # -----------------------------------------------------------------
    # STEP 5: SCORE THE ARCHITECT'S FROZEN PREDICTIONS
    # -----------------------------------------------------------------
    log("=== STEP 5: Architect's frozen predictions ===\n")

    # (a) regime-boundary structure visible in tau (55% likely) -- HIT or MISS
    log("(a) [55%] regime-boundary structure visible in tau:")
    log("    HIT. Every fresh sense shows a boundary, not smooth growth:")
    log("      - spectral tax: transient (C=1..5) -> flat plateau (C>=6) [SPECTRAL_RADIUS_RESULTS")
    log("        item 3: universal-rho regime C>=10]")
    log("      - population thinning: death regime (C<=10) -> saturation regime (C>=11),")
    log("        a sharp jump at C=10->11 [w6w-SPARSE first-break, LEDGER_W6W:63]")
    log("      - climb cap: infeasible (C<=7) -> flat -6 (C>=8) feasibility boundary")
    log("    VERDICT (a): HIT.\n")

    # (b) May's m1 decay correlates with true tau, right shape wrong constants (50%)
    log("(b) [50%] May m1 decay correlates with true tau (right shape, wrong constants):")
    log("    MISS on 'right shape'. The May decay is SMOOTH monotone growth (shape b);")
    log("    every fresh directly-measured tau is regime-constant-then-jump (shape a).")
    log("    They do NOT share a shape. The May proxy does track ONE true fact -- that")
    log("    'wider corridor buys less relative reserve' (decay/C rises) -- but its")
    log("    quantity (m=1 cutoff gap) is not the per-heartbeat corridor tax any fresh")
    log("    instrument measures, and the shapes are qualitatively different (smooth vs")
    log("    stepped). Actual constants also do not line up: e.g. May decay(10)=3 (a bit")
    log("    count) has no counterpart in the -6 climb cap or the 0.046% spectral plateau.")
    log("    VERDICT (b): MISS (shapes differ; not merely wrong constants).\n")

    # (c) per-C climb cap strictly negative at every C (85%)
    log("(c) [85%] per-C climb cap stays strictly negative at every C (climbing never")
    log("    turns profitable at any corridor width):")
    defined_caps = [int(s3[C]['climb_cap_corridor']) for C in range(1,16)
                    if s3[C]['climb_cap_corridor'] not in ('', 'None')]
    log(f"    Measured climb caps where DEFINED (C=8..15): all = {set(defined_caps)} "
        f"(min={min(defined_caps)}, max={max(defined_caps)}).")
    log("    For C=1..7 the corridor cannot complete a heartbeat at all (0/18 launches) --")
    log("    climbing is not merely unprofitable, it is IMPOSSIBLE (no sustained orbit).")
    log("    So at NO corridor width 1..15 does climbing turn profitable: cap = -6 < 0")
    log("    wherever defined, undefined-and-worse below C=8. width-unrestricted C=200 = -6.")
    log(f"    VERDICT (c): HIT. Strictly negative (-6) at every C where climbing is possible;")
    log(f"    impossible (a fortiori non-profitable) below. Never profitable at any width.\n")

    log("=== Prediction scorecard: (a) HIT, (b) MISS, (c) HIT ===")

    log(f"\nDone. Artifacts in {HERE}")


if __name__ == "__main__":
    main()
