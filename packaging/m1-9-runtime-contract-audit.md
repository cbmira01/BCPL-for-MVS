# M1.9 — Runtime Contract and Observability Audit

Status: **ACTIVE — Gate A accepted with explicitly bounded object-level evidence; Gate B in progress.** Opened 13 October 2026 after acceptance and closure of [M1.8](m1-8-reproducible-runtime.md).

## Objective

Produce a source-grounded, versioned **Runtime Contract Specification** for the five-component reconstructed BCPL runtime: BCPLMAIN, BCPLMEM, BCPLBYTE, BCPLAPT and BLIB. Identify existing behavior, interface exposure, historical compatibility and executable evidence. Establish an explicit observability contract for programmers and MVS operators.

**Audit first.** No production OBJ promotion, SOURCE/JCL synchronization, resident build, compiler modification, or runtime semantic change is authorized by opening M1.9. Git remains implementation authority; MVS is the build and execution target. DEVOBJ is the development/candidate object library; OBJ is the stable ordinary-application library, promoted only on separate authorization.

## Gates

| Gate | Scope | Acceptance evidence |
| --- | --- | --- |
| **A — Runtime interface inventory** | Five modules; exported entry points, global-vector slots, linkage conventions, dependencies, and registration | Source-anchored interface matrix, unknowns explicitly identified |
| **B — Storage and stack contracts** | GETVEC/FREEVEC, APTOVEC, stack frames, limits, ownership, cleanup | Implementation and boundary contracts; matching regressions or gaps |
| **C — I/O and termination contracts** | Stream naming, selected streams, record buffering, FINISH/STOP, completion codes, abnormal exit | Source-anchored I/O and termination map |
| **D — Observability inventory and exposure** | D1 mechanisms and owning modules; D2 BCPL/operator invocation and output; D3 tests and gaps | Observability contract with interface, trigger, data source, output, failure behavior, evidence |
| **E — Historical compatibility** | Cambridge BCPLMAIN/BLIB recovered evidence vs implemented semantics | Difference register: matched, intentional MVS adaptation, omission, uncertain, or defect |
| **F — Verification and acceptance** | Complete contract/evidence traceability, focused tests only where needed, document unresolved gaps | Accepted specification, coverage matrix, disposition register and milestone close |

## Gate A — preliminary source-grounded inventory

Source inspected directly at M1.9 opening: `asm/bcplmain.asm`, `asm/bcplmem.asm`, `asm/bcplbyte.asm`, `asm/bcplapt.asm`, and the M1.8 build/provenance record. **This is a preliminary inventory, not Gate A acceptance**; BLIB exported globals and all register preservation rules remain to be fully enumerated.

| Object/CSECT | Externally visible symbols or interface | Observed source behavior / audit question |
| --- | --- | --- |
| BCPLMAIN | CSECT BCPLMAIN; `ENTRY STKOVFL`; `EXTRN BLIB, GETVEC, FREEVEC, MEMDRAIN, MEMBIND` | MVS entry and saved caller context; allocates global/stack region; imports generated application and BLIB global registrations; publishes selected service slots; owns I/O, termination and stack failure path. |
| BCPLMEM | `ENTRY GETVEC,FREEVEC,MEMDRAIN,MEMBIND,MEMSTAT` | Owns vector allocation/deallocation, private teardown, G6!48-list binding and allocator statistics interface. Classify public BCPL services vs private assembler ABI. |
| BCPLBYTE | `ENTRY GETBYTE,PUTBYTE` | Byte primitives; BCPL argument/return register convention documented in source; G85/G86 slots published by BCPLMAIN. |
| BCPLAPT | `ENTRY APTOVEC,APLIMIT`, `EXTRN STKOVFL` | G40 temporary-vector call behavior and shared stack-overflow path; establish whether APLIMIT is a public symbol, runtime configuration, or purely internal state. |
| BLIB | Compiled generated BCPL object, imported via module trailer/global registration rather than assembler `ENTRY` list | Generated from historical `richards-bcpltape/bcplib/bcpl/blib` via `make-demoted.py`. Enumerate actual exported globals from source, not just historical names. |

### Confirmed BCPLMAIN publication paths requiring formal contract

- Main module trailer registration populates the global vector; BCPLMAIN then explicitly imports the separately linked BLIB module's global trailer (source around lines 687–719).
- G6 publishes a BCPL word pointer to save-area-compatible state, with modeled G6!29 load-list head and G6!48 allocator-list head. The details must be assessed for historical compatibility.
- G52/G53 main-program bounds and G54/G55 allocated stack extent are published at byte offsets 208/212 and 216/220. The safe frame limit is **not identical** to published G55: safe limit is 16,384 words from the stack base, with reserved clearance.
- G11, G12, G13, G14, G15, G16, G17, G33, G39, G40, G41, G42, G46, G47, G85, G86, G87, G88 and provisional G150 are among explicit service-publication paths observed around lines 752–810. This list is **not exhaustive** and must be reconciled to LIBHDR.
- G76 is imported from BLIB when present; BCPLMAIN installs a fallback only while the G76 slot retains the historical unset sentinel.

