#!/usr/bin/env python3
"""Compile-only CO.1 checked worker-entry and native return-frame oracle.

This module examines compiler text and tracked BCPLMAIN source. It does not
construct a coroutine or assert correctness of a native context switch.
"""
from __future__ import annotations

import re


class FrameOracleError(ValueError):
    """A required emitted-code/source-level frame fact was not verified."""


ENTRY = re.compile(r'^\s*STM\s+4,(6|7|8),0\(15\)(?:\s|$)', re.M | re.I)
CHECKED = re.compile(r'^\s*BAL\s+14,60\(11\)(?:\s|$)', re.I)
FRAME_WORD = re.compile(r'^\s*DC\s+A\(L(\d+)\)\s+STACK FRAME SIZE\s*$', re.I)
FRAME_EQU = re.compile(r'^L(\d+)\s+EQU\s+(\d+)\s+STACK FRAME SIZE\s*$', re.M | re.I)
RETURN = re.compile(r'^\s*BCR\s+15,11(?:\s|$)', re.I)
CALL = re.compile(r'^\s*BALR\s+6,4(?:\s|$)', re.I)
RAW_CHECKED = re.compile(r'^\s*BAL\s+14,60\(11\)(?:\s|$)', re.M | re.I)
COUNT = re.compile(r'^\s*BAL\s+14,(?:20|80)\(11\)(?:\s|$)', re.M | re.I)
RETIMPL = re.compile(
    r'^RETIMPL\s+L\s+6,8\(5\)\s*\n'
    r'\s*L\s+5,4\(5\)\s*\n'
    r'\s*L\s+4,0\(5\)\s*\n'
    r'\s*BCR\s+15,6(?:\s|$)', re.M | re.I,
)


def verify_compiler_listing(listing: str) -> dict[str, object]:
    """Require unique 0-, 1-, 2-argument prologues and a worker return."""
    lines = listing.splitlines()
    candidates = [(i, int(m.group(1))) for i, line in enumerate(lines)
                  if (m := ENTRY.match(line))]
    counts = {n: sum(last == n for _, last in candidates) for n in (6, 7, 8)}
    if counts != {6: 1, 7: 1, 8: 1}:
        raise FrameOracleError(f'expected one each STM 4,6/7/8 prologue, found {counts}')
    if COUNT.search(listing):
        raise FrameOracleError('unexpected +20/+80 counting service in /CN code')
    definitions: dict[str, list[int]] = {}
    for m in FRAME_EQU.finditer(listing):
        definitions.setdefault(m.group(1), []).append(int(m.group(2)))
    frames = []
    used_frame_labels: set[str] = set()
    for index, max_register in candidates:
        if index + 2 >= len(lines) or not CHECKED.match(lines[index + 1]):
            raise FrameOracleError(f'STM 4,{max_register} lacks adjacent +60 check')
        meta = FRAME_WORD.match(lines[index + 2])
        if not meta:
            raise FrameOracleError(f'STM 4,{max_register} lacks inline frame word')
        if meta.group(1) in used_frame_labels:
            raise FrameOracleError('multiple procedures reuse one inline frame-size label')
        used_frame_labels.add(meta.group(1))
        size = definitions.get(meta.group(1), [])
        if len(size) != 1 or size[0] <= 0 or size[0] % 4:
            raise FrameOracleError(f'STM 4,{max_register} has missing/duplicate/bad frame size')
        frames.append({'save_through': max_register, 'frame_bytes': size[0]})
    if len(RAW_CHECKED.findall(listing)) != 3:
        raise FrameOracleError('expected exactly three +60 checked entries')

    worker_start = next(i for i, last in candidates if last == 7)
    worker_end = min((i for i, _ in candidates if i > worker_start), default=len(lines))
    worker_returns = [i for i in range(worker_start + 3, worker_end)
                      if RETURN.match(lines[i])]
    if len(worker_returns) != 1:
        raise FrameOracleError('one-argument worker lacks exactly one normal system-vector return')
    if worker_returns[0] - worker_start > 120:
        raise FrameOracleError('worker return exceeds bounded procedure interval')
    invoke_start = next(i for i, last in candidates if last == 8)
    invoke_end = min((i for i, _ in candidates if i > invoke_start), default=len(lines))
    invoke_calls = sum(CALL.match(line) is not None
                       for line in lines[invoke_start + 3:invoke_end])
    if invoke_calls != 1:
        raise FrameOracleError(f'two-argument INVOKE requires one BALR 6,4, found {invoke_calls}')
    calls = sum(CALL.match(line) is not None for line in lines)
    if calls < 3:
        raise FrameOracleError(f'expected >=3 ordinary calls; found {calls}')
    return {'checked_entries': 3, 'zero_arg_entry': 1, 'one_arg_entry': 1,
            'two_arg_entry': 1, 'ordinary_calls': calls,
            'worker_return_line': worker_returns[0] + 1,
            'generated_frame_sizes': frames}


def verify_runtime_return(source: str) -> dict[str, bool]:
    """Inspect tracked BCPLMAIN source, not a resident linked object."""
    if len(RETIMPL.findall(source)) != 1:
        raise FrameOracleError('tracked BCPLMAIN does not contain expected RETIMPL order')
    if not re.search(r'^STKIMPL\s+LR\s+5,15\s*$', source, re.M):
        raise FrameOracleError('tracked BCPLMAIN does not install R5 from R15')
    return {'tracked_retimpl_order': True, 'tracked_stkimpl_frame_install': True}


def model_return(callee: tuple[int, int, int], caller_frame_word0: int) -> dict[str, int]:
    """Pure register/word model of current RETIMPL instruction order.

    Callee tuple corresponds to words 0..2 (R4, old R5, old R6).
    No stack allocation, descriptor layout, or actual S/370 code is implied.
    """
    if len(callee) != 3:
        raise FrameOracleError('callee frame requires three saved linkage words')
    return {'R6': callee[2], 'R5': callee[1], 'R4': caller_frame_word0}
