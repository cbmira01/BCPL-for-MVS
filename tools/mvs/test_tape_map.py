#!/usr/bin/env python3
"""Offline tape-map wrapper tests; never start Docker or submit JES."""
import importlib.machinery
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).with_name("tape-map")
loader = importlib.machinery.SourceFileLoader("tape_map", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)


class TapeMapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.tape_dir = Path(self.temp.name)
        self.image_name = "BTP001.aws"
        (self.tape_dir / self.image_name).write_bytes(b"fake AWS fixture")
        patch = mock.patch.object(mod, "TAPES", self.tape_dir)
        patch.start()
        self.addCleanup(patch.stop)

    def test_default_is_labels(self):
        with mock.patch.object(mod.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as run:
            self.assertEqual(mod.main([self.image_name]), 0)
        run.assert_called_once_with(
            ["docker", "exec", "mvs38j", "hetmap", "-l", "/tk5/tape/BTP001.aws"],
            check=False,
        )

    def test_explicit_modes(self):
        for opt, flag in (("--labels", "-l"), ("--all", "-a"),
                          ("--files", "-f"), ("--datasets", "-d"),
                          ("--text", "-t")):
            with self.subTest(mode=opt), mock.patch.object(
                    mod.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as run:
                self.assertEqual(mod.main([opt, self.image_name]), 0)
                self.assertEqual(run.call_args.args[0][4], flag)

    def test_reject_path_traversal(self):
        for bad in ("../BTP001.aws", "/tmp/BTP001.aws", "sub/BTP001.aws",
                    "..", ".", "\\evil.aws", "evil name.aws"):
            with self.subTest(image=bad), mock.patch.object(mod.subprocess, "run") as run:
                self.assertEqual(mod.main([bad]), 2)
                run.assert_not_called()

    def test_reject_symlink(self):
        (self.tape_dir / "link.aws").symlink_to(self.tape_dir / self.image_name)
        with mock.patch.object(mod.subprocess, "run") as run:
            self.assertEqual(mod.main(["link.aws"]), 2)
            run.assert_not_called()

    def test_reject_nonexistent_image(self):
        with mock.patch.object(mod.subprocess, "run") as run:
            self.assertEqual(mod.main(["missing.aws"]), 2)
            run.assert_not_called()

    def test_propagate_hetmap_failure(self):
        with mock.patch.object(mod.subprocess, "run", return_value=subprocess.CompletedProcess([], 5)):
            self.assertEqual(mod.main([self.image_name]), 5)

    def test_report_docker_unavailable(self):
        with mock.patch.object(mod.subprocess, "run", side_effect=FileNotFoundError("docker")):
            self.assertEqual(mod.main([self.image_name]), 1)

    def test_mutually_exclusive_modes(self):
        with self.assertRaises(SystemExit) as raised, mock.patch.object(mod.subprocess, "run") as run:
            mod.main(["--all", "--labels", self.image_name])
        self.assertEqual(raised.exception.code, 2)
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
