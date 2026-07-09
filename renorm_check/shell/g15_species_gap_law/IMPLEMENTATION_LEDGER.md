# g15_species_gap_law — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track `artifacts/summary.json` existed.
plan_mtime=1783567099.522947

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g15_species_gap_law/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g15_species_gap_law/artifacts/summary.json` (sum_mtime=1783567099.547812)
- `renorm_check/shell/g15_species_gap_law/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S15.1": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.99
  },
  "S15.2": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.9
  },
  "S15.3": {
    "verdict": "CONFIRMED",
    "gap_ln_at_10": 82148.92357835268,
    "confidence_prior": 0.85
  },
  "S15.4": {
    "verdict": "CONFIRMED",
    "count_le_1e12": 20,
    "kmax": 20,
    "confidence_prior": 0.95
  }
}
```

**Gates:** {"G1": "PASS"}
