#!/usr/bin/env python3
"""Prepare an isolated TEST-ONLY BCPLIO source with one denied QSAM OPEN.

The second DQOPEN invocation returns R15=8 before issuing SVC 19.
All other OPEN attempts use the genuine MVS SVC 19 sequence.
This exercises BCPLIO's cleanup/retry branch, NOT an actual
MVS QSAM OPEN error, failure code, IEC message or S013 behavior.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ANCHOR = "         LA    1,228(6)\n         SVC   19"
STATE_ANCHOR = "DQSAVE   DS    16F"

REPLACEMENT = """         CLI   F42PH,X'00'
         BE    F42ARM
         CLI   F42PH,X'01'
         BNE   F42GO
         MVI   F42PH,X'02'
         B     DQBAD
F42ARM   MVI   F42PH,X'01'
F42GO    LA    1,228(6)
         SVC   19"""


def transform(source: str) -> str:
    if source.count(ANCHOR) != 1:
        raise ValueError("expected one real DQOPEN SVC 19 call site")
    if source.count(STATE_ANCHOR) != 1:
        raise ValueError("expected one DQSAVE allocation")
    if "F42PH" in source or "F42ARM" in source:
        raise ValueError("already instrumented or name collision")
    result = source.replace(ANCHOR, REPLACEMENT, 1)
    result = result.replace(
        STATE_ANCHOR, STATE_ANCHOR + "\nF42PH    DC    X'00'\n"
        "         DS    0F", 1
    )
    for number, line in enumerate(result.splitlines(), 1):
        if not line.isascii() or len(line) > 71 or line.startswith("//"):
            raise ValueError(f"invalid IFOX card {number}: {line!r}")
    return result.rstrip("\n") + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    if args.source.resolve() == args.output.resolve():
        raise ValueError("source/output paths must differ")
    original = args.source.read_text(encoding="ascii")
    transformed = transform(original)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(transformed, encoding="ascii", newline="\n")
    print("M4.2 TEST-ONLY BCPLIO: DQOPEN second call denied before SVC19; "
          f"{args.output}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        sys.exit(f"prepare-bcplio-m42-open: {exc}")
