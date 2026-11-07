"""Offline checks for DSPAL JCL submission and job-start evidence."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stdout
from io import StringIO

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/mvs/submit-jcl"
SOURCE = ROOT / "tools/datasets/dspal-submit.py"

def load_submit():
    spec = importlib.util.spec_from_file_location("dspal_submit_checks", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

submit = load_submit()

class StoredJclSubmissionTests(unittest.TestCase):
    def setUp(self):
        self.cfg = {
            "mvs": {"hlq": "HERC02", "batch_user": "HERC02", "batch_password": "PW123"},
            "datasets": {"BOOT_JCL": {"dsn": "BCPL.BOOT.JCL", "dsorg": "PO",
                                      "recfm": "FB", "lrecl": 80}},
        }

    def test_launcher_cannot_submit_a_partial_job_deck(self):
        deck = submit.launcher_deck(self.cfg, "HERC02.BCPL.BOOT.JCL", "BLIBBLD")
        self.assertIn("//APPEND   EXEC PGM=IEBGENER,COND=(0,NE,MKJOB)", deck)
        self.assertIn("//SUBMIT   EXEC PGM=IEBGENER,COND=((0,NE,MKJOB),(0,NE,APPEND))", deck)
        self.assertIn("DSN=HERC02.BCPL.BOOT.JCL(BLIBBLD),DISP=SHR", deck)
        self.assertNotIn("DSPALLS", deck)

    def test_submit_uses_one_launcher_not_a_dspalls_lookup(self):
        out = StringIO()
        with mock.patch.object(submit.core, "load_config", return_value=self.cfg), \
             mock.patch.object(submit.core, "require_reader_ready"), \
             mock.patch.object(submit.core, "submit_and_wait", return_value=(801, "")) as dispatch, \
             mock.patch.object(submit, "printer_offset", return_value=100), \
             mock.patch.object(submit, "wait_for_payload_start", return_value=802), \
             mock.patch.object(submit, "wait_for_payload_completion", return_value=(0, "JOB RESULT: SUCCESS\n")), \
             mock.patch.object(sys, "argv", ["dspal", "BOOT_JCL", "BLIBBLD"]), \
             redirect_stdout(out):
            rc = submit.main()
        self.assertEqual(rc, 0)
        self.assertEqual(dispatch.call_count, 1)
        self.assertIn("DSPALSUB", dispatch.call_args.args[1])
        self.assertNotIn("DSPALLS", dispatch.call_args.args[1])

@unittest.skipUnless(shutil.which("timeout"), "timeout(1) is required")
class ReaderJobStartTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        program = self.root / "tools/mvs/submit-jcl"
        program.parent.mkdir(parents=True)
        shutil.copyfile(SCRIPT, program)
        self.program = program
        self.log = self.root / "mvs-state/prt/prt00e.txt"
        self.log.parent.mkdir(parents=True)
        self.jcl = self.root / "test.jcl"
        self.jcl.write_text("//DSPALLS  JOB (BCPL),'DSPAL LS',CLASS=A\n//STEP EXEC PGM=IEFBR14\n")
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        nc = bin_dir / "nc"
        nc.write_text("#!/usr/bin/env bash\ncat >/dev/null\n"
                      "if [ -n \"$PRINT_EVENT\" ]; then printf '%s\\n' \"$PRINT_EVENT\" >> \"$PRINTER_LOG\"; fi\n")
        nc.chmod(0o755)
        self.env = os.environ.copy()
        self.env["PATH"] = str(bin_dir) + os.pathsep + self.env["PATH"]
        self.env["PRINTER_LOG"] = str(self.log)

    def execute(self, previous="", event=""):
        self.log.write_text(previous)
        self.env["PRINT_EVENT"] = event
        return subprocess.run(["bash", str(self.program), "--timeout", "0", str(self.jcl)],
                              cwd=self.root, env=self.env, capture_output=True, text=True)

    def test_numbered_start_banner_without_hasp373(self):
        r = self.execute(event="****A  START JOB  987 DSPALLS HERC02 ROOM 5.23.10 AM 07 NOV 26")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "JOB 987")

    def test_old_banner_does_not_count_for_new_submission(self):
        old = "****A  START JOB  987 DSPALLS HERC02 ROOM 5.23.10 AM 07 NOV 26\n"
        r = self.execute(previous=old)
        self.assertEqual(r.returncode, 75)

    def test_unrelated_job_is_not_misattributed(self):
        r = self.execute(event="****A  START JOB  987 OTHERJOB HERC02 ROOM 5.23.10 AM 07 NOV 26")
        self.assertEqual(r.returncode, 75)

    def test_jcl_rejection_stops_without_a_job_id(self):
        r = self.execute(event="IEF452I DSPALLS JOB NOT RUN")
        self.assertEqual(r.returncode, 76)
        self.assertIn("JES rejected", r.stderr)

    def test_shell_syntax(self):
        r = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

if __name__ == "__main__":
    unittest.main()
