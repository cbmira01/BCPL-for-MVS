"""TA.2 pure/offline and refusal tests; no MVS/Docker/Git writes."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import os
import shutil
import unittest
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / 'packaging/distribution/create-tape/scripts/ta2-offline'
loader = importlib.machinery.SourceFileLoader('ta2_offline_tests', str(SRC))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)


class TA2OfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = ROOT / 'workarea' / ('ta2-offline-test-' + str(os.getpid()))
        cls.work.mkdir(parents=True, exist_ok=False)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.work)

    def setUp(self):
        self.m = {
            'phase': 'candidate',
            'release': {'candidate_id': 'EXAMPLE', 'version': '0.1.0-rc1',
                        'source_commit': 'a' * 40, 'native_compiler': 'absent'},
            'volume': {'volser': 'Q00001', 'registry_reservation': 'EXAMPLE'},
            'generation': {'producer_sha256': mod.digest(SRC.read_bytes()),
                           'canonical_validator_sha256': mod.digest(mod.VALIDATOR.read_bytes())},
            'datasets': [
                {'sequence': 1, 'kind': 'sequential_text', 'producer_source_dsn': 'TEST.BOOT.SEQ',
                 'source_dcb': {'dsorg': 'PS', 'recfm': 'FB', 'lrecl': 80, 'blksize': 800}},
                {'sequence': 2, 'kind': 'pds_unload', 'producer_source_dsn': 'TEST.INST.PDS',
                 'members': ['INSTALL'], 'dspal_key': 'INSTALL',
                 'source_dcb': {'dsorg': 'PO', 'recfm': 'FB', 'lrecl': 80, 'blksize': 800},
                 'unload_dcb': {'dsorg': 'PS', 'recfm': 'V', 'lrecl': 816, 'blksize': 820}},
                {'sequence': 3, 'kind': 'pds_unload', 'producer_source_dsn': 'TEST.SRC.PDS',
                 'members': ['ONE', 'TWO', 'THREE'], 'dspal_key': 'EXAMPLE',
                 'source_dcb': {'dsorg': 'PO', 'recfm': 'FB', 'lrecl': 80, 'blksize': 800},
                 'unload_dcb': {'dsorg': 'PS', 'recfm': 'VS', 'lrecl': 0, 'blksize': 6144}}
            ]
        }
        for row in self.m['datasets']:
            row['target_dcb'] = deepcopy(row['source_dcb'])
            row['member_provenance'] = {v: {'redistribution': 'approved',
                                           'rights_ref': 'reviewed', 'source_ref': 'commit'}
                                        for v in row.get('members', [])}
        self.dspal = {'datasets': {'EXAMPLE': {'members': {'ONE': 'example/one.bcpl',
                                                          'TWO': 'example/two.bcpl',
                                                          'THREE': 'example/three.bcpl'}}}}
        self.raw = b'fixture-release-candidate-manifest\n'
        self.record = {'candidate_id': 'EXAMPLE', 'state': 'reserved', 'version': '0.1.0-rc1',
                       'source_commit': 'a' * 40, 'volser': 'Q00001',
                       'manifest_sha256': mod.digest(self.raw)}
        self.reg = {'schema_version': 1, 'candidates': [self.record]}
        self.core = SimpleNamespace(check=lambda manifest, dspal, root, release: {
            'logical_datasets': len(manifest['datasets']),
            'selected_members': 4,
        })
        for row in self.m['datasets']:
            n = row['sequence']
            dsn = row['producer_source_dsn']
            row['producer_source_volume'] = 'TSO003'
            stat = f'RC=0\nDATASET:   {dsn}\nVOLUME:   TSO003\n'
            for k, v in row['source_dcb'].items():
                stat += f'{k.upper()}:   {v}\n'
            attachments = {'stat': stat}
            if n > 1:
                attachments['ls'] = 'RC=0\n' + dsn + ':\n' + ''.join(
                    '    ' + mem + '\n' for mem in row['members'])
            row['mvs_inventory_receipt'] = {}
            for name, content in attachments.items():
                p = self.work / f'evidence{n}-{name}.txt'
                p.write_text(content)
                row['mvs_inventory_receipt'][name] = {
                    'path': p.relative_to(ROOT).as_posix(),
                    'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}

    def check(self):
        return mod.check_candidate(self.m, self.dspal, self.reg, ROOT, self.raw,
                                   self.core, check_git=False)

    def rewrite_receipt(self, n, part, change):
        receipt = self.m['datasets'][n - 1]['mvs_inventory_receipt'][part]
        path = ROOT / receipt['path']
        path.write_text(change(path.read_text()))
        receipt['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()

    def test_failed_stat_inquiry_refused_even_with_good_fields(self):
        self.rewrite_receipt(3, 'stat', lambda s: s.replace('RC=0', 'RC=2', 1))
        with self.assertRaisesRegex(mod.Refusal, 'successful inquiry'):
            self.check()

    def test_failed_directory_inquiry_refused_even_with_good_members(self):
        self.rewrite_receipt(3, 'ls', lambda s: s.replace('RC=0', 'RC=2', 1))
        with self.assertRaisesRegex(mod.Refusal, 'successful inquiry'):
            self.check()

    def test_managed_logical_key_must_match_when_declared(self):
        row = self.m['datasets'][2]
        row['producer_source_key'] = 'EXAMPLE'
        self.rewrite_receipt(3, 'stat',
                             lambda s: s.replace('DATASET:   TEST.SRC.PDS',
                                                 'DATASET:   TEST.SRC.PDS (EXAMPLE)'))
        self.assertEqual(self.check()['logical_datasets'], 3)
        row['producer_source_key'] = 'WRONG'
        with self.assertRaisesRegex(mod.Refusal, 'logical key'):
            self.check()

    def test_unexpected_managed_key_in_unmanaged_staging_refused(self):
        self.rewrite_receipt(3, 'stat',
                             lambda s: s.replace('DATASET:   TEST.SRC.PDS',
                                                 'DATASET:   TEST.SRC.PDS (EXAMPLE)'))
        with self.assertRaisesRegex(mod.Refusal, 'logical key'):
            self.check()

    def test_ambiguous_saved_stat_heading_refused(self):
        self.rewrite_receipt(3, 'stat', lambda s: s + 'DATASET: TEST.BAD.DSN\n')
        with self.assertRaisesRegex(mod.Refusal, 'ambiguous'):
            self.check()

    def test_happy_offline_candidate(self):
        self.assertEqual(self.check()['logical_datasets'], 3)

    def test_render_uses_one_label_per_logical_dataset(self):
        j = mod.render_write_jcl(self.m)
        self.assertEqual([f'LABEL=({n},SL)' in j for n in (1, 2, 3)], [True] * 3)
        self.assertEqual(j.count('DSN=BCPL.BT'), 3)
        self.assertNotIn('BTA101', j)

    def test_render_select_is_exact_and_separate(self):
        j = mod.render_write_jcl(self.m)
        self.assertEqual(j.count(' SELECT MEMBER='), 4)
        for member in ['INSTALL', 'ONE', 'TWO', 'THREE']:
            self.assertIn(f' SELECT MEMBER=({member})', j)

    def test_render_retain_until_last_and_conditions(self):
        j = mod.render_write_jcl(self.m)
        self.assertEqual(j.count('PRIVATE,RETAIN,SER=Q00001'), 2)
        self.assertEqual(j.count('PRIVATE,SER=Q00001'), 1)
        self.assertEqual(j.count('COND=(0,NE)'), 2)
        self.assertEqual(j.count('EXEC PGM='), 3)

    def test_render_dcb_applies_to_bootstrap_only(self):
        j = mod.render_write_jcl(self.m)
        self.assertIn('DISP=(NEW,KEEP,KEEP),\n//            DCB=', j)
        self.assertEqual(j.count('//            DCB='), 1)
        self.assertNotIn('DCB=(DSORG=PO', j)

    def test_render_no_overlong_cards(self):
        j = mod.render_write_jcl(self.m)
        self.assertTrue(all(len(s) <= 80 for s in j.splitlines()))
        self.assertTrue(all(len(s) <= 71 for s in j.splitlines() if s.startswith('//')))

    def test_render_26_member_panel_no_overlength(self):
        self.m['datasets'][2]['members'] = ['M%07d' % n for n in range(26)]
        j = mod.render_write_jcl(self.m)
        self.assertEqual(j.count(' SELECT MEMBER='), 27)
        self.assertTrue(all(len(s) <= 80 for s in j.splitlines()))

    def test_bootstrap_wrong_kind_refused(self):
        self.m['datasets'][0]['kind'] = 'pds_unload'
        with self.assertRaises(mod.Refusal): mod.render_write_jcl(self.m)

    def test_sequence_gap_refused(self):
        self.m['datasets'][2]['sequence'] = 4
        with self.assertRaises(mod.Refusal): mod.render_write_jcl(self.m)

    def test_bad_member_refused(self):
        self.m['datasets'][2]['members'].append('9BAD')
        with self.assertRaises(mod.Refusal): mod.render_write_jcl(self.m)

    def test_old_scratch_volser_refused(self):
        self.m['volume']['volser'] = 'BTA102'
        with self.assertRaises(mod.Refusal): mod.render_write_jcl(self.m)

    def test_registry_duplicate_volser_refused(self):
        self.reg['candidates'].append(dict(self.record, candidate_id='OTHER'))
        with self.assertRaises(mod.Refusal): self.check()

    def test_registry_duplicate_candidate_refused(self):
        self.reg['candidates'].append(dict(self.record))
        with self.assertRaises(mod.Refusal): self.check()

    def test_registry_bad_lifecycle_refused(self):
        self.record['state'] = 'published'
        with self.assertRaises(mod.Refusal): self.check()

    def test_registry_sha_mismatch_refused(self):
        self.record['manifest_sha256'] = 'f' * 64
        with self.assertRaises(mod.Refusal): self.check()

    def test_registry_version_drift_refused(self):
        self.record['version'] = '1.0'
        with self.assertRaises(mod.Refusal): self.check()

    def test_registry_prepared_without_volser_permitted_for_other(self):
        self.reg['candidates'].append({'candidate_id': 'OTHER', 'state': 'prepared',
                                        'volser': None})
        self.assertEqual(self.check()['logical_datasets'], 3)

    def test_registry_built_without_volser_refused(self):
        self.reg['candidates'].append({'candidate_id': 'OTHER', 'state': 'built',
                                        'volser': None})
        with self.assertRaises(mod.Refusal): self.check()

    def test_missing_member_provenance_refused(self):
        del self.m['datasets'][2]['member_provenance']['TWO']['rights_ref']
        with self.assertRaises(mod.Refusal): self.check()

    def test_unpinned_mvs_receipt_refused(self):
        self.m['datasets'][1]['mvs_inventory_receipt']['stat']['sha256'] = 'f'*64
        with self.assertRaises(mod.Refusal): self.check()

    def test_receipt_outside_workarea_refused(self):
        self.m['datasets'][1]['mvs_inventory_receipt']['stat']['path'] = '../etc/passwd'
        with self.assertRaises(mod.Refusal): self.check()

    def test_wrong_source_volume_refused(self):
        self.m['datasets'][2]['producer_source_volume'] = 'TSO002'
        with self.assertRaises(mod.Refusal): self.check()

    def test_member_directory_incomplete_refused(self):
        self.m['datasets'][2]['members'].append('FOUR')
        with self.assertRaises(mod.Refusal): self.check()

    def test_invalid_receipt_shape_refused(self):
        self.m['datasets'][2]['mvs_inventory_receipt'].pop('ls')
        with self.assertRaises(mod.Refusal): self.check()

    def test_unsafe_candidate_id_refused(self):
        self.m['release']['candidate_id'] = 'BAD\n//JOB'
        with self.assertRaises(mod.Refusal): self.check()

    def test_registry_reservation_mismatch_refused(self):
        self.m['volume']['registry_reservation'] = 'OTHER'
        with self.assertRaises(mod.Refusal): self.check()

    def test_unload_dcb_missing_refused(self):
        del self.m['datasets'][2]['unload_dcb']
        with self.assertRaises(mod.Refusal): self.check()

    def test_load_mismatch_source_dcb_refused(self):
        self.m['datasets'][2]['target_dcb']['recfm'] = 'U'
        with self.assertRaises(mod.Refusal): self.check()

    def test_duplicate_staging_dsn_refused(self):
        self.m['datasets'][2]['producer_source_dsn'] = self.m['datasets'][1]['producer_source_dsn']
        with self.assertRaises(mod.Refusal): self.check()

    def test_invalid_staging_dsn_refused(self):
        self.m['datasets'][1]['producer_source_dsn'] = 'test.invalid'
        with self.assertRaises(mod.Refusal): self.check()

    def test_invalid_card_character_refused(self):
        with self.assertRaises(mod.Refusal): mod.checked_lines(['//TEST\tDD DUMMY'])

    def test_missing_registry_reservation_refused(self):
        self.reg['candidates'] = []
        with self.assertRaises(mod.Refusal): self.check()

    def test_unpinned_generator_refused(self):
        self.m['generation']['producer_sha256'] = 'f'*64
        with self.assertRaises(mod.Refusal): self.check()

    def test_unpinned_validator_refused(self):
        self.m['generation']['canonical_validator_sha256'] = 'f'*64
        with self.assertRaises(mod.Refusal): self.check()

    def test_canonical_validator_invoked(self):
        self.core.check = lambda *args, **kwargs: (_ for _ in ()).throw(mod.Refusal('canonical fails'))
        with self.assertRaisesRegex(mod.Refusal, 'canonical fails'): self.check()


if __name__ == '__main__':
    unittest.main()
