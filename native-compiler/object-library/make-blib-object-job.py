#!/usr/bin/env python3
"""Generate a non-executing BLIB object-PDS installation and IEWL probe."""
from __future__ import annotations

import argparse
from pathlib import Path
import re

MIN_INT_BAD = "DC F'-./,),(-*,('"


def source(path: Path) -> list[str]:
    lines = path.read_bytes().decode("latin-1").splitlines()
    result = []
    for number, raw in enumerate(lines, 1):
        if raw == "/*":
            raise ValueError(f"{path}:{number}: JCL delimiter in source")
        if any(ord(c) > 127 for c in raw):
            raise ValueError(f"{path}:{number}: non-ASCII assembly card")
        result.append(raw)
    return result


def blib_cards(path: Path) -> str:
    lines = source(path)
    sections = [i for i, s in enumerate(lines) if re.fullmatch(r"\s*CSECT\s*", s)]
    if len(sections) != 1:
        raise ValueError(f"expected one unnamed BLIB CSECT, got {len(sections)}")
    if sum(bool(re.fullmatch(r"\s*EXTRN\s+BCPLMAIN\s*", s)) for s in lines) != 1:
        raise ValueError("missing or duplicate EXTRN BCPLMAIN")
    if sum(bool(re.fullmatch(r"\s*END(?:\s+.*)?", s)) for s in lines) != 1:
        raise ValueError("missing or duplicate END")
    lines[sections[0]] = "BLIB     CSECT"
    repairs = [i for i, s in enumerate(lines) if s.strip() == MIN_INT_BAD]
    if len(repairs) > 1:
        raise ValueError("multiple signed-minimum constants")
    for i in repairs:
        lines[i] = "         DC X'80000000'"
    check_cards(lines)
    return "\n".join(lines) + "\n"


def check_cards(lines: list[str]) -> None:
    for i, line in enumerate(lines, 1):
        if len(line) > 71:
            raise ValueError(f"assembler card {i} exceeds column 71")
        if line == "/*":
            raise ValueError("invalid inline delimiter")


def runtime_cards(path: Path) -> str:
    lines = source(path)
    check_cards(lines)
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("blib_assembly", type=Path)
    parser.add_argument("runtime_assembly", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--dsn", default="HERC02.BCPL.OBJ")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Z0-9@$#]+(?:\.[A-Z0-9@$#]+)+", args.dsn):
        parser.error("invalid uppercase object-library DSN")
    blib = blib_cards(args.blib_assembly)
    runtime = runtime_cards(args.runtime_assembly)
    deck = f"""//BLIBOBJ  JOB (BCPL),'BLIB OBJECT PROBE',CLASS=A,MSGCLASS=A,
//             MSGLEVEL=(1,1)
//* PRECONDITION: {args.dsn} EXISTS AS RECFM=FB,LRECL=80 PDS
//* NO PROGRAM EXECUTION; NO CHANGE TO BCPLMAIN
//ASMBLIB  EXEC PGM=IFOX00,
//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD',
//             REGION=256K
//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR
//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))
//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSPRINT DD SYSOUT=*
//SYSPUNCH DD DUMMY
//SYSGO    DD DSN=&&BLIBOBJ,UNIT=SYSDA,
//             SPACE=(80,(300,100)),DISP=(NEW,PASS),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
//SYSIN    DD *
{blib}/*
//INSTALL  EXEC PGM=IEBGENER,COND=(4,LT,ASMBLIB)
//SYSPRINT DD SYSOUT=*
//SYSIN    DD DUMMY
//SYSUT1   DD DSN=&&BLIBOBJ,DISP=(OLD,PASS)
//SYSUT2   DD DSN={args.dsn}(BLIB),DISP=SHR
//ASMRUN   EXEC PGM=IFOX00,COND=(4,LT,ASMBLIB),
//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD',
//             REGION=256K
//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR
//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))
//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSPRINT DD SYSOUT=*
//SYSPUNCH DD DUMMY
//SYSGO    DD DSN=&&RUNOBJ,UNIT=SYSDA,
//             SPACE=(80,(300,100)),DISP=(NEW,PASS),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
//SYSIN    DD *
{runtime}/*
//LKED     EXEC PGM=IEWL,PARM='NCAL,LIST,XREF,MAP',
//             COND=((4,LT,ASMBLIB),(0,NE,INSTALL),(4,LT,ASMRUN))
//OBJ      DD DSN={args.dsn},DISP=SHR
//SYSLIN   DD DSN=&&RUNOBJ,DISP=(OLD,DELETE)
//         DD *
 INCLUDE OBJ(BLIB)
 ENTRY BLIB
 NAME BLIBCHK(R)
/*
//SYSLMOD  DD DSN=&&GOSET(BLIBCHK),UNIT=SYSDA,
//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)
//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))
//SYSPRINT DD SYSOUT=*
//
"""
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(deck, encoding="ascii", newline="\n")
    print(args.output)


if __name__ == "__main__":
    main()
