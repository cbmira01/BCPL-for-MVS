#!/usr/bin/env python3
"""Build experimental executable 069 from existing Stage 1 assembler.

A test-local BCPLMAIN variant imports BLIB's relocated module trailer.
The canonical runtime and resident OBJ(BLIB) are not changed.
"""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path
import os
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def inject_runtime(source: str) -> str:
    # Exact anchors prevent silent drift of the bootstrap runtime contract.
    anchor = "BCPLMAIN CSECT"
    if source.count(anchor) != 1:
        raise ValueError("expected exactly one runtime CSECT anchor")
    source = source.replace(anchor, anchor + "\n         EXTRN BLIB", 1)
    old = "GIDONE   L     4,4(12)"
    if source.count(old) != 1:
        raise ValueError("expected exactly one GIDONE anchor")
    new = """GIDONE   L     8,=A(BLIB)
* IMPORT BLIB EXPORTED GLOBALS BY EXPLICIT MODULE REGISTRATION.
* THE RELOCATED BLIB ENTRY POINT NAMES THE PREFIX AT OFFSET ZERO.
         LH    0,10(8)
         AR    8,0
BLIMP    AH    8,=H'-8'
         L     9,4(8)
         LTR   9,9
         BZ    BLIDONE
         L     1,0(8)
         C     1,=F'800'
         BH    GTOOBIG
         LR    2,12
         AR    2,1
         ST    9,0(2)
         B     BLIMP
BLIDONE  L     4,4(12)"""
    source = source.replace(old, new, 1)
    if any(len(line) > 71 for line in source.splitlines()):
        raise ValueError("injected BCPLMAIN exceeds assembler column 71")
    return source


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("generated_assembly", type=Path)
    p.add_argument("output_jcl", type=Path)
    p.add_argument("--test-number", type=int, default=69)
    p.add_argument("--external-apt", action="store_true")
    p.add_argument("--external-byte", action="store_true")
    args = p.parse_args()
    if not 69 <= args.test_number <= 999:
        raise ValueError("test number must be between 69 and 999")
    stage1_path = HERE / "prepare-linkage.py"
    spec = importlib.util.spec_from_file_location("stage1_069", stage1_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Stage 1 preparer")
    stage1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stage1)
    # Build an independent Stage 1 JCL first. Its separate section and
    # object-library INCLUDE contracts remain unchanged.
    intermediate = args.output_jcl.with_name("069-stage2-base.jcl")
    try:
        import sys
        saved = sys.argv
        sys.argv = [str(stage1_path), str(args.generated_assembly),
                    str(intermediate)]
        try:
            stage1.main()
        finally:
            sys.argv = saved
        deck = intermediate.read_text(encoding="ascii")
    finally:
        intermediate.unlink(missing_ok=True)
    runtime_source = ROOT / "asm/bcplmain-wip.asm"
    # Test-only, fail-closed transformation; never modify canonical source.
    for opt, helper in (
        (args.external_byte, "externalize-bcplbyte.py"),
        (args.external_apt, "externalize-bcplapt.py"),
    ):
        if opt:
            out = args.output_jcl.with_name("special-" + helper + ".asm")
            subprocess.run(["python3", str(ROOT / "tools/checks" / helper),
                            str(runtime_source), str(out)], check=True)
            runtime_source = out
    runtime = runtime_source.read_text(encoding="ascii")
    runtime = inject_runtime(runtime).rstrip("\n") + "\n"
    old = "//SYSIN    DD DSN=HERC02.BCPL.ASM(BCMWIP),DISP=SHR"
    if deck.count(old) != 1:
        raise ValueError("expected one runtime PDS SYSIN DD")
    deck = deck.replace(old, "//SYSIN    DD *\n" + runtime + "/*", 1)
    deck = deck.replace(
        "//* REGRESSION 069 STAGE 1 - NO GO; NO BLIB RECOMPILATION",
        "//* REGRESSION 069 STAGE 2 - OBJECT LINK AND GO",
    )
    deck = deck.replace("RG069L", "RG069X")
    deck = deck.replace("BCPL 069 LINK", "BCPL 069 GO")
    if args.test_number != 69:
        num = args.test_number
        deck = deck.replace("BCRG0069", f"BCRG{num:04d}")
        deck = deck.replace("RG069", f"RG{num:03d}")
        deck = deck.replace("BCPL 069", f"BCPL {num:03d}")
        deck = deck.replace("REGRESSION 069", f"REGRESSION {num:03d}")
    # Assemble any extracted machine services beside application and
    # BCPLMAIN, while retaining the resident BLIB object PDS INCLUDE.
    extra = []
    if args.external_byte:
        extra.append(("ASMBYTE", "BYTOBJ", ROOT / "asm/bcplbyte.asm"))
    if args.external_apt:
        extra.append(("ASMAPT", "APTOBJ",
                      ROOT / "tools/checks/bcplapt-linkage-probe.asm"))
    previous = "ASMRUN"
    for step, obj, source in extra:
        cards = source.read_text(encoding="ascii").rstrip("\n")
        addition = (
            f"//{step:<8} EXEC PGM=IFOX00,REGION=256K,\\n"
            f"//             COND=(0,NE,{previous}),\\n"
            "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'\\n"
            "//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR\\n"
            "//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))\\n"
            "//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))\\n"
            "//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))\\n"
            "//SYSPRINT DD SYSOUT=*\\n"
            "//SYSPUNCH DD DUMMY\\n"
            f"//SYSGO    DD DSN=&&{obj},UNIT=SYSDA,\\n"
            "//             SPACE=(80,(300,100)),DISP=(NEW,PASS),\\n"
            "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)\\n"
            "//SYSIN    DD *\\n" + cards + "\\n/*\\n"
        )
        place = "//LKED     EXEC PGM=IEWL"
        if deck.count(place) != 1:
            raise ValueError("missing unique LKED step")
        deck = deck.replace(place, addition + place, 1)
        syspass = "//         DD DSN=&&RUNOBJ,DISP=(OLD,DELETE)\\n"
        if deck.count(syspass) != 1:
            raise ValueError("missing RUNOBJ link-edit DD")
        deck = deck.replace(syspass, syspass +
            f"//         DD DSN=&&{obj},DISP=(OLD,DELETE)\\n", 1)
        previous = step
    if extra:
        names = ["ASMAP", "ASMRUN"] + [item[0] for item in extra]
        # Break at complete subparameter boundaries for 71-column JCL.
        def cond(steps):
            lines = []
            line = "//             COND=("
            for i, name in enumerate(steps):
                part = f"(0,NE,{name})" + ("," if i < len(steps)-1 else ")")
                if len(line + part) > 71:
                    lines.append(line)
                    line = "//             " + part
                else:
                    line += part
            lines.append(line)
            return "\\n".join(lines)
        old_link = "//             COND=((0,NE,ASMAP),(0,NE,ASMRUN))"
        if deck.count(old_link) != 1:
            raise ValueError("missing unique original LKED conditions")
        deck = deck.replace(old_link, cond(names), 1)
    if not deck.endswith("//\n"):
        raise ValueError("expected Stage 1 JCL terminator")
    deck = deck[:-3] + """//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,3),
//             COND=((0,NE,ASMAP),(0,NE,ASMRUN),(0,NE,LKED))
//SYSPRINT DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
//SYSUDUMP DD SYSOUT=*
//
"""
    if extra:
        old_go = "//             COND=((0,NE,ASMAP),(0,NE,ASMRUN),(0,NE,LKED))"
        if deck.count(old_go) != 1:
            raise ValueError("missing original GO conditions")
        deck = deck.replace(old_go, cond(names + ["LKED"]), 1)
    for number, line in enumerate(deck.splitlines(), 1):
        if len(line) > 71:
            raise ValueError(f"JCL line {number} exceeds column 71")
    args.output_jcl.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(args.output_jcl, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="ascii", newline="\n") as output:
        output.write(deck)
    print(args.output_jcl)


if __name__ == "__main__":
    main()
