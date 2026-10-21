#!/usr/bin/env bash
# R.0 Decision E: read-only installed core; temporary no-G76 BLIB.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$root"
probe=bootstrap-toolchain/probes/r0-g76-noexport-probe
out=workarea/runtime-extensions-r0-g76-noexport
mkdir -p "$out"
for src in "$probe" bootstrap-toolchain/asm/bcplmain.asm; do
 if [[ -n $(git status --porcelain -- "$src") ]]; then
  echo "Refuse uncommitted source/tool $src" >&2; exit 1
 fi
done
python3 -B -m unittest discover -s "$probe" -p 'test_*.py' -v
python3 -B "$probe/make-job.py" --check
bash -n "$probe/run.sh"
tools/bootstrap/compile-mvs "$probe/source.bcpl" \
  --job-name R0G76FC --output "$out/app.s370.asm"
python3 -B "$probe/make-job.py" --check --generated "$out/app.s370.asm"
python3 -B "$probe/make-job.py" --generated "$out/app.s370.asm"
printf 'Git HEAD: %s\n' "$(git rev-parse HEAD)" > "$out/provenance.txt"
sha256sum "$probe/source.bcpl" "$probe/blib-empty.asm" \
 "$probe/make-job.py" "$out/app.s370.asm" >> "$out/provenance.txt"
result=$(bash tools/mvs/submit-jcl "$out/r0-g76-noexport.jcl")
printf '%s\n' "$result"
job=$(awk '/^JOB [0-9]+/ {n=$2} END {print n}' <<< "$result")
[[ $job =~ ^[0-9]+$ ]] || { echo 'Missing JES job number' >&2; exit 1; }
printf '%s\n' "$job" > "$out/latest-job-number.txt"
sleep 5
tools/mvs/dump-report-for-job "$job" > "$out/job-$job.txt"
tools/mvs/job-summary "$job" --max-rc 0
python3 -B "$probe/verify-report.py" "$out/job-$job.txt"
echo "G!76 fallback fixture JOB $job: $out/job-$job.txt"
echo 'Confirm IEWL MAP/XREF resolves BLIB solely from temporary ASMB.'
