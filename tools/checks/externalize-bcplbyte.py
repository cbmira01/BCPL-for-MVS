#!/usr/bin/env python3
"""Externalize BCPLMAIN G85/G86 in an assembled BCPL regression copy."""
import argparse
from pathlib import Path
import re

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source",type=Path)
    ap.add_argument("output",type=Path)
    a=ap.parse_args()
    text=a.source.read_text(encoding="ascii")
    text,n=re.subn(r"(?m)^(BCPLMAIN CSECT\s*)$",r"\1\n         EXTRN GETBYTE,PUTBYTE",text)
    if n!=1:raise ValueError(f"expected one BCPLMAIN CSECT: {n}")
    for name in ("GETBYTE","PUTBYTE"):
        text,n=re.subn(rf"(?m)^         LA    1,{name}\s*$",
                       f"         L     1,=A({name})",text)
        if n!=1:raise ValueError(f"expected one global installation of {name}: {n}")
    first=text.index("* GETBYTE(S,I) -> R7")
    first=text.rfind("***********************************************************************",0,first)
    end=text.index("* GETVEC(N) -> R7",first)
    end=text.rfind("***********************************************************************",first,end)
    removed=text[first:end]
    for name in ("GETBYTE","PUTBYTE"):
        if len(re.findall(rf"(?m)^{name}\s+",removed))!=1:
            raise ValueError(f"missing unique original routine {name}")
    text=text[:first]+"* BCPLBYTE primitives resolved from external object.\n*\n"+text[end:]
    if a.source.resolve()==a.output.resolve():raise ValueError("output must be separate")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(text,encoding="ascii",newline="\n")
    print(f"External BCPLBYTE runtime: {a.output}")
if __name__=="__main__":
    try:main()
    except (OSError,ValueError) as exc:raise SystemExit(f"externalize-bcplbyte: {exc}")