### Initial observability inventory, not yet a compatibility claim

| Mechanism | Source evidence | Exposure question for Gate D |
| --- | --- | --- |
| Stack markers and high-water measurement | BCPLMAIN initializes alternating markers across 16,384 usable stack words and installs guard/marker metadata (around lines 616–657); historical BLIB implements STACKHWM | Verify current BLIB export and whether G56 STACKHWM operates against published G54/G55 and sentinel layout, then classify result semantics. |
| Stack exhaustion | BCPLMAIN STKIMPL checks frames against STKLIM; STKOVFL writes a diagnostic to the output buffer and enters termination (around lines 1011–1047); BCPLAPT branches to STKOVFL | Establish exact SYSOUT destination, return status, and whether backtrace or map occurs. |
| Heap accounting | BCPLMEM exports MEMSTAT and controls GETVEC/FREEVEC/MEMDRAIN; BCPLMAIN connects MEMBIND to G6!48 | Determine MEMSTAT contract, whether it is BCPL callable, what values it exposes and which test covers it. |
| Debug output | BCPLMAIN explicitly publishes DEBUGINT at G150 and includes a decimal output routine | Determine if documented BCPL service or provisional developer hook; output record behavior. |
| Historical post-mortem | Historical BLIB includes ABORT, BACKTRACE, MAPSTORE, WRITEARG; reconstructed BLIB object may contain these | Verify installed global addresses, actual runtime prerequisites (load list, SAVEAREA fields, program bounds), and executable behavior **before** advertising programmer-visible support. |

## Existing acceptance baseline

M1.8 Gate F: `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ tools/run-native-regression` resulted in **123 PASS, 0 FAIL, 1 expected SKIP (083 source-only instrumentation), TOTAL 124**. This is broad regression baseline evidence, not individual proof of every contract. Keep this baseline stable during audit.

## Immediate Gate A work

1. Enumerate the exact global-vector definitions in the tracked LIBHDR, and compare source-side registration and BLIB exports. Distinguish published and historical-only slots.
2. Extract actual BCPLMAIN, BCPLMEM, BCPLBYTE, BCPLAPT calling conventions and preserved/clobbered registers; classify assembler-private and BCPL-public entry points.
3. Map each service to existing regression cases and flag missing direct coverage.
4. Record unresolved differences, then accept Gate A only after a verified complete matrix. Gate B begins after Gate A closure.

## Non-goals and controls

No broad regression replay, change to resident MVS datasets, production library promotion, historical capability claims based solely on source presence, or speculative implementation while gates A–E are gathering evidence. Gate F may authorize focused new probes only with a clearly identified evidence gap.

## Gate A — source-entry and allocator ABI detail (13 October 2026)

This pass read the entire four canonical assembler modules and historical
`richards-bcpltape/bcplib/bcpl/blib` directly from Git. Assertions below are
**source observations**, not claims about the register behavior of every
linked application. The generated BLIB source's full export trailer and
resident LIBHDR have not yet been extracted; Gate A remains open.

### Externally linkable assembler symbols and their audiences

| Source | `ENTRY` symbols | Intended audience | Observed contract |
| --- | --- | --- | --- |
| `asm/bcplmain.asm` | `STKOVFL` (plus BCPLMAIN CSECT entry) | Native startup, shared abnormal-stack path | Receives generated module base via R15; `STKOVFL` moves message to buffered output and branches to termination. |
| `asm/bcplmem.asm` | `GETVEC`, `FREEVEC` | BCPL G87/G88 | GETVEC N in R7, returns BCPL word pointer in R7 or 0 on failure. FREEVEC accepts word pointer R7; zero or unknown pointer is no-op. |
| `asm/bcplmem.asm` | `MEMDRAIN`, `MEMBIND`, `MEMSTAT` | **Private assembler API**, not automatically BCPL callable | MEMDRAIN uses R14 linkage and frees outstanding allocations; MEMBIND accepts R1=address of published G6!48 list-head slot (zero to unbind); MEMSTAT writes four fullwords to R1 target; R10 clobbered. |
| `asm/bcplbyte.asm` | `GETBYTE`, `PUTBYTE` | BCPL G85/G86 | R7 word pointer, R8 byte offset, R9 byte value for PUTBYTE; GETBYTE returns R7 low-byte value; restores R4 via current frame at R5 and returns through R6. |
| `asm/bcplapt.asm` | `APTOVEC`, `APLIMIT` | G40 service; APLIMIT native linker symbol | R7 function, R8 vector size; temporary vector is passed to the function. APLIMIT is an exported data symbol used by the bounds check, **not proof of a BCPL function**. Shared failure path via external `STKOVFL`. |

