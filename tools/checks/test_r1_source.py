#!/usr/bin/env python3
"""R.1 artifact lint and conservative control-flow checks (NOT MVS)."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
ASM = ROOT / 'bootstrap-toolchain/asm'
R1 = ROOT / 'bootstrap-toolchain/probes/r1-registration'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class SourceContract(unittest.TestCase):
    def test_fixed_table_lengths(self):
        empty = (ASM / 'bcplreg-empty.asm').read_text('ascii')
        selected = (R1 / 'selected-registry.asm').read_text('ascii')
        descriptor = (R1 / 'descriptor.asm').read_text('ascii')
        self.assertIn("F'28',F'28',F'0',F'0'", empty)
        self.assertIn("F'28',F'44',F'1',F'1'", selected)
        self.assertIn("F'1',F'48',F'56'", descriptor)
        self.assertIn("F'298',A(R1DISP)", descriptor)
        self.assertIn('R1EXBEG', selected)
        self.assertIn('R1EXEND', selected)

    def test_source_cards_and_unique_labels(self):
        for path in [ASM/'bcplrgs.asm', ASM/'bcplreg-empty.asm',
                     *R1.glob('*.asm')]:
            with self.subTest(path=path.name):
                content = path.read_text('ascii')
                labels = []
                for no, line in enumerate(content.splitlines(), 1):
                    self.assertLessEqual(len(line), 71, f'{path}:{no}')
                    self.assertNotIn('\t', line)
                    if line and not line[0].isspace() and not line.startswith('*'):
                        labels.append(line.split()[0])
                self.assertEqual(len(labels), len(set(labels)))
                self.assertTrue(content.endswith('\n'))

    def test_public_diagnostic_mapping(self):
        reg = (ASM/'bcplrgs.asm').read_text('ascii')
        for n in range(1001, 1015):
            self.assertRegex(reg, rf"ERR{n}\s+WTO\s+'BCPLREG {n} ")
        self.assertIn('BCPLREG 2001', reg)
        # Publication must be after the entire validation+required phase.
        self.assertLess(reg.index('REQLIST'), reg.index('PUBLISH  '))
        self.assertLess(reg.index('PUBLISH  '), reg.index('ST    0,REGCOUNT'))
        self.assertIn('LTR   15,15', reg)

    def test_dependency_duplicate_check_is_bounded(self):
        reg = (ASM/'bcplrgs.asm').read_text('ascii')
        span = reg.split('DEDUPE   ', 1)[1].split('DEFIND   ', 1)[0]
        self.assertNotIn('CLC   0(8,8),0(8,1)', span)
        self.assertIn('L     8,RGDEPTR', span)
        self.assertIn('L     1,RGDEPTR', span)
        self.assertIn('CLC   0(8,8),0(1)', span)

    def test_no_register_zero_as_storage_base(self):
        # JOB 2225: ST 13,4(0) accessed absolute address 4, not R0+4.
        src = (ASM / 'bcplrgs.asm').read_text('ascii')
        for lineno, line in enumerate(src.splitlines(), 1):
            if not line.strip() or line.startswith('*'):
                continue
            with self.subTest(lineno=lineno):
                self.assertNotRegex(line, r'\b\d+\(0\)(?=\s|,|$)')
        self.assertEqual(src.count('LA    2,RSAVE'), 1)
        self.assertEqual(src.count('LA    2,FSAVE'), 1)
        self.assertIn('LR    4,10\n         AR    4,1\n         L     2,0(4)', src)
        self.assertNotIn('LR    0,10\n         AR    0,1\n         L     2,0(2)', src)

    def test_local_symbols_not_redeclared_extern(self):
        src = (ASM / 'bcplrgs.asm').read_text('ascii')
        definitions = set()
        externals = set()
        for line in src.splitlines():
            if not line or line.startswith('*'):
                continue
            fields = line.split()
            if not fields:
                continue
            if not line[0].isspace() and len(fields) >= 2:
                definitions.add(fields[0])
            elif fields[0] == 'EXTRN' and len(fields) >= 2:
                externals.update(fields[1].split(','))
        self.assertEqual(definitions & externals, set())
        self.assertIn('REGCOUNT', definitions)
        self.assertIn('REGFINTB', definitions)
        self.assertNotIn('REGCOUNT', externals)
        self.assertNotIn('REGFINTB', externals)

    def test_core_patch_anchors_and_effects(self):
        patcher = load('r1_patchcheck',ROOT/'tools/checks/r1_prepare_candidate.py')
        baseline = '''         EXTRN BLIB
         LA    11,SYSV
         L     15,DYNWORK
BADRETN  BAL   14,RELMEM
FINIMPL  XC    STOPRC(4),STOPRC
         B     FINEXIT
STOPENT  ST    7,STOPRC
FINEXIT  LR    9,10
         L     15,=A(IOFIN)
STOPRC   DC    F'0'
         BCT   1,GINIT
         ST    9,0(2)
         BC    15,GINST
         ST    9,0(2)
         B     BLIMP
BLIDONE  L     4,4(12)
         ST    1,24(12)
         ST    1,208(12)
         ST    1,212(12)
         ST    1,216(12)
         ST    1,220(12)
         ST    1,44(12)
         ST    1,64(12)
         ST    1,68(12)
         ST    1,156(12)
         ST    1,132(12)
         ST    1,52(12)
         ST    1,60(12)
         ST    1,168(12)
         ST    1,164(12)
         ST    1,48(12)
         ST    1,188(12)
         ST    1,184(12)
         ST    1,56(12)
         ST    1,304(12)
         ST    1,340(12)
         ST    1,344(12)
         ST    1,348(12)
         ST    1,352(12)
         ST    1,600(12)
         ST    1,160(12)
         ST    1,120(12)
'''
        output=patcher.adapt(baseline)
        self.assertIn('EXTRN RGINIT,RGFINI', output)
        self.assertIn('BNZ   R1BAD', output)
        self.assertIn('LA    15,12', output)
        self.assertIn('R1BAD    LR    9,10\n'
                      '         L     15,=A(IOFIN)\n'
                      '         BALR  14,15\n'
                      '         LR    10,9\n'
                      '         BAL   14,RELMEM', output)
        self.assertIn('FINEXIT  LR    9,10', output)
        self.assertIn('LA    1,R1REAS', output)
        self.assertIn('ST    1,STOPRC', output)
        self.assertLess(output.index('L     15,=A(RGFINI)'),
                        output.index('R1FINOK  L     15,=A(IOFIN)'))
        with self.assertRaises(ValueError):
            patcher.adapt(output)


if __name__ == '__main__':
    unittest.main()
