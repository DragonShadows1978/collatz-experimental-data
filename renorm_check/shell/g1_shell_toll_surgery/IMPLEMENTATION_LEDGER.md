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
