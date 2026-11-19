"""TA.2 approved staging-name catalog/VTOC read-only safety tests."""
from __future__ import annotations

import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / 'packaging/distribution/create-tape/scripts/ta2-target-preflight'
loader = importlib.machinery.SourceFileLoader('ta2_target_preflight_tests', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)


class FakeCore:
    def __init__(self, names):
        self.names = names
        self.calls = []
        self.reports = {
            100: '\n'.join(f'{n} NOT IN CATALOG' for n in names),
            101: 'IEH123I LISTVTOC FORMAT VOLUME TSO002\nTOTAL TRACKS 1000\n',
        }
        self.ready = True

    def authenticated_job_card(self, config, jobname, description, redact_password):
        return [f'//{jobname} JOB (BCPL),\'READ-ONLY\'']

    def stat_deck(self, config, names):
        return '\n'.join(["//DSPALST JOB (BCPL),'READ-ONLY'"] +
                         [f" LISTDS '{name}' LABEL" for name in names])

    def submit_and_wait(self, config, deck, max_rc=0):
        self.calls.append((deck, max_rc))
        return 99 + len(self.calls), 'OK'

    def job_report(self, job):
        return self.reports[job]

    def dataset_missing(self, report, name):
        return f'{name} NOT IN CATALOG' in report

    def extract_listds_block(self, report, name):
        return []

    def parse_listds(self, block):
        return {}


class TargetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.rows = [{'sequence': n} for n in range(3, 21)]
        self.dspal = {'mvs': {'hlq': 'HERC02'}, 'datasets': {
            'MR10_LOAD': {'dsn': 'BCPL.MR10KIT.LOAD'}}}
        self.names = mod.targets(self.rows, self.dspal)
        self.core = FakeCore(self.names)

    def test_exact_18_approved_names(self):
        self.assertEqual(len(self.names), 18)
        self.assertEqual(self.names[0], 'HERC02.BCPL.TA2STG.BT0003')
        self.assertEqual(self.names[-1], 'HERC02.BCPL.TA2STG.BT0020')

    def test_no_development_dsn(self):
        self.assertNotIn('HERC02.BCPL.MR10KIT.LOAD', self.names)

    def test_wrong_hlq(self):
        self.dspal['mvs']['hlq'] = 'OTHER'
        with self.assertRaisesRegex(mod.Refusal, 'HERC02'):
            mod.targets(self.rows, self.dspal)

    def test_duplicate_sequence(self):
        self.rows[1]['sequence'] = 3
        with self.assertRaisesRegex(mod.Refusal, 'canonical'):
            mod.targets(self.rows, self.dspal)

    def test_missing_sequence(self):
        with self.assertRaises(mod.Refusal):
            mod.targets(self.rows[:-1], self.dspal)

    def test_approved_name_conflict(self):
        self.dspal['datasets']['CONFLICT'] = {'dsn':'BCPL.TA2STG.BT0003'}
        with self.assertRaisesRegex(mod.Refusal, 'collides'):
            mod.targets(self.rows, self.dspal)

    def test_vtoc_jcl_is_read_only(self):
        deck = mod.vtoc_deck(self.core, {}, 'TSO002')
        self.assertIn('EXEC PGM=IEHLIST', deck)
        self.assertIn('LISTVTOC FORMAT,VOL=SYSDA=TSO002', deck)
        self.assertIn('DISP=SHR', deck)
        self.assertNotIn('DISP=NEW', deck)
        self.assertNotIn('EXEC PGM=IEFBR14', deck)
        self.assertTrue(all(len(x) <= 80 for x in deck.splitlines()))

    def test_bad_volume_refused(self):
        for vol in ('A-B', 'TOOLONG', '', 'tso002', 'ABC XYZ'):
            with self.subTest(vol=vol), self.assertRaises(mod.Refusal):
                mod.vtoc_deck(self.core, {}, vol)

    def test_catalog_absence(self):
        mod.catalog_absence(self.core, self.core.reports[100], self.names)

    def test_missing_absence_one_refused(self):
        report = self.core.reports[100].replace(self.names[0] + ' NOT IN CATALOG', '')
        with self.assertRaisesRegex(mod.Refusal, 'catalog-absence'):
            mod.catalog_absence(self.core, report, self.names)

    def test_contradictory_attributes_refused(self):
        self.core.extract_listds_block = lambda report, name: ['VOLUME', 'TSO002']
        self.core.parse_listds = lambda block: {'dsorg': 'PO'}
        with self.assertRaisesRegex(mod.Refusal, 'contradictory'):
            mod.catalog_absence(self.core, self.core.reports[100], self.names)

    def test_wrong_count_refused(self):
        with self.assertRaises(mod.Refusal):
            mod.catalog_absence(self.core, self.core.reports[100], self.names[:-1])

    def test_vtoc_has_volume_and_utility(self):
        mod.vtoc_observation(self.core.reports[101], 'TSO002', self.names)

    def test_vtoc_missing_identity_refused(self):
        with self.assertRaisesRegex(mod.Refusal, 'identify'):
            mod.vtoc_observation('NO REPORT', 'TSO002', self.names)

    def test_vtoc_other_volume_refused(self):
        with self.assertRaisesRegex(mod.Refusal, 'identify'):
            mod.vtoc_observation(self.core.reports[101], 'TSO003', self.names)

    def test_vtoc_uncataloged_collision_refused(self):
        report = self.core.reports[101] + self.names[0] + ' 1 TSO002 1 00001\n'
        with self.assertRaisesRegex(mod.Refusal, 'VTOC collision'):
            mod.vtoc_observation(report, 'TSO002', self.names)

    def test_successful_two_job_evidence(self):
        jobs = mod.inquire(self.core, {}, self.folder, self.names, 'TSO002')
        self.assertEqual(jobs, {'catalog_job': 100, 'vtoc_job': 101})
        self.assertEqual(len(self.core.calls), 2)
        self.assertEqual(self.core.calls[0][1], 8)
        self.assertEqual(self.core.calls[1][1], 0)
        self.assertEqual((self.folder/'catalog-report.txt').read_text(), self.core.reports[100])
        self.assertEqual((self.folder/'vtoc-report.txt').read_text(), self.core.reports[101])

    def test_failed_catalog_does_not_launch_vtoc(self):
        self.core.reports[100] = 'MVS failed'
        with self.assertRaises(mod.Refusal):
            mod.inquire(self.core, {}, self.folder, self.names, 'TSO002')
        self.assertEqual(len(self.core.calls), 1)
        self.assertFalse((self.folder/'vtoc-report.txt').exists())

    def test_failed_vtoc_keeps_both_reports(self):
        self.core.reports[101] = 'wrong volume'
        with self.assertRaises(mod.Refusal):
            mod.inquire(self.core, {}, self.folder, self.names, 'TSO002')
        self.assertTrue((self.folder/'vtoc-report.txt').is_file())

    def test_inquire_never_retries(self):
        self.core.submit_and_wait = lambda *args, **kwargs: (_ for _ in ()).throw(ValueError('JES refused'))
        with self.assertRaisesRegex(ValueError, 'JES refused'):
            mod.inquire(self.core, {}, self.folder, self.names, 'TSO002')
        self.assertEqual(list(self.folder.iterdir()), [])

    def test_exclusive_evidence(self):
        path = self.folder/'report.txt'
        mod.save(path, b'evidence')
        with self.assertRaises(mod.Refusal): mod.save(path, b'overwritten')
        self.assertEqual(path.read_bytes(), b'evidence')

    def test_checksum_set(self):
        mod.save(self.folder/'report.txt', b'hello')
        mod.checksums(self.folder)
        self.assertIn('report.txt', (self.folder/'SHA256SUMS').read_text())
        with self.assertRaises(mod.Refusal): mod.checksums(self.folder)

    def test_main_no_live_never_contacts_mvs(self):
        stage = Mock()
        stage.read_stage_run.return_value = ({'sources': []}, 'a'*64, b'RC=0\n')
        stage.validate_worksheet.return_value = self.rows
        source = Mock()
        canonical = Mock()
        canonical.load.side_effect = [{'phase':'design','datasets': []},self.dspal]
        source.core.return_value = canonical
        def importer(name, path):
            if name == 'ta2_target_stage_jcl': return stage
            if name == 'ta2_target_source': return source
            raise AssertionError('unwanted MVS access')
        with patch.object(mod,'import_script',side_effect=importer):
            rc = mod.main(['--stage-evidence', str(self.folder), '--volume', 'TSO002'])
        self.assertEqual(rc, 0)
        stage.verify_history.assert_called_once()

    def test_main_invalid_stage_history_stops_before_mvs(self):
        stage = Mock()
        stage.read_stage_run.return_value = ({'sources': []}, 'a'*64, b'RC=0\n')
        stage.validate_worksheet.return_value = self.rows
        stage.verify_history.side_effect = mod.Refusal('source evidence changed')
        source = Mock()
        canonical = Mock()
        canonical.load.side_effect = [{'phase':'design','datasets': []},self.dspal]
        source.core.return_value = canonical
        def importer(name, path):
            if name == 'ta2_target_stage_jcl': return stage
            if name == 'ta2_target_source': return source
            raise AssertionError('MVS access before validation')
        with patch.object(mod,'import_script',side_effect=importer):
            rc = mod.main(['--live', '--stage-evidence', str(self.folder), '--volume', 'TSO002'])
        self.assertEqual(rc, 1)

    def test_live_requires_explicit_volume(self):
        with self.assertRaises(SystemExit):
            mod.main(['--live','--stage-evidence',str(self.folder)])

    def test_failure_preserves_tmp_env(self):
        import os
        import tempfile as temp
        before_tmp = temp.tempdir
        before_env = os.environ.get('TMPDIR')
        self.core.reports[100]='catalog failure'
        with self.assertRaises(mod.Refusal):
            mod.inquire(self.core, {}, self.folder, self.names, 'TSO002')
        self.assertEqual(temp.tempdir, before_tmp)
        self.assertEqual(os.environ.get('TMPDIR'), before_env)


if __name__ == '__main__':
    unittest.main()
