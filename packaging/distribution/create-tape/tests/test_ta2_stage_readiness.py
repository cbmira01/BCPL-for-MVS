"""TA.2 readiness: immutable proposal, full replay and no-write MVS inquiry."""
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
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / 'packaging/distribution/create-tape/scripts/ta2-stage-readiness'
loader = importlib.machinery.SourceFileLoader('ta2_stage_readiness_tests', str(PATH))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'workarea').mkdir()
        self.base = self.root/'workarea/ta2-allocation-plan'
        self.folder = self.base/'20261119T204153Z-17905'
        self.folder.mkdir(parents=True)
        self.review = 'workarea/ta2-target-review/20261119T181059Z-17632'
        self.stage = 'workarea/ta2-stage-plan/20261119T155947Z-17087'
        self.allocation = {'schema_version': 1, 'staging_namespace': 'HERC02.BCPL.TA2STG',
                           'stage_worksheet_sha256': 'a'*64,
                           'targets': [{'sequence': n, 'dsn': f'HERC02.BCPL.TA2STG.BT{n:04d}',
                                        'volume': 'TSO002', 'space': {'primary_tracks': 35,
                                                                      'secondary_tracks': 3,
                                                                      'directory_blocks': 8}}
                                       for n in range(3, 21)]}
        self.plan = {'status': 'READ-ONLY MVS PLANNING PASS; ALLOCATIONS UNAPPROVED',
                     'volume': 'TSO002', 'target_review_directory': self.review,
                     'target_review_sha256': 'r'*64,
                     'source_worksheet_sha256': 'a'*64,
                     'fresh_mvs_jobs': {'catalog_job': 100, 'vtoc_job': 101},
                     'source_stat_sha256': '', 'primary_tracks_total': 630,
                     'secondary_tracks_total': 54, 'total_primary_secondary_budget': 684,
                     'unused_reported_tracks_after_budget': 15361,
                     'directory_blocks_total': 144,
                     'reported_free_tracks': 16045,
                     'sources': [{'sequence': n} for n in range(3,21)]}
        self.contents = {
            'stage-allocations-proposed.json': (json.dumps(self.allocation)+'\n').encode(),
            'planning-review.json': b'',
            'stage-iebcopy-draft.jcl': b'//S0003 EXEC PGM=IEBCOPY\n',
            'source-stat.txt': b'RC=0\nREAL SOURCE STAT\n',
            'catalog-report.txt': b'NOT IN CATALOG\n',
            'vtoc-report.txt': b'CONTENTS OF VTOC ON VOL TSO002\n',
        }
        self.plan['source_stat_sha256'] = mod.sha(self.contents['source-stat.txt'])
        self.contents['planning-review.json'] = (json.dumps(self.plan)+'\n').encode()
        self.save()
        self.patches = [patch.object(mod,'ROOT',self.root),
                        patch.object(mod,'PLAN_BASE',self.base),
                        patch.object(mod,'OUT',self.root/'workarea/ta2-stage-readiness')]
        for p in self.patches:p.start();self.addCleanup(p.stop)

    def save(self):
        for name,b in self.contents.items():
            (self.folder/name).write_bytes(b)
        sums = ''.join(mod.sha(self.contents[name])+'  '+name+'\n'
                       for name in sorted(self.contents))
        (self.folder/'SHA256SUMS').write_text(sums)

    def load(self):
        return mod.read_plan(self.folder)

    def test_saved_evidence_exact_six_records(self):
        raw,a,p,h = self.load()
        self.assertEqual(set(raw), mod.SAVED)
        self.assertEqual(a,self.allocation)
        self.assertEqual(p,self.plan)
        self.assertEqual(h,mod.sha(self.contents['planning-review.json']))

    def test_changed_planning_checksum_refused(self):
        (self.folder/'planning-review.json').write_bytes(b'{}')
        with self.assertRaisesRegex(mod.Refusal, 'checksum mismatch'):
            self.load()

    def test_changed_draft_checksum_refused(self):
        (self.folder/'stage-iebcopy-draft.jcl').write_bytes(b'changed')
        with self.assertRaises(mod.Refusal):self.load()

    def test_changed_saved_source_checksum_refused(self):
        (self.folder/'source-stat.txt').write_bytes(b'changed')
        with self.assertRaises(mod.Refusal):self.load()

    def test_unlisted_extra_file_refused(self):
        (self.folder/'foreign').write_text('secret')
        with self.assertRaisesRegex(mod.Refusal, 'extra'):
            self.load()

    def test_missing_critical_file_refused(self):
        (self.folder/'vtoc-report.txt').unlink()
        with self.assertRaises(mod.Refusal):self.load()

    def test_checksum_manifest_replaced_refused(self):
        (self.folder/'SHA256SUMS').write_text('')
        with self.assertRaisesRegex(mod.Refusal, 'incomplete'):
            self.load()

    def test_symlink_instead_of_report_refused(self):
        (self.folder/'vtoc-report.txt').unlink()
        (self.folder/'vtoc-report.txt').symlink_to(self.folder/'source-stat.txt')
        with self.assertRaisesRegex(mod.Refusal, 'linked'):
            self.load()

    def test_linked_directory_refused(self):
        link = self.folder.with_name('20261119T204154Z-17906')
        link.symlink_to(self.folder, target_is_directory=True)
        with self.assertRaisesRegex(mod.Refusal, 'private'):
            mod.read_plan(link)

    def test_directory_outside_workarea_refused(self):
        with self.assertRaises(mod.Refusal):mod.read_plan(self.root)

    def test_missing_run_date_refused(self):
        with self.assertRaises(mod.Refusal):mod.read_plan(self.base)

    def test_failed_source_stat_refused_even_rehashed(self):
        self.contents['source-stat.txt']=b'RC=12\nERROR\n'
        self.plan['source_stat_sha256']=mod.sha(self.contents['source-stat.txt'])
        self.contents['planning-review.json']=(json.dumps(self.plan)+'\n').encode()
        self.save()
        with self.assertRaisesRegex(mod.Refusal, 'did not complete'):
            self.load()

    def test_nonpassing_planner_status_refused(self):
        self.plan['status']='PROPOSED ONLY; NOT ALLOCATION AUTHORIZATION'
        self.contents['planning-review.json']=(json.dumps(self.plan)+'\n').encode()
        self.save()
        with self.assertRaisesRegex(mod.Refusal, 'not supported'):
            self.load()

    def test_missing_mvs_job_refused(self):
        self.plan['fresh_mvs_jobs']['catalog_job']=-1
        self.contents['planning-review.json']=(json.dumps(self.plan)+'\n').encode()
        self.save()
        with self.assertRaisesRegex(mod.Refusal, 'job receipt'):
            self.load()

    def test_duplicate_mvs_job_refused(self):
        self.plan['fresh_mvs_jobs']['catalog_job']=101
        self.contents['planning-review.json']=(json.dumps(self.plan)+'\n').encode()
        self.save()
        with self.assertRaises(mod.Refusal):self.load()

    def test_symlinked_outdir_refused(self):
        mod.OUT.symlink_to(self.folder, target_is_directory=True)
        with self.assertRaisesRegex(mod.Refusal, 'unsafe'):
            mod.make_run()

    def test_exclusive_write_never_overwrites(self):
        path=self.folder/'newrecord'
        mod.save_new(path,b'new')
        with self.assertRaisesRegex(mod.Refusal, 'overwrite'):
            mod.save_new(path,b'overwrite')
        self.assertEqual(path.read_bytes(),b'new')

    def test_seal_is_exclusive(self):
        sealed = self.root/'workarea'/'empty-receipt'
        sealed.mkdir()
        mod.save_new(sealed/'readiness.json', b'receipt')
        mod.seal(sealed)
        self.assertIn('readiness.json', (sealed/'SHA256SUMS').read_text())
        with self.assertRaises(mod.Refusal):mod.seal(sealed)

    def fake_modules(self):
        canonical=Mock()
        canonical.load.side_effect=[{'phase':'design','datasets':[]},{'mvs':{'hlq':'HERC02'}}]
        source=Mock(core=lambda:canonical,expected_sources=lambda *a: ['one'])
        stage=Mock()
        stage.read_stage_run.return_value=({'sources': [{'source_evidence_directory': 'BAD'}],
                                            'source_evidence_directory': 'workarea/ta2-source-preflight/X',
                                            'capacity_evidence_directory':'workarea/ta2-capacity-preflight/X'},
                                           'a'*64,b'RC=0\n')
        stage.validate_worksheet.return_value=[{'sequence':n} for n in range(3,21)]
        stage.validate_allocations.return_value=[{'sequence':n} for n in range(3,21)]
        stage.render_jcl.return_value=self.contents['stage-iebcopy-draft.jcl'].decode()
        target=Mock(targets=lambda rows,dspal: [f'HERC02.BCPL.TA2STG.BT{n:04d}' for n in range(3,21)])
        review=Mock()
        review.read_original.return_value={'summary.json':json.dumps({'stage_evidence':self.stage}).encode()}
        review.inspect_vtoc.return_value={'format1_names_sha256':'v'*64,
                                          'iehlist_reported_free_total_tracks':16045,
                                          'format1_datasets_seen':30}
        allocation=Mock()
        allocation.read_review.return_value=({'original_target_evidence': 'workarea/ta2-target-preflight/20261119T170234Z-17334',
                                             'format1_names_sha256':'v'*64,
                                             'iehlist_reported_free_total_tracks':16045}, {},'r'*64)
        allocation.audit_saved.return_value={'worksheet_sha':'a'*64,'plan':stage.read_stage_run.return_value[0]}
        allocation.derive_targets.return_value=(copy.deepcopy(self.allocation),
                                                 {'primary_tracks_total':630,
                                                  'secondary_tracks_total':54,
                                                  'directory_blocks_total':144,
                                                  'total_primary_secondary_budget':684,
                                                  'reported_free_tracks':16045,
                                                  'unused_reported_tracks_after_budget':15361,
                                                  'sources':self.plan['sources'],
                                                  'volume':'TSO002'})
        stageplan=Mock()
        core=Mock()
        return {'source':source,'stage':stage,'target':target,'review':review,
                'allocation':allocation,'source_review':Mock(), 'capacity':Mock(),
                'stageplan':stageplan, 'core':core}

    def replay(self, modules):
        raw, allocation, planning, _=self.load()
        return mod.replay(raw,allocation,planning,modules)

    def test_valid_replay_returns_18_targets(self):
        mods=self.fake_modules()
        checked,sizing,saved,items,names=self.replay(mods)
        self.assertEqual(len(names),18)
        self.assertEqual(sizing['total_primary_secondary_budget'],684)
        mods['stage'].verify_history.assert_called_once()
        mods['stageplan'].compare_current.assert_called_once()

    def test_altered_per_target_primary_refused(self):
        mods=self.fake_modules()
        self.allocation['targets'][5]['space']['primary_tracks']+=1
        self.contents['stage-allocations-proposed.json']=(json.dumps(self.allocation)+'\n').encode()
        self.save()
        with self.assertRaisesRegex(mod.Refusal, 'SPACE triples'):
            self.replay(mods)

    def test_altered_draft_but_valid_sha_refused(self):
        mods=self.fake_modules()
        self.contents['stage-iebcopy-draft.jcl']=b'//INVALID\n'
        self.save()
        with self.assertRaisesRegex(mod.Refusal, 'IEBCOPY draft'):
            self.replay(mods)

    def test_wrong_volume_refused(self):
        mods=self.fake_modules()
        self.plan['volume']='TSO003'
        self.contents['planning-review.json']=(json.dumps(self.plan)+'\n').encode()
        self.save()
        with self.assertRaisesRegex(mod.Refusal, 'TSO002'):
            self.replay(mods)

    def test_saved_target_review_drift_refused(self):
        mods=self.fake_modules()
        mods['allocation'].read_review.return_value=({}, {}, 'other')
        with self.assertRaisesRegex(mod.Refusal, 'evidence changed'):
            self.replay(mods)

    def test_stage_plan_checksum_drift_refused(self):
        mods=self.fake_modules()
        mods['stage'].read_stage_run.return_value=(mods['stage'].read_stage_run.return_value[0],
                                                    'b'*64,b'RC=0\n')
        with self.assertRaisesRegex(mod.Refusal, 'worksheet SHA'):
            self.replay(mods)

    def test_source_replay_drift_refused(self):
        mods=self.fake_modules()
        mods['stage'].verify_history.side_effect=mod.Refusal('MVS source changed')
        with self.assertRaisesRegex(mod.Refusal,'MVS source changed'):
            self.replay(mods)

    def test_raw_mvs_vtoc_collision_refused(self):
        mods=self.fake_modules()
        mods['review'].inspect_vtoc.side_effect=mod.Refusal('VTOC collides')
        with self.assertRaisesRegex(mod.Refusal,'VTOC collides'):
            self.replay(mods)

    def test_replay_catalog_collision_refused(self):
        mods=self.fake_modules()
        mods['target'].catalog_absence.side_effect=mod.Refusal('target present')
        with self.assertRaisesRegex(mod.Refusal,'target present'):
            self.replay(mods)

    def test_source_report_drift_refused(self):
        mods=self.fake_modules()
        mods['stageplan'].compare_current.side_effect=mod.Refusal('source HWM changed')
        with self.assertRaisesRegex(mod.Refusal, 'source HWM changed'):
            self.replay(mods)

    def test_readiness_no_live_does_not_submit(self):
        mods=self.fake_modules()
        with (patch.object(mod,'load',side_effect=lambda name,path: mods['core'] if name=='ta2_ready_core' else mods[next(k for k in mods if name=='ta2_ready_'+k)]),
              patch.object(mod,'make_run',side_effect=AssertionError('no workarea')),
              patch.object(mod.subprocess,'run',side_effect=AssertionError('no MVS'))):
            rc=mod.main(['--allocation-evidence',str(self.folder)])
        self.assertEqual(rc,0)

    def test_failed_source_inquiry_preserves_report(self):
        folder=self.root/'workarea'
        stageplan=Mock()
        p=SimpleNamespace(returncode=4,stdout='SOURCE FAILED',stderr='')
        with patch.object(mod.subprocess,'run',return_value=p):
            with self.assertRaisesRegex(mod.Refusal,'source capacity check failed'):
                mod.inquire_source(folder,stageplan,None,None,None,None,None)
        self.assertEqual((folder/'source-stat.txt').read_text(),'RC=4\nSOURCE FAILED')
        stageplan.compare_current.assert_not_called()

    def test_positive_source_inquiry_compares(self):
        folder=self.root/'workarea'
        stageplan=Mock()
        p=SimpleNamespace(returncode=0,stdout='SOURCE SUCCESS',stderr='')
        with patch.object(mod.subprocess,'run',return_value=p):
            value=mod.inquire_source(folder,stageplan,None,None,None,None,None)
        self.assertEqual(value,mod.sha(b'SOURCE SUCCESS'))
        stageplan.compare_current.assert_called_once()

    def test_main_live_saves_readonly_evidence_without_stage_submission(self):
        mods=self.fake_modules()
        names=mods['target'].targets([], {})
        record={'catalog_job': 409, 'vtoc_job': 410}
        def inquire(core, config, folder, asked_names, volume):
            self.assertEqual(asked_names,names)
            self.assertEqual(volume,'TSO002')
            (folder/'catalog-report.txt').write_text('NOT IN CATALOG\n')
            (folder/'vtoc-report.txt').write_text('CONTENTS OF VTOC ON VOL TSO002\n')
            return record
        mods['target'].inquire.side_effect=inquire
        mods['core'].load_config.return_value={'mvs':{'hlq':'HERC02'}}
        fake_import=lambda name,path: mods['core'] if name=='ta2_ready_core' else mods[next(k for k in mods if name=='ta2_ready_'+k)]
        with (patch.object(mod,'load',side_effect=fake_import),
              patch.object(mod,'inquire_source',return_value='c'*64),
              patch.object(mod,'OUT',self.root/'workarea/ta2-stage-readiness')):
            rc=mod.main(['--allocation-evidence',str(self.folder),'--live'])
        self.assertEqual(rc,0)
        runs=list((self.root/'workarea/ta2-stage-readiness').iterdir())
        self.assertEqual(len(runs),1)
        summary=json.loads((runs[0]/'readiness.json').read_text())
        self.assertEqual(summary['status'],
                         'READ-ONLY MVS CHECK PASS; STAGING WRITE NOT AUTHORIZED')
        self.assertEqual(summary['mvs_jobs'],record)
        self.assertEqual(summary['staging_datasets'],18)
        self.assertTrue((runs[0]/'SHA256SUMS').is_file())
        self.assertFalse((runs[0]/'failure.json').exists())
        self.assertEqual(len(mod.SAVED),6)

    def test_live_source_drift_stops_before_target_inquiry(self):
        mods=self.fake_modules()
        fake_import=lambda name,path: mods['core'] if name=='ta2_ready_core' else mods[next(k for k in mods if name=='ta2_ready_'+k)]
        with (patch.object(mod,'load',side_effect=fake_import),
              patch.object(mod,'inquire_source',side_effect=mod.Refusal('source changed'))):
            rc=mod.main(['--allocation-evidence',str(self.folder),'--live'])
        self.assertEqual(rc,1)
        mods['target'].inquire.assert_not_called()
        runs=list((self.root/'workarea/ta2-stage-readiness').iterdir())
        self.assertEqual(len(runs),1)
        self.assertEqual(json.loads((runs[0]/'failure.json').read_text())['reason'],
                         'source changed')
        self.assertTrue((runs[0]/'SHA256SUMS').is_file())

    def test_live_vtoc_drift_keeps_raw_mvs_reports(self):
        mods=self.fake_modules()
        mods['core'].load_config.return_value={'mvs':{'hlq':'HERC02'}}
        def inquire(core, config, folder, asked_names, volume):
            (folder/'catalog-report.txt').write_text('NOT IN CATALOG\n')
            (folder/'vtoc-report.txt').write_text('VTOC CHANGED\n')
            return {'catalog_job': 409,'vtoc_job':410}
        mods['target'].inquire.side_effect=inquire
        initial={'format1_names_sha256':'v'*64,
                 'iehlist_reported_free_total_tracks':16045,
                 'format1_datasets_seen':30}
        changed={'format1_names_sha256':'x'*64,
                 'iehlist_reported_free_total_tracks':16044,
                 'format1_datasets_seen':31}
        mods['review'].inspect_vtoc.side_effect=[initial, changed]
        fake_import=lambda name,path: mods['core'] if name=='ta2_ready_core' else mods[next(k for k in mods if name=='ta2_ready_'+k)]
        with (patch.object(mod,'load',side_effect=fake_import),
              patch.object(mod,'inquire_source',return_value='c'*64)):
            rc=mod.main(['--allocation-evidence',str(self.folder),'--live'])
        self.assertEqual(rc,1)
        runs=list((self.root/'workarea/ta2-stage-readiness').iterdir())
        self.assertEqual(len(runs),1)
        self.assertTrue((runs[0]/'failure.json').is_file())
        self.assertTrue((runs[0]/'vtoc-report.txt').is_file())
        self.assertTrue((runs[0]/'catalog-report.txt').is_file())
        self.assertFalse((runs[0]/'readiness.json').exists())

    def test_summary_sealing_never_modifies_plan(self):
        original=self.contents['stage-iebcopy-draft.jcl']
        self.load()
        self.assertEqual((self.folder/'stage-iebcopy-draft.jcl').read_bytes(),original)


if __name__ == '__main__':
    unittest.main()