`BCPLMEM` source explicitly labels itself a static singleton allocator
and non-reentrant. Its GETVEC allocation stores a private 12-byte control
header (BCPL word pointer, allocated byte length, next record byte
pointer) and keeps the list head in `VECLIST`, published through
`MEMBIND` to the G6!48 slot. The requested payload is `N+1`
words, and the byte allocation additionally includes 12 header bytes.
`MEMDRAIN` detaches the list head before `FREEMAIN` and decrements
current allocation counters. Peak counters are not reset on drain.

### Private observability: MEMSTAT is *not* yet a BCPL service

`MEMSTAT` has a concrete native snapshot ABI: on entry **R1** is the
address of four writable fullwords; on return they contain, in order,
`MEMCURN` (currently live vector count), `MEMPEAKN` (peak live
vector count), `MEMCURB` (current allocated bytes, including private
headers), and `MEMPEAKB` (peak allocated bytes). It preserves the
R14 return address, overwrites R14 temporarily, and clobbers R10 on
entry. It is explicitly intended for a quiescent singleton context.

There is **no demonstrated direct global-vector publication of
MEMSTAT** in `BCPLMAIN`'s explicit installation block (which
publishes GETVEC and FREEVEC). Do not document it as a callable
BCPL-language service or an operator command until an exposure
mechanism is established. This is a concrete Gate D exposure gap,
not an implementation absence.

### BLIB historical entry names versus actual export registration

The historical BLIB source contains procedure definitions including
WRITES, UNPACKSTRING, PACKSTRING, WRITEF, ABORT, ERRORMESSAGE,
PRINTWIDTH, STACKHWM, MAPSTORE, INPROGRAM, VALIDPOINTER, BACKTRACE,
WRITEARG, WRITED, WRITEN, NEWLINE, NEWPAGE, READN, WRITEOCT,
WRITEHEX, WRITEO and WRITEX. Those names establish source-level
definitions but **do not alone establish the current exported
global slots, executable code paths or compatibility**. The installed
object is made by compiling the mechanically demoted derivative;
its actual compiler-generated registration trailer and LIBHDR
mapping still need to be correlated.

### Audit cautions found in source headers

`asm/bcplbyte.asm` still says it is not used in normal regression
linkage, and `asm/bcplapt.asm` calls object-library acceptance
pending. The completed M1.8 DEVOBJ rebuild and regression show
both components are in the five-member accepted candidate library.
Treat those historical header comments as **stale wording requiring
documentation cleanup**, not as stronger evidence than the tested
linkage. No semantic source edit is justified by this observation.

### Outstanding Gate A evidence

1. **Resolved:** the tracked authoritative input is `richards-bcpltape/sys3/bcpl/libhdr`, mapped to SOURCE(LIBHDR) in `config/dspal.yaml`. Reconcile its full G-number/name table with installed native and BLIB services.
2. Enumerate actual exported BLIB globals and distinguish imported
   module trailer records from installed native service entries.
3. Cross-check assembler calling conventions (including register
   preservation, error paths and inter-module storage assumptions)
   with focused regression coverage before closing Gate A.
4. Identify which of MEMSTAT, STACKHWM, DEBUGINT and post-mortem
   routines have verified BCPL/operator invocation paths. Full
   exposure evaluation is Gate D.

## Gate A — authoritative LIBHDR and runtime registration crosswalk (13 October 2026)

The mapping has been resolved in Git without MVS operation:
`config/dspal.yaml` maps `SOURCE(LIBHDR)` directly to
`richards-bcpltape/sys3/bcpl/libhdr`. The tracked file contains a
single GLOBAL declaration for G1–G99 (with gaps) and defines
`FIRSTFREEGLOBAL=150`. This is the **compiler-visible name/slot
contract**, not evidence that each named facility has been installed.

### Runtime-owned or runtime-installed slots

The table below is derived by matching LIBHDR name:global declarations
to the explicit `BCPLMAIN` installation code (source lines 704–810).
A slot's presence in LIBHDR alone is **not** marked implemented.

