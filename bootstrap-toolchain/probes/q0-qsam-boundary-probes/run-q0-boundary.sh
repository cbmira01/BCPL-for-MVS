#!/usr/bin/env bash
# Isolated Q.0 F/FB boundary experiment; source/JCL generated locally.
set -euo pipefail
here="$(cd -- "$(dirname -- "$0")" && pwd)"
root="$(cd "$here/../../.." && pwd)"
cd "$root"
if (($# < 1)); then
  echo >&2 'Usage: run-q0-boundary.sh {f80|f1024|fb8k|fb16k} [--allow-large]'
  exit 64
fi
profile="$1"; shift
case "$profile" in f80|f1024|fb8k|fb16k) ;; *) echo >&2 "Invalid profile: $profile"; exit 64;; esac
python3 "$here/make-jobs.py" "$profile" "$@"
bash tools/mvs/submit-jcl "workarea/qsam-q0-boundary/q0-$profile.jcl"
