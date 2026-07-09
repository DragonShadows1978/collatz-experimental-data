# G10 — Species Sink × Climb Height

**Priors:** Terminal species \(x=(4^k-1)/3\) has closed-form certifier
`is_one_step_species` (descent_rule). Theorem U: every upcrossing is
ceiling∧drop∧a=1. G8: n_ups = max(0, max_d).

**Question:** How does **steps-to-species** (first odd-step landing in
species, or hitting 1) relate to **climb height** (max_d / n_ups)?

## Predictions (frozen pre-data)
| ID | Claim | Conf |
|----|-------|------|
| U10.1 | Every free-orbit start that reaches 1 hits species or 1 within max_steps | 0.85 |
| U10.2 | steps_to_species ≥ n_ups on all starts that hit species | 0.70 |
| U10.3 | Among starts with n_ups≥10, mean(steps_to_species / n_ups) ∈ [2, 50] | 0.50 |
| U10.4 | Species members themselves have steps_to_species = 0 (already in) or 1 if we count landing | 0.95 |

## Gates
≥200 starts measured; species certifier agrees with one_odd_step on species sample; summary JSON.
