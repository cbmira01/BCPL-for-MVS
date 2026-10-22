"""Offline R.2 batched acceptance source, fixture and JCL safety checks."""
import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class BatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.n=load(HERE/'make-negatives.py','r2_neg_tests')
        cls.m=load(HERE/'make-matrix.py','r2_matrix_tests')

    def test_cases_cover_all_diagnostics_and_positive_dependency(self):
        cases=self.n.CASES
        self.assertEqual(len(cases),21)
        self.assertEqual([c.name for c in cases].count('linkmiss'),1)
        self.assertEqual([c.name for c in cases].count('validdep'),1)
        self.assertTrue(set(range(1001,1015)).issubset(
            {c.diagnostic for c in cases}))
        self.assertTrue(any(c.name=='dupslot' for c in cases))
        self.assertTrue(any(c.name=='minor' for c in cases))

    def test_linked_fixture_inputs_are_distinct_and_readonly(self):
        trail=self.m.load(self.m.TRAIL,'r2_neg_fixture_test')
        data={x:trail.sample_generated() for x in ('zero','both')}
        deck=self.n.build(data,["//R2NEG JOB (BCPL),'R2 NEGATIVE',CLASS=A,MSGCLASS=A"],
                          'HERC02.BCPL.BOOT.OBJ')
        lines=deck.splitlines()
        self.assertEqual(lines.count('/*'),
                         21+len([x for x in lines if x.startswith('//AS') or x.startswith('//AG') or x.startswith('//AD')]))
        self.assertEqual(sum(row.startswith('//ASMN') for row in lines),1)
        self.assertEqual(sum(row.startswith('//ASMR') for row in lines),1)
        self.assertEqual(sum(row.startswith('//L') and ' EXEC PGM=IEWL' in row for row in lines),21)
        self.assertEqual(sum(row.startswith('//G') and ' EXEC PGM=*.' in row for row in lines),21)
        self.assertNotIn('BOOT.DEVOBJ',deck)
        self.assertNotIn('DISP=MOD',deck)
        self.assertIn('DISP=SHR',deck)
        self.assertTrue(all(row.isascii() and len(row)<=71 for row in lines))
        self.assertTrue(all('COND=(0,NE,L' in row for row in lines
                            if 'TIME=(,2),COND=' in row))

    def test_no_partial_global_publication_and_mutation_sources(self):
        old='R1BAD    LR    9,10\n         L     15,=A(IOFIN)\n'
        witness=self.n.witness(old)
        self.assertIn("X'C7D3F32C'",witness)
        self.assertIn("X'C7D3F4AC'",witness)
        self.assertIn('LA    15,16',witness)
        ext=self.m.extension_sources()
        by_name={c.name:c for c in self.n.CASES}
        d=self.n.fixture(by_name['validdep'],ext)[1]['b']
        self.assertIn("CL8'BCPLDEMO',F'1',F'0'",d)
        d=self.n.fixture(by_name['minor'],ext)[1]['b']
        self.assertIn("CL8'BCPLDEMO',F'1',F'1'",d)
        d=self.n.fixture(by_name['dupslot'],ext)[1]['b']
        self.assertIn("F'203',A(R2BDISP)",d)
        reg=self.n.fixture(by_name['required'],ext)[0]
        self.assertIn("F'1',F'2',F'0'",reg)


if __name__=='__main__':unittest.main()
