"""Offline Step 3 runner regression tests; no live reconstruction is reachable."""
from __future__ import annotations

import importlib.machinery
from pathlib import Path
import subprocess
import sys
import types
import unittest
from types import SimpleNamespace

TOOLS = Path(__file__).resolve().parents[1]
RECON = TOOLS / 'reconstruction'
sys.path.insert(0, str(RECON))
import contract
import verify

loader = importlib.machinery.SourceFileLoader('reconstruction_runner_existing_suite', str(RECON / 'run'))
run = types.ModuleType(loader.name)
run.__file__ = str(RECON / 'run')
loader.exec_module(run)


class RunnerTests(unittest.TestCase):
    def test_canonical_operations_cover_builds_and_guide(self):
        self.assertEqual(contract.OPERATIONS[0].check, 'cleanup')
        self.assertEqual(contract.OPERATIONS[-1].check, 'extensions-members')
        self.assertEqual(set(verify.EXPECTED_STEPS), {
            'IC19BLD', 'CAMBBLD', 'BLDBMAIN', 'BLIBBLD',
            'BCPLDEMO', 'BCPLTIME', 'BCPLQSAM'})
        guides = [int(x.guide) for x in contract.OPERATIONS]
        self.assertEqual(guides, sorted(guides))
        self.assertNotIn(4, guides)  # Guide 4 is intentionally outside reconstruction

    def test_no_regressions_or_release_side_effects(self):
        names = ' '.join(' '.join(op.command) for op in contract.OPERATIONS)
        self.assertNotIn('run-project-regressions', names)
        self.assertNotIn('run-suite', names)
        self.assertNotIn('git tag', names)
        self.assertNotIn('release', names)
        self.assertNotIn('resume', names)

    def test_all_destructive_operations_are_declared(self):
        writes = [op for op in contract.OPERATIONS if op.writes]
        self.assertGreater(len(writes), 10)
        self.assertEqual([x.check for x in writes[:3]], ['cleanup', 'purge', 'init'])

    def test_first_population_exact_rc2_exception(self):
        self.assertEqual([x.check for x in contract.OPERATIONS].count('first-populate'), 1)
        self.assertEqual([x.check for x in contract.OPERATIONS].count('generated-populate'), 1)

    def test_jes_guard_requires_two_distinct_clear_observations(self):
        observations = [SimpleNamespace(state='CLEAR'), SimpleNamespace(state='CLEAR')]
        run.require_jes_clear(lambda: (True, observations))

    def test_jes_guard_boolean_false_is_not_clear(self):
        for result in (None, False, True, 0, 2, (False, []),
                       (True, []), (True, [SimpleNamespace(state='CLEAR')]),
                       (True, [SimpleNamespace(state='CLEAR'), SimpleNamespace(state='ACTIVE')])):
            with self.subTest(result=result):
                with self.assertRaises(run.ReconstructionError):
                    run.require_jes_clear(lambda r=result: r)

    def test_jes_guard_exception_is_blocked(self):
        def fail():
            raise RuntimeError('console unavailable')
        with self.assertRaisesRegex(run.ReconstructionError, 'JES idle safeguard failed'):
            run.require_jes_clear(fail)

    def test_failed_subprocess_is_not_success(self):
        for rc in (True, None, '0', -1, 1, 4, 12):
            with self.subTest(rc=rc):
                with self.assertRaises(run.ReconstructionError):
                    run._rc0(rc, 'test operation')

    def test_payload_identity_rejects_missing_number(self):
        self.assertIsNone(run._payload_number_from_output('Launcher: JOB 8\n'))
        self.assertIsNone(run._payload_number_from_output('Payload: JOB 8\nPayload: JOB 9\n'))
        self.assertEqual(run._payload_number_from_output('Payload: JOB 9\n'), 9)

    def test_exact_payload_step_mapping(self):
        self.assertEqual(verify.EXPECTED_STEPS['IC19BLD'], ('ASM', 'LKED', 'SAVEOBJ'))
        self.assertEqual(len(verify.EXPECTED_STEPS['CAMBBLD']), 23)
        self.assertEqual(len(verify.EXPECTED_STEPS['BLDBMAIN']), 14)
        self.assertEqual(len(verify.EXPECTED_STEPS['BLIBBLD']), 6)

    def test_required_object_inventory(self):
        verify.required_inventory('BOOT_OBJ', verify.RUNTIME_MEMBERS)
        with self.assertRaises(verify.VerificationError):
            verify.required_inventory('BOOT_OBJ', verify.RUNTIME_MEMBERS - {'BCPLIO'})

    def test_exact_extension_inventory(self):
        verify.required_inventory('EXT_OBJ', verify.EXTENSION_MEMBERS)
        with self.assertRaises(verify.VerificationError):
            verify.required_inventory('EXT_OBJ', frozenset({'BCPLDEMO'}))

    def test_list_cli_is_read_only(self):
        cp = subprocess.run([sys.executable, str(RECON / 'run'), '--list'],
                            capture_output=True, text=True, check=False)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn('BCPLQSAM', cp.stdout)
        self.assertNotIn(' --run', cp.stdout)
        self.assertIn('No regressions', cp.stdout)

    def test_live_run_cli_disabled(self):
        cp = subprocess.run([sys.executable, str(RECON / 'run'), '--run'],
                            capture_output=True, text=True, check=False)
        self.assertEqual(cp.returncode, 2)
        self.assertIn('DISABLED', cp.stderr)

    def test_clean_workarea_standalone_requires_terminal(self):
        # No git repository is present at the staging fixture; cleanup must fail,
        # and must never perform an implicit noninteractive deletion.
        cp = subprocess.run([sys.executable, str(TOOLS / 'clean-workarea')],
                            capture_output=True, text=True, check=False)
        self.assertNotEqual(cp.returncode, 0)


if __name__ == '__main__':
    unittest.main()
