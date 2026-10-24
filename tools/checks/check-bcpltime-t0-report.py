#!/usr/bin/env python3
"""Check BCPLTIME T.0 selected-link facts in an actual IEWL JES report.

This does not replace job-summary's step-RC/ABEND checks or the accepted
combined-JES logical-record checker for the application output marker.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

ENTRY_LINE = re.compile(
    r"(?im)^[ \t\f]*[01+]?[ \t\f]*ENTRY[ \t]+ADDRESS[ \t]+"
    r"([0-9A-F]{1,8})[ \t]*$"
)


def verify(report: str) -> list[str]:
    chunks = report.split("CROSS REFERENCE TABLE")
    if len(chunks) != 2:
        return ["require exactly one IEWL cross-reference table"]
    mapping = chunks[1].split("LOCATION  REFERS TO SYMBOL", 1)[0]
    errors: list[str] = []

    def csect(name: str):
        m = re.search(
            r"(?m)^  " + re.escape(name) +
            r"\s+[0-9A-F]{1,8}\s+([0-9A-F]{1,8})\s*$",
            mapping,
        )
        return int(m.group(1), 16) if m else None

    for name in ("R0APP", "BCPLMAIN", "RGINIT", "TIMDESC", "TIMDISP"):
        if csect(name) is None:
            errors.append(f"missing IEWL section {name}")
    if csect("BCPLREG") != 44:
        errors.append("BCPLREG must be 44 bytes (one selected, required)")
    if csect("TIMDESC") != 56:
        errors.append("TIMDESC BCEX must be 56 bytes")
    if csect("DMODESC") is not None or csect("DMODISP") is not None:
        errors.append("unexpected BCPLDEMO sections in T.0 link")
    entries = ENTRY_LINE.findall(report)
    if len(entries) != 1 or int(entries[0], 16) != 0:
        errors.append("missing unique zero IEWL application entry address")
    return errors


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("report", type=Path)
    args = p.parse_args()
    problems = verify(args.report.read_text(encoding="utf-8", errors="replace"))
    if problems:
        raise SystemExit("BCPLTIME T.0 IEWL MAP FAIL: " + "; ".join(problems))
    print("BCPLTIME T.0 IEWL MAP: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
