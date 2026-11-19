"""TA.2 offline staging JCL: selected member closure, isolation, fail-closed tests."""
import copy
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/ta2-stage-jcl'
loader = importlib.machinery.SourceFileLoader('ta2_stage_jcl_tests', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)


class StageJCLTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.directory = self.root / 'workarea/ta2-stage-plan/20261119T155947Z-17087'
        self.directory.mkdir(parents=True)
        self.dspal = {'mvs': {'hlq': 'HERC02'}, 'datasets': {}}
        self.manifest = {'phase':'design','datasets':[{'sequence':1}, {'sequence':2}]}
        self.sources = []
        self.rows = []
        for n in range(3,21):
            key = 'SOURCE' + str(n)
            dsn = 'HERC02.BCPL.S' + str(n).zfill(3)
            self.dspal['datasets'][key] = {'dsn':dsn.removeprefix('HERC02.')}
            count = 8 if n == 20 else 7
            members = [f'M{j:07d}' for j in range(count)]
            dcb = {'dsorg': 'PO', 'recfm': 'U' if n == 12 else 'FB',
                   'lrecl':0 if n == 12 else 80,
                   'blksize':6144 if n == 12 else 800}
            self.manifest['datasets'].append({'sequence':n,'dspal_key':key,
                                               'target_dcb':dcb,'members':members})
            self.sources.append({'tape_sequence':n,'source_key':key,
                                 'source_dsn':dsn,'source_dcb':dcb,
                                 'selected_members':members,'selected_count':count,
                                 'source_volume':'TSO003','source_tracks_allocated':20,
                                 'source_tracks_through_hwm':16,
                                 'source_directory_allocated':8,'source_directory_used':5,
                                 'staging_dsn':None,'stage_space':None,
                                 'allocation_approved':False})
        self.plan = {'status':'READ-ONLY PLAN; STAGING NOT AUTHORIZED',
                     'source_pds':18,'selected_members':127,
                     'excluded_development_members':76,'sources':self.sources}
        self._save()
        self.worksheet_sha = hashlib.sha256((self.directory/'stage-worksheet.json').read_bytes()).hexdigest()
        self.allocation = {
            'schema_version':1, 'stage_worksheet_sha256':self.worksheet_sha,
            'staging_namespace':'HERC02.BCPL.TA2STG',
            'targets':[{'sequence':n,'dsn':f'HERC02.BCPL.TA2STG.BT{n:04d}',
                        'volume':'TSO002','space':{
                            'primary_tracks':50,'secondary_tracks':20,
                            'directory_blocks':16}} for n in range(3,21)]}
        self.rows = mod.validate_worksheet(self.plan,self.manifest,self.dspal)

    def _save(self):
        (self.directory/'stage-worksheet.json').write_text(json.dumps(self.plan,indent=2)+'\n')
        (self.directory/'dspal-stat-all.txt').write_text('RC=0\nDataset: something\n')
        (self.directory/'SHA256SUMS').write_text(''.join(
            hashlib.sha256((self.directory/name).read_bytes()).hexdigest() +
            '  '+name+'\n' for name in ('stage-worksheet.json','dspal-stat-all.txt')))

    def _rehash(self):
        (self.directory/'SHA256SUMS').write_text(''.join(
            hashlib.sha256((self.directory/name).read_bytes()).hexdigest() +
            '  '+name+'\n' for name in ('stage-worksheet.json','dspal-stat-all.txt')))

    def checked(self):
        return mod.validate_allocations(self.allocation,self.worksheet_sha,self.rows,self.dspal)

    def deck(self):
        return mod.render_jcl(self.checked())

    def test_draft_18_127(self):
        deck=self.deck()
        self.assertEqual(deck.count(' EXEC PGM=IEBCOPY'),18)
        self.assertEqual(deck.count(' SELECT MEMBER='),127)
        self.assertNotIn('HERCULES',deck)
        self.assertNotIn('BTA101',deck)
        self.assertNotIn('BTA102',deck)
        self.assertNotIn('JOB (',deck)
        self.assertIn('NOT APPROVED FOR MVS SUBMISSION',deck)
        self.assertIn('//S0012 EXEC PGM=IEBCOPY',deck)
        self.assertIn('DCB=(DSORG=PO,RECFM=U,BLKSIZE=6144)',deck)
        self.assertEqual(deck.count('DISP=(NEW,CATLG,DELETE)'),18)
        self.assertEqual(deck.count('DISP=SHR'),18)
        self.assertEqual(deck.count('COND=(0,NE)'),17)

    def test_fixed_card_widths(self):
        for line in self.deck().splitlines():
            self.assertLessEqual(len(line),80)
            if line.startswith('//') and not line.startswith('//*'):
                self.assertLessEqual(len(line),71)

    def test_no_other_development_members_selected(self):
        self.assertNotIn('DEVELOP1',self.deck())
        self.assertEqual([x for x in self.deck().splitlines() if
                          x.startswith(' SELECT MEMBER=')].count(' SELECT MEMBER=(M0000000)'),18)

    def test_space_exact_and_not_split_mid_expression(self):
        self.assertIn('//            SPACE=(TRK,(50,20,16)),',self.deck())

    def test_jobless_draft_and_stage_metadata(self):
        self.assertTrue(self.deck().endswith('/*\n//\n'))
        self.assertIn('DSN=HERC02.BCPL.TA2STG.BT0012',self.deck())

    def test_read_existing_stage_pass(self):
        plan,digest,raw=mod.read_stage_run(self.root,self.directory)
        self.assertEqual(plan,self.plan)
        self.assertEqual(digest,self.worksheet_sha)
        self.assertTrue(raw.startswith(b'RC=0\n'))

    def test_changed_stage_worksheet_checksum_refused(self):
        (self.directory/'stage-worksheet.json').write_text('{}')
        with self.assertRaisesRegex(mod.Refusal,'checksum mismatch'):
            mod.read_stage_run(self.root,self.directory)

    def test_changed_mvs_report_checksum_refused(self):
        (self.directory/'dspal-stat-all.txt').write_text('RC=0\nchanged')
        with self.assertRaisesRegex(mod.Refusal,'checksum mismatch'):
            mod.read_stage_run(self.root,self.directory)

    def test_failed_inquiry_rehashed_refused(self):
        (self.directory/'dspal-stat-all.txt').write_text('RC=2\n')
        self._rehash()
        with self.assertRaisesRegex(mod.Refusal,'not successful'):
            mod.read_stage_run(self.root,self.directory)

    def test_missing_evidence_refused(self):
        (self.directory/'SHA256SUMS').unlink()
        with self.assertRaisesRegex(mod.Refusal,'incomplete'):
            mod.read_stage_run(self.root,self.directory)

    def test_extra_evidence_refused(self):
        (self.directory/'unknown.txt').write_text('x')
        with self.assertRaisesRegex(mod.Refusal,'extra'):
            mod.read_stage_run(self.root,self.directory)

    def test_linked_report_refused(self):
        (self.directory/'dspal-stat-all.txt').unlink()
        (self.directory/'dspal-stat-all.txt').symlink_to(self.directory/'stage-worksheet.json')
        with self.assertRaisesRegex(mod.Refusal,'linked'):
            mod.read_stage_run(self.root,self.directory)

    def test_evidence_outside_root_refused(self):
        with self.assertRaises(mod.Refusal):
            mod.read_stage_run(self.root,self.root)

    def test_evidence_run_symlink_refused(self):
        link=self.directory.with_name('20261119T155948Z-17088')
        link.symlink_to(self.directory,target_is_directory=True)
        with self.assertRaises(mod.Refusal):
            mod.read_stage_run(self.root,link)

    def test_forged_member_selection_refused(self):
        self.plan['sources'][0]['selected_members'].append('DEVELOP1')
        with self.assertRaisesRegex(mod.Refusal,'canonical manifest'):
            mod.validate_worksheet(self.plan,self.manifest,self.dspal)

    def test_unapproved_staging_dsn_refused(self):
        self.sources[0]['staging_dsn']='HERC02.BCPL.TA2STG.BT0003'
        with self.assertRaises(mod.Refusal):
            mod.validate_worksheet(self.plan,self.manifest,self.dspal)

    def test_bad_member_count_refused(self):
        self.plan['selected_members']=128
        with self.assertRaises(mod.Refusal):
            mod.validate_worksheet(self.plan,self.manifest,self.dspal)

    def test_missing_extras_disclosure_refused(self):
        self.plan['excluded_development_members']=-1
        with self.assertRaises(mod.Refusal):
            mod.validate_worksheet(self.plan,self.manifest,self.dspal)

    def test_source_dsn_drift_refused(self):
        self.sources[0]['source_dsn']='HERC02.BCPL.FOREIGN'
        with self.assertRaises(mod.Refusal):
            mod.validate_worksheet(self.plan,self.manifest,self.dspal)

    def test_object_library_dcb_drift_refused(self):
        self.sources[9]['source_dcb']={**self.sources[9]['source_dcb'],'recfm':'FB'}
        with self.assertRaises(mod.Refusal):
            mod.validate_worksheet(self.plan,self.manifest,self.dspal)

    def test_wrong_volume_refused(self):
        self.sources[0]['source_volume']='TOOLONGX'
        with self.assertRaises(mod.Refusal):
            mod.validate_worksheet(self.plan,self.manifest,self.dspal)

    def test_wrong_stage_plan_digest_refused(self):
        self.allocation['stage_worksheet_sha256']='a'*64
        with self.assertRaisesRegex(mod.Refusal,'bound'):
            self.checked()

    def test_stage_dsn_replaces_development_refused(self):
        self.allocation['targets'][0]['dsn']=self.rows[0]['source_dsn']
        with self.assertRaises(mod.Refusal):
            self.checked()

    def test_namespace_overlaps_managed_dataset_refused(self):
        self.dspal['datasets']['MANAGED']={'dsn':'BCPL.TA2STG.LOAD'}
        with self.assertRaisesRegex(mod.Refusal,'overlaps'):
            self.checked()

    def test_other_but_valid_namespace_refused(self):
        self.allocation['staging_namespace']='HERC02.BCPL.PRIVATE'
        with self.assertRaisesRegex(mod.Refusal, 'owner-approved'):
            self.checked()

    def test_wrong_namespace_refused(self):
        self.allocation['staging_namespace']='HERC02.BCPL'
        with self.assertRaises(mod.Refusal):
            self.checked()

    def test_missing_allocation_refused(self):
        self.allocation['targets'].pop()
        with self.assertRaisesRegex(mod.Refusal,'exactly 18'):
            self.checked()

    def test_renumbered_target_refused(self):
        self.allocation['targets'][0]['sequence']=4
        with self.assertRaises(mod.Refusal):
            self.checked()

    def test_zero_space_refused(self):
        self.allocation['targets'][0]['space']['primary_tracks']=0
        with self.assertRaises(mod.Refusal):
            self.checked()

    def test_negative_space_refused(self):
        self.allocation['targets'][0]['space']['directory_blocks']=-1
        with self.assertRaises(mod.Refusal):
            self.checked()

    def test_float_space_refused(self):
        self.allocation['targets'][0]['space']['secondary_tracks']=1.5
        with self.assertRaises(mod.Refusal):
            self.checked()

    def test_space_overflow_refused(self):
        self.allocation['targets'][0]['space']['primary_tracks']=65536
        with self.assertRaises(mod.Refusal):
            self.checked()

    def test_approval_cannot_reselect_members(self):
        self.allocation['targets'][0]['members']=['EXTRA']
        with self.assertRaisesRegex(mod.Refusal,'fields'):
            self.checked()

    def test_jcl_duplicate_member_refused(self):
        rows=self.checked()
        rows[0]['members']=rows[0]['members']+[rows[0]['members'][0]]
        with self.assertRaisesRegex(mod.Refusal,'duplicate selected'):
            mod.render_jcl(rows)

    def test_jcl_invalid_member_refused(self):
        rows=self.checked()
        rows[0]['members']=['BAD-NAME']+rows[0]['members'][1:]
        with self.assertRaisesRegex(mod.Refusal,'invalid or duplicate'):
            mod.render_jcl(rows)

    def test_jcl_wrong_dcb_refused(self):
        rows=self.checked()
        rows[0]['dcb']={'dsorg':'PO','recfm':'FB','lrecl':81,'blksize':800}
        with self.assertRaisesRegex(mod.Refusal,'unsupported'):
            mod.render_jcl(rows)

    def test_jcl_bad_sequence_refused(self):
        rows=self.checked()
        rows[0]['sequence']=5
        with self.assertRaisesRegex(mod.Refusal,'noncontiguous'):
            mod.render_jcl(rows)

    def test_jcl_overwide_card_refused(self):
        rows=self.checked()
        rows[0]['source_dsn']='HERC02.BCPL.'+'X'*60
        with self.assertRaisesRegex(mod.Refusal,'exceeds'):
            mod.render_jcl(rows)

    def test_render_no_global_mvs_mutation(self):
        operation='\n'.join(x for x in self.deck().splitlines() if not x.startswith('//*'))
        self.assertFalse(any(word in operation for word in ('PUNCH','TAPE','DEVINIT','HETINIT')))

    def test_main_writes_only_new_private_draft(self):
        alloc=self.root/'alloc.json'
        alloc.write_text(json.dumps(self.allocation))
        out=self.root/'workarea'/'draft.jcl'
        fakecore=types.SimpleNamespace(load=lambda p:self.manifest if 'inventory' in str(p)
                                        else self.dspal,
                                        check=lambda *a, **kw:None)
        fakesource=types.SimpleNamespace(core=lambda:fakecore)
        with patch.object(mod,'ROOT',self.root), patch.object(mod,'import_script',return_value=fakesource), \
             patch.object(mod,'verify_history') as verifier:
            args=['--stage-evidence',str(self.directory),
                  '--allocations',str(alloc),'--output',str(out)]
            self.assertEqual(mod.main(args),0)
            self.assertEqual(verifier.call_count,1)
            self.assertEqual(out.read_text(),self.deck())
            self.assertEqual(mod.main(args),1)  # No draft overwrite, no retry
        self.assertEqual(out.read_text(),self.deck())

    def test_main_refuses_draft_outside_workarea(self):
        alloc=self.root/'alloc.json'
        alloc.write_text(json.dumps(self.allocation))
        out=self.root/'foreign.jcl'
        fakecore=types.SimpleNamespace(load=lambda p:self.manifest if 'inventory' in str(p)
                                        else self.dspal,
                                        check=lambda *a, **kw:None)
        fakesource=types.SimpleNamespace(core=lambda:fakecore)
        with patch.object(mod,'ROOT',self.root), patch.object(mod,'import_script',return_value=fakesource), \
             patch.object(mod,'verify_history'):
            self.assertEqual(mod.main(['--stage-evidence',str(self.directory),
                                        '--allocations',str(alloc),'--output',str(out)]),1)
        self.assertFalse(out.exists())

    def test_member_extras_count_is_observed_not_hardcoded(self):
        self.plan['excluded_development_members']=80
        self.assertEqual(len(mod.validate_worksheet(self.plan,self.manifest,self.dspal)),18)

    def test_main_uses_verified_worksheet_before_output(self):
        # Existing saved files are deliberately not accepted as enough:
        # stage history replay must be called, before writing any JCL.
        alloc=self.root/'alloc.json'
        alloc.write_text(json.dumps(self.allocation))
        out=self.root/'workarea'/'draft.jcl'
        fakecore=types.SimpleNamespace(load=lambda p:self.manifest if 'inventory' in str(p)
                                        else self.dspal,
                                        check=lambda *a, **kw:None)
        fakesource=types.SimpleNamespace(core=lambda:fakecore)
        with patch.object(mod,'ROOT',self.root), patch.object(mod,'import_script',return_value=fakesource), \
             patch.object(mod,'verify_history',side_effect=mod.Refusal('uncertain source')):
            rc=mod.main(['--stage-evidence',str(self.directory),
                         '--allocations',str(alloc),'--output',str(out)])
        self.assertEqual(rc,1)
        self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
