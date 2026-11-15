#!/usr/bin/env python3
"""Host-only deterministic verification of CO.4 inspection follow-up."""
from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT/'tools/coroutines/run-co4-inspection-followup.py'
spec = importlib.util.spec_from_file_location('followup', RUNNER)
if spec is None or spec.loader is None:
    raise RuntimeError('followup runner missing')
followup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(followup)


class FollowupTests(unittest.TestCase):
    def test_source_diagnostics_and_two_arg_snapshot(self):
        root = ROOT/'packaging/milestones/coroutines/candidates/co4-inspection-batch'
        class Sources:
            FIXTURE=root
            CASES={'account':('account-source.bcpl','CO4MEM',()),
                   'deny':('deny-source.bcpl','CO4DENY',())}
        followup.source_diagnostics(Sources())
        for key in followup.CASES:
            code=(root/(key+'-source.bcpl')).read_text('ascii')
            self.assertEqual(code.count('PROBEPTR:305'),1)
            self.assertEqual(code.count('AND SNAP(N,B) = VALOF'),1)
            self.assertEqual(code.count('PROBEPTR:=P'),1)
            self.assertEqual(code.count('LET P=PROBEPTR'),
                             2 if key=='account' else 1)
            self.assertNotIn('SNAP(P,',code)
            self.assertEqual(code.count('MARK("PASS")'),1)
            self.assertEqual(code.count('MARK("FAIL")'),1)
            self.assertTrue(all(len(x)<=80 and x.isascii() and
                                "\t" not in x for x in code.splitlines()))

    def test_missing_snapshot_pointer_fails_validation(self):
        root = ROOT/'packaging/milestones/coroutines/candidates/co4-inspection-batch'
        class Sources:
            FIXTURE=root
            CASES={'account':('account-source.bcpl','CO4MEM',()),
                   'deny':('deny-source.bcpl','CO4DENY',())}
        with tempfile.TemporaryDirectory() as t:
            clone=Path(t)
            for key in followup.CASES:
                name=key+'-source.bcpl'
                (clone/name).write_text((root/name).read_text('ascii').replace(
                    'PROBEPTR:=P','PROBEPTR:=0',1),encoding='ascii')
            Sources.FIXTURE=clone
            with self.assertRaisesRegex(followup.FollowupError,'publication drift'):
                followup.source_diagnostics(Sources())

    def test_cases_are_only_account_and_deny(self):
        self.assertEqual(followup.CASES, ('account', 'deny'))

    def test_bootstrap_machine_cursor_differs_until_first_worker(self):
        code=(ROOT/'packaging/milestones/coroutines/candidates/'
              'co4-inspection-batch/account-source.bcpl').read_text('ascii')
        self.assertEqual(code.count('AND BOOTSNAP(N,B) = VALOF'),1)
        self.assertEqual(code.count('IF BOOTSNAP(N+1,BYTES+108)=FALSE'),2)
        self.assertEqual(code.count('IF SNAP(N+1,BYTES+108)=FALSE'),1)
        before_first_worker = code.split('A:=CREATECO(WORK,1024)',1)[0]
        self.assertEqual(before_first_worker.count('IF BOOTSNAP('),2)
        self.assertEqual(before_first_worker.count('IF SNAP('),0)
        self.assertIn('P!4 \\= 0 | CO3CURR \\= CO3ROOT',code)
        # Strict post-CO2INIT CURPTR == CO3CURR condition is retained.
        self.assertIn('IF P!4 \\= CO3CURR DO',code)

    def test_early_machine_pointer_assumption_is_rejected(self):
        source=(ROOT/'packaging/milestones/coroutines/candidates/'
                'co4-inspection-batch')
        class Sources:
            FIXTURE=source
            CASES={'account':('account-source.bcpl','CO4MEM',()),
                   'deny':('deny-source.bcpl','CO4DENY',())}
        with tempfile.TemporaryDirectory() as temp:
            stage=Path(temp)
            for key in followup.CASES:
                name=key+'-source.bcpl'
                data=(source/name).read_text('ascii')
                if key=='account':
                    data=data.replace('IF BOOTSNAP(N+1,BYTES+108)=FALSE',
                                      'IF SNAP(N+1,BYTES+108)=FALSE',1)
                (stage/name).write_text(data,encoding='ascii')
            Sources.FIXTURE=stage
            with self.assertRaisesRegex(followup.FollowupError,'bootstrap CURPTR'):
                followup.source_diagnostics(Sources())

    def test_missing_bootstrap_cursor_diagnostic_rejected(self):
        source=(ROOT/'packaging/milestones/coroutines/candidates/'
                'co4-inspection-batch')
        class Sources:
            FIXTURE=source
            CASES={'account':('account-source.bcpl','CO4MEM',()),
                   'deny':('deny-source.bcpl','CO4DENY',())}
        with tempfile.TemporaryDirectory() as temp:
            stage=Path(temp)
            for key in followup.CASES:
                name=key+'-source.bcpl'
                data=(source/name).read_text('ascii')
                if key=='account':
                    data=data.replace('MARK("FBOOT")','MARK("FOTHER")',1)
                (stage/name).write_text(data,encoding='ascii')
            Sources.FIXTURE=stage
            with self.assertRaisesRegex(followup.FollowupError,'diagnostic marker'):
                followup.source_diagnostics(Sources())

    def test_oracle_only_requires_known_native_job(self):
        case={'status':'FAIL','rc':1,'native_job':'5430',
              'reason':"wrong ordered BCPL records: ['FAIL']"}
        self.assertTrue(followup.oracle_only_failure(case))
        for change in ({'status':'PASS'}, {'rc':0}, {'native_job':None},
                       {'reason':'native JES summary unsuccessful or highest RC nonzero'},
                       {'reason':'unrelated failure'}):
            new={**case,**change}
            self.assertFalse(followup.oracle_only_failure(new))

    def fake_prior(self, outcomes):
        class FakePrior:
            BASE=Path('fake-baseline')
            @staticmethod
            def load_module(*args):
                return object()
            @staticmethod
            def run_one(key, session, previous, pins):
                return outcomes[key]
        return FakePrior()

    def run_synthetic(self, outcomes, *, cases=followup.CASES):
        with tempfile.TemporaryDirectory() as t:
            prior=self.fake_prior(outcomes)
            with mock.patch.object(followup,'validate_inputs',return_value={'cases':{}}):
                with redirect_stdout(io.StringIO()):
                    rc=followup.run_followup(prior,work=Path(t),cases=cases)
            receipt=json.loads(next(Path(t).glob('*/batch-result.json')).read_text())
            return rc, receipt

    def test_both_success(self):
        success=lambda c:{'case':c,'status':'PASS','rc':0}
        rc,rec=self.run_synthetic({'account':success('account'),
                                   'deny':success('deny')})
        self.assertEqual(rc,0)
        self.assertEqual(rec['status'],'PASS')
        self.assertEqual(len(rec['cases']),2)

    def test_continues_after_account_oracle_mismatch(self):
        rc,rec=self.run_synthetic({
            'account':{'case':'account','status':'FAIL','rc':1,
                       'native_job':'5430',
                       'reason':"wrong ordered BCPL records: ['FCOUNT','FAIL']"},
            'deny':{'case':'deny','status':'PASS','rc':0}})
        self.assertEqual(rc,1)
        self.assertEqual([x['case'] for x in rec['cases']],['account','deny'])
        self.assertEqual(rec['status'],'FAIL')

    def test_account_only_does_not_rerun_accepted_deny(self):
        rc,rec=self.run_synthetic({
            'account':{'case':'account','status':'PASS','rc':0}},
            cases=('account',))
        self.assertEqual(rc,0)
        self.assertEqual(rec['status'],'PASS')
        self.assertEqual(rec['selected_cases'],['account'])
        self.assertEqual([x['case'] for x in rec['cases']],['account'])

    def test_bad_selected_cases_rejected(self):
        prior=self.fake_prior({})
        for selection in ((),('account','account'),('unsupported',)):
            with self.subTest(selection=selection):
                with self.assertRaisesRegex(followup.FollowupError,'invalid'):
                    followup.run_followup(prior, cases=selection)

    def test_stops_on_go_abend(self):
        rc,rec=self.run_synthetic({
            'account':{'case':'account','status':'FAIL','rc':1,
                       'native_job':'5430',
                       'reason':'native JES summary unsuccessful or highest RC nonzero'},
            'deny':{'case':'deny','status':'PASS','rc':0}})
        self.assertEqual(rc,1)
        self.assertEqual(len(rec['cases']),1)
        self.assertIn('JES',rec['reason'])

    def test_stops_on_compiler_failure(self):
        rc,rec=self.run_synthetic({
            'account':{'case':'account','status':'FAIL','rc':1,
                       'reason':'CO3ACMP compiler RC=2, jobs=[]'},
            'deny':{'case':'deny','status':'PASS','rc':0}})
        self.assertEqual(rc,1)
        self.assertEqual(len(rec['cases']),1)

    def test_cli_account_selection_does_not_submit_deny(self):
        with (mock.patch('sys.argv',[
                'run-co4-inspection-followup.py','--run','--case','account']),
              mock.patch.object(followup,'load_prior',return_value='PRIOR'),
              mock.patch.object(followup,'run_followup',return_value=0) as run):
            self.assertEqual(followup.main(),0)
        run.assert_called_once_with('PRIOR',cases=('account',))

    def test_cli_check_cannot_select_one_case(self):
        with mock.patch('sys.argv',[
                'run-co4-inspection-followup.py','--check','--case','account']):
            with self.assertRaises(SystemExit) as err:
                followup.main()
            self.assertEqual(err.exception.code,2)

    def test_cli_requires_explicit_action(self):
        with mock.patch('sys.argv',['run-co4-inspection-followup.py']):
            with self.assertRaises(SystemExit) as err:
                followup.main()
            self.assertEqual(err.exception.code,2)


if __name__ == '__main__':
    unittest.main()
