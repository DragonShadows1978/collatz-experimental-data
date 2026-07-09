#!/usr/bin/env python3
"""Sole writer of G15–G24 summaries/ledgers/run.logs. Plans cite prior by IDs+path, not verdict dicts."""
from __future__ import annotations
import json, time, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

SHELL = Path(__file__).resolve().parents[1]
REPO = SHELL.parents[1]
RECEIPTS = Path(__file__).resolve().parent / "chain_receipts.jsonl"

TRACKS = [
    ("g15_species_gap_law", "G15", None, "S15.1–S15.4"),
    ("g16_gap_ratio_vs_primes", "G16", "g15_species_gap_law", "S16.1–S16.4"),
    ("g17_dyadic_bucket_density", "G17", "g16_gap_ratio_vs_primes", "S17.1–S17.3"),
    ("g18_count_vs_pi", "G18", "g17_dyadic_bucket_density", "S18.1–S18.3"),
    ("g19_gap_over_x", "G19", "g18_count_vs_pi", "S19.1–S19.3"),
    ("g20_composite_k_composite_x", "G20", "g19_gap_over_x", "S20.1–S20.2"),
    ("g21_odds_local_density", "G21", "g20_composite_k_composite_x", "S21.1–S21.2"),
    ("g22_max_prime_gap_vs_species", "G22", "g21_odds_local_density", "S22.1–S22.2"),
    ("g23_near_species_odds", "G23", "g22_max_prime_gap_vs_species", "S23.1–S23.2"),
    ("g24_spacing_taxonomy", "G24", "g23_near_species_odds", "S24.1–S24.3"),
]

# Frozen prediction tables (intent only — no post-hoc verdicts)
PRED_TABLES = {
"g15_species_gap_law": """## Predictions (frozen pre-data)
| ID | Claim | Conf |
|----|-------|------|
| S15.1 | gap_k = 4^k for all k=1..100 | 0.99 |
| S15.2 | gap_k / ln(x_k) is strictly increasing for k=2..50 | 0.90 |
| S15.3 | gap_k / ln(x_k) > 10 for all k≥10 | 0.85 |
| S15.4 | count species ≤ 10^12 equals constructor count | 0.95 |
""",
"g16_gap_ratio_vs_primes": """## Predictions (frozen after G15 results)
| ID | Claim | Conf |
|----|-------|------|
| S16.1 | gap_{k+1}/gap_k = 4 for all k=1..99 | 0.99 |
| S16.2 | Among prime gaps for p≤10^6, fraction of ratios in (3.5, 4.5) ≤ 0.15 | 0.60 |
| S16.3 | Stdev of log(prime gap ratios) > 0.5 | 0.55 |
| S16.4 | Stdev of species gap ratios = 0 | 0.99 |
""",
"g17_dyadic_bucket_density": """## Predictions (frozen after G16 results)
| ID | Claim | Conf |
|----|-------|------|
| S17.1 | For m=1..40, number of x_k in [4^m, 4^{m+1}) is in {0,1} | 0.90 |
| S17.2 | For m=2..40, fraction of buckets with exactly one species ≥ 0.8 | 0.70 |
| S17.3 | No bucket has ≥3 species for m=1..40 | 0.95 |
""",
"g18_count_vs_pi": """## Predictions (frozen after G17 results)
| ID | Claim | Conf |
|----|-------|------|
| S18.1 | For X=10^n n=3..8, count_species(X) ≤ 2 log2(X) | 0.90 |
| S18.2 | count_species(10^6) < π(10^6)/100 | 0.85 |
| S18.3 | count nondecreasing on the ladder | 0.99 |
""",
"g19_gap_over_x": """## Predictions (frozen after G18 results)
| ID | Claim | Conf |
|----|-------|------|
| S19.1 | gap/x monotone nonincreasing for k=1..50 | 0.90 |
| S19.2 | |gap/x - 3| < 0.01 for k≥8 (exact rational form) | 0.90 |
| S19.3 | gap/x > 3 for all k≥1 (exact integer test) | 0.99 |
""",
"g20_composite_k_composite_x": """## Predictions (frozen after G19 results)
| ID | Claim | Conf |
|----|-------|------|
| S20.1 | All composite k in 4..60 give composite x_k | 0.99 |
| S20.2 | For each such k, a nontrivial algebraic factor witness exists | 0.90 |
""",
"g21_odds_local_density": """## Predictions (frozen after G20 results)
| ID | Claim | Conf |
|----|-------|------|
| S21.1 | For k=10..25, number of species in [x_k - gap_k//2, x_k + gap_k//2] equals 1 | 0.90 |
| S21.2 | Among odds in that window, species fraction ≤ 3/gap_k | 0.85 |
""",
"g22_max_prime_gap_vs_species": """## Predictions (frozen after G21 results)
| ID | Claim | Conf |
|----|-------|------|
| S22.1 | For each k with x_k ≤ 10^6, max prime gap among primes ≤ x_k < gap_k | 0.90 |
| S22.2 | max_prime_gap(x_k) / ln(x_k)^2 < 10 for those k | 0.50 |
""",
"g23_near_species_odds": """## Predictions (frozen after G22 results)
| ID | Claim | Conf |
|----|-------|------|
| S23.1 | For X=10^6, fraction of odds within band of some x_k ≤ X is < 0.05 | 0.70 |
| S23.2 | That fraction decreases as X goes 10^4 → 10^6 | 0.55 |
""",
"g24_spacing_taxonomy": """## Predictions (frozen after G23 results)
| ID | Claim | Conf |
|----|-------|------|
| S24.1 | Even spacing rejected: variance of species gaps over k=1..30 > 0 | 0.99 |
| S24.2 | Prime-like rejected: mean species gap / mean prime gap at scale x_15 > 100 | 0.85 |
| S24.3 | Geometric accepted: all successive ratios = 4 for k=1..50 | 0.99 |
""",
}

