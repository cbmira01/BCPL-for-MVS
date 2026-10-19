#!/usr/bin/env bash
# Execute only from a local BCPL-for-MVS Git checkout with live TK5.
set -euo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$here/../../.." && pwd)"
profile="${1:-OBJ}"
[[ "$profile" == OBJ || "$profile" == DEVOBJ ]] || {
  echo 'usage: run-q0.sh [OBJ|DEVOBJ]' >&2; exit 64;
}
work="$root/workarea/qsam-q0-abi"
mkdir -p "$work"

# The resident *demoted Cambridge compiler* generates our application ASM.
python3 "$root/tools/bootstrap/compile-mvs" \
  "$here/caller.bcpl" --job-name QS0DISPC \
  --output "$work/caller.s370.asm"

python3 "$here/prepare-job.py" \
  --generated "$work/caller.s370.asm" \
  --output "$work/qs0-dispatch.jcl" --profile "$profile"

# This GO job assembles the test dispatcher separately, includes existing
# BOOT_OBJ/BOOT_DEVOBJ runtime members, and DOES NOT write to object PDSs.
echo '=== Submitting Q.0 dispatcher ABI probe ==='
bash "$root/tools/mvs/submit-jcl" "$work/qs0-dispatch.jcl"
echo '=== Use the job number above to inspect JCL results ==='
echo 'tools/mvs/job-summary <number> --max-rc 0'
echo 'tools/mvs/dump-report-for-job <number>'
echo 'PASS requires ASMAP/ASMNAT/LKED/GO RC=0000 and DEBUGINT output 42.'
