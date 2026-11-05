"""Offline planner regression tests under the Step 3 managed-scope contract."""
from __future__ import annotations

import importlib.machinery
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest

from reconstruction_fixtures import REQUIRED_LOGICAL

TOOLS = Path(__file__).resolve().parents[1]
RECON = TOOLS / 'reconstruction'
sys.path.insert(0, str(RECON))


def load_plan():
    loader = importlib.machinery.SourceFileLoader('reconstruction_plan_legacy_suite', str(RECON / 'plan'))
    mod = types.ModuleType(loader.name)
    mod.__file__ = str(RECON / 'plan')
    loader.exec_module(mod)
    return mod


plan = load_plan()


class FakeCore:
    def __init__(self):
        self.config = {
            'mvs': {'hlq': 'HERC02', 'batch_user': 'HERC02', 'userid': 'HERC02',
                    'write_boundary': 'HERC02.**', 'batch_password': 'SECRET'},
            'datasets': {logical: {
                'dsn': 'BCPL.' + logical.replace('_', '.'), 'type': 'pds',
                'populate': False, 'members': {}, 'generated_members': {},
            } for logical in sorted(REQUIRED_LOGICAL)}
        }
        self.config['datasets']['MR10_JCL']['members']['IC19BLD'] = 'src/IC19BLD'
        for member in plan.REQUIRED_BUILD_MEMBERS['BOOT_JCL']:
            self.config['datasets']['BOOT_JCL']['members'][member] = 'src/' + member
        self.config['datasets']['BOOT_SOURCE']['members']['LIBHDR'] = 'src/libhdr'
        self.config['datasets']['BOOT_SOURCE']['generated_members']['TRNA'] = 'workarea/bootstrap/trna'

    def load_config(self):
        return self.config

    def load_simple_yaml(self, path):
        return {'datasets': {x: {} for x in REQUIRED_LOGICAL}}

    @staticmethod
    def full_dsn(cfg, spec):
        return cfg['mvs']['hlq'] + '.' + spec['dsn']

    @staticmethod
    def cheap_status(cfg):
        return {'container': (True, 'running'), 'reader': (True, 'reader')}


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.core = FakeCore()
        self.git('init', '-q', '-b', 'main')
        (self.root / 'workarea').mkdir()
        (self.root / 'workarea/.gitignore').write_text('*\n!.gitignore\n')
        for name in plan.REQUIRED_TOOLS:
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('fixture\n')
        for spec in self.core.config['datasets'].values():
            for name in spec.get('members', {}).values():
                p = self.root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text('//* fixture\n')
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 'commit', '-qm', 'fixture')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True,
                              capture_output=True, text=True).stdout

    def result(self, probe=False):
        return plan.prepare(self.root, self.core, probe)

    def test_clean_read_only_repeatable_and_exact_manifest(self):
        before = self.git('status', '--porcelain')
        a, errors = self.result()
        b, errors_b = self.result()
        self.assertEqual(a, b)
        self.assertEqual(errors, errors_b)
        self.assertFalse(errors, errors)
        self.assertIn('Approved dataset count: 29', a)
        self.assertIn('Guide 9: Install BCPLQSAM', a)
        self.assertNotIn('SECRET', a)
        self.assertEqual(before, self.git('status', '--porcelain'))

    def test_probe(self):
        report, errors = self.result(probe=True)
        self.assertFalse(errors, errors)
        self.assertIn('Connectivity container: READY', report)

    def test_missing_input_blocked(self):
        (self.root / 'src/libhdr').unlink()
        _, errors = self.result()
        self.assertTrue(any('Missing/unsafe tracked source' in e for e in errors))

    def test_dirty_checkout_blocked(self):
        (self.root / 'untracked').write_text('bad')
        _, errors = self.result()
        self.assertTrue(any('uncommitted or untracked' in e for e in errors))

    def test_scope_escape_blocked(self):
        self.core.config['datasets']['BOOT_SOURCE']['dsn'] = 'SYS1.PARMLIB'
        _, errors = self.result()
        self.assertTrue(any('out-of-scope DSN' in e for e in errors))

    def test_duplicate_dsn_blocked(self):
        self.core.config['datasets']['BOOT_SOURCE']['dsn'] = 'BCPL.BOOT.JCL'
        _, errors = self.result()
        self.assertTrue(any('duplicate managed dataset' in e for e in errors))

    def test_generated_outside_workarea_blocked(self):
        self.core.config['datasets']['BOOT_SOURCE']['generated_members']['TRNA'] = 'src/trna'
        _, errors = self.result()
        self.assertTrue(any('Generated input escapes workarea' in e for e in errors))

    def test_missing_required_jcl_blocked(self):
        del self.core.config['datasets']['BOOT_JCL']['members']['BLIBBLD']
        _, errors = self.result()
        self.assertTrue(any('BOOT_JCL(BLIBBLD)' in e for e in errors))

    def test_workarea_symlink_blocked(self):
        (self.root / 'workarea/.gitignore').unlink()
        (self.root / 'workarea').rmdir()
        (self.root / 'workarea').symlink_to(self.root / 'src')
        _, errors = self.result()
        self.assertTrue(any('workarea must not be a symlink' in e for e in errors))

    def test_extra_tracked_workarea_file_blocked(self):
        (self.root / 'workarea/tracked').write_text('bad')
        self.git('add', '-f', 'workarea/tracked')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 'commit', '-qm', 'extra')
        _, errors = self.result()
        self.assertTrue(any('Unexpected tracked files' in e for e in errors))

    def test_public_configuration_digest_excludes_passwords(self):
        cfg = self.core.load_config()
        first = plan.public_config_digest(cfg)
        cfg['mvs']['batch_password'] = 'NEW SECRET'
        self.assertEqual(first, plan.public_config_digest(cfg))
        cfg['mvs']['hlq'] = 'OTHER'
        self.assertNotEqual(first, plan.public_config_digest(cfg))

    def test_preview_includes_public_configuration_digest(self):
        report, errors = self.result()
        self.assertFalse(errors, errors)
        self.assertIn('Effective non-secret config SHA-256:', report)

    def test_probe_failure_blocked(self):
        self.core.cheap_status = lambda _cfg: {'reader': (False, 'offline')}
        _, errors = self.result(probe=True)
        self.assertTrue(any('Connectivity unavailable' in e for e in errors))

    def test_unapproved_jcl_read_blocked(self):
        (self.root / 'src/BLDBMAIN').write_text('//IN DD DSN=SYS1.PARMLIB,DISP=SHR\n')
        self.git('add', 'src/BLDBMAIN')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'read-only fixture')
        _, errors = self.result()
        self.assertFalse(errors, errors)  # explicit IBM read-only DD is permitted
        (self.root / 'src/BLDBMAIN').write_text('//OUT DD DSN=SYS1.PARMLIB,DISP=OLD\n')
        self.git('add', 'src/BLDBMAIN')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'write fixture')
        _, errors = self.result()
        self.assertTrue(any('Unapproved JCL' in e for e in errors))

    def test_unapproved_extra_inventory_blocked(self):
        self.core.config['datasets']['UNKNOWN'] = {'dsn': 'BCPL.UNKNOWN'}
        _, errors = self.result()
        self.assertTrue(any('effective inventory differs' in e for e in errors))


if __name__ == '__main__':
    unittest.main()
