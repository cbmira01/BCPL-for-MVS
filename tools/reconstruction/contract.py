"""Shared, immutable Step 3 reconstruction operations and host-scope safety.

This module has no ability to submit JES jobs or delete datasets.  The planner
and runner use the same operations, and the host cleaner uses the same snapshot.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Iterable, Mapping

HLQ = 'HERC02'
MANAGED_PREFIX = HLQ + '.BCPL.'


class ScopeError(RuntimeError):
    pass


@dataclass(frozen=True)
class Operation:
    guide: str
    name: str
    command: tuple[str, ...]
    check: str = 'zero'
    # A write description is visible during authorization; never conceal a
    # destructive operation behind a nominally read-only command.
    writes: tuple[str, ...] = ()


DSPAL = 'tools/datasets/dspal'
BOOTSTRAP = 'tools/bootstrap/prepare-bootstrap'
OPERATIONS = (
    Operation('1', 'Remove generated host workarea', ('tools/clean-workarea',), 'cleanup', ('host:workarea/* except .gitignore',)),
    Operation('2', 'Purge all managed BCPL datasets', (DSPAL, 'purgebcpl', '--yes'), 'purge', ('MVS:approved existing managed DSNs only',)),
    Operation('2', 'Recreate managed datasets', (DSPAL, 'initbcpl'), 'init', ('MVS:approved missing managed DSNs only',)),
    Operation('2', 'Verify all 29 managed allocations', (DSPAL, 'stat'), 'allocated-inventory'),
    Operation('2', 'Populate Git-backed members', (DSPAL, 'populate', 'all'), 'first-populate', ('MVS:tracked members from manifest',)),
    Operation('2', 'Check initial extension objects are empty', (DSPAL, 'ls', 'EXT_OBJ'), 'extension-empty'),
    Operation('2', 'Check initial development objects are empty', (DSPAL, 'ls', 'BOOT_DEVOBJ'), 'devobj-empty'),
    Operation('3', 'Build ICINT19', (DSPAL, 'submit', 'MR10_JCL', 'IC19BLD'), 'icint', ('MVS:MR10_OBJ(ICINT19), MR10_LOAD(ICINT19)',)),
    Operation('3', 'Check interpreter load library', (DSPAL, 'ls', 'MR10_LOAD'), 'icint-members'),
    Operation('3', 'Check interpreter object library', (DSPAL, 'ls', 'MR10_OBJ'), 'icint-members'),
    Operation('3', 'Smoke-test installed ICINT19', ('tools/mr10/compile-and-run', '--installed-icint', 'MR10_LOAD', '--results', 'mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.bcpl'), 'code-zero', ('MVS:smoke-test temporary datasets',)),
    Operation('5', 'Generate bootstrap and TRNILRG', (BOOTSTRAP, '--with-trnilrg'), 'bootstrap', ('host:workarea/bootstrap-cambridge/*',)),
    Operation('5', 'Populate generated-only members', (DSPAL, 'populate', 'all', '--generated-only'), 'generated-populate', ('MVS:generated members from manifest',)),
    Operation('5', 'Verify installed translator', (DSPAL, 'ls', 'BOOT_INTCODE'), 'trni-members'),
    Operation('6', 'Build CAMBCOMP', (DSPAL, 'submit', 'BOOT_JCL', 'CAMBBLD'), 'cambridge', ('MVS:BOOT_INTCODE(CAMBCOMP and 11 units)',)),
    Operation('6', 'Verify installed compiler INTCODE', (DSPAL, 'ls', 'BOOT_INTCODE'), 'cambridge-members'),
    Operation('6', 'Smoke-test assembler output', ('tools/bootstrap/compile-mvs', 'bootstrap-toolchain/regression/00-most-degenerate-bcpl-program/source.bcpl', '--output', 'workarea/m3-clean-smoke.s370.asm'), 'asm-smoke', ('host:workarea/m3-clean-smoke.s370.asm',)),
    Operation('7', 'Build Core Runtime', (DSPAL, 'submit', 'BOOT_JCL', 'BLDBMAIN'), 'runtime', ('MVS:BOOT_OBJ(seven Core Runtime members)',)),
    Operation('8', 'Build BLIB', (DSPAL, 'submit', 'BOOT_JCL', 'BLIBBLD'), 'blib', ('MVS:BOOT_OBJ(BLIB)',)),
    Operation('8', 'Verify Core Runtime and BLIB members', (DSPAL, 'ls', 'BOOT_OBJ'), 'runtime-members'),
    Operation('8', 'Verify development objects remain empty', (DSPAL, 'ls', 'BOOT_DEVOBJ'), 'devobj-empty'),
    Operation('9', 'Install BCPLDEMO', (DSPAL, 'submit', 'BOOT_JCL', 'BCPLDEMO'), 'bcpldemo', ('MVS:EXT_OBJ(BCPLDEMO)',)),
    Operation('9', 'Install BCPLTIME', (DSPAL, 'submit', 'BOOT_JCL', 'BCPLTIME'), 'bcpltime', ('MVS:EXT_OBJ(BCPLTIME)',)),
    Operation('9', 'Install BCPLQSAM', (DSPAL, 'submit', 'BOOT_JCL', 'BCPLQSAM'), 'bcplqsam', ('MVS:EXT_OBJ(BCPLQSAM)',)),
    Operation('9', 'Verify System Extensions', (DSPAL, 'ls', 'EXT_OBJ'), 'extensions-members'),
)


DSN_PATTERN = re.compile(r'[A-Z@$#][A-Z0-9@$#]{0,7}(?:\.[A-Z@$#][A-Z0-9@$#]{0,7})+')


def dataset_inventory(config: Mapping, full_dsn, *,
                      expected_logicals: Iterable[str] | None = None) -> tuple[tuple[str, str], ...]:
    mvs = config['mvs']
    for key in ('hlq', 'batch_user', 'userid'):
        if str(mvs.get(key, '')).upper() != HLQ:
            raise ScopeError(f'mvs.{key} must be {HLQ} for reconstruction')
    if str(mvs.get('write_boundary', '')).upper() != HLQ + '.**':
        raise ScopeError('unexpected MVS write boundary')
    logicals = set(config['datasets'])
    if expected_logicals is not None:
        tracked_logicals = frozenset(expected_logicals)
        if logicals != tracked_logicals:
            raise ScopeError('effective inventory differs from Git-tracked logical dataset manifest: '
                             f'missing={sorted(tracked_logicals-logicals)}, '
                             f'extra={sorted(logicals-tracked_logicals)}')
    if not logicals:
        raise ScopeError('managed dataset inventory is empty')
    pairs: list[tuple[str, str]] = []
    dsns = set()
    for logical, spec in config['datasets'].items():
        dsn = full_dsn(config, spec).upper()
        if not dsn.startswith(MANAGED_PREFIX) or DSN_PATTERN.fullmatch(dsn) is None:
            raise ScopeError(f'out-of-scope DSN in {logical}: {dsn}')
        if dsn in dsns:
            raise ScopeError(f'duplicate managed dataset: {dsn}')
        pairs.append((logical, dsn))
        dsns.add(dsn)
    return tuple(sorted(pairs))


def tracked_logicals(root: Path, core) -> frozenset[str]:
    source = core.load_simple_yaml(root / 'config/dspal.yaml')
    value = source.get('datasets')
    if not isinstance(value, dict) or not value:
        raise ScopeError('Git-tracked dataset manifest is missing or invalid')
    return frozenset(value)


def command_manifest(inventory: Iterable[tuple[str, str]]):
    return {
        'schema': 1,
        'hlq': HLQ,
        'persistent_evidence': {
            'root': 'mvs-state/reconstruction-evidence/',
            'contents': ['approved-plan identity', 'operation outputs', 'payload summaries',
                         'payload job reports', 'diagnostics', 'final attempt report'],
            'purpose': 'diagnosis only; no resume or baseline acceptance',
        },
        'managed_datasets': list(inventory),
        'operations': [{'guide': op.guide, 'name': op.name,
                        'command': list(op.command), 'check': op.check,
                        'writes': list(op.writes)} for op in OPERATIONS],
        'read_only_pre_destructive_checks': [
            'dspal purgebcpl --show-jcl', 'dspal initbcpl --show-jcl',
            'compare full DSN inventories with approved scope',
        ],
        'post_submit_verification': [
            'tools/mvs/job-summary PAYLOAD_JOB',
            'tools/mvs/dump-report-for-job PAYLOAD_JOB',
            'tools/datasets/dspal purgebcpl --show-jcl (read-only, pre-purge)',
            'tools/datasets/dspal initbcpl --show-jcl (read-only, pre-init)',
            'validate exact payload job/step/ICINT/IFOX/IEWL/readback evidence',
        ],
        'exclusions': ['regression suites', 'native Cambridge compiler',
                       'release', 'Git tag', 'resume'],
    }


def canonical_digest(obj: object) -> str:
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode('ascii')
    return hashlib.sha256(blob).hexdigest()


def mountpoints() -> frozenset[str]:
    """Include bind mounts whose device matches their parent."""
    paths = set()
    try:
        with open('/proc/self/mountinfo', encoding='utf-8') as stream:
            for row in stream:
                fields = row.split(' ', 5)
                if len(fields) < 5:
                    continue
                escaped = fields[4]
                path = re.sub(r'\\([0-7]{3})', lambda m: chr(int(m.group(1), 8)), escaped)
                paths.add(os.path.normpath(path))
    except OSError as exc:
        raise ScopeError('cannot verify mount boundaries') from exc
    return frozenset(paths)


def _entry_signature(st: os.stat_result) -> tuple[int, ...]:
    # Timestamps on directory entries may change when a sibling changes;
    # inode/device/mode bind identity, sizes and mtime bind file versions.
    basic = (st.st_dev, st.st_ino, stat.S_IFMT(st.st_mode), st.st_mode & 0o7777)
    return basic + ((st.st_size, st.st_mtime_ns, st.st_ctime_ns) if stat.S_ISREG(st.st_mode) else (st.st_ctime_ns,))


def _walk(fd: int, base: Path, prefix: str, root_device: int,
          mounted: frozenset[str], rows: list[tuple]) -> None:
    with os.scandir(fd) as iterator:
        names = sorted((entry.name for entry in iterator), key=os.fsencode)
    for name in names:
        if not prefix and name == '.gitignore':
            continue
        path = f'{prefix}/{name}' if prefix else name
        absolute = os.path.normpath(str(base / path))
        st = os.stat(name, dir_fd=fd, follow_symlinks=False)
        if absolute in mounted or os.path.ismount(absolute):
            raise ScopeError(f'mounted entry is not disposable: {path}')
        if st.st_dev != root_device:
            raise ScopeError(f'cross-device workarea entry: {path}')
        if not (stat.S_ISREG(st.st_mode) or stat.S_ISDIR(st.st_mode)):
            raise ScopeError(f'unsupported entry type (including symlink): {path}')
        rows.append((path, *_entry_signature(st)))
        if stat.S_ISDIR(st.st_mode):
            flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, 'O_CLOEXEC', 0)
            child = os.open(name, flags, dir_fd=fd)
            try:
                if _entry_signature(os.fstat(child)) != _entry_signature(st):
                    raise ScopeError(f'workarea directory replaced: {path}')
                _walk(child, base, path, root_device, mounted, rows)
            finally:
                os.close(child)


@dataclass(frozen=True)
class CleanupScope:
    fingerprint: str
    entries: tuple[tuple, ...]
    root_identity: tuple[int, ...]
    marker_identity: tuple[int, ...]


def workarea_scope(workarea: Path, *, mounted: frozenset[str] | None = None) -> CleanupScope:
    workarea = Path(os.path.abspath(workarea))
    if workarea.is_symlink():
        raise ScopeError('workarea must not be a symlink')
    if str(workarea) in (mounted if mounted is not None else mountpoints()):
        raise ScopeError('workarea itself is a mount point; refusing cleanup')
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, 'O_CLOEXEC', 0)
    try:
        fd = os.open(workarea, flags)
    except OSError as exc:
        raise ScopeError('cannot open workarea safely') from exc
    try:
        root_stat = os.fstat(fd)
        marker = os.stat('.gitignore', dir_fd=fd, follow_symlinks=False)
        if not stat.S_ISREG(marker.st_mode):
            raise ScopeError('workarea/.gitignore is not a regular file')
        rows: list[tuple] = []
        _walk(fd, workarea, '', root_stat.st_dev,
              mounted if mounted is not None else mountpoints(), rows)
        data = {'workarea': _entry_signature(root_stat),
                'marker': _entry_signature(marker), 'entries': rows}
        return CleanupScope(canonical_digest(data), tuple(rows),
                            _entry_signature(root_stat), _entry_signature(marker))
    finally:
        os.close(fd)


def validate_jcl(jcl_text: str, *, inventory: Iterable[tuple[str, str]]) -> None:
    """Reject JCL with persistent DSNs beyond the exact approved inventory.

    A system catalog/macro DD may refer outside the namespace only as SHR.
    Temporary && datasets are excluded.  This is static preflight validation,
    not a replacement for MVS authority checks.
    """
    allowed = {dsn for _, dsn in inventory}
    for line in jcl_text.upper().splitlines():
        if line.startswith('//*') or line.startswith('/*'):
            continue
        for match in re.finditer(r'\bDSN\s*=\s*([^,\s)]+(?:\([^\s,)]*\))?)', line):
            operand = match.group(1).strip("'\"")
            if operand.startswith('&&'):
                continue
            dsn = operand.split('(')[0].strip("'\"")
            if DSN_PATTERN.fullmatch(dsn) is None:
                raise ScopeError(f'unrecognized JCL DSN: {dsn}')
            if dsn in allowed:
                continue
            if dsn.startswith('SYS1.') and 'DISP=SHR' in line:
                continue
            raise ScopeError(f'JCL refers to unapproved dataset: {dsn}')


def remove_workarea_contents(workarea: Path, approved: CleanupScope) -> None:
    """Delete only reviewed regular files/directories using pinned dir FDs.

    Requires no hostile concurrent writer; identity is still verified at every
    use boundary.  A concurrent mutation raises ScopeError, never success.
    """
    workarea = Path(os.path.abspath(workarea))
    current = workarea_scope(workarea)
    if current != approved:
        raise ScopeError('workarea changed since approval; no cleanup started')
    by_path = {row[0]: tuple(row[1:]) for row in approved.entries}
    fd = os.open(workarea, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        if _entry_signature(os.fstat(fd)) != approved.root_identity:
            raise ScopeError('workarea directory replaced')
        if _entry_signature(os.stat('.gitignore', dir_fd=fd, follow_symlinks=False)) != approved.marker_identity:
            raise ScopeError('workarea marker changed')

        def remove_children(parent_fd: int, prefix: str) -> None:
            expected_path = os.path.normpath(str(workarea / prefix))
            observed_path = os.readlink(f'/proc/self/fd/{parent_fd}')
            if observed_path != expected_path:
                raise ScopeError(f'workarea directory moved out of approved scope: {prefix}')
            with os.scandir(parent_fd) as it:
                names = sorted((entry.name for entry in it), key=os.fsencode)
            for name in names:
                if not prefix and name == '.gitignore':
                    continue
                rel = f'{prefix}/{name}' if prefix else name
                original = by_path.get(rel)
                if original is None:
                    raise ScopeError(f'new unapproved workarea entry: {rel}')
                st = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                if _entry_signature(st) != original:
                    raise ScopeError(f'workarea entry changed before deletion: {rel}')
                abs_name = os.path.normpath(str(workarea / rel))
                if abs_name in mountpoints() or os.path.ismount(abs_name):
                    raise ScopeError(f'mount appeared before deletion: {rel}')
                if os.readlink(f'/proc/self/fd/{parent_fd}') != expected_path:
                    raise ScopeError(f'workarea parent directory moved: {prefix}')
                if stat.S_ISDIR(st.st_mode):
                    child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                    dir_fd=parent_fd)
                    try:
                        if _entry_signature(os.fstat(child)) != original:
                            raise ScopeError(f'workarea directory changed: {rel}')
                        remove_children(child, rel)
                    finally:
                        os.close(child)
                    # Directories' content-changing mtime is expected here.
                    after = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                    if _entry_signature(after)[:4] != original[:4]:
                        raise ScopeError(f'workarea directory replaced during deletion: {rel}')
                    os.rmdir(name, dir_fd=parent_fd)
                else:
                    os.unlink(name, dir_fd=parent_fd)
        remove_children(fd, '')
        with os.scandir(fd) as it:
            remaining = {entry.name for entry in it}
        if remaining != {'.gitignore'}:
            raise ScopeError(f'cleanup incomplete: unexpected remaining entries {sorted(remaining)}')
    finally:
        os.close(fd)
