# g27_free_vs_odds_median_steps — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track artifacts/summary.json existed.
plan_mtime=1783588530.345435

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g27_free_vs_odds_median_steps/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g27_free_vs_odds_median_steps/artifacts/summary.json` (sum_mtime=1783588530.511349)
- `renorm_check/shell/g27_free_vs_odds_median_steps/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S27.1": {
    "verdict": "CONFIRMED",
    "med_odds": 26,
    "confidence_prior": 0.7
  },
  "S27.2": {
    "verdict": "CONFIRMED",
    "med_free": 70,
    "confidence_prior": 0.65
  },
  "S27.3": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.55
  },
  "S27.4": {
    "verdict": "CONFIRMED",
    "free_hit_rate": 1.0,
    "confidence_prior": 0.9
  }
}
```

**Gates:** {"G1": "PASS", "n_free_hit": 308}
