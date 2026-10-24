# Milestone BCPLTIME — primitive System/370 and MVS time access

**Project:** BCPL for MVS 3.8 Reconstruction  
**Status:** ACTIVE — T.0 CLOSED; T.1 IN PROGRESS (owner decision 24 October 2026). T.0 MVS JOB 5436 PASS; installed-mode acceptance pending  
**Package:** `BCPLTIME` — optional System Extension  
**Target:** IBM System/370, MVS 3.8J TK5 under Hercules  
**Governing registration architecture:** BCEX/BCRG version 1, using the existing optional System Extension mechanisms  
**Public BCPL GLOBAL:** G!201, assigned to BCPLTIME in the Global Number Registry; proposed dispatcher spelling `TIMESVC`  
**Historical predecessor:** *Milestone Date and Time Services*, proposed 15 October 2026 (see historical record below)

## 1. Owner decision and objective

This revision replaces the original broad date/time-library proposal with **Milestone BCPLTIME**. The owner has directed **accelerated development**: proceed directly to a real optional-package descriptor and assembler dispatcher, then diagnose behavior through actual native BCPL execution under MVS. Do not start with a lengthy sequence of preliminary experiments or standalone probes.

BCPLTIME exposes only the primitive clock and date/time information supplied by the processor and operating system. **It is not a calendar, scheduling, or general timing library.** Its interface must not imply historical Cambridge BCPL provenance: this is a project-created System Extension for the reference MVS implementation.

## 2. Version-1 public API — exactly three opcodes

Use the established three-argument BCPL dispatcher pattern:

```text
TIMESVC(operation, output_vector, capacity_words)
```

`TIMESVC` is the proposed public spelling for G!201. A BCPL pointer is a 32-bit **word address**, and capacities are counts of 32-bit words. All output storage is owned by the caller. The dispatcher should check a null pointer, negative capacity, and insufficient capacity **before writing anything**. Caller-supplied pointers must designate accessible storage; the extension cannot authenticate arbitrary machine addresses.

| Opcode | Operation | Version-1 output | Ordinary successful return |
| ---: | --- | --- | ---: |
| **0** | `QUERY` | Standard six-word, shared Runtime Extensions capability descriptor | 6 |
| **1** | `STCK` | Raw 64-bit TOD value as two words, followed by the instruction condition code | 3 |
| **2** | `TIME` | Raw fullword contents of MVS `TIME DEC` R0 (time) and R1 (date), without interpretation | 2 |

These are the **only** initial operations. They are direct calls; no BCPL wrappers or library procedures are in scope.

### QUERY — opcode 0

Follow the existing shared QUERY version-1 contract, not a BCPLTIME-specific replacement:

- `TIMESVC(0, 0, 0)` returns 6 without writing storage.
- With a valid six-word output vector, return descriptor format 1, package API version 1.0, required length 6, supported-opcode bitmap **3** (opcodes 1 and 2), and initially no additional capability flags.
- Preserve the common standard errors: `-1` insufficient capacity; `-2` unknown opcode; `-3` invalid arguments. Never write a partial QUERY descriptor.

### STCK — opcode 1

Execute the problem-state System/370 `STCK` instruction directly, preserving the resulting 64-bit value without calendar or arithmetic conversion. Return the high-order 32 bits in `output_vector!0`, low-order 32 bits in `output_vector!1`, and the **STCK condition code (0–3)** in `output_vector!2`.

The TOD value is treated as a **64-bit unsigned bit pattern** with the conventional epoch of 00:00:00 GMT, 1 January 1900. Bit positions and counter units must be documented against the System/370 Principles of Operation. Do not treat the two words as a signed 64-bit BCPL integer or claim that reading the value guarantees a valid or monotonic clock.

The hardware condition code is essential: CC=0 indicates a set clock; CC=1 indicates a running but not-set clock; CC=2 indicates a clock error; CC=3 indicates an unusable/not-operational condition under the applicable period architecture. Preserve the raw words even when the clock condition makes them unsuitable for time measurement; the BCPL caller decides whether to use them. The wrapper-free dispatcher return counts words written; it is **not** a replacement for the hardware condition code.

