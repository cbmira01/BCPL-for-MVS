"""CO.6 second paired contract host tests; no JES or compiler execution."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tools/coroutines/run-co6-nested.py'
SPEC = importlib.util.spec_from_file_location('co6_nested_host', SOURCE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError('CO.6 nested driver unavailable')
NESTED = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NESTED)


class CO6NestedHostTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='co6-nested-host-')
        self.addCleanup(temp.cleanup)
        fixture = Path(temp.name) / 'fixture'
        shutil.copytree(NESTED.FIXTURE, fixture)
        change = patch.object(NESTED, 'FIXTURE', fixture)
        change.start()
        self.addCleanup(change.stop)

    def test_original_eighteen_record_contract(self):
        evidence = NESTED.validate_fixture()
        self.assertEqual(len(evidence), 2)
        self.assertEqual(len(NESTED.ORACLE), 18)
        self.assertEqual(NESTED.ORACLE[-6:],
                         ('DELA', 'DELB', 'C1', 'RC', 'DELC', 'PASS'))

    def test_exact_prefix_and_order(self):
        output = '\n'.join('CO6NEST ' + s for s in NESTED.ORACLE)
        self.assertEqual(NESTED.records(output), list(NESTED.ORACLE))
        self.assertNotEqual(NESTED.records(output + '\nCO6NEST A1'),
                            list(NESTED.ORACLE))

    def test_malformed_record_rejected(self):
        with self.assertRaisesRegex(NESTED.NestedError, 'malformed'):
            NESTED.records('CO6NEST A1 EXTRA')

    def test_modified_golden_rejected(self):
        path = NESTED.FIXTURE / 'expected.txt'
        path.write_text(path.read_text().replace('CO6NEST R3', 'CO6NEST R30'))
        with self.assertRaisesRegex(NESTED.NestedError, 'golden'):
            NESTED.validate_fixture()

    def test_missing_marker_rejected(self):
        path = NESTED.FIXTURE / 'mr10.bcpl'
        path.write_text(path.read_text().replace('MARK("DELC")', 'MARK("FAIL")'))
        with self.assertRaisesRegex(NESTED.NestedError, 'DELC'):
            NESTED.validate_fixture()

    def test_wrong_native_stack_size_rejected(self):
        path = NESTED.FIXTURE / 'native.bcpl'
        path.write_text(path.read_text().replace('CREATECO(BWORK,1024)',
                                                  'CREATECO(BWORK,100)'))
        with self.assertRaisesRegex(NESTED.NestedError, 'stack'):
            NESTED.validate_fixture()

    def test_changed_implementation_specific_descriptor_rejected(self):
        path = NESTED.FIXTURE / 'mr10.bcpl'
        path.write_text(path.read_text().replace('RESUMECO(COLIST!2,0)',
                                                  'RESUMECO(COLIST!26,0)'))
        with self.assertRaisesRegex(NESTED.NestedError, 'MR10 contract'):
            NESTED.validate_fixture()

    def test_base_preflight_preserved_with_nested_configuration(self):
        first = Path('first-fixture')
        called = []
        def original():
            called.append((base.FIXTURE, base.ORACLE))
            if base.FIXTURE != first or base.ORACLE != ('FIRST',):
                raise RuntimeError('original baseline not restored')
            return {'first_verified': 'yes'}
        base = SimpleNamespace(FIXTURE=first, ORACLE=('FIRST',),
                               WORK=Path('first-work'),
                               validate_inputs=original, records=None)
        NESTED.configure(base)
        self.assertEqual(base.FIXTURE, NESTED.FIXTURE)
        self.assertEqual(base.ORACLE, NESTED.ORACLE)
        self.assertEqual(base.WORK, NESTED.WORK)
        result = base.validate_inputs()
        self.assertEqual(result['first_verified'], 'yes')
        self.assertEqual(len(called), 1)
        self.assertEqual(called[0], (first, ('FIRST',)))
        self.assertEqual(base.FIXTURE, NESTED.FIXTURE)
        self.assertEqual(base.ORACLE, NESTED.ORACLE)
        self.assertEqual(base.records('CO6NEST A1'), ['A1'])

    def test_failed_base_preflight_blocks(self):
        base = SimpleNamespace(FIXTURE=Path('first'), ORACLE=('FIRST',),
                               WORK=Path('first-work'),
                               validate_inputs=lambda: (_ for _ in ()).throw(
                                   ValueError('old verified contract changed')),
                               records=None)
        NESTED.configure(base)
        with self.assertRaisesRegex(ValueError, 'old verified'):
            base.validate_inputs()
        self.assertEqual(base.FIXTURE, NESTED.FIXTURE)
        self.assertEqual(base.ORACLE, NESTED.ORACLE)


if __name__ == '__main__':
    unittest.main()
