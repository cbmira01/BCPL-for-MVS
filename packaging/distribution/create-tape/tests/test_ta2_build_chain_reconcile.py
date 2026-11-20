"""Synthetic join tests: no MVS, Git writes or binary certification."""
from __future__ import annotations
import copy
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[4]
SRC = REPO / 'packaging/distribution/create-tape/scripts/ta2-build-chain-reconcile'
loader = SourceFileLoader('ta2_binary_join_test', str(SRC))
spec = spec_from_loader(loader.name, loader)
mod = module_from_spec(spec)
loader.exec_module(mod)
CORE = ['BCPLMAIN','BCPLMEM','BCPLBYTE','BCPLAPT','BCPLIO','BCPLRGS','BCPLREG']
EXT = ['BCPLDEMO','BCPLTIME','BCPLQSAM']


def fixture():
    datasets = {n: {'sequence': n, 'dspal_key':f'EMPTY{n:04d}',
                    'tape_alias':f'BCPL.BT{n:04d}', 'status':'ACCEPTED_STAGING',
                    'selected_members':[]} for n in range(3,21)}
    selected = {'MR10_SOURCE':[f'M{i:07d}' for i in range(97)],
        'MR10_ASM':['ICINT19'],
        'BOOT_ASM':[ *CORE,'BCPLCO','COROUTIN'],
        'BOOT_SOURCE':['BLIB','COROUTIN'], 'EXT_ASM':EXT,
        'MR10_OBJ':['ICINT19'], 'MR10_LOAD':['ICINT19'],
        'BOOT_OBJ':[*CORE,'BLIB','BCPLCO','COROUTIN'], 'EXT_OBJ':EXT}
    positions = {k:i for i,k in enumerate(selected,start=3)}
    for key,n in positions.items():
        datasets[n]['dspal_key']=key
        datasets[n]['selected_members']=selected[key]
    assert sum(len(v['selected_members']) for v in datasets.values()) == 127
    stage = {'status':'ALL_20_STAGE_INPUTS_ACCEPTED','datasets':20, 'pds':19,
         'selected_payload_members':127,'candidate_id':'BCPL-0.1.0-rc1',
         'source_commit':'146ae09a58398c9b4d685500760f85592e770e1e',
         'volser_reserved':'BC0001','candidate_manifest_sha256':'a'*64,
         'mvs_jobs':{'bootstrap_stage':9317},'inputs':[
          {'status':'ACCEPTED_STAGING'}, {'status':'ACCEPTED_STAGING'},
           *datasets.values()]}
    classes = {'MR10_OBJ','MR10_LOAD','BOOT_OBJ','EXT_OBJ'}
    generated = {'BOOT_SOURCE(BLIB)','BOOT_ASM(COROUTIN)'}
    sources=[]
    for row in datasets.values():
        key=row['dspal_key']
        for member in row['selected_members']:
            ref=f'{key}({member})'
            cls = 'resident_binary' if key in classes else 'generated' if ref in generated else 'git_source'
            sources.append({'dataset_key':key,'member':member,
                'tape_sequence':row['sequence'], 'source_class':cls,
                'redistribution_review':'UNREVIEWED','rights_ref':None,
                'build_receipt':None,
                'frozen_git_source_ref':'git:sha:source@blob' if cls=='git_source' else None})
    lineage={'status':'TA2_FROZEN_SOURCE_LINEAGE_VERIFIED_RIGHTS_PENDING',
       'candidate_id':stage['candidate_id'],'source_git_sha':stage['source_commit'],
       'reserved_volser':'BC0001','candidate_manifest_sha256':'a'*64,
       'source_summary':{'git_source':110,'generated':2,'resident_binary':15,
         'redistribution_unreviewed':127,'generated_or_binary_build_receipts_pending':17,
         'git_blob_refs_verified':110},'sources':sources}
    builders={
        'MR10_OBJ':'IC19BLD','MR10_LOAD':'IC19BLD',
        'EXT_OBJ':'derived', 'BOOT_OBJ':'derived'}
    rows=[]
    for key in ('MR10_OBJ','MR10_LOAD','BOOT_OBJ','EXT_OBJ'):
        for name in selected[key]:
            target=f'{key}({name})'
            if key.startswith('MR10'):
                job='MR10_JCL(IC19BLD)';refs=['MR10_ASM(ICINT19)']
            elif key=='EXT_OBJ':
                job=f'BOOT_JCL({name})';refs=[f'EXT_ASM({name})']
            elif name=='BLIB':
                job='BOOT_JCL(BLIBBLD)';refs=['BOOT_SOURCE(BLIB)']
            elif name=='COROUTIN':
                job='BOOT_JCL(BLDCORLB)';refs=['BOOT_SOURCE(COROUTIN)','BOOT_ASM(COROUTIN)']
            elif name=='BCPLCO':
                job='BOOT_JCL(BLDCORCO)';refs=['BOOT_ASM(BCPLCO)']
            else:
                job='BOOT_JCL(BLDBMAIN)';refs=[f'BOOT_ASM({name})']
            rows.append({'target':target,'selected_source_members':refs,
               'build_job':job,'build_jcl_path':f'{job.split("(")[0]}/{job.split("(")[1][:-1]}.jcl',
               'build_jcl_on_tape':job!='BOOT_JCL(BLIBBLD)',
               'reconstruction_step_contract':['ASSEMBLE','PUT'],
               'requires_generated_assembler':target=='BOOT_OBJ(COROUTIN)',
               'requires_absent_compiler_for_bcpl_source_rebuild':target in {'BOOT_OBJ(BLIB)','BOOT_OBJ(COROUTIN)'},
               'mvs_build_receipt':None,'mvs_input_inventory_receipt':None,
               'mvs_binary_readback_receipt':None,
               'candidate_source_sha_verified':False,'redistribution_approved':False})
    binary={'status':'TA.0 RECONSTRUCTION BUILD PLAN ONLY; NO CANDIDATE OR BINARY ACCEPTANCE',
            'summary':{'binary_members':15,'mvs_receipts_verified':0,'rights_approvals':0},
            'members':rows}
    assert len(sources)==127 and sum(x['source_class']=='git_source' for x in sources)==110
    assert len(rows)==15
    return stage,lineage,binary


