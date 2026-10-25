#!/usr/bin/env python3
"""Validate observed Q.0 JES evidence, not IFOX source literals."""
from __future__ import annotations
from pathlib import Path
import re
import sys


def verify(profile, summary, report):
    if profile not in ('finish', 'stop'):
        raise ValueError('unknown native profile')
    steps = ('ASMWR', 'ASMA', 'ASMT', 'ASMG', 'LKWR',
             'LKED', 'WGO', 'GO')
    for name in steps:
        expected = '0008' if profile == 'stop' and name == 'GO' else '0000'
        if not re.search(r'^'+name+r'\s+.*RC='+expected+r'\s*$',
                         summary, re.M):
            raise ValueError(f'missing {name} RC={expected}')
    job = {'finish': 'Q0NFIN', 'stop': 'Q0NSTP'}[profile]
    boundary = re.search(r'^IEF236I ALLOC\. FOR '+job+r'\s+GO\s*$',
                         report, re.M)
    if boundary is None:
        raise ValueError('live GO-section start missing from JES')
    actual_go = report[boundary.start():]
    for marker in ('Q0 NATIVE 16 OPEN READ PASS',
                   f'Q0 NATIVE BCPL {profile.upper()} PASS',
                   f'Q0 FINALIZER {profile.upper()} 16 CLOSE FREE PASS'):
        if marker not in actual_go:
            raise ValueError(f'missing GO output marker: {marker}')
    for bad in ('Q0 FINALIZER BAD STATE',
                'Q0 NATIVE STAGE ALLOCATION FAILED',
                'Q0 NATIVE RECORD VERIFICATION FAILED',
                'BCPLREG 2001 FINALIZER RETURNED NONZERO',
                'ABEND S0', 'ABEND S1'):
        if bad in actual_go:
            raise ValueError(f'failure in GO report: {bad}')
    if not all(csect in report for csect in
               ('R0APP', 'BCPLMAIN', 'RGINIT',
                'Q0TDESC', 'Q0TDISP', 'Q0TFIN')):
        raise ValueError('IEWL MAP/XREF owner check incomplete')
    if 'BCPLREG' not in report:
        raise ValueError('no selected BCRG table visible')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit('Usage: verify-report.py finish|stop SUMMARY REPORT')
    try:
        verify(sys.argv[1],
               Path(sys.argv[2]).read_text(errors='replace'),
               Path(sys.argv[3]).read_text(errors='replace'))
    except (OSError, ValueError) as exc:
        raise SystemExit(f'Q.0 JES verification FAILED: {exc}')
    print(f'Q.0 {sys.argv[1]} observed JES evidence PASS')
