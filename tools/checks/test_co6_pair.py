"""CO.6 host-only isolated oracle and adapter safety checks; no MVS calls."""
from __future__ import annotations

import hashlib
import importlib.util
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tools/coroutines/run-co6-pair.py'
SPEC = importlib.util.spec_from_loader(
    'co6_pair_tests', SourceFileLoader('co6_pair_tests', str(SOURCE)))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError('CO.6 source cannot be loaded')
PAIR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PAIR)


class CO6PairHostTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='co6-pair-host-')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        fixture = self.root / 'fixture'
        shutil.copytree(PAIR.FIXTURE, fixture)
        patcher = patch.object(PAIR, 'FIXTURE', fixture)
        patcher.start()
        self.addCleanup(patcher.stop)
        # All disposable dependencies live in this isolated temporary root.
        accepted = self.root / 'accepted'
        accepted.mkdir()
        pin_accept = patch.object(PAIR, 'ACCEPTED', accepted)
        pin_accept.start()
        self.addCleanup(pin_accept.stop)
        for attr in ('MR10', 'ICINT', 'CO3_DRIVER', 'CO3_ADAPTER',
                     'SUMMARY', 'REPORT'):
            dest = self.root / (attr.lower() + '.fixture')
            dest.write_text('host fixture\n')
            patcher = patch.object(PAIR, attr, dest)
            patcher.start()
            self.addCleanup(patcher.stop)
        modules = tuple(self.root / f'module-{i}.bcpl' for i in range(2))
        for item in modules:
            item.write_text('host fixture\n')
        patcher = patch.object(PAIR, 'MR10_MODULES', modules)
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in PAIR.DEPENDENCY_GIT_BLOBS:
            (accepted / name).write_text('host fixture\n')
        fake_blobs = {}
        for name in PAIR.DEPENDENCY_GIT_BLOBS:
            path = PAIR.ACCEPTED / name
            if name == 'cambridge-parm.txt':
                path.write_text('/CN' + '/'*77 + '\n')
            raw = path.read_bytes()
            fake_blobs[name] = hashlib.sha1(
                f'blob {len(raw)}\0'.encode('ascii') + raw).hexdigest()
        pin = patch.object(PAIR, 'DEPENDENCY_GIT_BLOBS', fake_blobs)
        pin.start()
        self.addCleanup(pin.stop)

    def test_inputs_have_eleven_exact_markers(self):
        hashes = PAIR.validate_inputs()
        self.assertEqual(len(hashes), 2)
        self.assertEqual(len(PAIR.ORACLE), 11)
        self.assertEqual(PAIR.ORACLE[-2:], ('DEL', 'PASS'))

    def test_modified_oracle_refused(self):
        path = PAIR.FIXTURE / 'expected.txt'
        path.write_text(path.read_text().replace('CO6PAIR R2', 'CO6PAIR R99'))
        with self.assertRaisesRegex(PAIR.PairError, 'golden'):
            PAIR.validate_inputs()

    def test_missing_source_marker_refused(self):
        path = PAIR.FIXTURE / 'native.bcpl'
        path.write_text(path.read_text().replace('MARK("R4")', 'MARK("FAIL")'))
        with self.assertRaisesRegex(PAIR.PairError, 'R4 marker'):
            PAIR.validate_inputs()

    def test_changed_accepted_library_is_refused(self):
        with (PAIR.ACCEPTED / 'library.bcpl').open('a') as out:
            out.write('CHANGED\n')
        with self.assertRaisesRegex(PAIR.PairError, 'dependency drift'):
            PAIR.validate_inputs()

    def test_long_card_refused(self):
        path = PAIR.FIXTURE / 'mr10.bcpl'
        path.write_text(path.read_text() + '\n' + 'Z'*81 + '\n')
        with self.assertRaisesRegex(PAIR.PairError, 'exceeds 80'):
            PAIR.validate_inputs()

    def test_complete_ordered_output_only(self):
        correct = '\n'.join('CO6PAIR ' + x for x in PAIR.ORACLE)
        self.assertEqual(PAIR.records(correct), list(PAIR.ORACLE))
        self.assertNotEqual(PAIR.records(correct + '\nCO6PAIR W1'), list(PAIR.ORACLE))
        with self.assertRaisesRegex(PAIR.PairError, 'malformed'):
            PAIR.records('CO6PAIR W1 EXTRA')

    def test_mr10_strict_jes_checks(self):
        text = '\n'.join('CO6PAIR ' + x for x in PAIR.ORACLE)
        fake_summary = '\n'.join([
            'JOB 8111  CO6MPAIR',
            *(f'{name} {pgm} RC=0000' for name, pgm in PAIR.EXPECTED_STEPS),
            'JOB RESULT: SUCCESS', 'HIGHEST RC: 0000',
        ])
        fake_report = '\n'.join(
            [*(f'EXECUTION CYCLES = {i}, CODE = 0' for i in range(7)),
             text])
        def fake_shell(args, log, timeout=600):
            if log.name == 'mr10-compile.log':
                log.write_text('JOB 8111\n')
            elif log.name == 'mr10-jes-summary.log':
                log.write_text(fake_summary)
            else:
                log.write_text(fake_report)
            return SimpleNamespace(returncode=0)
        with patch.object(PAIR, 'shell', side_effect=fake_shell):
            result = PAIR.run_mr10(self.root)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['steps'], 14)

    def test_native_receipt_and_full_jes_oracle(self):
        holder = SimpleNamespace()
        def fake_import(path, name):
            return (SimpleNamespace(configure=lambda driver: None)
                    if path == PAIR.CO3_ADAPTER else holder)
        def execute(scenario):
            self.assertEqual(scenario, 'first')
            path = holder.WORK / 'receipt'
            path.mkdir()
            (path / 'job-report.log').write_text('\n'.join(
                'CO6PAIR ' + x for x in PAIR.ORACLE))
            (path / 'result.json').write_text(json.dumps({
                'status': 'PASS', 'bcpl_records': list(PAIR.ORACLE),
                'steps': {x: 0 for x in ('ASMA','ASML','ASMM','ASMS','LKED','GO')},
                'CO3ACMP_job': '1', 'CO3LCMP_job': '2', 'native_job': '3',
            }))
            return 0
        holder.execute = execute
        with (patch.object(PAIR, 'load_module', side_effect=fake_import),
              patch.object(PAIR, 'ROOT', self.root)):
            result = PAIR.run_native(self.root)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['native_job'], '3')


if __name__ == '__main__':
    unittest.main()
