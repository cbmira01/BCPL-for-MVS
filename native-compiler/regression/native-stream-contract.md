# Native BCPL stream contract — consolidation baseline

Status: **functional TK5 baseline accepted; strict JES DD attribution pending**.
Evidence: native regression 000–119, 120 PASS/0 FAIL on 2026-10-10,
plus individually executed stream regressions 094–119.
This document records the behavior of `asm/bcplmain-wip.asm`, **not**
a claim that the 1981 Cambridge runtime had identical semantics.

## Interfaces and handles

The runtime publishes callable entries through BCPL global vector G:

| G | Name | Current behavior |
|---|---|---|
| 11 | SELECTINPUT | Select recognized input handle |
| 12 | SELECTOUTPUT | Select recognized, open output handle |
| 13 | RDCH | Get byte or synthetic record newline, return -1 on EOF |
| 14 | WRCH | Buffer byte or emit record on newline (10) |
| 15 | UNRDCH | Repeat previous RDCH result once on selected stream |
| 16 | INPUT | Return selected input handle |
| 17 | OUTPUT | Return selected output handle |
| 33 | WRAPOUTPUT | Provisional: flush alternate output record |
| 39 | FINDPARM | Provisional: expose BCPIN handle |
| 41 | FINDOUTPUT | Recognize SYSPRINT and BCPALT |
| 42 | FINDINPUT | Recognize BCPIN and BCPINB |
| 46 | ENDREAD | Close selected input, clear selection |
| 47 | ENDWRITE | Close selected alternate output; restore SYSPRINT |

Handles are BCPL word addresses of fixed runtime control fields, **not**
DASD dataset numbers, file descriptors, or arbitrarily allocatable handles.
FINDINPUT and FINDOUTPUT return zero for unknown names; failed discovery
does not change the currently selected stream (regression 116).
FINDOUTPUT lazily opens BCPALT, whereas SYSPRINT opens at startup.

## Input

BCPIN and BCPINB are distinct QSAM FB80 sources with independent record
positions, newline/EOF flags, and pushback state. The bootstrap reader
trims right-hand FB80 padding and synthesizes a BCPL newline (10) per
record. Consequently, significant trailing blanks in input records
**cannot presently be represented reliably**. RDCH returns -1 after
end-of-data. UNRDCH may repeat the last result (including EOF), per
regressions 097, 099 and 117. ENDREAD closes the selected input,
invalidates that selection, and permits a subsequent FINDINPUT to reopen
the stream at its beginning; the other input remains unaffected (118).

This is fixed-record, named-DD behavior; the contract makes no promise
of arbitrary input DD discovery, sequential stream creation, rewind on
JES instream DATA, or device-independent records.

## Output

SYSPRINT and BCPALT use separate QSAM FB132 buffers, positions and DCBs.
WRCH(10) writes the selected 132-byte physical record (blank padded)
and clears that stream's buffer. Two adjacent newline operations
therefore write an empty logical record between nonempty records
(regressions 110–111). Characters before a newline are buffered
separately for each stream (114).

**An attempt to append a 133rd character without an intervening newline
terminates via STOP(12).** This is the intentional overflow policy,
established by regression 113. Exactly 132 characters are accepted (112).
There is no automatic continuation, truncation, or wrap. The policy
applies to the FB132 WRCH paths; it is not a global promise about
future RECFM/VB/BSAM formats.

ENDWRITE of selected BCPALT flushes pending nonempty data, closes its
DCB, and reselects SYSPRINT; attempts to select the closed handle are
rejected. A later FINDOUTPUT reopens BCPALT with a reset buffer (115).
FINISH and STOP drain pending nonempty buffers and close open
runtime-owned streams (119 and earlier termination tests).

The current WRAPOUTPUT and FINDPARM entries remain **provisional**.
Their historical signatures and failure semantics are not frozen.

## Error and lifetime boundaries

Unknown DD names return zero; this is not the same as an MVS OPEN error.
The bootstrap has not yet demonstrated robust propagation of every
QSAM OPEN, GET, PUT or CLOSE failure and does not promise arbitrary
invalid-pointer safety. STOP(12) is currently the prescribed overlength
record response, not a historical BCPL error-number claim. A future
implementation must check and document QSAM errors before describing
this subsystem as production-complete.

All static control fields, save images, and buffers belong to
BCPLMAIN-WIP and are not reentrant or per-task instances. Extraction
into separate object CSECTs must preserve BCPL G-number compatibility,
generated-code register invariants (particularly R0–R3, R11–R13),
handle stability through open/close, and independent input/output state.

## Verification boundary and next gate

The 120-test panel used the earlier matcher, which searched the
post-link JES job-report suffix and stripped whitespace. The
consolidation checker `tools/checks/check-combined-jes-records.py`
strengthens this by preserving leading blanks, requiring contiguous
ordered logical records, and rejecting missing linker boundaries.
Right-hand physical FB132 blank padding cannot be distinguished from
omission in the text printer report. More importantly, a flattened
printer report is **not a lossless record of JES DD boundaries**.
Consequently the checker deliberately says *DD attribution NOT VERIFIED*
and does **not** claim to establish that a match occurred in BCPALT
rather than SYSPRINT. The test suite after checker introduction must
be run anew; past 120 PASS does not validate the changed checker.

Before declaring physical-record acceptance, obtain a reproducible
GO-step SYSOUT extraction that identifies each DD and returns individual
132-byte records without stripping. Add strict per-DD equality checks
against dedicated fixture files, with negative fixture tests that swap
or corrupt the DD streams. Do not weaken prior assertions or silently
interpret combined-report ordering as DD identity.

## Modularization freeze line

Frozen **for restructuring**: G-number entry surface already exercised,
the two named input DDs, two named output DDs, selection rules,
WRCH newline and STOP(12) overflow, buffered flush on close/termination,
and independence of stream buffers/cursors. Provisional/unfinished:
historical FINDPARM and WRAPOUTPUT contracts, generalized streams,
full QSAM error mapping, true DD-attributed record validation,
and preservation of significant input trailing blanks.
