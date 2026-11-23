"""Offline positive/negative validation of saved-JOB RC3 human review gate."""
import importlib.machinery
import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/ta2-rc3-human-review'
loader = importlib.machinery.SourceFileLoader('ta2_r3_human_review_test', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def cases():
    result=[]
    for n in range(1,13):
        result.append({'step':f'R{n:02d}', 'name':f'case-{n}', 'actual_test':f'CASE {n}',
                       'printed_exp':[f'EXP: {n}'], 'actual_rp':[f'RP: {n}'],
                       'interpreted_codes':[0], 'checks':{
                           'test_identity':True,'rp_matches_golden':True,
                           'interpreted_code_zero':True,'exp_present':True,
                           'exp_matches_golden':True},'golden_and_code_match':True})
    return result


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=mod.WORK)
        self.addCleanup(self.temp.cleanup)
        self.work=Path(self.temp.name)
        self.folder=self.work/'original';self.folder.mkdir()
        self.marker=self.work/'marker.json'
        self.rc3=Mock()
        self.rc3.digest.side_effect=lambda b:hashlib.sha256(b).hexdigest()
        self.rc3.plan.return_value=(None,[('test',None,None)]*12,None,None,None,'MRREGRES')
        self.restore=Mock(CANDIDATE='BCPL-0.1.0-rc3', VOL='BC0003',AWS_SHA256='SHA')
        self.restore.digest.return_value='SHA'
        self.installed=Mock()
        self.reviewer=Mock()
        self.result={'status':'RC3_INSTALLED_MR10_EXP_RP_CODE_PASS_HUMAN_SIGNOFF_PENDING',
             'candidate':self.restore.CANDIDATE,'volser':self.restore.VOL,
             'aws_sha256':self.restore.AWS_SHA256,'original_restore_job':9363,
             'mvs_jobs':{'catalog':9367,'directory':9368,'regression':9369},
             'verified_datasets':21,'verified_members':146,
             'mr10_steps':63,'mr10_cases':12,'exp_rp_code':True,
             'human_signoff':'PENDING','publication_authorized':False}
        self.semantic={'mvs_job':9369,'candidate_id':'BCPL-0.1.0-rc3',
                       'observed_test_count':12,'cases':cases(),
                       'human_signoff':'PENDING','publication_authorized':False}
        self.rc3.validated_semantics.return_value=self.semantic
        self.marker.write_text(json.dumps({
             'status':'OWNER_APPROVED_RC3_INSTALLED_MR10_NO_RETRY',
             'candidate':'BCPL-0.1.0-rc3','volser':'BC0003',
             'original_restore_job':9363,
             'verification_jobs':{'catalog':9367,'directory':9368},
             'image_sha256':'SHA','evidence':self.folder.relative_to(mod.ROOT).as_posix(),
             'no_media_operations':True,'no_restore':True,
             'publication_authorized':False}))
        (self.folder/'result.json').write_text(json.dumps(self.result))
        (self.folder/'semantic-review.json').write_text(json.dumps(self.semantic))
        (self.folder/'regression-summary.txt').write_text(
             'JOB 9369 TA2R3MR\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n')
        (self.folder/'regression-report.txt').write_text('MVS SYSOUT')

    def accepted(self):
        with patch.object(mod,'ORIGINAL',self.folder), patch.object(mod,'ORIGINAL_MARKER',self.marker):
            return mod.accepted(self.rc3,self.installed,self.restore,self.reviewer)

    def test_valid_immutable_12_case_original(self):
        self.assertEqual(len(self.accepted()),12)
        self.installed.sealed.assert_called_once()
        self.rc3.verify_regression_execution.assert_called_once()
        self.restore.digest.assert_called_once()

    def test_missing_original_marker_fails(self):
        self.marker.unlink()
        with self.assertRaisesRegex(mod.Refusal,'marker not found'):
            self.accepted()

    def test_wrong_marker_job_fails(self):
        m=json.loads(self.marker.read_text());m['verification_jobs']['catalog']=9999
        self.marker.write_text(json.dumps(m))
        with self.assertRaisesRegex(mod.Refusal,'marker not exact'):
            self.accepted()

    def test_modified_original_acceptance_receipt_fails(self):
        self.result['verified_datasets']=20
        (self.folder/'result.json').write_text(json.dumps(self.result))
        with self.assertRaisesRegex(mod.Refusal,'acceptance receipt differs'):
            self.accepted()

    def test_wrong_mvs_job_identity_fails(self):
        (self.folder/'regression-summary.txt').write_text('JOB 9370 TA2R3MR\n')
        with self.assertRaisesRegex(mod.Refusal,'JOB 9369 result differs'):
            self.accepted()

    def test_semantic_receipt_vs_actual_mvs_mismatch_fails(self):
        self.semantic['cases'][0]['actual_rp']=['RP: WRONG']
        with self.assertRaisesRegex(mod.Refusal,'semantic receipt differs'):
            self.accepted()

    def test_case_exp_mismatch_fails(self):
        self.semantic['cases'][0]['checks']['exp_matches_golden']=False
        (self.folder/'semantic-review.json').write_text(json.dumps(self.semantic))
        with self.assertRaisesRegex(mod.Refusal,'automated semantic comparison not PASS'):
            self.accepted()

    def test_case_nonzero_interpreter_code_fails(self):
        self.semantic['cases'][0]['interpreted_codes']=[4]
        (self.folder/'semantic-review.json').write_text(json.dumps(self.semantic))
        with self.assertRaisesRegex(mod.Refusal,'automated semantic comparison not PASS'):
            self.accepted()

    def test_wrong_media_hash_fails(self):
        self.restore.digest.return_value='OTHER'
        with self.assertRaisesRegex(mod.Refusal,'image changed'):
            self.accepted()

    def test_human_12_cases_and_identified_signoff(self):
        prompts=iter(['P']*12+['Reviewer-1','SIGN'])
        decision,name=mod.human_decisions(cases(),lambda _:next(prompts))
        self.assertEqual(name,'Reviewer-1')
        self.assertEqual(len(decision),12)
        self.assertTrue(all(x['human_verdict']=='PASS' for x in decision))

    def test_human_case_fail_is_preserved(self):
        prompts=iter(['F']+['P']*11+['Reviewer-2','SIGN'])
        decision,_=mod.human_decisions(cases(),lambda _:next(prompts))
        self.assertEqual(decision[0]['human_verdict'],'FAIL')

    def test_unconfirmed_human_signoff_fails(self):
        prompts=iter(['P']*12+['Reviewer','NO'])
        with self.assertRaisesRegex(mod.Refusal,'sign-off not received'):
            mod.human_decisions(cases(),lambda _:next(prompts))

    def test_human_incomplete_12_case_review_fails(self):
        with self.assertRaisesRegex(mod.Refusal,'incomplete or aborted'):
            mod.human_decisions(cases(),lambda _:'Q')

    def test_human_invalid_signer_fails(self):
        prompts=iter(['P']*12+['','SIGN'])
        with self.assertRaisesRegex(mod.Refusal,'reviewer identifier'):
            mod.human_decisions(cases(),lambda _:next(prompts))

    def mocked_run(self, signoff, answers=(), *, compact=False):
        output=self.work/'review';output.mkdir(exist_ok=True)
        self.rc3.artifact.side_effect=lambda folder,name,data:(folder/name).write_text(data)
        self.rc3.seal.side_effect=lambda folder:(folder/'SHA256SUMS').write_text('sealed')
        from unittest.mock import patch as p
        from types import SimpleNamespace
        source=Mock(name='source',exec_module=Mock())
        source.name='source-name'
        spec=SimpleNamespace(loader=source)
        with p.object(mod,'OUT',output), \
             p('pathlib.Path.is_file',return_value=True), \
             p('importlib.machinery.SourceFileLoader',return_value=source), \
             p('importlib.util.spec_from_loader',return_value=spec), \
             p('importlib.util.module_from_spec',side_effect=[self.rc3,self.installed,self.restore,self.reviewer]), \
             p.object(mod,'accepted',return_value=cases()), \
             p.object(mod.sys.stdin,'isatty',return_value=True):
            rc=mod.run(signoff,ask=lambda _:next(answers),compact=compact)
        files=list(output.glob('review-*/review.json'))
        self.assertEqual(len(files),1)
        return rc,json.loads(files[0].read_text())

    def test_no_signoff_creates_pending_receipt_only(self):
        rc,receipt=self.mocked_run(False)
        self.assertEqual(rc,0)
        self.assertEqual(receipt['human_signoff'],'PENDING')
        self.assertEqual(receipt['status'],'AUTOMATED_12_CASES_PASS_HUMAN_REVIEW_PENDING')
        self.assertTrue(all(x['human_verdict']=='PENDING' for x in receipt['cases']))
        self.rc3.mvs_job.assert_not_called()
        self.rc3.run_command.assert_not_called()

    def test_interactive_signoff_all_12_pass(self):
        rc,receipt=self.mocked_run(True,iter(['P']*12+['Reviewer-1','SIGN']))
        self.assertEqual(rc,0)
        self.assertEqual(receipt['status'],'SIGNED_12_CASES_PASS_HUMAN_VERDICT')
        self.assertEqual(receipt['human_signoff'],'RECORDED')
        self.assertEqual(receipt['reviewer_identifier'],'Reviewer-1')
        self.assertEqual(len(receipt['cases']),12)
        self.assertFalse(receipt['publication_authorized'])
        self.rc3.mvs_job.assert_not_called()

    def test_interactive_one_case_fail_blocks_release(self):
        rc,receipt=self.mocked_run(True,iter(['F']+['P']*11+['Reviewer-2','SIGN']))
        self.assertEqual(rc,2)
        self.assertEqual(receipt['status'],'SIGNED_CASE_FAILURES_RELEASE_BLOCKED')
        self.assertEqual(receipt['cases'][0]['human_verdict'],'FAIL')
        self.assertFalse(receipt['publication_authorized'])

    def test_compact_one_line_all_pass_identified_signed(self):
        answers=iter(['PPPPPPPPPPPP reviewer-1 SIGN'])
        rc,receipt=self.mocked_run(True,answers,compact=True)
        self.assertEqual(rc,0)
        self.assertEqual(receipt['status'],'SIGNED_12_CASES_PASS_HUMAN_VERDICT')
        self.assertEqual(receipt['reviewer_identifier'],'reviewer-1')
        self.assertEqual(receipt['human_signature_token'],'SIGN')
        self.assertEqual(receipt['signoff_input_mode'],'COMPACT_ONE_LINE')
        self.assertEqual(len(receipt['cases']),12)
        self.assertTrue(all(x['human_verdict']=='PASS' for x in receipt['cases']))
        self.assertFalse(receipt['publication_authorized'])
        self.rc3.mvs_job.assert_not_called()

    def test_compact_one_line_failure_blocks(self):
        rc,receipt=self.mocked_run(True,iter(['PPFPPPPPPPPP reviewer-2 SIGN']),
                                    compact=True)
        self.assertEqual(rc,2)
        self.assertEqual(receipt['cases'][2]['human_verdict'],'FAIL')
        self.assertEqual(receipt['status'],'SIGNED_CASE_FAILURES_RELEASE_BLOCKED')

    def test_compact_one_line_invalid_input_refused(self):
        for entry in ('PPPPPPPPPPP reviewer SIGN',
                      'PPPPPPPPPPPP reviewer sign',
                      'PPPPPPPPPPPP SIGN',
                      'PPPPPPPPPPPP reviewer SIGN EXTRA',
                      'PPPPPPPPPPPPP reviewer SIGN',
                      'QQQQQQQQQQQQ reviewer SIGN'):
            with self.subTest(entry=entry), self.assertRaises(mod.Refusal):
                mod.compact_human_decisions(cases(),lambda _:entry)

    def test_compact_requires_exact_order_and_case_count(self):
        for invalid in (cases()[:11],list(reversed(cases()))):
            with self.subTest(case_count=len(invalid)), self.assertRaises(mod.Refusal):
                mod.compact_human_decisions(invalid,lambda _:'PPPPPPPPPPPP reviewer SIGN')

    def test_compact_asks_once_after_displaying_twelve_cases(self):
        seen=[]
        def ask(prompt):
            self.assertEqual(seen,[f'R{i:02d}' for i in range(1,13)])
            return 'PPPPPPPPPPPP reviewer SIGN'
        with patch.object(mod,'show_case',side_effect=lambda c:seen.append(c['step'])):
            reviewed,reviewer=mod.compact_human_decisions(cases(),ask)
        self.assertEqual(len(reviewed),12)
        self.assertEqual(reviewer,'reviewer')

    def test_compact_refuses_unsigned_mode(self):
        with self.assertRaisesRegex(mod.Refusal, 'must collect a signature'):
            mod.run(False, compact=True)


if __name__=='__main__': unittest.main()
