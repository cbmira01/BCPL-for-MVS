#!/usr/bin/env python3
"""Host-only check of M4.2.1 JCL patching; no MVS contact."""
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[2]
m = runpy.run_path(
    str(root / "tools/checks/prepare-m42-real-open-jcl.py"),
    run_name="m42_real_open_library",
)
patch = m["change_deck"]
fixture = (
    "//RG890R JOB (BCPL),'PROBE'\n"
    "//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),\n"
    "//             COND=((0,NE,ASMAP),(0,NE,LKED))\n"
    "//SYSPRINT DD SYSOUT=*\n"
    "//DD01     DD DATA,DLM=X0\n"
    "A\nB\nX0\n"
    "//SYSUDUMP DD SYSOUT=*\n"
)
changed = patch(fixture)
assert changed.count("//DD02     DD SYSOUT=*") == 1
assert changed.count("//* M4.2 REAL OPEN PROBE:") == 1
assert changed.index("//DD01     DD DATA") < changed.index(
    "//DD02     DD SYSOUT=*"
) < changed.index("//SYSUDUMP DD SYSOUT=*")
for corrupt in (
    fixture.replace("//RG890R", "//RG891R"),
    fixture.replace("//SYSUDUMP DD SYSOUT=*", ""),
    fixture.replace("//DD01     DD DATA,DLM=X0", ""),
    fixture.replace(
        "//SYSUDUMP DD SYSOUT=*",
        "//DD02     DD SYSOUT=*\n//SYSUDUMP DD SYSOUT=*",
    ),
):
    try:
        patch(corrupt)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid base JCL was accepted")
print("M4.2.1 real-OPEN JCL source-only checker: PASS")
print("M4.2.1 real MVS SVC19 OPEN: NOT YET RUN")
