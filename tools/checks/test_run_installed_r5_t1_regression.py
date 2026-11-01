#!/usr/bin/env python3
"""Offline contract tests for installed R.5/T.1 regression wrapper."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / "tools/bootstrap/run-installed-r5-t1-regression"
spec = importlib.util.spec_from_file_location("installed_r5_t1", WRAPPER)
if spec is None or spec.loader is None:
    # importlib.util.spec_from_file_location cannot infer extensionless scripts.
    from importlib.machinery import SourceFileLoader
    spec = importlib.util.spec_from_loader("installed_r5_t1", SourceFileLoader("installed_r5_t1", str(WRAPPER)))
assert spec is not None and spec.loader is not None
wrapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wrapper)


class FakeCore:
    @staticmethod
    def full_dsn(config, spec):
        return config["mvs"]["hlq"] + "." + spec["dsn"]

    def load_config(self):
        return {
            "mvs": {"hlq": "ALTERN8"},
            "datasets": {
                "EXT_OBJ": {"dsn": "BCPL.EXT.OBJ", "content_type": "object"},
                "EXT_MAC": {"dsn": "BCPL.EXT.MAC", "recfm": "FB"},
            },
        }


class WrapperTests(unittest.TestCase):
    def setUp(self):
        self.core = FakeCore()
        self.config = self.core.load_config()

    def test_resolved_config_sets_both_installed_modes(self):
        initial = {"PATH": "/bin", "BCPL_R5_EXTENSION_MODE": "source"}
        env = wrapper.installed_environment(
            self.core, self.config, initial, resume_punch=False
        )
        self.assertEqual(initial["BCPL_R5_EXTENSION_MODE"], "source")
        self.assertEqual(env["PATH"], "/bin")
        for prefix in ("BCPL_R5", "BCPL_T1"):
            self.assertEqual(env[prefix + "_EXTENSION_MODE"], "installed")
            self.assertEqual(env[prefix + "_EXTENSION_DSN"], "ALTERN8.BCPL.EXT.OBJ")
            self.assertEqual(env[prefix + "_MACRO_DSN"], "ALTERN8.BCPL.EXT.MAC")
        self.assertNotIn("Q4_PUNCH_RESUME", env)

    def test_inherited_resume_is_suppressed_without_flag(self):
        env = wrapper.installed_environment(
            self.core, self.config, {"Q4_PUNCH_RESUME": "1"},
            resume_punch=False,
        )
        self.assertNotIn("Q4_PUNCH_RESUME", env)

    def test_resume_requires_explicit_option(self):
        env = wrapper.installed_environment(
            self.core, self.config, {}, resume_punch=True
        )
        self.assertEqual(env["Q4_PUNCH_RESUME"], "1")

    def test_fail_closed_when_object_library_not_object(self):
        self.config["datasets"]["EXT_OBJ"]["content_type"] = "text"
        with self.assertRaisesRegex(ValueError, "EXT_OBJ"):
            wrapper.installed_environment(self.core, self.config, {}, resume_punch=False)

    def test_fail_closed_when_macro_library_not_fb(self):
        self.config["datasets"]["EXT_MAC"]["recfm"] = "U"
        with self.assertRaisesRegex(ValueError, "EXT_MAC"):
            wrapper.installed_environment(self.core, self.config, {}, resume_punch=False)

    def test_main_execs_existing_production_runner_and_forwards_arguments(self):
        with mock.patch.object(wrapper, "load_core", return_value=self.core), \
             mock.patch.object(wrapper.os, "execve") as execute, \
             mock.patch.dict(wrapper.os.environ, {"Q4_PUNCH_RESUME": "1"}):
            self.assertEqual(wrapper.main(["0", "176", "--show-output"]), 0)
        execute.assert_called_once()
        path, args, env = execute.call_args.args
        self.assertEqual(path, str(wrapper.RUNNER))
        self.assertEqual(args, [str(wrapper.RUNNER), "0", "176", "--show-output"])
        self.assertNotIn("Q4_PUNCH_RESUME", env)
        self.assertEqual(env["BCPL_T1_EXTENSION_MODE"], "installed")

    def test_main_resume_passes_opt_in_and_range(self):
        with mock.patch.object(wrapper, "load_core", return_value=self.core), \
             mock.patch.object(wrapper.os, "execve") as execute:
            self.assertEqual(wrapper.main(["--resume-punch", "0", "176"]), 0)
        self.assertEqual(execute.call_args.args[2]["Q4_PUNCH_RESUME"], "1")
        self.assertEqual(execute.call_args.args[1][-2:], ["0", "176"])

    def test_missing_library_returns_error_without_exec(self):
        del self.config["datasets"]["EXT_MAC"]
        self.core.load_config = lambda: self.config
        with mock.patch.object(wrapper, "load_core", return_value=self.core), \
             mock.patch.object(wrapper.os, "execve") as execute:
            self.assertEqual(wrapper.main(["0", "176"]), 2)
        execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
