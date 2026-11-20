"""Synthetic read-only source freeze and redistribution-triage contracts."""
from __future__ import annotations

import copy
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[4]
SRC = REPO / 'packaging/distribution/create-tape/scripts/ta2-source-lineage'
loader = SourceFileLoader('ta2_lineage_tests', str(SRC))
spec = spec_from_loader(loader.name, loader)
mod = module_from_spec(spec)
loader.exec_module(mod)


def fixture():
    design = {'schema_version': 1, 'phase': 'design', 'datasets': []}
    for n in range(1, 21):
        row = {'sequence': n, 'group': 'common', 'owner': 'test',
               'kind': 'sequential_text' if n == 1 else 'pds_unload',
               'transfer': 'sequential_standard_label' if n == 1 else 'iebcopy_unload',
               'target_dcb': {'dsorg': 'PS' if n == 1 else 'PO',
                              'recfm': 'FB', 'lrecl': 80, 'blksize': 800}}
        if n <= 2:
            row['generator'] = 'bootstrap_fb80' if n == 1 else 'installer_pds'
        else:
            row['dspal_key'] = f'LIB{n:04d}'
            row['target_dsn_template'] = f'{{HLQ}}.BCPL.LIB{n:04d}'
            row['members'] = [f'M{i:07d}' for i in range(7)]
        design['datasets'].append(row)
    design['datasets'][2]['members'].append('EXTRA')
    selected = [(row['sequence'], row['dspal_key'], member)
                for row in design['datasets'][2:] for member in row['members']]
    assert len(selected) == 127
    worksheet = {'members': []}
    frozen = {}
    for i, (n, key, member) in enumerate(selected):
        cls = 'git_source' if i < 110 else 'generated' if i < 112 else 'resident_binary'
        source = (f'richards-bcpltape/mr10/m{i:04d}' if i < 8 else
                  f'mr10-kit-compiler/source/m{i:04d}.int' if i < 55 else
                  f'bootstrap-toolchain/asm/m{i:04d}.asm') if cls == 'git_source' else (
                      f'workarea/generated/m{i:04d}.asm' if cls == 'generated' else None)
        worksheet['members'].append({
            'tape_sequence': n, 'dataset_key': key, 'member': member,
            'logical_owner': 'test', 'source_class': cls,
            'source_reference': source, 'source_hint_not_evidence':
                f'BOOT_ASM({member})' if cls == 'resident_binary' else None,
            'redistribution_review': 'UNREVIEWED', 'mvs_build_receipt': None})
        if cls == 'git_source':
            frozen[source] = ('100644', f'{i+1:040x}')
    candidate = copy.deepcopy(design)
    candidate.update({'phase': 'candidate', 'release': {
        'candidate_id': mod.CANDIDATE_ID,
        'version': '0.1.0-rc1', 'source_commit': mod.COMMIT,
        'native_compiler': 'absent'}, 'volume': {'volser': mod.VOLSER,
        'registry_reservation': mod.CANDIDATE_ID}})
    registry = {'schema_version': 1, 'candidates': [{
        'candidate_id': mod.CANDIDATE_ID, 'version': '0.1.0-rc1',
        'source_commit': mod.COMMIT, 'volser': mod.VOLSER,
        'manifest_sha256': 'a'*64, 'state': 'reserved'}]}
    return candidate, design, registry, worksheet, frozen