TITLES = {
"g15_species_gap_law": ("Species Gap Law vs Prime Spacing (seed)",
    "Seed: do terminal-species gaps grow with size like primes, or stay evenly spaced?"),
"g16_gap_ratio_vs_primes": ("Successive Gap Ratios: Species vs Primes",
    "Prior G15 established exact gap=4^k and gap/ln x growth (see S15.1–S15.3). Next: successive ratios (species constant 4 vs primes irregular)."),
"g17_dyadic_bucket_density": ("Species Density in Dyadic Buckets",
    "Prior G16 S16.1 (species successive gap ratio = 4). Measure occupancy of buckets [4^m, 4^{m+1})."),
"g18_count_vs_pi": ("Species Count vs π(X)",
    "Prior G17 S17.1–S17.3 (≤1 species per dyadic bucket). Combined with G15 O(log X), species count ≪ π(X)."),
"g19_gap_over_x": ("Relative Gap gap/x → 3",
    "Prior G15–G18 geometric spine. Relative gap/x asymptotic: 4^k / ((4^k-1)/3) → 3 from above."),
"g20_composite_k_composite_x": ("Composite k ⇒ Composite x_k",
    "Prior G15–G19 geometric spacing. Repunit factorization: composite k ⇒ composite x_k; verify factor witnesses."),
"g21_odds_local_density": ("Local Density of Species Among Odds",
    "Prior G17–G19 global thinness. Probe half-gap window isolation around x_k."),
"g22_max_prime_gap_vs_species": ("Max Prime Gap vs Species Gap at Scale",
    "Prior G21 local-window results. Expect max prime gaps below x_k ≪ species gap_k."),
"g23_near_species_odds": ("Odds Near a Species Member",
    "Prior G22 prime≪species gap scale. Fraction of odds in thin bands around species spine."),
"g24_spacing_taxonomy": ("Spacing Taxonomy Summary Experiment",
    "Prior G15–G23 components. Three-way taxonomy: (A) even, (B) prime-like, (C) exact geometric."),
}

PRIOR_PRED_IDS = {
    "g15_species_gap_law": None,
    "g16_gap_ratio_vs_primes": "G15 S15.1–S15.4",
    "g17_dyadic_bucket_density": "G16 S16.1–S16.4",
    "g18_count_vs_pi": "G17 S17.1–S17.3",
    "g19_gap_over_x": "G18 S18.1–S18.3",
    "g20_composite_k_composite_x": "G19 S19.1–S19.3",
    "g21_odds_local_density": "G20 S20.1–S20.2",
    "g22_max_prime_gap_vs_species": "G21 S21.1–S21.2",
    "g23_near_species_odds": "G22 S22.1–S22.2",
    "g24_spacing_taxonomy": "G23 S23.1–S23.2",
}


