"""Offline recipient-profile contract and refusal tests (no MVS state change)."""
import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/ta3-rc3-remaining-profiles'
loader=importlib.machinery.SourceFileLoader('ta3_profiles_tested',str(SCRIPT))
spec=importlib.util.spec_from_loader(loader.name,loader)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestProfiles(unittest.TestCase):
    def manifest(self):
        mr10=[5,1,4,9,11,21,26,1,1]
        native=[10,9,4,6,3,3,3,3,15]
        ds=[{'sequence':1},{'sequence':2}]
        for n in range(3,22):
            group=('common' if n==3 else 'mr10' if n<=12 else
                   'native' if n<=20 else 'cambridge-source')
            count=(7 if n==3 else mr10[n-4] if n<=12 else native[n-13])
            ds.append({'sequence':n,'group':group,
              'target_dsn_template':'{HLQ}.BCPL.'+('MR10KIT.LOAD' if n==12 else f'SOURCE.P{n:04d}'),
              'members':[f'M{i:03d}' for i in range(count)],
              'target_dcb':{'dsorg':'PO','recfm':'U' if n==12 else 'FB',
                            'lrecl':0 if n==12 else 80,
                            'blksize':6144 if n==12 else 800}})
        return {'release':{'candidate_id':'BCPL-0.1.0-rc3','native_compiler':'absent'},
                'volume':{'volser':'BC0003'},'datasets':ds}

    def test_native_combined_profiles(self):
        result=mod.selection(self.manifest(),'HERC02.')
        self.assertEqual([len(x[2]) for x in result.values()],[11,20])
        self.assertEqual([sum(len(row[2]) for row in x[2]) for x in result.values()],
                         [67,146])
        allnames=[row[1] for p in result.values() for row in p[2]]
        self.assertEqual(len(set(allnames)),31)
        self.assertNotIn('HERC02.BCPL.TA3N1.DIST.INST',allnames)
        self.assertIn('HERC02.BCPL.TA3N2.DIST.INST',allnames)
        self.assertIn('HERC02.BCPL.TA3N3.DIST.INST',allnames)

    def test_refuse_wrong_group_and_identity(self):
        m=self.manifest()
        m['datasets'][12]['group']='mr10'
        with self.assertRaises(mod.Refusal):mod.selection(m,'HERC02.')
        m=self.manifest()
        m['release']['native_compiler']='present'
        with self.assertRaises(mod.Refusal):mod.selection(m,'HERC02.')
        m=self.manifest()
        m['volume']['volser']='BC0002'
        with self.assertRaises(mod.Refusal):mod.selection(m,'HERC02.')

    def test_refuse_destination_collision(self):
        m=self.manifest()
        m['datasets'][4]['target_dsn_template']=m['datasets'][3]['target_dsn_template']
        with self.assertRaises(mod.Refusal):mod.selection(m,'HERC02.')

    def test_render_comments_and_active_controls(self):
        class Ref:
            TAPE_UNIT='480'
            VOLUME='TSO002'
        old=mod.JCL
        with tempfile.TemporaryDirectory(dir=SCRIPT.parents[4]/'workarea') as directory:
            try:
                mod.JCL=Path(directory)
                file=mod.JCL/'TA3NATV.jcl'
                file.write_text('//* ADD JOB CARD <HLQ> <DVOL>\n'
                                '//R0003 EXEC PGM=IEBCOPY\n'
                                '//INTAPE DD DSN=BCPL.BT0003,UNIT=<TAPE>\n'
                                '//OUTPDS DD DSN=<HLQ>.BCPL.DIST.DOCS,\n'
                                '//            VOL=SER=<DVOL>,UNIT=<DASD>\n//\n')
                rendered=mod.render('TA3NATV','HERC02.BCPL.TA3N2',Ref())
                self.assertIn('DSN=HERC02.BCPL.TA3N2.DIST.DOCS',rendered)
                self.assertIn('UNIT=480',rendered)
                file.write_text('//R0003 EXEC PGM=IEBCOPY\n'
                                '//INTAPE DD DSN=<MISSING>\n//\n')
                with self.assertRaises(mod.Refusal):
                    mod.render('TA3NATV','HERC02.BCPL.TA3N2',Ref())
            finally: mod.JCL=old

    def test_refuse_missing_ta3n1_receipt(self):
        class Ref:
            MARKER=SCRIPT.parents[4]/'workarea'/'not-a-ta3n1-receipt'
        with self.assertRaises(mod.Refusal):mod.prior_checkpoint(Ref())

    def test_recipient_uses_existing_mvs_tooling(self):
        ref=mod.tools()
        self.assertEqual(ref.GO_STEPS[-1],('R01','ICINT19'))
        self.assertEqual(ref.AWS_SHA256,
                         '6c54c4df2b75020a698110061c4f8003b09adbe21f738848dcaed3da495d81e1')


if __name__=='__main__':unittest.main()
