# g21_odds_local_density — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track `artifacts/summary.json` existed.
plan_mtime=1783567114.2246099

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g21_odds_local_density/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g21_odds_local_density/artifacts/summary.json` (sum_mtime=1783567114.2520854)
- `renorm_check/shell/g21_odds_local_density/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S21.1": {
    "verdict": "REFUTED",
    "confidence_prior": 0.9
  },
  "S21.2": {
    "verdict": "REFUTED",
    "confidence_prior": 0.85
  }
}
```

**Gates:** {"G1": "PASS"}
