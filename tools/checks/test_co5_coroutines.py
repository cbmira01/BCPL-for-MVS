"""CO.5 host-only checks; never calls MVS, Docker, Git, or JES."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'run-coroutine-regression.py'
spec = importlib.util.spec_from_file_location('co5_native_regression', SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError('missing CO.5 native regression adapter')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class CaseFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'tests/coroutines').mkdir(parents=True)
        for ident, reference in mod.SOURCE_REFS.items():
            source = self.root / reference
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text('LET START() BE FINISH\n')
            fixture = self.root / f'tests/coroutines/{ident:03d}-example'
            fixture.mkdir()
            (fixture / 'source-reference.txt').write_text(reference + '\n')
            (fixture / 'coroutine-native.txt').write_text('candidate-source\n')
            (fixture / 'expected.txt').write_text(f'CO3BCPL INIT\nCO3BCPL PASS\n')
            (fixture / 'README.md').write_text('# Example\n')
        self.patcher = patch.object(mod, 'ROOT', self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_all_13_case_identities_and_source_references(self):
        self.assertEqual(set(mod.CASES), set(range(177, 190)))
        for ident in mod.CASES:
            with self.subTest(case=ident):
                home = self.root / f'tests/coroutines/{ident:03d}-example'
                records, source = mod.fixture(home, ident)
                self.assertEqual(len(records), 2)
                self.assertEqual(source, (self.root / mod.SOURCE_REFS[ident]).resolve())

    def test_rejects_changed_source_reference(self):
        home = self.root / 'tests/coroutines/177-example'
        (home / 'source-reference.txt').write_text('../untrusted.bcpl\n')
        with self.assertRaises(mod.RegressionError):
            mod.fixture(home, 177)

    def test_rejects_truncation_duplicate_and_non_ascii(self):
        home = self.root / 'tests/coroutines/177-example'
        f = home / 'expected.txt'
        for body in (b'CO3BCPL INIT\n', b'CO3BCPL PASS\nCO3BCPL PASS\n',
                     b'CO3BCPL PASS\xff\n', b'CO3BCPL PASS EXTRA\n'):
            with self.subTest(body=body):
                f.write_bytes(body)
                with self.assertRaises(mod.RegressionError):
                    mod.fixture(home, 177)

    def test_exact_native_steps_and_independent_compilation(self):
        receipt = {'status': 'PASS', 'installed_mvs_objects_modified': False,
                   'bcpl_records': ['INIT', 'PASS'], 'native_job': '5401',
                   'CO3ACMP_job': '5399', 'CO3LCMP_job': '5400',
                   'steps': {name: 0 for name in
                             ('ASMA', 'ASML', 'ASMM', 'ASMS', 'LKED', 'GO')}}
        oracle = ['CO3BCPL INIT', 'CO3BCPL PASS']
        mod.native_records(receipt, 181, oracle)
        for key, value in [('status', 'FAIL'), ('installed_mvs_objects_modified', True),
                           ('bcpl_records', ['PASS']), ('CO3LCMP_job', None)]:
            bad = {**receipt, key: value}
            with self.subTest(key=key), self.assertRaises(mod.RegressionError):
                mod.native_records(bad, 181, oracle)
        bad = {**receipt, 'steps': {**receipt['steps'], 'GO': 4}}
        with self.assertRaises(mod.RegressionError):
            mod.native_records(bad, 181, oracle)

    def test_one_selected_batch_case_not_entire_batch(self):
        # Verify that one runner selection invokes one accepted run_one,
        # never the three-case run_batch entry point.
        home = self.root / 'workarea/co5-coroutines'
        source = self.root / mod.SOURCE_REFS[184]
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text('LET START() BE FINISH\n')
        class Prior: pass
        class Batch:
            FIXTURE = source.parent
            CASES = {'stack': (source.name, 'CO4STK', ('ROOT', 'PASS'))}
            SAFE_RUNNER = Path('safe-runner.py')
            def __init__(self): self.runs = []
            def validate_inputs(self): return {'source': 'verified'}
            def load_module(self, name, path): return Prior()
            def run_one(self, key, session, previous, hashes):
                self.runs.append(key)
                evidence = session / key / 'proof'; evidence.mkdir(parents=True)
                record = {'status': 'PASS', 'installed_mvs_objects_modified': False,
                          'bcpl_records': ['ROOT', 'PASS'], 'native_job': '3',
                          'CO3ACMP_job': '1', 'CO3LCMP_job': '2',
                          'steps': {name: 0 for name in
                                    ('ASMA', 'ASML', 'ASMM', 'ASMS', 'LKED', 'GO')}}
                (evidence / 'result.json').write_text(json.dumps(record))
                (evidence / 'job-report.log').write_text('CO4STK ROOT\nCO4STK PASS\n')
                return {'case': key, 'status': 'PASS', 'rc': 0, 'evidence_dir': str(evidence)}
            @staticmethod
            def parse_records(report, prefix):
                return [line.split()[1] for line in report.splitlines()]
        candidate = Batch()
        with patch.object(mod, 'load_module', return_value=candidate), \
             patch.object(mod, 'WORK', home):
            evidence = mod.run_batch_case(184, Path('batch.py'), 'stack',
                         ['CO4STK ROOT', 'CO4STK PASS'], source)
        self.assertEqual(candidate.runs, ['stack'])
        self.assertTrue((evidence / 'co4-case-result.json').is_file() is False)
        self.assertTrue((evidence.parents[1] / 'case-result.json').is_file())


if __name__ == '__main__':
    unittest.main()
