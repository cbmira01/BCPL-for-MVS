#!/usr/bin/env python3
"""R.0 Decision A: isolated, source-attested IFOX/IEWL boundary tests."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'workarea/runtime-extensions-r0-a'
CORE = ROOT / 'tools/datasets/dspal-core.py'
# Name, expected internal Decision G identifier, unique GO marker.
PROFILES = {
    'valid':    ('R0ALINK', 0,    'R0 A VALID LINK PASS'),
    'goodhook': ('R0AHOOK', 0,    'R0 A LINKED HOOK PASS'),
    'regzero':  ('R0AREGX', 1001, 'R0 A REG EXTENT 1001 PASS'),
    'regunal':  ('R0AUNAL', 1001, 'R0 A REG ALIGN 1001 PASS'),
    'pkgbound': ('R0APKGE', 1004, 'R0 A PKG EXTENT 1004 PASS'),
    'reglen':   ('R0ARLEN', 1003, 'R0 A REG LENGTH 1003 PASS'),
    'pkglen':   ('R0APLEN', 1006, 'R0 A PKG LENGTH 1006 PASS'),
    'regvers':  ('R0ARVER', 1002, 'R0 A REG HEADER 1002 PASS'),
    'pkgvers':  ('R0APVER', 1005, 'R0 A PKG HEADER 1005 PASS'),
    'badhook':  ('R0ABADH', 1013, 'R0 A HOOK TARGET 1013 PASS'),
}
OWNERS = {
    'R0ATST': 'R0ATST',
    'R0RB': 'R0AREG', 'R0RE': 'R0AREG',
    'R0PB': 'R0APKG', 'R0PE': 'R0APKG',
    'R0FUNC': 'R0AFUN', 'R0FIN': 'R0AFUN',
}


def checked_source(text: str, label: str) -> str:
    rows = text.rstrip('\n').splitlines()
    if not rows:
        raise ValueError(f'{label}: empty source')
    for n, line in enumerate(rows, 1):
        if not line.isascii() or len(line) > 71 or '\t' in line or line == '/*' or line.startswith('//'):
            raise ValueError(f'{label}:{n}: invalid IFOX card: {line!r}')
    return '\n'.join(rows) + '\n'


def single(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f'expected one token {old!r}, saw {text.count(old)}')
    return text.replace(old, new)


def sources(profile: str) -> dict[str, str]:
    if profile not in PROFILES:
        raise ValueError(f'unknown profile {profile}')
    job, expected, marker = PROFILES[profile]
    drv = (HERE / 'validator.asm').read_text('ascii')
    drv = single(drv, "DC    F'EXPCODE'", f"DC    F'{expected}'")
    drv = single(drv, "DC    CL80'PASSMARKER'", f"DC    CL80'{marker}'")
    if profile == 'regzero':
        drv = single(drv, 'L     9,=A(R0RE)', 'L     9,=A(R0RB)')
    if profile == 'regunal':
        drv = single(drv, 'L     8,=A(R0RB)', 'L     8,=A(R0RB+1)')
    reg = '\n'.join([
        '* R.0 TEST ONLY: INDEPENDENT REGISTRY CSECT, 44 BYTES.',
        'R0AREG   CSECT',
        '         ENTRY R0RB,R0RE',
        '         EXTRN R0PB,R0PE',
        "R0RB     DC    CL4'BCRG'",
        f"         DC    F'{2 if profile == 'regvers' else 1}'",
        "         DC    F'28'",
        f"         DC    F'{40 if profile == 'reglen' else 44}'",
        "         DC    F'1'",
        "         DC    F'1'",
        "         DC    F'0'",
        "         DC    A(R0PB)",
        '         DC    A(R0PB)' if profile == 'pkgbound' else '         DC    A(R0PE)',
        "         DC    CL8'PACKA   '",
        'R0RE     DS    0F',
        '         END   R0AREG',
    ])
    pkg = '\n'.join([
        '* R.0 TEST ONLY: INDEPENDENT DESCRIPTOR CSECT, 56 BYTES.',
        'R0APKG   CSECT',
        '         ENTRY R0PB,R0PE',
        '         EXTRN R0FUNC,R0FIN',
        "R0PB     DC    CL4'BCEX'",
        f"         DC    F'{2 if profile == 'pkgvers' else 1}'",
        "         DC    F'48'",
        f"         DC    F'{60 if profile == 'pkglen' else 56}'",
        "         DC    CL8'PACKA   '",
        "         DC    F'1'",
        "         DC    F'0'",
        "         DC    F'1'",
        ('         DC    A(R0FIN)' if profile == 'goodhook' else
         '         DC    A(R0FUNC)' if profile == 'badhook' else
         "         DC    F'0'"),
        "         DC    F'0'",
        "         DC    F'0'",
        "         DC    F'299'",
        "         DC    A(R0FUNC)",
        'R0PE     DS    0F',
        '         END   R0APKG',
    ])
    fun = (HERE / 'function.asm').read_text('ascii')
    result = dict(ASMD=checked_source(drv, 'validator'),
                  ASMR=checked_source(reg, 'registry'),
                  ASMP=checked_source(pkg, 'descriptor'),
                  ASMF=checked_source(fun, 'function'))
    verify_source_owners(result)
    return result


def verify_source_owners(src: dict[str, str]) -> None:
    """Reject substituted source ownership before any MVS submission.

    This is a controlled-source attest, not protection from a forged
    executable or from arbitrary memory pointers at runtime.
    """
    sections = dict(ASMD='R0ATST', ASMR='R0AREG',
                    ASMP='R0APKG', ASMF='R0AFUN')
    if set(src) != set(sections):
        raise ValueError('missing or unexpected assembly object')
    for step, section in sections.items():
        rows = src[step].splitlines()
        csects = [line[:8].strip() for line in rows if line[9:].startswith('CSECT')]
        if csects != [section]:
            raise ValueError(f'{step}: expected CSECT {section}, got {csects}')
    for symbol, owner in OWNERS.items():
        actual = []
        for step, content in src.items():
            labels = [line[:8].strip() for line in content.splitlines()
                      if line.startswith(symbol.ljust(8) + ' ') and
                      any(x in line[9:22] for x in ('CSECT', 'DC ', 'DS ', 'BR '))]
            actual.extend((sections[step], label) for label in labels)
        if actual != [(owner, symbol)]:
            raise ValueError(f'{symbol}: unexpected symbol ownership {actual}')
    for step, required in [('ASMR', 'ENTRY R0RB,R0RE'),
                           ('ASMP', 'ENTRY R0PB,R0PE'),
                           ('ASMF', 'ENTRY R0FUNC,R0FIN')]:
        if src[step].count(required) != 1:
            raise ValueError(f'{step}: missing or duplicated public symbols')
    if src['ASMD'].count('EXTRN R0RB,R0RE,R0PB,R0PE,R0FUNC,R0FIN') != 1:
        raise ValueError('validator references missing independent targets')


def asm_step(step: str, obj: str, text: str) -> list[str]:
    return [
        f'//{step:<8} EXEC PGM=IFOX00,REGION=256K,',
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
        *text.splitlines(),
        '/*',
    ]


def make_deck(profile: str, jobcard: list[str], src: dict[str, str] | None = None) -> str:
    job, _, marker = PROFILES[profile]
    if not jobcard or jobcard[0][2:10].rstrip() != job or not jobcard[0][10:].startswith(' JOB '):
        raise ValueError('unexpected job card')
    src = sources(profile) if src is None else src
    verify_source_owners(src)
    rows = [*jobcard, '//* R.0 A SOURCE-ATTESTED LINK: FOUR INDEPENDENT OBJECTS',
            '//* TEMP OBJECTS/LOAD ONLY; DO NOT MODIFY BOOT_OBJ']
    for step, obj in (('ASMD', 'R0DOBJ'), ('ASMR', 'R0ROBJ'),
                      ('ASMP', 'R0POBJ'), ('ASMF', 'R0FOBJ')):
        rows.extend(asm_step(step, obj, src[step]))
    rows += [
        '//LKED     EXEC PGM=IEWL,REGION=256K,',
        "//             PARM='NCAL,LIST,XREF,MAP',",
        '//             COND=((0,NE,ASMD),(0,NE,ASMR),',
        '//             (0,NE,ASMP),(0,NE,ASMF))',
        '//SYSLIN   DD  DSN=&&R0DOBJ,DISP=(OLD,DELETE)',
        '//         DD  DSN=&&R0ROBJ,DISP=(OLD,DELETE)',
        '//         DD  DSN=&&R0POBJ,DISP=(OLD,DELETE)',
        '//         DD  DSN=&&R0FOBJ,DISP=(OLD,DELETE)',
        '//         DD  *',
        ' ENTRY R0ATST',
        ' NAME R0ATRST(R)',
        '/*',
        '//SYSLMOD  DD  DSN=&&R0LOAD(R0ATRST),UNIT=SYSDA,',
        '//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)',
        '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))',
        '//SYSPRINT DD  SYSOUT=*',
        '//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,',
        '//             TIME=(,1),COND=(0,NE,LKED)',
        '//QOUT     DD  SYSOUT=*,',
        '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
        '//SYSUDUMP DD  SYSOUT=*',
        '//',
    ]
    for n, card in enumerate(rows, 1):
        if not card.isascii() or len(card) > 71 or '\t' in card:
            raise ValueError(f'invalid JCL card {n}: {card!r}')
    if rows.count('/*') != 5 or rows.count('//SYSIN    DD  *') != 4:
        raise ValueError('expected four IFOX source decks and one IEWL')
    if marker not in '\n'.join(rows):
        raise ValueError('missing exact GO QOUT marker')
    return '\n'.join(rows) + '\n'


def manifest(profile: str, src: dict[str, str], git_revision: str = 'owner-recorded-at-run') -> dict:
    return {'profile': profile, 'job_name': PROFILES[profile][0],
            'expected_internal_status': PROFILES[profile][1],
            'expected_actual_qout': PROFILES[profile][2],
            'github_revision': git_revision,
            'symbol_owner_expectations': OWNERS,
            'source_sha256': {step: hashlib.sha256(text.encode('ascii')).hexdigest()
                              for step, text in src.items()},
            'boundary': 'host-source attestation; actual MAP/XREF must be inspected'}


def config_module():
    s = importlib.util.spec_from_file_location('r0atrust_config', CORE)
    if s is None or s.loader is None:
        raise ValueError('cannot load local dspal config')
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('profile', choices=PROFILES)
    p.add_argument('--check', action='store_true', help='credential-free; writes no job')
    p.add_argument('--git-revision', help='source Git HEAD for audit manifest')
    a = p.parse_args()
    name = PROFILES[a.profile][0]
    src = sources(a.profile)
    if not a.check and not a.git_revision:
        p.error('--git-revision is required when generating JCL')
    if a.check:
        card = [f"//{name:<8} JOB (BCPL),'R0 A LINK',CLASS=A,MSGCLASS=A"]
    else:
        core = config_module()
        conf = core.load_config()
        card = core.authenticated_job_card(conf, name, 'R0 A LINK', redact_password=False)
    job = make_deck(a.profile, card, src)
    if a.check:
        print(f'CHECK R.0 A {a.profile}: {len(job.splitlines())} JCL cards; '
              'four source hashes; no credentials/JCL written')
        return
    OUT.mkdir(parents=True, exist_ok=True)
    deckpath = OUT / f'{name.lower()}.jcl'
    deckpath.write_text(job, encoding='ascii', newline='\n')
    deckpath.chmod(0o600)
    (OUT / f'{name.lower()}-sources.json').write_text(
        json.dumps(manifest(a.profile, src, a.git_revision), sort_keys=True, indent=2) + '\n',
        encoding='utf-8')
    print(f'Generated R.0 A test-only JCL: {deckpath}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f'R.0 A generation FAILED: {exc}')
