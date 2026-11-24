#!/usr/bin/env python3
"""Offline MVS tape JCL and saved-evidence checks. Never submits or mounts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

MEMBER = re.compile(r'[A-Z@$#][A-Z0-9@$#]{0,7}\Z')
VOLSER = re.compile(r'BC(?!0000)[0-9]{4}\Z')
CANDIDATE = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,47}\Z')
UNIT = re.compile(r'[0-9A-F]{3,4}\Z')
LABEL = re.compile(r"(?m)^Label\s+: '([A-Z0-9]{4})'\s*$")
FILE = re.compile(r'(?m)^File\s+#\s*:\s*(\d+)\s*$')
BLOCKS = re.compile(r'(?m)^Blocks\s*:\s*(\d+)\s*$')
SUMMARY = re.compile(r'(?m)^Summary\s*:\s*$')
RECORD = re.compile(r"(?m)^([A-Za-z ]+?)\s+: '([^']*)'\s*$")
CODE = re.compile(r'EXECUTION CYCLES\s*=.*?,\s*CODE\s*=\s*(-?\d+)', re.I)
TITLE = re.compile(r'\bWRITEF\s*\(\s*"TEST:\s*([^"\r\n]*?)\*N"', re.I)
MR10_CASES = ('scalar-vector', 'bytes', 'integer-arithmetic', 'branches-loops',
              'nested-recursion', 'separate-module', 'basic-library',
              'library-scalars', 'library-strings', 'library-line-io',
              'getvec-reuse', 'basic-coroutine')
PROFILES = {'mr10-only': ('MR10', 'M10PROC'),
            'native-only': ('NATIVE', 'NATPROC'), 'combined': ('COMBINED', 'ALLPROC')}


class Refusal(ValueError):
    pass


def need(ok, why):
    if not ok:
        raise Refusal(why)


def safe_dsn(value):
    return (isinstance(value, str) and 3 <= len(value) <= 44 and
            all(MEMBER.fullmatch(s) for s in value.split('.')))


def checked_lines(lines):
    need(all(isinstance(s, str) and len(s) <= 80 and
             all(' ' <= ch <= '~' for ch in s) for s in lines),
         'generated JCL is not ASCII FB80-safe')
    need(all(len(s) <= 71 for s in lines if s.startswith('//') and
             not s.startswith('//*')), 'JCL operation extends beyond column 71')
    return '\n'.join(lines) + '\n'


def identity(manifest):
    candidate = manifest['release']['candidate_id']
    volser = manifest['volume']['volser']
    entries = manifest['datasets']
    need(isinstance(candidate, str) and CANDIDATE.fullmatch(candidate), 'invalid candidate ID')
    need(isinstance(volser, str) and VOLSER.fullmatch(volser), 'invalid production VOLSER')
    need(isinstance(entries, list) and 1 <= len(entries) <= 9999 and
         all(type(row.get('sequence')) is int and row['sequence'] == i
             for i, row in enumerate(entries, 1)), 'noncontiguous logical tape sequence')
    return candidate, volser, entries


def render_write_jcl(manifest, *, unit='480', legacy_header=False):
    """Deterministic JOB-less SL tape write deck; source DSNs must be explicit."""
    candidate, vol, entries = identity(manifest)
    need(isinstance(unit, str) and UNIT.fullmatch(unit), 'invalid tape unit')
    lines = [f'//* {"TA.2 " if legacy_header else ""}FROZEN CANDIDATE {candidate}',
             '//* GENERATOR OUTPUT ONLY; NO JOB CARD; MVS VERIFICATION REQUIRED.',
             '//* NO CATALOGED TAPE DSNS. STOP ON ANY AMBIGUOUS FAILURE.']
    seen = set()
    for i, row in enumerate(entries, 1):
        source = row.get('producer_source_dsn')
        need(safe_dsn(source) and source not in seen and not source.startswith('BCPL.BT'),
             'invalid, repeated or tape-alias source DSN')
        seen.add(source)
        kind = row['kind']
        last = i == len(entries)
        retain = '' if last else 'RETAIN,'
        label = f'BCPL.BT{i:04d}'
        cond = '' if i == 1 else ',COND=(0,NE)'
        pgm = 'IEBGENER' if i == 1 else 'IEBCOPY'
        lines.extend([f'//T{i:04d} EXEC PGM={pgm},REGION=512K{cond}',
                      '//SYSPRINT DD SYSOUT=*'])
        if i == 1:
            need(kind == 'sequential_text', 'first tape dataset is not bootstrap')
            lines.extend(['//SYSIN DD DUMMY', f'//SYSUT1 DD DSN={source},',
                          '//            DISP=SHR'])
        else:
            need(kind == 'pds_unload', 'non-bootstrap tape dataset is not IEBCOPY')
            lines.extend([f'//INPDS DD DSN={source},', '//            DISP=SHR'])
        outdd = 'SYSUT2' if i == 1 else 'OUTTAPE'
        lines.extend([f'//{outdd} DD DSN={label},UNIT={unit},',
                      f'//            VOL=(PRIVATE,{retain}SER={vol}),',
                      f'//            LABEL=({i},SL),DISP=(NEW,KEEP,KEEP)' + (',' if i == 1 else '')])
        if i == 1:
            lines.append('//            DCB=(DSORG=PS,RECFM=FB,LRECL=80,BLKSIZE=800)')
        else:
            lines.extend(['//SYSUT3 DD UNIT=SYSDA,SPACE=(TRK,(10,5))',
                          '//SYSUT4 DD UNIT=SYSDA,SPACE=(TRK,(10,5))',
                          '//SYSIN DD *', ' COPY OUTDD=OUTTAPE,INDD=INPDS'])
            members = row.get('members')
            need(isinstance(members, list) and members and
                 all(isinstance(m, str) and MEMBER.fullmatch(m) for m in members) and
                 len(set(members)) == len(members), 'invalid SELECT member list')
            lines.extend(f' SELECT MEMBER=({m})' for m in members)
            lines.append('/*')
    lines.append('//')
    return checked_lines(lines)


def profile_positions(manifest, profile):
    _, _, rows = identity(manifest)
    need(profile in PROFILES and profile in manifest['profiles'], 'unknown installation profile')
    groups = manifest['profiles'][profile]
    need(isinstance(groups, list) and groups and all(isinstance(g, str) for g in groups),
         'invalid profile groups')
    positions = tuple(r['sequence'] for r in rows[2:] if r['group'] in groups)
    need(positions and all(g in {r['group'] for r in rows} for g in groups), 'empty or unknown profile group')
    return positions


def render_install_jcl(manifest, sizes, profile, *, hlq, site, tape_unit, dasd_unit, dasd_vol):
    """RC4-style PROC after BT0002 restoration; no JOB card or live action."""
    candidate, vol, rows = identity(manifest)
    positions = profile_positions(manifest, profile)
    label, proc = PROFILES[profile]
    need(all(isinstance(s, str) and MEMBER.fullmatch(s) for s in (hlq, site, dasd_unit)) and
         isinstance(tape_unit, str) and UNIT.fullmatch(tape_unit) and
         isinstance(dasd_vol, str) and re.fullmatch(r'[A-Z0-9]{6}', dasd_vol) and dasd_vol != vol,
         'invalid site, unit or DASD volume')
    lines = [f'//* {candidate} {vol} MVS-ONLY {label} INSTALL.',
             '//* SUPPLY AN AUTHORIZED JOB CARD BEFORE THESE RECORDS.',
             '//* DEFAULT HLQ/SITE/UNIT/VOLUME ARE OVERRIDABLE ON //GO EXEC.',
             '//* TARGETS MUST NOT EXIST: NO RESTART, SCRATCH OR OVERWRITE.',
             f'//{proc} PROC HLQ={hlq},SITE={site},TU={tape_unit},DU={dasd_unit},',
             f'//             DV={dasd_vol}']
    targets = set()
    for n in positions:
        row = rows[n-1]
        target = row['target_dsn_template']
        need(row['kind'] == 'pds_unload' and target.startswith('{HLQ}.BCPL.'), 'unsafe target template')
        suffix = target[len('{HLQ}.BCPL.'):]
        actual = f'{hlq}.BCPL.{site}.{suffix}'
        need(safe_dsn(actual) and suffix != 'DIST.INST' and actual not in targets, 'invalid or repeated target DSN')
        targets.add(actual)
        allocation = sizes.get(n)
        need(isinstance(allocation, (list, tuple)) and len(allocation) == 3 and
             all(type(x) is int and x > 0 for x in allocation), 'missing or invalid allocation')
        p, s, b = allocation
        dcb = row['target_dcb']
        if dcb == {'dsorg': 'PO', 'recfm': 'U', 'lrecl': 0, 'blksize': 6144}:
            dcb_lines = ['//            DCB=(DSORG=PO,RECFM=U,BLKSIZE=6144)']
        elif dcb == {'dsorg': 'PO', 'recfm': 'FB', 'lrecl': 80, 'blksize': 800}:
            dcb_lines = ['//            DCB=(DSORG=PO,RECFM=FB,LRECL=80,', '//            BLKSIZE=800)']
        else:
            raise Refusal('unsupported recipient DCB; new MVS verification required')
        cond = '' if n == positions[0] else ',COND=(0,NE)'
        lines.extend([f'//R{n:04d} EXEC PGM=IEBCOPY,REGION=512K{cond}',
                      '//SYSPRINT DD SYSOUT=*', f'//INTAPE DD DSN=BCPL.BT{n:04d},UNIT=&TU,',
                      f'//            VOL=(PRIVATE,RETAIN,SER={vol}),', f'//            LABEL=({n},SL),DISP=OLD',
                      f'//OUTPDS DD DSN=&HLQ..BCPL.&SITE..{suffix},',
                      '//            DISP=(NEW,CATLG,DELETE),UNIT=&DU,', '//            VOL=SER=&DV,',
                      f'//            SPACE=(TRK,({p},{s},{b})),', *dcb_lines,
                      '//SYSUT3 DD UNIT=SYSDA,SPACE=(TRK,(10,5))',
                      '//SYSUT4 DD UNIT=SYSDA,SPACE=(TRK,(10,5))',
                      '//SYSIN DD DSN=&HLQ..BCPL.&SITE..DIST.INST(COPY),', '//         DISP=SHR'])
    lines += ['// PEND', f'//GO EXEC {proc}', '//']
    return checked_lines(lines)


def labels_report(report, *, volser, count):
    need(isinstance(volser, str) and VOLSER.fullmatch(volser) and
         type(count) is int and 1 <= count <= 9999, 'invalid expected tape identity')
    matches = list(LABEL.finditer(report))
    want = ['VOL1'] + ['HDR1', 'HDR2', 'EOF1', 'EOF2'] * count
    need([m.group(1) for m in matches] == want, 'standard-label sequence/count differs')
    chunks = [report[m.end():matches[i+1].start() if i+1 < len(matches) else len(report)]
              for i, m in enumerate(matches)]
    need(dict(RECORD.findall(chunks[0])).get('Volume Serial') == volser,
         'VOL1 does not identify the reserved candidate volume')
    names = []
    for n in range(1, count+1):
        index = 1 + (n-1)*4
        name = f'BCPL.BT{n:04d}'
        for offset in (0, 2):
            record = dict(RECORD.findall(chunks[index+offset]))
            need(record.get('Dataset ID', '').strip() == name and
                 record.get('Dataset Sequence') == f'{n:04d}' and
                 record.get('Volume Serial') == volser, f'{name}: HDR1/EOF1 DSN, sequence or volume mismatch')
        names.append(name)
    return {'volser': volser, 'logical_datasets': count, 'dataset_names': names, 'label_records': len(want)}


def files_report(report, *, count):
    need(type(count) is int and 1 <= count <= 9999, 'invalid expected dataset count')
    summary = list(SUMMARY.finditer(report))
    need(len(summary) == 1, 'HETMAP -f summary missing/repeated')
    body, footer = report[:summary[0].start()], report[summary[0].end():]
    rows = list(FILE.finditer(body))
    need(len(rows) == count*3+1 and not FILE.search(footer),
         f'physical tape files differ: expected {count*3+1}, observed {len(rows)}')
    counts = []
    for i, m in enumerate(rows):
        end = rows[i+1].start() if i+1 < len(rows) else len(body)
        blocks = list(BLOCKS.finditer(body, m.end(), end))
        need(int(m.group(1)) == i+1 and len(blocks) == 1,
             'HETMAP file number/block count missing, repeated or out of order')
        counts.append(int(blocks[0].group(1)))
    footer_files = re.findall(r'(?m)^Files\s*:\s*(\d+)\s*$', footer)
    footer_blocks = re.findall(r'(?m)^Blocks\s*:\s*(\d+)\s*$', footer)
    need(len(footer_files) == len(footer_blocks) == 1 and int(footer_files[0]) == len(counts) and
         int(footer_blocks[0]) == sum(counts), f'HETMAP summary Files/Blocks does not reconcile with {count*3+1} physical files')
    for n in range(count):
        header, data, trailer = counts[3*n:3*n+3]
        need(header == (3 if n == 0 else 2) and data > 0 and trailer == 2,
             f'BCPL.BT{n+1:04d}: unexpected header, empty data or trailer file')
    need(counts[-1] == 0, 'no terminal empty tape file')
    return counts


def evaluate_hetmap(labels, files, *, volser, count):
    result = labels_report(labels, volser=volser, count=count)
    blocks = files_report(files, count=count)
    payload = [blocks[3*n+1] for n in range(count)]
    result.update(physical_files=len(blocks), payload_blocks=sum(payload), payload_blocks_by_dataset=payload,
                  qualification='AWS label and physical-file structure only; not MVS restore or member bytes')
    return result


def source_file(root, relative):
    need(relative and not relative.startswith('/') and '..' not in relative.split('/'), 'unsafe manifest path')
    path = root / relative
    need(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root.resolve()),
         'canonical manifest file missing')
    return path


def read_mr10_panel(root, manifest, jcl, expected=MR10_CASES):
    body = jcl.read_text(encoding='ascii')
    rows = []
    for raw in manifest.read_text(encoding='utf-8').splitlines():
        if not raw or raw.startswith('#'):
            continue
        fields = raw.split('\t')
        need(len(fields) == 7, 'regression manifest field count changed')
        name, _, src, _, _, golden, exit_code = fields
        need(len(rows) < len(expected) and name == expected[len(rows)] and exit_code == '0',
             'MR10 regression panel order or interpreted code changed')
        match = TITLE.search(source_file(root, src).read_text(encoding='ascii'))
        need(match is not None, 'BCPL TEST title absent: ' + name)
        records = [line.rstrip() for line in source_file(root, golden).read_text(encoding='utf-8').splitlines()]
        need(records and all(line.startswith('RP:') for line in records), 'golden RP records invalid: ' + name)
        need(f'//* EXECUTE CASE {len(rows)+1:02d}: {name}' in body, 'MVS regression JCL order differs: ' + name)
        rows.append({'step': f'R{len(rows)+1:02d}', 'name': name, 'title': match.group(1).strip(),
                     'golden': records, 'expected_code': int(exit_code)})
    need(rows and len(rows) == len(expected), 'MR10 panel case count differs')
    return rows


def line_value(line, prefix):
    pos = line.find(prefix)
    return line[pos:].rstrip() if pos >= 0 else None


def inspect_mr10(report, cases):
    """Exact ordered TEST/RP/EXP/CODE comparison; no JES or release sign-off."""
    need(bool(cases), 'empty MR10 case definitions')
    seen, orphan, current = [], [], None
    for raw in report.splitlines():
        if (value := line_value(raw, 'TEST:')) is not None:
            current = {'title': value[5:].strip(), 'rp': [], 'exp': [], 'codes': []}
            seen.append(current)
            continue
        for prefix in ('RP', 'EXP'):
            if (value := line_value(raw, prefix + ':')) is not None:
                if current is None:
                    orphan.append(prefix)
                else:
                    current[prefix.lower()].append(value)
        match = CODE.search(raw)
        if match is not None and current is not None:
            current['codes'].append(int(match.group(1)))
    results = []
    for i, definition in enumerate(cases):
        actual = seen[i] if i < len(seen) else None
        checks = {'test_identity': bool(actual and actual['title'] == definition['title']),
                  'rp_matches_golden': bool(actual and actual['rp'] == definition['golden']),
                  'interpreted_code_zero': bool(actual and actual['codes'] == [definition['expected_code']]),
                  'exp_present': bool(actual and actual['exp']),
                  'exp_matches_golden': bool(actual and actual['exp'] ==
                      [line.replace('RP:', 'EXP:', 1) for line in definition['golden']])}
        results.append({'step': definition['step'], 'name': definition['name'], 'expected_test': definition['title'],
                        'actual_test': None if actual is None else actual['title'], 'golden_rp': definition['golden'],
                        'actual_rp': [] if actual is None else actual['rp'], 'printed_exp': [] if actual is None else actual['exp'],
                        'interpreted_codes': [] if actual is None else actual['codes'], 'checks': checks,
                        'golden_and_code_match': all(checks[k] for k in ('test_identity', 'rp_matches_golden', 'interpreted_code_zero'))})
    complete = len(seen) == len(cases) and not orphan and all(r['golden_and_code_match'] for r in results)
    invalid = any(r['checks']['exp_present'] and not r['checks']['exp_matches_golden'] for r in results)
    exp_complete = complete and not invalid and all(r['checks']['exp_matches_golden'] for r in results)
    return {'status': ('MVS_MR10_SEMANTIC_COMPARISON_FAIL' if not complete or invalid else
                       'EXP_RP_CODE_COMPARISON_PASS' if exp_complete else 'GOLDEN_RP_CODE_MATCH_EXP_REQUIRED'),
            'observed_test_count': len(seen), 'orphan_print_records': orphan, 'cases': results,
            'golden_rp_and_code_match': complete, 'exp_contract_met': exp_complete}


def read_manifest(path):
    import yaml
    try:
        m = yaml.safe_load(path.read_text(encoding='utf-8'))
    except yaml.YAMLError as exc:
        raise Refusal('invalid YAML manifest') from exc
    candidate, _, rows = identity(m)
    v = m['volume']
    need(m.get('schema_version') == 1 and m.get('phase') == 'candidate' and
         v.get('format') == 'aws' and v.get('labeling') == 'SL' and v.get('volume_ordinal') == 1 and
         v.get('registry_reservation') == candidate, 'unsupported release manifest')
    need(len(rows) >= 3 and rows[0]['kind'] == 'sequential_text' and
         rows[0]['target_dcb'] == {'dsorg': 'PS', 'recfm': 'FB', 'lrecl': 80, 'blksize': 800} and
         rows[1]['kind'] == 'pds_unload' and 'COPY' in rows[1]['members'] and
         all(row['kind'] == 'pds_unload' for row in rows[1:]), 'unsupported bootstrap/installer layout')
    return m


def read_map(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            need(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    raw = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)
    need(isinstance(raw, dict) and all(re.fullmatch(r'[1-9][0-9]{0,3}', k) for k in raw), 'invalid sequence map')
    return {int(k): v for k, v in raw.items()}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    subs = p.add_subparsers(dest='command', required=True)
    w = subs.add_parser('write-jcl', help='render a JOB-less writer; no submission')
    w.add_argument('--manifest', type=Path, required=True)
    w.add_argument('--source-map', type=Path, required=True)
    w.add_argument('--unit', required=True)
    i = subs.add_parser('install-jcl', help='render an installer profile after BT0002 restore')
    i.add_argument('--manifest', type=Path, required=True)
    i.add_argument('--allocations', type=Path, required=True)
    i.add_argument('--profile', choices=PROFILES, required=True)
    for option in ('hlq', 'site', 'tape-unit', 'dasd-unit', 'dasd-vol'):
        i.add_argument('--' + option, required=True)
    h = subs.add_parser('review-tape', help='compare saved HETMAP reports with manifest')
    h.add_argument('--manifest', type=Path, required=True)
    h.add_argument('--labels', type=Path, required=True)
    h.add_argument('--files', type=Path, required=True)
    r = subs.add_parser('review-mr10', help='compare saved JES report with checked-in goldens')
    r.add_argument('--report', type=Path, required=True)
    r.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    a = p.parse_args(argv)
    try:
        if a.command == 'review-mr10':
            cases = read_mr10_panel(a.root, a.root/'mr10-kit-compiler/tests/00-regression-panel/manifest.tsv',
                                    a.root/'mr10-kit-compiler/jcl/run-regression-tests.jcl')
            result = inspect_mr10(a.report.read_text(encoding='utf-8'), cases)
            print(json.dumps(result, indent=2))
            return 0 if result['exp_contract_met'] else 2
        m = read_manifest(a.manifest)
        _, vol, rows = identity(m)
        if a.command == 'write-jcl':
            mapping = read_map(a.source_map)
            need(set(mapping) == set(range(1, len(rows)+1)), 'source map must cover exact tape sequence')
            for row in rows:
                row['producer_source_dsn'] = mapping[row['sequence']]
            print(render_write_jcl(m, unit=a.unit), end='')
        elif a.command == 'install-jcl':
            mapping = read_map(a.allocations)
            need(set(mapping) == set(range(3, len(rows)+1)), 'allocation map must cover exact payload sequence')
            print(render_install_jcl(m, mapping, a.profile, hlq=a.hlq, site=a.site, tape_unit=a.tape_unit,
                                     dasd_unit=a.dasd_unit, dasd_vol=a.dasd_vol), end='')
        else:
            result = evaluate_hetmap(a.labels.read_text(encoding='utf-8'), a.files.read_text(encoding='utf-8'),
                                     volser=vol, count=len(rows))
            print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError) as exc:
        print('REFUSED: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
