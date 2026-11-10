"""Offline tests for the simple reconstruction driver; no MVS or JES access."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'reconstruction/rebuild-from-source'


@unittest.skipUnless(shutil.which('script'), 'util-linux script(1) is required for PTY fixture')
class SimpleReconstructionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        destination = self.root / 'tools/reconstruction/rebuild-from-source'
        destination.parent.mkdir(parents=True)
        shutil.copyfile(SOURCE, destination)
        self.call_log = self.root / 'calls.txt'
        stub = """#!/usr/bin/env bash
printf '%s %s\\n' "${0##*/}" "$*" >> "$MOCK_LOG"
if [ "${0##*/}" = clean-workarea ] && [ "${1:-}" != --yes ]; then
    read -r answer
    [ "$answer" = DELETE ] || exit 3
fi
if [ "$1" = purgebcpl ] && [ "${2:-}" != --show-jcl ] && [ "${2:-}" != --yes ]; then
    read -r answer
    [ "$answer" = YES ] || exit 3
fi
if [ "$1" = --with-trnilrg ]; then
    mkdir -p workarea/bootstrap-cambridge
    echo '{"trnilrg_rebuilt": true}' > workarea/bootstrap-cambridge/prepare-bootstrap-manifest.json
fi
if [ "${0##*/}" = compile-mvs ]; then
    mkdir -p workarea
    echo CSECT > workarea/m3-clean-smoke.s370.asm
fi
if [ "${MOCK_FAIL:-}" = "${0##*/}:$*" ]; then
    exit 7
fi
if [ "${0##*/}" = dspal ] && [[ "$*" == 'populate all' || "$*" == 'populate all --dry-run' || "$*" == 'populate all --batch' ]]; then
    if [ "$*" = 'populate all --dry-run' ]; then
        printf 'Dry run: 162 ready member(s) would be written.\\n'
        phase=dry-run
    else
        printf 'populate completed: 162 ready member(s) written\\n'
        phase=install
    fi
    printf 'dspal: 12 generated member(s) unavailable; prepare-bootstrap required\\n' >&2
    count=12
    if [ "${MOCK_BAD_PHASE:-}" = "$phase" ]; then
        count=11
    fi
    for ((n=0; n < count; n++)); do
        printf '  MISSING GENERATED: BOOT_SOURCE(M%02d) <- generated/file%02d\\n' "$n" "$n" >&2
    done
    exit 2
