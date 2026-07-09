# G1 — Implementation Ledger

**Track:** `renorm_check/shell/g1_shell_toll_surgery/`
**Branch:** `grok/g1-shell-toll-surgery`
**Law:** Append-only receipts. Each entry records what was done, the
command/artifact that proves it, paths abandoned and why, bugs, course
corrections, evidence, what is not complete, and the next required
update. Match `renorm_check/shell/LEDGER_SYNTHESIS_POLICY.md`.

Do **not** edit `IMPLEMENTATION_PLAN.md` to match results.
Do **not** use this file as narrative essay — that is `SYNTHESIS.md`.

---

### 2026-07-08 — G1-0 Scaffold (plan freeze)

**Status:** complete

**Work done:**
- Created git branch `grok/g1-shell-toll-surgery` from `main`.
- Created track directory
  `renorm_check/shell/g1_shell_toll_surgery/` with
  `scripts/`, `artifacts/`.
- Wrote immutable `IMPLEMENTATION_PLAN.md` (experiments E1 letter
  surgery, E2 exit toll, optional E3 ΔM; frozen predictions P1.* /
  P2.* / P3.1; shared gates V0–V3).
- Wrote this ledger and initial `SYNTHESIS.md` / `README.md`.
- Intentionally did **not** stage unrelated dirty worktree files on
  `main` (other agents' in-progress renorm_check paths).

**Paths abandoned & WHY:**
- Did not start E1/E2 implementation in the scaffold commit — plan
  must freeze before data (house rule: predictions pre-registered).
- Did not adopt dual-game realizability or Ostrowski transducer as G1
  scope — those are larger tracks; G1 is feet-wet only.

**Bugs/issues:** none (scaffold only).

**Course corrections:** none.

**Evidence:**
- Branch name: `grok/g1-shell-toll-surgery`
- Plan path: `renorm_check/shell/g1_shell_toll_surgery/IMPLEMENTATION_PLAN.md`
- This ledger: `renorm_check/shell/g1_shell_toll_surgery/IMPLEMENTATION_LEDGER.md`
- Synthesis: `renorm_check/shell/g1_shell_toll_surgery/SYNTHESIS.md`

**Not complete until:**
- Plan committed on the branch (this entry's commit).
- V0–V3 instrument gates run.
- E1 and E2 executed or honestly walled with artifact paths.

**Prediction outcomes this entry:** none (no experiments run). Scoreboard
in the plan remains all "—".

**Next required update:** after shared validation V0–V3 completes (pass
or fail). If pass, begin E1. If fail, ledger the failure and fix
instrument before any E1/E2 claim.

### 2026-07-08 — G1-0b House Rules adoption

**Status:** complete

**Work done:**
- Located house rules at `/mnt/Shared/HOUSE_RULES.md` (user said
  `/mnt/Sharedx`; that path is not a mount — file is on `/mnt/Shared`).
- Installed identical copy as Grok project rules:
  - repo root: `AGENTS.md`
  - track: `renorm_check/shell/g1_shell_toll_surgery/AGENTS.md`
  - global: `~/.grok/AGENTS.md`
- Adopted for this session and subsequent G1 work. Grok auto-loads
  `AGENTS.md` (also reads `CLAUDE.md` for Claude-compat).

**Paths abandoned & WHY:** none.

**Bugs/issues:** none.

**Course corrections:**
- House Rules §3: **No git commits** by dispatched agents; operator
  reviews and commits. Prior G1 scaffold commit (`3d42c8b`) was under
  explicit user setup order before these rules were installed; going
  forward G1 file edits are left uncommitted unless David commits or
  explicitly grants commit authority.
- House Rules §3: **Do not spawn subagents** unless lead role; G1
  execution is solo.
- Document Trinity already matches G1 layout (plan / ledger /
  synthesis).

**Evidence:**
- Source: `/mnt/Shared/HOUSE_RULES.md` (7097 bytes, 132 lines, mtime
  2026-07-08)
- Install targets as listed above (byte-identical copies)

**Not complete until:** operator commits `AGENTS.md` files onto the
branch if they should be versioned (agent will not commit under §3).

**Next required update:** V0–V3 instrument gates when David says begin.

### 2026-07-08 — G1-1 Shared gates V0–V3

**Status:** complete — all PASS

**Work done:**
- Implemented `scripts/g1_common.py` (exact credits via bit_length,
  mechanical 22/53 word P=84, hybrid constructors, D_emp via
  `toy_automaton.run_heartbeat_generic`, shell profile, orbit helpers).
- Implemented and ran `scripts/run_v0v3.py`.

**Commands:**
```bash
cd /mnt/ForgeRealm/collatz-experimental-data
python3 renorm_check/shell/g1_shell_toll_surgery/scripts/run_v0v3.py
```
Elapsed: 94.6s. Exit 0.

**Evidence (artifact):**
`renorm_check/shell/g1_shell_toll_surgery/artifacts/v0v3_report.json`

| Gate | Result | Receipt |
|------|--------|---------|
| V0 | PASS | Lemma 3: 22/31 in first 53 true credits; mechanical 22/53 period OK; first true≠22/53 letter **k=358** |
| V1 | PASS | C=1..5 edges 4,7,9,12,14; markers `L`*edge+`..` via true-word heartbeat |
| V2 | PASS | D_emp==d_rat==d_irr for m=2..12 at C=10; first rat/irr D-divergence m=359 |
| V3 | PASS | credit_true matches bit_length identity for k=0..400 |

**Paths abandoned & WHY:** none.

**Bugs/issues:** none. Note: f64 credit disagreement not observed for k<2000
in this check (first_f64_disagreement_k=null); exact path still mandatory
per plan.

**Course corrections:** none.

**Not complete until:** n/a for V-gates.

**Next required update:** E1 execution entry.

---

### 2026-07-08 — G1-2 Experiment E1 letter surgery

**Status:** complete (gates PASS; predictions mixed)

**Work done:**
- Implemented `scripts/run_e1.py`.
- Proved letter-identity true≡22/53 on [0,358); first divergence k=358.
- Heartbeat D for pure true m=2..12; period derived under identity;
  hybrid N-grid filled by identity + 24 computed spot-checks (all match).
- Extended steps=371, m=2..8: pure true/period + hybrids N∈{350,357,358,359,360}
  forward and reverse — all **computed** (not derived).

**Commands:**
```bash
python3 renorm_check/shell/g1_shell_toll_surgery/scripts/run_e1.py \
  2>&1 | tee renorm_check/shell/g1_shell_toll_surgery/artifacts/e1_run.log
```
Elapsed: 25.9s. Exit 0.

**Evidence:**
- `artifacts/e1_hybrid_D.csv` (395 lines incl. header)
- `artifacts/e1_summary.json`
- `artifacts/e1_run.log`

**Gates:**
| ID | Result |
|----|--------|
| E1-G1 | PASS — pure true D(m)=d_rat(m) m=2..12 |
| E1-G2 | PASS — pure 22/53 D matches (identity) |
| E1-G3 | PASS_VACUOUS — all heartbeat D identical across N |

**Prediction outcomes (vs frozen plan):**
| ID | Prior conf | Outcome | Evidence class |
|----|------------|---------|----------------|
| P1.1 | 0.55 | **INCONCLUSIVE** | dense enum m≤8 steps=371: support counts move (fwd N=359: 153; rev: 155; others: 154) but **D identical** for all families. Not a refutation of W6D-M at m~359; instrument does not hear the letter at these m. |
| P1.2 | 0.85 | **CONFIRMED** | all heartbeat hybrid/pure D unique-per-m only |
| P1.3 | 0.80 | **CONFIRMED** | true D = period D m=2..12; letter div at 358 |
| P1.4 | 0.45 | NOT_A_MEASUREMENT | F5 still OPEN; no claim |
| P1.5 | 0.70 | **INCONCLUSIVE** | no D variation to show fwd/rev asymmetry (support *does* differ 153 vs 155) |

**Key numerical receipt (extended, all m=2..8):**
- D(true)=D(period)=D(all hybrids) ∈ {0,1,1,2,2,2,3} by m
- support over k=0..370: true=154, period=154, hybrid_fwd@359=153, hybrid_rev@359=155

**Paths abandoned & WHY:**
- Did not brute-force recompute full N-grid heartbeats (would be redundant
  under proven letter-identity [0,53) + spot-checks). Method tagged in CSV
  as `derived_letter_identity_0_53_plus_spotcheck` vs `computed`.

**Bugs/issues:** none.

**Course corrections:** none to plan gates. Interpretation: one-letter
support flip is real at k=358 but **D_emp at m≤8 is blind to it** even
over 371 steps — consistent with F9 (capacity discrimination needs large m)
and agreement-zone law.

**Not complete until:** synthesis updated (this round).

**Next required update:** E2 entry.

---

### 2026-07-08 — G1-3 Experiment E2 exit toll census

**Status:** complete — **P2.1 REFUTED**; P2.2–P2.4 CONFIRMED

**Work done:**
- Implemented `scripts/run_e2.py`.
- Starts frozen pre-run: 8 high-reserve + up to 200 breach candidates from
  `data/runs/lock3_C*_breach_follow/*.jsonl` (250 unique loaded, 200 used)
  + 100 random odds in [1,1e7) seed=20260708 → **308 starts**.
- Upcrossings: new max deficit. Annotated with F7 `in_shell` at m=6,
  a_k, return-within-200.

**Commands:**
```bash
python3 renorm_check/shell/g1_shell_toll_surgery/scripts/run_e2.py \
  2>&1 | tee renorm_check/shell/g1_shell_toll_surgery/artifacts/e2_run.log
```
Elapsed: 0.79s. Exit 0.

**Evidence:**
- `artifacts/e2_exit_events.csv` — **1195 events**
- `artifacts/e2_summary.json`
- `artifacts/e2_starts.json`
- `artifacts/e2_run.log`

**Gates:**
| ID | Result |
|----|--------|
| E2-G1 | PASS (1195 ≥ 30) |
| E2-G2 | PASS (shell instrument spot-check) |
| E2-G3 | REPORTED (rates + nulls in summary) |

**Prediction outcomes:**
| ID | Prior conf | Outcome | Numbers (evidence class: orbit reanalysis + F7 shell tables) |
|----|------------|---------|------|
| **P2.1** | 0.50 | **REFUTED** | At C_after=5: in_shell_after rate **0.0** (n=107) vs null shell rate **0.299** → enrichment **0.0** (<1.1). Overall in_shell_after=0.214, but hits only at C=1 (197/258) and C=2 (59/225); **zero shell hits for all C_after≥3**. Shell-toll as F7 membership enrichment is dead under this operationalization. |
| P2.2 | 0.75 | **CONFIRMED** | a_k=1 on **100%** of 1195 upcrossings |
| P2.3 | 0.65 | **CONFIRMED** | interior (delta_before≥3) rate **0.0** — all exits ceiling-adjacent relative to prior corridor |
| P2.4 | 0.70 | **CONFIRMED** | returned within 200 steps: **100%** (d≤C_before or hit 1) |

**Honest caveats (load-bearing):**
1. Upcrossing = new max d ⇒ post-exit state sits at ceiling of new corridor
   (delta_after=0). `near_ceil_after` is near-tautological; primary P2.1
   metric was F7 residual-dead membership, not near-ceil.
2. P2.3 is strongly expected for record-setting definition but not purely
   vacuous (d_before could lag C_before by ≥3); data shows it never did
   at exit steps.
3. Return metric uses segment-relative deficit from exit value, not global
   k-index — labels `d_le_C_before` / `hit_1` in CSV.

**Paths abandoned & WHY:** none mid-run.

**Bugs/issues:** none blocking. Optional future: pin global step index for
return test; multi-m shell membership.

**Course corrections:** none to frozen gates. **Hypothesis killed:**
"upward exits land in death-shell residual set more than null" — REFUTED.
Composition story must pivot (dual-game / realizability), not more F7
exit bookkeeping in this form.

**Not complete until:** synthesis narrative updated.

**Next required update:** optional E3 only if requested; else track idle
awaiting operator direction. No commit (House Rules §3).

---

### 2026-07-08 — G1-4 Prediction scoreboard (final for this run)

| ID | Claim | Outcome |
|----|-------|---------|
| P1.1 | Hybrid D tracks support splice | INCONCLUSIVE (m≤8) |
| P1.2 | No D split m≤12 | CONFIRMED |
| P1.3 | True vs period D agree dense | CONFIRMED |
| P1.4 | Conditional F5 only | NOT_A_MEASUREMENT |
| P1.5 | Reverse hybrid asymmetry | INCONCLUSIVE (m≤8) |
| P2.1 | Shell enrichment ≥1.5× | **REFUTED** |
| P2.2 | a=1 rate ≥0.70 | CONFIRMED (1.00) |
| P2.3 | Interior exits <20% | CONFIRMED (0.00) |
| P2.4 | Return ≥80% in 200 steps | CONFIRMED (1.00) |
| P3.1 | ΔM staircase | NOT RUN (stretch; E1/E2 complete but not required) |



### 2026-07-08 — G1-5 Experiment E3 ΔM staircase + track close

**Status:** complete — P3.1 **INCONCLUSIVE** (cluster half clear; alignment half no signal)

**Work done:**
- Froze genuine-death sources in `scripts/run_e3.py` BEFORE compute:
  1. `renorm_check/shell/underlock/w7a_renorm/W7A_ORDER.md` — C=1..26 measured edges
  2. `renorm_check/shell/underlock/w7a_renorm/w7a_new_edges.txt` — C=27..31 (genuine_death=True only; walls never written)
  3. Cross-check `renorm_check/shell/underlock/w7b_deep/W7B_FINDINGS.md` gates C=16,23,26 and table C=27..31
- Implemented pure table transform: load → monotone/contiguous gates → ΔM(C)=M(C)−M(C−1) → cluster stats → support-density alignment probe
- Unit tests in `scripts/test_e3.py` drive shipped `load_edges`, `compute_delta_rows`, `score_p31`, `main`

**Commands:**
```bash
cd /mnt/ForgeRealm/collatz-experimental-data
python3 renorm_check/shell/g1_shell_toll_surgery/scripts/run_e3.py \
  2>&1 | tee renorm_check/shell/g1_shell_toll_surgery/artifacts/e3_run.log
# also captured: /tmp/grok-goal-74c895a7b733/implementer/e3_run.log
cd renorm_check/shell/g1_shell_toll_surgery/scripts && python3 test_e3.py \
  2>&1 | tee /tmp/grok-goal-74c895a7b733/implementer/e3_tests.log
```
Exit 0 / ALL E3 TESTS PASSED.

**Evidence:**
- `artifacts/e3_delta_M.csv` (32 lines = header + C=1..31)
- `artifacts/e3_summary.json`
- `artifacts/e3_run.log`
- Scratch: `/tmp/grok-goal-74c895a7b733/implementer/e3_run.log`, `e3_tests.log`

**Edges (genuine-death only, n=31):**
C=1..31 M = 4,7,9,12,14,16,19,21,24,26,57,63,68,71,79,93,108,110,130,132,139,157,163,188,192,205,208,263,265,282,284

**ΔM sequence (C=2..31, n=30):**
[3, 2, 3, 2, 2, 3, 2, 3, 2, 31, 6, 5, 3, 8, 14, 15, 2, 20, 2, 7, 18, 6, 25, 4, 13, 3, 55, 2, 17, 2]

**Hand re-derives (evidence class: integer arithmetic on JSON edge table):**
- ΔM(28)=M(28)−M(27)=263−208=**55**
- ΔM(31)=M(31)−M(30)=284−282=**2**
- ΔM(16)=M(16)−M(15)=93−79=**14**

**Cluster stats:**
- mean≈9.33, stdev≈11.43, **cv≈1.22**, range max−min=**53** → not approximately constant
- small (Δ≤3): **15**; large (Δ>3): **15**
- large values include 31,55,25,20,18,17,15,14,13,8,7,6,6,5,4

**P3.1 outcome (prior conf 0.40):** **INCONCLUSIVE**
- Partial CONFIRMED: non-constant + clear small(≤3)/large split (15/15)
- Alignment half: support-density proxy on length-53 windows at start 2*C gave
  mean_large = mean_all = **22/53 ≈ 0.41509** (margin 0.0) — every 53-window of the
  true Sturmian word has exactly 22 supports, so this proxy cannot discriminate.
  Honest verdict INCONCLUSIVE on Ostrowski/support alignment, not forced CONFIRMED.
- Full P3.1 requires both halves → overall **INCONCLUSIVE** (not REFUTED: cluster
  structure is real; alignment untested by a discriminative instrument)

**Walls excluded:** C=31 first attempt wall (state_cap) never in w7a_new_edges.txt
(W7B_FINDINGS). No wall rows in edge table.

**Paths abandoned & WHY:** none. Did not invent new edges or re-sweep C≥32.

**Bugs/issues:** alignment probe is structurally blind on period-53 support
count; documented rather than re-tuned post-hoc to manufacture CONFIRMED
(threshold discipline).

**Course corrections:** none to frozen plan. E3 was optional stretch; executed
to close execution order item 5 under goal harness.

**IMPLEMENTATION_PLAN.md:** mtime unchanged (1783547005); not edited.

**Not complete until:** SYNTHESIS scoreboard lists P3.1; track marked execution-complete.

**Next required update:** none — G1 execution closed (scaffold, V0–V3, E1, E2, E3, narrative).
  Operator may commit when ready (House Rules §3: agent does not commit).

### 2026-07-08 — G1-6 Track execution COMPLETE

**Status:** complete

**Work done:** All implementation-plan execution steps 1–6 done on disk:
scaffold, V0–V3, E1, E2, E3, ledger+synthesis. Prediction scoreboard fully
filled (no NOT RUN remaining except N/A items).

**Evidence:** artifacts/ tree + this ledger G1-0..G1-6.

**Next required update:** idle / operator commit review.

### 2026-07-08 — G1-7 Branch documentation policy

**Status:** complete

**Work done:**
- Operator rule: one branch-level synthesis; plan+ledger stay per implementation.
- G1 narrative content migrated into `renorm_check/shell/GROK_SYNTHESIS.md`.
- This folder’s `SYNTHESIS.md` is now a pointer only. G1 plan file not edited
  (immutable); READMEs updated.

**Evidence:** `../GROK_SYNTHESIS.md`

**Next required update:** none (G1 execution already complete).
