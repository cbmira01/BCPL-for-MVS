#!/usr/bin/env python3
"""Externalize G40 APTOVEC in a disposable combined regression source."""
import argparse
from pathlib import Path
import re

def one(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"expected exactly one {old!r}, found {text.count(old)}")
    return text.replace(old, new, 1)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source",type=Path)
    ap.add_argument("output",type=Path)
    a=ap.parse_args()
    if a.source.resolve()==a.output.resolve():
        raise ValueError("source and output must differ")
    text=a.source.read_text(encoding="ascii")
    text=one(text,"BCPLMAIN CSECT\n",
        "BCPLMAIN CSECT\n         ENTRY STKOVFL\n"
        "         EXTRN APTOVEC,APLIMIT\n")
    text=one(text,"         LA    1,APTOVEC\n"
        "         ST    1,160(12)\n",
        "         L     1,=A(APTOVEC)\n"
        "         ST    1,160(12)\n"
        "         L     1,=A(APLIMIT)\n"
        "         L     2,STKLIM\n"
        "         ST    2,0(1)\n")
    start=text.index("* APTOVEC -- TEMPORARY STACK VECTOR")
    start=text.rfind("***********************************************************************",0,start)
    marker="APMAXN   DC    F'16380'"
    end=text.index(marker,start)+len(marker)
    section=text[start:end]
    for sym in ("APTOVEC","APMAXN"):
        if len(re.findall(rf"(?m)^{sym}\s+",section))!=1:
            raise ValueError(f"missing unique {sym} in original APTOVEC")
    text=text[:start]+"* APTOVEC supplied by independent BCPLAPT object.\n"+text[end:]
    if re.search(r"(?m)^APTOVEC\s+",text):
        raise ValueError("internal APTOVEC definition survived")
    for no,line in enumerate(text.splitlines(),1):
        if len(line)>71:
            raise ValueError(f"line {no} exceeds assembler column 71")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(text,encoding="ascii",newline="\n")
    print(f"External BCPLAPT runtime: {a.output}")
if __name__=="__main__":
    try:main()
    except (OSError,ValueError) as exc:
        raise SystemExit(f"externalize-bcplapt: {exc}")
