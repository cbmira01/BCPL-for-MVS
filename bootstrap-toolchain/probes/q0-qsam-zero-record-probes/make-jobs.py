#!/usr/bin/env python3
"""Generate isolated Q.0 V/VB zero-payload RDW probes from proven parent sources."""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT = HERE.parent / 'q0-qsam-dasd-probes' / 'make-jobs.py'
PROFILES = {'vzero': ('QS0VZER', 'V', 100, 104),
            'vbzero': ('QS0VBZER', 'VB', 100, 404)}


def replace_once(s, old, new):
    assert s.count(old) == 1, (old, s.count(old))
    return s.replace(old, new)


def modify_writer(s):
    # Last logical record consists of RDW only: total length 4, payload 0.
    s = replace_once(s, "DC    H'16',H'36',H'100'\nAREA", "DC    H'16',H'36',H'4'\nAREA")
    return s


def modify_reader(s, profile):
    s = replace_once(s, "RLOOP    GET   QDCB,AREA\n",
                     "RLOOP    GET   QDCB,AREA\n"
                     "         L     3,RECCNT\n"
                     "         C     3,=F'14'\n"
                     "         BE    ZEROREC\n")
    s = replace_once(s, "         LA    3,1(3)\n         ST    3,RECCNT",
                     "         B     RECOK\n"
                     "ZEROREC LH    2,AREA\n"
                     "         CH    2,=H'4'\n"
                     "         BNE   FAILED\n"
                     "         CLC   AREA+2(2),ZERO2\n"
                     "         BNE   FAILED\n"
                     "         L     3,RECCNT\n"
                     "RECOK    LA    3,1(3)\n"
                     "         ST    3,RECCNT")
    s = replace_once(s, "DC    H'16',H'36',H'100'\nAREA", "DC    H'16',H'36',H'4'\nAREA")
    s = replace_once(s, "Q0 VARIABLE 15 RECORDS PASS",
                     f"Q0 {profile.upper()} 15 RECORDS PASS")
    return s


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('profile', choices=PROFILES)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    spec = importlib.util.spec_from_file_location('q0_base', PARENT)
    if spec is None or spec.loader is None:
        raise RuntimeError('Parent generator unavailable')
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    job, recfm, lrecl, blksize = PROFILES[args.profile]
    base.PROFILES[args.profile] = (job, 'v-write.asm', 'v-read.asm',
                                   'Q0VW', 'Q0VR', recfm, lrecl, blksize)
    original = base.asm_source

    def source(name):
        s = original(name)
        if name == 'v-write.asm':
            s = modify_writer(s)
        elif name == 'v-read.asm':
            s = modify_reader(s, args.profile)
        else:
            raise ValueError(name)
        for n, line in enumerate(s.splitlines(), 1):
            if not line.isascii() or len(line) > 71:
                raise ValueError(f'Bad assembler card {name}:{n} {line!r}')
        return s

    base.asm_source = source
    core = base.config_module()
    config = core.load_config()
    card = core.authenticated_job_card(config, job, 'Q0 ZERO RDW', redact_password=False)
    deck = base.make_deck(args.profile, card)
    for mandatory in (f'RECFM={recfm},LRECL=100,BLKSIZE={blksize}',
                      "H'16',H'36',H'4'", "CH    2,=H'4'",
                      'ZEROREC', 'EODAD=ATEND', f'Q0 {args.profile.upper()} 15 RECORDS PASS'):
        if mandatory not in deck:
            raise AssertionError(mandatory)
    if args.check:
        print(f'CHECK {args.profile.upper()}: structure/source OK, {len(deck.splitlines())} cards; no JCL written')
        return
    path = ROOT / 'workarea/qsam-q0-zero' / f'q0-{args.profile}.jcl'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(deck, encoding='ascii', newline='\n')
    path.chmod(0o600)
    print(f'Q.0 {args.profile.upper()} JCL: {path}')

if __name__ == '__main__':
    main()
