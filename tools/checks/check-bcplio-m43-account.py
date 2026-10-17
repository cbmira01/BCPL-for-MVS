#!/usr/bin/env python3
"""Check M4.3 private accounting instrumentation without MVS."""
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
lib = runpy.run_path(
    str(ROOT / "tools/checks/prepare-bcplio-m43-account.py"),
    run_name="m43_test_library",
)
transform = lib["transform"]
names = lib["COUNTERS"]
original = (
    ROOT / "native-compiler/asm/bcplio.asm"
).read_text(encoding="ascii")
generated = transform(original)
terminal = transform(original, terminal_check=True)
assert terminal.count("DRAINDN  L     1,=A(DHEAD)") == 1
assert terminal.count("         BNZ   M43TRAP") == 2
assert terminal.count("         BNE   M43TRAP") == 6
# Two list heads plus six counter-pair comparisons = eight guards.
assert (terminal.count("         BNZ   M43TRAP") +
        terminal.count("         BNE   M43TRAP")) == 8
assert terminal.count("M43DONE  LM    0,10,DRSAVE") == 1
assert terminal.count("M43TRAP  DC    X\x270000\x27") == 1
assert terminal.count("         L     1,=A(M43TAB)") == 1
assert terminal.count("         END   BCPLIO") == 1
assert "M43TRAP" not in generated
assert terminal.count("         A     0,M43ONE") == 11
assert all(row.isascii() and len(row) <= 71
           for row in terminal.splitlines())
print("M4.3 post-IODRAIN terminal assertions: source check PASS")

for site, count in (
    ("GETMAIN RC,LV=32", 1),
    ("GETMAIN RC,LV=268", 1),
    ("GETMAIN RC,LV=16", 1),
    ("FREEMAIN R,LV=32", 2),
    ("FREEMAIN R,LV=268", 1),
    ("FREEMAIN R,LV=16", 1),
    ("         SVC   19", 1),
    ("         SVC   20", 1),
):
    assert original.count(site) == count, (site, "source drift")
    assert generated.count(site) == count, (site, "missing call site")
for i, name in enumerate(names):
    assert generated.count(f"{name:<8} DC    F'0'") == 1, i
    assert generated.count(f"A({name})") == 1, i
assert generated.count("         ENTRY IOACCT") == 1
assert generated.count("         END   BCPLIO") == 1
assert generated.count("         A     0,M43ONE") == 11
assert "         LA    0,1(0)" not in generated
for constant in ("M43ONED", "M43ONEQ", "M43ONEH", "M43ONER"):
    assert generated.count(f"{constant:<8} DC    F'1'") == 1
assert all(row.isascii() and len(row) <= 71
           for row in generated.splitlines())
try:
    transform(generated)
except ValueError:
    pass
else:
    raise AssertionError("repeat instrumentation accepted")
for site in (
    "         GETMAIN RC,LV=268",
    "         SVC   19",
    "         FREEMAIN R,LV=16,A=(1)",
):
    for bad in (original.replace(site, "", 1), original + site):
        try:
            transform(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted changed site {site!r}")
# JOB 7878 exposed a missing IFOX base register in the test shim.
# Require a base before the V-type external literal, separately from
# the canonical BCPLIO instrumentation source audit.
shim = (ROOT / "native-compiler/regression/139-dynamic-dd-resource-accounting/"
        "native.asm").read_text(encoding="ascii")
assert shim.count("         L     15,=V(IOACCT)") == 1
assert shim.count("         EXTRN IOACCT") == 1
assert shim.count("         BALR  10,0\n         USING *,10\n"
                  "         L     15,=V(IOACCT)") == 1
assert shim.count("         DROP  10") == 1
assert shim.count("         END") == 1
assert all(line.isascii() and len(line) <= 71
           for line in shim.splitlines())
print("M4.3 native counter shim base setup: source check PASS")
print("M4.3 private source accounting checks: PASS")
print("MVS assembly and execution/accounting evidence: NOT TESTED")