### TIME — opcode 2

Invoke the **MVS 3.8** `TIME DEC` macro. Copy the returned 32-bit R0 time word and 32-bit R1 date word into `output_vector!0` and `output_vector!1`, in that order. Do not convert the values into `YYYYMMDD`, ISO text, Unix time, seconds, or BCPL strings.

The exact MVS 3.8 `TIME DEC` bit layout, date/century convention, time precision, available return diagnostics, and macro register effects must be checked against period documentation and the **first actual MVS invocation**. Later z/OS or VM definitions must not silently substitute for this release's behavior. Document any observed Hercules/TK5 operator-clock discrepancies. The two returned words constitute one `TIME` invocation; they are not guaranteed to be simultaneous with a separate STCK read.

### Return/error policy

The positive returns above are word counts, following the BCPLDEMO teaching convention. Use only the shared `-1`/`-2`/`-3` argument/opcode errors initially. Do not invent extra error statuses without observed need and owner review. A successful raw hardware read does not assert that the timestamp represents valid wall time; inspect the returned STCK condition code.

## 3. Packaging and implementation boundaries

- Implement **one independently linkable package** named `BCPLTIME`, preferably using the R.5 **single-object/two-CSECT** BCPLDEMO pattern: a BCEX v1 descriptor with one exported dispatcher at **G!201**, and assembler dispatch code. No initializer, finalizer, dynamic allocation, or private persistent state is required.
- Reuse the accepted BCEX/BCRG v1 registration and the MVS-native `BCXSEL`/`BCXREQ`/`BCXCAT` known-package selection arrangement. A future accepted `BCXCAT` entry may select `BCPLTIME`; adding it is **not** authorization to write any resident MVS dataset.
- Provide a minimal BCPL public declaration header (GLOBAL and opcode constants), which is **not** a wrapper library. As with BCPLDEMO, an explicit GLOBAL in the initial test caller is acceptable if the bootstrap compilation path cannot consume the header directly.
- Preserve existing `BCPLMAIN`, `BCPLRGS`, `BCPLIO`, historical `BLIB`, compiler sources, and BCEX/BCRG contracts. Do not change the native compiler or the interpreter-hosted demoted Cambridge compiler.
- Retain GitHub `main` as the official source. Use temporary object datasets for development; permanent `EXT_*`, `BOOT_OBJ`, or `BOOT_DEVOBJ` writes require separate explicit owner authorization.

## 4. Explicit exclusions

No calendar arithmetic or Gregorian date validation; leap years; weekday, ordinal-date, or month/day conversion; text formatting/parsing; TOD arithmetic; elapsed-time library; BCPL wrapper procedures; automatic date/time data types; storage allocation; MVS `STIMER`/`TTIMER`; wait, alarm, interrupt, timeout, periodic callback, or timer exit; MVS clock setting; privileged `STCKC` or `STPT`; CPU accounting APIs; dynamic loading; or portability emulation for System/360.

Portable BCPL Standard Library code may eventually perform calendar and elapsed-time calculations, but is a **separate, unapproved future effort**, not a BCPLTIME exit condition.

## 5. Accelerated execution and minimal acceptance

### Active march structure — owner authorization, 24 October 2026

The owner has explicitly authorized a **new, accelerated two-march structure** for **Milestone BCPLTIME**. These are the current designations. The 15 October proposal's T.0–T.4 names and scopes remain preserved in Section 6 **as historical material only**; numbering is consciously reassigned by this new decision, not silently edited.

