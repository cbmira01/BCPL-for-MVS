# Cambridge BCPL runtime and library nomenclature

**Status:** Proposed project terminology and architectural direction, recorded 2026-10-15. This is a vocabulary and packaging design note, **not** a statement that all described modules or registries already exist.

## 1. Scope and governing principle

The Cambridge BCPL programming system should have a stable vocabulary for the compiler, the execution substrate, historical BCPL library services, optional reusable facilities, and programmer-developed routines.

**Distinguish what code does from how it is packaged.** A routine's *logical role* (core runtime, base library, system extension, standard library, user library) is independent of whether the code is written in BCPL or assembler, and independent of which MVS PDS member holds its object. Do not confuse a `GLOBAL` declaration with code, or a package with one load module.

Preserve historical names and interfaces where recoverable. Do not retrofit modern library categories onto historical sources as claims of original Cambridge organization. New names are **project conventions for future reconstruction and distribution**.

## 2. Umbrella terminology

**Cambridge BCPL Programming System:** compiler and its accompanying runtime, base library, optional extensions, standard libraries, tools, documentation and examples. Avoid calling this entire distribution simply "the runtime."

**Cambridge Compiler:** source-to-target transformation machinery (historical SYN/TRN/CG370 reconstruction and future native/self-hosted Cambridge). It does not acquire new functionality merely because a library is installed.

**Cambridge Runtime Library:** collective name for **Core Runtime + Base Library**: the essential services needed by an ordinary compiled BCPL program according to the established historical/accepted runtime contract. "Runtime library" is a logical collective name; it need not reside in a single physical object or load library.

**Cambridge Runtime and Libraries:** acceptable broader collective name when discussing core plus all optional facilities, including site/user packages.

## 3. Logical taxonomy

| Category | Proposed term | Illustrative modules | Intent / requirement |
| --- | --- | --- | --- |
| 1 | **Core Runtime** | `BCPLMAIN`, `BCPLMEM`, and core stream facilities (potentially `BCPLIO`) | Startup/termination, global vector, workspace, essential machine-dependent ABI/runtime; mandatory insofar as required by the accepted execution contract |
| 2 | **Base Library** | Historical `BLIB` | Essential historical BCPL-callable support routines. Preserve the source/name and recovered global assignments |
| 3 | **System Extensions** | `BCPLQSAM`, `BCPLTIME`, `BCPLDEC` | Optional facilities exposing MVS/System/370 services or strongly host-specific implementations |
| 4 | **Standard Libraries** | Prospective `BCPLMATH`, `BCPLCHAR`, `BCPLSTR` | Optional, generally useful, documented programming APIs distributed by the Cambridge project |
| 5 | **User Libraries** | `MYUTIL`, `ACCOUNT`, local mathematics or application packages | Reusable code owned by an individual programmer; a team's shared libraries may be called **Site Libraries** |

**Classification describes responsibility, not the language in which a member is implemented.** A System Extension can have a portable BCPL wrapper over assembler, while a Standard Library can use machine-specific optimizations behind a portable contract.

The named optional modules and standard libraries are **proposals**, not accepted deliverables. The current M3 manifest distinguishes accepted `BOOT_OBJ` members from development candidates in `BOOT_DEVOBJ`; e.g. `BCPLIO` is currently a development candidate, so listing it as a possible core role is **not** a claim of accepted/core installation.

### Core Runtime

Owns the executable's mandatory ABI and environment: MVS entry and exit, save-area discipline, workspace/stack, global-vector allocation/import, allocation primitives and the subset of historical I/O and diagnostics essential to accepted BCPL semantics. It should remain small and intelligible. Existing component boundaries and the historical runtime contract decide exactly what is mandatory; **do not move a historical essential service to an optional package by renaming it**.

### Base Library: BLIB

`BLIB` is the reconstructed **historical base library**, not a generic word for every new library. Keep that name rather than inventing `BCPLSTD` or renaming BLIB to "standard library." BLIB may contain both general-purpose and runtime-adjacent procedures; its historical contract takes priority over our neat taxonomy.

