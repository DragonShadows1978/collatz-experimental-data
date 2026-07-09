#!/usr/bin/env python3
"""G2 E3 — mixed climb-adjacent words from E1. Predictions Q3.1–Q3.3."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from g2_core import cylinder_for_word, pure_a1_cylinder, realizes_word  # noqa: E402

ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(parents=True, exist_ok=True)


def main() -> int:
    t0 = time.time()
    e1_path = ART / "e1_summary.json"
    if not e1_path.is_file():
        print("E3 FAIL: e1_summary.json missing — run E1 first")
        return 1
    e1 = json.loads(e1_path.read_text())
    top = e1.get("top_gap_words") or []
    # take up to 20, require ≥10
    words = []
    for item in top[:20]:
        w = tuple(item["word"])
        words.append((w, item["count"]))

    if len(words) < 10:
        print(f"E3 FAIL: only {len(words)} words from E1 (need ≥10)")
        return 1

    results = []
    for w, cnt in words:
        # general cylinder
        cyl = cylinder_for_word(w, max_bits=40)
        # also try pure-a1 closed form when all ones
        pure = all(a == 1 for a in w)
        if pure:
            pc = pure_a1_cylinder(len(w))
            min_x = pc.min_positive_odd
            mod_bits = pc.mod_bits
            residue = pc.residue
            modulus = pc.modulus
            nonempty = pc.nonempty
            note = pc.note
        else:
            min_x = cyl.min_positive_odd
            mod_bits = cyl.mod_bits
            residue = cyl.residue
            modulus = cyl.modulus
            nonempty = cyl.nonempty
            note = cyl.note

        if min_x is not None:
            assert realizes_word(min_x, w), (w, min_x)

        pure_bits = pure_a1_cylinder(len(w)).mod_bits if len(w) >= 1 else 0
        results.append(
            {
                "word": list(w),
                "word_str": ",".join(map(str, w)),
                "length": len(w),
                "e1_count": cnt,
                "nonempty": nonempty,
                "modulus": modulus,
                "mod_bits": mod_bits,
                "residue": residue,
                "min_positive_odd": min_x,
                "min_x_lt_1e6": min_x is not None and min_x < 1_000_000,
                "pure_a1_mod_bits_same_len": pure_bits,
                "stricter_than_pure_a1": mod_bits > pure_bits if not pure else False,
                "is_pure_a1": pure,
                "note": note,
            }
        )
        print(
            f"  word={w} count={cnt} nonempty={nonempty} "
            f"mod_bits={mod_bits} min_x={min_x}",
            flush=True,
        )

    # Q3.1 every frequent word realizable
    q31_ok = all(r["nonempty"] for r in results)
    q31 = {
        "verdict": "CONFIRMED" if q31_ok else "REFUTED",
        "n_words": len(results),
        "n_nonempty": sum(1 for r in results if r["nonempty"]),
        "confidence_prior": 0.60,
    }

    # Q3.2: no frequent word length ≥8 has witness < 1e6
    long_w = [r for r in results if r["length"] >= 8]
    if not long_w:
        q32 = {
            "verdict": "INCONCLUSIVE",
            "reason": "no frequent words with length≥8",
            "confidence_prior": 0.45,
        }
    else:
        # prediction: NO witness below 1e6 for those words
        any_small = any(r["min_x_lt_1e6"] for r in long_w)
        q32 = {
            "verdict": "CONFIRMED" if not any_small else "REFUTED",
            "long_words": [
                {
                    "word": r["word_str"],
                    "min_x": r["min_positive_odd"],
                    "lt_1e6": r["min_x_lt_1e6"],
                }
                for r in long_w
            ],
            "confidence_prior": 0.45,
        }

    # Q3.3: upcrossing/gap words stricter than pure a=1 of same length
    # Compare non-pure words: mod_bits > pure_a1 same length
    mixed = [r for r in results if not r["is_pure_a1"]]
    if not mixed:
        # all pure a=1 — stricter is false by definition; INCONCLUSIVE
        q33 = {
            "verdict": "INCONCLUSIVE",
            "reason": "all top words are pure a=1 runs; no mixed word to compare",
            "confidence_prior": 0.50,
        }
    else:
        frac = sum(1 for r in mixed if r["stricter_than_pure_a1"]) / len(mixed)
        q33 = {
            "verdict": "CONFIRMED" if frac >= 0.5 else "REFUTED",
            "frac_stricter": frac,
            "n_mixed": len(mixed),
            "confidence_prior": 0.50,
        }

    gates = {
        "E3-G1": "PASS" if len(results) >= 10 else "FAIL",
        "E3-G2": "PASS" if all("nonempty" in r for r in results) else "FAIL",
        "n_words": len(results),
    }

    summary = {
        "gates": gates,
        "predictions": {"Q3.1": q31, "Q3.2": q32, "Q3.3": q33},
        "results": results,
        "elapsed_sec": time.time() - t0,
    }
    out = ART / "e3_summary.json"
    out.write_text(json.dumps(summary, indent=2))
    # CSV-like jsonl
    with (ART / "e3_words.jsonl").open("w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(json.dumps({"gates": gates, "predictions": summary["predictions"]}, indent=2))
    print(f"WROTE {out}")
    return 0 if gates["E3-G1"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
