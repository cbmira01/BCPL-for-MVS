"""Offline Q2MIX mixed BCX catalog, temporary JES, and ABI checks."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    'q2mixprep', HERE / 'prepare-q2-mix.py')
assert SPEC is not None and SPEC.loader is not None
GEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GEN)


class MixCampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stop = GEN.module('prepare-q2-stop-flush.py')
        helper = stop.load_query().time_helper().trailer_helper()
        cls.deck = GEN.make_deck(
            helper.sample_generated(),
            ["//Q2MIX JOB (BCPL),'Q2 MIX CHECK',CLASS=A"],
            'HERC02.BCPL.BOOT.OBJ', 'HERC02.BCPL.EXT.OBJ')

    def test_native_two_package_selection(self):
        rows = self.deck.splitlines()
        self.assertEqual(rows.count('         BCXREQ BCPLQSAM'), 1)
        self.assertEqual(rows.count('         BCXREQ BCPLDEMO'), 1)
        self.assertIn("&BXCLIB  SETC  'QSMOBJ'", rows)
        self.assertIn("&BXCLIB  SETC  'EXTLIB(BCPLDEMO)'", rows)
        self.assertIn(
            '//EXTLIB   DD  DSN=HERC02.BCPL.EXT.OBJ,DISP=SHR', rows)
        self.assertIn(' NAME Q2MIX(R)', rows)
        self.assertNotIn(' NAME Q2STOP(R)', rows)
        self.assertNotIn('         BCXREQ BCPLTIME', rows)
        self.assertEqual(rows.count('//SYSIN    DD  *'), 6)
        self.assertEqual(rows.count('/*'), 8)

    def test_independent_native_readback_and_step_guards(self):
        rows = self.deck.splitlines()
        self.assertIn(' ENTRY Q2MVER', rows)
        self.assertIn(' NAME Q2MVER(R)', rows)
        self.assertIn('Q2MVER   CSECT', rows)
        self.assertIn(
            "PASSREC  DC    CL80'Q2 MIX BCPLQSAM BCPLDEMO FB80 EXACT PASS'",
            rows)
        for step in GEN.STEPS:
            self.assertEqual(
                sum(r.startswith(f'//{step:<8} EXEC ') for r in rows), 1)
        self.assertIn('//             TIME=(,2),COND=(8,NE,BGO)', rows)
        self.assertIn('//QPOST    DD  DSN=&&Q2POST,DISP=(NEW,PASS),', rows)
        self.assertIn('//QPOST    DD  DSN=&&Q2POST,DISP=(OLD,DELETE),', rows)
        self.assertTrue(all(r.isascii() and len(r) <= 71 for r in rows))
        self.assertNotIn('CATLG', self.deck)
        self.assertNotIn('DISP=MOD', self.deck)

    def test_interleaved_bcpl_calls(self):
        source = (HERE / 'test-q2-mix.bcpl').read_text('ascii')
        self.assertIn('QSAMSVC:200; DEMOSVC:203', source)
        self.assertEqual(source.count('    DEMOCHECK(V,'), 5)
        self.assertIn('QSAMSVC(1,Q,R)', source)
        self.assertIn('QSAMSVC(3,Q,R)', source)
        self.assertIn('STOP(8)', source)
        self.assertIn('Q2 MIX BCPLQSAM BCPLDEMO WRITTEN PASS', source)

    def test_bad_extension_dsn_or_job_rejected(self):
        with self.assertRaisesRegex(ValueError, 'EXT_OBJ'):
            GEN.make_deck(
                'bad', ["//Q2MIX JOB (BCPL),'BAD',CLASS=A"],
                'HERC02.BCPL.BOOT.OBJ', 'WRONG/DSN')
        with self.assertRaisesRegex(ValueError, 'Q2MIX'):
            GEN.make_deck(
                'bad', ["//WRONG JOB (BCPL),'BAD',CLASS=A"],
                'HERC02.BCPL.BOOT.OBJ', 'HERC02.BCPL.EXT.OBJ')


if __name__ == '__main__':
    unittest.main()
