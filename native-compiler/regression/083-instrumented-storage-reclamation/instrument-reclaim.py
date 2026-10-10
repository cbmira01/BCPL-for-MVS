#!/usr/bin/env python3
"""Instrument 083's generated BCPLMAIN copy, never canonical runtime."""
from __future__ import annotations
import argparse
from pathlib import Path

VEC = """         FREEMAIN R,LV=(10),A=(1)
         B     RELLOOP"""
VEC_NEW = """         FREEMAIN R,LV=(10),A=(1)
         L     2,TRV083
         LA    2,1(2)
         ST    2,TRV083
         B     RELLOOP"""
MAIN = """         FREEMAIN R,LV=(10),A=(1)
         XC    DYNBASE(4),DYNBASE"""
MAIN_NEW = """         FREEMAIN R,LV=(10),A=(1)
         L     2,TRM083
         LA    2,1(2)
         ST    2,TRM083
         XC    DYNBASE(4),DYNBASE"""
RETURN = """RELDONE  L     14,RELRET
         BR    14"""
RETURN_NEW = """RELDONE  MVC   OUTBUF(7),TRTXT83
         L     2,TRV083
         LA    2,240(2)
         STC   2,OUTBUF+2
         L     2,TRM083
         LA    2,240(2)
         STC   2,OUTBUF+6
         PUT   BCPOUT,OUTBUF
         L     14,RELRET
         BR    14"""
DATA = """RELRET   DC    F'0'"""
DATA_NEW = """RELRET   DC    F'0'
TRV083   DC    F'0'
TRM083   DC    F'0'
TRTXT83  DC    CL7'V=0 M=0'"""


def instrument(text: str) -> str:
    # This probe PUTs its counters after RELMEM. Keep its private DCB
    # open; canonical FINISH/CLOSE is exercised by regressions 084+.
    # Only suppress BCPOUT's CLOSE: the final instrumented PUT runs
    # after RELMEM. Retain BCPIN's conditional CLOSE and all other
    # canonical termination actions introduced by the stream-I/O march.
    close = "FINRETN  CLOSE (BCPOUT)"
    if text.count(close) != 1:
        raise ValueError("expected unique BCPOUT CLOSE anchor")
    text = text.replace(close, "FINRETN  EQU   *", 1)
    for old, new in [(VEC, VEC_NEW), (MAIN, MAIN_NEW),
                     (RETURN, RETURN_NEW), (DATA, DATA_NEW)]:
        if text.count(old) != 1:
            raise ValueError(f"instrumentation anchor not unique: {old!r}")
        text = text.replace(old, new, 1)
    for n, line in enumerate(text.splitlines(), 1):
        if len(line) > 71 or "\t" in line or line.rstrip() != line:
            raise ValueError(f"line {n}: assembler source hygiene failure")
    if any(text.count(label) != 1 for label in
           ("TRV083   DC", "TRM083   DC", "TRTXT83  DC")):
        raise ValueError("instrumentation state invalid")
    return text


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    args = p.parse_args()
    src = args.source.read_text(encoding="ascii")
    args.source.write_text(instrument(src), encoding="ascii",
                           newline="\n")
    print("083 instrumentation: OK (2 FREEMAIN counters; final PUT)")


if __name__ == "__main__":
    main()
