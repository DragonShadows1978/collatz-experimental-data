# G28 — Fixed-width species isolation (repair G21)

**Prior track:** `g27_free_vs_odds_median_steps/`
**Prior artifacts:** `g27_free_vs_odds_median_steps/artifacts/summary.json`
**Prior scored predictions cited:** G27 S27.1–S27.4 (see that summary.json scoreboard; do not embed verdicts here)

**Why this question:** Prior G27 timing (S27.*). G21 half-gap windows failed isolation; test fixed W=1000 windows around x_k.

## Predictions (frozen after G27 results)
| ID | Claim | Conf |
|----|-------|------|
| S28.1 | For k=8..15, exactly one species in [x_k−1000, x_k+1000] | 0.80 |
| S28.2 | species fraction in that window ≤ 0.01 for each such k | 0.75 |
| S28.3 | no window has more than 2 species for k=8..15 | 0.90 |
