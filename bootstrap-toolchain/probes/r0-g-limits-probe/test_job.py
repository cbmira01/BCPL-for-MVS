"""Generator/report checks; no JES access or private credentials."""
import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).parent


def load(file):
    spec = importlib.util.spec_from_file_location(file.replace('-', '_'), HERE/file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class GeneratorTest(unittest.TestCase):
    def test_deck(self):
        m=load('make-job.py')
        source=m.deck(["//R0GLIMIT JOB (BCPL),'R0 LIMITS',CLASS=A"])
        self.assertEqual(source.count('/*\n'),3)
        self.assertIn('ENTRY R0GCHK',source)
        self.assertNotIn('HERC02.BCPL.BOOT.OBJ',source)
        self.assertNotIn('DISP=MOD',source)
        self.assertEqual(len(m.CASES),14)
        self.assertEqual(len(set(c[0] for c in m.CASES)),14)
        self.assertTrue(all(len(x)<=71 for x in source.splitlines()))

    def test_credential_guard(self):
        m=load('make-job.py')
        with self.assertRaises(ValueError):
            m.deck(["//WRONG JOB (BCPL),'WRONG'"])

    def test_report_verifier(self):
        m=load('verify-report.py')
        sample='\n'.join(m.expected_markers())+'\n'
        m.verify(sample)
        with self.assertRaises(ValueError):
            m.verify(sample.replace(m.expected_markers()[0],''))
        with self.assertRaises(ValueError):
            m.verify(sample+m.expected_markers()[0]+'\n')
        with self.assertRaises(ValueError):
            m.verify(sample+'R0 G BOUNDARY CASE FAILED\n')

if __name__=='__main__': unittest.main()
