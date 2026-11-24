"""Reusable MVS release helpers, extracted from the BC0005-tested path.

No command-line entry point. Callers must establish candidate identity,
read-only preflight, authorization, exclusive intent and media safety.
Neither this module nor release.py is a complete live release producer.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import subprocess
import tempfile

from release import need, safe_dsn, MEMBER, VOLSER, UNIT, checked_lines, CODE

ROOT = Path(__file__).resolve().parents[2]
PROFILES = ('MR10', 'NATIVE', 'COMBINED')
MEMBERS = ('INSTALL', 'DATASETS', 'RELEASE', 'RESTORE', 'COPY', *PROFILES)
CANON = 'HERC02.BCPL.MR10KIT.'
DSN_LABEL = re.compile(r'[A-Z@$#][A-Z0-9@$#]{0,7}(?:\.[A-Z@$#][A-Z0-9@$#]{0,7})+\Z')
GUEST = re.compile(r'(?<![A-Z0-9])480[ \t]+3400[ \t]+(\S+)', re.I)
NEXT = re.compile(r'\b[0-9A-F]{3}[ \t]+[0-9A-F]{4}[ \t]+', re.I)
STEP = re.compile(r'^//([A-Z0-9]{2,8})\s+EXEC PGM=([A-Z0-9]+)\b', re.M)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def exclusive(path, data):
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, 'O_NOFOLLOW', 0)
    with os.fdopen(os.open(path, flags, 0o600), 'wb') as f:
        f.write(data); f.flush(); os.fsync(f.fileno())


def artifact(folder, name, data):
    need(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', name) is not None and
         folder.is_dir() and not folder.is_symlink(), 'unsafe evidence destination')
    exclusive(folder / name, data.encode('utf-8') if isinstance(data, str) else data)


def seal(folder):
    need(folder.is_dir() and not folder.is_symlink(), 'unsafe evidence directory')
    lines = []
    for p in sorted(folder.iterdir()):
        need(p.is_file() and not p.is_symlink() and p.name != 'SHA256SUMS' and
             re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', p.name), 'unsafe evidence member')
        lines.append(digest(p.read_bytes()) + '  ' + p.name + '\n')
    exclusive(folder / 'SHA256SUMS', ''.join(lines).encode('ascii'))


def run_command(folder, key, command, timeout=120):
    cp = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                        check=False, timeout=timeout)
    artifact(folder, key + '.txt', cp.stdout + ('\n' + cp.stderr if cp.stderr else ''))
    need(cp.returncode == 0 and bool(cp.stdout), key + ': host command failed')
    return cp.stdout


def jcl_control_cards(lines):
    """Return active JCL cards, excluding DD DATA,DLM=Z9 installer/source records."""
    outer = []
    in_data = False
    for number, line in enumerate(lines, 1):
        if in_data:
            if line == 'Z9':
                in_data = False
            continue
        need(line != 'Z9', f'orphan in-stream Z9 delimiter at record {number}')
        if line.startswith('//') and not line.startswith('//*'):
            need(len(line) <= 71,
                 f'JCL operands over column 71 at record {number} (width {len(line)})')
        outer.append(line)
        if line == '//SYSUT1 DD DATA,DLM=Z9':
            in_data = True
    need(not in_data, 'unterminated DD DATA,DLM=Z9')
    return outer


def submit_job(core, cfg, folder, key, name, body, expected, max_rc=0, *, description='BCPL DIST'):
    """Submit one authorized JES job and verify completion; never save the JOB card."""
    need(max_rc in (0, 8) and MEMBER.fullmatch(name), 'invalid job name or RC allowance')
    outer = jcl_control_cards(body.splitlines())
    need(body.endswith('//\n') and all(' JOB ' not in x for x in outer if x.startswith('//') and not x.startswith('//*')),
         'invalid or injected JOB card')
    need(all(len(x) <= 80 and all(' ' <= c <= '~' for c in x) for x in body.splitlines()), 'invalid FB80 records')
    artifact(folder, key+'-body.jcl', body)
    jobcard = core.authenticated_job_card(cfg, name, description, False)
    deck = '\n'.join(jobcard)+'\n'+body
    need(all(len(x) <= 71 for x in jobcard) and
         all(len(x) <= 80 for x in deck.splitlines()), 'job card overflow')
    oldtmp, oldenv = tempfile.tempdir, os.environ.get('TMPDIR')
    try:
        tempfile.tempdir = str(folder)
        os.environ['TMPDIR'] = str(folder)
        job, summary = core.submit_and_wait(
            cfg, deck, max_rc=max_rc, cursor_file=folder/(key+'-cursor.json'))
        artifact(folder, key+'-summary.txt', summary)
        report = core.job_report(job, cursor_file=folder/(key+'-cursor.json'))
        artifact(folder, key+'-report.txt', report)
    finally:
        tempfile.tempdir = oldtmp
        if oldenv is None:
            os.environ.pop('TMPDIR', None)
        else:
            os.environ['TMPDIR'] = oldenv
    need(re.search(rf'(?m)^JOB\s+{job}\s+{name}\s*$', summary) is not None and
         'JOB RESULT: SUCCESS' in summary, name+': JES completion not confirmed')
    actual = re.findall(r'(?m)^([A-Z][A-Z0-9]{1,7})\s+'
                        r'([A-Z][A-Z0-9]{1,7})\s+RC=(\d{4})\s*$', summary)
    if expected is not None:
        need(actual == [(a,b,'0000') for a,b in expected],
             name+': actual MVS step list/RC differs')
        for step, _ in expected:
            need(re.search(rf'(?m)^IEF142I\s+{name}\s+{step}\s+-\s+'
                           r'STEP WAS EXECUTED\s+-\s+COND CODE 0000\s*$',
                           report) is not None,
                 name+': IEF142I RC0000 missing for '+step)
    need(re.search(r'\b(IEF450I|IEF472I|IEA995I|ABEND)\b', report, re.I) is None,
         name+': system abend reported')
    return job, report, summary


def deck_without_job(deck, name):
    """Drop only the three trusted authenticated DSPAL JOB cards for re-use."""
    lines=deck.splitlines()
    need(name in ('DSPALLS', 'DSPALST') and len(lines)>=4 and lines[0].startswith('//'+name+' ') and
         lines[1].startswith('//             USER=') and
         lines[2].startswith('//             MSGLEVEL='),
         'unexpected authenticated inquiry deck')
    body = '\n'.join(lines[3:])+'\n'
    need(body.endswith(('/*\n','//\n')), 'unexpected DSPAL inquiry termination')
    return body if body.endswith('//\n') else body+'//\n'


def exact_listds(core, report, dsn):
    """Select only stand-alone exact DSN labels, never DSN-prefix results."""
    lines = report.replace('\r', '').splitlines()
    wanted = dsn.upper()
    candidates = []
    for index, line in enumerate(lines):
        if line.strip().upper() != wanted:
            continue
        block = [line.rstrip()]
        for following in lines[index + 1:]:
            token = following.strip().upper()
            if (DSN_LABEL.fullmatch(token) or
                token.startswith(('IEF','JES2.JOB','$HASP')) or
                re.search(r"\bLISTDS\s+'", token)):
                break
            block.append(following.rstrip())
            if len(block) >= 24:
                break
        if not any('RECFM' in text.upper() and 'DSORG' in text.upper() for text in block):
            continue
        actual = core.parse_listds(block)
        required = ('volume','dsorg','recfm','lrecl','blksize')
        if all(actual.get(k) is not None for k in required):
            candidates.append((actual, block))
    need(candidates, 'exact MVS LISTDS label/DCB missing for: ' + dsn)
    attrs, block = candidates[-1]
    need(all(a == attrs for a, _ in candidates),
         'contradictory duplicate exact LISTDS entries for: ' + dsn)
    return attrs, block


def verify_inventory(core,cfg,ls,folder,label,rows,*,volume):
    """Read-only catalog and exact PDS directory/DCB verification."""
    names=[r[1] for r in rows]
    need(names and len(set(names))==len(names) and all(safe_dsn(n) for n in names), 'invalid inventory names')
    body=deck_without_job(core.stat_deck(cfg,names), 'DSPALST')
    cat,report,_=submit_job(core,cfg,folder,label+'-catalog',
                             'DSPALST',body,[('STAT','IKJEFT01')])
    for n,dsn,*rest in rows:
        dcb={'recfm':'FB','lrecl':80,'blksize':800} if n==2 else rest[1]
        actual,_=exact_listds(core,report,dsn)
        expect={'volume':volume,'dsorg':'PO','recfm':dcb['recfm'],
                'lrecl':str(dcb['lrecl']),'blksize':str(dcb['blksize'])}
        need(all(actual.get(k)==v for k,v in expect.items()),
             label+': recipient MVS DCB/volume differs: '+dsn)
    directory_deck=deck_without_job(ls.list_members_deck(cfg,names), 'DSPALLS')
    job,report,_=submit_job(core,cfg,folder,label+'-directory',
                             'DSPALLS',directory_deck,[('LIST','IKJEFT01')])
    blocks=ls.member_blocks(report,names)
    need(set(blocks)==set(names),label+': MVS PDS directory incomplete')
    count=0
    for n,dsn,members,*_ in rows:
        actual=ls.parse_members(blocks[dsn])
        need(len(actual)==len(set(actual)) and set(actual)==set(members)
             and len(actual)==len(members),
             label+': member directory mismatch: '+dsn)
        count+=len(actual)
    return cat,job,count


def stage_deck(bt1,members,*,stage,dasd):
    need(stage.endswith('.') and safe_dsn(stage+'BT0001') and safe_dsn(stage+'BT0002') and re.fullmatch(r'[A-Z0-9]{6}', dasd), 'invalid staging DSN or DASD volume')
    need(set(members)==set(MEMBERS), 'installer member set differs')
    lines=["//* BCPL BOOTSTRAP AND INSTALLER STAGING; NEW TARGETS ONLY."]
    def data(text):
        content=text.splitlines()
        need(content and all(not x.startswith("Z9") for x in content),
             "empty input or DD DATA delimiter collision")
        return ["//SYSUT1 DD DATA,DLM=Z9",*content,"Z9"]
    lines += ["//B0001 EXEC PGM=IEBGENER,REGION=512K",
              "//SYSPRINT DD SYSOUT=*","//SYSIN DD DUMMY",*data(bt1),
              "//SYSUT2 DD DSN="+stage+"BT0001,",
              "//            DISP=(NEW,CATLG,DELETE),UNIT=SYSDA,",
              "//            VOL=SER="+dasd+",SPACE=(TRK,(5,1)),",
              "//            DCB=(DSORG=PS,RECFM=FB,LRECL=80,BLKSIZE=800)",
              "//A0002 EXEC PGM=IEFBR14,COND=(0,NE)",
              "//OUTPDS DD DSN="+stage+"BT0002,",
              "//            DISP=(NEW,CATLG,DELETE),UNIT=SYSDA,",
              "//            VOL=SER="+dasd+",SPACE=(TRK,(50,5,15)),",
              "//            DCB=(DSORG=PO,RECFM=FB,LRECL=80,BLKSIZE=800)"]
    for i,member in enumerate(MEMBERS,1):
        lines.extend([f"//M{i:04d} EXEC PGM=IEBGENER,REGION=512K,COND=(0,NE)",
                      "//SYSPRINT DD SYSOUT=*","//SYSIN DD DUMMY",
                      *data(members[member]),
                      "//SYSUT2 DD DSN="+stage+f"BT0002({member}),",
                      "//            DISP=SHR"])
    lines.append("//")
    outer=jcl_control_cards(lines)
    need(len([x for x in outer if " EXEC PGM=IEBGENER" in x])==9 and
         len([x for x in outer if x=="//SYSUT1 DD DATA,DLM=Z9"])==9 and
         sum("DISP=(NEW,CATLG,DELETE)" in x for x in outer)==2,
         "staging steps or new allocation count changed")
    need(all(len(x)<=80 and all(' ' <= c <= '~' for c in x) for x in lines), 'invalid FB80 data cards')
    return '\n'.join(lines)+'\n'


def bootstrap_decks(prefix, *, volser, tape_unit, dasd_unit, dasd_vol):
    """External bootstrap and BT0002 restore; generated from accepted JCL."""
    need(safe_dsn(prefix+'.DIST.INST') and VOLSER.fullmatch(volser) and
         UNIT.fullmatch(tape_unit) and MEMBER.fullmatch(dasd_unit) and
         re.fullmatch(r'[A-Z0-9]{6}', dasd_vol) and dasd_vol!=volser, 'invalid bootstrap target or unit')
    boot = "//* BCPL READ BT0001 ON AN UNINSTALLED MVS SYSTEM.\n//* ADD SITE JOB CARD; MOUNT <VOL>.\n//BOOTREAD EXEC PGM=IEBGENER,REGION=256K\n//SYSPRINT DD SYSOUT=*\n//SYSIN DD DUMMY\n//SYSUT1 DD DSN=BCPL.BT0001,UNIT=<TAPE>,\n//            VOL=(PRIVATE,RETAIN,SER=<VOL>),\n//            LABEL=(1,SL),DISP=OLD\n//SYSUT2 DD SYSOUT=*\n//\n"
    bt2 = "//* BCPL RESTORE <VOL> BT0002 INSTALLER PDS.\n//* ADD SITE JOB CARD.\n//* OUTPUT MUST BE ABSENT; NO OVERWRITE OR RETRY.\n//BT2REST EXEC PGM=IEBCOPY,REGION=512K\n//SYSPRINT DD SYSOUT=*\n//INTAPE DD DSN=BCPL.BT0002,UNIT=<TAPE>,\n//            VOL=(PRIVATE,RETAIN,SER=<VOL>),\n//            LABEL=(2,SL),DISP=OLD\n//OUTPDS DD DSN=<PREFIX>.DIST.INST,\n//            DISP=(NEW,CATLG,DELETE),UNIT=<DASD>,\n//            VOL=SER=<DVOL>,SPACE=(TRK,(20,5,10)),\n//            DCB=(DSORG=PO,RECFM=FB,LRECL=80,BLKSIZE=800)\n//SYSUT3 DD UNIT=SYSDA,SPACE=(TRK,(10,5))\n//SYSUT4 DD UNIT=SYSDA,SPACE=(TRK,(10,5))\n//SYSIN DD *\n COPY OUTDD=OUTPDS,INDD=INTAPE\n/*\n//\n"
    def render(body):
        body = (body.replace('<VOL>',volser).replace('<PREFIX>',prefix)
                .replace('<TAPE>',tape_unit).replace('<DASD>',dasd_unit)
                .replace('<DVOL>',dasd_vol))
        return checked_lines(body.splitlines())
    return render(boot), render(bt2)


def readback_deck(prefix,member):
    need(member in PROFILES,"unexpected requested on-tape profile")
    name=prefix+".DIST.INST"
    need(safe_dsn(name), 'invalid installer readback DSN')
    steps=[("P0001",member),("P0002","COPY")]
    lines=["//* MVS IEBGENER READS ACTUAL TAPE-RESTORED JCL DATA."]
    for step,item in steps:
        lines.extend([
            f"//{step} EXEC PGM=IEBGENER,REGION=512K",
            "//SYSPRINT DD SYSOUT=*",
            "//SYSIN DD DUMMY",
            f"//SYSUT1 DD DSN={name}({item}),",
            "//            DISP=SHR",
            "//SYSUT2 DD SYSOUT=*",
        ])
    lines.append("//")
    return checked_lines(lines)


def extract_profile(report,canonical):
    """Extract exact profile JCL cards, in order, from printed MVS SYSOUT."""
    lines=canonical.splitlines()
    need(lines and lines[-1]=="//","canonical on-tape profile termination missing")
    extracted=[]
    index=0
    for physical in report.splitlines():
        if index==len(lines):break
        expected=lines[index]
        candidate=physical.rstrip(" \r\n")
        if candidate.endswith(expected):
            extracted.append(candidate[len(candidate)-len(expected):])
            index+=1
    need(index==len(lines) and extracted==lines,
         f"MVS SYSOUT printed only {index}/{len(lines)} "
         "canonical on-tape profile records (no unsafe submission)")
    return "\n".join(extracted)+"\n"


def profile_result(name,report,summary,positions):
    """Check actual MVS/IEBCOPY procedure steps, regardless of JES PROC prefix."""
    need(MEMBER.fullmatch(name) and positions and "JOB RESULT: SUCCESS" in summary and
         "HIGHEST RC: 0000" in summary and
         re.search(r"\b(?:ABEND|IEF450I|IEF472I|IEA995I)\b",report,re.I) is None,
         "MVS tape-resident procedure failed or abended: "+name)
    entries=re.findall(
        rf"(?m)^IEF142I\s+{name}\s+(.+?)\s+-\s+"
        r"STEP WAS EXECUTED\s+-\s+COND CODE (\d{4})\s*$",report)
    steps=[]
    for field,rc in entries:
        names=[word for word in re.split(r"[\s.]+",field)
               if re.fullmatch(r"R\d{4}",word)]
        need(len(names)==1,
             "ambiguous MVS in-stream PROC step identity for "+name)
        steps.append((names[0],rc))
    need(steps==[(f"R{n:04d}","0000") for n in positions],
         "actual IEF142I tape-resident PROC step list/RC differs: "+name)
    return len(steps)


def parse_mvs(output: str) -> str:
    """Inspect the established TK5 unit 480 console contract."""
    occurrences = [(line, match.start(), match.group(1).upper())
                   for line in output.splitlines()
                   for match in GUEST.finditer(line)]
    distinct = set(occurrences)
    need(len(distinct) == 1, 'MVS 480/3400 row missing, duplicated differently or ambiguous')
    line, start, state = next(iter(distinct))
    need(state in ('O', 'O-NRD'), 'MVS 480 not online/empty-compatible: ' + state)
    tail = line[start:]
    next_unit = NEXT.search(tail, 3)
    if next_unit is not None:
        tail = tail[:next_unit.start()]
    need(re.search(r'\b(?:ALLOC|ALLOCATED|BUSY)\b', tail, re.I) is None,
         'MVS 480 appears allocated/busy')
    return state


def drive_state(hercules, guest, allowed_images):
    """Return EMPTY or the exact allowlisted mounted image; refuse unknown media."""
    rows = re.findall(r'\bHHC02279I\s+(?:[0-9A-Fa-f]+:)?0480\s+3420\s+(.*)',hercules)
    need(len(rows)==1 and 'busy' not in rows[0].lower(), 'ambiguous/busy tape drive')
    state = parse_mvs(guest)
    if re.match(r'\*\s',rows[0]):
        need(state=='O-NRD', 'empty tape not confirmed by MVS')
        return 'EMPTY'
    names = [n for n in allowed_images if re.search(r'(?<![A-Za-z0-9_.-])'+re.escape(n)+r'(?![A-Za-z0-9_.-])',rows[0])]
    need(state=='O' and len(names)==1, 'foreign or non-idle media; refusing to displace')
    return names[0]


def volser_from_hetmap(report: str) -> str:
    """Identify physical VOL1, not a DATA SET serial in HDR1 or EOF1."""
    labels = list(re.finditer(r"(?m)^Label\s+: '([A-Z0-9]{4})'\s*$", report))
    need(labels and labels[0].group(1) == 'VOL1' and
         sum(m.group(1) == 'VOL1' for m in labels) == 1,
         'HETMAP missing, repeated or displaced physical VOL1 label')
    end = labels[1].start() if len(labels) > 1 else len(report)
    chunk = report[labels[0].end():end]
    serials = re.findall(r"(?m)^Volume Serial\s+: '([A-Z0-9]{1,6})'\s*$", chunk)
    need(len(serials) == 1, 'HETMAP physical VOL1 serial missing/duplicated')
    return serials[0]


def verify_codes(report, expected):
    codes = [int(c) for c in CODE.findall(report)]
    need(codes == [0] * expected,
         f'interpreted ICINT19 CODE contract failed: {len(codes)}/{expected}')
    return codes


def verify_demos(report, selection, steps):
    codes = verify_codes(report, sum(p == 'ICINT19' for _, p in steps))
    demo = [x.strip() for x in report.splitlines() if 'DEMO:' in x]
    need(len(demo) == len(selection),
         f'demo output count differs: {len(demo)}/{len(selection)}')
    need(not any('ABEND' in x.upper() for x in demo),
         'demo application reported abend')
    return {'run_cases': list(selection), 'interpreted_zero_codes': len(codes),
            'demo_print_records': demo}


def cards(body):
    lines = body.splitlines()
    need(bool(lines) and body.endswith('\n') and body.isascii(), 'invalid MVS deck encoding')
    need(all('\t' not in x and len(x) <= 80 for x in lines), 'MVS FB80 card overflow')
    need(all(len(x) <= 71 for x in lines if x.startswith('//') and
             not x.startswith('//*')), 'MVS JCL control column overflow')
    need(not any(' JOB ' in x for x in lines if x.startswith('//') and
                 not x.startswith('//*')), 'injected JOB card')
    need(not any('<' in x or '>' in x for x in lines if x.startswith('//') and
                 not x.startswith('//*')), 'unresolved JCL placeholder')
    return body


def read_cards(report, canonical):
    """Recover ordered exact card text from MVS print; refuse missing cards."""
    expected = canonical.rstrip('\n').splitlines()
    need(expected and all(x.strip() for x in expected), 'unexpected blank canonical card')
    actual = []
    for line in report.splitlines():
        if len(actual) == len(expected):
            break
        card = expected[len(actual)].rstrip()
        if line.rstrip().endswith(card):
            actual.append(card)
    need(actual == [x.rstrip() for x in expected], 'incomplete MVS JCL member readback')
    return '\n'.join(actual) + '\n'


def suite_deck(body, prefix, count, allowed):
    """Bind trusted MR10 suite JCL to an explicitly allowlisted recipient."""
    need(safe_dsn(prefix+'.MR10KIT.LOAD') and allowed and
         all(safe_dsn(n) and n.startswith(prefix+'.') for n in allowed), 'invalid MR10 namespace or allowlist')
    target = prefix + '.MR10KIT.'
    body = body.replace(CANON, target).rstrip('\n') + '\n'
    if not body.endswith('//\n'):
        body += '//\n'
    cards(body)
    steps = STEP.findall(body)
    need(len(steps) == count and len(set(s for s, _ in steps)) == count and
         all(p in ('IEBGENER', 'ICINT19') for _, p in steps) and
         sum(p == 'IEBGENER' for _, p in steps) == 5, 'unexpected MR10 step sequence')
    need(body.count('DSN=' + target + 'LOAD') == count - 5 and CANON not in body and
         'DISP=(NEW,CATLG' not in body and 'DISP=MOD' not in body, 'unsafe MR10 deck')
    dsns = re.findall(r'\bDSN=([A-Z0-9@$#.&]+)', body)
    need(dsns and all(d.startswith('&&') or d in allowed for d in dsns), 'foreign MR10 dataset')
    lines = body.splitlines()
    for index, line in enumerate(lines):
        match = re.search(r'\bDSN=([A-Z0-9@$#.&]+)', line)
        if match and not match.group(1).startswith('&&'):
            need('DISP=SHR' in line or (line.endswith(',') and index+1<len(lines) and
                 re.fullmatch(r'//\s+DISP=SHR', lines[index+1])), 'persistent MR10 DD not SHR')
    return body, steps
