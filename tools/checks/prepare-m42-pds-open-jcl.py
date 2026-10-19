#!/usr/bin/env python3
"""Create (do NOT submit) M4.2.2 QSAM OPEN diagnostic JCL.

Use existing compiled BCPL assembler, DEVOBJ BCPLM6 + BCPLIO.
DD02 is read-only SYS1.MACLIB, a PDS with no member selected.
The GO step may ABEND. Not a regression and not a PDS edit.
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
SYSUDUMP = "//SYSUDUMP DD SYSOUT=*"
DD02 = "//DD02     DD DSN=SYS1.MACLIB,DISP=SHR"
BANNER = "//* M4.2.2 PDS WITHOUT MEMBER: MAY ABEND; NOT REGRESSION"
GO = "//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),"


def transform(base: str) -> str:
    if not base.lstrip().startswith("//RG891R"):
        raise ValueError("expected unique RG891R exploratory job identity")
    if base.count("//DD01     DD DATA,DLM=X0") != 1:
        raise ValueError("missing DD01 DATA fixture in base deck")
    if base.count(SYSUDUMP) != 1 or base.count(GO) != 1:
        raise ValueError("missing unique GO/SYSUDUMP anchors")
    if any(line.lstrip().startswith("//DD02") for line in base.splitlines()):
        raise ValueError("DD02 already allocated: refusing duplicate")
    result = base.replace(SYSUDUMP, DD02 + "\n" + SYSUDUMP, 1)
    result = result.replace(GO, BANNER + "\n" + GO, 1)
    if result.count(DD02) != 1 or result.count(BANNER) != 1:
        raise ValueError("probe JCL insertion count mismatch")
    for line_no, card in enumerate(result.splitlines(), 1):
        if len(card) > 71 or not card.isascii():
            raise ValueError(f"invalid JCL card {line_no}: {card!r}")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("generated", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    for key, value in (
        ("BCPL_RUNTIME_PDS", "1"),
        ("BCPL_RUNTIME_LIBRARY", "DEVOBJ"),
        ("BCPL_RUNTIME_CANDIDATE", "1"),
        ("BCPL_RUNTIME_CANDIDATE_MEMBER", "BCPLM6"),
    ):
        if os.environ.get(key) != value:
            raise ValueError(f"{key} must be {value} for M4.2.2")
    if not args.generated.is_file():
        raise ValueError(f"missing compiled assembler: {args.generated}")
    if args.generated.resolve() == args.output.resolve():
        raise ValueError("input and output may not be the same path")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".base")
    try:
        subprocess.run(
            [
                sys.executable, str(BASE),
                str(args.generated), str(temporary),
                "--test-number", "891", "--case-dir", str(CASE),
            ],
            cwd=ROOT, check=True,
        )
        data = transform(temporary.read_text(encoding="ascii"))
        args.output.write_text(data, encoding="ascii", newline="\n")
    finally:
        temporary.unlink(missing_ok=True)
    print("Prepared M4.2.2 read-only PDS QSAM OPEN exploratory deck:")
    print(args.output)
    print("RG891R: DD01=DATA; DD02=SYS1.MACLIB,DISP=SHR (no member)")
    print("The GO job was NOT submitted; no PDS object was modified.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        sys.exit(f"prepare-m42-pds-open-jcl: {exc}")
