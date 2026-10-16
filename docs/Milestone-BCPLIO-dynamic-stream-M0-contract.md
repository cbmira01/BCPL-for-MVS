# Milestone - BCPLIO dynamic stream: M0 contract and acceptance

Status: **M0 design accepted; M1 not started**  
Decision date: 2026-10-16  
Parent: [Milestone-BCPLIO-dynamic-stream.md](Milestone-BCPLIO-dynamic-stream.md)

## Baseline and reproducibility

Operator-reported local repository commit: `73a6591d7dc574603b19ea025a3d8c9a428f5e36`.  
Command: `tools/native/run-regression`.  
Result: 00–123, 124 cases; **123 PASS, 0 FAIL, 1 expected SKIP (083, source-only instrumentation)**. Stream cases 094–119 passed. Local `tools/datasets/dspal status` reported Docker up, Hercules and JES reader reachable; MVS/JES2 not independently probed. This is operator-provided execution evidence, not a fresh execution by the author of this note.

Installed PDS inventory reported by operator:
- `HERC02.BCPL.NATIVE.OBJ`: BCPLMAIN, BCPLMEM, BLIB.
- `HERC02.BCPL.NATIVE.DEVOBJ`: BCPLAPT, BCPLBYTE, BCPLIO.
- `HERC02.BCPL.NATIVE.JCL`: contains BLDBMAIN, BLDDEVI and other resident jobs.

`NATIVE_JCL(BLDBMAIN)` assembles BCPLMAIN and BCPLMEM to production OBJ; `NATIVE_JCL(BLDDEVI)` assembles BCPLIO independently to DEVOBJ. Do not use `dspal put` for binary object members. The canonical installed-object regression job generator `tools/checks/prepare-runtime-pds-regression.py` defaults to `BCPL_RUNTIME_LIBRARY=MIXED`: BCPLMAIN/BCPLMEM/BLIB from OBJ, BCPLBYTE/BCPLAPT from DEVOBJ, **without separately including BCPLIO**. The production 123-pass panel alone does not prove BCPLIO linkage.

Prior accepted Gate D D6 candidate evidence: `DEVOBJ(BCPLM6)` with independently linked `BCPLIO`, assembler/install JOB 2389 RC=0000, link JOB 2393 IEWL RC=0000 and MAP/XREF confirming input and output service resolution in BCPLIO. Focused 084–119 36 PASS; complete D6 candidate 00–123 **123 PASS / 0 FAIL / 1 SKIP**. See `packaging/m2-0-gate-d-bcplio-extraction-plan.md`. That historical candidate is a design and linkage precedent, **not a claim that BCPLM6 is presently installed**. Current DEVOBJ inventory does not list BCPLM6. M1 must re-establish the modular candidate through the resident PDS reconstruction/build procedure rather than assume an old object is still installed.

## Architectural boundary

Extend the independent BCPLIO CSECT; keep BCPLMAIN small and responsible for runtime bootstrap, G-vector installation, FINISH/STOP orchestration and its existing memory services. BCPLIO owns stream handles, descriptors, DCBs, buffers, selected streams, EOF/unread state and stream cleanup. Preserve private IOINIT/IOFIN linkage, BCPL R6 return/R7 argument and result, R5 frame/R4 restoration, and the generated-code register invariants. Do not alter global numbering. No QSAM application library, VSAM, dataset dynamic allocation, new compiler syntax or extension dispatcher.

## Decisions explicitly approved by project owner, 2026-10-16

