#!/usr/bin/env python3
"""R.0 Decision A stage 2: test-only binary FB80 compare jobs; never install."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'workarea/runtime-extensions-r0-object-identity'
SOURCE = ROOT / 'bootstrap-toolchain/asm/bcplmem.asm'
CORE = ROOT / 'tools/datasets/dspal-core.py'
PROFILES = {'calibrate': 'R0BICAL', 'member': 'R0BIMEM'}
CAL_A = ('* R.0 B: OBJECT CALIBRATION RECORD A.\n'
         'R0BICA   CSECT\n'
         "         DC    F'111'\n"
         '         END   R0BICA\n')
CAL_B = CAL_A.replace('R0BICA', 'R0BICB').replace("F'111'", "F'222'")


def checked_source(src: str, name: str) -> str:
    if not src or not src.endswith('\n'):
        raise ValueError(f'{name}: missing source or final LF')
    for i, line in enumerate(src.splitlines(), 1):
        if not line.isascii() or len(line) > 71 or '\t' in line or line == '/*' or line.startswith('//'):
            raise ValueError(f'{name}: invalid card {i}')
    return src


def core_module():
    spec = importlib.util.spec_from_file_location('r0bi_dspal', CORE)
    if spec is None or spec.loader is None:
        raise ValueError('cannot locate dspal-core.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def obj_spec(core, config: dict) -> str:
    spec = config['datasets']['BOOT_OBJ']
    if any((spec.get('dsorg') != 'PO', spec.get('recfm') != 'FB',
            int(spec.get('lrecl', 0)) != 80, int(spec.get('blksize', 0)) != 800,
            spec.get('content_type') != 'object', spec.get('populate') is not False)):
        raise ValueError('BOOT_OBJ must be unmanaged read-only object PDS, PO FB80 BLKSIZE 800')
    dsn = core.full_dsn(config, spec)
    if not re.fullmatch(r'[A-Z0-9@$#]{1,8}(?:\.[A-Z0-9@$#]{1,8}){1,5}', dsn):
        raise ValueError('invalid BOOT_OBJ DSN')
    return dsn


def asm_step(name: str, obj: str, source: str) -> list[str]:
    return [
        f'//{name:<8} EXEC PGM=IFOX00,REGION=256K,',
        "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'",
        '//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR',
        '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))',
        '//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))',
        '//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))',
        '//SYSPRINT DD  SYSOUT=*',
        '//SYSPUNCH DD  DUMMY',
        f'//SYSGO    DD  DSN=&&{obj},UNIT=SYSDA,',
        '//             SPACE=(80,(300,100)),DISP=(NEW,PASS),',
        '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
        '//SYSIN    DD  *',
        *checked_source(source, name).splitlines(),
        '/*',
    ]


def copy_step() -> list[str]:
    return [
        '//COPYA    EXEC PGM=IEBGENER,COND=(0,NE,ASMA)',
        '//SYSPRINT DD  SYSOUT=*',
        '//SYSIN    DD  DUMMY',
        '//SYSUT1   DD  DSN=&&OBJA,DISP=(OLD,PASS)',
        '//SYSUT2   DD  DSN=&&COPYA,UNIT=SYSDA,',
        '//             SPACE=(80,(20,10)),DISP=(NEW,PASS),',
        '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
    ]


def compr_step(name: str, a: str, b: str, cond: str | None = None) -> list[str]:
    # MVS 3.8 manual uses COMPARE TYPORG=PS; do not depend on defaults.
    first = f'//{name:<8} EXEC PGM=IEBCOMPR'
    if cond:
        first += f',COND={cond}'
    return [first,
            '//SYSPRINT DD  SYSOUT=*',
            f'//SYSUT1   DD  DSN={a},DISP=SHR' if not a.startswith('&&') else
            f'//SYSUT1   DD  DSN={a},DISP=(OLD,PASS)',
            f'//SYSUT2   DD  DSN={b},DISP=SHR' if not b.startswith('&&') else
            f'//SYSUT2   DD  DSN={b},DISP=(OLD,PASS)',
            '//SYSIN    DD  *',
            ' COMPARE TYPORG=PS',
            '/*']


def make_deck(profile: str, card: list[str], *, dsn: str | None = None,
              source: str | None = None) -> str:
    if profile not in PROFILES:
        raise ValueError('unknown profile')
    job = PROFILES[profile]
    if not card or card[0].split()[:2] != [f'//{job}', 'JOB']:
        raise ValueError('incorrect authenticated JOB card')
    rows = [*card, '//* R.0 DECISION A STAGE 2: OBJECT RECORD COMPARISON',
            '//* TEMP BINARY FB80 ONLY; BOOT_OBJ MUST NEVER BE OUTPUT']
    if profile == 'calibrate':
        rows += asm_step('ASMA', 'OBJA', CAL_A)
        rows += asm_step('ASMB', 'OBJB', CAL_B)
        rows += copy_step()
        rows += compr_step('SAME', '&&OBJA', '&&COPYA',
                           '((0,NE,ASMB),(0,NE,COPYA))')
        rows += compr_step('DIFFER', '&&OBJA', '&&OBJB',
                           '((0,NE,ASMB),(0,NE,SAME))')
    else:
        if not dsn or source is None:
            raise ValueError('member comparison requires BOOT_OBJ name and Git source')
        rows += asm_step('ASMMEM', 'MEMOBJ', source)
        rows += compr_step('COMPARE', f'{dsn}(BCPLMEM)', '&&MEMOBJ',
                           '(0,NE,ASMMEM)')
    rows.append('//')
    for i, item in enumerate(rows, 1):
        if not item.isascii() or len(item) > 71 or '\t' in item:
            raise ValueError(f'bad JCL card {i}: {item!r}')
    if profile == 'calibrate':
        assert_guard(rows, 2, 2)
    else:
        assert_guard(rows, 1, 1, dsn=dsn)
    return '\n'.join(rows) + '\n'


def assert_guard(rows: list[str], asms: int, comps: int, dsn: str | None = None) -> None:
    deck = '\n'.join(rows)
    if rows.count('//SYSIN    DD  *') != asms + comps or rows.count('/*') != asms + comps:
        raise ValueError('unexpected inline source/control streams')
    if deck.count('EXEC PGM=IFOX00') != asms or deck.count('EXEC PGM=IEBCOMPR') != comps:
        raise ValueError('unexpected assembler/comparator steps')
    if 'COMPARE TYPORG=PS' not in deck or 'DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)' not in deck:
        raise ValueError('binary FB80 / historical compare contract absent')
    if dsn:
        mentions = [r for r in rows if dsn in r]
        if len(mentions) != 1 or mentions[0] != f'//SYSUT1   DD  DSN={dsn}(BCPLMEM),DISP=SHR':
            raise ValueError('BOOT_OBJ must be input-only member on SYSUT1')
    if any('BOOT_OBJ' in r and r.startswith('//SYSUT') for r in rows):
        raise ValueError('hardcoded BOOT_OBJ dataset')
    if re.search(r'EXEC PGM=(?:IEBCOPY|IEWL|AMASPZAP)', deck) or 'DISP=MOD' in deck:
        raise ValueError('unsafe output or link step')
    for row in rows:
        if row.startswith('//SYSGO') or row.startswith('//SYSLMOD') or row.startswith('//SYSUT2'):
            if dsn and dsn in row:
                raise ValueError('attempt to write accepted dataset')


def source_manifest(profile: str, src: str | None, git_revision: str,
                    dsn: str | None) -> dict:
    items = {'profile': profile, 'github_revision': git_revision,
             'job': PROFILES[profile],
             'historical_compare_control': 'COMPARE TYPORG=PS',
             'object_comparison': 'logical record bytes and count, FB80',
             'installed_object_member': f'{dsn}(BCPLMEM)' if dsn else None,
             'source_file': 'bootstrap-toolchain/asm/bcplmem.asm' if src else None,
             'source_sha256': hashlib.sha256(src.encode('ascii')).hexdigest() if src else None,
             'calibration_a_sha256': hashlib.sha256(CAL_A.encode()).hexdigest(),
             'calibration_b_sha256': hashlib.sha256(CAL_B.encode()).hexdigest(),
             'evidence_boundary': 'No deployed objects changed; equality not implied by generation'}
    return items


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('profile', choices=PROFILES)
    p.add_argument('--check', action='store_true', help='no credentials, JCL or MVS')
    p.add_argument('--git-revision', help='exact revision for source attestation')
    args = p.parse_args()
    if not args.check and (not args.git_revision or
                           not re.fullmatch(r'[0-9a-f]{40}', args.git_revision)):
        p.error('40-digit Git revision required for authenticated JCL')
    src = checked_source(SOURCE.read_text(encoding='ascii'), 'BCPLMEM') if args.profile == 'member' else None
    if args.check:
        dsn = 'HERC02.BCPL.BOOT.OBJ'
        card = [f"//{PROFILES[args.profile]} JOB (BCPL),'R0 B ID',CLASS=A,MSGCLASS=A"]
    else:
        core = core_module()
        config = core.load_config()
        dsn = obj_spec(core, config)
        card = core.authenticated_job_card(config, PROFILES[args.profile],
                                            'R0 B IDENT', redact_password=False)
    deck = make_deck(args.profile, card, dsn=dsn, source=src)
    if args.check:
        print(f'CHECK R.0 B {args.profile}: {len(deck.splitlines())} cards; '
              'no credentials, dataset writes or MVS execution')
        return
    OUT.mkdir(parents=True, exist_ok=True)
    name = PROFILES[args.profile].lower()
    path = OUT / f'{name}.jcl'
    path.write_text(deck, encoding='ascii', newline='\n')
    path.chmod(0o600)
    (OUT / f'{name}-source.json').write_text(
        json.dumps(source_manifest(args.profile, src, args.git_revision, dsn),
                   indent=2, sort_keys=True) + '\n', encoding='ascii')
    print(f'Generated test-only, input-safe JCL: {path}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit(f'R.0 B generation FAILED: {exc}')
