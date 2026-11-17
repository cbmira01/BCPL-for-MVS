#!/usr/bin/env python3
"""One-time atomic relocation of existing TA.0 evidence into ignored workarea/.

Moves the existing ~/ta0-mvs-evidence-20261117 tree, preserving private
JES report bytes and SHA256 receipts.  It does not create any new file or
folder outside the project, touch MVS, or run a JES job.  No overwrite,
copy/delete fallback, or symlink traversal.  Rerunning after a clean move is
safe and reports that the evidence already resides in workarea/.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
from pathlib import Path
import stat
import sys

ROOT = Path(__file__).resolve().parents[2]
LABEL = 'ta0-mvs-evidence-20261117'
MUST_HAVE = ('SHA256SUMS', 'MR10_LOAD.txt', 'MR10_LOAD.stat-raw.txt',
             'ta0-mr10-load-iehlist/receipt.json',
             'ta0-mr10-load-directory-reviewed/directory-review.json')


class RelocateError(ValueError):
    pass


def need(ok: bool, problem: str) -> None:
    if not ok:
        raise RelocateError(problem)


def module_paths():
    spec = importlib.util.spec_from_file_location('ta0_location_policy',
                  Path(__file__).with_name('ta0_evidence_paths.py'))
    need(spec is not None and spec.loader is not None, 'location policy missing')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def scan(folder: Path) -> tuple[int, int, str]:
    """Stream a deterministic inventory digest without printing private names.

    Symlinks, hard-linked files, sockets, FIFOs and devices are refused; only
    ordinary files/directories are expected in the retained MVS evidence tree.
    """
    lines: list[tuple[str, int, str]] = []
    count = total = 0
    for current, dirs, files in os.walk(folder, topdown=True, followlinks=False):
        base = Path(current)
        dirs.sort()
        files.sort()
        for name in dirs:
            child = base / name
            mode = child.lstat().st_mode
            need(stat.S_ISDIR(mode) and not stat.S_ISLNK(mode), 'linked or non-directory evidence component')
        for name in files:
            child = base / name
            info = child.lstat()
            need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                 'linked or non-regular evidence file')
            digest = hashlib.sha256()
            with child.open('rb') as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(block)
            rel = child.relative_to(folder).as_posix()
            lines.append((rel, info.st_size, digest.hexdigest()))
            count += 1
            total += info.st_size
    need(count > 0, 'no evidence files found')
    aggregate = hashlib.sha256()
    for name, size, digest in sorted(lines):
        aggregate.update(f'{name}\0{size}\0{digest}\n'.encode('utf-8'))
    return count, total, aggregate.hexdigest()


def relocate(*, root: Path = ROOT, home: Path | None = None) -> dict:
    home = Path.home() if home is None else home
    need(home.is_absolute() and home.is_dir(), 'home directory is unavailable')
    source = home / LABEL
    destination = root / 'workarea' / LABEL
    paths = module_paths()
    paths.guard(destination, new=not destination.exists(), root=root)
    if not source.exists():
        need(destination.is_dir() and not destination.is_symlink(),
             'neither original evidence nor migrated destination found')
        count, size, digest = scan(destination)
        return {'status': 'already-local', 'files': count,
                'bytes': size, 'inventory_sha256': digest, 'path': destination}
    need(source.is_dir() and not source.is_symlink(), 'home evidence is linked or invalid')
    need(not destination.exists() and not destination.is_symlink(),
         'both original and destination exist: refusing overwrite or merge')
    for entry in MUST_HAVE:
        path = source / entry
        need(path.is_file() and not path.is_symlink(),
             'required historical TA.0 evidence is missing or unsafe')
    before = scan(source)
    # os.rename is atomic for the usual WSL filesystem layout; EXDEV fails
    # without a copying fallback.  The original source must never be deleted
    # until we know that this exact directory has safely moved.
    os.rename(source, destination)
    after = scan(destination)
    need(before == after, 'evidence content changed during relocation')
    return {'status': 'moved', 'files': before[0], 'bytes': before[1],
            'inventory_sha256': before[2], 'path': destination}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    try:
        result = relocate()
    except (RelocateError, OSError, ValueError) as exc:
        # Error names only: never disclose/report original JES or JOB-card text.
        print(f'TA.0 EVIDENCE RELOCATION REFUSED: {type(exc).__name__}: {exc}',
              file=sys.stderr)
        return 1
    print(f"TA.0 EVIDENCE {result['status']}: {result['path']} "
          f"({result['files']} preserved files, {result['bytes']} bytes)")
    print('No JES submissions; SHA-256 inventory unchanged by relocation.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
