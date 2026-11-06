"""End-to-end synthetic one-run controller; NEVER talks to MVS/JES."""
from __future__ import annotations
from reconstruction_fixtures import REQUIRED_LOGICAL

import hashlib
import importlib.machinery
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
RECON = TOOLS / 'reconstruction'
sys.path.insert(0, str(RECON))
import contract
import verify
from test_reconstruction_payload import fixture


def extensionless(name):
    loader = importlib.machinery.SourceFileLoader('test_integration_'+name, str(RECON/name))
    module = types.ModuleType(loader.name)
    module.__file__ = str(RECON/name)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module

plan = extensionless('plan')
auth = extensionless('authorize')
run = extensionless('run')


class FakeCore:
    def __init__(self, config):
        self.config = config
    def load_config(self):
        return self.config
    def load_simple_yaml(self, path):
        return self.config
    @staticmethod
    def full_dsn(config, spec):
        return config['mvs']['hlq'] + '.' + spec['dsn']
    @staticmethod
    def cheap_status(config):
        return {'reader': (True, 'ready'), 'container': (True, 'running')}


class ReconstructionIntegration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'workarea').mkdir()
        (self.root / 'workarea/.gitignore').write_text('*\n')
        (self.root / 'workarea/old').write_text('garbage')
        (self.root / 'mvs-state').mkdir()
        cfg = {'mvs': {'hlq': 'HERC02', 'userid': 'HERC02', 'batch_user': 'HERC02',
                       'write_boundary': 'HERC02.**', 'batch_password': 'NotForLogs123'},
               'datasets': {logical: {'dsn': 'BCPL.' + logical.replace('_', '.'),
                                      'populate': False, 'members': {}, 'dsorg':'PO',
                                      'recfm':'FB','lrecl':80,'blksize':800}
                            for logical in REQUIRED_LOGICAL}}
        cfg['datasets']['MR10_JCL']['members']['IC19BLD'] = 'jcl/IC19BLD'
        for member in plan.REQUIRED_BUILD_MEMBERS['BOOT_JCL']:
            cfg['datasets']['BOOT_JCL']['members'][member] = 'jcl/'+member
        cfg['datasets']['BOOT_SOURCE']['populate'] = True
        cfg['datasets']['BOOT_SOURCE']['members']['HEADER'] = 'src/header'
        cfg['datasets']['BOOT_SOURCE']['generated_members'] = {'TRNA': 'workarea/bootstrap-cambridge/demoted/trna'}
        self.cfg = cfg
        self.core = FakeCore(cfg)
        for path in plan.REQUIRED_TOOLS:
            f = self.root / path
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text('fixture\n')
        for ds in cfg['datasets'].values():
            for value in ds['members'].values():
                p = self.root/value
                p.parent.mkdir(exist_ok=True, parents=True)
                p.write_text('//SYSUT1 DD DSN=HERC02.BCPL.BOOT.OBJ(BLIB),DISP=SHR\n')
        self.inventory = contract.dataset_inventory(cfg, FakeCore.full_dsn)
        self.command_log = []
        self.built_camb = False
        self.summary_broken = None
        self.orig_git = plan.run_git
        def git(root, *args):
            if args == ('rev-parse', '--show-toplevel'):
                return str(root)
            if args == ('rev-parse', 'HEAD'):
                return 'a' * 40
            if args == ('symbolic-ref', '--short', 'HEAD'):
                return 'main'
            if args == ('status', '--porcelain', '--untracked-files=normal'):
                return ''
            if args == ('ls-files', '--', 'workarea/'):
                return 'workarea/.gitignore'
            raise ValueError(args)
        plan.run_git = git
        self.addCleanup(lambda: setattr(plan, 'run_git', self.orig_git))

    def execute(self, cmd):
        self.command_log.append(tuple(cmd))
        inv = dict(self.inventory)
        if cmd == ['tools/datasets/dspal', 'purgebcpl', '--show-jcl']:
            return 0, '\n'.join(f" DELETE '{dsn}'" for logical, dsn in self.inventory)+'\n'
        if cmd == ['tools/datasets/dspal', 'initbcpl', '--show-jcl']:
            return 0, '\n'.join(f'//D{i:03d} DD DSN={dsn},' for i,(logical,dsn) in enumerate(self.inventory, 1))+'\n'
        if cmd == ['tools/datasets/dspal', 'stat']:
            return 0, ''.join(
                f'Dataset:   {dsn} ({logical})\n    Job:777,  DSORG:PO,  RECFM:FB,  LRECL:80,  BLKSIZE:800\n'
                for logical, dsn in self.inventory)
        if cmd[0] == 'tools/clean-workarea':
            self.assertEqual(cmd[1], '--reconstruction-scope')
            self.assertEqual(cmd[2], contract.workarea_scope(self.root/'workarea').fingerprint)
            contract.remove_workarea_contents(self.root/'workarea', contract.workarea_scope(self.root/'workarea'))
            return 0, 'cleaned\n'
        if cmd[1:3] == ['populate', 'all'] and '--generated-only' not in cmd:
            return 2, ('populate completed: 1 ready member(s) written\n'
                       ' MISSING GENERATED: BOOT_SOURCE(TRNA) <- workarea/bootstrap-cambridge/demoted/trna\n')
        if cmd[1:3] == ['populate', 'all'] and '--generated-only' in cmd:
            return 0, 'populate completed: 1 ready member(s) written\n'
        if cmd[0] == 'tools/bootstrap/prepare-bootstrap':
            base = self.root/'workarea/bootstrap-cambridge'
            (base/'demoted').mkdir(parents=True)
            source = base/'demoted/trna'
            source.write_bytes(b'demoted')
            (base/'trni-large-names.int').write_bytes(b'interpreter image')
            outputs = {str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                       for path in (source, base/'trni-large-names.int')}
            (base/'prepare-bootstrap-manifest.json').write_text(json.dumps({
               'format':1, 'trnilrg_rebuilt': True, 'inputs': {}, 'outputs': outputs}))
            return 0, 'READY\n'
        if cmd[0] == 'tools/bootstrap/compile-mvs':
            (self.root/'workarea/m3-clean-smoke.s370.asm').write_text('CSECT\nEXTRN BCPLMAIN\nEND\n')
            return 0, 'INTERPRETER CODE=0\n'
        if cmd[0] == 'tools/mr10/compile-and-run':
            return 0, 'INTERPRETER CODE=0\n'
        if cmd[1] == 'submit':
            member = cmd[-1]
            if member == 'CAMBBLD':
                self.built_camb = True
            return 0, ('Submitted HERC02.BCPL.' + ('MR10KIT.JCL' if member == 'IC19BLD' else 'BOOT.JCL')
                       + f'({member})\nLauncher: JOB 777\nPayload:  JOB 888\n')
        if cmd[0] in ('tools/mvs/job-summary', 'tools/mvs/dump-report-for-job'):
            member = next(c[-1] for c in reversed(self.command_log)
                          if len(c) == 4 and c[1] == 'submit')
            summary, detail = fixture(member, omit=self.summary_broken if member == 'BLDBMAIN' else None)
            return 0, summary if cmd[0].endswith('job-summary') else detail
        if cmd[1] == 'ls':
            logical = cmd[2]
            if logical in ('MR10_LOAD', 'MR10_OBJ'):
                members = ('ICINT19',)
            elif logical == 'BOOT_INTCODE':
                members = tuple(sorted(verify.CAMB_UNITS | {'TRNILRG', 'CAMBCOMP'})) if self.built_camb else ('TRNILRG',)
            elif logical == 'BOOT_OBJ':
                members = tuple(sorted(verify.RUNTIME_MEMBERS))
            elif logical == 'EXT_OBJ':
                members = ('BCPLDEMO','BCPLTIME','BCPLQSAM') if any(c[-1]=='BCPLQSAM' for c in self.command_log if len(c)==4 and c[1]=='submit') else ()
            else:
                members = ()
            return 0, inv[logical] + ':\n' + (''.join('    '+m+'\n' for m in members) if members else '    (empty)\n')
        return 0, 'success\n'

    def planner(self):
        return plan.prepare(self.root, self.core, probe=True)

    def grant(self, mutator=None):
        report, errors = self.planner()
        self.assertFalse(errors, errors)
        phrase = 'REBUILD HERC02 ' + auth.digest_report(report)[:12]
        def read_line(prompt):
            if mutator:
                mutator()
            return phrase
        return auth.request_approval(self.planner, output=io.StringIO(),
                                     read_line=read_line, interactive=True)

    def run_engine(self, grant):
        from evidence import EvidenceLog
        e = EvidenceLog(self.root, git_sha=grant.git_sha, plan_sha256=grant.digest,
                        inventory=grant.managed_dsns,
                        secrets=(self.cfg['mvs']['batch_password'],))
        engine = run.Runner(self.root, run_command=self.execute, emit=lambda msg: None,
                            plan=plan, core=self.core, approval=auth, grant=grant,
                            planner=self.planner, evidence=e)
        return engine, e

    def test_complete_synthetic_reconstruction(self):
        grant = self.grant()
        engine, e = self.run_engine(grant)
        engine.run()
        self.assertEqual(e.state, 'SUCCESS')
        self.assertEqual(len(e.operations), len(contract.OPERATIONS))
        self.assertFalse(any('run-regression' in op[0] for op in self.command_log))
        self.assertTrue((self.root/'workarea/.gitignore').exists())
        self.assertFalse((self.root/'workarea/old').exists())
        self.assertNotIn('NotForLogs123', (e.directory/'report.json').read_text())

    def test_bad_payload_halts_before_blib(self):
        grant = self.grant()
        engine, e = self.run_engine(grant)
        self.summary_broken = 'PUTREG'
        with self.assertRaises(verify.VerificationError):
            engine.run()
        self.assertEqual(e.state, 'FAILED')
        self.assertFalse(any(c[-1]=='BLIBBLD' for c in self.command_log if len(c)==4 and c[1]=='submit'))

    def test_host_cleanup_changed_during_prompt_refuses_without_operations(self):
        with self.assertRaises(auth.ApprovalError):
            self.grant(lambda: (self.root/'workarea/injected').write_text('new'))
        self.assertEqual(self.command_log, [])

    def test_guard_boolean_and_missing_result_fail_closed(self):
        for value in (False, True, 0, None, (False, []), (True, [])):
            with self.subTest(return_value=value):
                with self.assertRaises(run.ReconstructionError):
                    run.require_jes_clear(lambda: value)

    def test_two_distinct_clear_guard_observations_required(self):
        class Observation:
            def __init__(self, state): self.state = state
        run.require_jes_clear(lambda: (True, [Observation('CLEAR'), Observation('CLEAR')]))
        with self.assertRaises(run.ReconstructionError):
            run.require_jes_clear(lambda: (True, [Observation('CLEAR'), Observation('ACTIVE')]))


    def test_false_guard_cannot_reach_cleanup_or_purge(self):
        report, errors = self.planner()
        self.assertFalse(errors)
        phrase = 'REBUILD HERC02 ' + auth.digest_report(report)[:12]
        with patch('sys.stdout', new_callable=io.StringIO):
            with self.assertRaisesRegex(run.ReconstructionError, 'JES idle'):
                run.authorized_run(self.root, plan, auth, self.core, self.execute,
                                   lambda msg: None, terminal=True,
                                   prompt=lambda _: phrase,
                                   jes_idle_guard=lambda: False)
        self.assertEqual(self.command_log, [])
        receipts = list((self.root/'mvs-state/reconstruction-evidence').glob('*/report.json'))
        self.assertEqual(len(receipts), 1)
        self.assertEqual(json.loads(receipts[0].read_text())['state'], 'BLOCKED')

    def test_purge_scope_mismatch_blocks_before_actual_purge(self):
        grant = self.grant()
        engine, evidence = self.run_engine(grant)
        original = self.execute
        def forged_preview(cmd):
            if cmd == ['tools/datasets/dspal', 'purgebcpl', '--show-jcl']:
                self.command_log.append(tuple(cmd))
                return 0, " DELETE 'HERC02.BCPL.UNKNOWN'\n"
            return original(cmd)
        engine.command = forged_preview
        with self.assertRaisesRegex(run.ReconstructionError, 'purge JCL'):
            engine.run()
        self.assertFalse(any(c[1:] == ('purgebcpl', '--yes') for c in self.command_log))
        self.assertEqual(evidence.state, 'FAILED')

    def test_changed_config_before_purge_halts(self):
        grant = self.grant()
        engine, e = self.run_engine(grant)
        self.cfg['mvs']['hlq'] = 'HERC01'
        with self.assertRaises(auth.ApprovalError):
            engine.run()
        self.assertEqual(e.state, 'BLOCKED')
        self.assertEqual(self.command_log, [])

    def test_status_not_success_after_missing_payload_step(self):
        grant = self.grant()
        engine, e = self.run_engine(grant)
        self.summary_broken = 'VERIFY'
        # Missing VERIFY on BCPLQSAM rather than BLDBMAIN:
        original = self.execute
        def bad_qsam(cmd):
            if cmd[0] in ('tools/mvs/job-summary', 'tools/mvs/dump-report-for-job'):
                member = next(c[-1] for c in reversed(self.command_log)
                              if len(c) == 4 and c[1] == 'submit')
                if member == 'BCPLQSAM':
                    s, d = fixture(member, omit='VERIFY')
                    self.command_log.append(tuple(cmd))
                    return 0, s if cmd[0].endswith('job-summary') else d
            return original(cmd)
        engine.command = bad_qsam
        with self.assertRaises(verify.VerificationError):
            engine.run()
        self.assertEqual(e.state, 'FAILED')
        self.assertFalse(any(c[1:3] == ('ls', 'BOOT_INTCODE') for c in self.command_log[-2:]))


    def test_interruption_is_reported_without_running_next_step(self):
        grant = self.grant()
        engine, e = self.run_engine(grant)
        original = self.execute
        def interrupted(cmd):
            if cmd[:2] == ['tools/datasets/dspal', 'initbcpl'] and '--show-jcl' not in cmd:
                raise KeyboardInterrupt()
            return original(cmd)
        engine.command = interrupted
        with self.assertRaises(KeyboardInterrupt):
            engine.run()
        self.assertEqual(e.state, 'INTERRUPTED')
        self.assertEqual(e.operations[-2]['result'], 'FAIL')
        self.assertFalse(any(c[1:3] == ('populate', 'all') for c in self.command_log))

    def test_cli_rejects_noninteractive_without_reconstruction(self):
        import subprocess
        cp = subprocess.run([sys.executable, str(RECON/'run'), '--run'], text=True, capture_output=True)
        self.assertEqual(cp.returncode, 2)
        self.assertIn('BLOCKED: reconstruction requires interactive', cp.stdout)


if __name__ == '__main__':
    unittest.main()
