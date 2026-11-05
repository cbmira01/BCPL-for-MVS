"""Offline tests of the read-only clean-room reconstruction planner."""
import importlib.machinery
from pathlib import Path
import subprocess
import tempfile
import types
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'reconstruction' / 'plan'


def load_plan():
    loader = importlib.machinery.SourceFileLoader('reconstruction_plan_test', str(SCRIPT))
    mod = types.ModuleType(loader.name)
    mod.__file__ = str(SCRIPT)
    loader.exec_module(mod)
    return mod


plan = load_plan()


class FakeCore:
    class DspalError(Exception):
        pass

    def __init__(self):
        self.config = {
            'mvs': {'hlq': 'HERC02', 'batch_user': 'HERC02', 'batch_password': 'SECRET'},
            'datasets': {
                'MR10_JCL': {'dsn': 'BCPL.MR10KIT.JCL', 'type': 'pds',
                             'members': {'IC19BLD': 'src/ic19.jcl'}},
                'BOOT_JCL': {'dsn': 'BCPL.BOOT.JCL', 'type': 'pds',
                             'members': {m: 'src/'+m+'.jcl' for m in plan.REQUIRED_BUILD_MEMBERS['BOOT_JCL']}},
                'BOOT_SOURCE': {'dsn': 'BCPL.BOOT.SOURCE', 'type': 'pds',
                                'members': {'LIBHDR': 'src/libhdr'},
                                'generated_members': {'TRNA': 'workarea/bootstrap/trna'}},
            },
        }

    def load_config(self):
        return self.config

    @staticmethod
    def full_dsn(config, spec):
        return config['mvs']['hlq']+'.'+spec['dsn']

    @staticmethod
    def cheap_status(config):
        return {'container': (True, 'running'), 'reader': (True, 'reader'),
                'hercules': (True, 'console')}


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.core = FakeCore()
        self.git('init', '-q', '-b', 'main')
        (self.root / 'workarea').mkdir()
        (self.root / 'workarea/.gitignore').write_text('*\n!.gitignore\n')
        for t in plan.REQUIRED_TOOLS:
            p = self.root / t
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('placeholder\n')
        for spec in self.core.config['datasets'].values():
            for src in spec.get('members', {}).values():
                p = self.root / src
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text('fixture\n')
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 'commit', '-qm', 'fixture')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True,
                              capture_output=True, text=True).stdout

    def result(self, probe=False):
        return plan.prepare(self.root, self.core, probe)

    def test_clean_read_only_and_repeatable(self):
        before = self.git('status', '--porcelain')
        a, errors = self.result()
        b, errors_b = self.result()
        self.assertEqual(a, b)
        self.assertFalse(errors)
        self.assertEqual(errors, errors_b)
        self.assertIn('Managed datasets: 3; tracked members: 8; generated members: 1', a)
        self.assertEqual(before, self.git('status', '--porcelain'))
        self.assertNotIn('SECRET', a)

    def test_probe(self):
        output, errors = self.result(probe=True)
        self.assertFalse(errors)
        self.assertIn('container: READY', output)

    def test_missing_input_is_blocked(self):
        (self.root / 'src/libhdr').unlink()
        report, errs = self.result()
        self.assertTrue(errs)
        self.assertIn('Missing tracked source', report)

    def test_dirty_checkout_is_blocked(self):
        (self.root / 'extra').write_text('dirty')
        _, errs = self.result()
        self.assertTrue(any('uncommitted' in e for e in errs))

    def test_scope_escape_is_blocked(self):
        self.core.config['datasets']['BOOT_SOURCE']['dsn'] = 'SYS1.PARMLIB'
        _, errs = self.result()
        self.assertTrue(any('outside approved BCPL' in e for e in errs))

    def test_duplicate_dsn_is_blocked(self):
        self.core.config['datasets']['BOOT_SOURCE']['dsn'] = 'BCPL.BOOT.JCL'
        _, errs = self.result()
        self.assertTrue(any('Duplicate managed dataset' in e for e in errs))

    def test_generated_outside_workarea_is_blocked(self):
        self.core.config['datasets']['BOOT_SOURCE']['generated_members']['TRNA'] = 'src/trna'
        _, errs = self.result()
        self.assertTrue(any('Generated input outside' in e for e in errs))

    def test_missing_required_jcl_is_blocked(self):
        del self.core.config['datasets']['BOOT_JCL']['members']['BLIBBLD']
        _, errs = self.result()
        self.assertTrue(any('BOOT_JCL(BLIBBLD)' in e for e in errs))

    def test_workarea_symlink_is_blocked(self):
        (self.root / 'workarea/.gitignore').unlink()
        (self.root / 'workarea').rmdir()
        (self.root / 'workarea').symlink_to(self.root / 'src')
        _, errs = self.result()
        self.assertTrue(any('symbolic link' in e for e in errs))

    def test_extra_tracked_workarea_file_is_blocked(self):
        (self.root / 'workarea/tracked').write_text('bad')
        self.git('add', '-f', 'workarea/tracked')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 'commit', '-qm', 'extra')
        _, errs = self.result()
        self.assertTrue(any('Unexpected tracked workarea' in e for e in errs))

    def test_probe_failure_is_blocked(self):
        self.core.cheap_status = lambda _cfg: {'reader': (False, 'offline')}
        _, errs = self.result(probe=True)
        self.assertTrue(any('Connectivity' in e for e in errs))


if __name__ == '__main__':
    unittest.main()
