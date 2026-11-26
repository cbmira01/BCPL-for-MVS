# Explanation of System Extensions

*Cambridge BCPL Programming System for MVS 3.8J*

See the [reference](Reference-for-System-Extensions.md), [how-to](How-to-Use-System-Extensions.md) and [tutorial](Tutorial-on-System-Extensions.md) for interfaces and usage.

## 1. Role of System Extensions

Optional platform facilities and reference implementations are distinct from Core Runtime, historical Base Library (BLIB), Coroutine Support Library and Standard Libraries. Logical responsibility is independent of source language or PDS packaging. Extensions provide services, not compiler syntax. A program without any selected extension must still run. See [nomenclature](../../packaging/architecture/runtime-and-library-nomenclature.md).

## 2. Global dispatch and public headers

One package normally owns one dispatcher global. BCPLDEMO is the package identity, DEMOSVC the global name at 203, DMODISP the assembler entry. Opcodes are package-local. The [Global Number Registry](../../packaging/architecture/global-number-registry.md) owns allocations. Declarations compile numeric references, not addresses or code. The native first three arguments enter R7/R8/R9, result R7; BCPL word pointers differ from linked byte addresses. QUERY discovers capabilities of a registered package, not absent objects.

## 3. BCEX descriptors and BCRG registration records

BCEX describes identity, API version, exports, dependencies and optional finalizer. BCRG is the application's selected extents and required identities; BCPLREG is its control section.


```text
BCPL source + declarations -> application object
BCX selection -> BCRG object + IEWL INCLUDE
package object -> BCEX + dispatcher (+ finalizer)
                         |
                        IEWL
                         |
          linked application / relocated addresses
                         |
          BCPLMAIN / BCPLRGS -> validate -> register -> START
```

Independently relocated extents enable bounds checks, not protection from hostile machine pointers. The [R.0 approved layouts](../../packaging/milestones/runtime-extensions/runtime-extensions-r0-owner-abi-decisions.md) supersede the earlier 40-byte proposal.

## 4. BCPLREG startup, validation, ownership and finalization

Startup imports actual application/BLIB exports and native services. It is designed to validate registry and selected extents, identity, version, ownership and dependency order before START. Publication is separate from validation. DR.5 corrected generic dependency-validation defects, including multiple dependencies, later descriptor preflight, malformed versions and nonzero dependency ordinals. The private and installed 18-assertion registrar probe passed on MVS; the maintained packages themselves have zero dependencies. See chapter 2 of the reference. Failed validation returning through the registrar publishes no optional entries. A real empty registry describes no packages. Historical G!76 precedence does not permit new optional overwrites.

There is no v1 initializer; packages acquire resources lazily. On normal termination finalizers run once in reverse order before IOFIN/MEMDRAIN. Returned finalizer error changes ordinary FINISH to RC8; explicit STOP preserves requested status. Abends can bypass this. See [R.1 closure](../../packaging/milestones/runtime-extensions/runtime-extensions-r1-closure-20261022.md) and [BCPLRGS](../../bootstrap-toolchain/asm/bcplrgs.asm).

## 5. Known-package selection and IEWL linkage

IFOX concatenates BCXPRE, catalog, application cards and BCXPOST. BCXSEL/BCXREQ emit one INCLUDE and extent per distinct package; BCXREQ records a required identity. IEWL relocates entries and descriptor bounds. Explicit application ENTRY avoids selecting a registry or descriptor as executable entry; R.4 retains the initial failure and corrected result.

The current [catalog](../../system-extensions/bcx/BCXCAT.asm) names DEMO, TIME and QSAM with EXTLIB member expressions. Source mode may use temporary DDs. IEWL INCLUDE alone was not proven to discover arbitrary descriptors. Dependency validation is not automatic transitive selection. See [R.4 closure](../../packaging/milestones/runtime-extensions/runtime-extensions-r4-closure-20261024.md).

## 6. BCPLDEMO, BCPLTIME and BCPLQSAM as examples

| Package | Architectural lesson |
| --- | --- |
| BCPLDEMO | Stateless dispatch, capability inquiry and no-write capacity failure |
| BCPLTIME | Native hardware/MVS adapter, aligned scratch, permanent-register preservation |
| BCPLQSAM | Owned stages and DCBs, logical records, pending retries, generic finalizer |

Each package is one independently selected object, despite multiple CSECTs. QSAM owns private stages, not caller buffers. Unlike BCPLIO, it does not trim, insert newline or translate bytes. QSAM handles blocking/deblocking; RDW is private to variable records; ASA byte belongs to the caller's FBA record.

## 7. Portability, safety and lifecycle

A common QUERY prefix does not unify ordinary opcodes or results. Valid storage and honest capacity are caller obligations. Native ABI is not MR10 INTCODE. Private scratch/state constrains reentrancy. MVS may abend instead of returning control; output accepted by QSAM is not necessarily delivered to its device. Quarantine after returned CLOSE failure avoids falsely claiming resource ownership or reusing uncertain DCB storage.

## 8. Deferred design and limitations

BCPLDEC remains proposed on indefinite deep background, G!202 reserved. R2TESTB and historical 298/299 bindings are fixtures, not public allocations; native coroutine support now owns those slots. G!150 DEBUGINT/FORMTREE remains unresolved.

The [expanded milestone closure](../../packaging/milestones/runtime-extensions/runtime-extensions-milestone-formal-closure-20261116.md) qualifies R.0–R.5: no runtime dynamic loader, arbitrary discovery, automatic dependency selection, general User/Site catalogs or universal interoperability. QSAM source-backed installation is not independent installed linkage proof. [RC4](../../packaging/distribution/publication/RC4-README.md) supplies native components as work in progress; native development acceptance is separate.
