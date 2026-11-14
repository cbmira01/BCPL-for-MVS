#!/usr/bin/env python3
"""Offline read-only receipt inspection checks for CO.3."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
MODULE=ROOT/'tools/coroutines/inspect-co3-evidence.py'
spec=importlib.util.spec_from_file_location('co3_evidence',MODULE)
co3=importlib.util.module_from_spec(spec)
spec.loader.exec_module(co3)

class InspectionChecks(TestCase):
    def test_saved_parent_chain_failure_receipt(self):
        with TemporaryDirectory() as parent:
            work=Path(parent)
            folder=work/'20261114T190836Z-v_koeeti'
            folder.mkdir()
            (folder/'result.json').write_text(json.dumps({
                'march':'CO.3','scenario':'parent-chain',
                'native_job':'5399','git_head':'a09e371edb3ca75c09ae8c0580ff09d0cb7f1ed0',
                'status':'FAIL','reason':'native GO job did not complete RC=0',
            }),encoding='utf-8')
            summary='''JOB 5399 CO3BGO
ASMA   PGM=IFOX00 RC=0000
ASML   PGM=IFOX00 RC=0012
JOB RESULT: FAILURE
HIGHEST RC: 0012
BYPASSED: one or more steps
'''
            report='CO3BCPL MADE\nCO3BCPL A1\nIEF450I CO3BGO GO - ABEND=S0C4\n'
            (folder/'job-summary.log').write_text(summary,encoding='utf-8')
            (folder/'job-report.log').write_text(report,encoding='utf-8')
            with patch.object(co3,'WORK',work):
                lines=co3.read_receipt(folder)
                self.assertIn('CO.3 parent-chain JOB 5399',lines)
                self.assertIn('  ASML   PGM=IFOX00 RC=0012',lines)
                self.assertIn('BCPL records: MADE A1',lines)
                self.assertTrue(any('IEF450I' in x for x in lines))
                self.assertLess(len(lines),20)
                (folder/'job-summary.log').write_text(summary.replace('JOB 5399','JOB 5398'),encoding='utf-8')
                with self.assertRaisesRegex(co3.ReceiptError,'identity'):
                    co3.read_receipt(folder)
                (folder/'job-summary.log').write_text(summary,encoding='utf-8')
                (folder/'job-report.log').unlink()
                with self.assertRaisesRegex(co3.ReceiptError,'missing or invalid'):
                    co3.read_receipt(folder)
                with self.assertRaisesRegex(co3.ReceiptError,'expected one'):
                    co3.read_receipt(work)

if __name__ == '__main__':
    main()
