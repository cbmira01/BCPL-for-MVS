#!/usr/bin/env python3
"""Build M4.2 real-OPEN exploratory JCL (NEVER submit).

Forces one DD02 SYSOUT allocation under a program requesting input.
Uses the normal installed DEVOBJ BCPLM6 + BCPLIO, not fault injection.
The resulting job may ABEND; it is not part of native regression.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "bootstrap-toolchain/probes/m42-real-open"
GENERATOR = ROOT / "tools/checks/prepare-runtime-pds-regression.py"
SYSUDUMP = "//SYSUDUMP DD SYSOUT=*"
DD02 = (
    "//DD02     DD SYSOUT=*,"
    "DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)"
)
NOTICE = "//* M4.2 REAL OPEN PROBE: GO MAY ABEND; NOT REGRESSION"


def single(data: str, token: str) -> None:
    if data.count(token) != 1:
        raise ValueError(
            f"expected one {token!r}, observed {data.count(token)}"
        )


def change_deck(data: str) -> str:
    single(data, SYSUDUMP)
    single(data, "//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),")
    single(data, "//DD01     DD DATA,DLM=X0")
    if "//DD02" in data:
        raise ValueError("DD02 already present in baseline job")
    if not data.lstrip().startswith("//RG890R"):
        raise ValueError("unexpected job identity, expected RG890R")
    data = data.replace(SYSUDUMP, DD02 + "\n" + SYSUDUMP, 1)
    data = data.replace(
        "//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),",
        NOTICE + "\n"
        "//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),",
        1,
    )
    for n, card in enumerate(data.splitlines(), 1):
        if not card.isascii() or len(card) > 71:
            raise ValueError(f"invalid JCL card {n}: {card!r}")
    return data


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("generated", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    for key, required in (
        ("BCPL_RUNTIME_PDS", "1"),
        ("BCPL_RUNTIME_LIBRARY", "DEVOBJ"),
        ("BCPL_RUNTIME_CANDIDATE", "1"),
        ("BCPL_RUNTIME_CANDIDATE_MEMBER", "BCPLM6"),
    ):
        if os.environ.get(key) != required:
            raise ValueError(f"{key} must be {required} for probe")
    if not args.generated.is_file():
        raise ValueError(f"missing Cambridge generated code: {args.generated}")
    if args.generated.resolve() == args.output.resolve():
        raise ValueError("generated source and JCL output must differ")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".base")
    try:
        subprocess.run(
            [
                sys.executable, str(GENERATOR),
                str(args.generated), str(temporary),
                "--test-number", "890",
                "--case-dir", str(FIXTURES),
            ], cwd=ROOT, check=True
        )
        transformed = change_deck(
            temporary.read_text(encoding="ascii")
        )
        args.output.write_text(
            transformed, encoding="ascii", newline="\n"
        )
    finally:
        temporary.unlink(missing_ok=True)
    print("Prepared non-submitting real-OPEN exploratory deck:")
    print(args.output)
    print("DD01=DATA; DD02=SYSOUT; FINDINPUT(DD02) may ABEND.")
    print("No JES submission and no MVS PDS modifications occurred.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        sys.exit(f"prepare-m42-real-open-jcl: {exc}")
