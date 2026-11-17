"""TA.0 offline-only synthetic, pinned two-member JES readback tests."""
from __future__ import annotations

import hashlib
import contextlib
import io
from types import SimpleNamespace
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SRC = ROOT / 'tools/distribution/decode-iebptpch-multi.py'
SINGLE = ROOT / 'tools/distribution/decode-iebptpch-readback.py'
FIX = HERE / 'fixtures/ta0-job9044-bcpldemo-transcribed.txt'
SPEC = importlib.util.spec_from_file_location('ta0_multi_decoder', SRC)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def sample_report() -> str:
    """Compose synthetic two-member print from bytes of JOB 9044 fixture.

    This is deliberately NOT a claimed JOB 9045 printer transcript.
    """
    listing = FIX.read_text(encoding='utf-8')
    lines = listing.splitlines()
    head = lines.index('MEMBER NAME  BCPLDEMO')
    data = lines[head + 1:head + 7]
    assert len(data) == 6 and all(len(line.split('  ')) in (8, 12) for line in data)
    data[3] = data[3].removesuffix('*') + '**'
    data[5] = data[5].removesuffix('*') + '**'
    return ('13.25.35 JOB 9045  $HASP373 TA0MULT STARTED - INIT 1 - CLASS A\n'
            '13.25.35 JOB 9045  TA0MULT TA0HEX IEBPTPCH RC= 0000\n'
            'IEF142I TA0MULT TA0HEX - STEP WAS EXECUTED - COND CODE 0000\n'
            '13.25.35 JOB 9045  $HASP395 TA0MULT ENDED\n'
            'PRINT/PUNCH DATA SET UTILITY       PAGE 0001\n'
            '         PRINT TYPORG=PO,TOTCONV=XE,MAXNAME=2\n'
            '         MEMBER NAME=BCPLTIME\n'
            '         MEMBER NAME=BCPLQSAM\n'
            ' EOF ON SYSIN\n END OF DATA FOR SDS OR MEMBER\n'
            '            PAGE 0001\n'
            'MEMBER NAME  BCPLTIME\n' + '\n'.join(data[:4]) + '\n'
            '            PAGE 0002\n'
            'MEMBER NAME  BCPLQSAM\n' + '\n'.join(data[4:]) + '\n'
            '     TTTTTTTTTT   AAAAAAAAAAAAA\n')


def new_evidence(directory: Path, report: str, *, job=9045, names=None,
                 jobname='TA0MULT', re_pin=True) -> None:
    names = names or ['BCPLTIME', 'BCPLQSAM']
    directory.mkdir()
    body = ('//* No JOB-card secrets here.\n'
            '//SYSUT1   DD DSN=HERC02.BCPL.EXT.OBJ,DISP=SHR\n'
            f'         PRINT TYPORG=PO,TOTCONV=XE,MAXNAME={len(names)}\n' +
            ''.join(f'         MEMBER NAME={name}\n' for name in names))
    sources = {
        'cursor.json': b'{"synthetic": true}\n',
        'job-body-redacted.jcl': body.encode('ascii'),
        'job-summary.txt': (f'JOB {job}  {jobname}\n'
                            'STEP PROGRAM RESULT\nTA0HEX    IEBPTPCH    RC=0000\n').encode(),
        'job-report.txt': report.encode('utf-8'),
        'printer-window.raw': report.encode('utf-8'),
    }
    for filename, payload in sources.items():
        (directory / filename).write_bytes(payload)
    receipt = {
        'phase': 'TA.0 MVS READBACK PILOT — NOT BINARY/RELEASE ACCEPTANCE',
        'job': job, 'jobname': jobname, 'step': 'TA0HEX',
        'source_dataset': 'HERC02.BCPL.EXT.OBJ', 'dataset_key': 'EXT_OBJ',
        'requested_members': names,
        'sha256': {name: hashlib.sha256(data).hexdigest() for name, data in sources.items()},
        'verification': 'IEBPTPCH RC=0000 and report captured; member bytes NOT decoded',
    }
    (directory / 'receipt.json').write_text(json.dumps(receipt) + '\n', encoding='utf-8')


def repin(directory: Path, name: str, payload: bytes) -> None:
    (directory / name).write_bytes(payload)
    file = directory / 'receipt.json'
    record = json.loads(file.read_text())
    record['sha256'][name] = hashlib.sha256(payload).hexdigest()
    file.write_text(json.dumps(record) + '\n')


