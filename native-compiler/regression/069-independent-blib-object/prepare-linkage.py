#!/usr/bin/env python3
"""Generate non-executing three-section 069 object-linkage JCL.

Input is recovered, resident-Cambridge-produced application assembler;
BLIB is retrieved from the persistent OBJ(BLIB) member, never rebuilt.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import re


def app_cards(path: Path) -> str:
    text = path.read_bytes().decode("latin-1")
    text = "".join(c if ord(c) < 128 else "?" for c in text)
    lines = text.splitlines()
    csects = [i for i, s in enumerate(lines)
              if re.fullmatch(r"\s*CSECT\s*", s)]
    externs = [s for s in lines
               if re.fullmatch(r"\s*EXTRN\s+BCPLMAIN\s*", s)]
    ends = [i for i, s in enumerate(lines)
            if re.fullmatch(r"\s*END(?:\s+.*)?", s)]
    if len(csects) != 1 or len(externs) != 1 or len(ends) != 1:
        raise ValueError("expected one unnamed CSECT, EXTRN BCPLMAIN and END")
    lines[csects[0]] = "BCRG0069 CSECT"
    bad = [i for i, s in enumerate(lines)
           if s.strip() == "DC F'-./,),(-*,('"]
    if len(bad) > 1:
        raise ValueError("multiple malformed signed-minimum constants")
    for i in bad:
        lines[i] = "         DC X'80000000'"
    for i, line in enumerate(lines, 1):
        if len(line) > 71 or line == "/*":
            raise ValueError(f"invalid assembler card at line {i}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generated_assembly", type=Path)
    parser.add_argument("output_jcl", type=Path)
    args = parser.parse_args()
    app = app_cards(args.generated_assembly)
    root = Path(__file__).resolve().parents[3]
    core_path = root / "tools/dspal-core.py"
    spec = importlib.util.spec_from_file_location("dspal_core_069", core_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import dspal configuration")
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    config = core.load_config()
    header = "\n".join(core.authenticated_job_card(
        config, "RG069L", "BCPL REGRESSION 069 LINK", redact_password=False
    )) + "\n"
    deck = header + """//* REGRESSION 069 STAGE 1 — NO GO; NO BLIB RECOMPILATION
//* APPLICATION, BCPLMAIN AND LIBRARY ARE INDEPENDENT CSECTS
//ASMAP    EXEC PGM=IFOX00,REGION=256K,
//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'
//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR
//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))
//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSPRINT DD SYSOUT=*
//SYSPUNCH DD DUMMY
//SYSGO    DD DSN=&&APOBJ,UNIT=SYSDA,
//             SPACE=(80,(300,100)),DISP=(NEW,PASS),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
//SYSIN    DD *
""" + app + """/*
//ASMRUN   EXEC PGM=IFOX00,REGION=256K,COND=(0,NE,ASMAP),
//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'
//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR
//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))
//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSPRINT DD SYSOUT=*
//SYSPUNCH DD DUMMY
//SYSGO    DD DSN=&&RUNOBJ,UNIT=SYSDA,
//             SPACE=(80,(300,100)),DISP=(NEW,PASS),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
//SYSIN    DD DSN=HERC02.BCPL.ASM(BCMWIP),DISP=SHR
//*
//LKED     EXEC PGM=IEWL,PARM='NCAL,LIST,XREF,MAP',
//             COND=((0,NE,ASMAP),(0,NE,ASMRUN))
//OBJ      DD DSN=HERC02.BCPL.OBJ,DISP=SHR
//SYSLIN   DD DSN=&&APOBJ,DISP=(OLD,DELETE)
//         DD DSN=&&RUNOBJ,DISP=(OLD,DELETE)
//         DD *
 INCLUDE OBJ(BLIB)
 ENTRY BCRG0069
 NAME RG069OBJ(R)
/*
//SYSLMOD  DD DSN=&&GOSET(RG069OBJ),UNIT=SYSDA,
//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)
//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))
//SYSPRINT DD SYSOUT=*
//
"""
    if any(len(line) > 71 for line in deck.splitlines()):
        raise ValueError("JCL card exceeds column 71")
    args.output_jcl.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(args.output_jcl, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="ascii", newline="\n") as output:
        output.write(deck)
    print(args.output_jcl)


if __name__ == "__main__":
    main()
