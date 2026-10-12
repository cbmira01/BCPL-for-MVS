#!/usr/bin/env bash
# Gate B: synchronize assembler source and build JCL ONLY.
# Does NOT submit BLDBMAIN and does NOT write OBJ.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$root"
python3 tools/checks/stage-bldbmain.py
echo "Inspect workarea/runtime-object-candidates/bldbmain-gate-b.manifest"
echo "Source and JCL updates are separate PDS batches."
echo "Checking existing members..."
src_members="$(tools/dspal ls SOURCE)"
jcl_members="$(tools/dspal ls JCL)"
for member in BCPLMAIN BCPLMEM; do
  if grep -qx "$member" <<< "$src_members"; then
    tools/dspal rm SOURCE "$member"
  fi
done
# Compress ONCE after the entire SOURCE removal batch; even if none existed.
tools/dspal compress SOURCE
tools/dspal put SOURCE BCPLMAIN workarea/runtime-object-candidates/bcplmain-pds.asm
tools/dspal put SOURCE BCPLMEM asm/bcplmem.asm
if grep -qx BLDBMAIN <<< "$jcl_members"; then
  tools/dspal rm JCL BLDBMAIN
fi
tools/dspal compress JCL
tools/dspal put JCL BLDBMAIN jcl/build-bcplmain-objects.jcl
echo "Checking resident source and build JCL by readback..."
tools/dspal get SOURCE BCPLMAIN workarea/runtime-object-candidates/readback-bcplmain.asm
tools/dspal get SOURCE BCPLMEM workarea/runtime-object-candidates/readback-bcplmem.asm
tools/dspal get JCL BLDBMAIN workarea/runtime-object-candidates/readback-bldbmain.jcl
python3 - <<'PY'
from pathlib import Path
root = Path("workarea/runtime-object-candidates")
for a, b in (
    (root / "bcplmain-pds.asm", root / "readback-bcplmain.asm"),
    (Path("asm/bcplmem.asm"), root / "readback-bcplmem.asm"),
    (Path("jcl/build-bcplmain-objects.jcl"), root / "readback-bldbmain.jcl"),
):
    original = a.read_text("ascii").splitlines()
    actual = b.read_text("ascii").splitlines()
    if [line.rstrip(" ") for line in original] != [line.rstrip(" ") for line in actual]:
        raise SystemExit(f"READBACK MISMATCH: {a}")
    print(f"READBACK OK: {a}")
PY
echo "Gate B resident text synchronized; OBJ was NOT changed."
echo "Optional next: tools/dspal submit JCL BLDBMAIN --wait"