| G slot(s) | LIBHDR name | Publication evidence | Status |
| --- | --- | --- | --- |
| 1 | START | Generated application trailer is imported; G1 checked for sentinel | Registered by application; not hardwired runtime routine |
| 6 | SAVEAREA | `ST 1,24(12)` | Published BCPL word pointer to save-area-compatible area |
| 11,12 | SELECTINPUT, SELECTOUTPUT | BCPLMAIN writes offsets 44,48 | Explicit native service entries |
| 13–17 | RDCH, WRCH, UNRDCH, INPUT, OUTPUT | Offsets 52,56,60,64,68 | Explicit native service entries |
| 30 | STOP | Offset 120 | Explicit native service entry |
| 33 | WRAPOUTPUT | Offset 132 | Explicit native service entry |
| 39 | FINDPARM | Offset 156 | Explicit native service entry |
| 40 | APTOVEC | Offset 160 | Explicit native service entry; separately linkable BCPLAPT also exists; distinguish call sites |
| 41–42 | FINDOUTPUT, FINDINPUT | Offsets 164,168 | Explicit native service entries |
| 46–47 | ENDREAD, ENDWRITE | Offsets 184,188 | Explicit native service entries |
| 52–53 | LOADPOINT, ENDPOINT | Offsets 208,212 | Published program extent data, not functions |
| 54–55 | STACKBASE, STACKEND | Offsets 216,220 | Published stack extent data, not functions |
| 76 | WRITEF | BLIB trailer import preferred; native fallback at 304 only if unset | Conditional fallback; ownership may be BLIB |
| 85–86 | GETBYTE, PUTBYTE | Offsets 340,344 | Native assembler symbols from BCPLBYTE |
| 87–88 | GETVEC, FREEVEC | Offsets 348,352 | Native assembler symbols from BCPLMEM |
| 150 | Not named in historical LIBHDR; first free global | Offset 600 | Native provisional DEBUGINT, an extension |

BCPLMAIN additionally imports all recognized exported entries from
the compiled **BLIB registration trailer**, so the table is **not**
an exhaustive installed-global table. In particular, a historical
BLIB procedure with a LIBHDR name (e.g. STACKHWM G56) can be present
through trailer import even without an explicit `ST` in this table.
The precise compiler-emitted trailer and coverage evidence remain
necessary for complete Gate A acceptance.

### LIBHDR observability interfaces and classifications to verify

| G slot | Name | Audit classification |
| --- | --- | --- |
| 2 | SETPM | Historical interface; check whether available to native applications |
| 3 | ABORT | Historical BLIB source definition; operational post-mortem unverified |
| 4 | BACKTRACE | Historical BLIB source definition; native frame-walk compatibility unverified |
| 5 | ERRORMESSAGE | Historical BLIB source definition; stream fallback compatibility unverified |
| 31 | LEVEL | Historical service needed by BACKTRACE; verify native provider |
| 52–55 | LOADPOINT, ENDPOINT, STACKBASE, STACKEND | Explicitly published runtime data |
| 56 | STACKHWM | Historical BLIB definition; compare to native stack marker layout |
| 58–59 | INPROGRAM, VALIDPOINTER | Historical BLIB definitions; assess savearea/load-list prerequisites |
| 69 | WRITEARG | Historical BLIB formatter; pointer / function-tag interpretation unverified |
| 78 | MAPSTORE | Historical BLIB definition; structural compatibility unverified |
| 79 | USERPOSTMORTEM | Historical extension hook; verify initialization and invocation |
| 82–84 | SETBREAK, ISBREAK, ERRORRESET | Historical interface only, until native implementation evidence |
| 150 | DEBUGINT (extension) | Explicit native installation; BCPL caller usability and output contract unverified |
| — | MEMSTAT | Assembler-private snapshot ABI, **no LIBHDR slot or explicit native global publication** |

### Historical LIBHDR anomaly — do not silently amend

The checked-in historical LIBHDR assigns both
`OPENBLOCKFILE:94` and `UPDATEBLOCKFILE:94`. This duplicate is
present in **the source itself**; audit the historical semantics and
whether both names intentionally alias the same service before
changing any compiler-facing header. Other gaps such as G50 and
G57 are not automatically evidence of implementation defects.

### Gate A verification boundary

We now have the correct tracked LIBHDR mapping and precise **explicit
native-publication** evidence. This does **not yet establish**:
all compiler-emitted BLIB trailer registrations, comprehensive
MVS/BCPL register preservation for each native entry, or executable
coverage for each LIBHDR slot. Those remain explicit Gate A tasks;
they are not grounds for broad runtime changes.

## Gate A — BLIB definition-to-global crosswalk and regression trace (13 October 2026)

The tracked historical `richards-bcpltape/bcplib/bcpl/blib` was
compared to the tracked compiler header
`richards-bcpltape/sys3/bcpl/libhdr` and the six-stage resident
`jcl/build-dev-blib.jcl` pipeline. The latter compiles
`SOURCE(BLIB)` under `SOURCE(LIBHDR)`, repairs the two known
CG370 cards, assembles its independent CSECT and installs
`DEVOBJ(BLIB)`. All steps were RC=0000 during M1.8 Gate C.
**The source-level mapping below is not a decoded object trailer**;
it enumerates the named top-level definitions and their LIBHDR
slots, to be checked against generated trailer evidence if needed.

