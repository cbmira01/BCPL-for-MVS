"""TA.1B new AWS writer safety tests. Entirely synthetic; no Docker/JES access."""
from __future__ import annotations
import hashlib
import importlib.machinery
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

SRC = Path(__file__).resolve().parents[1] / 'scripts/run-ta1-track-b-write'
loader = importlib.machinery.SourceFileLoader('run_ta1b_write', str(SRC))
spec = importlib.util.spec_from_loader(loader.name, loader)
script = importlib.util.module_from_spec(spec)
loader.exec_module(script)
REVIEW = Path(__file__).resolve().parents[4]


def labels():
    return ("Label               : 'VOL1'\nVolume Serial       : 'BTA102'\n"
            "Label               : 'HDR1'\nDataset ID          : 'BCPL.BT0001    '\n"
            "Volume Serial       : 'BTA102'\nDataset Sequence    : '0001'\n"
            "Label               : 'HDR2'\n"
            "Label               : 'EOF1'\nDataset ID          : 'BCPL.BT0001    '\n"
            "Volume Serial       : 'BTA102'\nDataset Sequence    : '0001'\n"
            "Label               : 'EOF2'\n")


def layout(numbers=(3, 22, 2, 0)):
    return ''.join(f'File #              : {i}\nBlocks              : {v}\n'
                   for i, v in enumerate(numbers, 1))


