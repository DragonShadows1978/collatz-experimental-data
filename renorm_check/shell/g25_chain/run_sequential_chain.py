#!/usr/bin/env python3
"""Sole writer of G25–G34 summaries/ledgers/run.logs. Plans cite prior IDs+path only."""
from __future__ import annotations
import json, time, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

SHELL = Path(__file__).resolve().parents[1]
REPO = SHELL.parents[1]
RECEIPTS = Path(__file__).resolve().parent / "chain_receipts.jsonl"

TRACKS = [
    ("g25_immediate_basin_shell", "G25", "g24_spacing_taxonomy"),
    ("g26_layered_basin_cdf", "G26", "g25_immediate_basin_shell"),
    ("g27_free_vs_odds_median_steps", "G27", "g26_layered_basin_cdf"),
    ("g28_fixed_width_isolation", "G28", "g27_free_vs_odds_median_steps"),
    ("g29_entry_a_distribution", "G29", "g28_fixed_width_isolation"),
    ("g30_shell_preimage_a", "G30", "g29_entry_a_distribution"),
    ("g31_multistep_shell_density", "G31", "g30_shell_preimage_a"),
    ("g32_basin_vs_prime_density", "G32", "g31_multistep_shell_density"),
    ("g33_steps_vs_bitlength", "G33", "g32_basin_vs_prime_density"),
    ("g34_basin_taxonomy", "G34", "g33_steps_vs_bitlength"),
]

TITLES = {
"g25_immediate_basin_shell": ("Immediate basin shell B1 density",
    "G24 standing picture: spine is C_exact_geometric and O(log X)-thin. Measure density of odds that are species or map to species in one odd-step (immediate shell) vs spine."),
"g26_layered_basin_cdf": ("Layered basin CDF among odds",
    "Prior G25 S25.1–S25.4 (immediate shell thicker than spine). Measure fraction of odds with steps_to_species ≤ L on a layer ladder."),
"g27_free_vs_odds_median_steps": ("Free-orbit vs odds median steps-to-species",
    "Prior G26 layered CDF (S26.*). Compare median steps on free sample vs odds ≤10^4."),
"g28_fixed_width_isolation": ("Fixed-width species isolation (repair G21)",
    "Prior G27 timing (S27.*). G21 half-gap windows failed isolation; test fixed W=1000 windows around x_k."),
"g29_entry_a_distribution": ("Entry valuation a into species",
    "Prior G28 fixed-width isolation (S28.*). Measure last-step a distribution for odds hitting species."),
"g30_shell_preimage_a": ("Reverse preimage a of species members",
    "Prior G29 entry-a (S29.*). Algebraic reverse preimages of species: a-distribution."),
"g31_multistep_shell_density": ("Multi-step shell density growth",
    "Prior G30 reverse preimage structure (S30.*). Growth of basin fraction with reverse/forward depth L=0..10."),
"g32_basin_vs_prime_density": ("Basin density vs prime density (comparison sample)",
    "Prior G31 multi-step growth (S31.*). Compare f(steps≤20) to π(X)/X — primes as density reference only, not prediction."),
"g33_steps_vs_bitlength": ("Steps-to-species vs bit-length (free sample)",
    "Prior G32 basin vs prime density (S32.*). Spearman correlation of steps with bit_length on free starts."),
"g34_basin_taxonomy": ("Basin taxonomy summary",
    "Prior G25–G33 components. Three-way taxonomy: spine thin / shell moderate / bulk nearly full."),
}

