# Dynamic BCPLIO streams — M1 progress log

Status: **M1 in progress; assembler ABI integration JOB 5766 accepted; compiled BCPL validation pending**  
Started: 2026-10-16  
Predecessor: [M0 contract](Milestone-BCPLIO-dynamic-stream-M0-contract.md)

## First implementation slice: DD-name normalization

A private non-exported helper `IONORM` was added to `native-compiler/asm/bcplio.asm`, with **no caller and no change to FINDINPUT/FINDOUTPUT**. This is deliberately an isolated M1 staging step, not functional arbitrary-DD discovery.

Contract: native R14-linked private call, R1 byte address of a counted BCPL string, R2 eight-byte caller-owned destination; R15=0 for valid DD name and 8 for invalid. R10 is clobbered; other registers except result R15 are saved/restored. Accept 1–8 characters, convert EBCDIC lowercase alphabetic ranges to uppercase, pad with EBCDIC blanks, validate alphabetic/@/#/$ initial character and alphabetic/digit/@/#/$ subsequent characters. It relies on the established MVS EBCDIC input representation, **not ASCII bytes in the string**.

## Verification status

- Source format: staged helper lines checked at <=71 characters for IFOX fixed-card compatibility.
- The staging helper is not yet assembled by IFOX, linked by IEWL, or executed under MVS. Register preservation, addressing and instruction legality remain hypotheses until these checks.
- Existing FIND operations retain their fixed-name implementation; **no regression or new-stream success is claimed**.
- Before wiring the helper, create a direct MVS assembler harness proving mixed-case normalization and rejection of zero-length, 9-character, illegal and digit-leading names. Verify the exact byte output and preserved registers. Correct any IFOX diagnostics first.
- Next slice: conditional GETMAIN-backed descriptor/DCB/buffer ownership and stable handle identity; RDJFCB validation/OPEN; wire FIND after tests. Stale handles must never alias a reused active handle.
- Keep production OBJ and unrelated compiler/BLIB objects untouched. Rebuild candidate through PDS-resident `BLDDEVI`; do not copy binary objects using `dspal put`.

## Gate status

M1 **not accepted**. Required exit remains arbitrary third input/output DD names, absent-DD nonfatal return zero, and no static allowlist, with integrated candidate MVS evidence and baseline regression preservation.


## Second implementation slice: isolated IFOX/IEWL/GO probe

- Exported `IONORM` as a native-private BCPLIO ENTRY (not a new BCPL G slot).
- Added `native-compiler/asm/bcplio-name-probe.asm` (`IONMPRB`) and `native-compiler/jcl/bcplio-name-probe.jcl`.
- Probe checks mixed/lowercase `customer` and `RepOrt`, digit after a letter, zero-length, over-eight-character, and digit-leading name. Expects native RC=0 for accepted and RC=8 for rejected names, with exact normalized eight-byte EBCDIC comparisons.
- JCL references `HERC02.BCPL.NATIVE.ASM(IONMPRB)` and links `HERC02.BCPL.NATIVE.DEVOBJ(BCPLIO)`; no production object library modifications.
- Do **not** treat file creation or static inspection as assembler or runtime acceptance. IFOX and IEWL have not run for these additions.

Operator execution sequence (from repository root after `git pull --ff-only`):

```sh
tools/datasets/dspal put NATIVE_ASM BCPLIO native-compiler/asm/bcplio.asm
tools/datasets/dspal put NATIVE_ASM IONMPRB native-compiler/asm/bcplio-name-probe.asm
tools/datasets/dspal put NATIVE_JCL IONMPRB native-compiler/jcl/bcplio-name-probe.jcl
tools/datasets/dspal submit NATIVE_JCL BLDDEVI
# Verify payload ASMIO and PUTIO RC=0000, no severe IFOX diagnostics.
tools/datasets/dspal submit NATIVE_JCL IONMPRB
# Verify payload ASMNORM, LKED, GO all RC=0000.
# Confirm IEWL MAP/XREF resolves IONORM to DEVOBJ(BCPLIO).
```

Before running, verify the installed `BLDDEVI` member still targets the current `NATIVE.ASM` and `NATIVE.DEVOBJ` datasets. Preserve JES job numbers and failure listing if anything disagrees. The normalizer remains disconnected from FINDINPUT/FINDOUTPUT. M1 gate remains open.


## First MVS test feedback (2026-10-16, jobs 5576/5579)

Operator staged ASM(BCPLIO), ASM(IONMPRB), JCL(IONMPRB) in jobs 5571–5573. Payload BLDDEVI JOB **5576**: ASMIO IFOX00 RC=0008, one `IFO209` addressability error at expanded `PUT IO2DCB,IO2BUF` statement 88; PUTIO bypassed. The enlarged CSECT placed IO2DCB outside R10's 12-bit displacement from IOFIN. Corrective source establishes an additional R11 base at IOFIN+4098 (R11 saved/restored by IOFIN), without changing stream semantics. **Not yet reassembled.**

IONMPRB payload JOB **5579**: ASMNORM RC=0000, LKED RC=0008 and GO bypassed. IEWL reported unresolved `IONORM` and missing SYSLIB. Expected because JOB 5576 did not install the new BCPLIO object: DEVOBJ still contains the old module without the IONORM ENTRY. Do not interpret the linker's missing SYSLIB search diagnostic as proof the include DD was absent; retest with installed rebuilt object first.

Retest: synchronize the corrected source, `dspal put NATIVE_ASM BCPLIO native-compiler/asm/bcplio.asm`, submit resident NATIVE_JCL(BLDDEVI), inspect ASMIO=0 and PUTIO=0, then submit NATIVE_JCL(IONMPRB), requiring ASMNORM/LKED/GO RC=0. If new assembler diagnostics or unresolved symbols remain, stop and inspect full report; no DEVOBJ acceptance yet. Production OBJ remains unchanged.


## IONORM MVS validation accepted — 2026-10-16

Operator evidence: installed corrected BCPLIO into NATIVE.DEVOBJ from BLDDEVI payload JOB 5583, IFOX ASMIO RC=0000, IEBGENER PUTIO RC=0000 (0 flagged statements). IONMPRB payload JOB 5586: ASMNORM RC=0000, IEWL LKED RC=0000, GO RC=0000. Link map resolves IONORM to the BCPLIO control section at location X'422'. Six normalization checks passed for customer, RepOrt, DD1, empty name, nine-byte name and digit-leading name. The prior addressability and unresolved-symbol problems are resolved. This accepts the **isolated name normalization helper**; no dynamic stream FIND integration, no M1 march acceptance, and no production OBJ modification are claimed.


## M1 candidate descriptor registry — 2026-10-16

Commit `432b4e8` adds non-wired, private native entries `DALLOC` and `DREL` to BCPLIO. `DALLOC` takes an eight-byte normalized name at R2 and a direction at R3, calls conditional `GETMAIN RC,LV=32`, clears a 32-byte descriptor, copies name/direction, and inserts it at the head of a singly linked active registry. Returns descriptor **byte address** in R15 on success, zero on allocation failure. `DREL` takes R1 descriptor address, searches the registry for identity without dereferencing the supplied untrusted pointer, unlinks on success, and uses matching `FREEMAIN R,LV=32,A=(1)`; R15=0 for success, 8 if absent. Both are R14-linked, use static shared save storage and clobber R10. Not reentrant.

**Important:** DALLOC's returned address is strictly internal. It is **not** a BCPL stream handle and must never be exposed to BCPL. Stable non-reused external handle records, actual DCBs/buffers, RDJFCB discovery, QSAM OPEN, and integration with FIND/END/IOFIN are *not* implemented in this slice. This registry is an isolated substrate only; it deliberately does not change any current stream behavior.

Code has only undergone source-layout inspection (all lines <=71 columns). IFOX assembly, linkage, and runtime validation **pending**. M1 gate remains open. Suggested next validation: stage NATIVE_ASM(BCPLIO), run installed NATIVE_JCL(BLDDEVI), inspect IFOX flagged statements and PUTIO RC; then write an independent registry harness verifying allocate/two inserts, direction/name contents, unlink head/middle, double release rejection, and conditional failure handling before wiring it into FIND.


## Descriptor registry IFOX build accepted; execution pending

Operator staged BCPLIO source via JOB 5587, then ran resident BLDDEVI payload **JOB 5590** on 2026-10-16. ASMIO (IFOX00) RC=0000; PUTIO (IEBGENER) RC=0000; zero flagged statements, zero assembler diagnostic severity. This **accepts assembly and DEVOBJ installation**, but not runtime allocation/free behavior.

An isolated native execution harness is now staged in repository source as `native-compiler/asm/bcplio-registry-probe.asm` (IODRPRB) with `native-compiler/jcl/bcplio-registry-probe.jcl`. It allocates two 32-byte descriptors, verifies direction/name/links, unlinks a non-head descriptor then the head, and checks double release yields 8. Expected assembler, linker and GO RC all zero.

Operator sequence after synchronizing Git:

```sh
tools/datasets/dspal put native_asm IODRPRB native-compiler/asm/bcplio-registry-probe.asm
tools/datasets/dspal put native_jcl IODRPRB native-compiler/jcl/bcplio-registry-probe.jcl
tools/datasets/dspal submit native_jcl IODRPRB
```

Do not claim acceptance until the payload's ASMREG, LKED and GO steps succeed under MVS. Keep `NATIVE.OBJ` untouched. Dynamic DCBs, RDJFCB, stable external handles and FIND dispatch remain unimplemented.


## Descriptor registry execution acceptance — 2026-10-16

Operator staged NATIVE.ASM(IODRPRB) via JOB 5591 and NATIVE.JCL(IODRPRB) via JOB 5592. Resident JCL launch JOB 5594, payload **JOB 5595**, completed successfully: ASMREG IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000; assembler flagged 0 statements, highest severity 0. The standalone probe's GO success supports its assertions for two allocations, descriptor names/directions and linkage, unlinking non-head and head nodes, matching FREEMAIN, and double-release rejection. This **accepts the isolated descriptor-registry execution checkpoint**. The test does not demonstrate allocation failure under actual storage pressure, stable BCPL handle identity, RDJFCB/DD discovery, OPEN, or FIND integration. Those remain M1 work. No production OBJ change was made.


## Stable handle lifecycle staging — 2026-10-16

Source commit `1995a7f` adds three private native BCPLIO entries, without changing FIND, QSAM operations, or global slots: `HNEW` (R1=descriptor address; R15=word-address identity handle or 0), `HLOOK` (R1=handle; R15=live descriptor or zero), and `HCLOSE` (R1=handle; R15=detached descriptor or zero, then invalidates handle). Each handle uses conditional GETMAIN for a 16-byte retained record; record +4 holds the live descriptor pointer. The BCPL handle is the **word address of that record's +4 field**, consistent with existing opaque word-address conventions. Registry search compares the supplied handle without dereferencing it, so stale handles do not touch freed descriptors. Handle records are intentionally never reused; reclamation at IOFIN is **still to be implemented**, as is rollback if caller cannot complete descriptor setup. The HCLOSE caller must independently release the returned descriptor using DREL.

