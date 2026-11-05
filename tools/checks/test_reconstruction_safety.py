"""Offline negative tests for Step 3 destructive-scope invariants."""
from reconstruction_fixtures import REQUIRED_LOGICAL
import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'reconstruction/contract.py'
spec = importlib.util.spec_from_file_location('reconstruction_contract_test', SOURCE)
mod = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class CleanupScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name) / 'workarea'
        self.work.mkdir()
        (self.work / '.gitignore').write_text('*\n')

    def test_preserves_gitignore_and_removes_regular_tree(self):
        (self.work / 'a').mkdir()
        (self.work / 'a/file').write_text('discard')
        (self.work / 'z').write_text('discard')
        approved = mod.workarea_scope(self.work)
        mod.remove_workarea_contents(self.work, approved)
        self.assertEqual([p.name for p in self.work.iterdir()], ['.gitignore'])

    def test_symlink_direct_rejected(self):
        (self.work / 'escape').symlink_to(self.temp.name)
        with self.assertRaisesRegex(mod.ScopeError, 'symlink'):
            mod.workarea_scope(self.work)

    def test_nested_symlink_rejected(self):
        (self.work / 'a').mkdir()
        (self.work / 'a/escape').symlink_to('/tmp')
        with self.assertRaisesRegex(mod.ScopeError, 'symlink'):
            mod.workarea_scope(self.work)

    def test_replaced_file_same_name_rejected(self):
        item = self.work / 'item'
        item.write_text('old')
        approved = mod.workarea_scope(self.work)
        item.unlink()
        item.write_text('new')
        with self.assertRaisesRegex(mod.ScopeError, 'changed'):
            mod.remove_workarea_contents(self.work, approved)
        self.assertEqual(item.read_text(), 'new')

    def test_replaced_directory_rejected(self):
        item = self.work / 'sub'
        item.mkdir()
        approved = mod.workarea_scope(self.work)
        item.rmdir()
        item.mkdir()
        with self.assertRaisesRegex(mod.ScopeError, 'changed'):
            mod.remove_workarea_contents(self.work, approved)
        self.assertTrue(item.is_dir())

    def test_added_file_inside_directory_rejected(self):
        d = self.work / 'dir'
        d.mkdir()
        (d / 'first').write_text('first')
        approved = mod.workarea_scope(self.work)
        (d / 'second').write_text('second')
        with self.assertRaisesRegex(mod.ScopeError, 'changed'):
            mod.remove_workarea_contents(self.work, approved)
        self.assertTrue((d / 'first').exists())

    def test_unsupported_fifo_rejected(self):
        os.mkfifo(self.work / 'pipe')
        with self.assertRaisesRegex(mod.ScopeError, 'unsupported'):
            mod.workarea_scope(self.work)

    def test_bind_mount_from_mountinfo_rejected(self):
        (self.work / 'mounted').mkdir()
        with self.assertRaisesRegex(mod.ScopeError, 'mounted'):
            mod.workarea_scope(self.work,
              mounted=frozenset({str(self.work / 'mounted')}))

    def test_nested_bind_mount_rejected(self):
        (self.work / 'a').mkdir()
        (self.work / 'a' / 'mounted').mkdir()
        with self.assertRaisesRegex(mod.ScopeError, 'mounted'):
            mod.workarea_scope(self.work,
              mounted=frozenset({str(self.work / 'a' / 'mounted')}))

    def test_marker_symlink_rejected(self):
        (self.work / '.gitignore').unlink()
        (self.work / '.gitignore').symlink_to('/etc/passwd')
        with self.assertRaisesRegex(mod.ScopeError, 'regular file'):
            mod.workarea_scope(self.work)


