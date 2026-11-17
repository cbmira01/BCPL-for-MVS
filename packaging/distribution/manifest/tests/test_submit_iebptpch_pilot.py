"""TA.0 pilot submission orchestration tests; all MVS actions mocked."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
SPEC = importlib.util.spec_from_file_location('ta0_mvs_pilot',
    ROOT / 'tools/distribution/submit-iebptpch-pilot.py')
assert SPEC and SPEC.loader
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)
prep = pilot.load_python(ROOT / 'tools/distribution/prepare-iebptpch-readback.py',
                         'ta0_prep_for_pilot_test')


class FakeCore:
    def __init__(self):
        self.submissions = 0
        self.fail = False
        self.config = {
            'mvs': {'hlq': 'HERC02'},
            'datasets': {'EXT_OBJ': {'dsn': 'BCPL.EXT.OBJ', 'dsorg': 'PO',
                                     'recfm': 'FB', 'lrecl': 80, 'blksize': 800}},
        }

    def load_config(self):
        return self.config

    def full_dsn(self, config, source):
        return config['mvs']['hlq'] + '.' + source['dsn']

    def authenticated_job_card(self, config, jobname, description, redact_password):
        return ['//' + jobname + ' JOB (BCPL),\'TA0\',CLASS=A,MSGCLASS=A,',
                '//             USER=HERC02,PASSWORD=SECRET,']

    def submit_and_wait(self, config, deck, max_rc, cursor_file):
        self.submissions += 1
        if self.fail:
            raise RuntimeError('mocked submission failed')
        cursor_file.write_text('FAKE CURSOR\n')
        cursor_file.chmod(0o600)
        return 9088, 'JOB 9088 TA0MULT\nTA0HEX IEBPTPCH RC=0000\n'

    def job_report(self, job, cursor_file):
        return '13.25.35 JOB 9088 $HASP373 TA0MULT STARTED\n//TA0HEX EXEC PGM=IEBPTPCH\n'


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[4] / 'workarea')
        self.addCleanup(self.temp.cleanup)
        self.tmpdir = Path(self.temp.name)
        self.output = self.tmpdir / 'pilot'
        self.core = FakeCore()
        manifest = {'datasets': [
            {'dspal_key': 'EXT_OBJ', 'kind': 'pds_unload',
             'transfer': 'iebcopy_unload',
             'target_dcb': {'dsorg': 'PO', 'recfm': 'FB', 'lrecl': 80, 'blksize': 800},
             'members': ['BCPLDEMO', 'BCPLTIME', 'BCPLQSAM']},
        ]}
        dspal = {'mvs': {'hlq': 'HERC02'}, 'datasets': {
            'EXT_OBJ': {'dsn': 'BCPL.EXT.OBJ', 'dsorg': 'PO', 'recfm': 'FB',
                        'lrecl': 80, 'blksize': 800, 'content_type': 'object'},
        }}
        patcher = patch.object(prep, 'load_yaml',
                               side_effect=lambda path: manifest if path == prep.MANIFEST else dspal)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.patched = patch.object(pilot, 'capture_window',
                                    side_effect=lambda core, cfg, cur, output:
                                    pilot.save_private(output, b'SIMULATED RAW PRINTER BYTES\n'))
        self.patched.start()
        self.addCleanup(self.patched.stop)

    def run_one(self, members=None, **kwargs):
        return pilot.run_one(self.core, prep, key='EXT_OBJ',
                             members=members or ['BCPLTIME', 'BCPLQSAM'],
                             output=self.output, **kwargs)

    def test_success_one_read_only_mvs_job_private_complete(self):
        receipt = self.run_one()
        self.assertEqual(self.core.submissions, 1)
        self.assertEqual(receipt['job'], 9088)
        self.assertEqual(receipt['requested_members'], ['BCPLTIME', 'BCPLQSAM'])
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o700)
        self.assertEqual(len(list(self.output.iterdir())), 6)
        self.assertNotIn('PASSWORD=', (self.output / 'job-body-redacted.jcl').read_text())
        self.assertIn('MAXNAME=2', (self.output / 'job-body-redacted.jcl').read_text())
        self.assertNotIn('SECRET', (self.output / 'job-report.txt').read_text())
        self.assertEqual(set(receipt['sha256']), {
            'cursor.json', 'job-body-redacted.jcl', 'job-summary.txt',
            'job-report.txt', 'printer-window.raw'})
        for name, digest in receipt['sha256'].items():
            self.assertEqual(hashlib.sha256((self.output / name).read_bytes()).hexdigest(), digest)
            self.assertEqual((self.output / name).stat().st_mode & 0o777, 0o600)
        self.assertEqual(json.loads((self.output / 'receipt.json').read_text())['job'], 9088)
        self.assertEqual((self.output / 'receipt.json').stat().st_mode & 0o777, 0o600)

    def test_preexisting_output_fails_before_mvs(self):
        self.output.mkdir()
        with self.assertRaisesRegex(pilot.PilotError, 'new private directory'):
            self.run_one()
        self.assertEqual(self.core.submissions, 0)

    def test_relative_path_fails_before_mvs(self):
        with self.assertRaisesRegex(pilot.PilotError, 'new private directory'):
            pilot.run_one(self.core, prep, key='EXT_OBJ',
                          members=['BCPLTIME'], output=Path('relative/pilot'))
        self.assertEqual(self.core.submissions, 0)

    def test_unselected_member_fails_before_mvs(self):
        with self.assertRaisesRegex(prep.PreparationError, 'not selected'):
            self.run_one(['BCPLTIME', 'NOEXIST'])
        self.assertEqual(self.core.submissions, 0)
        self.assertFalse(self.output.exists())

    def test_wrong_active_dcb_fails_before_mvs(self):
        self.core.config['datasets']['EXT_OBJ']['recfm'] = 'U'
        with self.assertRaisesRegex(pilot.PilotError, 'DCB not FB80'):
            self.run_one()
        self.assertEqual(self.core.submissions, 0)

    def test_wrong_active_dsn_fails_before_mvs(self):
        self.core.config['datasets']['EXT_OBJ']['dsn'] = 'BCPL.UNKNOWN.OBJ'
        with self.assertRaisesRegex(pilot.PilotError, 'differs from'):
            self.run_one()
        self.assertEqual(self.core.submissions, 0)

    def test_invalid_jobname_fails_before_mvs(self):
        with self.assertRaisesRegex(pilot.PilotError, 'jobname'):
            self.run_one(jobname='verylongname')
        self.assertEqual(self.core.submissions, 0)

    def test_failed_submission_preserves_cursor_no_retry(self):
        self.core.fail = True
        with self.assertRaisesRegex(RuntimeError, 'submission failed'):
            self.run_one()
        self.assertEqual(self.core.submissions, 1)
        self.assertTrue((self.output / 'failure.txt').exists())
        self.assertNotIn('SECRET', (self.output / 'failure.txt').read_text())
        self.assertFalse((self.output / 'receipt.json').exists())

    def test_inside_checkout_rejected_before_mvs(self):
        with self.assertRaisesRegex(pilot.PilotError, 'under repository workarea/'):
            pilot.run_one(self.core, prep, key='EXT_OBJ', members=['BCPLTIME'],
                          output=ROOT / 'untracked-evidence')
        self.assertEqual(self.core.submissions, 0)


if __name__ == '__main__':
    unittest.main()
