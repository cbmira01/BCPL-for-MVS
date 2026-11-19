"""Synthetic TA.2 target evidence replay, VTOC limits and safe MVS readback."""
from __future__ import annotations

import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / 'packaging/distribution/create-tape/scripts/ta2-target-review'
ldr = importlib.machinery.SourceFileLoader('ta2_target_review_test', str(SCRIPT))
spec = importlib.util.spec_from_loader(ldr.name, ldr)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FakeCore:
    def dataset_missing(self, report, dsn):
        return f'{dsn} NOT IN CATALOG' in report

    def extract_listds_block(self, report, dsn):
        return []

    def parse_listds(self, block):
        return {}

    def load_config(self):
        return {'mvs': {'hlq': 'HERC02'}}

    def require_reader_ready(self, config):
        pass


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'workarea').mkdir()
        self.base = self.root/'workarea/ta2-target-preflight'
        self.dir = self.base/'20261119T170234Z-17334'
        self.dir.mkdir(parents=True)
        self.stage_rel = 'workarea/ta2-stage-plan/20261119T155947Z-17087'
        self.names = [f'HERC02.BCPL.TA2STG.BT{n:04d}' for n in range(3,21)]
        self.target = types.SimpleNamespace(NAMESPACE='HERC02.BCPL.TA2STG',
                                            VOLUME=mod.re.compile('[A-Z0-9]{1,6}\\Z'),
                                            catalog_absence=self._catalog_absence,
                                            vtoc_observation=self._vtoc_observation,
                                            targets=lambda rows,dspal: self.names)
        self.core = FakeCore()
        self.summary = {'status':'CATALOG ABSENCE CHECKED; VTOC SPACE REVIEW PENDING',
                        'staging_namespace':'HERC02.BCPL.TA2STG',
                        'proposed_dasd_volume':'TSO002', 'target_dsns':self.names,
                        'stage_evidence':self.stage_rel,
                        'stage_worksheet_sha256':'a'*64,
                        'mvs_jobs':{'catalog_job':9231,'vtoc_job':9232},
                        'qualification':'free capacity not established'}
        self.catalog = '\n'.join(n + ' NOT IN CATALOG' for n in self.names) + '\n'
        self.vtoc = '''SYSTEMS SUPPORT UTILITIES---IEHLIST
 CONTENTS OF VTOC ON VOL TSO002
 ---------------DATA SET NAME----------------  SER NO  SEQNO  DATE.CRE
 SYS1.PARMLIB                              1 TSO002     1    00001
 HERC02.BCPL.MR10KIT.LOAD                  1 TSO002     1    00001
 FORMAT 4 DSCB
'''
        self._save()
        self.patch1 = patch.object(mod,'ROOT',self.root)
        self.patch2 = patch.object(mod,'EVIDENCE_BASE',self.base)
        self.patch3 = patch.object(mod,'OUT',self.root/'workarea/ta2-target-review')
        self.patch1.start();self.patch2.start();self.patch3.start()
        self.addCleanup(self.patch3.stop);self.addCleanup(self.patch2.stop);self.addCleanup(self.patch1.stop)

    def _catalog_absence(self, core, report, names):
        for name in names:
            if not core.dataset_missing(report,name):
                raise mod.Refusal('catalog conflict')

    def _vtoc_observation(self, report, volume, names):
        for name in names:
            if name in report:
                raise mod.Refusal('VTOC collision')

    def _save(self):
        (self.dir/'summary.json').write_text(json.dumps(self.summary,indent=2)+'\n')
        (self.dir/'catalog-report.txt').write_text(self.catalog)
        (self.dir/'vtoc-report.txt').write_text(self.vtoc)
        text = ''.join(hashlib.sha256((self.dir/k).read_bytes()).hexdigest()+'  '+k+'\n'
                       for k in sorted(mod.EXPECTED))
        (self.dir/'SHA256SUMS').write_text(text)

    def raw(self):
        return mod.read_original(self.dir)

    def inspect(self):
        return mod.inspect_saved(self.raw(),'a'*64,self.names,self.stage_rel,
                                 self.target,self.core)

    def test_real_iehlist_format1_dscb_field(self):
        # Actual MVS VTOC FORMAT-1 as parsed by tools/datasets/dspal-space.py:
        # DSN, DSCB type 1, VOLSER, sequence, date.
        rows = [(m.group(1), m.group(2)) for m in mod.ENTRY.finditer(self.vtoc)]
        self.assertEqual(rows, [('SYS1.PARMLIB', 'TSO002'),
                                ('HERC02.BCPL.MR10KIT.LOAD', 'TSO002')])
        self.assertEqual(self.inspect()['format1_datasets_seen'], 2)

    def test_old_fixture_layout_still_recognized(self):
        old = self.vtoc.replace('1 TSO002     1    00001',
                                'TSO002     1    2026.323')
        self.assertEqual(mod.inspect_vtoc(old, 'TSO002', self.names)['format1_names_sha256'],
                         mod.inspect_vtoc(self.vtoc, 'TSO002', self.names)['format1_names_sha256'])

    def test_other_dscb_type_not_counted_as_format1(self):
        stray = self.vtoc + ' SYS1.LINKLIB 4 TSO002 1 00001\n'
        self.assertEqual(mod.inspect_vtoc(stray, 'TSO002', self.names)['format1_datasets_seen'], 2)

    def test_actual_dscb_field_other_volume_still_refused(self):
        bad = self.vtoc + ' SYS1.LINKLIB 1 TSO003 1 00001\n'
        with self.assertRaisesRegex(mod.Refusal, 'unexpected VOLSER'):
            mod.inspect_vtoc(bad, 'TSO002', self.names)

    def test_exact_checked_evidence(self):
        self.assertEqual(len(self.raw()),3)
        self.assertEqual(self.inspect()['format1_datasets_seen'],2)
        self.assertEqual(self.inspect()['saved_mvs_jobs'],{'catalog_job':9231,'vtoc_job':9232})

    def test_never_infer_volume_free_tracks(self):
        v=mod.inspect_vtoc(self.vtoc, 'TSO002',self.names)
        self.assertIsNone(v['volume_free_tracks'])
        self.assertFalse(v['volume_free_tracks_verified'])
        self.assertTrue(v['format4_heading_seen'])

    def test_iehlist_volume_free_summary_is_planning_only(self):
        s=self.vtoc+'THERE ARE   21 EMPTY CYLINDERS PLUS   14 EMPTY TRACKS ON THIS VOLUME\n'
        r=mod.inspect_vtoc(s,'TSO002',self.names)
        self.assertEqual(r['iehlist_reported_free_total_tracks'],329)
        self.assertIsNone(r['volume_free_tracks'])
        self.assertFalse(r['volume_free_tracks_verified'])

    def test_invalid_track_remainder_refused(self):
        s=self.vtoc+'THERE ARE 21 EMPTY CYLINDERS PLUS 15 EMPTY TRACKS ON THIS VOLUME\n'
        with self.assertRaisesRegex(mod.Refusal,'remainder'):
            mod.inspect_vtoc(s,'TSO002',self.names)

    def test_multiple_free_summaries_refused(self):
        s=self.vtoc+('THERE ARE 21 EMPTY CYLINDERS PLUS 14 EMPTY TRACKS ON THIS VOLUME\n'*2)
        with self.assertRaisesRegex(mod.Refusal,'ambiguous'):
            mod.inspect_vtoc(s,'TSO002',self.names)

    def test_header_wrong_volume(self):
        with self.assertRaisesRegex(mod.Refusal,'heading'):
            mod.inspect_vtoc(self.vtoc,'TSO003',self.names)

    def test_header_ambiguous_volume(self):
        with self.assertRaises(mod.Refusal):
            mod.inspect_vtoc(self.vtoc+'\nCONTENTS OF VTOC ON VOL TSO003\n','TSO002',self.names)

    def test_missing_header(self):
        with self.assertRaises(mod.Refusal):
            mod.inspect_vtoc('IEHLIST FORMAT ON TSO002','TSO002',self.names)

    def test_no_format1_rows(self):
        with self.assertRaisesRegex(mod.Refusal,'no recognizable'):
            mod.inspect_vtoc('CONTENTS OF VTOC ON VOL TSO002\nDATA SET NAME SER NO SEQNO\n','TSO002',self.names)

    def test_uncataloged_collision(self):
        with self.assertRaisesRegex(mod.Refusal,'possible uncataloged'):
            mod.inspect_vtoc(self.vtoc+self.names[0]+' TSO002 1 2026.323\n','TSO002',self.names)

    def test_partial_name_not_collision(self):
        v=mod.inspect_vtoc(self.vtoc+self.names[0]+'X \n','TSO002',self.names)
        self.assertEqual(v['format1_datasets_seen'],2)

    def test_mismatched_entry_volume(self):
        with self.assertRaisesRegex(mod.Refusal,'unexpected VOLSER'):
            mod.inspect_vtoc(self.vtoc+'SYS1.SOMETHIN TSO003 1 2026.323\n', 'TSO002',self.names)

    def test_duplicate_data_set_rows(self):
        with self.assertRaisesRegex(mod.Refusal,'duplicate'):
            mod.inspect_vtoc(self.vtoc+'SYS1.PARMLIB TSO002 1 2026.323\n','TSO002',self.names)

    def test_missing_format_header_refused(self):
        with self.assertRaisesRegex(mod.Refusal, 'data-set header'):
            mod.inspect_vtoc(self.vtoc.replace('DATA SET NAME', 'DATA XXX NAME'),'TSO002',self.names)

    def test_inventory_hash_changes_on_name_change(self):
        changed=self.vtoc.replace('SYS1.PARMLIB','SYS1.LINKLIB')
        self.assertNotEqual(mod.inspect_vtoc(changed,'TSO002',self.names)['format1_names_sha256'],
                            mod.inspect_vtoc(self.vtoc,'TSO002',self.names)['format1_names_sha256'])

    def test_ieh_error_refusal(self):
        with self.assertRaisesRegex(mod.Refusal,'error'):
            mod.inspect_vtoc(self.vtoc+'\nIEH999E failure\n','TSO002',self.names)

    def test_abend_refusal(self):
        with self.assertRaisesRegex(mod.Refusal,'error'):
            mod.inspect_vtoc(self.vtoc+'\nABEND 001\n','TSO002',self.names)

    def test_catalog_report_drift(self):
        self.catalog=self.catalog.replace(self.names[-1]+' NOT IN CATALOG','')
        self._save()
        with self.assertRaisesRegex(mod.Refusal,'catalog conflict'):
            self.inspect()

    def test_summary_forgery(self):
        self.summary['stage_worksheet_sha256']='b'*64
        self._save()
        with self.assertRaisesRegex(mod.Refusal,'receipt disagrees'):
            self.inspect()

    def test_schema_extra_field(self):
        self.summary['unknown']='unknown'
        self._save()
        with self.assertRaisesRegex(mod.Refusal,'schema'):
            self.inspect()

    def test_stage_path_forgery(self):
        self.summary['stage_evidence']='workarea/ta2-stage-plan/DIFFERENT'
        self._save()
        with self.assertRaisesRegex(mod.Refusal,'receipt disagrees'):
            self.inspect()

    def test_negative_job_id(self):
        self.summary['mvs_jobs']['vtoc_job']=-1
        self._save()
        with self.assertRaisesRegex(mod.Refusal,'JES job'):
            self.inspect()

    def test_duplicate_job_id(self):
        self.summary['mvs_jobs']['vtoc_job']=9231
        self._save()
        with self.assertRaisesRegex(mod.Refusal,'JES job'):
            self.inspect()

    def test_bad_checksum_original(self):
        (self.dir/'vtoc-report.txt').write_text('tamper')
        with self.assertRaisesRegex(mod.Refusal,'SHA-256 mismatch'):
            self.raw()

    def test_no_partial_checksum_file(self):
        (self.dir/'SHA256SUMS').write_text('')
        with self.assertRaisesRegex(mod.Refusal,'incomplete'):
            self.raw()

    def test_unexpected_evidence_file(self):
        (self.dir/'extra.txt').write_text('extra')
        with self.assertRaisesRegex(mod.Refusal,'missing or extra'):
            self.raw()

    def test_linked_evidence_file(self):
        (self.dir/'vtoc-report.txt').unlink()
        (self.dir/'vtoc-report.txt').symlink_to('summary.json')
        with self.assertRaisesRegex(mod.Refusal,'linked'):
            self.raw()

    def test_linked_evidence_dir(self):
        p=self.dir.with_name('20261119T170235Z-17335')
        p.symlink_to(self.dir,target_is_directory=True)
        with self.assertRaisesRegex(mod.Refusal,'unsafe'):
            mod.safe_evidence(p,self.base)

    def test_external_dir(self):
        with self.assertRaisesRegex(mod.Refusal,'unsafe'):
            mod.safe_evidence(self.root,self.base)

    def test_exclusive_write(self):
        p=self.root/'workarea/review.json'
        mod.save(p,b'original')
        with self.assertRaisesRegex(mod.Refusal,'overwritten'):
            mod.save(p,b'next')
        self.assertEqual(p.read_bytes(),b'original')

    def test_saved_checksum_receipt(self):
        folder=self.root/'workarea/review'
        folder.mkdir()
        mod.save(folder/'review.json',b'hello')
        mod.write_sums(folder)
        self.assertIn('review.json',(folder/'SHA256SUMS').read_text())

    def importer(self, name,path):
        stage=Mock()
        stage.read_stage_run.return_value=({'sources':[{'source_tracks_allocated':20,
                'source_tracks_through_hwm':16,'source_directory_allocated':8,
                'source_directory_used':5} for _ in range(18)]},'a'*64,b'RC=0\n')
        stage.validate_worksheet.return_value=[{'sequence':n} for n in range(3,21)]
        source=Mock()
        canon=Mock()
        canon.load.side_effect=[{}, {'mvs':{'hlq':'HERC02'}}]
        source.core.return_value=canon
        if name=='ta2_review_source':return source
        if name=='ta2_review_stage':return stage
        if name=='ta2_review_target':return self.target
        if name=='ta2_review_core':return self.core
        raise AssertionError('unexpected tool import: '+name)

    def test_main_no_live_never_queries_mvs(self):
        # Avoid the real stage-history dependency; the synthetic importer returns mocks.
        with patch.object(mod,'load_module',side_effect=self.importer):
            self.assertEqual(mod.main(['--target-evidence',str(self.dir)]),0)
        reviewdirs=list((self.root/'workarea/ta2-target-review').iterdir())
        self.assertEqual(len(reviewdirs),1)
        self.assertTrue((reviewdirs[0]/'SHA256SUMS').exists())
        data=json.loads((reviewdirs[0]/'review.json').read_text())
        self.assertEqual(data['source_allocated_tracks_total'],360)
        self.assertEqual(data['source_directory_allocated_total'],144)
        self.assertFalse(data['source_capacity_is_destination_free_space'])

    def test_main_live_two_inquiries_saved(self):
        def inquire(core, config, folder, names, volume):
            (folder/'vtoc-report.txt').write_text(self.vtoc)
            (folder/'catalog-report.txt').write_text(self.catalog)
            return {'catalog_job':9233,'vtoc_job':9234}
        self.target.inquire=inquire
        with patch.object(mod,'load_module',side_effect=self.importer):
            self.assertEqual(mod.main(['--target-evidence',str(self.dir),'--live']),0)
        rdir=list((self.root/'workarea/ta2-target-review').iterdir())[0]
        data=json.loads((rdir/'review.json').read_text())
        self.assertTrue(data['live_recheck'])
        self.assertEqual(data['fresh_mvs_jobs']['vtoc_job'],9234)

    def test_live_drift_refuses_preserves_reports(self):
        def inquire(core, config, folder, names, volume):
            (folder/'vtoc-report.txt').write_text(self.vtoc+'SYS1.EXTRA TSO002 1 2026.323\n')
            (folder/'catalog-report.txt').write_text(self.catalog)
            return {'catalog_job':9233,'vtoc_job':9234}
        self.target.inquire=inquire
        with patch.object(mod,'load_module',side_effect=self.importer):
            self.assertEqual(mod.main(['--target-evidence',str(self.dir),'--live']),1)
        rdir=list((self.root/'workarea/ta2-target-review').iterdir())[0]
        self.assertTrue((rdir/'failure.json').exists())
        self.assertTrue((rdir/'vtoc-report.txt').exists())


if __name__ == '__main__':
    unittest.main()
