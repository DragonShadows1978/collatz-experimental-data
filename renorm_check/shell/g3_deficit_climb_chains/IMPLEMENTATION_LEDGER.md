# G3 — Implementation Ledger

**Track:** `renorm_check/shell/g3_deficit_climb_chains/`  
**Branch:** `grok/g1-shell-toll-surgery`  
Narrative → `../GROK_SYNTHESIS.md` only.

---

### 2026-07-08 — G3-0 Scaffold (plan freeze)

**Status:** complete

**Work done:**
- Created track folder; wrote immutable IMPLEMENTATION_PLAN.md with
  predictions R1.*–R4.* grounded in G1/G2 (a=1 ups + cylinders weak alone).
- Opened this ledger.

**Next:** V0–V1 + E1–E4 execution.


### 2026-07-08 — G3-1 Full execution V0–E4

**Status:** complete

**Commands:**
```bash
python3 renorm_check/shell/g3_deficit_climb_chains/scripts/run_all.py
python3 renorm_check/shell/g3_deficit_climb_chains/scripts/test_g3.py
```
Artifacts under `artifacts/`. Tests ALL PASS.

**V0–V1:** PASS (lemma3 22/31; dual d identity 100% on 80049391, n=211).

**E1** n_ups=1217, a1_rate=1.0
| ID | Verdict | Key number |
|----|---------|------------|
| R1.1 | CONFIRMED | frac_c2=1.0 |
| R1.2 | CONFIRMED | frac_c1=0.0 |
| R1.3 | CONFIRMED | frac_ceil_c1=0.0 |

**E2** Mersenne x=2^{L+1}-1, L=1..24
| ID | Verdict | Key |
|----|---------|-----|
| R2.1 | REFUTED | mean ups/L=0.5073 (threshold 0.50) |
| R2.2 | CONFIRMED | max_d_prefix ≤ L all L |
| R2.3 | CONFIRMED | extended max_d not monotone |

**E3** dual a=1 grid 4664 cells
| ID | Verdict | Key |
|----|---------|-----|
| R3.1 | REFUTED | frac nonneg L=24 = 1.0 (predicted ≤0.25 — wrong direction: a=1 **raises** mean d) |
| R3.2 | REFUTED | d0=0 frac=1.0 |
| R3.3 | REFUTED | mean virt ups=14.038 |

**E4** streaks
| ID | Verdict | Key |
|----|---------|-----|
| R4.1 | CONFIRMED | max_streak=2 |
| R4.2 | REFUTED | frac isolated=0.676 (hist 1:823, 2:197) |

**Course corrections:** none to frozen gates. R3 predictions underestimated drift of a=1 under mean c≈1.585.

**Next:** synthesis update; track idle.
