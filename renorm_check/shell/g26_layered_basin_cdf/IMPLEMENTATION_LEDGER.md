# g26_layered_basin_cdf — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track artifacts/summary.json existed.
plan_mtime=1783588527.8874006

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g26_layered_basin_cdf/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g26_layered_basin_cdf/artifacts/summary.json` (sum_mtime=1783588528.0386698)
- `renorm_check/shell/g26_layered_basin_cdf/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S26.1": {
    "verdict": "CONFIRMED",
    "f0": 0.0014,
    "f1": 0.0042,
    "confidence_prior": 0.9
  },
  "S26.2": {
    "verdict": "REFUTED",
    "f5": 0.0408,
    "confidence_prior": 0.55
  },
  "S26.3": {
    "verdict": "CONFIRMED",
    "f50": 0.8448,
    "confidence_prior": 0.6
  },
  "S26.4": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.99
  }
}
```

**Gates:** {"G1": "PASS", "X": 10000, "n_odds": 5000}
