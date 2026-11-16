"""Host-only integration checks: CO.6 paired evidence inside project coordinator.

No actual MVS/JES work. All evidence and runners are synthetic temporary files.
"""
from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'tests/run-project-regressions'
loader = SourceFileLoader('co6_contract_coordinator_module', str(SOURCE))
spec = importlib.util.spec_from_loader(loader.name, loader)
if spec is None or spec.loader is None:
    raise RuntimeError('missing project coordinator')
MOD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MOD)


class CO6CoordinatorTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='co6-coordinator-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for name, value in {
            'ROOT': self.root,
            'COROUTINE_CONTRACT': self.root / 'tools/coroutines/run-co6-contract-regressions.py',
            'COROUTINE_CONTRACT_MANIFEST': self.root / 'tests/suites/coroutine-contract.tsv',
        }.items():
            p = patch.object(MOD, name, value)
            p.start()
            self.addCleanup(p.stop)
        self.declared = ['co6-pair', 'co6-nested']
        self.evidence = self.root / 'workarea/co6-contract-regressions/session'
        self.evidence.mkdir(parents=True)
        self.rows = []
        for case in self.declared:
            paired = self.root / 'workarea' / case / 'session'
            paired.mkdir(parents=True)
            (paired / 'result.json').write_text(json.dumps({
                'status':'PASS','selected':['mr10','native'],
                'paths':{'mr10':{'status':'PASS'}, 'native':{'status':'PASS'}}
            }))
            self.rows.append({'id':case,'status':'PASS',
                              'paired_evidence':str(paired.relative_to(self.root))})

    def log(self):
        return f'CO6 REGRESSION EVIDENCE: {self.evidence}\n'

    def put(self, states=None, *, status=None, rc=None):
        if states is None:
            states = ['PASS','PASS']
        cases = []
        for row, state in zip(self.rows, states):
            item = {'id':row['id'],'status':state}
            if state == 'PASS':
                item['paired_evidence'] = row['paired_evidence']
            if state == 'FAIL':
                item['reason'] = 'fake failing MVS job'
            cases.append(item)
        counts = {k:states.count(k) for k in ('PASS','FAIL','NOT_RUN')}
        actual = status or ('FAIL' if counts['FAIL'] else 'PASS')
        (self.evidence / 'summary.json').write_text(json.dumps({
            'schema':1, 'suite':'coroutine-contract',
            'selected_cases':self.declared,'cases':cases,
            'status':actual, 'counts':counts,
        }))
        return MOD.parse_coroutine_contract(self.log(),self.declared,
            rc if rc is not None else (1 if counts['FAIL'] else 0))

    def test_complete_two_case_evidence_passes(self):
        result = self.put()
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['counts'], {'PASS':2,'FAIL':0,'SKIP':0,
                                             'BLOCKED':0,'TOTAL':2})
        self.assertEqual([x['id'] for x in result['cases']],self.declared)

    def test_failure_preserves_not_run_and_returns_fail(self):
        result = self.put(['FAIL','NOT_RUN'])
        self.assertEqual(result['status'],'FAIL')
        self.assertEqual(result['cases'][1]['status'],'NOT_RUN')

    def test_all_pass_with_wrong_process_rc_refused(self):
        with self.assertRaises(MOD.VerificationError):
            self.put(rc=1)

    def test_mid_suite_fail_cannot_hide_later_pass(self):
        with self.assertRaises(MOD.VerificationError):
            self.put(['FAIL','PASS'])

    def test_missing_paired_receipt_refused(self):
        (self.root / self.rows[0]['paired_evidence'] / 'result.json').unlink()
        with self.assertRaises(MOD.VerificationError):
            self.put()

    def test_source_pair_false_positive_refused(self):
        file = self.root / self.rows[0]['paired_evidence'] / 'result.json'
        content = json.loads(file.read_text())
        content['paths']['native']['status'] = 'FAIL'
        file.write_text(json.dumps(content))
        with self.assertRaises(MOD.VerificationError):
            self.put()

    def test_duplicate_evidence_marker_refused(self):
        self.put()
        with self.assertRaises(MOD.VerificationError):
            MOD.parse_coroutine_contract(self.log() + self.log(),self.declared,0)

    def test_coordinator_new_suite_command_and_progress(self):
        command = MOD.suite_command('coroutine-contract',
                                    {'coroutine-contract':self.declared},None,False)
        self.assertEqual(command[-2:], [str(MOD.COROUTINE_CONTRACT),'--run'])
        self.assertEqual(MOD.progress_case('coroutine-contract',
            'PASS    co6-nested: exact paired MVS oracle and JES receipt'),
            'PASS    co6-nested')
        self.assertIn('coroutine-contract', MOD.SUITES)
        self.assertIn('mr10-coroutines', MOD.SUITES)

    def test_co6_host_check_pins_case_manifest(self):
        manifest = MOD.COROUTINE_CONTRACT_MANIFEST
        manifest.parent.mkdir(parents=True)
        manifest.write_text('case_id\trunner\toracle\nco6-pair\tx\ty\nco6-nested\ta\tb\n')
        runner = MOD.COROUTINE_CONTRACT
        runner.parent.mkdir(parents=True)
        runner.write_text('#!/bin/sh\nexit 0\n')
        with patch.object(MOD.subprocess, 'run', return_value=SimpleNamespace(
                returncode=0,stdout='CHECK PASS',stderr='')):
            self.assertEqual(MOD.coroutine_contract_cases(),self.declared)
        manifest.write_text(manifest.read_text().replace('co6-nested','co6-other'))
        with patch.object(MOD.subprocess, 'run', return_value=SimpleNamespace(
                returncode=0,stdout='CHECK PASS',stderr='')):
            with self.assertRaises(MOD.VerificationError):
                MOD.coroutine_contract_cases()


if __name__=='__main__':
    unittest.main()
