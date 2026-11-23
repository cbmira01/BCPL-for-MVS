"""Offline refusal and structural tests for the TA.3 BC0003 recipient runner."""
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/ta3-rc3-recipient'
loader = SourceFileLoader('ta3_tested', str(SCRIPT))
spec = spec_from_loader(loader.name, loader)
mod = module_from_spec(spec)
spec.loader.exec_module(mod)


class TestRecipient(unittest.TestCase):
    def test_canonical_positions_and_member_count(self):
        counts = [7,5,1,4,9,11,21,26,1,1]
        ds = [{'sequence':n,'group':('common' if n == 3 else 'mr10'),
               'target_dsn_template':'{HLQ}.BCPL.P%04d' % n,
               'members':['M%03d' % j for j in range(counts[n-3])]}
              for n in range(3,13)]
        manifest = {'release':{'candidate_id':'BCPL-0.1.0-rc3',
                               'native_compiler':'absent'},
                    'volume':{'volser':'BC0003'},
                    'datasets':[{'sequence':1},{'sequence':2}]+ds+
                        [{'sequence':n} for n in range(13,22)]}
        target = mod.target_rows(manifest)
        self.assertEqual(len(target),11)
        self.assertEqual(sum(len(t[2]) for t in target),90)
        self.assertEqual(target[0][1],'HERC02.BCPL.TA3N1.DIST.INST')
        manifest['volume']['volser']='BC0002'
        with self.assertRaises(mod.Refusal):mod.target_rows(manifest)

    def test_strict_missing_and_stale(self):
        class C:
            @staticmethod
            def dataset_missing(report, name):return name in report
        self.assertTrue(mod.absent(C(),'DS1 DS2',['DS1','DS2']))
        self.assertFalse(mod.absent(C(),'DS1',['DS1','DS2']))

    def test_remove_only_valid_jobcard(self):
        j='//DSPALST JOB (X)\n//             USER=ABC,PASSWORD=*****\n//             MSGLEVEL=(1,1)\n//STAT EXEC PGM=IKJEFT01\n'
        self.assertEqual(mod.deck_without_stat(j),'//STAT EXEC PGM=IKJEFT01\n')
        with self.assertRaises(mod.Refusal): mod.deck_without_stat('junk\n'+j)

    def test_report_step_sequence_rejection(self):
        class RC:
            @staticmethod
            def artifact(folder,name,body):
                (folder/name).write_text(body)
        class C:
            @staticmethod
            def authenticated_job_card(cfg,name,desc,redact):
                return [f'//{name:<8} JOB (X)',
                        '//             USER=X,PASSWORD=TEST',
                        '//             MSGLEVEL=(1,1)']
            @staticmethod
            def submit_and_wait(cfg,deck,max_rc,cursor_file):
                return 123,('JOB 123 TA3BOOT\nJOB RESULT: SUCCESS\n'
                            'HIGHEST RC: 0000\nBOOTREAD IEBGENER RC=0000\n')
            report='IEF142I TA3BOOT BOOTREAD - STEP WAS EXECUTED - COND CODE 0000\n'
            @classmethod
            def job_report(cls,job,cursor_file):return cls.report
        work=SCRIPT.parents[4]/'workarea'
        work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as td:
            p=Path(td)
            job,_,_=mod.mvs_job(RC(),C(),{},p,'boot','TA3BOOT',
                                 '//BOOTREAD EXEC PGM=IEBGENER\n//\n',
                                 [('BOOTREAD','IEBGENER')])
            self.assertEqual(job,123)
            C.report='IEF142I TA3BOOT BOOTREAD - STEP WAS EXECUTED - COND CODE 0008\n'
            with self.assertRaises(mod.Refusal):
                mod.mvs_job(RC(),C(),{},p,'bad','TA3BOOT',
                            '//BOOTREAD EXEC PGM=IEBGENER\n//\n',
                            [('BOOTREAD','IEBGENER')])


if __name__=='__main__':unittest.main()
