#!/usr/bin/env python3
"""Generate an application-only native regression using five installed OBJ members.

Non-submitting. Does not assemble or overwrite BCPLMAIN or service modules.
Only the simple single-BCPL-source strategy is supported by this first gate.
"""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generated", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--test-number", type=int, required=True)
    args = parser.parse_args()
    args.output.unlink(missing_ok=True)
    n = args.test_number
    if not 0 <= n <= 999:
        raise ValueError("invalid regression number")
    original = args.generated.read_bytes().decode("latin-1")
    original = "".join(c if ord(c) < 128 else "?" for c in original)
    lines = original.splitlines()
    csects = [i for i, row in enumerate(lines)
              if re.fullmatch(r"\s*CSECT\s*", row)]
    externs = [row for row in lines
               if re.fullmatch(r"\s*EXTRN\s+BCPLMAIN\s*", row)]
    ends = [i for i, row in enumerate(lines)
            if re.fullmatch(r"\s*END(?:\s+.*)?", row)]
    if len(csects) != 1 or len(externs) != 1 or len(ends) != 1:
        raise ValueError("application requires one CSECT, EXTRN BCPLMAIN, END")
    entry = f"BCRG{n:04d}"
    lines[csects[0]] = f"{entry} CSECT"
    # Match the proven BLIB consumer's handling of malformed signed-minimum
    # constants emitted by this historical CG370 printer transport.
    bad = [i for i, row in enumerate(lines)
           if row.strip() == "DC F'-./,),(-*,('"]
    if len(bad) > 1:
        raise ValueError("multiple malformed minimum-integer constants")
    for index in bad:
        lines[index] = "         DC X'80000000'"
    if any(len(row) > 71 or row == "/*" or row.startswith("//")
           for row in lines):
        raise ValueError("invalid application assembler card")
    core = load(ROOT / "tools/dspal-core.py", "runtime_pds_dspal")
    config = core.load_config()
    dsn, _ = core.resolve_dsn(config, "OBJ")
    if dsn.upper() != "HERC02.BCPL.OBJ":
        raise ValueError(f"unexpected OBJ dataset {dsn}")
    job = f"RG{n:03d}R"
    cards = [
        *core.authenticated_job_card(config, job, "BCPL PDS REG",
                                    redact_password=False),
        "//* OPT-IN INSTALLED RUNTIME; APP ASSEMBLY ONLY",
        "//ASMAP    EXEC PGM=IFOX00,REGION=256K,",
        "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'",
        "//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR",
        "//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))",
        "//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSPRINT DD SYSOUT=*",
        "//SYSPUNCH DD DUMMY",
        "//SYSGO    DD DSN=&&APOBJ,UNIT=SYSDA,",
        "//             SPACE=(80,(300,100)),DISP=(NEW,PASS),",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//SYSIN    DD *", *lines, "/*",
        "//LKED     EXEC PGM=IEWL,PARM='LIST,XREF,MAP',",
        "//             COND=(0,NE,ASMAP)",
        f"//OBJ      DD DSN={dsn},DISP=SHR",
        "//SYSLIN   DD DSN=&&APOBJ,DISP=(OLD,DELETE)",
        "//         DD *",
        " INCLUDE OBJ(BCPLMAIN)",
        " INCLUDE OBJ(BCPLBYTE)",
        " INCLUDE OBJ(BCPLAPT)",
        " INCLUDE OBJ(BCPLMEM)",
        " INCLUDE OBJ(BLIB)",
        f" ENTRY {entry}",
        f" NAME RG{n:03d}OBJ(R)",
        "/*",
        f"//SYSLMOD  DD DSN=&&GOSET(RG{n:03d}OBJ),UNIT=SYSDA,",
        "//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)",
        "//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))",
        "//SYSPRINT DD SYSOUT=*",
        "//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),",
        "//             COND=((0,NE,ASMAP),(0,NE,LKED))",
        "//SYSPRINT DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)",
        "//SYSUDUMP DD SYSOUT=*",
        "//",
    ]
    for index, card in enumerate(cards, 1):
        if len(card) > 71 or not card.isascii():
            raise ValueError(f"invalid JCL card {index}: {card!r}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(cards) + "\n", encoding="ascii", newline="\n")
    print(f"Prepared installed-runtime PDS regression: {args.output}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit(f"runtime-pds-regression: {exc}")