Independent probe sources `native-compiler/asm/bcplio-handle-probe.asm` (IOHPRB) and `native-compiler/jcl/bcplio-handle-probe.jcl` test allocation/lookup/close, DREL, second open with distinct handle, old-handle rejection across possible recycled descriptor storage, and double close. No MVS assembly, linkage or execution result is claimed for these additions.

Operator validation after git pull:

```sh
tools/datasets/dspal put native_asm BCPLIO native-compiler/asm/bcplio.asm
tools/datasets/dspal put native_asm IOHPRB native-compiler/asm/bcplio-handle-probe.asm
tools/datasets/dspal put native_jcl IOHPRB native-compiler/jcl/bcplio-handle-probe.jcl
tools/datasets/dspal submit native_jcl BLDDEVI
# Require ASMIO=0000 and PUTIO=0000 before submitting IOHPRB.
tools/datasets/dspal submit native_jcl IOHPRB
# Require ASMHND=0000, LKED=0000 and GO=0000.
```

M1 acceptance remains pending; all work is isolated to NATIVE.DEVOBJ and repository sources.


## Stable handle MVS acceptance — 2026-10-16

Operator staged NATIVE.ASM(BCPLIO) JOB 5596, NATIVE.ASM(IOHPRB) JOB 5597, and NATIVE.JCL(IOHPRB) JOB 5598. Resident BLDDEVI payload **JOB 5601**: ASMIO IFOX00 RC=0000 and PUTIO IEBGENER RC=0000, zero flagged statements. IOHPRB payload **JOB 5604**: ASMHND IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000, zero flagged statements. The standalone probe passed creation/lookup, close and DREL, stale-handle rejection after allocating a second descriptor, distinct handle identity, and double-close rejection. **Accept isolated stable-handle checkpoint.** IOFIN reclamation, conditional failure edge cases, dynamic DD discovery and FIND integration are still pending. No production OBJ promotion.


## RDJFCB discovery staging — 2026-10-16

A private `DDVERIFY` entry was added to BCPLIO. Its native R14 calling contract accepts R1 pointing to a normalized EBCDIC eight-byte DD name, returns R15=0 for RDJFCB success or 8 otherwise, and clobbers R10. It uses a separate scratch DCB, writes the DDNAME at DCB +40 (as established by the IFOX-generated DCB expansions), and issues `RDJFCB ((2))`. This is **only a DD allocation inquiry**: it does not OPEN, create descriptors, allocate handles, or connect to BCPL FIND calls. Nonreentrant module-level storage remains the design baseline.

An independent `IODVPRB` test checks the GO step's allocated `CUSTOMER` DD, unallocated `ZXYZ1234`, then `CUSTOMER` again. JCL allocates CUSTOMER against `SYS1.MACLIB` with DISP=SHR and explicitly includes the independent BCPLIO in the link. Source and JCL are staged in `native-compiler/asm/bcplio-ddverify-probe.asm` and `native-compiler/jcl/bcplio-ddverify-probe.jcl`. IFOX, IEWL and GO **not yet executed** for this slice; RDJFCB error/flag semantics and DCB scratch reuse require observation under MVS.

Run after synchronizing Git:

```sh
tools/datasets/dspal put native_asm BCPLIO native-compiler/asm/bcplio.asm
tools/datasets/dspal put native_asm IODVPRB native-compiler/asm/bcplio-ddverify-probe.asm
tools/datasets/dspal put native_jcl IODVPRB native-compiler/jcl/bcplio-ddverify-probe.jcl
tools/datasets/dspal submit native_jcl BLDDEVI
# Require ASMIO / PUTIO both RC=0000.
tools/datasets/dspal submit native_jcl IODVPRB
# Require ASMDV / LKED / GO all RC=0000.
```

Production NATIVE.OBJ remains out of scope. M1 not yet accepted.


## RDJFCB first MVS run — JOB 5613 — FAILED, correction staged

Operator rebuilt BCPLIO into DEVOBJ with BLDDEVI payload JOB 5610 (ASMIO=0000, PUTIO=0000). IODVPRB payload JOB 5613 completed ASMDV=0000 and LKED=0000, but **GO ABEND S240-08** (IEC155I 240-08 in IGC0006D). The scratch DCB originally specified no EXLST. RDJFCB requires a JFCB exit-list entry and target area; lacking it raises the S240-08 condition. The dump includes a static message string about blank DDNAME, but that is *not* the emitted JES diagnostic and should not be diagnosed as the cause without further evidence. IBM documents 240-08 as absent DCB EXLST address in this interface. The analogous ICINT v19 templates use EXLST=GENEXL and a X'87' JFCB exit entry to a 176-byte work area.

Corrective commit 9489142 adds EXLST=DVEXL to DVDCB, a fullword-aligned DVEXL DC X'87',AL3(DVJFCB), and DVJFCB DS CL176. Not yet reassembled or tested. Re-stage BCPLIO, rebuild BLDDEVI and rerun IODVPRB, recording all steps. Do not claim RDJFCB checkpoint acceptance until GO RC=0000.


## RDJFCB discovery acceptance — 2026-10-16

Operator restaged corrected BCPLIO as JOB 5614. BLDDEVI payload **JOB 5617**: ASMIO IFOX00 RC=0000, PUTIO IEBGENER RC=0000; zero assembler statements flagged. IODVPRB payload **JOB 5620**: ASMDV IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000; zero statements flagged. The GO result accepts the probe assertions: allocated CUSTOMER DD succeeds, absent ZXYZ1234 DD fails gracefully, and repeated CUSTOMER lookup succeeds. The previous S240-08 (JOB 5613) was resolved by supplying the JFCB exit list and 176-byte JFCB area. **Isolated DDVERIFY checkpoint accepted.** No FIND wiring, QSAM OPEN, production OBJ promotion, or whole-M1 acceptance is asserted.


## Explicit native BCPL regression gate adopted — 2026-10-16

M1 acceptance now requires compiled-BCPL panel tests for the new public FIND features, not merely assembler helper probes. The milestone M1 exit clause was amended and M5 clarified as expansion of tests begun in M1. The planned contiguous IDs 124..130, with test 131 reserved for 13 streams (potential M2 gate), test DD configurations, expected evidence and runner/link-mode prerequisite are recorded in `native-compiler/regression/dynamic-stream-M1-test-plan.md`. These test cases are **planned, not created or executed**; existing 00..123 remain intact. Critical dependency: explicitly ensure the native regression runner tests DEVOBJ BCPLIO rather than assuming its currently monolithic BCPLMAIN path exercises the newly staged routines. The M1 gate remains open.


## Development-only BCPL regression linkage staged — 2026-10-16

Added `tools/native/run-dynamic-regression` (invoke with `bash`), requiring explicit `BCPL_DYNAMIC_MAIN_MEMBER=BCPLM3..BCPLM7`. It selects existing candidate mode with development BCPLMAIN and BCPLIO from NATIVE.DEVOBJ, BCPLBYTE/BCPLAPT from NATIVE.DEVOBJ, and BLIB/BCPLMEM from production NATIVE.OBJ, with explicit COREOBJ DD routing fixed in `prepare-runtime-pds-regression.py`. Normal native regression defaults are unchanged. This mode has **not been executed** in the current M1 checkpoint; do not claim a candidate BCPLMAIN object exists in PDS after rebuild. Next operator work: verify/rebuild source-derived compatible BCPLMAIN candidate, inspect generated JCL and link map, then run legacy stream cases 114..119 in development mode. BCPL 124..130 cases remain planned, not created.


## Development BCPLMAIN candidate absent; source rebuild prepared

Operator `tools/datasets/dspal ls native_DEVOBJ` returned only `BCPLAPT`, `BCPLBYTE`, and `BCPLIO`; **no BCPLM3..BCPLM7** development object is installed. Consequently, the dynamic regression launcher cannot yet execute. Rather than migrate a binary, the repository retains `native-compiler/asm/bcplmain-d7-candidate.asm`, a modular BCPLMAIN candidate. A modern dataset-qualified JCL source `native-compiler/jcl/build-native-bcplm7-for-dynamic.jcl` has been added to assemble NATIVE.ASM(BCPLM7) and install only NATIVE.DEVOBJ(BCPLM7). This is an *unverified source-build candidate*, not new design acceptance. Its ability to link against current BCPLIO and execute regressions must be established.

Operator procedure (staging and build only, no production OBJ writes):

```sh
git pull --ff-only
tools/datasets/dspal put native_asm BCPLM7 native-compiler/asm/bcplmain-d7-candidate.asm
tools/datasets/dspal put native_jcl BLDD7MN native-compiler/jcl/build-native-bcplm7-for-dynamic.jcl
tools/datasets/dspal submit native_jcl BLDD7MN
```

Require IFOX assembler and PUTMAIN RC=0000, confirm `native_DEVOBJ` lists BCPLM7, then run `BCPL_DYNAMIC_MAIN_MEMBER=BCPLM7 bash tools/native/run-dynamic-regression 114 119`. Inspect the generated JCL's OBJ/DEVOBJ/COREOBJ routing and link map, along with all regression results. If source build or linkage fails, diagnose before attempting dynamic FIND integration. D7 object presence and compatibility **not yet verified**.


## D7 modular rebuild and preliminary BCPL regression — 2026-10-16

Operator staged NATIVE.ASM(BCPLM7) JOB 5622 and NATIVE.JCL(BLDD7MN) JOB 5623; BLDDEV D7 payload **JOB 5626**: ASMMMAIN IFOX00 RC=0000, PUTMAIN IEBGENER RC=0000 (0 flagged statements). NATIVE.DEVOBJ then enumerated BCPLAPT, BCPLBYTE, BCPLIO, BCPLM7. Invoked `BCPL_DYNAMIC_MAIN_MEMBER=BCPLM7 bash tools/native/run-dynamic-regression 114 119`. Results: **PASS 116,117,118; FAIL 114 (RG114R JOB 5629), 115 (RG115R JOB 5631), 119 (RG119R JOB 5639)**. All failing applications assembled and link-edited RC=0000, but their GO steps abended (no system code in supplied short summaries). The 114,115,119 regression fixtures include `expected-alt.txt`, which requests a BCPALT output DD; this is a correlation, not yet proof of root cause. Do not accept development BCPLIO compatibility or add new FIND tests based on this partial pass. Obtain the complete report for JOB 5629 (and perhaps 5631), including IEF450I and SYSUDUMP, before source modifications. The current `prepare-runtime-pds-regression.py` generator includes BCPALT DD if `expected-alt.txt` is present, so absence of allocation is not yet established. No production OBJ write occurred.


## JOB 5629 complete SYSUDUMP analysis — S0C4, suspect return linkage

