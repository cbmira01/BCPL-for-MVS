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
    args = p.parse_args()
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
    runtime = (ROOT / "asm/bcplmain-wip.asm").read_text(encoding="ascii")
    runtime = inject_runtime(runtime).rstrip("\n") + "\n"
    old = "//SYSIN    DD DSN=HERC02.BCPL.ASM(BCMWIP),DISP=SHR"
    if deck.count(old) != 1:
        raise ValueError("expected one runtime PDS SYSIN DD")
    deck = deck.replace(old, "//SYSIN    DD *\n" + runtime + "/*", 1)
    deck = deck.replace("RG069L", "RG069X")
    deck = deck.replace("BCPL 069 LINK", "BCPL 069 GO")
    if not deck.endswith("//\n"):
        raise ValueError("expected Stage 1 JCL terminator")
    deck = deck[:-3] + """//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,3),
//             COND=((0,NE,ASMAP),(0,NE,ASMRUN),(0,NE,LKED))
//SYSPRINT DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
//SYSUDUMP DD SYSOUT=*
//
"""
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
