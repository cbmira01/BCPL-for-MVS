"""Offline checks: never transmit to JES or access Hercules."""
import importlib.machinery
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main, mock
import io

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "submit-scratch-job"
loader = importlib.machinery.SourceFileLoader("submit_scratch_job", str(SCRIPT))
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
        password = "REDACTED" if redact_password else "LOCALSECRET"
        return [f"//{job:<8} JOB (BCPL),'SCRATCH',CLASS=A,",
                f"//             USER=HERC02,PASSWORD={password}"]

    @classmethod
    def submit_and_wait(cls, config, deck, max_rc):
        cls.submitted = (deck, max_rc)
        return 42, "JOB 42: PASS"


class TestSubmitScratchJob(TestCase):
    def setUp(self):
        FakeCore.submitted = None
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name)
        self.source.joinpath("TP01PRE.jcl").write_text(
            "//* SAMPLE\n//COPY     EXEC PGM=IEBCOPY\n//SYSIN    DD  *\n"
            " COPY OUTDD=OUTPDS,INDD=INPDS\n/*\n//\n",
            encoding="ascii")
        self.patch_jcl = mock.patch.object(mod, "JCL_DIR", self.source)
        self.patch_jcl.start()
        self.addCleanup(self.patch_jcl.stop)
        self.patch_core = mock.patch.object(mod, "load_core", return_value=FakeCore)
        self.patch_core.start()
        self.addCleanup(self.patch_core.stop)

    def test_preview_is_redacted_and_does_not_submit(self):
        with mock.patch.object(mod.sys, "stdout", new_callable=io.StringIO) as out:
            self.assertEqual(mod.main(["TP01PRE"]), 0)
            self.assertIn("PASSWORD=REDACTED", out.getvalue())
            self.assertNotIn("LOCALSECRET", out.getvalue())
        self.assertIsNone(FakeCore.submitted)

    def test_noninteractive_run_refused(self):
        with mock.patch.object(mod.sys.stdin, "isatty", return_value=False):
            self.assertEqual(mod.main(["TP01PRE", "--run"]), 2)
        self.assertIsNone(FakeCore.submitted)

    def test_wrong_confirmation_refused(self):
        with mock.patch.object(mod.sys.stdin, "isatty", return_value=True), \
             mock.patch("builtins.input", return_value="no"):
            self.assertEqual(mod.main(["TP01PRE", "--run"]), 2)
        self.assertIsNone(FakeCore.submitted)

    def test_accepted_confirmation_calls_existing_submitter_once(self):
        with mock.patch.object(mod.sys.stdin, "isatty", return_value=True), \
             mock.patch("builtins.input", return_value="SUBMIT TP01PRE"):
            self.assertEqual(mod.main(["TP01PRE", "--run"]), 0)
        self.assertEqual(FakeCore.submitted[1], 0)
        self.assertIn("PASSWORD=LOCALSECRET", FakeCore.submitted[0])
        self.assertEqual(FakeCore.submitted[0].count("EXEC PGM=IEBCOPY"), 1)

    def test_tape_job_requires_existing_image(self):
        self.source.joinpath("TP02UNLD.jcl").write_text(
            "//* SAMPLE\n//UNLOAD EXEC PGM=IEBCOPY\n/*\n//\n", encoding="ascii")
        with mock.patch.object(mod, "TAPE_IMAGE", self.source / "missing.aws"):
            self.assertEqual(mod.main(["TP02UNLD", "--run"]), 2)
        self.assertIsNone(FakeCore.submitted)

    def test_wrong_hlq_refused(self):
        with mock.patch.object(FakeCore, "load_config",
                               return_value={"mvs": {"hlq": "UNSAFE"}}):
            self.assertEqual(mod.main(["TP01PRE"]), 2)
        self.assertIsNone(FakeCore.submitted)

    def test_embedded_job_card_rejected(self):
        self.source.joinpath("TP01PRE.jcl").write_text(
            "//BADJOB JOB CLASS=A\n/*\n//\n", encoding="ascii")
        with self.assertRaisesRegex(ValueError, "JOB card"):
            mod.read_body("TP01PRE")

    def test_card_too_long_rejected(self):
        self.source.joinpath("TP01PRE.jcl").write_text(
            "//*" + "X" * 80 + "\n/*\n//\n", encoding="ascii")
        with self.assertRaisesRegex(ValueError, "80-column"):
            mod.read_body("TP01PRE")


if __name__ == "__main__":
    main()
