#!/usr/bin/env bash
# Q.0 isolated QSAM DASD experiment. No production object PDS writes.
set -euo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$here/../../.." && pwd)"
cd "$root"
profile=${1:-fb}
case "$profile" in fb|v|vb) ;; *) echo "usage: $0 {fb|v|vb}" >&2; exit 64;; esac
python3 "$here/make-jobs.py" "$profile"
echo "=== Submit isolated $profile QSAM DASD probe ==="
bash tools/mvs/submit-jcl "workarea/qsam-q0-dasd/q0-$profile.jcl"
