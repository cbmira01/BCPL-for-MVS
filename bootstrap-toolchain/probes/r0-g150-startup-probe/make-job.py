#!/usr/bin/env python3
"""Build a test-only G!150 startup-owner observation with installed BOOT_OBJ."""
from __future__ import annotations

import argparse
import importlib.util
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / 'workarea/runtime-extensions-r0-g150'
TRAIL = HERE.parent / 'r0-export-trailer-probe/make-job.py'
HELPER = ROOT / 'bootstrap-toolchain/regression/prepare-native-global.py'
JOB = 'R0G150'
MEMBERS = ('BCPLMAIN', 'BCPLIO', 'BCPLMEM', 'BCPLBYTE', 'BCPLAPT', 'BLIB')


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f'unavailable helper {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def application_source(generated: str) -> list[str]:
    trail = load(TRAIL, 'r0g150trail')
    helper = load(HELPER, 'r0g150helper')
    rows = trail.application_source(generated)
    start, limit, pairs = helper.find_trailer(rows)
    if pairs != [(4, '0+L1')] and not (
        len(pairs) == 1 and pairs[0][0] == 4 and
        re.fullmatch(r'L\d+|\d+\+L\d+', pairs[0][1])
    ):
        raise ValueError('CG370 application must export START G!1 only')
    if limit < 4 or limit > 2796 or limit % 4:
        raise ValueError('invalid original CG370 global limit')
    if rows.count('         ENTRY R0APP') != 1:
        raise ValueError('expected one relocated R0APP entry')
    rows.insert(rows.index('         ENTRY R0APP') + 1,
                '         EXTRN R0MARK,R0CK15')
    start, limit, pairs = helper.find_trailer(rows)
    last = helper.one_index(rows, helper.L998, 'L998')
    pairs += [(600, 'R0MARK'), (604, 'R0CK15')]
    replacement = [f"         DC F'{max(limit, 604)}'", "         DC F'0'"]
    for byte_offset, addr in pairs:
        replacement += [f"         DC F'{byte_offset}'", f'         DC A({addr})']
    rows[start:last] = replacement
    return trail.checked_asm('\n'.join(rows), 'G150 application')


def checked_observer(observer: str) -> list[str]:
    trail = load(TRAIL, 'r0g150cards')
    rows = trail.checked_asm(observer, 'G150 observer')
    executable = '\n'.join(row for row in rows if not row.startswith('*'))
    required = ('R0O150   CSECT', '         ENTRY R0MARK,R0CK15',
                '         EXTRN BLIB', "         L     7,600(12)",
                '         L     8,=A(R0MARK)', '         CR    7,8',
                "         C     7,=X'C7D3F258'",
                '         L     8,=A(BLIB)', "         C     7,=F'600'",
                'R0ACT    L     7,600(12)',
                'R0APPV   L     7,=A(R0MARK)',
                '         END   R0O150')
    if any(executable.count(part) != 1 for part in required):
        raise ValueError('observer lacks required independent ownership checks')
    if not rows[-1] == '         END   R0O150':
        raise ValueError('wrong observer end')
    if any(re.search(r'\bST\s+\d+,600\(12\)', line) for line in rows):
        raise ValueError('G150 observer must not write global slot')
    return rows


def make_deck(jobcard: list[str], generated: str, observer: str,
              obj_dsn: str) -> str:
    trail = load(TRAIL, 'r0g150job')
    if not jobcard or jobcard[0].split()[:2] != ['//R0G150', 'JOB']:
        raise ValueError('expected authenticated R0G150 job card')
    if not re.fullmatch(r'[A-Z0-9@#$]+(?:\.[A-Z0-9@#$]+)+', obj_dsn):
        raise ValueError('invalid installed object dataset')
    if not obj_dsn.endswith('.BOOT.OBJ'):
        raise ValueError('unexpected BOOT_OBJ dataset')
    cards = [*jobcard, '//* R.0 G150 OWNER: OBSERVE ONLY; BOOT_OBJ READ ONLY']
    cards += trail.asm_step('ASMA', 'R0AOBJ', application_source(generated))
    cards += trail.asm_step('ASMP', 'R0POBJ', checked_observer(observer))
    cards += [
        '//LKED     EXEC PGM=IEWL,REGION=256K,',
        "//             PARM='NCAL,LIST,XREF,MAP',",
        '//             COND=((0,NE,ASMA),(0,NE,ASMP))',
        f'//OBJ      DD  DSN={obj_dsn},DISP=SHR',
        '//SYSLIN   DD  DSN=&&R0AOBJ,DISP=(OLD,DELETE)',
        '//         DD  DSN=&&R0POBJ,DISP=(OLD,DELETE)',
        '//         DD  *',
        *(f' INCLUDE OBJ({name})' for name in MEMBERS),
        ' ENTRY R0APP',
        ' NAME R0G150(R)',
        '/*',
        '//SYSLMOD  DD  DSN=&&R0LOAD(R0G150),UNIT=SYSDA,',
        '//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)',
        '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))',
        '//SYSPRINT DD  SYSOUT=*',
        '//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,',
        '//             TIME=(,2),COND=(0,NE,LKED)',
        '//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,',
        '//             BLKSIZE=132)',
        '//SYSUDUMP DD  SYSOUT=*',
        '//',
    ]
    for number, row in enumerate(cards, 1):
        if len(row) > 71 or not row.isascii() or '\t' in row:
            raise ValueError(f'invalid JCL line {number}: {row!r}')
    if cards.count('/*') != 3:
        raise ValueError('require two assembler and one IEWL control streams')
    permanent = [row for row in cards if 'DSN=' in row and '&&' not in row
                 and 'SYS1.MACLIB' not in row]
    if permanent != [f'//OBJ      DD  DSN={obj_dsn},DISP=SHR']:
        raise ValueError('accepted permanent dataset cannot be written')
    if any(row == ' INCLUDE OBJ(R0O150)' for row in cards):
        raise ValueError('observer must resolve from temp object')
    return '\n'.join(cards) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--generated', type=Path)
    args = parser.parse_args()
    if not args.check and args.generated is None:
        parser.error('--generated required unless --check')
    trail = load(TRAIL, 'r0g150cli')
    generated = (args.generated.read_bytes().decode('latin-1')
                 if args.generated else trail.sample_generated())
    observer = (HERE / 'observer.asm').read_text('ascii')
    if args.check:
        card = ["//R0G150  JOB (BCPL),'G150 OWNER',CLASS=A,MSGCLASS=A"]
        obj_dsn = 'HERC02.BCPL.BOOT.OBJ'
    else:
        core = trail.load_core()
        cfg = core.load_config()
        spec = cfg['datasets']['BOOT_OBJ']
        if (spec.get('content_type') != 'object' or spec.get('dsorg') != 'PO'
                or spec.get('recfm') != 'FB' or int(spec.get('lrecl', 0)) != 80):
            raise ValueError('BOOT_OBJ must be FB/80 object PDS')
        card = core.authenticated_job_card(cfg, JOB, 'R0 G150 OWNER',
                                           redact_password=False)
        obj_dsn = core.full_dsn(cfg, spec)
    deck = make_deck(card, generated, observer, obj_dsn)
    if args.check:
        print(f'CHECK R.0 G150: {len(deck.splitlines())} cards; '
              'no credentials, writes or MVS submission')
    else:
        WORK.mkdir(parents=True, exist_ok=True)
        dest = WORK / 'r0-g150.jcl'
        dest.write_text(deck, 'ascii', newline='\n')
        dest.chmod(0o600)
        print(f'Generated test-only JCL: {dest}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit(f'R.0 G150 generator FAILED: {exc}')
