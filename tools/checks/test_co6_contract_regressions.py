"""Host-only tests for the two-case paired System/370/MR10 regression panel.

Synthetic child scripts and JES receipts; no MVS submission or network access.
"""
from __future__ import annotations

import contextlib
import importlib.util
from importlib.machinery import SourceFileLoader
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / 'coroutines/run-co6-contract-regressions.py'
loader = SourceFileLoader('co6_contract_runner_test_module', str(SRC))
spec = importlib.util.spec_from_loader(loader.name, loader)
assert spec and spec.loader
MOD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MOD)


class CO6ContractSuiteTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='co6-contract-test-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for name, target in {
            'ROOT': self.root,
            'MANIFEST': self.root / 'tests/suites/coroutine-contract.tsv',
            'WORK': self.root / 'workarea/co6-contract-regressions',
        }.items():
            patcher = patch.object(MOD, name, target)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch.object(MOD, 'git_head', return_value='a'*40)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.fixtures()

    def fixtures(self):
        MOD.MANIFEST.parent.mkdir(parents=True)
        MOD.MANIFEST.write_text('case_id\trunner\toracle\n' + ''.join(
            f'{c[0]}\t{c[1]}\t{c[2]}\n' for c in MOD.CASES), encoding='ascii')
        for ident, runner, oracle, prefix, evidence, count in MOD.CASES:
            target = self.root / oracle
            target.parent.mkdir(parents=True)
            target.write_text(''.join(f'{prefix} T{i}\n' for i in range(1,count)) +
                              f'{prefix} PASS\n', encoding='ascii')
            runpath = self.root / runner
            runpath.parent.mkdir(parents=True, exist_ok=True)
            runpath.write_text('''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys
if sys.argv[1:] == ['--check']:
    print('HOST CHECK PASS')
    sys.exit(0)
assert sys.argv[1:] == ['--run']
ident, root, oracle = %r, Path(%r), Path(%r)
with (root / 'executed').open('a') as output:
    output.write(ident + '\\n')
if os.environ.get('FAKE_CO6_FAILURE') == ident:
    print('child failed')
    sys.exit(1)
path = root / ('workarea/' + ident) / 'session'
path.mkdir(parents=True, exist_ok=True)
prefix_records = [x.split(' ',1)[1] for x in oracle.read_text().splitlines()]
mr10 = {'status': 'PASS', 'records': prefix_records,
        'steps': 14, 'phase_codes': [0]*7, 'job': '8121'}
native = {'status': 'PASS', 'records': list(prefix_records),
          'steps': {'ASMA':0,'ASML':0,'ASMM':0,'ASMS':0,'LKED':0,'GO':0},
          'compiler_jobs':['8122','8123'], 'native_job':'8124'}
mode = os.environ.get('FAKE_CO6_TAMPER','')
if mode == 'MR10_CODE' and ident == 'co6-pair':
    mr10['phase_codes'][-1] = -1
if mode == 'NATIVE_RECORD' and ident == 'co6-nested':
    native['records'][-1] = 'FAIL'
payload = {'status':'PASS', 'selected':['mr10','native'],
           'paths':{'mr10':mr10,'native':native}}
(path / 'result.json').write_text(json.dumps(payload))
if mode == 'WRONG_PATH' and ident == 'co6-pair':
    path = root / 'workarea' / 'unrelated' / 'session'
print('CO.6 PAIRED EVIDENCE: ' + str(path.relative_to(root)))
''' % (ident, str(self.root), str(target)), encoding='utf-8')
            runpath.chmod(0o755)

    def invoke(self, *arguments):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = MOD.main(list(arguments))
        return rc, stdout.getvalue(), stderr.getvalue()

    def result(self):
        runs = list(MOD.WORK.iterdir())
        self.assertEqual(len(runs), 1)
        return json.loads((runs[0]/'summary.json').read_text('utf-8'))

    def test_check_and_list_are_host_only(self):
        rc, out, error = self.invoke('--check')
        self.assertEqual((rc,error),(0,''))
        self.assertIn('2 cases; host-only',out)
        rc, out, _ = self.invoke('--list')
        self.assertEqual(rc,0)
        self.assertIn('co6-nested',out)
        self.assertFalse((self.root / 'executed').exists())
        self.assertFalse(MOD.WORK.exists())

    def test_two_valid_receipts_and_independent_case_evidence(self):
        rc, out, error = self.invoke('--run')
        self.assertEqual((rc,error),(0,''))
        self.assertIn('CO6 REGRESSION RESULT: PASS',out)
        data = self.result()
        self.assertEqual(data['status'],'PASS')
        self.assertEqual(data['counts'], {'PASS':2,'FAIL':0,'NOT_RUN':0})
        self.assertEqual(data['git_head'],'a'*40)
        self.assertEqual([r['records'] for r in data['cases']],[11,18])
        self.assertEqual((self.root/'executed').read_text(), 'co6-pair\nco6-nested\n')

    def test_failure_stops_before_next_mvs_candidate(self):
        with patch.dict(os.environ, {'FAKE_CO6_FAILURE':'co6-pair'}):
            rc, out, error = self.invoke('--run')
        self.assertEqual((rc,error),(1,''))
        self.assertIn('CO6 REGRESSION RESULT: FAIL',out)
        result = self.result()
        self.assertEqual([x['status'] for x in result['cases']], ['FAIL','NOT_RUN'])
        self.assertEqual((self.root/'executed').read_text(),'co6-pair\n')

    def test_second_failure_preserves_first_pass(self):
        with patch.dict(os.environ, {'FAKE_CO6_FAILURE':'co6-nested'}):
            rc, _, _ = self.invoke('--run')
        self.assertEqual(rc,1)
        data = self.result()
        self.assertEqual([x['status'] for x in data['cases']], ['PASS','FAIL'])
        self.assertEqual(data['counts']['PASS'],1)

    def test_mr10_phase_negative_is_not_pass(self):
        with patch.dict(os.environ, {'FAKE_CO6_TAMPER':'MR10_CODE'}):
            rc, _, _ = self.invoke('--run')
        self.assertEqual(rc,1)
        self.assertIn('ICINT/JES',self.result()['cases'][0]['reason'])

    def test_native_oracle_mismatch_is_not_pass(self):
        with patch.dict(os.environ, {'FAKE_CO6_TAMPER':'NATIVE_RECORD'}):
            rc, _, _ = self.invoke('--run')
        self.assertEqual(rc,1)
        self.assertIn('native Cambridge',self.result()['cases'][1]['reason'])

    def test_evidence_outside_case_root_rejected(self):
        with patch.dict(os.environ, {'FAKE_CO6_TAMPER':'WRONG_PATH'}):
            rc, _, _ = self.invoke('--run')
        self.assertEqual(rc,1)
        self.assertIn('outside independent paired',self.result()['cases'][0]['reason'])

    def test_manifest_case_identity_is_pinned(self):
        MOD.MANIFEST.write_text(MOD.MANIFEST.read_text().replace(
            'co6-nested\t', 'co6-nestedd\t'))
        rc, _, error = self.invoke('--check')
        self.assertEqual(rc,2)
        self.assertIn('contract mismatch',error)
        self.assertFalse(MOD.WORK.exists())

    def test_oracle_requires_complete_unique_records(self):
        p = self.root / MOD.CASES[0][2]
        p.write_text(p.read_text().replace('CO6PAIR T1','CO6PAIR PASS'))
        self.assertEqual(self.invoke('--check')[0],2)
        self.assertFalse(MOD.WORK.exists())

    def test_partial_receipt_cannot_be_pass(self):
        case = MOD.CASES[0]
        text = (self.root / case[2]).read_text()
        tokens = [x.split(' ',1)[1] for x in text.splitlines()]
        good = {'status':'PASS','selected':['mr10','native'],
                'paths':{'mr10':{'status':'PASS','records':tokens,
                       'steps':14,'phase_codes':[0]*7,'job':'99'},
                       'native':{'status':'PASS','records':tokens,
                       'steps':MOD.NATIVE_STEPS,'compiler_jobs':['1','2'],
                       'native_job':'3'}}}
        MOD.strict_receipt(good,case)
        good['paths']['mr10']['steps'] = 13
        with self.assertRaises(MOD.RegressionError):
            MOD.strict_receipt(good,case)


if __name__=='__main__':
    unittest.main()