PRED = {
"g25_immediate_basin_shell": """## Predictions (frozen after G24 results)
| ID | Claim | Conf |
|----|-------|------|
| S25.1 | shell_count / spine_count ≥ 2 for X in {10^3,10^4,10^5} | 0.85 |
| S25.2 | frac_shell(10^5) < frac_shell(10^3) | 0.60 |
| S25.3 | frac_shell(10^5) > frac_spine(10^5) | 0.95 |
| S25.4 | frac_shell(10^3) > 0.01 | 0.70 |
""",
"g26_layered_basin_cdf": """## Predictions (frozen after G25 results)
| ID | Claim | Conf |
|----|-------|------|
| S26.1 | Among odds ≤10^4, frac(steps≤0) < frac(steps≤1) | 0.90 |
| S26.2 | frac(steps≤5) ≥ 0.05 | 0.55 |
| S26.3 | frac(steps≤50) ≥ 0.50 | 0.60 |
| S26.4 | layer fractions nondecreasing on ladder | 0.99 |
""",
"g27_free_vs_odds_median_steps": """## Predictions (frozen after G26 results)
| ID | Claim | Conf |
|----|-------|------|
| S27.1 | median steps among hit odds ≤10^4 is ≤ 100 | 0.70 |
| S27.2 | median steps among hit free starts is ≤ 300 | 0.65 |
| S27.3 | median free > median odds | 0.55 |
| S27.4 | free-sample hit rate ≥ 0.99 | 0.90 |
""",
"g28_fixed_width_isolation": """## Predictions (frozen after G27 results)
| ID | Claim | Conf |
|----|-------|------|
| S28.1 | For k=8..15, exactly one species in [x_k−1000, x_k+1000] | 0.80 |
| S28.2 | species fraction in that window ≤ 0.01 for each such k | 0.75 |
| S28.3 | no window has more than 2 species for k=8..15 | 0.90 |
""",
"g29_entry_a_distribution": """## Predictions (frozen after G28 results)
| ID | Claim | Conf |
|----|-------|------|
| S29.1 | Among odds 1..2001 hitting species in ≤200 steps, frac(a≥2) ≥ 0.70 | 0.70 |
| S29.2 | frac(a=1) ≤ 0.30 | 0.65 |
| S29.3 | n_hit ≥ 500 | 0.90 |
""",
"g30_shell_preimage_a": """## Predictions (frozen after G29 results)
| ID | Claim | Conf |
|----|-------|------|
| S30.1 | ≥20 reverse preimages of species k=1..11 with y≤10^6 | 0.90 |
| S30.2 | frac of those with a≥2 ≥ 0.80 | 0.70 |
| S30.3 | frac with a=1 ≤ 0.25 | 0.60 |
""",
"g31_multistep_shell_density": """## Predictions (frozen after G30 results)
| ID | Claim | Conf |
|----|-------|------|
| S31.1 | frac(steps≤L) nondecreasing for L in {0,1,2,3,5,10} on odds ≤10^4 | 0.99 |
| S31.2 | frac(steps≤2) ≥ 2·frac(steps≤0) (or frac0=0 and frac2>0) | 0.70 |
| S31.3 | frac(steps≤10) ≥ 0.10 | 0.55 |
| S31.4 | frac(steps≤0) < 0.01 | 0.85 |
""",
"g32_basin_vs_prime_density": """## Predictions (frozen after G31 results)
| ID | Claim | Conf |
|----|-------|------|
| S32.1 | f(steps≤20) > π(X)/X for X in {10^3,10^4,10^5} | 0.75 |
| S32.2 | f_basin/prime_dens at 10^4 > 5 | 0.60 |
| S32.3 | f(steps≤20) at 10^3 > 0.05 | 0.55 |
""",
"g33_steps_vs_bitlength": """## Predictions (frozen after G32 results)
| ID | Claim | Conf |
|----|-------|------|
| S33.1 | |Spearman(rho)| of (bit_length, steps) on free hits < 0.85 | 0.70 |
| S33.2 | rho > −0.2 | 0.55 |
| S33.3 | mean steps in high-bit tercile ≥ 0.5 · mean low-bit tercile | 0.55 |
""",
"g34_basin_taxonomy": """## Predictions (frozen after G33 results)
| ID | Claim | Conf |
|----|-------|------|
| S34.1 | frac_spine among odds ≤10^4 < 0.01 | 0.95 |
| S34.2 | frac_immediate_shell in (frac_spine, 0.50) | 0.70 |
| S34.3 | frac(steps≤100) ≥ 0.90 among odds ≤10^4 | 0.75 |
""",
}