fi
exit 0
"""
        for name in (
            'tools/mvs/start-tk5', 'tools/datasets/dspal',
            'tools/bootstrap/prepare-bootstrap', 'tools/clean-workarea',
            'tools/mr10/compile-and-run', 'tools/bootstrap/compile-mvs',
            'bin/git',
        ):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(stub, encoding='utf-8')
            path.chmod(0o755)

    def invoke(self, *, approve=True, fail=None, bad_phase=None, batch=False):
        env = os.environ.copy()
        env['PATH'] = str(self.root / 'bin') + os.pathsep + env['PATH']
        env['MOCK_LOG'] = str(self.call_log)
        if fail:
            env['MOCK_FAIL'] = fail
        if bad_phase:
            env['MOCK_BAD_PHASE'] = bad_phase
        # script(1) allocates an interactive PTY for the child command.
        answers = ('\n\nDELETE\n\nYES\n' + '\n' * 16) if approve else 'NO\n'
        command = 'bash tools/reconstruction/rebuild-from-source'
        if batch:
            command += ' --batch-populate'
        return subprocess.run(
            ['script', '-q', '-e', '-c', command, '/dev/null'],
            cwd=self.root, env=env, input=answers,
            capture_output=True, text=True, check=False,
        )

    def invoke_unattended(self, *, fail=None, batch=False, options=None):
        env = os.environ.copy()
        env['PATH'] = str(self.root / 'bin') + os.pathsep + env['PATH']
        env['MOCK_LOG'] = str(self.call_log)
        if fail:
            env['MOCK_FAIL'] = fail
        flags = (['--unattended', '--batch-populate'] if batch
                 else ['--unattended'])
        if options is not None:
            flags = list(options)
        return subprocess.run(
            ['bash', 'tools/reconstruction/rebuild-from-source', *flags],
            cwd=self.root, env=env, stdin=subprocess.DEVNULL,
            capture_output=True, text=True, check=False,
        )


    def test_batch_opt_in_unattended_changes_both_writes_only(self):
        result = self.invoke_unattended(batch=True)
        self.assertEqual(result.returncode, 0, result.stdout[-2500:])
        self.assertIn('POPULATION MODE: bounded per-PDS', result.stdout)
        self.assertEqual(result.stdout.count('Expected first-pass RC=2'), 2)
        commands = self.call_log.read_text(encoding='utf-8')
        self.assertIn('dspal populate all --dry-run\n', commands)
        self.assertIn('dspal populate all --batch\n', commands)
        self.assertIn('dspal populate all --generated-only --dry-run\n', commands)
        self.assertIn('dspal populate all --generated-only --batch\n', commands)
        self.assertNotIn('dspal populate all\n', commands)
        self.assertNotIn('dspal populate all --generated-only\n', commands)
        self.assertIn('dspal submit BOOT_JCL BCPLQSAM\n', commands)
        self.assertNotIn('run-project-regressions', commands)

    def test_batch_opt_in_interactive_keeps_confirmation_gates(self):
        result = self.invoke(batch=True)
        self.assertEqual(result.returncode, 0, result.stdout[-2500:])
        self.assertIn('hit ENTER to continue, Ctrl-C to stop', result.stdout)
        commands = self.call_log.read_text(encoding='utf-8')
        self.assertIn('clean-workarea \n', commands)
        self.assertIn('dspal purgebcpl\n', commands)
        self.assertIn('dspal populate all --batch\n', commands)
        self.assertIn('dspal populate all --generated-only --batch\n', commands)

    def test_batch_first_pass_failure_stops_before_interpreter_build(self):
        result = self.invoke_unattended(batch=True, fail='dspal:populate all --batch')
        self.assertEqual(result.returncode, 7, result.stdout[-2200:])
        self.assertIn('STOPPED: Guide Step 2', result.stderr)
        commands = self.call_log.read_text(encoding='utf-8')
        self.assertIn('dspal populate all --batch\n', commands)
        self.assertNotIn('dspal submit MR10_JCL IC19BLD', commands)
        self.assertNotIn('dspal populate all --generated-only --batch', commands)

    def test_batch_generated_pass_failure_stops_before_compiler_build(self):
        result = self.invoke_unattended(
            batch=True, fail='dspal:populate all --generated-only --batch')
        self.assertEqual(result.returncode, 7, result.stdout[-2200:])
        self.assertIn('STOPPED: Guide Step 5', result.stderr)
        commands = self.call_log.read_text(encoding='utf-8')
        self.assertIn('dspal populate all --batch\n', commands)
        self.assertIn('dspal populate all --generated-only --batch\n', commands)
        self.assertNotIn('dspal submit BOOT_JCL CAMBBLD', commands)

    def test_batch_flag_in_either_order_and_duplicate_refusal(self):
        result = self.invoke_unattended(
            options=['--batch-populate', '--unattended'])
        self.assertEqual(result.returncode, 0, result.stdout[-2000:])
        commands = self.call_log.read_text(encoding='utf-8')
        self.assertIn('dspal populate all --batch\n', commands)

        self.call_log.unlink()
        duplicate = self.invoke_unattended(
            options=['--unattended', '--batch-populate', '--batch-populate'])
        self.assertEqual(duplicate.returncode, 2)
        self.assertIn('duplicate --batch-populate', duplicate.stderr)
        self.assertFalse(self.call_log.exists())

    def test_batch_option_alone_still_requires_terminal(self):
        result = self.invoke_unattended(options=['--batch-populate'])
        self.assertEqual(result.returncode, 2)
        self.assertIn('interactive terminal', result.stderr)
        self.assertFalse(self.call_log.exists())

    def test_total_time_reported_on_success_and_failure(self):
        success = self.invoke_unattended(batch=True)
        self.assertEqual(success.returncode, 0, success.stdout[-2200:])
        self.assertRegex(
            success.stdout, r"TOTAL REBUILD EXECUTION TIME: \d+m \d{2}s \(RC=0\)")
        self.assertEqual(success.stdout.count("TOTAL REBUILD EXECUTION TIME:"), 1)

        failure = self.invoke_unattended(
            fail="dspal:submit MR10_JCL IC19BLD")
        self.assertEqual(failure.returncode, 7, failure.stdout[-2200:])
        self.assertRegex(
            failure.stdout, r"TOTAL REBUILD EXECUTION TIME: \d+m \d{2}s \(RC=7\)")
        self.assertEqual(failure.stdout.count("TOTAL REBUILD EXECUTION TIME:"), 1)
        self.assertTrue(failure.stdout.rstrip().endswith("(RC=7)"))

    def test_unattended_completes_with_no_tty_and_no_prompts(self):
        result = self.invoke_unattended()
        self.assertEqual(result.returncode, 0, result.stdout[-2500:])
        self.assertIn('REBUILD COMMANDS COMPLETED', result.stdout)
        self.assertIn('UNATTENDED: workarea cleanup', result.stdout)
        self.assertNotIn('hit ENTER to continue', result.stdout)
        commands = self.call_log.read_text(encoding='utf-8')
        self.assertIn('clean-workarea --yes\n', commands)
        self.assertIn('dspal purgebcpl --show-jcl\n', commands)
        self.assertIn('dspal purgebcpl --yes\n', commands)
        self.assertIn('dspal submit BOOT_JCL BCPLQSAM\n', commands)
        self.assertEqual(result.stdout.count('Expected first-pass RC=2'), 2)

    def test_unattended_failure_stops_downstream_operations(self):
        result = self.invoke_unattended(fail='dspal:submit MR10_JCL IC19BLD')
        self.assertEqual(result.returncode, 7, result.stdout[-1800:])
        self.assertIn('STOPPED: Guide Step 3', result.stderr)
        commands = self.call_log.read_text(encoding='utf-8')
        self.assertNotIn('submit BOOT_JCL CAMBBLD', commands)

    def test_default_mode_requires_terminal(self):
        result = subprocess.run(
            ['bash', str(SOURCE)], cwd=self.root,
            stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn('interactive terminal', result.stderr)
        self.assertFalse(self.call_log.exists())

    def test_unrecognized_option_is_rejected_before_operations(self):
        result = subprocess.run(
            ['bash', str(SOURCE), '--resume'], cwd=self.root,
            stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn('[--unattended]', result.stderr)
        self.assertFalse(self.call_log.exists())
    def test_shell_syntax(self):
        result = subprocess.run(['bash', '-n', str(SOURCE)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_declined_confirmation_runs_nothing(self):
        result = self.invoke(approve=False)
        self.assertEqual(result.returncode, 3, result.stdout[-1000:])
        self.assertIn('hit ENTER to continue, Ctrl-C to stop: ', result.stdout)
        self.assertFalse(self.call_log.exists())

    def test_full_rebuild_accepts_verified_rc2_for_dry_run_and_install(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout[-2000:])
        self.assertIn('REBUILD COMMANDS COMPLETED', result.stdout)
        self.assertIn('hit ENTER to continue, Ctrl-C to stop: ', result.stdout)
        self.assertEqual(result.stdout.count('Expected first-pass RC=2'), 2)
        commands = self.call_log.read_text(encoding='utf-8')
        self.assertIn('dspal populate all --dry-run\n', commands)
        self.assertIn('dspal populate all\n', commands)
        self.assertIn('dspal submit BOOT_JCL BCPLQSAM\n', commands)
        self.assertNotIn('run-project-regressions', commands)
        self.assertNotIn('jes-idle', commands)

    def test_dry_run_rc2_without_twelve_missing_stops(self):
        result = self.invoke(bad_phase='dry-run')
        self.assertEqual(result.returncode, 2, result.stdout[-1000:])
        self.assertIn('first-pass RC=2 did not match', result.stdout)
        commands = self.call_log.read_text(encoding='utf-8')
        self.assertIn('dspal populate all --dry-run\n', commands)
        self.assertNotIn('dspal populate all\n', commands)

    def test_install_rc2_without_twelve_missing_stops(self):
        result = self.invoke(bad_phase='install')
        self.assertEqual(result.returncode, 2, result.stdout[-1000:])
        commands = self.call_log.read_text(encoding='utf-8')
        self.assertIn('dspal populate all\n', commands)
        self.assertNotIn('submit MR10_JCL IC19BLD', commands)

    def test_error_stops_and_never_runs_downstream_build(self):
        result = self.invoke(fail='dspal:submit MR10_JCL IC19BLD')
        self.assertEqual(result.returncode, 7, result.stdout[-1000:])
        self.assertIn('STOPPED: Guide Step 3', result.stdout)
        self.assertNotIn('submit BOOT_JCL CAMBBLD',
                         self.call_log.read_text(encoding='utf-8'))

    def test_compiler_smoke_source_exists(self):
        relative = 'tests/bootstrap/00-most-degenerate-bcpl-program/source.bcpl'
        self.assertIn(relative, SOURCE.read_text(encoding='utf-8'))
        self.assertTrue((SOURCE.parents[2] / relative).is_file())

    def test_no_resume_arguments(self):
        result = subprocess.run(
            ['bash', str(SOURCE), '--resume'],
            cwd=self.root, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn('always starts at Step 0', result.stderr)


if __name__ == '__main__':
    unittest.main()
