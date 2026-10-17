#!/usr/bin/env python3
"""Create a TEST-ONLY BCPLIO assembler copy with one allocation failure.

Only the second visit to the selected GETMAIN site is denied.
Neither canonical BCPLIO source nor any MVS PDS member is modified.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys


SITES = {
    "descriptor32": ("         GETMAIN RC,LV=32\n"
                     "         LTR   15,15", "FI32", "DSAVE    DS    16F"),
    "buffer268": ("         GETMAIN RC,LV=268\n"
                  "         LTR   15,15", "FI268", "DSAVE    DS    16F"),
    "handle16": ("         GETMAIN RC,LV=16\n"
                 "         LTR   15,15", "FI16", "HSAVE    DS    16F"),
}


def only(text: str, needle: str) -> None:
    if text.count(needle) != 1:
        raise ValueError(
            f"expected one assembler anchor, found {text.count(needle)}: "
            f"{needle!r}"
        )


def instrument(source: str, mode: str) -> str:
    anchor, prefix, data_anchor = SITES[mode]
    only(source, anchor)
    only(source, data_anchor)
    phase = prefix + "PH"
    arm = prefix + "ARM"
    get = prefix + "GET"
    ret = prefix + "RET"
    # On visit 1, set phase=1 and run the real GETMAIN.
    # On visit 2, set phase=2 and synthesize nonzero R15.
    # On later visits, run the real GETMAIN (no permanent fault).
    size = {"descriptor32": 32, "buffer268": 268, "handle16": 16}[mode]
    replacement = "\n".join([
        f"         CLI   {phase},X'00'",
        f"         BE    {arm}",
        f"         CLI   {phase},X'01'",
        f"         BNE   {get}",
        f"         MVI   {phase},X'02'",
        "         LA    15,8",
        f"         B     {ret}",
        f"{arm:<8} MVI   {phase},X'01'",
        f"{get:<8} GETMAIN RC,LV={size}",
        f"{ret:<8} LTR   15,15",
    ])
    source = source.replace(anchor, replacement, 1)
    source = source.replace(
        data_anchor,
        data_anchor + f"\n{phase:<8} DC    X'00'\n"
                      "         DS    0F",
        1,
    )
    lines = source.splitlines()
    for number, line in enumerate(lines, 1):
        if len(line) > 71 or not line.isascii() or line.startswith("//"):
            raise ValueError(f"invalid IFOX assembler line {number}: {line!r}")
    for label in (phase, arm, get, ret):
        if len(label) > 8:
            raise ValueError(f"assembler label exceeds 8 chars: {label}")
    return source.rstrip("\n") + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--mode", choices=sorted(SITES), required=True)
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve():
        raise ValueError("source and test output may not be identical")
    data = args.source.read_text(encoding="ascii")
    transformed = instrument(data, args.mode)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(transformed, encoding="ascii", newline="\n")
    print(f"M4.1 TEST-ONLY BCPLIO: {args.mode}; "
          f"second site visit fails; {args.output}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as exc:
        sys.exit(f"prepare-bcplio-m41-fault: {exc}")
