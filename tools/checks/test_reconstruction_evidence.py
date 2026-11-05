import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'reconstruction/evidence.py'
spec = importlib.util.spec_from_file_location('reconstruction_evidence_test', SOURCE)
ev = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ev
spec.loader.exec_module(ev)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def log(self):
        return ev.EvidenceLog(self.root, git_sha='a'*40, plan_sha256='b'*64,
                              inventory=(('DIST_DOCS', 'HERC02.BCPL.DIST.DOCS'),),
                              secrets=('SuperSecret123',))

    def test_report_is_persistent_outside_workarea(self):
        run = self.log()
        run.record(1, 'Clean workarea', ('tools/clean-workarea',), 0, 'done', result='PASS')
        run.finish('SUCCESS')
        self.assertIn('mvs-state/reconstruction-evidence', str(run.directory))
        report = json.loads((run.directory / 'report.json').read_text())
        self.assertEqual(report['state'], 'SUCCESS')
        self.assertEqual(report['operations'][0]['result'], 'PASS')

    def test_partial_run_cannot_report_success(self):
        run = self.log()
        run.record(1, 'failed', ('tools/a',), 1, 'failure', result='FAIL')
        with self.assertRaises(ev.EvidenceError):
            run.finish('SUCCESS')
        run.finish('FAILED', 'needed remediation')
        self.assertEqual(json.loads((run.directory / 'report.json').read_text())['state'], 'FAILED')

    def test_redacts_credentials_in_output_and_report(self):
        run = self.log()
        run.record(1, 'secret', ('tools/a',), 0,
                   'PASSWORD=abcxyz SuperSecret123 PASSWORD = moresecret', result='PASS')
        run.detail(1, 'payload', 'my token=1234 SuperSecret123')
        run.finish('SUCCESS')
        for item in run.directory.iterdir():
            content = item.read_text()
            for secret in ('SuperSecret123', 'abcxyz', 'moresecret', '1234'):
                self.assertNotIn(secret, content)
        self.assertEqual((run.directory / 'report.json').stat().st_mode & 0o777, 0o600)

    def test_redacts_config_tree(self):
        scrub = ev.publicize({'mvs': {'batch_password': 'SuperSecret123',
                                      'hlq': 'HERC02'}}, ('SuperSecret123',))
        self.assertEqual(scrub['mvs']['batch_password'], '[REDACTED]')
        self.assertEqual(scrub['mvs']['hlq'], 'HERC02')


if __name__ == '__main__':
    unittest.main()
