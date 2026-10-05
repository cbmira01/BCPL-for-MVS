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

The larger static image also pushes the implicit end-of-CSECT literal pool past
the three established 4K USING regions.  Emit the executable-code literal pool
explicitly at the existing code/data boundary with LTORG.  This preserves the
V18 register/base architecture; it is an assembler-layout accommodation only.

The enlarged image also places the final MAPSTORE text MSEND at x'300A', just
beyond the R10 x'2000' USING window.  Load that one full address through the
reachable literal pool (=A(MSEND)) instead of adding a fourth permanent base.

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
        "*   - PLACE THE EXECUTABLE-CODE LITERAL POOL AT THE CODE/DATA\n"
        "*     BOUNDARY SO THE EXISTING THREE USING REGIONS STILL REACH IT.\n"
        "*   - LOAD THE ONE POST-X'2FFF' MAPSTORE MESSAGE ADDRESS THROUGH\n"
        "*     THAT REACHABLE LITERAL POOL RATHER THAN ADDING A BASE REG.\n"
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

    # JOB 896 reduced the V19 assembly to one IFO209: MSEND moved to x'300A',
    # ten bytes past the third USING region.  Load its full address from a
    # literal, which the LTORG below places inside the reachable code area.
    text = replace_once(
        text,
        "MSGDONE LA    R2,MSEND",
        "MSGDONE L     R2,=A(MSEND)",
        "MSEND address load",
    )

    # JOB 895 showed 21 IFO209 addressability errors because the enlarged
    # static area pushed part of the implicit final literal pool above x'2FFF'.
    # Keep the established R12/R11/R10 USING map and emit all literals used by
    # executable code immediately before the existing data/static area.
    code_data_boundary = (
        "SHRINT   L     R0,B\n"
        "         L     R1,A\n"
        "         SRL   R0,0(R1)\n"
        "         BR    R14\n"
        "***********************************************************************\n"
        "* GLOBALS / STREAMS / DCB / TABLES\n"
        "***********************************************************************\n"
    )
    code_data_with_ltorg = (
        "SHRINT   L     R0,B\n"
        "         L     R1,A\n"
        "         SRL   R0,0(R1)\n"
        "         BR    R14\n"
        "         LTORG\n"
        "***********************************************************************\n"
        "* GLOBALS / STREAMS / DCB / TABLES\n"
        "***********************************************************************\n"
    )
    text = replace_once(
        text,
        code_data_boundary,
        code_data_with_ltorg,
        "code/data LTORG boundary",
    )

    TARGET.write_text(text, encoding="ascii")

    print(f"generated {TARGET.relative_to(ROOT)}")
    print("  GLOBCNT : 401 -> 700 words (G!0..G!699)")
    print("  GLOBLEN : 1604 -> 2800 bytes")
    print("  OP1 guard: G+400 -> G+699")
    print("  GUSED   : 401 -> 700 bytes")
    print("  tracking/map bounds: 400 -> 699")
    print("  literal pool: LTORG at executable-code/data boundary")
    print("  MSEND address: loaded through =A(MSEND) literal")


if __name__ == "__main__":
    main()
