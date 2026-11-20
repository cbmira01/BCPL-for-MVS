"""Focused offline safety tests; writes only beneath repository workarea."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
MODULE = ROOT / 'packaging/distribution/compiler-source/pack.py'
spec = importlib.util.spec_from_file_location('ta2_cambridge_source_pack', MODULE)
pack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pack)
SELECTION = json.loads((MODULE.parent / 'source-selection.json').read_text())


class SourcePackTests(unittest.TestCase):
    def setUp(self):
        (ROOT / 'workarea').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='ta2-cam-source-',
                                                dir=ROOT / 'workarea')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.selection = copy.deepcopy(SELECTION)
        members = [
            {'HIST': 'richards-bcpltape/bcplib/bcpl/hist'},
            {'DERIVE': 'workarea/bootstrap-cambridge/demoted/derive'},
            {'HELP': 'bootstrap-toolchain/jcl/helper'},
        ]
        for group, mapping in zip(self.selection['source_sets'], members):
            group['members'] = mapping
            path = self.root / next(iter(mapping.values()))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'ABC\nZ  \n')
        (self.root / 'workarea').mkdir(exist_ok=True)

    def test_proposed_inventory_counts(self):
        entries = pack.parse_selection(SELECTION, ROOT)
        self.assertEqual(len(entries), 29)
        self.assertEqual({role: sum(e[0] == role for e in entries)
                          for role in pack.EXPECTED_ROLES},
                         {'historical': 15, 'derived': 11, 'support': 3})

    def test_mvs_fb80_ebcdic_and_padded_records(self):
        buf, count = pack.encode_fb80(b'A \nZ\n', 'fixture')
        self.assertEqual(count, 2)
        self.assertEqual(len(buf), 160)
        self.assertEqual(buf[:3], bytes([0xC1, 0x40, 0x40]))
        self.assertEqual(buf[80], 0xE9)
        self.assertEqual(buf[79], 0x40)

    def test_proposed_only_no_derived_reads(self):
        (self.root / 'workarea/bootstrap-cambridge/demoted/derive').unlink()
        result, decks = pack.evaluate(self.root, self.selection)
        self.assertEqual(len(result), 3)
        self.assertEqual(len(decks), 2)
        self.assertEqual(result[1]['status'], 'requires-derivation')

    def test_generated_requires_source(self):
        (self.root / 'workarea/bootstrap-cambridge/demoted/derive').unlink()
        with self.assertRaisesRegex(pack.InvalidSource, 'source missing'):
            pack.evaluate(self.root, self.selection, include_generated=True)

    def test_full_derived_report(self):
        report, decks = pack.evaluate(self.root, self.selection, include_generated=True)
        self.assertEqual(len(report), 3)
        self.assertEqual(len(decks), 3)
        self.assertTrue(all(len(x['fb80_sha256']) == 64 for x in report))
        self.assertEqual(report[0]['records'], 2)

    def test_no_release_identity_allowed(self):
        self.selection['volser'] = 'BC0002'
        with self.assertRaisesRegex(pack.InvalidSource, 'do not assign'):
            pack.parse_selection(self.selection, self.root)

    def test_native_executable_claim_rejected(self):
        self.selection['capabilities']['native_cambridge_executable'] = 'included'
        with self.assertRaisesRegex(pack.InvalidSource, 'must not assert'):
            pack.parse_selection(self.selection, self.root)

    def test_unknown_generator_rejected(self):
        self.selection['generation']['generator'] = 'unknown.py'
        with self.assertRaisesRegex(pack.InvalidSource, 'generator'):
            pack.parse_selection(self.selection, self.root)

    def test_unsafe_source_path_rejected(self):
        self.selection['source_sets'][0]['members']['HIST'] = \
            'richards-bcpltape/../../etc/passwd'
        with self.assertRaisesRegex(pack.InvalidSource, 'unsafe'):
            pack.parse_selection(self.selection, self.root)

    def test_cross_family_path_rejected(self):
        self.selection['source_sets'][1]['members']['DERIVE'] = \
            'richards-bcpltape/bcplib/bcpl/hist'
        with self.assertRaisesRegex(pack.InvalidSource, 'outside approved'):
            pack.parse_selection(self.selection, self.root)

    def test_invalid_member_rejected(self):
        self.selection['source_sets'][1]['members']['TOO-LONG-NAME'] = \
            self.selection['source_sets'][1]['members'].pop('DERIVE')
        with self.assertRaisesRegex(pack.InvalidSource, 'invalid MVS member'):
            pack.parse_selection(self.selection, self.root)

    def test_record_width_and_control_rejected(self):
        for raw in (b'A' * 81 + b'\n', b'A\tB\n', b'A\r\n', b'\xff\n', b'A'):
            with self.subTest(raw=raw), self.assertRaises(pack.InvalidSource):
                pack.encode_fb80(raw, 'fixture')

    def test_symlink_rejected(self):
        source = self.root / 'richards-bcpltape/bcplib/bcpl/hist'
        source.unlink()
        source.symlink_to(self.root / 'bootstrap-toolchain/jcl/helper')
        with self.assertRaisesRegex(pack.InvalidSource, 'symlink'):
            pack.parse_selection(self.selection, self.root)

    def test_exclusive_private_output(self):
        report, decks = pack.evaluate(self.root, self.selection, include_generated=True)
        output = self.root / 'workarea' / 'decks'
        pack.write_decks(self.root, output, report, decks)
        self.assertEqual(len(list(output.glob('*.fb80'))), 3)
        self.assertTrue((output / 'source-receipt.json').is_file())
        with self.assertRaisesRegex(pack.InvalidSource, 'already exists'):
            pack.write_decks(self.root, output, report, decks)

    def test_outside_workarea_rejected(self):
        report, decks = pack.evaluate(self.root, self.selection, include_generated=True)
        with self.assertRaisesRegex(pack.InvalidSource, 'remain under'):
            pack.write_decks(self.root, self.root / 'packaging', report, decks)


if __name__ == '__main__':
    unittest.main()
