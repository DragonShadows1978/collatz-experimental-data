# G8 — Upcrossings vs max C (packing)

**Prior (G7):** Ceiling sojourns end only via support or a≥3; flats (a=2,c=2) keep ceiling without up. G6: ~61% of ceil-drops become ups.

**Algebra probe:** Each up raises C by exactly 1 (Δd=c−a=1). From C=0, conjecturally **n_ups = max_C**.

**Question:** Confirm identity; measure ups per 53-step window and max ups in free orbits vs greedy dual 31.

## Predictions
| ID | Claim | Conf |
|----|-------|------|
| T8.1 | On all free starts: n_ups == max(0, max_d) (ups raise max by 1; negative max ⇒ 0 ups) | 0.90 |
| T8.2 | Mean ups per start < 30 for random odds (max_steps 8000) | 0.70 |
| T8.3 | Mean ups per start for high-reserve ≥ 15 | 0.60 |
| T8.4 | Max ups in any 53-step window on free sample ≤ 12 | 0.50 |
