"""Offline TA.1 Track B live-preflight negative and parser tests."""
from __future__ import annotations

from importlib.machinery import SourceFileLoader
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[4]
P=SourceFileLoader('ta1b_preflight',str(ROOT/'packaging/distribution/create-tape/scripts/ta1b-preflight')).load_module()


def stat():
    return ('Dataset:   HERC02.BCPL.MR10KIT.LOAD (MR10_LOAD)\n'
            '    Job:9092,  Volume:TSO002,  DSORG:PO,  RECFM:U,  LRECL:0,  BLKSIZE:6144\n')


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'workarea')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.tapes=self.root/'mvs-state/tape';self.tapes.mkdir(parents=True)
        self.logs=self.root/'workarea';self.logs.mkdir()
        for attr,value in [('ROOT',self.root),('WORK',self.logs),('TAPES',self.tapes)]:
            patch=mock.patch.object(P,attr,value);patch.start();self.addCleanup(patch.stop)

    def test_dcb_parse(self):
        self.assertEqual(P.parse_source_stat(stat()),'TSO002')

    def test_missing_volume_refused(self):
        with self.assertRaisesRegex(P.Refusal,'volume'):
            P.parse_source_stat(stat().replace('Volume:TSO002,',''))

    def test_wrong_recformat_refused(self):
        with self.assertRaisesRegex(P.Refusal,'PO/U/0/6144'):
            P.parse_source_stat(stat().replace('RECFM:U','RECFM:FB'))

    def test_wrong_blksize_refused(self):
        with self.assertRaisesRegex(P.Refusal,'PO/U/0/6144'):
            P.parse_source_stat(stat().replace('BLKSIZE:6144','BLKSIZE:800'))

    def test_source_member_only(self):
        P.parse_members('HERC02.BCPL.MR10KIT.LOAD:\n    ICINT19\n')

    def test_multiple_source_members_refused(self):
        with self.assertRaisesRegex(P.Refusal,'one selected'):
            P.parse_members('HERC02.BCPL.MR10KIT.LOAD:\n    ICINT19\n    BLIB\n')

    def test_absent_dataset_standard(self):
        P.absent(2,'dspal: data set not found: '+P.DST+'\n', P.DST)

    def test_success_response_does_not_prove_absence(self):
        with self.assertRaisesRegex(P.Refusal,'cataloged'):
            P.absent(0,'Dataset: '+P.DST, P.DST)

    def test_unknown_response_does_not_prove_absence(self):
        with self.assertRaisesRegex(P.Refusal,'ambiguous'):
            P.absent(2,'JES2 error', P.DST)

    def test_volser_from_hetmap(self):
        self.assertEqual(P.parse_volser("Label               : 'VOL1'\nVolume Serial       : 'BTA101'\n"),'BTA101')

    def test_missing_vol1_refused(self):
        with self.assertRaisesRegex(P.Refusal,'VOL1'):
            P.parse_volser('Volume Serial       : BTA101')

    def test_inventory_all_different(self):
        (self.tapes/'one.aws').write_bytes(b'fixture')
        with mock.patch.object(P,'checked',return_value="Label               : 'VOL1'\nVolume Serial       : 'BTA101'\n"):
            self.assertEqual(P.verify_image_inventory(self.logs),1)

    def test_inventory_collision(self):
        (self.tapes/'one.aws').write_bytes(b'fixture')
        with mock.patch.object(P,'checked',return_value="Label               : 'VOL1'\nVolume Serial       : 'BTA102'\n"):
            with self.assertRaisesRegex(P.Refusal,'already present'):
                P.verify_image_inventory(self.logs)

    def test_image_name_collision(self):
        (self.tapes/P.IMAGE).write_bytes(b'valuable existing tape')
        with self.assertRaisesRegex(P.Refusal,'already exists'):
            P.verify_image_inventory(self.logs)
        self.assertEqual((self.tapes/P.IMAGE).read_bytes(),b'valuable existing tape')

    def test_dangling_symlink_refused(self):
        (self.tapes/'old.aws').symlink_to(self.root/'missing')
        with self.assertRaisesRegex(P.Refusal,'unknown tape entry'):
            P.verify_image_inventory(self.logs)

    def test_unit_empty(self):
        def checked(args,name,folder):
            if name=='hercules-0480': return 'HHC02279I 0:0480 3420 * IO[6] maxsize=0\n'
            return '480 3400 O-NRD /REMOV\n'
        with mock.patch.object(P,'checked',side_effect=checked):
            self.assertEqual(P.inspect_unit(self.logs),'EMPTY')

    def test_unit_occupied_does_not_mount(self):
        def checked(args,name,folder):
            if name=='hercules-0480': return 'HHC02279I 0:0480 3420 /tk5/tape/bcpl01.aws IO[0]\n'
            return '480 3400 O /REMOV\n'
        with mock.patch.object(P,'checked',side_effect=checked) as c:
            self.assertEqual(P.inspect_unit(self.logs),'OCCUPIED')
            self.assertEqual(c.call_count,2)

    def test_unit_busy_refused(self):
        def checked(args,name,folder):
            return 'HHC02279I 0:0480 3420 * busy\n'
        with mock.patch.object(P,'checked',side_effect=checked):
            with self.assertRaisesRegex(P.Refusal,'busy'):
                P.inspect_unit(self.logs)

    def test_mvs_offline_refused(self):
        def checked(args,name,folder):
            return 'HHC02279I 0:0480 3420 *\n' if name=='hercules-0480' else '480 3400 OFFLINE\n'
        with mock.patch.object(P,'checked',side_effect=checked):
            with self.assertRaisesRegex(P.Refusal,'unavailable'):
                P.inspect_unit(self.logs)

    def test_run_does_not_use_shell_and_records_output(self):
        with mock.patch.object(P.subprocess,'run') as runner:
            runner.return_value.returncode=0
            runner.return_value.stdout='read-only MVS inquiry'
            runner.return_value.stderr=''
            rc,text=P.run(['tools/datasets/dspal','stat','MR10_LOAD'],'stat',self.logs)
            self.assertEqual(rc,0)
            self.assertIn('read-only',text)
            self.assertEqual(runner.call_args.kwargs['cwd'],self.root)
            self.assertFalse(runner.call_args.kwargs['check'])
            self.assertEqual((self.logs/'stat.txt').read_text(),'RC=0\nread-only MVS inquiry')


if __name__=='__main__':unittest.main()
