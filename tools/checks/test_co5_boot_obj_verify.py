"""Host-only exact BOOT_OBJ member inventory tests (no MVS access)."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'tools/reconstruction/verify-boot-obj.py'
spec = importlib.util.spec_from_file_location('co5_verify_boot_obj', SCRIPT)
assert spec is not None and spec.loader is not None
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)
from verify import RUNTIME_MEMBERS


class BootObjectInventoryTests(unittest.TestCase):
    def setUp(self):
        self.dsn = 'HERC02.BCPL.BOOT.OBJ'
        self.complete = (self.dsn + ':\n' +
                         ''.join(f'    {m}\n'
                                 for m in sorted(RUNTIME_MEMBERS)))

    def test_exact_ten_member_inventory(self):
        self.assertEqual(len(verifier.verify_listing(self.complete, self.dsn)), 10)

    def test_missing_coroutine_object_is_failure(self):
        with self.assertRaisesRegex(verifier.VerificationError, 'inventory'):
            verifier.verify_listing(self.complete.replace('    BCPLCO\n', ''), self.dsn)

    def test_extra_member_is_failure(self):
        with self.assertRaisesRegex(verifier.VerificationError, 'inventory'):
            verifier.verify_listing(self.complete + '    STALE\n', self.dsn)

    def test_wrong_dataset_is_failure(self):
        with self.assertRaisesRegex(verifier.VerificationError, 'heading'):
            verifier.verify_listing(self.complete, 'HERC03.BCPL.BOOT.OBJ')

    def test_duplicate_member_is_failure(self):
        with self.assertRaisesRegex(verifier.VerificationError, 'duplicate'):
            verifier.verify_listing(self.complete + '    BCPLCO\n', self.dsn)


if __name__ == '__main__':
    unittest.main()
