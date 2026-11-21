"""TA.2 rc2 display parser and safety contract: no MVS calls in tests."""
import importlib.machinery
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/ta2-rc2-media-preflight'
loader = importlib.machinery.SourceFileLoader('ta2rc2media', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

H = '[hercules / inquiry] devlist\n13:23:32 HHC02279I 0:0480 3420 * IO[31] maxsize=0 eotmargin=128K deonirq=N\n'
M = '[mvs / inquiry] /D U,TAPE\n23:36:00 / 480  3400 O-NRD              /REMOV 481  3400 OFFLINE\n'

class TestMediaReadOnly(unittest.TestCase):
    def test_hercules_empty(self): self.assertEqual(mod.parse_hercules(H),'EMPTY')
    def test_hercules_loaded_refused(self):
        with self.assertRaises(mod.Refusal): mod.parse_hercules(H.replace(' * IO',' /tk5/tape/other.aws IO'))
    def test_hercules_busy_refused(self):
        with self.assertRaises(mod.Refusal): mod.parse_hercules(H.replace('IO[31]', 'BUSY IO[31]'))
    def test_hercules_duplicate_refused(self):
        with self.assertRaises(mod.Refusal): mod.parse_hercules(H+H)
    def test_hercules_missing_refused(self):
        with self.assertRaises(mod.Refusal): mod.parse_hercules('HTTP accepted; no response')
    def test_mvs_onrd_and_adjacent_offline(self): self.assertEqual(mod.parse_mvs(M), 'O-NRD')
    def test_mvs_online(self): self.assertEqual(mod.parse_mvs(M.replace('O-NRD','O')), 'O')
    def test_mvs_identical_echo(self): self.assertEqual(mod.parse_mvs(M+M), 'O-NRD')
    def test_mvs_conflicting_echo(self):
        with self.assertRaises(mod.Refusal): mod.parse_mvs(M+M.replace('O-NRD','O'))
    def test_mvs_alloc_refused(self):
        with self.assertRaises(mod.Refusal): mod.parse_mvs(M.replace('O-NRD','O-NRD ALLOC'))
    def test_mvs_busy_refused(self):
        with self.assertRaises(mod.Refusal): mod.parse_mvs(M.replace('O-NRD','O-NRD BUSY'))
    def test_mvs_offline_refused(self):
        with self.assertRaises(mod.Refusal): mod.parse_mvs(M.replace('O-NRD','OFFLINE'))
    def test_mvs_no_row_refused(self):
        with self.assertRaises(mod.Refusal): mod.parse_mvs('No console messages captured in observation window')
    def test_reject_noninquiry(self):
        with self.assertRaises(mod.Refusal): mod.inquire(('tools/mvs/mvs-console','tape','mount','480','x.aws'), 'media', None)
    def test_default_never_inquires(self):
        with patch.object(mod,'validate_plan',return_value='abc'), patch.object(mod,'inquire',side_effect=AssertionError('MVS called')):
            self.assertEqual(mod.run(False), 0)

if __name__=='__main__': unittest.main()
