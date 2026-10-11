#!/usr/bin/env python3
"""Test-only BCPLMEM extraction from a disposable regression assembler copy."""
from pathlib import Path
import argparse
import re

def replace_one(text, old, new):
    n=text.count(old)
    if n!=1:
        raise ValueError(f"expected one anchor {old!r}; got {n}")
    return text.replace(old,new,1)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source",type=Path)
    ap.add_argument("output",type=Path)
    args=ap.parse_args()
    if args.source.resolve()==args.output.resolve():
        raise ValueError("source must not be overwritten")
    text=args.source.read_text(encoding="ascii")
    text=replace_one(text,"BCPLMAIN CSECT\n",
        "BCPLMAIN CSECT\n         EXTRN GETVEC,FREEVEC,MEMDRAIN\n")
    for label,offset in (("GETVEC",348),("FREEVEC",352)):
        text=replace_one(text,
            f"         LA    1,{label}\n         ST    1,{offset}(12)\n",
            f"         L     1,=A({label})\n         ST    1,{offset}(12)\n")
    start=text.index("GETVEC   LTR   7,7")
    end=text.index("DEBUGINT LTR   7,7",start)
    # Keep DEBUGINT comment header, discard the allocator implementation.
    header=text.rfind("***********************************************************************",start,end)
    if header<start:
        raise ValueError("missing DEBUGINT section divider")
    block=text[start:header]
    for name in ("GETVEC","FREEVEC"):
        if len(re.findall(rf"(?m)^{name}\s+",block))!=1:
            raise ValueError(f"missing one {name} body")
    text=text[:start]+"* BCPLMEM external allocator routines.\n*\n"+text[header:]
    start=text.index("VECLIST  DC    F'0'")
    end=text.index("FVWSAVE  DC    F'0'",start)+len("FVWSAVE  DC    F'0'")
    text=text[:start]+"* Allocator state moved to BCPLMEM."+text[end:]
    old="""RELLOOP  L     1,VECLIST
         LTR   1,1
         BZ    RELMAIN
         L     10,4(1)
         L     9,8(1)
         ST    9,VECLIST
         FREEMAIN R,LV=(10),A=(1)
         B     RELLOOP
RELMAIN  L     1,DYNBASE"""
    new="""         L     1,=A(MEMDRAIN)
         BALR  14,1
RELMAIN  L     1,DYNBASE"""
    text=replace_one(text,old,new)
    # R11 addresses the system-vector region including RELMEM, whereas
    # the final END literal pool lies outside its displacement range.
    # Emit MEMDRAIN's address literal immediately after RELMEM returns.
    text=replace_one(text,
        "RELDONE  L     14,RELRET\n         BR    14\n",
        "RELDONE  L     14,RELRET\n         BR    14\n"
        "         LTORG\n")
    for name in ("GETVEC","FREEVEC","VECLIST"):
        if re.search(rf"(?m)^{name}\s+",text):
            raise ValueError(f"duplicate private definition {name}")
    for i,line in enumerate(text.splitlines(),1):
        if len(line)>71 or "\t" in line or line.rstrip()!=line:
            raise ValueError(f"assembler card {i} invalid")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(text,encoding="ascii",newline="\n")
    print(f"Externalized BCPLMEM: {args.output}")

if __name__=="__main__":
    try:main()
    except (OSError,ValueError) as e:
        raise SystemExit(f"externalize-bcplmem: {e}")