| BLIB top-level definition | LIBHDR slot | Existing executable evidence (scope) |
| --- | --- | --- |
| ABORT | G3 | Historical reporting path only; no direct post-mortem execution proof |
| BACKTRACE | G4 | No native call-chain validation identified |
| ERRORMESSAGE | G5 | No dedicated fault-stream validation identified |
| STACKHWM | G56 | 120 tests initialized-stack in-range high-water return |
| INPROGRAM, VALIDPOINTER | G58, G59 | 121 empty lists; 122 descriptor/list traversal; 123 automatic G6!48 allocator-list publication |
| WRITES | G60 | 065 historical WRITES; 067/069 separately linked BLIB |
| WRITEN | G62 | 066 historical WRITEN; 067/069 separately linked BLIB |
| NEWLINE, NEWPAGE | G63, G64 | BLIB formatting/link paths; dedicated NEWPAGE semantic proof not yet mapped |
| WRITEO | G65 | 074 independent BLIB object |
| PACKSTRING, UNPACKSTRING | G66, G67 | 071 in-place pack; 070 unpack |
| WRITED | G68 | 072 field-width behavior |
| WRITEARG | G69 | Used by historical reporting; independent format/pointer classification proof not mapped |
| READN | G70 | No direct focused input parsing evidence identified yet |
| WRITEX, WRITEHEX | G74, G75 | 073 width path; further coverage mapping needed |
| WRITEF | G76 | 068 formatted output, 075 mixed arguments, 076 diagnostics, 081 nested argument cursor |
| WRITEOCT | G77 | 058 and 064 format cases; independent direct-entry coverage to check |
| MAPSTORE | G78 | No complete native post-mortem map validation identified |
| PRINTWIDTH | **No LIBHDR global slot** | Top-level helper name does not establish a public BCPL global |

The name `PRINTWIDTH` appears as a top-level BLIB procedure but
not in the tracked LIBHDR; an actual compiler export cannot be
inferred from procedure visibility alone. Likewise, the header's
G79 USERPOSTMORTEM is **not defined by this BLIB source**.
Its slot must not be equated with an implemented callback.

### Why this is a meaningful exposure distinction

- **Named public slot:** LIBHDR assigns a global number and compiled
  code may reference it; runtime installation still requires an actual
  registered module or explicit native publisher.
- **Defined historical routine:** BLIB source has an implementation,
  but its successful translation and link do not establish the
  correctness of all control/data prerequisites.
- **Proven focused behavior:** individual regressions exercise only
  the specifically asserted path. For example, test 120 confirms
  `STACKHWM` returns an in-range word address, *not* precise
  usage accounting, and test 121 establishes only empty-list
  behavior for pointer predicates.
- **Private native entry:** `MEMSTAT` is exported through a native
  assembler symbol with a defined R1 snapshot ABI but has no
  LIBHDR assignment or direct published global slot.

### Traceability caveat — historical README status text

Some regression READMEs retain older staging instructions (e.g.
069 describes an earlier planned failure; 121–123 warn that installed
PDS mode cannot yet work; 082 says TK5 execution pending).
These are **historical checkpoint narratives**, not a current status
override: M1.8's 13 October 2026 full DEVOBJ panel reported
123 PASS / 0 FAIL / 1 expected SKIP, including cases
069, 082, 120, 121, 122 and 123. Use dated actual execution
evidence rather than assuming the first paragraph of an older
test README represents the current runtime.

### Remaining Gate A verification

The current inventory identifies header slots, historical BLIB
definitions and most representative tests. To treat the crosswalk
as a complete *actual exports* ledger, recover the compiler-produced
global-registration trailer (from retained CG370 assembly, a
non-mutating linkage report, or a deliberately isolated probe).
Also reconcile assembler-private register clobbers and callback
boundaries. No MVS deployment or production OBJ operation is
authorized by this audit.

## Gate A — linkage reconstruction and remaining evidence boundary (13 October 2026)

Further source inspection confirmed that the canonical BCPLMAIN
`GIDONE/BLIMP` sequence locates the BLIB module end using the
halfword offset at BLIB+10, then walks backward through eight-byte
(global byte offset, relocated entry address) pairs until a zero
entry address. Each nonzero pair is installed into the global
vector after validating its offset. The application uses the same
general trailer-registration mechanism. This proves **how**
compiled BLIB exports become callable in the current runtime, without
decoding every individual export pair in the specific assembled deck.

