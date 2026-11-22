"""Safety tests for read-only BC0003 MVS recipient/BOOT diagnosis."""
import hashlib
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/ta2-rc3-recipient-diagnostic'
loader=SourceFileLoader('rc3diagnostic',str(SCRIPT))
spec=spec_from_loader(loader.name,loader)
mod=module_from_spec(spec)
spec.loader.exec_module(mod)


def rows():
    return [{'target':f'HERC02.BCPL.TA2R3I.{i:02d}',
             'dcb':{'dsorg':'PS' if i==0 else 'PO','recfm':'FB',
                    'lrecl':80,'blksize':800},
             'members':[] if i==0 else [f'M{i:07d}']}
            for i in range(21)]

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=mod.WORK)
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.rc3=Mock(VOLUME='TSO002',digest=lambda b:hashlib.sha256(b).hexdigest())
        self.core=Mock()
        self.core.dataset_missing.return_value=False
        self.core.extract_listds_block.side_effect=lambda report,dsn:[dsn]
        self.core.parse_listds.side_effect=lambda block:{'volume':'TSO002', 'dsorg':
            'PS' if block[0].endswith('.00') else 'PO','recfm':'FB','lrecl':'80','blksize':'800'}

    def make_receipt(self):
        base=self.root/'original';base.mkdir()
        summary='JOB 9363 TA2R3RES\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n'
        summary+=''.join(f'R{i:04d} {"IEBGENER" if i==1 else "IEBCOPY"} RC=0000\n' for i in range(1,22))
        report=''.join(f'IEF142I TA2R3RES R{i:04d} - STEP WAS EXECUTED - COND CODE 0000\n' for i in range(1,22))
        files={'failure.json':json.dumps({'status':'HALTED_NO_RETRY',
                'reason':'recipient DCB/volume differs: HERC02.BCPL.TA2R3I.BOOT'}),
               'restore-summary.txt':summary,'restore-report.txt':report,
               'recipient-summary.txt':'JOB 9364 DSPALST','recipient-report.txt':'OLD LISTDS'}
        for name,text in files.items(): (base/name).write_text(text)
        (base/'SHA256SUMS').write_text(''.join(hashlib.sha256((base/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in sorted(files)))
        marker=self.root/'marker.json'
        marker.write_text(json.dumps({'status':'OWNER_APPROVED_BC0003_RESTORE_NO_RETRY',
                                      'candidate':'BCPL-0.1.0-rc3',
                                      'image_sha256':'123',
                                      'evidence':base.relative_to(mod.ROOT).as_posix()}))
        return base,marker

    def test_original_restore_21_steps_and_failure_seal(self):
        base,marker=self.make_receipt()
        continuation=Mock(AWS_SHA256='123')
        with patch.object(mod,'ORIGINAL',base),patch.object(mod,'ORIGINAL_MARKER',marker):
            self.assertEqual(mod.sealed_incident(self.rc3,continuation)[0],9363)

    def test_original_evidence_tamper_rejected(self):
        base,marker=self.make_receipt()
        (base/'restore-report.txt').write_text('ALTERED')
        with patch.object(mod,'ORIGINAL',base),patch.object(mod,'ORIGINAL_MARKER',marker):
            with self.assertRaisesRegex(mod.Refusal,'evidence modified'):
                mod.sealed_incident(self.rc3,Mock(AWS_SHA256='123'))

    def test_original_restore_nonzero_ief142i_rejected(self):
        base,marker=self.make_receipt()
        p=base/'restore-report.txt';p.write_text(p.read_text().replace('COND CODE 0000','COND CODE 0004',1))
        pseal=base/'SHA256SUMS';pseal.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n'
            for p in sorted(base.iterdir()) if p.name!='SHA256SUMS'))
        with patch.object(mod,'ORIGINAL',base),patch.object(mod,'ORIGINAL_MARKER',marker):
            with self.assertRaisesRegex(mod.Refusal,'21-step IEF142I'):
                mod.sealed_incident(self.rc3,Mock(AWS_SHA256='123'))

    def test_catalog_all_expected_match(self):
        result=mod.analyze_catalog(self.core,self.rc3,rows(),'REPORT')
        self.assertEqual(len(result),21)
        self.assertFalse(any(r['mismatches'] for r in result))

    def test_catalog_boot_dcb_discrepancy_fields(self):
        self.core.parse_listds.side_effect=lambda b:{'volume':'TSO002','dsorg':'PS',
                     'recfm':'FB','lrecl':'80','blksize':'3120'}
        result=mod.analyze_catalog(self.core,self.rc3,rows(),'REPORT')
        self.assertEqual(result[0]['mismatches'],['blksize: expected 800, observed 3120'])
        self.assertEqual(result[0]['raw_listds_block'],[rows()[0]['target']])

    def test_catalog_missing_block_does_not_accept(self):
        self.core.extract_listds_block.return_value=[]
        self.core.extract_listds_block.side_effect=None
        result=mod.analyze_catalog(self.core,self.rc3,rows(),'REPORT')
        self.assertEqual(len(result[0]['mismatches']),5)

    def test_member_directory_match_and_duplicate_detection(self):
        ls=Mock()
        selected=rows()
        ls.member_blocks.return_value={r['target']:r['members'] for r in selected[1:]}
        ls.parse_members.side_effect=lambda b:b
        good=mod.analyze_members(ls,selected,'REPORT')
        self.assertTrue(all(r['match'] for r in good))
        ls.member_blocks.return_value[selected[1]['target']]=['M0000001','M0000001']
        bad=mod.analyze_members(ls,selected,'REPORT')
        self.assertFalse(bad[0]['match'])

    def test_member_directory_missing_block_refused_by_match(self):
        ls=Mock()
        selected=rows()
        ls.member_blocks.return_value={r['target']:r['members'] for r in selected[2:]}
        ls.parse_members.side_effect=lambda b:b
        got=mod.analyze_members(ls,selected,'REPORT')
        self.assertFalse(got[0]['match'])

    def test_one_readonly_mvs_job_checks_real_ief142i(self):
        self.core.submit_and_wait.return_value=(9365,'JOB 9365 DSPALST\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n')
        self.core.job_report.return_value='IEF142I DSPALST STAT - STEP WAS EXECUTED - COND CODE 0000\n'
        self.rc3.artifact.side_effect=lambda folder,name,data:(folder/name).write_text(data)
        job,report=mod.submit_readonly(self.core,{},self.rc3,self.root,'catalog','JCL')
        self.assertEqual(job,9365)
        self.assertIn('IEF142I',report)
        self.core.job_report.return_value='IEF142I DSPALST STAT - STEP WAS EXECUTED - COND CODE 0004\n'
        with self.assertRaisesRegex(mod.Refusal,'IEF142I'):
            mod.submit_readonly(self.core,{},self.rc3,self.root,'catalog','JCL')

    def test_mvs_diagnostic_full_mock_flow_no_tape_write(self):
        base,marker=self.make_receipt()
        selected=rows()
        self.rc3.plan.return_value=(selected,[1]*12,None,None,None,None)
        self.rc3.load.side_effect=[self.core,Mock()]
        self.rc3.artifact.side_effect=lambda folder,name,data:(folder/name).write_text(data)
        self.rc3.seal.side_effect=lambda folder:(folder/'SHA256SUMS').write_text('SHA')
        self.core.load_config.return_value={'mvs':{'hlq':'HERC02'}}
        ls=Mock()
        with patch.object(mod,'load',side_effect=[self.rc3,Mock(IMAGE='IMG',AWS_SHA256='123',CANDIDATE='BCPL-0.1.0-rc3',digest=lambda p:'123')]),\
             patch.object(mod,'sealed_incident',return_value=(9363,'SAVED')) ,\
             patch.object(mod,'submit_readonly',side_effect=[(9364,'LIVE'),(9365,'MEMBERS')]),\
             patch.object(mod,'OUT',self.root/'output'),\
             patch.object(mod,'analyze_catalog',return_value=[{'dataset':r['target'],'actual':{},'mismatches':[], 'raw_listds_block':[]} for r in selected]),\
             patch.object(mod,'analyze_members',return_value=[{'dataset':r['target'],'match':True,'actual_count':1} for r in selected[1:]]):
            # Mocks isolate run from the workstation/Hercules entirely.
            self.assertEqual(mod.run(),0)
        self.rc3.run_command.assert_not_called()

if __name__=='__main__': unittest.main()
