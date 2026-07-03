"""
Assembles results.md from the JSON artifacts produced by validate.py,
small_side_sweep.py, embedding_test.py, and size_comparison.py.

Run this LAST, after all other scripts have completed.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT_DIR = Path(__file__).parent


def load(name):
    p = OUT_DIR / name
    if not p.exists():
        return None
    return json.loads(p.read_text())


def main():
    validation = load("validation_results.json")
    small_side = load("small_side_results.json")
    embedding = load("embedding_test_results.json")
    size_comp = load("size_comparison_results.json")

    lines = []
    lines.append("# Renormalization / Corridor-Embedding Conjecture: Test Results\n")
    lines.append("Testing whether A(C+22, m+53) contains an exact self-embedding of "
                  "A(C, m), per COLLATZ_PROOF.md's residue automaton (Section 4.2-4.3).\n")

    lines.append("## 1. Validation (mandatory pre-check)\n")
    if validation:
        lines.append(f"- Lemma 3 (22 support / 31 drop in first 53 Sturmian credits): "
                      f"**{'PASS' if validation['lemma3']['matches_lemma3'] else 'FAIL'}**")
        lines.append(f"- M_edge(C) formula match (C=1..5): "
                      f"**{'PASS' if validation['M_edge_formula']['all_pass'] else 'FAIL'}**")
        lines.append(f"- Zero-birth-edge (Theorem 1 / Certificate 1) reproduced "
                      f"independently for C=3,4,5: "
                      f"**{'PASS' if validation['zero_birth_edge']['all_pass'] else 'FAIL'}**")
        lines.append(f"- Overall: **{'PASS' if validation['overall_pass'] else 'FAIL'}**\n")
    else:
        lines.append("- NOT RUN\n")

    lines.append("## 2. Small-side |live(C,m)| table (dense, exact)\n")
    if small_side:
        lines.append("| C | m | M_edge(C) | live | possible | live_fraction | terminal_compat | time(s) |")
        lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|")
        for row in small_side["rows"]:
            lines.append(f"| {row['C']} | {row['m']} | {row['M_edge_C']} | "
                          f"{row['total_live_states']} | {row['total_possible_states']} | "
                          f"{row['live_fraction']:.6e} | {row['terminal_compatible_count']} | "
                          f"{row['compute_time_sec']:.2f} |")
        lines.append("")
    else:
        lines.append("- NOT RUN\n")

    lines.append("## 3. Explicit embedding-map test (Step 3)\n")
    if embedding:
        lines.append(f"Corridor shift = {embedding['corridor_shift']}, heartbeat = {embedding['heartbeat']}, "
                      f"max elements sampled per pair = {embedding['max_elements_per_pair']}, "
                      f"oracle call cap = {embedding['oracle_call_cap']}.\n")

        # Aggregate totals across all pairs, per candidate.
        totals = {}
        for pair in embedding["pairs"]:
            for cname, cdata in pair["candidates"].items():
                t = totals.setdefault(cname, {"matched": 0, "failed": 0, "inconclusive": 0,
                                               "undefined": 0, "tested": 0})
                t["matched"] += cdata["matched"]
                t["failed"] += cdata["failed"]
                t["inconclusive"] += cdata["inconclusive"]
                t["undefined"] += cdata["undefined"]
                t["tested"] += cdata["n_tested"]
        lines.append("### Aggregate totals across all 10 tested (C,m) pairs\n")
        lines.append("| candidate | tested | matched | failed | inconclusive | match rate of decided |")
        lines.append("|:---|---:|---:|---:|---:|---:|")
        for cname, t in totals.items():
            decided = t["matched"] + t["failed"]
            rate = f"{t['matched']/decided:.0%}" if decided > 0 else "N/A (0 decided)"
            lines.append(f"| {cname} | {t['tested']} | {t['matched']} | {t['failed']} | "
                          f"{t['inconclusive']} | {rate} |")
        lines.append("")
        lines.append("| C | m | C2 | m2 | candidate | tested | matched | failed | inconclusive | undefined | verdict |")
        lines.append("|---:|---:|---:|---:|:---|---:|---:|---:|---:|---:|:---|")
        for pair in embedding["pairs"]:
            for cname, cdata in pair["candidates"].items():
                n = cdata["n_tested"]
                matched = cdata["matched"]
                failed = cdata["failed"]
                inconclusive = cdata["inconclusive"]
                undefined = cdata["undefined"]
                decided = matched + failed
                if decided == 0:
                    verdict = "ALL INCONCLUSIVE"
                elif failed == 0 and inconclusive == 0 and undefined == 0:
                    verdict = "EXACT CONTAINMENT (fully decided)"
                elif failed == 0 and inconclusive > 0:
                    verdict = f"CONTAINMENT HOLDS ON DECIDED SUBSET (100% of {decided}/{n}; {inconclusive} inconclusive)"
                elif matched == 0 and decided > 0:
                    verdict = "DEAD"
                else:
                    frac = matched / decided
                    verdict = f"PARTIAL ({frac:.0%} of {decided} decided; {inconclusive} inconclusive)"
                lines.append(f"| {pair['C']} | {pair['m']} | {pair['C2']} | {pair['m2']} | "
                              f"{cname} | {n} | {matched} | {failed} | {inconclusive} | {undefined} | {verdict} |")
        lines.append("")
    else:
        lines.append("- NOT RUN\n")

    lines.append("## 4. Size comparison smoke test (Step 4, NOT proof of embedding)\n")
    if size_comp:
        lines.append("### Small-side structural (exact)\n")
        lines.append("| C | m | live | possible | live_fraction |")
        lines.append("|---:|---:|---:|---:|---:|")
        for row in size_comp["small_side_structural"]:
            lines.append(f"| {row['C']} | {row['m']} | {row['total_live']} | "
                          f"{row['total_possible']} | {row['live_fraction']:.6e} |")
        lines.append("\n### Big-side Monte Carlo estimate (NOT exact)\n")
        lines.append("| C | m | C2 | m2 | decided/samples | est. live_frac (big) | exact live_frac (small) | ratio |")
        lines.append("|---:|---:|---:|---:|:---|---:|---:|---:|")
        for row in size_comp["big_side_monte_carlo"]:
            est = row["estimated_live_fraction"]
            est_str = f"{est:.4f}" if est is not None else "N/A"
            ratio = row["fraction_ratio_big_over_small"]
            ratio_str = f"{ratio:.3f}" if ratio is not None else "N/A"
            lines.append(f"| {row['C']} | {row['m']} | {row['C2']} | {row['m2']} | "
                          f"{row['n_decided']}/{row['n_samples']} | {est_str} | "
                          f"{row['small_side_live_fraction_exact']:.6e} | {ratio_str} |")
        lines.append("")
    else:
        lines.append("- NOT RUN\n")

    lines.append("## 5. Honest limitations (what was NOT tested / could not be tested)\n")
    lines.append("- **Dense enumeration of the big-side automaton A(C+22, m+53) is "
                  "mathematically impossible on any hardware**: even the smallest "
                  "required big-side precision (m+53 >= 54) needs 3^54 ~ 5.8e25 "
                  "residues per deficit level. This is not a compute-budget "
                  "limitation to be optimized away; it is combinatorial.")
    lines.append("- The big-side membership oracle (backward reachability, see "
                  "oracle.py) is exact where it decides, but its decidability "
                  "(non-inconclusive) rate DROPS as corridor width and precision "
                  "grow, even at C+22=23 (the narrowest big-side corridor tested). "
                  "This means containment claims are demonstrated on a DECREASING "
                  "fraction of the sampled elements as (C,m) grows -- see the "
                  "'inconclusive' column throughout.")
    lines.append("- **Surjectivity of any candidate map was NOT tested** -- this "
                  "would require enumerating live(C+22,m+53) in full, which is "
                  "exactly the infeasible operation above. All verdicts in Section 3 "
                  "concern containment (phi(live) subset of live'), not surjectivity.")
    lines.append("- Sample sizes per (C,m) pair are capped at 15 elements (40 in an "
                  "initial, abandoned run at C=1 only -- see embedding_test.py's "
                  "'NOTE ON BUDGET TUNING' comment) for compute-time reasons; this "
                  "is a SAMPLE, not exhaustive coverage, of live(C,m).")
    lines.append("- Corridor widths C=6..15 (required by the mission spec's C=1..15 "
                  "range) were **not reached** on the small side: dense computation "
                  "at C=6's target precision (m=18) already requires ~2.7 billion "
                  "states, and C=7+ requires 8e10+ states -- both infeasible in the "
                  "time available. Only C=1..5 were computed. This is reported here "
                  "explicitly rather than silently narrowing scope.")
    lines.append("- The initial embedding-test run (uncapped, MAX_ELEMENTS_PER_PAIR=40, "
                  "ORACLE_CALL_CAP=800,000) was killed after ~100s once it became clear "
                  "it would not finish C=2..5 in reasonable time; it was restarted with "
                  "tighter budgets (15 elements, 150,000 call cap, 90s per-pair wall-clock "
                  "budget) that traded per-pair depth for breadth across C. No pair in "
                  "the final run hit the 90s wall-clock cap (all completed under it), "
                  "so the reported results are not truncated by that budget -- only by "
                  "the per-query oracle call cap (visible in the 'inconclusive' counts).")
    lines.append("- The Monte Carlo big-side live-fraction estimates (Section 4, Part 2) "
                  "use only 60 samples per (C,m) pair, of which roughly 25-35 resolved "
                  "(the rest inconclusive) -- standard error on the resulting fraction "
                  "is large (~0.06-0.09). The ratios reported (0.5x to 2.0x) show no "
                  "clean pattern at this sample size and should NOT be read as evidence "
                  "of (or against) a specific closed-form size relationship.")
    lines.append("- Candidate (c)'s exponent policy (a = c_k at every step) is one "
                  "natural choice among several the raw automaton's branching permits; "
                  "other fixed policies (e.g. always-maximal-a, or policies tied to a "
                  "specific target residue's own forward trajectory) were not tested.")
    lines.append("")

    (OUT_DIR / "results.md").write_text("\n".join(lines))
    print(f"Wrote {OUT_DIR / 'results.md'}")


if __name__ == "__main__":
    main()