class DatasetContractTests(unittest.TestCase):
    def setUp(self):
        self.cfg = {'mvs': {'hlq': 'HERC02', 'batch_user': 'HERC02',
                            'userid': 'HERC02', 'write_boundary': 'HERC02.**'},
                    'datasets': {logical: {'dsn': 'BCPL.' + logical.replace('_', '.')}
                                 for logical in REQUIRED_LOGICAL}}
        self.full = lambda cfg, spec: cfg['mvs']['hlq'] + '.' + spec['dsn']

    def test_exact_29_inventory(self):
        inv = mod.dataset_inventory(self.cfg, self.full, expected_logicals=REQUIRED_LOGICAL)
        self.assertEqual(len(inv), 29)
        self.assertIn('CAMB_LOAD', [x[0] for x in inv])
        self.assertIn('DIST_DOCS', [x[0] for x in inv])

    def test_omitted_reserved_dataset_blocks(self):
        del self.cfg['datasets']['CAMB_LOAD']
        with self.assertRaisesRegex(mod.ScopeError, 'Git-tracked'):
            mod.dataset_inventory(self.cfg, self.full, expected_logicals=REQUIRED_LOGICAL)

    def test_extra_dataset_blocks(self):
        self.cfg['datasets']['EXTRA'] = {'dsn': 'BCPL.EXTRA'}
        with self.assertRaisesRegex(mod.ScopeError, 'Git-tracked'):
            mod.dataset_inventory(self.cfg, self.full, expected_logicals=REQUIRED_LOGICAL)

    def test_namespace_escape_blocks(self):
        self.cfg['datasets']['BOOT_OBJ']['dsn'] = 'SYS1.PARMLIB'
        with self.assertRaisesRegex(mod.ScopeError, 'out-of-scope'):
            mod.dataset_inventory(self.cfg, self.full, expected_logicals=REQUIRED_LOGICAL)

    def test_alternate_identity_blocks(self):
        self.cfg['mvs']['batch_user'] = 'HERC01'
        with self.assertRaisesRegex(mod.ScopeError, 'batch_user'):
            mod.dataset_inventory(self.cfg, self.full, expected_logicals=REQUIRED_LOGICAL)

    def test_write_boundary_blocks(self):
        self.cfg['mvs']['write_boundary'] = 'HERC02.** OTHER.**'
        with self.assertRaisesRegex(mod.ScopeError, 'write boundary'):
            mod.dataset_inventory(self.cfg, self.full, expected_logicals=REQUIRED_LOGICAL)

    def test_out_of_scope_jcl_write_blocks(self):
        inventory = mod.dataset_inventory(self.cfg, self.full, expected_logicals=REQUIRED_LOGICAL)
        with self.assertRaisesRegex(mod.ScopeError, 'unapproved'):
            mod.validate_jcl('//SYSUT2 DD DSN=SYS1.PARMLIB,DISP=OLD', inventory=inventory)

    def test_out_of_scope_read_blocks(self):
        inventory = mod.dataset_inventory(self.cfg, self.full, expected_logicals=REQUIRED_LOGICAL)
        with self.assertRaisesRegex(mod.ScopeError, 'unapproved'):
            mod.validate_jcl('//SYSUT1 DD DSN=HERC02.BCPL.UNKNOWN,DISP=SHR', inventory=inventory)

    def test_normal_jcl_is_allowed(self):
        inventory = mod.dataset_inventory(self.cfg, self.full, expected_logicals=REQUIRED_LOGICAL)
        mod.validate_jcl('''//SYSLIB DD DSN=SYS1.MACLIB,DISP=SHR
//SYSUT1 DD DSN=HERC02.BCPL.BOOT.OBJ(BLIB),DISP=SHR
//SYSUT2 DD DSN=&&TMP,UNIT=SYSDA,DISP=(NEW,PASS)
''', inventory=inventory)

    def test_canonical_manifest_has_no_regression_or_release_operations(self):
        inv = mod.dataset_inventory(self.cfg, self.full, expected_logicals=REQUIRED_LOGICAL)
        manifest = mod.command_manifest(inv)
        a = mod.canonical_digest(manifest)
        self.assertEqual(a, mod.canonical_digest(manifest))
        self.assertEqual(len(manifest['operations']), 25)
        self.assertFalse(any('run-regression' in op.command[0] for op in mod.OPERATIONS))


if __name__ == '__main__':
    unittest.main()
