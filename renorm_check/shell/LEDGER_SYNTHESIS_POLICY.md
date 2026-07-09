# STANDING POLICY — the Ledger + Synthesis discipline (calibrated to David's own ledgers)

Directive (David, 2026-07-05, mandatory). An agent's chat output to the
orchestrator is a courtesy summary ONLY — never the record. The record
lives on disk, readable by any future session with the orchestrator gone.
Reference standard: GraftRepository/docs/*_LEDGER.md and
/mnt/ForgeRealm/AI_Research_Board.md — match their form, not a paraphrase.

## 1. THE LEDGER — receipt book of the PROCESS
Append to renorm_check/IMPLEMENTATION_LEDGER.md (or LEDGER_<ROUND>.md the
orchestrator merges). Follow the GraftRepository ledger skeleton:

**Ledger law** (state it, then obey it): update whenever a step completes;
each entry records what was done, the command/artifact that PROVES it, and
what remains blocked or unfinished.

Each entry:
```
### YYYY-MM-DD - <Round/Step Title>
**Status:** complete | partial | abandoned
**Work done:** <bulleted, specific — each approach TRIED>
**Paths abandoned & WHY:** <every dead end, dropped hypothesis, swapped
  instrument — WITH the reason. Load-bearing. The corpses stay in the
  book so the next session doesn't re-walk them.>
**Bugs/issues:** <each bug, how it was caught (which gate/cross-check),
  the fix or workaround>
**Course corrections:** <where the plan changed mid-run and why>
**Evidence:** <exact artifact paths, exact numbers, exact counts —
  GraftRepo cites byte-counts and revisions; match that precision>
**Not complete until:** <distinguish IMPLEMENTED from PROVEN — name the
  gates/controls still owed before the result is scientifically done>
**Next required update:** <what triggers the next entry>
```

A skeptic reads the ledger and reconstructs the ENTIRE decision process:
what was tried, what broke, what was dropped and for what reason, what
finally worked. It is "how we actually got here" — forks and corpses
included — NOT a tidy list of outcomes.

## 2. THE SYNTHESIS — the interpreted finding
Append to renorm_check/SYNTHESIS.md. What the surviving results MEAN:
verdict vs hypothesis, how it moves the standing picture, what it
opens/closes. Cite exact paths for every claim.

## 3. THE BOARD — cross-track memory (orchestrator's job, not the agent's)
/mnt/ForgeRealm/AI_Research_Board.md is the program-level ledger: each
track a dated, verdict-carrying section, updated at every milestone by
whichever session lands it. The board is the map of ALL tracks; the
per-round ledger is the receipt book of ONE. The orchestrator updates
the board when a round changes a track's state.

## Rules
Ledger + Synthesis every round, non-optional, exact paths throughout.
An agent that only reports to chat, or only writes a "findings" summary,
has NOT completed its task. The files are the memory; the orchestrator is
a router that reads them, not a narrator that holds them in its head.
