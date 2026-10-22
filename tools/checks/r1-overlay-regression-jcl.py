#!/usr/bin/env python3
"""Insert TEMPORARY R.1 BCPLMAIN, registrar, and empty BCRG into native JCL.

Operates on an already generated *production OBJ* native-regression deck.
Never writes an MVS PDS. The output only contains temporary FB80 objects.
This overlay is intentionally opt-in, and refuses unexpected JCL syntax.
"""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
ASM = ROOT / 'bootstrap-toolchain/asm'
TRAIL = ROOT / 'bootstrap-toolchain/probes/r0-export-trailer-probe/make-job.py'
PATCHER = ROOT / 'tools/checks/r1_prepare_candidate.py'


def _module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise ValueError(f'missing generator helper: {path}')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def _once(lines: list[str], row: str) -> int:
    positions = [i for i, line in enumerate(lines) if line == row]
    if len(positions) != 1:
        raise ValueError(f'expected one {row!r}, found {len(positions)}')
    return positions[0]


def overlay(jcl: str, baseline: str, registrar: str, registry: str) -> str:
    rows = jcl.splitlines()
    if re.search(r'^//.*(?:DISP=MOD|DISP=OLD).*BOOT\.(?:OBJ|DEVOBJ)', jcl, re.M):
        raise ValueError('unsafe persistent object-library DD')
    if 'EXPLICIT BCPLMAIN CANDIDATE: 0' not in jcl:
        raise ValueError('overlay requires production profile, not DEVOBJ')
    if not any('RUNTIME LIBRARY: OBJ' in row for row in rows):
        raise ValueError('overlay requires all production OBJ services')
    if any('R1NOBJ' in row or 'R1ROBJ' in row or 'R1GOBJ' in row for row in rows):
        raise ValueError('duplicate R.1 overlay')
    main = _module(PATCHER, 'r1_overlay_main').adapt(baseline)
    trail = _module(TRAIL, 'r1_overlay_trail')
    # All three sources are independently assembled and kept in temporary
    # FB80 datasets for one IEWL. The accepted BOOT_OBJ is DISP=SHR only.
    sources = (
        ('ASMR1N', 'R1NOBJ', main),
        ('ASMR1R', 'R1ROBJ', registrar),
        ('ASMR1G', 'R1GOBJ', registry),
    )
    extra: list[str] = []
    for step, obj, source in sources:
        extra.extend(trail.asm_step(step, obj, trail.checked_asm(source, step)))
    link = next((i for i, line in enumerate(rows) if line.startswith('//LKED')
                 and 'EXEC' in line), None)
    if link is None:
        raise ValueError('no linker step')
    rows[link:link] = [
        '//* R.1 TEMPORARY CORE / REGISTRAR / EMPTY BCRG',
        '//* BOOT_OBJ READ ONLY; NO PDS INSTALLATION',
        *extra,
    ]
    # IEWL's explicit source objects must come before the in-stream DD.
    syspass = _once(rows, '//         DD *')
    rows[syspass:syspass] = [
        f'//         DD DSN=&&{obj},DISP=(OLD,DELETE)'
        for _, obj, _ in sources
    ]
    owner = _once(rows, ' INCLUDE OBJ(BCPLMAIN)')
    del rows[owner]
    if not any(' INCLUDE OBJ(BCPLIO)' == r for r in rows):
        # Fault-mode tests may provide their own ASMFIO object instead.
        if 'ASMFIO' not in jcl:
            raise ValueError('missing Core Runtime BCPLIO inclusion')
    result = '\n'.join(rows) + '\n'
    if result.count(' INCLUDE OBJ(BCPLMAIN)') or not re.search(r'DISP=SHR', result):
        raise ValueError('source object selection failed')
    if any(not x.isascii() or len(x) > 71 for x in rows):
        raise ValueError('bad IFOX/JCL card width')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    p.add_argument('output', type=Path)
    args = p.parse_args()
    if args.input.resolve() == args.output.resolve():
        raise ValueError('output must differ from source JCL')
    baseline = (ASM / 'bcplmain.asm').read_text('ascii')
    registrar = (ASM / 'bcplrgs.asm').read_text('ascii')
    registry = (ASM / 'bcplreg-empty.asm').read_text('ascii')
    deck = overlay(args.input.read_text('ascii'), baseline, registrar, registry)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(deck, encoding='ascii', newline='\n')
    args.output.chmod(0o600)
    print(f'R.1 temporary runtime overlay: {args.output}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit(f'R.1 regression overlay FAILED: {exc}')
