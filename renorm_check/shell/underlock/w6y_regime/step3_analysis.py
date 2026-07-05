#!/usr/bin/env python3
"""
W6Y-REGIME -- Step 3: analysis.

Reads step2_measurement_full.json (the C=16..26 edge sweep) and:
  (a) builds the extended (C, edge, regime) table with residuals vs
      law1/law2/law3
  (b) tests whether a sharper 2-heartbeat constant floor((106C+b)/22)
      fixes the residuals for the C where 2-heartbeat still applies
  (c) tests the regime-transition rule: graduate from h-heartbeat to
      (h+1)-heartbeat when law_h(C) would exceed h*53 - Delta, Delta
      measured at the known 1->2 transition (C=10->11)
  (d) reports the fit quality and transition point(s) found
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).parent


def law1(C):
    return (53 * (C + 1)) // 22


def law2(C):
    return (106 * (C + 1)) // 22


def law3(C):
    return (159 * (C + 1)) // 22


def main():
    data = json.loads((HERE / "step2_measurement_full.json").read_text())
    results = data["results"]

    print("=== Extended (C, edge, regime) table ===")
    print(f"{'C':>3} {'edge':>5} {'law1':>5} {'law2':>5} {'law3':>5} "
          f"{'res_l2':>7} {'res_l3':>7} {'peak_live':>12} {'monotone':>9} {'wall':>6}")
    rows = []
    for r in results:
        C = r["C"]
        edge = r["edge"]
        res2 = (edge - law2(C)) if edge is not None else None
        res3 = (edge - law3(C)) if edge is not None else None
        rows.append((C, edge, law1(C), law2(C), law3(C), res2, res3, r["peak_live"], r["monotone"], r["wall"]))
        print(f"{C:>3} {edge!s:>5} {law1(C):>5} {law2(C):>5} {law3(C):>5} "
              f"{res2!s:>7} {res3!s:>7} {r['peak_live']:>12} {r['monotone']!s:>9} {r['wall']!s:>6}")

    print("\n=== Fit attempt: sharper 2-heartbeat law floor((106C+b)/22) ===")
    best_b, best_mae = None, None
    for b in range(-30, 60):
        residuals = []
        for C, edge, *_ in rows:
            if edge is None:
                continue
            pred = (106 * C + b) // 22
            residuals.append(edge - pred)
        mae = sum(abs(x) for x in residuals) / len(residuals) if residuals else None
        if best_mae is None or (mae is not None and mae < best_mae):
            best_mae, best_b = mae, b
    print(f"best b={best_b}, MAE={best_mae:.3f} over all swept C (searching -30..60)")
    print("(if best_mae is still large, no single b in the (106C+b)/22 family fits -- "
          "the 2-heartbeat form itself is likely wrong for this C range, not just the constant)")

    print("\n=== Regime transition rule test ===")
    print("Rule (task 3c): graduate from h-heartbeat to (h+1)-heartbeat when")
    print("law_h(C) would exceed h*53 - Delta, Delta measured at the known 1->2 transition.")
    print(f"Measured Delta at C=11 (first regime-2 edge, law1={law1(11)}): 53-{law1(11)}={53-law1(11)}")
    print("(the transition C=10->11 is the boundary; law1(11)=28, 53-28=25 -- this is the")
    print(" Delta approx 25 the mission brief references)")

    print("\nApplying the SAME rule to predict the 2->3 transition (using Delta=25, h=2, window=106):")
    for C in range(16, 27):
        l2 = law2(C)
        thresh = 2 * 53 - 25  # 81
        would_graduate = l2 > thresh
        print(f"  C={C}: law2={l2} threshold(2*53-25)={thresh} would_graduate={would_graduate}")

    print("\n=== Smooth-drift diagnostic: edge/(C+1) ratio and closest n-heartbeat law ===")
    print("(a clean heartbeat-quantized law would sit at n*53/22 = n*2.409 and JUMP")
    print(" discretely between n values; a continuous climb through the gaps means the")
    print(" quantization is NOT exact in the transition zone)")
    print(f"{'C':>3} {'edge':>5} {'edge/(C+1)':>11} {'closest_n':>10} {'law_n':>6} {'|resid|':>8}")
    # include the W6X-MULTI C=11..15 edges for the full-picture trend
    known_1115 = {11: 57, 12: 63, 13: 68, 14: 71, 15: 79}
    all_edges = dict(known_1115)
    for C, edge, *_ in rows:
        if edge is not None:
            all_edges[C] = edge
    for C in sorted(all_edges):
        e = all_edges[C]
        laws = {n: (n * 53 * (C + 1)) // 22 for n in range(1, 6)}
        best_n = min(laws, key=lambda n: abs(laws[n] - e))
        ratio = e / (C + 1)
        print(f"{C:>3} {e:>5} {ratio:>11.3f} {best_n:>10} {laws[best_n]:>6} {abs(laws[best_n]-e):>8}")

    print("\nn=2 ratio target = 106/22 = {:.3f}; n=3 ratio target = 159/22 = {:.3f}".format(
        106/22, 159/22))
    print("If edge/(C+1) climbs smoothly THROUGH the n=2 target and toward n=3 rather than")
    print("staying pinned at 106/22 then jumping to 159/22, the heartbeat-quantized law is")
    print("REFUTED as an exact law in this range (it holds only near the CENTER of each")
    print("regime, breaking down in the transition zones between consecutive n).")

    print("\n=== Best-fit closest-n MAE per regime band ===")
    for n in [2, 3]:
        band = [(C, e) for C, e in all_edges.items()
                if min(range(1, 6), key=lambda k: abs((k*53*(C+1))//22 - e)) == n]
        if band:
            mae = sum(abs((n*53*(C+1))//22 - e) for C, e in band) / len(band)
            Cs = sorted(C for C, _ in band)
            print(f"  n={n}: C in {Cs}, closest-n MAE={mae:.2f}")


if __name__ == "__main__":
    main()
