#!/usr/bin/env python3
"""Check class-separated TK5 JES printer images for a single completed job.

A: device 00E / PRINTER1 / class A / GO SYSPRINT
Z: device 00F / PRINTER2 / class Z / GO BCPALT

Reads bytes starting at explicit pre-submit offsets, requiring correct job
banners and complete, distinct physical printer-file sections. This does NOT
prove the original 132-byte QSAM records: JES printer images apply formatting.
"""
import argparse
from pathlib import Path
import re
import sys

def parse_segment(path, offset, job, name, printer, queue):
    with path.open("rb") as f:
        f.seek(0, 2)
        end = f.tell()
        if offset < 0 or offset >= end:
            raise ValueError(f"{name}: invalid start offset {offset} (size {end})")
        f.seek(offset)
        raw = f.read()
    lines = [line.rstrip(b"\r\n") for line in raw.splitlines()]
    ident = re.compile(
        rb"^\*\*\*\*" + queue.encode() +
        rb"\s+(START|END)\s+JOB\s+" + str(job).encode() +
        rb"\s+" + name.encode() + rb"\b.*\b" + printer.encode() +
        rb"\b.*\bJOB\s+" + str(job).encode() + rb"\b"
    )
    events = [(i, match.group(1)) for i, line in enumerate(lines)
              if (match := ident.match(line))]
    starts = [i for i, event in events if event == b"START"]
    ends = [i for i, event in events if event == b"END"]
    if not starts or not ends or max(ends) <= min(starts):
        raise ValueError(f"{name}: completed {queue}/{printer} job section absent")
    first, last = min(starts), max(ends)
    if any(i > last for i in starts) or any(i < first for i in ends):
        raise ValueError(f"{name}: inconsistent job section boundaries")
    # The TK5 writer repeats banners four times. Reject foreign job sections
    # in the selected interval, to avoid silently misattributing records.
    foreign = re.compile(rb"^\*\*\*\*[A-Z]\s+(?:START|END)\s+JOB\s+")
    for line in lines[first:last+1]:
        if foreign.match(line) and not ident.match(line):
            raise ValueError(f"{name}: foreign JES job banner in section")
    # TK5 printer places an ASCII FF at start of a new printed page.\n    # Strip only this printer-control prefix; preserve BCPL leading blanks.\n    payload = [line.removeprefix(b"\\x0c").rstrip(b" \\t")\n               for line in lines[max(starts)+1:min(ends)]]
    return payload

def matched_positions(payload, expected):
    if not expected:
        raise ValueError("empty expected record sequence")
    return [i for i in range(len(payload)-len(expected)+1)
            if payload[i:i+len(expected)] == expected]

def verify(a_path, z_path, a_offset, z_offset, job, jobname, expected_a, expected_z, diagnose=False):
    if a_path.resolve() == z_path.resolve():
        raise ValueError("A and Z printer files must be different")
    a = parse_segment(a_path,a_offset,job,jobname,"PRINTER1","A")
    z = parse_segment(z_path,z_offset,job,jobname,"PRINTER2","Z")
    ea = [x.encode("ascii") for x in expected_a.read_text(encoding="ascii").splitlines()]
    ez = [x.encode("ascii") for x in expected_z.read_text(encoding="ascii").splitlines()]
    if not matched_positions(a,ea):
        if diagnose:
            print(f"DEBUG class A payload: {len(a)} lines; wanted {ea!r}", file=sys.stderr)
            candidates = [(i,line[:160]) for i,line in enumerate(a)\n                          if line in ea or b"AUTHORIZATION CODE IS" in line]\n            print(f"DEBUG class A candidate lines (last 12): {candidates[-12:]!r}", file=sys.stderr)\n            print(f"DEBUG class A final 12 lines: {a[-12:]!r}", file=sys.stderr)
        raise ValueError("class A missing contiguous GO SYSPRINT records")
    if not matched_positions(z,ez):
        raise ValueError("class Z missing contiguous GO BCPALT records")
    # Check *entire* per-job printer sections for exact records intended for
    # the other stream. Dedicated probe 114 has disjoint distinctive values.
    if any(line in ez for line in a):
        raise ValueError("class A includes a BCPALT record")
    if any(line in ea for line in z):
        raise ValueError("class Z includes a SYSPRINT record")
    print(f"PASS job {job} {jobname}: class A / PRINTER1 matched "
          f"{len(ea)} SYSPRINT records; class Z / PRINTER2 matched "
          f"{len(ez)} BCPALT records; cross-destination contamination absent")
    print("LIMIT: JES printer image does not prove unmodified FB132 bytes")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("job",type=int)
    p.add_argument("--jobname",default="AT114R")
    p.add_argument("--a-file",type=Path,default=Path("mvs-state/prt/prt00e.txt"))
    p.add_argument("--z-file",type=Path,default=Path("mvs-state/prt/prt00f.txt"))
    p.add_argument("--a-offset",required=True,type=int,help="A file size before submission, bytes")
    p.add_argument("--z-offset",required=True,type=int,help="Z file size before submission, bytes")
    p.add_argument("--expected-a",type=Path,default=Path(
        "native-compiler/regression/114-interleaved-stream-records/expected.txt"))
    p.add_argument("--expected-z",type=Path,default=Path(
        "native-compiler/regression/114-interleaved-stream-records/expected-alt.txt"))
    p.add_argument("--diagnose",action="store_true",help="show candidate raw printer lines on failure")
    args=p.parse_args()
    try:
        verify(args.a_file,args.z_file,args.a_offset,args.z_offset,
               args.job,args.jobname,args.expected_a,args.expected_z,args.diagnose)
    except (ValueError,OSError,UnicodeError) as error:
        p.exit(1,f"dd-attribution: FAIL: {error}\n")

if __name__=="__main__":
    main()
