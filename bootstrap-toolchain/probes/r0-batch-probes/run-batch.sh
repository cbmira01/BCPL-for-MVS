#!/usr/bin/env bash
# R.0 evidence batch: 20 cases, one MVS job, no accepted PDS updates.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$ROOT"
PROBE=bootstrap-toolchain/probes/r0-batch-probes
OUT=workarea/runtime-extensions-r0-batch

if [ -n "$(git status --porcelain)" ]; then
    echo 'ERROR: Git working tree is not clean.' >&2
    git status --short
    exit 1
fi

python3 -B -m unittest discover -s "$PROBE" -p test_batch.py -v
python3 -B "$PROBE/make-batch.py" --check
python3 -B "$PROBE/make-batch.py"

result=$(bash tools/mvs/submit-jcl "$OUT/r0-batch.jcl")
echo "$result"
job=$(awk '/^JOB [0-9]+/ {n=$2} END {print n}' <<< "$result")
if [ -z "$job" ]; then
    echo 'ERROR: Could not determine JES job number.' >&2
    exit 1
fi
printf '%s\n' "$job" > "$OUT/latest-job-number.txt"
sleep 5
report="$OUT/job-${job}.txt"
tools/mvs/dump-report-for-job "$job" > "$report"

echo "========= R.0 BATCH — JOB $job ========="
tools/mvs/job-summary "$job" --max-rc 0

count=0
while IFS= read -r marker; do
    if ! grep -Fqx -- "$marker" "$report"; then
        echo "ERROR: Actual QOUT marker missing: $marker" >&2
        echo "Report: $report" >&2
        exit 1
    fi
    printf 'VERIFIED: %s\n' "$marker"
    count=$((count+1))
done < "$OUT/expected-markers.txt"

if [ "$count" -ne 20 ]; then
    echo "ERROR: Expected 20 markers, found $count" >&2
    exit 1
fi
actual=$(grep -Ec '^R0 [DF][0-9][0-9] ' "$report" || true)
if [ "$actual" -ne 20 ]; then
    echo "ERROR: Expected exactly 20 R.0 QOUT markers, got $actual" >&2
    exit 1
fi

echo "R.0 BATCH: ALL 20 CASES VERIFIED IN JOB $job"
echo "Full JES report: $report"
git status --short
