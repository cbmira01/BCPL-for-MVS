"""Strict verification of MVS reconstruction payload and installed members.

Consumes independent job-summary and dump-report-for-job output.  A launcher
RC, job-wide highest RC, or a member inventory alone cannot satisfy a job.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping


class VerificationError(RuntimeError):
    pass


ASM_CORE = ('ASMMMAIN', 'ASMMMEM', 'ASMMBYTE', 'ASMMAPT', 'ASMMIO', 'ASMRGS', 'ASMREG')
PUT_CORE = ('PUTMAIN', 'PUTMEM', 'PUTBYTE', 'PUTAPT', 'PUTIO', 'PUTRGS', 'PUTREG')
CAMBRIDGE_PHASES = tuple(step for number in range(1, 12)
                         for step in (f'C{number:02d}CMP', f'C{number:02d}CG'))
EXPECTED_STEPS: dict[str, tuple[str, ...]] = {
    'IC19BLD': ('ASM', 'LKED', 'SAVEOBJ'),
    'CAMBBLD': (*CAMBRIDGE_PHASES, 'PACKCOMP'),
    'BLDBMAIN': (*ASM_CORE, *PUT_CORE),
    'BLIBBLD': ('COMP', 'PREPASM', 'PREPLK', 'FIXASM', 'ASMBLIB', 'INSTALL'),
    'BCPLDEMO': ('ASMDEMO', 'PUTDEMO', 'READBACK', 'VERIFY'),
    'BCPLTIME': ('ASMTIME', 'PUTTIME', 'READBACK', 'VERIFY'),
    'BCPLQSAM': ('ASMQ', 'PUTQSAM', 'READBACK', 'VERIFY'),
}
EXPECTED_PROGRAMS = {
    'IC19BLD': {'ASM': 'IFOX00', 'LKED': 'IEWL', 'SAVEOBJ': 'IEBGENER'},
    'CAMBBLD': {**{x: 'ICINT19' for x in CAMBRIDGE_PHASES}, 'PACKCOMP': 'IEBGENER'},
    'BLDBMAIN': {**{x: 'IFOX00' for x in ASM_CORE}, **{x: 'IEBGENER' for x in PUT_CORE}},
    'BLIBBLD': {'COMP': 'ICINT19', 'PREPASM': 'IFOX00', 'PREPLK': 'IEWL',
                'ASMBLIB': 'IFOX00', 'INSTALL': 'IEBGENER'},
    'BCPLDEMO': {'ASMDEMO': 'IFOX00', 'PUTDEMO': 'IEBGENER',
                 'READBACK': 'IEBGENER', 'VERIFY': 'IEBCOMPR'},
    'BCPLTIME': {'ASMTIME': 'IFOX00', 'PUTTIME': 'IEBGENER',
                 'READBACK': 'IEBGENER', 'VERIFY': 'IEBCOMPR'},
    'BCPLQSAM': {'ASMQ': 'IFOX00', 'PUTQSAM': 'IEBGENER',
                 'READBACK': 'IEBGENER', 'VERIFY': 'IEBCOMPR'},
}
ASSEMBLER_COUNTS = {'IC19BLD': 1, 'BLDBMAIN': 7, 'BLIBBLD': 2,
                    'BCPLDEMO': 1, 'BCPLTIME': 1, 'BCPLQSAM': 1}
ASSEMBLER_JOBS = frozenset(ASSEMBLER_COUNTS)
CODE_COUNTS = {'CAMBBLD': 22, 'BLIBBLD': 1}
JOB_HEADER = re.compile(r'^JOB\s+(\d+)\s+([A-Z0-9@$#]{1,8})\s*$', re.M)
STEP_ROW = re.compile(r'^([A-Z0-9@$#]{1,8})\s+([^\s]+)\s+RC=(\d{4})\s*$', re.M)
SUMMARY_SUCCESS = re.compile(r'^JOB RESULT: SUCCESS\s*$', re.M)
SUMMARY_ZERO = re.compile(r'^HIGHEST RC: 0000\s*$', re.M)
SEVERITY_ZERO = re.compile(r'^\s*Highest severity:\s*0\s*$', re.M)
# Interpreter completions appear either as dedicated CODE=0 records or as
# ICINT19's observed "EXECUTION CYCLES = n, CODE = 0" records.  Only whole
# records count; JCL comments and echoed source cards must not count.
CODE_RECORD = re.compile(
    r'^\s*(?:(?:(?:INTERPRETER|ICINT19)\s*:?\s*)?CODE\s*=\s*0|'
    r'EXECUTION CYCLES\s*=\s*\d+\s*,\s*CODE\s*=\s*0)\s*


@dataclass(frozen=True)
class VerifiedPayload:
    job: str
    payload_number: int
    launcher_number: int
    step_codes: tuple[tuple[str, int], ...]
    interpreter_codes: int


def parse_submission(output: str, *, member: str) -> tuple[int, int]:
    launchers = re.findall(r'^Launcher:\s*JOB\s+(\d+)\s*$', output, re.M)
    payloads = re.findall(r'^Payload:\s*JOB\s+(\d+)\s*$', output, re.M)
    if len(launchers) != 1 or len(payloads) != 1:
        raise VerificationError(f'{member}: missing/ambiguous launcher or payload identity')
    if (re.search(r'^Submitted\s+HERC02\.BCPL\.[A-Z0-9.]+\('
                  + re.escape(member) + r'\)\s*$', output, re.M) is None):
        raise VerificationError(f'{member}: submitted member identity missing')
    return int(launchers[0]), int(payloads[0])


def verify_payload(member: str, payload_number: int, launcher_number: int,
                   summary: str, full_report: str) -> VerifiedPayload:
    if member not in EXPECTED_STEPS:
        raise VerificationError(f'unknown build payload {member}')
    headers = JOB_HEADER.findall(summary)
    if len(headers) != 1 or headers[0] != (str(payload_number), member):
        raise VerificationError(f'{member}: wrong/missing payload job identity')
    if not SUMMARY_SUCCESS.search(summary) or not SUMMARY_ZERO.search(summary):
        raise VerificationError(f'{member}: failed or incomplete payload')
    if re.search(r'^(?:ABEND:|JCL ERROR:|BYPASSED:)', summary, re.M):
        raise VerificationError(f'{member}: abnormal completion or bypass')
    rows = STEP_ROW.findall(summary)
    names = tuple(name for name, _, _ in rows)
    if len(names) != len(set(names)) or set(names) != set(EXPECTED_STEPS[member]):
        raise VerificationError(f'{member}: missing, extra or repeated steps: {names!r}')
    if any(int(rc) != 0 for _, _, rc in rows):
        raise VerificationError(f'{member}: one or more step return codes nonzero')
    for name, program, _ in rows:
        required = EXPECTED_PROGRAMS[member].get(name)
        if required and program != required:
            raise VerificationError(f'{member}.{name}: expected {required}, found {program}')
    if member in ASSEMBLER_JOBS:
        if not SEVERITY_ZERO.search(summary):
            raise VerificationError(f'{member}: IFOX highest severity zero not proved')
    expected_assemblies = ASSEMBLER_COUNTS.get(member, 0)
    severities = [int(x) for x in re.findall(r'\bHIGHEST SEVERITY WAS\s+(\d+)\b', full_report, re.I)]
    if len(severities) != expected_assemblies or any(n != 0 for n in severities):
        raise VerificationError(f'{member}: assembler severity evidence incomplete or nonzero')
    count = len(CODE_RECORD.findall(full_report))
    if member in CODE_COUNTS and count != CODE_COUNTS[member]:
        raise VerificationError(f'{member}: expected {CODE_COUNTS[member]} interpreted CODE=0 records; got {count}')
    if member not in CODE_COUNTS and count != 0:
        # Some non-interpreter jobs may invoke unrelated programs, but that
        # requires an explicit update to this checked, accepted contract.
        raise VerificationError(f'{member}: unexpected interpreted CODE=0 records ({count})')
    if member in ('BCPLDEMO', 'BCPLTIME', 'BCPLQSAM'):
        if ('COMPARE FAILED' in full_report.upper() or
            'DATA SETS ARE NOT EQUAL' in full_report.upper()):
            raise VerificationError(f'{member}: IEBCOMPR reported mismatch')
    return VerifiedPayload(member, payload_number, launcher_number,
                           tuple((name, int(rc)) for name, _, rc in rows), count)


def inventory_members(text: str, dsn: str) -> frozenset[str]:
    lines = text.splitlines()
    if not lines or lines[0] != f'{dsn}:':
        raise VerificationError(f'unexpected inventory heading for {dsn}')
    if len(lines) == 2 and lines[1].strip() == '(empty)':
        return frozenset()
    seen: set[str] = set()
    for line in lines[1:]:
        if not re.fullmatch(r'    [A-Z@$#][A-Z0-9@$#]{0,7}', line):
            raise VerificationError(f'invalid member inventory row for {dsn}')
        name = line.strip()
        if name in seen:
            raise VerificationError(f'duplicate member {name}')
        seen.add(name)
    return frozenset(seen)


RUNTIME_MEMBERS = frozenset(('BCPLMAIN', 'BCPLMEM', 'BCPLBYTE', 'BCPLAPT',
                             'BCPLIO', 'BCPLRGS', 'BCPLREG', 'BLIB'))
EXTENSION_MEMBERS = frozenset(('BCPLDEMO', 'BCPLTIME', 'BCPLQSAM'))
CAMB_UNITS = frozenset(('BCPL', 'SYN', 'LEX', 'TRNA', 'TRNB', 'CGA', 'CGB',
                        'CGC', 'CGD', 'CGE', 'BOOTHOST'))

def required_inventory(logical: str, members: frozenset[str]) -> None:
    required: Mapping[str, frozenset[str]] = {
        'MR10_LOAD': frozenset(('ICINT19',)),
        'MR10_OBJ': frozenset(('ICINT19',)),
        'BOOT_INTCODE_TRNI': frozenset(('TRNILRG',)),
        'BOOT_INTCODE_COMPLETE': frozenset((*CAMB_UNITS, 'TRNILRG', 'CAMBCOMP')),
        'BOOT_OBJ_CORE': RUNTIME_MEMBERS - {'BLIB'},
        'BOOT_OBJ': RUNTIME_MEMBERS,
        'BOOT_DEVOBJ': frozenset(),
        'EXT_OBJ': EXTENSION_MEMBERS,
    }
    if logical not in required or members != required[logical]:
        raise VerificationError(f'{logical}: exact member inventory mismatch: {sorted(members)}')
,
    re.M | re.I,
)


@dataclass(frozen=True)
class VerifiedPayload:
    job: str
    payload_number: int
    launcher_number: int
    step_codes: tuple[tuple[str, int], ...]
    interpreter_codes: int


def parse_submission(output: str, *, member: str) -> tuple[int, int]:
    launchers = re.findall(r'^Launcher:\s*JOB\s+(\d+)\s*$', output, re.M)
    payloads = re.findall(r'^Payload:\s*JOB\s+(\d+)\s*$', output, re.M)
    if len(launchers) != 1 or len(payloads) != 1:
        raise VerificationError(f'{member}: missing/ambiguous launcher or payload identity')
    if (re.search(r'^Submitted\s+HERC02\.BCPL\.[A-Z0-9.]+\('
                  + re.escape(member) + r'\)\s*$', output, re.M) is None):
        raise VerificationError(f'{member}: submitted member identity missing')
    return int(launchers[0]), int(payloads[0])


def verify_payload(member: str, payload_number: int, launcher_number: int,
                   summary: str, full_report: str) -> VerifiedPayload:
    if member not in EXPECTED_STEPS:
        raise VerificationError(f'unknown build payload {member}')
    headers = JOB_HEADER.findall(summary)
    if len(headers) != 1 or headers[0] != (str(payload_number), member):
        raise VerificationError(f'{member}: wrong/missing payload job identity')
    if not SUMMARY_SUCCESS.search(summary) or not SUMMARY_ZERO.search(summary):
        raise VerificationError(f'{member}: failed or incomplete payload')
    if re.search(r'^(?:ABEND:|JCL ERROR:|BYPASSED:)', summary, re.M):
        raise VerificationError(f'{member}: abnormal completion or bypass')
    rows = STEP_ROW.findall(summary)
    names = tuple(name for name, _, _ in rows)
    if len(names) != len(set(names)) or set(names) != set(EXPECTED_STEPS[member]):
        raise VerificationError(f'{member}: missing, extra or repeated steps: {names!r}')
    if any(int(rc) != 0 for _, _, rc in rows):
        raise VerificationError(f'{member}: one or more step return codes nonzero')
    for name, program, _ in rows:
        required = EXPECTED_PROGRAMS[member].get(name)
        if required and program != required:
            raise VerificationError(f'{member}.{name}: expected {required}, found {program}')
    if member in ASSEMBLER_JOBS:
        if not SEVERITY_ZERO.search(summary):
            raise VerificationError(f'{member}: IFOX highest severity zero not proved')
    expected_assemblies = ASSEMBLER_COUNTS.get(member, 0)
    severities = [int(x) for x in re.findall(r'\bHIGHEST SEVERITY WAS\s+(\d+)\b', full_report, re.I)]
    if len(severities) != expected_assemblies or any(n != 0 for n in severities):
        raise VerificationError(f'{member}: assembler severity evidence incomplete or nonzero')
    count = len(CODE_RECORD.findall(full_report))
    if member in CODE_COUNTS and count != CODE_COUNTS[member]:
        raise VerificationError(f'{member}: expected {CODE_COUNTS[member]} interpreted CODE=0 records; got {count}')
    if member not in CODE_COUNTS and count != 0:
        # Some non-interpreter jobs may invoke unrelated programs, but that
        # requires an explicit update to this checked, accepted contract.
        raise VerificationError(f'{member}: unexpected interpreted CODE=0 records ({count})')
    if member in ('BCPLDEMO', 'BCPLTIME', 'BCPLQSAM'):
        if ('COMPARE FAILED' in full_report.upper() or
            'DATA SETS ARE NOT EQUAL' in full_report.upper()):
            raise VerificationError(f'{member}: IEBCOMPR reported mismatch')
    return VerifiedPayload(member, payload_number, launcher_number,
                           tuple((name, int(rc)) for name, _, rc in rows), count)


def inventory_members(text: str, dsn: str) -> frozenset[str]:
    lines = text.splitlines()
    if not lines or lines[0] != f'{dsn}:':
        raise VerificationError(f'unexpected inventory heading for {dsn}')
    if len(lines) == 2 and lines[1].strip() == '(empty)':
        return frozenset()
    seen: set[str] = set()
    for line in lines[1:]:
        if not re.fullmatch(r'    [A-Z@$#][A-Z0-9@$#]{0,7}', line):
            raise VerificationError(f'invalid member inventory row for {dsn}')
        name = line.strip()
        if name in seen:
            raise VerificationError(f'duplicate member {name}')
        seen.add(name)
    return frozenset(seen)


RUNTIME_MEMBERS = frozenset(('BCPLMAIN', 'BCPLMEM', 'BCPLBYTE', 'BCPLAPT',
                             'BCPLIO', 'BCPLRGS', 'BCPLREG', 'BLIB'))
EXTENSION_MEMBERS = frozenset(('BCPLDEMO', 'BCPLTIME', 'BCPLQSAM'))
CAMB_UNITS = frozenset(('BCPL', 'SYN', 'LEX', 'TRNA', 'TRNB', 'CGA', 'CGB',
                        'CGC', 'CGD', 'CGE', 'BOOTHOST'))

def required_inventory(logical: str, members: frozenset[str]) -> None:
    required: Mapping[str, frozenset[str]] = {
        'MR10_LOAD': frozenset(('ICINT19',)),
        'MR10_OBJ': frozenset(('ICINT19',)),
        'BOOT_INTCODE_TRNI': frozenset(('TRNILRG',)),
        'BOOT_INTCODE_COMPLETE': frozenset((*CAMB_UNITS, 'TRNILRG', 'CAMBCOMP')),
        'BOOT_OBJ_CORE': RUNTIME_MEMBERS - {'BLIB'},
        'BOOT_OBJ': RUNTIME_MEMBERS,
        'BOOT_DEVOBJ': frozenset(),
        'EXT_OBJ': EXTENSION_MEMBERS,
    }
    if logical not in required or members != required[logical]:
        raise VerificationError(f'{logical}: exact member inventory mismatch: {sorted(members)}')
