"""Offline authorization tests for object-tape submissions."""
import importlib.machinery
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "submit-scratch-job"
loader = importlib.machinery.SourceFileLoader("submit_object_tape", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)


class FakeCore:
    submitted = None

    @staticmethod
    def load_config():
        return {"mvs": {"hlq": "HERC02"}}

    @staticmethod
    def authenticated_job_card(config, job, description, redact_password):
        secret = "REDACTED" if redact_password else "PRIVATE"
        return [f"//{job:<8} JOB USER=HERC02,PASSWORD={secret}"]

    @classmethod
    def submit_and_wait(cls, config, deck, max_rc):
        cls.submitted = (deck, max_rc)
        return 99, "JOB 99 PASS"


class ObjectTapeSubmitTests(unittest.TestCase):
    def setUp(self):
        FakeCore.submitted = None
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.image = Path(self.tmp.name) / "object.aws"
        for field, value in (("JCL_DIR", Path(__file__).resolve().parents[1] / "jcl"),
                             ("OBJECT_TAPE_IMAGE", self.image)):
            patcher = mock.patch.object(mod, field, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        core = mock.patch.object(mod, "load_core", return_value=FakeCore)
        core.start()
        self.addCleanup(core.stop)

    def test_preview_all_four_without_submission(self):
        for job in ("TO01PRE", "TO02UNLD", "TO03REST", "TO04COMP"):
            with self.subTest(job=job), mock.patch.object(mod.sys, "stdout", new_callable=io.StringIO) as output:
                self.assertEqual(mod.main([job]), 0)
                self.assertIn(f"//{job}", output.getvalue())
                self.assertIn("PASSWORD=REDACTED", output.getvalue())
        self.assertIsNone(FakeCore.submitted)

    def test_unload_and_restore_require_existing_regular_image(self):
        for job in ("TO02UNLD", "TO03REST"):
            self.assertEqual(mod.main([job, "--run"]), 2)
        self.assertIsNone(FakeCore.submitted)

    def test_symlink_image_is_refused(self):
        self.image.symlink_to(Path(__file__))
        self.assertEqual(mod.main(["TO03REST", "--run"]), 2)
        self.assertIsNone(FakeCore.submitted)

    def test_exact_authorization_submits_once(self):
        self.image.write_bytes(b"aws stub")
        with mock.patch.object(mod.sys.stdin, "isatty", return_value=True), \
             mock.patch("builtins.input", return_value="SUBMIT TO02UNLD"):
            self.assertEqual(mod.main(["TO02UNLD", "--run"]), 0)
        self.assertEqual(FakeCore.submitted[1], 0)
        self.assertIn("PASSWORD=PRIVATE", FakeCore.submitted[0])

    def test_wrong_confirmation_does_not_submit(self):
        with mock.patch.object(mod.sys.stdin, "isatty", return_value=True), \
             mock.patch("builtins.input", return_value="yes"):
            self.assertEqual(mod.main(["TO01PRE", "--run"]), 2)
        self.assertIsNone(FakeCore.submitted)


if __name__ == "__main__":
    unittest.main()
