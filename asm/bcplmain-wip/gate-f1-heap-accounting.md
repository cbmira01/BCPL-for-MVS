# Gate F1 — BCPLMEM heap accounting candidate

Status: **source staged; NOT assembled, linked, executed or installed** (12 October 2026).
Gate E installed OBJ baseline remains accepted and untouched.

## Scope and ownership

`asm/bcplmem.asm` maintains four **private 32-bit unsigned fullwords**:

| Symbol | Meaning |
| --- | --- |
| MEMCURN | Current live GETVEC allocation count |
| MEMPEAKN | Peak simultaneous allocation count |
| MEMCURB | Current live allocated bytes, **including** 12-byte descriptors |
| MEMPEAKB | Peak simultaneous allocated bytes |

Each successful GETVEC updates current totals after linking its descriptor and raises
peaks if necessary. Failed GETVEC leaves all counters unchanged. Successful FREEVEC
removes the descriptor from the live list and decrements both current values;
unknown or zero pointers leave them unchanged. MEMDRAIN decrements the current
values for every detached block; peaks persist after drain for final reporting.

The accounting covers only allocations managed by this BCPLMEM GETVEC and
FREEVEC, not the combined global/stack allocation owned by BCPLMAIN or other
MVS-managed storage. No counter is exposed as a BCPL global. Ordinary output,
GETVEC/FREEVEC ABI, three-word descriptors, G6!48 publication and production
object library are unchanged.

## New private assembler entry: MEMSTAT

`ENTRY MEMSTAT` supplies a **read-only snapshot**. Its caller passes in R1
the **native byte address** of an aligned, writable 16-byte output buffer:

| Byte displacement | Value |
| --- | --- |
| +0 | MEMCURN |
| +4 | MEMPEAKN |
| +8 | MEMCURB |
| +12 | MEMPEAKB |

Returns through R14. Preserves R0–R9, R11–R15 and R1 (R14 is temporarily
used internally then restored). **Clobbers R10**, consistent with the existing
private MEMBIND entry. The caller must preserve its own R10 if needed. Does
not provide synchronization or reentrancy guarantees; BCPLMEM is a singleton.
The private save slot and counters are module-static, so repeated starts,
parallel callers, and nested execution require separate lifecycle work.

This is a **new reconstruction engineering interface**, not a recovered
historical Cambridge contract. No diagnostic output or runtime configuration
switch is introduced.

## Verification gate before any installation

1. Run `python3 tools/checks/check-asm-source.py asm/bcplmem.asm`.
2. Assemble candidate BCPLMEM with IFOX00 in a temporary deck; require
   RC 0000, zero flagged statements and expected `MEMSTAT` ESD export.
3. Link a purpose-built temporary assembler observation probe against
   candidate BCPLMEM and externalized candidate BCPLMAIN. Do **not**
   link the probe to installed OBJ(BCPLMEM) yet.
4. Verify snapshots at initial state, after successful allocations of
   different sizes, after non-head and head FREEVEC, after failed and
   unknown-pointer operations, and after MEMDRAIN. Check count and byte
   peaks independently; check restored registers and unchanged G6!48.
5. Repeat all source-mode independent-allocator regressions, including
   039, 082, 083, 088, 122, and 123, and the full source-mode panel.
6. Only after explicit operator authorization, plan coordinated production
   installation and repeat the eligible full installed-runtime panel.

**Accounting caveat:** counters change on issuance of FREEMAIN after
descriptor unlink, not after independent verification of MVS storage manager
success. A counters-to-zero result is not proof of successful FREEMAIN return.
The existing 083 source-only instrumentation remains separately relevant.

## Open issues

- R10 clobber makes MEMSTAT inappropriate for a direct generated-BCPL call.
- There is presently no production caller or automatic report path.
- Overflow is not expected under present 24-bit allocator constraints,
  but arithmetic overflow policy is not yet separately exercised.
- Initialization is by module-static zero values, not a reset on every START;
  repeated execution in the same loaded image is outside this march.
- Physical assembler-addressability, listing, linkage and runtime checks
  are **pending MVS operator evidence**. No installation is authorized by
  this staging commit alone.

## Observed MVS execution evidence (12 October 2026)

- **JOB 9638** (`BCF1ASM`): candidate BCPLMEM assembled with IFOX00
  RC=0000; VERIFY IEFBR14 RC=0000; zero flagged statements, severity 0.
  ESD contains `MEMSTAT` as LD at X'204', BCPLMEM length X'2AC'.
- **JOB 9639**: ASMMEM, ASMDRV, LKED RC=0000; GO returned RC=3408.
  The probe's exit incorrectly restored R15, so this is not an
  interpretable accounting result.
- **JOB 9640**: same three build/link steps RC=0000; GO RC=0478.
  A further test-driver exit bug restored R1 before retrieving the
  completion code. Again not an interpretable accounting result.
- **JOB 9641**: ASMMEM, ASMDRV, LKED, GO **all RC=0000**. The temporary
  driver asserts snapshots for initial zero, GETVEC(2) = 24 bytes,
  GETVEC(4) = 32 bytes (56 total), rejected negative size, unknown
  FREEVEC, non-head FREEVEC, and head FREEVEC. Both assembler passes
  report no flagged statements and severity zero. The link map resolves
  `GETVEC`, `FREEVEC`, and `MEMSTAT` against freshly linked BCPLMEM.
  **This is isolated candidate execution acceptance, not production PDS
  acceptance.** The probe does not independently verify FREEMAIN return
  accounting.

After JOB 9641, the standalone JCL was extended to verify
`MEMDRAIN` using two outstanding allocations (checkpoints 8 and 9).
This revision has **not** yet been executed; do not credit JOB 9641
with checking drain behavior.

Next acceptance steps: execute the extended temporary-object probe,
then execute the source-mode independent-object regression panel and
only subsequently consider an explicit, controlled installation gate.
No object-PDS installation has occurred during F1.

## JOB 9642 — extended isolated execution acceptance

On 12 October 2026, JOB **9642** (BCF1RUN) completed ASMMEM IFOX00
RC=0000, ASMDRV IFOX00 RC=0000, LKED IEWL RC=0000, and GO RC=0000.
Both assembler listings reported no flagged statements and severity 0.
The IEWL map resolved GETVEC, FREEVEC, MEMSTAT and MEMDRAIN against
the freshly assembled BCPLMEM candidate.

Nine assertions passed. Checkpoints 8 and 9 repeat two outstanding
GETVEC allocations and verify that a subsequent MEMDRAIN returns
current allocation count and allocated bytes to zero while preserving
peak count and peak bytes. This fulfills the isolated MEMDRAIN behavior
gate; it does not establish independent MVS FREEMAIN return-code checks.

**Next gate:** BCPL runtime source-mode / independent-object regressions.
No production PDS object installation or installed-regression acceptance
has been carried out for Gate F1.
