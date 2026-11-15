#!/usr/bin/env python3
"""Host-only source/oracle/harness tests for CO.4 inspection batch."""
from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT/'tools/coroutines/run-co4-inspection-batch.py'
spec = importlib.util.spec_from_file_location('co4inspection', SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError('test target unavailable')
co4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(co4)


class OfflineSourceTests(unittest.TestCase):
    def test_exact_case_order_and_lengths(self):
        self.assertEqual(tuple(co4.CASES), ('limits', 'account', 'deny'))
        self.assertEqual(tuple(len(x[2]) for x in co4.CASES.values()),
                         (12, 8, 12))

    def test_all_sources_validate(self):
        for key in co4.CASES:
            with self.subTest(case=key):
                value = co4.validate_case(key)
                self.assertEqual(value['oracle_count'], len(co4.CASES[key][2]))
                self.assertEqual(len(value['sha256']), 64)

    def test_extension_is_separate_read_only_ifox(self):
        value = co4.validate_extension()
        self.assertEqual(value['file'], 'co4probe.inc')
        self.assertEqual(len(value['sha256']), 64)

    def test_records_strict(self):
        for key, (_, prefix, expected) in co4.CASES.items():
            with self.subTest(case=key):
                report = 'noise\n'+'\n'.join(prefix+' '+v for v in expected)
                self.assertEqual(co4.parse_records(report, prefix),
                                 list(expected))

    def test_reject_malformed_records(self):
        for _, prefix, _ in co4.CASES.values():
            for record in (prefix, prefix+' EXTRA EXTRA', prefix+' BAD-1'):
                with self.subTest(record=record):
                    with self.assertRaisesRegex(co4.CandidateError, 'malformed'):
                        co4.parse_records(record, prefix)

    def test_no_unknown_case(self):
        with self.assertRaisesRegex(co4.CandidateError, 'unknown'):
            co4.validate_case('not-a-case')

    def test_source_oracle_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            dst = root/co4.FIXTURE.relative_to(co4.ROOT)
            dst.mkdir(parents=True)
            for key, (file, _, expected) in co4.CASES.items():
                source = (co4.FIXTURE/file).read_text('ascii')
                (dst/file).write_text(source.replace(
                    f'MARK("{expected[-1]}")', 'MARK("UNEXPECTED")'))
                with self.subTest(key=key):
                    with self.assertRaisesRegex(co4.CandidateError, 'oracle'):
                        co4.validate_case(key, root)

    def test_refusal_overrides_balanced(self):
        src = (co4.FIXTURE/'deny-source.bcpl').read_text('ascii')
        self.assertEqual(src.count('GETVEC:=DENY'), 2)
        self.assertEqual(src.count('GETVEC:=SAVEDGET'), 2)
        self.assertIn('RESULTIS SAVEDGET(N)', src)
        self.assertIn('IF REQUESTS=FAILAT RESULTIS 0', src)

    def test_mutated_refusal_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            dst = root/co4.FIXTURE.relative_to(co4.ROOT)
            dst.mkdir(parents=True)
            text = (co4.FIXTURE/'deny-source.bcpl').read_text('ascii')
            (dst/'deny-source.bcpl').write_text(text.replace(
                'GETVEC:=SAVEDGET', 'GETVEC:=DENY', 1))
            with self.assertRaisesRegex(co4.CandidateError, 'override/restore'):
                co4.validate_case('deny', root)

    def test_modified_assembler_mvs_services_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            dst = root/co4.EXTENSION.relative_to(co4.ROOT)
            dst.parent.mkdir(parents=True)
            dst.write_text(co4.EXTENSION.read_text('ascii')+
                           '         GETMAIN R,LV=(4),A=(1)\n')
            with self.assertRaisesRegex(co4.CandidateError, 'observer must not'):
                co4.validate_extension(root)


    def test_original_probe_missing_r10_restore_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root/co4.EXTENSION.relative_to(co4.ROOT)
            path.parent.mkdir(parents=True)
            data = co4.EXTENSION.read_text('ascii')
            restore = '         LR    10,4          RESTORE BASE BEFORE BRANCH/LITERALS\n'
            self.assertIn(restore, data)
            path.write_text(data.replace(restore, ''), encoding='ascii')
            with self.assertRaisesRegex(co4.CandidateError, 'restore R10 base'):
                co4.validate_extension(root)

    def test_memstat_restore_after_branch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root/co4.EXTENSION.relative_to(co4.ROOT)
            path.parent.mkdir(parents=True)
            data = co4.EXTENSION.read_text('ascii')
            restore = '         LR    10,4          RESTORE BASE BEFORE BRANCH/LITERALS\n'
            self.assertIn(restore, data)
            data = data.replace(restore, '').replace(
                '         B     C4PRET\n',
                '         B     C4PRET\n'+restore)
            path.write_text(data, encoding='ascii')
            with self.assertRaisesRegex(co4.CandidateError, 'restore R10 base'):
                co4.validate_extension(root)


class NativeBindingTests(unittest.TestCase):
    # Synthetic CG370 trailer and BCPLCO anchor based on the accepted
    # interface; this is structural host validation, not native IFOX.
    class FakeCO2:
        @staticmethod
        def checked_cards(data, description):
            rows=data.splitlines()
            if any(len(r)>71 or not r.isascii() for r in rows):
                raise ValueError(description+' invalid cards')
            return rows

    class FakeDriver:
        co2=None

        @staticmethod
        def trailer(rows):
            import re
            last=rows.index('L998 EQU *')
            start=rows.index("         DC F'1200'")
            maximum=int(rows[start].split("'")[1])
            pairs=[]
            for i in range(start+2,last,2):
                slot=int(rows[i].split("'")[1])
                alias=rows[i+1].split('(')[1].split(')')[0]
                pairs.append((slot,alias))
            return start,last,maximum,pairs

    @classmethod
    def setUpClass(cls):
        cls.baseline=cls.FakeDriver()
        cls.baseline.co2=cls.FakeCO2()

    def test_bridge_two_additions_in_private_stream(self):
        before = ('BCPLCO   CSECT\n'
                  '         ENTRY CO2INIT,CHANGECO\n'
                  '         EXTRN STKLIM,APLIMIT\n'
                  '         DS    0F\nROOTPTR  DC    F\'0\'\n'
                  '         END   BCPLCO\n')
        extension = co4.EXTENSION.read_text('ascii')
        patched = co4.patch_bridge(before, extension)
        self.assertEqual(patched.count('         ENTRY CO4PROB'), 1)
        self.assertEqual(patched.count('         EXTRN MEMSTAT'), 1)
        self.assertEqual(patched.count('CO4PROB  STM'), 1)
        self.assertEqual(patched.count('         END   BCPLCO'), 1)
        self.assertEqual(before.count('CO4PROB'),0)
        for i,row in enumerate(patched.splitlines(),1):
            self.assertTrue(row.isascii(),i)
            self.assertLessEqual(len(row),71,(i,row))

    def test_bridge_refuses_drift(self):
        with self.assertRaisesRegex(co4.CandidateError, 'anchors'):
            co4.patch_bridge('wrong data',co4.EXTENSION.read_text())

    def test_generated_global_trailer_binding(self):
        code = ['CO3APP   CSECT', '         EXTRN CO3DROP',
                "         DC F'1200'", "         DC F'0'",
                "         DC F'1200'", '         DC A(CO3DROP)',
                'L998 EQU *', '         END   CO3APP']
        after=co4.patch_application(code,self.baseline)
        self.assertIn("         DC F'1204'",after)
        self.assertIn('         DC A(CO4PROB)',after)
        self.assertEqual(after.count('         EXTRN CO4PROB'),1)
        self.assertIn('         DC A(CO3DROP)',after)

    def test_g301_collision_rejected(self):
        class CollisionDriver(self.FakeDriver):
            @staticmethod
            def trailer(rows):
                return 2,8,1204,[(1204,'EXISTING')]
        d=CollisionDriver()
        d.co2=self.FakeCO2()
        code=['CO3APP   CSECT','         EXTRN CO3DROP',
              "         DC F'1204'", "         DC F'0'",
              "         DC F'1204'", '         DC A(EXISTING)',
              'L998 EQU *', '         END   CO3APP']
        with self.assertRaisesRegex(co4.CandidateError,'G301'):
            co4.patch_application(code,d)

    def test_no_jcl_submission_during_validation(self):
        with mock.patch.object(co4,'run_batch',side_effect=AssertionError(
                'host validation invoked JES')):
            result=co4.validate_inputs()
            self.assertEqual(len(result['cases']),3)
            self.assertEqual(len(result['accepted_co3']['co4_source_sha256']),64)


class RawPrinterDecoderTests(unittest.TestCase):
    def test_non_utf8_printer_bytes_preserve_report_text(self):
        # This is synthetic local process output, not MVS or JES evidence.
        class Driver:
            REPORT=Path(sys.executable)
            ROOT=Path(__file__).resolve().parents[2]
            class co2:
                @staticmethod
                def shell(cmd, *, timeout=240):
                    raise AssertionError('raw report must bypass UTF-8 shell')
        driver=Driver()
        co4.configure_report_decoder(driver)
        code = ("import os; os.write(1, "
                "b'CO4LIM PASS\\n\\xd7\\n')")
        result=driver.co2.shell([sys.executable, '-c', code],timeout=15)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, 'CO4LIM PASS\n\u00d7\n')
        self.assertEqual(co4.parse_records(result.stdout, 'CO4LIM'), ['PASS'])

    def test_other_commands_delegate_to_accepted_shell(self):
        calls=[]
        class Driver:
            REPORT=Path('/fake/raw-printer-report')
            ROOT=Path('/fake/root')
            class co2:
                @staticmethod
                def shell(cmd, *, timeout=240):
                    calls.append((cmd,timeout))
                    return 'delegate-result'
        driver=Driver()
        co4.configure_report_decoder(driver)
        self.assertEqual(driver.co2.shell(['git','rev-parse','HEAD'],timeout=15),
                         'delegate-result')
        self.assertEqual(calls,[(['git','rev-parse','HEAD'],15)])

    def test_only_raw_printer_subprocess_has_latin1(self):
        class Driver:
            REPORT=Path('/fake/dump-report-for-job')
            ROOT=Path('/fake/root')
            class co2:
                @staticmethod
                def shell(cmd, *, timeout=240):
                    raise AssertionError('generic shell path forbidden')
        driver=Driver()
        co4.configure_report_decoder(driver)
        with mock.patch.object(co4.subprocess,'run',return_value='receipt') as run:
            self.assertEqual(driver.co2.shell([str(driver.REPORT),'42'],timeout=9),
                             'receipt')
        run.assert_called_once_with([str(driver.REPORT),'42'],
                                    cwd=driver.ROOT,text=True,
                                    encoding='latin-1',capture_output=True,
                                    check=False,timeout=9)


