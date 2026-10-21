#!/usr/bin/env bash
# R.0 test only: installed BOOT_OBJ read-only; no G150 mutation.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$root"
probe=bootstrap-toolchain/probes/r0-g150-startup-probe
out=workarea/runtime-extensions-r0-g150
mkdir -p "$out"
for src in "$probe" bootstrap-toolchain/asm/bcplmain.asm; do
  if [[ -n $(git status --porcelain -- "$src") ]]; then
    echo "Uncommitted probe/runtime source: $src" >&2; exit 1
  fi
done
python3 -B -m unittest discover -s "$probe" -p 'test_*.py' -v
python3 -B "$probe/make-job.py" --check
bash -n "$probe/run.sh"
tools/bootstrap/compile-mvs "$probe/source.bcpl" \
  --job-name R0G150C --output "$out/app.s370.asm"
python3 -B "$probe/make-job.py" --check --generated "$out/app.s370.asm"
python3 -B "$probe/make-job.py" --generated "$out/app.s370.asm"
printf 'Git HEAD: %s\n' "$(git rev-parse HEAD)" > "$out/provenance.txt"
sha256sum "$probe/source.bcpl" "$probe/observer.asm" \
  "$probe/make-job.py" "$out/app.s370.asm" >> "$out/provenance.txt"
response=$(bash tools/mvs/submit-jcl "$out/r0-g150.jcl")
printf '%s\n' "$response"
job=$(awk '/^JOB [0-9]+/ {n=$2} END {print n}' <<< "$response")
[[ $job =~ ^[0-9]+$ ]] || { echo 'No JES job number' >&2; exit 1; }
printf '%s\n' "$job" > "$out/latest-job-number.txt"
sleep 5
report="$out/job-$job.txt"
tools/mvs/dump-report-for-job "$job" > "$report"
tools/mvs/job-summary "$job" --max-rc 0
python3 -B "$probe/verify-report.py" "$report"
echo "G!150 startup observer JOB $job: $report"
echo 'Review IEWL MAP/XREF for all G150 owner symbols and installed BLIB.'
