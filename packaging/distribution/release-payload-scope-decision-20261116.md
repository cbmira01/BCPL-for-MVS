# Release payload scope expansion - owner decisions, 16 November 2026

**Project:** BCPL for MVS 3.8 Reconstruction  
**Status:** Owner-approved release payload scope and acceptance requirements; **not implemented or release-accepted**  
**Authority:** GitHub `main`; supersedes the narrower product-inventory exclusions of [8 November 2026](native-cambridge-compiler-distribution-decisions-20261108.md), while retaining its tape naming, release identity, single-manifest, installation safety and acceptance rules.

## Subsequent owner clarification — 16 November 2026

The owner subsequently approved the [`EXP:` expected-output and manual MVS-verification decision](mr10-regression-exp-manual-verification-decision-20261116.md) for the standard **12-case `MRREGRES` panel**. Every BCPL regression will print fixed literal `EXP:` records alongside unchanged actual `RP:` results, and a person will inspect all 12 cases plus interpreted `CODE=`, recording explicit per-case PASS/FAIL and overall sign-off. The existing WSL `RP:`/`CODE=` automated runner remains. This later decision **supersedes the automatic MVS-resident PASS/FAIL comparison and automatic semantic-mismatch non-success requirement** described below. Those requirements remain preserved below as the earlier decision record, not as live acceptance gates. MVS-only verified execution and human sign-off **remain unimplemented**.

The nine-march [Tape artifact release milestone](../milestones/tape-artifact-release/milestone-tape-artifact-release.md), TA.0–TA.8, was also owner-approved on 16 November 2026. Neither decision authorizes media creation, MVS changes or publication.

## Owner decisions

In discussion on 16 November 2026, the owner expanded the proposed Cambridge BCPL Programming System distribution to include the **Coroutine Support Library**, **all three currently implemented and accepted System Extensions**, and the **MR10 Kit Compiler** as a fully usable, independent interpreted programming environment with its demonstrations. The owner additionally directed inclusion of the **12-case MR10 Kit Compiler regression panel**, conditional on recipients being able to compile, run and verify that panel **entirely under MVS 3.8J**. No distribution media, installer or publication was authorized.

The native-running **Cambridge Compiler** remains the principal release deliverable and retains its native self-compilation acceptance requirement. Distribution of the MR10 kit does not substitute for or block verification of the native compiler. The independently reconstructed, interpreter-hosted/demoted `CAMBCOMP` and host development/bootstrap utilities remain outside the required release payload.

## Approved logical payload

| Component | In-scope payload and role |
| --- | --- |
| Native Cambridge Compiler | Ready-to-run native compiler, source and supporting assembly, MVS build/link JCL, documentation, application examples and tests; demonstrate self-compilation with the distributed native executable |
| Core Runtime and historical Base Library | Required source, headers, object modules, build instructions and `BLIB` for the native compiler/programs |
| Coroutine Support Library | `coroutines.bcpl`, `coroutines.h`, native `COROUTIN` object, associated Core Runtime bridge `BCPLCO` and maintained assembler source; preserve their accepted bounded native behavioral contract |
| `BCPLDEMO` | Supported reference System Extension, with object/source/header, BCEX/BCRG v1 selection information and representative verification |
| `BCPLTIME` | Installed/accepted System Extension, with object/source/header, selection information and verification |
| `BCPLQSAM` | Installed/accepted sequential-record System Extension, with object/source/header, selection information, DD/JCL documentation and verification |
| MR10 Kit Compiler | Independently installable, ready-to-run `ICINT19`, its assembler source/build JCL; `SYNI`, `TRNI`, `CGI`, `BLIBI`, `ICLIB` INTCODE decks; all required program/runtime inputs, source/provenance, MVS compilation/execution JCL and user documentation |
| MR10 demos | All **11 language demonstrations** (`MRLANGDM`) and **17 BCPL demonstrations** (`MRBCDEMO`), their BCPL sources, library/input dependencies, on-MVS job procedures and instructions |
| MR10 regression panel | All **12 standard panel cases** (`MRREGRES`), required BCPL and library/input members, golden `RP:` output records, interpreted completion expectations, MVS compile/run/verification procedures and readable per-case PASS/FAIL reporting |
| Release installation/documentation | MVS-only tape bootstrap, allocation/restore and verification JCL, site-parameterized dataset names, release manifest, documentation and external bootstrap instructions |

