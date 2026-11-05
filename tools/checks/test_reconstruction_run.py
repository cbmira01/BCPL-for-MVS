"""Offline simulation of complete reconstruction sequencing and scope checks."""
from __future__ import annotations

import hashlib
import importlib.machinery
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'reconstruction/run'
CLEAN = Path(__file__).resolve().parents[1] / 'clean-workarea'


def load_runner():
    loader = importlib.machinery.SourceFileLoader('reconstruction_run_test', str(SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


run = load_runner()


class FakeCore:
    def __init__(self):
        self.config = {'mvs': {'batch_password': 'SECRET'}, 'datasets': {
            'BOOT_SOURCE': {'populate': True, 'members': {'A': 'src/a'},
                            'generated_members': {'TRNILRG': 'workarea/bootstrap/x'}},
        }}

    def load_config(self):
        return self.config


class FakePlan:
    def __init__(self, core):
        self.core = core
        self.sha = 'a' * 40
        self.branch = 'main'
        self.status = ''

    def run_git(self, root, *args):
        return {('rev-parse', 'HEAD'): self.sha,
                ('symbolic-ref', '--short', 'HEAD'): self.branch,
                ('status', '--porcelain', '--untracked-files=normal'): self.status}[args]

    def load_dspal_core(self, root):
        return self.core

    def public_config_digest(self, config):
        return str(config['mvs']['batch_password'])[:0] + str(config['datasets']['BOOT_SOURCE']['members'])


class Approval:
    def verify_approval(self, grant, planner):
        self.checked = True
        assert planner() == ('scope', [])


class Grant:
    git_sha = 'a' * 40


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name)
        (self.root / 'workarea').mkdir()
        (self.root / 'workarea/.gitignore').write_text('*')
        (self.root / 'workarea/garbage').write_text('old')
        (self.root / 'workarea/m3-clean-smoke.s370.asm').write_text('CSECT\nEXTRN BCPLMAIN\nEND\n')
        self.core = FakeCore()
        self.plan = FakePlan(self.core)
        self.approval = Approval()
        self.log = []
        self.commands = []
        self.payload = 888

    def execute(self, cmd):
        self.commands.append(cmd)
        if cmd[0] == 'tools/clean-workarea':
            self.assertEqual(cmd[1], '--reconstruction-scope')
            self.assertEqual(cmd[2], run.scope_snapshot(self.root))
            for entry in (self.root / 'workarea').iterdir():
                if entry.name != '.gitignore':
                    if entry.is_dir():
                        raise AssertionError('fixture should only contain files')
                    entry.unlink()
        if cmd[1:3] == ['populate', 'all'] and '--generated-only' not in cmd:
            return (2, 'populate completed: 1 ready member(s) written\n'
                    '  MISSING GENERATED: BOOT_SOURCE(TRNILRG) <- workarea/bootstrap/x\n')
        if cmd[1] == 'submit':
            self.payload += 1
            return (0, f'Launcher: JOB 102\nPayload: JOB {self.payload}\n'
                       f'JOB {self.payload} NAME\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n')
        if cmd[1:3] == ['ls', 'BOOT_OBJ']:
            return (0, 'HERC02.BCPL.BOOT.OBJ:\n' + ''.join('    '+m+'\n' for m in sorted(run.RUNTIME_MEMBERS)))
        if cmd[1:3] == ['ls', 'EXT_OBJ']:
            return (0, 'HERC02.BCPL.EXT.OBJ:\n' + ''.join('    '+m+'\n' for m in sorted(run.EXTENSION_MEMBERS)))
        if cmd[1] == 'ls':
            return (0, 'HERC02.BCPL.MR10KIT.OBJ:\n    ICINT19\n')
        if cmd[0] in ('tools/mr10/compile-and-run', 'tools/bootstrap/compile-mvs'):
            if cmd[0] == 'tools/bootstrap/compile-mvs':
                (self.root / 'workarea/m3-clean-smoke.s370.asm').write_text('CSECT\nEXTRN BCPLMAIN\nEND\n')
            return (0, 'Interpreter CODE=0\n')
        return (0, 'success')

    def runner(self):
        obj = run.Runner(self.root, run_command=self.execute, emit=self.log.append,
                         plan=self.plan, approval=self.approval,
                         planner=lambda: ('scope', []),
                         config_hash=self.plan.public_config_digest(self.core.config))
        obj.set_approval(Grant())
        return obj

    def test_full_sequence_with_fake_mvs_commands(self):
        self.runner().run(self.core.config)
        self.assertTrue(self.approval.checked)
        self.assertEqual(len(self.commands), len(run.STEPS))
        self.assertEqual(self.commands[1], ['tools/datasets/dspal', 'purgebcpl', '--yes'])
        self.assertEqual(self.commands[2], ['tools/datasets/dspal', 'initbcpl'])
        self.assertFalse(any('regressions' in ' '.join(c) for c in self.commands))
        self.assertTrue(any('PASS' in line for line in self.log))

    def test_wrong_population_missing_count_fails_closed(self):
        orig = self.execute
        def broken(cmd):
            if cmd[1:3] == ['populate', 'all'] and '--generated-only' not in cmd:
                self.commands.append(cmd)
                return 2, 'dspal: different reason\n'
            return orig(cmd)
        runner = self.runner()
        runner.command = broken
        with self.assertRaisesRegex(run.ReconstructionError, 'first population'):
            runner.run(self.core.config)
        self.assertEqual(len(self.commands), 4)

    def test_nonzero_rc_halts_before_dependency(self):
        def failing(cmd):
            self.commands.append(cmd)
            return 1, 'error'
        runner = self.runner()
        runner.command = failing
        with self.assertRaises(run.ReconstructionError):
            runner.run(self.core.config)
        self.assertEqual(len(self.commands), 1)

    def test_changed_revision_refuses_before_work(self):
        self.plan.sha = 'f' * 40
        with self.assertRaisesRegex(run.ReconstructionError, 'Git revision changed'):
            self.runner().run(self.core.config)
        self.assertEqual(self.commands, [])

    def test_changed_config_refuses_before_work(self):
        runner = self.runner()
        self.core.config['datasets']['BOOT_SOURCE']['members']['B'] = 'src/b'
        with self.assertRaisesRegex(run.ReconstructionError, 'config'):
            runner.run(self.core.config)
        self.assertEqual(self.commands, [])

    def test_inventory_is_strict(self):
        with self.assertRaises(run.ReconstructionError):
            run.inventory_members('unverified text')
        self.assertEqual(run.inventory_members('HERC02.BCPL.TEST:\n    HELLO\n'), {'HELLO'})

    def test_live_run_cli_disabled(self):
        cp = subprocess.run([sys.executable, str(SCRIPT), '--run'], capture_output=True, text=True)
        self.assertEqual(cp.returncode, 2)
        self.assertIn('DISABLED', cp.stderr)

    def test_idle_guard_blocks_before_cleanup_or_purge(self):
        class Denial:
            def request_approval(self, *args, **kwargs):
                return Grant()
        self.plan.prepare = lambda root, core, probe: ('scope', [])
        def not_verified():
            raise run.ReconstructionError('active JES status unverified')
        with self.assertRaisesRegex(run.ReconstructionError, 'unverified'):
            run.authorized_run(self.root, self.plan, Denial(), self.core,
                               self.execute, self.log.append, terminal=True,
                               jes_idle_guard=not_verified)
        self.assertEqual(self.commands, [])

    def test_operator_decline_blocks_before_guard(self):
        class Denial:
            def request_approval(self, *args, **kwargs):
                raise RuntimeError('operator refused')
        self.plan.prepare = lambda root, core, probe: ('scope', [])
        guard_called = []
        with self.assertRaisesRegex(RuntimeError, 'operator refused'):
            run.authorized_run(self.root, self.plan, Denial(), self.core,
                               self.execute, self.log.append, terminal=True,
                               jes_idle_guard=lambda: guard_called.append(True))
        self.assertEqual(guard_called, [])
        self.assertEqual(self.commands, [])

    def test_list_is_non_destructive(self):
        cp = subprocess.run([sys.executable, str(SCRIPT), '--list'], capture_output=True, text=True)
        self.assertEqual(cp.returncode, 0)
        self.assertIn('BCPLQSAM', cp.stdout)
        self.assertNotIn('--run', cp.stdout)


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'tools').mkdir()
        (self.root / 'tools/clean-workarea').write_bytes(CLEAN.read_bytes())
        (self.root / 'tools/clean-workarea').chmod(0o755)
        (self.root / 'workarea').mkdir()
        (self.root / 'workarea/.gitignore').write_text('*\n')
        subprocess.run(['git', '-C', str(self.root), 'init', '-q', '-b', 'main'], check=True)
        subprocess.run(['git', '-C', str(self.root), 'add', '-f', 'workarea/.gitignore'], check=True)

    def invoke(self, *args):
        return subprocess.run(['bash', str(self.root / 'tools/clean-workarea'), *args],
                              stdin=subprocess.DEVNULL,
                              capture_output=True, text=True)

    def test_cleanup_scope_exact_and_marker_preserved(self):
        (self.root / 'workarea/old').write_text('old')
        token = run.scope_snapshot(self.root)
        cp = self.invoke('--reconstruction-scope', token)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertFalse((self.root / 'workarea/old').exists())
        self.assertTrue((self.root / 'workarea/.gitignore').exists())

    def test_cleanup_changed_entries_blocked(self):
        (self.root / 'workarea/old').write_text('old')
        token = run.scope_snapshot(self.root)
        (self.root / 'workarea/new').write_text('new')
        cp = self.invoke('--reconstruction-scope', token)
        self.assertNotEqual(cp.returncode, 0)
        self.assertTrue((self.root / 'workarea/old').exists())
        self.assertIn('changed', cp.stderr)

    def test_standalone_still_requires_terminal(self):
        (self.root / 'workarea/old').write_text('old')
        cp = self.invoke()
        self.assertNotEqual(cp.returncode, 0)
        self.assertIn('Interactive terminal required', cp.stderr)
        self.assertTrue((self.root / 'workarea/old').exists())


if __name__ == '__main__':
    unittest.main()
