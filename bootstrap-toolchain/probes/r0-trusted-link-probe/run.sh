#!/usr/bin/env bash
# R.0 Decision A isolated link experiment; accepted object PDS unchanged.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$root"
probe=bootstrap-toolchain/probes/r0-trusted-link-probe
out=workarea/runtime-extensions-r0-a
profile=${1:-valid}
case "$profile" in
 valid|goodhook|regzero|regunal|pkgbound|reglen|pkglen|regvers|pkgvers|badhook) ;;
 *) echo "Unknown R.0 A profile: $profile" >&2; exit 2 ;;
esac
mkdir -p "$out"
python3 -B -m unittest discover -s "$probe" -p 'test_*.py' -v
for p in valid goodhook regzero regunal pkgbound reglen pkglen regvers pkgvers badhook; do
 python3 -B "$probe/make-jobs.py" "$p" --check
done
revision=$(git rev-parse HEAD)
python3 -B "$probe/make-jobs.py" "$profile" --git-revision "$revision"
command -v sha256sum >/dev/null
printf '%s\n' "$revision" > "$out/git-revision.txt"
sha256sum "$probe/make-jobs.py" "$probe/validator.asm" "$probe/function.asm" > "$out/generator-sha256.txt"
name=$(printf '%s' "$profile" | tr '[:upper:]' '[:lower:]')
case "$profile" in
 valid) jobname=r0alink ;;
 goodhook) jobname=r0ahook ;;
 regzero) jobname=r0aregx ;;
 regunal) jobname=r0aunal ;;
 pkgbound) jobname=r0apkge ;;
 reglen) jobname=r0arlen ;;
 pkglen) jobname=r0aplen ;;
 regvers) jobname=r0arver ;;
 pkgvers) jobname=r0apver ;;
 badhook) jobname=r0abadh ;;
esac
result=$(bash tools/mvs/submit-jcl "$out/$jobname.jcl")
printf '%s\n' "$result"
job=$(awk '/^JOB [0-9]+/ {n=$2} END {print n}' <<< "$result")
[[ $job =~ ^[0-9]+$ ]] || { echo 'No JES JOB number returned' >&2; exit 1; }
printf '%s\n' "$job" > "$out/$profile-job.txt"
sleep 5
report="$out/job-$job.txt"
tools/mvs/dump-report-for-job "$job" > "$report"
tools/mvs/job-summary "$job" --max-rc 0
python3 -B "$probe/verify-report.py" "$profile" "$report"
echo "R.0 A $profile MVS evidence: JOB $job"
echo "IEWL MAP/XREF requires owner inspection: $report"
echo 'Expected CSECT owners: R0ATST / R0AREG / R0APKG / R0AFUN.'
