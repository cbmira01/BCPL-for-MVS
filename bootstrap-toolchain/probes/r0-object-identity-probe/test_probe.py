"""Credential-free checks for binary-safe Decision A stage-2 JCL."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load('r0bimake', 'make-jobs.py')
        cls.v = load('r0biverify', 'verify-report.py')

    def job(self, profile):
        return [f"//{self.m.PROFILES[profile]} JOB (BCPL),'R0 B ID',CLASS=A,MSGCLASS=A"]

    def deck(self, profile):
        return self.m.make_deck(profile, self.job(profile),
                                dsn='HERC02.BCPL.BOOT.OBJ',
                                source='BCPLMEM  CSECT\n         END BCPLMEM\n')

    def test_calibration_both_assembler_objects(self):
        d=self.deck('calibrate')
        self.assertEqual(d.count('EXEC PGM=IFOX00'), 2)
        self.assertIn("DC    F'111'",d)
        self.assertIn("DC    F'222'",d)
        self.assertEqual(d.count('EXEC PGM=IEBCOMPR'),2)

    def test_calibration_copy_and_equal(self):
        d=self.deck('calibrate')
        self.assertIn('//COPYA    EXEC PGM=IEBGENER',d)
        self.assertIn('//SYSUT2   DD  DSN=&&COPYA,UNIT=SYSDA,',d)
        self.assertIn('//SAME     EXEC PGM=IEBCOMPR',d)
        self.assertIn('//DIFFER   EXEC PGM=IEBCOMPR',d)
        self.assertEqual(d.count(' COMPARE TYPORG=PS'),2)

    def test_member_input_only(self):
        d=self.deck('member')
        self.assertIn('//SYSUT1   DD  DSN=HERC02.BCPL.BOOT.OBJ(BCPLMEM),DISP=SHR',d)
        self.assertEqual(d.count('HERC02.BCPL.BOOT.OBJ'),1)
        self.assertNotIn('EXEC PGM=IEBGENER',d)
        self.assertIn('//SYSGO    DD  DSN=&&MEMOBJ',d)
        self.assertIn(' EXEC PGM=IEBCOMPR',d)
        self.assertEqual(d.count(' COMPARE TYPORG=PS'),1)
        self.assertNotIn('DSN=HERC02.BCPL.BOOT.OBJ(BCPLMEM),DISP=OLD',d)

    def test_no_accepted_dataset_writers(self):
        for p in self.m.PROFILES:
            d=self.deck(p)
            for line in d.splitlines():
                self.assertLessEqual(len(line),71)
                self.assertTrue(line.isascii())
            self.assertNotIn('PUTMEM',d)
            self.assertNotIn('DISP=MOD',d)
            self.assertNotIn('//SYSLMOD',d)
            self.assertNotIn('EXEC PGM=IEWL',d)

    def test_missing_member_identity_rejected(self):
        with self.assertRaisesRegex(ValueError,'BOOT_OBJ name'):
            self.m.make_deck('member',self.job('member'),source='A CSECT\n')

    def test_real_job_card_is_padded_to_eight_columns(self):
        card=[f'//{self.m.PROFILES["calibrate"]:<8} JOB (BCPL),\'R0 B ID\'']
        self.assertIn('EXEC PGM=IEBCOMPR', self.m.make_deck('calibrate', card))

    def test_wrong_job_card_rejected(self):
        with self.assertRaisesRegex(ValueError,'JOB card'):
            self.m.make_deck('calibrate',['//BADJOB JOB ...'])

    def test_invalid_source_rejected(self):
        for text in ('A CSECT\t\n', 'x'*72+'\n', 'A CSECT', '//SYSUT2 DD *\n'):
            with self.assertRaises(ValueError):self.m.checked_source(text,'bad')

    def test_bad_dataset_config_rejected(self):
        class Core:
            @staticmethod
            def full_dsn(config,spec):return 'HERC02.BCPL.BOOT.OBJ'
        spec={'dsorg':'PO','recfm':'FB','lrecl':80,'blksize':800,
              'content_type':'object','populate':False}
        self.assertEqual(self.m.obj_spec(Core(),{'datasets':{'BOOT_OBJ':spec}}),
                         'HERC02.BCPL.BOOT.OBJ')
        for key,bad in [('recfm','VB'),('lrecl',81),('populate',True),('dsorg','PS')]:
            wrong=dict(spec);wrong[key]=bad
            with self.assertRaises(ValueError):
                self.m.obj_spec(Core(),{'datasets':{'BOOT_OBJ':wrong}})

    def test_manifest_correct_source_hash(self):
        src='BCPLMEM CSECT\n'
        m=self.m.source_manifest('member',src,'a'*40,'HERC02.BCPL.BOOT.OBJ')
        self.assertEqual(m['source_sha256'],__import__('hashlib').sha256(src.encode()).hexdigest())
        self.assertIn('(BCPLMEM)',m['installed_object_member'])

    def report(self,job,rc):
        result = ''.join(f'IEF142I {job} {name} - STEP WAS EXECUTED - COND CODE {code:04d}\n' for name,code in rc.items())
        return result + 'TOTAL RECORDS PUNCHED                        3\n' * (2 if job == 'R0BICAL' else 1)

    def test_calibration_exact_steps(self):
        text=self.report('R0BICAL',self.v.SUCCESS['calibrate'])
        result=self.v.verify('calibrate',text)
        self.assertEqual(result['status'],'RC_CALIBRATION_PASSED')
        with self.assertRaises(ValueError):
            self.v.verify('calibrate',text.replace('COND CODE 0008','COND CODE 0000'))
        with self.assertRaises(ValueError):
            self.v.verify('calibrate',text.replace('COND CODE 0000','COND CODE 0008',1))

    def test_utility_error_rc8_is_not_claimed_unequal(self):
        text=self.report('R0BIMEM',{'ASMMEM':0,'COMPARE':8})
        self.assertEqual(self.v.verify('member',text)['status'],'RC8_REVIEW_INEQUALITY_OR_ERROR')
        with self.assertRaises(ValueError):
            self.v.verify('member',text+'IEB001I SYSUT1 NOT OPENED\n')

    def test_member_equal_and_unknown(self):
        text=self.report('R0BIMEM',{'ASMMEM':0,'COMPARE':0})
        self.assertEqual(self.v.verify('member',text)['status'],'REPORTED_EQUAL')
        for changes in [{'ASMMEM':4,'COMPARE':0},{'ASMMEM':0,'COMPARE':12}, {'ASMMEM':0}]:
            with self.assertRaises(ValueError):
                self.v.verify('member',self.report('R0BIMEM',changes))

    def test_empty_or_missing_assembler_object_rejected(self):
        report=self.report('R0BICAL',self.v.SUCCESS['calibrate'])
        with self.assertRaises(ValueError):
            self.v.verify('calibrate',report.replace('RECORDS PUNCHED                        3','RECORDS PUNCHED                        0',1))
        with self.assertRaises(ValueError):
            self.v.verify('calibrate',report.split('TOTAL RECORDS PUNCHED')[0])

    def test_duplicate_step_result_rejected(self):
        text=self.report('R0BICAL',self.v.SUCCESS['calibrate'])
        with self.assertRaisesRegex(ValueError,'duplicate'):
            self.v.verify('calibrate',text+text)


if __name__=='__main__': unittest.main()
