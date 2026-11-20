"""Synthetic read-only MVS contract tests for the two remaining staging inputs."""
from __future__ import annotations

from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import os
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / 'packaging/distribution/create-tape/scripts/ta2-bootstrap-target-preflight'
loader = SourceFileLoader('ta2_bt_preflight_tests', str(SRC))
spec = spec_from_loader(loader.name, loader)
mod = module_from_spec(spec)
loader.exec_module(mod)


class ReadOnlyBootTargets(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = {'mvs': {'hlq': 'HERC02'}}
        self.core = SimpleNamespace(
            stat_deck=Mock(return_value='//TA2C EXEC PGM=IKJEFT01\n//'),
            submit_and_wait=Mock(side_effect=[(100, 'summary'), (101, 'summary')]),
            job_report=Mock(side_effect=['DATA SET NOT IN CATALOG', 'TSO002 IEHLIST LISTVTOC']),
            dataset_missing=Mock(return_value=True),
            extract_listds_block=Mock(return_value=[]),
            parse_listds=Mock(return_value={}))
        self.target = SimpleNamespace(
            vtoc_deck=Mock(return_value='//TA2V EXEC PGM=IEHLIST\n//'),
            vtoc_observation=Mock(return_value=None))

    def test_approved_targets_exact(self):
        mod.ensure_names(mod.NAMES, 'TSO002')
        self.assertEqual(mod.NAMES, ['HERC02.BCPL.TA2STG.BT0001',
                                     'HERC02.BCPL.TA2STG.BT0002'])

    def test_changed_volume_refused(self):
        with self.assertRaisesRegex(mod.Refusal, 'only exact'):
            mod.ensure_names(mod.NAMES, 'TSO003')

    def test_other_pds_refused(self):
        with self.assertRaisesRegex(mod.Refusal, 'only exact'):
            mod.ensure_names(mod.NAMES + ['HERC02.BCPL.TA2STG.BT0003'], 'TSO002')

    def test_catalog_absent_positive(self):
        mod.catalog_absence(self.core, 'MVS LISTDS', mod.NAMES)
        self.assertEqual(self.core.dataset_missing.call_count, 2)

    def test_catalog_one_missing_response_refused(self):
        self.core.dataset_missing.side_effect = [True, False]
        with self.assertRaisesRegex(mod.Refusal, 'BT0002'):
            mod.catalog_absence(self.core, 'MVS LISTDS', mod.NAMES)

    def test_catalog_attributes_contradiction_refused(self):
        self.core.extract_listds_block.return_value = ['DSORG=PO']
        self.core.parse_listds.return_value = {'DSORG': 'PO'}
        with self.assertRaisesRegex(mod.Refusal, 'contradictory'):
            mod.catalog_absence(self.core, 'MVS LISTDS', mod.NAMES)

    def test_two_read_only_mvs_jobs_preserved(self):
        result = mod.inquire(self.core, self.config, self.target, self.root)
        self.assertEqual(result['status'], 'READ_ONLY_MVS_CATALOG_ABSENCE_VTOC_OBSERVED')
        self.assertEqual(result['jobs'], {'catalog': 100, 'vtoc': 101})
        self.assertEqual(self.core.submit_and_wait.call_count, 2)
        self.assertEqual((self.root / 'catalog-report.txt').read_text(), 'DATA SET NOT IN CATALOG')
        self.assertEqual((self.root / 'vtoc-report.txt').read_text(), 'TSO002 IEHLIST LISTVTOC')
        self.target.vtoc_observation.assert_called_once()
        self.assertEqual(self.core.submit_and_wait.call_args_list[0].kwargs['max_rc'], 8)
        self.assertEqual(self.core.submit_and_wait.call_args_list[1].kwargs['max_rc'], 0)

    def test_temporary_mvs_files_stay_in_repo_and_restore_settings(self):
        original_temp = tempfile.tempdir
        original_env = os.environ.get('TMPDIR')
        observed = []
        def snapshot(*args, **kwargs):
            observed.append((tempfile.tempdir, os.environ.get('TMPDIR')))
            return (100 if len(observed) == 1 else 101, 'summary')
        self.core.submit_and_wait.side_effect = snapshot
        mod.inquire(self.core, self.config, self.target, self.root)
        self.assertEqual(observed, [(str(self.root), str(self.root))] * 2)
        self.assertEqual(tempfile.tempdir, original_temp)
        self.assertEqual(os.environ.get('TMPDIR'), original_env)

    def test_first_job_failure_does_not_trigger_vtoc(self):
        self.core.dataset_missing.return_value = False
        with self.assertRaisesRegex(mod.Refusal, 'BT0001'):
            mod.inquire(self.core, self.config, self.target, self.root)
        self.assertEqual(self.core.submit_and_wait.call_count, 1)
        self.assertTrue((self.root / 'catalog-report.txt').is_file())
        self.assertFalse((self.root / 'vtoc-report.txt').exists())

    def test_bad_vtoc_response_refused(self):
        self.target.vtoc_observation.side_effect = ValueError('wrong VTOC')
        with self.assertRaisesRegex(ValueError, 'wrong VTOC'):
            mod.inquire(self.core, self.config, self.target, self.root)
        self.assertTrue((self.root / 'vtoc-report.txt').exists())

    def test_plan_mode_has_no_mvs_calls(self):
        with patch.object(mod, 'import_script', side_effect=AssertionError('MVS prohibited')):
            self.assertEqual(mod.main([]), 0)

    def test_report_sealing_no_overwrite(self):
        mod.save(self.root / 'result.json', b'{}')
        mod.seal(self.root)
        self.assertIn('result.json', (self.root / 'SHA256SUMS').read_text())
        with self.assertRaises(FileExistsError): mod.seal(self.root)

    def test_prohibited_catalog_jcl_width(self):
        self.core.stat_deck.return_value = '//*' + 'X' * 81
        with self.assertRaisesRegex(mod.Refusal, 'card width'):
            mod.inquire(self.core, self.config, self.target, self.root)
        self.assertEqual(self.core.submit_and_wait.call_count, 0)


if __name__ == '__main__':
    unittest.main()
