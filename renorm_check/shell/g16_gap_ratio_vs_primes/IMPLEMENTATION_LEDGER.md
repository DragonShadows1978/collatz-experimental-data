# g16_gap_ratio_vs_primes — Implementation Ledger

### Freeze
Plan frozen in IMPLEMENTATION_PLAN.md after prior-track `artifacts/summary.json` existed.
plan_mtime=1783567101.8546026

### Execution
**Commands (chain sole writer):**
```bash
python3 renorm_check/shell/g16_gap_ratio_vs_primes/scripts/run_all.py
```
**Artifacts:**
- `renorm_check/shell/g16_gap_ratio_vs_primes/artifacts/summary.json` (sum_mtime=1783567102.0167391)
- `renorm_check/shell/g16_gap_ratio_vs_primes/artifacts/run.log`

**Scoreboard (from summary.json after this run):**
```json
{
  "S16.1": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.99
  },
  "S16.2": {
    "verdict": "CONFIRMED",
    "frac_near_4": 0.021708112515287405,
    "confidence_prior": 0.6
  },
  "S16.3": {
    "verdict": "CONFIRMED",
    "stdev_log_prime_ratios": 1.1947343417303817,
    "confidence_prior": 0.55
  },
  "S16.4": {
    "verdict": "CONFIRMED",
    "stdev_species": 0.0,
    "confidence_prior": 0.99
  }
}
```

**Gates:** {"G1": "PASS", "n_primes": 78498}
