#!/usr/bin/env python3
"""Validate ordered logical output records in a TK5 combined JES report.

This is a *combined-report* verifier, NOT physical DD attribution. JES spool
dataset boundaries are absent from dump-report-for-job's text rendition.
Fail closed if an expectation is not found after the final linker boundary.
"""
import argparse
from pathlib import Path
import sys

def records(path):
    # A blank line is an expected logical empty record, not a wildcard.
    return Path(path).read_text(encoding="utf-8").splitlines()

def candidate_lines(path):
    report = Path(path).read_text(encoding="latin-1").splitlines()
    boundaries = [i for i, line in enumerate(report)
                  if "AUTHORIZATION CODE IS" in line]
    if not boundaries:
        raise ValueError("link-edit authorization boundary missing")
    # Preserve leading whitespace and all non-padding content. The printer
    # may omit the rightmost blanks from physical FB132 records.
    return [line.rstrip(" \r\t") for line in report[boundaries[-1]+1:]]

def validate(expected_path, report_path, destination):
    expected = records(expected_path)
    if not expected:
        raise ValueError("empty expectation cannot prove an output destination")
    if any(len(line) > 132 for line in expected):
        raise ValueError("expected logical record longer than FB132")
    observed = candidate_lines(report_path)
    matches = [i for i in range(len(observed)-len(expected)+1)
               if observed[i:i+len(expected)] == expected]
    if not matches:
        raise ValueError(
            f"{destination}: ordered logical records not found in GO suffix; "
            "leading blanks and interior blanks are significant"
        )
    return len(matches)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("expected")
    ap.add_argument("report")
    ap.add_argument("--destination",choices=("SYSPRINT","BCPALT"),required=True)
    args=ap.parse_args()
    try:
        occurrences=validate(args.expected,args.report,args.destination)
    except (OSError,UnicodeError,ValueError) as exc:
        print(f"record-check: {exc}",file=sys.stderr)
        return 1
    print(f"record-check: {args.destination} logical sequence matched "
          f"({occurrences} occurrence(s)); JES DD attribution NOT VERIFIED")
    return 0
if __name__=="__main__":
    sys.exit(main())
