#!/usr/bin/env python3
"""Prepare a TEST-ONLY BCPLIO copy with private M4.3 counters.

No installation, no JCL submission, and no change to canonical source.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

COUNTERS = (
    "M43G32", "M43F32", "M43G268", "M43F268",
    "M43G16", "M43F16", "M43OATT", "M43OSUC",
    "M43CATT", "M43CRET",
)

def one(source: str, old: str, replacement: str) -> str:
    count = source.count(old)
    if count != 1:
        raise ValueError(f"expected exactly one anchor ({count}): {old!r}")
    return source.replace(old, replacement, 1)

def bump(label: str) -> str:
    assert label in COUNTERS
    # Register zero cannot be an RX-form base on System/370.
    # Use a nearby fullword +1 and ordinary A instruction.
    if label in COUNTERS[:4]:
        plus_one = "M43ONED"
    elif label in COUNTERS[6:]:
        plus_one = "M43ONEQ"
    elif label == "M43G16":
        plus_one = "M43ONEH"
    else:
        plus_one = "M43ONER"
    return "\n".join((
        f"         L     0,{label}",
        f"         A     0,{plus_one}",
        f"         ST    0,{label}",
    ))

def terminal_assertions() -> str:
    """Test-only resource comparison after all IODRAIN releases."""
    lines = [
        "DRAINDN  L     1,=A(DHEAD)",
        "         L     2,0(1)",
        "         LTR   2,2",
        "         BNZ   M43TRAP",
        "         L     1,=A(HHEAD)",
        "         L     2,0(1)",
        "         LTR   2,2",
        "         BNZ   M43TRAP",
        "         L     1,=A(M43TAB)",
    ]
    for first, second in ((0, 4), (8, 12), (16, 20),
                          (24, 28), (24, 32), (32, 36)):
        lines.extend((
            f"         L     2,{first}(1)",
            "         L     2,0(2)",
            f"         L     3,{second}(1)",
            "         L     3,0(3)",
            "         CR    2,3",
            "         BNE   M43TRAP",
        ))
    lines.append("M43DONE  LM    0,10,DRSAVE")
    return "\n".join(lines)



# Exactly one controlled denial on the second visit to a private
# operation. All real GETMAIN/SVC calls remain present and counted.
FAULT_MODES = ("descriptor32", "buffer268", "handle16",
               "open-before-svc19")

def add_failure(source: str, mode: str) -> str:
    if mode not in FAULT_MODES or "F43PH" in source:
        raise ValueError(f"unexpected or repeated fault mode: {mode}")
    if mode == "open-before-svc19":
        anchor = ("         ST    0,M43R0Q\n"
                  + bump("M43OATT"))
        saved = "DQSAVE   DS    16F"
        execute = anchor
        deny = "         B     DQBAD"
    else:
        size, bad, saved = {
            "descriptor32": (32, "DALFAIL", "DSAVE    DS    16F"),
            "buffer268": (268, "DALNOMEM", "DSAVE    DS    16F"),
            "handle16": (16, "HNEWBAD", "HSAVE    DS    16F"),
        }[mode]
        anchor = (f"         GETMAIN RC,LV={size}\n"
                  "         LTR   15,15\n"
                  f"         BNZ   {bad}")
        execute = (f"F43GET   GETMAIN RC,LV={size}\n"
                   "F43RET   LTR   15,15\n"
                   f"         BNZ   {bad}")
        deny = "         LA    15,8\n         B     F43RET"
    if mode == "open-before-svc19":
        execute = "F43GET   " + execute.lstrip()
    replacement = "\n".join((
        "         CLI   F43PH,X'00'",
        "         BE    F43ARM",
        "         CLI   F43PH,X'01'",
        "         BNE   F43GET",
        "         MVI   F43PH,X'02'",
        deny,
        "F43ARM   MVI   F43PH,X'01'",
        execute,
    ))
    source = one(source, anchor, replacement)
    source = one(source, saved,
                 saved + "\nF43PH    DC    X'00'")
    return source

def transform(source: str, terminal_check: bool = False,
              fault_mode: str | None = None) -> str:
    if "         ENTRY IOACCT" in source or any(
        f"{name:<8} DC    F'0'" in source for name in COUNTERS
    ):
        raise ValueError("test instrumentation already present")
    # Fail closed on extra or missing uninstrumented call sites.
    for call, expected in (
        ("GETMAIN RC,LV=32", 1),
        ("GETMAIN RC,LV=268", 1),
        ("GETMAIN RC,LV=16", 1),
        ("FREEMAIN R,LV=32", 2),
        ("FREEMAIN R,LV=268", 1),
        ("FREEMAIN R,LV=16", 1),
        ("         SVC   19", 1),
        ("         SVC   20", 1),
    ):
        if source.count(call) != expected:
            raise ValueError(f"changed call count: {call}")

    # Conditional successful GETMAIN. Preserve existing R15 / branch.
    for size, branch, name in (
        (32, "DALFAIL", "M43G32"),
        (268, "DALNOMEM", "M43G268"),
        (16, "HNEWBAD", "M43G16"),
    ):
        anchor = (f"         GETMAIN RC,LV={size}\n"
                  "         LTR   15,15\n" f"         BNZ   {branch}")
        source = one(source, anchor, anchor + "\n" + bump(name))

    # Count FREEMAIN calls that return. No claim of host free status.
    for size, next_line, name in (
        (32, "DALFAIL", "M43F32"),
        (32, "         XC    DRESULT", "M43F32"),
        (268, "         L     1,DTARGET", "M43F268"),
        (16, "         L     1,=A(HHEAD)", "M43F16"),
    ):
        anchor = f"         FREEMAIN R,LV={size},A=(1)\n{next_line}"
        source = one(source, anchor,
                     f"         FREEMAIN R,LV={size},A=(1)\n"
                     + bump(name) + "\n" + next_line)

    # Count actual SVC19 attempts and source-observed open DCBs.
    source = one(source, "         LA    1,228(6)\n         SVC   19",
                 "         ST    0,M43R0Q\n" + bump("M43OATT")
                 + "\n         L     0,M43R0Q"
                 + "\n         LA    1,228(6)\n         SVC   19")
    source = one(source,
                 "         LTR   7,7\n         BZ    DQBAD\n"
                 "         L     1,DQARG",
                 "         LTR   7,7\n         BZ    DQBAD\n"
                 + bump("M43OSUC") + "\n         L     1,DQARG")

    # SVC20 attempted versus returned control; not QSAM status.
    source = one(source, "         LA    1,232(6)\n         SVC   20",
                 "         ST    0,M43R0Q\n" + bump("M43CATT")
                 + "\n         L     0,M43R0Q"
                 + "\n         LA    1,232(6)\n         SVC   20\n"
                 + bump("M43CRET"))

    # Keep counters near the routines whose USING bases access them.
    for anchor, entries, one_label in (
        ("DSAVE    DS    16F", COUNTERS[:4], "M43ONED"),
        ("DQSAVE   DS    16F", COUNTERS[6:], "M43ONEQ"),
        ("HSAVE    DS    16F", (COUNTERS[4],), "M43ONEH"),
        ("DRSAVE   DS    16F", (COUNTERS[5],), "M43ONER"),
    ):
        new = (anchor + "\n         DS    0F\n"
               + "\n".join(f"{name:<8} DC    F'0'" for name in entries)
               + f"\n{one_label:<8} DC    F'1'")
        if anchor == "DQSAVE   DS    16F":
            new += "\nM43R0Q   DC    F'0'"
        source = one(source, anchor, new)

    # Private R14 linkage: R1 counter ID 0..9; R15 value/-1.
    # Not a public BCPL global. Preserve R0-9 and R11-14.
    accessor = "\n".join((
        "* PRIVATE M4.3 TEST-ONLY QUERY. NEVER INSTALL THIS OBJECT.",
        "         ENTRY IOACCT",
        "IOACCT   BALR  10,0",
        "         USING *,10",
        "         STM   0,9,M43SAVE",
        "         STM   11,14,M43SAVE+44",
        "         LTR   1,1",
        "         BM    M43BAD",
        "         C     1,M43MAX",
        "         BH    M43BAD",
        "         SLL   1,2",
        "         L     2,M43TAB(1)",
        "         L     15,0(2)",
        "         B     M43RET",
        "M43BAD   L     15,M43NEG",
        "M43RET   ST    15,M43RES",
        "         LM    0,9,M43SAVE",
        "         LM    11,14,M43SAVE+44",
        "         L     15,M43RES",
        "         BR    14",
        "         DROP  10",
        "         DS    0F",
        "M43TAB   DC    A(M43G32),A(M43F32)",
        "         DC    A(M43G268),A(M43F268)",
        "         DC    A(M43G16),A(M43F16)",
        "         DC    A(M43OATT),A(M43OSUC)",
        "         DC    A(M43CATT),A(M43CRET)",
        "M43MAX   DC    F'9'",
        "M43NEG   DC    F'-1'",
        "M43RES   DC    F'0'",
        "M43SAVE  DS    16F",
        "         LTORG",
    ))
    source = one(source, "         END   BCPLIO",
                 accessor + "\n         END   BCPLIO")
    if fault_mode:
        source = add_failure(source, fault_mode)

    if terminal_check:
        source = one(source, "DRAINDN  LM    0,10,DRSAVE",
                     terminal_assertions())
        source = one(
            source,
            "         BR    14\n         LTORG\n         DROP  11\n"
            "         DS    0F\nDRDESC",
            "         BR    14\n"
            "* M4.3 TEST ONLY: invalid opcode flags resource mismatch.\n"
            "M43TRAP  DC    X\x270000\x27\n"
            "         LTORG\n         DROP  11\n"
            "         DS    0F\nDRDESC",
        )

    for i, line in enumerate(source.splitlines(), 1):
        if not line.isascii() or len(line) > 71 or \
                line.startswith("//") or line == "/*":
            raise ValueError(f"invalid IFOX card {i}: {line!r}")
    return source.rstrip("\n") + "\n"

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--terminal-check", action="store_true")
    ap.add_argument("--fault-mode", choices=FAULT_MODES)
    args = ap.parse_args()
    if args.source.resolve() == args.output.resolve():
        raise ValueError("must not overwrite source")
    result = transform(args.source.read_text(encoding="ascii"),
                       terminal_check=args.terminal_check,
                       fault_mode=args.fault_mode)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="ascii", newline="\n")
    print("M4.3 test-only source prepared (MVS NOT RUN)")
    if args.terminal_check:
        print("M4.3 post-IODRAIN terminal assertions armed")
    if args.fault_mode:
        print("M4.3 private counted fault mode: " + args.fault_mode)
    print("Counter IDs: " + ", ".join(
        f"{i}={name}" for i, name in enumerate(COUNTERS)))
    print(args.output)

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        sys.exit(f"prepare-bcplio-m43-account: {exc}")
