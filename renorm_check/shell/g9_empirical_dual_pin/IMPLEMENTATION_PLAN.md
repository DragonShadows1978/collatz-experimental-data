# G9 — Empirical a-Pin Dual Walker

**Prior (G8):** n_ups = max(0,max_d); random mean ups tiny (0.83); HR ~25; max ups in 53-step window = **23** (near greedy 31).  
**Prior (G6):** At ceiling+drop, a ~ hist (61% a=1, 28% a=2, 11% a≥3).

**Question:** Dual walker that at ceiling+drop draws a from the **empirical multiset** (not always a=1) — does packing collapse vs pure greedy?

## Predictions
| ID | Claim | Conf |
|----|-------|------|
| T9.1 | Max ups over 53 steps (any k0,d0≤10) with empirical pin ≤ 25 | 0.55 |
| T9.2 | That max is **strictly < 31** (greedy all a=1) | 0.75 |
| T9.3 | Max streak under empirical pin ≤ 2 | 0.80 |
| T9.4 | Mean ups/53 over k0=0..52, d0=0 ≤ 18 | 0.50 |

Empiric multiset fixed from G6 artifact a_hist (frozen at plan time from G6 summary).