class EvidenceBridgeTests(unittest.TestCase):
    def setUp(self):
        self.stage,self.source,self.binary=fixture()
        self.tmp=tempfile.TemporaryDirectory(dir=REPO/'workarea')
        self.addCleanup(self.tmp.cleanup)
        self.work=Path(self.tmp.name)
        p=patch.object(mod,'WORKAREA',self.work)
        p.start();self.addCleanup(p.stop)

    def make(self):return mod.join(self.stage,self.source,self.binary)

    def test_combines_exact_existing_evidence(self):
        output=self.make()
        self.assertEqual(output['summary'],{
            'mvs_staged_datasets':20,'payload_members':127,'git_sources_frozen':110,
            'generated_sources_pending':2,'binary_targets_pending':15,
            'build_job_contracts_traced':8,'unshipped_build_jobs':1,
            'redistribution_reviews_pending':127,
            'candidate_specific_build_receipts_accepted':0})
        self.assertEqual(len(output['build_jobs']),8)
        self.assertEqual(len(output['binary_targets']),15)
        self.assertEqual(len(output['generated_sources']),2)

    def test_unshipped_blib_builder_explicit(self):
        result=self.make()
        row=next(x for x in result['build_jobs'] if x['builder']=='BOOT_JCL(BLIBBLD)')
        self.assertFalse(row['selected_on_tape'])
        row=next(x for x in result['binary_targets'] if x['target']=='BOOT_OBJ(BLIB)')
        self.assertTrue(row['recipient_bcpl_source_rebuild_unavailable'])

    def test_coroutine_generated_chain_kept_separate(self):
        result=self.make()
        generated={x['source']:x['consumed_by'] for x in result['generated_sources']}
        self.assertEqual(generated['BOOT_ASM(COROUTIN)'],['BOOT_OBJ(COROUTIN)'])
        self.assertEqual(generated['BOOT_SOURCE(BLIB)'],['BOOT_OBJ(BLIB)'])
        row=next(x for x in result['binary_targets'] if x['target']=='BOOT_OBJ(COROUTIN)')
        self.assertTrue(row['requires_generated_assembler'])
        self.assertIn('BOOT_SOURCE(COROUTIN)',row['selected_sources'])

    def test_mvs_stage_must_be_accepted(self):
        self.stage['inputs'][0]['status']='PENDING'
        with self.assertRaisesRegex(mod.Refusal,'20-input'):self.make()

    def test_candidate_sha_binding_cannot_change(self):
        self.stage['candidate_manifest_sha256']='b'*64
        with self.assertRaisesRegex(mod.Refusal,'candidate differs'):self.make()

    def test_frozen_git_source_count_must_match(self):
        self.source['source_summary']['git_blob_refs_verified']=109
        with self.assertRaisesRegex(mod.Refusal,'counts'):self.make()

    def test_rights_never_implicitly_approved(self):
        self.source['sources'][0]['redistribution_review']='approved'
        with self.assertRaisesRegex(mod.Refusal,'rights differ'):self.make()

    def test_generated_binary_cannot_pose_as_git_blob(self):
        row=next(x for x in self.source['sources'] if x['source_class']=='generated')
        row['frozen_git_source_ref']='git:fake'
        with self.assertRaisesRegex(mod.Refusal,'incorrectly represented'):self.make()

    def test_wrong_generated_class_refused(self):
        row=next(x for x in self.source['sources'] if x['source_class']=='generated')
        row['source_class']='git_source';row['frozen_git_source_ref']='git:sha:fake@blob'
        with self.assertRaisesRegex(mod.Refusal,'generated/binary member'):self.make()

    def test_missing_binary_build_target_refused(self):
        self.binary['members'].pop()
        with self.assertRaisesRegex(mod.Refusal,'15 binary'):self.make()

    def test_unselected_build_source_refused(self):
        self.binary['members'][0]['selected_source_members']=['MR10_ASM(WRONG)']
        with self.assertRaisesRegex(mod.Refusal,'invalid selected'):self.make()

    def test_compiler_dependency_cannot_be_hidden(self):
        row=next(x for x in self.binary['members'] if x['target']=='BOOT_OBJ(COROUTIN)')
        row['requires_absent_compiler_for_bcpl_source_rebuild']=False
        with self.assertRaisesRegex(mod.Refusal,'acceptance not supported'):self.make()

    def test_unshipped_jcl_cannot_be_claimed_on_tape(self):
        row=next(x for x in self.binary['members'] if x['target']=='BOOT_OBJ(BLIB)')
        row['build_jcl_on_tape']=True
        with self.assertRaisesRegex(mod.Refusal,'acceptance not supported'):self.make()

    def test_binary_mvs_receipt_requires_real_input(self):
        self.binary['members'][0]['mvs_build_receipt']='unverified'
        with self.assertRaisesRegex(mod.Refusal,'acceptance not supported'):self.make()

    def test_missing_builder_contract_refused(self):
        self.binary['members'][0]['reconstruction_step_contract']=[]
        with self.assertRaisesRegex(mod.Refusal,'verified IFOX'):self.make()

    def test_duplicate_binary_refused(self):
        self.binary['members'][1]['target']=self.binary['members'][0]['target']
        with self.assertRaisesRegex(mod.Refusal,'duplicated'):self.make()

    def test_exclusive_private_output(self):
        out=self.work/'new-review.json';mod.write_new(out,self.make())
        self.assertEqual(json.loads(out.read_text())['summary']['build_job_contracts_traced'],8)
        with self.assertRaises(FileExistsError):mod.write_new(out,self.make())

    def test_output_cannot_escape_workarea(self):
        child=self.work/'subdir';child.mkdir()
        with self.assertRaisesRegex(mod.Refusal,'workarea'):
            mod.write_new(child/'test.json',self.make())

    def test_no_jes_or_tape_submission(self):
        text=SRC.read_text()
        self.assertNotIn('submit_and_wait',text)
        self.assertNotIn('tape.write(',text)
        self.assertNotIn('git push',text)


if __name__=='__main__':unittest.main()
