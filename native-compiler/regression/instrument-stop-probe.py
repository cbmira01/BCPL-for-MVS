#!/usr/bin/env python3
"""Inject a test-only G!30 STOP adapter into the combined assembler."""
import argparse
from pathlib import Path

def instrument(source: str, code: int) -> str:
    substitutions = [
        ("         ST    1,600(12)\n",
         "         ST    1,600(12)\n"
         "         LA    1,STOPENT\n"
         "         ST    1,120(12)\n"),
        ("         SR    15,15\n         BR    14\n*\n"
         "* Drain live GETVEC",
         (f"         LA    15,{code}\n" if code else
          "         SR    15,15\n")
         + "         BR    14\n*\n"
         "STOPENT  C     7,STOPWNT\n"
         "         BNE   STOPBAD\n"
         "         B     FINIMPL\n"
         "STOPBAD  MVI   OUTBUF,C'X'\n"
         "         B     FINIMPL\n*\n"
         "* Drain live GETVEC"),
        ("RELRET   DC    F'0'\n",
         f"RELRET   DC    F'0'\nSTOPWNT  DC    F'{code}'\n"),
    ]
    for before, after in substitutions:
        if source.count(before) != 1:
            raise ValueError("STOP instrumentation anchor not unique: "
                             + repr(before[:42]))
        source = source.replace(before, after, 1)
    for number, line in enumerate(source.splitlines(), 1):
        if len(line) > 71 or "\t" in line or line.rstrip() != line:
            raise ValueError(f"assembler hygiene error line {number}")
    return source

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--code", type=int, choices=(0,100), required=True)
    args = parser.parse_args()
    text = args.source.read_text(encoding="ascii")
    args.source.write_text(instrument(text,args.code),
                           encoding="ascii",newline="\n")
    print(f"STOP test adapter: OK (argument and MVS RC={args.code})")

if __name__ == "__main__":
    main()
