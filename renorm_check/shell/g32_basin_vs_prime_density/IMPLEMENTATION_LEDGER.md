# g32_basin_vs_prime_density — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track artifacts/summary.json existed.
plan_mtime=1783588542.385421

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g32_basin_vs_prime_density/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g32_basin_vs_prime_density/artifacts/summary.json` (sum_mtime=1783588542.8056407)
- `renorm_check/shell/g32_basin_vs_prime_density/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S32.1": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.75
  },
  "S32.2": {
    "verdict": "REFUTED",
    "ratio": 3.2986167615947926,
    "confidence_prior": 0.6
  },
  "S32.3": {
    "verdict": "CONFIRMED",
    "f": 0.602,
    "confidence_prior": 0.55
  }
}
```

**Gates:** {"G1": "PASS"}