class DecodeMulti(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.evidence = self.home / 'evidence'
        self.output = self.home / 'decoded'
        self.report = sample_report()
        new_evidence(self.evidence, self.report)

    def run_command(self, *extra):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            rc = mod.main(['--evidence-dir', str(self.evidence),
                           '--output-dir', str(self.output), *extra])
        return SimpleNamespace(returncode=rc, stdout=output.getvalue(),
                               stderr=errors.getvalue())

    def test_cli_smoke(self):
        cp = subprocess.run([sys.executable, '-B', str(SRC),
                             '--evidence-dir', str(self.evidence),
                             '--output-dir', str(self.output)],
                            capture_output=True, text=True, check=False)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn('JOB 9045', cp.stdout)

    def check_failure(self, expected):
        run = self.run_command()
        self.assertEqual(run.returncode, 1, run.stdout)
        self.assertIn(expected, run.stderr)
        self.assertFalse(self.output.exists())

    def test_success_two_members_and_pins(self):
        run = self.run_command()
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn('JOB 9045', run.stdout)
        self.assertIn('BCPLTIME', run.stdout)
        self.assertIn('BCPLQSAM', run.stdout)
        self.assertEqual((self.output / 'BCPLTIME.fb80').stat().st_size, 160)
        self.assertEqual((self.output / 'BCPLQSAM.fb80').stat().st_size, 80)
        meta = json.loads((self.output / 'decode-receipt.json').read_text())
        self.assertEqual([x['record_count'] for x in meta['members']], [2, 1])
        self.assertFalse(meta['members'][0]['expected_records_supplied'])
        self.assertEqual(meta['source_job'], 9045)
        self.assertEqual(meta['source_report_sha256'], hashlib.sha256(self.report.encode()).hexdigest())
        self.assertEqual(meta['source_receipt_sha256'], hashlib.sha256((self.evidence / 'receipt.json').read_bytes()).hexdigest())
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o700)
        for file in self.output.iterdir():
            self.assertEqual(file.stat().st_mode & 0o777, 0o600)
        self.assertEqual(len(list(self.output.iterdir())), 5)

    def test_validated_expected_counts(self):
        run = self.run_command('--expected-records', 'BCPLTIME:2',
                               '--expected-records', 'BCPLQSAM:1')
        self.assertEqual(run.returncode, 0, run.stderr)
        meta = json.loads((self.output / 'decode-receipt.json').read_text())
        self.assertTrue(all(x['expected_records_supplied'] for x in meta['members']))

    def test_wrong_expected_record_count_fails_before_output(self):
        run = self.run_command('--expected-records', 'BCPLTIME:3',
                               '--expected-records', 'BCPLQSAM:1')
        self.assertEqual(run.returncode, 1)
        self.assertIn('observed', run.stderr)
        self.assertFalse(self.output.exists())

    def test_partial_counts_fails(self):
        run = self.run_command('--expected-records', 'BCPLTIME:2')
        self.assertEqual(run.returncode, 1)
        self.assertIn('cover every', run.stderr)

    def test_invalid_expected_count_fails(self):
        run = self.run_command('--expected-records', 'BCPLTIME:-1',
                               '--expected-records', 'BCPLQSAM:1')
        self.assertEqual(run.returncode, 1)
        self.assertIn('invalid --expected-records', run.stderr)

    def test_duplicate_expected_count_fails(self):
        run = self.run_command('--expected-records', 'BCPLTIME:2',
                               '--expected-records', 'BCPLTIME:2',
                               '--expected-records', 'BCPLQSAM:1')
        self.assertEqual(run.returncode, 1)
        self.assertIn('invalid --expected-records', run.stderr)

    def test_wrong_receipt_pin_fails(self):
        (self.evidence / 'job-report.txt').write_text(self.report + 'TAMPERED\n')
        self.check_failure('evidence digest mismatch: job-report.txt')

    def test_wrong_raw_printer_pin_fails(self):
        (self.evidence / 'printer-window.raw').write_text('TAMPERED\n')
        self.check_failure('evidence digest mismatch: printer-window.raw')

    def test_wrong_summary_pin_fails(self):
        (self.evidence / 'job-summary.txt').write_text('TAMPERED\n')
        self.check_failure('evidence digest mismatch: job-summary.txt')

    def test_failed_step_after_pin_fails(self):
        changed = self.report.replace('RC= 0000', 'RC= 0012')
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.check_failure('IEBPTPCH TA0HEX RC=0000')

    def test_wrong_jes_job_fails(self):
        changed = self.report.replace('JOB 9045', 'JOB 9999')
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.check_failure('JES START identity')

    def test_missing_job_end_fails(self):
        changed = self.report.replace('$HASP395', '$HASP998')
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.check_failure('JES END identity')

    def test_duplicate_job_start_fails(self):
        changed = self.report.replace('13.25.35 JOB 9045  $HASP373 TA0MULT STARTED - INIT 1 - CLASS A\n',
                                      '13.25.35 JOB 9045  $HASP373 TA0MULT STARTED - INIT 1 - CLASS A\n'*2)
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.check_failure('duplicate JES START')

    def test_missing_ief142i_fails(self):
        changed = self.report.replace('IEF142I TA0MULT', 'IEF999I TA0MULT')
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.check_failure('IEF142I')

    def test_missing_member_header_fails(self):
        changed = self.report.replace('MEMBER NAME  BCPLQSAM', 'MEMBER N4ME  BCPLQSAM')
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.check_failure('printed member headers')

    def test_swapped_headers_fails(self):
        changed = self.report.replace('MEMBER NAME  BCPLTIME', 'MEMBER NAME  TEMP0001').replace(
            'MEMBER NAME  BCPLQSAM', 'MEMBER NAME  BCPLTIME').replace(
            'MEMBER NAME  TEMP0001', 'MEMBER NAME  BCPLQSAM')
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.check_failure('printed member headers')

    def test_duplicate_member_heading_fails(self):
        changed = self.report + 'MEMBER NAME  BCPLTIME\n'
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.check_failure('printed member headers')

    def test_print_control_order_fails(self):
        changed = self.report.replace('MEMBER NAME=BCPLTIME\n         MEMBER NAME=BCPLQSAM',
                                      'MEMBER NAME=BCPLQSAM\n         MEMBER NAME=BCPLTIME')
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.check_failure('control-member order')

    def test_wrong_maxname_fails(self):
        changed = self.report.replace('MAXNAME=2', 'MAXNAME=1')
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.check_failure('control statement mismatch')

    def test_no_first_binary_fails(self):
        changed = self.report.replace('02C5E2C4  40404040', 'ZZC5E2C4  40404040', 1)
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.check_failure('unexpected content in member body')

    def test_record_continuation_corrupt_fails(self):
        changed = self.report.replace('F0F0F0F1*', 'F0F0F0F1?', 1)
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.check_failure('invalid 32-byte')

    def test_missing_block_boundary_fails(self):
        changed = self.report.replace('F0F0F0F2**', 'F0F0F0F2*')
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.check_failure('no final FB block boundary')

    def test_early_block_boundary_does_not_terminate_member(self):
        changed = self.report.replace('F0F0F0F1*', 'F0F0F0F1**')
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.assertEqual(self.run_command().returncode, 0)
        meta = json.loads((self.output / 'decode-receipt.json').read_text())
        self.assertEqual(meta['members'][0]['block_end_records'], [1,2])

    def test_unexpected_text_between_members_fails(self):
        changed = self.report.replace('MEMBER NAME  BCPLQSAM', 'UNEXPECTED RECORD GAP\nMEMBER NAME  BCPLQSAM')
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.check_failure('unexpected content in member body')

    def test_page_title_between_records_ok(self):
        changed = self.report.replace('F0F0F0F1*\n02C5E2C4',
                                      'F0F0F0F1*\nPRINT/PUNCH DATA SET UTILITY         PAGE 0003\n02C5E2C4', 1)
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.assertEqual(self.run_command().returncode, 0)

    def test_page_inside_record_fails(self):
        changed = self.report.replace('F0F0F0F1*', 'PAGE 0003\nF0F0F0F1*', 1)
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.check_failure('invalid 32-byte')

    def test_unattached_second_line_fails(self):
        continuation = self.report.split('MEMBER NAME  BCPLQSAM\n', 1)[1].splitlines()[1]
        changed = self.report.replace('MEMBER NAME  BCPLQSAM\n',
                                      'MEMBER NAME  BCPLQSAM\n' + continuation + '\n')
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.assertEqual(self.run_command().returncode, 1)

    def test_duplicate_binary_after_last_member_fails(self):
        second = self.report.split('MEMBER NAME  BCPLQSAM\n')[1].splitlines()[:2]
        changed = self.report + '\n'.join(second) + '\n'
        repin(self.evidence, 'job-report.txt', changed.encode())
        self.check_failure('additional binary data')

    def test_summary_claim_mismatch_after_repin_fails(self):
        repin(self.evidence, 'job-summary.txt', b'JOB 9045 TA0MULT\nTA0HEX IEBPTPCH RC=0008\n')
        self.check_failure('job-summary')

    def test_changed_jobbody_after_repin_fails(self):
        old = (self.evidence / 'job-body-redacted.jcl').read_text()
        repin(self.evidence, 'job-body-redacted.jcl', old.replace('MAXNAME=2', 'MAXNAME=3').encode())
        self.check_failure('member count')

    def test_rejects_already_existing_output(self):
        self.output.mkdir()
        self.assertEqual(self.run_command().returncode, 1)
        self.assertEqual(list(self.output.iterdir()), [])

    def test_refuse_inside_checkout(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            # this test creates a short-lived temp directory in isolated
            # harness checkout, never user working tree.
            run = subprocess.run([sys.executable, '-B', str(SRC),
                                  '--evidence-dir', str(self.evidence),
                                  '--output-dir', str(Path(folder) / 'result')],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            self.assertIn('outside Git checkout', run.stderr)

    def test_nonexistent_report_fails_without_output(self):
        (self.evidence / 'job-report.txt').unlink()
        self.check_failure('not a plain evidence file')

    def test_report_symlink_rejected(self):
        path = self.evidence / 'job-report.txt'
        path.unlink()
        path.symlink_to(self.evidence / 'printer-window.raw')
        self.check_failure('not a plain evidence file')

    def test_tampered_receipt_job_fails(self):
        p = self.evidence / 'receipt.json'
        receipt = json.loads(p.read_text())
        receipt['job'] = 9999
        p.write_text(json.dumps(receipt))
        self.check_failure('job-summary')


if __name__ == '__main__':
    unittest.main()
