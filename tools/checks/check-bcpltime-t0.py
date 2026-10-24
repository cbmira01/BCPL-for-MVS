#!/usr/bin/env python3
"""Offline structural checks only; NOT an IFOX/MVS validation."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[2]
asm=(root/'bootstrap-toolchain/extensions/bcpltime/bcpltime.asm').read_text('ascii')
hdr=(root/'bootstrap-toolchain/extensions/bcpltime/bcpltime.h').read_text('ascii')
client=(root/'bootstrap-toolchain/extensions/bcpltime/test.bcpl').read_text('ascii')
ml=(root/'packaging/milestone-date-and-time-services.md').read_text('utf-8')
for n,line in enumerate(asm.splitlines(),1):
    assert len(line)<=71,(n,len(line),line)
    if line and line[0] not in '* ':
        label=line[:8].strip()
        assert len(label)<=8,(n,label)
assert sum(bool(re.match(r'^[A-Z0-9]{1,8}\s+CSECT\s*$', line)) for line in asm.splitlines())==2
for token in ("CL8'BCPLTIME'", "F'201',A(TIMDISP)", 'ENTRY TIMBEG,TIMEND',
              'ENTRY TIMDISP','STCK  CLKBUF','TIME  DEC','BC    8,CCZERO',
              'BC    4,CCONE','BC    2,CCTWO',"LA    14,3", 'CLKBUF   DS    0D'):
    assert token in asm,token
# The MVS TIME macro overwrites CG370's permanent R0/R1 bases.
# Keep the save, raw-result stores, and restore in one exact sequence.
dotime = asm.split('DOTIME   LTR   8,8',1)
assert len(dotime) == 2, 'missing TIME dispatch entry'
body = dotime[1].split('BADOP    L',1)
assert len(body) == 2, 'TIME dispatch exit boundary missing'
sequence = (
    'SLL   8,2',
    'STM   0,1,24(5)',
    'TIME  DEC',
    'ST    0,0(8)',
    'ST    1,4(8)',
    'LM    0,1,24(5)',
    'LA    7,2',
    'BCR   15,11',
)
lines = [line.strip() for line in body[0].splitlines()
         if line.strip() and not line.startswith('*')]
assert lines[-len(sequence):] == list(sequence), (
    'TIME DEC must preserve R0/R1 across the service call')
assert 'GLOBAL $( TIMESVC:201 $)' in hdr
assert 'TIME_QUERY=0; TIME_STCK=1; TIME_MVS=2' in hdr
assert 'TIMESVC:201' in client
for token in ('TIMESVC(0,INFO,6)','TIMESVC(1,CLOCK,3)','TIMESVC(2,MVS,2)',
              'TIMESVC(99,0,0)','BCPLTIME T0 PASS'):
    assert token in client,token
assert 'T.0 — Descriptor, Dispatcher, and Native Execution' in ml
assert 'T.1 — Packaging and Acceptance' in ml
catalog=(root/'bootstrap-toolchain/extensions/bcpltime/t0-catalog.asm').read_text('ascii')
selection=(root/'bootstrap-toolchain/extensions/bcpltime/t0-selection.asm').read_text('ascii')
assert "&BXCLIB  SETC  'TIMEOBJ'" in catalog
assert "&BXCBEG  SETC  'TIMBEG'" in catalog
assert "&BXCFIN  SETC  'TIMEND'" in catalog
assert 'BCXREQ BCPLTIME' in selection
for filename in ('t0-catalog.asm','t0-selection.asm'):
    src=(root/'bootstrap-toolchain/extensions/bcpltime'/filename).read_text('ascii')
    assert max(map(len,src.splitlines()))<=71
assert '15 October' in ml
print('BCPLTIME T.0 offline structural checks: PASS (not IFOX/MVS)')