| March | Current status | Work | Exit gate |
| --- | --- | --- | --- |
| **T.0 — Descriptor, Dispatcher, and Native Execution** | **CLOSED — 24 October 2026** | Write actual single-object BCPLTIME BCEX descriptor, dispatcher opcodes 0/1/2, public declaration header, and one direct native BCPL caller. Debug the production-intended assembler against IFOX/IEWL/GO rather than running a preliminary probe campaign. | Actual MVS 3.8J IFOX + IEWL + GO PASS, G!201 registered via BCEX/BCRG v1, QUERY/STCK/TIME and basic error/no-partial-write behavior confirmed, observed clock data and any OS-specific caveats recorded. |
| **T.1 — Packaging and Acceptance** | **IN PROGRESS — 24 October 2026** | Add approved known-package selection/catalog and safe installation path, verify absence/presence on link, run the installed-mode tests and existing native production panel, document rebuild and package usage. | Owner reviews JES/IEWL evidence, regression and installation receipts, and explicitly accepts the optional extension. No permanent dataset writes without separate authorization. |

**Formal owner decision (24 October 2026): CLOSE T.0; OPEN T.1.**
The [T.0 owner closure](bcpltime-t0-closure-20261024.md) records
JOB 5436: five IFOX assemblies, IEWL and GO all RC=0000; IEWL MAP
PASS; raw STCK/TIME output and `BCPLTIME T0 PASS` observed. The
prior S0C4 in JOB 5434 was resolved by preserving permanent R0/R1
across MVS `TIME DEC`. The record check matched the expected logical
output but independently verifying JES DD attribution remains open.

**T.1 design gate:** Before any permanent deployment, review the
BCXCAT catalog changes, object/macro member names, installation and
rollback procedure, and acceptance matrix with the owner. Starting
T.1 does **not** authorize modifications of resident MVS PDSes.
Preserve BCEX/BCRG v1, BCPLDEMO, and accepted Runtime/Base Library
objects. Temporary T.0 linkage is still a valid development path.

**T.1 numbered regression candidates:** New cases **159–162** are
specified for BCPLTIME alone and for BCPLDEMO+BCPLTIME selection,
reverse-order inclusion, and requirement-upgrade/deduplication.
Cases 00–158 remain unchanged, including the accepted R.5 no-extension
and BCPLDEMO-alone coverage. See the
[T.1 regression design](../bootstrap-toolchain/extensions/bcpltime/T1-REGRESSION.md).
**Operator-reported source-mode acceptance:** All four native cases
159–162 PASS, 0 FAIL, 0 SKIP (24 October 2026); 15 T.1 offline tests
also PASS. The console excerpt did not expose individual JES payload
job numbers. The approved [T.1 installation design](bcpltime-t1-installation-design.md)
now specifies EXT_ASM(BCPLTIME), EXT_SOURCE(TIMEHDR), EXT_OBJ(BCPLTIME),
a revised production BCXCAT, and BOOT_JCL(T1TINST). These are Git
source changes, not resident PDS installation. Installed-mode tests,
full regression and owner acceptance remain open. **This design approval
does not authorize permanent MVS dataset writes.**

**T.0 began with implementation, not reconnaissance.** The first MVS job should assemble the BCPLTIME candidate and exercise the actual dispatcher from the native BCPL caller using temporary datasets. A working local source tree is not equivalent to an accepted MVS build. No march closes automatically or without owner review.

**Start with actual source, not preliminary probes.** Adapt the accepted BCPLDEMO descriptor/dispatcher and package-selection method to implement the three opcodes. The first test should be a single integrated IFOX/IEWL/native BCPL job that exercises QUERY (including size and invalid-capacity checks), STCK (raw words plus condition code), and TIME (raw R0/R1 words). Debug the same production-intended dispatcher from JES and assembler evidence, rather than constructing many disposable experiments.

Minimum acceptance:

