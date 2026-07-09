# g28_fixed_width_isolation — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track artifacts/summary.json existed.
plan_mtime=1783588532.8197482

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g28_fixed_width_isolation/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g28_fixed_width_isolation/artifacts/summary.json` (sum_mtime=1783588532.8779101)
- `renorm_check/shell/g28_fixed_width_isolation/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S28.1": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.8
  },
  "S28.2": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.75
  },
  "S28.3": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.9
  }
}
```

**Gates:** {"G1": "PASS", "W": 1000}