class TestWrite(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(dir=REVIEW / 'workarea')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / 'mvs-state/tape').mkdir(parents=True)
        (self.root / 'workarea').mkdir()
        values = {'ROOT':self.root,
                  'TAPE':self.root / 'mvs-state/tape/bcpl-ta1-b-20261117-01.aws',
                  'OPS':self.root / 'workarea/ta1b-operations',
                  'ATTEMPT':self.root / 'workarea/ta1b-operations/BTA102-track-b-init-write.json',
                  'EVIDENCE':self.root / 'workarea/ta1b-operations/BTA102-test-evidence'}
        for name, val in values.items():
            p = patch.object(script, name, val)
            p.start()
            self.addCleanup(p.stop)

    def test_default_is_inert(self):
        with patch.object(script.sys, 'stdout', new_callable=io.StringIO):
            self.assertEqual(script.main([]), 0)
        self.assertFalse(script.TAPE.exists())
        self.assertFalse(script.ATTEMPT.exists())

    def test_requires_tty(self):
        with patch.object(script.sys.stdin, 'isatty', return_value=False), \
             patch.object(script.sys, 'stderr', new_callable=io.StringIO):
            self.assertEqual(script.main(['--run']), 2)
        self.assertFalse(script.TAPE.exists())
        self.assertFalse(script.ATTEMPT.exists())

    def test_no_retry(self):
        script.OPS.mkdir()
        script.take_attempt()
        with self.assertRaisesRegex(script.Halt, 'DO NOT RETRY'):
            script.take_attempt()

    def test_no_overwrite(self):
        script.TAPE.write_bytes(b'important volume')
        with self.assertRaisesRegex(script.Halt, 'DO NOT OVERWRITE'):
            script.check_paths()
        with self.assertRaisesRegex(script.Halt, 'refuse overwrite'):
            script.reserve_image()
        self.assertEqual(script.TAPE.read_bytes(), b'important volume')

    def test_dangling_symlink_refused(self):
        script.TAPE.symlink_to(self.root / 'missing')
        with self.assertRaisesRegex(script.Halt, 'DO NOT OVERWRITE'):
            script.check_paths()

    def test_attempt_receipt_is_private_and_durable(self):
        script.OPS.mkdir()
        script.take_attempt()
        obj = json.loads(script.ATTEMPT.read_text())
        self.assertEqual(obj['volser'], 'BTA102')
        self.assertTrue(obj['no_retry'])
        self.assertEqual(script.ATTEMPT.stat().st_mode & 0o777, 0o600)

    def test_correct_label_contract(self):
        script.final_labels(labels())

    def test_wrong_header_dsn(self):
        with self.assertRaisesRegex(script.Halt, 'HDR1'):
            script.final_labels(labels().replace('BCPL.BT0001', 'BCPL.BT0099', 1))

    def test_duplicate_header(self):
        with self.assertRaisesRegex(script.Halt, 'exactly one HDR1'):
            script.final_labels(labels() + "Label               : 'HDR1'\n")

    def test_bad_sequence(self):
        with self.assertRaisesRegex(script.Halt, 'EOF1'):
            script.final_labels(labels().replace("Label               : 'EOF1'\nDataset ID          : 'BCPL.BT0001    '\nVolume Serial       : 'BTA102'\nDataset Sequence    : '0001'",
                                                 "Label               : 'EOF1'\nDataset ID          : 'BCPL.BT0001    '\nVolume Serial       : 'BTA102'\nDataset Sequence    : '0002'"))

    def test_volume_label_wrong(self):
        with self.assertRaisesRegex(script.Halt, 'serial'):
            script.final_labels(labels().replace('BTA102', 'BTO001'))

    def test_expected_four_file_layout(self):
        self.assertEqual(script.physical_files(layout()), [3,22,2,0])

    def test_wrong_file_count(self):
        with self.assertRaisesRegex(script.Halt, 'unexpected'):
            script.physical_files(layout([3,22,2]))

    def test_zero_payload_refused(self):
        with self.assertRaisesRegex(script.Halt, 'unexpected'):
            script.physical_files(layout([3,0,2,0]))

    def test_file_number_gap_refused(self):
        with self.assertRaisesRegex(script.Halt, 'ambiguous'):
            script.physical_files(layout().replace('File #              : 3', 'File #              : 4', 1))

    def test_mvs_step_rc_confirmed(self):
        script.check_summary('JOB 9100  TA1BWRIT\nUNLOAD IEBCOPY RC=0000\n'
                             'JOB RESULT: SUCCESS\nHIGHEST RC: 0000\n',9100)

    def test_unexpected_step_refused(self):
        with self.assertRaisesRegex(script.Halt, 'one successful'):
            script.check_summary('JOB 9100  TA1BWRIT\nOTHER IEBCOPY RC=0000\n'
                                 'JOB RESULT: SUCCESS\nHIGHEST RC: 0000\n',9100)

    def test_mvs_nonzero_rc_refused(self):
        with self.assertRaisesRegex(script.Halt, 'not successful'):
            script.check_summary('JOB 9100  TA1BWRIT\nUNLOAD IEBCOPY RC=0008\n'
                                 'JOB RESULT: FAIL\nHIGHEST RC: 0008\n',9100)

    def test_readiness_empty(self):
        def checked(argv, name, folder):
            if argv[1:3] == ['tape', 'status']:
                return 'HHC02279I 0:0480 3420 * IO[6] maxsize=0\n'
            return '480 3400 O /REMOV\n'
        script.unit_ready(types.SimpleNamespace(checked=checked), self.root, mounted=False)

    def test_readiness_foreign_volume_refused(self):
        def checked(argv, name, folder):
            return ('HHC02279I 0:0480 3420 /tk5/tape/bcpl01.aws IO[0]\n'
                    if argv[1:3] == ['tape', 'status'] else '480 3400 O /REMOV')
        with self.assertRaisesRegex(script.Halt, 'displace'):
            script.unit_ready(types.SimpleNamespace(checked=checked), self.root, mounted=False)
        with self.assertRaisesRegex(script.Halt, 'expected BTA102'):
            script.unit_ready(types.SimpleNamespace(checked=checked), self.root, mounted=True)

    def test_unmounted_online_not_ready_accepted(self):
        # MVS O-NRD is valid for an empty, online 3420 with no medium.
        def checked(argv, name, folder):
            return ('HHC02279I 0:0480 3420 * IO[6] maxsize=0\n'
                    if argv[1:3] == ['tape','status']
                    else 'UNIT TYPE STATUS VOLSER VOLSTATE\n480 3400 O-NRD /REMOV\n')
        script.unit_ready(types.SimpleNamespace(checked=checked), self.root, mounted=False)

    def test_mounted_online_not_ready_refused(self):
        # After devinit, MVS must see a ready tape (O, not O-NRD).
        def checked(argv, name, folder):
            return ('HHC02279I 0:0480 3420 /tk5/tape/bcpl-ta1-b-20261117-01.aws IO[0]\n'
                    if argv[1:3] == ['tape','status']
                    else '480 3400 O-NRD /REMOV\n')
        with self.assertRaisesRegex(script.Halt, 'not ready after BTA102 mount'):
            script.unit_ready(types.SimpleNamespace(checked=checked), self.root, mounted=True)

    def test_unmounted_offline_not_ready_refused(self):
        def checked(argv, name, folder):
            return ('HHC02279I 0:0480 3420 * IO[6]\n' if argv[1:3] == ['tape','status']
                    else '480 3400 F-NRD /REMOV\n')
        with self.assertRaisesRegex(script.Halt, 'status unrecognized'):
            script.unit_ready(types.SimpleNamespace(checked=checked), self.root, mounted=False)

    def test_unmounted_allocated_refused(self):
        def checked(argv, name, folder):
            return ('HHC02279I 0:0480 3420 * IO[6]\n' if argv[1:3] == ['tape','status']
                    else '480 3400 A /REMOV\n')
        with self.assertRaisesRegex(script.Halt, 'status unrecognized'):
            script.unit_ready(types.SimpleNamespace(checked=checked), self.root, mounted=False)

    def test_mvs_duplicate_unit_rows_refused(self):
        def checked(argv, name, folder):
            return ('HHC02279I 0:0480 3420 * IO[6]\n' if argv[1:3] == ['tape','status']
                    else '480 3400 O /REMOV\n480 3400 O /REMOV\n')
        with self.assertRaisesRegex(script.Halt, 'row missing/ambiguous'):
            script.unit_ready(types.SimpleNamespace(checked=checked), self.root, mounted=False)

    def test_mvs_unrecognized_state_reports_observed_row(self):
        def checked(argv, name, folder):
            return ('HHC02279I 0:0480 3420 * IO[6]\n' if argv[1:3] == ['tape','status']
                    else '480 3400 O-XYZ /REMOV\n')
        with self.assertRaisesRegex(script.Halt, '480 3400 O-XYZ'):
            script.unit_ready(types.SimpleNamespace(checked=checked), self.root, mounted=False)

    def test_docker_identity_mismatch(self):
        fake = types.SimpleNamespace(run=lambda argv,name,folder:(0,'["MVS_UID=-1","MVS_GID=-1"]'))
        with self.assertRaisesRegex(script.Halt, 'UID/GID mismatch'):
            script.docker_identity(fake, self.root)

    def test_docker_environment_not_written(self):
        fake = types.SimpleNamespace(run=Mock(return_value=(0,'["MVS_UID=-1","MVS_GID=-1","SECRET=123"]')))
        with self.assertRaises(script.Halt):
            script.docker_identity(fake, self.root)
        self.assertEqual(fake.run.call_args.args[2], None)

    def test_successful_mock_operation_one_shot(self):
        contract = types.SimpleNamespace(validate_static=lambda:None)
        def checked(argv, name, folder):
            return ''
        preflight = types.SimpleNamespace(live=lambda c,folder:('TSO003','EMPTY',4), checked=checked)
        def fake_import(name, alias):
            return contract if name == 'ta1b-contract' else preflight
        stdout = io.StringIO()
        with patch.object(script.sys.stdin,'isatty',return_value=True), \
             patch('builtins.input',side_effect=['INIT MOUNT WRITE BTA102',
                                                'SUBMIT TA1BWRIT BTA102']), \
             patch.object(script, 'import_script', side_effect=fake_import), \
             patch.object(script, 'unit_ready'), \
             patch.object(script, 'docker_identity'), \
             patch.object(script, 'submit_once', return_value=9100) as submit, \
             patch.object(script, 'inspect_written', return_value=('a'*64,[3,10,2,0])), \
             patch.object(script, 'volume_label', return_value='BTA102'), \
             patch.object(script.sys,'stdout',stdout):
            self.assertEqual(script.operation(), 0)
        self.assertTrue(script.TAPE.exists())
        self.assertTrue(script.ATTEMPT.exists())
        submit.assert_called_once()
        self.assertIn('TA1BWRIT MVS JOB 9100',stdout.getvalue())
        with self.assertRaisesRegex(script.Halt, 'DO NOT RETRY'):
            script.check_paths()

    def test_cancellation_is_read_only(self):
        contract = types.SimpleNamespace(validate_static=lambda:None)
        preflight = types.SimpleNamespace(live=lambda c,folder:('TSO003','EMPTY',4),
                                          checked=lambda argv,name,folder:'')
        with patch.object(script.sys.stdin,'isatty',return_value=True), \
             patch('builtins.input',return_value='NO'), \
             patch.object(script,'import_script',side_effect=lambda name,alias:contract if name == 'ta1b-contract' else preflight), \
             patch.object(script,'unit_ready'),patch.object(script,'docker_identity'), \
             patch.object(script.sys,'stdout',new_callable=io.StringIO):
            with self.assertRaisesRegex(script.Halt,'did not confirm'):
                script.operation()
        self.assertFalse(script.TAPE.exists())
        self.assertFalse(script.ATTEMPT.exists())

    def test_source_volume_drift_refused_before_media_creation(self):
        contract = types.SimpleNamespace(validate_static=lambda:None)
        preflight = types.SimpleNamespace(live=lambda c,folder:('TSO999','EMPTY',4))
        with patch.object(script.sys.stdin,'isatty',return_value=True), \
             patch.object(script,'import_script',side_effect=lambda name,alias:contract if name == 'ta1b-contract' else preflight):
            with self.assertRaisesRegex(script.Halt, 'volume changed'):
                script.operation()
        self.assertFalse(script.TAPE.exists())
        self.assertFalse(script.ATTEMPT.exists())

    def test_occupied_drive_refused_before_media_creation(self):
        contract = types.SimpleNamespace(validate_static=lambda:None)
        preflight = types.SimpleNamespace(live=lambda c,folder:('TSO003','OCCUPIED',4))
        with patch.object(script.sys.stdin,'isatty',return_value=True), \
             patch.object(script,'import_script',side_effect=lambda name,alias:contract if name == 'ta1b-contract' else preflight):
            with self.assertRaisesRegex(script.Halt, 'occupied'):
                script.operation()
        self.assertFalse(script.TAPE.exists())
        self.assertFalse(script.ATTEMPT.exists())


if __name__ == '__main__':
    unittest.main()
