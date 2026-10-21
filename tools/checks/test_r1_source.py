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

    def test_local_symbols_not_redeclared_extern(self):
        # IFOX diagnoses IFO196 when a symbol defined in an earlier
        # CSECT is declared EXTRN in the same assembly (JOB 2224).
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
'''
        output=patcher.adapt(baseline)
        self.assertIn('EXTRN RGINIT,RGFINI', output)
        self.assertIn('BNZ   R1BAD', output)
        self.assertIn('LA    15,12', output)
        self.assertIn('LA    1,R1REAS', output)
        self.assertIn('ST    1,STOPRC', output)
        self.assertLess(output.index('L     15,=A(RGFINI)'),
                        output.index('R1FINOK  L     15,=A(IOFIN)'))
        with self.assertRaises(ValueError):
            patcher.adapt(output)


if __name__ == '__main__':
    unittest.main()
