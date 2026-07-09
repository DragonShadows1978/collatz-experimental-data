# g24_spacing_taxonomy — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track `artifacts/summary.json` existed.
plan_mtime=1783567121.2879574

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g24_spacing_taxonomy/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g24_spacing_taxonomy/artifacts/summary.json` (sum_mtime=1783567121.8740146)
- `renorm_check/shell/g24_spacing_taxonomy/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S24.1": {
    "verdict": "CONFIRMED",
    "variance": 44635804302900878699596173894280596,
    "confidence_prior": 0.99
  },
  "S24.2": {
    "verdict": "CONFIRMED",
    "species_gap_over_mean_prime_gap": 71358597.88548487,
    "confidence_prior": 0.85
  },
  "S24.3": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.99
  }
}
```

**Gates:** {"G1": "PASS"}
