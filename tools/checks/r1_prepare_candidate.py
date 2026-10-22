#!/usr/bin/env python3
"""Prepare an R.1 BCPLMAIN candidate without touching tracked source.

Requires the Git checkout at repository root, exactly the R.1 handoff
revision's BCPLMAIN anchors, and explicit --output. No Git writes or
MVS dataset updates. This script is intentionally guarded and idempotent.
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'bootstrap-toolchain/asm/bcplmain.asm'


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f'expected one BCPLMAIN anchor, found {count}: {old[:66]!r}')
    return text.replace(old, new)


def adapt(source: str) -> str:
    result = replace_once(
        source,
        '         EXTRN BLIB\n',
        '         EXTRN BLIB\n'
        '         EXTRN RGINIT,RGFINI\n',
    )
    result = replace_once(
        result,
        '         LA    11,SYSV\n         L     15,DYNWORK\n',
        '* R.1: CORE AND BLIB BINDING COMPLETE; VALIDATE BEFORE START.\n'
        '         ST    12,R1GVEC\n'
        '         LA    1,R1GVEC\n'
        '         L     15,=A(RGINIT)\n'
        '         BALR  14,15\n'
        '         LTR   15,15\n'
        '         BNZ   R1BAD\n'
        '         LA    11,SYSV\n'
        '         L     15,DYNWORK\n',
    )
    result = replace_once(
        result,
        'BADRETN  BAL   14,RELMEM\n',
        '* REGISTRATION REJECTION: IOINIT HAS RUN, BUT START HAS NOT.\n'
        '* IOFIN USES R10 AS A PRIVATE BASE. PRESERVE OUR BASE IN R9.\n'
        'R1BAD    LR    9,10\n'
        '         L     15,=A(IOFIN)\n'
        '         BALR  14,15\n'
        '         LR    10,9\n'
        '         BAL   14,RELMEM\n'
        '         L     13,4(13)\n'
        '         LM    14,12,12(13)\n'
        '         LA    15,12\n'
        '         BR    14\n'
        'BADRETN  BAL   14,RELMEM\n',
    )
    result = replace_once(
        result,
        'FINIMPL  XC    STOPRC(4),STOPRC\n'
        '         B     FINEXIT\n'
        'STOPENT  ST    7,STOPRC\n'
        'FINEXIT  LR    9,10\n'
        '         L     15,=A(IOFIN)\n',
        'FINIMPL  XC    STOPRC(4),STOPRC\n'
        '         XC    R1REAS(4),R1REAS\n'
        '         XC    R1CODE(4),R1CODE\n'
        '         B     FINEXIT\n'
        'STOPENT  ST    7,STOPRC\n'
        '         ST    7,R1CODE\n'
        '         LA    1,1\n'
        '         ST    1,R1REAS\n'
        'FINEXIT  LR    9,10\n'
        '* FINALIZERS FIRST; ERROR RAISES ORDINARY FINISH TO RC=8.\n'
        '         LA    1,R1REAS\n'
        '         L     15,=A(RGFINI)\n'
        '         BALR  14,15\n'
        '         LTR   15,15\n'
        '         BZ    R1FINOK\n'
        '         L     1,R1REAS\n'
        '         LTR   1,1\n'
        '         BNZ   R1FINOK\n'
        '         LA    1,8\n'
        '         ST    1,STOPRC\n'
        'R1FINOK  L     15,=A(IOFIN)\n',
    )
    result = replace_once(
        result,
        "STOPRC   DC    F'0'\n",
        "STOPRC   DC    F'0'\n"
        "R1GVEC   DC    F'0'\n"
        "R1REAS   DC    F'0'\n"
        "R1CODE   DC    F'0'\n",
    )
    if any(not line.isascii() or len(line) > 71 for line in result.splitlines()):
        raise ValueError('candidate BCPLMAIN contains non-IFOX-compatible cards')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify only')
    parser.add_argument('--output', type=Path, help='write candidate outside tracked sources')
    args = parser.parse_args()
    if not args.check and not args.output:
        parser.error('use --check or --output')
    data = SOURCE.read_text(encoding='ascii')
    candidate = adapt(data)
    if args.check:
        print('R.1 BCPLMAIN six-anchored adaptation: valid, no files written')
    if args.output:
        target = args.output.resolve()
        if target == SOURCE.resolve():
            raise ValueError('refusing to overwrite canonical BCPLMAIN')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(candidate, encoding='ascii', newline='\n')
        print(f'Wrote candidate: {target}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f'R.1 candidate preparation FAILED: {exc}')
