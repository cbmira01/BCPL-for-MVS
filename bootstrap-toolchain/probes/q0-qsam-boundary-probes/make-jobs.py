#!/usr/bin/env python3
"""Generate isolated Q.0 QSAM DASD F/FB boundary job from proven probes.

No existing repository files are modified. Generated JCL stays in workarea/.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT = HERE.parent / 'q0-qsam-dasd-probes' / 'make-jobs.py'

# profile: jobname, RECFM, LRECL, BLKSIZE, logical-record count
# Upper profiles are safe only after reviewing SYSDA allocation and device type.
PROFILES = {
    'f80': ('QS0F080', 'F', 80, 80, 23),
    'f1024': ('QS0F1K', 'F', 1024, 1024, 7),
    'fb8k': ('QS0B8K', 'FB', 80, 8000, 105),
    'fb16k': ('QS0B16K', 'FB', 80, 16000, 210),
}


def load_parent():
    if not PARENT.is_file():
        raise FileNotFoundError(f'Missing established Q.0 probe generator: {PARENT}')
    spec = importlib.util.spec_from_file_location('q0_dasd_existing', PARENT)
    if spec is None or spec.loader is None:
        raise RuntimeError('Unable to load existing generator')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def exactly(text: str, before: str, after: str, label: str) -> str:
    if text.count(before) != 1:
        raise ValueError(f'Unexpected {label}: expected one {before!r}, saw {text.count(before)}')
    return text.replace(before, after)


def asm_variation(original: str, profile: str, which: str) -> str:
    job, recfm, lrecl, blksize, count = PROFILES[profile]
    s = original
    expected = 1 if which == 'writer' else 2
    occurrences = s.count("=F'23'")
    if occurrences != expected:
        raise ValueError(
            f"Unexpected {which} record-count comparisons: "
            f"expected {expected}, found {occurrences}"
        )
    s = s.replace("=F'23'", f"=F'{count}'")
    if which == 'reader':
        s = exactly(s, "X'90'", "X'80'" if recfm == 'F' else "X'90'", 'effective RECFM')
        # Rewrite LRECL first: a revised BLKSIZE of 80 would otherwise
        # introduce a second =H'80' match during F80 generation.
        s = exactly(s, "=H'80'", f"=H'{lrecl}'", 'effective LRECL')
        s = exactly(s, "=H'800'", f"=H'{blksize}'", 'effective BLKSIZE')
        s = exactly(s, 'Q0 FB DASD 23 RECORDS PASS',
                    f'Q0 {profile.upper()} {count} RECORDS PASS', 'success marker')
    if lrecl != 80:
        if which == 'writer':
            s = exactly(s, "BLANKS   DC    CL80' '",
                        "BLANKS   DC    CL256' '", 'writer blanks')
        else:
            s = exactly(s, "BLANKS   DC    CL70' '",
                        "BLANKS   DC    CL256' '", 'reader blanks')
        s = exactly(s, 'AREA     DS    CL80', f'AREA     DS    CL{lrecl}', 'record area')
        s = exactly(s, 'AREA+79', f'AREA+{lrecl-1}', 'last byte')
        if which == 'writer':
            copies = [f'         MVC   AREA+{at}({min(256,lrecl-at)}),BLANKS'
                      for at in range(0, lrecl, 256)]
            copies[0] = copies[0].replace('         MVC', 'WLOOP    MVC', 1)
            s = exactly(s, 'WLOOP    MVC   AREA(80),BLANKS', '\n'.join(copies), 'fill full large record')
        else:
            n_blank = lrecl - 10  # first 8 bytes, sequence at +8, final byte
            compares = []
            for at in range(0, n_blank, 256):
                length = min(256, n_blank-at)
                compares.extend([
                    f'         CLC   AREA+{9+at}({length}),BLANKS',
                    '         BNE   FAILED',
                ])
            s = exactly(s, '         CLC   AREA+9(70),BLANKS\n         BNE   FAILED',
                        '\n'.join(compares), 'full large-record padding checks')
    for i, line in enumerate(s.splitlines(), 1):
        if not line.isascii() or len(line) > 71:
            raise ValueError(f'Invalid IFOX card ({which}, line {i}): {line!r}')
    return s


def create(profile: str, check: bool, allow_large: bool) -> Path | None:
    if profile == 'fb16k' and not allow_large:
        raise ValueError('fb16k requires --allow-large after confirming actual SYSDA volume geometry')
    base = load_parent()
    job, recfm, lrecl, block, count = PROFILES[profile]
    base.PROFILES[profile] = (job, 'fb-write.asm', 'fb-read.asm',
                              'Q0FBW', 'Q0FBR', recfm, lrecl, block)
    original_asm_source = base.asm_source

    def varying_source(name: str) -> str:
        original = original_asm_source(name)
        if name == 'fb-write.asm':
            return asm_variation(original, profile, 'writer')
        if name == 'fb-read.asm':
            return asm_variation(original, profile, 'reader')
        raise ValueError(f'Unexpected source {name!r}')

    base.asm_source = varying_source
    # Local credentials stay inside the generated JCL, never printed or tracked.
    conf = base.config_module().load_config()
    card = base.config_module().authenticated_job_card(
        conf, job, 'Q0 QSAM BOUNDARY', redact_password=False)
    deck = base.make_deck(profile, card)
    required = ['//ASMWR', '//ASMRD', '//LKWR', '//LKRD', '//WGO', '//RGO',
                'DSN=&&Q0DISK,DISP=(NEW,PASS)',
                'DSN=&&Q0DISK,DISP=(OLD,DELETE)',
                f'RECFM={recfm},LRECL={lrecl},BLKSIZE={block}',
                f"=F'{count}'"]
    for needle in required:
        if needle not in deck:
            raise AssertionError(f'Missing job component {needle}')
    if check:
        print(f'CHECK {profile.upper()}: structure/source OK, {len(deck.splitlines())} cards; no job submitted')
        return None
    output = ROOT / 'workarea/qsam-q0-boundary' / f'q0-{profile}.jcl'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(deck, encoding='ascii', newline='\n')
    output.chmod(0o600)
    print(f'Q.0 {profile.upper()} JCL: {output}')
    return output


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('profile', choices=sorted(PROFILES))
    ap.add_argument('--check', action='store_true', help='Validate but do not write JCL')
    ap.add_argument('--allow-large', action='store_true',
                    help='Acknowledge checking actual disk geometry for fb16k')
    args = ap.parse_args()
    create(args.profile, args.check, args.allow_large)


if __name__ == '__main__':
    main()
