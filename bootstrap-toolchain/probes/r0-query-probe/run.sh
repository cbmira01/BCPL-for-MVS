#!/usr/bin/env bash
# R.0 isolated shared QUERY experiment: no accepted-object writes.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$root"
probe=bootstrap-toolchain/probes/r0-query-probe
out=workarea/runtime-extensions-r0-query
mkdir -p "$out"

python3 -B -m unittest discover -s "$probe" -p 'test_*.py' -v
python3 -B "$probe/make-job.py" --check

tools/bootstrap/compile-mvs "$probe/caller.bcpl" \
  --job-name R0QCOMP --output "$out/app.s370.asm"
python3 -B "$probe/make-job.py" --check --generated "$out/app.s370.asm"
python3 -B "$probe/make-job.py" --generated "$out/app.s370.asm"

printf 'Git HEAD: %s\n' "$(git rev-parse HEAD)" > "$out/provenance.txt"
sha256sum "$probe/caller.bcpl" "$probe/dispatcher-a.asm" \
  "$probe/dispatcher-b.asm" "$out/app.s370.asm" >> "$out/provenance.txt"
result=$(bash tools/mvs/submit-jcl "$out/r0-query.jcl")
printf '%s\n' "$result"
job=$(awk '/^JOB [0-9]+/ {n=$2} END {print n}' <<< "$result")
[[ $job =~ ^[0-9]+$ ]] || { echo 'no JES job number' >&2; exit 1; }
printf '%s\n' "$job" > "$out/latest-job-number.txt"
sleep 5
report="$out/job-$job.txt"
tools/mvs/dump-report-for-job "$job" > "$report"
tools/mvs/job-summary "$job" --max-rc 0
python3 -B "$probe/verify-report.py" "$report"
echo "R.0 shared QUERY test-only MVS evidence: JOB $job"
echo "Report: $report"
echo 'Review IFOX and IEWL MAP/XREF for separate R0QAA and R0QBB.'
