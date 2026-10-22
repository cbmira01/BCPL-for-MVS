#!/usr/bin/env python3
"""Read accepted R.1 BCPLMAIN or adapt a historical base source.

Requires the Git checkout at repository root, exactly the R.1 handoff
revision's BCPLMAIN anchors, and explicit --output. No Git writes or
MVS dataset updates. This script is intentionally guarded and idempotent.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'bootstrap-toolchain/asm/bcplmain.asm'


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f'expected one BCPLMAIN anchor, found {count}: {old[:66]!r}')
    return text.replace(old, new)


# R.1-private provenance tags: 1=application, 2=BLIB, 4=Core.
# The bitmap is an internal witness, not a new public registration ABI.
CORE_START = 'BLIDONE  L     4,4(12)\n'
CORE_END = '         ST    1,120(12)\n'


def add_owner_ledger(result: str) -> str:
    result = replace_once(
        result,
        '         BCT   1,GINIT\n',
        '         BCT   1,GINIT\n'
        '* ZERO ALL PRIVATE PER-GLOBAL OWNER BITS BEFORE IMPORTING.\n'
        '         L     4,=A(R1OWNB)\n'
        '         XC    0(256,4),0(4)\n'
        '         XC    256(256,4),256(4)\n'
        '         XC    512(188,4),512(4)\n',
    )
    for label, tag in [('GINST', '01'), ('BLIMP', '02')]:
        # Unique importing store; leave both original trailer walkers intact.
        if label == 'GINST':
            old = '         ST    9,0(2)\n         BC    15,GINST\n'
        else:
            old = '         ST    9,0(2)\n         B     BLIMP\n'
        result = replace_once(result, old,
            '         ST    9,0(2)\n'
            '         LR    4,1\n'
            '         SRL   4,2\n'
            '         L     2,=A(R1OWNB)\n'
            '         AR    2,4\n'
            f"         OI    0(2),X'{tag}'\n" +
            ('         BC    15,GINST\n' if label=='GINST' else
             '         B     BLIMP\n'))
    # Each native direct store is recorded, including conditional G!76.
    if result.count(CORE_START) != 1 or result.count(CORE_END) != 1:
        raise ValueError('expected exact core ownership boundary')
    before, body = result.split(CORE_START, 1)
    core, after = body.split(CORE_END, 1)
    block = CORE_START + core + CORE_END
    matches = []
    def rewrite(match):
        offset = int(match.group(2))
        if offset % 4 or offset == 0 or offset > 2796:
            raise ValueError(f'invalid native owner slot: {offset}')
        matches.append(offset//4)
        return (match.group(0) + '\n'
                '         L     8,=A(R1OWNB)\n'
                f"         OI    {offset//4}(8),X'04'")
    block = re.sub(r'^         ST    ([0-9]+),([0-9]+)\(12\)$',
                   rewrite, block, flags=re.M)
    required = {6,52,53,54,55,11,16,17,39,33,13,15,42,41,
                12,47,46,14,76,85,86,87,88,150,40,30}
    if set(matches) != required:
        raise ValueError(f'native owner writer census changed: '
                         f'{set(matches)^required}')
    result = before + block + after
    return replace_once(result,
        "R1CODE   DC    F'0'\n",
        "R1CODE   DC    F'0'\n"
        '         DS    0F\n'
        'R1OWNB   DS    CL700\n')


def adapt(source: str) -> str:
    # Canonical BCPLMAIN includes the accepted R.1 integration.
    # Continue to support historical pre-integration source fixtures.
    if '         EXTRN RGINIT,RGFINI\n' in source:
        for marker in ('R1GVEC   DC', 'R1OWNB   DS',
                       'R1BAD    LR', 'R1FINOK  L'):
            if source.count(marker) != 1:
                raise ValueError('partially integrated BCPLMAIN: '+marker)
        return source
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
        "R1OWNP   DC    A(R1OWNB)\n"
        "R1REAS   DC    F'0'\n"
        "R1CODE   DC    F'0'\n",
    )
    result = add_owner_ledger(result)
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
        print('R.1 BCPLMAIN integration: valid, no files written')
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
