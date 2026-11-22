"""Isolated real-parser, evidence, MVS refusal and orchestration tests."""
from __future__ import annotations
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec,spec_from_loader
import hashlib,json
from pathlib import Path
import tempfile,unittest
from unittest.mock import Mock, patch

SRC=Path(__file__).resolve().parents[1]/'scripts/ta2-rc3-installed-mr10-continuation'
loader=SourceFileLoader('ta2r3_mr_cont_test',str(SRC))
spec=spec_from_loader(loader.name,loader)
mod=module_from_spec(spec)
spec.loader.exec_module(mod)

BOOT='HERC02.BCPL.TA2R3I.BOOT'
OTHER=BOOT+'.JCL'

def make_block(dsn,org):
    return (f'{dsn}\n--RECFM-LRECL-BLKSIZE-DSORG\n'
            f'  FB    80    800     {org}\n--VOLUMES--\n  TSO002\n'
            '--FORMAT 1 DSCB--\nF1 C4C1E3C1 0001 1A0147\n')


def parse_listds(block):
    x=' '.join(block)
    return {'volume':'TSO002','recfm':'FB','lrecl':'80','blksize':'800',
            'dsorg':'PS' if '     PS' in x else 'PO'}


def rows():
    return [{'target':BOOT if i==0 else (OTHER if i==1 else f'HERC02.BCPL.TA2R3I.T{i:02d}'),
             'dcb':{'dsorg':'PS' if i==0 else 'PO',
                    'recfm':'FB','lrecl':80,'blksize':800},
             'members':[] if i==0 else [f'M{i:07d}']}
            for i in range(21)]


def full_report():
    return "LISTDS '"+BOOT+"' LABEL\n"+ ''.join(make_block(r['target'],r['dcb']['dsorg']) for r in rows())