`LIBHDR` is the **historical base declaration header**, not an executable library. It publishes `GLOBAL` names/numbers and `MANIFEST` constants. It does not itself link any code or populate slots. The source under `richards-bcpltape/sys3/bcpl/libhdr` is the evidence authority for the historical names present there; its complete implementation remains subject to reconstruction.

### System Extensions

A System Extension is an optional package primarily intended to expose platform facilities. `BCPLQSAM` (MVS record I/O), `BCPLTIME` (MVS clock bridge) and `BCPLDEC` (initial System/370 packed-decimal implementation) are the first candidates. None is intrinsically part of BCPLMAIN or a prerequisite for M4.

Category boundaries may change without ABI disruption as functionality matures. For example, **pure Gregorian calendar arithmetic** might eventually become a portable standard package while the MVS clock adapter remains a System Extension. Likewise, a decimal API could become portable even if its initial implementation is System/370 assembler. Avoid using "standard" as a claim of cross-platform availability until its contract and distribution policy are defined.

### Standard Libraries

These supply reusable *programming facilities*, not operating-system primitives or compiler features: mathematics, character classification/conversion, string manipulation, data structures, etc. A standard library is **Cambridge-distributed and maintained**, but need not be required by every application. Distinguish "distributed with the product" from "linked into every program."

### User and Site Libraries

A User Library is produced outside the Cambridge distribution and is owned by a programmer or organization. A Site Library is the same kind of package maintained for a particular installation or team. User/site packages **use the same compiled/assembled module ABI, optional registration, headers and link-edit rules** as Cambridge-maintained packages. Ownership is different; no second class of function call is needed.

## 4. Physical artifacts: unambiguous vocabulary

| Term | Precise meaning | Not the same as |
| --- | --- | --- |
| **BCPL source** | BCPL program/procedure declarations and implementation | A compiled object module |
| **Header / declaration header** | BCPL source included by other sources, containing public `GLOBAL`, `MANIFEST`, and other declarations; historical `LIBHDR` is the example | A linked library or a registration table |
| **Source module** | Independently maintained translation or assembly unit, generally producing relocatable code/data | A multi-module package |
| **Object module** | Relocatable output consumed by MVS IEWL, possibly containing one or more control sections | An executable load module |
| **Package** | Named distribution unit: public contract/header, implementation module(s), dependencies, build/link instructions, examples/tests and version information | Necessarily one object/PDS member |
| **Object library** | An MVS partitioned dataset holding relocatable object members, e.g. manifest's `BOOT_OBJ` or `BOOT_DEVOBJ` | The logical Base/Standard Library |
| **Load library** | MVS library of link-edited executable load-module members | An object library or BCPL source package |
| **Global Number Registry** | Source-controlled authority that assigns and reserves BCPL `G!N` numbers to exported symbols/packages | The startup registration table or `LIBHDR` |
| **Module Registration Table** (provisional `BCPLREG`) | Per-application, link-time selected table telling the startup runtime which linked optional modules/exports to install | Global-number allocator, header or dynamic loader |

Avoid unqualified "library" where ambiguity matters. Say **Base Library**, **Standard Library**, **User Library**, **object library PDS**, or **load library PDS**.

## 5. Module, package and public interface conventions

A new optional package should define:

1. A stable **package name** (e.g. `BCPLQSAM`), purpose and ownership/classification.
2. One or more **implementation source modules**, BCPL, assembler, or both, each with a clear responsibility. Meaningful subdivision is preferred over one monolithic source file, without gratuitous fragmentation.
3. One or more **public BCPL declaration headers**, publishing globally agreed exported names/numbers and constants; private declarations stay private.
4. Its compiled/assembled **object module(s)**, built from tracked source. A package can contain multiple object members, with explicit IEWL inclusion and dependencies.
5. A **versioned public ABI and documented semantics**, including arguments, return/status, string/byte/word pointers, resources and error behavior.
6. Where needed, the shared **optional global registration descriptor** described by Milestone Runtime Extensions.
7. **Build/test evidence, example BCPL usage, and link-edit/JCL instructions**, including MVS DDs for system-specific services.

