#!/usr/bin/env python3
"""Prepare a generated BCPL module to export an external native routine.

Regression scaffolding only.  The generated application's trailer is extended
with one G slot whose address is an external assembler symbol.  The linkage
editor resolves that symbol from a separately assembled object module.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re


CSECT = re.compile(r"\s*CSECT\s*")
EXTRN_MAIN = re.compile(r"\s*EXTRN\s+BCPLMAIN\s*")
END_STMT = re.compile(r"\s*END(?:\s+.*)?")
L998 = re.compile(r"\s*L998\s+EQU\s+\*\s*")
DCF = re.compile(r"\s*DC\s+F'(-?\d+)'\s*")
DCA = re.compile(r"\s*DC\s+A\((.+)\)\s*")


def one_index(lines: list[str], pattern: re.Pattern[str], what: str) -> int:
    indexes = [i for i, line in enumerate(lines) if pattern.fullmatch(line)]
    if len(indexes) != 1:
        raise ValueError(f"expected one {what}, found {len(indexes)}")
    return indexes[0]


def find_trailer(lines: list[str]) -> tuple[int, int, list[tuple[int, str]]]:
    end = one_index(lines, L998, "L998")

    candidates: list[int] = []
    for i in range(end - 1):
        first = DCF.fullmatch(lines[i])
        second = DCF.fullmatch(lines[i + 1])
        if first and second and int(second.group(1)) == 0:
            rest = lines[i + 2 : end]
            if len(rest) % 2:
                continue
            if all(
                DCF.fullmatch(rest[j]) and DCA.fullmatch(rest[j + 1])
                for j in range(0, len(rest), 2)
            ):
                candidates.append(i)

    if len(candidates) != 1:
        raise ValueError(
            f"expected one generated trailer before L998, found {len(candidates)}"
        )

    start = candidates[0]
    maximum = int(DCF.fullmatch(lines[start]).group(1))
    pairs: list[tuple[int, str]] = []
    for i in range(start + 2, end, 2):
        pairs.append(
            (
                int(DCF.fullmatch(lines[i]).group(1)),
                DCA.fullmatch(lines[i + 1]).group(1),
            )
        )
    return start, maximum, pairs


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("generated")
    p.add_argument("runtime")
    p.add_argument("output")
    p.add_argument("entry")
    p.add_argument("symbol")
    p.add_argument("global_number", type=int)
    args = p.parse_args()

    generated_path = Path(args.generated)
    runtime_path = Path(args.runtime)
    output_path = Path(args.output)

    text = generated_path.read_bytes().decode("latin-1")
    text = "".join(ch if ord(ch) < 128 else "?" for ch in text)
    lines = text.splitlines()

    csect = one_index(lines, CSECT, "generated CSECT")
    extrn = one_index(lines, EXTRN_MAIN, "EXTRN BCPLMAIN")
    end_stmt = one_index(lines, END_STMT, "generated END statement")

    lines[csect] = f"{args.entry} CSECT"
    lines.insert(csect + 1, f"         EXTRN {args.symbol}")

    # Account for insertion before the original EXTRN/END indexes.
    extrn += 1
    end_stmt += 1
    for index in sorted((extrn, end_stmt), reverse=True):
        del lines[index]

    trailer_start, maximum, pairs = find_trailer(lines)
    offset = args.global_number * 4

    if any(existing == offset for existing, _ in pairs):
        raise ValueError(
            f"generated module already exports G!{args.global_number}"
        )

    l998 = one_index(lines, L998, "L998")
    new_maximum = max(maximum, offset)

    replacement = [
        f"         DC F'{new_maximum}'",
        "         DC F'0'",
    ]
    for existing, address in pairs:
        replacement.append(f"         DC F'{existing}'")
        replacement.append(f"         DC A({address})")
    replacement.append(f"         DC F'{offset}'")
    replacement.append(f"         DC A({args.symbol})")

    lines[trailer_start:l998] = replacement

    generated = "\n".join(lines).rstrip() + "\n"
    runtime = runtime_path.read_text(encoding="ascii")
    combined = (
        generated
        + "*\n"
        + "* BCPLMAIN WIP FOLLOWS\n"
        + "*\n"
        + runtime.rstrip("\n")
        + "\n"
    )

    for number, line in enumerate(combined.splitlines(), 1):
        if len(line) > 71:
            raise ValueError(
                f"{output_path}:{number}: source exceeds column 71 "
                f"(length {len(line)})"
            )

    output_path.write_text(combined, encoding="ascii", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