1. **Real integration:** IFOX, IEWL, and native BCPL GO succeed under MVS 3.8J; correct G!201 registration and effective IEWL map are observed. A selected BCPLTIME package must be genuinely optional.
2. **Three-opcode contract:** QUERY returns the shared descriptor; STCK returns two unchanged words and its CC; TIME returns the two macro result words. Null, undersized, and unsupported-opcode calls return the documented errors with no partial writes.
3. **Reproducibility:** Build the package from Git-controlled source and document the minimal installation/link instructions. No permanent MVS dataset change without owner authorization.
4. **Regression:** Run the existing native production regression panel at the acceptance gate and preserve its known outcomes. Record real JOB IDs, step return codes, output observations, and any limitations. Do **not** require a complete new clean-room rebuild as a prerequisite to the first implementation or each correction.

Document only decisions, failures, or observations that materially change the public contract. No separate broad reconnaissance campaign, multi-job probe matrix, or wrapper/library development is required.

## 6. Historical record: superseded 15 October 2026 proposal

The original repository file, titled **Milestone Date and Time Services**, was proposed on **15 October 2026**, marked **Proposed, not started**, and outlined a considerably larger optional service: Gregorian calendar arithmetic, validation, leap years, ordinal dates, weekdays, addition/difference of days, ISO presentation and parsing, plus MVS `TIME` and optional clock/elapsed-time functions.

Its former provisional API included `DATENOW`, `DATEVALID`, `DATELEAP`, `DATEORDINAL`, `DATEADD`, `DATEDIFF`, `DATEWEEKDAY`, `TIMEVALID`, `TIMESECONDS`, `DATEFORMAT`, `DATEPARSE`, `CLOCKREAD`, and `CLOCKELAPSED`. These names were concepts, **not implemented or accepted exports**.

The original **proposed, unstarted** march outline was:

| Historical march | Original scope | Current disposition |
| --- | --- | --- |
| **T.0 — Evidence and contract** | MVS interfaces, ABI, century/zone policy | Historical proposal; not activated here |
| **T.1 — Pure calendar core** | Leap years, validation, weekday, date arithmetic | Superseded by minimal scope |
| **T.2 — MVS clock adapter** | Assembler `TIME` service and date extraction | Superseded by raw `STCK`/`TIME` dispatcher |
| **T.3 — Presentation and optional timing** | Formatting/parsing and elapsed timing | Superseded; excluded |
| **T.4 — Packaging and acceptance** | Library demonstration, registration, regression, release | Superseded by accelerated single acceptance gate |

The historical T.0–T.4 entries above are **superseded proposals**, not active gates. On 24 October 2026, the owner explicitly authorized the replacement two-march T.0/T.1 structure in Section 5. The **reuse of T.0 and T.1 is deliberate and documented**, not an alteration of historical evidence. No other marches are established.

The original full proposal remains permanently recoverable through Git history, at the exact pre-revision commit:

[`fc7f12d3a541f22c07528ac7c7161d3e18eafafa:packaging/milestone-date-and-time-services.md`](https://github.com/cbmira01/BCPL-for-MVS/blob/fc7f12d3a541f22c07528ac7c7161d3e18eafafa/packaging/milestone-date-and-time-services.md).

Keeping the existing file path preserves current repository links while the **title and current scope** become *Milestone BCPLTIME*. No evidence from the original plan is erased; it remains explicitly distinguishable from the newly approved direction.

## 7. References and authority

- [Runtime Extensions milestone and R.0–R.5 closure records](milestone-runtime-extensions.md): accepted BCEX/BCRG v1, optional selection, and registration.
- [BCPLDEMO reference implementation](../bootstrap-toolchain/extensions/bcpldemo/README.md): reusable single-object package and dispatcher model.
- [Global Number Registry](global-number-registry.md): reserved G!201, proposed `TIMESVC` spelling.
- [Runtime and Library Nomenclature](runtime-and-library-nomenclature.md): System Extension versus Standard Library distinction.
- IBM *System/370 Principles of Operation*: `STCK` and condition-code semantics.
- Period IBM OS/VS2 MVS *Supervisor Services and Macro Instructions*: actual `TIME` macro layout, register effects, and operating-system behavior.

**Source of truth:** GitHub `main` after an explicitly approved commit. A proposed design and a local document draft do not establish verified MVS behavior or authorize installation.
