"""Isolated contract tests; use only repository workarea for temporary files."""
import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/mr10-exp-source-check'
loader = importlib.machinery.SourceFileLoader('exp_source_check', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DisplayContractTests(unittest.TestCase):
    def test_exact_literal_panel(self):
        with tempfile.TemporaryDirectory(dir=SCRIPT.parents[4] / 'workarea') as temp:
            root = Path(temp)
            manifest = root / 'mr10-kit-compiler/tests/00-regression-panel/manifest.tsv'
            jcl = root / 'mr10-kit-compiler/jcl/run-regression-tests.jcl'
            manifest.parent.mkdir(parents=True)
            jcl.parent.mkdir(parents=True)
            rows = []
            comments = []
            for num, name in enumerate(module.EXPECTED_NAMES, 1):
                source = f'sources/t{num:02d}.bcpl'
                expected = f'golden/t{num:02d}.expected'
                src = root / source
                gold = root / expected
                src.parent.mkdir(parents=True, exist_ok=True)
                gold.parent.mkdir(parents=True, exist_ok=True)
                src.write_text(f'GLOBAL $( WRITEF:76 $)\nLET START() BE $(\n'
                               f' WRITEF("TEST: case {num}*N")\n'
                               f' WRITEF("EXP: CASE {num}*N")\n'
                               f' WRITEF("RP: CASE %N*N", {num})\n $)\n')
                gold.write_text(f'RP: CASE {num}\n')
                rows.append('\t'.join((name, 'cat', source, '', '', expected, '0')))
                comments.append(f'//* EXECUTE CASE {num:02d}: {name}')
            manifest.write_text('# panel\n' + '\n'.join(rows) + '\n')
            jcl.write_text('\n'.join(comments) + '\n')
            self.assertEqual(module.check_manifest(root), (12, 12))
            source = root / 'sources/t03.bcpl'
            baseline = source.read_text()
            for changed in (baseline.replace('EXP: CASE 3', 'EXP: WRONG'),
                            baseline.replace('EXP: CASE 3', 'EXP: CASE %N'),
                            baseline.replace('EXP: CASE 3', 'RP: CASE 3'),
                            baseline.replace('EXP: CASE 3', 'EXP: ' + 'X' * 85)):
                source.write_text(changed)
                with self.assertRaises(ValueError):
                    module.check_manifest(root)
            source.write_text(baseline)
            self.assertEqual(module.check_manifest(root), (12, 12))
            jcl.write_text(jcl.read_text().replace('EXECUTE CASE 09', 'EXECUTE CASE 19'))
            with self.assertRaises(ValueError):
                module.check_manifest(root)

    def test_regex_requires_literal_exp(self):
        source = ' WRITEF("EXP: SCALAR 17 42*N")\n WRITEF("EXP: LITERAL*N")\n'
        self.assertEqual(module.EXP.findall(source), ['EXP: SCALAR 17 42', 'EXP: LITERAL'])
        self.assertEqual(module.EXP.findall(' WRITEF("EXP: %N*N", X)\n'), [])


if __name__ == '__main__':
    unittest.main()
