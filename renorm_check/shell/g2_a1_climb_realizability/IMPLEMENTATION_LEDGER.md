# G2 — Implementation Ledger

**Track:** `renorm_check/shell/g2_a1_climb_realizability/`
**Branch:** `grok/g1-shell-toll-surgery` (shared Grok working branch)
**Law:** Append-only receipts. House Rules + `LEDGER_SYNTHESIS_POLICY.md`.

Do **not** edit `IMPLEMENTATION_PLAN.md` to match results.
Narrative meaning → `../GROK_SYNTHESIS.md` (branch-level, shared).

---

### 2026-07-08 — G2-0 Scaffold (plan freeze)

**Status:** complete

**Work done:**
- Created track folder `renorm_check/shell/g2_a1_climb_realizability/`
  on existing branch `grok/g1-shell-toll-surgery` (no new branch — tracks
  are directories under the Grok working branch).
- Wrote immutable `IMPLEMENTATION_PLAN.md` with pre-registered predictions
  Q1.*–Q4.1 grounded in G1 outcomes (esp. P2.1 REFUTED, P2.2 a=1 100%).
- Opened this ledger and initial `SYNTHESIS.md` / `README.md`.
- Deleted unused branch name `grok/g2-a1-climb-realizability` if present
  (operator preference: one Grok branch).

**Paths abandoned & WHY:**
- Did not start E1–E4 in the freeze commit — predictions first.
- Did not continue F7 exit-shell work — G1 P2.1 killed that operationalization.

**Evidence:**
- Plan: `renorm_check/shell/g2_a1_climb_realizability/IMPLEMENTATION_PLAN.md`
- G1 pressure receipts: `../g1_shell_toll_surgery/artifacts/e2_summary.json`
  (P2.2 a1_rate=1.0, n_events=1195)

**Not complete until:** operator says begin execution (V0+).

**Next required update:** after V0–V2 validation.

### 2026-07-08 — G2-0b Branch documentation policy

**Status:** complete

**Work done:**
- Operator rule: **one synthesis for the whole Grok branch**; each new
  implementation gets a **new plan** and a **new ledger** only.
- Branch narrative file: `renorm_check/shell/GROK_SYNTHESIS.md`
- Per-track `SYNTHESIS.md` reduced to pointer stubs (G1 and G2).
- G2 plan layout section updated to drop per-track synthesis.

**Evidence:** `../GROK_SYNTHESIS.md`; stub `SYNTHESIS.md` in this folder.

**Next required update:** V0 when execution starts.


### 2026-07-08 — G2-1 Shared gates V0–V2

**Status:** complete — all PASS

**Work done:**
- Implemented `scripts/g2_core.py` (orbit, climb_run, pure a=1 closed form,
  general word cylinders, a-prediction).
- Implemented/ran `scripts/run_v0v2.py`.

**Commands:**
```bash
python3 renorm_check/shell/g2_a1_climb_realizability/scripts/run_v0v2.py
# log: artifacts/v0v2_run.log and /tmp/grok-goal-7fbc2612b498/implementer/g2_v0v2.log
```

**Evidence:** `artifacts/v0v2_report.json`
- V0 PASS: start 80049391 has 23 upcrossings, all a=1
- V1 PASS: a=1 iff x≡3 mod 4 on odds 1..2000
- V2 PASS: 20 random odds × j∈{3,5,8,12} residue a-prediction matches

**Next:** E1

---

### 2026-07-08 — G2-2 Experiment E1 climb census

**Status:** complete

**Commands:**
```bash
python3 renorm_check/shell/g2_a1_climb_realizability/scripts/run_e1.py
```
**Evidence:** `artifacts/e1_climb_runs.csv`, `e1_summary.json`, `e1_starts.json`

**Gates:** E1-G1 PASS (n_runs=662); E1-G2 PASS (a1_rate=1.0); n_upcrossings=1217

**Predictions:**
| ID | Verdict | Numbers |
|----|---------|---------|
| Q1.1 | CONFIRMED | max_L=20 |
| Q1.2 | REFUTED | L counts 1,2,3 = [25, 155, 141] (mode at L=2 not L=1) |
| Q1.3 | CONFIRMED | mean ups HR=24.875, random=1.0 |

**climb_run definition used:** maximal consecutive a=1 steps containing ≥1 upcrossing.

**Next:** E2

---

### 2026-07-08 — G2-3 Experiment E2 pure a=1 cylinders

**Status:** complete — all Q2.* CONFIRMED

**Commands:**
```bash
python3 renorm_check/shell/g2_a1_climb_realizability/scripts/run_e2.py
```
**Evidence:** `artifacts/e2_cylinders.csv`, `e2_summary.json`

**Closed form:** first L steps all a=1 ⇔ x ≡ −1 (mod 2^{L+1}); min positive odd = 2^{L+1}−1.
Verified L=1..32; L=1 → residue 3 mod 4; mod_bits = L+1 nondecreasing; m(L)≥L.

**Predictions:** Q2.1–Q2.4 all **CONFIRMED** (slope log2(min_x) vs L = 1.0; inverse limit −1 in ℤ₂).

**Next:** E3

---

### 2026-07-08 — G2-4 Experiment E3 mixed climb-adjacent words

**Status:** complete

**Bug fixed mid-run:** first cylinder engine applied every a to the *same* x
(wrong). Replaced with full-word `realizes_word` scan / linear witness +
modulus-from-lifts. Observed orbit words are nonempty after fix.

**Commands:**
```bash
python3 renorm_check/shell/g2_a1_climb_realizability/scripts/run_e3.py
```
**Evidence:** `artifacts/e3_summary.json`, `e3_words.jsonl`

**Gates:** 20 words analyzed (top gap-words from E1).

**Predictions:**
| ID | Verdict | Notes |
|----|---------|-------|
| Q3.1 | CONFIRMED | 20/20 nonempty |
| Q3.2 | REFUTED | long words have min_x < 1e6 (e.g. 15355, 89083, 154619) |
| Q3.3 | CONFIRMED | frac_stricter=1.0 on 18 mixed |

**Next:** E4

---

### 2026-07-08 — G2-5 Experiment E4 (stretch) U vs max deficit

**Status:** complete

**Commands:**
```bash
python3 renorm_check/shell/g2_a1_climb_realizability/scripts/run_e4.py
```
**Evidence:** `artifacts/e4_summary.json`

**Q4.1** CONFIRMED: rule U≤M+1 on starts with max_d≥0
(n_scoped=284, violations=0).
Starts with max_d<0 excluded (rule meaningless there).

---

### 2026-07-08 — G2-6 Tests + track close

**Status:** complete

**Commands:**
```bash
cd renorm_check/shell/g2_a1_climb_realizability/scripts && python3 test_g2.py
# log: /tmp/grok-goal-7fbc2612b498/implementer/g2_tests.log
```
ALL G2 UNIT TESTS PASSED.

**IMPLEMENTATION_PLAN.md:** not edited (immutable).

**Scoreboard final:** see GROK_SYNTHESIS.md G2 section.

**Next required update:** idle — G2 execution complete.
