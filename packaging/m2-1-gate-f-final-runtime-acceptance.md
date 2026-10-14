# M2.1 Gate F — Final D7 Native Runtime Acceptance

**Status: READY FOR OWNER ACCEPTANCE — 14 October 2026.** Gates A–E have been formally accepted and closed. This Gate F packet documents the current independent native runtime deliverable; it does **not** begin Cambridge compiler-phase compilation.

## Candidate identity and release boundary

- Authoritative main source: `asm/bcplmain-d7-candidate.asm` → `HERC02.BCPL.DEVOBJ(BCPLM7)`.
- Separate native service sources: `asm/bcplio.asm`, `asm/bcplmem.asm`, `asm/bcplbyte.asm`, `asm/bcplapt.asm`; the historical compiler-generated `BLIB` is a separate linked object.
- Development link target: `HERC02.BCPL.DEVOBJ`. The accepted D6 baseline and `HERC02.BCPL.OBJ` production library are **unchanged**. No implicit promotion is authorized or required for M2.1 closure.
- The present compiler CAMBCOMP is INTCODE under ICINT19; native applications execute with this runtime. No assertion that compiler phases are natively runnable.

## Gate F deliverables (in repository)

1. [Current runtime contract](m2-1-runtime-contract-v2.md) — supported BCPL global subset, linkage/storage/I/O/termination semantics, deliberate MVS adaptations, and explicit omissions. Supersedes the older M1.9 [v1 specification](runtime-contract-v1.md) only for this D7 candidate; historical document is not rewritten.
2. [Completion-code registry](m2-1-runtime-completion-codes.md) — sources/cleanup and evidence levels for RC 0, application STOP(N), runtime RC12, 16, 20, 24 and 36. Separates GO return code from assembler/link-edit RC and MVS ABEND.
3. [Regression interface coverage matrix](m2-1-runtime-coverage-matrix.md) — tested native interfaces and limitations, 083 expected SKIP and historical unsupported services.
4. [Gate E accepted independent application LINK/GO evidence](m2-1-gate-e-application-integration.md) — JOB 3646 and full post-focused regression; final Gate F closure checklist below.

## Evidence consolidation

| Evidence | Result |
| --- | --- |
| D7 resident assembler/install, payload JOB 2989 | ASMMMAIN IFOX00 RC=0000; PUTMAIN IEBGENER RC=0000; zero flagged statements |
| D7 integrated DEVOBJ link, payload JOB 2992 | IEWL RC=0000 |
| Gate B overflow contract | 052 and 093 PASS with diagnostic `STACK OVERFLOW` and GO RC=0012 |
| Gate E focused integration | 025, 026, 069, 075, 091, 101, 119, 121 all PASS |
| Gate E post-focused full suite | 00–123, **123 PASS / 0 FAIL / 1 expected SKIP 083 / 124 total** |
| Gate E independent link/GO, JOB 3646 RG069R | ASMAP RC=0000; LKED RC=0000; GO RC=0000; output `BLIB 42` |
| IEWL CSECTs | BCRG0069 000000/000088; BCPLMAIN 000088/000C00; BCPLIO 000C88/000FF8; BCPLBYTE 001C80/000026; BCPLAPT 001CA8/00006C; BCPLMEM 001D18/0002AC; BLIB 001FC8/001BB0. Total 003B78. |
| IEWL externals | XREF confirms runtime-to-BCPLIO, BCPLMEM, BCPLBYTE, BCPLAPT, and BLIB-to-BCPLMAIN symbol resolution |

**Source freeze:** No runtime assembler or regression test code changed in Gates C–F. Thus the already reported complete D7 candidate panel tests the exact resident object code being accepted. The Gate F changes are documents/README instructions only; no duplicate MVS rebuild or full suite is required solely for documentation changes.

## Gate F review and exclusions

The deliverable is a historically grounded, modest, programmer-facing **native BCPL application runtime on MVS 3.8J**. It is not the full historical Cambridge BCPLMAIN; it does not promise generic DDNAME discovery, reentrant operation, all LIBHDR services, nonlocal parser recovery, complete ABORT/BACKTRACE/MAPSTORE, system-level ABEND recovery, quantitative OS heap instrumentation, or native Cambridge compiler execution. No new runtime services are implicitly required to close this version.

Historical test READMEs for regressions 120 and 121 contained obsolete production promotion instructions, replaced with current explicit DEVOBJ(BCPLM7) reproduction instructions. Earlier dated audit documents may continue to report old D6/M1.9 conditions; their dated scope is authoritative for the older baseline only.

## Closure checklist

- [x] Gate A contract reconciliation accepted.
- [x] Gate B D7 controlled failure semantics accepted.
- [x] Gate C compatibility boundary accepted.
- [x] Gate D programmer diagnostics accepted.
- [x] Gate E independent native application integration accepted.
- [x] Completion-code registry created by Gate F as promised.
- [x] Regression coverage matrix and v2 runtime contract created.
- [x] Obsolete production promotion instructions corrected in 120 and 121 READMEs.
- [x] Final D7 installed-object assembler/link/GO and native full panel accepted from operator evidence; no binary changes since.
- [ ] **Owner explicitly accepts Gate F and closes M2.1**, with no production promotion.

**Recommendation:** accept Gate F and formally close the M2.1 native runtime reconstruction march. Preserve D7 as current stable development baseline for *subsequent* compiler-focused work. No MVS task remains required by Gate F at the present unchanged binary boundary.
