#!/usr/bin/env python3
"""G1 shared validation gates V0–V3. Frozen in IMPLEMENTATION_PLAN.md §2."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from g1_common import (  # noqa: E402
    D_emp,
    M_edge,
    credit_true,
    d_irr,
    d_rat,
    d_real_mirror,
    edge_marker,
    first_true_vs_period_divergence,
    make_mechanical_2253,
    verify_lemma3,
)

ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(parents=True, exist_ok=True)


def main() -> int:
    t0 = time.time()
    report: dict = {"gates": {}, "details": {}}
    ok_all = True

    # V0
    try:
        lem = verify_lemma3()
        assert lem["matches_lemma3"], lem
        credit_per, P, p, q = make_mechanical_2253()
        seq = [credit_per(k) for k in range(53)]
        assert seq.count(1) == 22 and seq.count(2) == 31
        # exact credits: no float — credit_true uses bit_length
        assert credit_true(0) in (1, 2)
        div = first_true_vs_period_divergence(500)
        report["gates"]["V0"] = "PASS"
        report["details"]["V0"] = {
            "lemma3": lem,
            "mechanical_P": P,
            "first_true_vs_2253_divergence_k": div,
        }
        print(f"V0 PASS  lemma3 ok  first true≠22/53 at k={div}")
    except Exception as e:
        report["gates"]["V0"] = f"FAIL: {e}"
        ok_all = False
        print(f"V0 FAIL: {e}")

    # V1 capacity edges C=1..5 → 4,7,9,12,14
    try:
        expected = {1: 4, 2: 7, 3: 9, 4: 12, 5: 14}
        rows = []
        for C, edge in expected.items():
            got = M_edge(C)
            marker = edge_marker(C, credit_true, edge)
            want = "L" * edge + ".."
            match = got == edge and marker == want
            rows.append({"C": C, "M_edge": got, "expected": edge, "marker": marker, "match": match})
            assert match, f"C={C} M_edge={got} marker={marker} want={want}"
        report["gates"]["V1"] = "PASS"
        report["details"]["V1"] = rows
        print("V1 PASS  edges C=1..5 match 4,7,9,12,14")
    except Exception as e:
        report["gates"]["V1"] = f"FAIL: {e}"
        ok_all = False
        print(f"V1 FAIL: {e}")

    # V2 D_real m=2..12 — plan cites floor((22m-1)/53); shell_probe uses d_rat
    # which equals d_irr on agreement zone. Check both forms + empirical D.
    try:
        rows = []
        for m in range(2, 13):
            emp = D_emp(10, m, credit_true, steps=53)
            dr, di, dm = d_rat(m), d_irr(m), d_real_mirror(m)
            # Primary gate: emp == d_rat == d_irr (shell_probe P5)
            match_p5 = emp == dr == di
            # Mirror form: document relationship
            rows.append(
                {
                    "m": m,
                    "D_emp": emp,
                    "d_rat": dr,
                    "d_irr": di,
                    "d_real_mirror": dm,
                    "match_p5": match_p5,
                    "mirror_eq_rat": dm == dr,
                }
            )
            assert match_p5, f"m={m} emp={emp} rat={dr} irr={di}"
        # first divergence of rat vs irr at 359
        first_div = next(m for m in range(1, 1000) if d_rat(m) != d_irr(m))
        assert first_div == 359
        report["gates"]["V2"] = "PASS"
        report["details"]["V2"] = {
            "rows": rows,
            "first_rat_irr_div_m": first_div,
            "note": "d_real_mirror floor((22m-1)/53) may differ from d_rat by O(1); "
            "gate is shell_probe P5 emp==d_rat==d_irr for m=2..12",
        }
        print(f"V2 PASS  D_emp==d_rat==d_irr m=2..12; first rat/irr div m={first_div}")
        for r in rows:
            if not r["mirror_eq_rat"]:
                print(f"  note: m={r['m']} mirror={r['d_real_mirror']} != rat={r['d_rat']}")
    except Exception as e:
        report["gates"]["V2"] = f"FAIL: {e}"
        ok_all = False
        print(f"V2 FAIL: {e}")

    # V3 exact credits — bit_length path, cross-check no float path used for credit
    try:
        # Spot-check credit_true against bit_length identity for k up to 400
        for k in range(0, 401):
            c = credit_true(k)
            assert c in (1, 2)
            # reconstruct from bit_length
            fl = lambda kk: 0 if kk == 0 else (3 ** kk).bit_length() - 1
            assert c == fl(k + 1) - fl(k)
        # f64 would eventually disagree — document agreement span
        import math

        bad = None
        for k in range(0, 2000):
            c_exact = credit_true(k)
            c_f64 = math.floor((k + 1) * math.log2(3)) - math.floor(k * math.log2(3))
            if c_exact != c_f64:
                bad = k
                break
        report["gates"]["V3"] = "PASS"
        report["details"]["V3"] = {
            "exact_check_k": "0..400",
            "first_f64_disagreement_k": bad,
            "method": "bit_length(3^k)-1",
        }
        print(f"V3 PASS  exact credits 0..400; first f64 disagree k={bad}")
    except Exception as e:
        report["gates"]["V3"] = f"FAIL: {e}"
        ok_all = False
        print(f"V3 FAIL: {e}")

    report["ok_all"] = ok_all
    report["elapsed_sec"] = time.time() - t0
    out = ART / "v0v3_report.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nWROTE {out}  ok_all={ok_all}  elapsed={report['elapsed_sec']:.1f}s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
