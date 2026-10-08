#!/usr/bin/env bash
# Stage 1 only: compile 069 on resident Cambridge; link three CSECTs;
# verify the IEWL map manually. NO GO and NO BLIB recompilation.
set -euo pipefail
root="$(cd "$(dirname "$0")/../../.." && pwd)"
case_dir="$root/native-compiler/regression/069-independent-blib-object"
work="$root/workarea/native-regression/069-independent-blib-object"
mkdir -p "$work"
cp "$case_dir/source.bcpl" "$work/069-independent-blib-object.bcpl"
cd "$root"
python3 tools/cambridge-compile-mvs \
    "$work/069-independent-blib-object.bcpl" \
    --job-name RG069C --listing light --timeout 180
recovered="$root/workarea/069-independent-blib-object.s370.asm"
test -s "$recovered" || { echo "Missing resident compiler output: $recovered" >&2; exit 1; }
mv "$recovered" "$work/generated.s370.asm"
python3 "$case_dir/prepare-linkage.py" \
    "$work/generated.s370.asm" "$work/069-stage1-link.jcl"
echo "=== Submit regression 069, Stage 1 only (no GO) ==="
bash tools/submit-jcl --timeout 30 "$work/069-stage1-link.jcl"
echo "Use tools/job-summary JOBNO and tools/dump-report-for-job JOBNO"
echo "Inspect IEWL map for BCRG0069, BCPLMAIN and BLIB."
