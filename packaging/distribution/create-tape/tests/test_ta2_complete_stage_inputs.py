"""Synthetic tests of the accepted 20-input projection; no MVS utility calls."""
from __future__ import annotations

import copy
import hashlib
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
loader = SourceFileLoader('ta2_complete_inputs_test', str(ROOT / 'packaging/distribution/create-tape/scripts/ta2-complete-stage-inputs'))
spec = spec_from_loader(loader.name, loader)
mod = module_from_spec(spec)
loader.exec_module(mod)


def fixtures():
    from pathlib import Path
    d = {'schema_version': 1, 'phase': 'design', 'datasets': []}
    for n in range(1, 21):
        row = {'sequence': n, 'group': 'common', 'owner': 'distribution',
               'kind': 'sequential_text' if n == 1 else 'pds_unload',
               'transfer': 'sequential_standard_label' if n == 1 else 'iebcopy_unload',
               'target_dcb': {'dsorg': 'PS' if n == 1 else 'PO', 'recfm':'U' if n==12 else 'FB',
                              'lrecl': 0 if n==12 else 80, 'blksize': 6144 if n==12 else 800}}
        if n <= 2:
            row['generator'] = 'bootstrap_fb80' if n == 1 else 'installer_pds'
        else:
            row.update({'dspal_key': 'MR10_LOAD' if n == 12 else f'LIB{n:04d}',
                        'target_dsn_template': f'{{HLQ}}.BCPL.LIB{n:04d}',
                        'members': ['ICINT19'] if n == 12 else [f'M{j:07d}' for j in range(7)]})
        d['datasets'].append(row)
    # 17 other PDSes * 7 + load 1 = 120; make 127 with 7 further distinct names.
    d['datasets'][2]['members'] += [f'N{j:07d}' for j in range(7)]
    c = copy.deepcopy(d)
    c.update({'phase':'candidate','release':{'candidate_id':'BCPL-0.1.0-rc1',
        'version':'0.1.0-rc1','source_commit':'146ae09a58398c9b4d685500760f85592e770e1e',
        'native_compiler':'absent'},
        'volume':{'volser':'BC0001','registry_reservation':'BCPL-0.1.0-rc1'}})
    earlier = {'status':'ACCEPTED_STAGED_PDS; BT0001/BT0002_PENDING',
               'accepted_verification_sha256':'b'*64,
               'staging':{'members':127,'directory_dcb_jobs':{'catalog':9311,'members':9312}},
               'inputs': []}
    for n,r in enumerate(d['datasets'],1):
        earlier['inputs'].append({'sequence':n,'tape_alias':f'BCPL.BT{n:04d}',
          'status':'NOT_PREPARED' if n <= 2 else 'ACCEPTED_STAGING',
          'producer_source_dsn':None if n <= 2 else mod.DSNS[n-1],
          **({} if n <= 2 else {'selected_members':r['members'], 'source_volume':'TSO002', 'source_dcb':r['target_dcb']})})
    bt={'status':'MVS_BT0001_BT0002_DCB_DIRECTORY_PASS','stage_job':9317,
        'stage_evidence':mod.ORIGINAL_BT_STAGE,'volume':'TSO002', 'datasets':2,
        'installer_members':mod.MEMBERS,'mvs_jobs':{'catalog':9318,'members':9319},
        'stage_result_sha256':'a'*64}
    registry={'schema_version':1,'candidates':[{'state':'reserved','candidate_id':'BCPL-0.1.0-rc1',
              'version':'0.1.0-rc1', 'source_commit':'146ae09a58398c9b4d685500760f85592e770e1e',
              'volser':'BC0001','manifest_sha256':'c'*64}]}
    return earlier,bt,c,d,registry