All three listed System Extensions are **included on the release medium but remain optional at application link-edit time**. The Coroutine Support Library is separately classified from historical `BLIB` and is not a System Extension. The MR10 interpreted environment and native compiler environment are independently installable and independently usable; they do not share a binary ABI, and interpreted versus native coroutine behavior is guaranteed only over the separately accepted common domain.

**Excluded/deferred:** `BCPLDEC` is proposed but indefinitely deferred; no `BCPLDEC` object is included. The unimplemented BCPL Standard Library is not in scope. The interpreter-hosted/demoted Cambridge Compiler `CAMBCOMP`, developer-only Hercules/WSL/Python/`dspal` tools and full historical source reconstruction tree are not required release payloads. Historical MR10 development-probe suites are **not automatically included** merely because the standard 12-case regression panel is included. Any extra components require a separate inventory decision.

## MR10 standalone acceptance requirements

The existing `mr10-kit-compiler/jcl/run-regression-tests.jcl` is an **MVS-executable** stored job body that stages five compiler/runtime decks, performs 46 compiler/generator steps and 12 execution steps for the 12 cases. It currently refers to development `HERC02` datasets and lacks a site-specific JOB card. Both must be adapted for distribution. The suite documentation identifies MVS job bodies `MRLANGDM`, `MRBCDEMO` and `MRREGRES`.

**Important current gap:** `MRREGRES` executes on MVS but does **not** presently compare interpreted `CODE=` and semantic `RP:` records with the golden output. A zero JES condition code alone does not prove a regression case passed. That comparison is currently done by the separate host-side `tools/mr10/run-regression-panel`. Consequently **MVS-only verified panel acceptance is not yet demonstrated**.

Before a release can claim an independently verified MR10 panel, the tape-installed environment must:

1. Supply `ICINT19`, compiler/runtime decks, demo and panel sources, expected results, and any required DD input data without needing GitHub, WSL, Python, `dspal` or host-side manifest processing.
2. Provide site-parameterized, operable MVS batch/JES JCL to compile and execute the complete standard **12-case** panel; provide separate instructions/JCL for all 11 + 17 demos.
3. Check each case's interpreter-level completion and semantic `RP:` golden output **on MVS**, reporting clear per-case PASS/FAIL and non-success overall when a case diverges. The implementation mechanism is **not yet selected**; do not claim a finished MVS verifier.
4. Prove on a freshly installed MVS target that all 12 cases can be compiled, run and evaluated with only the tape payload and ordinary available MVS facilities; demonstrate that neither compiler environment depends on installing or invoking the other.
5. Preserve historical test fixtures and actual known limitations rather than silently converting failing unrelated development probes to PASS. This decision concerns the standard 12-case `00-regression-panel`, not the separate `mr10-probes` or historical coroutine diagnostics.

## Retained distribution rules and open work

The approved [8 November distribution design](native-cambridge-compiler-distribution-decisions-20261108.md) still controls one canonical release manifest, producer/consumer consistency, `BCPL.BT0001` read-only EBCDIC FB80 bootstrap text, `BCPL.BT0002` installation JCL, subsequent `BCPL.BTnnnn` standard-label logical tape datasets, target-site HLQ selection, frozen Git revision, version and unique VOLSER, exact tape SHA-256, clean-target verification and publication of **only the tested bytes** after separate owner approval.

The exact tape dataset inventory and order, installation-mode choices, site-independent JCL, independent compiler verification, native compiler self-hosting, on-MVS MR10 golden verifier, complete multi-dataset tape writer, clean-target installation, version/VOLSER registry, and complete per-component redistribution/provenance audit **remain to be designed, built and tested**. No source compilation, IFOX/IEWL/JES operation, AWS image creation, MVS dataset mutation, test run, or release publication is performed by recording this decision.
