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
        self.assertEqual(variant.count('L     15,=A(IODIAG)'), 4)
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
