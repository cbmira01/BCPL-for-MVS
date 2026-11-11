"""Host-only test doubles for the 11 unaccepted MR10 development probes."""
from __future__ import annotations

import sys
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'mr10'))
import dev_probe_extras as ex


class ExtrasTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.asm = self.file('mr10-kit-compiler/asm/icintv19.asm')
        for n in (12, 13, 14):
            self.file(f'mr10-kit-compiler/asm/icintv{n}.asm')
        for engine in ('run-intcode', 'compile-and-run'):
            self.file(f'tools/mr10/{engine}')
        self.artifacts = self.root / 'workarea/evidence/probe'
        self.artifacts.mkdir(parents=True)

    def file(self, path, content='fixture\n'):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='ascii')
        return p

    def row(self, ident, *, engine='compile-and-run', interpreter='current',
            artifacts='none', modules='', sysin='', dd_bindings='', code='0'):
        return dict(case_id=ident, engine=engine, interpreter=interpreter,
                    verification='UNVERIFIED', source='mr10-kit-compiler/tests/test.bcpl',
                    modules=modules, sysin=sysin, dd_bindings=dd_bindings,
                    expected_code=code, artifacts=artifacts)

    def output(self, lines, code='0'):
        return ('JOB 9000\n INTCODE SYSTEM ENTERED\n PROGRAM SIZE = 42\n'
                + '\n'.join(' ' + line for line in lines)
                + f'\n EXECUTION CYCLES = 100, CODE = {code}\n')

    def test_expected_identity_set_is_11_distinct(self):
        self.assertEqual(len(ex.ADDITIONAL), 11)
        self.assertEqual(len(set(ex.ADDITIONAL)), 11)
        self.assertEqual(len(ex.TRACE), 5)

    def test_pinned_interpreter_must_exist(self):
        for version in ('v12', 'v13', 'v14'):
            p = ex.interpreter(self.root, self.asm, self.row(ex.ADDITIONAL[0], interpreter=version))
            self.assertEqual(p.name, f'icint{version}.asm')
        with self.assertRaises(ex.ExtraError):
            ex.interpreter(self.root, self.asm, self.row(ex.ADDITIONAL[0], interpreter='v16'))

    def test_historical_intcode_and_runtime_modules(self):
        row = self.row('03-compile-richards-factorial/v14-intcode',
                       engine='run-intcode', interpreter='v14',
                       modules='mr10-kit-compiler/source/blibi.int;mr10-kit-compiler/source/iclib.int')
        cmd = ex.command(self.root, row, self.asm, self.artifacts / 'test.jcl', 'DP000001', self.artifacts)
        self.assertIn('icintv14.asm', ' '.join(cmd))
        self.assertEqual(sum('+.int' in arg for arg in cmd), 0)
        self.assertIn('+' + str(self.root / 'mr10-kit-compiler/source/blibi.int'), cmd)
        self.assertNotIn('--save-intcode', cmd)

    def test_echo_sysin_is_passed_to_run_intcode(self):
        row = self.row('01-echo-test', engine='run-intcode',
                       sysin='mr10-kit-compiler/tests/01-echo-test/best-of-times.txt')
        cmd = ex.command(self.root, row, self.asm, self.artifacts / 'test.jcl', 'DP000001', self.artifacts)
        self.assertIn('--sysin', cmd)
        self.assertIn(str(self.root / row['sysin']), cmd)

    def test_compiler_artifacts_have_scoped_directory(self):
        row = self.row('08-character-translation', artifacts='ocode,intcode',
                       dd_bindings='PUNCT=mr10-kit-compiler/tests/08-character-translation/punct.txt')
        cmd = ex.command(self.root, row, self.asm, self.artifacts / 'test.jcl', 'DP000001', self.artifacts)
        self.assertEqual(cmd[cmd.index('--artifact-dir')+1], str(self.artifacts))
        self.assertIn('--save-ocode', cmd)
        self.assertIn('--save-intcode', cmd)
        self.assertEqual(cmd[cmd.index('--dd')+1],
                         'PUNCT=' + str(self.root / 'mr10-kit-compiler/tests/08-character-translation/punct.txt'))

    def test_missing_engine_rejected(self):
        (self.root / 'tools/mr10/run-intcode').unlink()
        with self.assertRaises(ex.ExtraError):
            ex.command(self.root, self.row('01-echo-test', engine='run-intcode'),
                       self.asm, self.artifacts/'t.jcl', 'DP001111', self.artifacts)

    def test_accepted_case_not_sent_to_experimental_runner(self):
        with self.assertRaises(ex.ExtraError):
            ex.command(self.root, self.row('05-named-dd'), self.asm,
                       self.artifacts/'t.jcl', 'DP001111', self.artifacts)

    def test_accepted_coroutine_command_requires_exact_golden(self):
        ident = "10-coroutines/resumeco-chain"
        row = self.row(ident)
        row["verification"] = "ACCEPTED"
        row["oracle"] = "file:mr10-kit-compiler/tests/10-coroutines/resumeco-chain.expected"
        command = ex.command(self.root, row, self.asm,
                             self.artifacts/"t.jcl", "DP001111", self.artifacts)
        self.assertIn(str(self.root / "mr10-kit-compiler/tests/test.bcpl"), command)
        row["verification"] = "UNVERIFIED"
        with self.assertRaisesRegex(ex.ExtraError, "accepted coroutine golden"):
            ex.command(self.root, row, self.asm, self.artifacts/"t.jcl",
                       "DP001111", self.artifacts)

    def test_exact_synthetic_factorials(self):
        row = self.row('03-compile-richards-factorial/v14-intcode', engine='run-intcode', interpreter='v14')
        lines = [f'F({i}), = {value}' for i, value in enumerate(ex.FACTORIAL, 1)]
        self.assertEqual(ex.assess(self.root, row, self.output(lines), 0, self.artifacts)['status'], 'OBSERVED')
        with self.assertRaises(ex.ExtraError):
            ex.assess(self.root, row, self.output(lines[:-1]), 0, self.artifacts)

    def test_honors_thesis_format(self):
        row = self.row('02-honors-thesis-and-mapstore/honors-thesis', engine='run-intcode', interpreter='v12')
        lines = [f'F({i}) = {value}' for i, value in enumerate(ex.FACTORIAL, 1)]
        self.assertEqual(ex.assess(self.root, row, self.output(lines), 0, self.artifacts)['status'], 'OBSERVED')

    def test_negative_diagnostic_must_have_code_and_mapstore(self):
        row = self.row('02-honors-thesis-and-mapstore/mapstore', engine='run-intcode', interpreter='v13', code='-1')
        self.assertEqual(ex.assess(self.root, row, self.output(['X38 ERROR', 'BEGIN MAPSTORE'], '-1'), 0, self.artifacts)['status'], 'OBSERVED')
        with self.assertRaises(ex.ExtraError):
            ex.assess(self.root, row, self.output(['X38 ERROR'], '-1'), 0, self.artifacts)
        with self.assertRaises(ex.ExtraError):
            ex.assess(self.root, row, self.output(['X38 ERROR', 'BEGIN MAPSTORE'], '0'), 0, self.artifacts)

    def test_echo_exact_input(self):
        p = self.file('mr10-kit-compiler/tests/01-echo-test/best-of-times.txt', 'ONE\nTWO\n')
        row = self.row('01-echo-test', engine='run-intcode', sysin=str(p.relative_to(self.root)))
        self.assertEqual(ex.assess(self.root, row, self.output(['ONE', 'TWO']), 0, self.artifacts)['status'], 'OBSERVED')
        with self.assertRaises(ex.ExtraError):
            ex.assess(self.root, row, self.output(['ONE', 'THREE']), 0, self.artifacts)

    def test_coroutine_trace_exact(self):
        for ident, trace in ex.TRACE.items():
            with self.subTest(ident=ident):
                row = self.row(ident)
                self.assertEqual(ex.assess(self.root, row, self.output(trace), 0, self.artifacts)['status'], 'OBSERVED')
                with self.assertRaises(ex.ExtraError):
                    ex.assess(self.root, row, self.output(trace[:-1]), 0, self.artifacts)

    def test_coroutine_structural_artifacts_compare_historical(self):
        for name in ('compiler-probe','frame-layout-probe'):
            ident = f'10-coroutines/{name}'
            row = self.row(ident, artifacts='ocode,intcode')
            row['source'] = f'mr10-kit-compiler/tests/10-coroutines/{name}.bcpl'
            for ext, content in (('.ocode','STACK 2 GLOBAL 1'), ('.intcode','G1L5 Z')):
                self.file(f'mr10-kit-compiler/tests/10-coroutines/evidence/{name}{ext}', content+'\n')
                self.file(str((self.artifacts / (name+ext)).relative_to(self.root)), content+'\n')
            observed = ex.assess(self.root, row, self.output(ex.TRACE[ident]), 0, self.artifacts)
            self.assertEqual(observed['status'], 'OBSERVED')
            self.assertEqual(set(observed['artifacts']), {'ocode', 'intcode'})
            (self.artifacts / f'{name}.ocode').write_text('STACK 3 GLOBAL 1\n')
            with self.assertRaises(ex.ExtraError):
                ex.assess(self.root, row, self.output(ex.TRACE[ident]), 0, self.artifacts)

    def test_character_translation_requires_valid_records(self):
        row = self.row('08-character-translation')
        prefix = ['BACKSLASH OPERATORS', 'LOGICAL OR  = -1', 'LOGICAL AND = -1',
                  'NOT EQUAL   = -1', 'LOGICAL NOT = -1', 'RDCH CHARACTER CODES']
        good = self.output([*prefix, *[str(x) for x in range(9)]])
        self.assertEqual(ex.assess(self.root, row, good, 0, self.artifacts)['status'], 'OBSERVED')
        with self.assertRaises(ex.ExtraError):
            ex.assess(self.root, row, self.output([*prefix, '999']), 0, self.artifacts)

    def test_wrong_return_code_and_job_number_fail(self):
        row = self.row('10-coroutines/resumeco-chain')
        with self.assertRaises(ex.ExtraError):
            ex.assess(self.root, row, self.output(ex.TRACE[row['case_id']]), 2, self.artifacts)
        with self.assertRaises(ex.ExtraError):
            ex.assess(self.root, row, self.output(ex.TRACE[row['case_id']]).replace('JOB 9000', 'JOB 9000\nJOB 9001'), 0, self.artifacts)



    def fake_jes(self, row, *, wrong_name=False, missing_step=False, bad_code=False,
                 tool_failure=False):
        self.file('mvs-state/prt/prt00e.txt')
        self.file('tools/mvs/job-summary')
        self.file('tools/mvs/dump-report-for-job')
        expected_name = 'DP000001'
        if row['engine'] == 'run-intcode':
            names = ['ASM', 'LKED', 'GO']
            codes = [-1 if row['expected_code'] == '-1' else 0]
        else:
            n = 1 + (len(row['modules'].split(';')) if row['modules'] else 0)
            names = ['ASM', 'LKED', 'STGSYNI', 'STGTRNI', 'STGCGI',
                     'STGBLIB', 'STGICLIB']
            names += [f'COMP{i:02d}' for i in range(1,n+1)] if n > 1 else ['COMP']
            names += [f'CG{i:02d}' for i in range(1,n+1)] if n > 1 else ['CG']
            names += ['RUN']
            codes = [0]*(2*n+1)
        if missing_step:
            names = names[:-1]
        lines = [f'JOB 9000  {"BOGUS" if wrong_name else expected_name}',
                 'STEP       PROGRAM      RESULT']
        lines.extend(f'{name:<10} {"RUNMOD":<12} RC=0000' for name in names)
        lines.extend(['JOB RESULT: SUCCESS', 'HIGHEST RC: 0000'])
        if bad_code:
            codes = codes[:-1]
        report = ''.join(f' EXECUTION CYCLES = {i+100}, CODE = {code}\n'
                         for i, code in enumerate(codes))
        calls = [SimpleNamespace(returncode=1 if tool_failure else 0,
                                 stdout='\n'.join(lines)+'\n', stderr=''),
                 SimpleNamespace(returncode=0, stdout=report, stderr='')]
        with patch.object(ex.subprocess, 'run', side_effect=calls):
            return ex.capture_jes(self.root, row, '9000', expected_name, self.artifacts, 'case')

    def test_jes_capture_checks_compiler_pipeline(self):
        row = self.row('10-coroutines/create-delete-static-pool',
                       modules='mr10-kit-compiler/library/allocator.bcpl;mr10-kit-compiler/library/coroutines.bcpl')
        result = self.fake_jes(row)
        self.assertEqual(result['jes_phase_codes'], [0]*7)
        self.assertEqual(len(result['jes_step_codes']), 14)
        self.assertTrue((self.artifacts/'case-jes-report.txt').is_file())

    def test_jes_capture_negative_interpreter_code(self):
        row = self.row('02-honors-thesis-and-mapstore/mapstore',
                       engine='run-intcode', interpreter='v13', code='-1')
        result = self.fake_jes(row)
        self.assertEqual(result['jes_phase_codes'], [-1])

    def test_jes_capture_refuses_wrong_identity(self):
        row = self.row('01-echo-test', engine='run-intcode')
        with self.assertRaisesRegex(ex.ExtraError, 'identity mismatch'):
            self.fake_jes(row, wrong_name=True)

    def test_jes_capture_refuses_missing_step(self):
        row = self.row('01-echo-test', engine='run-intcode')
        with self.assertRaisesRegex(ex.ExtraError, 'step structure missing'):
            self.fake_jes(row, missing_step=True)

    def test_jes_capture_refuses_bad_phase_count(self):
        row = self.row('10-coroutines/create-delete-static-pool')
        with self.assertRaisesRegex(ex.ExtraError, 'interpreted phase codes'):
            self.fake_jes(row, bad_code=True)

    def test_jes_capture_refuses_tool_error(self):
        row = self.row('01-echo-test', engine='run-intcode')
        with self.assertRaisesRegex(ex.ExtraError, 'report utilities failed'):
            self.fake_jes(row, tool_failure=True)


if __name__ == '__main__':
    unittest.main()
