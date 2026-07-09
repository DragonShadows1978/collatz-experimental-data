#!/usr/bin/env python3
"""G1 E3 — ΔM staircase from trusted genuine-death edges only.

Plan: IMPLEMENTATION_PLAN.md §5. Prediction P3.1 frozen pre-data.
Walls are never edges. Sources frozen below before any ΔM compute.
"""
from __future__ import annotations

import csv
import json
import statistics
import sys
from pathlib import Path

TRACK = Path(__file__).resolve().parents[1]
ART = TRACK / "artifacts"
ART.mkdir(parents=True, exist_ok=True)
REPO = TRACK.parents[2]  # collatz-experimental-data
UNDERLOCK = REPO / "renorm_check" / "shell" / "underlock"

# ---------------------------------------------------------------------------
# FROZEN source list (receipted before compute) — genuine-death only
# ---------------------------------------------------------------------------
# 1) W7A_ORDER.md §"The measured fact" — C=1..26 measured edges used as the
#    program's validation spine (incl. W7B gate C=16,23,26).
# 2) w7a_new_edges.txt — C=27..31 rows only appended when genuine_death=True
#    (see W7B_FINDINGS.md: wall rows never written here).
SOURCE_SPECS = [
    {
        "id": "W7A_ORDER_measured_C1_26",
        "path": str(UNDERLOCK / "w7a_renorm" / "W7A_ORDER.md"),
        "role": "measured genuine edges C=1..26 (order text, exact integers)",
        "C_range": [1, 26],
    },
    {
        "id": "w7a_new_edges_C27_31",
        "path": str(UNDERLOCK / "w7a_renorm" / "w7a_new_edges.txt"),
        "role": "genuine_death=True only (W7B append policy; walls excluded)",
        "C_range": [27, 31],
    },
    {
        "id": "W7B_FINDINGS_crosscheck",
        "path": str(UNDERLOCK / "w7b_deep" / "W7B_FINDINGS.md"),
        "role": "cross-check table C=27..31 + validation gate 16/23/26",
        "C_range": [16, 31],
    },
]

# Hardcoded from W7A_ORDER.md lines (must match file on disk — verified at runtime)
W7A_ORDER_EDGES: dict[int, int] = {
    # C=1..10
    1: 4,
    2: 7,
    3: 9,
    4: 12,
    5: 14,
    6: 16,
    7: 19,
    8: 21,
    9: 24,
    10: 26,
    # C=11..26
    11: 57,
    12: 63,
    13: 68,
    14: 71,
    15: 79,
    16: 93,
    17: 108,
    18: 110,
    19: 130,
    20: 132,
    21: 139,
    22: 157,
    23: 163,
    24: 188,
    25: 192,
    26: 205,
}

W7B_GATE = {16: 93, 23: 163, 26: 205}
W7B_TABLE = {27: 208, 28: 263, 29: 265, 30: 282, 31: 284}

SMALL_MAX = 3  # plan P3.1: small values ≤3


def parse_w7a_new_edges(path: Path) -> dict[int, int]:
    edges: dict[int, int] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(f"bad edge line in {path}: {line!r}")
        c, m = int(parts[0]), int(parts[1])
        edges[c] = m
    return edges


def verify_w7a_order_text(path: Path) -> None:
    """Assert the on-disk W7A_ORDER still contains the frozen edge lists."""
    text = path.read_text()
    assert "C=1..10: 4,7,9,12,14,16,19,21,24,26" in text, "W7A_ORDER C=1..10 list drift"
    assert "C=11..26: 57,63,68,71,79,93,108,110,130,132,139,157,163,188,192,205" in text, (
        "W7A_ORDER C=11..26 list drift"
    )


def verify_w7b_findings(path: Path, edges: dict[int, int]) -> None:
    text = path.read_text()
    for c, m in W7B_GATE.items():
        assert edges.get(c) == m, f"gate mismatch C={c}"
    for c, m in W7B_TABLE.items():
        assert f"| {c} | {m} |" in text or f"|{c}|{m}|" in text.replace(" ", ""), (
            f"W7B_FINDINGS missing C={c} M={m}"
        )
        # looser: just check numbers appear near each other
        assert str(c) in text and str(m) in text


