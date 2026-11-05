"""Offline, subprocess-based cooperative admission and controller lease tests."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1] / 'mvs'
sys.path.insert(0, str(HERE))
import jes_submission_gate as gate

CHILD = r'''
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
from jes_submission_gate import SubmissionDenied, admit
try:
    with admit(Path(sys.argv[2])):
        print('ADMITTED')
except SubmissionDenied as exc:
    print('DENIED', exc)
    raise SystemExit(77)
'''


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'mvs-state').mkdir()
        self.old = os.environ.pop(gate.ENV_FD, None)
        self.addCleanup(self.restore_env)

    def restore_env(self):
        os.environ.pop(gate.ENV_FD, None)
        if self.old is not None:
            os.environ[gate.ENV_FD] = self.old

    def child(self, inherited=False):
        cmd = [sys.executable, '-B', '-c', CHILD, str(HERE), str(self.root)]
        fds = gate.child_pass_fds(self.root) if inherited else ()
        env = os.environ.copy()
        if not inherited:
            env.pop(gate.ENV_FD, None)
        return subprocess.run(cmd, capture_output=True, text=True,
                              pass_fds=fds, env=env, check=False)

    def test_ordinary_job_admitted(self):
        self.assertEqual(0, self.child().returncode)
        with gate.admit(self.root):
            self.assertEqual(0, self.child().returncode)

    def test_exclusive_window_blocks_ordinary_external_submission(self):
        with gate.controller_window(self.root):
            result = self.child()
            self.assertEqual(77, result.returncode)
            self.assertIn('DENIED', result.stdout)
        self.assertEqual(0, self.child().returncode)

    def test_controller_children_inherit_verified_lease(self):
        with gate.controller_window(self.root) as fd:
            self.assertFalse(os.get_inheritable(fd))
            result = self.child(inherited=True)
            self.assertEqual(0, result.returncode, result.stdout+result.stderr)
            self.assertIn('ADMITTED', result.stdout)
            # Python would close a high FD by default; no env-based bypass.
            result = self.child(inherited=False)
            self.assertEqual(77, result.returncode)

    def test_python_subprocess_forwards_lease_through_two_generations(self):
        intermediary = (
            'import subprocess,sys; '
            'sys.path.insert(0,sys.argv[1]); '
            'from pathlib import Path; '
            'from jes_submission_gate import child_pass_fds; '
            'r=Path(sys.argv[2]); '
            'p=subprocess.run([sys.executable,"-B","-c",sys.argv[3],'
            'sys.argv[1],sys.argv[2]],pass_fds=child_pass_fds(r),'
            'capture_output=True,text=True); '
            'print(p.stdout);sys.exit(p.returncode)'
        )
        with gate.controller_window(self.root):
            process = subprocess.run(
                [sys.executable, '-B', '-c', intermediary, str(HERE),
                 str(self.root), CHILD],
                pass_fds=gate.child_pass_fds(self.root), capture_output=True,
                text=True, check=False)
            self.assertEqual(0, process.returncode, process.stdout+process.stderr)
            self.assertIn('ADMITTED', process.stdout)

    def test_kernel_releases_lock_after_controller_is_killed(self):
        import signal
        import time
        code = (
            'import sys,time;from pathlib import Path;'
            'sys.path.insert(0,sys.argv[1]);'
            'from jes_submission_gate import controller_window;'
            'r=Path(sys.argv[2]);'
            'with_block=controller_window(r);'
            'with_block.__enter__();'
            'print("LOCKED",flush=True);time.sleep(30)'
        )
        proc = subprocess.Popen(
            [sys.executable, '-B', '-c', code, str(HERE), str(self.root)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual('LOCKED', proc.stdout.readline().strip())
            self.assertEqual(77, self.child().returncode)
        finally:
            proc.send_signal(signal.SIGKILL)
            proc.communicate(timeout=3)
        self.assertEqual(0, self.child().returncode)

    def test_bogus_env_descriptor_is_refused(self):
        os.environ[gate.ENV_FD] = '4'
        with self.assertRaises(gate.SubmissionDenied):
            with gate.admit(self.root):
                pass

    def test_forged_descriptor_same_inode_refused_during_controller(self):
        with gate.controller_window(self.root):
            # Another process may open the exact same file while the original
            # exclusive lease exists. Its new description must NOT qualify.
            path = self.root/'mvs-state/locks/jes-submission.lock'
            attacker = os.open(path, os.O_RDONLY)
            try:
                result = subprocess.run(
                    [sys.executable, '-B', '-c', CHILD,
                     str(HERE), str(self.root)],
                    env={**os.environ, gate.ENV_FD: str(attacker)},
                    pass_fds=(attacker,), capture_output=True, text=True)
                self.assertEqual(77, result.returncode, result.stdout+result.stderr)
                self.assertIn('DENIED', result.stdout)
            finally:
                os.close(attacker)

    def test_fd_wrong_file_refused(self):
        with tempfile.TemporaryFile() as handle:
            os.environ[gate.ENV_FD] = str(handle.fileno())
            with self.assertRaises(gate.SubmissionDenied):
                with gate.admit(self.root):
                    pass

    def test_controller_refuses_nested_window(self):
        with gate.controller_window(self.root):
            with self.assertRaises(gate.SubmissionDenied):
                with gate.controller_window(self.root):
                    pass
        self.assertNotIn(gate.ENV_FD, os.environ)

    def test_controller_refuses_other_current_submitter(self):
        # Shared admission is an existing in-flight submission.
        with gate.admit(self.root):
            with self.assertRaises(gate.SubmissionDenied):
                with gate.controller_window(self.root):
                    pass
        with gate.controller_window(self.root):
            pass

    def test_symlinked_lock_directory_rejected(self):
        target = self.root / 'elsewhere'
        target.mkdir()
        (self.root / 'mvs-state/locks').symlink_to(target)
        with self.assertRaises(gate.SubmissionDenied):
            with gate.admit(self.root):
                pass

    def test_symlinked_lock_file_rejected(self):
        (self.root / 'mvs-state/locks').mkdir(mode=0o700)
        (self.root / 'mvs-state/locks/jes-submission.lock').symlink_to(self.root/'elsewhere')
        with self.assertRaises(gate.SubmissionDenied):
            with gate.admit(self.root):
                pass

    def test_insecure_lock_directory_rejected(self):
        folder = self.root / 'mvs-state/locks'
        folder.mkdir(mode=0o777)
        folder.chmod(0o777)
        with self.assertRaises(gate.SubmissionDenied):
            with gate.admit(self.root):
                pass

    def test_lease_cleared_even_on_exception(self):
        with self.assertRaisesRegex(RuntimeError, 'synthetic failure'):
            with gate.controller_window(self.root):
                raise RuntimeError('synthetic failure')
        self.assertNotIn(gate.ENV_FD, os.environ)
        self.assertEqual(0, self.child().returncode)

    def test_submitted_command_preserves_rc_and_denies_outsiders(self):
        with gate.controller_window(self.root):
            self.assertEqual(23, gate.submit_command(
                self.root, [sys.executable, '-c', 'raise SystemExit(23)']))
            self.assertEqual(77, self.child().returncode)
        self.assertEqual(0, gate.submit_command(
            self.root, [sys.executable, '-c', 'print("OK")']))


class PublicSubmitTests(unittest.TestCase):
    """Exercise the public wrapper against a harmless local Bash stand-in."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'mvs-state').mkdir()
        (self.root/'tools/mvs').mkdir(parents=True)
        import shutil
        for name in ('jes_submission_gate.py', 'submit-jcl'):
            shutil.copy(HERE/name, self.root/'tools/mvs'/name)
        (self.root/'tools/mvs/submit-jcl-core.sh').write_text(
            '#!/usr/bin/env bash\n'
            'echo "HELPER JOB 900 $*"\n'
            'sleep 0.1\n'
            'exit 0\n')

    def call(self, inherit=False):
        env = os.environ.copy()
        if not inherit:
            env.pop(gate.ENV_FD, None)
        return subprocess.run([sys.executable, '-B', str(self.root/'tools/mvs/submit-jcl'),
                               '--timeout', '99', '/tmp/dummy.jcl'], env=env,
                              pass_fds=gate.child_pass_fds(self.root) if inherit else (),
                              capture_output=True, text=True, check=False)

    def test_public_submit_runs_existing_helper_when_uncontended(self):
        result = self.call()
        self.assertEqual(0, result.returncode, result.stdout+result.stderr)
        self.assertIn('HELPER JOB 900 --timeout 99 /tmp/dummy.jcl', result.stdout)

    def test_in_flight_public_submit_prevents_controller_takeover(self):
        import time
        helper = self.root/'tools/mvs/submit-jcl-core.sh'
        marker = self.root/'helper-running'
        helper.write_text('#!/usr/bin/env bash\n'
                          f'touch {marker}\n'
                          'sleep 1\n'
                          'echo JOB 901\n')
        process = subprocess.Popen(
            [sys.executable, '-B', str(self.root/'tools/mvs/submit-jcl')],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            # Wait for a marker written by the admitted helper.
            deadline = time.monotonic() + 4
            while not marker.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(marker.exists(), 'helper never started')
            with self.assertRaises(gate.SubmissionDenied):
                with gate.controller_window(self.root):
                    pass
            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(0, process.returncode, stderr)
            self.assertIn('JOB 901', stdout)
            with gate.controller_window(self.root):
                pass
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)

    def test_public_submit_denied_during_exclusive_window(self):
        with gate.controller_window(self.root):
            result = self.call()
            self.assertEqual(77, result.returncode)
            self.assertNotIn('HELPER JOB', result.stdout)
            owned = self.call(inherit=True)
            self.assertEqual(0, owned.returncode, owned.stderr)
            self.assertIn('HELPER JOB', owned.stdout)
        self.assertEqual(0, self.call().returncode)


if __name__ == "__main__":
    unittest.main()
