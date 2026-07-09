#!/usr/bin/env python3
"""G2 E4 stretch — U vs max deficit from E1 starts. Optional."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ART = Path(__file__).resolve().parents[1] / "artifacts"


def main() -> int:
    starts = json.loads((ART / "e1_starts.json").read_text())
    # Scope: starts that reach nonnegative max deficit (corridor-relevant).
    # Negative max_d means orbit never entered d≥0; U≤M+1 is vacuous/meaningless.
    scoped = [s for s in starts if s["max_d"] >= 0]
    violations = []
    for s in scoped:
        U = s["n_upcrossings"]
        M = s["max_d"]
        # Q4.1: U ≤ M+1
        if U > M + 1:
            violations.append(s)
    ok = len(violations) == 0 and len(scoped) > 0
    summary = {
        "prediction_Q4.1": {
            "verdict": "CONFIRMED" if ok else "REFUTED",
            "rule": "U <= M+1 for starts with max_d >= 0",
            "n_starts": len(starts),
            "n_scoped": len(scoped),
            "n_violations": len(violations),
            "violations_head": violations[:5],
            "confidence_prior": 0.55,
        }
    }
    (ART / "e4_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
