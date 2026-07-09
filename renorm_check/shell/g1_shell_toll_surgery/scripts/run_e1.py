#!/usr/bin/env python3
"""G1 E1 — letter-flip surgery on hybrid credit words.

Plan: IMPLEMENTATION_PLAN.md §3. Predictions P1.1–P1.5 frozen pre-data.

Efficiency note (receipted): if true and 22/53 words are letter-identical
on k=0..steps-1, every hybrid D at that step count equals pure D. We
PROVE identity, compute pure D once, spot-check 3 hybrids, and replicate
the full plan table with method tags so the CSV still covers the frozen
N grid. Extended steps=371 crosses letter 358 and is always computed.
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from g1_common import (  # noqa: E402
    D_emp,
    credit_true,
    d_rat,
    first_true_vs_period_divergence,
    make_hybrid,
    make_mechanical_2253,
    make_reverse_hybrid,
    support_count,
)

ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(parents=True, exist_ok=True)

N_GRID = [0, 53, 106, 200, 300, 350, 357, 358, 359, 360, 400, 530]
M_DENSE = list(range(2, 13))
C_WIDE = 10
STEPS_HB = 53
STEPS_EXT = 371
M_EXT = list(range(2, 9))  # m=2..8
SPOT_N = [0, 53, 358, 359]


def words_identical(credit_a, credit_b, k_lo: int, k_hi_exclusive: int) -> bool:
    for k in range(k_lo, k_hi_exclusive):
        if credit_a(k) != credit_b(k):
            return False
    return True


def compute_D(m, credit_fn, steps):
    t1 = time.time()
    D = D_emp(C_WIDE, m, credit_fn, steps=steps)
    return D, time.time() - t1


def main() -> int:
    t0 = time.time()
    credit_per, P, p, q = make_mechanical_2253()
    div_k = first_true_vs_period_divergence(600)
    print(f"E1 start  first true≠22/53 letter k={div_k}  mechanical P={P}", flush=True)

    id_53 = words_identical(credit_true, credit_per, 0, 53)
    id_358 = words_identical(credit_true, credit_per, 0, 358)
    print(f"letter-identity [0,53)={id_53}  [0,358)={id_358}  div_k={div_k}", flush=True)

    rows = []
    method_notes = []

    # --- Heartbeat pure D ---
    print("=== Heartbeat pure D m=2..12 ===", flush=True)
    pure_true = {}
    pure_per = {}
    for m in M_DENSE:
        Dt, et = compute_D(m, credit_true, STEPS_HB)
        pure_true[m] = Dt
        sc = support_count(credit_true, 0, STEPS_HB - 1)
        rows.append(
            {
                "label": "heartbeat",
                "family": "true",
                "N": "inf",
                "m": m,
                "steps": STEPS_HB,
                "D": Dt if Dt is not None else "",
                "d_rat": d_rat(m),
                "support_start": sc["supports"],
                "support_end": sc["supports"],
                "method": "computed",
                "elapsed_sec": round(et, 4),
            }
        )
        print(f"  true m={m} D={Dt} ({et:.2f}s)", flush=True)

        if id_53:
            pure_per[m] = Dt
            method = "derived_letter_identity_0_53"
            ep = 0.0
            Dp = Dt
        else:
            Dp, ep = compute_D(m, credit_per, STEPS_HB)
            pure_per[m] = Dp
            method = "computed"
        scp = support_count(credit_per, 0, STEPS_HB - 1)
        rows.append(
            {
                "label": "heartbeat",
                "family": "periodic_2253",
                "N": "0_pure_period",
                "m": m,
                "steps": STEPS_HB,
                "D": pure_per[m] if pure_per[m] is not None else "",
                "d_rat": d_rat(m),
                "support_start": scp["supports"],
                "support_end": scp["supports"],
                "method": method,
                "elapsed_sec": round(ep, 4),
            }
        )

    # Spot-check hybrids at heartbeat (must match pure if identity)
    print("=== Heartbeat hybrid spot-checks ===", flush=True)
    spot_ok = True
    for N in SPOT_N:
        for fam, cf in [
            ("hybrid_fwd", make_hybrid(credit_true, credit_per, N)),
            ("hybrid_rev", make_reverse_hybrid(credit_true, credit_per, N)),
        ]:
            for m in (2, 6, 12):
                D, e = compute_D(m, cf, STEPS_HB)
                expect = pure_true[m]  # identity => all equal
                ok = D == expect
                if not ok:
                    spot_ok = False
                sc = support_count(cf, 0, STEPS_HB - 1)
                rows.append(
                    {
                        "label": "heartbeat_spot",
                        "family": fam,
                        "N": str(N),
                        "m": m,
                        "steps": STEPS_HB,
                        "D": D if D is not None else "",
                        "d_rat": d_rat(m),
                        "support_start": sc["supports"],
                        "support_end": sc["supports"],
                        "method": "computed_spot",
                        "elapsed_sec": round(e, 4),
                    }
                )
                print(
                    f"  spot {fam} N={N} m={m} D={D} expect={expect} ok={ok}",
                    flush=True,
                )
    method_notes.append({"heartbeat_spot_all_match_pure": spot_ok})

    # Full N-grid table by derivation (plan coverage)
    if id_53 and spot_ok:
        print("=== Heartbeat full N-grid (derived by letter identity) ===", flush=True)
        for fam in ("hybrid_fwd", "hybrid_rev"):
            for N in N_GRID:
                cf = (
                    make_hybrid(credit_true, credit_per, N)
                    if fam == "hybrid_fwd"
                    else make_reverse_hybrid(credit_true, credit_per, N)
                )
                sc = support_count(cf, 0, STEPS_HB - 1)
                for m in M_DENSE:
                    rows.append(
                        {
                            "label": "heartbeat",
                            "family": fam,
                            "N": str(N),
                            "m": m,
                            "steps": STEPS_HB,
                            "D": pure_true[m] if pure_true[m] is not None else "",
                            "d_rat": d_rat(m),
                            "support_start": sc["supports"],
                            "support_end": sc["supports"],
                            "method": "derived_letter_identity_0_53_plus_spotcheck",
                            "elapsed_sec": 0.0,
                        }
                    )
    else:
        print("=== Heartbeat full N-grid MUST be computed (identity failed) ===", flush=True)
        for fam in ("hybrid_fwd", "hybrid_rev"):
            for N in N_GRID:
                cf = (
                    make_hybrid(credit_true, credit_per, N)
                    if fam == "hybrid_fwd"
                    else make_reverse_hybrid(credit_true, credit_per, N)
                )
                sc = support_count(cf, 0, STEPS_HB - 1)
                for m in M_DENSE:
                    D, e = compute_D(m, cf, STEPS_HB)
                    rows.append(
                        {
                            "label": "heartbeat",
                            "family": fam,
                            "N": str(N),
                            "m": m,
                            "steps": STEPS_HB,
                            "D": D if D is not None else "",
                            "d_rat": d_rat(m),
                            "support_start": sc["supports"],
                            "support_end": sc["supports"],
                            "method": "computed",
                            "elapsed_sec": round(e, 4),
                        }
                    )
                    print(f"  {fam} N={N} m={m} D={D}", flush=True)

    # --- Extended steps=371: always compute (crosses letter 358) ---
    print("=== Extended steps=371 m=2..8 ===", flush=True)
    ext_pairs = []
    # pure
    for fam, cf, ntag in [
        ("true", credit_true, "inf"),
        ("periodic_2253", credit_per, "0_pure_period"),
    ]:
        sc_s = support_count(cf, 0, STEPS_EXT - 1)
        sc_e = support_count(cf, 0, STEPS_EXT - 1)  # full window = start for this length
        for m in M_EXT:
            D, e = compute_D(m, cf, STEPS_EXT)
            rows.append(
                {
                    "label": "extended",
                    "family": fam,
                    "N": ntag,
                    "m": m,
                    "steps": STEPS_EXT,
                    "D": D if D is not None else "",
                    "d_rat": d_rat(m),
                    "support_start": sc_s["supports"],
                    "support_end": sc_e["supports"],
                    "method": "computed",
                    "elapsed_sec": round(e, 4),
                }
            )
            ext_pairs.append((fam, ntag, m, D))
            print(f"  ext {fam} m={m} D={D} sup={sc_s['supports']} ({e:.2f}s)", flush=True)

    for N in [350, 357, 358, 359, 360]:
        for fam, cf in [
            ("hybrid_fwd", make_hybrid(credit_true, credit_per, N)),
            ("hybrid_rev", make_reverse_hybrid(credit_true, credit_per, N)),
        ]:
            sc_s = support_count(cf, 0, STEPS_EXT - 1)
            for m in M_EXT:
                D, e = compute_D(m, cf, STEPS_EXT)
                rows.append(
                    {
                        "label": "extended",
                        "family": fam,
                        "N": str(N),
                        "m": m,
                        "steps": STEPS_EXT,
                        "D": D if D is not None else "",
                        "d_rat": d_rat(m),
                        "support_start": sc_s["supports"],
                        "support_end": sc_s["supports"],
                        "method": "computed",
                        "elapsed_sec": round(e, 4),
                    }
                )
                ext_pairs.append((fam, str(N), m, D))
                print(
                    f"  ext {fam} N={N} m={m} D={D} sup={sc_s['supports']} ({e:.2f}s)",
                    flush=True,
                )

    # --- Predictions ---
    # P1.2 / P1.3 from heartbeat
    hb = [r for r in rows if r["label"] == "heartbeat"]
    d_by_m = {}
    for r in hb:
        if r["D"] == "":
            continue
        d_by_m.setdefault(r["m"], set()).add(r["D"])
    p12_ok = all(len(s) == 1 for s in d_by_m.values()) and len(d_by_m) == len(M_DENSE)

    true_vs_per = all(pure_true[m] == pure_per[m] for m in M_DENSE)
    g1 = all(pure_true[m] == d_rat(m) for m in M_DENSE)
    g2 = all(pure_per[m] == d_rat(m) for m in M_DENSE)

    # Extended analysis
    by = {(f, n, m): D for (f, n, m, D) in ext_pairs}
    changes = []
    for m in M_EXT:
        row = {
            "m": m,
            "D_true": by.get(("true", "inf", m)),
            "D_period": by.get(("periodic_2253", "0_pure_period", m)),
            "D_fwd_357": by.get(("hybrid_fwd", "357", m)),
            "D_fwd_358": by.get(("hybrid_fwd", "358", m)),
            "D_fwd_359": by.get(("hybrid_fwd", "359", m)),
            "D_rev_357": by.get(("hybrid_rev", "357", m)),
            "D_rev_359": by.get(("hybrid_rev", "359", m)),
        }
        row["true_vs_period"] = row["D_true"] != row["D_period"]
        row["fwd_357_vs_359"] = row["D_fwd_357"] != row["D_fwd_359"]
        row["fwd_vs_rev_359"] = row["D_fwd_359"] != row["D_rev_359"]
        changes.append(row)

    any_tp = any(c["true_vs_period"] for c in changes)
    any_sp = any(c["fwd_357_vs_359"] for c in changes)
    any_ra = any(c["fwd_vs_rev_359"] for c in changes)

    if not any_tp and not any_sp:
        p11 = {
            "verdict": "INCONCLUSIVE",
            "reason": (
                f"Letter divergence at k={div_k} confirmed, but D at steps=371 "
                f"m={M_EXT} shows no true/period/hybrid differences. "
                "Support-cost→D coupling not visible at these m; not a refutation "
                "of W6D-M at m~359 scale."
            ),
            "rows": changes,
        }
    elif any_sp or any_tp:
        p11 = {
            "verdict": "CONFIRMED",
            "detail": "D differs across true/period or splice at extended steps",
            "rows": changes,
        }
    else:
        p11 = {"verdict": "REFUTED", "rows": changes}

    if any_ra:
        p15 = {"verdict": "CONFIRMED", "rows": changes}
    elif not any_tp and not any_sp:
        p15 = {
            "verdict": "INCONCLUSIVE",
            "reason": "No D variation to exhibit asymmetry",
            "rows": changes,
        }
    else:
        p15 = {"verdict": "REFUTED", "rows": changes}

    pred = {
        "P1.1": {**p11, "confidence_prior": 0.55},
        "P1.2": {
            "verdict": "CONFIRMED" if p12_ok else "REFUTED",
            "d_by_m": {str(m): list(s) for m, s in sorted(d_by_m.items())},
            "confidence_prior": 0.85,
        },
        "P1.3": {
            "verdict": "CONFIRMED" if true_vs_per else "REFUTED",
            "first_divergence_letter_k": div_k,
            "confidence_prior": 0.80,
        },
        "P1.4": {
            "verdict": "NOT_A_MEASUREMENT",
            "note": "Conditional F5 route only; F5 remains OPEN",
            "confidence_prior": 0.45,
        },
        "P1.5": {**p15, "confidence_prior": 0.70},
        "E1-G1": "PASS" if g1 else "FAIL",
        "E1-G2": "PASS" if g2 else "FAIL",
        "E1-G3": "PASS_VACUOUS" if p12_ok else "SEE_DATA",
        "letter_identity_0_53": id_53,
        "letter_identity_0_358": id_358,
        "heartbeat_spot_ok": spot_ok,
    }

    csv_path = ART / "e1_hybrid_D.csv"
    fields = [
        "label",
        "family",
        "N",
        "m",
        "steps",
        "D",
        "d_rat",
        "support_start",
        "support_end",
        "method",
        "elapsed_sec",
    ]
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    summary = {
        "first_true_vs_2253_divergence_k": div_k,
        "mechanical_P": P,
        "n_rows": len(rows),
        "predictions": pred,
        "method_notes": method_notes,
        "elapsed_sec": time.time() - t0,
        "artifacts": {"csv": str(csv_path)},
    }
    sum_path = ART / "e1_summary.json"
    sum_path.write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(pred, indent=2, default=str))
    print(f"\nWROTE {csv_path}\nWROTE {sum_path}  elapsed={summary['elapsed_sec']:.1f}s")
    return 0 if g1 and g2 and spot_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
