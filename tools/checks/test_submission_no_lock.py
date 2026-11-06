"""Offline checks for ordinary submission paths without a WSL admission lock."""
from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
PROJECT = TOOLS.parent
SUBMIT = TOOLS / 'mvs/submit-jcl'


class NoLockSubmissionTests(unittest.TestCase):
    def test_submit_help_requires_no_mvs_state(self):
        cp = subprocess.run([str(SUBMIT), '--help'], capture_output=True,
                            text=True, check=False)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn('Usage:', cp.stdout)

    def test_missing_deck_is_rejected_before_reader(self):
        cp = subprocess.run([str(SUBMIT), '/nonexistent/BCPL-DO-NOT-SUBMIT.jcl'],
                            capture_output=True, text=True, check=False)
        self.assertEqual(cp.returncode, 66)
        self.assertIn('cannot read JCL', cp.stderr)

    def test_dspal_submission_does_not_forward_lease_fd(self):
        tree = ast.parse((TOOLS / 'datasets/dspal-core.py').read_text())
        function = next(n for n in tree.body
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and n.name == 'submit_and_wait')
        calls = [n for n in ast.walk(function) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute) and n.func.attr == 'run']
        self.assertTrue(calls)
        for call in calls:
            self.assertNotIn('pass_fds', [k.arg for k in call.keywords])

    def test_direct_mr10_socket_submit_has_no_host_lock(self):
        import importlib.util
        path = TOOLS / 'mr10/compile-and-run-core.py'
        spec = importlib.util.spec_from_file_location('test_mr10_no_lock', path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        class Socket:
            def __init__(self):
                self.deck = b''
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def sendall(self, content):
                self.deck += content

        socket = Socket()
        with tempfile.TemporaryDirectory() as tmp:
            jcl = Path(tmp) / 'in.jcl'
            jcl.write_bytes(b'//TEST JOB\n')
            with patch.object(mod, 'printer_offset', return_value=321):
                with patch.object(mod.socket, 'create_connection', return_value=socket) as connection:
                    self.assertEqual(mod.submit_job(jcl, '127.0.0.1', 3505), 321)
        self.assertEqual(socket.deck, b'//TEST JOB\n')
        connection.assert_called_once_with(('127.0.0.1', 3505), timeout=10.0)

    def test_old_gate_module_and_wrapper_are_absent(self):
        self.assertFalse((TOOLS / 'mvs/jes_submission_gate.py').exists())
        self.assertFalse((TOOLS / 'mvs/submit-jcl-core.sh').exists())
        self.assertTrue(SUBMIT.read_text().startswith('#!/usr/bin/env bash'))


if __name__ == '__main__':
    unittest.main()
