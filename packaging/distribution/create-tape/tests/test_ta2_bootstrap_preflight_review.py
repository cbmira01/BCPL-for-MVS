"""TA.2 saved read-only MVS target evidence review; no JES execution."""
from __future__ import annotations

import hashlib
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'packaging/distribution/create-tape/scripts/ta2-bootstrap-preflight-review'
loader = SourceFileLoader('bt_review_test', str(SOURCE))
spec = spec_from_loader(loader.name, loader)
mod = module_from_spec(spec)
loader.exec_module(mod)


class SavedReviewTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.work.cleanup)
        self.root = Path(self.work.name)
        (self.root / 'workarea').mkdir()
        self.base = self.root / 'workarea/ta2-bootstrap-target-preflight'
        self.base.mkdir()
        self.run = self.base / '20261120T025333Z-20572'
        self.run.mkdir()
        self.result = {
            'status': 'READ_ONLY_MVS_CATALOG_ABSENCE_VTOC_OBSERVED',
            'volume': 'TSO002', 'targets': list(mod.EXPECTED),
            'jobs': {'catalog': 9313, 'vtoc': 9314},
            'qualification': 'no write'
        }
        self.files = {'result.json': (json.dumps(self.result)+'\n').encode(),
                      'catalog-report.txt': b'MVS reports catalog absence\n',
                      'vtoc-report.txt': b'IEHLIST TSO002 raw report\n',
                      'catalog-cursor.json': b'{}\n',
                      'vtoc-cursor.json': b'{}\n'}
        self.seal()
        self.patch = [patch.object(mod, 'ROOT', self.root),
                      patch.object(mod, 'INROOT', self.base),
                      patch.object(mod, 'OUTROOT', self.root / 'workarea/ta2-bootstrap-preflight-review')]
        for obj in self.patch:
            obj.start(); self.addCleanup(obj.stop)
        self.core = SimpleNamespace()
        self.target = SimpleNamespace(catalog_absence=Mock())
        self.vtoc = SimpleNamespace(inspect_vtoc=Mock(return_value={
            'iehlist_reported_free_total_tracks': 16045,
            'staging_names_in_formatted_vtoc': 0,
            'format1_datasets_seen': 180
        }))
        self.older = SimpleNamespace(vtoc_observation=Mock())

    def seal(self):
        for name, blob in self.files.items():
            (self.run / name).write_bytes(blob)
        ledger = ''.join(hashlib.sha256(blob).hexdigest()+'  '+name+'\n'
                         for name, blob in sorted(self.files.items()))
        (self.run / 'SHA256SUMS').write_text(ledger)

    def inspect(self):
        contents = mod.saved_files(self.run)
        with patch.object(mod, 'load_module', return_value=self.older):
            return mod.inspect(contents, self.core, self.target, self.vtoc)

    def test_saved_full_report_pass_with_space_budget(self):
        result = self.inspect()
        self.assertEqual(result['status'], 'READ_ONLY_SAVED_MVS_REVIEW_PASS')
        self.assertEqual(result['targets'], list(mod.EXPECTED))
        self.assertEqual(result['iehlist_reported_free_tracks'], 16045)
        self.assertEqual(result['proposed_track_budget'], 31)
        self.target.catalog_absence.assert_called_once()
        self.older.vtoc_observation.assert_called_once()
        self.vtoc.inspect_vtoc.assert_called_once()

    def test_missing_sha_refused(self):
        (self.run / 'SHA256SUMS').unlink()
        with self.assertRaisesRegex(mod.Refusal, 'checksum ledger'):
            mod.saved_files(self.run)

    def test_modified_original_report_refused(self):
        (self.run / 'vtoc-report.txt').write_text('TAMPERED')
        with self.assertRaisesRegex(mod.Refusal, 'evidence changed'):
            mod.saved_files(self.run)

    def test_unknown_unsealed_file_refused(self):
        (self.run / 'injected.txt').write_text('not sealed')
        with self.assertRaisesRegex(mod.Refusal, 'differs from seal'):
            mod.saved_files(self.run)

    def test_duplicate_checksum_refused(self):
        with (self.run / 'SHA256SUMS').open('a') as f:
            f.write(hashlib.sha256(b'junk').hexdigest() + '  result.json\n')
        with self.assertRaisesRegex(mod.Refusal, 'duplicated'):
            mod.saved_files(self.run)

    def test_linked_raw_report_refused(self):
        original = self.run / 'vtoc-report.txt'
        blob = original.read_bytes()
        original.unlink()
        path = self.root / 'link-target'
        path.write_bytes(blob)
        original.symlink_to(path)
        with self.assertRaisesRegex(mod.Refusal, 'linked'):
            mod.saved_files(self.run)

    def test_other_evidence_run_refused(self):
        other = self.root / 'not-an-approved-run'
        other.mkdir()
        with self.assertRaisesRegex(mod.Refusal, 'original BT-only'):
            mod.saved_files(other)

    def test_wrong_mvs_job_ids_refused(self):
        self.result['jobs']['vtoc'] = self.result['jobs']['catalog']
        self.files['result.json'] = json.dumps(self.result).encode()
        self.seal()
        with self.assertRaisesRegex(mod.Refusal, 'conflicting JES'):
            self.inspect()

    def test_wrong_original_names_refused(self):
        self.result['targets'][1] = 'HERC02.BCPL.TA2STG.BT0003'
        self.files['result.json'] = json.dumps(self.result).encode()
        self.seal()
        with self.assertRaisesRegex(mod.Refusal, 'exact two'):
            self.inspect()

    def test_insufficient_mvs_tracks_refused(self):
        self.vtoc.inspect_vtoc.return_value['iehlist_reported_free_total_tracks'] = 30
        with self.assertRaisesRegex(mod.Refusal, 'free-track budget'):
            self.inspect()

    def test_mvs_free_summary_missing_refused(self):
        self.vtoc.inspect_vtoc.return_value['iehlist_reported_free_total_tracks'] = None
        with self.assertRaisesRegex(mod.Refusal, 'free-track budget'):
            self.inspect()

    def test_unexpected_formatted_vtoc_presence_refused(self):
        self.vtoc.inspect_vtoc.return_value['staging_names_in_formatted_vtoc'] = 1
        with self.assertRaisesRegex(mod.Refusal, 'present on formatted'):
            self.inspect()

    def test_snapshot_receipt_saved_exclusively(self):
        result = self.inspect()
        folder = mod.save_review(result)
        self.assertTrue((folder / 'review.json').is_file())
        self.assertIn('review.json', (folder / 'SHA256SUMS').read_text())
        self.assertEqual(json.loads((folder / 'review.json').read_text())['status'],
                         'READ_ONLY_SAVED_MVS_REVIEW_PASS')
        with patch.object(mod, 'datetime') as fake_dt, patch.object(mod.os, 'getpid', return_value=200):
            fake_dt.now.return_value.strftime.return_value = '20261120T025333Z'
            first = mod.save_review(result)
            with self.assertRaises(FileExistsError):
                mod.save_review(result)

    def test_no_new_mvs_submission(self):
        self.assertNotIn('submit_and_wait', SOURCE.read_text())
        self.assertNotIn('require_reader_ready', SOURCE.read_text())


if __name__ == '__main__':
    unittest.main()