The operator supplied `dump-report-for-job 5629` (RG114R, 2026-10-16). JES: ASMAP RC=0000, LKED RC=0000, **GO ABEND S0C4** (`IEF450I`, `IEF472I`). IEWL map: `BCRG0114` origin X'0000', `BCPLMAIN` X'0138', `BCPLIO` X'0D38' (IOFIN X'0D9C'), total length X'41B0'; load-module entry X'000A5E50' and extent to ~X'000AA000'. The failing PSW is `078D0000 001407FE`; R14 at time of error is `D01407FE`. The low 24 bits of R14 equal the failing PSW address X'1407FE', **outside the linked module**. This is evidence consistent with branching via a corrupted return register, not proof of which routine altered it. The GO TIOT and JCL both show BCPALT allocated. Output-related cases 114,115,119 failed; 116..118 passed. In BCPLIO, specifically inspect IOWRCH/IOENDW/IOFIN R14 saves/restores and interaction with QSAM PUT/CLOSE macros. IOFIN now also establishes a second R11 USING base to resolve DCB displacement; verify the IFOX expansion/addressing before presuming it correct. Do not ascribe the S0C4 to missing DD or to new dynamic-descriptor routines without a causal trace. Require focused diagnostic evidence (e.g. failing-step dump with source-correlated runtime listing) before modifying source. M1 BCPL regression gate remains blocked, and production NATIVE.OBJ stays unchanged.


## JOB 5631 secondary-output S0C4 comparison — 2026-10-16

Operator supplied full `dump-report-for-job 5631`: RG115R ASMAP RC=0000, LKED RC=0000, GO **ABEND S0C4**. Program load begins X'000A5E10'; module length X'41F0'; PSW instruction X'001407FE' lies outside this load module. R15 = X'D01407FE' (address low 24 bits X'1407FE'), R14 = X'600A70F2'. **Correction to prior JOB 5629 analysis:** X'D01407FE' was **R15**, not R14. JOB 5629 likewise has R15 X'D01407FE', PSW X'001407FE', but R14 X'600A6CAA'. Link map places BCPLIO at relative X'0D78' in 5631, with `IOENDW` relative X'12AA'; runtime `IOENDW` therefore begins X'000A70BA', placing R14 low-24-bit address X'000A70F2' within that routine. These details significantly narrow the reproduction to secondary-output linkage and QSAM PUT/CLOSE or their DCB state, but do **not** identify the specific fault-producing instruction. `BCPALT` is allocated in JCL/TIOT; don't treat missing allocation as cause. Next inspect the actual IFOX expansion for BCPLIO `IOENDW` (particularly PUT and CLOSE) using the BLDDEVI assembler listing and independently compare output-path macro linkage in passing tests. No source fix or M1 gate acceptance yet.


## S0C4 diagnostic gate: exact IOENDW instruction map

Both JOB 5629 and JOB 5631 fault with PSW X'001407FE' and R15 X'D01407FE'. The R14 low 24-bit value in JOB 5631 is X'000A70F2'; subtracting load origin X'000A5E10' gives relative X'12E2', exactly IOENDW (X'12AA') + X'38'. That identifies a return/continuation site within IOENDW, but not the macro operation producing the bad R15. The earlier interpretation of R15 as R14 was incorrect and has been corrected.

The next evidence required is the actual IFOX00 BCPLIO assembler listing from BLDDEVI JOB 5617, which was assembled with LIST/XREF/ESD/RLD. Extract the section around IOENDW, IOEWCLOS, IOEWRET, and the PUT/CLOSE macro expansion and correlate machine-code offset X'12E2'. Do not assume source lines correspond directly to machine-code offsets; do not patch QSAM code speculatively. Operator command: `tools/mvs/dump-report-for-job 5617 > /tmp/bcplio-5617.txt`; then `grep -n -E 'IOENDW|IOEWCLOS|IOEWRET|CLOSE|PUT' /tmp/bcplio-5617.txt | head -100`, followed by surrounding line inspection. The current development BCPL regression gate remains 3 PASS / 3 FAIL; production NATIVE.OBJ unchanged.


## IFOX PUT macro correlation — JOB 5617 listing supplied

Operator extracted IFOX listing for staged BCPLIO from JOB 5617. `IOENDW` begins at BCPLIO-relative X'0532', which corresponds to combined-module relative X'12AA' in JOB 5631. The expanded `PUT IO2DCB,IO2BUF` has `L 15,48(0,1)` at BCPLIO X'0564' and `BALR 14,15` at X'0568'. Its continuation is X'056A': application absolute address X'000A70F2', precisely the low 24 bits of dump R14 X'600A70F2'. Dump R15 is X'D01407FE' and PSW target X'001407FE'. **Mechanism established:** QSAM PUT calls through the unusable routine pointer loaded from IO2DCB+48. This is not a BR 14 return-address problem. Cause of bad DCB pointer remains to be determined: unopened/closed DCB, failed OPEN, or overwrite are among possibilities, not findings. In particular, IOENDW tests IO2ACTV instead of the MVS DCB OPEN bit, and IOFOUT marks IO2ACTV after OPEN without checking DCB OPEN success; inspect existing DCB state and opening sequence before changing behavior. The existing regression gate remains 3 PASS / 3 FAIL.


## Read-only QSAM pointer diagnostic staged — 2026-10-16

Added private BCPLIO entry `IO2PTR` (returns R15 contents of IO2DCB+48; no normal runtime entry behavior changed), probe `native-compiler/asm/bcplio-qptr-probe.asm` and development JCL `native-compiler/jcl/bcplio-qptr-probe.jcl`. Probe captures +48 before IOINIT and after IOINIT / IOSEL(2), without executing PUT. Return status: RC=0000 changed to nonzero non-matching pointer, RC=0004 unchanged, RC=0008 zero, RC=0012 observed bad D01407FE, RC=0016 IOSEL failure. The `IOSEL` return indicates only its software status, not proven DCB OPEN success. No IOFIN executed within probe to isolate from CLOSE; MVS job cleanup owns closure. This diagnostic is **staged, not run**. It can only separate immediate post-OPEN invalid pointer from a pointer changed later; an unexpected value must still be interpreted with actual DCB state. Build via existing BLDDEVI into DEVOBJ; never write production OBJ. For repeatability record test job numbers, assembler/link/GO RC, and if needed whole SYSUDUMP. No public FIND wiring or runtime correction yet.


## JOB 5645 / JOB 5648 probe outcome — S013-34 on SYSPRINT (2026-10-16)

Operator rebuilt BCPLIO from source into NATIVE.DEVOBJ in BLDDEVI JOB 5645 (ASMIO and PUTIO both RC=0000, zero flagged assembly statements). IO2DPRB JOB 5648 successfully assembled and linked (both RC=0000) but GO abended **S013-34** with JES message `IEC141I 013-34,IGG0199G,IO2DPRB,GO,SYSPRINT`. The probe's GO SYSPRINT was `DD SYSOUT=*` without DCB attributes, unlike existing native regressions specifying `DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)`. Since IOINIT opens SYSPRINT before IOSEL tries BCPALT, this probe never successfully measured BCPALT's post-OPEN PUT pointer; no conclusion about secondary DCB can be drawn. Corrected the probe GO SYSPRINT DD to FB132; **correction not yet submitted/executed**. Next operator task: git pull, re-PUT only JCL IO2DPRB, re-submit IO2DPRB (no BCPLIO rebuild necessary), inspect GO result. Production NATIVE.OBJ unchanged.


## IO2DPRB retry JOB 5652 — secondary OPEN S0C4 (2026-10-16)

After repairing GO SYSPRINT to FB132, operator submitted IO2DPRB JOB 5652: ASMDP RC=0000, LKED RC=0000, **GO ABEND S0C4**. No preceding IEC141I on SYSPRINT. SYSUDUMP: PSW X'078D0000 000A5CB4', ILC=4, INTC=0004; probe entry X'000A5938', BCPLIO IOSEL linked at X'000A5C7E', so failing PSW location is IOSEL+X'36'. Saved probe call context R1 X'00000002', R14 X'400A5962' (probe continuation), R10 X'400A5C80', R15 X'00000002'. MVS TIOT allocates BCPALT. Thus the probe still did **not** capture the post-OPEN pointer; its failure is in the secondary OPEN sequence, not in its diagnostic result comparison. Do not assume the earlier invalid PUT pointer was corruption after a successful OPEN. For next diagnostic, correlate PSW X'000A5CB4' and ILC=4 with the expanded `OPEN (IO2DCB,(OUTPUT))` in the BCPLIO IFOX listing from JOB 5645. Inspect precisely the generated BAL/list/SVC 19 instructions, base registers, and DCB operand. Avoid speculative modifications to BCPLIO or production OBJ until mapping is proven.


## JOB 5645 IFOX listing: leaked R11 base and corrective gate

User-supplied IFOX listing of JOB 5645 resolves JOB 5652's S0C4: `IOSEL` entry relative X'020E', failing PSW relative X'0244' = `MVC IO2BUF+1(131),IO2BUF` (`D282 B003 B002`); preceding MVI is `9240 B002`. The assembler selected R11 for IO2BUF (relative X'1068'), but IOSEL establishes only R10. At runtime R11 is not the IOFIN-specific data base. In the preceding `IOFIN` entry, `USING IOFIN+4098,11` was left active in the assembler until subsequent routines, because the entry ended with `DROP 10` only. R11 restoration at runtime does not cancel an assembler USING. This is a **confirmed base-register-scope defect**, not a QSAM OPEN failure or specifically a bad DCB OPEN indicator. Added `DROP 11` at IOFIN's end immediately before its existing `DROP 10` to limit assembler address selection to appropriately established bases. This fix has **not yet been assembled or tested under MVS**. First require BLDDEVI assembler severity 0 and verify new generated IOSEL MVI/MVC instructions do not reference R11. If assembler diagnoses an out-of-range operand elsewhere, add a locally initialized base in the affected entry, not a global stale USING. Then rerun IO2DPRB and D7 development regressions 114..119; no gate acceptance until six pass and any QSAM pointer validation is resolved. No production OBJ modification.


## Compatibility repair accepted — 2026-10-16

Operator rebuilt `NATIVE.ASM(BCPLIO)` from committed source after `DROP 11` fix: upload JOB 5653, BLDDEVI payload JOB **5656**, ASMIO IFOX00 RC=0000 (zero flagged statements), PUTIO IEBGENER RC=0000; only `NATIVE.DEVOBJ(BCPLIO)` updated. Isolated `IO2DPRB` payload JOB **5659**: ASMDP RC=0000, LKED RC=0000, GO RC=0000. Under its documented diagnostic contract, this is a changed, nonzero IO2DCB+48 pointer different from X'D01407FE'; it does not independently prove every possible DCB lifecycle case. D7 source-built candidate `BCPLM7` plus DEVOBJ BCPLIO with production BLIB/BCPLMEM: `BCPL_DYNAMIC_MAIN_MEMBER=BCPLM7 bash tools/native/run-dynamic-regression 114 119` yielded **6 PASS, 0 FAIL, 0 SKIP**. Previously failing tests 114, 115 and 119 now pass; 116..118 retained PASS. The leaked assembler R11 USING scope was the confirmed cause of this observed regression failure cluster. **Compatibility repair gate accepted.** This is not acceptance of M1 dynamic FINDINPUT/FINDOUTPUT, per-DD OPEN/CLOSE, or planned regressions 124..130. Production NATIVE.OBJ unchanged.


