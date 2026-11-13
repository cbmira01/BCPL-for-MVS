#!/usr/bin/env python3
"""Conservative review of CALLIND R4 provenance in generated CG370 assembler.

A unique three-formal checked prologue identifies CALLIND in the fixed fixture;
procedure-name comments are optional and not used as an executable-code anchor.
This is textual evidence only, not proof of native execution.
"""
from __future__ import annotations

import re

PROLOGUE = re.compile(r'^\s*STM\s+4,9,0\(15\)(?:\s|$)', re.I)
ANY_PROLOGUE = re.compile(r'^\s*STM\s+4,\d+,0\(15\)(?:\s|$)', re.I)
CHECK = re.compile(r'^\s*BAL\s+14,60\(11\)(?:\s|$)', re.I)
FRAME = re.compile(r'^\s*DC\s+A\(L\d+\)\s+STACK FRAME SIZE(?:\s|$)', re.I)
CALL = re.compile(r'^\s*BALR\s+6,4(?:\s|$)', re.I)
RETURN = re.compile(r'^\s*BCR\s+15,11(?:\s|$)', re.I)
LABEL = re.compile(r'^\s*L\d+\s+EQU\s+\*\s+ENTRY TO\s+(\w+)', re.I)
# Conservative allowance: the formal F is the first BCPL parameter at P!3
# (byte offset 12), or R7 when it has not been changed by the callee.
DIRECT = re.compile(r'^\s*LR\s+4,7(?:\s|$)', re.I)
SAVED = re.compile(r'^\s*L\s+4,12\(5\)(?:\s|$)', re.I)
BRANCH = re.compile(r'^\s*(?:B|BC|BCR|BAL|BALR|BASR|BXH|BXLE)\s', re.I)
LM = re.compile(r'^\s*LM\s', re.I)
WRITE_R4 = re.compile(
    r'^\s*(?:L|LR|LA|LH|IC|AR|AH|ALR|A|SR|S|SLR|NR|N|OR|O|XR|X|'
    r'SLL|SRL|SRA|SLA|LCR|LPR|LNR|LTR|BASR|BALR)\s+4\s*,', re.I)
WRITE_R7 = re.compile(
    r'^\s*(?:L|LR|LA|LH|IC|AR|AH|ALR|A|SR|S|SLR|NR|N|OR|O|XR|X|'
    r'SLL|SRL|SRA|SLA|LCR|LPR|LNR|LTR|BASR|BALR)\s+7\s*,', re.I)


class TargetAuditError(ValueError):
    """The recovered listing is insufficient for an indirect-target claim."""


def audit_indirect_target(listing: str) -> dict[str, object]:
    """Locate unique CALLIND by structural prologue and trace the R4 call target.

    Never infer a unique site merely from the program-wide call count or a
    comment containing a source procedure name.
    """
    lines = listing.splitlines()
    matches = [i for i, line in enumerate(lines) if PROLOGUE.match(line)]
    if len(matches) != 1:
        raise TargetAuditError(f'expected one three-formal checked prologue; found {len(matches)}')
    start = matches[0]
    # Historical CGSAVE emits STM, BAL and one inline frame fullword.
    if start + 2 >= len(lines) or not CHECK.match(lines[start + 1]) or not FRAME.match(lines[start + 2]):
        raise TargetAuditError('three-formal prologue lacks adjacent checked entry and frame word')

    # Bound the procedure by its next normal system-vector return; never borrow
    # a BALR from the next procedure if this simple fixture changes.
    later_prologues = [i for i in range(start + 1, len(lines)) if ANY_PROLOGUE.match(lines[i])]
    next_prologue = later_prologues[0] if later_prologues else len(lines)
    returns = [i for i in range(start + 3, next_prologue) if RETURN.match(lines[i])]
    if len(returns) != 1:
        raise TargetAuditError(f'expected one CALLIND normal return before next prologue; found {len(returns)}')
    end = returns[0]
    if end - start > 90:
        raise TargetAuditError('CALLIND candidate region too long for this fixed fixture')
    # In the fixed source there is exactly one indirect F(A,B) call.
    calls = [i for i in range(start + 3, end) if CALL.match(lines[i])]
    if len(calls) != 1:
        raise TargetAuditError(f'expected one BALR 6,4 within three-formal procedure; found {len(calls)}')
    call = calls[0]
    # No procedural branch may intervene between candidate entry and call;
    # this fixed fixture does not contain a conditional dispatch.
    if any(BRANCH.match(lines[i]) for i in range(start + 3, call)):
        raise TargetAuditError('unexpected control transfer before indirect CALLIND call')

    writes = [i for i in range(start + 3, call) if WRITE_R4.match(lines[i])]
    if not writes:
        raise TargetAuditError('no identifiable R4 definition before indirect BALR')
    definition = writes[-1]
    instruction = lines[definition].strip()
    if not (SAVED.match(instruction) or DIRECT.match(instruction)):
        raise TargetAuditError(f'final R4 definition not traced to F: {instruction[:70]}')
    if DIRECT.match(instruction) and any(WRITE_R7.match(lines[i]) or LM.match(lines[i])
                                         for i in range(start + 3, definition)):
        raise TargetAuditError('R7 origin changed before transfer to R4')
    if any(LM.match(lines[i]) or BRANCH.match(lines[i])
           for i in range(definition + 1, call)):
        raise TargetAuditError('R4 origin obscured after candidate target load')
    if call - definition > 8:
        raise TargetAuditError('R4 target definition too distant from BALR')

    labels = [(i + 1, m.group(1).upper()) for i, line in enumerate(lines)
              if (m := LABEL.match(line))]
    # A parsed label is supplementary only, never a prerequisite.
    return {
        'identification': 'unique STM 4,9,0(15) plus adjacent checked entry and bounded return',
        'name_labels_found': len(labels),
        'entry_line': start + 1,
        'return_line': end + 1,
        'target_line': definition + 1,
        'call_line': call + 1,
        'target_instruction': instruction,
        'target_origin': 'R7 unchanged first formal F' if DIRECT.match(instruction) else 'P!3 first formal F at 12(R5)',
        'balr_count': 1,
        'evidence_class': 'recovered compiler text; no IFOX/IEWL/GO',
    }