Source naming should favor stable, recognizable names. `BCPL*` names are useful for Cambridge-distributed modules; local/user names must not impersonate official core/historical names. Naming or exporting an assembler symbol does not automatically allocate its global number.

**Example only:**

```text
BCPLCHAR package
  public header: CHARHDR       (conceptual name, not allocated)
  BCPL source:   classification and conversion routines
  object member: BCPLCHAR      (or several named members)
  registration:  selected exports in the common BCPLREG table
  tests:         character classification and conversion cases
```

Do not impose new directories or PDS names without first checking `config/dspal.yaml` and current build conventions. On MVS, partitioned dataset **member naming constraints** and source record width must be respected, separately from longer Git filenames.

## 6. Global-space ownership: allocation versus installation

The BCPL global-vector slots are **statically numbered ABI locations**. A compiled reference to global `N` uses the assigned `G!N`; it cannot safely be renumbered by a run-time allocation scheme without rewriting references.

Two complementary registries are therefore required conceptually:

1. **Global Number Registry — development/compile-time policy.** One authoritative Git-maintained catalog of allocated/reserved public slot numbers, names, package ownership, status and compatibility policy. Proposed future machine-readable form under `packaging/` or a designated configuration directory; the authoritative record now exists as [`global-number-registry.md`](global-number-registry.md). Existing `LIBHDR` is a historically authoritative declaration source, but not a complete multi-package allocation registry.
2. **Module Registration Table — link-time/startup machinery.** A list of selected, linked packages and their exported addresses, possibly `BCPLREG`. Its layout, assembler interface and validation remain to be decided and tested in **Milestone Runtime Extensions, R.0**. It does not assign global numbers.

**Global-number policy:** reserve historically assigned slots intact; allocate permanent non-conflicting slots/ranges for Cambridge-managed packages; retain released assignments as tombstones unless an explicit major compatibility break is approved. G!200 (BCPLQSAM), G!201 (BCPLTIME), and G!202 (BCPLDEC) are officially allocated in the [Global Number Registry](global-number-registry.md); other illustrative numbers must not be treated as allocations.

Historical `LIBHDR` already names `READREC:23`, `WRITEREC:24`, `TIMEOFDAY:27`, `TIME:28`, `DATE:29` and `FIRSTFREEGLOBAL=150`. The reconstructed BCPLMAIN currently uses `G!150` for provisional diagnostics. **The first-free constant does not mean every higher slot is presently unused.** R.0 must inventory the entire current/global historical occupancy, and assess present capacity before making assignments.

For **user/site packages**, a central Cambridge registry cannot realistically allocate every programmer's private routines worldwide. Reserve a documented user/site allocation policy or range *after capacity and existing usage are inspected*; each installation or application's dependency set must maintain an **effective composed registry** and reject collisions before compiling/linking. Site-private assignments are not universal ABI guarantees. Published third-party packages that need cross-installation compatibility should register or document globally stable allocations through an agreed process rather than assume arbitrary free slots.

A header makes names visible to the **compiler**. IEWL includes chosen **objects**. The **startup registrar** installs associated addresses. Those are distinct phases. Linking an optional object alone does not guarantee global registration; importing a header alone does not guarantee the extension is available.

### Optional package dispatch and public header conventions

The preferred design under [Milestone Runtime Extensions](milestone-runtime-extensions.md) is **one public global-vector slot for the dispatcher of an optional package**, not one slot per operation. Each package then owns a separate, permanently numbered **opcode namespace**. **Opcode 0** is the **owner-approved** common side-effect-free capability/version query. This is an approved R.0 contract, **not** an implemented optional registrar or accepted package.

A package header can publish both its assigned dispatcher slot and its local opcode constants:

```bcpl
GLOBAL $( TIMESVC:201 $)          // illustrative name; G201 assigned to BCPLTIME
MANIFEST $( T_QUERY=0; T_NOW=1; T_ADD=2 $)
```

