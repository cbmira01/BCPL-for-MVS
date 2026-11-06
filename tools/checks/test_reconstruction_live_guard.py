"""Offline-only proof that the live guard path cannot invoke reconstruction."""
from __future__ import annotations

import contextlib
import importlib.machinery
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
RECON = TOOLS / 'reconstruction'
sys.path.insert(0, str(RECON))
sys.path.insert(0, str(TOOLS / 'mvs'))
import jes_submission_gate as gate

CHILD = """\
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
from jes_submission_gate import admit, SubmissionDenied
try:
    with admit(Path(sys.argv[2])):
        print('ALLOWED')
except SubmissionDenied:
    print('BLOCKED')
"""

loader = importlib.machinery.SourceFileLoader('reconstruction_guard_only_tests', str(RECON / 'run'))
run = types.ModuleType(loader.name)
run.__file__ = str(RECON / 'run')
loader.exec_module(run)


class LiveGuardOnlyTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / 'mvs-state').mkdir()
        self.messages = []
        # Fail if the test-only path ever tries to enter the stage engine.
        self.engine_patch = patch.object(run, 'Runner', side_effect=AssertionError('runner invoked'))
        self.engine_patch.start()
        self.addCleanup(self.engine_patch.stop)

    def fake_observe(self, states):
        def observe(root, emit):
            self.assertEqual(root, self.root)
            self.assertIsNotNone(gate.child_pass_fds(root))
            self.assertEqual(len(gate.child_pass_fds(root)), 1,
                             'JES inquiry must execute under exclusive project lease')
            # Other clients cannot open an ordinary submission window.
            child = subprocess.run(
                [sys.executable, '-B', '-c', CHILD,
                 str(TOOLS / 'mvs'), str(root)],
                capture_output=True, text=True,
                env={k: v for k, v in os.environ.items() if k != gate.ENV_FD},
                check=False)
            self.assertEqual(child.returncode, 0, child.stderr)
            self.assertIn('BLOCKED', child.stdout)
            emit('Synthetic JES evidence')
            return (all(s == 'CLEAR' for s in states),
                    [types.SimpleNamespace(state=s) for s in states])
        return observe

    def test_clear_exits_safely_and_releases_lock(self):
        rc = run.check_live_guard(self.root, observe=self.fake_observe(['CLEAR','CLEAR']),
                                  emit=self.messages.append)
        self.assertEqual(rc, 0)
        self.assertIn('no reconstruction attempted', self.messages[-1])
        with gate.admit(self.root):
            pass

    def test_active_blocks_before_any_engine(self):
        rc = run.check_live_guard(self.root, observe=self.fake_observe(['ACTIVE']),
                                  emit=self.messages.append)
        self.assertEqual(rc, 2)
        self.assertIn('BLOCKED', self.messages[-1])
        with gate.admit(self.root):
            pass

    def test_ambiguous_observation_fails_closed(self):
        for result in (None, True, (True, []), (True, [types.SimpleNamespace(state='CLEAR')])):
            with self.subTest(result=result):
                rc = run.check_live_guard(self.root,
                      observe=lambda root,emit: result, emit=self.messages.append)
                self.assertEqual(rc, 2)
        with gate.admit(self.root):
            pass

    def test_exceptions_do_not_leak_secrets_and_release_lock(self):
        secret = 'SYNTHETIC_SECRET_4808'
        def broken(root,emit):
            raise RuntimeError('password=' + secret)
        rc = run.check_live_guard(self.root, observe=broken, emit=self.messages.append)
        self.assertEqual(rc, 2)
        self.assertNotIn(secret, '\n'.join(self.messages))
        with gate.admit(self.root):
            pass

    def test_cli_routes_only_check_flag_to_read_only_path(self):
        with patch.object(run, 'check_live_guard', return_value=19) as mock:
            with patch.object(sys, 'argv', ['run', '--check-live-guard']):
                self.assertEqual(run.main(), 19)
            mock.assert_called_once_with(run.ROOT)

    def test_check_flag_is_exclusive_with_run(self):
        with patch.object(sys,'argv',['run','--check-live-guard','--run']):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as cm:
                    run.main()
        self.assertEqual(cm.exception.code, 2)

    def test_no_lock_directory_cannot_accidentally_proceed(self):
        os.chmod(self.root/'mvs-state', 0o700)
        (self.root/'mvs-state/locks').mkdir(mode=0o700)
        (self.root/'mvs-state/locks').chmod(0o777)
        called=[]
        def should_not_run(*args):
            called.append(1)
            return (True,[types.SimpleNamespace(state='CLEAR')]*2)
        self.assertEqual(run.check_live_guard(self.root, observe=should_not_run,
                        emit=self.messages.append), 2)
        self.assertEqual(called, [])


if __name__ == '__main__':
    unittest.main()
