# G12 — Mersenne Pure-a=1 Prefix → Species

**Prior (G11):** After last up, median 62 steps to species; ~77% of deep
trajectories' length is post-last-up; 91.6% hit species within 100 post steps.
**Prior (G2):** x_L = 2^{L+1}-1 realizes L steps of a=1.

**Question:** After the pure a=1 block of Mersenne odds, how fast to species?
Does larger L delay species hit?

## Predictions
| ID | Claim | Conf |
|----|-------|------|
| U12.1 | For L=1..40, x_L eventually hits species within 100k steps | 0.85 |
| U12.2 | steps_to_species(x_L) ≥ L (a=1 block does not include species mid-block) | 0.70 |
| U12.3 | Correlation: steps_to_species tends to increase with L (Spearman > 0 on L=1..40) | 0.50 |
| U12.4 | Max steps_to_species for L≤40 ≤ 5000 | 0.45 |
