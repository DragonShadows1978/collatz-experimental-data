#!/usr/bin/env python3
"""
W7B-DEEP -- push PAST the C=31 state_cap wall.

The C=31 wall in the main sweep was the state_cap=64,000,000 I chose, NOT
a hardware limit (RSS at the wall was only 15,872 MB of 32,000). This run
raises state_cap to 120,000,000 and rss_cap to 28,000 MB to try to capture
C=31 as a GENUINE edge. Same frozen gates apply: sweep_c27_up.main()
re-runs the C=16=93 / C=23=163 / C=26=205 validation gate inline before
trusting C=31, and enforces the wall-vs-edge + monotonicity rules in code.
Only a genuine death (wall=None, real first_dead, M>prev=M(30)=282) gets
appended to ../w7a_renorm/w7a_new_edges.txt.
"""
import sweep_c27_up as s

s.RSS_CAP_MB = 28_000.0
s.STATE_CAP = 120_000_000
# make the already-validated C=27..30 edges known so the C=31 monotonicity
# baseline is M(30)=282 (driver seeds prev_edge = KNOWN_EDGES[c_start-1]).
s.KNOWN_EDGES.update({27: 208, 28: 263, 29: 265, 30: 282})

if __name__ == "__main__":
    s.main(c_start=31, c_stop=31)
