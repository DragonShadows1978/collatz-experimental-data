# g19_gap_over_x — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track `artifacts/summary.json` existed.
plan_mtime=1783567109.5631015

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g19_gap_over_x/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g19_gap_over_x/artifacts/summary.json` (sum_mtime=1783567109.5881717)
- `renorm_check/shell/g19_gap_over_x/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S19.1": {
    "verdict": "CONFIRMED",
    "rel_at_50": 3.0,
    "confidence_prior": 0.9
  },
  "S19.2": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.9
  },
  "S19.3": {
    "verdict": "CONFIRMED",
    "min_rel_float": 3.0,
    "confidence_prior": 0.99
  }
}
```

**Gates:** {"G1": "PASS"}
