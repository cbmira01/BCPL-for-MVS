"""Synthetic retained-evidence fixtures. Never contacts or claims results from MVS."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import test_binary_build_chain as fixtures

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / 'tools/distribution/audit-mvs-build-evidence.py'
spec = importlib.util.spec_from_file_location('ta0_evidence_under_test', SRC)
assert spec and spec.loader
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
SHA = 'a' * 40


class OfflineMvsEvidence(unittest.TestCase):
    def setUp(self):
        self.helper = fixtures.BinaryChainAudit()
        self.helper.setUp()
        self.addCleanup(self.helper.doCleanups)
        self.root = self.helper.root
        self.manifest, self.dspal = self.helper.manifest, self.helper.dspal
        self.folder = self.root / 'evidence'
        self.folder.mkdir()
        jobs = []
        for i, (name, steps) in enumerate(fixtures.STEPS.items(), 1):
            payload = i * 10 + 1
            summary = [f'JOB {payload} {name}']
            for step in steps:
                program = audit.verify.EXPECTED_PROGRAMS[name].get(step, 'UNKNOWN')
                summary.append(f'{step} {program} RC=0000')
            summary.extend(['JOB RESULT: SUCCESS', 'HIGHEST RC: 0000', 'Highest severity: 0'])
            report = ['HIGHEST SEVERITY WAS 0'] * audit.verify.ASSEMBLER_COUNTS[name]
            report += ['CODE=0'] * audit.verify.CODE_COUNTS.get(name, 0)
            jobs.append({'name': name, 'launcher_job': payload - 1,
                         'payload_job': payload,
                         'summary': self._put(f'jobs/{name}-summary.txt', '\n'.join(summary) + '\n'),
                         'report': self._put(f'jobs/{name}-report.txt', '\n'.join(report) + '\n')})
        inventories = []
        for key in audit.chain.BINARY_KEYS:
            row = next(r for r in self.manifest['datasets'] if r.get('dspal_key') == key)
            dsn = 'HERC02.' + self.dspal['datasets'][key]['dsn']
            contents = f'{dsn}:\n' + ''.join(f'    {m}\n' for m in row['members'])
            inventories.append({'dataset_key': key,
                                'file': self._put(f'inventories/{key}.txt', contents)})
        self.index = {'schema_version': 1, 'source_git_sha': SHA, 'hlq': 'HERC02',
                      'jobs': jobs, 'inventories': inventories}
        self.index_path = self.folder / 'index.json'
        self._save()

    def _put(self, name, content):
        path = self.folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        data = content.encode('utf-8') if isinstance(content, str) else content
        path.write_bytes(data)
        return {'path': name, 'sha256': hashlib.sha256(data).hexdigest()}

    def _save(self):
        self.index_path.write_text(json.dumps(self.index), encoding='utf-8')

    def run_audit(self, *, sha=SHA):
        return audit.inspect(self.index_path, expected_source_sha=sha,
                             manifest=self.manifest, dspal=self.dspal,
                             repo_root=self.root,
                             verification_path=self.root / 'tools/reconstruction/verify.py')

    def test_complete_bundle_is_structural_not_binary_acceptance(self):
        r = self.run_audit()
        self.assertEqual(r['build_jobs_verified'], 8)
        self.assertEqual(r['binary_inventories_verified'], 4)
        self.assertEqual(r['binary_provenance_plan_members'], 15)
        self.assertEqual(r['binary_members_with_actual_readback_hashes'], 0)
        self.assertEqual(r['candidate_specific_rights_approvals'], 0)
        self.assertEqual(len(r['verified_job_receipts']), 8)

    def test_source_sha_mismatch(self):
        with self.assertRaisesRegex(audit.EvidenceError, 'source Git SHA'):
            self.run_audit(sha='b' * 40)

    def test_reject_unpinned_source(self):
        with self.assertRaisesRegex(audit.EvidenceError, '--source-sha'):
            self.run_audit(sha='not a sha')

    def test_duplicate_json_key(self):
        self.index_path.write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaisesRegex(audit.EvidenceError, 'duplicate JSON'):
            self.run_audit()

    def test_unknown_schema_field(self):
        self.index['unreviewed_rights'] = 'APPROVED'
        self._save()
        with self.assertRaisesRegex(audit.EvidenceError, 'index must contain'):
            self.run_audit()

    def test_wrong_digest(self):
        (self.folder / self.index['jobs'][0]['report']['path']).write_text('corrupt')
        with self.assertRaisesRegex(audit.EvidenceError, 'digest mismatch'):
            self.run_audit()

    def test_symlink_attachment(self):
        p = self.folder / self.index['jobs'][0]['report']['path']
        original = p.read_bytes()
        p.unlink()
        target = self.folder / 'outside.txt'
        target.write_bytes(original)
        p.symlink_to(target)
        with self.assertRaisesRegex(audit.EvidenceError, 'symbolic link'):
            self.run_audit()

    def test_path_traversal(self):
        self.index['jobs'][0]['report']['path'] = '../outside.txt'
        self._save()
        with self.assertRaisesRegex(audit.EvidenceError, 'unsafe attachment path'):
            self.run_audit()

    def test_duplicate_attachment_reference(self):
        self.index['jobs'][1]['summary'] = copy.deepcopy(self.index['jobs'][0]['summary'])
        self._save()
        with self.assertRaisesRegex(audit.EvidenceError, 'attachment reused'):
            self.run_audit()

    def test_missing_job(self):
        self.index['jobs'].pop()
        self._save()
        with self.assertRaisesRegex(audit.EvidenceError, 'eight unique'):
            self.run_audit()

    def test_duplicate_build_job(self):
        self.index['jobs'][1]['name'] = self.index['jobs'][0]['name']
        self._save()
        with self.assertRaisesRegex(audit.EvidenceError, 'duplicated'):
            self.run_audit()

    def test_missing_inventory(self):
        self.index['inventories'].pop()
        self._save()
        with self.assertRaisesRegex(audit.EvidenceError, 'four binary'):
            self.run_audit()

    def test_inventory_missing_member(self):
        row = next(x for x in self.index['inventories'] if x['dataset_key'] == 'BOOT_OBJ')
        p = self.folder / row['file']['path']
        rows = p.read_text().splitlines()
        row['file'] = self._put(row['file']['path'], '\n'.join(rows[:-1]) + '\n')
        self._save()
        with self.assertRaisesRegex(audit.EvidenceError, 'listing differs'):
            self.run_audit()

    def test_nonzero_job_rc(self):
        row = self.index['jobs'][0]
        p = self.folder / row['summary']['path']
        row['summary'] = self._put(row['summary']['path'], p.read_text().replace('RC=0000', 'RC=0004', 1))
        self._save()
        with self.assertRaisesRegex(audit.EvidenceError, 'reconstruction job verification failed'):
            self.run_audit()

    def test_missing_interpreter_code_receipt(self):
        row = next(x for x in self.index['jobs'] if x['name'] == 'BLIBBLD')
        p = self.folder / row['report']['path']
        row['report'] = self._put(row['report']['path'], p.read_text().replace('CODE=0\n', ''))
        self._save()
        with self.assertRaisesRegex(audit.EvidenceError, 'expected 1 interpreted CODE=0'):
            self.run_audit()

    def test_payload_job_identity(self):
        self.index['jobs'][0]['payload_job'] = 4001
        self._save()
        with self.assertRaisesRegex(audit.EvidenceError, 'wrong/missing payload job identity'):
            self.run_audit()

    def test_launcher_equals_payload(self):
        self.index['jobs'][0]['launcher_job'] = self.index['jobs'][0]['payload_job']
        self._save()
        with self.assertRaisesRegex(audit.EvidenceError, 'invalid launcher/payload'):
            self.run_audit()

    def test_non_utf8_report(self):
        row = self.index['jobs'][0]
        row['report'] = self._put(row['report']['path'], b'\xff\xfe')
        self._save()
        with self.assertRaisesRegex(audit.EvidenceError, 'not UTF-8'):
            self.run_audit()


if __name__ == '__main__':
    unittest.main()
