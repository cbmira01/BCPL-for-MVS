"""Synthetic safety and JES receipt tests: never contacts MVS/Hercules."""
import hashlib
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent/'scripts/run-ta1-track-b-go'
loader = importlib.machinery.SourceFileLoader('test_ta1b_go_runner', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
g = importlib.util.module_from_spec(spec)
loader.exec_module(g)


class GOGuards(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(dir=HERE.parents[3]/'workarea')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)/'repo'
        self.ops = self.root/'workarea/ta1b-operations'
        self.ops.mkdir(parents=True)
        self.tape = self.root/'mvs-state/tape/bcpl-ta1-b-20261117-01.aws'
        self.tape.parent.mkdir(parents=True)
        self.tape.write_bytes(b'BTA102 SYNTHETIC TAPE; NOT ACTUAL AWS')
        self.sha = hashlib.sha256(self.tape.read_bytes()).hexdigest()
        self.dlog = self.ops/'BTA102-track-b-directory-20261119T024927Z-11906'
        self.dlog.mkdir()
        self.log = self.ops/'go-check-new'
        self.marker = self.ops/'BTA102-track-b-go-attempt.json'
        self.dmarker = self.ops/'BTA102-track-b-directory-attempt.json'
        self.dmarker.write_text(json.dumps({'state':'DIRECTORY_SUBMISSION_ATTEMPTED',
            'jobs':['TA1BSRC','TA1BDST'],'restore_job':9136,
            'image_sha256':self.sha,'no_retry':True}))
        self.entries = [dict(job=n,jobname=j,dsn=dsn,volume=vol,
                             entry='000000',attributes='02E2')
                        for (j,dsn,vol),n in zip((('TA1BSRC',g.SOURCE,'TSO003'),
                                                  ('TA1BDST',g.TARGET,'TSO002')),
                                                 (9151,9152))]
        (self.dlog/'directory-comparison.json').write_text(json.dumps({
            'source':self.entries[0], 'restored':self.entries[1],
            'status':'IEHLIST_DIRECTORY_MATCH_ONLY_NOT_EXECUTABLE_PROOF'}))
        for row in self.entries:
            folder=self.dlog/row['jobname'];folder.mkdir()
            (folder/'summary.txt').write_text('JOB '+str(row['job'])+' '+row['jobname']+'\nDIRLIST IEHLIST RC=0000\n')
            (folder/'report.txt').write_text('DIRECTORY:'+row['dsn'])
        self.checker=types.SimpleNamespace(parse_directory=lambda text,*,dsn,volser,member:{
            'member':'ICINT19','other_member_rows':0,'directory_dataset':dsn,
            'directory_volume':volser,'entry_point_hex':'000000','attributes_hex':'02E2'})
        def cmp(items):
            self.assertEqual(items,self.entries)
            return {'source':items[0], 'restored':items[1],
                    'status':'IEHLIST_DIRECTORY_MATCH_ONLY_NOT_EXECUTABLE_PROOF'}
        self.dir=types.SimpleNamespace(validate_job=lambda *args:None,compare=cmp)
        for name,val in {'ROOT':self.root,'OPS':self.ops,'TAPE':self.tape,
                         'SHA':self.sha,'DIRECTORY_LOG':self.dlog,
                         'DIRECTORY_MARKER':self.dmarker,'LOG':self.log,
                         'MARKER':self.marker}.items():
            p=patch.object(g,name,val);p.start();self.addCleanup(p.stop)
        p=patch.object(g,'helper',return_value=self.checker);p.start();self.addCleanup(p.stop)

    def test_actual_directory_receipts_accepted(self):
        g.verify_directory_receipts(self.dir)

    def test_directory_marker_missing(self):
        self.dmarker.unlink()
        with self.assertRaises(g.Halt):g.verify_directory_receipts(self.dir)

    def test_directory_marker_state_mismatch(self):
        r=json.loads(self.dmarker.read_text());r['state']='WRONG'
        self.dmarker.write_text(json.dumps(r))
        with self.assertRaisesRegex(g.Halt,'marker mismatch'):g.verify_directory_receipts(self.dir)

    def test_directory_marker_wrong_jobs(self):
        r=json.loads(self.dmarker.read_text());r['jobs']=['TA1BSRC']
        self.dmarker.write_text(json.dumps(r))
        with self.assertRaises(g.Halt):g.verify_directory_receipts(self.dir)

    def test_source_restored_record_forgery_detected(self):
        doc=self.dlog/'directory-comparison.json';s=json.loads(doc.read_text())
        s['restored']['entry']='000001';doc.write_text(json.dumps(s))
        with self.assertRaisesRegex(g.Halt,'contradicts'):g.verify_directory_receipts(self.dir)

    def test_directory_wrong_report_refused(self):
        bad=types.SimpleNamespace(validate_job=lambda *args: (_ for _ in ()).throw(g.Halt('wrong IEHLIST job')),
                                  compare=self.dir.compare)
        with self.assertRaisesRegex(g.Halt,'wrong IEHLIST'):g.verify_directory_receipts(bad)

    def test_directory_missing_report(self):
        (self.dlog/'TA1BDST/report.txt').unlink()
        with self.assertRaisesRegex(g.Halt,'missing/unsafe'):g.verify_directory_receipts(self.dir)

    def test_directory_symlink_refused(self):
        f=self.dlog/'TA1BDST/report.txt';f.unlink();f.symlink_to(self.dlog/'TA1BSRC/report.txt')
        with self.assertRaisesRegex(g.Halt,'missing/unsafe'):g.verify_directory_receipts(self.dir)

    def test_bta102_changed(self):
        self.tape.write_bytes(b'ALTERED TAPE')
        with self.assertRaisesRegex(g.Halt,'checksum changed'):g.verify_directory_receipts(self.dir)

    def test_bta102_symlink(self):
        self.tape.unlink();self.tape.symlink_to(self.dmarker)
        with self.assertRaisesRegex(g.Halt,'missing/unsafe'):g.verify_directory_receipts(self.dir)

    def fake_body(self):
        head='//* CANONICAL RESTORED GO SCALVEC\n'
        for s,p in zip(g.STEPS,g.PROGRAMS):
            head+=f'//{s:<8} EXEC PGM={p}\n'
            if p=='ICINT19':head+=f'//STEPLIB DD DSN={g.TARGET},DISP=SHR\n'
            if s=='C01A':head+='//SYSIN DD DSN=HERC02.BCPL.MR10KIT.TESTS(SCALVEC),DISP=SHR\n'
            head+='//SYSUT2 DD DSN=&&TEMP,DISP=(NEW,PASS)\n//*\n'
        return head

    def test_canonical_body_accepted(self):
        self.assertIn('HERC02.BCPL.TA1B.LOAD',g.job_body(types.SimpleNamespace(go_body=self.fake_body)))

    def test_source_steplib_rejected(self):
        old=self.fake_body().replace(g.TARGET,g.SOURCE)
        with self.assertRaises(g.Halt):g.job_body(types.SimpleNamespace(go_body=lambda:old))

    def test_only_two_restored_steplibs_rejected(self):
        old=self.fake_body().replace('//STEPLIB DD DSN='+g.TARGET+',DISP=SHR\n','',1)
        with self.assertRaises(g.Halt):g.job_body(types.SimpleNamespace(go_body=lambda:old))

    def test_extra_step_rejected(self):
        s=self.fake_body()+'//BADSTEP  EXEC PGM=IEFBR14\n'
        with self.assertRaises(g.Halt):g.job_body(types.SimpleNamespace(go_body=lambda:s))

    def test_permanent_output_rejected(self):
        s=self.fake_body().replace('DISP=(NEW,PASS)','DISP=(NEW,CATLG,DELETE)')
        with self.assertRaises(g.Halt):g.job_body(types.SimpleNamespace(go_body=lambda:s))

    def test_one_shot_marker_exclusive_and_private(self):
        g.begin_once();self.assertEqual(self.marker.stat().st_mode&0o777,0o600)
        self.assertEqual(json.loads(self.marker.read_text())['target'],g.TARGET)
        with self.assertRaises(FileExistsError):g.begin_once()

    def make_report(self,job=9160):
        report=f'20:00:00 JOB {job} $HASP373 {g.JOBNAME} STARTED\n'
        for step,program in zip(g.STEPS,g.PROGRAMS):
            report+=f'20:00:01 JOB {job} {g.JOBNAME} {step} {program} RC=0000\n'
            report+=f'IEF142I {g.JOBNAME} {step} - STEP WAS EXECUTED - COND CODE 0000\n'
        report+='CODE=0\nCODE=0\nCODE=0\nRP: SCALAR 17 42\nRP: VECTOR 5 10 15 20\n'
        report+=f'20:00:02 JOB {job} $HASP395 {g.JOBNAME} ENDED\n'
        summary=f'JOB {job} {g.JOBNAME}\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n'
        summary+=''.join(f'{x} {p} RC=0000\n' for x,p in zip(g.STEPS,g.PROGRAMS))
        return report,summary

    def test_full_synthetic_jes_pass(self):
        report,summary=self.make_report()
        result=g.validate_execution(report,summary,9160)
        self.assertEqual(result['icint19_invocations'],3)
        self.assertEqual(result['rp_records'],list(g.GOLDEN))

    def test_wrong_golden_rejected(self):
        r,s=self.make_report()
        with self.assertRaisesRegex(g.Halt,'golden'):g.validate_execution(r.replace('VECTOR 5 10 15 20','VECTOR 5 10 15 21'),s,9160)

    def test_missing_step_rejected(self):
        r,s=self.make_report()
        s=s.replace('R01 ICINT19 RC=0000\n','')
        with self.assertRaisesRegex(g.Halt,'eight'):g.validate_execution(r,s,9160)

    def test_missing_ief142i_rejected(self):
        r,s=self.make_report()
        r=r.replace('IEF142I TA1BGO R01 - STEP WAS EXECUTED - COND CODE 0000\n','')
        with self.assertRaisesRegex(g.Halt,'IEF142I'):g.validate_execution(r,s,9160)

    def test_abend_rejected(self):
        r,s=self.make_report()
        with self.assertRaisesRegex(g.Halt,'ABEND'):g.validate_execution(r+'IEA995I  ABEND\n',s,9160)

    def test_nonzero_interpreted_code_rejected(self):
        r,s=self.make_report()
        with self.assertRaisesRegex(g.Halt,'CODE'):g.validate_execution(r.replace('CODE=0','CODE=4',1),s,9160)

    def test_mismatched_job_rejected(self):
        r,s=self.make_report()
        with self.assertRaises(g.Halt):g.validate_execution(r,s,9161)

    def test_duplicate_ief142i_rejected(self):
        r,s=self.make_report()
        r+='IEF142I TA1BGO R01 - STEP WAS EXECUTED - COND CODE 0000\n'
        with self.assertRaises(g.Halt):g.validate_execution(r,s,9160)

    def synthetic_live(self, *, branch='main', modified='', golden=None):
        expected = golden if golden is not None else g.GOLDEN
        path = self.root/'mr10-kit-compiler/tests/00-regression-panel/data-movement'
        path.mkdir(parents=True)
        (path/'scalar-vector.expected').write_text('\n'.join(expected)+'\n')
        class Directory:
            JOBS=(('TA1BSRC', g.SOURCE, 'TSO003'),('TA1BDST',g.TARGET,'TSO002'))
            def __init__(self): self.stated=[];self.listed=[]
            def stat_contract(self,s,dsn,vol):self.stated.append((dsn,vol))
            def check_list(self,s,dsn):self.listed.append(dsn)
            def verify_receipt(self):pass
            def live_preflight(self,*args):raise AssertionError('must not reuse directory submission guard')
        directory=Directory()
        def checked(argv,name,folder):
            if name=='git-branch':return branch+'\n'
            if name=='git-go-guard':return modified
            if name.startswith(('stat-','members-')):return 'MOCK MVS OUTPUT'
            raise AssertionError(argv)
        preflight=types.SimpleNamespace(checked=checked)
        contract=types.SimpleNamespace(validate_static=lambda:None,go_body=self.fake_body)
        return directory,preflight,contract

    def test_live_go_preflight_follows_completed_directory(self):
        d,p,c=self.synthetic_live()
        with patch.object(g,'verify_directory_receipts') as verify:
            body=g.live_preflight(d,p,c,self.ops)
        self.assertEqual(body,self.fake_body())
        self.assertEqual(d.stated,[(g.SOURCE,'TSO003'),(g.TARGET,'TSO002')])
        self.assertEqual(d.listed,[g.SOURCE,g.TARGET]);verify.assert_called_once_with(d)

    def test_live_go_preflight_rejects_wrong_branch(self):
        d,p,c=self.synthetic_live(branch='topic-branch')
        with self.assertRaisesRegex(g.Halt,'main'):g.live_preflight(d,p,c,self.ops)

    def test_live_go_preflight_rejects_modified_sources(self):
        d,p,c=self.synthetic_live(modified=' M script')
        with self.assertRaisesRegex(g.Halt,'modified'):g.live_preflight(d,p,c,self.ops)

    def test_live_go_preflight_rejects_drifted_golden(self):
        d,p,c=self.synthetic_live(golden=('RP: SCALAR 17 42','RP: VECTOR 5 10 15 21'))
        with patch.object(g,'verify_directory_receipts'):
            with self.assertRaisesRegex(g.Halt,'expected output changed'):
                g.live_preflight(d,p,c,self.ops)

    def test_live_go_preflight_rejects_existing_go_marker(self):
        d,p,c=self.synthetic_live()
        self.marker.write_text('previous attempt')
        with patch.object(g,'verify_directory_receipts'):
            with self.assertRaisesRegex(g.Halt,'already attempted'):
                g.live_preflight(d,p,c,self.ops)

    def test_default_preflight_does_not_submit(self):
        self.log.mkdir(mode=0o700)
        with patch.object(g,'helper',return_value=Mock()), \
             patch.object(g,'live_preflight',return_value=self.fake_body()), \
             patch.object(g,'begin_once') as marker, \
             patch.object(g,'submit_once') as submit, \
             patch.object(g,'LOG',self.ops/'unused-evidence'), \
             patch.object(g.sys,'stdout',io.StringIO()):
            self.assertEqual(g.operation(run=False),0)
        marker.assert_not_called();submit.assert_not_called()
        self.assertFalse(self.marker.exists())

    def test_authorization_denial_has_no_marker(self):
        with patch.object(g,'helper',return_value=Mock()), \
             patch.object(g,'live_preflight',return_value=self.fake_body()), \
             patch.object(g.sys.stdin,'isatty',return_value=True), \
             patch('builtins.input',return_value='NOT AUTHORIZED'), \
             patch.object(g.sys,'stdout',io.StringIO()), \
             patch.object(g,'submit_once') as submit:
            with self.assertRaisesRegex(g.Halt,'GO not explicitly confirmed'):
                g.operation(run=True)
        self.assertFalse(self.marker.exists());submit.assert_not_called()

    def test_one_shot_mock_submission(self):
        core=types.SimpleNamespace(load_config=lambda:{'mvs':{'hlq':'HERC02'}})
        body=self.fake_body()
        with patch.object(g,'helper',side_effect=[Mock(),Mock(),Mock(),core]), \
             patch.object(g,'live_preflight',return_value=body), \
             patch.object(g.sys.stdin,'isatty',return_value=True), \
             patch('builtins.input',return_value='RUN RESTORED ICINT19 SCALVEC'), \
             patch.object(g,'submit_once',return_value={'job':9160}) as submit, \
             patch.object(g,'verify_directory_receipts'), \
             patch.object(g.sys,'stdout',io.StringIO()):
            self.assertEqual(g.operation(run=True),0)
        submit.assert_called_once();self.assertTrue(self.marker.exists())


if __name__=='__main__':unittest.main(verbosity=2)
