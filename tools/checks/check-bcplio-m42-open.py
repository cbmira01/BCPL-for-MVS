#!/usr/bin/env python3
"""Static fail-closed audit of M4.2 private OPEN-denial source transform."""
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
original = (ROOT / "bootstrap-toolchain/asm/bcplio.asm").read_text(
    encoding="ascii"
)
module = runpy.run_path(
    str(ROOT / "tools/checks/prepare-bcplio-m42-open.py"),
    run_name="bcplio_m42_transform",
)
anchor = module["ANCHOR"]
transform = module["transform"]
assert original.count(anchor) == 1, "DQOPEN SVC19 call not unique"
changed = transform(original)
assert changed.count("         SVC   19") == original.count(
    "         SVC   19"
), "SVC19 count changed"
assert changed.count("         GETMAIN RC,LV=") == original.count(
    "         GETMAIN RC,LV="
), "GETMAIN count changed"
assert changed.count("F42PH    DC    X'00'") == 1
assert changed.count("         B     DQBAD") >= 1
assert changed.count("F42GO    LA    1,228(6)") == 1
assert all(len(line) <= 71 for line in changed.splitlines())
try:
    transform(changed)
except ValueError:
    pass
else:
    raise AssertionError("repeat instrumentation was not rejected")
print("M4.2 synthetic OPEN source-only checks: PASS")
print("M4.2 actual MVS OPEN failure: NOT TESTED")