## M1 new march: private dynamic-DD QSAM output probe staged

Staged `native-compiler/asm/dynamic-qsam-output-probe.asm` (entry DQOPRB) and `native-compiler/jcl/dynamic-qsam-output-probe.jcl`. This deliberately minimal, self-contained assembler probe uses a static prototype QSAM DCB with `DDNAME=DUMMY`, overwrites the verified DDNAME field at DCB+40 with EBCDIC `REPORT` **at runtime**, issues OPEN OUTPUT, validates the initialized QSAM PUT dispatch word at DCB+48 against zero and the previously observed invalid value, PUTs one FB132 logical record `DYNAMIC QSAM DD PROBE PASSED`, then CLOSEs. JCL allocates only `REPORT DD SYSOUT=*` with explicit FB132; there is no DUMMY allocation. Requires GO RC=0000 *and* record on REPORT, with zero assembler errors. **This is not yet dynamically allocated per-descriptor DCB storage, nor a BCPLIO API, and the probe has not been run.** After this gate: add per-stream owned QSAM storage to DALLOC, map DCB/buffer and state to HNEW/HLOOK/HCLOSE, and provide a private lifecycle probe with multiple independent DDs; only then wire BCPL FINDOUTPUT. Development and production OBJ are not modified by this source/JCL-only step.


## Private dynamic-DD QSAM output probe accepted — JOB 5676 (2026-10-16)

Operator staged `DQOPRB` source and JCL (PUT jobs 5672/5673); executed payload JOB **5676**, launcher JOB 5675. `ASMDQ` IFOX00 RC=0000 (zero flagged statements, severity 0), `LKED` IEWL RC=0000, GO RC=0000, no abend. Full JES report contains a separate `REPORT` SYSOUT logical record `DYNAMIC QSAM DD PROBE PASSED` (visible after link map). The IFOX listing confirms execution-time replacement of DCB DDNAME at +40 (`MVC OUTDCB+40(8),DDNAME`), followed by `OPEN`, dispatch pointer check, `PUT`, and `CLOSE`. The DCB's assembly-time DDNAME was `DUMMY`; GO JCL allocated `REPORT` only. **Accept private runtime-selected DDNAME QSAM output gate.** The probe's DCB is static; this result does not yet establish dynamically allocated DCB/buffer instances, input GET, two simultaneous streams, or BCPL FIND wiring. No NATIVE.DEVOBJ or production OBJ altered by this isolated probe.

## Next gate: descriptor-owned QSAM storage and two independent outputs

Retain 32-byte DALLOC descriptor ABI and stable 16-byte handle records. Proposed descriptor extension: +16 owned storage pointer, +20 owned DCB pointer, +24 record position/state, +28 flags (exact fields to finalize in implementation). Allocate the DCB and FB132 buffer as descriptor-owned storage with a well-defined FREE path; install the CL8 DDNAME from +8 in the DCB at +40; do not keep a global OPEN/CLOSE parameter-list address tied to one stream. Verify the MVS SVC19/SVC20 execute parameter-list format from actual IFOX listings and dynamically substitute the DCB address; the static inline OPEN/CLOSE macros from DQOPRB cannot themselves select an arbitrary per-descriptor DCB. Confirm each OPEN succeeded before PUT. The acceptance probe should OPEN `REPORT` and `REPORT2` simultaneously, interleave distinct 132-byte PUT records, CLOSE one while the other stays usable, close the other, and verify separate SYSOUT outputs. Exercise HNEW/HLOOK/HCLOSE/DREL lifecycle including stale-handle miss and descriptor release. Keep this private: public BCPL `FINDOUTPUT` remains unwired until this passes. Preserve proper assembler USING/DROP scope, rebuild only development artifacts, and leave production OBJ untouched.


## M1 two-output allocated-QSAM prototype staged (unexecuted)

Added `native-compiler/asm/dynamic-qsam-two-output-probe.asm` (`DQ2PRB`) and `native-compiler/jcl/dynamic-qsam-two-output-probe.jcl`. This isolated prototype obtains two 288-byte private regions via GETMAIN, each with a 32-byte descriptor envelope, 132-byte record buffer, separate 96-byte IFOX DCB copied from an unopened template, and private four-byte SVC19/SVC20 lists. It replaces DCB+40 with the descriptor's normalized DD name; list DCB addresses are installed via STCM. Both REPORT and REPORT2 OPEN concurrently; PUT records are interleaved; REPORT closes before final REPORT2 PUT and CLOSE; each region is freed after close. The expected SYSOUT records are REPORT: `REPORT RECORD ONE`, `REPORT RECORD TWO`; REPORT2: `REPORT2 RECORD ONE`, `REPORT2 RECORD TWO`. Require ASMDQ/LKED/GO RC=0000, zero assembler flags, no abend, exact records under respective JES DD SYSOUT. **Not yet assembled or run.** The probe duplicates descriptor layout as a private prototype; it is NOT integrated into BCPLIO DALLOC/HNEW/HLOOK/HCLOSE/DREL and cannot satisfy that separate integration gate by itself. The next slice is to factor the proved allocation/open/close into BCPLIO's private descriptor operations and test actual stable-handle lifecycle. Leave public FINDINPUT/FINDOUTPUT unwired and production OBJ unchanged. Beware IFOX/S370 SS instruction max length 256: prototype clears 288 bytes with XC 256+32, not XC(288).


## JOB 5681 JCL ingestion failure and correction

Operator staged DQ2PRB as ASM JOB 5677 and JCL JOB 5678, and submitted payload JOB **5681**. JES reported `IEF452I DQ2PRB JOB NOT RUN - JCL ERROR` / `IEF607I JOB HAS NO STEPS`, with **three cards read** and zero executed steps; hence no evidence concerning two-stream assembler execution. Repo source JCL had a `//* Development test only...` comment directly after the two-line JOB statement. Removed that line so `//ASMDQ EXEC` immediately follows the JOB header; this is a cautious deck-shaping correction, not yet an independently verified explanation of why input stopped at three records. Stage only the revised JCL member and resubmit. If JES still sees only the header, inspect DSPAL transport/card reader treatment of internal `//*` comments and ensure the actual staged member contains the full deck. Do not modify assembler source or production OBJ on the strength of JOB 5681.


## JOB 5686: confirmed duplicate JOB card in dspal submit payload

Re-submitted DQ2PRB after removal of an inline `//*` comment: upload JOB 5683, launcher JOB 5685, payload JOB **5686**, still `IEF607I JOB HAS NO STEPS` with 3 cards read. Inspected `tools/datasets/dspal-submit.py`: the launcher first creates `&&PAYLOAD` containing an *authenticated generated JOB card* for member DQ2PRB, APPENDs the stored PDS JCL member unchanged, then submits combined sequential FB80 deck through INTRDR. Our DQ2PRB source JCL independently began with its own two-line `//DQ2PRB JOB`, so the next JOB card prematurely delimited the generated job and left it without EXEC statements. **Confirmed double-JOB error**, unrelated to assembler or QSAM. Removed the embedded two-line JOB header; the PDS member now begins directly with `//ASMDQ EXEC`. The probe has not yet executed. For next run, restage **only** `native_jcl DQ2PRB` and resubmit; review assembler and GO results separately. Do not add explicit JOB cards to decks submitted using dspal. Production OBJ unchanged.


## JOB 5691: two-output allocated-QSAM prototype executes RC=0000

Operator restaged corrected JOB-card-free DQ2PRB JCL via JOB 5688; launcher JOB 5690, payload JOB **5691** on 2026-10-16. `ASMDQ` IFOX00 RC=0000, no flagged statements/severity zero; `LKED` IEWL RC=0000; `GO` RC=0000; no reported abend; JES reports 30 cards and 408 SYSOUT records. This proves the private probe completed its dynamic two-region OPEN/PUT/CLOSE/FREEMAIN path without observed failure. **Output-content gate pending**: operator should show the `REPORT RECORD ONE/TWO` and `REPORT2 RECORD ONE/TWO` lines in the full job report and confirm DD separation. Do not conflate this isolated prototype with actual BCPLIO DALLOC/HNEW lifecycle integration. Production OBJ remains unchanged.


## JOB 5691: two-stream private QSAM gate accepted (2026-10-16)

Operator used `tools/mvs/dump-report-for-job 5691` and showed actual SYSOUT output (not merely assembler source lines): line 455 `REPORT RECORD ONE`, line 456 `REPORT RECORD TWO`, line 458 `REPORT2 RECORD ONE`, line 459 `REPORT2 RECORD TWO`. The corresponding assembler literal definitions also occur at lines 316–319; acceptance relies on **lines 455–459**. Combined with ASMDQ/LKED/GO all RC=0000, zero flagged assembler statements, the separate REPORT and REPORT2 SYSOUT sections and expected record order satisfy this private two-descriptor prototype gate. **Accept private two-stream QSAM storage lifecycle prototype.** Next work: integrate actual BCPLIO DALLOC/DREL and HNEW/HLOOK/HCLOSE on DEVOBJ, validate independently; do not infer that public FINDOUTPUT has already been implemented. Production NATIVE.OBJ remains unchanged.


## M1 DEVOBJ descriptor/handle QSAM integration staged — awaiting MVS validation

BCPLIO `DALLOC` now allocates its historical 32-byte descriptor plus a separately owned 268-byte region containing a 132-byte record buffer, private 96-byte copy of an unopened IFOX-generated QSAM OUTPUT DCB, and private OPEN/CLOSE SVC parameter lists. Descriptor +16/+20/+24 hold the region, DCB address, and OPEN state; the 32-byte descriptor size and HNEW/HLOOK/HCLOSE identities are unchanged. DREL frees the QSAM region and descriptor only if not open. Private `DQOPEN`, `DQPUT`, `DQCLOSE` use descriptor pointers and the proven SVC19/20 and QSAM PUT approach, with no BCPL global-vector wiring. Source is staged only; no MVS assembly evidence yet. Added `DQHPRB` assembler/JCL to allocate two descriptors via DALLOC, create/resolve handles with HNEW/HLOOK, independently OPEN REPORT/REPORT2, PUT interleaved records, CLOSE and invalidate first handle, verify HLOOK stale miss, DREL first, continue writing second, then CLOSE/HCLOSE/DREL second. Require build of DEVOBJ(BCPLIO) via BLDDEVI, ASM/LKED/GO RC0, and output REPORT `DQH REPORT ONE`, REPORT2 `DQH REPORT2 ONE` and `DQH REPORT2 TWO`; check full output independently. No production OBJ changes; milestone not yet accepted. Potential assembler base-range and macro issues must be diagnosed from IFOX listing rather than presumed resolved.


