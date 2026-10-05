#!/usr/bin/env python3
"""Create the Cambridge-bootstrap ICINT V18 candidate from V17.

V18 is intentionally a capacity-only revision.  It preserves V17 execution,
stream, diagnostics, and instruction semantics and changes only the BCPL
PROGVEC capacity from 20,001 to 40,001 words, plus the version/scope comments.

The generated file is asm/icintv18.asm.  This script refuses to overwrite an
existing V18 so that an already-reviewed checkpoint cannot be replaced silently.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "asm" / "icintv17.asm"
TARGET = ROOT / "asm" / "icintv18.asm"


def main() -> None:
    if TARGET.exists():
        raise SystemExit(f"refusing to overwrite existing {TARGET.relative_to(ROOT)}")

    text = SOURCE.read_text(encoding="ascii")

    if text.count("ICINT V17 - RICHARDS INTCODE ASSEMBLER/INTERPRETER") != 1:
        raise SystemExit("unexpected V17 title")
    if text.count("PROGCNT  EQU   20001") != 1:
        raise SystemExit("unexpected V17 PROGCNT definition")

    text = text.replace(
        "ICINT V17 - RICHARDS INTCODE ASSEMBLER/INTERPRETER",
        "ICINT V18 - RICHARDS INTCODE ASSEMBLER/INTERPRETER",
        1,
    )

    marker = "* V17 INVALID-ADDRESS TRACE DIAGNOSTICS\n"
    if marker not in text:
        raise SystemExit("V17 scope marker not found")
    text = text.replace(
        marker,
        "* V18 CAMBRIDGE BOOTSTRAP CAPACITY\n"
        "*\n"
        "* BASE:\n"
        "*   ICINT V17. EXECUTION AND HOSTING SEMANTICS ARE UNCHANGED.\n"
        "*\n"
        "* V18 SCOPE:\n"
        "*   - ENLARGE PROGVEC FROM 20,001 TO 40,001 BCPL WORDS.\n"
        "*   - THIS IS A CAPACITY-ONLY CHANGE JUSTIFIED BY THE CAMBRIDGE SYN\n"
        "*     BOOTSTRAP PROBES; NO INTCODE OR STREAM SEMANTICS CHANGE.\n"
        "*\n"
        + marker,
        1,
    )

    text = text.replace("PROGCNT  EQU   20001", "PROGCNT  EQU   40001", 1)
    TARGET.write_text(text, encoding="ascii")

    print(f"generated {TARGET.relative_to(ROOT)}")
    print("  PROGCNT: 20001 -> 40001 words")
    print("  PROGLEN : 80004 -> 160004 bytes")


if __name__ == "__main__":
    main()