Evidence from regression 069's recorded historical three-CSECT
linker map and successful `BLIB 42` GO validates the independent
BLIB registration model. The later authoritative M1.8 DEVOBJ
full-suite acceptance includes 069, 067–081 and 120–123.
Older README statuses described intermediate developmental checkpoints
and must not be mistaken for 13 October 2026 acceptance status.

### Register / linkage boundary matrix (source observed)

| Interface | Linkage / input | Return and controls | Scope |
| --- | --- | --- | --- |
| Generated module → BCPLMAIN | R15 contains compiled-module base; entry prefix transfers to BCPLMAIN | BCPLMAIN builds MVS R13 save area, G vector, BCPL stack and system vector; dispatches START | Native startup, not an ordinary BCPL callable function |
| BCPL call to GETVEC / FREEVEC | R5 current frame, R6 return, R7 first argument; R10 used as BCPLMEM local base | GETVEC returns R7 pointer or 0; FREEVEC returns through R6 and restores R4 from caller frame | G87/G88 |
| BCPL call to GETBYTE / PUTBYTE | R7 pointer, R8 byte offset, R9 byte argument for PUTBYTE | GETBYTE returns byte in R7; both restore R4 from 0(R5) and branch via R6 | G85/G86 |
| BCPL call to APTOVEC | R7 target function, R8 number of words; R15 next frame, R5 current frame | Constructs temporary vector and invokes R7 function; uses R6 for nested BCPL return; overflow branches STKOVFL | G40; separate APLIMIT symbol is data |
| BCPLMAIN → MEMBIND | R1 points at writable G6!48 slot, R14 supplies native return | Registers live-list publication; R1=0 unbinds | Private assembler ABI |
| BCPLMAIN → MEMDRAIN | R14 native return | Frees outstanding vector records and refreshes published head | Private assembler ABI |
| Native private → MEMSTAT | R1 points to 16 writable bytes, R14 native return | Four snapshot fullwords written, R10 clobbered; no BCPL global exposure established | Private assembler ABI |
| BCPL generated code → system vector | R11 supplies SYSV base; branch slots at relative offsets 0,20,40,60,80 | Return, count, finish, checked-entry and checked-count hooks. COUNT and checked-count are labeled stubs in current source | Machine-code system interface, not LIBHDR globals |

**Important limits:** these rows summarize source-visible conventions,
not a complete exhaustive clobber audit for every BCPLMAIN stream
service. The byte service's source header saying it is not used in
normal regression linkage and BCPLAPT's pending-acceptance comment
are stale relative to M1.8 build/test evidence.

### Gate A decision / evidence not yet possessed

- **Proven:** authoritative LIBHDR location, native entry symbols,
  native explicit global publishers, BLIB source-defined global names,
  compiler trailer import mechanism, and focused acceptance of
  representative actual BLIB object services.
- **Still not proven by an explicit artifact:** complete set of
  assembled BLIB trailer entries and their individual addresses,
  and exhaustive per-entry clobber matrices for all native services.
  No retained generated BLIB assembler listing was identified in
  the inspected tracked sources. A new resident compilation solely
  to extract it is **not** being triggered during this source-only
  audit.

Keep Gate A **open** until the complete actual BLIB export-trailer
ledger can be reconciled, or explicitly adopt the narrower
source/header/registration-and-regression proof as its acceptance
criterion. Do not silently equate names found in a historical
source file with directly observed object exports.

## Gate A — complete source-level BLIB export candidate ledger (13 October 2026)

A direct, systematic comparison of the tracked historical
`richards-bcpltape/bcplib/bcpl/blib` with the actual configured
`SOURCE(LIBHDR)` input
(`richards-bcpltape/sys3/bcpl/libhdr`) identified **22 top-level
BLIB definitions**: **21 named globals** and **one top-level
unmapped helper, PRINTWIDTH**. Local nested functions such as
MAPSTORE's MAPOUT are not top-level candidates.

The resulting ordered list is:

| Name | LIBHDR global | Name | LIBHDR global |
| --- | --- | --- | --- |
| WRITES | 60 | UNPACKSTRING | 67 |
| PACKSTRING | 66 | WRITEF | 76 |
| ABORT | 3 | ERRORMESSAGE | 5 |
| PRINTWIDTH | *none* | STACKHWM | 56 |
| MAPSTORE | 78 | INPROGRAM | 58 |
| VALIDPOINTER | 59 | BACKTRACE | 4 |
| WRITEARG | 69 | WRITED | 68 |
| WRITEN | 62 | NEWLINE | 63 |
| NEWPAGE | 64 | READN | 70 |
| WRITEOCT | 77 | WRITEHEX | 75 |
| WRITEO | 65 | WRITEX | 74 |

This reconciles **all 22 source-level definitions** against the
selected LIBHDR, without silently promoting PRINTWIDTH to a public
global. No duplicate G number appears among the 21 named BLIB
definitions. The historical LIBHDR's unrelated G94 duplicate
remains a distinct header issue.

