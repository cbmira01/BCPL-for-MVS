"""TA.1B directory evidence checks; no live JES operations."""
import importlib.machinery
import importlib.util
import io
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/run-ta1-track-b-directory'
loader = importlib.machinery.SourceFileLoader('ta1b_dir_guard', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)

class ContractTests(TestCase):
    def rows(self):
        return [{'jobname': n, 'dsn': d, 'volume': v,
                 'entry':'000000','attributes':'02E2'} for n,d,v in m.JOBS]

    def test_expected_source_target_contract(self):
        self.assertEqual(tuple(x[2] for x in m.JOBS), ('TSO003','TSO002'))
        self.assertEqual(m.compare(self.rows())['status'],
                         'IEHLIST_DIRECTORY_MATCH_ONLY_NOT_EXECUTABLE_PROOF')

    def test_wrong_attributes_rejected(self):
        rows=self.rows(); rows[1]['attributes']='02E3'
        with self.assertRaises(m.Halt): m.compare(rows)

    def test_wrong_entry_rejected(self):
        rows=self.rows(); rows[1]['entry']='000001'
        with self.assertRaises(m.Halt): m.compare(rows)

    def test_wrong_order_rejected(self):
        with self.assertRaises(m.Halt): m.compare(self.rows()[::-1])

    def test_unexpected_dcb_rejected(self):
        stat='Dataset:   '+m.TARGET+'\nDSORG:PO RECFM:FB LRECL:0 BLKSIZE:6144 Volume:TSO002'
        with self.assertRaises(m.Halt):m.stat_contract(stat,m.TARGET,'TSO002')

    def test_member_alias_or_extra_refused(self):
        with self.assertRaises(m.Halt):
            m.check_list(m.TARGET+':\n    ICINT19\n    ALIAS\n',m.TARGET)

    def test_iebcopy_9136_receipt_required(self):
        text='JOB 9136 TA1BREST\nRESTORE IEBCOPY RC=0000\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000'
        self.assertIn('RC=0000',text)
        with self.assertRaises(m.Halt):
            m.validate_job('JOB 9137 TA1BSRC\nDIRLIST IEHLIST RC=0004','', 'TA1BSRC',9137)

    def test_default_mode_never_submits(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[4]/'workarea') as base:
            ops=Path(base)/'ops';ops.mkdir()
            log=ops/'directory-log'
            with patch.object(m,'module',side_effect=[Mock(),Mock()]), \
                 patch.object(m,'live_preflight'), \
                 patch.object(m,'begin_once') as marker, \
                 patch.object(m,'submit_directory') as submit, \
                 patch.object(m.sys,'stdout',io.StringIO()), \
                 patch.object(m,'OPS',ops), patch.object(m,'LOG',log), \
                 patch.object(m,'ROOT',Path(base)):
                self.assertEqual(m.operation(run=False),0)
            marker.assert_not_called();submit.assert_not_called()
