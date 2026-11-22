"""Synthetic TA.2 acceptance guards; never submit MVS jobs."""
import importlib.machinery
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/ta2-rc2-acceptance'
loader = importlib.machinery.SourceFileLoader('ta2_install_acceptance', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SUFFIXES = [
    'DIST.DOCS','MR10KIT.SOURCE','MR10KIT.ASM','MR10KIT.JCL',
    'MR10KIT.LIBRARY','MR10KIT.LANGDEMO','MR10KIT.BCPLDEMO',
    'MR10KIT.TESTS','MR10KIT.OBJ','MR10KIT.LOAD','BOOT.OBJ',
    'BOOT.ASM','BOOT.SOURCE','BOOT.JCL','EXT.OBJ','EXT.ASM',
    'EXT.SOURCE','EXT.MAC','CAMBRIDG.SOURCE']

def fixtures():
    datasets=[]; rows=[]
    for n in range(1,22):
        members = ([] if n == 1 else ['INSTALL','DATASETS','RELEASE','RESTORE'] if n == 2
                   else [f'M{i:07d}' for i in range(110)] if n == 3
                   else [f'S{i:07d}' for i in range(15)] if n == 21 else ['ONE'])
        dcb = {'dsorg':'PS' if n==1 else 'PO','recfm':'U' if n==12 else 'FB',
               'lrecl':0 if n==12 else 80,'blksize':6144 if n==12 else 800}
        datasets.append({'sequence':n, 'target_dsn_template':
                         '{HLQ}.BCPL.' + SUFFIXES[n-3] if n >= 3 else None})
        rows.append({'n':n,'target':f'HERC02.BCPL.TA2RB.BT{n:04d}',
                     'source':f'HERC02.BCPL.TA2STG.BT{n:04d}',
                     'dcb':dcb,'members':members,'space':(5,1,0) if n==1 else (20,5,10)})
    return rows, {'release':{'native_compiler':'absent'},
                  'volume':{'volser':'BC0002'},'datasets':datasets}

def fake_regression():
    lines = ['//* MRREGRES CANONICAL 12 CASES']
    for name in ['SSYNI','STRNI','SCGI','SBLIBI','SICLIB']:
        lines.append('//'+name+' EXEC PGM=IEBGENER')
    for n in range(1,24):
        for letter in ('C','G'):
            lines.extend([f'//{letter}{n:02d}A EXEC PGM=ICINT19',
                          '//STEPLIB DD DSN=HERC02.BCPL.MR10KIT.LOAD,DISP=SHR'])
    for n in range(1,13):
        lines.extend([f'//R{n:02d} EXEC PGM=ICINT19',
                      '//STEPLIB DD DSN=HERC02.BCPL.MR10KIT.LOAD,DISP=SHR'])
    return '\n'.join(lines) + '\n'

class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.raw, self.manifest = fixtures()
        self.rows = mod.mapped(self.raw,self.manifest)

    def test_21_new_destinations_and_volume(self):
        self.assertEqual(len(self.rows),21)
        self.assertEqual(len(set(r['install'] for r in self.rows)),21)
        self.assertTrue(all(r['install'].startswith(mod.INST_PREFIX) for r in self.rows))
        self.assertEqual(self.rows[11]['install'],'HERC02.BCPL.TA2INS.MR10KIT.LOAD')
        self.assertEqual(self.rows[20]['install'],'HERC02.BCPL.TA2INS.CAMBRIDG.SOURCE')
        self.assertEqual(self.rows[11]['dcb']['recfm'],'U')

    def test_install_jcl_all_21_and_no_tape(self):
        jcl=mod.installation_body(self.rows)
        self.assertEqual(jcl.count('EXEC PGM=IEBCOPY'),20)
        self.assertEqual(jcl.count('EXEC PGM=IEBGENER'),1)
        self.assertEqual(jcl.count('DISP=(NEW,CATLG,DELETE)'),21)
        self.assertEqual(jcl.count('DISP=SHR'),21)
        self.assertIn('DSORG=PO,RECFM=U,LRECL=0,BLKSIZE=6144',jcl)
        self.assertNotIn('UNIT=480',jcl)
        self.assertNotIn('BCPL.TA2STG.',jcl)
        self.assertNotIn('DISP=OLD',jcl)

    def test_genuine_regression_63_steps_and_12_cases(self):
        job=mod.regression_body(fake_regression())
        self.assertEqual(job.count('EXEC PGM='),63)
        self.assertIn('DSN=HERC02.BCPL.TA2INS.MR10KIT.LOAD',job)
        self.assertNotIn('HERC02.BCPL.MR10KIT.',job)
        self.assertTrue(job.endswith('//\n'))

    def test_jcl_card_lengths(self):
        for content in (mod.installation_body(self.rows),mod.regression_body(fake_regression())):
            self.assertTrue(all(len(x)<=80 for x in content.splitlines()))
            self.assertTrue(all(len(x)<=71 for x in content.splitlines()
                                if x.startswith('//') and not x.startswith('//*')))

    def test_reject_manifest_misordering(self):
        broken=dict(self.manifest, datasets=self.manifest['datasets'][:])
        broken['datasets'][8]=dict(broken['datasets'][8], sequence=11)
        with self.assertRaises(mod.Refusal):mod.mapped(self.raw,broken)

    def test_reject_unexpected_cambridge_claim(self):
        broken=dict(self.manifest,release={'native_compiler':'included'})
        with self.assertRaises(mod.Refusal):mod.mapped(self.raw,broken)

    def test_reject_alias(self):
        broken=[dict(r) for r in self.raw]
        broken[11]['target']=broken[10]['target']
        with self.assertRaises(mod.Refusal):mod.mapped(broken,self.manifest)

    def test_reject_regression_mismatch(self):
        for bad in (fake_regression().replace('MRREGRES','WRONG'),
                    fake_regression().replace('//R01 EXEC','//X01 EXEC'),
                    fake_regression().replace('EXEC PGM=IEBGENER','EXEC PGM=FAKE',1)):
            with self.subTest(bad=bad[:30]),self.assertRaises(mod.Refusal):
                mod.regression_body(bad)

    def test_job_success_not_semantic_acceptance(self):
        summary='JOB 9345 TA2INST\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n'+''.join(
            f'I{i:04d} {"IEBGENER" if i==1 else "IEBCOPY"} RC=0000\n' for i in range(1,22))
        mod.exact_install_result(9345,summary,'IEF142I completed normally')
        with self.assertRaises(mod.Refusal):
            mod.exact_install_result(9345,summary.replace('I0012 IEBCOPY RC=0000',
                                                           'I0012 IEBCOPY RC=0004'),'')

    def test_21_dcb_matches_21_absence(self):
        class Core:
            def dataset_missing(self,report,dsn):return dsn.startswith(mod.INST_PREFIX)
            def extract_listds_block(self,report,dsn):return [dsn]
            def parse_listds(self,block):
                n=int(block[0].split('BT')[-1]); d=self_ref.rows[n-1]['dcb']
                return dict(volume='TSO002',dsorg=d['dsorg'],recfm=d['recfm'],
                            lrecl=str(d['lrecl']),blksize=str(d['blksize']))
        self_ref=self
        mod.validate_catalog(Core(),'synthetic',self.rows)
        class BadCore(Core):
            def dataset_missing(self,report,dsn):return False
        with self.assertRaises(mod.Refusal):mod.validate_catalog(BadCore(),'synthetic',self.rows)

    def test_regression_steps_requires_12_runs(self):
        summary='JOB 9350 TA2MR10\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n'+''.join(
            f'R{i:02d} ICINT19 RC=0000\n' for i in range(1,13))
        mod.regression_steps(9350,summary)
        with self.assertRaises(mod.Refusal):
            mod.regression_steps(9350,summary.replace('R09 ICINT19 RC=0000','R09 ICINT19 RC=0004'))

    def test_run_closed_before_any_mvs_job(self):
        with patch.object(mod,'APPROVAL',Path('/missing/approval')):
            with self.assertRaisesRegex(mod.Refusal,'separate owner approval'):
                mod.owner_approval(('a','b'))

    def test_refuse_unsafe_jcl(self):
        with self.assertRaises(mod.Refusal):mod.cards('//'+'X'*72+'\n')
        with self.assertRaises(mod.Refusal):mod.cards('//X DD DUMMY\t\n')

    def test_save_exclusive_and_sealed(self):
        with tempfile.TemporaryDirectory(dir=SCRIPT.parents[4] / 'workarea') as path:
            d=Path(path);mod.save(d/'x',b'abc')
            with self.assertRaises(FileExistsError):mod.save(d/'x',b'bye')
            mod.seal(d)
            self.assertEqual(len((d/'SHA256SUMS').read_text().splitlines()),1)

if __name__ == '__main__':unittest.main()
