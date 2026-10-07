#!/usr/bin/env python3
"""Build JCL for a two-object native regression.

The BCPL-generated/runtime source and a native assembler routine are assembled
in separate IFOX steps.  IEWL then resolves externals across both object decks
and runs the resulting load module.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def read_source(path: Path) -> str:
    text = path.read_text(encoding="ascii").replace("\r\n", "\n").replace("\r", "\n")
    for number, line in enumerate(text.splitlines(), 1):
        if len(line) > 71:
            raise ValueError(f"{path}:{number}: source exceeds assembler column 71")
        if line == "/*":
            raise ValueError(f"{path}:{number}: /* would terminate inline SYSIN")
    if not text.strip():
        raise ValueError(f"{path}: source is empty")
    return text.rstrip("\n") + "\n"


def asm_step(name: str, obj: str, source: str, cond: str = "") -> str:
    condition = f",\n//             COND={cond}" if cond else ""
    return f"""//{name:<8} EXEC PGM=IFOX00,{condition}
//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD',REGION=256K
//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR
//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))
//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSPRINT DD  SYSOUT=*
//SYSPUNCH DD  DUMMY
//SYSGO    DD  DSN=&&{obj},UNIT=SYSDA,SPACE=(80,(300,100)),
//             DISP=(MOD,PASS)
//SYSIN    DD  *
{source}/*
"""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("bcpl_source", type=Path)
    p.add_argument("native_source", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--entry", required=True)
    p.add_argument("--job-name", required=True)
    args = p.parse_args()

    bcpl = read_source(args.bcpl_source)
    native = read_source(args.native_source)

    deck = f"""//{args.job_name:<8} JOB (MVS),'ASM LINK GO',CLASS=A,MSGCLASS=A,
//             MSGLEVEL=(1,1)
//* REGRESSION: BCPL AND NATIVE ROUTINE ASSEMBLED SEPARATELY
{asm_step("ASMBCPL", "OBJBCPL", bcpl)}
{asm_step("ASMNAT", "OBJNAT", native, "(4,LT,ASMBCPL)")}
//LKED     EXEC PGM=IEWL,PARM='LET,NCAL,LIST,XREF',REGION=256K,
//             COND=((4,LT,ASMBCPL),(4,LT,ASMNAT))
//SYSLIN   DD  DSN=&&OBJBCPL,DISP=(OLD,DELETE)
//         DD  DSN=&&OBJNAT,DISP=(OLD,DELETE)
//         DD  *
  ENTRY {args.entry}
  NAME RUNMOD(R)
/*
//SYSLMOD  DD  DSN=&&GOSET(RUNMOD),UNIT=SYSDA,
//             SPACE=(1024,(50,20,1)),DISP=(MOD,PASS)
//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))
//SYSPRINT DD  SYSOUT=*
//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),
//             COND=((4,LT,ASMBCPL),(4,LT,ASMNAT),(4,LT,LKED))
//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
//SYSUDUMP DD  SYSOUT=*
//
"""
    args.output.write_text(deck, encoding="ascii", newline="\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
