#!/usr/bin/env python3
"""Fail-closed audit of a CG370 CALLIND procedure-valued call site.

Analyzes recovered text assembler only. Does not validate execution/target memory.
"""
from __future__ import annotations

import re

# Non-naming /CN CODE listings still identify procedures: CGENTRY emits
# 'L<n> EQU * ENTRY TO ' followed by the (up to seven-char) BCPL name.
ENTRY = re.compile(r"^L(\d+)\s+EQU\s+\*\s+ENTRY TO\s+([A-Z0-9@$#]+)\b", re.I)
STM = re.compile(r"^\s*STM\s+4,9,0\(15\)(?:\s|$)", re.I)
BAL60 = re.compile(r"^\s*BAL\s+14,60\(11\)(?:\s|$)", re.I)
CALL = re.compile(r"^\s*BALR\s+6,4\b", re.I)
# A standalone LR moves F from its incoming first-argument register R7.
# Alternatively, an L reloads F from P!3 (byte offset 12) after CGSAVE.
DIRECT = re.compile(r"^\s*LR\s+4,7\s*(?:\*.*)?$", re.I)
SPILLED = re.compile(r"^\s*L\s+4,12\(5\)\s*(?:\*.*)?$", re.I)
# For the source's simple CALLIND(F,A,B), do not claim a target is
# established if a later instruction writes a different value into R4.
CONTROL_TRANSFER = re.compile(r"^\s*(?:B|BC|BCR|BAL|BALR|BASR|BXH|BXLE)\s", re.I)
MULTI_REGISTER_LOAD = re.compile(r"^\s*LM\s", re.I)
WRITE_R7 = re.compile(
    r"^\s*(?:L|LR|LA|LH|IC|AR|AH|ALR|A|SR|S|SLR|NR|N|OR|O|XR|X|"
    r"SLL|SRL|SRA|SLA|LCR|LPR|LNR|LTR|BASR|BALR)\s+7\s*,", re.I
)
WRITE_R4 = re.compile(
    r"^\s*(?:L|LR|LA|LH|IC|AR|AH|ALR|A|SR|S|SLR|NR|N|OR|O|XR|X|"
    r"SLL|SRL|SRA|SLA|SLA|LCR|LPR|LNR|LTR|BASR|BALR)\s+4\s*,", re.I
)


class TargetAuditError(ValueError):
    """The recovered listing cannot substantiate the indirect target."""


def audit_indirect_target(listing: str) -> dict[str, object]:
    lines = listing.splitlines()
    entries = [(n, m.group(1), m.group(2).upper()) for n, line in enumerate(lines)
               if (m := ENTRY.match(line))]
    names = [name for _, _, name in entries]
    if names.count('CALLIND') != 1:
        raise TargetAuditError(f'expected exactly one ENTRY TO CALLIND, found {names.count("CALLIND")}')
    start_index = next(k for k, (_, _, name) in enumerate(entries) if name == 'CALLIND')
    start, label, _ = entries[start_index]
    end = entries[start_index + 1][0] if start_index + 1 < len(entries) else len(lines)
    body = lines[start + 1:end]
    if len([line for line in body if STM.match(line)]) != 1:
        raise TargetAuditError('CALLIND does not have one STM 4,9,0(15) prologue')
    if len([line for line in body if BAL60.match(line)]) != 1:
        raise TargetAuditError('CALLIND does not have one BAL 14,60(11) checked entry')
    calls = [n for n, line in enumerate(body) if CALL.match(line)]
    if len(calls) != 1:
        raise TargetAuditError(f'CALLIND must contain exactly one BALR 6,4, found {len(calls)}')
    call_index = calls[0]
    candidates = [(n, line.strip()) for n, line in enumerate(body[:call_index]) if WRITE_R4.match(line)]
    if not candidates:
        raise TargetAuditError('no identifiable R4 definition before CALLIND BALR 6,4')
    last_index, target = candidates[-1]
    if not (DIRECT.match(target) or SPILLED.match(target)):
        raise TargetAuditError(f'R4 final definition does not trace to formal F: {target[:70]}')
    if DIRECT.match(target) and any(WRITE_R7.match(line) or MULTI_REGISTER_LOAD.match(line)
                                   for line in body[:last_index]):
        raise TargetAuditError('R7 formal F origin obscured before LR 4,7')
    if any(CONTROL_TRANSFER.match(line) or MULTI_REGISTER_LOAD.match(line)
           for line in body[last_index + 1:call_index]):
        raise TargetAuditError('control transfer or LM obscures R4 origin before CALLIND BALR')
    if call_index - last_index > 8:
        raise TargetAuditError('R4 target assignment is too distant from CALLIND BALR 6,4')
    return {'entry_label': 'L' + label, 'target_instruction': target,
            'target_origin': 'R7 incoming formal F' if DIRECT.match(target) else '12(R5) P!3 saved formal F',
            'balr_count': 1, 'entry_line': start + 1,
            'target_line': start + 1 + last_index + 1,
            'call_line': start + 1 + call_index + 1,
            'evidence_class': 'CG370 emitted text only; no native GO'}
