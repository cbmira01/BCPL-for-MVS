"""Offline proof that the read-only JES check cannot invoke reconstruction."""
from __future__ import annotations

import contextlib
import importlib.machinery
import io
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
RECON = TOOLS / 'reconstruction'
sys.path.insert(0, str(RECON))

loader = importlib.machinery.SourceFileLoader('reconstruction_guard_only_tests', str(RECON / 'run'))
run = types.ModuleType(loader.name)
run.__file__ = str(RECON / 'run')
loader.exec_module(run)


class LiveGuardOnlyTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.messages = []
        for name in ('Runner', 'authorized_run'):
            mock = patch.object(run, name, side_effect=AssertionError(name + ' invoked'))
            mock.start()
            self.addCleanup(mock.stop)

    @staticmethod
    def observation(states):
        return (all(s == 'CLEAR' for s in states),
                [types.SimpleNamespace(state=s) for s in states])

    def test_clear_exits_without_engine_or_lock_file(self):
        def observe(root, emit):
            self.assertEqual(root, self.root)
            self.assertFalse((root / 'mvs-state').exists())
            emit('Two synthetic JES2 observations')
            return self.observation(['CLEAR', 'CLEAR'])
        rc = run.check_live_guard(self.root, observe=observe, emit=self.messages.append)
        self.assertEqual(rc, 0)
        self.assertIn('no reconstruction attempted', self.messages[-1])
        self.assertFalse((self.root / 'mvs-state').exists())

    def test_active_blocks_without_engine(self):
        result = self.observation(['ACTIVE'])
        rc = run.check_live_guard(self.root, observe=lambda root,emit: result,
                                  emit=self.messages.append)
        self.assertEqual(rc, 2)
        self.assertIn('BLOCKED', self.messages[-1])

    def test_unknown_or_ambiguous_result_blocks(self):
        bad = (None, True, False, (True, []),
               (True, [types.SimpleNamespace(state='CLEAR')]),
               self.observation(['CLEAR', 'UNKNOWN']))
        for result in bad:
            with self.subTest(result=result):
                self.assertEqual(run.check_live_guard(
                    self.root, observe=lambda root,emit: result,
                    emit=self.messages.append), 2)

    def test_observer_failure_does_not_leak_secrets(self):
        secret = 'SYNTHETIC_SECRET_4808'
        def fail(root, emit):
            raise RuntimeError('password=' + secret)
        rc = run.check_live_guard(self.root, observe=fail,
                                  emit=self.messages.append)
        self.assertEqual(rc, 2)
        self.assertNotIn(secret, '\n'.join(self.messages))
        self.assertFalse((self.root / 'mvs-state').exists())

    def test_flag_routes_to_read_only_observer(self):
        with patch.object(run, 'check_live_guard', return_value=19) as fake:
            with patch.object(sys, 'argv', ['run', '--check-live-guard']):
                self.assertEqual(run.main(), 19)
            fake.assert_called_once_with(run.ROOT)

    def test_check_flag_is_mutually_exclusive_with_run(self):
        with patch.object(sys, 'argv', ['run', '--check-live-guard', '--run']):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as cm:
                    run.main()
        self.assertEqual(cm.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