## JOB 5697 assembler RC=0008: shared DQ return block base scope (2026-10-16)

Operator uploaded BCPLIO and DQHPRB source (JOB 5692/5693), JCL (JOB 5694), submitted BLDDEVI launcher JOB 5696, payload JOB **5697**. IFOX ASMIO RC=0008, severity 8; PUTIO skipped; **DEVOBJ was not replaced**. Assembler listing flags statements 1508, 1510–1513 (`B DQRET`, `ST 15,DQRESULT`, `LM ... DQSAVE`, `L 15,DQRESULT`) in shared `DQGOOD`/`DQBAD`/`DQRET` tail. Prior DQCLOSE ended with `DROP 10`, leaving no valid active USING for references in the tail. This is analogous to the previous incorrect assembler scope, but here no USING exists. Source corrected by giving DQGOOD a local BALR R10,0/USING */DROP scope for its branch, and by establishing a fresh BALR R10,0/USING * on entry to DQRET, including paths from DQBAD. MVS assembler rerun and DQHPRB probe remain pending. Do not run DQHPRB against stale DEVOBJ after BLDDEVI fails; only rebuild DEVOBJ after severity 0.


## JOB 5701 and 5704: integrated descriptor/handle execution RC0 (2026-10-16)

Operator staged updated BCPLIO in ASM JOB 5698; BLDDEVI launcher JOB 5700, payload JOB **5701**: ASMIO IFOX00 RC=0000, zero statements flagged and highest severity zero; PUTIO IEBGENER RC=0000, DEVOBJ(BCPLIO) rebuilt. Then DQHPRB launcher JOB 5703, payload JOB **5704**: ASMDQ IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000, zero flagged assembler statements. Integration probe successfully returned through descriptor allocation, stable-handle creation/lookup, OPEN/PUT, first CLOSE/HCLOSE, stale-handle HLOOK miss, first DREL, second PUT/CLOSE/HCLOSE/DREL without failing its assertions. **SYSOUT content verification remains pending**: inspect report to establish REPORT `DQH REPORT ONE`, REPORT2 `DQH REPORT2 ONE` and `DQH REPORT2 TWO` are actual output records (not assembler literal listings). No production OBJ modifications reported. Do not close M1 or public FIND gate on these results.


## JOB 5704: BCPLIO descriptor/handle integration gate ACCEPTED (2026-10-16)

Operator extracted full job report with `tools/mvs/dump-report-for-job 5704` and confirmed **actual output records**: line 455 `DQH REPORT ONE`; line 457 `DQH REPORT2 ONE`; line 458 `DQH REPORT2 TWO`. These appear after the assembler listing and correspond to the separately allocated REPORT and REPORT2 DD SYSOUT outputs. Combined with JOB 5701 DEVOBJ BCPLIO `ASMIO/PUTIO RC=0000`, JOB 5704 `ASMDQ/LKED/GO RC=0000`, zero flagged statements, and the probe's explicit descriptor/handle/stale-handle assertions, **accept the private BCPLIO descriptor-owned QSAM and stable-handle lifecycle gate**. This is an internal output-stream gate, not acceptance of BCPL FINDOUTPUT, FINDINPUT, dynamic input, or full M1. Next integration: programmer-visible `FINDOUTPUT` with runtime DD normalization, allocation verification, dynamic DALLOC/HNEW/DQOPEN, selection, write, and ENDWRITE while preserving legacy streams and protecting production OBJ.


## M1 programmer-visible FINDOUTPUT fallback staged — first slice, untested

Modified BCPLIO `IOFOUT` to preserve recognized `SYSPRINT` and `BCPALT` cases, then dispatch otherwise to private R14-linked `DQFIND`: `IONORM` counted BCPL DD string -> `DDVERIFY` (RDJFCB allocation) -> `DALLOC` (descriptor plus owned QSAM region) -> `DQOPEN` -> `HNEW`, returning stable word-address handle or zero. Error paths release owned resources; on failed HNEW, CLOSE precedes DREL. DQFIND uses independent R11 base; existing private helpers save R11/R14. No production OBJ update. Added `native-compiler/asm/bcplio-dynamic-find-probe.asm` and `native-compiler/jcl/bcplio-dynamic-find-probe.jcl` (MVS member DQFPRB) to call DQFIND with `REPORT`, check stable handle lookup, PUT one fixed record, CLOSE/HCLOSE/DREL, confirm stale handle absent, and reject missing `ZZZZZZZZ`. **This is only public FINDOUTPUT fallback initiation; SELECTOUTPUT, WRCH, ENDWRITE, and termination cleanup remain unmodified and do not recognize dynamic handles.** DQFPRB tests a private call, not a compiled-BCPL program. Gate: stage BCPLIO and DQFPRB source/JCL, run DEVOBJ-only BLDDEVI ASMIO/PUTIO RC0 and zero flags, run DQFPRB ASMDQ/LKED/GO RC0, verify `DQFIND OUTPUT SUCCESS` in actual REPORT SYSOUT. Continue only after source validation and then add selected-stream I/O wiring and compiled-BCPL regression. Check IFOX USING/DROP ranges and DDVERIFY failure behavior. No MVS results yet.


## JOB 5710 — DQFIND label length correction (2026-10-16)

Operator staged BCPLIO ASM (JOB 5705), DQFPRB ASM (JOB 5706), DQFPRB JCL (JOB 5707), then ran BLDDEVI launcher JOB 5709, payload **JOB 5710**. IFOX ASMIO RC=0008; PUTIO flushed, leaving DEVOBJ unchanged. Full assembler diagnostics show statement 1627 IFO236, statement 1635 IFO236, statement 1638 IFO236, and statement 1653 IFO016. All four are the too-long nine-character `DFFRESULT` symbol (three references and the definition); IFOX Assembler F requires maximum eight-character labels. Replaced all five occurrences of the symbol with `DFFRES` in native-compiler/asm/bcplio.asm. This is a source-only correction; it has not yet been reassembled on MVS. Restage BCPLIO, rerun BLDDEVI and require ASMIO/PUTIO RC0000, then execute already staged DQFPRB. Production OBJ unchanged.


## JOB 5714: corrected FINDOUTPUT development BCPLIO build passes (2026-10-16)

Operator restaged BCPLIO ASM via JOB 5711 and submitted BLDDEVI launcher JOB 5713, payload JOB **5714**. ASMIO IFOX00 RC=0000, PUTIO IEBGENER RC=0000, zero flagged assembler statements and severity zero. This resolves JOB 5710's invalid `DFFRESULT` IFOX symbol by using `DFFRES`; current BCPLIO object is installed in DEVOBJ(BCPLIO) only. **DQFPRB has not yet been executed against this build**. Next submit the already staged `native_jcl DQFPRB`; require ASMDQ/LKED/GO RC0 and check actual REPORT `DQFIND OUTPUT SUCCESS`. Preserve production OBJ.


## JOB 5717: DQFIND private runtime probe RC0 (2026-10-16)

Operator submitted staged DQFPRB after successful JOB 5714 DEVOBJ build. Launcher JOB 5716, payload **JOB 5717**: ASMDQ IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000; zero flagged assembler statements, highest severity zero. The DQFPRB assertions run through DQFIND("REPORT"), HLOOK/DQPUT/DQCLOSE/HCLOSE/DREL, stale-handle rejection, and missing DD `ZZZZZZZZ` rejection. **REPORT SYSOUT record content is not yet verified**; request full report or grep for an actual `DQFIND OUTPUT SUCCESS` line, not assembler literal. This is a private direct-call probe; actual BCPL `IOFOUT` dispatch and SELECTOUTPUT/WRCH/ENDWRITE dynamic integration remain untested. No production OBJ changes.


## JOB 5717 DQFIND discovery gate ACCEPTED (2026-10-16)

Operator confirmed actual SYSOUT line 364 `DQFIND OUTPUT SUCCESS` from `tools/mvs/dump-report-for-job 5717` (as distinct from source literal). Coupled with JOB 5714 DEVOBJ ASMIO/PUTIO RC=0000, and JOB 5717 ASMDQ/LKED/GO RC=0000 with zero flagged assembler statements, this **accepts the private DQFIND dynamic output discovery and stable-handle lifecycle gate**. DQFPRB explicitly tested valid REPORT DD, DQPUT, close, HCLOSE, DREL, stale-handle HLOOK rejection, and nonexistent DD rejection. Public IOFOUT dispatch and compiled-BCPL FINDOUTPUT remain to be exercised; SELECTOUTPUT, WRCH, ENDWRITE dynamic handles are not yet wired. Next gate: selected-stream buffered output with full compiled-BCPL regression and legacy compatibility. Production NATIVE.OBJ untouched.


## M1 selected dynamic output staged — DEVOBJ assembler gate pending (2026-10-16)

Added `IOSELCT=X'03'` dynamic output dispatch. `IOSOUT` resolves otherwise-unrecognized handles via HLOOK without dereferencing caller-supplied addresses, selecting live dynamic output handles. `IOWRCH` appends characters into the descriptor-owned 132-byte buffer, tracks fill in previously unused QSAM region offset +236, PUTs a full FB132 record on newline and clears the buffer. `IOENDW` for selected dynamic stream flushes non-empty final buffer, DQCLOSEs, HCLOSEs, DRELs, and reselects primary stream. `DALLOC` initializes buffer to blanks, preserving existing static SYSPRINT and BCPALT paths. The new path uses private helper calls and preserves BCPL R6 return ABI. **This is staged source, NOT MVS-tested; no DEVOBJ rebuild yet.** Gate 1: ASMIO/PUTIO via BLDDEVI in DEVOBJ, zero IFOX severity. Gate 2: isolated direct BCPL output API probe and full compiled-BCPL stream test with real DD outputs, interleaving, newline and ENDWRITE. Gate 3: full DEVOBJ regression compatibility. Outstanding: dynamic IOFIN cleanup for streams left open and WRAPOUTPUT semantics, explicit stale-handle behavior; do not accept complete milestone until covered. Production OBJ unchanged.


## JOB 5721 IFOX addressability failure — corrective source staged (2026-10-16)

Operator staged dynamic selected-output BCPLIO ASM through JOB 5718 and submitted BLDDEVI launcher JOB 5720, payload **JOB 5721**. ASMIO IFOX00 RC=0008, PUTIO flushed; therefore current DEVOBJ(BCPLIO) was **not** replaced. The IFOX diagnostic summary reports 10 `IFO209 ADDRESSABILITY ERROR` diagnostics over eight statements: 46, 47 (twice), 154, 180, 187, 188, 192, 193 (twice). All involve static `IOBUF`/`IO2BUF`/`IODCB`/`IO2DCB` operands in `IOINIT` and `IOWRCH`; extra code has moved these areas past the one-register 4 KB addressing range. Added independent R11 secondary base in both entry paths using `LA 11,3584(10)` and `USING IOINIT+3586,11` / `USING IOWRCH+3586,11`, after R11 saved and before buffer accesses; paired `DROP 11` after each return. This includes the lower static IOBUF and higher DCBs inside the second base window without disturbing the previously established R10 base. Correction is staged in Git, **not yet assembled under MVS**. Rerun DEVOBJ-only BLDDEVI and require both steps RC0 before any runtime probe or compiled regression. Production OBJ unchanged.


