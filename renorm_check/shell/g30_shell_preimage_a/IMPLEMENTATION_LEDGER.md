# g30_shell_preimage_a — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track artifacts/summary.json existed.
plan_mtime=1783588537.549676

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g30_shell_preimage_a/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g30_shell_preimage_a/artifacts/summary.json` (sum_mtime=1783588537.6135073)
- `renorm_check/shell/g30_shell_preimage_a/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S30.1": {
    "verdict": "CONFIRMED",
    "n": 44,
    "confidence_prior": 0.9
  },
  "S30.2": {
    "verdict": "CONFIRMED",
    "frac_a_ge2": 0.9090909090909091,
    "confidence_prior": 0.7
  },
  "S30.3": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.6
  }
}
```

**Gates:** {"G1": "PASS"}