class NativeReportDiagnosticTests(unittest.TestCase):
    def test_abend_s0c1_report_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p/'job-summary.log').write_text(
                'JOB 5419  CO3BGO\nASMA IFOX00 RC=0000\n'
                'LKED IEWL RC=0000\nJOB RESULT: FAILURE\n'
                'HIGHEST RC: 0000\nABEND: detected\n')
            (p/'job-report.log').write_text(
                '4.13.31 JOB 5419 IEF450I CO3BGO GO - ABEND S0C1 U0000\n'
                'PSW AT ENTRY TO ABEND 078D0000 000A9828\n')
            result = co4.native_failure_detail(p)
            self.assertIn('JES ABEND', result)
            self.assertIn('S0C1', result)
            self.assertIn('000A9828', result)
            self.assertLessEqual(len(result), 280)

    def test_nonzero_ifox_step_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p/'job-summary.log').write_text(
                'ASMS IFOX00 RC=0012\nJOB RESULT: FAILURE\n')
            self.assertIn('ASMS RC=0012', co4.native_failure_detail(p))

    def test_success_summary_has_no_failure_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p/'job-summary.log').write_text(
                'ASMS IFOX00 RC=0000\nJOB RESULT: SUCCESS\n')
            self.assertIsNone(co4.native_failure_detail(p))


