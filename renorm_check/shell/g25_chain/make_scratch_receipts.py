#!/usr/bin/env python3
"""Scratch receipts for G25–G34 verification (does not re-run experiments for summaries)."""
from __future__ import annotations
import json, os, re, subprocess, sys
from pathlib import Path

SHELL = Path(__file__).resolve().parents[1]
REPO = SHELL.parents[1]
SCRATCH = Path(os.environ.get("SCRATCH", "/tmp/grok-goal-04053eac7d02/implementer"))
RECEIPTS = Path(__file__).resolve().parent / "chain_receipts.jsonl"

TRACKS = [
"g25_immediate_basin_shell","g26_layered_basin_cdf","g27_free_vs_odds_median_steps",
"g28_fixed_width_isolation","g29_entry_a_distribution","g30_shell_preimage_a",
"g31_multistep_shell_density","g32_basin_vs_prime_density","g33_steps_vs_bitlength",
"g34_basin_taxonomy"]


def main() -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    lines = ["# Ten tracks G25–G34", ""]
    for t in TRACKS:
        lines.append(t + "/")
        for f in ["IMPLEMENTATION_PLAN.md","IMPLEMENTATION_LEDGER.md",
                  "artifacts/summary.json","artifacts/run.log",
                  f"scripts/run_all.py", f"scripts/test_{t.split('_')[0]}.py"]:
            p = SHELL/t/f
            if p.exists():
                st = p.stat()
                lines.append(f"  {f}  mtime={st.st_mtime} size={st.st_size}")
    (SCRATCH/"ten_tracks_list.txt").write_text("\n".join(lines)+"\n")

    cit = []
    for t in TRACKS:
        plan = (SHELL/t/"IMPLEMENTATION_PLAN.md").read_text()
        cit.append(f"===== {t} =====")
        n = 0
        for line in plan.splitlines():
            if line.strip():
                cit.append(line); n += 1
                if n >= 12: break
        has_v = ("CONFIRMED" in plan) or ("REFUTED" in plan)
        cit.append(f"  plan_embeds_verdict_words={has_v}")
        cit.append("")
    (SCRATCH/"chain_citations.txt").write_text("\n".join(cit))

    gs = (SHELL/"GROK_SYNTHESIS.md").read_text()
    if "# Chain G25–G34" in gs:
        idx = gs.rfind("# Chain G25–G34")
        (SCRATCH/"synthesis_tail.md").write_text(gs[idx:])
        headers = re.findall(r"^## G(?:2[5-9]|3[0-4]) — .+\(\*\*COMPLETE\*\*\)\s*$", gs[idx:], re.M)
        (SCRATCH/"synthesis_headers.txt").write_text("\n".join(headers)+f"\ncount={len(headers)}\n")
    else:
        (SCRATCH/"synthesis_tail.md").write_text("MISSING G25–G34\n")
        (SCRATCH/"synthesis_headers.txt").write_text("count=0\n")

    before = {t: (SHELL/t/"artifacts"/"summary.json").stat().st_mtime for t in TRACKS}
    parts = []
    for t in TRACKS:
        lab = t.split("_")[0]
        r = subprocess.run([sys.executable, str(SHELL/t/"scripts"/f"test_{lab}.py")],
                           capture_output=True, text=True, cwd=str(REPO))
        parts.append(f"=== {lab} rc={r.returncode} ===\n{r.stdout}{r.stderr}")
        (SCRATCH/f"{lab}_tests.log").write_text(r.stdout+r.stderr)
        rl = SHELL/t/"artifacts"/"run.log"
        if rl.exists():
            (SCRATCH/f"{lab}_run.log").write_text(rl.read_text())
    (SCRATCH/"all_ten_tests.log").write_text("\n".join(parts))
    after = {t: (SHELL/t/"artifacts"/"summary.json").stat().st_mtime for t in TRACKS}
    stable = all(before[t]==after[t] for t in TRACKS)
    (SCRATCH/"summary_mtime_stable_after_tests.txt").write_text(
        f"stable={stable}\n"+"\n".join(f"{t}: {before[t]} -> {after[t]}" for t in TRACKS)+"\n")

    spots = []
    for t in TRACKS:
        s = json.loads((SHELL/t/"artifacts"/"summary.json").read_text())
        sb = {k:v["verdict"] for k,v in s["predictions"].items()}
        spots.append(f"{t}: {sb}")
        # one extra numeric
        if "rows" in s:
            rows = s["rows"]
            if isinstance(rows, dict):
                spots.append(f"  rows_keys={list(rows.keys())[:5]}")
            else:
                spots.append(f"  rows_n={len(rows)} sample0={rows[0] if rows else None}")
        if "frac" in s:
            spots.append(f"  frac={s['frac']}")
        if "taxonomy" in s:
            spots.append(f"  taxonomy={s['taxonomy']}")
        if "rho" in s:
            spots.append(f"  rho={s['rho']}")
        if "med_odds" in s:
            spots.append(f"  med_odds={s['med_odds']} med_free={s.get('med_free')}")
    (SCRATCH/"spot_checks.txt").write_text("\n".join(spots)+"\n")

    ver = []
    all_ok = True
    if RECEIPTS.exists():
        ver.extend(RECEIPTS.read_text().splitlines())
    prev_sm = None
    for t in TRACKS:
        pm = (SHELL/t/"IMPLEMENTATION_PLAN.md").stat().st_mtime
        sm = (SHELL/t/"artifacts"/"summary.json").stat().st_mtime
        lm = (SHELL/t/"IMPLEMENTATION_LEDGER.md").stat().st_mtime
        pok = True if prev_sm is None else pm > prev_sm
        # G25 prior is g24
        if t == TRACKS[0]:
            p24 = (SHELL/"g24_spacing_taxonomy"/"artifacts"/"summary.json").stat().st_mtime
            pok = pm > p24
        lok = lm >= sm - 1e-6
        plan = (SHELL/t/"IMPLEMENTATION_PLAN.md").read_text()
        no_v = ("CONFIRMED" not in plan) and ("REFUTED" not in plan)
        ok = pok and lok and no_v
        all_ok &= ok
        ver.append(f"DISK {t}: plan>prior={pok} led>=sum={lok} no_verdict_in_plan={no_v}")
        prev_sm = sm
    all_ok &= stable
    ver.append(f"summary_mtime_stable_after_tests={stable}")
    ver.append(f"ALL_OK={all_ok}")
    (SCRATCH/"seq_chain_verify.txt").write_text("\n".join(ver)+"\n")
    print(f"ALL_OK={all_ok} stable={stable}")
    return 0 if all_ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
