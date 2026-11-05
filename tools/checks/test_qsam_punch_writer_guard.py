"""Host-only guard tests for case 175 JES2 punch writer handling.

All JES2 and Docker interactions are mocked. No JES commands are sent.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools/checks/run-q2-qsam-regression.py"
SPEC = importlib.util.spec_from_file_location("qsam_punch_guard_test", SOURCE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load QSAM native runner")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

CARD_IMAGE = (
    b"Q4CARD01\n"
    + b"Q4CARD02" + b" " * 71 + b"X\n"
    + b"Q4CARD03" + b" " * 71 + b"Y\n"
    + b"\n"
)
PAUSED = (
    "00:08:30 / 1.08.30 $HASP000 PUNCH1 00D PAUSED "
    "F=0001,AUTOM P=Y R=LOCAL S=N LIM=0-* Q=B\n"
)
QUEUE_9977 = (
    "00:09:25 / 1.09.25 JOB 9977 $HASP000 Q4PUNCH "
    "PRT LOCAL PUN LOCAL PRIO 1 ANY\n"
)


class PunchWriterGuardTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.attempt = self.root / "attempt"
        self.attempt.mkdir()
        self.capture = self.root / "pch00d.txt"
        self.capture.write_bytes(b"A" * 1032)
        self.log = self.root / "mvs-state/log/3033.log"
        self.log.parent.mkdir(parents=True)
        self.log.write_text("")
        self.calls = []
        self.status = PAUSED
        self.queue = QUEUE_9977
        self.ack_job = "9977"
        self.curl_rc = 0
        self.suite_patches = [
            patch.object(MOD, "ROOT", self.root),
            patch.object(MOD, "TOOLS", self.root / "tools"),
            patch.dict(MOD.SYSOUT_PATHS, {"punch": self.capture}),
            patch.object(MOD, "invoke", side_effect=self.fake_invoke),
            patch.object(MOD.time, "sleep", return_value=None),
            patch.dict(os.environ, {"Q4_PUNCH_RESUME": "1"}),
        ]
        for operation in self.suite_patches:
            operation.start()
            self.addCleanup(operation.stop)

    def fake_invoke(self, command, dest, limit):
        self.calls.append(command)
        if command[-2:] == ["jes2", "punches"]:
            response = self.status
            rc = 0
        elif command[-2:] == ["jes2", "$DN,Q=PPU"]:
            response = self.queue
            rc = 0
        elif command[:2] == ["docker", "exec"]:
            rc = self.curl_rc
            response = '<PRE>HHC00013I "/" input: "$S PUN1"</PRE>\n'
            if rc == 0:
                self.capture.write_bytes(self.capture.read_bytes() + CARD_IMAGE)
                self.log.write_text(
                    f"00:12:41 / 1.12.40 JOB {self.ack_job} "
                    "$HASP150 Q4PUNCH ON PUNCH1 3 CARDS\n"
                    "$HASP175 PUNCH1 PAUSED\n")
        else:
            self.fail(f"unexpected command: {command}")
        Path(dest).write_text(response, encoding="utf-8")
        return rc, response

    def starts(self):
        return sum(call[:2] == ["docker", "exec"] for call in self.calls)

    def test_one_exclusive_queued_job_starts_and_exact_bytes_pass(self):
        self.assertEqual(MOD.maybe_resume_punch_writer(1032, self.attempt, "9977"), [])
        self.assertEqual(self.starts(), 1)
        self.assertEqual(self.capture.stat().st_size, 1204)
        self.assertEqual(MOD.check_sysout_capture("punch", 1032, self.attempt), [])
        self.assertEqual((self.attempt / "sysout-capture.bin").read_bytes(), CARD_IMAGE)
        self.assertIn("JOB 9977", (self.attempt / "punch-writer-result.log").read_text())

    def test_no_opt_in_does_not_query_or_start(self):
        with patch.dict(os.environ, {"Q4_PUNCH_RESUME": ""}):
            self.assertEqual(MOD.maybe_resume_punch_writer(1032, self.attempt, "9977"), [])
        self.assertEqual(self.calls, [])

    def test_foreign_job_blocks_start(self):
        self.queue = (
            "JOB 9205 $HASP000 Q4PUNCH PRT LOCAL PUN LOCAL PRIO 14 ANY\n"
            + QUEUE_9977)
        errors = MOD.maybe_resume_punch_writer(1032, self.attempt, "9977")
        self.assertIn("not exclusive", errors[0])
        self.assertEqual(self.starts(), 0)
        self.assertEqual(self.capture.stat().st_size, 1032)

    def test_unrecognized_foreign_punch_routing_blocks_start(self):
        self.queue = (
            "JOB 9205 $HASP000 Q4PUNCH PRT LOCAL PUN REMOTE\n"
            + QUEUE_9977)
        errors = MOD.maybe_resume_punch_writer(1032, self.attempt, "9977")
        self.assertIn("not exclusive", errors[0])
        self.assertEqual(self.starts(), 0)

    def test_only_foreign_job_blocks_start(self):
        self.queue = "JOB 9205 $HASP000 Q4PUNCH PRT LOCAL PUN LOCAL\n"
        self.assertTrue(MOD.maybe_resume_punch_writer(1032, self.attempt, "9977"))
        self.assertEqual(self.starts(), 0)

    def test_unknown_queue_blocks_start(self):
        self.queue = "$HASP000 3 PERCENT SPOOL UTILIZATION\n"
        self.assertTrue(MOD.maybe_resume_punch_writer(1032, self.attempt, "9977"))
        self.assertEqual(self.starts(), 0)

    def test_wrong_device_state_blocks_start(self):
        self.status = PAUSED.replace("PAUSED", "ACTIVE")
        self.assertIn("not verified PAUSED",
                      MOD.maybe_resume_punch_writer(1032, self.attempt, "9977")[0])
        self.assertEqual(self.starts(), 0)

    def test_not_class_b_blocks_start(self):
        self.status = PAUSED.replace("Q=B", "Q=A")
        self.assertTrue(MOD.maybe_resume_punch_writer(1032, self.attempt, "9977"))
        self.assertEqual(self.starts(), 0)

    def test_preexisting_capture_change_does_not_start(self):
        self.capture.write_bytes(b"A" * 1033)
        self.assertEqual(MOD.maybe_resume_punch_writer(1032, self.attempt, "9977"), [])
        self.assertEqual(self.calls, [])

    def test_unacknowledged_target_job_fails_without_retry(self):
        self.ack_job = "9205"
        errors = MOD.maybe_resume_punch_writer(1032, self.attempt, "9977")
        self.assertIn("did not confirm JOB 9977", errors[0])
        self.assertEqual(self.starts(), 1)

    def test_http_failure_does_not_retry(self):
        self.curl_rc = 22
        errors = MOD.maybe_resume_punch_writer(1032, self.attempt, "9977")
        self.assertIn("do not retry", errors[0])
        self.assertEqual(self.starts(), 1)


if __name__ == "__main__":
    unittest.main()