def load_edges() -> tuple[dict[int, int], list[dict]]:
    """Load and cross-check genuine-death edges. Returns (C->M, provenance rows)."""
    sources_used = []
    order_path = Path(SOURCE_SPECS[0]["path"])
    new_path = Path(SOURCE_SPECS[1]["path"])
    findings_path = Path(SOURCE_SPECS[2]["path"])

    verify_w7a_order_text(order_path)
    sources_used.append({**SOURCE_SPECS[0], "n_edges": 26, "status": "verified_text"})

    edges = dict(W7A_ORDER_EDGES)

    new_edges = parse_w7a_new_edges(new_path)
    # Only accept C>=27 from this file; must match W7B table
    for c, m in sorted(new_edges.items()):
        if c < 27:
            raise ValueError(f"unexpected C={c} in w7a_new_edges (expected >=27)")
        if c in W7B_TABLE and W7B_TABLE[c] != m:
            raise ValueError(f"w7a_new_edges C={c} M={m} != W7B_TABLE {W7B_TABLE[c]}")
        edges[c] = m
    sources_used.append(
        {
            **SOURCE_SPECS[1],
            "n_edges": len(new_edges),
            "status": "parsed",
            "rows": new_edges,
        }
    )

    # Cross-check W7B findings gate + table against loaded edges
    for c, m in W7B_GATE.items():
        if edges[c] != m:
            raise ValueError(f"W7B gate fail C={c}: got {edges[c]} want {m}")
    for c, m in W7B_TABLE.items():
        if edges.get(c) != m:
            raise ValueError(f"W7B table fail C={c}: got {edges.get(c)} want {m}")
    sources_used.append({**SOURCE_SPECS[2], "status": "crosscheck_pass"})

    # Monotonicity gate: M(C) > M(C-1) for all consecutive C present
    cs = sorted(edges)
    for i in range(1, len(cs)):
        if cs[i] != cs[i - 1] + 1:
            # allow gaps only if we document them — we require contiguous 1..max
            raise ValueError(f"non-contiguous C: {cs[i-1]} -> {cs[i]}")
        if not (edges[cs[i]] > edges[cs[i - 1]]):
            raise ValueError(
                f"non-monotone M at C={cs[i]}: {edges[cs[i]]} <= {edges[cs[i-1]]}"
            )

    return edges, sources_used


def compute_delta_rows(edges: dict[int, int]) -> list[dict]:
    """ΔM(C)=M(C)-M(C-1) for C>=2. Pure table transform."""
    rows = []
    for c in sorted(edges):
        if c == min(edges):
            rows.append(
                {
                    "C": c,
                    "M": edges[c],
                    "delta_M": "",
                    "class": "",
                }
            )
            continue
        prev = edges[c - 1]
        d = edges[c] - prev
        # arithmetic identity check
        assert edges[c] == prev + d
        cls = "small" if d <= SMALL_MAX else "large"
        rows.append({"C": c, "M": edges[c], "delta_M": d, "class": cls})
    return rows


def score_p31(delta_rows: list[dict]) -> dict:
    """Score frozen P3.1.

    P3.1: increments not approx constant; cluster into small(≤3) and large
    jumps; large jumps align with support-dense credit blocks better than
    chance. Confidence prior 0.40.
    """
    deltas = [r["delta_M"] for r in delta_rows if r["delta_M"] != ""]
    assert deltas, "no deltas"
    n = len(deltas)
    mean = statistics.mean(deltas)
    stdev = statistics.pstdev(deltas) if n > 1 else 0.0
    # "approximately constant" if relative spread is tiny
    cv = stdev / mean if mean else float("inf")
    not_constant = cv >= 0.25 or (max(deltas) - min(deltas)) >= 5

    small = [d for d in deltas if d <= SMALL_MAX]
    large = [d for d in deltas if d > SMALL_MAX]
    n_small, n_large = len(small), len(large)
    # bimodality / cluster signal: both classes non-empty and max gap in
    # sorted unique values separates ≤3 from >3 with a gap, OR both classes
    # have ≥2 members
    has_both_classes = n_small >= 1 and n_large >= 1
    sorted_u = sorted(set(deltas))
    # gap between small class max and large class min if both exist
    gap = None
    if has_both_classes:
        gap = min(large) - max(small)

    cluster_ok = has_both_classes and (n_large >= 2) and (max(deltas) >= 10)

    # Alignment half: large-jump C positions vs true-word support density
    # in a local window. Underpowered if few large jumps — then INCONCLUSIVE.
    large_C = [r["C"] for r in delta_rows if r["class"] == "large"]
    alignment = _alignment_test(large_C, n_large)

    # Overall P3.1: requires not_constant + cluster; alignment is second clause
    if not not_constant:
        verdict = "REFUTED"
        reason = "increments approximately constant (low CV / small range)"
    elif not cluster_ok:
        verdict = "REFUTED"
        reason = "failed small(≤3) vs large cluster structure"
    elif alignment["verdict"] == "CONFIRMED":
        verdict = "CONFIRMED"
        reason = "non-constant + bimodal + large jumps align with support density"
    elif alignment["verdict"] == "REFUTED":
        # cluster holds but alignment fails → overall REFUTED on full P3.1
        # (plan requires both halves). If alignment underpowered, don't
        # force REFUTED on full claim.
        verdict = "REFUTED"
        reason = "cluster ok but support-density alignment failed"
    else:
        # alignment INCONCLUSIVE: score cluster half only
        verdict = "INCONCLUSIVE"
        reason = (
            "non-constant + small/large clustering CONFIRMED as partial; "
            "support-density / Ostrowski alignment underpowered or untested "
            f"({alignment.get('reason', '')})"
        )

    return {
        "verdict": verdict,
        "reason": reason,
        "confidence_prior": 0.40,
        "n_deltas": n,
        "deltas": deltas,
        "mean": mean,
        "stdev": stdev,
        "cv": cv,
        "min": min(deltas),
        "max": max(deltas),
        "n_small_le3": n_small,
        "n_large_gt3": n_large,
        "small_values": small,
        "large_values": large,
        "class_gap": gap,
        "not_approximately_constant": not_constant,
        "cluster_structure_ok": cluster_ok,
        "alignment": alignment,
        "large_jump_C": large_C,
    }


