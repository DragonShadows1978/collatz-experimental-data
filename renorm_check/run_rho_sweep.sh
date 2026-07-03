#!/usr/bin/env bash
# Sweep rho(C) using the repo's own (unmodified) spectral_radius_sparse binary.
# Read-only w.r.t. repo source; binary built to a scratch target-dir.
# Runs many C values in parallel (bounded by $JOBS) at a fixed precision m,
# writes one CSV line per (C,m) to $OUTFILE.
#
# Usage: run_rho_sweep.sh <m> <c_list_file> <outfile> <jobs> <heartbeats>
set -euo pipefail

M="$1"
CLIST="$2"
OUTFILE="$3"
JOBS="${4:-10}"
HEARTBEATS="${5:-500}"
BIN=/tmp/collatz-verify-build/release/spectral_radius_sparse

echo "m,C,states,nnz_per_step,spectral_radius,gap,mode,time_sec" > "$OUTFILE"

run_one() {
  local c="$1"
  local m="$2"
  local hb="$3"
  local tmp
  tmp=$(mktemp)
  if timeout 600 "$BIN" --C "$c" --m-min "$m" --m-max "$m" --mode iterative --heartbeats "$hb" > "$tmp" 2>/dev/null; then
    tail -n +2 "$tmp"
  else
    echo "$m,$c,ERROR,,,,timeout_or_fail,"
  fi
  rm -f "$tmp"
}
export -f run_one
export BIN

cat "$CLIST" | xargs -P "$JOBS" -I{} bash -c 'run_one "$@"' _ {} "$M" "$HEARTBEATS" >> "$OUTFILE"

echo "done: $OUTFILE"
