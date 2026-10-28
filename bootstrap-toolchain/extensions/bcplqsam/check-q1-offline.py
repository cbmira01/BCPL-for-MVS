#!/usr/bin/env python3
"""Offline BCPLQSAM diagnostics for Q.1 invariants plus Q.2 source.

No assembler, linker, compiler, JES, or MVS runtime is used here. Passing
this program MUST NOT be presented as IFOX/IEWL/GO or Q.1 acceptance.
"""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRANCHES = {'B', 'BE', 'BNE', 'BZ', 'BNZ', 'BM', 'BNM', 'BP', 'BNP',
            'BH', 'BL', 'BNH', 'BNL', 'BAL', 'BCT'}


COUNTER_NAMES = ('QSLIVE', 'QSDCBS', 'QSSTAGES', 'QSQUAR', 'QFCOUNT')


def check_counter_increments(asm: str) -> None:
    """Require five correct R0 counter-increment triplets."""
    lines = [line.strip() for line in asm.splitlines()]
    for name in COUNTER_NAMES:
        expected = [f'L     0,{name}', "A     0,=F'1'", f'ST    0,{name}']
        matches = sum(lines[i:i + 3] == expected
                      for i in range(len(lines) - 2))
        assert matches == 1, f'{name}: expected one L/A/ST increment triplet'
    assert lines.count("A     0,=F'1'") == len(COUNTER_NAMES), (
        'wrong number of R0 counter increments')
    assert not any(re.fullmatch(r'LA\s+0,1\(0\)', line) for line in lines), (
        'LA 0,1(0) cannot increment R0')

def parse() -> tuple[str, dict[str, int], list[tuple[int, str, str]]]:
    lines = (HERE / 'bcplqsam.asm').read_text(encoding='ascii').splitlines()
    symbols: dict[str, int] = {}
    branches = []
    for n, card in enumerate(lines, 1):
        assert card.isascii(), f'nonascii card {n}'
        assert len(card) <= 71, f'IFOX card {n} exceeds column 71 ({len(card)})'
        assert '\t' not in card, f'card {n} has tab'
        if not card.strip() or card[0] == '*':
            continue
        fields = card.split()
        if not card[0].isspace():
            lab = fields[0]
            assert re.fullmatch(r'[A-Z@#$][A-Z0-9@#$]{0,7}', lab), (
                f'bad 8-character assembler label {lab!r}, line {n}')
            assert lab not in symbols, f'duplicate label {lab} at {n}'
            symbols[lab] = n
            fields = fields[1:]
        assert fields, f'missing operation at line {n}'
        op = fields[0]
        if op == 'C':
            assert len(fields) >= 2 and re.match(r'^(?:[0-9]|1[0-5]),', fields[1]), (
                f'malformed C register operand at line {n}: {card}')
        if op in BRANCHES:
            assert len(fields) >= 2, f'missing branch operand at {n}'
            target = fields[1].split(',')[-1]
            if not re.fullmatch(r'[0-9]+', target):
                branches.append((n, op, target))
    for n, op, dest in branches:
        assert dest in symbols, f'unresolved internal {op} target {dest} line {n}'
    return '\n'.join(lines) + '\n', symbols, branches


