# Dynamic BCPLIO streams — M1 progress log

Status: **M1 in progress; no acceptance claimed**  
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
