# BCPLMAIN system-vector and runtime-global audit — checkpoint 1

**Status:** Evidence inventory; no executable changes. Baseline: 119/119
installed production-object tests plus 120/120 mixed-mode regressions
accepted 2026-10-11. This march is restricted to system-vector/global
interface reconciliation, not new I/O, loading, or recovery implementations.

## Sources examined

* `richards-bcpltape/bcplib/bcpl/cghdr` (Cambridge CGHDR)
* `richards-bcpltape/sys3/bcpl/libhdr` (surviving SYS3 LIBHDR)
* `asm/bcplmain-wip/10-bootstrap-and-system.asmfrag`
* `asm/bcplmain-wip/00-contract.asmfrag`
* Accepted runtime PDS record in `packaging/`

**Evidence caution:** Surviving headers describe interface names and
global numbers, not definitive historical ownership or complete behavior.
The reconstructed SYSV implementation explicitly documents its own
historical instruction layout as unknown.

## Machine system vector (R11)

CGHDR declares `S.COUNT=20`, `S.FIN=40`, `S.STKCK=60`,
`S.STKCKCOUNT=80`. The WIP's `SYSV` region installs corresponding
branch entry slots: `SYSCOUNT` to `CNTIMPL`, `SYSFIN` to
`FINIMPL`, `SYSSTK` to `STKIMPL`, and `SYSSTKC` to
`STKCIMP`. Each slot occupies 20 bytes; byte zero is a return entry.
This is an **implemented tested reconstruction**, not recovered
historical machine code. Exact historical stack-check and counting
semantics remain open.

## Public globals: initial ownership/coverage

Offsets below are G-number times four bytes, observed in the startup
code. `Installed` means BCPLMAIN's startup writes a routine address or
value; it does **not** independently prove complete LIBHDR semantics.

| LIBHDR entries | WIP evidence | Classification |
| --- | --- | --- |
| G1 START | Module export-trailer ingestion | application-owned; installed by runtime |
| G6 SAVEAREA | startup stores R13 converted to BCPL word address (+24) | provisional |
| G11 SELECTINPUT, G12 SELECTOUTPUT | SELINP (+44), SELOUT (+48) | implemented subset |
| G13 RDCH, G14 WRCH, G15 UNRDCH | +52, +56, +60 | implemented subset |
| G16 INPUT, G17 OUTPUT | +64, +68 | implemented subset |
| G30 STOP | STOPENT (+120) | implemented |
| G33 WRAPOUTPUT | WRAPENT (+132) | implemented subset |
| G39 FINDPARM | PARMENT (+156) | implemented subset; not JCL PARM parsing |
| G40 APTOVEC | +160; standalone BCPLAPT production object | implemented |
| G41 FINDOUTPUT, G42 FINDINPUT | +164, +168 | implemented subset |
| G46 ENDREAD, G47 ENDWRITE | +184, +188 | implemented subset |
| G52 LOADPOINT, G53 ENDPOINT | +208, +212: provisional main-module extent | provisional; not dynamic LOAD |
| G54 STACKBASE, G55 STACKEND | +216, +220 | implemented extents, historical semantics unverified |
| G76 WRITEF | +304 only if unset; preserves imported BLIB export | fallback; BLIB owner preferred |
| G85 GETBYTE, G86 PUTBYTE | +340, +344; BCPLBYTE | implemented |
| G87 GETVEC, G88 FREEVEC | +348, +352; BCPLMEM | implemented |
| G150 DEBUGINT | +600, outside enumerated LIBHDR globals | nonstandard diagnostic extension |

LIBHDR also names unverified or incompletely mapped services including
G2–G5, G7–G10, G18–G29, G31–G32, G34–G38, G43–G45,
G48–G49, G51, G56–G84, G89–G99. **Not directly installed by
the startup statements above** does **not** mean missing: application
export trailers and BLIB supply some values, and further implementation
inspection is required before assigning definitive statuses.

## Ownership rules for this march

1. LIBHDR defines names and slots; never infer implementation ownership
   from numbering alone.
2. BCPLMAIN owns startup, global-vector construction, installing runtime
   entries and control transfer. Portable BLIB exports must not be
   overwritten (the conditional G76 WRITEF fallback is precedent).
3. New machine-dependent services should have separately linked object
   owners and explicit BCPL calling/register contracts.
4. Keep R11 system-vector linkage distinct from R12 global-vector
   addressing.
5. Maintain the accepted five-member installed PDS linkage and the
   120/120 mixed-mode test baseline during this audit.

## Next bounded evidence gate

**Before coding:** reconcile every LIBHDR G1–G99 slot against actual
exports from BLIB and application-generated modules, startup writes,
and runtime routines. Produce a table with owner, evidence source,
implemented/tested status, and gap severity. Specifically investigate
G56 STACKHWM, G57 OS/CMS marker, and G45 PARMS as narrowly scoped
candidates; do **not** implement them until their contracts are traced
to consumers and historical sources.

Acceptance for checkpoint 1 is this initial audited mapping and an
explicitly bounded next step. No claim of full historical parity.
