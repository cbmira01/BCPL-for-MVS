#!/usr/bin/env bash
# R.0 test-only; does not overwrite BOOT_OBJ, BOOT_DEVOBJ or runtime source.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$root"
probe=bootstrap-toolchain/probes/r0-export-trailer-probe
out=workarea/runtime-extensions-r0-trailers
mkdir -p "$out"

python3 -B -m unittest discover -s "$probe" -p test_trailers.py -v
python3 -B "$probe/make-job.py" --check

# Actual resident CAMBCOMP compiles the sample application to CG370 ASM.
# This step runs ICINT19 in a normal, read-only compiler JOB.
tools/bootstrap/compile-mvs \
  bootstrap-toolchain/regression/00-most-degenerate-bcpl-program/source.bcpl \
  --job-name R0TRCMP \
  --output "$out/app.s370.asm"

python3 -B "$probe/make-job.py" --check --generated "$out/app.s370.asm"
python3 -B "$probe/make-job.py" --generated "$out/app.s370.asm"

printf '%s\n' "Source Git HEAD: $(git rev-parse HEAD)" \
  > "$out/source-provenance.txt"
sha256sum "$probe/trailer-observer.asm" "$out/app.s370.asm" \
  >> "$out/source-provenance.txt"
printf '%s\n' "Generated evidence JCL: $out/r0-trailer.jcl"

result=$(bash tools/mvs/submit-jcl "$out/r0-trailer.jcl")
printf '%s\n' "$result"
job=$(awk '/^JOB [0-9]+/ {n=$2} END {print n}' <<< "$result")
if [[ ! $job =~ ^[0-9]+$ ]]; then
  echo 'ERROR: no JES job number in submission output' >&2
  exit 1
fi
printf '%s\n' "$job" > "$out/latest-job-number.txt"
sleep 5
report="$out/job-$job.txt"
tools/mvs/dump-report-for-job "$job" > "$report"
tools/mvs/job-summary "$job" --max-rc 0
python3 -B "$probe/parse-report.py" "$report" \
  --job-number "$job" --output "$out/ledger-job-$job.json"
echo "R.0 linked application + installed BLIB evidence: JOB $job"
echo "Report: $report"
echo "Linker MAP, all step RCs, and object build provenance need review."
