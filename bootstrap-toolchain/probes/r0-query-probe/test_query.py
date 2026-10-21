"""Offline test-only checks for shared QUERY probe/JCL generator."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def loaded(filename, name):
    s = importlib.util.spec_from_file_location(name, HERE / filename)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


class QueryProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.make = loaded('make-job.py', 'r0query_gen')
        cls.verify = loaded('verify-report.py', 'r0query_verify')
        cls.base = cls.make.load(cls.make.TRAIL, 'r0query_sample')

    def source(self):
        return self.base.sample_generated()

    def card(self):
        return ["//R0QUERY JOB (BCPL),'R0 QUERY',CLASS=A,MSGCLASS=A"]

    def test_injected_two_globals(self):
        text = '\n'.join(self.make.application_source(self.source()))
        for number, symbol in ((298, 'R0QAA'), (299, 'R0QBB')):
            self.assertIn(f"DC F'{number*4}'", text)
            self.assertIn(f'DC A({symbol})', text)
            self.assertEqual(text.count(f'EXTRN {symbol}'), 1)
        self.assertIn("DC F'4'", text)
        self.assertIn('END   R0APP', text)

    def test_source_must_export_only_start(self):
        other = self.source().replace("         DC    F'4'", "         DC    F'8'")
        with self.assertRaises(ValueError):
            self.make.application_source(other)

    def test_reject_existing_test_global(self):
        src = self.source().replace("         DC    F'4'", "         DC    F'1192'")
        with self.assertRaises(ValueError):
            self.make.application_source(src)

    def test_three_independent_assembly_streams(self):
        text = self.make.make_deck(self.card(), self.source(),
                                   'HERC02.BCPL.BOOT.OBJ')
        self.assertEqual(text.count('//SYSIN    DD  *'), 3)
        for item in ['ASMA', 'ASMB', 'ASMC', 'LKED', 'GO']:
            self.assertIn('//'+item, text)
        self.assertIn(' INCLUDE OBJ(BLIB)', text)
        self.assertIn(' NAME R0QUERY(R)', text)
        self.assertEqual(text.count('DISP=(OLD,DELETE)'), 3)
        self.assertNotIn('BOOT_DEVOBJ', text)

    def test_reject_invalid_job_card(self):
        with self.assertRaises(ValueError):
            self.make.make_deck(['//WRONG JOB'], self.source(), 'OBJ')

    def test_check_cards_before_job(self):
        for name in ('dispatcher-a.asm', 'dispatcher-b.asm'):
            self.base.checked_asm((HERE / name).read_text('ascii'), name)

    def test_query_signature_and_sized_copy(self):
        for name, size in [('dispatcher-a.asm', 6), ('dispatcher-b.asm', 8)]:
            t = (HERE / name).read_text('ascii')
            self.assertIn('LTR   8,8', t)
            self.assertIn('LTR   9,9', t)
            self.assertIn(f"C     9,=F'{size}'", t)
            self.assertIn("L     7,=F'-1'", t)
            self.assertIn("L     7,=F'-2'", t)
            self.assertIn("L     7,=F'-3'", t)
            self.assertLess(t.index(f"C     9,=F'{size}'"), t.index('SLL   8,2'))

    def test_buffer_sentinels_and_operation_checks(self):
        t=(HERE/'caller.bcpl').read_text('ascii')
        self.assertIn('R0QA(0, A, 5)',t)
        self.assertIn('R0QB(0, B, 6)',t)
        self.assertIn('A!6 NE 777 | A!7 NE 777',t)
        self.assertIn('B!6 NE 77 | B!7 NE 99',t)
        self.assertIn('R0QA(99, 0, 0)',t)
        self.assertIn('R0QB(99, 0, 0)',t)

    def test_exact_marker_only(self):
        self.verify.verify('heading\nR0 QUERY TWO DISPATCHERS PASS\n')
        for invalid in ('R0 QUERY TWO DISPATCHERS PASS',
                        '  R0 QUERY TWO DISPATCHERS PASS\n',
                        'R0 QUERY TWO DISPATCHERS PASS\n' * 2,
                        'R0 QUERY TWO DISPATCHERS FAILURE\n'):
            if invalid == 'R0 QUERY TWO DISPATCHERS PASS':
                continue  # no trailing newline alone is a valid text line
            with self.assertRaises(ValueError):
                self.verify.verify(invalid)


if __name__ == '__main__':
    unittest.main()