### Strength and limitation of this ledger

This is the **complete source/header candidate-export ledger**,
not a byte-for-byte dump of the generated module's relocation or
global-registration trailer. The M1.8 six-step resident BLIB build
completed at RC=0000; BCPLMAIN's actual import code scans the BLIB
trailer; and the M1.8 full DEVOBJ regression passed all executable
cases, including representative independent BLIB linkage and
observability services. This is substantial *behavioral corroboration*,
but neither compiler success nor sampled execution proves that
**every** one of the 21 candidate trailer pairs exists, carries
the correct relocated address, and can be called correctly.

**Disposition:** retain that explicit object-trailer verification
as an open evidence item, without requiring a fresh build or changing
MVS data during source-only Gate A. A full generated-assembly listing
or object-level registration dump, obtained read-only from an
existing artifact or from a deliberately isolated probe, could
resolve it. Gate A is not yet closed by this source-level enumeration.

## Gate A — acceptance decision (13 October 2026)

**Accepted for runtime interface inventory, with an explicit
object-evidence limitation.** The ledger accounts for all 22
top-level BLIB procedures (21 LIBHDR-numbered candidates, one
unnumbered PRINTWIDTH helper), all explicit assembler ENTRY
symbols of the four canonical native modules, canonical LIBHDR
mapping, native global installers, application/BLIB registration
mechanism, representative calling conventions, and available
regression evidence. The current M1.8 full DEVOBJ panel supplies
123 passing executable regressions and an expected source-only
skip, without claiming each global has its own test.

**Non-closure item / deferred verification:** There is no retained
complete decoded export trailer for installed DEVOBJ(BLIB) in the
inspected Git inputs. The exact compiled trailer pair count and
individual relocations are **not verified**. Do not report them
as byte-level proven or conflate source-to-LIBHDR mapping with
an ESD/RLD inspection. If future work needs an exact binary
inventory, collect a read-only object-deck listing or decode a
binary-safe copy under a separately controlled evidence task.

`tools/dspal cat/get` deliberately rejects object libraries for
text transfer; using it on DEVOBJ(BLIB) would be incorrect. This
does not prevent Gate A acceptance because the contract inventory
records uncertainty rather than inventing operational proof.

**Gate A disposition: ACCEPTED, qualified as above.** No resident
MVS dataset or runtime implementation was changed.

## Gate B — storage and stack audit opened

Examine concrete source/behavior in this order:

1. **Heap ownership:** BCPLMEM's GETMAIN size, the 12-byte record
   header and linked list, G87/G88 return/error contracts,
   pointer handling, counters, G6!48 publication and MEMDRAIN.
2. **Frame layout and checked entry:** generated CG370 call
   convention; STKIMPL frame-size check, STKLIM safe boundary,
   STKCIMP call-count stub and return path.
3. **Stack high-water:** physical GETMAIN bounds versus the
   published G54/G55 extent, alternating marker initialization,
   BLIB STACKHWM predicate and what regression 120 proves.
4. **Temporary vectors:** BCPLAPT's APTOVEC and APLIMIT contract,
   nested calls and stack-limit failures.
5. **Exit ownership:** which allocations are drained on
   FINISH/STOP/abnormal paths, and whether failure paths report
   appropriate completion codes. Gate C covers full termination
   semantics; Gate B records storage-specific prerequisites.

Distinguish implemented behavior, separately tested behavior,
and remaining historical-equivalence gaps. Avoid changing
runtime source during the audit.

## Gate B — storage ownership and stack implementation audit (13 October 2026)

**Source inspection completed for core allocator, frame limit,
stack markers and termination reclaim. Gate B remains OPEN** pending
validation of independent APTOVEC limit initialization and detailed
semantic/observability checks.

### Main storage allocation

Canonical `asm/bcplmain.asm` defines one static
`DYNLEN=68592` byte MVS GETMAIN allocation: 700 global-vector
fullwords (2,800 bytes), 16,384 working-stack fullwords
(65,536 bytes), and 256 reserved bytes. `DYNWORK` begins at
the end of the globals; `STKLIM = DYNWORK+65536`; and
`DYNEND = STKLIM+256`. G54 (STACKBASE) publishes
`DYNWORK>>2`, while G55 (STACKEND) publishes
`DYNEND>>2` — **the exposed extent includes clearance beyond the
operational frame limit**. A check that merely verifies a pointer
is below G55 is therefore not a proof the pointer is within the
safe working-stack region.

### GETVEC / FREEVEC and allocator accounting

