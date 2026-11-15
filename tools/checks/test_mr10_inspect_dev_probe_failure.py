"""Read-only MR10 receipt inspector tests; no JES execution."""
import importlib.util
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / 'mr10/inspect-dev-probe-failure'
SPEC = importlib.util.spec_from_loader('probe_inspector', SourceFileLoader('probe_inspector', str(SRC)))
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

class InspectorTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        patcher = patch.object(MOD, 'ROOT', self.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.project = self.root / 'workarea/project-regressions/run'
        self.probe = self.root / 'workarea/mr10-probes/probe'
        self.project.mkdir(parents=True)
        self.probe.mkdir(parents=True)
        (self.project / 'summary.json').write_text(json.dumps({'selected_suites':['mr10-probes'], 'git_head':'abc'}))
        (self.project / 'mr10-probes.log').write_text('MR10 PROBE EVIDENCE: '+str(self.probe)+'\n')
        self.record = self.probe / 'summary.json'
        self.record.write_text(json.dumps({'suite':'mr10-probes','cases':[{'id':MOD.CASE,'status':'FAIL','jes_job_id':'123', 'reason':'CODE=-1'}]}))
        self.raw = self.probe / '10-coroutines--fixed-stack-producer-consumer.log'
        self.raw.write_text('INTCODE SYSTEM ENTERED\nEXECUTION CYCLES = 2, CODE = 0\n'
                            'INTCODE SYSTEM ENTERED\nEXECUTION CYCLES = 3, CODE = 0\n'
                            'INTCODE SYSTEM ENTERED\nPRODUCER: 1\nINTCODE ERROR AT C = 99\n'
                            '*** ICINT RECENT INSTRUCTION TRACE ***\nC=99\n*** END ICINT TRACE ***\n'
                            'EXECUTION CYCLES = 4, CODE = -1\n')

    def test_phase_codes_and_trace(self):
        output = MOD.inspect(Path('run'))
        self.assertIn('INTERPRETED PHASE CODES: [0, 0, -1]', output)
        self.assertIn('INTCODE ERROR AT C = 99', output)
        self.assertIn('PRODUCER: 1', output)
        self.assertIn('STATUS: FAIL', output)

    def test_missing_trace_preserves_failure(self):
        self.raw.write_text('INTCODE SYSTEM ENTERED\nEXECUTION CYCLES = 3, CODE = -1\n')
        self.assertIn('INTERPRETER ERRORS:\n(none)', MOD.inspect(Path('run')))

    def test_rejects_non_project_directory(self):
        with self.assertRaises(ValueError):
            MOD.inspect(self.probe)

    def test_rejects_forged_path(self):
        (self.project / 'mr10-probes.log').write_text('MR10 PROBE EVIDENCE: /tmp/invalid\n')
        with self.assertRaises(ValueError):
            MOD.inspect(Path('run'))

    def test_rejects_non_fail_status(self):
        self.record.write_text(json.dumps({'suite':'mr10-probes', 'cases':[{'id':MOD.CASE,'status':'PASS'}]}))
        with self.assertRaises(ValueError):
            MOD.inspect(Path('run'))

    def test_bounded_trace_output(self):
        self.raw.write_text('INTCODE SYSTEM ENTERED\n'+
                            '*** ICINT RECENT INSTRUCTION TRACE ***\n'+
                            ''.join(f'CYCLE={i}\n' for i in range(75))+
                            '*** END ICINT TRACE ***\nEXECUTION CYCLES = 5, CODE = -1\n')
        output = MOD.inspect(Path('run'))
        self.assertIn('CYCLE=74', output)
        self.assertNotIn('CYCLE=1\n', output)

if __name__ == '__main__':
    unittest.main()
