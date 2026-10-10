#!/usr/bin/env python3
"""Prepare a two-object runtime integration probe from native regression 38.

Requires the accepted generated workarea/native-regression/114.../native-test.asm.
Makes a separate modified copy and JCL, never modifies the baseline.
"""
import argparse
from pathlib import Path
import re
import subprocess

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=Path(
        "workarea/native-regression/38-putbyte-getbyte-roundtrip/native-test.asm"))
    p.add_argument("--outdir",type=Path,default=Path(
        "workarea/native-regression/38-putbyte-getbyte-roundtrip/byte-object-probe"))
    args=p.parse_args()
    raw=args.source.read_text(encoding="ascii")
    original=raw
    # This build is valid only for one specific assembled BCPLMAIN.
    raw,n=re.subn(r"(?m)^(BCPLMAIN CSECT\s*)$",r"\1\n         EXTRN GETBYTE,PUTBYTE",raw)
    if n!=1: raise ValueError(f"expected one BCPLMAIN CSECT; found {n}")
    for name,disp in (("GETBYTE",340),("PUTBYTE",344)):
        raw,n=re.subn(
            rf"(?m)^         LA    1,{name}\s*$",
            f"         L     1,=A({name})",raw)
        if n!=1: raise ValueError(f"expected one G{disp//4} {name} installation; found {n}")
    # Remove only the two original bodies, preserving the rest verbatim.
    first=raw.index("* GETBYTE(S,I) -> R7")
    # Start at the preceding separator line, avoid duplicate local definitions.
    first=raw.rfind("***********************************************************************",0,first)
    end=raw.index("* GETVEC(N) -> R7",first)
    end=raw.rfind("***********************************************************************",first,end)
    removed=raw[first:end]
    for name in ("GETBYTE","PUTBYTE"):
        if len(re.findall(rf"(?m)^{name}\s+",removed))!=1:
            raise ValueError(f"expected one original {name} label in removed section")
    raw=raw[:first]+"* Byte primitives now resolved from BCPLBYTE object.\n*\n"+raw[end:]
    if raw==original:raise ValueError("no source change")
    args.outdir.mkdir(parents=True,exist_ok=True)
    modified=args.outdir/"native-external-byte.asm"
    modified.write_text(raw,encoding="ascii",newline="\n")
    job=args.outdir/"byte-object-probe.jcl"
    cmd=["python3","native-compiler/regression/make-two-object-job.py",
         str(modified),"asm/bcplbyte.asm",str(job),
         "--entry","BCRG0038","--job-name","BY038R"]
    subprocess.run(cmd,check=True)
    deck=job.read_text(encoding="ascii")
    anchor="//SYSUDUMP DD  SYSOUT=*\n"
    if deck.count(anchor)!=1:raise ValueError("SYSUDUMP anchor is ambiguous")
    deck=deck.replace(anchor,
        "//BCPALT   DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)\n"+anchor)
    job.write_text(deck,encoding="ascii",newline="\n")
    print(f"Prepared: {job}")
    print("Two separately assembled objects; BCPLMAIN G85/G86 external.")
    print("Expected BCPL byte-service result for regression 38: 42")

if __name__=="__main__":
    try:main()
    except (OSError,ValueError,subprocess.CalledProcessError) as err:
        raise SystemExit(f"byte-object-probe: FAIL: {err}")
