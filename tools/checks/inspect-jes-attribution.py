#!/usr/bin/env python3
"""Read-only JES spool attribution reconnaissance from the TK5 printer file.

No claim of DD attribution: IEF285I names spool datasets but physical
printer records do not carry the original DD in this combined stream.
"""
import argparse
from pathlib import Path
import re

def extract(raw, job):
    # Match the same Hercules printed-job delimiters as dump-report-for-job.
    start = re.compile(rb"\*\*\*\*A  START.*JOB\s+" + str(job).encode() + rb"\b")
    end = re.compile(rb"\*\*\*\*A   END.*JOB\s+" + str(job).encode() + rb"\b")
    selected = []
    active = False
    for line in raw.splitlines(keepends=True):
        if not active and start.search(line):
            active = True
            continue
        if active and end.search(line):
            return selected
        if active:
            selected.append(line)
    if not active:
        raise ValueError(f"no printer START delimiter found for JOB {job}")
    raise ValueError(f"JOB {job} has no matching END delimiter")

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("job",type=int)
    ap.add_argument("--printer",type=Path,default=Path("mvs-state/prt/prt00e.txt"))
    ap.add_argument("--sample",type=int,default=8)
    args=ap.parse_args()
    selected=extract(args.printer.read_bytes(),args.job)
    lines=[v.rstrip(b"\r\n") for v in selected]
    print(f"JOB {args.job}: {len(lines)} printer lines; {sum(map(len,selected))} raw bytes")
    for row in lines:
        if b"JES2.JOB" in row or (b"IEF237I" in row and
            any(dd in row for dd in (b"SYSPRINT",b"BCPALT",b"SYSUDUMP"))):
            print("SPOOL/MESSAGE:",row.decode("latin-1","replace")[:160])
    markers=[(i,row) for i,row in enumerate(lines)
             if b"AUTHORIZATION CODE IS" in row]
    if markers:
        start=markers[-1][0]+1
        print(f"FINAL LINKER BOUNDARY: printer line {start}")
        for i,row in enumerate(lines[start:start+args.sample],start):
            print(f"POST-LINK {i}: bytes={len(row)} "
                  f"repr={row[:132]!r}")
    else:
        print("FINAL LINKER BOUNDARY: absent")
    print("CONCLUSION: separate JES spool SO identifiers in job log do not "
          "by themselves identify each printed application's DD.")
if __name__=="__main__":
    main()
