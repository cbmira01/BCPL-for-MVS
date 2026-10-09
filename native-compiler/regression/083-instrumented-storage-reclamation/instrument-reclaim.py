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
RETURN_NEW = """RELDONE  MVC   OUTBUF(7),=C'V=0 M=0'
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
TRM083   DC    F'0'"""


def instrument(text: str) -> str:
    for old, new in [(VEC, VEC_NEW), (MAIN, MAIN_NEW),
                     (RETURN, RETURN_NEW), (DATA, DATA_NEW)]:
        if text.count(old) != 1:
            raise ValueError(f"instrumentation anchor not unique: {old!r}")
        text = text.replace(old, new, 1)
    for n, line in enumerate(text.splitlines(), 1):
        if len(line) > 71 or "\t" in line or line.rstrip() != line:
            raise ValueError(f"line {n}: assembler source hygiene failure")
    if text.count("TRV083   DC") != 1 or text.count("TRM083   DC") != 1:
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
