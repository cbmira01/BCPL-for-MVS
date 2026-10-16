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
