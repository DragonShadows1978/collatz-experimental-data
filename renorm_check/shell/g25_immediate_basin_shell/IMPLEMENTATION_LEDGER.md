# g25_immediate_basin_shell — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track artifacts/summary.json existed.
plan_mtime=1783588525.503143

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g25_immediate_basin_shell/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g25_immediate_basin_shell/artifacts/summary.json` (sum_mtime=1783588525.57965)
- `renorm_check/shell/g25_immediate_basin_shell/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S25.1": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.85
  },
  "S25.2": {
    "verdict": "CONFIRMED",
    "frac_1e3": 0.028,
    "frac_1e5": 0.00062,
    "confidence_prior": 0.6
  },
  "S25.3": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.95
  },
  "S25.4": {
    "verdict": "CONFIRMED",
    "frac_1e3": 0.028,
    "confidence_prior": 0.7
  }
}
```

**Gates:** {"G1": "PASS"}