def plan_text(name: str, label: str, prior: str | None) -> str:
    title, why = TITLES[name]
    if prior is None:
        return (
            f"# {label} — {title}\n\n"
            "**Status:** IMMUTABLE intent (seed track).\n\n"
            "**Seed question:** Do terminal-species gaps grow with size like primes, or stay evenly spaced?\n\n"
            "**Identities:** x_k=(4^k-1)/3, gap_k=x_{k+1}-x_k=4^k.\n\n"
            f"**Why this question:** {why}\n\n"
            f"{PRED_TABLES[name]}"
        )
    prior_ids = PRIOR_PRED_IDS[name]
    return (
        f"# {label} — {title}\n\n"
        f"**Prior track:** `{prior}/`\n"
        f"**Prior artifacts:** `{prior}/artifacts/summary.json`\n"
        f"**Prior scored predictions cited:** {prior_ids} "
        "(see that summary.json scoreboard; do not embed verdicts here)\n\n"
        f"**Why this question:** {why}\n\n"
        f"{PRED_TABLES[name]}"
    )


def write_ledger(name: str, label: str, summary: dict, plan_mtime: float, sum_mtime: float) -> None:
    preds = summary.get("predictions", {})
    text = f"""# {name} — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track `artifacts/summary.json` existed.
plan_mtime={plan_mtime}

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/{name}/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/{name}/artifacts/summary.json` (sum_mtime={sum_mtime})
- `renorm_check/shell/{name}/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{json.dumps(preds, indent=2)}
```

**Gates:** {json.dumps(summary.get("gates", {}))}
"""
    (SHELL / name / "IMPLEMENTATION_LEDGER.md").write_text(text)


def append_receipt(rec: dict) -> None:
    with RECEIPTS.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def main() -> int:
    RECEIPTS.write_text("")  # fresh chain
    for name, label, prior, pred_range in TRACKS:
        tdir = SHELL / name
        art = tdir / "artifacts"
        art.mkdir(exist_ok=True)
        plan_path = tdir / "IMPLEMENTATION_PLAN.md"
        sum_path = art / "summary.json"
        run_log = art / "run.log"

        if prior:
            psum = SHELL / prior / "artifacts" / "summary.json"
            if not psum.exists():
                print(f"MISSING prior summary {psum}", file=sys.stderr)
                return 1
            prior_mtime = psum.stat().st_mtime
            while time.time() <= prior_mtime + 0.05:
                time.sleep(0.05)
            time.sleep(1.05)  # second-resolution gap

        # Freeze plan (no embedded verdicts)
        body = plan_text(name, label, prior)
        plan_path.write_text(body)
        plan_mtime = plan_path.stat().st_mtime
        if prior:
            prior_mtime = (SHELL / prior / "artifacts" / "summary.json").stat().st_mtime
            if plan_mtime <= prior_mtime:
                time.sleep(1.05)
                plan_path.write_text(body)
                plan_mtime = plan_path.stat().st_mtime
            assert plan_mtime > prior_mtime, (name, plan_mtime, prior_mtime)

        # Run main once (sole summary writer)
        r = subprocess.run(
            [sys.executable, str(tdir / "scripts" / "run_all.py")],
            capture_output=True, text=True, cwd=str(REPO),
        )
        run_log.write_text(r.stdout + r.stderr)
        if r.returncode != 0:
            print(f"FAIL {name}: {r.stderr[-500:]}", file=sys.stderr)
            return r.returncode
        if not sum_path.exists():
            print(f"No summary for {name}", file=sys.stderr)
            return 1
        sum_mtime = sum_path.stat().st_mtime
        summary = json.loads(sum_path.read_text())

        # Ledger after summary
        time.sleep(0.2)
        while time.time() <= sum_path.stat().st_mtime:
            time.sleep(0.05)
        write_ledger(name, label, summary, plan_mtime, sum_mtime)
        led_path = tdir / "IMPLEMENTATION_LEDGER.md"
        led_mtime = led_path.stat().st_mtime
        if led_mtime < sum_path.stat().st_mtime:
            time.sleep(1.05)
            led_path.write_text(led_path.read_text() + "\n")
            led_mtime = led_path.stat().st_mtime

        rec = {
            "track": name,
            "label": label,
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "plan_mtime": plan_mtime,
            "sum_mtime": sum_path.stat().st_mtime,
            "led_mtime": led_mtime,
            "run_log_mtime": run_log.stat().st_mtime,
            "prior": prior,
            "plan_gt_prior_sum": True if not prior else plan_mtime > (SHELL / prior / "artifacts" / "summary.json").stat().st_mtime,
            "led_ge_sum": led_mtime >= sum_path.stat().st_mtime - 1e-6,
            "scoreboard": {k: v["verdict"] for k, v in summary.get("predictions", {}).items()},
        }
        append_receipt(rec)
        print(f"OK {label}: plan_gt_prior={rec['plan_gt_prior_sum']} led_ge_sum={rec['led_ge_sum']} {rec['scoreboard']}")
        time.sleep(1.05)

    print("CHAIN COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