class CompleteInputsTests(unittest.TestCase):
    def setUp(self):
        self.earlier,self.bt,self.candidate,self.design,self.registry = fixtures()
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/'workarea')
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.target=self.root/'receipt'
        self.target.mkdir()
        self.repoint = patch.object(mod,'BT_RECEIPT',self.target)
        self.repoint.start();self.addCleanup(self.repoint.stop)
        self.repoint_root=patch.object(mod,'ROOT',self.root)
        self.repoint_root.start();self.addCleanup(self.repoint_root.stop)
        self.bt_stage_dir = self.root/'workarea/ta2-bootstrap-stage-verification'
        self.bt_stage_dir.mkdir(parents=True)
        self.target2 = self.bt_stage_dir/'20261120T132703Z-22108'
        self.target2.mkdir()
        # Override folder to expected pinned path.
        self.repoint.stop()
        self.repoint=patch.object(mod,'BT_RECEIPT',self.target2)
        self.repoint.start()
        self.prepare()

    def prepare(self):
        (self.target2/'verification.json').write_text(json.dumps(self.bt))
        for name in ('catalog-report.txt','members-report.txt','catalog-summary.txt',
                     'members-summary.txt','catalog-cursor.json','members-cursor.json'):
            (self.target2/name).write_text('original JES data\n')
        self.resign()

    def resign(self):
        ledger=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n'
                       for p in sorted(self.target2.iterdir()) if p.name!='SHA256SUMS')
        (self.target2/'SHA256SUMS').write_text(ledger)

    def build(self):
        return mod.build(self.earlier,self.bt,'d'*64,self.candidate,self.design,self.registry,'c'*64)

    def test_all_20_stage_inputs_accepted(self):
        x=self.build()
        self.assertEqual((x['datasets'],x['pds'],x['sequential'],x['selected_payload_members']),(20,19,1,127))
        self.assertEqual([x['producer_source_dsn'] for x in x['inputs']],mod.DSNS)
        self.assertTrue(all(r['status']=='ACCEPTED_STAGING' for r in x['inputs']))
        self.assertEqual(x['inputs'][1]['selected_members'], mod.MEMBERS)
        self.assertEqual(x['inputs'][11]['source_dcb']['recfm'],'U')
        self.assertEqual(x['mvs_jobs']['bootstrap_members'],9319)
        self.assertIn('rights/lineage', x['blockers'][0])

    def test_schema_mutation_refused(self):
        self.candidate['datasets'][6]['members']=['WRONG']
        with self.assertRaisesRegex(mod.Refusal,'BT0007'): self.build()

    def test_cannot_substitute_volser(self):
        self.candidate['volume']['volser']='BC0002'
        with self.assertRaisesRegex(mod.Refusal,'identity'): self.build()

    def test_registry_candidate_sha_mismatch_refused(self):
        self.registry['candidates'][0]['manifest_sha256']='f'*64
        with self.assertRaisesRegex(mod.Refusal,'registry'): self.build()

    def test_acceptance_job_mismatch_refused(self):
        self.earlier['staging']['directory_dcb_jobs']['members']=9300
        with self.assertRaisesRegex(mod.Refusal,'18-PDS'): self.build()

    def test_missing_bt_acceptance_refused(self):
        self.bt['mvs_jobs']['members']=9999
        with self.assertRaisesRegex(mod.Refusal,'BT0001'): self.build()

    def test_missing_original_bt_receipt_refused(self):
        (self.target2/'verification.json').unlink()
        with self.assertRaisesRegex(mod.Refusal,'incomplete'): mod.read_receipt(self.target2)

    def test_tampered_bt_report_refused(self):
        (self.target2/'members-report.txt').write_text('TAMPERED')
        with self.assertRaisesRegex(mod.Refusal,'checksum'): mod.read_receipt(self.target2)

    def test_wrong_bt_job_in_receipt_refused(self):
        self.bt['mvs_jobs']['catalog']=9999
        (self.target2/'verification.json').write_text(json.dumps(self.bt))
        self.resign()
        with self.assertRaisesRegex(mod.Refusal,'receipt identity'): mod.read_receipt(self.target2)

    def test_new_private_snapshot_no_overwrite(self):
        plan=self.build(); dst=self.root/'workarea'/'accepted-map.json'
        mod.write_new(dst,plan)
        self.assertEqual(json.loads(dst.read_text())['status'],'ALL_20_STAGE_INPUTS_ACCEPTED')
        with self.assertRaises(FileExistsError): mod.write_new(dst,plan)


if __name__ == '__main__': unittest.main()
