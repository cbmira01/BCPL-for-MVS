#!/usr/bin/env python3
"""Private TA.0 output location policy: only ignored repository workarea/.

The repository has a tracked workarea/.gitignore which ignores everything
below it.  Private JES reports (possibly containing JOB-card credentials)
must never be written to tracked packaging/ or unrelated $HOME directories.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class EvidencePathError(ValueError):
    """An evidence directory is not a safe project-local workarea directory."""


def guard(path: Path, *, new: bool, root: Path | None = None) -> None:
    """Validate a directory before reading or creating evidence.

    Reject lexical traversal, symlinks in path components, missing parents,
    and any location other than a descendant of <repo>/workarea/.  Caller
    creates a new directory with restrictive permissions after this check.
    """
    repo = (ROOT if root is None else root).absolute()
    workarea = repo / 'workarea'
    if not path.is_absolute() or '..' in path.parts or path == workarea:
        raise EvidencePathError('TA.0 evidence path must be below repository workarea/')
    if not path.is_relative_to(workarea):
        raise EvidencePathError('TA.0 evidence path must be below repository workarea/')
    if not workarea.is_dir() or workarea.is_symlink():
        raise EvidencePathError('repository workarea/ must be a real directory')
    # Inspect every component, not just the immediate parent.  A symlink in
    # the middle could escape the ignored tree even when the path looks safe.
    check = path
    while check != workarea:
        if check.is_symlink():
            raise EvidencePathError('TA.0 evidence paths cannot contain symlinks')
        check = check.parent
    if new:
        if path.exists() or not path.parent.is_dir():
            raise EvidencePathError('TA.0 output must be a new directory with existing workarea parent')
    elif not path.is_dir():
        raise EvidencePathError('existing TA.0 evidence directory is missing')
    if not path.resolve(strict=False).is_relative_to(workarea.resolve()):
        raise EvidencePathError('TA.0 evidence path escaped workarea/')
