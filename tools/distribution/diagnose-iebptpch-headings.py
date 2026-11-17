#!/usr/bin/env python3
"""TA.0: safely diagnose a retained MVS IEBPTPCH member-heading mismatch.

Reads one already-collected, SHA256-pinned pilot, NEVER submits a job,
modifies a dataset, or prints report lines (which may include credentials).
This diagnostic is NOT an alternate decoder or binary acceptance gate.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
MULTI = HERE / 'decode-iebptpch-multi.py'
MAX_LINES = 1000000
MAX_HEADER_OBSERVATIONS = 40

# Both patterns reject control statements ('MEMBER NAME=...') and SQL/JCL text.
STRICT = re.compile(r'^MEMBER NAME  ([A-Z@$#][A-Z0-9@$#]{0,7})\s*$')
FLEXIBLE = re.compile(r'^\s*MEMBER\s+NAME\s+([A-Z@$#][A-Z0-9@$#]{0,7})\s*$', re.ASCII)
EMBEDDED = re.compile(r'(?<![A-Z])MEMBER\s+NAME\s+([A-Z@$#][A-Z0-9@$#]{0,7})\b', re.ASCII)
CONTROL = re.compile(r'^\s*MEMBER\s+NAME\s*=\s*([A-Z@$#][A-Z0-9@$#]{0,7})\s*$', re.ASCII)
HEX48 = re.compile(r'^(?:[0-9A-F]{8}  ){11}[0-9A-F]{8}\s*$')
HEX32 = re.compile(r'^(?:[0-9A-F]{8}  ){7}[0-9A-F]{8}\*{1,2}\s*$')


def inspect(report: str, requested: list[str]) -> dict:
    """Return only safe labels and counts; never release report text."""
    lines = report.replace('\r', '').replace('\f', '\n').splitlines()
    if len(lines) > MAX_LINES:
        raise ValueError('report exceeds diagnostic line limit')
    strict: list[str] = []
    flexible: list[str] = []
    embedded: list[str] = []
    control: list[str] = []
    unusual = 0
    count_hex48 = 0
    count_hex32 = 0
    for line in lines:
        # Use direct full-line matching to avoid echoing credential-bearing lines.
        stripped = line.rstrip(' ')
        s = STRICT.fullmatch(stripped)
        f = FLEXIBLE.fullmatch(stripped)
        c = CONTROL.fullmatch(stripped)
        if s:
            strict.append(s.group(1))
        if f:
            flexible.append(f.group(1))
        if c:
            control.append(c.group(1))
        if not f and not c and (m := EMBEDDED.search(line)):
            if len(embedded) < MAX_HEADER_OBSERVATIONS:
                embedded.append(m.group(1))
            unusual += 1
        if HEX48.fullmatch(stripped):
            count_hex48 += 1
        if HEX32.fullmatch(stripped):
            count_hex32 += 1

    if len(strict) > MAX_HEADER_OBSERVATIONS or len(flexible) > MAX_HEADER_OBSERVATIONS:
        raise ValueError('too many member headings; unsafe/unsupported report')
    unique = set(flexible)
    missing = [m for m in requested if m not in unique]
    unexpected = [m for m in flexible if m not in set(requested)]
    duplicate = sorted({m for m in unique if flexible.count(m) > 1})
    return {
        'requested_members': requested,
        'printed_headers_exact': strict,
        'printed_headers_whitespace_tolerant': flexible,
        'printed_headers_appear_out_of_order': sorted(flexible) == sorted(requested) and flexible != requested,
        'missing_requested_members': missing,
        'unexpected_printed_members': unexpected,
        'duplicated_printed_members': duplicate,
        'nonstandard_embedded_header_candidates': embedded,
        'nonstandard_header_candidate_count': unusual,
        'member_control_statements': control,
        'first_hex_line_count': count_hex48,
        'second_hex_line_count': count_hex32,
        'header_count_matches_request': len(flexible) == len(requested),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if not MULTI.is_file():
            raise ValueError('existing validated multi-member reader missing')
        spec = importlib.util.spec_from_file_location('ta0_multi_diag_loader', MULTI)
        if spec is None or spec.loader is None:
            raise ValueError('could not load TA.0 evidence validator')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt, report, _pins = module.load_evidence(args.evidence_dir)
        result = inspect(report, receipt['requested_members'])
    except (ValueError, OSError, UnicodeError) as exc:
        # No source content or raw exception text: paths may contain private data.
        print(f'TA.0 heading diagnosis REFUSED: {type(exc).__name__}', file=sys.stderr)
        return 1
    print(f"TA.0 JOB {receipt['job']} {receipt['jobname']} pinned report heading diagnosis")
    for key, value in result.items():
        print(f'  {key}: {value}')
    print('No binary readback acceptance, source ancestry or release proof established.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
