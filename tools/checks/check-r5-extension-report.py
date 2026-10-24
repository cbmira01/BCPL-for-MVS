#!/usr/bin/env python3
"""Verify R.5 IEWL registration and package exclusion from a real JES report."""
import argparse
from pathlib import Path
import re


# The IEWL entry-address field need not occur within the XREF slice.
# An ASA carriage-control character may precede the field in a report.
ENTRY_LINE = re.compile(
    r"(?im)^[ \t\f]*[01+]?[ \t\f]*ENTRY[ \t]+ADDRESS[ \t]+"
    r"([0-9A-F]{1,8})[ \t]*$"
)


def verify(text, number):
    if number < 146 or number > 158:
        raise ValueError("number outside R.5 range")
    chunks = text.split("CROSS REFERENCE TABLE")
    if len(chunks) != 2:
        raise ValueError("expected exactly one IEWL cross-reference table")
    mapping = chunks[1].split("LOCATION  REFERS TO SYMBOL", 1)[0]
    selected = number not in (146, 158)
    expected_bytes = 36 if number == 156 else 44 if selected else 28
    problems = []
    def csect(name):
        match = re.search(
            r"(?m)^  " + re.escape(name) +
            r"\s+[0-9A-F]{1,8}\s+([0-9A-F]{1,8})\s*$",
            mapping)
        return int(match.group(1), 16) if match else None
    for name in ("R0APP", "BCPLMAIN", "RGINIT"):
        if csect(name) is None:
            problems.append("missing control section: " + name)
    if csect("BCPLREG") != expected_bytes:
        problems.append("wrong BCPLREG bytes, wanted " + str(expected_bytes))
    for name in ("DMODESC", "DMODISP"):
        found = csect(name) is not None
        if found != selected:
            problems.append("wrong " + name + " inclusion")
    # R.5 contains no BCPLTIME in any selection, including 146/158.
    # A resident BCXCAT now knows BCPLTIME but must not auto-include it.
    for name in ("TIMDESC", "TIMDISP"):
        if csect(name) is not None:
            problems.append("unexpected BCPLTIME section: " + name)
    entries = ENTRY_LINE.findall(text)
    if len(entries) != 1:
        problems.append("expected exactly one IEWL entry address; found " +
                        str(len(entries)))
    elif int(entries[0], 16) != 0:
        problems.append("IEWL entry address " + entries[0] + " is not zero")
    return problems


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("report", type=Path)
    p.add_argument("--test-number", type=int, required=True)
    a = p.parse_args()
    report = a.report.read_text(encoding="utf-8", errors="replace")
    issues = verify(report, a.test_number)
    if issues:
        raise SystemExit("R.5 MAP FAIL: " + "; ".join(issues))
    print(f"R.5 MAP PASS case {a.test_number}")


if __name__ == "__main__":
    main()
