#!/usr/bin/env python3
"""G2 shared validation V0–V2."""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from g2_core import (  # noqa: E402
    a1_iff_3_mod_4,
    count_upcrossings,
    odd_step,
    predicts_a_matches,
    pure_a1_cylinder,
    realizes_word,
    v2,
    walk_orbit,
)

ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(parents=True, exist_ok=True)


def main() -> int:
    t0 = time.time()
    report: dict = {"gates": {}, "details": {}}
    ok = True

    # V0: 80049391 has ≥1 upcrossing with a=1
    try:
        steps = walk_orbit(80049391, max_steps=8000)
        ups = [s for s in steps if s["upcrossing"]]
        a1_ups = [s for s in ups if s["a"] == 1]
        assert len(ups) >= 1, "no upcrossings"
        assert len(a1_ups) >= 1, "no a=1 upcrossing"
        assert all(s["a"] == 1 for s in ups), "non-a1 upcrossing on 80049391"
        report["gates"]["V0"] = "PASS"
        report["details"]["V0"] = {
            "start": 80049391,
            "n_upcrossings": len(ups),
            "n_a1_upcrossings": len(a1_ups),
            "first_up": ups[0],
        }
        print(f"V0 PASS  ups={len(ups)} all a=1 on 80049391")
    except Exception as e:
        report["gates"]["V0"] = f"FAIL: {e}"
        ok = False
        print(f"V0 FAIL: {e}")

    # V1: a=1 iff x≡3 mod 4 for all odds mod 4, and exhaustive small odds
    try:
        for x in range(1, 2001, 2):
            assert a1_iff_3_mod_4(x), x
        # mod 4 classes only two odds: 1 and 3
        assert v2(3 * 1 + 1) != 1 or (1 % 4 == 3)  # x=1: 4, v2=2
        assert v2(3 * 3 + 1) == 1
        report["gates"]["V1"] = "PASS"
        report["details"]["V1"] = {"checked_odds": "1..2000"}
        print("V1 PASS  a=1 iff x≡3 mod 4 on odds 1..2000")
    except Exception as e:
        report["gates"]["V1"] = f"FAIL: {e}"
        ok = False
        print(f"V1 FAIL: {e}")

    # V2: 20 random odds, a prediction from residue matches when a < j
    try:
        rng = random.Random(20260709)
        n = 20
        fails = 0
        samples = []
        for _ in range(n):
            x = rng.randrange(1, 10**7, 2)
            for j in (3, 5, 8, 12):
                if not predicts_a_matches(x, j):
                    fails += 1
                samples.append(
                    {
                        "x": x,
                        "j": j,
                        "a": v2(3 * x + 1),
                        "ok": predicts_a_matches(x, j),
                    }
                )
        assert fails == 0, f"{fails} prediction mismatches"
        # pure a=1 L=1 cylinder
        c = pure_a1_cylinder(1)
        assert c.residue == 3 and c.modulus == 4
        assert realizes_word(3, (1,))
        report["gates"]["V2"] = "PASS"
        report["details"]["V2"] = {"n_starts": n, "fails": fails, "sample_head": samples[:4]}
        print(f"V2 PASS  {n} random odds × j∈{{3,5,8,12}} a-prediction OK")
    except Exception as e:
        report["gates"]["V2"] = f"FAIL: {e}"
        ok = False
        print(f"V2 FAIL: {e}")

    report["ok_all"] = ok
    report["elapsed_sec"] = time.time() - t0
    out = ART / "v0v2_report.json"
    out.write_text(json.dumps(report, indent=2, default=str))
    print(f"WROTE {out} ok_all={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
