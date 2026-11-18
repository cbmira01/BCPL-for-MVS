"""Completely offline TA.1 BTA101 readback gate negative and positive tests."""
import importlib.machinery
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / 'scripts/run-ta1-track-a-readback'
loader = importlib.machinery.SourceFileLoader('ta1_readback', str(SRC))
spec = importlib.util.spec_from_loader(loader.name, loader)
rb = importlib.util.module_from_spec(spec)
loader.exec_module(rb)
ROOT = Path(__file__).resolve().parents[4]


def label_fixture(seq2=2):
    chunks = ["Label               : 'VOL1'\nVolume Serial       : 'BTA101'\n"]
    for number, dsn in [(1, 'BCPL.BT0001'), (seq2, 'BCPL.BT0002')]:
        for label in ('HDR1', 'HDR2', 'EOF1', 'EOF2'):
            chunks.append(f"Label               : '{label}'\n")
            if label in ('HDR1', 'EOF1'):
                chunks.append(f"Dataset ID          : '{dsn}    '\n"
                              f"Volume Serial       : 'BTA101'\n"
                              f"Dataset Sequence    : '{number:04d}'\n")
    return ''.join(chunks)


class ReadbackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ops = self.root / 'workarea/ta1-operations'
        self.ops.mkdir(parents=True)
        self.tape = self.root / 'mvs-state/tape/bcpl-ta1-a-20261117-01.aws'
        self.tape.parent.mkdir(parents=True)
        self.evidence = self.ops / 'BTA101-track-a-execution-20261118T010626Z-5215'
        self.evidence.mkdir()
        self.log = self.ops / 'new-evidence'
        self.log.mkdir()
        for name, value in [('ROOT', self.root), ('OPS', self.ops), ('TAPE', self.tape),
                            ('WRITE_EVIDENCE', self.evidence), ('ATTEMPT', self.ops / 'BTA101-track-a-readback.json'),
                            ('RUN_LOG', self.log)]:
            patch = mock.patch.object(rb, name, value)
            patch.start()
            self.addCleanup(patch.stop)

    def test_successful_two_dataset_labels(self):
        rb.verify_labels(label_fixture())

    def test_wrong_second_dataset_sequence(self):
        with self.assertRaisesRegex(rb.Halt, 'sequence'):
            rb.verify_labels(label_fixture(1))

    def test_wrong_volume(self):
        with self.assertRaisesRegex(rb.Halt, 'VOLSER'):
            rb.verify_labels(label_fixture().replace('BTA101', 'BTO001'))

    def test_missing_eof2(self):
        with self.assertRaisesRegex(rb.Halt, 'standard-label'):
            rb.verify_labels(label_fixture().replace("Label               : 'EOF2'", "Label               : 'EOV2'", 1))

    def test_attempt_atomic(self):
        rb.begin_once()
        self.assertTrue(rb.ATTEMPT.exists())
        with self.assertRaisesRegex(rb.Halt, 'NEVER rerun'):
            rb.begin_once()

    def test_unrecognized_image_refused(self):
        with self.assertRaisesRegex(rb.Halt, 'image missing'):
            rb.check_sha()

    def test_modified_image_refused(self):
        self.tape.write_bytes(b'altered AWS tape')
        with self.assertRaisesRegex(rb.Halt, 'checksum differs'):
            rb.check_sha()

    def test_symlink_image_refused(self):
        self.tape.symlink_to(self.root / 'elsewhere')
        with self.assertRaisesRegex(rb.Halt, 'image missing/unsafe'):
            rb.check_sha()

    def test_write_receipt_absent_refused(self):
        with self.assertRaisesRegex(rb.Halt, 'evidence summary.txt missing'):
            rb.verify_write_receipt()

    def test_write_receipt_validates_provenance_and_sha(self):
        import hashlib
        self.tape.write_bytes(b'sample AWS bytes')
        expected = hashlib.sha256(b'sample AWS bytes').hexdigest()
        with mock.patch.object(rb, 'EXPECTED_SHA', expected):
            (self.evidence / 'sha256.txt').write_text(expected + '  mvs-state/tape/' + self.tape.name + '\n')
            (self.evidence / 'labels-final.txt').write_text(label_fixture())
            (self.evidence / 'submit.txt').write_text('TA1AWRIT: JES JOB 9076 returned accepted RC=0')
            (self.evidence / 'summary.txt').write_text('JOB 9076  TA1AWRIT\nBOOTSTRP IEBGENER RC=0000\nUNLOAD IEBCOPY RC=0000\nJOB RESULT: SUCCESS')
            rb.verify_write_receipt()

    def test_tape_state_unmounted(self):
        def fake_run(_write, label, argv, evidence=None):
            return 'HHC02279I 0:0480 3420 * IO[0]\n' if label.startswith('tape-status') else '480 3400 O-NRD /REMOV\n'
        with mock.patch.object(rb, 'run', side_effect=fake_run):
            self.assertEqual(rb.tape_state(None, self.log, 'x'), 'empty')

    def test_tape_state_mounted(self):
        def fake_run(_write, label, argv, evidence=None):
            return 'HHC02279I 0:0480 3420 /tk5/tape/bcpl-ta1-a-20261117-01.aws IO[0]\n' if label.startswith('tape-status') else '480 3400 O /REMOV\n'
        with mock.patch.object(rb, 'run', side_effect=fake_run):
            self.assertEqual(rb.tape_state(None, self.log, 'x'), 'mounted')

    def test_tape_state_wrong_mount(self):
        def fake_run(_write, label, argv, evidence=None):
            return 'HHC02279I 0:0480 3420 /tk5/tape/bcpl01.aws IO[0]\n' if label.startswith('tape-status') else '480 3400 O /REMOV\n'
        with mock.patch.object(rb, 'run', side_effect=fake_run):
            with self.assertRaisesRegex(rb.Halt, 'DIFFERENT image'):
                rb.tape_state(None, self.log, 'x')

    def test_tape_state_offline(self):
        def fake_run(_write, label, argv, evidence=None):
            return 'HHC02279I 0:0480 3420 * IO[0]\n' if label.startswith('tape-status') else '480 3400 OFFLINE\n'
        with mock.patch.object(rb, 'run', side_effect=fake_run):
            with self.assertRaisesRegex(rb.Halt, 'offline/ambiguous'):
                rb.tape_state(None, self.log, 'x')

    def test_mounted_but_mvs_not_ready_refused(self):
        def fake_run(_write, label, argv, evidence=None):
            return ('HHC02279I 0:0480 3420 /tk5/tape/bcpl-ta1-a-20261117-01.aws IO[0]\n'
                    if label.startswith('tape-status') else '480 3400 O-NRD /REMOV\n')
        with mock.patch.object(rb, 'run', side_effect=fake_run):
            with self.assertRaisesRegex(rb.Halt, 'not ready'):
                rb.tape_state(None, self.log, 'x')

    def test_ensure_mounted_does_not_remount(self):
        self.tape.write_bytes(b'tape fixture')
        with mock.patch.object(rb, 'check_sha'), mock.patch.object(rb, 'tape_state', return_value='mounted'), \
                mock.patch.object(rb, 'run') as call:
            rb.ensure_mounted(None, self.log, 'TA1AR001')
            call.assert_not_called()

    def test_ensure_mounted_mount_once(self):
        with mock.patch.object(rb, 'check_sha'), mock.patch.object(rb, 'tape_state', side_effect=['empty', 'mounted']), \
                mock.patch.object(rb, 'run', return_value='mounted') as call:
            rb.ensure_mounted(None, self.log, 'TA1AR001')
            self.assertEqual(call.call_count, 1)
            self.assertIn('mount', call.call_args.args[1])

    def test_expected_comparison_both_steps(self):
        summary = ('JOB RESULT: SUCCESS\nCMPFB IEBCOMPR RC=0000\n'
                   'CMPPDS IEBCOMPR RC=0000\n')
        def out(_write, label, argv, evidence=None):
            if label.startswith('submit'):
                return 'TA1ACOMP: JES JOB 9079 returned accepted RC=0'
            if label.startswith('summary'):
                return summary
            return 'JES copy'
        with mock.patch.object(rb, 'run', side_effect=out):
            self.assertEqual(rb.submit(None, self.log, 'TA1ACOMP', 'CMPFB,CMPPDS'), 9079)

    def test_missing_second_compare_is_rejected(self):
        def out(_write, label, argv, evidence=None):
            if label.startswith('submit'):
                return 'TA1ACOMP: JES JOB 9079 returned accepted RC=0'
            return 'JOB RESULT: SUCCESS\nCMPFB IEBCOMPR RC=0000\n'
        with mock.patch.object(rb, 'run', side_effect=out):
            with self.assertRaisesRegex(rb.Halt, 'CMPPDS'):
                rb.submit(None, self.log, 'TA1ACOMP', 'CMPFB,CMPPDS')

    def test_restored_pds_members_mismatch(self):
        def out(_write, label, argv, evidence=None):
            if label.startswith('stat'):
                return 'Dataset: HERC02.BCPL.TA1A.PDSREST DSORG:PO RECFM:FB LRECL:80 BLKSIZE:800'
            return 'HERC02.BCPL.TA1A.PDSREST:\n    COMPILE\n'
        with mock.patch.object(rb, 'run', side_effect=out):
            with self.assertRaisesRegex(rb.Halt, 'seven-member inventory'):
                rb.check_restored(type('MockWrite', (), {'EXPECTED_MEMBERS': {'COMPILE', 'README'}}),
                                  self.log, 'HERC02.BCPL.TA1A.PDSREST', 'PO')


if __name__ == '__main__':
    unittest.main()
