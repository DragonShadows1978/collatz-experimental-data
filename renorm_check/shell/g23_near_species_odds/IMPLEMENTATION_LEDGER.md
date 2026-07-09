# g23_near_species_odds — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track `artifacts/summary.json` existed.
plan_mtime=1783567118.9524267

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g23_near_species_odds/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g23_near_species_odds/artifacts/summary.json` (sum_mtime=1783567118.9817016)
- `renorm_check/shell/g23_near_species_odds/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S23.1": {
    "verdict": "REFUTED",
    "frac_1e6": 0.069908,
    "confidence_prior": 0.7
  },
  "S23.2": {
    "verdict": "CONFIRMED",
    "fracs": {
      "10000": 0.1094,
      "100000": 0.17478,
      "1000000": 0.069908
    },
    "confidence_prior": 0.55
  }
}
```

**Gates:** {"G1": "PASS"}