class TriageTests(unittest.TestCase):
    def setUp(self):
        self.candidate, self.design, self.registry, self.sheet, self.frozen = fixture()
        self.current = dict(self.frozen)
        work = REPO / 'workarea'
        work.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=work)
        self.addCleanup(self.temp.cleanup)
        self.outroot = Path(self.temp.name)
        p = patch.object(mod, 'WORKAREA', self.outroot)
        p.start()
        self.addCleanup(p.stop)

    def build(self):
        return mod.build(self.candidate, self.design, self.registry, self.sheet,
                         self.frozen, self.current, 'a'*64)

    def test_110_frozen_git_sources_without_rights_claim(self):
        result = self.build()
        self.assertEqual(result['source_summary'], {
            'git_source': 110, 'generated': 2, 'resident_binary': 15,
            'git_blob_refs_verified': 110, 'redistribution_unreviewed': 127,
            'generated_or_binary_build_receipts_pending': 17})
        self.assertEqual(len(result['sources']), 127)
        self.assertEqual(sum(bool(x['frozen_git_source_ref']) for x in result['sources']), 110)
        self.assertEqual({x['redistribution_review'] for x in result['sources']}, {'UNREVIEWED'})
        self.assertTrue(all(x['rights_ref'] is None and x['build_receipt'] is None
                            for x in result['sources']))
        self.assertEqual(result['reserved_volser'], 'BC0001')

    def test_historical_rights_not_conferred_by_git(self):
        report = self.build()
        self.assertEqual(report['sources'][0]['review_track'], 'HISTORICAL_MATERIAL_RIGHTS_REVIEW')
        self.assertEqual(report['sources'][9]['review_track'], 'HISTORICAL_DERIVATION_RIGHTS_REVIEW')
        self.assertEqual(report['sources'][80]['review_track'], 'PROJECT_OR_DERIVED_RIGHTS_REVIEW')

    def test_generated_and_binary_unproven(self):
        rows = self.build()['sources']
        self.assertEqual(rows[110]['review_track'], 'GENERATED_CHAIN_EVIDENCE_REQUIRED')
        self.assertIsNone(rows[110]['frozen_git_source_ref'])
        self.assertEqual(rows[112]['review_track'], 'MVS_BINARY_BUILD_CHAIN_REQUIRED')
        self.assertEqual(rows[112]['source_hint_not_evidence'], 'BOOT_ASM(M0000006)')

    def test_source_content_drift_refused(self):
        key = next(iter(self.current))
        self.current[key] = ('100644', 'f'*40)
        with self.assertRaisesRegex(mod.Refusal, 'changed after approved source freeze'):
            self.build()

    def test_symlink_git_source_refused(self):
        key = next(iter(self.current))
        self.current[key] = ('120000', self.frozen[key][1])
        self.frozen[key] = ('120000', self.frozen[key][1])
        with self.assertRaisesRegex(mod.Refusal, 'changed after approved source freeze'):
            self.build()

    def test_untracked_git_member_refused(self):
        key = next(iter(self.current))
        self.current.pop(key)
        with self.assertRaisesRegex(mod.Refusal, 'missing at frozen/current'):
            self.build()

    def test_unapproved_rights_cannot_be_smuggled(self):
        self.sheet['members'][0]['redistribution_review'] = 'approved'
        with self.assertRaisesRegex(mod.Refusal, 'unexpected certified'):
            self.build()

    def test_changed_candidate_identity_refused(self):
        self.candidate['volume']['volser'] = 'BC0099'
        with self.assertRaisesRegex(mod.Refusal, 'approved candidate'):
            self.build()

    def test_manifest_registry_sha_mismatch_refused(self):
        self.registry['candidates'][0]['manifest_sha256'] = 'b'*64
        with self.assertRaisesRegex(mod.Refusal, 'registry'):
            self.build()

    def test_changed_ta0_members_refused(self):
        self.candidate['datasets'][2]['members'][0] = 'ALTERED'
        with self.assertRaisesRegex(mod.Refusal, 'BT0003'):
            self.build()

    def test_changed_sheet_member_refused(self):
        self.sheet['members'][1]['member'] = 'ALTERED'
        with self.assertRaisesRegex(mod.Refusal, 'TA.0 source worksheet'):
            self.build()

    def test_changed_source_classes_refused(self):
        self.sheet['members'][109]['source_class'] = 'resident_binary'
        with self.assertRaisesRegex(mod.Refusal, 'binary source falsely represented|source provenance classes'):
            self.build()

    def test_git_path_traversal_refused(self):
        key = next(iter(self.frozen))
        self.sheet['members'][0]['source_reference'] = '../' + key
        with self.assertRaisesRegex(mod.Refusal, 'missing at frozen/current'):
            self.build()

    def test_git_tree_parser_on_real_format(self):
        tree = (b'100644 blob ' + b'a'*40 + b'\tbootstrap-toolchain/asm/a.asm\0' +
                b'100755 blob ' + b'b'*40 + b'\tmr10-kit-compiler/jcl/a.jcl\0')
        result = mod.parse_tree(tree)
        self.assertEqual(result['bootstrap-toolchain/asm/a.asm'], ('100644', 'a'*40))
        self.assertEqual(result['mr10-kit-compiler/jcl/a.jcl'], ('100755', 'b'*40))

    def test_git_tree_duplicate_rejected(self):
        row = b'100644 blob ' + b'a'*40 + b'\tpath/a\0'
        with self.assertRaisesRegex(mod.Refusal, 'repeated Git'):
            mod.parse_tree(row + row)

    def test_exclusive_report_inside_workarea(self):
        dest = self.outroot / 'source.json'
        mod.write_new(dest, self.build())
        self.assertEqual(json.loads(dest.read_text())['source_summary']['git_blob_refs_verified'], 110)
        with self.assertRaises(FileExistsError):
            mod.write_new(dest, self.build())

    def test_cannot_write_outside_workarea(self):
        dest = self.outroot / 'child'
        dest.mkdir()
        with self.assertRaisesRegex(mod.Refusal, 'workarea'):
            mod.write_new(dest / 'source.json', self.build())

    def test_evaluate_uses_existing_ta0_provenance_report(self):
        lookup = {mod.CANDIDATE:self.candidate, mod.DESIGN:self.design,
                  mod.DSPAL:{"datasets": {}}, mod.REGISTRY:self.registry}
        core = SimpleNamespace(load=Mock(side_effect=lambda name: lookup[name]),
                               check=Mock(), provenance_report=Mock(return_value=self.sheet))
        with patch.object(mod, 'load_validator', return_value=core), \
             patch.object(mod, 'source_bytes', return_value=b'approved candidate'), \
             patch.object(mod, 'sha256', return_value='a'*64), \
             patch.object(mod, 'frozen_trees', return_value=(self.frozen, self.current)) as trees:
            output = mod.evaluate()
        self.assertEqual(output['source_summary']['git_blob_refs_verified'], 110)
        core.provenance_report.assert_called_once_with(self.design, lookup[mod.DSPAL])
        core.check.assert_called_once_with(self.candidate, lookup[mod.DSPAL], mod.ROOT, release=False)
        self.assertEqual(len(trees.call_args.args[0]), 110)

    def test_git_tree_lookup_is_read_only_and_limited_to_selected_paths(self):
        one = 'bootstrap-toolchain/asm/test.asm'
        payload = b'100644 blob ' + b'a'*40 + b'\t' + one.encode() + b'\0'
        calls = []
        def mock_git(*args):
            calls.append(args)
            if args[:2] == ('symbolic-ref', '--short'):
                return b'main\n'
            if args[0] == 'cat-file':
                return b'commit\n'
            if args[0] == 'merge-base':
                return b''
            if args[0] == 'ls-tree':
                return payload
            raise AssertionError('unexpected Git request')
        with patch.object(mod, 'git_call', side_effect=mock_git):
            before, after = mod.frozen_trees([one])
        self.assertEqual(before, after)
        self.assertEqual(calls[-2], ('ls-tree', '-rz', mod.COMMIT, '--', one))
        self.assertEqual(calls[-1], ('ls-tree', '-rz', 'HEAD', '--', one))
        self.assertTrue(all(x[0] not in {'commit', 'push', 'checkout'} for x in calls))

    def test_frozen_trees_refuse_repeated_selected_path(self):
        with patch.object(mod, 'git_call', return_value=b'main'):
            with self.assertRaisesRegex(mod.Refusal, 'path selection'):
                mod.frozen_trees(['repeat', 'repeat'])

    def test_no_mvs_or_tape_operations(self):
        script = SRC.read_text()
        self.assertNotIn('submit_and_wait', script)
        self.assertNotIn('IEBGENER EXEC', script)
        self.assertNotIn('tape write', script.lower().split('def evaluate()', 1)[-1])


if __name__ == '__main__':
    unittest.main()
