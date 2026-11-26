# How to Use System Extensions

*Cambridge BCPL Programming System for MVS 3.8J*

For native application programmers in the development environment. See the [tutorial](Tutorial-on-System-Extensions.md) and [reference](Reference-for-System-Extensions.md). RC4 alone is not an eligible native compilation environment.

## 1. Choose packages and prerequisites

| Need | Package | Evidence |
| --- | --- | --- |
| Learn dispatch or verify interoperability | BCPLDEMO | Accepted installed reference |
| Read raw clock and MVS time words | BCPLTIME | Accepted source/installed modes |
| Exact sequential logical records | BCPLQSAM | Accepted source-mode and temporary-PDS selection; installed verification qualified |
| Decimal arithmetic | BCPLDEC | Proposed, not available |

For ordinary character streams use BCPLIO. Ensure CAMBCOMP, ICINT19, IFOX, IEWL, accepted BOOT_OBJ and BCPLRGS work. Consult [dataset configuration](../../config/dspal.yaml) for EXT_ASM, EXT_SOURCE, EXT_MAC, EXT_OBJ and BOOT_OBJ; these are manifest keys, not literal DDs. Permanent object installation is separate from application linkage.

## 2. Include declarations and query capabilities

Use [bcpldemo.h](../../system-extensions/bcpldemo/bcpldemo.h), [bcpltime.h](../../system-extensions/bcpltime/bcpltime.h), or [bcplqsam.h](../../system-extensions/bcplqsam/bcplqsam.h) as the declaration authority. Supply them through an appropriate verified compiler input arrangement. Existing regression programs repeat the GLOBAL/manifest declarations; do not assume their jobs exercised extension-header GET transport.

After selection and registration, call opcode 0 with two zero arguments to get the size. Provide at least that many words in an accessible vector: use a compile-time constant VEC upper bound or a checked GETVEC allocation for a runtime size. Query the complete descriptor, check returned size, format, API major/minor, opcode bitmap and capabilities. Do not call an absent global. Do not assume ordinary operations all take a word capacity: QSAM uses request/result pointers.

## 3. Prepare selection, assemble and link objects

Concatenate MVS macro source members in this order:


```text
BCXPRE
BCXCAT
         BCXREQ BCPLDEMO
BCXPOST
```

The unindented names denote input members, not executable cards. BCXPOST invokes BCXEND. IFOX produces a BCRG registry object and PUNCH INCLUDE statements. Link both with the application, Core Runtime, BLIB and BCPLRGS. Installed catalog EXTLIB DD is the approved read-only FB80 object PDS; temporary source-mode catalogs refer to temporary objects. Use explicit application ENTRY. Even a no-extension application needs one empty registry.

Inspect current [BCXPRE](../../system-extensions/bcx/BCXPRE.asm), [BCXCAT](../../system-extensions/bcx/BCXCAT.asm), [BCXPOST](../../system-extensions/bcx/BCXPOST.asm). The old DEMO-only catalog description is historical. See [R.4](../../packaging/milestones/runtime-extensions/runtime-extensions-r4-closure-20261024.md) and [R.5](../../packaging/milestones/runtime-extensions/runtime-extensions-r5-closure-20261024.md) for actual IFOX/IEWL evidence.

Existing application recipes (submit actual MVS jobs, no package installation):


```sh
tools/bootstrap/run-installed-r5-t1-regression 148
tools/bootstrap/run-production-regression 168
```

The first uses installed R.5/T.1 objects. The second uses the source-selected QSAM writer/reader/verifier. Source-mode PASS is not installed-object acceptance.

## 4. Use multiple extensions without collisions

Select each required package explicitly:


```asm
         BCXREQ BCPLDEMO
         BCXREQ BCPLTIME
```

This is an illustrative card pair using the accepted macro syntax. See actual [case 160](../../tests/system-extensions/bcpltime/160-bcpldemo-bcpltime/source.bcpl), 161 reverse order and 162 requirement upgrade. BCXSEL selects; BCXREQ selects and requires. Repeated selections do not duplicate INCLUDE; a later requirement upgrades an existing selection. Arrange dependency-first order explicitly. The three maintained packages have zero dependencies. DR.5 verified the corrected registrar with two distinct earlier dependencies and a nonzero dependency ordinal; malformed, missing and forward dependencies are rejected in the tested cases. Consult reference chapter 2 for version and evidence limits. Inspect MAP/XREF and global ownership against the [registry](../../packaging/architecture/global-number-registry.md). R2TESTB is a fixture, not a supported package.

