#!/usr/bin/env python3
"""Make an isolated class-A/class-Z probe from regression 114's generated JCL.

Run regression 114 first if workarea/native-regression/.../native-test-heavy.jcl
does not exist. This helper ONLY writes a new deck; it does not submit it or
modify the original regression case.
"""
from pathlib import Path
import argparse
import re

def prepare(source, output):
    text=source.read_text(encoding="ascii")
    if not text.endswith("\n"):
        raise ValueError("incomplete JCL deck")
    # JOB statement and all original 114 source/program logic remain intact.
    lines=text.splitlines(keepends=True)
    if not lines or not re.match(r"^//RG114R\s+JOB\b",lines[0]):
        raise ValueError("input must be regression 114 RG114R native GO deck")
    lines[0]=re.sub(r"^//RG114R", "//AT114R", lines[0],count=1)
    go=[i for i,line in enumerate(lines)
        if re.match(r"^//GO\s+EXEC\b",line)]
    if len(go)!=1:
        raise ValueError("expected exactly one GO step")
    start=go[0]+1
    end=next((i for i in range(start,len(lines))
              if re.match(r"^//[A-Z0-9$#@]+\s+EXEC\b",lines[i])),len(lines))
    block="".join(lines[start:end])
    # Change only GO output DD assignments, never assembler and linker output.
    for dd,cls in (("SYSPRINT","A"),("BCPALT","Z")):
        pattern=rf"(?m)^(//{dd}\s+DD\s+)SYSOUT=(?:\*|[A-Z0-9])(?=,|\s|$)"
        block,count=re.subn(pattern,lambda m:m.group(1)+"SYSOUT="+cls,block)
        if count!=1:
            raise ValueError(f"expected exactly one GO {dd} SYSOUT assignment, saw {count}")
    lines[start:end]=[block]
    final="".join(lines)
    if "SYSOUT=Z" not in block:
        raise ValueError("class Z output missing")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(final,encoding="ascii",newline="\n")
    print(f"Prepared: {output}")
    print("Job: AT114R; GO SYSPRINT SYSOUT=A; GO BCPALT SYSOUT=Z")
    print("Original runtime, generated code, and regression JCL unchanged.")

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source",type=Path,default=Path(
        "workarea/native-regression/114-interleaved-stream-records/native-test-heavy.jcl"))
    ap.add_argument("--output",type=Path,default=Path(
        "workarea/native-regression/114-interleaved-stream-records/dd-attribution-probe.jcl"))
    args=ap.parse_args()
    try:
        prepare(args.source,args.output)
    except (OSError,ValueError) as exc:
        ap.exit(1,f"attribution-probe: {exc}\n")
if __name__=="__main__":
    main()
