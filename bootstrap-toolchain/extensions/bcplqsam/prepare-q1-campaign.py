#!/usr/bin/env python3
"""Prepare Q.1 test-only four-case native lifecycle campaign; never submit JES.

Q16FIN/Q16STP: 16 independent temporary F1024 datasets, explicit GO DCB.
Q1NEG: arguments/missing DD/invalid handles, no QSAM allocation.
Q1OUT: QOUT output OPEN/INFO/CLOSE, no record write.
Each job has isolated assembler/link/GO steps, accepted Runtime Extensions
selection, native GO REGION=256K and no permanent dataset operations.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / 'workarea/bcplqsam-q1'
PROFILE = {'finish': ('Q16FIN', 'test-q1-finish.bcpl'),
           'stop': ('Q16STP', 'test-q1-stop.bcpl'),
           'negative': ('Q1NEG', 'test-q1-negative.bcpl'),
           'output': ('Q1OUT', 'test-q1-output.bcpl')}
DCB = '//             DCB=(RECFM=F,LRECL=1024,BLKSIZE=1024)'
GO = '//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,'
WGO = '//WGO      EXEC PGM=*.LKWR.SYSLMOD,REGION=256K,'


def module(filename: str):
    p = HERE / filename
    spec = importlib.util.spec_from_file_location(filename.replace('-', '_'), p)
    if spec is None or spec.loader is None:
        raise ValueError('missing source-controlled helper: ' + filename)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def replace_one(rows: list[str], old: str, new: str):
    if rows.count(old) != 1:
        raise ValueError('expected exactly one card: ' + old)
    rows[rows.index(old)] = new


def span(rows: list[str], step: str):
    indices = [i for i, r in enumerate(rows)
               if r.startswith(f'//{step:<8} EXEC ')]
    if len(indices) != 1:
        raise ValueError('expected exactly one step: ' + step)
    start = indices[0]
    nexts = [i for i in range(start+1, len(rows))
             if re.match(r'^//[A-Z0-9]{1,8} +EXEC ', rows[i])]
    end = nexts[0] if nexts else len(rows)
    return start, end


def source_span(rows: list[str], step: str):
    a, b = span(rows, step)
    openings = [i for i in range(a, b) if rows[i] == '//SYSIN    DD  *']
    endings = [i for i in range(a, b) if rows[i] == '/*']
    if len(openings) != 1 or len(endings) != 1 or openings[0] >= endings[0]:
        raise ValueError('one in-stream assembler source required: ' + step)
    return openings[0]+1, endings[0]


def verify(rows: list[str], job: str, profile: str):
    if not rows or not re.match(rf'^//{job}\s+JOB\b', rows[0]):
        raise ValueError('incorrect JOB card')
    if rows.count(GO) != 1 or rows.count('         BCXREQ BCPLQSAM') != 1:
        raise ValueError('missing GO / BCX selection')
    if rows.count('//SYSIN    DD  *') != (6 if profile in ('finish','stop') else 5):
        raise ValueError('assembler count incorrect')
    if rows.count('/*') != (8 if profile in ('finish','stop') else 6):
        raise ValueError('in-stream boundary count incorrect')
    if rows.count(' ENTRY R0APP') != 1 or rows.count(f' NAME {job}(R)') != 1:
        raise ValueError('incorrect application entry/link-name')
    for i, r in enumerate(rows, 1):
        if not r.isascii() or len(r) > 71 or '\t' in r:
            raise ValueError(f'invalid card {i}: {r!r}')
        if ('CATLG' in r or 'DISP=MOD' in r or '//EXTLIB' in r or
            (r.startswith('//') and 'BOOT_DEVOBJ' in r)):
            raise ValueError('permanent operation forbidden')
    if profile in ('finish', 'stop'):
        if rows.count(WGO) != 1 or rows.count(DCB) != 32:
            raise ValueError('writer/reader geometry missing')
        for i in range(16):
            wr = f'//Q{i:02d}      DD  DSN=&&Q1H{i:02d},DISP=(NEW,PASS),'
            rd = f'//Q{i:02d}      DD  DSN=&&Q1H{i:02d},DISP=(OLD,DELETE),'
            if rows.count(wr) != 1 or rows.count(rd) != 1:
                raise ValueError('missing distinct temporary DD: '+str(i))
            if rows[rows.index(rd)+1] != DCB:
                raise ValueError('reader DCB missing: '+str(i))
            if not rows.index(WGO) < rows.index(wr) < rows.index(GO) < rows.index(rd):
                raise ValueError('DD attached to wrong step')
    else:
        if any(r.startswith('//WGO ') for r in rows):
            raise ValueError('non-lifecycle case must not write input')
        if profile == 'negative' and any(r.startswith('//Q00 ') for r in rows):
            raise ValueError('negative case cannot OPEN QSAM')
        if profile == 'output':
            qout = '//QOUT     DD  DSN=&&Q1OUT,DISP=(NEW,DELETE),'
            if rows.count(qout) != 1 or rows[rows.index(qout)+2] != DCB:
                raise ValueError('QOUT dataset/geometry missing')
    return '\n'.join(rows) + '\n'


def make_deck(profile: str, generated: str, jobcard: list[str], obj_dsn: str):
    if profile not in PROFILE:
        raise ValueError('unknown profile')
    job = PROFILE[profile][0]
    if not jobcard or not re.match(rf'^//{job}\s+JOB\b', jobcard[0]):
        raise ValueError('incorrect authenticated JOB header')
    if profile in ('finish', 'stop'):
        three = module('prepare-q1-3dd.py')
        rows = three.make_deck(
            generated, ["//Q13DD JOB (BCPL),'Q1 TEMPLATE',CLASS=A"],
            obj_dsn).splitlines()
        rows[0:1] = jobcard
        replace_one(rows, ' NAME Q13DD(R)', f' NAME {job}(R)')
        replace_one(rows, '//SYSLMOD  DD  DSN=&&Q1LOAD(Q13DD),',
                    f'//SYSLMOD  DD  DSN=&&Q1LOAD({job}),')
        # Change only the ASMWR source.  Reuse accepted 16-DCB writer.
        writer = three.q0_writer_helper()
        left, right = source_span(rows, 'ASMWR')
        rows[left:right] = writer.make_source(16, False).splitlines()
        # Rebuild WGO-to-GO DD interval; keep original EXEC guards.
        wgo, _ = span(rows, 'WGO')
        go = rows.index(GO)
        writer_first = next(i for i in range(wgo, go)
                            if rows[i].startswith('//Q00      DD'))
        dump = next(i for i in range(writer_first, go)
                    if rows[i] == '//SYSUDUMP DD  SYSOUT=*')
        new_writer = []
        for n in range(16):
            new_writer.extend([
                f'//Q{n:02d}      DD  DSN=&&Q1H{n:02d},DISP=(NEW,PASS),',
                '//             UNIT=SYSDA,SPACE=(TRK,(2,1)),', DCB])
        rows[writer_first:dump] = new_writer
        go = rows.index(GO)
        end = next(i for i in range(go+1, len(rows))
                   if rows[i].startswith('//SYSPRINT DD '))
        first_go_dd = next(i for i in range(go+1, end)
                           if rows[i].startswith('//Q00      DD '))
        reader = []
        for n in range(16):
            reader.extend([
                f'//Q{n:02d}      DD  DSN=&&Q1H{n:02d},DISP=(OLD,DELETE),',
                DCB])
        rows[first_go_dd:end] = reader
    else:
        query = module('prepare-q1-query.py')
        rows = query.make_deck(
            generated, ["//Q1QUERY JOB (BCPL),'Q1 TEMPLATE',CLASS=A"],
            obj_dsn).splitlines()
        rows[0:1] = jobcard
        replace_one(rows, ' NAME Q1QUERY(R)', f' NAME {job}(R)')
        replace_one(rows, '//SYSLMOD  DD  DSN=&&Q1LOAD(Q1QUERY),',
                    f'//SYSLMOD  DD  DSN=&&Q1LOAD({job}),')
        if profile == 'output':
            go = rows.index(GO)
            rows[go+2:go+2] = [
                '//QOUT     DD  DSN=&&Q1OUT,DISP=(NEW,DELETE),',
                '//             UNIT=SYSDA,SPACE=(TRK,(2,1)),', DCB]
    return verify(rows, job, profile)


def allowed_generated(path: Path):
    p = path.resolve()
    if (ROOT / 'workarea').resolve() not in p.parents or not p.is_file():
        raise ValueError('generated assembler must exist under workarea')
    return p


def prepare(profile: str, generated: Path):
    query = module('prepare-q1-query.py')
    core = query.time_helper().trailer_helper().load_core()
    config = core.load_config()
    spec = config['datasets']['BOOT_OBJ']
    if (spec.get('content_type') != 'object' or spec.get('dsorg') != 'PO'
        or spec.get('recfm') != 'FB' or int(spec.get('lrecl', 0)) != 80):
        raise ValueError('BOOT_OBJ is not approved FB80 object PDS')
    job = PROFILE[profile][0]
    jobcard = core.authenticated_job_card(config,job,'Q1 BATCH',
                                           redact_password=False)
    content = make_deck(profile, allowed_generated(generated).read_bytes().decode('latin-1'),
                        jobcard, core.full_dsn(config, spec))
    WORK.mkdir(parents=True, exist_ok=True)
    target = WORK / f'q1-campaign-{profile}.jcl'
    fd = os.open(target, os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as f:
        f.write(content)
    return target, hashlib.sha256(content.encode('ascii')).hexdigest(),len(content.splitlines())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    p.add_argument('--profile', choices=PROFILE)
    p.add_argument('--generated', type=Path)
    a = p.parse_args()
    if a.check:
        if a.profile or a.generated:
            p.error('--check does not accept --profile/--generated')
        query = module('prepare-q1-query.py')
        sample = query.time_helper().trailer_helper().sample_generated()
        for profile,(job,_) in PROFILE.items():
            deck = make_deck(profile, sample,
                             [f"//{job} JOB (BCPL),'Q1 CHECK',CLASS=A"],
                             'HERC02.BCPL.BOOT.OBJ')
            print(f'PASS: {job} {profile} {len(deck.splitlines())} cards; no JES')
        return
    if not a.profile or not a.generated:
        p.error('--profile and --generated required')
    target, checksum, cards = prepare(a.profile,a.generated)
    print(f'PREPARED ONLY: {target} ({cards} cards)')
    print(f'SHA-256: {checksum}; no JES submission or installed changes')

if __name__ == '__main__':
    try:main()
    except (OSError,ValueError,UnicodeError) as e:
        raise SystemExit('Q.1 campaign preparation FAILED: '+str(e))
