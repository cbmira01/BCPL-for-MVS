"""Host-only CO.6 supported MR10 selection / strict evidence tests."""
from __future__ import annotations

import contextlib
import importlib.util
from importlib.machinery import SourceFileLoader
import io
import json
from pathlib import Path
import re
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'mr10/run-supported-coroutines.py'
SPEC = importlib.util.spec_from_loader('co6_supported', SourceFileLoader('co6_supported', str(SCRIPT)))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError('cannot load supported coroutine runner')
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
BASE = Path(__file__).resolve().parents[2]
STEPS = (
    ('ASM','IFOX00'), ('LKED','IEWL'),
    ('STGSYNI','IEBGENER'), ('STGTRNI','IEBGENER'),
    ('STGCGI','IEBGENER'), ('STGBLIB','IEBGENER'),
    ('STGICLIB','IEBGENER'), ('COMP','RUNMOD'),
    ('CG','RUNMOD'), ('RUN','RUNMOD'),
)


class SupportedHostTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='co6-supported-test-')
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.root = root
        for name, path in {
            'ROOT': root,
            'MANIFEST': root / 'mr10-kit-compiler/tests/10-coroutines/supported-manifest.tsv',
            'CANDIDATE': root / 'mr10-kit-compiler/tests/10-coroutines/fixed-stack-co0-candidate.bcpl',
            'GOLDEN': root / 'mr10-kit-compiler/tests/10-coroutines/fixed-stack-co0-candidate.expected',
            'HISTORICAL': root / 'mr10-kit-compiler/tests/10-coroutines/fixed-stack-producer-consumer.bcpl',
            'HISTORICAL_GOLDEN': root / 'mr10-kit-compiler/tests/10-coroutines/fixed-stack-producer-consumer.expected',
            'PROBES': root / 'tools/mr10/run-dev-probes',
            'COMPILE': root / 'tools/mr10/compile-and-run',
            'WORK': root / 'workarea/mr10-supported-coroutines',
        }.items():
            patcher = patch.object(MOD, name, path)
            patcher.start()
            self.addCleanup(patcher.stop)
        folder = BASE / 'mr10-kit-compiler/tests/10-coroutines'
        for name in ('supported-manifest.tsv', 'fixed-stack-co0-candidate.bcpl',
                     'fixed-stack-producer-consumer.bcpl', 'fixed-stack-producer-consumer.expected',
                     'fixed-stack-co0-candidate.expected'):
            target = root / 'mr10-kit-compiler/tests/10-coroutines' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(folder / name, target)
        for ident in MOD.ACCEPTED:
            name = ident.split('/')[-1]
            for ext in ('.bcpl', '.expected'):
                (root / 'mr10-kit-compiler/tests/10-coroutines' / (name + ext)).write_text('fixture\n')
        (root / 'tools/mr10').mkdir(parents=True)
        for name in ('run-dev-probes', 'compile-and-run'):
            (root / 'tools/mr10' / name).write_text('synthetic host executable\n')
        (root / 'mr10-kit-compiler/asm').mkdir(parents=True)
        (root / 'mr10-kit-compiler/asm/CURRENT').write_text('icintv19.asm\n')
        (root / 'mr10-kit-compiler/asm/icintv19.asm').write_text('MVS source fixture\n')
        self.job = '8124'
        self.accepted_statuses = ['PASS'] * 4
        self.bad_code = None
        self.extra_record = False
        self.recpt = None
        self.fake = SimpleNamespace(
            JOB_RE=re.compile(r'(?m)^JOB\s+(\d+)\s*$'),
            CODE_RE=re.compile(r'EXECUTION CYCLES\s*=\s*\d+,\s*CODE\s*=\s*(-?\d+)'),
            EXTRAS=SimpleNamespace(TRACE={MOD.OLD_ID: MOD.GOLDEN_LINES}),
            EXPECTED_STEPS=STEPS,
            git_head=lambda: 'a' * 40,
            manifest_cases=lambda: [
                {'case_id': ident, 'verification': 'ACCEPTED'}
                for ident in (*MOD.ACCEPTED, MOD.OLD_ID)],
            current_interpreter=lambda: root / 'mr10-kit-compiler/asm/icintv19.asm',
            expected_jes_steps=self.expected_steps,
            verify_accepted_output=self.verify_output,
            verify_jes_steps=self.verify_jes,
            verify_jes_output_records=self.verify_jes_output,
        )
        patcher = patch.object(MOD, 'load_probes', return_value=self.fake)
        patcher.start()
        self.addCleanup(patcher.stop)
        patcher = patch.object(MOD, 'run_host', side_effect=self.fake_run)
        patcher.start()
        self.addCleanup(patcher.stop)

    def expected_steps(self, ident):
        if ident in MOD.ACCEPTED[-2:]:
            return [*STEPS[:7],
                    *(item for i in range(1,4)
                      for item in ((f'COMP{i:02d}', 'RUNMOD'), (f'CG{i:02d}', 'RUNMOD'))),
                    STEPS[-1]]
        return list(STEPS)

    def verify_output(self, text, golden):
        begin = text.index('INTCODE SYSTEM ENTERED')
        end = text.index('EXECUTION CYCLES = ', begin)
        actual = [x for x in text[begin + len('INTCODE SYSTEM ENTERED'):end].strip().splitlines() if x]
        if actual != golden.read_text('ascii').splitlines():
            raise MOD.SupportedError('golden output mismatch')

    def verify_jes_output(self, lines, expected):
        ordered = [line for line in lines if line.startswith(('PRODUCER:', 'CONSUMER:'))]
        if ordered != list(expected):
            raise MOD.SupportedError('wrong JES records')

    def verify_jes(self, job, name, folder, ident):
        self.assertEqual(ident, MOD.OLD_ID)
        self.assertEqual((job, name), (self.job, 'CO6VALID'))
        path = folder / f"{MOD.OLD_ID.replace('/','--')}-jes-report.txt"
        path.write_text('\n'.join(MOD.GOLDEN_LINES) + '\n')
        return {'jes_step_codes': [dict(step=s, program=p, rc=0) for s,p in STEPS],
                'jes_phase_codes': [0,0,0],
                'jes_summary': str((folder / 'synthetic-jes-summary.txt').relative_to(self.root)),
                'jes_report': str(path.relative_to(self.root))}

    def fake_run(self, command, logfile):
        if logfile.name == 'four-accepted.log':
            evidence = self.root / 'workarea/mr10-probes' / 'accepted'
            evidence.mkdir(parents=True)
            logfile.write_text(f'MR10 PROBE EVIDENCE: {evidence}\n')
            rows = []
            for ident,status in zip(MOD.ACCEPTED, self.accepted_statuses):
                steps = self.expected_steps(ident)
                rows.append({'id':ident,'status':status,'verification':'ACCEPTED',
                             'runner_rc': 0 if status=='PASS' else 1,
                             'interpreted_code': 0 if status=='PASS' else -1,
                             'jes_job_id': self.job,
                             'jes_step_codes': [dict(step=s, program=p, rc=0) for s,p in steps] if status=='PASS' else [],
                             'jes_phase_codes':[0]*(1+2*sum(s.startswith('COMP') for s,p in steps)) if status=='PASS' else []})
            counts={x: self.accepted_statuses.count(x)
                    for x in ('PASS','FAIL','OBSERVED','NOT_RUN')}
            state='FAIL' if counts['FAIL'] else 'PASS'
            (evidence / 'summary.json').write_text(json.dumps({
                'suite':'mr10-probes', 'selected_cases':list(MOD.ACCEPTED),
                'continue_known_fixed_stack_failure':False,
                'cases':rows,'counts':counts,'status':state}))
            return 1 if state=='FAIL' else 0
        self.assertEqual(logfile.name,'fixed-frame.log')
        output = ['JOB '+self.job,'INTCODE SYSTEM ENTERED', *MOD.GOLDEN_LINES]
        if self.extra_record:
            output.append('EXTRA USER OUTPUT')
        output.append('EXECUTION CYCLES = 99, CODE = '+str(self.bad_code if self.bad_code is not None else 0))
        logfile.write_text('\n'.join(output)+'\n')
        return 0

    def test_successful_host_preflight(self):
        self.assertEqual(MOD.validate(), MOD.FIXED_BLOBS)

    def test_production_original_and_corrected_source_exact_hashes(self):
        self.assertEqual(MOD.blob(MOD.CANDIDATE), MOD.FIXED_BLOBS['candidate'])
        self.assertEqual(MOD.blob(MOD.HISTORICAL), MOD.FIXED_BLOBS['original'])
        self.assertNotEqual(MOD.blob(MOD.CANDIDATE), MOD.blob(MOD.HISTORICAL))

    def test_manifest_reorder_fails_preflight(self):
        text = MOD.MANIFEST.read_text()
        lines = text.splitlines()
        lines[1], lines[2] = lines[2], lines[1]
        MOD.MANIFEST.write_text('\n'.join(lines)+'\n')
        with self.assertRaisesRegex(MOD.SupportedError, 'order changed'):
            MOD.validate()

    def test_candidate_source_tampering_fails_preflight(self):
        with MOD.CANDIDATE.open('a') as handle:
            handle.write('\n// tampered\n')
        with self.assertRaisesRegex(MOD.SupportedError, 'bytes changed'):
            MOD.validate()

    def test_original_source_tampering_fails_preflight(self):
        with MOD.HISTORICAL.open('a') as handle:
            handle.write('\n// tampered\n')
        with self.assertRaisesRegex(MOD.SupportedError, 'bytes changed'):
            MOD.validate()

    def test_noncanonical_interpreter_refused_before_mvs(self):
        self.fake.current_interpreter = lambda: self.root / 'mr10-kit-compiler/asm/icintv20.asm'
        with self.assertRaisesRegex(MOD.SupportedError, 'canonical ICINT19'):
            MOD.validate_baseline(self.fake)

    def test_golden_file_tampering_fails(self):
        MOD.GOLDEN.write_text('PRODUCER: 1\n')
        with self.assertRaisesRegex(MOD.SupportedError, 'golden changed'):
            MOD.validate()

    def test_missing_accepted_fixture_fails(self):
        (MOD.MANIFEST.parent / 'compiler-probe.bcpl').unlink()
        with self.assertRaisesRegex(MOD.SupportedError, 'missing/outside-repository'):
            MOD.validate()

    def test_supported_success_all_five_pass(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = MOD.execute()
        self.assertEqual(rc,0)
        self.assertEqual(stdout.getvalue().count('PASS    '), 5)
        self.assertNotIn(MOD.OLD_ID+':', stdout.getvalue())
        folder = next(MOD.WORK.iterdir())
        payload=json.loads((folder/'summary.json').read_text())
        self.assertEqual(payload['counts'], {'PASS':5,'FAIL':0,'NOT_RUN':0})
        result=MOD.verify_coordinator_result(stdout.getvalue(), 0)
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['counts']['TOTAL'],5)

    def test_supported_bad_code_fails_real_case(self):
        self.bad_code=-1
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc=MOD.execute()
        self.assertEqual(rc,1)
        folder=next(MOD.WORK.iterdir())
        summary=json.loads((folder/'summary.json').read_text())
        self.assertEqual([x['status'] for x in summary['cases']],['PASS']*4+['FAIL'])
        result=MOD.verify_coordinator_result(out.getvalue(),rc)
        self.assertEqual(result['status'],'FAIL')

    def test_supported_extra_program_output_fails(self):
        self.extra_record=True
        with contextlib.redirect_stdout(io.StringIO()):
            rc=MOD.execute()
        self.assertEqual(rc,1)

    def test_accepted_failure_does_not_run_fixed_case(self):
        self.accepted_statuses=['PASS','PASS','FAIL','NOT_RUN']
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc=MOD.execute()
        self.assertEqual(rc,1)
        folder=next(MOD.WORK.iterdir())
        summary=json.loads((folder/'summary.json').read_text())
        self.assertEqual([x['status'] for x in summary['cases']],['PASS','PASS','FAIL','NOT_RUN','NOT_RUN'])
        self.assertFalse((folder/'fixed-frame.log').exists())
        verified=MOD.verify_coordinator_result(out.getvalue(),rc)
        self.assertEqual(verified['counts']['FAIL'],1)

    def test_reported_status_cannot_disagree_with_rc(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            MOD.execute()
        with self.assertRaisesRegex(MOD.SupportedError, 'RC disagrees'):
            MOD.verify_coordinator_result(out.getvalue(),1)

    def test_coordinator_rejects_mutated_candidate_phase(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            MOD.execute()
        folder=next(MOD.WORK.iterdir())
        receipt=folder/'summary.json'
        payload=json.loads(receipt.read_text())
        payload['cases'][4]['jes_phase_codes']=[0,-1,0]
        receipt.write_text(json.dumps(payload))
        with self.assertRaisesRegex(MOD.SupportedError, 'JES/ICINT receipt'):
            MOD.verify_coordinator_result(out.getvalue(),0)

    def test_coordinator_rejects_mutated_accepted_job(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            MOD.execute()
        folder=next(MOD.WORK.iterdir())
        receipt=folder/'summary.json'
        payload=json.loads(receipt.read_text())
        payload['cases'][0]['jes_job_id']='OTHER'
        receipt.write_text(json.dumps(payload))
        with self.assertRaisesRegex(MOD.SupportedError, 'JES verification'):
            MOD.verify_coordinator_result(out.getvalue(),0)

    def test_coordinator_rejects_outside_evidence_path(self):
        with self.assertRaisesRegex(MOD.SupportedError, 'outside expected workarea'):
            MOD.verify_coordinator_result('MR10 SUPPORTED EVIDENCE: /tmp/fake\n',0)

    def test_coordinator_rejects_modified_jcl_report(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            MOD.execute()
        folder=next(MOD.WORK.iterdir())
        raw=folder/f"{MOD.OLD_ID.replace('/', '--')}-jes-report.txt"
        raw.write_text('PRODUCER: 99\n')
        with self.assertRaisesRegex(MOD.SupportedError, 'wrong JES records'):
            MOD.verify_coordinator_result(out.getvalue(),0)

    def test_cli_check_is_host_only(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc=MOD.main(['--check'])
        self.assertEqual(rc,0)
        self.assertIn('host-only',out.getvalue())
        self.assertFalse(MOD.WORK.exists())


if __name__ == '__main__':
    unittest.main()
