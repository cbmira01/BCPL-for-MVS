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
    # The printer report concatenates JES messages, assembler source
    # listings, link maps, and GO SYSPRINT. A substring search through
    # EOF falsely detects *unexecuted* WTO operands in IFOX listings.
    end = re.search(r'^IEF142I '+job+r' GO - STEP WAS EXECUTED - '
                    r'COND CODE (\d{4})\s*$', report[boundary.end():], re.M)
    if end is None:
        raise ValueError('live GO-section completion missing from JES')
    expected_go = '0000' if profile == 'finish' else '0008'
    if end.group(1) != expected_go:
        raise ValueError(f'actual GO condition code {end.group(1)}')
    end_pos = boundary.end() + end.start()
    actual_go = report[boundary.end():end_pos]

    def emitted(line, text):
        # Only an entire output line, optionally prefixed by a WTO plus sign,
        # counts. Listing cards with WTO operands or quoted literals
        # cannot impersonate an executed output message.
        return bool(re.search(r'^\s*\+?'+re.escape(text)+r'\s*$',
                              line, re.M))

    for marker in ('Q0 NATIVE 16 OPEN READ PASS',
                   f'Q0 FINALIZER {profile.upper()} 16 CLOSE FREE PASS'):
        if not emitted(actual_go, marker):
            raise ValueError(f'missing live GO WTO marker: {marker}')

    # BCPL WRITES uses GO SYSPRINT, not WTO/JES console output. Its
    # complete output line can legitimately follow the IFOX/IEWL
    # listings, but an assembler 'DC C<...>' line is not evidence.
    bcpl_marker = f'Q0 NATIVE BCPL {profile.upper()} PASS'
    if not emitted(report[boundary.end()+end.end():], bcpl_marker):
        raise ValueError(f'missing live GO SYSPRINT marker: {bcpl_marker}')

    for bad in ('Q0 FINALIZER BAD STATE',
                'Q0 NATIVE STAGE ALLOCATION FAILED',
                'Q0 NATIVE RECORD VERIFICATION FAILED',
                'BCPLREG 2001 FINALIZER RETURNED NONZERO',
                'ABEND S0', 'ABEND S1'):
        if emitted(actual_go, bad):
            raise ValueError(f'failure in live GO report: {bad}')
    # WTO messages appear in the JES job log as '+...' as well as
    # IEF236I..IEF142I JESYSMSG; inspect those genuine log events.
    for bad in ('Q0 FINALIZER BAD STATE',
                'Q0 NATIVE STAGE ALLOCATION FAILED',
                'Q0 NATIVE RECORD VERIFICATION FAILED',
                'BCPLREG 2001 FINALIZER RETURNED NONZERO'):
        if re.search(r'^\d{2}\.\d{2}\.\d{2}\s+JOB\s+\d+\s+\+'
                     + re.escape(bad) + r'\s*$', report, re.M):
            raise ValueError(f'failure in JES job log: {bad}')
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
