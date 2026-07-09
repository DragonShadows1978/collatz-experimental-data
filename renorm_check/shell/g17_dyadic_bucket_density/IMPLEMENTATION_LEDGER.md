# g17_dyadic_bucket_density — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track `artifacts/summary.json` existed.
plan_mtime=1783567104.3248057

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g17_dyadic_bucket_density/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g17_dyadic_bucket_density/artifacts/summary.json` (sum_mtime=1783567104.3514295)
- `renorm_check/shell/g17_dyadic_bucket_density/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S17.1": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.9
  },
  "S17.2": {
    "verdict": "CONFIRMED",
    "frac_exactly_one": 1.0,
    "confidence_prior": 0.7
  },
  "S17.3": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.95
  }
}
```

**Gates:** {"G1": "PASS"}