The [approved shared QUERY v1 contract](runtime-extensions-r0-query-abi-decision-20261021.md) returns a **caller-owned numeric capability descriptor**, not a free-form string or unmanaged function pointer. Its six-word prefix contains format version, package API major/minor, required word count, operation bitmap and package-specific flags. Calls use `PACKAGE_SVC(0, info, capacity_words)` and the size inquiry `PACKAGE_SVC(0,0,0)`; a missing or unregistered extension **cannot** be queried safely. Cross-package MVS evidence is pending.

The **Global Number Registry** reserves the package's dispatcher slot; a **package API registry/header** defines stable opcode numbers. Generated BCPL headers and assembler definitions should derive from the authoritative assignments rather than silently diverging. Private implementations and optional future source-level helper wrappers do not require new global slots. User/Site Libraries use the same arrangement with a documented local-number and collision policy.

## 7. Inclusion policy and runtime startup

| Scope | Inclusion rule |
| --- | --- |
| **Building the Cambridge distribution** | Select minimal/full installation profiles and which optional packages to provide; no source-level compiler dependency on those packages |
| **Building a particular BCPL application** | Explicitly link required optional object modules in MVS JCL / IEWL and include the matching application registration object/table |
| **Starting an application** | Core startup populates the global vector from the application, historical BLIB/core and **only selected** extensions, then invokes `START` |
| **Running the program** | JCL supplies DDNAME allocations and other runtime resources; it should not determine optional code inclusion retroactively |

Initially prefer **explicit programmer-selected IEWL `INCLUDE` statements** for visibility and historical simplicity. Future build tooling may automate generation of those statements and the registry table without changing the fundamental ABI.

Startup registration should reject invalid/duplicate assignments and range violations instead of silently overwriting core/historical globals. The design must handle no optional packages, optional dependencies, missing referenced functions, and deterministic ordering. See [Milestone Runtime Extensions](milestone-runtime-extensions.md); these are **planned requirements**, not present runtime guarantees.

## 8. Intended build/documentation structure

For a package, documentation should answer in order:

- What API does it expose, and which header declares it?
- Which globally assigned numbers and version of the ABI does it use?
- What source modules and object members implement it?
- Is it essential/core, historical base, optional system extension, optional Cambridge standard, or local user/site code?
- Which optional dependencies and MVS DD allocations does it require?
- How is it linked, registered, rebuilt from Git, tested on TK5/MVS and cleanly excluded?

Use the manifest `config/dspal.yaml` for actual MVS datasets; do not confuse example `OBJLIB` / `EXTLIB` DD labels with real DSNs. Candidate objects remain in `BOOT_DEVOBJ` until accepted; `BOOT_OBJ` is an accepted object library, **not** the entire Cambridge runtime. Do not migrate binaries into future Cambridge namespaces: rebuild from tracked sources and preserve JES/IFOX/IEWL evidence.

## 9. Examples of how to speak about the system

- "The **Cambridge Compiler** produces a relocatable object for the application."
- "The **Core Runtime**, with historical **BLIB**, provides the **Cambridge Runtime Library**."
- "The optional **BCPLQSAM System Extension** is installed but not linked into this application."
- "The optional **BCPLMATH Standard Library** provides numerical routines independent of the application."
- "The accountant's **User Library** or the installation's **Site Library** is distributed and linked using the same conventions."
- "`LIBHDR` is a **header**, not the BLIB object."
- "`BOOT_OBJ` is an **object library PDS**, not a semantic collection of 'standard library functions'."
- "The **Global Number Registry** allocates permanent slot numbers; `BCPLREG` (if adopted) registers addresses in a particular executable."

## 10. Status and follow-up

This nomenclature is recorded for future design and documentation consistency; it makes no changes to compiler/runtime functionality. The detailed startup/import mechanism, registry schema, global ranges, header generation, optional object naming and site-extension policy must be designed and validated before acceptance.

In **Milestone Runtime Extensions R.0**, explicitly include (a) global-number ownership and user/site collision rules, (b) the source/header/object/package separation, and (c) the same import mechanism for project and independently developed packages. The taxonomy should remain stable even if the implementation or physical packaging changes. Neither this note nor the optional extension milestones block **M4** self-hosting.