## JOB 5725: dynamic selected-stream BCPLIO DEVOBJ assembly gate ACCEPTED (2026-10-16)

Operator restaged BCPLIO via JOB 5722 and submitted BLDDEVI launcher JOB 5724, payload **JOB 5725**. ASMIO IFOX00 RC=0000, PUTIO IEBGENER RC=0000, zero flagged statements, highest severity zero. The secondary R11 base correction resolves JOB 5721's IFOX addressability failures and installs the selected-output BCPLIO implementation into `HERC02.BCPL.NATIVE.DEVOBJ(BCPLIO)` only. **Assembly gate accepted; runtime gate pending.** Next stage and run an isolated test of BCPL-facing IOFOUT, IOSOUT, IOWRCH, IOENDW with R6/R7/R5 linkage, verifying actual DD output and both legacy-stream compatibility and stale-handle behavior. Existing private DQFPRB alone does not test these paths. No production OBJ changes.


## M1 BCPL-facing selected-output probe staged (2026-10-16)

After JOB 5725 accepted DEVOBJ assembly, source review uncovered an important fall-through defect: static `IOEWDONE` reset selection to primary but then fell through into dynamic `IOEWDYN` cleanup. Corrected by explicitly branching `B IOEWRET` after reset. **This correction requires a fresh BLDDEVI**; JOB 5725 DEVOBJ does not include it.

Added `native-compiler/asm/bcplio-dynamic-bcpl-probe.asm` and `native-compiler/jcl/bcplio-dynamic-bcpl-probe.jcl` (PDS member `DQBPRB`). Test calls BCPL-facing `IOFOUT`, `IOSOUT`, `IOWRCH`, `IOENDW`, `IOOUT` via actual R5 frame/R6 return/R7 argument ABI, with IOINIT/IOFIN native entry. It discovers REPORT and REPORT2, interleaves two FB132 output streams, flushes first on newline, flushes second's partial final record on ENDWRITE, confirms both handles stale via HLOOK, and confirms primary SYSPRINT selection/output. Expected actual SYSOUT text: `DQB REPORT A`, `DQB REPORT B`, `DQB REPORT2 PART`, `DQB PRIMARY`. Requires ASM and JCL members staged, BCPLIO reassembled into DEVOBJ and DQBPRB job executed RC0 with zero assembler flags and actual four output lines inspected. This is an **assembler ABI integration probe**, not yet compiled BCPL source or full regression; gate remains pending, production OBJ protected. Further work must cover WRAPOUTPUT, selected dynamic handles at IOFIN and alternate legacy BCPALT behavior.


## JOB 5734 — DQBPRB S0C4 and R10 base fix staged (2026-10-16)

Operator staged BCPLIO/DQBPRB ASM/JCL (JOBS 5726/5727/5728), built DEVOBJ BCPLIO JOB **5731** (ASMIO/PUTIO RC=0000, zero flags), then submitted DQBPRB payload JOB **5734** (ASMDQ/LKED RC=0000, GO **ABEND S0C4**). SYSUDUMP entry PSW `078D2000 000A5B80`, ILC4/INTC0011; map BCPLIO origin `000A5610`, IOSOUT entry `000A5B32`. At `000A5B80`, IOSOUT `C 7,IOCURH` is accessed with invalid R10=`500A6D64`, inherited from HLOOK's private R14-linked helper (documented R10 clobber). This is a **BCPLIO integration caller error**: BCPL-facing entry must restore its own R10 base after each R14 helper. Source correction `a1678a5` snapshots R10 into preserved R9 before dynamic calls, restores `LR 10,9` after `HLOOK` in IOSOUT, after HLOOK/DQPUT/HLOOK in IOWRCH and after HLOOK/DQPUT/DQCLOSE/HCLOSE/DREL in IOENDW. R9 is saved by each BCPL entry and preserved by private helpers. Correction is **not yet assembled or run**; restage BCPLIO, DEVOBJ-only BLDDEVI, rerun previously installed DQBPRB. The selected-output gate remains **FAILED/PENDING**, not accepted by successful assembly. Do not modify production NATIVE.OBJ.


## JOB 5741: second DQBPRB S0C4 at IOWRCH return (2026-10-16)

Operator rebuilt corrected BCPLIO into DEVOBJ via JOB **5738** (ASMIO/PUTIO RC=0000, zero IFOX flags), then DQBPRB payload **JOB 5741** (ASMDQ/LKED RC=0000; GO **ABEND S0C4**). SYSUDUMP PSW `078D2000 000A587C`, ILC4, INTC0010; load map `BCPLIO` origin `000A55F8`, `IOWRCH` +`0x122`. At `000A5878` the code executes `LM 11,15,IOSAVE+44`; the PSW identifies its next instruction address at `000A587C`. This restore depends on the R11 secondary static-data base, which may no longer be valid following dynamic private helpers. The prior fix did restore R10 but not independently reestablish secondary R11. Commit `622025c` inserts `LA 11,3584(10)` immediately before the `IOWRCH` regular return save-area loads and nonreturning overflow return save-area loads. Correction staged, **not MVS-tested**. Next restage BCPLIO, run DEVOBJ-only BLDDEVI, rerun DQBPRB and inspect actual output records. Gate remains open; production OBJ unchanged.


## JOB 5748: DQBPRB S0C4 persists in IOWRCH register restore (2026-10-16)

Operator staged latest source in JOB 5742, built DEVOBJ via payload JOB **5745** (ASMIO/PUTIO RC=0000, zero assembler flags), then executed DQBPRB payload JOB **5748** (ASMDQ/LKED RC=0000, GO ABEND S0C4). Dump PSW `078D2000 000A587C`, ILC4, interruption code `0010`, same instruction region as JOB 5741. Code at `000A587C` is `LM 11,15,IOSAVE+44` in `IOWRCH` return; R11 is also the effective-address base for IOSAVE. Reestablishing R11 before that instruction did not eliminate the fault. This is *not* an accepted runtime test. Corrective commit `18d210b` changes both `IOWRCH` return paths to `LM 12,15,IOSAVE+48` followed by `L 11,IOSAVE+44`, so the register supplying the save-area address is restored last, avoiding base/target overlap in LM. **Hypothesis, not yet validated.** Next rebuild only DEVOBJ(BCPLIO) and rerun staged DQBPRB; preserve production OBJ. If S0C4 persists, instrument return path and inspect exact save-area bytes rather than stacking unverified fixes.


## JOB 5755: persistent IOWRCH S0C4 despite ordered restore (2026-10-16)

Operator staged BCPLIO as JOB 5749, BLDDEVI payload JOB **5752** ASMIO/PUTIO RC=0000, no flagged statements. DQBPRB payload JOB **5755** ASMDQ/LKED RC=0000, GO **ABEND S0C4**. PSW `078D2000 000A587C`, interruption code `0010`, same local IOWRCH return region after ordered `LM 12,15,IOSAVE+48` / `L 11,IOSAVE+44`. Link map BCPLIO origin +`238`, IOWRCH +`35A`; live dump at 0A586C.. includes `LA 11,3584(10)`, `LM 0,9,IOSAVE`, `LM 12,15,IOSAVE+48`, `L 11,IOSAVE+44`, `L 4,0(5)`. Do not claim ordered-restore hypothesis successful; no further speculative code changes. Next narrow to actual failing instruction with ILC semantics and exact register image, inspect IOSAVE bytes at its mapped static location, and isolate first-call vs later-call by a deliberately instrumented DQBPRB. Previous accepted private DQFPRB remains distinct; BCPL selected-stream integration gate remains FAILED/PENDING. Production OBJ untouched.


## JOB 5755: corrected instruction identification; frame-preservation diagnostic staged

Reinspection of the exact JOB 5755 runtime bytes at `000A586C`–`000A5884` identifies `000A587C` as **`L 4,0(5)`**, following the two register loads and the final R11 restore, not an LM instruction itself. At abend R5=`009BC7B0` (TCB address), whereas probe's frame is `FRAME` in DQBPRB's load section (`000A5550`). Thus the fault is an invalid BCPL frame pointer being dereferenced. Previous diagnoses attributing the S0C4 directly to secondary R11 or LM overlap are superseded. The first loss of R5 is not yet established. Rather than edit BCPLIO speculatively, staged diagnostic-only DQBPRB changes (commit `89e8d84`) assert `R5 == address(FRAME)` after each BCPL-facing or native public call, including each IOWRCH in SEND. Failure routes to RC=12 (`BADFRAME`) without invoking the next runtime operation; other assertion failures continue to produce RC=8. Next stage *only* ASM DQBPRB, rerun its already staged JCL against the current DEVOBJ BCPLIO; inspect GO RC (12 indicates frame corruption) and actual records. If the existing runtime still abends *inside* WRCH prior to returning, additionally instrument before call. Production OBJ unchanged.


## JOB 5759: IOWRCH base-register mismatch identified

DQBPRB JOB 5759: ASMDQ and LKED RC=0000, GO S0C4, PSW 000A587C. Dump code and data demonstrate R11 addressing two bytes past intended static data. IOWRCH begins at 000A570A with LR 4,10 then BALR 10,0, placing R10 at 000A570E. LA 11,3584(10) therefore places R11 at 000A650E (IOWRCH+3588), but source declared USING IOWRCH+3586,11. Actual IOSAVE is at 000A6548; LM 0,9,IOSAVE consequently reads from 000A654A. Dumped original bytes 009BE508 000A5550 00000040 009B0634 yield erroneous registers E508000A 55500000 0040009B 0634400A, exactly matching the EED Type1 register image. This establishes the two-byte addressing error, superseding previous speculative R5/R11 restore explanations. Commit a33d380 fixes the USING constant to +3588. A separate source-review fix inserts B IOWRET after IOW2PUT to prevent fallthrough into the dynamic branch. Changes are not yet MVS validated. Rebuild BCPLIO only into DEVOBJ; retest existing DQBPRB and inspect real DD records. Production OBJ unchanged.


## JOBS 5763 and 5766: BCPL-facing dynamic selected-output integration gate ACCEPTED (2026-10-17)

Operator updated local source from `442fca9` and staged corrected `BCPLIO` as JOB **5760**. DEVOBJ-only `BLDDEVI` launcher JOB 5762, payload **JOB 5763**, passed **ASMIO IFOX00 RC=0000; PUTIO IEBGENER RC=0000**, with zero flagged statements and highest assembler severity zero. This installed corrected `HERC02.BCPL.NATIVE.DEVOBJ(BCPLIO)`; no production `NATIVE.OBJ` change.

Operator then submitted already staged `DQBPRB` (with post-call R5 frame assertions), launcher JOB 5765, payload **JOB 5766** on **17 Oct 2026 at 00:02**. `ASMDQ IFOX00 RC=0000`, `LKED IEWL RC=0000`, **GO RC=0000**, zero flagged statements. JES full report contains actual output records from GO DD streams, not just assembler literals:

