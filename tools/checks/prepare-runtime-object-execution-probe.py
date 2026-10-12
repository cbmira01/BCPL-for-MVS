#!/usr/bin/env python3
"""Build a non-installing executable probe using the existing regression 28 app.

Requires previously generated Cambridge CG370 assembly from regression 28.
No writes to HERC02.BCPL.OBJ; both runtime candidates are freshly assembled.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "workarea/runtime-object-candidates"
CASE = ROOT / "native-compiler/regression/28-freevec"
GENERATED = ROOT / "workarea/native-regression/28-freevec/generated.s370.asm"


def import_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"module load failed: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / "execute-candidates.jcl"
    dest.unlink(missing_ok=True)
    if not GENERATED.is_file():
        raise ValueError(
            "Missing compiled regression 28 code. Run "
            "BCPL_RUNTIME_PDS=0 BCPLMEM_OBJECT=1 "
            "tools/run-native-regression 28 first."
        )
    if not (OUT / "bcplmain-external-mem.asm").is_file():
        raise ValueError("Run prepare-runtime-object-candidates.py first")
    candidate = import_module(
        ROOT / "tools/checks/prepare-runtime-object-link-probe.py", "cand_link"
    )
    assembler = candidate.load_candidate()
    original_main = OUT / "bcplmain-external-mem.asm"
    main_text = original_main.read_text(encoding="ascii")
    anchor = "BCPLMAIN CSECT\n"
    if main_text.count(anchor) != 1 or "STKOVFL" not in main_text:
        raise ValueError("unrecognized candidate BCPLMAIN")
    linked_main = OUT / "bcplmain-link-export.asm"
    linked_main.write_text(
        main_text.replace(anchor, anchor + "         ENTRY STKOVFL\n", 1),
        encoding="ascii", newline="\n"
    )
    base = OUT / "pds-baseline-28.jcl"
    base.unlink(missing_ok=True)
    subprocess.run(
        [sys.executable, str(ROOT / "tools/checks/prepare-runtime-pds-regression.py"),
         str(GENERATED), str(base), "--test-number", "28",
         "--case-dir", str(CASE)],
        check=True
    )
    cards = base.read_text(encoding="ascii").splitlines()
    jobcards = [i for i, row in enumerate(cards) if row.startswith("//RG028R ")]
    if jobcards != [0]:
        raise ValueError("unexpected baseline job card")
    cards[0] = cards[0].replace("RG028R", "BCOEX28", 1)
    # Keep the PDS DD read-only for BCPLBYTE, BCPLAPT, BLIB.
    start = cards.index("//LKED     EXEC PGM=IEWL,PARM='LIST,XREF,MAP',")
    prefix = [
        *assembler.asm("ASMMMAIN", "MAINOBJ", linked_main),
        *assembler.asm("ASMMMEM", "MEMOBJ", ROOT / "asm/bcplmem.asm",
                       "ASMMMAIN"),
    ]
    cards[start:start] = prefix
    start += len(prefix)
    cond = cards.index("//             COND=(0,NE,ASMAP)", start)
    cards[cond] = (
        "//             COND=((0,NE,ASMAP),(0,NE,ASMMMAIN),"
    )
    cards.insert(cond + 1, "//             (0,NE,ASMMMEM))")
    sl = cards.index("//SYSLIN   DD DSN=&&APOBJ,DISP=(OLD,DELETE)", cond)
    cards[sl + 1:sl + 1] = [
        "//         DD DSN=&&MAINOBJ,DISP=(OLD,DELETE)",
        "//         DD DSN=&&MEMOBJ,DISP=(OLD,DELETE)",
    ]
    for member in ("BCPLMAIN", "BCPLMEM"):
        entry = f" INCLUDE OBJ({member})"
        if cards.count(entry) != 1:
            raise ValueError(f"unexpected include count for {member}")
        cards.remove(entry)
    go_cond = cards.index("//             COND=((0,NE,ASMAP),(0,NE,LKED))")
    cards[go_cond] = "//             COND=((0,NE,ASMAP),(0,NE,ASMMMAIN),"
    cards.insert(go_cond + 1, "//             (0,NE,ASMMMEM),(0,NE,LKED))")
    # Give the output load module a probe name without changing ENTRY.
    name = " NAME RG028OBJ(R)"
    if cards.count(name) != 1:
        raise ValueError("unexpected IEWL NAME")
    cards[cards.index(name)] = " NAME BCOEX28(R)"
    load_dd = "//SYSLMOD  DD DSN=&&GOSET(RG028OBJ),UNIT=SYSDA,"
    if cards.count(load_dd) != 1:
        raise ValueError("unexpected SYSLMOD member naming")
    cards[cards.index(load_dd)] = (
        "//SYSLMOD  DD DSN=&&GOSET(BCOEX28),UNIT=SYSDA,"
    )
    if any(len(row)>71 or not row.isascii() for row in cards):
        raise ValueError("generated job contains bad JCL cards")
    dest.write_text("\n".join(cards) + "\n", encoding="ascii", newline="\n")
    print(f"Prepared non-installing executable regression-28 probe: {dest}")
    print("Expected: ASMAP, ASMMMAIN, ASMMMEM, LKED, GO RC=0000")
    print("Expected BCPL output: 42")
    print("Check IEWL map for candidate BCPLMAIN, BCPLMEM and STKOVFL.")
    print("Only existing BCPLBYTE, BCPLAPT, BLIB are read from OBJ.")
    print("No PDS writes. Do not count this as backup/restore acceptance.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"runtime-execution-probe: FAIL: {exc}")