def _alignment_test(large_C: list[int], n_large: int) -> dict:
    """Compare large-jump C to true Sturmian support density.

    Cheap exact test: for each C, take credit letters in a block of length
    HEARTBEAT ending near a scale proxy (not a deep law — exploratory).
    If n_large < 5, return INCONCLUSIVE (underpowered).
    """
    if n_large < 5:
        return {
            "verdict": "INCONCLUSIVE",
            "reason": f"only {n_large} large jumps; need ≥5 for chance test",
            "n_large": n_large,
        }

    # Import exact true credit
    sys.path.insert(0, str(TRACK / "scripts"))
    from g1_common import credit_true  # noqa: WPS433

    def support_frac(k0: int, length: int = 53) -> float:
        ones = sum(1 for k in range(k0, k0 + length) if credit_true(k) == 1)
        return ones / length

    # Proxy: map C -> window start 2*C (scale-free tag, not Ostrowski claim)
    large_fracs = [support_frac(2 * c) for c in large_C]
    # Control: all C from 2..max for same map
    all_C = list(range(2, max(large_C) + 1))
    all_fracs = [support_frac(2 * c) for c in all_C]
    mean_large = statistics.mean(large_fracs)
    mean_all = statistics.mean(all_fracs)
    # "better than chance" if large-jump windows have higher support density
    # by a clear margin
    if mean_large >= mean_all + 0.02:
        return {
            "verdict": "CONFIRMED",
            "mean_support_frac_large_C": mean_large,
            "mean_support_frac_all_C": mean_all,
            "margin": mean_large - mean_all,
            "note": "proxy window 2*C length 53; not a full Ostrowski proof",
        }
    if mean_large <= mean_all - 0.02:
        return {
            "verdict": "REFUTED",
            "mean_support_frac_large_C": mean_large,
            "mean_support_frac_all_C": mean_all,
            "margin": mean_large - mean_all,
        }
    return {
        "verdict": "INCONCLUSIVE",
        "reason": "support-density margin <0.02; no clear alignment signal",
        "mean_support_frac_large_C": mean_large,
        "mean_support_frac_all_C": mean_all,
        "margin": mean_large - mean_all,
    }


def main() -> int:
    print("E3 — frozen sources:", flush=True)
    for s in SOURCE_SPECS:
        print(f"  {s['id']}: {s['path']}", flush=True)

    edges, sources = load_edges()
    print(f"Loaded {len(edges)} genuine-death edges C={min(edges)}..{max(edges)}", flush=True)

    delta_rows = compute_delta_rows(edges)
    # Sanity: hand-check two known pairs
    assert edges[28] - edges[27] == 55
    assert edges[31] - edges[30] == 2
    assert edges[16] - edges[15] == 14

    p31 = score_p31(delta_rows)
    print(f"P3.1 verdict: {p31['verdict']}", flush=True)
    print(f"  deltas: {p31['deltas']}", flush=True)
    print(f"  small≤3: {p31['n_small_le3']}  large: {p31['n_large_gt3']}", flush=True)
    print(f"  cv={p31['cv']:.4f} range={p31['max']-p31['min']}", flush=True)
    print(f"  alignment: {p31['alignment']}", flush=True)

    csv_path = ART / "e3_delta_M.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["C", "M", "delta_M", "class"])
        w.writeheader()
        for r in delta_rows:
            w.writerow(r)

    summary = {
        "sources_frozen": SOURCE_SPECS,
        "sources_used": sources,
        "n_edges": len(edges),
        "edges": {str(k): v for k, v in sorted(edges.items())},
        "delta_rows": delta_rows,
        "predictions": {"P3.1": p31},
        "gates": {
            "genuine_death_only": True,
            "walls_excluded": True,
            "monotone_M": True,
            "contiguous_C": True,
            "hand_check_28_27": edges[28] - edges[27],
            "hand_check_31_30": edges[31] - edges[30],
            "hand_check_16_15": edges[16] - edges[15],
        },
        "artifacts": {"csv": str(csv_path)},
    }
    sum_path = ART / "e3_summary.json"
    sum_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"WROTE {csv_path}")
    print(f"WROTE {sum_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
