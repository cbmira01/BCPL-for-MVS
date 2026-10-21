"""R.0 isolated G!150 test-only source/JCL/report safeguards."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import re
import unittest

HERE=Path(__file__).resolve().parent

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

class StartupOwnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.make=load(HERE/'make-job.py','g150make')
        cls.verify=load(HERE/'verify-report.py','g150verify')
        cls.trail=cls.make.load(cls.make.TRAIL,'g150trailtest')
        cls.helper=cls.make.load(cls.make.HELPER,'g150helpertest')
        cls.generated=cls.trail.sample_generated()
        cls.asm=(HERE/'observer.asm').read_text('ascii')

    def test_source_exercises_real_g150_read_without_call(self):
        source=(HERE/'source.bcpl').read_text('ascii')
        self.assertIn('CHECK150(0) NE 0 DO STOP(8)',source)
        self.assertIn('CHECK150(1), CHECK150(2)',source)
        self.assertIn('ACT=%X8 APP=%X8 PASS*N',source)
        self.assertNotIn('FORMTREE(',source)
        self.assertNotIn('MARK150(',source)

    def test_application_real_trailer_only_three_exports(self):
        source=self.make.application_source(self.generated)
        _,limit,pairs=self.helper.find_trailer(source)
        self.assertEqual(limit,2796)
        self.assertEqual([p[0] for p in pairs],[4,600,604])
        self.assertEqual(pairs[1:],[(600,'R0MARK'),(604,'R0CK15')])
        self.assertEqual(source.count('         EXTRN R0MARK,R0CK15'),1)
        self.assertEqual(source.count('R0APP    CSECT'),1)
        self.assertEqual(source.count('         END   R0APP'),1)

    def test_reject_duplicate_export_app(self):
        altered=self.generated.replace("         DC    F'4'", "         DC    F'604'",1)
        with self.assertRaises(ValueError):self.make.application_source(altered)

    def test_reject_non_cg370(self):
        with self.assertRaises(ValueError):self.make.application_source('NOTACSECT CSECT\n')

    def test_reject_source_without_trailer(self):
        with self.assertRaises(ValueError):self.make.application_source(self.generated.replace('L998     EQU   *','BAD      EQU   *'))

    def test_observer_checks_linked_Blib_and_marker(self):
        rows=self.make.checked_observer(self.asm)
        self.assertEqual(rows.count('         EXTRN BLIB'),1)
        self.assertIn('         L     7,600(12)',rows)
        self.assertIn('         L     8,=A(R0MARK)',rows)
        self.assertIn("         C     7,=F'600'",rows)
        self.assertNotIn('         ST    7,600(12)',rows)

    def test_reject_observer_write(self):
        with self.assertRaises(ValueError):self.make.checked_observer(self.asm.replace('         L     7,600(12)','         ST    7,600(12)',1))

    def test_reject_observer_missing_check(self):
        with self.assertRaises(ValueError):self.make.checked_observer(self.asm.replace("         C     7,=F'600'","         C     7,=F'604'"))

    def test_reject_observer_long_card(self):
        with self.assertRaises(ValueError):self.make.checked_observer(self.asm+'*'+'X'*80+'\n')

    def deck(self):
        return self.make.make_deck(["//R0G150  JOB (BCPL),'G150 OWNER',CLASS=A,MSGCLASS=A"],self.generated,self.asm,'HERC02.BCPL.BOOT.OBJ')

    def test_deck_is_read_only(self):
        deck=self.deck()
        self.assertEqual(deck.count(' INCLUDE OBJ('),6)
        self.assertIn(' INCLUDE OBJ(BLIB)',deck)
        self.assertIn('//OBJ      DD  DSN=HERC02.BCPL.BOOT.OBJ,DISP=SHR',deck)
        self.assertIn(' NAME R0G150(R)',deck)
        self.assertNotIn('DISP=MOD',deck)
        self.assertNotIn('BOOT.DEVOBJ',deck)
        self.assertEqual(deck.splitlines().count('/*'),3)

    def test_deck_cards_under_col71(self):
        for i,row in enumerate(self.deck().splitlines(),1):
            self.assertLessEqual(len(row),71,(i,row))

    def test_reject_bad_job_name(self):
        with self.assertRaises(ValueError):
            self.make.make_deck(['//WRONG JOB (BCPL),CLASS=A'],self.generated,self.asm,'HERC02.BCPL.BOOT.OBJ')

    def test_reject_incorrect_dsn(self):
        with self.assertRaises(ValueError):
            self.make.make_deck(['//R0G150 JOB (BCPL)'],self.generated,self.asm,'HERC02.BCPL.BOOT.DEVOBJ')

    def test_verify_good(self):
        r=self.sample_report()
        result=self.verify.verify(r)
        self.assertEqual(result['observed_g150_hex'],'000AC9F4')
        self.assertEqual(result['application_owner_hex'],'00088EE0')
        self.assertFalse(result['exact_debugint_address_proved'])

    @staticmethod
    def sample_report(actual='000AC9F4',app='00088EE0'):
        return '\n'.join([
            'IEF142I R0G150 ASMA - STEP WAS EXECUTED - COND CODE 0000',
            'IEF142I R0G150 ASMP - STEP WAS EXECUTED - COND CODE 0000',
            'IEF142I R0G150 LKED - STEP WAS EXECUTED - COND CODE 0000',
            'IEF142I R0G150 GO - STEP WAS EXECUTED - COND CODE 0000',
            'NO STATEMENTS FLAGGED IN THIS ASSEMBLY',
            'HIGHEST SEVERITY WAS    0',
            'TOTAL RECORDS PUNCHED                         6',
            'NO STATEMENTS FLAGGED IN THIS ASSEMBLY',
            'HIGHEST SEVERITY WAS    0',
            'TOTAL RECORDS PUNCHED                         9',
            f'R0 G150 OVERWRITE ACT={actual} APP={app} PASS',''])

    def test_reject_same_addresses(self):
        with self.assertRaises(ValueError):self.verify.verify(self.sample_report('00088EE0','00088EE0'))

    def test_reject_unset_sentinel(self):
        with self.assertRaises(ValueError):self.verify.verify(self.sample_report('C7D3F258'))

    def test_reject_bad_hex(self):
        with self.assertRaises(ValueError):self.verify.verify(self.sample_report('000000XX'))

    def test_reject_zero_address(self):
        with self.assertRaises(ValueError):self.verify.verify(self.sample_report('00000000'))

    def test_reject_duplicate_marker(self):
        with self.assertRaises(ValueError):self.verify.verify(self.sample_report()*2)

    def test_reject_wrong_step(self):
        with self.assertRaises(ValueError):self.verify.verify(self.sample_report().replace('CODE 0000','CODE 0008',1))

    def test_reject_duplicate_step(self):
        with self.assertRaises(ValueError):self.verify.verify(self.sample_report().replace('IEF142I R0G150 GO','IEF142I R0G150 ASMP'))

    def test_reject_missing_assembler_records(self):
        with self.assertRaises(ValueError):self.verify.verify(self.sample_report().replace('PUNCHED                         9','PUNCHED                         0'))

    def test_reject_missing_listing(self):
        with self.assertRaises(ValueError):self.verify.verify(self.sample_report().replace('HIGHEST SEVERITY WAS    0','HIGHEST SEVERITY WAS    4',1))

    def test_reject_abend(self):
        with self.assertRaises(ValueError):self.verify.verify(self.sample_report()+'IEF450I R0G150 - ABEND\n')

if __name__=='__main__':unittest.main()
