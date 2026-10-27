"""Isolated synthetic-card and negative tests for consolidated Q.1 preparation.

The full --check additionally runs the source-controlled Q.1/Q.0 helpers on WSL.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('q1_campaign', HERE/'prepare-q1-campaign.py')
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def base_query():
    rows=["//Q1QUERY JOB (BCPL),'Q1 SAMPLE',CLASS=A"]
    for step in ['ASMA','ASMN','ASMR','ASMQ','ASMG']:
        rows += [f'//{step:<8} EXEC PGM=IFOX00',
                 '//SYSIN    DD  *','         ABC   X','/*']
    rows += ['         BCXREQ BCPLQSAM',
             '//LKED     EXEC PGM=IEWL',' ENTRY R0APP',
             ' NAME Q1QUERY(R)','/*',
             '//SYSLMOD  DD  DSN=&&Q1LOAD(Q1QUERY),',
             mod.GO, '//             TIME=(,2),COND=(0,NE,LKED)',
             '//SYSPRINT DD  SYSOUT=*', '//SYSUDUMP DD  SYSOUT=*','//']
    return '\n'.join(rows)+'\n'


def base_three():
    rows = base_query().splitlines()
    rows[0] = "//Q13DD JOB (BCPL),'Q1 SAMPLE',CLASS=A"
    at=1
    rows[at:at]=[
        '//ASMWR    EXEC PGM=IFOX00','//SYSIN    DD  *',
        'Q0HNW    CSECT','         BR    14','/*',
        '//LKWR     EXEC PGM=IEWL',' ENTRY Q0HNW','/*']
    rows=[r.replace(' NAME Q1QUERY(R)',' NAME Q13DD(R)').replace(
        '//SYSLMOD  DD  DSN=&&Q1LOAD(Q1QUERY),',
        '//SYSLMOD  DD  DSN=&&Q1LOAD(Q13DD),') for r in rows]
    go=rows.index(mod.GO)
    writer=[mod.WGO,'//             TIME=(,2),COND=(0,NE,LKWR)']
    for i in range(3):
        writer += [f'//Q{i:02d}      DD  DSN=&&Q1H{i:02d},DISP=(NEW,PASS),',
                   '//             UNIT=SYSDA,SPACE=(TRK,(2,1)),',mod.DCB]
    writer += ['//SYSUDUMP DD  SYSOUT=*']
    rows[go:go]=writer
    go=rows.index(mod.GO)
    reader=[f'//Q{i:02d}      DD  DSN=&&Q1H{i:02d},DISP=(OLD,DELETE)'
            for i in range(3)]
    rows[go+2:go+2]=reader
    return '\n'.join(rows)+'\n'


class CampaignTest(unittest.TestCase):
    def setUp(self):
        self.three = SimpleNamespace(
            make_deck=lambda *_: base_three(),
            q0_writer_helper=lambda: SimpleNamespace(make_source=lambda n,r:
                '\n'.join(['Q0HNW    CSECT']+
                          [f'DC{i:02d}     DCB DDNAME=Q{i:02d}' for i in range(n)])))
        self.query = SimpleNamespace(make_deck=lambda *_: base_query())

    def make(self, profile, header=None):
        job=mod.PROFILE[profile][0]
        with patch.object(mod, 'module', side_effect=lambda n:
                          self.three if n=='prepare-q1-3dd.py' else self.query):
            return mod.make_deck(profile,'SOURCE',header or
                 [f"//{job} JOB (BCPL),'Q1 CHECK',CLASS=A"],
                 'HERC02.BCPL.BOOT.OBJ')

    def test_sixteen_with_unique_temporary_dds(self):
        for profile in ('finish','stop'):
            with self.subTest(profile=profile):
                d=self.make(profile)
                rows=d.splitlines()
                self.assertEqual(rows.count(mod.DCB),32)
                self.assertEqual(rows.count(mod.WGO),1)
                self.assertEqual(rows.count(mod.GO),1)
                self.assertIn('DC15     DCB DDNAME=Q15',d)
                self.assertEqual(rows.count('//SYSIN    DD  *'),6)
                self.assertEqual(rows.count('/*'),8)
                self.assertEqual(rows[-1],'//')
                self.assertNotIn('DISP=MOD',d)
                self.assertNotIn('CATLG',d)
                self.assertNotIn('DSN=&&Q1H16',d)
                for n in range(16):
                    self.assertIn(f'//Q{n:02d}      DD  DSN=&&Q1H{n:02d},DISP=(OLD,DELETE),\n'+mod.DCB,d)

    def test_negative_and_output_uneventful(self):
        n=self.make('negative')
        o=self.make('output')
        self.assertNotIn('//WGO ',n)
        self.assertNotIn('//Q00 ',n)
        self.assertNotIn('//WGO ',o)
        self.assertIn('//QOUT     DD  DSN=&&Q1OUT,DISP=(NEW,DELETE),',o)
        self.assertIn(mod.DCB,o)
        self.assertEqual(n.count('//SYSIN    DD  *'),5)
        self.assertEqual(o.count('//SYSIN    DD  *'),5)

    def test_invalid_inputs_or_structure_rejected(self):
        with self.assertRaises(ValueError):
            self.make('finish',["//Q1NEG JOB (BCPL),'WRONG',CLASS=A"])
        with self.assertRaises(ValueError):
            mod.make_deck('unknown', '',[], '')
        with self.assertRaises(ValueError):
            mod.verify(base_three().splitlines(),'Q13DD','finish')
        modified=base_query().replace('         BCXREQ BCPLQSAM','         BCXREQ BCPLQSAM\n         BCXREQ BCPLQSAM')
        with patch.object(mod,'module',return_value=SimpleNamespace(make_deck=lambda *_:modified)):
            with self.assertRaises(ValueError):
                mod.make_deck('negative','SOURCE',
                    ["//Q1NEG JOB (BCPL),'CHECK',CLASS=A"],
                    'HERC02.BCPL.BOOT.OBJ')

    def test_job_continuation_preserved(self):
        extra='//             MSGCLASS=A'
        self.assertEqual(self.make('finish',[
            "//Q16FIN JOB (BCPL),'Q1 CHECK',CLASS=A,",extra]).splitlines()[1],extra)

    def test_no_submit_or_installed_mutations(self):
        src=(HERE/'prepare-q1-campaign.py').read_text('utf-8')
        self.assertNotIn('submit-jcl',src)
        self.assertNotIn('subprocess',src)
        self.assertIn('os.O_EXCL',src)
        self.assertIn('REGION=256K',src)

if __name__=='__main__':
    unittest.main()
