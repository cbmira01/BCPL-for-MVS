"""Fail-closed CO.5 generation/staging/oracle checks after each rebuild operation."""
from __future__ import annotations
import json
from pathlib import Path
import re

COMPILED = Path('workarea/co5-production/coroutines-generated.asm')
PREPARED = Path('workarea/co5-production/coroutin-prepared.asm')
ORACLE_ROOT = Path('workarea/co5-installed-coroutines')

def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError('CO.5: ' + reason)

def verify_reconstruction_coroutine(kind: str, *, root: Path,
                                    output: str, git_sha: str,
                                    inventory: dict[str, str]) -> str | None:
    """Return strict oracle result text for persistent evidence, or None."""
    if kind == 'coroutine-compile':
        file = root / COMPILED
        require(len(re.findall(r'(?m)^JOB [0-9]+$', output)) == 1 and
                output.count(f'saved Cambridge CODE: {COMPILED}') == 1 and
                file.is_file() and not file.is_symlink() and file.stat().st_size > 0,
                'resident Cambridge coroutine CODE missing')
        return None
    if kind == 'coroutine-prepare':
        file = root / PREPARED
        cards = re.findall(r'(?m)^Prepared IFOX COROUTIN: ' +
                           re.escape(str(PREPARED)) +
                           r' \(([0-9]+) cards\)$', output)
        require(len(cards) == 1 and file.is_file() and not file.is_symlink(),
                'prepared IFOX COROUTIN missing')
        rows = file.read_text('ascii').splitlines()
        require(len(rows) == int(cards[0]) and len(rows) >= 100 and
                all(len(x) <= 71 and '\t' not in x for x in rows) and
                rows.count('CO3LIB   CSECT') == 1 and
                any('ENTRY C3INIT,C3CREATE,C3DELETE' in x for x in rows) and
                rows[-1].strip() == 'END   CO3LIB',
                'prepared IFOX cards or exports invalid')
        return None
    if kind == 'coroutine-stage':
        expected = (r'put completed as JOB [0-9]+: ' +
                    re.escape(str(PREPARED)) + r' -> ' +
                    re.escape(inventory['BOOT_ASM']) + r'\(COROUTIN\)')
        require(re.fullmatch(expected, output.strip()) is not None,
                'BOOT_ASM(COROUTIN) stage receipt invalid')
        return None
    if kind == 'coroutine-oracle':
        jobs = re.findall(r'(?m)^INSTALLED COROUTINES PASS: compiler JOB ([0-9]+), '
                          r'native JOB ([0-9]+); IFOX/IEWL/GO all RC=0000$', output)
        paths = re.findall(r'(?m)^Installed coroutine evidence: (workarea/[^\s]+)$',
                           output)
        require(len(jobs) == 1 and len(paths) == 1,
                'installed IFOX/IEWL/GO PASS receipt missing')
        folder = Path(paths[0])
        require(folder.parent == ORACLE_ROOT and
                re.fullmatch(r'[0-9]{8}T[0-9]{6}Z-[A-Za-z0-9_-]+',
                             folder.name) is not None,
                'installed oracle evidence location invalid')
        result = root / folder / 'result.json'
        require(result.is_file() and not result.is_symlink(),
                'installed oracle result.json missing')
        report = result.read_text('utf-8')
        data = json.loads(report)
        require(isinstance(data, dict) and data.get('status') == 'PASS' and
                data.get('git_head') == git_sha and
                str(data.get('compiler_job')) == jobs[0][0] and
                str(data.get('native_job')) == jobs[0][1] and
                data.get('installed_objects_modified') is False and
                data.get('linkage') ==
                    'installed BOOT_OBJ(BCPLMAIN/BCPLCO/COROUTIN)' and
                data.get('steps') == {'ASMA': 0, 'LKED': 0, 'GO': 0},
                'installed oracle revision, job or linker contract mismatch')
        rows = data.get('bcpl_records')
        require(isinstance(rows, list) and len(rows) == 21 and
                rows[0] == 'CO3BCPL MADE' and rows[-1] == 'CO3BCPL PASS',
                'installed oracle 21-record output missing')
        return report
    raise ValueError(f'CO.5: unknown operation {kind}')
