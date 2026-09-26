#!/usr/bin/env python3
"""Generate a self-contained TK5 IFOX assemble, link-edit, and run job."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


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
        if (
            match := re.fullmatch(
                r"([A-Za-z@#$][\w@#$]{0,7})\s+CSECT(?:\s+.*)?",
                line,
            )
        )
    }

    ends = [
        match.group(1).upper()
        for line in source.splitlines()
        if (
            match := re.match(
                r"^\s+END\s+([A-Za-z@#$][\w@#$]{0,7})(?:\s|$)",
                line,
            )
        )
    ]

    return ends[-1] if ends and ends[-1] in sections else None


def check_source(path: Path) -> str:
    """Read and perform basic validation of an assembler source file."""
    try:
        source = path.read_text(encoding="ascii")
    except (OSError, UnicodeError) as exc:
        raise ValueError(
            f"cannot read ASCII assembler source {path}: {exc}"
        ) from exc

    for number, line in enumerate(source.splitlines(), 1):
        if len(line) > 71:
            raise ValueError(
                f"{path}:{number}: source exceeds assembler column 71"
            )

        if line == "/*":
            raise ValueError(
                f"{path}:{number}: /* would terminate inline SYSIN"
            )

    if not source.strip():
        raise ValueError(f"{path}: source is empty")

    return source.rstrip("\r\n") + "\n"


def make_deck(
    source: str,
    name: str,
    entry: str,
    job: str,
    listing: str,
    parm: str | None,
) -> str:
    """Construct the complete assemble, link-edit, and run JCL deck."""
    asm_options, link_options = PROFILES[listing]

    go_parm = f",PARM='{parm}'" if parm is not None else ""
    go_exec = f"//GO       EXEC PGM=*.LKED.SYSLMOD{go_parm},"

    if len(go_exec) > 71:
        raise ValueError(
            "GO PARM is too long for a JCL statement; shorten --parm"
        )

    return f"""//{job:<8} JOB (MVS),'ASM LINK GO',CLASS=A,MSGCLASS=A,
//             MSGLEVEL=(1,1)
//* GENERATED FROM {name.upper()}; LISTING={listing.upper()}
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
        description=(
            "Generate an IFOX/IEWL/GO JCL deck from an assembler source file."
        ),
        epilog=(
            "Example: python tools/make-asm-job.py "
            "asm/assembler-demo.asm --output-dir jcl --listing heavy "
            "--parm XS,1"
        ),
    )

    parser.add_argument(
        "source",
        type=Path,
        help="path to assembler source file",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="existing directory in which to write the generated JCL deck",
    )

    parser.add_argument(
        "--listing",
        choices=PROFILES,
        default="light",
        help=(
            "light: no listings (default); "
            "medium: listing, short XREF and map; "
            "heavy: full XREF, ESD/RLD and link listings. "
            "Source PRINT controls also apply."
        ),
    )

    parser.add_argument(
        "--entry",
        help=(
            "MVS entry control section "
            "(inferred from END operand when possible)"
        ),
    )

    parser.add_argument(
        "--job-name",
        help="override derived MVS JOB name (up to 8 characters)",
    )

    parser.add_argument(
        "--parm",
        help="optional GO EXEC parameter text, e.g. XS,1",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing output deck",
    )

    args = parser.parse_args(argv)

    path = args.source

    if not path.is_file():
        parser.error(f"source does not exist: {path}")

    if not args.output_dir.is_dir():
        parser.error(
            f"output directory does not exist or is not a directory: "
            f"{args.output_dir}"
        )

    name = path.stem

    try:
        source = check_source(path)

        entry = (args.entry or source_entry(source) or "").upper()

        if not MVS_NAME.fullmatch(entry):
            raise ValueError(
                "cannot infer a CSECT from END; specify --entry NAME"
            )

        job = (
            args.job_name
            or re.sub(r"[^A-Z0-9]", "", name.upper())[:8]
        ).upper()

        if not MVS_NAME.fullmatch(job):
            raise ValueError(
                "--job-name must be a valid MVS name of at most 8 characters"
            )

        if args.parm is not None and not re.fullmatch(
            r"[A-Za-z0-9,.=+\-]*",
            args.parm,
        ):
            raise ValueError(
                "--parm supports letters, digits, comma, period, =, +, and -"
            )

        deck = make_deck(
            source,
            path.name,
            entry,
            job,
            args.listing,
            args.parm,
        )

        output = args.output_dir / f"{name}-{args.listing}.jcl"

        with output.open(
            "w" if args.force else "x",
            encoding="ascii",
            newline="\n",
        ) as stream:
            stream.write(deck)

    except (ValueError, OSError) as exc:
        parser.error(str(exc))

    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())