```text
DQB PRIMARY
DQB REPORT A
DQB REPORT B
DQB REPORT2 PART
```

This supports acceptance of this **assembler ABI integration gate** for BCPL-facing `IOFOUT` / `IOSOUT` / `IOWRCH` / `IOENDW` / `IOOUT` under R5/R6/R7 ABI. The test discovers REPORT and REPORT2 DD allocations, interleaves writes through selected handles, flushes line records and a partial final record, verifies stale handles through HLOOK, verifies primary output restored, and verifies frame preservation. The earlier repeated S0C4 is resolved by the correctly matched `USING IOWRCH+3588,11` secondary base, as evidenced by this passing runtime job (source correction `a33d380`). Static BCPALT newline fallthrough correction also assembled, but **not yet directly exercised** by this probe.

**Gate accepted; milestone M1 remains active.** Explicitly still unverified: use from *compiled BCPL program source* through its compiler/linkage, compatibility of the full 124-test native regression suite with the new DEVOBJ module, legacy BCPALT path and WRAPOUTPUT semantics, dynamically selected streams left open at IOFIN, and invalid/closed handle behavior through the public SELECTOUTPUT entry (versus HLOOK-only checks). Complete these in separate development gates before any promotion to production NATIVE.OBJ.


## Compiled BCPL dynamic-output test 124 staged (not yet MVS validated)

Added `native-compiler/regression/124-dynamic-dd-selected-output` as a real native Cambridge-compiled BCPL test, with source, candidate-only marker, README and three logical-output fixtures. BCPL uses G41 FINDOUTPUT, G12 SELECTOUTPUT, G17 OUTPUT, G14 WRCH, G47 ENDWRITE, G60 WRITES (BLIB). GO JCL created by the existing installed-PDS regression preparer now allocates FB132 DDs REPORT and REPORT2 from explicit fixture files. The regression compares combined post-link GO logical output for primary SYSPRINT (`BCPL DYNAMIC OK`), REPORT (`BCPL REPORT A`, `BCPL REPORT B`), and REPORT2 (`BCPL REPORT2 PART`) with exact ordered expected records. It tests failed FINDOUTPUT on absent NOFILE, selection preservation, interleaving, buffered partial flush, rejected stale handle and primary reselection. Combined JES text does *not* independently establish DD attribution; fixture checker continues to say so. No MVS compile/assemble/link/GO result has been observed for this case.

The case is **candidate-only**; full default production panel skips 124 while continuing to report the original 00..123 results. To run case 124 require all four variables: `BCPL_RUNTIME_PDS=1`, `BCPL_RUNTIME_LIBRARY=DEVOBJ`, `BCPL_RUNTIME_CANDIDATE=1`, `BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6`. The linker thereby explicitly includes DEVOBJ BCPLM6 and BCPLIO along with existing service-object links. The M0 inventory did not establish that BCPLM6 was currently installed: before running, check `tools/datasets/dspal ls native_devOBJ`; if absent, stage historical `asm/bcplmain-d6-candidate.asm` as SOURCE(BCPLM6), stage `jcl/build-dev-bcplmain-d6.jcl` as NATIVE.JCL(BLDD6MN), submit BLDD6MN and demand ASMMMAIN/PUTMAIN RC0. No production object mutation is authorized. A test-124 PASS must include the MVS compile, IFOX, IEWL, GO, actual GO records and no unexpected 124 skip. Once accepted, run baseline 00..123 explicitly through the same modular candidate and record actual totals. Do not treat source commits as acceptance.


### BCPLM6 candidate PDS staging clarification

Verified the historical D6 candidate file exists at `native-compiler/asm/bcplmain-d6-candidate.asm`, and its old builder at `native-compiler/jcl/build-dev-bcplmain-d6.jcl` still names obsolete `HERC02.BCPL.SOURCE`/`HERC02.BCPL.DEVOBJ` datasets. Added `native-compiler/jcl/build-dev-bcplm6.jcl` with the current `HERC02.BCPL.NATIVE.ASM(BCPLM6)` input and `HERC02.BCPL.NATIVE.DEVOBJ(BCPLM6)` output, conditional upon IFOX success. Stage via `dspal put native_asm BCPLM6 native-compiler/asm/bcplmain-d6-candidate.asm`, `dspal put native_jcl BLDDEVM6 native-compiler/jcl/build-dev-bcplm6.jcl`, and submit `native_jcl BLDDEVM6` before test 124. The previous note's SOURCE/BLDD6MN instructions referred to pre-refactor paths and should not be used. No MVS build or compiled BCPL execution has yet been observed for the new candidate/build gate. This preserves accepted production OBJ and the existing independent BCPLIO DEVOBJ object.

## Compiled BCPL candidate gate: JOB 5771 / native regression 124 PASS (2026-10-17)

Operator pulled repo at commit `9691a60`. Staged `native-compiler/asm/bcplmain-d6-candidate.asm` into `HERC02.BCPL.NATIVE.ASM(BCPLM6)` (JOB **5767**) and `native-compiler/jcl/build-dev-bcplm6.jcl` into `HERC02.BCPL.NATIVE.JCL(BLDDEVM6)` (JOB **5768**). Submitted `BLDDEVM6` launcher JOB **5770**, payload **JOB 5771**, dated 17 Oct 2026 00:12:10-00:12:11. `ASMMMAIN IFOX00 RC=0000`; `PUTMAIN IEBGENER RC=0000`; no flagged assembler statements; highest severity 0. Installs **DEVOBJ(BCPLM6)** only; production OBJ unmodified.

Operator then ran exactly:

```sh
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 124 --show-output
```

Native-compiled BCPL regression **124-dynamic-dd-selected-output PASS 1 / FAIL 0 / SKIP 0 / TOTAL 1**. Its runner compiles source through resident Cambridge, then assembles/links/executes under the DEVOBJ modular BCPLM6+BCPLIO candidate, allocates JCL DDs REPORT/REPORT2, checks three named logical-output fixtures and post-link SYSPRINT success marker, and rejects missing DD and stale selection through BCPL globals. The stdout provided only the concise panel result, not detailed JES GO job numbers or separately extracted DD spool records; the regression result is operator evidence that its existing checks passed. The combined JES checker explicitly **does not prove physical DD attribution**, even though the expected per-name logical records match. **Compiled BCPL dynamic output test-124 gate ACCEPTED; entire M1 not accepted.**

Next execute full baseline **00..123** under these identical DEVOBJ candidate environment variables (do not substitute default MIXED or OBJ paths), and record PASS/FAIL/SKIP and failing cases if any. Expected previous baseline: 123 PASS, 0 FAIL, expected SKIP 083; these numbers are not a prediction or current acceptance. Additional M1 exit obligations include dynamic FINDINPUT from compiled BCPL, absent-DD input, no static allowlist, repeat names/cleanup, and richer QSAM failure handling. No permission for production OBJ promotion.


## Full candidate 00..123: 122 PASS, 1 FAIL, 1 SKIP — JOB 5999 S0C1 (2026-10-17)

Operator ran the baseline 124-case panel with **explicit** `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6` after accepted compiled dynamic-output test 124. Observed **122 PASS, 1 FAIL, 1 expected SKIP (083)**. Only regression **113-overlong-output-rejected** failed. Its historical contract: after 132 buffered FB132 output characters, 133rd `WRCH` must invoke `STOP(12)`, giving controlled **GO RC=0012**. Resident Cambridge compilation JOB **5998** completed COMP/SVCODE RC=0000; payload JOB **5999 RG113R** assembled `ASMAP` RC=0000, linked `LKED` RC=0000, but **GO ABEND S0C1**. SYSUDUMP PSW `078D0000 00000004`, ILC 2, INTC 0001 (attempted execution near null); return and callback registers R14=00000000, R10=E2E3C1C3 (`STAC` as EBCDIC), R11=000A5E62 (BCPL system-vector base). MAP confirms BCPLMAIN and BCPLIO resolved from DEVOBJ, plus production BLIB/MEM and development APT/BYTE. **Full baseline FAILED; do not accept milestone or promote OBJ.**

Root-cause source inspection of `native-compiler/asm/bcplio.asm` found the separate `IOWRCH` high base R11 was restored to the BCPL caller *too early* on **both** the normal return path `IOWRET` and nonreturning overflow callback `IOWFULL`. The original sequence executed `L 11,IOSAVE+44` **before** subsequent R11-based static loads `L 10,IOSAVE+40` and, on overflow, `L 14,IOOVHAND`. Thus the assembled address calculations for IOSAVE/IOOVHAND could use the caller's unrelated system-vector base rather than BCPLIO's secondary base; this explains the nonsensical R10 word and possible zero callback target. The earlier fix for the two-byte `USING IOWRCH+3588,11` mismatch was required but did **not** address this return-sequencing defect. Source-only correction commit **`ab97a19`** now leaves R11 as the secondary base until after the last static memory access: overflow loads IOOVHAND and saved R10 before `L 11,IOSAVE+44`; normal return loads saved R10 before `L 11,IOSAVE+44`. No functional change to success-path buffering or public globals. Corrected source has zero lines beyond IFOX column 71; **not yet assembled/executed by MVS.**

Next narrow retest:
1. `git pull --ff-only`, stage only `native_asm BCPLIO` from `native-compiler/asm/bcplio.asm`.
2. Submit installed `native_jcl BLDDEVI` to assemble/install **only DEVOBJ(BCPLIO)**; demand ASMIO/PUTIO RC=0000 with zero flags.
3. Run candidate test **113** with the exact four DEVOBJ environment variables and `--show-output`; acceptance requires GO RC=0012 (expected controlled STOP), no S0C1 and regression PASS. This test contains no expected logical output; it must not require a marker.
4. If 113 passes, rerun candidate **124** then full **00..123**; require 123 PASS, 0 FAIL, 1 SKIP. Do not adjust the expected-go-rc fixture or excuse an abend. Production OBJ untouched.

## JOB 6023 — corrected IOWRCH overflow exit accepted; test 113 PASS (2026-10-17)

Operator pulled `ec847bf`, staged corrected `native-compiler/asm/bcplio.asm` as `HERC02.BCPL.NATIVE.ASM(BCPLIO)` via JOB **6020**, and submitted existing DEVOBJ-only `BLDDEVI` (launcher **6022**, payload **6023**). Job 6023 on 17 October 2026 00:24:13: `ASMIO IFOX00 RC=0000`, `PUTIO IEBGENER RC=0000`, zero flagged assembler statements and severity zero. The corrected `DEVOBJ(BCPLIO)` now contains source fix `ab97a19` (with comment clarification `ec847bf`): delay R11 restoration until after all R11-relative IOSAVE and IOOVHAND loads in both IOWRCH return paths. No other runtime PDS members reinstalled.

