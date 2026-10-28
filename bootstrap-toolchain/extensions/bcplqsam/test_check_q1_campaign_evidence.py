"""Negative and positive proof tests for Q.1 native report review."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
S=importlib.util.spec_from_file_location('evidence',Path(__file__).with_name('check-q1-campaign-evidence.py'))
assert S and S.loader
E=importlib.util.module_from_spec(S)
S.loader.exec_module(E)


def fixture(profile):
    job,steps,go,markers=E.CASES[profile]
    body='\n'.join(f'{name:<10} PGM=*.DD  RC={go if name=="GO" else 0:04}' for name in sorted(steps))
    summary=f'JOB 9999  {job}\n'+body+'\nAssembler:\n  Statements flagged: 0\n  Highest severity: 0\n'
    report='BAD SOURCE\n'+ '\n'.join(markers)+'\nAUTHORIZATION CODE IS 00000000\n'+'\n'.join(markers)+'\n'
    return summary,report


class EvidenceTest(unittest.TestCase):
    def test_all_four_profiles_are_valid_with_real_native_records(self):
        for profile in E.CASES:
            with self.subTest(profile=profile):
                s,r=fixture(profile)
                self.assertEqual(E.review(profile,s,r),(True,[]))

    def test_stop_rc8_is_not_a_failure_but_finish_rc8_is(self):
        s,r=fixture('finish')
        s=s.replace('GO         PGM=*.DD  RC=0000','GO         PGM=*.DD  RC=0008')
        self.assertFalse(E.review('finish',s,r)[0])
        s,r=fixture('stop')
        self.assertTrue(E.review('stop',s,r)[0])

    def test_listing_marker_is_not_native_evidence(self):
        s,r=fixture('finish')
        r=r.split('AUTHORIZATION CODE IS')[0]+'AUTHORIZATION CODE IS 00000000\n'
        self.assertFalse(E.review('finish',s,r)[0])

    def test_missing_job_assembler_and_duplicate_steps(self):
        s,r=fixture('negative')
        self.assertFalse(E.review('negative',s.replace('Q1NEG','WRONG'),r)[0])
        self.assertFalse(E.review('negative',s.replace('Highest severity: 0','Highest severity: 4'),r)[0])
        self.assertFalse(E.review('negative',s+'GO         PGM=*.DD  RC=0000\n',r)[0])

    def test_bad_native_messages_fail(self):
        s,r=fixture('stop')
        self.assertFalse(E.review('stop',s,r+'BCPLREG 2001 FINALIZER RETURNED NONZERO\n')[0])

    def test_console_supplies_missing_wto_but_not_source_listing(self):
        s,r=fixture('finish')
        r=r.replace('AUTHORIZATION CODE IS 00000000\n'+
                    '\n'.join(E.CASES['finish'][3]),
                    'AUTHORIZATION CODE IS 00000000\nBCPLQSAM Q1 16 FINISH PASS')
        self.assertFalse(E.review('finish',s,r)[0])
        console='IEF403I Q16FIN - STARTED\n'+E.FINAL+'\nIEF404I Q16FIN - ENDED\n'
        self.assertTrue(E.review('finish',s,r,console)[0])
        listing=console.replace(E.FINAL,"WTO '"+E.FINAL+"'")
        self.assertFalse(E.review('finish',s,r,listing)[0])

    def test_negative_failure_reports_status(self):
        s,r=fixture('negative')
        r=r+'BCPLQSAM Q1 NEGATIVE FAIL 3 RC=-6\n'
        ok,issues=E.review('negative',s,r)
        self.assertFalse(ok)
        self.assertIn('negative assertion 3 returned -6',issues)

if __name__=='__main__':unittest.main()
