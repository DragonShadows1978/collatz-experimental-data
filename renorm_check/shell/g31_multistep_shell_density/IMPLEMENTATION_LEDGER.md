# g31_multistep_shell_density — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track artifacts/summary.json existed.
plan_mtime=1783588539.9251902

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g31_multistep_shell_density/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g31_multistep_shell_density/artifacts/summary.json` (sum_mtime=1783588540.0781922)
- `renorm_check/shell/g31_multistep_shell_density/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S31.1": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.99
  },
  "S31.2": {
    "verdict": "CONFIRMED",
    "f0": 0.0014,
    "f2": 0.0096,
    "confidence_prior": 0.7
  },
  "S31.3": {
    "verdict": "CONFIRMED",
    "f10": 0.1524,
    "confidence_prior": 0.55
  },
  "S31.4": {
    "verdict": "CONFIRMED",
    "f0": 0.0014,
    "confidence_prior": 0.85
  }
}
```

**Gates:** {"G1": "PASS", "X": 10000}