Canonical `asm/bcplmem.asm` is a static, non-reentrant singleton.
GETVEC accepts N in R7, rejects negative N and values above
4,194,299, then asks MVS for **4(N+1)+12 bytes**. On success,
its 12-byte prefix records the returned BCPL word pointer,
total byte extent, and the previous allocation-list head.
The returned word pointer is the base byte address plus 12,
shifted right two bits. Failure returns R7=0. Linked successful
allocations increment current/peak live-object count and
current/peak allocated bytes; the byte statistics include
the 12-byte header, not just usable vector data.

FREEVEC accepts the BCPL word pointer R7. Zero or a pointer not
found by **exact head-record pointer comparison** is a no-op.
A found allocation is unlinked and freed using its stored size
and byte base. It decrements live-count/byte counters and, when
the head changes, publishes the new head through MEMBIND.

MEMBIND accepts R1 pointing to writable G6!48, publishing the
allocator byte-pointer list head (or R1=0 to unbind).
MEMDRAIN walks live records, unlinks before FREEMAIN, decrements
current statistics, and refreshes the published head. MEMSTAT
writes current count, peak count, current allocated bytes and
peak allocated bytes to four successive fullwords at R1.
MEMSTAT is assembler-private and not a demonstrated BCPL global.

**Evidence:** GETVEC/FREEVEC regressions 27–32, release/termination
39 and 82, manually traversed live descriptors in 122, and
automatic G6!48 publication in 123. Test 82 explicitly does not
prove exact MVS FREEMAIN quantities; the implementation and
contract must not claim instrumentation beyond the observed test.

### Stack initialization and high-water calculation

BCPLMAIN writes 8,192 pairs of historical EBCDIC marker fullwords,
`X'5C40E2E3'` (EVENSTACK) then `X'C3D2405C'` (ODDSTACK),
over the 16,384-word working area. It writes the EVENSTACK guard
at `DYNEND-8` (G55-2), and stores at `DYNEND-4` (G55-1)
the word address `(STKLIM-8)>>2`.

Historical BLIB STACKHWM first checks the guard at
`STACKEND-2`, checks the saved scan starting word address
against STACKBASE..STACKEND, and requires EVENSTACK at that
starting word. It then walks backward in steps of two words
until a marker mismatch; its outputs are a BCPL word address
of high-water usage, UNSET=1, or OVERFLOW=0. **A measurement
is not a byte or word count.** Test 120 validates that the
installed service returned an address in range, not the precise
highest used address or full postmortem semantics.

### Checked entries and overflow

The system vector referenced through R11 implements S.STKCK
at displacement 60; the checked-entry call supplies an inline
frame-size fullword, and STKIMPL validates the size/alignment,
calculates `next-frame+size`, and compares against STKLIM,
which is *stricter than G55*. Its success return skips the
inline fullword. The malformed-frame path exits with R15=36.
The overflow route STKOVFL buffers `STACK OVERFLOW`
and takes the FINIMPL termination path, which currently clears
the normal completion code to zero. **Flag for Gates C/D:**
this may produce an abnormal-looking diagnostic with a normal
completion code; do not advertise reliable nonzero overflow
status without independent execution evidence.

S.COUNT (displacement 20) and S.STKCKCOUNT (80) are explicit
return-over-inline-word stubs, not actual call counters.

### APTOVEC discrepancy requiring directed investigation

The canonical BCPLMAIN source still includes a local
`APTOVEC` implementation checking its own STKLIM, while
the separately built `asm/bcplapt.asm` exports
`APTOVEC` and an `APLIMIT` data symbol, initialized to
zero in that source. BCPLMAIN's explicit G40 installation
uses local `LA 1,APTOVEC`; no `APLIMIT` reference or
initialization appears in the inspected canonical BCPLMAIN
assembler source. This raises a **linkage-selection and
initialization question**, not a proven runtime defect:
the native regression/link setup may externalize G40 or
initialize the independent APLIMIT in a build-specific path.
Regressions 091–093 passed in the M1.8 DEVOBJ panel, but
their link/edit inputs must be examined before asserting
that the independent APTOVEC and its limit are exercised in
the default runtime. Gate B will trace the actual selection.

### Termination ownership boundary

FINISH clears STOPRC; STOP saves R7 into STOPRC. Both use
FINEXIT to flush and close buffered streams, then RELMEM
invokes private MEMDRAIN and MEMBIND(0), and FREEMAIN releases
the global/stack allocation before returning to MVS. The
storage cleanup is source-observable on these normal and
explicit STOP paths. Not every early exit follows FINEXIT:
for example, the malformed checked-frame path returns 36
via an independent branch. Gate C must classify all error
paths individually rather than generalizing cleanup behavior.

**Gate B next:** inspect the actual regression-linker selection
and APLIMIT setup; map outcomes and refine the storage/stack
contract with explicit tested versus source-observed evidence.
