"""Offline approval gate tests: no JES submission or write operations."""
import importlib.machinery
import importlib.util
import io
from pathlib import Path
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "reconstruction/authorize"


def load_authorize():
    loader = importlib.machinery.SourceFileLoader("reconstruction_authorize_test", str(SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module  # dataclass annotations need a module reference
    loader.exec_module(module)
    return module


authorize = load_authorize()


def report(*, sha="a" * 40, hlq="HERC02", cfg="b" * 64, extra=""):
    return (
        "CLEAN-ROOM RECONSTRUCTION — READ-ONLY PREFLIGHT / DRY-RUN\n"
        "No changes will be made; no JES jobs submitted; no approval requested.\n"
        f"Git: {sha} (branch main)\n"
        f"Target: HLQ={hlq} batch-user=HERC02\n"
        f"Effective non-secret config SHA-256: {cfg}\n"
        "Authentication: configured (value never displayed)\n"
        "MANAGED MVS DATASETS TO DELETE AND RECREATE (preview only):\n"
        "  BOOT_OBJ       HERC02.BCPL.BOOT.OBJ [pds]\n"
        + extra +
        "\nREADY — read-only preflight passed; no authorization or execution performed.\n"
    )


class AuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.text = report()
        self.output = io.StringIO()
        self.calls = 0

    def planner(self):
        self.calls += 1
        return self.text, []

    def phrase(self):
        return "REBUILD HERC02 " + authorize.digest_report(self.text)[:12]

    def request(self, text=None, *, interactive=True, planner=None):
        return authorize.request_approval(
            planner or self.planner,
            output=self.output,
            read_line=lambda _prompt: self.phrase() if text is None else text,
            interactive=interactive,
        )

    def test_exact_acknowledgment_yields_ephemeral_grant(self):
        approved = self.request()
        self.assertEqual(approved.git_sha, "a" * 40)
        self.assertEqual(approved.hlq, "HERC02")
        self.assertEqual(self.calls, 2)
        self.assertIn(self.text, self.output.getvalue())
        self.assertIn("Type exactly: REBUILD HERC02", self.output.getvalue())
        authorize.verify_approval(approved, self.planner)
        self.assertEqual(self.calls, 3)

    def test_approval_is_bound_to_full_preview_content(self):
        approved = self.request()
        self.text = report(extra="  EXTRA HERC02.BCPL.EXTRALIB [pds]\n")
        with self.assertRaisesRegex(authorize.ApprovalError, "scope changed"):
            authorize.verify_approval(approved, self.planner)

    def test_approval_bound_to_private_config_override_mapping(self):
        approved = self.request()
        self.text = report(cfg="c" * 64)
        with self.assertRaises(authorize.ApprovalError):
            authorize.verify_approval(approved, self.planner)

    def test_no_tty_blocks_before_prompt(self):
        with self.assertRaisesRegex(authorize.ApprovalError, "interactive WSL"):
            self.request(interactive=False)
        self.assertEqual(self.calls, 1)

    def test_bad_phrase_does_not_authorize(self):
        for phrase in ("YES", "REBUILD HERC02", self.phrase() + " ", ""):
            self.output = io.StringIO()
            with self.assertRaises(authorize.ApprovalError) as ctx:
                self.request(text=phrase)
            self.assertEqual(ctx.exception.code, 3)

    def test_eof_cancels(self):
        def eof(_):
            raise EOFError()
        with self.assertRaises( authorize.ApprovalError) as ctx:
            authorize.request_approval(self.planner, output=self.output,
                                       read_line=eof, interactive=True)
        self.assertEqual(ctx.exception.code, 3)

    def test_preflight_errors_block_without_prompt(self):
        def bad_plan():
            return self.text.replace("READY —", "BLOCKED —"), ["wrong target"]
        with self.assertRaisesRegex(authorize.ApprovalError, "preflight BLOCKED"):
            self.request(planner=bad_plan)

    def test_preflight_drift_during_prompt_refuses(self):
        first = self.text
        changed = report(sha="c" * 40)
        n = iter([(first, []), (changed, [])])
        def planner():
            return next(n)
        with self.assertRaisesRegex(authorize.ApprovalError, "scope changed"):
            self.request(planner=planner)

    def test_second_preflight_can_be_blocked(self):
        n = iter([(self.text, []), (self.text, ["new issue"])])
        with self.assertRaisesRegex(authorize.ApprovalError, "BLOCKED"):
            self.request(planner=lambda: next(n))

    def test_malformed_or_missing_scope_is_blocked(self):
        for data in (report(sha="UNKNOWN"),
                     report(cfg="not-a-hash"),
                     report(hlq="BADSCOPE.JUNK"),
                     self.text.replace("READY —", "BLOCKED —")):
            with self.assertRaises(authorize.ApprovalError):
                authorize.identity(data)

    def test_approval_data_is_immutable(self):
        approved = self.request()
        from dataclasses import FrozenInstanceError
        with self.assertRaises(FrozenInstanceError):
            approved.git_sha = "c" * 40


if __name__ == "__main__":
    unittest.main()
