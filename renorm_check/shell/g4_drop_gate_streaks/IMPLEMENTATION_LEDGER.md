# G4 — Implementation Ledger

**Track:** `g4_drop_gate_streaks/`  
Narrative → `../GROK_SYNTHESIS.md`

### 2026-07-08 — G4-0 Scaffold

**Status:** complete  
**Work done:** Plan freeze (Theorem U + streak/drop/support experiments S0–S4).  
**Next:** execute run_all.


### 2026-07-08 — G4-1 Full execution

**Status:** complete

**Theorem U (proved + machine-checked):**
d′=d+c−a; upcross needs c−a > slack=C−d ≥ 0; c−a ≤ 1 ⇒ slack=0 and (c,a)=(2,1).
Every upcrossing is at-ceiling, drop-phase, a=1.

**Commands:**
```bash
python3 renorm_check/shell/g4_drop_gate_streaks/scripts/run_all.py
python3 renorm_check/shell/g4_drop_gate_streaks/scripts/test_g4.py
```

**Results:**
| ID | Verdict | Key |
|----|---------|-----|
| S0.1 | CONFIRMED | free sample 1180 ups, 0 fail |
| S0.2 | CONFIRMED | odds 1..1e5, 41209 ups, 0 fail |
| S1.1–S1.3 | CONFIRMED | R_max drop-run = 2 (block and 10k); mean run ≈1.41 |
| S2.1–S2.3 | CONFIRMED | max up-streak=2=R_max; drop-pair→double-up only 5.1% |
| S3.1–S3.3 | CONFIRMED | 74.8% post-up support; second-up 16.4%; support⇒no second up (0) |
| S4.1 | REFUTED | greedy max ups/53 = **31** (= #drops) |
| S4.2 | REFUTED | greedy max ups/106 = **62** |
| S4.3 | CONFIRMED | greedy max streak=2≤R_max |

**Interpretation:** Theorem U is closed. Streaks hard-capped by drop-run length 2 in the credit word. Support phases interrupt (never second up after c=1). Dual-greedy can still pack ~one up per drop letter if always at ceiling — so **count** of ups is not bounded by 15 without further corridor/precision constraints; **streak length** is.

**Next:** synthesis; track idle. Successor: couple Theorem U + precision/shell so that "always at ceiling for every drop" is impossible for long horizons.
