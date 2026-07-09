# G12 Ledger
### freeze
Prior G11 collapse phase. Mersenne a=1 then species timing.

### G12-1 complete
U12.1 CONFIRMED all hit; U12.2 REFUTED (species can appear before end of nominal a=1 length window — intermediate hits); U12.3 CONFIRMED spearman~0.81; U12.4 CONFIRMED max_steps=190.
Next: a-values in the last steps before species (large-a drain).


### 2026-07-08 — G12-2 CORRECTION (U12.2 scorer bug)

**Bug:** `ge_L = all(... >= L for r in rows)` used loop variable `L`
left at 40 after `for L in range(1,41)`, so compared every row to 40
and falsely scored U12.2 REFUTED.

**Fix:** compare `r["steps_to_species"] >= r["L"]`. Re-ran `run_all.py`.

**Correct scoreboard:**
{
  "U12.1": {
    "verdict": "CONFIRMED",
    "confidence_prior": 0.85
  },
  "U12.2": {
    "verdict": "CONFIRMED",
    "n_ge_L": 40,
    "n_rows": 40,
    "min_steps_minus_L": 0,
    "confidence_prior": 0.7
  },
  "U12.3": {
    "verdict": "CONFIRMED",
    "spearman_proxy": 0.8115384615384615,
    "confidence_prior": 0.5
  },
  "U12.4": {
    "verdict": "CONFIRMED",
    "max_steps": 190,
    "confidence_prior": 0.45
  }
}

**Data fact:** for all L=1..40, steps_to_species >= L (min_steps_minus_L=0).
There is NO "species mid-path before L ends" in this Mersenne sample.
