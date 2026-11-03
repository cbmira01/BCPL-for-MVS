# BCPL Standard Library (BSL) — scope and module design discussion

**Project:** BCPL for MVS 3.8 Reconstruction  
**Recorded:** 3 November 2026  
**Status:** Future design discussion; not an approved milestone, API, implementation, or release commitment

## Purpose and classification

The **BCPL Standard Library (BSL)** is proposed as a Cambridge-distributed collection of optional, reusable, predominantly BCPL-written facilities for application programs. The acronym **BSL** is a working shorthand, not a finalized MVS object or dataset naming scheme. The official architectural category in [runtime and library nomenclature](runtime-and-library-nomenclature.md) is **Standard Libraries**.

Maintain these boundaries:

- **Core Runtime:** mandatory execution and ABI machinery.
- **Base Library (BLIB):** recovered historical Cambridge routines and interfaces; retain historical ownership and names.
- **BSL / Standard Libraries:** reusable application algorithms, data structures, formatting and conversions, independently selectable where practical.
- **System Extensions:** optional platform services such as BCPLQSAM and BCPLTIME; their direct BCPL API wrappers belong to their owning extension packages.
- **User/Site Libraries:** separately owned packages using compatible mechanisms.

The BSL is a project-developed addition. Do not describe it as part of the recovered historical Cambridge distribution. Its installation does **not** imply every application links it.

## Tentative catalog

These are **functional families**, not a declaration that each row becomes one object member or receives the displayed name as a public API.

| Family | Candidate operations | Initial interest |
| --- | --- | --- |
| Strings | compare, copy, concatenate, search, substring, case mapping, trim | High |
| Conversion | parse/format signed integers and hexadecimal, decimal and binary representations | High |
| Mathematics | integer power, gcd/lcm, integer square root, range and rounding utilities | High |
| Bit operations | masks, fields, shifts/rotates, bit counting, packing | High |
| Arrays/vectors | copy, fill, compare, search, reverse; capacity-aware helpers | High |
| Sorting/search | insertion/quicksort/merge, binary search, comparator-based operations | High |
| Collections | lists, stacks, queues, expandable vectors, sets | Medium |
| Maps | hash tables, dictionaries, symbol tables | Medium |
| Calendar | leap years, validation, conversions, day of week, arithmetic and formatting | Medium |
| Text processing | tokenization, wrapping, field layout and text tables | Medium |
| Random | deterministic pseudorandom sequences and bounded values | Medium |
| Checksums | CRC-16/CRC-32 and simple checksums/hashes | Medium |
| Numeric | fixed-point/extended precision; floating point only after separate design | Later |
| Trees | searching, traversal and balanced trees | Later |
| Parsing | lexical scanning and reusable parsing primitives | Later |
| Encoding | hex/Base64/escaping with explicit byte and character semantics | Later |
| Statistics | aggregate and distribution operations | Later |
| Formatting | reusable data/report layout | Later |

A **possible first implementation cohort** is Strings, Conversion, Mathematics, Arrays, Sorting and Collections. This is not a milestone plan or an authorized implementation order. Check BLIB first to avoid needless duplication.

## Source, compilation and link model

Proposed programmer experience:

1. Include the relevant BCPL declaration header using the supported source inclusion convention (for example, `GET`), which supplies global declarations, manifest constants and contracts **but no object code**.
2. Compile the application's BCPL source with the Cambridge compiler.
3. Select the required precompiled BSL object members, their dependencies, and the required Core Runtime/BLIB members for MVS IEWL.
4. Ensure callable exports are installed in the BCPL global vector according to a verified registration/import mechanism.

The preferred first granularity is **independently linked modules**, not the entire BSL. Function-level dead-code elimination or automatic library search is a later investigation, **not a verified IEWL capability here**. Family labels such as COLLECTIONS may organize smaller linked members such as LIST, STACK and QUEUE.

**Important unresolved design question:** Cambridge-compiled BCPL exports use global-vector bindings; the historical/app-trailer import and BLIB-specific mechanisms are not identical to optional assembler System Extension BCEX/BCRG registration. Examine the actual generated objects, global-number registry and IEWL behavior before choosing BSL module registration. Do not assume that including a member automatically registers its globals, or that the optional System Extension dispatcher ABI is the appropriate API for every BSL routine.

## Design principles and contracts to settle

- **Portability:** prefer ordinary BCPL and portable semantics; machine-dependent optimized implementations may exist behind stable interfaces.
- **Extension boundary:** direct wrappers such as QSOPEN/QSREAD belong to BCPLQSAM. An optional BSL utility may depend explicitly on BCPLQSAM, but no core BSL use should require a platform extension.
- **Dependency transparency:** document intra-BSL, BLIB, runtime and extension dependencies and avoid accidental linkage of unrelated families.
- **String representation:** support historical length-prefixed strings as such; longer/dynamic strings require a separate type, capacity and ownership contract.
- **Memory:** use established BCPLMEM/GETVEC/FREEVEC conventions where appropriate; document ownership, lifetime, failure and mutation semantics.
- **Numbers:** 32-bit BCPL words; define signedness, overflow, division, fixed-point and precision expectations explicitly. Floating-point is a distinct design.
- **Global namespace:** allocate public globals through the project registry; measure capacity before committing a large catalog. Investigate dispatch approaches without silently changing the ABI.
- **Module headers:** declarations and symbolic constants are not code or a link directive; version and public/private name policies remain open.
- **Cross-platform character issues:** distinguish EBCDIC character handling, arbitrary bytes, and textual encodings. No implicit translation of binary data.
- **MVS distribution:** later decide source/header/object PDS layout and link instructions; GitHub remains the source authority.

## Verification expectation

Each linkable module should have BCPL tests for normal, boundary, invalid and resource paths. Families need interaction tests; integration tests must verify selective linkage (for example, strings without collections or optional System Extensions). Acceptance should include **actual System/370 native execution under MVS 3.8J** using the project compiler, assembler, IEWL and JES evidence. BSL testing must be independently reported from foundational bootstrap testing; see [regression suite separation discussion](regression-suite-separation-20261103.md).

## Deferred decisions

Finalize package/member names, headers and global allocations; determine module export/initialization mechanism; select initial families; decide whether BSL public APIs expose direct global calls or module dispatchers; decide optional dependency policy; specify versioning, error/ownership rules and acceptance gates. No code, JCL, datasets, milestones or regression acceptance states are changed by this note.
