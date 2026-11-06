"""Offline bootstrap child-process tests without host-side JES lease forwarding."""
from __future__ import annotations

import importlib.machinery
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]


def load_bootstrap():
    path = TOOLS / 'bootstrap/prepare-bootstrap'
    loader = importlib.machinery.SourceFileLoader('isolated_bootstrap_children_test', str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


class BootstrapChildrenTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='bcpl-bootstrap-children-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        build = self.root / 'bootstrap-toolchain/bootstrap-cambridge'
        build.mkdir(parents=True)
        (self.root / 'src').mkdir()
        (self.root / 'src/input').write_text('tracked input\n')
        (build / 'make-demoted.py').write_text(
            'from pathlib import Path\n'
            'p=Path("workarea/bootstrap-cambridge/demoted/test")\n'
            'p.parent.mkdir(parents=True,exist_ok=True)\n'
            'p.write_text("demoted")\n')
        (build / 'make-mr10-trn-large-names.py').write_text(
            'from pathlib import Path\n'
            'p=Path("workarea/bootstrap-cambridge/mr10-trn-large-names/test")\n'
            'p.parent.mkdir(parents=True,exist_ok=True)\n'
            'p.write_text("mr10")\n')
        (build / 'build-mr10-trni-large-names.sh').write_text(
            '#!/usr/bin/env bash\n'
            'printf "intcode" > workarea/bootstrap-cambridge/trni-large-names.int\n')
        self.mod = load_bootstrap()
        self.mod.ROOT = self.root
        self.mod.BASE = self.root / 'workarea/bootstrap-cambridge'
        self.mod.INPUTS = ('src/input',)
        self.mod.outputs = lambda live: (
            [self.mod.BASE / 'demoted/test',
             self.mod.BASE / ('trni-large-names.int' if live else 'mr10-trn-large-names/test')])

    def test_normal_offline_generation(self):
        with patch.object(sys, 'argv', ['prepare-bootstrap']):
            self.assertEqual(self.mod.main(), 0)
        manifest = json.loads((self.mod.BASE / 'prepare-bootstrap-manifest.json').read_text())
        self.assertFalse(manifest['trnilrg_rebuilt'])
        self.assertEqual(2, len(manifest['outputs']))

    def test_bash_trnilrg_child_runs_without_lease(self):
        with patch.object(sys, 'argv', ['prepare-bootstrap', '--with-trnilrg']):
            self.assertEqual(self.mod.main(), 0)
        manifest = json.loads((self.mod.BASE / 'prepare-bootstrap-manifest.json').read_text())
        self.assertTrue(manifest['trnilrg_rebuilt'])
        self.assertEqual(2, len(manifest['outputs']))

    def test_failed_child_does_not_leave_stale_manifest(self):
        self.mod.BASE.mkdir(parents=True)
        (self.mod.BASE / 'prepare-bootstrap-manifest.json').write_text('old')
        script = self.root / 'bootstrap-toolchain/bootstrap-cambridge/make-demoted.py'
        script.write_text('raise SystemExit(23)\n')
        with patch.object(sys, 'argv', ['prepare-bootstrap']):
            with self.assertRaises(subprocess.CalledProcessError) as error:
                self.mod.main()
        self.assertEqual(error.exception.returncode, 23)
        self.assertFalse((self.mod.BASE / 'prepare-bootstrap-manifest.json').exists())

    def test_read_only_check_inputs(self):
        with patch.object(sys, 'argv', ['prepare-bootstrap', '--check-inputs']):
            self.assertEqual(self.mod.main(), 0)
        self.assertFalse(self.mod.BASE.exists())


if __name__ == '__main__':
    unittest.main()
