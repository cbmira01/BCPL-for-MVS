"""TA.2 rc2 preview isolated tests; no MVS, media or network calls."""
import importlib.machinery
import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/ta2-rc2-producer-preview'
loader = importlib.machinery.SourceFileLoader('ta2rc2preview', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixture():
    rows = []
    for n in range(1, 22):
        dcb = {'dsorg': 'PS', 'recfm': 'FB', 'lrecl': 80, 'blksize': 800} if n == 1 else (mod.LOAD if n == 12 else mod.FB)
        row = {'sequence': n, 'kind': 'sequential_text' if n == 1 else 'pds_unload', 'target_dcb': deepcopy(dcb)}
        if n == 1: row['generator'] = 'bootstrap_fb80'
        elif n == 2: row['generator'] = 'installer_pds'
        else:
            row['transfer'] = 'iebcopy_unload'
            row['members'] = [f'M{i:07d}' for i in range(8 if n == 3 else 7)] if n <= 20 else [f'C{i:07d}' for i in range(15)]
        if n == 21:
            row['dspal_key'] = 'CAMB_SOURCE'
            row['rights_status'] = 'preservation-policy-approved-rights-unresolved'
        rows.append(row)
    return ({'datasets': deepcopy(rows[:20])},
            {'phase':'candidate', 'release': {'candidate_id':'BCPL-0.1.0-rc2', 'native_compiler':'absent', 'cambridge_source':'included'},
             'volume': {'volser':'BC0002'}, 'datasets': rows})

class Renderer:
    def render_write_jcl(self, manifest):
        lines=[]
        for n,row in enumerate(manifest['datasets'],1):
            lines.extend([f'//T{n:04d} EXEC PGM=' + ('IEBGENER' if n==1 else 'IEBCOPY'),
                          f'//OUT DD DSN=BCPL.BT{n:04d},', f'//    LABEL=({n},SL)'])
            lines.extend(f' SELECT MEMBER=({m})' for m in row.get('members',[]))
        return '\n'.join(lines)+'\n'

class TestPreview(unittest.TestCase):
    def setUp(self): self.rc1,self.rc2=fixture()
    def test_21_positions_and_nonmutating(self):
        original=deepcopy(self.rc2)
        text=mod.preview(self.rc1,self.rc2,Renderer())
        self.assertIn('DSN=BCPL.BT0021',text)
        self.assertEqual(self.rc2,original)
        self.assertEqual(mod.source_plan(self.rc1,self.rc2)['datasets'][1]['members'],list(mod.INSTALLER))
        self.assertEqual(mod.source_plan(self.rc1,self.rc2)['datasets'][20]['producer_source_dsn'],'HERC02.BCPL.TA2STG.BT0021')
    def test_reject_source_mutation(self):
        self.rc2['datasets'][3]['members'][0]='ALTERED'
        with self.assertRaises(mod.Refusal): mod.source_plan(self.rc1,self.rc2)
    def test_reject_duplicate_member(self):
        self.rc2['datasets'][20]['members'][1]=self.rc2['datasets'][20]['members'][0]
        with self.assertRaises(mod.Refusal): mod.source_plan(self.rc1,self.rc2)
    def test_reject_wrong_dcb(self):
        self.rc2['datasets'][20]['target_dcb']['blksize']=1600
        with self.assertRaises(mod.Refusal): mod.source_plan(self.rc1,self.rc2)
    def test_reject_rights_reclassification(self):
        self.rc2['datasets'][20]['rights_status']='approved'
        with self.assertRaises(mod.Refusal): mod.source_plan(self.rc1,self.rc2)
    def test_reject_native_compiler_claim(self):
        self.rc2['release']['native_compiler']='present'
        with self.assertRaises(mod.Refusal): mod.source_plan(self.rc1,self.rc2)
    def test_reject_incomplete_jcl(self):
        class Broken:
            def render_write_jcl(self,plan): return '//INVALID\n'
        with self.assertRaises(mod.Refusal): mod.preview(self.rc1,self.rc2,Broken())
    def test_reject_wrong_member_total(self):
        self.rc2['datasets'][20]['members'].pop()
        with self.assertRaises(mod.Refusal): mod.source_plan(self.rc1,self.rc2)

if __name__=='__main__': unittest.main()
