"""Offline tests for explicitly gated single-submission TA.1 job helper."""
import importlib.machinery
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main, mock
import io
import json

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'submit-ta1-job'
loader = importlib.machinery.SourceFileLoader('submit_ta1_job', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)
ROOT = Path(__file__).resolve().parents[4]


class FakeCore:
    submitted = []
    @staticmethod
    def load_config():
        return {'mvs': {'hlq': 'HERC02'}}
    @staticmethod
    def authenticated_job_card(config, job, description, redact_password):
        return [f'//{job} JOB PASSWORD=' + ('REDACTED' if redact_password else 'SECRET')]
    @classmethod
    def submit_and_wait(cls, config, deck, max_rc, *, cursor_file=None):
        cls.submitted.append((deck, max_rc, cursor_file))
        return 99, 'JOB 99 TA1AWRIT  BOOTSTRP IEBGENER RC=0000'


class TestOneShot(TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.tape = self.root / 'BTA101.aws'
        self.lockdir = self.root / 'ledger'
        FakeCore.submitted.clear()
        for key, value in [('TAPE', self.tape), ('LOCKDIR', self.lockdir)]:
            p = mock.patch.object(mod, key, value)
            p.start(); self.addCleanup(p.stop)
        self.original = mod.load_script
        def fake_loader(path, name):
            module = self.original(path, name)
            if name == 'ta1_submit_util':
                module.load_core = lambda: FakeCore
            return module
        p = mock.patch.object(mod, 'load_script', side_effect=fake_loader)
        p.start(); self.addCleanup(p.stop)

    def test_preview_does_not_submit_or_create_marker(self):
        with mock.patch.object(mod.sys, 'stdout', new_callable=io.StringIO) as out:
            self.assertEqual(mod.main(['TA1AWRIT', '--show-deck']), 0)
            self.assertIn('PASSWORD=REDACTED', out.getvalue())
            self.assertNotIn('PASSWORD=SECRET', out.getvalue())
        self.assertEqual(FakeCore.submitted, [])
        self.assertFalse(self.lockdir.exists())

    def test_missing_media_refused(self):
        self.assertEqual(mod.main(['TA1AWRIT', '--run']), 2)
        self.assertEqual(FakeCore.submitted, [])

    def test_noninteractive_refused(self):
        self.tape.write_bytes(b'scratch media')
        with mock.patch.object(mod.sys.stdin, 'isatty', return_value=False):
            self.assertEqual(mod.main(['TA1AWRIT', '--run']), 2)
        self.assertEqual(FakeCore.submitted, [])

    def test_bad_confirmation_refused(self):
        self.tape.write_bytes(b'scratch media')
        with mock.patch.object(mod.sys.stdin, 'isatty', return_value=True), \
             mock.patch('builtins.input', return_value='NO'):
            self.assertEqual(mod.main(['TA1AWRIT', '--run']), 2)
        self.assertFalse(self.lockdir.exists())

    def test_one_submission_only_and_marker_survives(self):
        self.tape.write_bytes(b'scratch media')
        with mock.patch.object(mod.sys.stdin, 'isatty', return_value=True), \
             mock.patch('builtins.input', return_value='SUBMIT TA1AWRIT BTA101'):
            self.assertEqual(mod.main(['TA1AWRIT', '--run']), 0)
            self.assertEqual(mod.main(['TA1AWRIT', '--run']), 2)
        self.assertEqual(len(FakeCore.submitted), 1)
        self.assertEqual(FakeCore.submitted[0][1], 0)
        self.assertTrue(str(FakeCore.submitted[0][2]).endswith('BTA101-TA1AWRIT.cursor.json'))
        self.assertIn('PASSWORD=SECRET', FakeCore.submitted[0][0])
        data = json.loads((self.lockdir / 'BTA101-TA1AWRIT.json').read_text())
        self.assertEqual(data['state'], 'SUBMISSION_ATTEMPTED')

    def test_failure_keeps_one_shot_marker(self):
        self.tape.write_bytes(b'scratch media')
        with mock.patch.object(mod.sys.stdin, 'isatty', return_value=True), \
             mock.patch('builtins.input', return_value='SUBMIT TA1AWRIT BTA101'), \
             mock.patch.object(FakeCore, 'submit_and_wait', side_effect=TimeoutError('uncertain')):
            self.assertEqual(mod.main(['TA1AWRIT', '--run']), 2)
        self.assertTrue((self.lockdir / 'BTA101-TA1AWRIT.json').exists())

    def test_symlink_tape_refused(self):
        self.tape.symlink_to(self.root / 'missing')
        self.assertEqual(mod.main(['TA1AR001', '--run']), 2)
        self.assertEqual(FakeCore.submitted, [])


if __name__ == '__main__':
    main()
