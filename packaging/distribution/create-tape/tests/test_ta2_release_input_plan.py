"""Offline negative and positive tests for accepted staging-to-producer input map."""
from __future__ import annotations

import hashlib
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / 'packaging/distribution/create-tape/scripts/ta2-release-input-plan'
loader = SourceFileLoader('ta2_release_input_plan_test', str(SRC))
spec = spec_from_loader(loader.name, loader)
mod = module_from_spec(spec)
loader.exec_module(mod)


def fixture():
    rows = [
        {'sequence': 1, 'kind': 'sequential_text', 'generator': 'bootstrap_fb80',
         'target_dcb': {'dsorg': 'PS', 'recfm': 'FB', 'lrecl': 80, 'blksize': 800}},
        {'sequence': 2, 'kind': 'pds_unload', 'generator': 'installer_pds',
         'target_dcb': mod.FB}]
    for n in range(3, 21):
        rows.append({'sequence': n, 'kind': 'pds_unload',
                     'transfer': 'iebcopy_unload',
                     'dspal_key': 'MR10_LOAD' if n == 12 else ('DIST_DOCS' if n == 3 else 'KEY'),
                     'target_dcb': mod.LOAD if n == 12 else mod.FB,
                     'members': ['ICINT19'] if n == 12 else
                     ['M%07d' % v for v in range(7 if n < 19 else 5)]})
    # All 17 FB library member lists are synthetic; adjust to 126 total.
    total = sum(len(x['members']) for x in rows[2:])
    while total < 127:
        seq = next(x for x in rows if x['sequence'] == 3)
        seq['members'].append('N%07d' % total)
        total += 1
    while total > 127:
        seq = next(x for x in rows if x['sequence'] == 3)
        if len(seq['members']) > 1:
            seq['members'].pop()
        else:
            seq = next(x for x in rows if x['sequence'] == 4)
            seq['members'].pop()
        total -= 1
    manifest = {'schema_version': 1, 'phase': 'design',
                'release': {'candidate_id': None, 'version': None},
                'volume': {'volser': None}, 'datasets': rows}
    return manifest, {'mvs': {'hlq': 'HERC02'}}


class InputPlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.folder = self.root / 'accepted'
        self.folder.mkdir()
        self.manifest, self.dspal = fixture()
        self.metadata = {'status': mod.PASSED, 'original_stage_job': 9310,
                         'original_stage_evidence': mod.ACCEPTED_STAGE,
                         'volume': 'TSO002', 'pds': 18, 'selected_members': 127,
                         'mvs_jobs': {'catalog': 9311, 'members': 9312},
                         'qualification': 'record-level identity not checked'}
        self.make_receipt()
        self.patches = [patch.object(mod, 'ROOT', self.root),
                        patch.object(mod, 'ACCEPTED', self.folder),
                        patch.object(mod, 'OUTROOT', self.root)]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)

    def make_receipt(self):
        (self.folder / 'verification.json').write_text(json.dumps(self.metadata))
        for name in ['catalog-report.txt', 'members-report.txt', 'catalog-summary.txt',
                     'members-summary.txt', 'catalog-cursor.json', 'members-cursor.json']:
            (self.folder / name).write_text('Original MVS output not modified\n')
        ledger = ''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name + '\n'
                         for p in sorted(self.folder.iterdir()) if p.name != 'SHA256SUMS')
        (self.folder / 'SHA256SUMS').write_text(ledger)

    def test_passed_stage_produces_exact_map(self):
        evidence, checksum = mod.receipt(self.folder)
        plan = mod.build(self.manifest, self.dspal, evidence, checksum, 'a'*64)
        self.assertEqual(len(plan['inputs']), 20)
        self.assertEqual(len([x for x in plan['inputs'] if x['status']=='ACCEPTED_STAGING']), 18)
        self.assertEqual(plan['staging']['members'], 127)
        self.assertEqual(plan['inputs'][11]['source_dcb'], mod.LOAD)
        self.assertEqual(plan['inputs'][11]['producer_source_dsn'], 'HERC02.BCPL.TA2STG.BT0012')
        self.assertEqual([x['tape_alias'] for x in plan['inputs']],
                         [f'BCPL.BT{i:04d}' for i in range(1, 21)])
        self.assertIsNone(plan['inputs'][0]['producer_source_dsn'])
        self.assertNotIn('volser', plan)

    def test_wrong_9312_receipt_refused(self):
        self.metadata['mvs_jobs']['members'] = 9999
        self.make_receipt()
        with self.assertRaisesRegex(mod.Refusal, '9311/9312'):
            mod.receipt(self.folder)

    def test_tampered_report_refused(self):
        (self.folder / 'members-report.txt').write_text('tampered')
        with self.assertRaisesRegex(mod.Refusal, 'checksum mismatch'):
            mod.receipt(self.folder)

    def test_missing_report_refused(self):
        (self.folder / 'catalog-report.txt').unlink()
        with self.assertRaisesRegex(mod.Refusal, 'incomplete'):
            mod.receipt(self.folder)

    def test_extra_report_refused(self):
        (self.folder / 'extra.txt').write_text('foreign')
        with self.assertRaisesRegex(mod.Refusal, 'unexpected'):
            mod.receipt(self.folder)

    def test_damaged_checksum_line_refused(self):
        (self.folder / 'SHA256SUMS').write_text('bad')
        with self.assertRaisesRegex(mod.Refusal, 'malformed'):
            mod.receipt(self.folder)

    def test_untrusted_path_refused(self):
        other = self.root / 'other'; other.mkdir()
        with self.assertRaisesRegex(mod.Refusal, 'accepted'):
            mod.receipt(other)

    def test_manifest_sequence_gap_refused(self):
        self.manifest['datasets'][3]['sequence'] = 99
        with self.assertRaisesRegex(mod.Refusal, '20-entry'):
            mod.build(self.manifest, self.dspal, self.metadata, 'a'*64, 'b'*64)

    def test_misclassified_load_refused(self):
        self.manifest['datasets'][11]['target_dcb'] = mod.FB
        with self.assertRaisesRegex(mod.Refusal, 'BT0012'):
            mod.build(self.manifest, self.dspal, self.metadata, 'a'*64, 'b'*64)

    def test_wrong_load_key_refused(self):
        self.manifest['datasets'][11]['dspal_key'] = 'KEY'
        with self.assertRaisesRegex(mod.Refusal, 'BT0012'):
            mod.build(self.manifest, self.dspal, self.metadata, 'a'*64, 'b'*64)

    def test_changed_bootstrap_role_refused(self):
        self.manifest['datasets'][0]['generator'] = 'something_else'
        with self.assertRaisesRegex(mod.Refusal, 'BT0001'):
            mod.build(self.manifest, self.dspal, self.metadata, 'a'*64, 'b'*64)

    def test_wrong_total_refused(self):
        self.manifest['datasets'][2]['members'].pop()
        with self.assertRaisesRegex(mod.Refusal, 'selection count'):
            mod.build(self.manifest, self.dspal, self.metadata, 'a'*64, 'b'*64)

    def test_duplicate_member_refused(self):
        self.manifest['datasets'][2]['members'][1] = self.manifest['datasets'][2]['members'][0]
        with self.assertRaisesRegex(mod.Refusal, 'BT0003'):
            mod.build(self.manifest, self.dspal, self.metadata, 'a'*64, 'b'*64)

    def test_candidate_identity_refused(self):
        self.manifest['volume']['volser'] = 'BC9999'
        with self.assertRaisesRegex(mod.Refusal, 'identity'):
            mod.build(self.manifest, self.dspal, self.metadata, 'a'*64, 'b'*64)

    def test_plan_written_exclusively(self):
        plan=mod.build(self.manifest,self.dspal,self.metadata,'a'*64,'b'*64)
        file=self.root/'plan.json'
        mod.write_plan(file,plan)
        self.assertEqual(json.loads(file.read_text())['staging']['pds'],18)
        with self.assertRaises(FileExistsError): mod.write_plan(file,plan)

    def test_output_outside_workarea_refused(self):
        plan=mod.build(self.manifest,self.dspal,self.metadata,'a'*64,'b'*64)
        sub=self.root/'other'; sub.mkdir()
        with self.assertRaisesRegex(mod.Refusal, 'workarea'):
            mod.write_plan(sub/'plan.json',plan)


if __name__ == '__main__':
    unittest.main()
