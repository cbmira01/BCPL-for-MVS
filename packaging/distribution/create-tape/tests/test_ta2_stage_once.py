from __future__ import annotations
import copy
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock,patch

ROOT=Path(__file__).resolve().parents[4]
SCRIPT=ROOT/'packaging/distribution/create-tape/scripts/ta2-stage-once'
loader=importlib.machinery.SourceFileLoader('ta2_stage_once_test',str(SCRIPT))
spec=importlib.util.spec_from_loader(loader.name,loader)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class StagingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'workarea')
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/'workarea').mkdir()
        self.pack=self.root/'packaging/distribution/create-tape'
        self.pack.mkdir(parents=True)
        self.proposal=json.loads((ROOT/'packaging/distribution/create-tape/ta2-stage-space-proposal-20261119.json').read_text())
        self.rdir=self.root/'workarea/ta2-stage-readiness/20261119T210718Z-18180'
        self.rdir.mkdir(parents=True)
        self.ops=self.root/'workarea/ta2-stage-operations'
        self.data={
          'readiness.json':b'',
          'source-stat.txt':b'RC=0\nSOURCE REPORT\n',
          'catalog-report.txt':b'ALL ABSENT\n',
          'vtoc-report.txt':b'IEHLIST VTOC ON TSO002\n'
        }
        self.receipt={'status':'READ-ONLY MVS CHECK PASS; STAGING WRITE NOT AUTHORIZED',
           'allocation_evidence':self.proposal['allocation_evidence'],
           'volume':'TSO002','staging_datasets':18,'selected_members':127,
           'primary_tracks':645,'secondary_tracks':65,'requested_total_tracks':710,
           'reported_free_tracks':16045,'format1_datasets':30,'directory_blocks':149,
           'mvs_jobs':{'catalog_job':10,'vtoc_job':11}}
        self.data['readiness.json']=(json.dumps(self.receipt)+'\n').encode()
        self.save_data()
        (self.pack/'ta2-stage-space-proposal-20261119.json').write_text(json.dumps(self.proposal)+'\n')
        ps=[patch.object(mod,'ROOT',self.root),patch.object(mod,'PROPOSAL',self.pack/'ta2-stage-space-proposal-20261119.json'),patch.object(mod,'APPROVAL',self.pack/'ta2-stage-write-approval.json'),patch.object(mod,'BASE',self.root/'workarea/ta2-stage-readiness'),patch.object(mod,'OPERATIONS',self.ops),patch.object(mod,'ATTEMPT',self.ops/'TA2STG-TSO002-attempt.json')]
        for p in ps:p.start();self.addCleanup(p.stop)

    def save_data(self):
        for k,v in self.data.items():(self.rdir/k).write_bytes(v)
        (self.rdir/'SHA256SUMS').write_text(''.join(mod.digest(self.data[k])+'  '+k+'\n' for k in sorted(self.data)))

    def read(self):
        return mod.read_readiness(self.rdir,self.proposal)

    def test_all_18_proposed_triples_exact_and_budget(self):
        p,h=mod.read_proposal()
        self.assertEqual([r['sequence'] for r in p['targets']],list(range(3,21)))
        self.assertEqual(sum(r['primary_tracks'] for r in p['targets']),645)
        self.assertEqual(sum(r['secondary_tracks'] for r in p['targets']),65)
        self.assertEqual(len(h),64)
        self.assertEqual(p['targets'][2],{'sequence':5,'primary_tracks':176,'secondary_tracks':16,'directory_blocks':7})
        self.assertEqual(p['targets'][3],{'sequence':6,'primary_tracks':110,'secondary_tracks':10,'directory_blocks':13})

    def test_proposal_total_tamper(self):
        x=copy.deepcopy(self.proposal);x['targets'][0]['primary_tracks']+=1
        mod.PROPOSAL.write_text(json.dumps(x))
        with self.assertRaisesRegex(mod.Refusal,'18 exact'):mod.read_proposal()

    def test_proposal_extra_member(self):
        x=copy.deepcopy(self.proposal);x['selected_members']=128
        mod.PROPOSAL.write_text(json.dumps(x))
        with self.assertRaisesRegex(mod.Refusal,'fixed'):mod.read_proposal()

    def test_proposal_volume_change(self):
        x=copy.deepcopy(self.proposal);x['volume']='TSO003'
        mod.PROPOSAL.write_text(json.dumps(x))
        with self.assertRaises(mod.Refusal):mod.read_proposal()

    def test_readiness_pinned_success(self):
        receipt,data,hash_=self.read()
        self.assertEqual(receipt['format1_datasets'],30)
        self.assertEqual(hash_,mod.digest(self.data['readiness.json']))
        self.assertEqual(set(data),mod.READINESS_FILES)

    def test_readiness_has_wrong_path(self):
        x=copy.deepcopy(self.proposal);x['readiness_evidence']='workarea/ta2-stage-readiness/20260101T000000Z-1'
        with self.assertRaises(mod.Refusal):mod.read_readiness(self.rdir,x)

    def test_readiness_extra_file(self):
        (self.rdir/'other.txt').write_text('surprise')
        with self.assertRaisesRegex(mod.Refusal,'extra'):self.read()

    def test_readiness_missing_file(self):
        (self.rdir/'vtoc-report.txt').unlink()
        with self.assertRaises(mod.Refusal):self.read()

    def test_readiness_symlink(self):
        (self.rdir/'vtoc-report.txt').unlink()
        (self.rdir/'vtoc-report.txt').symlink_to(self.rdir/'source-stat.txt')
        with self.assertRaises(mod.Refusal):self.read()

    def test_readiness_hash_tamper(self):
        (self.rdir/'catalog-report.txt').write_text('CATALOGED')
        with self.assertRaisesRegex(mod.Refusal,'SHA256'):self.read()

    def test_duplicate_checksum_record(self):
        with (self.rdir/'SHA256SUMS').open('a') as f:f.write(mod.digest(b'X')+'  source-stat.txt\n')
        with self.assertRaises(mod.Refusal):self.read()

    def test_invalid_receipt_target_free(self):
        self.receipt['reported_free_tracks']=16044
        self.data['readiness.json']=json.dumps(self.receipt).encode();self.save_data()
        with self.assertRaises(mod.Refusal):self.read()

    def test_invalid_receipt_member_count(self):
        self.receipt['selected_members']=126
        self.data['readiness.json']=json.dumps(self.receipt).encode();self.save_data()
        with self.assertRaises(mod.Refusal):self.read()

    def test_invalid_receipt_mvs_jobs(self):
        self.receipt['mvs_jobs']={'catalog_job':11,'vtoc_job':11}
        self.data['readiness.json']=json.dumps(self.receipt).encode();self.save_data()
        with self.assertRaises(mod.Refusal):self.read()

    def test_invalid_receipt_source_rc(self):
        self.data['source-stat.txt']=b'RC=12\nERROR\n';self.save_data()
        with self.assertRaises(mod.Refusal):self.read()

    def test_readiness_parent_link(self):
        self.rdir.rename(self.rdir.parent/'old')
        self.rdir.symlink_to(self.rdir.parent/'old',target_is_directory=True)
        with self.assertRaises(mod.Refusal):self.read()

    def test_mvs_write_unapproved_refuses(self):
        with self.assertRaisesRegex(mod.Refusal,'not approved'):mod.read_approval('a'*64,'b'*64)

    def test_mvs_write_forged_local_approval_refuses(self):
        mod.APPROVAL.write_text('{}')
        with patch.object(mod,'git_original',side_effect=mod.Refusal('not committed on main')):
            with self.assertRaisesRegex(mod.Refusal,'not committed'):mod.read_approval('a'*64,'b'*64)

    def test_approval_exact_two_hashes(self):
        p,r='a'*64,'b'*64
        a={'status':'OWNER_APPROVED_ONE_SHOT_STAGING','volume':'TSO002',
           'approval_scope':'18_NEW_PDS_IEBCOPY_ONLY','proposal_sha256':p,'readiness_sha256':r,
           'readiness_evidence':self.proposal['readiness_evidence'],'no_retry':True}
        mod.APPROVAL.write_text(json.dumps(a))
        with patch.object(mod,'git_original',return_value=mod.APPROVAL.read_bytes()):
            self.assertEqual(mod.read_approval(p,r),a)
            with self.assertRaises(mod.Refusal):mod.read_approval('c'*64,r)
            with self.assertRaises(mod.Refusal):mod.read_approval(p,'c'*64)

    def test_approval_cannot_approve_different_volume(self):
        a={'status':'OWNER_APPROVED_ONE_SHOT_STAGING','volume':'TSO003',
           'approval_scope':'18_NEW_PDS_IEBCOPY_ONLY','proposal_sha256':'a'*64,'readiness_sha256':'b'*64,
           'readiness_evidence':self.proposal['readiness_evidence'],'no_retry':True}
        mod.APPROVAL.write_text(json.dumps(a))
        with patch.object(mod,'git_original',return_value=mod.APPROVAL.read_bytes()):
            with self.assertRaises(mod.Refusal):mod.read_approval('a'*64,'b'*64)

    def test_approval_tracking_git_checks(self):
        mod.APPROVAL.write_text('approved')
        responses=[SimpleNamespace(returncode=0,stdout='main\n'),SimpleNamespace(returncode=0,stdout='abc\n'),SimpleNamespace(returncode=0,stdout='abc\n'),SimpleNamespace(returncode=0,stdout=''),SimpleNamespace(returncode=0,stdout=b'approved')]
        with patch.object(mod.subprocess,'run',side_effect=responses):
            self.assertEqual(mod.git_original(mod.APPROVAL),b'approved')

    def test_approval_tracking_local_main_moved(self):
        mod.APPROVAL.write_text('approved')
        responses=[SimpleNamespace(returncode=0,stdout='main\n'),SimpleNamespace(returncode=0,stdout='abc\n'),SimpleNamespace(returncode=0,stdout='xyz\n')]
        with patch.object(mod.subprocess,'run',side_effect=responses):
            with self.assertRaisesRegex(mod.Refusal,'match'):mod.git_original(mod.APPROVAL)

    def test_job_deck_no_write_from_bad_body(self):
        with self.assertRaises(mod.Refusal):mod.job_deck(None,{},'//DRAFT\n')

    def test_job_deck_exact_body_and_no_passthrough(self):
        body='//* TA.2 DRAFT: NOT APPROVED FOR MVS SUBMISSION.\n'+(' SELECT MEMBER=(ABC)\n'*127)+('//S0003 EXEC PGM=IEBCOPY\n'*18)+'//\n'
        core=SimpleNamespace(authenticated_job_card=lambda *a,**k:['//TA2STAGE JOB (BCPL),\'STAGE\''])
        deck=mod.job_deck(core,{},body)
        self.assertIn('TA.2 OWNER-APPROVED',deck)
        self.assertNotIn('NOT APPROVED',deck)
        self.assertEqual(deck.count(' SELECT MEMBER='),127)

    def test_job_deck_jcl_column_width(self):
        body='//* TA.2 DRAFT: NOT APPROVED FOR MVS SUBMISSION.\n'+(' SELECT MEMBER=(ABC)\n'*127)+('//S0003 EXEC PGM=IEBCOPY\n'*18)+'//\n'
        core=SimpleNamespace(authenticated_job_card=lambda *a,**k:['//'+'X'*89])
        with self.assertRaises(mod.Refusal):mod.job_deck(core,{},body)

    def test_attempt_file_one_shot(self):
        self.ops.mkdir()
        mod.arm_attempt({'state':'SUBMISSION_ATTEMPTED_NO_RETRY','no_retry':True})
        self.assertTrue(mod.ATTEMPT.exists())
        with self.assertRaisesRegex(mod.Refusal,'DO NOT RETRY'):mod.arm_attempt({})

    def test_job_mvs_success_all_18(self):
        steps=[f'S{i:04d}' for i in range(3,21)]
        summary='JOB 4321 TA2STAGE\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n' + ''.join(f'{s} IEBCOPY RC=0000\n' for s in steps)
        report=''.join(f'IEF142I TA2STAGE {s} - STEP WAS EXECUTED - COND CODE 0000\n' for s in steps)
        x=mod.validate_job(4321,summary,report)
        self.assertEqual(x['step_count'],18)
        self.assertIn('AUDIT_PENDING',x['status'])

    def test_job_mvs_nonzero_rc(self):
        steps=[f'S{i:04d}' for i in range(3,21)]
        summary='JOB 4321 TA2STAGE\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n' + ''.join(f'{s} IEBCOPY RC={"0008" if i==5 else "0000"}\n' for i,s in enumerate(steps))
        report=''.join(f'IEF142I TA2STAGE {s} - STEP WAS EXECUTED - COND CODE 0000\n' for s in steps)
        with self.assertRaises(mod.Refusal):mod.validate_job(4321,summary,report)

    def test_job_mvs_missing_step(self):
        steps=[f'S{i:04d}' for i in range(3,20)]
        summary='JOB 4321 TA2STAGE\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n' + ''.join(f'{s} IEBCOPY RC=0000\n' for s in steps)
        report=''.join(f'IEF142I TA2STAGE {s} - STEP WAS EXECUTED - COND CODE 0000\n' for s in steps)
        with self.assertRaises(mod.Refusal):mod.validate_job(4321,summary,report)

    def test_job_mvs_duplicate_message(self):
        steps=[f'S{i:04d}' for i in range(3,21)]
        summary='JOB 4321 TA2STAGE\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n' + ''.join(f'{s} IEBCOPY RC=0000\n' for s in steps)
        report=''.join(f'IEF142I TA2STAGE {s} - STEP WAS EXECUTED - COND CODE 0000\n' for s in steps)+'IEF142I TA2STAGE S0003 - STEP WAS EXECUTED - COND CODE 0000\n'
        with self.assertRaises(mod.Refusal):mod.validate_job(4321,summary,report)

    def test_job_mvs_ief_abend(self):
        steps=[f'S{i:04d}' for i in range(3,21)]
        summary='JOB 4321 TA2STAGE\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n' + ''.join(f'{s} IEBCOPY RC=0000\n' for s in steps)
        report=''.join(f'IEF142I TA2STAGE {s} - STEP WAS EXECUTED - COND CODE 0000\n' for s in steps)+'IEF450I TA2STAGE ABEND\n'
        with self.assertRaises(mod.Refusal):mod.validate_job(4321,summary,report)

    def test_fresh_readonly_checks_use_readiness(self):
        f=self.ops/'fresh';f.mkdir(parents=True)
        ready=SimpleNamespace(inquire_source=Mock(return_value='sha'))
        vtoc={'format1_names_sha256':'h','format1_datasets_seen':30,'iehlist_reported_free_total_tracks':16045}
        core=SimpleNamespace(load_config=Mock(return_value={'mvs':{'hlq':'HERC02'}}),require_reader_ready=Mock())
        def inquire(core,conf,folder,names,volume):
            self.assertEqual(volume,'TSO002')
            (folder/'catalog-report.txt').write_text('NOT IN CATALOG')
            (folder/'vtoc-report.txt').write_text('VTOC')
            return {'catalog_job':2,'vtoc_job':3}
        target=SimpleNamespace(inquire=inquire,catalog_absence=Mock())
        review=SimpleNamespace(inspect_vtoc=lambda *args:vtoc)
        mods={'ready':ready,'core':core,'target':target,'review':review,'stageplan':object(), 'capacity':object(), 'source':object()}
        x=mod.fresh_check(f,mods,{}, {'reported_free_tracks':16045}, {},[],[],object(),vtoc)
        self.assertEqual(x['reported_free_tracks'],16045)
        self.assertEqual(x['mvs_jobs']['vtoc_job'],3)

    def test_fresh_readonly_rejects_vtoc_drift(self):
        f=self.ops/'fresh';f.mkdir(parents=True)
        vtoc={'format1_names_sha256':'not-h','format1_datasets_seen':30,'iehlist_reported_free_total_tracks':16045}
        core=SimpleNamespace(load_config=lambda : {'mvs':{'hlq':'HERC02'}},require_reader_ready=lambda *a:None)
        def inquire(*args):
            (f/'catalog-report.txt').write_text('NOT IN CATALOG')
            (f/'vtoc-report.txt').write_text('VTOC')
            return {'catalog_job':2,'vtoc_job':3}
        mods={'ready':SimpleNamespace(inquire_source=lambda *args:'sha'), 'core':core,'target':SimpleNamespace(inquire=inquire,catalog_absence=lambda *a:None),'review':SimpleNamespace(inspect_vtoc=lambda *args:vtoc),'stageplan':object(),'capacity':object(),'source':object()}
        with self.assertRaisesRegex(mod.Refusal,'drift'):mod.fresh_check(f,mods,{}, {'reported_free_tracks':16045}, {},[],[],object(),{'format1_names_sha256':'h'})

    def test_default_never_calls_fresh_mvs(self):
        # The normal path verifies original run & uses source-only modules; no MVS calls.
        checked,sizing,saved,items,names,source,body={}, {},{},[],[],object(),'BODY'
        with patch.object(mod,'modules',return_value={}), patch.object(mod,'replay',return_value=(checked,sizing,saved,items,names,source,body)),patch.object(mod,'fresh_check') as fresh:
            args=SimpleNamespace(readiness_evidence=self.root/self.proposal['readiness_evidence'],live=False,run=False)
            self.assertEqual(mod.operation(args),0)
            fresh.assert_not_called()

    def test_run_without_approval_fails_before_mvs(self):
        checked,sizing,saved,items,names,source,body={}, {},{},[],[],object(),'BODY'
        with patch.object(mod,'modules',return_value={}), patch.object(mod,'replay',return_value=(checked,sizing,saved,items,names,source,body)),patch.object(mod,'fresh_check') as fresh:
            args=SimpleNamespace(readiness_evidence=self.root/self.proposal['readiness_evidence'],live=True,run=True)
            with self.assertRaisesRegex(mod.Refusal,'not approved'):mod.operation(args)
            fresh.assert_not_called()

if __name__=='__main__':unittest.main()
