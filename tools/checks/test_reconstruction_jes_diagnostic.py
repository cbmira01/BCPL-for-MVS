"""Offline regression tests for reconstruction JES diagnostic capture."""
from __future__ import annotations

import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'reconstruction'))
import live_entry as entry


REPLY = "16:11:41 /17.11.41           $HASP000 NO ACTIVE JOBS\n"
ECHO = (
    "16:11:41 HHC00013I '/' input entered for console 0:0009: "
    '"$DA"\n'
    "16:11:41 $DA\n"
)
UNKNOWN_DELTA = ECHO * 3 + REPLY


class DiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.messages = []
        self.commands = []
        self.real_mkstemp = tempfile.mkstemp

        # Use the production parser, but replace the live console transport.
        self.probe = entry.load_extensionless(
            Path(__file__).resolve().parents[1] / 'reconstruction/jes-idle',
            'reconstruction_diag_test_probe',
        )

    def observe(self, delta, *, diagnostic):
        class Console:
            def capture(inner, command, *, timeout, settle):
                self.commands.append((command, timeout, settle))
                return 0, delta

        def private_temp(*args, **kwargs):
            kwargs['dir'] = self.root
            return self.real_mkstemp(*args, **kwargs)

        environment = {'BCPL_RECON_JES_DIAGNOSE': '1'} if diagnostic else {}

        with patch.dict(os.environ, environment, clear=True), \
             patch.object(entry, 'load_extensionless', return_value=self.probe), \
             patch.object(self.probe, 'load_mvs_console', return_value=Console()), \
             patch.object(entry.tempfile, 'mkstemp', side_effect=private_temp):
            return entry.observe_jes(self.root, self.messages.append)

    def test_unknown_diagnostic_is_private_and_exact(self):
        ok, observations = self.observe(UNKNOWN_DELTA, diagnostic=True)
        self.assertFalse(ok)
        self.assertEqual('UNKNOWN', observations[0].state)
        self.assertEqual([('/$DA', 10.0, 2.0)], self.commands)

        files = list(self.root.glob('bcpl-reconstruction-jes-*.txt'))
        self.assertEqual(1, len(files))
        self.assertEqual(0o600, stat.S_IMODE(files[0].stat().st_mode))
        self.assertIn(repr(UNKNOWN_DELTA), files[0].read_text())
        self.assertTrue(any('PRIVATE JES diagnostic file:' in x
                            for x in self.messages))

    def test_unknown_without_opt_in_creates_no_file(self):
        ok, observations = self.observe(UNKNOWN_DELTA, diagnostic=False)
        self.assertFalse(ok)
        self.assertEqual('UNKNOWN', observations[0].state)
        self.assertEqual([], list(self.root.iterdir()))

    def test_clear_creates_no_diagnostic_file(self):
        ok, observations = self.observe(REPLY, diagnostic=True)
        self.assertTrue(ok)
        self.assertEqual(['CLEAR', 'CLEAR'],
                         [obs.state for obs in observations])
        self.assertEqual(2, len(self.commands))
        self.assertEqual([], list(self.root.iterdir()))

    def test_unknown_never_becomes_authorization(self):
        ok, observations = self.observe(UNKNOWN_DELTA, diagnostic=True)
        self.assertFalse(ok)
        self.assertNotEqual('CLEAR', observations[0].state)
        self.assertFalse(all(obs.state == 'CLEAR' for obs in observations))


if __name__ == '__main__':
    unittest.main()
