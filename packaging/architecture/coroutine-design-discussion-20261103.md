# Coroutine support — interpreter-hosted and native System/370 design discussion

**Project:** BCPL for MVS 3.8 Reconstruction  
**Recorded:** 3 November 2026  
**Status:** Architectural discussion; proposed direction, not an accepted implementation contract or milestone

## 1. Purpose

Record the architectural discussion concerning BCPL coroutine support, its place in the Cambridge Runtime Library, and the relationship between the interpreter-hosted and native System/370 implementations.

The intended result is coroutine compatibility between BCPL executing under INTCODE and BCPL executing natively under MVS 3.8J.

## 2. Architectural classification

The recommended classification is:

- **Core Runtime:** machine-dependent coroutine context-switching mechanism, principally `CHANGECO`.
- **Base Library (BLIB):** historical coroutine management routines where their historical ownership and implementation are established.
- **Compiler:** generates ordinary BCPL procedure calls and compatible activation records, without requiring a new coroutine language construct.
- **System Extensions:** not required for coroutine execution.

Higher-level routines, potentially including `CREATECO`, `DELETECO`, `CALLCO`, `COWAIT`, and `RESUMECO`, should retain their historical interfaces where recoverable.

Their exact presence, names, ownership, and global assignments in the target Cambridge sources require verification. They must not be introduced as accepted historical interfaces solely because later BCPL implementations provide them.

A separate portable coroutine library is a possible implementation choice if the target historical BLIB does not establish ownership.

## 3. Interpreter-hosted implementation as reference

The working interpreter-hosted environment offers an important source of behavioral evidence.

The investigation should establish:

1. How coroutine descriptors identify suspended execution contexts.
2. Which interpreter registers and activation-record fields are retained across a switch.
3. How the active coroutine is identified and updated.
4. How execution resumes at a previously suspended call.
5. How arguments, function results, and coroutine termination are handled.

Later Richards Cintcode implementations provide useful comparative evidence, but their internal representations must not automatically be attributed to the project's earlier INTCODE implementation.

The actual ICINT19 and historical bootstrap sources must be examined before adopting a particular context layout or switching algorithm.

## 4. Native System/370 implementation

Native `CHANGECO` should preserve the observable behavior established by the interpreter-hosted implementation while using the accepted System/370 BCPL calling convention.

The existing runtime contract identifies:

| Register | Established native role |
| --- | --- |
| R5 | Current BCPL activation frame |
| R6 | BCPL return linkage |
| R7–R9 | Arguments and results |
| R4 | Frame-dependent value restored by the native return convention |
| R11 | Generated-code system-vector base |

The implementation must determine which additional registers and machine state are live at a suspension point. It cannot assume that every register must be saved or that the interpreter's virtual registers map directly onto physical System/370 registers.

The existing BCPLMAIN system-vector return path, activation-frame layout, and CG370-generated call sequences are primary implementation evidence.

### Switching model

Conceptually, native `CHANGECO` must:

1. Preserve the outgoing coroutine's resumable execution context.
2. Store that context in the appropriate coroutine descriptor.
3. Select the incoming coroutine and obtain its saved context.
4. Restore the required native execution state.
5. Transfer execution to the incoming coroutine's saved continuation with the correct BCPL result semantics.

The exact order, descriptor fields, and register assignments remain unresolved.

`CHANGECO` is a cooperative context transfer, not an MVS task dispatch or a supervisor-level context switch.

## 5. Stack architecture

The current native Core Runtime establishes a global vector and a bounded working-stack region during initialization.

Coroutines require independently preserved activation-record chains and storage that remains valid while another coroutine executes.

An important open question is whether the existing stack allocation and stack-check facilities can accommodate multiple coroutine-owned stack regions without changing the accepted native ABI.

The design must address stack allocation, bounds checking, stack-high-water behavior, exhaustion, reclamation, and termination.

A coroutine must not resume into storage already reclaimed or repurposed by another coroutine.

## 6. Bootstrap and native compiler relationship

The project distinguishes two execution environments:

- **Interpreter-hosted bootstrap toolchain:** the Cambridge compiler executes as INTCODE under ICINT19 and generates native System/370 code.
- **Native Cambridge compiler:** the separately reconstructed compiler executes directly under MVS using the native BCPL runtime.

Implementing native `CHANGECO` does not, by itself, convert the interpreter-hosted compiler into a native compiler.

Likewise, the existence of interpreter coroutine support does not establish native support.

Both environments should be tested against the same observable coroutine behavior, with implementation-specific tests for their respective execution mechanisms.

## 7. Verification strategy

Before implementation, inspect the actual historical and reconstructed sources and document the coroutine descriptor layout and switching contract.

A bounded native test sequence should establish:

1. Two independently initialized coroutine contexts.
2. Initial transfer and correct entry into the second coroutine.
3. Suspension and resumption of each context.
4. Preservation of local variables and nested activation records.
5. Correct argument/result transfer.
6. Repeated switching without corruption.
7. Stack-boundary and lifecycle handling.
8. Compatibility with the existing native regression suite.

Where feasible, equivalent BCPL tests should run under INTCODE and native System/370.

Native acceptance requires observed IFOX assembly, IEWL linkage, and execution under MVS 3.8J, supported by actual JES/test evidence.

## 8. Decisions remaining open

The following are not settled by this discussion:

- Exact historical coroutine operations present in the target Cambridge distribution.
- The actual INTCODE `CHANGECO` mechanism.
- The native coroutine descriptor and stack representation.
- Register preservation and continuation-restoration details.
- Coroutine initialization and destruction.
- Ownership of higher-level coroutine routines within BLIB or a separate library.
- Whether native compiler reconstruction requires coroutine support immediately or may add it after initial compiler execution.

## 9. Recommended direction

Use the interpreter-hosted implementation to establish the behavioral contract. Then derive an IFOX implementation of native `CHANGECO` from the verified System/370 BCPL calling convention.

Keep the machine-dependent primitive in the Core Runtime and retain historical higher-level routines wherever possible.

Do not introduce an optional System Extension merely to supply fundamental coroutine execution support.

This is a design discussion only. No implementation, global-number allocation, JCL, MVS dataset, acceptance record, milestone, or march status is modified by it.

## 10. Repository references

- `packaging/architecture/runtime-and-library-nomenclature.md`
- `packaging/architecture/runtime-contract-v1.md`
- `packaging/architecture/global-number-registry.md`
- `bootstrap-toolchain/asm/bcplmain.asm`
- `bootstrap-toolchain/README.md`
- `richards-bcpltape/`
- `mr10-kit-compiler/`
