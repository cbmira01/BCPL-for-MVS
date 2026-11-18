"""No Docker/JES/tape operations: negative and synthetic TA.1 runner tests."""
from __future__ import annotations

import importlib.machinery
import importlib.util
import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[4]
S = ROOT / 'packaging/distribution/create-tape/scripts/run-ta1-track-a'
l = importlib.machinery.SourceFileLoader('ta1_track_a_one_shot', str(S))
spec = importlib.util.spec_from_loader(l.name, l)
mod = importlib.util.module_from_spec(spec)
l.exec_module(mod)


def labels(seq2=2):
    result = "Label               : 'VOL1'\nVolume Serial       : 'BTA101'\n"
    for seq, dsn in [(1, 'BCPL.BT0001'), (seq2, 'BCPL.BT0002')]:
        for name in ('HDR1', 'HDR2', 'EOF1', 'EOF2'):
            result += (f"Label               : '{name}'\n"
                       f"Dataset ID          : '{dsn}    '\n"
                       f"Volume Serial       : 'BTA101'\n"
                       f"Dataset Sequence    : '{seq:04d}'\n")
    return result


class TestRunner(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tapes = self.root / 'mvs-state/tape'
        self.tapes.mkdir(parents=True)
        (self.root / 'workarea').mkdir()
        self.log = self.root / 'workarea/log'
        self.log.mkdir()
        attrs = [('ROOT', self.root), ('TAPE', self.tapes / mod.IMAGE),
                 ('OPS', self.root / 'workarea/ta1-operations'),
                 ('ATTEMPT', self.root / 'workarea/ta1-operations/attempt.json'),
                 ('LOG', self.log)]
        for name, value in attrs:
            p = mock.patch.object(mod, name, value)
            p.start(); self.addCleanup(p.stop)

    def test_default_refuses_operation(self):
        with mock.patch.object(mod.sys, 'stdout', new_callable=io.StringIO):
            self.assertEqual(mod.main([]), 0)
        self.assertFalse(mod.ATTEMPT.exists())
        self.assertFalse(mod.TAPE.exists())

    def test_no_tty_does_not_create_media(self):
        with mock.patch.object(mod.sys.stdin, 'isatty', return_value=False), \
             mock.patch.object(mod.sys, 'stderr', new_callable=io.StringIO):
            self.assertEqual(mod.main(['--run']), 2)
        self.assertFalse(mod.ATTEMPT.exists())
        self.assertFalse(mod.TAPE.exists())

    def test_atomic_attempt_cannot_repeat(self):
        mod.reserve_once()
        self.assertTrue(mod.ATTEMPT.exists())
        with self.assertRaisesRegex(mod.Halt, 'already attempted'):
            mod.reserve_once()

    def test_atomic_image_cannot_overwrite(self):
        mod.reserve_image()
        self.assertEqual(mod.TAPE.read_bytes(), b'')
        mod.TAPE.write_bytes(b'valuable existing data')
        with self.assertRaisesRegex(mod.Halt, 'refuse overwrite'):
            mod.reserve_image()
        self.assertEqual(mod.TAPE.read_bytes(), b'valuable existing data')

    def test_existing_image_rejected(self):
        mod.TAPE.write_bytes(b'valuable data')
        with self.assertRaisesRegex(mod.Halt, 'NO OVERWRITE'):
            mod.check_existing_media(self.log)
        self.assertEqual(mod.TAPE.read_bytes(), b'valuable data')

    def test_any_existing_volser_collision_rejected(self):
        (self.tapes / 'else.aws').write_bytes(b'fake')
        with mock.patch.object(mod, 'tape_map', return_value=labels()):
            with self.assertRaisesRegex(mod.Halt, 'already on else.aws'):
                mod.check_existing_media(self.log)

    def test_unrecognized_media_refused(self):
        (self.tapes / 'unexpected.dat').write_bytes(b'data')
        with self.assertRaisesRegex(mod.Halt, 'unknown or unsafe'):
            mod.check_existing_media(self.log)

    def test_symlinked_media_refused(self):
        (self.tapes / 'bad.aws').symlink_to(self.root / 'no-data')
        with self.assertRaisesRegex(mod.Halt, 'unknown or unsafe'):
            mod.check_existing_media(self.log)

    def test_empty_tape_inventory_allowed(self):
        mod.check_existing_media(self.log)

    def test_unmounted_device_ready(self):
        def good(name, argv, **kwargs):
            return (0, '23:50 HHC02279I 0:0480 3420 * IO[6] maxsize=0\n') if name.startswith('hercules') else \
                   (0, 'UNIT TYPE STATUS VOLSER VOLSTATE\n480 3400 O /REMOV\n')
        with mock.patch.object(mod, 'must_run', side_effect=good):
            mod.inspect_device(self.log, 'test', mounted=False)

    def test_wrong_mounted_image_refused(self):
        def responses(name, argv, **kwargs):
            return (0, 'HHC02279I 0:0480 3420 /tk5/tape/other.aws IO[0]\n') if name.startswith('hercules') else \
                   (0, '480 3400 O /REMOV')
        with mock.patch.object(mod, 'must_run', side_effect=responses):
            with self.assertRaisesRegex(mod.Halt, 'mount not confirmed'):
                mod.inspect_device(self.log, 'wrong', mounted=True)

    def test_offline_unit_refused(self):
        def responses(name, argv, **kwargs):
            return (0, 'HHC02279I 0:0480 3420 * IO[6]\n') if name.startswith('hercules') else \
                   (0, '480 3400 O-NRD /REMOV')
        with mock.patch.object(mod, 'must_run', side_effect=responses):
            with self.assertRaisesRegex(mod.Halt, 'not online/ready'):
                mod.inspect_device(self.log, 'offline', mounted=False)

    def test_mvs_catalog_ambiguity_refused(self):
        def result(name, argv, **kwargs):
            if name == 'mvs-source-stat':
                return (0, 'Dataset: HERC02.BCPL.DIST.DOCS DSORG:PO RECFM:FB LRECL:80 BLKSIZE:800')
            if name == 'mvs-source-members':
                return (0, 'HERC02.BCPL.DIST.DOCS:\n' + '\n'.join('    ' + x for x in sorted(mod.EXPECTED_MEMBERS)))
            return (0, 'no diagnostics')
        with mock.patch.object(mod, 'must_run', side_effect=result), \
             mock.patch.object(mod, 'capture', return_value=(0, 'ambiguous')):
            with self.assertRaisesRegex(mod.Halt, 'catalog collision'):
                mod.check_guest(self.log)

    def test_valid_two_dataset_label_sequence(self):
        mod.TAPE.write_bytes(b'aws synthetic record data')
        def response(name, argv, **kwargs):
            (self.log / (name + '.txt')).write_text(labels() if name == 'labels-final' else 'filemark fixture')
            return 0, 'fixture'
        with mock.patch.object(mod, 'must_run', side_effect=response), \
             mock.patch.object(mod.sys, 'stdout', new_callable=io.StringIO):
            mod.finish_inspection(self.log)
        self.assertEqual(len((self.log / 'sha256.txt').read_text().split()[0]), 64)

    def test_wrong_second_sequence_refused(self):
        mod.TAPE.write_bytes(b'aws synthetic record data')
        def response(name, argv, **kwargs):
            (self.log / (name + '.txt')).write_text(labels(1) if name == 'labels-final' else 'filemark fixture')
            return 0, 'fixture'
        with mock.patch.object(mod, 'must_run', side_effect=response):
            with self.assertRaisesRegex(mod.Halt, 'sequence for BCPL.BT0002'):
                mod.finish_inspection(self.log)


if __name__ == '__main__':
    unittest.main()