def check() -> None:
    asm, labels, branches = parse()
    check_counter_increments(asm)
    assert len([line for line in asm.splitlines()
                if re.search(r'\s+CSECT
    for symbol in ('QSMBEG', 'QSMEND', 'QSMDISP', 'QSMCORE',
                   'QSMCLS1', 'QSMIO', 'QSMFIN', 'QSMCTRL', 'QSMDCBS'):
        assert symbol in labels, f'missing {symbol}'
    desc = asm.split('QSMBEG   DS')[1].split('QSMEND   EQU')[0]
    for card in ("DC    CL4'BCEX'", "DC    F'1',F'48',F'56'",
                 "DC    CL8'BCPLQSAM'", "DC    F'200',A(QSMDISP)",
                 "DC    F'1',F'0',F'1',A(QSMFIN),F'0',F'0'"):
        assert card in desc, f'descriptor mismatch: {card}'
    assert "LA    14,25" in asm, 'QUERY 0x19 bitmap absent'
    assert "ST    14,20(8)" in asm, 'QUERY flags-word write absent'
    assert "LA    14,6" in asm, 'QUERY required size absent'
    assert "GETMAIN RC,LV=1024" in asm
    assert "FREEMAIN R,LV=1024,A=(1)" in asm
    assert 'RDJFCB ((2))' in asm
    for token in ("QCDBCOPY", "QCDREST", "QSFIRST  DC    32X'00'",
                  "QSDCOPY  DS    CL3072", "MVC   0(96,5),0(2)",
                  "MVC   0(96,2),0(5)"):
        assert token in asm, f'missing DCB reuse control: {token}'
    assert not re.search(r'^\w+\s+C\s+\d+\(', asm, re.M), (
        'C macro must include a first register operand')
    assert 'OPEN  ((2),(INPUT))' in asm
    assert 'OPEN  ((2),(OUTPUT))' in asm
    assert 'CLOSE ((2))' in asm
    # Accepted BCPLIO uses the DCB+48 fullword as the nonzero QSAM
    # entry address. It is not an arbitrary open-state bit mask.
    assert "L     0,48(2)" in asm
    assert "TM    48(2),X'10'" not in asm
    # IBM S/370 DR is register/register; use D for memory literals.
    assert len(re.findall(r"^\s+D\s+6,=F'44'", asm, re.M)) == 2
    assert not re.search(r"^\s+DR\s+6,=F'44'", asm, re.M)
    assert 'QSCQUAR' in asm and 'QSMFIN' in asm
    assert "C     7,=X'7FFFFFFF'" in asm
    assert 'QCEXHAUS XC    QSNEXT(4),QSNEXT' in asm
    assert 'BE    QCEXHAUS' in asm
    for i in range(16):
        assert f'QS{i:02d}     DC ' in asm
        assert f'QJ{i:02d}     DS    CL176' in asm
        assert f'QI{i:02d}     DCB ' in asm
        assert f'QO{i:02d}     DCB ' in asm
        assert f'QE{i:02d}     DC ' in asm
    assert len(re.findall(r'^Q[IO][0-9]{2}\s+DCB\s+', asm, re.M)) == 32
    # Stage, private handle, and quarantine are independently represented.
    for literal in ("QSNEXT   DC    F'1'", "QSLIVE   DC    F'0'",
                    "QSSTAGES DC    F'0'", "QSQUAR   DC    F'0'",
                    'QSCQUAR', 'QFOTHER', 'QCVFORM', 'QCFIND'):
        assert literal in asm
    # Q.2 move-mode I/O; GET/PUT remain unverified on native MVS.
    assert asm.count('         GET   (2),(1)') == 1
    assert asm.count('         PUT   (2),(1)') == 1
    assert "QISTATES DC    16X'00'" in asm
    assert "QIPENDS  DC    16F'0'" in asm
    for i in range(16):
        assert re.search(
            rf'^QI{i:02d}\s+DCB\s+.*EODAD=E,SYNAD=QS$',
            asm, re.M)
        assert re.search(
            rf'^QO{i:02d}\s+DCB\s+.*SYNAD=QS$',
            asm, re.M)
    header = (HERE / 'bcplqsam.h').read_text(encoding='ascii')
    for word, value in {'QS_QUERY': 0, 'QS_OPEN': 1, 'QS_READ': 2,
                        'QS_WRITE': 3, 'QS_CLOSE': 4, 'QS_INFO': 5,
                        'QS_INPUT': 1, 'QS_OUTPUT': 2, 'QS_ERR_OPCODE': -2,
                        'QS_ERR_RESOURCE': -11, 'QS_ERR_CLOSE': -14,
                        'QS_FMT_F': 1, 'QS_FMT_FB': 2,
                        'QS_FMT_V': 3, 'QS_FMT_VB': 4}.items():
        assert re.search(r'\b' + word + r'\s*=\s*' + str(value) + r'\b',
                         header), f'header mismatch {word}'
    cat = (HERE / 'q1-catalog.asm').read_text(encoding='ascii')
    assert "('&PKG' EQ 'BCPLQSAM')" in cat
    for symbol in ("'QSMOBJ'", "'QSMBEG'", "'QSMEND'"):
        assert symbol in cat
    assert 'BCXREQ BCPLQSAM' in (HERE / 'q1-selection.asm').read_text()
    assert (HERE / 'test-q1-output.bcpl').is_file()
    for candidate in HERE.glob('test-q1-*.bcpl'):
        s = candidate.read_text(encoding='ascii')
        assert 'QSAMSVC:200' in s and 'LET START() BE' in s
        assert 'STOP(8)' in s and candidate.name.endswith('.bcpl')
    for mode in ('finish', 'stop'):
        s = (HERE / f'test-q1-{mode}.bcpl').read_text()
        for i in range(16):
            assert f'Q!0 := "Q{i:02d}"' in s
        for operation in ('QSAMSVC(5,Q,R)', 'QSAMSVC(4,Q,R)'):
            assert operation in s
        assert 'IF QSAMSVC(1,Q,R) NE -11' in s
        assert 'IF QSAMSVC(4,Q,R) NE -7' in s
    print(f'PASS: {len(labels)} labels, {len(branches)} branches, '
          '16 slots, 32 DCBs, Q.1 invariants and Q.2 candidate shape')
    print('NOT TESTED: IFOX syntax/expansion, IEWL relocation, MVS/JES, '
          'real QSAM, or REGION=256K runtime consumption')


if __name__ == '__main__':
    check()
, line)]) == 8
    for symbol in ('QSMBEG', 'QSMEND', 'QSMDISP', 'QSMCORE',
                   'QSMCLS1', 'QSMFIN', 'QSMCTRL', 'QSMDCBS'):
        assert symbol in labels, f'missing {symbol}'
    desc = asm.split('QSMBEG   DS')[1].split('QSMEND   EQU')[0]
    for card in ("DC    CL4'BCEX'", "DC    F'1',F'48',F'56'",
                 "DC    CL8'BCPLQSAM'", "DC    F'200',A(QSMDISP)",
                 "DC    F'1',F'0',F'1',A(QSMFIN),F'0',F'0'"):
        assert card in desc, f'descriptor mismatch: {card}'
    assert "LA    14,25" in asm, 'QUERY 0x19 bitmap absent'
    assert "ST    14,20(8)" in asm, 'QUERY flags-word write absent'
    assert "LA    14,6" in asm, 'QUERY required size absent'
    assert "GETMAIN RC,LV=1024" in asm
    assert "FREEMAIN R,LV=1024,A=(1)" in asm
    assert 'RDJFCB ((2))' in asm
    for token in ("QCDBCOPY", "QCDREST", "QSFIRST  DC    32X'00'",
                  "QSDCOPY  DS    CL3072", "MVC   0(96,5),0(2)",
                  "MVC   0(96,2),0(5)"):
        assert token in asm, f'missing DCB reuse control: {token}'
    assert not re.search(r'^\w+\s+C\s+\d+\(', asm, re.M), (
        'C macro must include a first register operand')
    assert 'OPEN  ((2),(INPUT))' in asm
    assert 'OPEN  ((2),(OUTPUT))' in asm
    assert 'CLOSE ((2))' in asm
    # Accepted BCPLIO uses the DCB+48 fullword as the nonzero QSAM
    # entry address. It is not an arbitrary open-state bit mask.
    assert "L     0,48(2)" in asm
    assert "TM    48(2),X'10'" not in asm
    # IBM S/370 DR is register/register; use D for memory literals.
    assert len(re.findall(r"^\s+D\s+6,=F'44'", asm, re.M)) == 2
    assert not re.search(r"^\s+DR\s+6,=F'44'", asm, re.M)
    assert 'QSCQUAR' in asm and 'QSMFIN' in asm
    assert "C     7,=X'7FFFFFFF'" in asm
    assert 'QCEXHAUS XC    QSNEXT(4),QSNEXT' in asm
    assert 'BE    QCEXHAUS' in asm
    for i in range(16):
        assert f'QS{i:02d}     DC ' in asm
        assert f'QJ{i:02d}     DS    CL176' in asm
        assert f'QI{i:02d}     DCB ' in asm
        assert f'QO{i:02d}     DCB ' in asm
        assert f'QE{i:02d}     DC ' in asm
    assert len(re.findall(r'^Q[IO][0-9]{2}\s+DCB\s+', asm, re.M)) == 32
    # Stage, private handle, and quarantine are independently represented.
    for literal in ("QSNEXT   DC    F'1'", "QSLIVE   DC    F'0'",
                    "QSSTAGES DC    F'0'", "QSQUAR   DC    F'0'",
                    'QSCQUAR', 'QFOTHER', 'QCVFORM', 'QCFIND'):
        assert literal in asm
    # Only QUERY, OPEN, CLOSE and INFO are implemented. No record transfer.
    for line in asm.splitlines():
        if line and line[0] != '*':
            assert not re.search(r'^\s+(GET|PUT)\s+', line), (
                'READ/WRITE must remain unimplemented in Q.1')
    header = (HERE / 'bcplqsam.h').read_text(encoding='ascii')
    for word, value in {'QS_QUERY': 0, 'QS_OPEN': 1, 'QS_READ': 2,
                        'QS_WRITE': 3, 'QS_CLOSE': 4, 'QS_INFO': 5,
                        'QS_INPUT': 1, 'QS_OUTPUT': 2, 'QS_ERR_OPCODE': -2,
                        'QS_ERR_RESOURCE': -11, 'QS_ERR_CLOSE': -14,
                        'QS_FMT_F': 1, 'QS_FMT_FB': 2,
                        'QS_FMT_V': 3, 'QS_FMT_VB': 4}.items():
        assert re.search(r'\b' + word + r'\s*=\s*' + str(value) + r'\b',
                         header), f'header mismatch {word}'
    cat = (HERE / 'q1-catalog.asm').read_text(encoding='ascii')
    assert "('&PKG' EQ 'BCPLQSAM')" in cat
    for symbol in ("'QSMOBJ'", "'QSMBEG'", "'QSMEND'"):
        assert symbol in cat
    assert 'BCXREQ BCPLQSAM' in (HERE / 'q1-selection.asm').read_text()
    assert (HERE / 'test-q1-output.bcpl').is_file()
    for candidate in HERE.glob('test-q1-*.bcpl'):
        s = candidate.read_text(encoding='ascii')
        assert 'QSAMSVC:200' in s and 'LET START() BE' in s
        assert 'STOP(8)' in s and candidate.name.endswith('.bcpl')
    for mode in ('finish', 'stop'):
        s = (HERE / f'test-q1-{mode}.bcpl').read_text()
        for i in range(16):
            assert f'Q!0 := "Q{i:02d}"' in s
        for operation in ('QSAMSVC(5,Q,R)', 'QSAMSVC(4,Q,R)'):
            assert operation in s
        assert 'IF QSAMSVC(1,Q,R) NE -11' in s
        assert 'IF QSAMSVC(4,Q,R) NE -7' in s
    print(f'PASS: {len(labels)} labels, {len(branches)} branches, '
          '16 slots, 32 DCBs, Q.1 source invariants')
    print('NOT TESTED: IFOX syntax/expansion, IEWL relocation, MVS/JES, '
          'real QSAM, or REGION=256K runtime consumption')


if __name__ == '__main__':
    check()
