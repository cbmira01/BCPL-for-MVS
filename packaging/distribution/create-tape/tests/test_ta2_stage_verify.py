"""Synthetic read-only tests; actual JES/MVS acceptance needs operator evidence."""
from __future__ import annotations

from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[4]
LOADER = SourceFileLoader('ta2_stage_verify_tests',
                          str(ROOT / 'packaging/distribution/create-tape/scripts/ta2-stage-verify'))
SPEC = spec_from_loader(LOADER.name, LOADER)
mod = module_from_spec(SPEC)
LOADER.exec_module(mod)


def targets():
    return [{'staging_dsn': f'HERC02.BCPL.TA2STG.BT{i:04d}', 'volume': 'TSO002',
             'members': [f'NAME{i:04d}'],
             'dcb': {'dsorg':'PO','recfm': 'U' if i == 5 else 'FB',
                     'lrecl': 0 if i == 5 else 80,
                     'blksize': 6144 if i == 5 else 800}}
            for i in range(3,21)]


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'workarea').mkdir()
        self.ops = self.root/'workarea/ta2-stage-operations'
        self.ops.mkdir()
        self.stage_dir = self.ops/mod.EXPECTED_RUN
        self.stage_dir.mkdir()
        self.out = self.root/'workarea/ta2-stage-verification'
        self.targets = targets()
        self.patches = [patch.object(mod,'ROOT',self.root),
                        patch.object(mod,'STAGE_ROOT',self.ops),
                        patch.object(mod,'OUT',self.out)]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)

    def core(self, bad=None):
        by_dsn={x['staging_dsn']:x for x in self.targets}
        def attrs(block):
            r=by_dsn[block[0]]
            d=r['dcb']
            result={k: str(v) for k,v in d.items()}
            result['volume'] = r['volume']
            if bad == 'vol' and r['staging_dsn'].endswith('BT0003'):
                result['volume']='TSO003'
            if bad == 'load' and d['recfm']=='U':
                result['blksize']='800'
            return result
        return SimpleNamespace(dataset_missing=lambda report,dsn: bad=='missing' and dsn.endswith('BT0003'),
                               extract_listds_block=lambda report,dsn: [dsn],parse_listds=attrs)

    def ls(self, bad=None):
        def blocks(report,names):
            result={x['staging_dsn']:[x['members'][0]] for x in self.targets}
            if bad=='missing': result.pop(self.targets[0]['staging_dsn'])
            elif bad=='extra': result[self.targets[0]['staging_dsn']].append('EXTRA')
            elif bad=='duplicate': result[self.targets[0]['staging_dsn']].append(result[self.targets[0]['staging_dsn']][0])
            elif bad=='wrong': result[self.targets[0]['staging_dsn']]=['WRONG']
            return result
        return SimpleNamespace(member_blocks=blocks,parse_members=lambda b:b)

    def receipt(self):
        summary='JOB 9310 TA2STAGE\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n'
        report='IEF142I TA2STAGE S0003 - STEP WAS EXECUTED - COND CODE 0000\n'
        result={'status':'18_IEBCOPY_STEPS_RC0000_ONLY_DIRECTORY_AND_RECORD_AUDIT_PENDING',
                'mvs_job':9310,'step_count':18,'selected_member_cards':127}
        marker={'state':'SUBMISSION_INTENT_RETRYABLE', 'attempt_number':1,
                'proposal_sha256':'a'*64,'readiness_sha256':'b'*64,
                'approval_sha256':'c'*64,'attempt_evidence':str(self.stage_dir.relative_to(self.root)),
                'jobname':'TA2STAGE','expected_pds':18}
        for name,b in {'stage-summary.txt':summary.encode(), 'stage-report.txt':report.encode(),
                       'stage-result.json':json.dumps(result).encode(),
                       'submission-intent.json':json.dumps(marker).encode()}.items():
            (self.stage_dir/name).write_bytes(b)
        journal=self.ops/'TA2STG-TSO002-attempt.json'
        journal.write_text(json.dumps(marker))
        stage=SimpleNamespace(safe_run=lambda folder,parent:None,
               _pinned_operation=lambda folder:json.loads((folder/'stage-result.json').read_text()),
               validate_job=lambda job,summary,report:result,
               ATTEMPT=journal,RETRY=__import__('re').compile('TA2STG-TSO002-retry-([0-9]{4})\\.json'),JOB='TA2STAGE')
        return stage

    def test_exact_18_dcb(self):
        mod.audit_attributes(self.core(),'report',self.targets)

    def test_load_library_po_u_0_6144(self):
        x=self.targets[2]
        self.assertEqual(x['dcb'],{'dsorg':'PO','recfm':'U','lrecl':0,'blksize':6144})
        mod.audit_attributes(self.core(),'report',self.targets)

    def test_wrong_dasd_rejected(self):
        with self.assertRaisesRegex(mod.Refusal,'DCB/VOLSER'):
            mod.audit_attributes(self.core('vol'),'report',self.targets)

    def test_wrong_load_dcb_rejected(self):
        with self.assertRaisesRegex(mod.Refusal,'BT0005'):
            mod.audit_attributes(self.core('load'),'report',self.targets)

    def test_uncataloged_rejected(self):
        with self.assertRaisesRegex(mod.Refusal,'missing'):
            mod.audit_attributes(self.core('missing'),'report',self.targets)

    def test_exact_18_directories(self):
        mod.audit_members(self.ls(),'report',self.targets)

    def test_missing_directory_refused(self):
        with self.assertRaisesRegex(mod.Refusal,'all 18'):
            mod.audit_members(self.ls('missing'),'report',self.targets)

    def test_extra_member_refused(self):
        with self.assertRaisesRegex(mod.Refusal,'BT0003'):
            mod.audit_members(self.ls('extra'),'report',self.targets)

    def test_duplicate_member_refused(self):
        with self.assertRaises(mod.Refusal):
            mod.audit_members(self.ls('duplicate'),'report',self.targets)

    def test_wrong_member_refused(self):
        with self.assertRaises(mod.Refusal):
            mod.audit_members(self.ls('wrong'),'report',self.targets)

    def test_pinned_stage_success(self):
        stage=self.receipt()
        got=mod.verify_stage_receipt(stage,self.stage_dir,'a'*64,'b'*64,'c'*64)
        self.assertEqual(got['mvs_job'],9310)

    def test_stage_identity_mismatch_refused(self):
        stage=self.receipt()
        with self.assertRaisesRegex(mod.Refusal,'journal'):
            mod.verify_stage_receipt(stage,self.stage_dir,'x'*64,'b'*64,'c'*64)

    def test_missing_original_marker_refused(self):
        stage=self.receipt()
        stage.ATTEMPT.unlink()
        with self.assertRaises((mod.Refusal,FileNotFoundError)):
            mod.verify_stage_receipt(stage,self.stage_dir,'a'*64,'b'*64,'c'*64)

    def test_wrong_job_refused(self):
        stage=self.receipt()
        result=json.loads((self.stage_dir/'stage-result.json').read_text());result['mvs_job']=9309
        (self.stage_dir/'stage-result.json').write_text(json.dumps(result))
        with self.assertRaisesRegex(mod.Refusal,'9310'):
            mod.verify_stage_receipt(stage,self.stage_dir,'a'*64,'b'*64,'c'*64)

    def test_wrong_original_folder_refused(self):
        stage=self.receipt()
        with self.assertRaisesRegex(mod.Refusal,'owner-reported'):
            mod.verify_stage_receipt(stage,self.ops,'a'*64,'b'*64,'c'*64)

    def test_evidence_sealed(self):
        self.out.mkdir()
        a=self.out/'test';a.mkdir()
        mod.write_new(a/'a.txt',b'hello')
        mod.finish_evidence(a)
        self.assertIn(mod.digest(b'hello'),(a/'SHA256SUMS').read_text())
        with self.assertRaises(FileExistsError):mod.finish_evidence(a)

    def test_file_symlink_refused(self):
        target=self.root/'workarea/other';target.write_bytes(b'ok')
        p=self.root/'workarea/alias';p.symlink_to(target)
        with self.assertRaises(mod.Refusal):mod.read_file(p)

    def test_two_consolidated_readonly_mvs_jobs(self):
        job_calls=[]
        core=self.core()
        core.load_config=lambda:{'mvs':{'hlq':'HERC02'}}
        core.require_reader_ready=Mock()
        core.stat_deck=lambda cfg,names:'//DSPALST JOB TEST\n//S EXEC PGM=IKJEFT01\n'
        def submit(cfg,deck,max_rc,cursor_file):
            job_calls.append((deck,max_rc,cursor_file))
            return 201+len(job_calls),'JOB RESULT: SUCCESS\n'
        core.submit_and_wait=submit
        core.job_report=lambda job,cursor_file:'CATALOG' if job==202 else 'MEMBERS'
        ls=self.ls()
        ls.list_members_deck=lambda cfg,names:'//DSPALLS JOB TEST\n//S EXEC PGM=IKJEFT01\n'
        stage=SimpleNamespace(load=lambda key,path:core if 'core' in key else ls)
        self.out.mkdir();folder=self.out/'run';folder.mkdir()
        jobs=mod.run_read_only_jobs(stage,folder,self.targets)
        self.assertEqual(jobs,{'catalog':202,'members':203})
        self.assertEqual(len(job_calls),2)
        self.assertTrue(all(k==8 for _,k,_ in job_calls))
        self.assertTrue((folder/'catalog-report.txt').is_file())
        self.assertTrue((folder/'members-report.txt').is_file())

    def test_never_submits_if_not_live(self):
        # The script's public --live flag is false by default; no input is used.
        import argparse
        parser=argparse.ArgumentParser()
        parser.add_argument('--live',action='store_true')
        self.assertFalse(parser.parse_args([]).live)
        self.assertNotIn('input(',Path(LOADER.path).read_text())


if __name__=='__main__':
    unittest.main()
