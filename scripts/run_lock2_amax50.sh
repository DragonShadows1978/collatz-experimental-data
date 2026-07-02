#!/usr/bin/env bash
set -euo pipefail

cd /mnt/ForgeRealm/collatz-experimental-data

exec /usr/bin/time -f 'elapsed=%E maxrss_kb=%M' \
  /tmp/collatz-rust-target/release/lock2_scan \
  --Amax 50 \
  --threads 12 \
  --split-depth 12 \
  --top-n 200 \
  --prediction-top-n 200 \
  --out-dir data/runs \
  --stamp 20260522T_lock2_rust_parallel_Amax50 \
  --progress-every 1000000000 \
  --predict-rho-slack-min 8 \
  --predict-theta-candidates-min 1
