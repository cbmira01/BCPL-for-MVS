#!/usr/bin/env python3
"""Combine independently generated BCPL S/370 units for a regression test.

This is deliberately test scaffolding, not a reconstructed BCPL loader.

The current WIP BCPLMAIN scans only the trailer of the generated module that
enters it.  To test separate BCPL compilation before LOAD/UNLOAD is rebuilt,
this tool:

* keeps the application generated module as the executable module;
* renames all local Lnnn labels in the library unit to Qnnn;
* extracts the library generated code body;
* merges the library exported-global trailer pairs into the application
  trailer; and
* appends the WIP BCPLMAIN source as the regression runner already does.

No BCPL source is combined or recompiled.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re


LOCAL_LABEL = re.compile(r"\bL(\d+)\b")
CSECT = re.compile(r"\s*CSECT\s*")
EXTRN_MAIN = re.compile(r"\s*EXTRN\s+BCPLMAIN\s*")
END_STMT = re.compile(r"\s*END(?:\s+.*)?")
EQU = lambda name: re.compile(rf"\s*{re.escape(name)}\s+EQU\s+\*\s*")
DCF = re.compile(r"\s*DC\s+F'(-?\d+)'\s*")
DCA = re.compile(r"\s*DC\s+A\((.+)\)\s*")


def read_generated(path: Path) -> list[str]:
    text = path.read_bytes().decode("latin-1")
    # Printer recovery can leave non-ASCII comment bytes.  Generated target
    # constants are represented textually, so replacement is transport-only.
    text = "".join(ch if ord(ch) < 128 else "?" for ch in text)
    return text.splitlines()


def one_index(lines: list[str], pattern: re.Pattern[str], what: str) -> int:
    indexes = [i for i, line in enumerate(lines) if pattern.fullmatch(line)]
    if len(indexes) != 1:
        raise ValueError(f"expected one {what}, found {len(indexes)}")
    return indexes[0]


def trailer(lines: list[str], end_label: str) -> tuple[int, int, list[tuple[int, str]]]:
    end = one_index(lines, EQU(end_label), end_label)

    candidates: list[int] = []
    for i in range(end - 1):
        first = DCF.fullmatch(lines[i])
        second = DCF.fullmatch(lines[i + 1])
        if first and second and int(second.group(1)) == 0:
            # A valid trailer continues from the sentinel as F/A pairs all
            # the way to the end label.
            rest = lines[i + 2 : end]
            if len(rest) % 2:
                continue
            ok = True
            for j in range(0, len(rest), 2):
                if not DCF.fullmatch(rest[j]) or not DCA.fullmatch(rest[j + 1]):
                    ok = False
                    break
            if ok:
                candidates.append(i)

    if len(candidates) != 1:
        raise ValueError(
            f"expected one generated trailer before {end_label}, "
            f"found {len(candidates)}"
        )

    start = candidates[0]
    maximum = int(DCF.fullmatch(lines[start]).group(1))
    pairs: list[tuple[int, str]] = []
    for i in range(start + 2, end, 2):
        offset = int(DCF.fullmatch(lines[i]).group(1))
        address = DCA.fullmatch(lines[i + 1]).group(1)
        pairs.append((offset, address))
    return start, maximum, pairs


def prepare_main(lines: list[str], entry: str) -> list[str]:
    csect = one_index(lines, CSECT, "generated CSECT")
    extrn = one_index(lines, EXTRN_MAIN, "EXTRN BCPLMAIN")
    end = one_index(lines, END_STMT, "generated END statement")

    lines = list(lines)
    lines[csect] = f"{entry} CSECT"

    for index in sorted((extrn, end), reverse=True):
        del lines[index]
    return lines


def prepare_library(lines: list[str]) -> tuple[list[str], int, list[tuple[int, str]]]:
    renamed = [LOCAL_LABEL.sub(lambda m: "Q" + m.group(1), line) for line in lines]

    # Verify expected generated-module framing even though the framing itself
    # is deliberately not copied into the application module.
    one_index(renamed, CSECT, "library generated CSECT")
    one_index(renamed, EXTRN_MAIN, "library EXTRN BCPLMAIN")
    one_index(renamed, END_STMT, "library generated END statement")

    start_label = one_index(renamed, EQU("Q999"), "library Q999")
    trailer_start, maximum, pairs = trailer(renamed, "Q998")

    if start_label >= trailer_start:
        raise ValueError("library Q999 does not precede its generated trailer")

    # A generated BCPL module begins after Q999 with the five-statement
    # entry wrapper:
    #
    #   STM 14,12,12(13)
    #   L   4,12(15)
    #   BCR 15,4
    #   DC  AL2(Q998-Q999)
    #   DC  A(BCPLMAIN)
    #
    # That wrapper is meaningful only when this unit is entered as an
    # independent BCPL module.  The static regression combiner incorporates
    # the library into the application's generated section instead, so do not
    # copy the wrapper or its Q998/Q999 references.  Preserve everything after
    # it: generated constants/data, procedures, and local labels.
    body_start = start_label + 6
    if body_start > trailer_start:
        raise ValueError("library generated entry wrapper is incomplete")

    body = renamed[body_start:trailer_start]
    # CG370 occasionally references the section's own entry origin
    # from code retained in the static body. Keep its symbol available
    # at the original origin (16 bytes before the first retained byte),
    # despite dropping the 16-byte standalone entry wrapper.
    if any(re.search(r"\bQ999\b", line) for line in body):
        body.insert(0, "Q999 EQU *-16")
    # The historical CG370 decimal printer cannot represent the
    # minimum signed 32-bit value: its output is the exact malformed
    # F-constant below. Repair only that one verified transport form,
    # restoring the original 0x80000000 bit pattern without changing
    # any historical BCPL source.
    malformed = "DC F'-./,),(-*,('"
    matches = [i for i, line in enumerate(body) if line.strip() == malformed]
    if len(matches) > 1:
        raise ValueError("more than one malformed signed-minimum constant")
    if matches:
        body[matches[0]] = "         DC X'80000000'"
    if not body:
        raise ValueError("library generated code body is empty")
    if not pairs:
        raise ValueError("library exports no globals")

    return body, maximum, pairs


def merge_units(main: list[str], library: list[str]) -> list[str]:
    main_trailer, main_maximum, main_pairs = trailer(main, "L998")
    lib_body, lib_maximum, lib_pairs = prepare_library(library)

    main_offsets = {offset for offset, _ in main_pairs}
    duplicate = sorted(main_offsets.intersection(offset for offset, _ in lib_pairs))
    if duplicate:
        slots = ", ".join(str(offset // 4) for offset in duplicate)
        raise ValueError(f"duplicate exported global slot(s): {slots}")

    maximum = max(main_maximum, lib_maximum)

    merged: list[str] = []
    merged.extend(main[:main_trailer])
    merged.extend(
        [
            "*",
            "* SEPARATELY COMPILED BCPL LIBRARY BODY FOLLOWS",
            "* LOCAL LNNN LABELS WERE RENAMED TO QNNN BY TEST SCAFFOLDING",
            "*",
        ]
    )
    merged.extend(lib_body)
    merged.extend(
        [
            "*",
            "* MERGED GENERATED GLOBAL TRAILER",
            "*",
            f"         DC F'{maximum}'",
            "         DC F'0'",
        ]
    )

    for offset, address in lib_pairs + main_pairs:
        merged.append(f"         DC F'{offset}'")
        merged.append(f"         DC A({address})")

    # Drop the original main trailer sentinel/pairs but preserve L998 and
    # everything after it.
    _, _, _ = trailer(main, "L998")
    main_end = one_index(main, EQU("L998"), "main L998")
    merged.extend(main[main_end:])
    return merged


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("application")
    p.add_argument("library")
    p.add_argument("runtime")
    p.add_argument("output")
    p.add_argument("entry")
    args = p.parse_args()

    application_path = Path(args.application)
    library_path = Path(args.library)
    runtime_path = Path(args.runtime)
    output_path = Path(args.output)

    app = prepare_main(read_generated(application_path), args.entry)
    lib = read_generated(library_path)
    generated = "\n".join(merge_units(app, lib)).rstrip() + "\n"
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
