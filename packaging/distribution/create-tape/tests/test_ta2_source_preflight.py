"""Offline synthetic TA.2 MVS source-preflight parsing and safety checks."""
import importlib.machinery
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / 'packaging/distribution/create-tape/scripts/ta2-source-preflight'
loader = importlib.machinery.SourceFileLoader('ta2_source_preflight_tests', str(SRC))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)


class SourcePreflightTests(unittest.TestCase):
    dcb = {'dsorg': 'PO', 'recfm': 'U', 'lrecl': 0, 'blksize': 6144}
    dsn = 'HERC02.BCPL.MR10KIT.LOAD'
    stat = ('Dataset:   HERC02.BCPL.MR10KIT.LOAD (MR10_LOAD)\n'
            '    Job:9169,  Volume:TSO003,  DSORG:PO,  RECFM:U,  LRECL:0,  BLKSIZE:6144\n')
    ls = 'HERC02.BCPL.MR10KIT.LOAD:\n    ICINT19\n'

    def test_actual_ta1b_shape(self):
        self.assertEqual(mod.inspect_stat(self.stat, self.dsn, 'MR10_LOAD', self.dcb), 'TSO003')
        self.assertEqual(mod.inspect_ls(self.ls, self.dsn, ['ICINT19'])['missing_members'], [])

    def test_stat_wrong_dsn(self):
        with self.assertRaises(mod.Refusal):
            mod.inspect_stat(self.stat, 'HERC02.BCPL.BOOT.OBJ', 'BOOT_OBJ', self.dcb)

    def test_stat_wrong_logical_key(self):
        with self.assertRaises(mod.Refusal):
            mod.inspect_stat(self.stat, self.dsn, 'MR10_OBJ', self.dcb)

    def test_stat_missing_logical_key(self):
        with self.assertRaises(mod.Refusal):
            mod.inspect_stat(self.stat.replace(' (MR10_LOAD)', ''),
                             self.dsn, 'MR10_LOAD', self.dcb)

    def test_stat_duplicated_or_spoofed_heading(self):
        with self.assertRaises(mod.Refusal):
            mod.inspect_stat(self.stat.replace(' (MR10_LOAD)', ' (MR10_LOAD) unexpected'),
                             self.dsn, 'MR10_LOAD', self.dcb)

    def test_stat_multiple_dataset_headings_refused(self):
        with self.assertRaises(mod.Refusal):
            mod.inspect_stat(self.stat + 'Dataset:   HERC02.BCPL.BOOT.OBJ (BOOT_OBJ)\n',
                             self.dsn, 'MR10_LOAD', self.dcb)

    def test_stat_wrong_dcb(self):
        for key, value in [('dsorg', 'PS'), ('recfm', 'FB'), ('lrecl', 80), ('blksize', 800)]:
            with self.subTest(key=key), self.assertRaises(mod.Refusal):
                mod.inspect_stat(self.stat, self.dsn, 'MR10_LOAD', {**self.dcb, key: value})

    def test_stat_without_volume(self):
        with self.assertRaises(mod.Refusal):
            mod.inspect_stat(self.stat.replace('Volume:TSO003', ''), self.dsn, 'MR10_LOAD', self.dcb)

    def test_extra_development_members_not_selected(self):
        x = mod.inspect_ls(self.ls + '    EXTRA\n', self.dsn, ['ICINT19'])
        self.assertEqual(x['development_extras'], ['EXTRA'])
        self.assertEqual(x['missing_members'], [])

    def test_missing_selected_member_reported(self):
        x = mod.inspect_ls(self.ls, self.dsn, ['ICINT19', 'MISSING'])
        self.assertEqual(x['missing_members'], ['MISSING'])

    def test_duplicate_member_refused(self):
        with self.assertRaises(mod.Refusal):
            mod.inspect_ls(self.ls + '    ICINT19\n', self.dsn, ['ICINT19'])

    def test_wrong_directory_heading_refused(self):
        with self.assertRaises(mod.Refusal):
            mod.inspect_ls(self.ls, 'HERC02.BCPL.BOOT.OBJ', ['ICINT19'])

    def test_18_sources_derived_from_design_not_second_manifest(self):
        manifest = {'datasets': [dict(sequence=1), dict(sequence=2)] +
                    [dict(sequence=i, dspal_key=f'D{i}', target_dcb=self.dcb,
                          members=['X']) for i in range(3, 21)]}
        dspal = {'mvs': {'hlq': 'HERC02'}, 'datasets': {
            f'D{i}': {'dsn': f'TEST.D{i}'} for i in range(3, 21)}}
        x = mod.expected_sources(manifest, dspal)
        self.assertEqual(len(x), 18)
        self.assertEqual((x[0]['sequence'], x[-1]['sequence']), (3, 20))

    def test_invalid_source_hlq_refused(self):
        with self.assertRaises(mod.Refusal):
            mod.expected_sources({'datasets': []}, {'mvs': {'hlq': 'lower'},
                                                     'datasets': {}})

    def test_invalid_cli_arguments_are_inert(self):
        self.assertEqual(mod.main(['--run']), 2)


if __name__ == '__main__':
    unittest.main()
