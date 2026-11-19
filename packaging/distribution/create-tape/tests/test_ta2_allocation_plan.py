"""TA.2 fail-closed staging SPACE proposal and saved MVS receipt tests."""
from __future__ import annotations
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / 'packaging/distribution/create-tape/scripts/ta2-allocation-plan'
loader = importlib.machinery.SourceFileLoader('ta2_allocation_plan_test', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class AllocationProposalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.work = self.root/'workarea'
        self.base = self.work/'ta2-target-review'
        self.run = self.base/'20261119T181059Z-17632'
        self.run.mkdir(parents=True)
        self.patch_root = patch.object(mod, 'ROOT', self.root)
        self.patch_base = patch.object(mod, 'REVIEW_BASE', self.base)
        self.patch_out = patch.object(mod, 'OUT', self.work/'ta2-allocation-plan')
        for p in (self.patch_root,self.patch_base,self.patch_out):
            p.start();self.addCleanup(p.stop)
        self.review = {
            'status':'PASS (catalog and formatted VTOC identity only)',
            'live_recheck':True, 'volume':'TSO002',
            'source_target_count':18, 'format1_datasets_seen':30,
            'fresh_vtoc_format1_datasets_seen':30,
            'staging_names_in_formatted_vtoc':0,
            'source_capacity_is_destination_free_space':False,
            'iehlist_reported_free_total_tracks':16045}
        self.set_review()
        self.rows=[];self.sources=[]
        for n in range(3,21):
            dcb={'dsorg':'PO','recfm':'U' if n==12 else 'FB',
                 'lrecl':0 if n==12 else 80,
                 'blksize':6144 if n==12 else 800}
            cnt=8 if n==20 else 7
            members=[f'M{i:07d}' for i in range(cnt)]
            src_dsn='HERC02.BCPL.S'+f'{n:03d}'
            self.rows.append({'sequence':n,'source_dsn':src_dsn,'dcb':dcb,'members':members})
            self.sources.append({'tape_sequence':n,'source_dsn':src_dsn,
                'source_dcb':dcb, 'selected_members':members,'selected_count':cnt,
                'source_tracks_allocated':25,'source_tracks_through_hwm':20,
                'source_directory_allocated':10,'source_directory_used':7})

    def set_review(self):
        for name,body in [('review.json',json.dumps(self.review,indent=2)+'\n'),
                          ('catalog-report.txt','18 missing\n'),
                          ('vtoc-report.txt','30 rows; TSO002\n')]:
            (self.run/name).write_text(body)
        self.seal()

    def seal(self):
        lines=''.join(hashlib.sha256((self.run/n).read_bytes()).hexdigest()+'  '+n+'\n'
                      for n in sorted(['review.json','catalog-report.txt','vtoc-report.txt']))
        (self.run/'SHA256SUMS').write_text(lines)

    def proposal(self):
        return mod.derive_targets(self.rows,self.sources,'a'*64,self.review,'TSO002')

    def test_source_bounded_allocation_exact(self):
        allocation,report=self.proposal()
        self.assertEqual((len(allocation['targets']),report['primary_tracks_total'],
                          report['secondary_tracks_total']), (18,18*29,18*3))
        self.assertEqual(report['total_primary_secondary_budget'],18*32)
        self.assertEqual(report['unused_reported_tracks_after_budget'],16045-576)
        self.assertEqual(report['directory_blocks_total'],18*13)
        self.assertEqual(allocation['targets'][9]['dsn'], 'HERC02.BCPL.TA2STG.BT0012')
        self.assertEqual(allocation['targets'][9]['space']['directory_blocks'],13)
        self.assertNotIn('members',allocation['targets'][9])
        self.assertEqual(allocation['staging_namespace'],'HERC02.BCPL.TA2STG')

    def test_127_selections_not_changed(self):
        allocation,report=self.proposal()
        self.assertEqual(sum(x['selected_members'] for x in report['sources']),127)
        self.assertEqual([x['sequence'] for x in allocation['targets']],list(range(3,21)))

    def test_underallocated_volume_refuses(self):
        self.review['iehlist_reported_free_total_tracks']=100
        with self.assertRaisesRegex(mod.Refusal, '50%'):
            self.proposal()

    def test_budget_includes_possible_secondary_extents(self):
        self.review['iehlist_reported_free_total_tracks']=1100
        with self.assertRaisesRegex(mod.Refusal, '50%'):
            self.proposal()

    def test_exact_budget_boundary(self):
        self.review['iehlist_reported_free_total_tracks']=1152
        self.proposal()
        self.review['iehlist_reported_free_total_tracks']=1151
        with self.assertRaises(mod.Refusal):self.proposal()

    def test_primary_tracks_source_allocated_not_hwm(self):
        self.sources[0]['source_tracks_through_hwm']=1
        allocation,_=self.proposal()
        self.assertEqual(allocation['targets'][0]['space']['primary_tracks'],29)

    def test_hwm_larger_than_allocation_refused(self):
        self.sources[3]['source_tracks_through_hwm']=99
        with self.assertRaisesRegex(mod.Refusal, 'invalid source allocation'):
            self.proposal()

    def test_zero_source_allocation_refused(self):
        self.sources[3]['source_tracks_allocated']=0
        with self.assertRaises(mod.Refusal):self.proposal()

    def test_directory_source_allocation_refused(self):
        self.sources[3]['source_directory_allocated']=0
        with self.assertRaises(mod.Refusal):self.proposal()

    def test_directory_used_larger_than_allocated_refused(self):
        self.sources[3]['source_directory_used']=11
        with self.assertRaises(mod.Refusal):self.proposal()

    def test_negative_tracks_refused(self):
        self.sources[3]['source_tracks_allocated']=-1
        with self.assertRaises(mod.Refusal):self.proposal()

    def test_float_tracks_refused(self):
        self.sources[3]['source_tracks_allocated']=25.5
        with self.assertRaises(mod.Refusal):self.proposal()

    def test_member_selection_drift_refused(self):
        self.sources[3]['selected_members'].append('OTHER')
        with self.assertRaisesRegex(mod.Refusal,'source/selection'):
            self.proposal()

    def test_dcb_drift_refused(self):
        self.sources[9]['source_dcb']={**self.sources[9]['source_dcb'],'recfm':'FB'}
        with self.assertRaisesRegex(mod.Refusal,'source/selection'):
            self.proposal()

    def test_source_sequence_drift_refused(self):
        self.sources[3]['tape_sequence']=19
        with self.assertRaises(mod.Refusal):self.proposal()

    def test_volume_drift_refused(self):
        self.review['volume']='TSO003'
        with self.assertRaises(mod.Refusal):self.proposal()

    def test_missing_free_tracks_refused(self):
        self.review['iehlist_reported_free_total_tracks']=None
        with self.assertRaises(mod.Refusal):self.proposal()

    def test_space_overflow_refused(self):
        self.sources[0]['source_tracks_allocated']=65535
        self.sources[0]['source_tracks_through_hwm']=65535
        with self.assertRaisesRegex(mod.Refusal,'exceeds limits'):
            self.proposal()

    def test_huge_directory_refused(self):
        self.sources[0]['source_directory_allocated']=60000
        with self.assertRaisesRegex(mod.Refusal,'exceeds limits'):
            self.proposal()

    def test_verified_review_receipt(self):
        review,data,pin=mod.read_review(self.run,'TSO002')
        self.assertEqual(review,self.review)
        self.assertEqual(len(data),3)
        self.assertEqual(pin, hashlib.sha256((self.run/'review.json').read_bytes()).hexdigest())

    def test_unverified_review_rejected(self):
        self.review['live_recheck']=False
        self.set_review()
        with self.assertRaisesRegex(mod.Refusal,'incomplete'):
            mod.read_review(self.run,'TSO002')

    def test_saved_vtoc_report_checksum_tampering(self):
        (self.run/'vtoc-report.txt').write_text('forged\n')
        with self.assertRaisesRegex(mod.Refusal,'checksum'):
            mod.read_review(self.run,'TSO002')

    def test_saved_json_checksum_tampering(self):
        (self.run/'review.json').write_text('{}')
        with self.assertRaisesRegex(mod.Refusal,'checksum'):
            mod.read_review(self.run,'TSO002')

    def test_failed_volume_probe_not_accepted(self):
        self.review['iehlist_reported_free_total_tracks']=None
        self.set_review()
        with self.assertRaisesRegex(mod.Refusal,'incomplete'):
            mod.read_review(self.run,'TSO002')

    def test_missing_checksum_refused(self):
        (self.run/'SHA256SUMS').unlink()
        with self.assertRaises(mod.Refusal):mod.read_review(self.run,'TSO002')

    def test_missing_raw_report_refused(self):
        (self.run/'vtoc-report.txt').unlink()
        with self.assertRaises(mod.Refusal):mod.read_review(self.run,'TSO002')

    def test_extra_report_refused(self):
        (self.run/'UNEXPECTED').write_text('x')
        with self.assertRaises(mod.Refusal):mod.read_review(self.run,'TSO002')

    def test_symlinked_report_refused(self):
        (self.run/'catalog-report.txt').unlink()
        (self.run/'catalog-report.txt').symlink_to(self.run/'review.json')
        with self.assertRaises(mod.Refusal):mod.read_review(self.run,'TSO002')

    def test_symlinked_run_refused(self):
        sibling=self.base/'20261119T181100Z-22222'
        sibling.symlink_to(self.run, target_is_directory=True)
        with self.assertRaises(mod.Refusal):mod.read_review(sibling,'TSO002')

    def test_untrusted_review_dir_refused(self):
        with self.assertRaises(mod.Refusal):mod.read_review(self.root,'TSO002')

    def saved_audit(self, *, drift=False, capacity_drift=False):
        review={**self.review,
                'original_target_evidence':'workarea/ta2-target-preflight/20261119T170234Z-17334',
                'stage_worksheet_sha256':'a'*64,
                'original_target_summary_sha256':hashlib.sha256(b'{"stage_evidence":"workarea/ta2-stage-plan/20261119T155947Z-17087"}').hexdigest(),
                'format1_names_sha256':'a'*64,
                'source_allocated_tracks_total':450,
                'source_tracks_through_hwm_total':360,
                'source_directory_allocated_total':180}
        original={'summary.json':b'{"stage_evidence":"workarea/ta2-stage-plan/20261119T155947Z-17087"}'}
        stage=types.SimpleNamespace(
            read_stage_run=lambda *args:({'sources':self.sources},'a'*64,b'RC=0\n'),
            verify_history=lambda *args:None)
        target=types.SimpleNamespace(targets=lambda *args:[f'HERC02.BCPL.TA2STG.BT{n:04d}'
                                                            for n in range(3,21)],
            catalog_absence=lambda *args:None)
        validated={'format1_names_sha256':'a'*64, 'format1_datasets_seen':30,
                   'iehlist_reported_free_total_tracks':16045}
        fresh={**validated}
        if drift:
            fresh['format1_names_sha256']='f'*64
        if capacity_drift:
            fresh['iehlist_reported_free_total_tracks']=16044
        reviewer=types.SimpleNamespace(read_original=lambda *args:original,
            inspect_saved=lambda *args:validated,inspect_vtoc=lambda *args:fresh)
        return mod.audit_saved(review,{'vtoc-report.txt':b'MVS TSO002',
                                     'catalog-report.txt':b'CATALOG'},
               stage,target,reviewer,object(),{}, {},self.rows,'TSO002')

    def test_saved_audit_reconstructs_18_target_names(self):
        checked=self.saved_audit()
        self.assertEqual(len(checked['names']),18)
        self.assertEqual(checked['worksheet_sha'],'a'*64)

    def test_saved_audit_refuses_drifted_vtoc_inventory(self):
        with self.assertRaisesRegex(mod.Refusal,'VTOC inventory'):
            self.saved_audit(drift=True)

    def test_saved_audit_refuses_drifted_vtoc_free_tracks(self):
        with self.assertRaisesRegex(mod.Refusal,'VTOC inventory'):
            self.saved_audit(capacity_drift=True)

    def test_saved_audit_refuses_forged_source_capacity(self):
        self.sources[0]['source_tracks_allocated']=26
        with self.assertRaisesRegex(mod.Refusal,'source totals'):
            self.saved_audit()

    def fake_modules(self, *, source_drift=False, catalog_drift=False):
        """An executable synthetic main() harness; all MVS calls intercepted."""
        from unittest.mock import Mock
        canonical=Mock()
        canonical.load.side_effect=[{'phase':'design'}, {'mvs':{'hlq':'HERC02'}}]
        source=types.SimpleNamespace(core=lambda:canonical,expected_sources=lambda *args: self.rows)
        plan={'sources':self.sources,'source_evidence_directory':'workarea/src',
              'capacity_evidence_directory':'workarea/capacity'}
        stage=types.SimpleNamespace(
            read_stage_run=lambda *args:(plan,'a'*64,b'RC=0\n'),
            validate_worksheet=lambda *args:self.rows,
            validate_allocations=lambda proposal, pin, rows, dspal:self.assert_proposal(proposal),
            render_jcl=lambda *args:(' EXEC PGM=IEBCOPY\n'*18)+' SELECT MEMBER=(ONE)\n'*127)
        source_stat=Mock()
        if source_drift:
            source_stat.compare_current.side_effect=mod.Refusal('fresh source drift')
        target=Mock()
        target.targets.return_value=[f'HERC02.BCPL.TA2STG.BT{n:04d}' for n in range(3,21)]
        def inquire(core,config,directory,names,volume):
            (directory/'catalog-report.txt').write_text('MVS catalog: all missing\n')
            (directory/'vtoc-report.txt').write_text('MVS TSO002 30 rows 16045 free\n')
            if catalog_drift:
                raise mod.Refusal('catalog drift')
            return {'catalog_job': 111, 'vtoc_job': 112}
        target.inquire.side_effect=inquire
        reviewer=Mock()
        reviewer.read_original.return_value={'summary.json':b'{"stage_evidence":"workarea/ta2-stage-plan/20261119T155947Z-17087"}'}
        reviewer.inspect_vtoc.return_value={'format1_names_sha256':'a'*64,
                                           'iehlist_reported_free_total_tracks':16045}
        core=Mock()
        core.load_config.return_value={'mvs':{'hlq':'HERC02'}}
        capacity=Mock();src_review=Mock()
        return {'ta2_alloc_source':source, 'ta2_alloc_stage':stage,
                'ta2_alloc_capacity':capacity, 'ta2_alloc_src_review':src_review,
                'ta2_alloc_source_stat':source_stat, 'ta2_alloc_target':target,
                'ta2_alloc_review':reviewer, 'ta2_alloc_core':core}

    def assert_proposal(self, proposal):
        self.assertEqual(len(proposal['targets']),18)
        self.assertEqual(proposal['staging_namespace'],'HERC02.BCPL.TA2STG')
        return proposal['targets']

    def test_main_offline_never_invokes_mvs(self):
        modules=self.fake_modules()
        self.review.update({'original_target_evidence':'workarea/ta2-target-preflight/20261119T170234Z-17334',
                            'format1_names_sha256':'a'*64})
        self.set_review()
        with patch.object(mod,'load',side_effect=lambda name,path:modules[name]),\
             patch.object(mod,'audit_saved',return_value={'plan':{'sources':self.sources},
                           'names':[f'HERC02.BCPL.TA2STG.BT{n:04d}' for n in range(3,21)]}),\
             patch.object(mod,'ROOT',self.root):
            self.assertEqual(mod.main(['--target-review',str(self.run),'--volume','TSO002']),0)
        modules['ta2_alloc_core'].require_reader_ready.assert_not_called()
        modules['ta2_alloc_target'].inquire.assert_not_called()

    def test_main_live_replays_and_saves_draft(self):
        from unittest.mock import Mock
        self.review.update({'original_target_evidence':'workarea/ta2-target-preflight/20261119T170234Z-17334',
                            'format1_names_sha256':'a'*64})
        self.set_review()
        modules=self.fake_modules()
        receipt={'evidence_directory':'src'}
        modules['ta2_alloc_src_review'].inspect.return_value=receipt
        modules['ta2_alloc_source_stat'].read_capacity.return_value={'summary.json':b'{}'}
        modules['ta2_alloc_source_stat'].replay_capacity.return_value={'libraries':18}
        fake_completed=types.SimpleNamespace(returncode=0,stdout='MVS STAT',stderr='')
        with patch.object(mod,'load',side_effect=lambda name,path:modules[name]),\
             patch.object(mod,'audit_saved',return_value={'plan':{'sources':self.sources,
                            'source_evidence_directory':'workarea/src',
                            'capacity_evidence_directory':'workarea/capacity'},
                            'names':[f'HERC02.BCPL.TA2STG.BT{n:04d}' for n in range(3,21)]}),\
             patch.object(mod.subprocess,'run',return_value=fake_completed) as submitted:
            self.assertEqual(mod.main(['--target-review',str(self.run),'--volume','TSO002','--live']),0)
        submitted.assert_called_once()
        self.assertEqual(submitted.call_args.args[0], ['tools/datasets/dspal','stat'])
        self.assertTrue(submitted.call_args.kwargs['env']['TMPDIR'].startswith(str(self.work)))
        modules['ta2_alloc_target'].inquire.assert_called_once()
        created=list((self.work/'ta2-allocation-plan').glob('*/planning-review.json'))
        self.assertEqual(len(created),1)
        self.assertEqual(json.loads(created[0].read_text())['fresh_mvs_jobs'],
                         {'catalog_job':111,'vtoc_job':112})
        output=created[0].parent
        self.assertEqual(len(json.loads((output/'stage-allocations-proposed.json').read_text())['targets']),18)
        self.assertTrue((output/'stage-iebcopy-draft.jcl').is_file())
        self.assertTrue((output/'SHA256SUMS').is_file())

    def test_main_live_source_drift_never_attempts_target(self):
        self.review.update({'original_target_evidence':'workarea/ta2-target-preflight/20261119T170234Z-17334',
                            'format1_names_sha256':'a'*64})
        self.set_review()
        modules=self.fake_modules(source_drift=True)
        with patch.object(mod,'load',side_effect=lambda name,path:modules[name]),\
             patch.object(mod,'audit_saved',return_value={'plan':{'sources':self.sources,
                            'source_evidence_directory':'workarea/src',
                            'capacity_evidence_directory':'workarea/capacity'},
                            'names':[f'HERC02.BCPL.TA2STG.BT{n:04d}' for n in range(3,21)]}),\
             patch.object(mod.subprocess,'run',return_value=types.SimpleNamespace(
                          returncode=0,stdout='MVS STAT',stderr='')):
            self.assertEqual(mod.main(['--target-review',str(self.run),'--volume','TSO002','--live']),1)
        modules['ta2_alloc_target'].inquire.assert_not_called()
        fail=list((self.work/'ta2-allocation-plan').glob('*/failure.json'))
        self.assertEqual(len(fail),1)
        self.assertIn('source drift',fail[0].read_text())

    def test_new_private_run_and_checksum_evidence(self):
        out=mod.create_run()
        mod.save_new(out/'stage-allocations-proposed.json',b'{}\n')
        mod.seal(out)
        self.assertTrue((out/'SHA256SUMS').is_file())
        with self.assertRaises(mod.Refusal):mod.save_new(out/'stage-allocations-proposed.json',b'changed')

    def test_redundant_seal_refused(self):
        out=mod.create_run()
        mod.save_new(out/'a.txt',b'hello')
        mod.seal(out)
        with self.assertRaises(mod.Refusal):mod.seal(out)

    def test_no_repository_sibling_writes(self):
        before=set(self.root.iterdir())
        out=mod.create_run()
        self.assertEqual(before,set(self.root.iterdir()))
        self.assertEqual(out.parent,self.work/'ta2-allocation-plan')


if __name__ == '__main__':
    unittest.main()
