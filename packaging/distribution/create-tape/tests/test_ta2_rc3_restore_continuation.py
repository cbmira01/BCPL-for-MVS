"""TA.2 BC0003 restore continuation isolated safety and MVS orchestration tests."""
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/ta2-rc3-restore-continuation'
loader = importlib.machinery.SourceFileLoader('ta2_rc3_continue', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=mod.WORK)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def fake_receipt(self):
        original = self.root / 'original'
        original.mkdir()
        (original / 'failure.json').write_text(json.dumps(mod.FAILURE))
        (original / 'stage-summary.txt').write_text('stage summary')
        (original / 'stage-report.txt').write_text('stage report')
        (original / 'write-summary.txt').write_text('write summary')
        (original / 'write-report.txt').write_text('write report')
        (original / 'aws-labels.txt').write_text('labels')
        (original / 'aws-files.txt').write_text('files')
        (original / 'drive-h-3.txt').write_text('Hercules 480 empty')
        (original / 'drive-m-3.txt').write_text('MVS 480 O-NRD')
        manifest = ''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name + '\n'
                           for p in sorted(original.iterdir()))
        (original / 'SHA256SUMS').write_text(manifest)
        marker = self.root / 'marker.json'
        marker.write_text(json.dumps({'status':'ONE_SHOT_CONSENT_CONSUMED_NO_RETRY',
             'candidate': mod.CANDIDATE, 'volser': mod.VOL,
             'evidence': original.relative_to(mod.ROOT).as_posix()}))
        return original, marker

    def test_sealed_original_receipt_and_marker(self):
        original, marker = self.fake_receipt()
        with patch.object(mod,'ORIGINAL',original), patch.object(mod,'ORIGINAL_MARKER',marker):
            self.assertEqual(len(mod.sealed_original()),9)
            (original / 'failure.json').write_text('modified')
            with self.assertRaisesRegex(mod.Refusal, 'original receipt modified'):
                mod.sealed_original()

    def test_sealed_original_rejects_extra_file(self):
        original, marker = self.fake_receipt()
        (original/'not-sealed').write_text('x')
        with patch.object(mod,'ORIGINAL',original), patch.object(mod,'ORIGINAL_MARKER',marker):
            with self.assertRaisesRegex(mod.Refusal, 'receipt changed'):
                mod.sealed_original()

    def test_original_jes_exact_steps(self):
        original, _ = self.fake_receipt()
        jobs = [('S0001','IEBGENER'),('S0002','IEBCOPY')]
        summary = 'JOB 9360 TA2R3STG\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n'
        summary += ''.join(f'{step} {pgm} RC=0000\n' for step,pgm in jobs)
        report = ''.join(f'IEF142I TA2R3STG {step} - STEP WAS EXECUTED - COND CODE 0000\n' for step,_ in jobs)
        (original / 'stage-summary.txt').write_text(summary)
        (original / 'stage-report.txt').write_text(report)
        with patch.object(mod,'ORIGINAL',original):
            mod.checked_original_job('stage','TA2R3STG',jobs)
            with self.assertRaisesRegex(mod.Refusal,'original stage JES steps'):
                mod.checked_original_job('stage','TA2R3STG',jobs+[('S0003','IEBCOPY')])
            (original / 'stage-report.txt').write_text(report.replace('0000','0004'))
            with self.assertRaisesRegex(mod.Refusal,'IEF142I'):
                mod.checked_original_job('stage','TA2R3STG',jobs)

    def test_digest_requires_regular_unmodified_file(self):
        image = self.root/'test.aws'
        image.write_bytes(b'test media')
        self.assertEqual(mod.digest(image),hashlib.sha256(b'test media').hexdigest())
        with self.assertRaisesRegex(mod.Refusal,'missing/linked'):
            mod.digest(self.root/'absent.aws')

    def directory_stubs(self):
        dsns = [f'HERC02.BCPL.TA2R3I.T{i:04d}' for i in range(2,22)]
        members = [[f'X{k:07d}' for k in range(1+(i*7),1+((i+1)*7))]
                   for i in range(20)]
        members[-1] += [f'Y{k:07d}' for k in range(6)]
        rows = [{'target':dsn,'members':list(names)} for dsn,names in zip(dsns,members)]
        rows.insert(0,{'target':'HERC02.BCPL.TA2R3I.BOOT','members':[]})
        self.assertEqual(sum(len(r['members']) for r in rows),146)
        rc3 = Mock()
        rc3.load.return_value.list_members_deck.return_value = 'DIRECTORY JCL'
        rc3.load.return_value.member_blocks.return_value = {r['target']:r['members'] for r in rows[1:]}
        rc3.load.return_value.parse_members.side_effect = lambda b:b
        core=Mock()
        core.submit_and_wait.return_value=(9372,'JOB 9372 DSPALLS\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n')
        core.job_report.return_value='IEF142I DSPALLS LIST - STEP WAS EXECUTED - COND CODE 0000'
        return rc3,core,rows

    def test_146_member_directory_success_and_refusal(self):
        rc3,core,rows = self.directory_stubs()
        with patch.object(mod,'ROOT',self.root), patch.object(mod,'tempfile',mod.tempfile):
            self.assertEqual(mod.directory_check(rc3,core,{},self.root,rows),(9372,146))
            rc3.load.return_value.member_blocks.return_value.pop(rows[1]['target'])
            with self.assertRaisesRegex(mod.Refusal,'missing/extra PDS'):
                mod.directory_check(rc3,core,{},self.root,rows)

    def test_directory_refuses_duplicate_and_unexpected_members(self):
        rc3,core,rows = self.directory_stubs()
        blocks=rc3.load.return_value.member_blocks.return_value
        blocks[rows[1]['target']][0]=blocks[rows[1]['target']][1]
        with self.assertRaisesRegex(mod.Refusal,'member directory differs'):
            mod.directory_check(rc3,core,{},self.root,rows)

    def test_target_absence_checks_all_21(self):
        dsns = [f'HERC02.BCPL.TA2R3I.TEST{i:04d}' for i in range(21)]
        rows = [{'target':name} for name in dsns]
        core=Mock()
        core.submit_and_wait.return_value=(9371,'JOB 9371 DSPALST\n')
        core.dataset_missing.return_value=True
        rc3=Mock()
        self.assertEqual(mod.check_new_targets(core,{},rc3,self.root,rows),9371)
        core.dataset_missing.side_effect=lambda r,name:name!=dsns[-1]
        with self.assertRaisesRegex(mod.Refusal,'recipient already exists'):
            mod.check_new_targets(core,{},rc3,self.root,rows)

    def test_read_only_plan_never_mounts_or_submits(self):
        original = self.root/'original'; original.mkdir()
        rc3,core,rows=self.directory_stubs()
        rc3.plan.return_value=(rows,[1]*12,None,None,'DISP=(NEW,CATLG,DELETE)'*21,
                               'MR10KIT.'*40)
        rc3.INSTALL=''
        rc3.load.return_value=Mock()
        with patch.object(mod,'load_rc3',return_value=rc3), \
             patch.object(mod,'accepted_tape',return_value={}), \
             patch.object(mod,'MARKER',self.root/'no-marker'):
            self.assertEqual(mod.run(False),0)
            core.submit_and_wait.assert_not_called()

    def test_consumed_continuation_refuses_without_mvs(self):
        marker = self.root/'consumed'
        marker.write_text('consumed')
        rc3 = Mock()
        with patch.object(mod,'load_rc3',return_value=rc3), \
             patch.object(mod,'MARKER',marker), \
             patch.object(mod.sys.stdin,'isatty',return_value=True):
            self.assertEqual(mod.run(True),2)
            rc3.plan.assert_not_called()

    def test_complete_one_shot_simulation_without_tape_rewrite(self):
        rc3,core,rows = self.directory_stubs()
        rc3.plan.return_value=(rows,[1]*12,None,None,'DISP=(NEW,CATLG,DELETE)'*21,
                               ('MR10KIT.'*40))
        rc3.INSTALL=''
        rc3.JOBS={'restore':'TA2R3RES','regression':'TA2R3MR'}
        rc3.drive.side_effect=['EMPTY','RC3','EMPTY']
        rc3.load.side_effect=[Mock(),core,Mock(),Mock(),Mock(),Mock()]
        core.load_config.return_value={'mvs':{'hlq':'HERC02'}}
        rc3.exclusive.side_effect=lambda p,data:p.write_bytes(data)
        rc3.mvs_job.side_effect=[(9376,'RESTORED','RESTORE SUMMARY'),
                                 (9379,'MR OUTPUT','JOB 9379 TA2R3MR')]
        rc3.catalog.return_value=9377
        rc3.validated_semantics.return_value={'status':'EXP_RP_CODE_COMPARISON_PASS_HUMAN_SIGNOFF_PENDING'}
        rc3.JOBS['regression']='TA2R3MR'
        original_out = self.root/'output';original_out.mkdir()
        with patch.object(mod,'load_rc3',return_value=rc3),\
             patch.object(mod,'accepted_tape',return_value={}),\
             patch.object(mod,'digest',return_value=mod.AWS_SHA256),\
             patch.object(mod,'fresh_tape'),\
             patch.object(mod,'check_new_targets',return_value=9375),\
             patch.object(mod,'directory_check',return_value=(9378,146)),\
             patch.object(mod,'OUT',original_out),\
             patch.object(mod,'MARKER',original_out/'once.json'),\
             patch.object(mod.sys.stdin,'isatty',return_value=True),\
             patch('builtins.input',return_value='Y'):
            self.assertEqual(mod.run(True),0)
            self.assertTrue((original_out/'once.json').exists())
            rc3.mvs_job.assert_called()
            calls=[str(x) for x in rc3.run_command.call_args_list]
            self.assertEqual(len(calls),1)
            self.assertIn('mount-existing',calls[0])
            self.assertFalse(any('hetinit' in x for x in calls))
            self.assertFalse(any('unmount' in x for x in calls))


if __name__ == '__main__':
    unittest.main()
