#!/usr/bin/env python3
"""Create ICINT V19 from the proven V18 Cambridge-bootstrap candidate.

V19 is intentionally a capacity-only revision.  It preserves V18 execution,
stream, diagnostics, PROGVEC, and instruction semantics while enlarging the
BCPL global vector from 401 entries (G!0..G!400) to 700 entries (G!0..G!699).

The Cambridge compiler master declares TOPGLOB:699 and CGHDR uses globals into
the 690s.  Every V18 structure tied to the old 401-entry global-vector ceiling
is expanded together:

- GLOBCNT 401 -> 700;
- OP1 global-store upper bound G+400 -> G+699;
- GUSED bitmap CL401 -> CL700;
- GUSED startup clear 401 -> 700 bytes;
- decoded-global GUSED bounds 400 -> 699;
- MAPSTORE global scan 400 -> 699.

The generated file is asm/icintv19.asm.  The script refuses to overwrite an
existing V19 candidate.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "asm" / "icintv18.asm"
TARGET = ROOT / "asm" / "icintv19.asm"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one occurrence, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    if TARGET.exists():
        raise SystemExit(f"refusing to overwrite existing {TARGET.relative_to(ROOT)}")

    text = SOURCE.read_text(encoding="ascii")

    text = replace_once(
        text,
        "ICINT V18 - RICHARDS INTCODE ASSEMBLER/INTERPRETER",
        "ICINT V19 - RICHARDS INTCODE ASSEMBLER/INTERPRETER",
        "V18 title",
    )

    marker = "* V18 CAMBRIDGE BOOTSTRAP CAPACITY\n"
    if marker not in text:
        raise SystemExit("V18 scope marker not found")
    text = text.replace(
        marker,
        "* V19 CAMBRIDGE GLOBAL-VECTOR CAPACITY\n"
        "*\n"
        "* BASE:\n"
        "*   ICINT V18. EXECUTION AND HOSTING SEMANTICS ARE UNCHANGED.\n"
        "*\n"
        "* V19 SCOPE:\n"
        "*   - ENLARGE GLOBAL VECTOR FROM 401 TO 700 BCPL WORDS,\n"
        "*     SUPPORTING G!0 THROUGH G!699 AS REQUIRED BY THE CAMBRIDGE\n"
        "*     COMPILER MASTER AND SYSTEM/370 CGHDR.\n"
        "*   - ENLARGE THE MATCHING OP1 GLOBAL STORE GUARD, GUSED BITMAP,\n"
        "*     GLOBAL-USE TRACKING BOUNDS, AND MAPSTORE GLOBAL SCAN.\n"
        "*   - NO INTCODE, STREAM, OR PROGVEC SEMANTICS CHANGE.\n"
        "*\n"
        + marker,
        1,
    )

    text = replace_once(text, "GLOBCNT  EQU   401", "GLOBCNT  EQU   700", "GLOBCNT")

    # Clear 700 bytes in legal <=256-byte XC chunks: 256 + 256 + 188.
    old_clear = "         XC    GUSED(256),GUSED\n         XC    GUSED+256(145),GUSED+256"
    new_clear = (
        "         XC    GUSED(256),GUSED\n"
        "         XC    GUSED+256(256),GUSED+256\n"
        "         XC    GUSED+512(188),GUSED+512"
    )
    text = replace_once(text, old_clear, new_clear, "GUSED clear")

    # Three independent old-global ceilings must move together.
    old_bound = "=F'400'"
    if text.count(old_bound) != 3:
        raise SystemExit(
            f"global ceiling: expected exactly three {old_bound} occurrences, "
            f"found {text.count(old_bound)}"
        )
    text = text.replace(old_bound, "=F'699'")

    text = replace_once(text, "GUSED    DS    CL401", "GUSED    DS    CL700", "GUSED size")

    TARGET.write_text(text, encoding="ascii")

    print(f"generated {TARGET.relative_to(ROOT)}")
    print("  GLOBCNT : 401 -> 700 words (G!0..G!699)")
    print("  GLOBLEN : 1604 -> 2800 bytes")
    print("  OP1 guard: G+400 -> G+699")
    print("  GUSED   : 401 -> 700 bytes")
    print("  tracking/map bounds: 400 -> 699")


if __name__ == "__main__":
    main()
