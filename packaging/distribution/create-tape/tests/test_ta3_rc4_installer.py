"""TA.3 RC4 offline tape-resident installer contract tests; never touch MVS."""
import importlib.machinery
import importlib.util
import unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/ta3-rc4-installer'
loader=importlib.machinery.SourceFileLoader('ta3_rc4_unit',str(SCRIPT))
spec=importlib.util.spec_from_loader(loader.name,loader)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestRC4(unittest.TestCase):
    def test_identity_registry_scope(self):
        manifest,sizes=mod.load()
        self.assertEqual(manifest['release']['candidate_id'],'BCPL-0.1.0-rc4')
        self.assertEqual(manifest['volume']['volser'],'BC0004')
        self.assertEqual(manifest['release']['native_compiler'],'absent')
        self.assertEqual(len(manifest['datasets']),21)
        self.assertEqual(len(sizes),19)
        self.assertEqual(manifest['datasets'][1]['members'],list(mod.MEMBERS))

    def test_three_profile_selection_and_no_prohibited_instream(self):
        m,sizes=mod.load()
        for key,n in (('MR10',10),('NATIVE',10),('COMBINED',19)):
            body=mod.profile(m,sizes,key)
            self.assertEqual(body.count(' EXEC PGM=IEBCOPY'),n)
            self.assertEqual(body.count('DISP=(NEW,CATLG,DELETE)'),n)
            self.assertEqual(body.count('DIST.INST(COPY)'),n)
            self.assertEqual(body.count('VOL=(PRIVATE,RETAIN,SER=BC0004)'),n)
            self.assertEqual(body.count('SYSIN DD DSN='),n)
            self.assertNotIn('SYSIN DD *',body)
            self.assertNotIn(' DD DATA',body)
            self.assertTrue(body.endswith('//\n'))
            self.assertEqual(body.count(' PEND'),1)
            self.assertEqual(body.count('//GO EXEC'),1)
            self.assertTrue(all(len(x)<=71 for x in body.splitlines()
                            if x.startswith('//') and not x.startswith('//*')))

    def test_profile_dcb_records(self):
        m,sizes=mod.load()
        combined=mod.profile(m,sizes,'COMBINED')
        self.assertEqual(combined.count('RECFM=U,BLKSIZE=6144'),1)
        self.assertEqual(combined.count('BLKSIZE=800)'),18)

    def test_members_and_bootstrap(self):
        m,sizes=mod.load()
        bt1,members=mod.materials(m,sizes)
        self.assertEqual(tuple(members),mod.MEMBERS)
        self.assertEqual(members['COPY'].strip(),
                         'COPY OUTDD=OUTPDS,INDD=INTAPE')
        self.assertIn('NATIVE CAMBRIDGE COMPILER ABSENT',bt1)
        self.assertIn('BC0004',members['RELEASE'])
        self.assertTrue(all(len(x)<=80 for value in members.values()
                        for x in value.splitlines()))
        self.assertTrue(all(len(x)<=80 for x in bt1.splitlines()))

    def test_stage_is_only_two_new_datasets_and_eight_members(self):
        m,sizes=mod.load()
        bt1,members=mod.materials(m,sizes)
        deck=mod.stage_deck(bt1,members)
        self.assertEqual(deck.count('DISP=(NEW,CATLG,DELETE)'),2)
        self.assertEqual(deck.count('//SYSUT1 DD DATA,DLM=Z9'),9)
        self.assertEqual(deck.count('\nZ9\n'),9)
        self.assertEqual(deck.count(' EXEC PGM=IEBGENER'),9)
        self.assertEqual(deck.count(' EXEC PGM=IEFBR14'),1)
        self.assertNotIn('BCPL.TA2R3S',deck)

    def test_writer_reuses_only_untouched_rc3_payload(self):
        m,sizes=mod.load()
        deck=mod.write_deck(m)
        self.assertEqual(deck.count(' EXEC PGM=IEBGENER'),1)
        self.assertEqual(deck.count(' EXEC PGM=IEBCOPY'),20)
        self.assertEqual(deck.count(' SELECT MEMBER='),150)
        self.assertIn('HERC02.BCPL.TA3R4S.BT0001',deck)
        self.assertIn('HERC02.BCPL.TA3R4S.BT0002',deck)
        self.assertIn('HERC02.BCPL.TA2R3S.BT0021',deck)
        self.assertNotIn('SER=BC0003',deck)
        self.assertTrue(all(len(x)<=80 for x in deck.splitlines()))

    def test_no_allocation_in_offline_plan(self):
        bt1,members,stage,writer=mod.plan()
        self.assertTrue(bt1 and stage and writer)
        self.assertEqual(len(members),8)

    def test_width_and_delimiter_refusals(self):
        with self.assertRaises(mod.Refusal):
            mod.cards(['//X '+('X'*78)],jcl=True)
        with self.assertRaises(mod.Refusal):
            mod.cards(['\t'],jcl=False)


if __name__=='__main__':unittest.main()