PRIOR_IDS = {
    "g25_immediate_basin_shell": "G24 S24.1–S24.3",
    "g26_layered_basin_cdf": "G25 S25.1–S25.4",
    "g27_free_vs_odds_median_steps": "G26 S26.1–S26.4",
    "g28_fixed_width_isolation": "G27 S27.1–S27.4",
    "g29_entry_a_distribution": "G28 S28.1–S28.3",
    "g30_shell_preimage_a": "G29 S29.1–S29.3",
    "g31_multistep_shell_density": "G30 S30.1–S30.3",
    "g32_basin_vs_prime_density": "G31 S31.1–S31.4",
    "g33_steps_vs_bitlength": "G32 S32.1–S32.3",
    "g34_basin_taxonomy": "G33 S33.1–S33.3",
}


def plan_text(name: str, label: str, prior: str) -> str:
    title, why = TITLES[name]
    return (
        f"# {label} — {title}\n\n"
        f"**Prior track:** `{prior}/`\n"
        f"**Prior artifacts:** `{prior}/artifacts/summary.json`\n"
        f"**Prior scored predictions cited:** {PRIOR_IDS[name]} "
        "(see that summary.json scoreboard; do not embed verdicts here)\n\n"
        f"**Why this question:** {why}\n\n"
        f"{PRED[name]}"
    )


def write_ledger(name: str, label: str, summary: dict, plan_mtime: float, sum_mtime: float) -> None:
    preds = summary.get("predictions", {})
    text = f"""# {name} — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track artifacts/summary.json existed.
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


def main() -> int:
    RECEIPTS.write_text("")
    for name, label, prior in TRACKS:
        tdir = SHELL / name
        art = tdir / "artifacts"
        art.mkdir(exist_ok=True)
        plan_path = tdir / "IMPLEMENTATION_PLAN.md"
        sum_path = art / "summary.json"
        run_log = art / "run.log"

        psum = SHELL / prior / "artifacts" / "summary.json"
        if not psum.exists():
            print(f"MISSING prior {psum}", file=sys.stderr)
            return 1
        prior_mtime = psum.stat().st_mtime
        while time.time() <= prior_mtime + 0.05:
            time.sleep(0.05)
        time.sleep(1.05)

        body = plan_text(name, label, prior)
        plan_path.write_text(body)
        plan_mtime = plan_path.stat().st_mtime
        prior_mtime = psum.stat().st_mtime
        if plan_mtime <= prior_mtime:
            time.sleep(1.05)
            plan_path.write_text(body)
            plan_mtime = plan_path.stat().st_mtime
        assert plan_mtime > prior_mtime, (name, plan_mtime, prior_mtime)

        r = subprocess.run(
            [sys.executable, str(tdir / "scripts" / "run_all.py")],
            capture_output=True, text=True, cwd=str(REPO),
        )
        run_log.write_text(r.stdout + r.stderr)
        if r.returncode != 0:
            print(f"FAIL {name} rc={r.returncode}\n{r.stderr[-800:]}\n{r.stdout[-800:]}", file=sys.stderr)
            return r.returncode
        if not sum_path.exists():
            print(f"No summary {name}", file=sys.stderr)
            return 1
        summary = json.loads(sum_path.read_text())
        sum_mtime = sum_path.stat().st_mtime

        time.sleep(0.2)
        while time.time() <= sum_path.stat().st_mtime:
            time.sleep(0.05)
        write_ledger(name, label, summary, plan_mtime, sum_mtime)
        led_path = tdir / "IMPLEMENTATION_LEDGER.md"
        if led_path.stat().st_mtime < sum_path.stat().st_mtime:
            time.sleep(1.05)
            led_path.write_text(led_path.read_text() + "\n")

        sb = {k: v["verdict"] for k, v in summary.get("predictions", {}).items()}
        rec = {
            "track": name, "label": label,
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "plan_mtime": plan_mtime,
            "sum_mtime": sum_path.stat().st_mtime,
            "led_mtime": led_path.stat().st_mtime,
            "plan_gt_prior_sum": plan_mtime > (SHELL / prior / "artifacts" / "summary.json").stat().st_mtime,
            "led_ge_sum": led_path.stat().st_mtime >= sum_path.stat().st_mtime - 1e-6,
            "scoreboard": sb,
        }
        with RECEIPTS.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"OK {label}: prior_ok={rec['plan_gt_prior_sum']} led_ok={rec['led_ge_sum']} {sb}")
        time.sleep(1.05)

    print("CHAIN COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