class Tests(unittest.TestCase):
    def setUp(self):
        self.scratch=tempfile.TemporaryDirectory(dir=mod.WORK)
        self.addCleanup(self.scratch.cleanup)
        self.work=Path(self.scratch.name)
        self.core=Mock()
        self.core.parse_listds.side_effect=parse_listds
        self.core.dataset_missing.return_value=False
        self.rc3=Mock()
        self.rc3.VOLUME='TSO002'
        self.rc3.digest.side_effect=lambda b:hashlib.sha256(b).hexdigest()

    def test_exact_boot_vs_boot_jcl_prefix_collision(self):
        data=make_block(BOOT,'PS')+make_block(OTHER,'PO')
        got, block=mod.exact_listds(self.core,data,BOOT)
        self.assertEqual(got['dsorg'],'PS')
        self.assertEqual(block[0],BOOT)
        self.assertNotIn(OTHER,block)
        self.assertEqual(mod.exact_listds(self.core,data,OTHER)[0]['dsorg'],'PO')

    def test_exact_prefix_only_refuses(self):
        with self.assertRaisesRegex(mod.Refusal,'exact MVS LISTDS'):
            mod.exact_listds(self.core,make_block(OTHER,'PO'),BOOT)

    def test_exact_ignores_command_echo_and_requires_header(self):
        data=f"LISTDS '{BOOT}' LABEL\n{BOOT}\nNOT AN ATTRIBUTES BLOCK\n"
        with self.assertRaisesRegex(mod.Refusal,'exact MVS LISTDS'):
            mod.exact_listds(self.core,data,BOOT)

    def test_exact_repeated_identical_results_accepted(self):
        data=make_block(BOOT,'PS')*2
        self.assertEqual(mod.exact_listds(self.core,data,BOOT)[0]['dsorg'],'PS')

    def test_exact_duplicate_contradiction_refuses(self):
        data=make_block(BOOT,'PS')+make_block(BOOT,'PO')
        with self.assertRaisesRegex(mod.Refusal,'contradictory duplicate'):
            mod.exact_listds(self.core,data,BOOT)

    def test_exact_inventory_all_21_match(self):
        got=mod.exact_inventory(self.core,self.rc3,rows(),full_report())
        self.assertEqual(len(got),21)
        self.assertFalse(any(x['differences'] for x in got))
        self.assertEqual(got[0]['actual']['dsorg'],'PS')

    def test_exact_inventory_detects_actual_boot_wrong_org(self):
        report=full_report().replace(make_block(BOOT,'PS'),make_block(BOOT,'PO'))
        got=mod.exact_inventory(self.core,self.rc3,rows(),report)
        self.assertEqual(got[0]['differences'],['dsorg expected PS observed PO'])
        self.assertEqual(got[1]['differences'],[])

    def test_exact_inventory_rejects_missing_boot(self):
        report=full_report().replace(make_block(BOOT,'PS'),'')
        with self.assertRaisesRegex(mod.Refusal,'exact MVS LISTDS label'):
            mod.exact_inventory(self.core,self.rc3,rows(),report)

    def fixture_diagnostic(self):
        folder=self.work/'diagnostic'; folder.mkdir()
        selected=rows()
        for i,row in enumerate(selected[1:]):
            row['members']=[f'A{i:02d}{j:05d}' for j in range(8 if i<6 else 7)]
        catalog=[]
        for i,r in enumerate(selected):
            catalog.append({'dataset':r['target'],
                'expected':{'volume':'TSO002','dsorg':r['dcb']['dsorg']},
                'actual':{'volume':'TSO002','dsorg':'PO' if i==0 else r['dcb']['dsorg']},
                'mismatches':['dsorg: expected PS, observed PO'] if i==0 else [],
                'raw_listds_block':[OTHER,'--RECFM-'] if i==0 else []})
        members=[{'dataset':r['target'],'match':True,'actual_count':len(r['members'])}
                 for r in selected[1:]]
        record={'status':'DIAGNOSTIC_ONLY_NOT_INSTALL_ACCEPTANCE',
                'candidate':'BCPL-0.1.0-rc3','aws_sha256':'HASH',
                'restore_job':9363,'catalog_job':9365,'directory_job':9366,
                'dcb_discrepancies':1,'member_discrepancies':0,
                'verified_member_count':146,
                'existing_restore_not_repeated':True,
                'regression_executed':False,'publication_authorized':False,
                'live_catalog':catalog,'members':members}
        (folder/'diagnostic.json').write_text(json.dumps(record))
        for fn in ['catalog-summary.txt','catalog-report.txt','members-summary.txt','members-report.txt']:
            (folder/fn).write_text('MVS JOB 9365 BOOT.JCL diagnostic')
        self.seal_folder(folder)
        return folder, selected

    def seal_folder(self,folder):
        (folder/'SHA256SUMS').write_text(''.join(
            hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n'
            for p in sorted(folder.iterdir()) if p.name!='SHA256SUMS'))

    def test_checkpoint_accepts_only_specific_sealed_previous_misbind(self):
        folder,selected=self.fixture_diagnostic()
        diag=Mock()
        diag.sealed_incident.return_value=(9363,'JOB 9364 report')
        cont=Mock(AWS_SHA256='HASH',CANDIDATE='BCPL-0.1.0-rc3')
        cont.digest.return_value='HASH'
        with patch.object(mod,'DIAGNOSTIC',folder):
            self.assertIn('BOOT.JCL',mod.diagnostic_checkpoint(self.rc3,diag,cont,selected))

    def test_checkpoint_refuses_modified_historical_misbind(self):
        folder,selected=self.fixture_diagnostic()
        record=json.loads((folder/'diagnostic.json').read_text())
        record['live_catalog'][0]['raw_listds_block'][0]=BOOT
        (folder/'diagnostic.json').write_text(json.dumps(record))
        self.seal_folder(folder)
        diag=Mock();diag.sealed_incident.return_value=(9363,'JOB 9364')
        cont=Mock(AWS_SHA256='HASH',CANDIDATE='BCPL-0.1.0-rc3')
        cont.digest.return_value='HASH'
        with patch.object(mod,'DIAGNOSTIC',folder):
            with self.assertRaisesRegex(mod.Refusal,'historic BOOT-prefix'):
                mod.diagnostic_checkpoint(self.rc3,diag,cont,selected)

    def test_checkpoint_refuses_corrupted_historical_report(self):
        folder,selected=self.fixture_diagnostic()
        (folder/'catalog-report.txt').write_text('ALTERED')
        diag=Mock();diag.sealed_incident.return_value=(9363,'JOB 9364')
        cont=Mock(AWS_SHA256='HASH',CANDIDATE='BCPL-0.1.0-rc3')
        cont.digest.return_value='HASH'
        with patch.object(mod,'DIAGNOSTIC',folder):
            with self.assertRaisesRegex(mod.Refusal,'checksum differs'):
                mod.diagnostic_checkpoint(self.rc3,diag,cont,selected)

    def test_diagnostic_receipt_refuses_missing_or_tamper(self):
        dsn=self.work/'diag';dsn.mkdir()
        (dsn/'SHA256SUMS').write_text('bad')
        with patch.object(mod,'DIAGNOSTIC',dsn):
            with self.assertRaises(mod.Refusal):
                mod.sealed(dsn,self.rc3,{'diagnostic.json'})

    def test_catalog_replay_wrong_name_cannot_pass_as_ps(self):
        report=make_block(OTHER,'PO')
        with self.assertRaises(mod.Refusal):
            mod.exact_inventory(self.core,self.rc3,rows(),report)

    def test_mvs_catalog_checks_job_ief142i_and_exact_dcb(self):
        self.core.stat_deck.return_value='READ ONLY LISTDS'
        self.core.submit_and_wait.return_value=(9380,'JOB 9380 DSPALST\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n')
        self.core.job_report.return_value='IEF142I DSPALST STAT - STEP WAS EXECUTED - COND CODE 0000\n'+full_report()
        self.rc3.artifact.side_effect=lambda folder,name,data:(folder/name).write_text(data)
        job=mod.catalog(self.core,{},self.rc3,self.work,rows())
        self.assertEqual(job,9380)
        self.core.job_report.return_value='IEF142I DSPALST STAT - STEP WAS EXECUTED - COND CODE 0000\n'+full_report().replace(make_block(BOOT,'PS'),make_block(BOOT,'PO'))
        with self.assertRaisesRegex(mod.Refusal,'restored MVS DCB/volume mismatch'):
            mod.catalog(self.core,{},self.rc3,self.work,rows())

    def test_mvs_catalog_refuses_nonzero_ief142i(self):
        self.core.stat_deck.return_value='READ ONLY LISTDS'
        self.core.submit_and_wait.return_value=(9380,'JOB 9380 DSPALST\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n')
        self.core.job_report.return_value='IEF142I DSPALST STAT - STEP WAS EXECUTED - COND CODE 0004\n'+full_report()
        self.rc3.artifact.side_effect=lambda folder,name,data:(folder/name).write_text(data)
        with self.assertRaisesRegex(mod.Refusal,'verification job not clean'):
            mod.catalog(self.core,{},self.rc3,self.work,rows())

    def test_marker_consumption_prevents_second_run(self):
        self.rc3.check_git.return_value=lambda *args:b'BCPL SOURCE'
        self.rc3.plan.return_value=(rows(),[(f'M{i}','p','BCPL SOURCE') for i in range(12)],None,None,None,'MR10KIT.'*40)
        self.rc3.INSTALL=''
        self.rc3.COMMIT='COMMIT'
        self.rc3.load.return_value=Mock()
        marker=self.work/'marker'
        marker.write_text('already consumed')
        with patch.object(mod,'load',side_effect=[self.rc3,Mock(),Mock()]),\
             patch.object(mod,'diagnostic_checkpoint',return_value='REPORT'),\
             patch.object(mod,'MARKER',marker),\
             patch.object(mod.sys.stdin,'isatty',return_value=True):
            self.assertEqual(mod.run(True),2)
            self.assertEqual(marker.read_text(),'already consumed')
            self.rc3.mvs_job.assert_not_called()

    def test_full_mvs_mock_one_panel_no_tape_or_restore(self):
        self.rc3.check_git.return_value=lambda *args:b'BCPL SOURCE'
        self.rc3.plan.return_value=(rows(),[(f'M{i}','p','BCPL SOURCE') for i in range(12)],None,None,None,'MR10KIT.'*40)
        self.rc3.INSTALL=''
        self.rc3.COMMIT='COMMIT'
        self.rc3.JOBS={'regression':'TA2R3MR'}
        self.rc3.load.side_effect=[Mock(),self.core,Mock(),Mock()]
        self.core.load_config.return_value={'mvs':{'hlq':'HERC02'}}
        self.rc3.artifact.side_effect=lambda folder,name,data:(folder/name).write_text(data)
        self.rc3.exclusive.side_effect=lambda path,data:path.write_bytes(data)
        self.rc3.seal.side_effect=lambda folder:(folder/'SHA256SUMS').write_text('SEALED')
        self.rc3.mvs_job.return_value=(9382,'TEST: ...\nEXP: ...\nRP: ...\nCODE=0\n','JOB 9382 TA2R3MR\n')
        self.rc3.validated_semantics.return_value={'status':'EXP_RP_CODE_COMPARISON_PASS_HUMAN_SIGNOFF_PENDING'}
        self.rc3.VOLUME='TSO002'
        cont=Mock()
        cont.AWS_SHA256='HASH';cont.CANDIDATE='BCPL-0.1.0-rc3';cont.VOL='BC0003'
        cont.digest.return_value='HASH'
        output=self.work/'output';output.mkdir()
        with patch.object(mod,'load',side_effect=[self.rc3,cont,Mock()]),\
             patch.object(mod,'diagnostic_checkpoint',return_value=full_report()),\
             patch.object(mod,'catalog',return_value=9380),\
             patch.object(mod,'OUT',output),\
             patch.object(mod,'MARKER',output/'once.json'),\
             patch.object(mod.sys.stdin,'isatty',return_value=True),\
             patch('builtins.input',return_value='Y'):
            cont.directory_check.return_value=(9381,146)
            # Saved exact row matches the simulated actual BOOT PS dataset.
            self.core.parse_listds.side_effect=parse_listds
            self.core.dataset_missing.return_value=False
            self.assertEqual(mod.run(True),0)
        self.assertTrue((output/'once.json').exists())
        self.rc3.mvs_job.assert_called_once()
        self.rc3.run_command.assert_not_called()
        self.assertEqual(self.rc3.mvs_job.call_args.args[3],'regression')
        self.assertEqual(self.rc3.mvs_job.call_args.args[4],'TA2R3MR')

    def test_stateful_refusal_before_marker_on_incorrect_mvs_dcb(self):
        self.rc3.check_git.return_value=lambda *args:b'BCPL SOURCE'
        self.rc3.plan.return_value=(rows(),[(f'M{i}','p','BCPL SOURCE') for i in range(12)],
                                    None,None,None,'MR10KIT.'*40)
        self.rc3.INSTALL=''; self.rc3.COMMIT='COMMIT'
        self.rc3.load.side_effect=[Mock(),self.core,Mock(),Mock()]
        self.core.load_config.return_value={'mvs':{'hlq':'HERC02'}}
        self.rc3.artifact.side_effect=lambda folder,name,data:(folder/name).write_text(data)
        self.rc3.seal.side_effect=lambda folder:(folder/'SHA256SUMS').write_text('SEALED')
        cont=Mock()
        cont.AWS_SHA256='HASH';cont.digest.return_value='HASH'
        output=self.work/'output';output.mkdir()
        with patch.object(mod,'load',side_effect=[self.rc3,cont,Mock()]),\
             patch.object(mod,'diagnostic_checkpoint',return_value=full_report()),\
             patch.object(mod,'catalog',side_effect=mod.Refusal('BOOT is genuinely PO')),\
             patch.object(mod,'OUT',output),\
             patch.object(mod,'MARKER',output/'one-shot'),\
             patch.object(mod.sys.stdin,'isatty',return_value=True):
            self.assertEqual(mod.run(True),2)
        self.assertFalse((output/'one-shot').exists())
        self.rc3.mvs_job.assert_not_called()

if __name__=='__main__':unittest.main()
