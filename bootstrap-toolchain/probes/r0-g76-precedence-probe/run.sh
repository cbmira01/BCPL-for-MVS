#!/usr/bin/env bash
# R.0 G!76 evidence only: installed BOOT_OBJ is read, never modified.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$root"
probe=bootstrap-toolchain/probes/r0-g76-precedence-probe
out=workarea/runtime-extensions-r0-g76
mkdir -p "$out"

python3 -B -m unittest discover -s "$probe" -p test_probe.py -v
python3 -B "$probe/make-job.py" --check

tools/bootstrap/compile-mvs "$probe/source.bcpl" \
  --job-name R0G76C --output "$out/app.s370.asm"
python3 -B "$probe/make-job.py" --check --generated "$out/app.s370.asm"
python3 -B "$probe/make-job.py" --generated "$out/app.s370.asm"

printf 'Git HEAD: %s\n' "$(git rev-parse HEAD)" > "$out/provenance.txt"
sha256sum "$probe/source.bcpl" "$probe/check76.asm" \
  "$out/app.s370.asm" >> "$out/provenance.txt"
result=$(bash tools/mvs/submit-jcl "$out/r0-g76.jcl")
printf '%s\n' "$result"
job=$(awk '/^JOB [0-9]+/ {n=$2} END {print n}' <<< "$result")
[[ $job =~ ^[0-9]+$ ]] || { echo 'no JES job number' >&2; exit 1; }
printf '%s\n' "$job" > "$out/latest-job-number.txt"
sleep 5
report="$out/job-$job.txt"
tools/mvs/dump-report-for-job "$job" > "$report"
tools/mvs/job-summary "$job" --max-rc 0
python3 -B "$probe/verify-report.py" "$report"
echo "R.0 G!76 actual installed-runtime evidence: JOB $job"
echo "Report: $report"
echo 'Review IFOX/IEWL MAP and installed-object provenance.'