1. **Stable handle identity and stale-handle rejection.** Return opaque BCPL-word-address handles referring to small, stable control records. A close invalidates the control record and releases the larger dynamic descriptor, DCB and record buffer. Do not recycle handle identity addresses during a program run; otherwise an old handle could unexpectedly designate a later stream. Retired handle records can be reclaimed at final termination. This intentionally uses storage proportional to *cumulative opens*, not just concurrent opens. Inspect and document exhaustion behavior. Selected handles must be validated before access; stale/invalid handles must not dereference freed memory.
2. **Duplicate FIND.** FINDINPUT/FINDOUTPUT called repeatedly with the same normalized name and same direction while open return the **same active handle**; no duplicate DCB OPEN. Reopening after close establishes a new logical stream lifetime and handle.
3. **DD-name normalization.** BCPL counted strings must contain 1–8 valid MVS DD-name characters. Convert lowercase letters to uppercase, then store/compare an eight-character space-padded EBCDIC name. No truncation of longer names; reject empty/invalid names. Use historically valid DD character rules, tested before final assembly; do not mistake DD *discovery* for enumeration. The application supplies the name and JCL supplies its allocation.
4. **Graceful FIND failure.** Unknown/unallocated DD, invalid name, conditional GETMAIN exhaustion or unsuccessful OPEN return **zero**; current input/output selection remains unchanged. No abend for ordinary FIND failure. Capture internal status for diagnostics without adding BCPL global slots. Further MVS OPEN/GET/PUT/CLOSE failure mapping must be documented by M4; do not claim unchecked paths are already robust.
5. **Preserve existing behavior initially.** Retain FB80 input, right-trimmed padding, synthetic newline character 10, RDCH EOF -1 and per-stream UNRDCH behavior; FB132 output, newline-triggered record emission, independent partial records, 132-character maximum and STOP(12) overflow; existing close/reopen/flush, special streams and PARM behavior. Significant trailing blanks remain an acknowledged limitation, not a silent semantic change. WRAPOUTPUT and FINDPARM remain provisional except for regression-established behavior.

## Proposed implementation detail within accepted principles

Use a simple linked registry of active ordinary stream descriptors, indexed by normalized DD name plus direction and by live handle identity. Each ordinary descriptor owns its independently allocated state, copied QSAM DCB and buffer; link only after successful DD validation/OPEN, or precisely document and reverse any provisional registration on OPEN error. Use conditional GETMAIN and matching FREEMAIN sizes. RDJFCB discovery follows `mr10-kit-compiler/asm/icintv19.asm` DYNFIND/DYFALLOC/DYFVERIF/DYNFREE/MAKENAME/OPENSTRM as a **conceptual** reference, not a drop-in copy: ICINT directly uses host pointers and releases descriptor addresses, while the native ABI requires opaque BCPL-word handles that cannot alias newly reused storage.

Preserve known standard DD names BCPIN, BCPINB, SYSPRINT and BCPALT, including startup/lazy-open behavior as currently accepted; EXEC PARM is a separate memory pseudo-stream. Selection of invalid or closed handle leaves previous selection unchanged. ENDREAD/ENDWRITE and IOFIN close only owned open resources and never double-free. Stream limits derive from storage and MVS QSAM constraints, not an arbitrary fixed stream count.

## Required verification in M1–M5

- Rebuild/install a fresh modular BCPLMAIN candidate and BCPLIO into DEVOBJ using PDS-resident JCL; verify IFOX step codes, IEWL MAP/XREF and GO step codes. Do not promote DEVOBJ into production OBJ without separate authorization.
- First dynamic tests: `FINDINPUT("CUSTOMER")` and `FINDOUTPUT("REPORT")` with corresponding JCL DD statements, absent DD, invalid name, lowercase name, duplicate FIND and selection preservation.
- Exercise 3, 12 and at least 13 simultaneous independent input streams and interleaved output streams; close/reopen, stale handle rejection, resource-exhaustion paths and FINISH/STOP cleanup.
- Preserve the 00–123 regression baseline, with the expected skip 083, and compare behavior with ICINT v19 test 07-many-streams.
- Verify output attribution using DD-specific lossless records, not solely flattened JES printer reports; retain job/step/result evidence.
- Record any unavoidable MVS-specific restrictions before claiming full milestone acceptance.

## Gate disposition

**M0 contract accepted** on explicit agreement to all five decisions. This closes the M0 design gate and **authorizes planning/implementation of M1 only as a separate march**. No functional assembler changes or M1 test claims are made here.
