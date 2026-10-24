#!/usr/bin/env python3
"""T.1 IEWL MAP/XREF verifier for native BCPLTIME interoperability."""
from __future__ import annotations

import argparse
from pathlib import Path
import re

ENTRY = re.compile(
    r"(?im)^[ \t\f]*[01+]?[ \t\f]*ENTRY[ \t]+ADDRESS[ \t]+"
    r"([0-9A-F]{1,8})[ \t]*$"
)


def verify(report: str, number: int) -> list[str]:
    if number not in range(159, 163):
        raise ValueError("T.1 test number must be 159..162")
    chunks = report.split("CROSS REFERENCE TABLE")
    if len(chunks) != 2:
        return ["expected exactly one IEWL cross-reference table"]
    mapping = chunks[1].split("LOCATION  REFERS TO SYMBOL", 1)[0]
    rows = re.findall(r"(?m)^  ([A-Z0-9@$#]{1,8})\s+"
                      r"[0-9A-F]{1,8}\s+([0-9A-F]{1,8})\s*$", mapping)
    entries: dict[str, list[int]] = {}
    for name, size in rows:
        entries.setdefault(name, []).append(int(size, 16))
    problems = []
    def require(name: str, size: int | None = None) -> None:
        values = entries.get(name, [])
        if len(values) != 1:
            problems.append(f"{name} CSECT count {len(values)}; expected 1")
        elif size is not None and values[0] != size:
            problems.append(f"{name} length {values[0]}; expected {size}")
    for name in ("R0APP", "BCPLMAIN", "RGINIT", "TIMDISP"):
        require(name)
    require("TIMDESC", 56)
    require("BCPLREG", 44 if number == 159 else 60)
    for name in ("DMODESC", "DMODISP"):
        if number == 159:
            if entries.get(name):
                problems.append(f"unselected {name} must be absent")
        else:
            require(name, 56 if name == "DMODESC" else None)
    addr = ENTRY.findall(report)
    if len(addr) != 1 or int(addr[0], 16) != 0:
        problems.append("expected one zero IEWL ENTRY ADDRESS")
    return problems


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("report", type=Path)
    p.add_argument("--test-number", required=True, type=int)
    args = p.parse_args()
    errors = verify(args.report.read_text(encoding="utf-8", errors="replace"),
                    args.test_number)
    if errors:
        raise SystemExit("T.1 IEWL MAP FAIL: " + "; ".join(errors))
    print(f"BCPLTIME T.1 IEWL MAP: PASS {args.test_number}")


if __name__ == "__main__":
    main()
