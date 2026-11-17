"""No-MVS tests of the TA.0 workarea evidence policy and one-time move."""
from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parents[4] / 'tools/distribution'
SPEC = importlib.util.spec_from_file_location('relocate', HERE/'relocate-ta0-evidence.py')
assert SPEC and SPEC.loader
move = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(move)
LOC_SPEC = importlib.util.spec_from_file_location('locations', HERE/'ta0_evidence_paths.py')
assert LOC_SPEC and LOC_SPEC.loader
loc = importlib.util.module_from_spec(LOC_SPEC)
LOC_SPEC.loader.exec_module(loc)


class EvidenceLocations(unittest.TestCase):
    def setUp(self):
        # Tests create no files outside the repository's ignored workarea.
        suite_workarea = Path(__file__).resolve().parents[4] / 'workarea'
        self.temp = tempfile.TemporaryDirectory(dir=suite_workarea)
        self.addCleanup(self.temp.cleanup)
        top = Path(self.temp.name)
        self.repo = top/'repo'
        self.home = top/'home'
        (self.repo/'workarea').mkdir(parents=True)
        self.home.mkdir()
        self.dest = self.repo/'workarea'/move.LABEL
        self.src = self.home/move.LABEL

    def provision(self):
        self.src.mkdir(mode=0o700)
        (self.src/'SHA256SUMS').write_bytes(b'abc123\n')
        (self.src/'MR10_LOAD.txt').write_bytes(b'ICINT19\n')
        (self.src/'MR10_LOAD.stat-raw.txt').write_bytes(b'PO/U/0/6144\n')
        (self.src/'ta0-mr10-load-iehlist').mkdir()
        (self.src/'ta0-mr10-load-iehlist'/'receipt.json').write_bytes(b'{}\n')
        (self.src/'ta0-mr10-load-directory-reviewed').mkdir()
        (self.src/'ta0-mr10-load-directory-reviewed'/'directory-review.json').write_bytes(b'{}\n')
        (self.src/'ta0-ext-single-panel').mkdir()
        (self.src/'ta0-ext-single-panel'/'job-report.txt').write_bytes(b'JES\x00DATA\n')

    def test_workarea_new_and_existing(self):
        loc.guard(self.dest, new=True, root=self.repo)
        self.dest.mkdir()
        loc.guard(self.dest, new=False, root=self.repo)

    def test_reject_home_and_packaging(self):
        for outside in [self.home/'evidence', self.repo/'packaging'/'evidence', self.repo/'mvs-state'/'other']:
            with self.subTest(outside=outside), self.assertRaises(loc.EvidencePathError):
                loc.guard(outside, new=True, root=self.repo)

    def test_reject_lexical_escape(self):
        with self.assertRaises(loc.EvidencePathError):
            loc.guard(self.repo/'workarea'/'..'/'out', new=True, root=self.repo)

    def test_reject_symlink_intermediate(self):
        (self.repo/'workarea'/'bad').symlink_to(self.home, target_is_directory=True)
        with self.assertRaises(loc.EvidencePathError):
            loc.guard(self.repo/'workarea'/'bad'/'target', new=True, root=self.repo)

    def test_reject_existing_new_output(self):
        self.dest.mkdir()
        with self.assertRaises(loc.EvidencePathError):
            loc.guard(self.dest, new=True, root=self.repo)

    def test_reject_new_output_missing_parent(self):
        with self.assertRaises(loc.EvidencePathError):
            loc.guard(self.repo/'workarea'/'not-here'/'target', new=True, root=self.repo)

    def test_move_preserves_binary_and_tree(self):
        self.provision()
        original = move.scan(self.src)
        result = move.relocate(root=self.repo, home=self.home)
        self.assertEqual(result['status'], 'moved')
        self.assertFalse(self.src.exists())
        self.assertEqual(result['path'], self.dest)
        self.assertEqual(move.scan(self.dest), original)
        self.assertEqual((self.dest/'ta0-ext-single-panel'/'job-report.txt').read_bytes(), b'JES\x00DATA\n')

    def test_second_run_is_idempotent(self):
        self.provision()
        first=move.relocate(root=self.repo, home=self.home)
        second=move.relocate(root=self.repo, home=self.home)
        self.assertEqual(second['status'], 'already-local')
        self.assertEqual(first['inventory_sha256'], second['inventory_sha256'])

    def test_destination_collision_refused(self):
        self.provision()
        self.dest.mkdir()
        with self.assertRaises(move.RelocateError):
            move.relocate(root=self.repo, home=self.home)
        self.assertTrue(self.src.exists())

    def test_missing_source_refused(self):
        with self.assertRaises(move.RelocateError):
            move.relocate(root=self.repo, home=self.home)

    def test_missing_required_receipt_refused(self):
        self.provision()
        (self.src/'ta0-mr10-load-iehlist'/'receipt.json').unlink()
        with self.assertRaises(move.RelocateError):
            move.relocate(root=self.repo, home=self.home)
        self.assertTrue(self.src.exists())

    def test_nested_symlink_refused(self):
        self.provision()
        (self.src/'ta0-ext-single-panel'/'secret').symlink_to(self.home)
        with self.assertRaises(move.RelocateError):
            move.relocate(root=self.repo, home=self.home)
        self.assertTrue(self.src.exists())

    def test_hardlink_refused(self):
        self.provision()
        os.link(self.src/'SHA256SUMS', self.src/'duplicate.txt')
        with self.assertRaises(move.RelocateError):
            move.relocate(root=self.repo, home=self.home)

    def test_exdev_does_not_copy_or_delete_source(self):
        self.provision()
        with mock.patch.object(move.os,'rename', side_effect=OSError('simulated cross-device EXDEV')):
            with self.assertRaises(OSError):
                move.relocate(root=self.repo, home=self.home)
        self.assertTrue(self.src.is_dir())
        self.assertFalse(self.dest.exists())

    def test_reject_workarea_symlink(self):
        (self.repo/'workarea').rmdir()
        (self.repo/'workarea').symlink_to(self.home, target_is_directory=True)
        with self.assertRaises(loc.EvidencePathError):
            loc.guard(self.repo/'workarea'/'target', new=True, root=self.repo)

if __name__ == '__main__':
    unittest.main()
