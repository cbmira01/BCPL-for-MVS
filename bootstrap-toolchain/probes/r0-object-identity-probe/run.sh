#!/usr/bin/env bash
# R.0 Decision A stage 2; never writes BOOT_OBJ, BOOT_DEVOBJ or load PDS.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$root"
probe=bootstrap-toolchain/probes/r0-object-identity-probe
out=workarea/runtime-extensions-r0-object-identity
profile=${1:-calibrate}
case "$profile" in
 calibrate|member) ;;
 *) echo "Usage: $0 [calibrate|member]" >&2; exit 2 ;;
esac
# Never attest a tracked source file that differs from HEAD.
for target in bootstrap-toolchain/asm/bcplmem.asm "$probe"; do
 if [[ -n $(git status --porcelain -- "$target") ]]; then
  echo "Source or tool has uncommitted changes: $target" >&2; exit 1
 fi
done
revision=$(git rev-parse HEAD)
mkdir -p "$out"
python3 -B -m unittest discover -s "$probe" -p 'test_*.py' -v
python3 -B "$probe/make-jobs.py" calibrate --check
python3 -B "$probe/make-jobs.py" member --check
if [[ $profile == member ]]; then
 # Do not accidentally run against installed object before positive AND
 # deliberately negative historical IEBCOMPR calibration is reviewed.
 [[ -f "$out/confirmed-calibration.txt" ]] || {
  echo "Stage 2 calibration not owner-confirmed; inspect R0BICAL first." >&2
  echo "After reviewing its IEBCOMPR SYSPRINT, create the approval marker:" >&2
  echo "  printf '%s\\n' '$revision' > '$out/confirmed-calibration.txt'" >&2
  exit 1
 }
 [[ $(cat "$out/confirmed-calibration.txt") == "$revision" ]] || {
  echo 'Calibration approval marker belongs to a different revision' >&2; exit 1
 }
fi
python3 -B "$probe/make-jobs.py" "$profile" --git-revision "$revision"
name=r0bical
[[ $profile == member ]] && name=r0bimem
printf '%s\n' "$revision" > "$out/$name-revision.txt"
sha256sum "$probe/make-jobs.py" "$probe/verify-report.py" \
 "$probe/run.sh" "$probe/test_probe.py" \
 bootstrap-toolchain/asm/bcplmem.asm > "$out/$name-source-sha256.txt"
result=$(bash tools/mvs/submit-jcl "$out/$name.jcl")
printf '%s\n' "$result"
job=$(awk '/^JOB [0-9]+/ {n=$2} END {print n}' <<< "$result")
[[ $job =~ ^[0-9]+$ ]] || { echo 'Missing JES JOB number' >&2; exit 1; }
printf '%s\n' "$job" > "$out/$name-job.txt"
sleep 5
report="$out/job-$job.txt"
tools/mvs/dump-report-for-job "$job" > "$report"
tools/mvs/job-summary "$job" --max-rc 8
# RC=8 is expected in the intentionally unequal calibration comparison;
# it can also indicate an unsuccessful real-member comparison.
python3 -B "$probe/verify-report.py" "$profile" "$report"
echo "R.0 B $profile JES JOB $job; full report $report"
if [[ $profile == calibrate ]]; then
 echo 'Calibration RC pattern passed. Inspect IEBCOMPR SYSPRINT manually.'
 echo 'Only approve member comparison after confirming actual binary mismatch.'
else
 echo 'A comparison RC alone is not final provenance acceptance.'
fi
