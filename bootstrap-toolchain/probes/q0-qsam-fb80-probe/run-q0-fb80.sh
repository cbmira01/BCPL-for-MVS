#!/usr/bin/env bash
# Q.0 only: produces temporary IFOX / IEWL / GO job, no PDS writes.
set -euo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$here/../../.." && pwd)"
cd "$root"
python3 "$here/make-job.py"
echo '=== Submit standalone MVS 3.8 FB80 QSAM probe ==='
bash tools/mvs/submit-jcl workarea/qsam-q0-fb80/qs0-fb80.jcl
printf '%s\n' 'Check returned job number with:'   '  tools/mvs/job-summary <JOB> --max-rc 0'   '  tools/mvs/dump-report-for-job <JOB>'
