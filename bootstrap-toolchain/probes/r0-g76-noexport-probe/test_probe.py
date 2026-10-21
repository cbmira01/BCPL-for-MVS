"""Host-only bounds, linkage and output tests for the R.0 G!76 fixture."""
from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def module(path, name):
    spec = importlib.util.spec_from_loader(name, SourceFileLoader(name, str(path)))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class NoExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gen = module(HERE / 'make-job.py', 'r0g76fgen')
        cls.verify = module(HERE / 'verify-report.py', 'r0g76fverify')
        cls.fixture = (HERE / 'blib-empty.asm').read_text('ascii')
        cls.sample = cls.gen.load(cls.gen.TRAIL, 'r0g76ftrailtest').sample_generated()
        cls.card = ["//R0G76F  JOB (BCPL),'TEST',CLASS=A,MSGCLASS=A"]
        cls.obj = 'HERC02.BCPL.BOOT.OBJ'

    def test_exact_fixture(self):
        self.assertEqual(self.gen.fixture_source(self.fixture)[-1], '         END   BLIB')
        self.assertIn("         DC    F'0'", self.fixture)
        self.assertIn('         DC    AL2(BLEND-BLIB)', self.fixture)

    def test_reject_fixture_extra_export(self):
        broken = self.fixture.replace("         DC    F'0'", "         DC    F'304'\n         DC    A(BLIB)")
        with self.assertRaisesRegex(ValueError, 'exact no-export'):
            self.gen.fixture_source(broken)

    def test_reject_fixture_shortened_length(self):
        with self.assertRaises(ValueError):
            self.gen.fixture_source(self.fixture.replace('BLEND-BLIB', 'BLEND-BLIB-4'))

    def test_reject_fixture_extra_symbol(self):
        with self.assertRaises(ValueError):
            self.gen.fixture_source(self.fixture.replace('ENTRY BLIB', 'ENTRY BLIB,WRITEF'))

    def test_source_requires_writef_and_no_blib_calls(self):
        src = (HERE / 'source.bcpl').read_text('ascii')
        self.assertIn('WRITEF:76', src)
        self.assertIn('WRITEF("R0 G76 FALLBACK %N PASS", 31415)', src)
        self.assertNotIn('WRITES:', src)
        self.assertNotIn('NEWLINE:', src)

    def test_app_start_only(self):
        rows = self.gen.application_source(self.sample)
        self.assertIn('R0APP    CSECT', rows)
        self.assertNotIn('         EXTRN BLIB', rows)

    def test_application_extra_export_rejected(self):
        broken = self.sample.replace('L998     EQU   *', "         DC F'604'\n         DC A(L999)\nL998     EQU   *")
        with self.assertRaises(ValueError):
            self.gen.application_source(broken)

    def test_jcl_no_installed_blib(self):
        deck = self.gen.make_deck(self.card, self.sample, self.fixture, self.obj)
        self.assertNotIn(' INCLUDE OBJ(BLIB)', deck)
        self.assertIn('//OBJ      DD  DSN=HERC02.BCPL.BOOT.OBJ,DISP=SHR', deck)
        self.assertIn(' ENTRY R0APP', deck)
        self.assertIn(' NAME R0G76F(R)', deck)
        self.assertEqual(deck.splitlines().count('/*'), 3)
        self.assertEqual(deck.count('PGM=IFOX00'), 2)
        self.assertEqual(deck.count('DSN=&&R0BOBJ'), 2)
        self.assertNotIn('DISP=MOD', deck)

    def test_reject_bad_dsn(self):
        with self.assertRaises(ValueError):
            self.gen.make_deck(self.card, self.sample, self.fixture, 'HERC02.BCPL.BOOT.DEVOBJ')

    def test_reject_wrong_jobcard(self):
        with self.assertRaises(ValueError):
            self.gen.make_deck(['//WRONG JOB TEST'], self.sample, self.fixture, self.obj)

    def test_jcl_all_lines_fixed_width(self):
        deck = self.gen.make_deck(self.card, self.sample, self.fixture, self.obj)
        self.assertTrue(all(len(x) <= 71 and x.isascii() for x in deck.splitlines()))

    def fake_report(self, marker=True, rc=0, recs=(5, 3)):
        text = '\n'.join(
            f'IEF142I R0G76F {step} - STEP WAS EXECUTED - COND CODE {rc if step == "GO" else 0:04d}'
            for step in ('ASMA', 'ASMB', 'LKED', 'GO')
        ) + '\n'
        text += '\n'.join('TOTAL RECORDS PUNCHED '+str(n)+'\nNO STATEMENTS FLAGGED IN THIS ASSEMBLY\nHIGHEST SEVERITY WAS 0' for n in recs)
        return text+'\n'+('R0 G76 FALLBACK 31415 PASS\n' if marker else '')

    def test_output_good(self):
        result = self.verify.verify(self.fake_report())
        self.assertEqual(result['status'], 'R0_G76_NO_EXPORT_FALLBACK_PASS')

    def test_wrong_rc_rejected(self):
        with self.assertRaises(ValueError):
            self.verify.verify(self.fake_report(rc=8))

    def test_missing_marker_rejected(self):
        with self.assertRaises(ValueError):
            self.verify.verify(self.fake_report(marker=False))

    def test_duplicate_marker_rejected(self):
        with self.assertRaises(ValueError):
            self.verify.verify(self.fake_report()+self.verify.MARKER+'\n')

    def test_empty_object_rejected(self):
        with self.assertRaises(ValueError):
            self.verify.verify(self.fake_report(recs=(5, 0)))

    def test_duplicate_step_rejected(self):
        with self.assertRaises(ValueError):
            self.verify.verify(self.fake_report()+'IEF142I R0G76F GO - STEP WAS EXECUTED - COND CODE 0000\n')

    def test_utility_abend_rejected(self):
        with self.assertRaises(ValueError):
            self.verify.verify(self.fake_report()+'IEF450I R0G76F ABEND SYSTEM=0C4\n')


if __name__ == '__main__':
    unittest.main()