Operator then ran `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 tools/native/run-regression 113 --show-output`; observed **PASS 1, FAIL 0, SKIP 0, TOTAL 1**. Test 113's expected GO RC fixture is `0012`, so runner PASS establishes that its controlled STOP(12) termination check succeeded rather than the earlier S0C1; separate GO job number / step summary not supplied. **Regression 113 targeted gate ACCEPTED.** This does not overwrite or negate historical failure evidence for JOB 5999, but documents its remediation.

**Next gate still open:** reexecute candidate regression **124** and entire **00..123** with identical four environment variables, after this updated BCPLIO install. Require 124 PASS and baseline 123 PASS / 0 FAIL / 1 expected SKIP 083. Then proceed to compiled BCPL dynamic-input and independent DD attribution; milestone M1 remains active. Production NATIVE.OBJ untouched.

## BCPL dynamic output and full native compatibility: ACCEPTED (2026-10-17)

The operator pulled commit `fdc46d0` and executed the **same modular DEVOBJ candidate** after JOB 6023 had installed the corrected BCPLIO. Exact environment:

```sh
export BCPL_RUNTIME_PDS=1
export BCPL_RUNTIME_LIBRARY=DEVOBJ
export BCPL_RUNTIME_CANDIDATE=1
export BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6
tools/native/run-regression 124 --show-output
tools/native/run-regression 0 123
```

**Test 124** `124-dynamic-dd-selected-output`: **PASS 1 / FAIL 0 / SKIP 0 / TOTAL 1**. It compiles a BCPL source client and verifies expected logical GO output from two JCL-defined dynamic DD names and restored primary output against fixtures. The combined JES verifier remains *insufficient for independent physical DD attribution*.

**Full baseline 00..123**: **PASS 123 / FAIL 0 / SKIP 1 (expected source-only test 083) / TOTAL 124**. Explicit results include test **113-overlong-output-rejected PASS** (controlled STOP(12) expected termination), tests **094..119** stream regressions all PASS, and other compiler/linkage/memory/BLIB/STOP regressions all PASS. This supersedes the failed earlier JOB 5999 full-panel result as the *current* accepted candidate while preserving that incident's history.

**Acceptance decision:** compiled-BCPL dynamic-output **integration and baseline compatibility gates CLOSED/ACCEPTED** for the isolated `DEVOBJ(BCPLM6)+DEVOBJ(BCPLIO)` candidate. This demonstrates no regression relative to the original 00..123 panel at the tested revision, but does **not** accept the entire M1 milestone or authorize promotion into production `HERC02.BCPL.NATIVE.OBJ`.

**Remaining M1 scope:** make dynamic DD-backed *input* work through compiled BCPL `FINDINPUT`/`SELECTINPUT`/`RDCH`/`UNRDCH`/`ENDREAD`; test absent/invalid DDs, simultaneously open streams (target >=12 per milestone), independent positions and EOF/unread handling, cleanup on FINISH/STOP, repeat opens and closed handles, failure paths and resource limits. Output tests should additionally establish DD attribution from independently identified JES spool files rather than rely solely on combined logical-record matching. Retest full candidate panel after any subsequent runtime edits.

## M1 dynamic input: permanent candidate regression 125 staged (2026-10-17)

**Scope:** introduce a test-first permanent regression for the next input march without changing accepted output runtime objects. Added `native-compiler/regression/125-dynamic-dd-two-input-streams` with real Cambridge-compiled BCPL `source.bcpl`, deterministic `expected.txt` and two distinct `DD DATA` fixtures `input-dda.records` and `input-ddb.records`. The BCPL application opens **DDA** and **DDB**, not existing fixed `BCPIN` and `BCPINB`. It alternates selections and verifies independent read positions, `UNRDCH` on characters and EOF, synthetic newline, missing-DD discovery, `ENDREAD`, stale-handle selection rejection, and selected-input state. Each assertion fails through **STOP(8)**, success alone emits `BCPL INPUT OK` on primary SYSPRINT then FINISH. No BCPL compiler syntax, native compiler, runtime G-number assignment or BCPLIO assembler changes were made in this staging action.

The installed-object regression JCL generator `tools/checks/prepare-runtime-pds-regression.py` now maps up to 36 constrained case-local `input-dd*.records` to distinct DD DATA allocations using unique validated delimiters. DD-name validation and input-card safety checking fail closed. This is intentionally extensible to the later twelve-stream test 126; it does not interfere with existing `input.records`/BCPIN or `input-b.records`/BCPINB fixtures.

Test 125 includes `candidate-only.txt` and therefore must use `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6`, just as case 124. The candidate-only skip guard leaves ordinary production testing unaffected. Its positive acceptance condition is GO RC=0000 and exact `BCPL INPUT OK` output. **This test is not yet executed or accepted.** Source review establishes the current `native-compiler/asm/bcplio.asm` `IOFINDIN` path only recognizes fixed BCPIN and BCPINB: it does not have a dynamic DD registry/Open/GET/Close backend. **A first run of 125 on the current DEVOBJ is expected to FAIL through STOP(8)**; this is a deliberate red gate and must not be reported as a regression of the accepted output test 124 or the baseline 00..123. Obtain test 125's failure evidence before changing the runtime.

Next march: design and implement dynamic DD-backed input descriptor ownership with authentic QSAM OPEN/GET/EODAD/CLOSE; preserve each stream's cursor/EOF/pushback; invalidate handles on ENDREAD; verify cleanup on FINISH/STOP and re-run 113, 124 and 00..123. Source with test pass is not enough: require operator MVS assembler/link/GO evidence. Then add stress regression 126 for 12 simultaneously open DDs and resource-error/cleanup gates. No production NATIVE.OBJ writes permitted.

## Regression 125 red gate observed: JOBS 6274/6275 (2026-10-17)

Operator ran candidate-only `tools/native/run-regression 125 --show-output` after pulling commit `491749f`, with the mandated DEVOBJ BCPLM6 flags. Resident Cambridge compilation generated native assembly as **JOB 6274**. Native link-and-execute **JOB 6275 RG125R**: `ASMAP IFOX00 RC=0000` (zero flagged, severity zero), `LKED IEWL RC=0000`, **GO RC=0008**, no system abend. JCL visibly allocated both `DDA DD DATA,DLM=X0` and `DDB DD DATA,DLM=X1`. Load map resolved BCPLMAIN/BCPLIO through DEVOBJ; the expected `BCPL INPUT OK` marker was not emitted. The regression reported **PASS 0 / FAIL 1 / SKIP 0 / TOTAL 1**. This is the anticipated and accepted **RED test-first checkpoint**, **not** an accepted regression PASS. The old IOFINDIN only recognizes BCPIN and BCPINB; the test stops at the first required dynamic FINDINPUT. Preserve this evidence.

**Source development staged, but entirely UNTESTED under MVS** in commits `d349c03`, `6faf032`, `72d89ad`, `66ea13e`: 
- `IOFINDIN` now delegates unrecognized names to private `DIFIND` (IONORM + DDVERIFY + DALLOC(input direction=1) + DQOPEN + HNEW, full cleanup on open/handle failure).
- `DALLOC` clones a QSAM GM DCB template `DQTIN` with `EODAD=INDYEOD`, rather than its output PM template; both share the existing +132 DCB/+228 SVC19/+232 SVC20 descriptor format.
- FB80 dynamic input buffers preserve per-stream +236 cursor, +240 trimmed length, +244 pending newline, +245 unread flag, +246 seen, +247 EOF, +248 last character. `IORDCH` uses QSAM `GET (1),(0)`; EODAD marks EOF per active descriptor; `IOUNRD` uses descriptor-local pushback.
- `IOSELIN` enforces live HLOOK and input direction; `IOENDRD` closes QSAM input DCB, invalidates handle, releases descriptor, and clears selection. New helper calls in public SELECTINPUT/UNRDCH preserve the complete caller register image, including address constants R1-R3.
- No production object change; the accepted dynamic-output and 00..123 baseline **have not yet been rerun with this implementation**. This assembler source has been checked for IFOX card widths (all <=71); no IFOX syntax/macro assembly, link, or GO result exists yet.

**Immediate execution gate**: operator pulls source, stages `native_asm BCPLIO`, runs the existing DEVOBJ-only `BLDDEVI` (ASMIO/PUTIO RC0 required), then reruns candidate regression 125 with `--show-output`. Accept only positive PASS 125 GO RC0 with the marker; do not weaken fixture. On failure inspect the assembly diagnostics or QSAM dump and remediate before attempting 126. Upon positive result rerun 113, 124, full 00..123 for compatibility; remaining FINISH/STOP cleanup, repeated DD identity, resource limits and DD-attribution gates remain open.

## JOB 6279 — IFOX addressability failure; DEVOBJ unchanged (2026-10-17)

Operator pulled dynamic-input source at `58225af`, staged `native_asm BCPLIO` via JOB **6276**, submitted `BLDDEVI` launcher **6278**, payload **6279** (00:42:34). `ASMIO IFOX00 RC=0008`; conditional `PUTIO IEBGENER` **FLUSHED**, so the previously accepted DEVOBJ(BCPLIO) is **unchanged**. The full assembler listing shows **IFO209 base/displacement addressability** at statement IDs **32, 33** (IOINIT's IOISAVE), **66, 67** (IOFIN's IOFSAVE), **139, 140, 141** (IOWRCH's IOSAVE), and **282, 283** (IOSEL's IO2BUF; stmt 283 diagnosed twice). **Nine statements flagged, severity 8**. Expanded dynamic input instructions displaced the legacy save areas and alternate-output buffer more than 4095 bytes past the relevant R10 base; IFOX emitted zeroed placeholders, so this failed object must never be installed.

Corrective source commits: `e0fa82c` initially attempted to move all four save images near IOFIN, but review found that would put IOSAVE *before* IOWRCH's R10 base and cause a new negative-displacement addressability failure. It was **superseded immediately** by `fe3463a`, which places **IOSAVE, IOISAVE and IOFSAVE after IOWRCH** (forward-reachable from all three entry R10 bases), retains IOESAVE at its original later address, and establishes the second R11 base for IOSEL only **after** its initial register saves. `IOSEL+3586` corresponds exactly to runtime `BALR 10,0; LA 11,3584(10)`. Additional review found dynamic DALLOC used the output SVC19 option byte X'8F' for both directions: commit `de264c7` selects X'80' for input descriptors while retaining X'8F' for output; SVC20 CLOSE stays X'80'. All edited source cards are within IFOX's 71-column limit.

**Validation status:** corrections committed, **not yet assembled, linked or executed** by MVS. Rebuild only DEVOBJ BCPLIO with `dspal put native_asm BCPLIO native-compiler/asm/bcplio.asm` then `dspal submit native_jcl BLDDEVI`. Require ASMIO/PUTIO RC0, zero flagged statements. If this succeeds run candidate-only regression 125 and examine any runtime failures separately. The red gate JOB 6275 remains the last verified 125 result; a successful IFOX assembly will not by itself establish input semantics. Existing production NATIVE.OBJ is unaffected.
