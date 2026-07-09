# g29_entry_a_distribution — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track artifacts/summary.json existed.
plan_mtime=1783588535.183789

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g29_entry_a_distribution/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g29_entry_a_distribution/artifacts/summary.json` (sum_mtime=1783588535.2420075)
- `renorm_check/shell/g29_entry_a_distribution/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S29.1": {
    "verdict": "CONFIRMED",
    "frac_a_ge2": 0.96,
    "confidence_prior": 0.7
  },
  "S29.2": {
    "verdict": "CONFIRMED",
    "frac_a1": 0.034,
    "confidence_prior": 0.65
  },
  "S29.3": {
    "verdict": "CONFIRMED",
    "n": 1000,
    "confidence_prior": 0.9
  }
}
```

**Gates:** {"G1": "PASS"}
