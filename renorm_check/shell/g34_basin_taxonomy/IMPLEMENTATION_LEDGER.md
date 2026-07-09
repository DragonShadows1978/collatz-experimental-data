# g34_basin_taxonomy — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track artifacts/summary.json existed.
plan_mtime=1783588547.5123556

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g34_basin_taxonomy/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g34_basin_taxonomy/artifacts/summary.json` (sum_mtime=1783588547.6581557)
- `renorm_check/shell/g34_basin_taxonomy/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S34.1": {
    "verdict": "CONFIRMED",
    "frac_spine": 0.0014,
    "confidence_prior": 0.95
  },
  "S34.2": {
    "verdict": "CONFIRMED",
    "frac_shell": 0.0042,
    "confidence_prior": 0.7
  },
  "S34.3": {
    "verdict": "CONFIRMED",
    "f100": 1.0,
    "confidence_prior": 0.75
  }
}
```

**Gates:** {"G1": "PASS", "X": 10000}
