"""Offline invariants for temporary Q.1 OPEN-stage diagnostic generation."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'open_stage', HERE / 'prepare-q1-3dd-open-diag.py')
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class OpenStageTest(unittest.TestCase):
    def test_exact_failure_sites(self):
        original = (HERE / 'bcplqsam.asm').read_text('ascii')
        variant = mod.instrument_asm(original)
        self.assertEqual(variant.count('L     15,=A(IODIAG)'), 5)
        self.assertEqual(variant.count('LA    10,4095(12)'), 5)
        self.assertIn("QCNOPEN  L     7,=F'-6'", variant)
        for label in ('Q1O:RDJFCB ', 'Q1O:PREFORM ',
                      'Q1O:DCBPTR ', 'Q1O:POSTFORM '):
            self.assertEqual(variant.count(label), 1)
        for operation in ('RDJFCB ((2))', 'OPEN  ((2),(INPUT))',
                          'OPEN  ((2),(OUTPUT))', 'GETMAIN RC,LV=1024'):
            self.assertIn(operation, original)
            self.assertIn(operation, variant)
        self.assertEqual(original,
                         (HERE / 'bcplqsam.asm').read_text('ascii'))
        with self.assertRaises(ValueError):
            mod.instrument_asm(variant)

    def test_preflight_geometry_capture_before_qcvform(self):
        source = (HERE / 'bcplqsam.asm').read_text('ascii')
        variant = mod.instrument_asm(source)
        self.assertRegex(
            variant,
            r'LH\s+6,102\(2\)\s*BAL\s+14,QDGTRACE\s*'
            r'BAL\s+14,QCVFORM\s*LTR\s+15,15\s*BNZ\s+QCPREBAD')
        for ins in (
            'QDGTRACE STM   0,15,QDGSAVE',
            'ST    3,QDGVALS', 'ST    5,QDGVALS+4',
            'ST    6,QDGVALS+8', 'LA    5,QDGBUF+12',
            'LA    9,3', 'LA    4,8',
            'IC    0,0(7,1)', 'SLL   2,4',
            'LA    2,45', 'LM    0,15,QDGSAVE'):
            self.assertIn(ins, variant)
        self.assertIn("QDGBUF   DC    C'Q1O:GEOM R3=',8C'0'", variant)
        self.assertIn("DC    C' R5=',8C'0',C' R6=',8C'0',C' '",
                      variant)
        self.assertIn("QDGHEXT  DC    C'0123456789ABCDEF'", variant)
        self.assertEqual(variant.count('BAL   14,QDGTRACE'), 1)
        self.assertEqual(variant.count('BAL   14,QCVFORM'), 2)
        self.assertEqual(variant.count('Q1O:GEOM R3='), 1)

    def test_temporary_jcl_only_changes_as_mq(self):
        spec = importlib.util.spec_from_file_location(
            'three_gate', HERE / 'prepare-q1-3dd.py')
        assert spec is not None and spec.loader is not None
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        helper = gate.query_helper().time_helper().trailer_helper()
        baseline = gate.make_deck(
            helper.sample_generated(),
            ["//Q13DD JOB (BCPL),'OPEN DIAG',CLASS=A"],
            'HERC02.BCPL.BOOT.OBJ')
        variant = mod.instrument_deck(baseline)
        self.assertIn('Q1O:RDJFCB ', variant)
        self.assertEqual(
            variant.count('//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,'), 1)
        source = (HERE / 'bcplqsam.asm').read_text('ascii').rstrip('\n')
        altered = mod.instrument_asm(source + '\n').rstrip('\n')
        self.assertEqual(variant.replace(altered, source, 1), baseline)
        with self.assertRaises(ValueError):
            mod.instrument_deck(variant)
        with self.assertRaises(ValueError):
            mod.instrument_deck(baseline.replace('REGION=256K', 'REGION=512K'))

    def test_refuse_paths_outside_workarea(self):
        with self.assertRaises(ValueError):
            mod.in_workarea(Path('/tmp/not-workarea.jcl'))


if __name__ == '__main__':
    unittest.main()
