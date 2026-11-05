"""Cooperative, fail-closed JES reader admission for the one local TK5 instance.

A reconstruction controller holds an exclusive flock for its entire execution
window, including preflight/approval and completion. All *project submission
transports* take shared admission on the same file before sending a JCL deck.
The controller's subprocesses receive a kernel-inherited lease FD; an
unrelated process cannot obtain admission while the controller owns the lock.

This coordinates project tools on one host. It DOES NOT close Hercules' reader,
block a 3270/console submission, or lock external network clients. Operators
must quiesce those external paths; never claim system-wide JES exclusivity.
"""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
import os
from pathlib import Path
import re
import stat
import subprocess
from typing import Iterator

ENV_FD = 'BCPL_JES_EXCLUSIVE_FD'
LOCK_DIR = 'locks'
LOCK_NAME = 'jes-submission.lock'


class SubmissionDenied(RuntimeError):
    """No trusted lease or an incompatible project JES submission window."""


def _open_lock(root: Path) -> int:
    """Open trusted lock file via no-follow directory descriptors."""
    state = Path(root) / 'mvs-state'
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    try:
        state_fd = os.open(state, flags)
    except OSError as exc:
        raise SubmissionDenied('MVS state is unavailable or unsafe') from exc
    try:
        try:
            os.mkdir(LOCK_DIR, mode=0o700, dir_fd=state_fd)
        except FileExistsError:
            pass
        lock_dir_fd = os.open(LOCK_DIR, flags, dir_fd=state_fd)
        try:
            info = os.fstat(lock_dir_fd)
            if info.st_uid != os.getuid() or info.st_mode & 0o077:
                raise SubmissionDenied('JES lock directory has unsafe ownership or permissions')
            fd = os.open(LOCK_NAME, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC,
                         0o600, dir_fd=lock_dir_fd)
            try:
                info = os.fstat(fd)
                if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or
                        info.st_uid != os.getuid() or info.st_mode & 0o077):
                    raise SubmissionDenied('JES lock file has unsafe ownership or permissions')
                return fd
            except BaseException:
                os.close(fd)
                raise
        finally:
            os.close(lock_dir_fd)
    except OSError as exc:
        raise SubmissionDenied('cannot establish trusted JES submission lock') from exc
    finally:
        os.close(state_fd)


def _inherited_lease(root: Path) -> int | None:
    raw = os.environ.get(ENV_FD)
    if raw is None:
        return None
    if not re.fullmatch(r'[1-9][0-9]{0,4}', raw):
        raise SubmissionDenied('invalid inherited JES controller lease descriptor')
    fd = int(raw)
    candidate = _open_lock(root)
    try:
        info = os.fstat(candidate)
        try:
            original = os.fstat(fd)
        except OSError as exc:
            raise SubmissionDenied('inherited JES controller descriptor is closed') from exc
        if (info.st_dev, info.st_ino) != (original.st_dev, original.st_ino):
            raise SubmissionDenied('inherited JES controller descriptor targets another lock')
        # Check the inherited open-file *description* itself owns an exclusive
        # flock. Linux flock operates on descriptions: reacquiring EX on the
        # inherited description is idempotent; a newly opened FD cannot take
        # EX while another controller holds it. Checking only the inode and
        # contention on candidate would incorrectly trust a forged open FD.
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SubmissionDenied('inherited JES descriptor does not own exclusive lease') from exc
        # Independently confirm the lock is visible to a new open description.
        try:
            fcntl.flock(candidate, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError:
            return fd
        else:
            fcntl.flock(candidate, fcntl.LOCK_UN)
            raise SubmissionDenied('inherited JES controller lease is not exclusive')
    finally:
        os.close(candidate)


@contextmanager
def admit(root: Path) -> Iterator[None]:
    """Allow a single ordinary submission, or use an inherited controller FD."""
    lease = _inherited_lease(root)
    if lease is not None:
        yield
        return
    fd = _open_lock(root)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SubmissionDenied('JES submission blocked: reconstruction owns the reader window') from exc
        yield
    finally:
        os.close(fd)


@contextmanager
def controller_window(root: Path) -> Iterator[int]:
    """Reserve all cooperative project submission paths until context exit."""
    if os.environ.get(ENV_FD) is not None:
        raise SubmissionDenied('nested or inherited JES controller window is prohibited')
    fd = _open_lock(root)
    previous = None
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SubmissionDenied('cannot enter reconstruction: JES submissions already active') from exc
        # The descriptor stays close-on-exec. Only explicit pass_fds may
        # delegate it to the controller's trusted subprocesses.
        previous = os.environ.get(ENV_FD)
        os.environ[ENV_FD] = str(fd)
        yield fd
    finally:
        if previous is None:
            os.environ.pop(ENV_FD, None)
        else:
            os.environ[ENV_FD] = previous
        os.close(fd)


def child_pass_fds(root: Path) -> tuple[int, ...]:
    """Forward a verified controller lease across Python subprocess boundaries."""
    fd = _inherited_lease(root)
    return () if fd is None else (fd,)


def submit_command(root: Path, command: list[str], *, source=None) -> int:
    """Run a socket-writer command while admitted; preserve its real exit status."""
    if not command:
        raise SubmissionDenied('missing JES socket-writer command')
    with admit(root):
        completed = subprocess.run(command, stdin=source, check=False)
    return completed.returncode
