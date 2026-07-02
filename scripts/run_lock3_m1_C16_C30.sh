#!/usr/bin/env bash
set -euo pipefail

ROOT="/mnt/ForgeRealm/collatz-experimental-data"
BIN="/tmp/collatz-rust-target-lineage/release/lock3_census"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_DIR="$ROOT/logs"
SUMMARY="$LOG_DIR/lock3_m1_C16_C30_${STAMP}.summary.log"

mkdir -p "$LOG_DIR"
exec >> "$SUMMARY" 2>&1

echo "lock3 m1 C16-C30 batch start stamp=$STAMP"
echo "root=$ROOT"
echo "bin=$BIN"

for C in $(seq 16 30); do
  existing="$(find "$ROOT/data/runs" -maxdepth 2 -type f -path "$ROOT/data/runs/lock3_C${C}_N2000_residue_m1*/lock3_summary_C${C}.json" | head -n 1 || true)"
  if [[ -n "$existing" ]]; then
    echo "skip C=$C existing=$existing"
    continue
  fi

  OUT="$ROOT/data/runs/lock3_C${C}_N2000_residue_m1_lineage_cohorts_${STAMP}"
  RUN_LOG="$OUT/run.log"
  mkdir -p "$OUT"

  echo "run C=$C out=$OUT"
  (
    cd "$ROOT"
    "$BIN" \
      --C "$C" \
      --depth 2000 \
      --residue-mod-power 1 \
      --out-dir "$OUT" \
      --progress-every 100 \
      --label lock3 \
      --memory-lean \
      --no-checkpoint \
      --memory-cap-mb 8192 \
      --progress-jsonl "$OUT/live_events.jsonl"
  ) > "$RUN_LOG" 2>&1
  rc=$?
  echo "done C=$C rc=$rc log=$RUN_LOG"
done

echo "lock3 m1 C16-C30 batch complete stamp=$STAMP"
