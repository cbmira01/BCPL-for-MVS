#!/usr/bin/env python3
"""Check Q2FULL native summary and three execution PASS markers.

This is a post-JES evidence check, not a submission. It must not
describe a missing, partial, or failed record as successful.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

STEPS = ("ASMA", "ASMB", "ASMV", "ASMN", "ASMR", "ASMQ", "ASMG",
         "LKED", "LKRD", "LKVR", "WGO", "RGO", "VGO")
MARKERS = (
    "BCPLQSAM Q2 WRITE 23 F80 FB80 PASS",
    "BCPLQSAM Q2 READ COPY EOF RETRY PASS",
    "BCPLQSAM Q2 COPY 23 FB80 EXACT PASS",
)


def check(summary: str, report: str) -> list[str]:
    """Return concrete evidence problems; do not infer missing steps."""
    problems: list[str] = []
    lines = summary.replace("\f", "").splitlines()
    for step in STEPS:
        candidates = [
            line.strip() for line in lines
            if re.match(rf"^{step}\s", line)
        ]
        passed = [line for line in candidates
                  if re.search(r"\bRC=0000\s*$", line)]
        if len(candidates) != 1 or len(passed) != 1:
            problems.append(
                f"{step}: require one summary step with RC=0000; "
                f"found {len(candidates)} steps and {len(passed)} passing")
    # Exact output-record equality prevents assembler literal/listing
    # lines and quoted JCL source text from satisfying a PASS marker.
    records = [line.strip() for line in
               report.replace("\f", "").splitlines()]
    for marker in MARKERS:
        count = records.count(marker)
        if count != 1:
            problems.append(f"{marker}: expected one GO record, found {count}")
    positions = [records.index(m) if m in records else -1
                 for m in MARKERS]
    if all(p >= 0 for p in positions) and positions != sorted(positions):
        problems.append("native writer/reader/verifier records out of order")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    problems = check(
        args.summary.read_text(encoding="latin-1"),
        args.report.read_text(encoding="latin-1"))
    if problems:
        print("Q2FULL NATIVE EVIDENCE: NOT VERIFIED")
        for problem in problems:
            print(" - " + problem)
        return 1
    print("Q2FULL NATIVE EVIDENCE: PASS")
    print("13 RC=0000 steps and three ordered exact GO markers")
    print("Inspect full IFOX severity and JES records before acceptance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
