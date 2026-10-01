#!/usr/bin/env python3
"""Generate a self-contained TK5 IFOX assemble, link-edit, and run job."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ASM_DIR = ROOT / "asm"
JCL_DIR = ROOT / "jcl"
PROFILES = {
    "light": ("OBJECT,NODECK,NOLIST,NOXREF", "LET,NCAL"),
    "medium": ("OBJECT,NODECK,LIST,XREF(SHORT)", "LET,NCAL,MAP"),
    "heavy": ("OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD", "LET,NCAL,LIST,XREF"),
}
MVS_NAME = re.compile(r"[A-Z@#$][A-Z0-9@#$]{0,7}\Z")


def source_entry(source: str) -> str | None:
    """Use the END operand when it names a control section in this source."""
    sections = {
        match.group(1).upper()
        for line in source.splitlines()
        if (match := re.fullmatch(
            r"([A-Za-z@#$][\w@#$]{0,7})\s+CSECT(?:\s+.*)?", line
        ))
    }
    ends = [
        match.group(1).upper()
        for line in source.splitlines()
        if (match := re.match(r"^\s+END\s+([A-Za-z@#$][\w@#$]{0,7})(?:\s|$)", line))
    ]
    return ends[-1] if ends and ends[-1] in sections else None


def check_source(path: Path) -> str:
    try:
        source = path.read_text(encoding="ascii")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read ASCII assembler source {path}: {exc}") from exc
    for number, line in enumerate(source.splitlines(), 1):
        if len(line) > 71:
            raise ValueError(f"{path}:{number}: source exceeds assembler column 71")
        if line == "/*":
            raise ValueError(f"{path}:{number}: /* would terminate inline SYSIN")
    if not source.strip():
        raise ValueError(f"{path}: source is empty")
    return source.rstrip("\r\n") + "\n"


def make_deck(source: str, name: str, entry: str, job: str,
              listing: str, parm: str | None) -> str:
    asm_options, link_options = PROFILES[listing]
    go_parm = f",PARM='{parm}'" if parm is not None else ""
    go_exec = f"//GO       EXEC PGM=*.LKED.SYSLMOD{go_parm},"
    if len(go_exec) > 71:
        raise ValueError("GO PARM is too long for a JCL statement; shorten --parm")
    return f"""//{job:<8} JOB (BCPL),'ASM LINK GO',CLASS=A,MSGCLASS=A,
//             MSGLEVEL=(1,1)
//* GENERATED FROM ASM/{name.upper()}.ASM; LISTING={listing.upper()}
//* THE ASM SOURCE IS INLINED BELOW. REGENERATE AFTER EDITING IT.
//ASM      EXEC PGM=IFOX00,
//             PARM='{asm_options}',REGION=256K
//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR
//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))
//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSPRINT DD  SYSOUT=*
//SYSPUNCH DD  DUMMY
//SYSGO    DD  DSN=&&OBJSET,UNIT=SYSDA,SPACE=(80,(300,100)),
//             DISP=(MOD,PASS)
//SYSIN    DD  *
{source}/*
//*
//LKED     EXEC PGM=IEWL,PARM='{link_options}',REGION=256K,
//             COND=(4,LT,ASM)
//SYSLIN   DD  DSN=&&OBJSET,DISP=(OLD,DELETE)
//         DD  *
  ENTRY {entry}
  NAME RUNMOD(R)
/*
//SYSLMOD  DD  DSN=&&GOSET(RUNMOD),UNIT=SYSDA,
//             SPACE=(1024,(50,20,1)),DISP=(MOD,PASS)
//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))
//SYSPRINT DD  SYSOUT=*
//*
{go_exec}
//             COND=((4,LT,ASM),(4,LT,LKED))
//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
//SYSUDUMP DD  SYSOUT=*
//
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inline asm/NAME.asm into an IFOX/IEWL/GO JCL deck in jcl/.",
        epilog="Example: python tools/make-asm-job.py assembler-demo "
               "--listing heavy --parm XS,1",
    )
    parser.add_argument("program", nargs="?", help="source basename in asm/ (with or without .asm)")
    parser.add_argument("--listing", choices=PROFILES, default="medium",
                        help="light: no listings; medium: listing, short XREF and map "
                             "(default); heavy: full XREF, ESD/RLD and link listings. "
                             "Source PRINT controls also apply.")
    parser.add_argument("--entry", help="MVS entry control section (inferred from END operand when possible)")
    parser.add_argument("--job-name", help="override derived MVS JOB name (up to 8 characters)")
    parser.add_argument("--parm", help="optional GO EXEC parameter text, e.g. XS,1")
    parser.add_argument("--output", type=Path, help="output deck (default: jcl/NAME.jcl)")
    parser.add_argument("--force", action="store_true", help="replace an existing output deck")
    parser.add_argument("--list", action="store_true", help="list available asm/ programs")
    args = parser.parse_args(argv)
    if args.list:
        for path in sorted(ASM_DIR.glob("*.asm")):
            print(path.name)
        return 0
    if not args.program:
        parser.print_help()
        return 0
    name = args.program.removesuffix(".asm")
    if not name or Path(name).name != name or name in (".", ".."):
        parser.error("program must be a basename inside asm/")
    path = ASM_DIR / f"{name}.asm"
    if not path.is_file():
        parser.error(f"source does not exist: {path}")
    try:
        source = check_source(path)
        entry = (args.entry or source_entry(source) or "").upper()
        if not MVS_NAME.fullmatch(entry):
            raise ValueError("cannot infer a CSECT from END; specify --entry NAME")
        job = (args.job_name or "BC" + re.sub(r"[^A-Z0-9]", "", name.upper())[:6]).upper()
        if not MVS_NAME.fullmatch(job):
            raise ValueError("--job-name must be a valid MVS name of at most 8 characters")
        if args.parm is not None and not re.fullmatch(r"[A-Za-z0-9,.=+\-]*", args.parm):
            raise ValueError("--parm supports letters, digits, comma, period, =, +, and -")
        deck = make_deck(source, name, entry, job, args.listing, args.parm)
        output = args.output or JCL_DIR / f"{name}.jcl"
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w" if args.force else "x", encoding="ascii", newline="\n") as stream:
            stream.write(deck)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