## 5. Supply DDs, record geometry and buffers for BCPLQSAM

Allocate the existing sequential dataset or supported SYSOUT in JCL. Example reader DD shape (illustrative, not newly executed; supply the actual DSN):


```jcl
//QINPUT DD DSN=YOUR.INPUT,DISP=SHR,
//          DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
```

The source uses fail-closed RDJFCB geometry preflight and post-OPEN checks; explicit compatible attributes are prudent where otherwise incomplete. A valid DD name alone is insufficient.

Allocate Q=VEC 3 and R=VEC 7, zero reserved fields. OPEN with a counted DD name and mode; retain R!1 handle. INFO with handle and zero remaining request fields returns actual attributes; use R!7 maximum data bytes. Use a compile-time constant local vector, for example `LET BUF = VEC 255` (256 native words, 1024 bytes), declared before commands. That covers the current 1024-byte fixed-record and 1020-byte variable-payload ceilings; check the successful INFO result against the actual allocated capacity. For a dynamically sized buffer, use GETVEC with upper bound `(B+3)/4-1` for positive B bytes, or 0 for zero bytes; check for allocation failure before use and FREEVEC the owned buffer when finished. A local VEC dimension is a compile-time constant, not a runtime expression. The fixed-size example is illustrative; [case 171](../../tests/system-extensions/bcplqsam/171-qsam-v-read/source.bcpl) uses a constant VEC 259 and verifies guard bytes. Ordinary record capacities count bytes; QUERY counts words.

READ with handle, writable buffer and byte capacity. On -1 use R!1 required size and retry the same handle; EOF is status 1, not length zero. WRITE uses exact byte count; F/FB/FBA must match LRECL; V/VB use payload only. Include ASA byte for FBA; do not add RDW/BDW for V/VB. CLOSE with only handle set. Study [168](../../tests/system-extensions/bcplqsam/168-qsam-fixed-full/README.md) and [171](../../tests/system-extensions/bcplqsam/171-qsam-v-read/README.md) for independent byte verification, retry and EOF.

## 6. Use time and demo services

The [BCPLTIME direct caller](../../system-extensions/bcpltime/test.bcpl) checks QUERY then STCK (three output words: high, low, CC) and TIME DEC (two raw R0/R1 words). Treat them as bit patterns, not independently established calendar fields. The BCPLDEMO tutorial uses case 151 to retrieve 10, 20, 30 and check a sentinel. These are sample values, not pointers.

## 7. Handle statuses, close resources and verify results

QUERY, DEMO and TIME return positive word counts for success. QSAM ordinary calls return zero, READ EOF=1 or negative error. Check every result. Do not read stale result fields after unsupported opcode or invalid pointer rejection. Explicitly close owned QSAM handles. On returned CLOSE failure the handle is unusable and ownership uncertain; do not retry blindly. Generic normal FINISH/STOP finalization is not arbitrary abend recovery.

Compare actual records and independent verifier output. Cases 175/176 require device opt-in: --allow-device on the coordinator only with operator authorization. --resume-punch may issue JES2 $S PUN1 and release unrelated queued work; do not use indiscriminately. Rendered printer/punch output is not raw EBCDIC record identity.

## 8. Diagnose selection, registration, linkage and MVS errors

| Symptom | Check |
| --- | --- |
| IFOX unknown package | Catalog version, name, concatenation |
| IEWL unresolved or unexpected module | INCLUDE, EXTLIB, object member, explicit ENTRY, MAP/XREF |
| Startup RC12 | Registration diagnostic, extents, identity, version, ownership, dependencies |
| QUERY -1/-3 | Real storage, word capacity, null/negative arguments |
| QSAM -5/-6/-9 | DD, preflight/effective geometry, supported formats |
| QSAM -7/-8 | Handle validity and direction |
| QSAM -11/-14 | Resource refusal or uncertain CLOSE; no forced recovery |
| Abend or missing output | Actual JES/GO and device diagnostics |

Use job-summary and dump-report-for-job for known jobs; do not blindly repeat a timed-out submission. Preserve original failure evidence. See [reference](Reference-for-System-Extensions.md) for distinct status namespaces.
