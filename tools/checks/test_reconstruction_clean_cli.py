"""Full CLI-level offline tests of the standalone workarea cleaner."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'reconstruction/contract.py'
spec = importlib.util.spec_from_file_location('clean_contract_tests', SOURCE)
contract = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = contract
spec.loader.exec_module(contract)
CLEAN = Path(__file__).resolve().parents[1] / 'clean-workarea'


class CleanCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'tools/reconstruction').mkdir(parents=True)
        shutil.copyfile(CLEAN, self.root/'tools/clean-workarea')
        shutil.copyfile(SOURCE, self.root/'tools/reconstruction/contract.py')
        (self.root/'workarea').mkdir()
        (self.root/'workarea/.gitignore').write_text('*\n')
        subprocess.run(['git','-C',str(self.root),'init','-q','-b','main'],check=True)
        subprocess.run(['git','-C',str(self.root),'add','-f','workarea/.gitignore'],check=True)

    def invoke(self, *args):
        return subprocess.run([sys.executable, str(self.root/'tools/clean-workarea'),*args],
                              text=True, capture_output=True, stdin=subprocess.DEVNULL)

    def test_exact_approved_cleanup_and_marker_preserved(self):
        (self.root/'workarea/one').mkdir()
        (self.root/'workarea/one/two').write_bytes(b'old')
        digest = contract.workarea_scope(self.root/'workarea').fingerprint
        result = self.invoke('--reconstruction-scope', digest)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([x.name for x in (self.root/'workarea').iterdir()], ['.gitignore'])

    def test_changed_file_blocks_without_deletion(self):
        file = self.root/'workarea/one'
        file.write_bytes(b'old')
        digest = contract.workarea_scope(self.root/'workarea').fingerprint
        file.write_bytes(b'changed')
        result = self.invoke('--reconstruction-scope', digest)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(file.read_bytes(), b'changed')

    def test_no_tty_no_implicit_approval(self):
        file = self.root/'workarea/one'
        file.write_text('old')
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(file.exists())
        self.assertIn('interactive terminal', result.stderr)

    def test_symlink_escapes_rejected(self):
        (self.root/'workarea/escape').symlink_to(self.root)
        digest = 'f'*64
        result = self.invoke('--reconstruction-scope', digest)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.root/'workarea/escape').is_symlink())


if __name__ == '__main__':
    unittest.main()
