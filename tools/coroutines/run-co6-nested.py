#!/usr/bin/env python3
"""CO.6 nested paired MVS probe; reuse the verified first-pair pipeline.

Only a separate, source-verified fixture, record prefix and evidence root
are substituted. No installed MVS datasets or production objects are written.
"""
from __future__ import annotations

import hashlib
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'tools/coroutines/run-co6-pair.py'
FIXTURE = ROOT / 'packaging/milestones/coroutines/candidates/co6-nested'
WORK = ROOT / 'workarea/co6-nested'
PREFIX = 'CO6NEST'
ORACLE = ('MADE', 'A1', 'B1', 'A2', 'B2', 'R1', 'A3', 'R2', 'B3',
          'R3', 'A4', 'R4', 'DELA', 'DELB', 'C1', 'RC', 'DELC', 'PASS')
NEEDED = ('NESTA(2)', 'NESTB(2)', 'CALLCO(A,11)', 'CALLCO(A,55)',
          'CALLCO(B,110)', 'CALLCO(A,77)', 'CALLCO(C,5)',
          'RESUMECO(', 'COWAIT(33)', 'COWAIT(66)', 'COWAIT(99)',
          'KEEP=123+N', 'KEEP=456+N',
          'DELETECO(A)', 'DELETECO(B)', 'DELETECO(C)')


class NestedError(ValueError):
    pass


def records(report: str) -> list[str]:
    """Reject malformed/ambiguous nested-oracle records."""
    result = []
    for line in report.replace('\f', '').splitlines():
        row = line.strip()
        if not row.startswith(PREFIX):
            continue
        m = re.fullmatch(r'CO6NEST\s+([A-Z0-9]+)', row)
        if not m:
            raise NestedError(f'malformed CO6NEST output: {row!r}')
        result.append(m.group(1))
    return result


def validate_fixture() -> dict[str, str]:
    """No MVS I/O; validate both actual BCPL sources and golden records."""
    expected = (FIXTURE / 'expected.txt').read_text('ascii').splitlines()
    if expected != [PREFIX + ' ' + item for item in ORACLE]:
        raise NestedError('CO.6 nested golden oracle changed')
    digest = {}
    for name, size in (('mr10', '100'), ('native', '1024')):
        raw = (FIXTURE / (name + '.bcpl')).read_bytes()
        source = raw.decode('ascii')
        for number, line in enumerate(source.splitlines(), 1):
            if len(line) > 80 or '\t' in line:
                raise NestedError(f'{name}: BCPL card {number} exceeds 80 columns')
        for marker in ORACLE:
            if source.count('MARK("' + marker + '")') != 1:
                raise NestedError(f'{name}: missing/repeated marker {marker}')
        for snippet in NEEDED:
            if snippet not in source:
                raise NestedError(f'{name}: missing BCPL contract {snippet}')
        for worker in ('AWORK', 'BWORK', 'CWORK'):
            if f'CREATECO({worker},{size})' not in source:
                raise NestedError(f'{name}: incorrect {worker} stack contract')
        if name == 'mr10':
            for binding in ('CURRCO:7', 'COLIST:8', 'RESUMECO:95',
                            'RESUMECO(COLIST!2,0)', 'HEAPINIT(ARENA,501)'):
                if binding not in source:
                    raise NestedError(f'MR10 contract missing {binding}')
        else:
            for binding in ('CO3CURR:295', 'CO3LIST:297',
                            'RESUMECO(CO3LIST!26,0)', 'STACKBASE', 'STACKEND'):
                if binding not in source:
                    raise NestedError(f'native contract missing {binding}')
        digest[name + '_sha256'] = hashlib.sha256(raw).hexdigest()
    return digest


def configure(base) -> None:
    """Isolated process-local selection; the accepted driver stays unedited."""
    first_fixture = base.FIXTURE
    first_oracle = base.ORACLE
    first_check = base.validate_inputs

    def validate() -> dict[str, str]:
        # Revalidate the original accepted engine and its exact CO.3 pins;
        # never skip base preflight or silently weaken its MVS requirements.
        try:
            base.FIXTURE = first_fixture
            base.ORACLE = first_oracle
            prior = first_check()
        finally:
            base.FIXTURE = FIXTURE
            base.ORACLE = ORACLE
        return {**prior, **validate_fixture()}

    base.FIXTURE = FIXTURE
    base.ORACLE = ORACLE
    base.WORK = WORK
    base.records = records
    base.validate_inputs = validate


def main(argv=None) -> int:
    loader = SourceFileLoader('co6_accepted_pair_driver', str(BASE))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None or spec.loader is None:
        raise NestedError('CO.6 accepted paired driver unavailable')
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    configure(base)
    return base.main(argv)


if __name__ == '__main__':
    raise SystemExit(main())
