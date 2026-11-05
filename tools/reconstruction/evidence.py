"""Durable per-attempt reconstruction evidence outside disposable workarea.

No checkpoint/resume state, no credentials, and no implicit acceptance or release.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any


class EvidenceError(RuntimeError):
    pass


def redact(value: str, secrets: tuple[str, ...] = ()) -> str:
    out = re.sub(r'(?i)(\b(?:PASSWORD|PASSWD|TOKEN|SECRET|CREDENTIAL)\s*=\s*)[^,\s\r\n]+',
                 r'\1[REDACTED]', str(value))
    for secret in sorted((x for x in secrets if x), key=len, reverse=True):
        out = out.replace(secret, '[REDACTED]')
    return out


def publicize(obj: Any, secrets: tuple[str, ...]) -> Any:
    if isinstance(obj, dict):
        return {str(key): '[REDACTED]' if re.search(r'password|secret|token|credential', str(key), re.I)
                else publicize(v, secrets) for key, v in obj.items()}
    if isinstance(obj, (tuple, list)):
        return [publicize(x, secrets) for x in obj]
    if isinstance(obj, str):
        return redact(obj, secrets)
    return obj


def write_durable(path: Path, contents: str) -> None:
    """Atomic per-file publication, restrictive modes, and flush to storage."""
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.pending-', suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as f:
            f.write(contents)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
        parent_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class EvidenceLog:
    """Only a single live attempt writes a directory; failed runs are immutable."""

    def __init__(self, root: Path, *, git_sha: str, plan_sha256: str,
                 inventory: tuple[tuple[str, str], ...],
                 secrets: tuple[str, ...] = ()):
        self.secrets = tuple(x for x in secrets if x)
        state = root / 'mvs-state'
        if state.is_symlink():
            raise EvidenceError('MVS-state directory is a symlink')
        parent = state / 'reconstruction-evidence'
        if parent.is_symlink():
            raise EvidenceError('evidence root is a symlink')
        parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if not parent.is_dir():
            raise EvidenceError('evidence root unavailable')
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-')
        self.directory = Path(tempfile.mkdtemp(prefix=stamp, dir=parent))
        self.operations: list[dict[str, Any]] = []
        self.state = 'IN_PROGRESS'
        self.begun_at = datetime.now(timezone.utc).isoformat()
        self.git_sha = git_sha
        self.plan_sha256 = plan_sha256
        self.inventory = inventory
        self._save()

    def _save(self):
        document = publicize({
            'schema': 1, 'state': self.state, 'begun_at_utc': self.begun_at,
            'source_git_sha': self.git_sha, 'approved_plan_sha256': self.plan_sha256,
            'managed_datasets': list(self.inventory), 'operations': self.operations,
            'note': 'Operational evidence only; not acceptance, resume, tag, or release',
        }, self.secrets)
        write_durable(self.directory / 'report.json', json.dumps(document, indent=2) + '\n')

    def record(self, index: int, name: str, command: tuple[str, ...],
               rc: int | None, output: str, *, payload: int | None = None,
               launcher: int | None = None, result: str = 'FAIL',
               diagnostic: str = '') -> None:
        basename = f'{index:02d}-operation'
        write_durable(self.directory / (basename + '.log'),
                      redact(output, self.secrets))
        self.operations.append({
            'index': index, 'name': name, 'command': list(command),
            'rc': rc, 'result': result, 'payload_job': payload,
            'launcher_job': launcher, 'diagnostic': diagnostic,
            'log': basename + '.log',
        })
        self._save()

    def detail(self, index: int, kind: str, text: str) -> None:
        if not re.fullmatch(r'[a-z-]+', kind):
            raise EvidenceError('unsafe evidence detail name')
        write_durable(self.directory / f'{index:02d}-{kind}.log', redact(text, self.secrets))

    def finish(self, state: str, reason: str = '') -> None:
        if state not in ('SUCCESS', 'FAILED', 'BLOCKED', 'INTERRUPTED'):
            raise EvidenceError('invalid final reconstruction state')
        if state == 'SUCCESS' and (not self.operations or
                                   any(op['result'] != 'PASS' for op in self.operations)):
            raise EvidenceError('partial reconstruction cannot be reported successful')
        self.state = state
        if reason:
            self.operations.append({'result': 'DIAGNOSTIC', 'message': redact(reason, self.secrets)})
        self._save()
