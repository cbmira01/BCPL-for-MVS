#!/usr/bin/env bash
# Test-only R.0 Decision G: no installed object mutation.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$root"
probe=bootstrap-toolchain/probes/r0-g-limits-probe
out=workarea/runtime-extensions-r0-g-limits
mkdir -p "$out"
PYTHONPATH="$probe" python3 -B -m unittest discover -s "$probe" -p 'test_*.py' -v
python3 -B "$probe/make-job.py" --check
python3 -B "$probe/make-job.py"
result=$(bash tools/mvs/submit-jcl "$out/r0-g-limits.jcl")
printf '%s\n' "$result"
job=$(awk '/^JOB [0-9]+/ {n=$2} END {print n}' <<< "$result")
[[ $job =~ ^[0-9]+$ ]] || { echo 'No JES JOB number' >&2; exit 1; }
printf '%s\n' "$job" > "$out/latest-job-number.txt"
sleep 5
tools/mvs/dump-report-for-job "$job" > "$out/job-$job.txt"
tools/mvs/job-summary "$job" --max-rc 0
python3 -B "$probe/verify-report.py" "$out/job-$job.txt"
echo "R.0 Decision G MVS boundary evidence: JOB $job"
echo "Report: $out/job-$job.txt"
