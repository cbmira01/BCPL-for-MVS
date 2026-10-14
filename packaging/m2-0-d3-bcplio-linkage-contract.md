# M2.0 / Gate D / D3: BCPLIO linkage and ownership contract

**Status: candidate; MVS lifecycle retest pending.** D3 is a portion within Gate D, not a milestone.

## Single ownership

BCPLIO will own SYSPRINT, BCPALT, BCPIN, BCPINB and their buffers/DCBs after full extraction. BCPLMAIN keeps global-vector bootstrap, STOPRC, FINISH/STOP orchestration and memory reclamation. Never OPEN the same SYSPRINT DD via BCPLMAIN BCPOUT and BCPLIO IODCB in a single integrated execution.

## Currently implemented BCPLIO native-private entries

- IOINIT: BALR R14,entry, R1=original EXEC PARM pointer, R13=active MVS savearea. Opens primary SYSPRINT once, blanks buffer, clears sticky overflow. Repeated call while active: no-op. Returns via R14, preserves R0-R9 and R11-R15, clobbers R10.
- IOFIN: BALR R14,entry, flushes nonempty output and closes active primary DCB; repeated call while inactive does not PUT/CLOSE. Same register preservation and return. Must precede MEMDRAIN/FREEMAIN; BCPLMAIN STOPRC must survive.
- IOSTAT: native BALR R14,entry, returns sticky status 0/12 in R15.
- IOWRCH: BCPL R6 return; R7 character, code 10 newline/PUT, R4 restored from 0(R5). Preserves R0-R3, R5-R9, R11-R12, R15; R10 is private base. Full buffer latches status 12 but DOES NOT terminate. Must not be wired to G14 yet.

Static save areas mean nonreentrant/nonrecursive service calls. An overflow direct STOP call nested within IOWRCH remains unimplemented, and could overwrite static state if wired naively.

## Integrated interfaces still to be designed and implemented

- Selected-stream dispatch compatible with G12/14/16/17/41, and BCPALT lazy open, WRAPOUTPUT, ENDWRITE. Current IOWRCH writes only SYSPRINT.
- One narrow private append/record entry for bootstrap WRITEST and DEBUGINT, and STKOVFL diagnostic, replacing direct writes to BCPLMAIN OUTPOS/OUTBUF at the same time ownership transfers.
- Ordinary G14 overflow must select STOP(12); existing STKOVFL currently branches to FINIMPL and yields RC=0. Preserve and test that distinction until a separately approved policy change.
- Input BCPIN/BCPINB and their EODAD handlers must relocate together; original MVS PARM pointer transfers once from BCPLMAIN.
- Integrated candidate must link DEVOBJ-only, show BCPLIO symbols in IEWL map, and pass focused lifecycle, overflow, alternate-stream, formatter, input, and PARM tests before D4.

## First D3 implementation slice

Commit ba71439439a767714ac9d5ab543bbd52f3baffbf changes only asm/bcplio.asm: IOINIT/IOFIN now save and restore caller machine registers across OPEN/PUT/CLOSE, IOINIT guarded against repeated OPEN, IOFIN still guards repeated CLOSE. This is a **candidate**, not MVS-tested. Existing BCPLMAIN startup, G14, and FINISH remain untouched. No production OBJ changes.
