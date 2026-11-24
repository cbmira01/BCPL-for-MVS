"""Offline TA.4 automatic acceptance tests; never contact MVS or ask humans."""
import json
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/ta4-mr10-automatic-acceptance'
loader = SourceFileLoader('ta4_auto_review_test', str(SCRIPT))
spec = spec_from_loader(loader.name, loader)
mod = module_from_spec(spec)
spec.loader.exec_module(mod)


def cases():
    return [{'step': f'R{i:02d}', 'name': f'case{i}',
             'checks': {k: True for k in ('test_identity', 'rp_matches_golden',
                    'interpreted_code_zero', 'exp_present', 'exp_matches_golden')},
             'golden_and_code_match': True,
             'printed_exp': ['EXP: A'], 'actual_rp': ['RP: A'],
             'interpreted_codes': [0]} for i in range(1, 13)]


class Tests(unittest.TestCase):
    def test_automatic_twelve_pass_no_signature(self):
        result = mod.automatic_cases(cases())
        self.assertEqual([r['verdict'] for r in result], ['PASS'] * 12)
        self.assertNotIn('human_verdict', result[0])

    def test_semantic_divergence_fails(self):
        for key, value in (('actual_rp', []), ('interpreted_codes', [4]),
                           ('golden_and_code_match', False)):
            entries = cases()
            entries[3][key] = value
            with self.subTest(key=key), self.assertRaises(mod.Refusal):
                mod.automatic_cases(entries)
        entries = cases()
        entries[4]['checks']['exp_matches_golden'] = False
        with self.assertRaises(mod.Refusal):
            mod.automatic_cases(entries)

    def test_missing_and_reordered_cases_fail(self):
        for entries in (cases()[:-1], list(reversed(cases()))):
            with self.assertRaises(mod.Refusal):
                mod.automatic_cases(entries)

    def test_ta4_evidence_and_receipt_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / 'evidence'
            folder.mkdir()
            marker = root / 'marker.json'
            marker.write_text(json.dumps({
                'status': 'TA4_RC4_REBUILD_DEMOS_OWNER_CONFIRMATION_CONSUMED_NO_RETRY',
                'candidate': 'BCPL-0.1.0-rc4', 'aws_sha256': mod.AWS_SHA,
                'evidence': 'evidence',
                'new_datasets': ['HERC02.BCPL.TA4R1.OBJ', 'HERC02.BCPL.TA4R1.LOAD'],
                'no_tape_operations': True, 'no_existing_pds_writes': True,
                'publication_authorized': False}))
            receipt = {'status': 'TA4_RC4_REBUILD_AND_11_17_DEMOS_MVS_PASS',
                       'candidate': 'BCPL-0.1.0-rc4', 'jobs': dict(mod.JOBS),
                       'fresh_object_pds': 'HERC02.BCPL.TA4R1.OBJ',
                       'fresh_load_pds': 'HERC02.BCPL.TA4R1.LOAD',
                       'human_12_case_signoff': 'PENDING',
                       'publication_authorized': False}
            (folder / 'result.json').write_text(json.dumps(receipt))
            for key, count, codes in (('language', 11, 33), ('bcpl', 17, 57)):
                (folder / (key + '-semantics.json')).write_text(json.dumps({
                    'mvs_job': mod.JOBS[key],
                    'run_cases': [str(n) for n in range(count)],
                    'demo_print_records': ['demo'] * count,
                    'interpreted_zero_codes': codes}))
            (folder / 'smoke-semantics.json').write_text(json.dumps({
                'mvs_job': mod.JOBS['smoke'], 'observed_test_count': 1,
                'golden_rp_and_code_match': True, 'exp_contract_met': True}))
            seal = Mock()
            with patch.object(mod, 'ROOT', root), patch.object(mod, 'TA4', folder), \
                 patch.object(mod, 'MARKER', marker):
                self.assertEqual(mod.verify_ta4(Mock(), seal), receipt)
                seal.sealed.assert_called_once()
                receipt['jobs']['bcpl'] = 9999
                (folder / 'result.json').write_text(json.dumps(receipt))
                with self.assertRaisesRegex(mod.Refusal, 'receipt differs'):
                    mod.verify_ta4(Mock(), seal)

    def test_no_signoff_argument(self):
        with patch.object(mod.sys, 'argv', ['script', '--signoff']):
            self.assertEqual(mod.main(), 2)

    def test_main_no_interaction(self):
        with patch.object(mod.sys, 'argv', ['script']), \
             patch.object(mod, 'accept', return_value=0) as called:
            self.assertEqual(mod.main(), 0)
            called.assert_called_once()


if __name__ == '__main__':
    unittest.main()
