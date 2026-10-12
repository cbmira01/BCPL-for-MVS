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
