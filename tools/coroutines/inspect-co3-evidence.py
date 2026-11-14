#!/usr/bin/env python3
"""Read an existing CO.3 native MVS/JES receipt; submit no new work."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'workarea/co3-first-lifecycle'
STEPS = ('ASMA', 'ASML', 'ASMM', 'ASMS', 'LKED', 'GO')

class ReceiptError(ValueError):
    pass


def read_receipt(folder: Path) -> list[str]:
    folder = folder.resolve()
    if folder.parent != WORK.resolve() or not folder.is_dir():
        raise ReceiptError('expected one CO.3 evidence directory under workarea')
    try:
        result = json.loads((folder/'result.json').read_text('utf-8'))
        summary = (folder/'job-summary.log').read_text('utf-8')
        report = (folder/'job-report.log').read_text('utf-8')
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReceiptError(f'missing or invalid CO.3 evidence: {exc}') from exc
    if not isinstance(result, dict) or result.get('march') != 'CO.3':
        raise ReceiptError('wrong receipt march')
    job = result.get('native_job')
    if not isinstance(job, str) or re.fullmatch(r'[0-9]{1,5}', job) is None:
        raise ReceiptError('missing or invalid native JES job number')
    if not re.search(rf'^JOB\s+{re.escape(job)}\s+CO3BGO\s*$', summary, re.M):
        raise ReceiptError('summary does not match saved native job identity')
    output = [f'CO.3 {result.get("scenario", "unknown")} JOB {job}',
              f'Source: {result.get("git_head", "unknown")}',
              f'Runner status: {result.get("status", "unknown")}',
              f'Runner reason: {result.get("reason", "none")}']
    step_re = re.compile(r'^\s*(ASMA|ASML|ASMM|ASMS|LKED|GO)\s+.*?RC=\d{4}\s*$')
    status_re = re.compile(r'^\s*(?:JOB RESULT|HIGHEST RC|ABEND|BYPASSED|JCL ERROR)\s*:')
    steps, statuses = [], []
    for line in summary.splitlines():
        if step_re.fullmatch(line):
            steps.append(line.strip())
        elif status_re.match(line):
            statuses.append(line.strip())
    output.append('MVS JES:')
    output.extend('  '+line for line in steps[:6])
    output.extend('  '+line for line in statuses[:5])
    if not steps:
        output.append('  No completed steps reported')
    markers=[]
    for line_number, raw in enumerate(report.replace('\f','').splitlines(), 1):
        line=raw.strip()
        if not line.startswith('CO3BCPL'):
            continue
        match=re.fullmatch(r'CO3BCPL\s+([A-Z0-9]+)',line)
        if not match:
            output.append(f'Malformed CO3BCPL at JES line {line_number}')
            break
        markers.append(match.group(1))
    output.append('BCPL records: '+(' '.join(markers) if markers else '(none)'))
    diagnostics=[]
    for raw in report.splitlines():
        if re.search(r'\b(?:IEF450I|IEF472I|IEA995I|IEF452I|IEA000I|IEA008I)\b',raw):
            diagnostics.append(raw.strip()[:160])
    output.extend('MVS diagnostic: '+line for line in diagnostics[:6])
    if len(diagnostics)>6:
        output.append(f'MVS diagnostics omitted: {len(diagnostics)-6}')
    return output


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence',type=Path,help='existing CO.3 receipt directory')
    args=parser.parse_args()
    try:
        print('\n'.join(read_receipt(args.evidence)))
    except ReceiptError as exc:
        print(f'CO.3 evidence inspection FAIL: {exc}',file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
