#!/usr/bin/env python3
"""Credential-free structural checks for the proposed Q.0 MVS batch."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g = load(HERE / 'make-jobs.py', 'q0_native_generation')
v = load(HERE / 'verify-report.py', 'q0_native_verification')


def example(profile):
    job, _ = g.PROFILES[profile]
    t = g.load(g.TRAIL, 'q0_native_unit_trailer')
    return g.deck(profile, t.sample_generated(),
                  [f"//{job:<8} JOB (BCPL),'Q0 TEST',CLASS=A"],
                  'HERC02.BCPL.BOOT.OBJ')


def sample_evidence(profile):
    steps = ('ASMWR', 'ASMA', 'ASMT', 'ASMG', 'LKWR',
             'LKED', 'WGO', 'GO')
    summary = '\n'.join(f'{step} PGM=TEST RC='+(
        '0008' if profile == 'stop' and step == 'GO' else '0000')
                        for step in steps)
    job = {'finish': 'Q0NFIN', 'stop': 'Q0NSTP'}[profile]
    report = ('IEWL MAP R0APP BCPLMAIN RGINIT Q0TDESC Q0TDISP '
              'Q0TFIN BCPLREG\n'
              + f'IEF236I ALLOC. FOR {job} GO\n'
              + 'Q0 NATIVE 16 OPEN READ PASS\n'
              + f'Q0 NATIVE BCPL {profile.upper()} PASS\n'
              + f'Q0 FINALIZER {profile.upper()} 16 CLOSE FREE PASS\n')
    return summary, report


class NativeQ0Batch(unittest.TestCase):
    def test_synthetic_all_profiles(self):
        for profile in g.PROFILES:
            with self.subTest(profile=profile):
                deck = example(profile)
                self.assertEqual(deck.splitlines().count('/*'), 6)
                self.assertIn(' ENTRY R0APP', deck)
                self.assertIn('//OBJ      DD  DSN=HERC02.BCPL.BOOT.OBJ,DISP=SHR',
                              deck)
                self.assertNotIn('DISP=MOD', deck)
                self.assertNotIn('CATLG', deck)
                for i in range(16):
                    self.assertEqual(deck.count(f'DSN=&&Q0H{i:02d}'), 2)

    def test_test_only_package_and_allocation(self):
        src = g.extension()
        self.assertIn("F'299',A(Q0TDISP)", src)
        # Native dispatcher must retain R4 as its CSECT base;
        # R15 points at the BCPL argument/result frame.
        self.assertIn('         USING Q0TDISP,4', src)
        self.assertNotIn('         LR    4,15', src)
        self.assertNotIn("F'200',", src)
        self.assertEqual(src.count('         GETMAIN RC,LV=1024'), 16)
        self.assertEqual(src.count('         FREEMAIN R,LV=1024,A=(1)'),
                         32)   # rollback + finalizer
        self.assertEqual(src.count('         OPEN  (DC'), 16)
        self.assertEqual(src.count('         CLOSE (DC'), 16)
        self.assertEqual(src.count('         GET   DC'), 16)
        self.assertIn("CL8'Q0PROBE'", g.registry())
        self.assertIn("F'1',F'28',F'44',F'1',F'1',F'0'", g.registry())
        self.assertIn("F'1',F'48',F'56'", src)
        g.checked(src.splitlines())

    def test_mvs_return_status_survives_register_restore(self):
        # JOB 6595 reached all 16 staged DCBs but helper restoration
        # overwrote R15 and wrongly directed FINISH to STOP(8).
        src = g.extension()
        for label, result_cell in (
                ('Q0TRET', 'IRESULT'),
                ('Q0TFRET', 'FRESULT')):
            with self.subTest(label=label):
                sequence = '\n'.join((
                    f'{label:<8} ST    15,{result_cell}',
                    '         L     13,4(13)',
                    '         LM    14,14,12(13)',
                    f'         L     15,{result_cell}',
                    '         LM    0,12,20(13)',
                    '         BR    14'))
                self.assertIn(sequence, src)
        self.assertNotIn('         LM    14,12,12(13)', src)
        self.assertIn("IRESULT  DC    F'0'", src)

    def test_live_go_only_and_step_codes(self):
        for profile in ('finish', 'stop'):
            s, report = sample_evidence(profile)
            v.verify(profile, s, report)
            with self.assertRaises(ValueError):
                v.verify(profile, s, report.replace(
                    f'Q0 FINALIZER {profile.upper()} 16 CLOSE FREE PASS\n',
                    ''))
            with self.assertRaises(ValueError):
                v.verify(profile, s.replace('LKED PGM=TEST RC=0000',
                                            'LKED PGM=TEST RC=0008'), report)
            with self.assertRaises(ValueError):
                v.verify(profile, s, report.replace(
                    'Q0 NATIVE 16 OPEN READ PASS\n',
                    'Q0 FINALIZER BAD STATE\n'))
            with self.assertRaises(ValueError):
                v.verify(profile, s, report +
                         'BCPLREG 2001 FINALIZER RETURNED NONZERO\n')

    def test_go_marker_in_listing_not_sufficient(self):
        s, report = sample_evidence('finish')
        report = report.replace('Q0 NATIVE 16 OPEN READ PASS\n', '')
        report = 'Q0 NATIVE 16 OPEN READ PASS\n' + report
        with self.assertRaises(ValueError):
            v.verify('finish', s, report)


if __name__ == '__main__':
    unittest.main()
