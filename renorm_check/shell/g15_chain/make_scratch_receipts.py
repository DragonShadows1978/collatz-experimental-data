#!/usr/bin/env python3
"""Emit verification scratch files from stable disk state (does not re-run experiments)."""
from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path

SHELL = Path(__file__).resolve().parents[1]
REPO = SHELL.parents[1]
SCRATCH = Path(os.environ.get("SCRATCH", "/tmp/grok-goal-442fba59c68a/implementer"))
RECEIPTS = Path(__file__).resolve().parent / "chain_receipts.jsonl"

TRACKS = [
"g15_species_gap_law","g16_gap_ratio_vs_primes","g17_dyadic_bucket_density",
"g18_count_vs_pi","g19_gap_over_x","g20_composite_k_composite_x",
"g21_odds_local_density","g22_max_prime_gap_vs_species","g23_near_species_odds",
"g24_spacing_taxonomy"]


def main() -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)

    # 1 ten_tracks_list
    lines = ["# Ten tracks G15–G24", ""]
    for t in TRACKS:
        lines.append(t + "/")
        for f in ["IMPLEMENTATION_PLAN.md", "IMPLEMENTATION_LEDGER.md",
                  "artifacts/summary.json", "artifacts/run.log",
                  f"scripts/run_all.py", f"scripts/test_{t.split('_')[0]}.py"]:
            p = SHELL / t / f
            if p.exists():
                st = p.stat()
                lines.append(f"  {f}  mtime={st.st_mtime} size={st.st_size}")
    (SCRATCH / "ten_tracks_list.txt").write_text("\n".join(lines) + "\n")

    # 2 chain_citations — plan excerpts with prior citation
    cit = []
    for t in TRACKS:
        plan = (SHELL / t / "IMPLEMENTATION_PLAN.md").read_text()
        cit.append(f"===== {t} =====")
        # first 12 non-empty lines
        n = 0
        for line in plan.splitlines():
            if line.strip():
                cit.append(line)
                n += 1
                if n >= 12:
                    break
        cit.append("")
    (SCRATCH / "chain_citations.txt").write_text("\n".join(cit))

    # 3 synthesis_tail (full G15–G24 chain block, not truncated)
    gs = (SHELL / "GROK_SYNTHESIS.md").read_text()
    if "# Chain G15–G24" in gs:
        # last occurrence (file may have historical cruft above)
        idx = gs.rfind("# Chain G15–G24")
        tail = gs[idx:]
        (SCRATCH / "synthesis_tail.md").write_text(tail)
        # explicit per-track COMPLETE headers for verification step 3
        import re
        headers = re.findall(
            r"^## G(?:1[5-9]|2[0-4]) — .+\(\*\*COMPLETE\*\*\)\s*$",
            tail,
            flags=re.M,
        )
        (SCRATCH / "synthesis_g15_g24_headers.txt").write_text(
            "\n".join(headers) + f"\ncount={len(headers)}\n"
        )
    else:
        (SCRATCH / "synthesis_tail.md").write_text("MISSING G15–G24 section\n")

    # 4 tests (pure compute — must not rewrite summaries)
    # snapshot summary mtimes before tests
    before = {t: (SHELL / t / "artifacts" / "summary.json").stat().st_mtime for t in TRACKS}
    test_parts = []
    for t in TRACKS:
        lab = t.split("_")[0]
        r = subprocess.run(
            [sys.executable, str(SHELL / t / "scripts" / f"test_{lab}.py")],
            capture_output=True, text=True, cwd=str(REPO),
        )
        test_parts.append(f"=== {lab} rc={r.returncode} ===\n{r.stdout}{r.stderr}")
        # also per-track logs
        (SCRATCH / f"{lab}_tests.log").write_text(r.stdout + r.stderr)
        # copy run.log to scratch
        rl = SHELL / t / "artifacts" / "run.log"
        if rl.exists():
            (SCRATCH / f"{lab}_run.log").write_text(rl.read_text())
    (SCRATCH / "all_ten_tests.log").write_text("\n".join(test_parts))
    after = {t: (SHELL / t / "artifacts" / "summary.json").stat().st_mtime for t in TRACKS}
    stable = all(before[t] == after[t] for t in TRACKS)
    (SCRATCH / "summary_mtime_stable_after_tests.txt").write_text(
        f"stable={stable}\n" + "\n".join(f"{t}: {before[t]} -> {after[t]}" for t in TRACKS) + "\n"
    )

    # 5 spot_checks — one numerical claim per track from artifact JSON
    spots = []
    s15 = json.loads((SHELL / "g15_species_gap_law" / "artifacts" / "summary.json").read_text())
    spots.append(f"G15: S15.1={s15['predictions']['S15.1']['verdict']}; count_le_1e12={s15['predictions']['S15.4'].get('count_le_1e12')}; gap_ln_at_10={s15['predictions']['S15.3'].get('gap_ln_at_10')}")
    # algebraic re-derive
    for k in (1, 5, 10):
        gap = 4**k
        x = (4**k - 1) // 3
        spots.append(f"G15 re-derive k={k}: x={x} gap={gap} (4^k)")

    s16 = json.loads((SHELL / "g16_gap_ratio_vs_primes" / "artifacts" / "summary.json").read_text())
    spots.append(f"G16: frac_near_4={s16['predictions']['S16.2'].get('frac_near_4')}; stdev_species={s16['predictions']['S16.4'].get('stdev_species')}")

    s17 = json.loads((SHELL / "g17_dyadic_bucket_density" / "artifacts" / "summary.json").read_text())
    spots.append(f"G17: frac_exactly_one={s17['predictions']['S17.2'].get('frac_exactly_one')}; sample buckets={s17.get('buckets_sample')}")

    s18 = json.loads((SHELL / "g18_count_vs_pi" / "artifacts" / "summary.json").read_text())
    spots.append(f"G18: count@1e6={s18['predictions']['S18.2'].get('count')} pi={s18['predictions']['S18.2'].get('pi')}")

    s19 = json.loads((SHELL / "g19_gap_over_x" / "artifacts" / "summary.json").read_text())
    spots.append(f"G19: rel_at_50={s19['predictions']['S19.1'].get('rel_at_50')}; rel_sample={s19.get('rel_sample')}")

    s20 = json.loads((SHELL / "g20_composite_k_composite_x" / "artifacts" / "summary.json").read_text())
    spots.append(f"G20: n_composite_k={s20['predictions']['S20.1'].get('n_composite_k')}; n_with_factor={s20['predictions']['S20.2'].get('n_with_factor')}")

    s21 = json.loads((SHELL / "g21_odds_local_density" / "artifacts" / "summary.json").read_text())
    spots.append(f"G21: S21.1={s21['predictions']['S21.1']['verdict']} S21.2={s21['predictions']['S21.2']['verdict']}; row0={s21.get('rows', [None])[0]}")

    s22 = json.loads((SHELL / "g22_max_prime_gap_vs_species" / "artifacts" / "summary.json").read_text())
    spots.append(f"G22: rows_sample={s22.get('rows', [])[:3]}")

    s23 = json.loads((SHELL / "g23_near_species_odds" / "artifacts" / "summary.json").read_text())
    spots.append(f"G23: frac_1e6={s23['predictions']['S23.1'].get('frac_1e6')}; fracs={s23.get('fracs')}")

    s24 = json.loads((SHELL / "g24_spacing_taxonomy" / "artifacts" / "summary.json").read_text())
    spots.append(f"G24: taxonomy={s24.get('taxonomy')}; ratio={s24['predictions']['S24.2'].get('species_gap_over_mean_prime_gap')}")
    (SCRATCH / "spot_checks.txt").write_text("\n".join(spots) + "\n")

    # 6 seq_chain_verify from receipts + live mtimes
    ver = []
    all_ok = True
    if RECEIPTS.exists():
        for line in RECEIPTS.read_text().splitlines():
            if line.strip():
                ver.append(line)
    prev_sm = None
    for t in TRACKS:
        pm = (SHELL / t / "IMPLEMENTATION_PLAN.md").stat().st_mtime
        sm = (SHELL / t / "artifacts" / "summary.json").stat().st_mtime
        lm = (SHELL / t / "IMPLEMENTATION_LEDGER.md").stat().st_mtime
        rlm = (SHELL / t / "artifacts" / "run.log").stat().st_mtime if (SHELL / t / "artifacts" / "run.log").exists() else None
        pok = True if prev_sm is None else pm > prev_sm
        lok = lm >= sm - 1e-6
        # plan before summary for this track
        plan_before_sum = pm <= sm + 1e-3 or pm < sm
        # run.log should be ~same era as summary (chain wrote both)
        run_ok = rlm is not None and abs(rlm - sm) < 5.0
        ok = pok and lok and run_ok
        all_ok &= ok
        ver.append(f"DISK {t}: plan={pm} sum={sm} led={lm} runlog={rlm} plan>prior_sum={pok} led>=sum={lok} runlog~sum={run_ok}")
        # plan must not embed verdict dicts
        plan_txt = (SHELL / t / "IMPLEMENTATION_PLAN.md").read_text()
        no_verdict_dict = "CONFIRMED" not in plan_txt and "REFUTED" not in plan_txt
        ver.append(f"  plan_has_no_verdict_words={no_verdict_dict}")
        if not no_verdict_dict and t != "g15_species_gap_law":
            # seed plan also should not have CONFIRMED
            all_ok = False
            ver.append("  FAIL: plan embeds CONFIRMED/REFUTED")
        elif "CONFIRMED" in plan_txt or "REFUTED" in plan_txt:
            all_ok = False
            ver.append("  FAIL: plan embeds CONFIRMED/REFUTED")
        prev_sm = sm
    ver.append(f"summary_mtime_stable_after_tests={stable}")
    ver.append(f"ALL_OK={all_ok and stable}")
    (SCRATCH / "seq_chain_verify.txt").write_text("\n".join(ver) + "\n")
    print(f"ALL_OK={all_ok and stable} stable_after_tests={stable}")
    print((SCRATCH / "seq_chain_verify.txt").read_text())
    return 0 if (all_ok and stable) else 1


if __name__ == "__main__":
    raise SystemExit(main())
