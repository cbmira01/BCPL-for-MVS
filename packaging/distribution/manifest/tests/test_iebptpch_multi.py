"""TA.0: fail-closed multi-MEMBER IEBPTPCH generator, no MVS execution."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'tools/distribution/prepare-iebptpch-readback.py'
SPEC = importlib.util.spec_from_file_location('ta0_iebptpch_multi', SOURCE)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class MultiPrint(unittest.TestCase):
    def setUp(self):
        self.manifest = {'datasets': [
            {'dspal_key': 'EXT_OBJ', 'kind': 'pds_unload',
             'transfer': 'iebcopy_unload',
             'target_dcb': {'dsorg': 'PO', 'recfm': 'FB', 'lrecl': 80, 'blksize': 800},
             'members': ['BCPLDEMO', 'BCPLTIME', 'BCPLQSAM']},
        ]}
        self.dspal = {'mvs': {'hlq': 'HERC02'}, 'datasets': {
            'EXT_OBJ': {'dsn': 'BCPL.EXT.OBJ', 'dsorg': 'PO', 'recfm': 'FB',
                        'lrecl': 80, 'blksize': 800, 'content_type': 'object'},
        }}

    def render(self, members):
        return mod.make_job_body(self.manifest, self.dspal,
                                 dataset_key='EXT_OBJ', members=members)

    def test_two_members_one_step(self):
        body = self.render(['BCPLTIME', 'BCPLQSAM'])
        self.assertIn('PRINT TYPORG=PO,TOTCONV=XE,MAXNAME=2', body)
        self.assertLess(body.index('MEMBER NAME=BCPLTIME'), body.index('MEMBER NAME=BCPLQSAM'))
        self.assertNotIn('BCPLDEMO', body)
        self.assertIn('DSN=HERC02.BCPL.EXT.OBJ,DISP=SHR', body)
        self.assertEqual(body.count('EXEC PGM=IEBPTPCH'), 1)
        self.assertEqual(body.count('MEMBER NAME='), 2)
        self.assertTrue(all(len(line) <= 80 for line in body.splitlines()))
        self.assertTrue(body.endswith('/*\n'))

    def test_three_members(self):
        self.assertIn('MAXNAME=3', self.render(['BCPLDEMO', 'BCPLTIME', 'BCPLQSAM']))

    def test_empty_selection_fails(self):
        with self.assertRaisesRegex(mod.PreparationError, 'one to 20'):
            self.render([])

    def test_duplicate_fails(self):
        with self.assertRaisesRegex(mod.PreparationError, 'duplicate'):
            self.render(['BCPLTIME', 'BCPLTIME'])

    def test_unselected_fails(self):
        with self.assertRaisesRegex(mod.PreparationError, 'not selected'):
            self.render(['BCPLTIME', 'FAKEMOD'])

    def test_malformed_name_fails(self):
        with self.assertRaisesRegex(mod.PreparationError, 'uppercase'):
            self.render(['BCPLTIME', 'bcplqsam'])

    def test_nonstring_name_fails(self):
        with self.assertRaisesRegex(mod.PreparationError, 'uppercase'):
            self.render(['BCPLTIME', 100])

    def test_mixed_legacy_and_multi_fails(self):
        with self.assertRaisesRegex(mod.PreparationError, 'either'):
            mod.make_job_body(self.manifest, self.dspal,
                              dataset_key='EXT_OBJ', member='BCPLTIME',
                              members=['BCPLQSAM'])

    def test_missing_selection_fails(self):
        with self.assertRaisesRegex(mod.PreparationError, 'either'):
            mod.make_job_body(self.manifest, self.dspal, dataset_key='EXT_OBJ')

    def test_dcb_mismatch_fails(self):
        self.dspal['datasets']['EXT_OBJ']['recfm'] = 'U'
        with self.assertRaisesRegex(mod.PreparationError, 'binary FB80'):
            self.render(['BCPLTIME', 'BCPLQSAM'])

    def test_cli_repeated_member(self):
        with tempfile.TemporaryDirectory() as folder:
            p1, p2 = Path(folder) / 'manifest.yaml', Path(folder) / 'dspal.yaml'
            p1.write_text(yaml.safe_dump(self.manifest))
            p2.write_text(yaml.safe_dump(self.dspal))
            base = [sys.executable, '-B', str(SOURCE), '--manifest', str(p1),
                    '--dspal', str(p2), '--dataset-key', 'EXT_OBJ']
            cp = subprocess.run(base + ['--member', 'BCPLTIME', '--member', 'BCPLQSAM'],
                                capture_output=True, text=True)
            self.assertEqual(cp.returncode, 0, cp.stderr)
            self.assertIn('MAXNAME=2', cp.stdout)
            bad = subprocess.run(base + ['--member', 'BCPLTIME', '--member', 'BCPLTIME'],
                                 capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1)
            self.assertEqual(bad.stdout, '')


if __name__ == '__main__':
    unittest.main()
