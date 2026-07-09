# g33_steps_vs_bitlength — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track artifacts/summary.json existed.
plan_mtime=1783588545.1453285

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g33_steps_vs_bitlength/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g33_steps_vs_bitlength/artifacts/summary.json` (sum_mtime=1783588545.2048225)
- `renorm_check/shell/g33_steps_vs_bitlength/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S33.1": {
    "verdict": "CONFIRMED",
    "rho": 0.4892245514584112,
    "confidence_prior": 0.7
  },
  "S33.2": {
    "verdict": "CONFIRMED",
    "rho": 0.4892245514584112,
    "confidence_prior": 0.55
  },
  "S33.3": {
    "verdict": "CONFIRMED",
    "mean_low": 61.088235294117645,
    "mean_high": 102.98039215686275,
    "confidence_prior": 0.55
  }
}
```

**Gates:** {"G1": "PASS", "n": 308}