class BatchReceiptTests(unittest.TestCase):
    def test_host_synthetic_all_success(self):
        with tempfile.TemporaryDirectory() as t:
            work=Path(t)
            def fake(key, session, previous, hashes):
                return {'status':'PASS','case':key,'rc':0,'reason':None}
            with (mock.patch.object(co4,'WORK',work),
                  mock.patch.object(co4,'validate_inputs',return_value={'cases':{}}),
                  mock.patch.object(co4,'load_module',return_value=object()),
                  mock.patch.object(co4,'run_one',side_effect=fake),
                  redirect_stdout(io.StringIO())):
                self.assertEqual(co4.run_batch(),0)
            receipts=list(work.glob('*/batch-result.json'))
            self.assertEqual(len(receipts),1)
            data=json.loads(receipts[0].read_text())
            self.assertEqual(data['status'],'PASS')
            self.assertEqual([c['case'] for c in data['cases']],
                             ['limits','account','deny'])

    def test_host_synthetic_fail_fast_preserves_two_receipts(self):
        with tempfile.TemporaryDirectory() as t:
            work=Path(t)
            called=[]
            def fake(key, session, previous, hashes):
                called.append(key)
                return {'status':'FAIL' if key=='account' else 'PASS',
                        'case':key,'rc':1 if key=='account' else 0,
                        'reason':'FAKE-NOT-MVS'}
            with (mock.patch.object(co4,'WORK',work),
                  mock.patch.object(co4,'validate_inputs',return_value={'cases':{}}),
                  mock.patch.object(co4,'load_module',return_value=object()),
                  mock.patch.object(co4,'run_one',side_effect=fake),
                  redirect_stdout(io.StringIO())):
                self.assertEqual(co4.run_batch(),1)
            self.assertEqual(called,['limits','account'])
            receipt=json.loads(next(work.glob('*/batch-result.json')).read_text())
            self.assertEqual(receipt['status'],'FAIL')
            self.assertEqual(len(receipt['cases']),2)
            self.assertEqual(receipt['reason'],'account: FAKE-NOT-MVS')


if __name__ == '__main__':
    unittest.main()
