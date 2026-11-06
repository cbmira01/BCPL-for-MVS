"""Offline regression for passing a reconstruction JES lease through bootstrap's Bash child."""
from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS / 'mvs'))
from jes_submission_gate import admit, controller_window, SubmissionDenied


def load_bootstrap():
    path = TOOLS / 'bootstrap/prepare-bootstrap'
    loader = importlib.machinery.SourceFileLoader('isolated_bootstrap_lease_test', str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


class BootstrapLeaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='bcpl-bootstrap-lease-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'mvs-state').mkdir()
        (self.root / 'bootstrap-toolchain/bootstrap-cambridge').mkdir(parents=True)
        (self.root / 'tools/mr10').mkdir(parents=True)
        (self.root / 'src').mkdir()
        (self.root / 'src/input').write_text('tracked input\n')
        script_dir = self.root / 'bootstrap-toolchain/bootstrap-cambridge'
        (script_dir/'make-demoted.py').write_text(
            'from pathlib import Path\n'
            'p=Path("workarea/bootstrap-cambridge/demoted/test")\n'
            'p.parent.mkdir(parents=True,exist_ok=True)\n'
            'p.write_text("demoted")\n')
        (script_dir/'build-mr10-trni-large-names.sh').write_text(
            '#!/usr/bin/env bash\n'
            'tools/mr10/compile-and-run\n'
            'rc=$?\n'
            'if [ "$rc" -ne 0 ]; then exit "$rc"; fi\n'
            'printf "intcode" > workarea/bootstrap-cambridge/trni-large-names.int\n')
        helper = self.root/'tools/mr10/compile-and-run'
        helper.write_text(
            '#!/usr/bin/env python3\n'
            'import sys\nfrom pathlib import Path\n'
            f'sys.path.insert(0, {str(TOOLS / "mvs")!r})\n'
            'from jes_submission_gate import admit, SubmissionDenied\n'
            'try:\n'
            f'    with admit(Path({str(self.root)!r})): print("MR10 ADMITTED")\n'
            'except SubmissionDenied as e:\n'
            '    print("MR10 BLOCKED", e, file=sys.stderr)\n'
            '    sys.exit(77)\n')
        helper.chmod(0o700)
        self.mod = load_bootstrap()
        self.mod.ROOT = self.root
        self.mod.BASE = self.root/'workarea/bootstrap-cambridge'
        self.mod.INPUTS = ('src/input',)
        self.mod.outputs = lambda include: (
            [self.mod.BASE/'demoted/test', self.mod.BASE/'trni-large-names.int']
            if include else [self.mod.BASE/'demoted/test'])

    def test_nested_bootstrap_exec_preserves_exclusive_lease(self):
        with controller_window(self.root):
            with patch.object(sys, 'argv', ['prepare-bootstrap', '--with-trnilrg']):
                self.assertEqual(self.mod.main(), 0)
        data = json.loads((self.mod.BASE/'prepare-bootstrap-manifest.json').read_text())
        self.assertTrue(data['trnilrg_rebuilt'])
        self.assertEqual(2, len(data['outputs']))

    def test_standalone_bootstrap_without_lease_still_works(self):
        with patch.object(sys,'argv', ['prepare-bootstrap','--with-trnilrg']):
            self.assertEqual(self.mod.main(), 0)

    def test_bootstrap_detects_missing_fd_if_removed(self):
        import jes_submission_gate as gate
        original = self.mod.child_pass_fds
        try:
            self.mod.child_pass_fds = lambda _: ()
            with gate.controller_window(self.root):
                with patch.object(sys,'argv',['prepare-bootstrap','--with-trnilrg']):
                    with self.assertRaises(subprocess.CalledProcessError):
                        self.mod.main()
                self.assertFalse((self.mod.BASE/'prepare-bootstrap-manifest.json').exists())
        finally:
            self.mod.child_pass_fds = original


if __name__ == '__main__':
    unittest.main()
