"""TA.2 successor source-only layout contract: synthetic, offline tests."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[4]
CODE=ROOT/'packaging/distribution/compiler-source/successor-contract.py'
spec=importlib.util.spec_from_file_location('source_successor_contract',CODE)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SELECTION=json.loads((CODE.parent/'source-selection.json').read_text())
DCB={'dsorg':'PO','recfm':'FB','lrecl':80,'blksize':800}

class TestSuccessor(unittest.TestCase):
    def setUp(self):
        self.rc1={
            'schema_version':1,'phase':'candidate',
            'release':{'candidate_id':'BCPL-0.1.0-rc1','version':'0.1.0-rc1',
                       'source_commit':'1'*40,'native_compiler':'absent'},
            'volume':{'volser':'BC0001'},
            'datasets':[{'sequence':i,'generator':('bootstrap_fb80' if i==1 else 'installer_pds')
                         if i<3 else None,'dspal_key':f'EXIST{i:02d}'}
                        for i in range(1,21)]}
        self.rc2=copy.deepcopy(self.rc1)
        self.rc2['release'].update(candidate_id='BCPL-0.1.0-rc2',
             version='0.1.0-rc2',source_commit='2'*40,cambridge_source='included')
        self.rc2['volume']={'volser':'BC0002','registry_reservation':'BCPL-0.1.0-rc2'}
        self.rc2['profiles']={'mr10-only':['common','mr10'],
             'native-only':['common','native','cambridge-source'],
             'combined':['common','mr10','native','cambridge-source']}
        self.dspal={'datasets':{}}
        groups={g['role']:g['members'] for g in SELECTION['source_sets']}
        for seq,key,mapping,generated,family in [
            (21,'CAMB_SOURCE',groups['historical'],{},'historical')]:
            dsn='BCPL.CAMBRIDG.'+('SOURCE' if seq==21 else 'DEMOTED')
            self.dspal['datasets'][key]=dict(dsn=dsn,populate=True,type='pds',**DCB,
                                            members=copy.deepcopy(mapping),generated_members=copy.deepcopy(generated))
            row=dict(sequence=seq,group='cambridge-source',owner='cambridge-compiler-source',
                     kind='pds_unload',transfer='iebcopy_unload',dspal_key=key,
                     target_dsn_template='{HLQ}.'+dsn,target_dcb=copy.deepcopy(DCB),
                     members=list(mapping)+list(generated),source_family=family,
                     rights_status='preservation-policy-approved-rights-unresolved')
            self.rc2['datasets'].append(row)
        self.selection=copy.deepcopy(SELECTION)
        self.raw=b'release candidate synthetic raw YAML\n'
        self.registry={'candidates':[
            dict(candidate_id='BCPL-0.1.0-rc1',volser='BC0001',state='reserved',
                 source_commit='1'*40,manifest_sha256='abc'),
            dict(candidate_id='BCPL-0.1.0-rc2',version='0.1.0-rc2',
                 volser='BC0002',state='reserved',source_commit='2'*40,
                 manifest_sha256=hashlib.sha256(self.raw).hexdigest())]}
    def check(self):
        return mod.verify(self.rc1,self.rc2,self.dspal,self.registry,self.selection,self.raw)
    def test_valid(self):
        v=self.check()
        self.assertEqual((v['tape_datasets'],v['new_source_members'],v['native_compiler']),
                         (21,15,'absent'))
        self.assertFalse(v['mvs_stage_verified'])
    def test_version_drift(self):
        self.rc2['release']['version']='0.1.0-rc1'
        self.assertRaises(mod.ContractError,self.check)
    def test_volser_drift(self):
        self.rc2['volume']['volser']='BC0001'
        self.assertRaises(mod.ContractError,self.check)
    def test_native_claim_refused(self):
        self.rc2['release']['native_compiler']='included'
        self.assertRaises(mod.ContractError,self.check)
    def test_missing_source_claim_refused(self):
        self.rc2['release'].pop('cambridge_source')
        self.assertRaises(mod.ContractError,self.check)
    def test_first_twenty_immutable(self):
        self.rc2['datasets'][4]['members']=['ADDED']
        self.assertRaises(mod.ContractError,self.check)
    def test_bootstrap_role_refused(self):
        self.rc2['datasets'][0]['generator']='wrong'
        self.assertRaises(mod.ContractError,self.check)
    def test_missing_source_pds(self):
        self.rc2['datasets'].pop()
        self.assertRaises(mod.ContractError,self.check)
    def test_wrong_group(self):
        self.rc2['datasets'][-1]['group']='cambridge'
        self.assertRaises(mod.ContractError,self.check)
    def test_wrong_profile(self):
        self.rc2['profiles']['mr10-only'].append('cambridge-source')
        self.assertRaises(mod.ContractError,self.check)
    def test_mutated_historical_member(self):
        self.dspal['datasets']['CAMB_SOURCE']['members']['BCPL']='unapproved'
        self.assertRaises(mod.ContractError,self.check)
    def test_demoted_pds_forbidden_even_if_unselected(self):
        self.dspal['datasets']['CAMB_DEMOTED'] = {'populate': False}
        self.assertRaises(mod.ContractError,self.check)
    def test_demoted_tape_append_forbidden(self):
        extra = copy.deepcopy(self.rc2['datasets'][-1])
        extra.update(sequence=22, dspal_key='CAMB_DEMOTED')
        self.rc2['datasets'].append(extra)
        self.assertRaises(mod.ContractError,self.check)
    def test_historical_source_must_not_be_generated(self):
        self.dspal['datasets']['CAMB_SOURCE']['generated_members']={'CG': 'workarea/cg'}
        self.assertRaises(mod.ContractError,self.check)
    def test_development_family_is_not_a_tape_selection(self):
        self.selection['source_sets'][1]['members']['MORE'] = 'workarea/only'
        self.assertEqual(self.check()['new_source_members'], 15)
    def test_unverified_rights_guard(self):
        self.rc2['datasets'][-1]['rights_status']='approved'
        self.assertRaises(mod.ContractError,self.check)
    def test_wrong_record_format(self):
        self.rc2['datasets'][-1]['target_dcb']['recfm']='VB'
        self.assertRaises(mod.ContractError,self.check)
    def test_registry_digest_mismatch(self):
        self.registry['candidates'][1]['manifest_sha256']='0'*64
        self.assertRaises(mod.ContractError,self.check)
    def test_registry_double_volser(self):
        self.registry['candidates'][1]['volser']='BC0001'
        self.assertRaises(mod.ContractError,self.check)
    def test_old_reservation_disturbed(self):
        self.registry['candidates'][0]['state']='retired'
        self.assertRaises(mod.ContractError,self.check)
    def test_frozen_source_not_rc1(self):
        self.rc2['release']['source_commit']='1'*40
        self.assertRaises(mod.ContractError,self.check)
    def test_extra_member_rejected(self):
        self.rc2['datasets'][20]['members'].append('EXTRA')
        self.assertRaises(mod.ContractError,self.check)
if __name__=='__main__':unittest.main()
