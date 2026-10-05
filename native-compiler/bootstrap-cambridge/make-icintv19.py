#!/usr/bin/env python3
"""Create ICINT V19 from the proven V18 Cambridge-bootstrap candidate.

V19 enlarges the BCPL global vector from 401 entries (G!0..G!400) to
700 entries (G!0..G!699), preserves the V18 40,001-word PROGVEC, supplies
the Cambridge STACKBASE/STACKEND host globals, and reports interpreted
storage capacity immediately after INTCODE assembly and before execution.

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

The enlarged image also places several MAPSTORE texts beyond the direct USING
windows.  Load those full addresses through the reachable literal pool rather
than adding a fourth permanent base.

After ASSEMBLE completes, V19 prints a compact four-space-indented capacity
report: program size and PROGVEC capacity, free stack/work words, STACKBASE and
STACKEND, global-vector capacity, count of globals referenced by the assembled
image, and the highest such global.  GUSED is scanned before execution, so the
last two values describe the assembled image rather than runtime activity.

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
        "* V19 CAMBRIDGE GLOBAL-VECTOR CAPACITY AND STARTUP REPORT\n"
        "*\n"
        "* BASE:\n"
        "*   ICINT V18. INTCODE EXECUTION SEMANTICS ARE UNCHANGED.\n"
        "*\n"
        "* V19 SCOPE:\n"
        "*   - ENLARGE GLOBAL VECTOR FROM 401 TO 700 BCPL WORDS,\n"
        "*     SUPPORTING G!0 THROUGH G!699 AS REQUIRED BY THE CAMBRIDGE\n"
        "*     COMPILER MASTER AND SYSTEM/370 CGHDR.\n"
        "*   - ENLARGE THE MATCHING OP1 GLOBAL STORE GUARD, GUSED BITMAP,\n"
        "*     GLOBAL-USE TRACKING BOUNDS, AND MAPSTORE GLOBAL SCAN.\n"
        "*   - SUPPLY CAMBRIDGE STACKBASE/STACKEND GLOBALS G!54/G!55.\n"
        "*   - REPORT PROGRAM, STACK/WORK, AND GLOBAL CAPACITY AFTER\n"
        "*     ASSEMBLY AND BEFORE EXECUTION.\n"
        "*   - PLACE THE EXECUTABLE-CODE LITERAL POOL AT THE CODE/DATA\n"
        "*     BOUNDARY SO THE EXISTING THREE USING REGIONS STILL REACH IT.\n"
        "*   - LOAD POST-X'2FFF' MAPSTORE MESSAGE ADDRESSES THROUGH\n"
        "*     THAT REACHABLE LITERAL POOL RATHER THAN ADDING A BASE REG.\n"
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

    # The old banner was emitted before ASSEMBLE.  V19 emits it with the
    # capacity block after assembly, so every displayed value describes the
    # complete loaded INTCODE image immediately before interpretation.
    text = replace_once(
        text,
        "         LA    R2,ENTERMSG\n         BAL   R14,WRITES\n",
        "",
        "pre-assembly INTCODE banner",
    )

    # PROGRAM SIZE used to be a stand-alone line before STKBASE existed.
    # Move it into the unified post-assembly report below.
    text = replace_once(
        text,
        "NOSYSIN  LA    R2,SIZEMSG\n"
        "         L     R3,P\n"
        "         S     R3,PROGWORD\n"
        "         BAL   R14,WRITEF\n"
        "         LA    R2,ATOETAB+4\n",
        "NOSYSIN  LA    R2,ATOETAB+4\n",
        "old program-size report",
    )

    # The Cambridge compiler expects LIBHDR globals STACKBASE (G!54) and
    # STACKEND (G!55) to describe the interpreted stack/workspace region.
    # STKBASE is the first free BCPL word after the loaded INTCODE image;
    # PROGWORD+40001 is the first word beyond the V18/V19 PROGVEC.
    #
    # Immediately after establishing those values, scan GUSED and print the
    # complete storage report.  R6=count, R7=index, R8=highest global; WRITEF
    # preserves R6-R9 by the ICINT internal-call convention.
    stack_setup = (
        "         L     R2,P\n"
        "         ST    R2,STKBASE\n"
        "         LA    R2,INITCODE\n"
    )
    stack_setup_with_globals = (
        "         L     R2,P\n"
        "         ST    R2,STKBASE\n"
        "***********************************************************************\n"
        "* CAMBRIDGE HOST STACK-BOUND GLOBALS\n"
        "*   G!54 = STACKBASE, FIRST FREE BCPL WORD AFTER LOADED INTCODE\n"
        "*   G!55 = STACKEND, FIRST WORD BEYOND THE 40,001-WORD PROGVEC\n"
        "***********************************************************************\n"
        "         L     R3,G\n"
        "         SLL   R3,2\n"
        "         L     R2,STKBASE\n"
        "         ST    R2,216(R3)\n"
        "         L     R2,PROGWORD\n"
        "         A     R2,=F'40001'\n"
        "         ST    R2,220(R3)\n"
        "***********************************************************************\n"
        "* POST-ASSEMBLY CAPACITY REPORT\n"
        "***********************************************************************\n"
        "         SR    R6,R6\n"
        "         SR    R7,R7\n"
        "         L     R8,=F'-1'\n"
        "RPTGLOOP C     R7,=F'700'\n"
        "         BNL   RPTGDONE\n"
        "         LA    R9,GUSED\n"
        "         AR    R9,R7\n"
        "         CLI   0(R9),0\n"
        "         BE    RPTGNEXT\n"
        "         LA    R6,1(R6)\n"
        "         LR    R8,R7\n"
        "RPTGNEXT LA    R7,1(R7)\n"
        "         B     RPTGLOOP\n"
        "RPTGDONE L     R2,=A(ENTERMSG)\n"
        "         BAL   R14,WRITES\n"
        "         L     R2,=A(RPTPSIZE)\n"
        "         L     R3,P\n"
        "         S     R3,PROGWORD\n"
        "         BAL   R14,WRITEF\n"
        "         L     R2,=A(RPTPCAP)\n"
        "         L     R3,=F'40001'\n"
        "         BAL   R14,WRITEF\n"
        "         L     R2,=A(RPTFREE)\n"
        "         L     R3,PROGWORD\n"
        "         A     R3,=F'40001'\n"
        "         S     R3,STKBASE\n"
        "         BAL   R14,WRITEF\n"
        "         L     R2,=A(RPTSBAS)\n"
        "         L     R3,STKBASE\n"
        "         BAL   R14,WRITEF\n"
        "         L     R2,=A(RPTSEND)\n"
        "         L     R3,PROGWORD\n"
        "         A     R3,=F'40001'\n"
        "         BAL   R14,WRITEF\n"
        "         L     R2,=A(RPTGCAP)\n"
        "         BAL   R14,WRITES\n"
        "         L     R2,=A(RPTGUSE)\n"
        "         LR    R3,R6\n"
        "         BAL   R14,WRITEF\n"
        "         LTR   R6,R6\n"
        "         BZ    RPTHNONE\n"
        "         L     R2,=A(RPTHIGH)\n"
        "         LR    R3,R8\n"
        "         BAL   R14,WRITEF\n"
        "         B     RPTDONE\n"
        "RPTHNONE L     R2,=A(RPTNONE)\n"
        "         BAL   R14,WRITES\n"
        "RPTDONE  L     R2,=A(RPTBLNK)\n"
        "         BAL   R14,WRITES\n"
        "         LA    R2,INITCODE\n"
    )
    text = replace_once(
        text,
        stack_setup,
        stack_setup_with_globals,
        "Cambridge STACKBASE/STACKEND globals and capacity report",
    )

    # Replace the old banner/program-size strings with the unified report
    # strings.  Keep source records comfortably inside IFOX card columns by
    # splitting the longer counted strings across contiguous DC statements.
    old_messages = (
        "ENTERMSG DC    AL1(24),C'INTCODE SYSTEM ENTERED, '\n"
        "BADCHMSG DC    AL1(21),X'15',C'BAD CH %C AT P = %N',X'15'\n"
        "BADCDMSG DC    AL1(20),X'15',C'BAD CODE AT P = %N',X'15'\n"
        "UNSETMSG DC    AL1(10),C'L%N UNSET',X'15'\n"
        "ALSETMSG DC    AL1(32),C'L%N ALREADY SET TO %N AT P = %N',X'15'\n"
        "INTEMSG  DC    AL1(25),X'15',C'INTCODE ERROR AT C = %N',X'15'\n"
        "SIZEMSG  DC    AL1(20),C'PROGRAM SIZE = %N',X'15',X'15',X'15'\n"
    )
    new_messages = (
        "ENTERMSG DC    AL1(23),C'INTCODE SYSTEM ENTERED',X'15'\n"
        "RPTPSIZE DC    AL1(33),C'    PROGRAM SIZE      = '\n"
        "         DC    C'%N WORDS',X'15'\n"
        "RPTPCAP  DC    AL1(33),C'    PROGVEC CAPACITY  = '\n"
        "         DC    C'%N WORDS',X'15'\n"
        "RPTFREE  DC    AL1(33),C'    FREE STACK/WORK   = '\n"
        "         DC    C'%N WORDS',X'15'\n"
        "RPTSBAS  DC    AL1(27),C'    STACKBASE         = %N',X'15'\n"
        "RPTSEND  DC    AL1(27),C'    STACKEND          = %N',X'15'\n"
        "RPTGCAP  DC    AL1(46),C'    GLOBAL CAPACITY   = 700 WORDS,'\n"
        "         DC    C' G!0..G!699',X'15'\n"
        "RPTGUSE  DC    AL1(27),C'    GLOBALS USED      = %N',X'15'\n"
        "RPTHIGH  DC    AL1(29),C'    HIGHEST GLOBAL    = G!%N',X'15'\n"
        "RPTNONE  DC    AL1(29),C'    HIGHEST GLOBAL    = NONE',X'15'\n"
        "RPTBLNK  DC    AL1(1),X'15'\n"
        "BADCHMSG DC    AL1(21),X'15',C'BAD CH %C AT P = %N',X'15'\n"
        "BADCDMSG DC    AL1(20),X'15',C'BAD CODE AT P = %N',X'15'\n"
        "UNSETMSG DC    AL1(10),C'L%N UNSET',X'15'\n"
        "ALSETMSG DC    AL1(32),C'L%N ALREADY SET TO %N AT P = %N',X'15'\n"
        "INTEMSG  DC    AL1(25),X'15',C'INTCODE ERROR AT C = %N',X'15'\n"
    )
    text = replace_once(text, old_messages, new_messages, "startup report messages")

    # V19 static growth, including the startup report strings, pushes several
    # existing diagnostic/trace/MAPSTORE texts outside direct addressability.
    # Use full addresses from the reachable LTORG pool rather than consuming
    # another permanent base register.
    for old, new, label in (
        ("         LA    R2,EXECMSG", "         L     R2,=A(EXECMSG)", "EXECMSG address load"),
        ("ADEFAULT LA    R2,BADCHMSG", "ADEFAULT L     R2,=A(BADCHMSG)", "BADCHMSG address load"),
        ("         LA    R2,BADCDMSG", "         L     R2,=A(BADCDMSG)", "BADCDMSG address load"),
        ("         LA    R2,UNSETMSG", "         L     R2,=A(UNSETMSG)", "UNSETMSG address load"),
        ("         LA    R2,ALSETMSG", "         L     R2,=A(ALSETMSG)", "ALSETMSG address load"),
        ("         LA    R2,INTEMSG", "         L     R2,=A(INTEMSG)", "INTEMSG address load"),
        ("         LA    R2,MSHEAD", "         L     R2,=A(MSHEAD)", "MSHEAD address load"),
        ("         LA    R2,MSREG1", "         L     R2,=A(MSREG1)", "MSREG1 address load"),
        ("         LA    R2,MSREG2", "         L     R2,=A(MSREG2)", "MSREG2 address load"),
        ("         LA    R2,MSCYCMSG", "         L     R2,=A(MSCYCMSG)", "MSCYCMSG address load"),
        ("         LA    R2,MSFRMH", "         L     R2,=A(MSFRMH)", "MSFRMH address load"),
        ("         LA    R2,MSFRAME1", "         L     R2,=A(MSFRAME1)", "MSFRAME1 address load"),
        ("         LA    R2,MSFRAME2", "         L     R2,=A(MSFRAME2)", "MSFRAME2 address load"),
        ("         LA    R2,TRHEAD", "         L     R2,=A(TRHEAD)", "TRHEAD address load"),
        ("         LA    R2,TRBAD1", "         L     R2,=A(TRBAD1)", "TRBAD1 address load"),
        ("         LA    R2,TRBAD2", "         L     R2,=A(TRBAD2)", "TRBAD2 address load"),
        ("         LA    R2,TRLINE1", "         L     R2,=A(TRLINE1)", "TRLINE1 address load"),
        ("         LA    R2,TRLINE2", "         L     R2,=A(TRLINE2)", "TRLINE2 address load"),
        ("         LA    R2,TRLINE3", "         L     R2,=A(TRLINE3)", "TRLINE3 address load"),
        ("         LA    R2,MSGLOB", "         L     R2,=A(MSGLOB)", "MSGLOB address load"),
        ("MSGDONE LA    R2,MSEND", "MSGDONE L     R2,=A(MSEND)", "MSEND address load"),
        ("MSFBAD  LA    R2,MSBADFR", "MSFBAD  L     R2,=A(MSBADFR)", "MSBADFR address load"),
        ("MSFEND  LA    R2,MSGLOBH", "MSFEND  L     R2,=A(MSGLOBH)", "MSGLOBH address load"),
        ("         LA    R2,MSFRAME3", "         L     R2,=A(MSFRAME3)", "MSFRAME3 address load"),
    ):
        text = replace_once(text, old, new, label)

    # The enlarged static area pushes part of the implicit final literal pool
    # above x'2FFF'.  Keep R12/R11/R10 and emit executable-code literals at the
    # existing code/data boundary.
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
    print("  stack globals: G!54=STACKBASE, G!55=STACKEND")
    print("  post-assembly capacity report: enabled")
    print("  literal pool: LTORG at executable-code/data boundary")
    print("  far diagnostic/trace/MAPSTORE addresses: loaded through =A(...) literals")


if __name__ == "__main__":
    main()
