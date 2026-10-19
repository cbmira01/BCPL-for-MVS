#!/usr/bin/env python3
"""Stage M4.2.3 bad-FB-blocksize QSAM OPEN exploratory JCL. NEVER submit.

Normal installed DEVOBJ BCPLM6+BCPLIO; reused compiled BCPL assembler.
The DD02 SYSOUT DCB asks RECFM=FB,LRECL=80,BLKSIZE=81, which
violates FB block-size divisibility. MVS/JES may reject before OPEN,
fail/abend during SVC19, or accept; all results are exploratory.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "tools/checks/prepare-runtime-pds-regression.py"
CASE = ROOT / "bootstrap-toolchain/probes/m42-real-open"
GO = "//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),"
SYSUDUMP = "//SYSUDUMP DD SYSOUT=*"
DD02 = "//DD02     DD SYSOUT=*,DCB=(RECFM=FB,LRECL=80,BLKSIZE=81)"
BANNER = "//* M4.2.3 INVALID FB DCB MAY ABEND; NOT REGRESSION"


def transform(base: str) -> str:
    if not base.startswith("//RG892R"):
        raise ValueError("expected RG892R generated JOB card")
    if base.count("//DD01     DD DATA,DLM=X0") != 1:
        raise ValueError("expected exactly one DD01 data fixture")
    if base.count(GO) != 1 or base.count(SYSUDUMP) != 1:
        raise ValueError("expected unique GO and SYSUDUMP anchors")
    if any(line.startswith("//DD02") for line in base.splitlines()):
        raise ValueError("DD02 was already allocated")
    data = base.replace(SYSUDUMP, DD02 + "\n" + SYSUDUMP, 1)
    data = data.replace(GO, BANNER + "\n" + GO, 1)
    if data.count(DD02) != 1 or data.count(BANNER) != 1:
        raise ValueError("duplicate/absent diagnostic JCL changes")
    for line_no, card in enumerate(data.splitlines(), 1):
        if not card.isascii() or len(card) > 71:
            raise ValueError(f"unsafe JCL card {line_no}: {card!r}")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generated", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    for key, expected in (
        ("BCPL_RUNTIME_PDS", "1"),
        ("BCPL_RUNTIME_LIBRARY", "DEVOBJ"),
        ("BCPL_RUNTIME_CANDIDATE", "1"),
        ("BCPL_RUNTIME_CANDIDATE_MEMBER", "BCPLM6"),
    ):
        if os.environ.get(key) != expected:
            raise ValueError(f"{key} must be {expected}")
    if not args.generated.is_file():
        raise ValueError(f"missing Cambridge output: {args.generated}")
    if args.generated.resolve() == args.output.resolve():
        raise ValueError("input and output paths cannot be equal")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".base")
    try:
        subprocess.run(
            [
                sys.executable, str(BASE),
                str(args.generated), str(temporary),
                "--test-number", "892", "--case-dir", str(CASE),
            ],
            cwd=ROOT, check=True,
        )
        data = transform(temporary.read_text(encoding="ascii"))
        args.output.write_text(data, encoding="ascii", newline="\n")
    finally:
        temporary.unlink(missing_ok=True)
    print("Prepared M4.2.3 INVALID-FB real OPEN exploratory deck:")
    print(args.output)
    print("RG892R: DD02 SYSOUT,RECFM=FB,LRECL=80,BLKSIZE=81")
    print("INVALID: 81 is not divisible by 80; JES or OPEN may reject")
    print("GO job NOT submitted. No installed PDS member changed.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        sys.exit(f"prepare-m42-fb-open-jcl: {exc}")
