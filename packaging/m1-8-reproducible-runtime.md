# M1.8 — Reproducible Runtime Builds and MVS Synchronization

Status: **CLOSED — Gates A–D and F accepted; optional Gate E deferred, not authorized.**

Governing policy: [Git and MVS authority](git-mvs-authority.md).
Git defines the implementation; resident MVS provides the target
build and execution proof. MVS libraries do not become a second
source-of-truth. This march does not change BCPL runtime semantics.

## Gates

| Gate | Proof |
| --- | --- |
| **A — Provenance audit** | Each of the five component sources, toolchain inputs, JCL and host-to-resident mappings identified, including non-Git dependencies |
| **B — Git-based rebuild readiness** | A clean source checkout can identify and stage its tracked inputs; any externally derived/untracked inputs must have explicit, reproducible provenance |
| **C — Controlled synchronization** | Explicit synchronization of selected source/JCL members, followed by resident independent rebuild into DEVOBJ, with no production write |
| **D — Rebuild acceptance** | Independent builds and focused execution tests for the rebuilt DEVOBJ set; confirm dependencies, member inventory and test evidence |
| **E — Optional production alignment** | Only with **separate, explicit operator authorization**, synchronize approved candidate to OBJ; never implicitly promote |
| **F — Final acceptance** | One full panel against the selected accepted object library, documenting any exceptional skip |

Gate E authorization is not inferred from running Gates A–D. A promotion
may be deferred without invalidating reproducible candidate-build
evidence; production alignment then remains pending.

## Gate A — known source provenance

| Object member | Build input mapping in `config/dspal.yaml` | Build job | Provenance |
| --- | --- | --- | --- |
| BCPLMAIN | `SOURCE(BCPLMAIN) ← asm/bcplmain.asm` | BLDDEVN | Git-tracked canonical assembler |
| BCPLMEM | `SOURCE(BCPLMEM) ← asm/bcplmem.asm` | BLDDEVM | Git-tracked canonical assembler |
| BCPLBYTE | `SOURCE(BCPLBYTE) ← asm/bcplbyte.asm` | BLDDEVB | Git-tracked canonical assembler |
| BCPLAPT | `SOURCE(BCPLAPT) ← asm/bcplapt.asm` | BLDDEVA | Git-tracked canonical assembler |
| BLIB | `SOURCE(BLIB) ← workarea/bootstrap-cambridge/demoted/blib` | BLDDEVL | **Generated (not tracked): deterministic Git-tracked `make-demoted.py --blib-only` derivative of `richards-bcpltape/bcplib/bcpl/blib`; resident sync must be verified** |

The BLIB job also reads resident `LOAD(ICINT19)`,
`INTCODE(CAMBCOMP)`, and `SOURCE(OPTIONS,CAMBPARM,LIBHDR,SYNHDR,
TRNHDR,CGHDR)`; it uses the resident IFOX assembler and an internal
two-card CG370 repair program. The SOURCEmember input paths for most
of these support records are specified by `config/dspal.yaml`, but
the exact resident binaries and their construction must be traced
before claiming clean-checkout rebuildability.

**Gate A finding (refined):** the four assembler modules are tracked
in Git. BLIB is *derivable* from Git: run
`python3 bootstrap-toolchain/bootstrap-cambridge/make-demoted.py --blib-only`.
Its input is tracked historical `richards-bcpltape/bcplib/bcpl/blib`;
the generator validates the SECTION header, two inequality tokens,
LIBHDR use and an 80-column limit before creating the ignored output.
The build still requires explicit re-generation and SOURCE(BLIB)
synchronization: a successful resident object does not prove its
source matched a particular Git revision.

## Independent Gate A source preflight

The tracked historical `richards-bcpltape/bcplib/bcpl/blib`
was fetched directly from Git. Its `SECTION "BLIB"` header
occurs in the expected position, it contains exactly two `~=`
operators and exactly one `GET "LIBHDR"` directive. These are the
three structural checks required by `make-demoted.py --blib-only`.
They passed in an independent check. This is **not** evidence that the
generator has already been executed on the operator workstation, or
that resident SOURCE(BLIB) currently equals its regenerated output.

## Gate A — resident compiler construction traced

The Git-tracked `jcl/build-cambridge-resident.jcl` (`JCL(CAMBBLD)`)
provides an explicit three-stage reconstruction recipe:

1. IFOX00 assembles `ASM(ICINT19)` and IEWL links it as
   `LOAD(ICINT19)`.
2. Running under that interpreter, the established MR10
   `SYNI + TRNILRG + BLIBI + ICLIB` compiler chain translates
   the demoted Cambridge BCPL, SYN, LEX, TRNA, TRNB, CGA–CGE and
   BOOTHOST sources to individual resident INTCODE members. The
   OCODE-to-INTCODE phase uses `CGI + BLIBI + ICLIB`.
3. IEBGENER concatenates the eleven compiler/host members with
   `BLIBI` and `ICLIB` into `INTCODE(CAMBCOMP)`.

Thus `LOAD(ICINT19)` and `INTCODE(CAMBCOMP)` are **build products
with a versioned JCL recipe**, not unexplained original inputs.
The chain still assumes that `INTCODE(TRNILRG)` and other MR10
bootstrap members have been prepared. `config/dspal.yaml` maps
`TRNILRG` to the ignored generated
`workarea/bootstrap-cambridge/trni-large-names.int`.
Reconstruction of that generated member, its producer, and the
initial bootstrap inputs must be independently verified before
declaring a clean-checkout bootstrap. No claim is made here that
CAMBBLD has been freshly rerun for M1.8.

This job also writes `LOAD(ICINT19)` and the CAMBCOMP/constituent
INTCODE members, so it should **not** be rerun casually as a
read-only provenance check. Its MVS execution is a separately
controlled rebuild operation.

## Gate A — TRNILRG derivation traced (13 October 2026)

Operator reported the local generated file
`workarea/bootstrap-cambridge/trni-large-names.int` at 20,885 bytes,
with eight `mr10-trn-large-names` source files (TRNHDR and TRN0–TRN6).
Generated Cambridge demoted and diagnostic source directories were
also present. This is file-presence evidence, not regenerated equivalence.

The tracked producer
`bootstrap-toolchain/bootstrap-cambridge/build-mr10-trni-large-names.sh`
first runs
`bootstrap-toolchain/bootstrap-cambridge/make-mr10-trn-large-names.py`.
The Python generator splits tracked historical
`richards-bcpltape/mr10/bcplkit/trn`, increasing the TRN0
declaration-vector capacity from 1200 to 2400 words with strict
anchors. The shell script compiles its generated TRN units under
`asm/icintv19.asm` with `tools/mr10/compile-and-run --save-intcode`,
using the tracked large-tree options and LIBHDR, then concatenates
the resulting INTCODE into the configured `TRNILRG` file.

The source-generation graph for TRNILRG is thus documented in Git.
The independent `TRNILRG` bootstrap build has **not** been
re-executed in this march and its output has not been compared to
the resident MVS member or the current local file. A fresh
reconstruction/equivalence claim requires that comparison.

## Gate A — initial MR10 bootstrap closure

GitHub inspection confirmed tracked files for the initial compiler
chain: `intcode/syni.int`, `intcode/cgi.int`,
`intcode/blibi.int`, `intcode/iclib.int`,
`asm/icintv19.asm`, historical MR10 translator source
`richards-bcpltape/mr10/bcplkit/trn`, target LIBHDR
`richards-bcpltape/sys3/bcpl/libhdr`, and the
`bootstrap-toolchain/bootstrap-cambridge/options-large-tree.txt`
option file. The Cambridge demotion inputs
`bootstrap-toolchain/bootstrap-cambridge/source/syn`,
`source/trn`, historical `bcplib/bcpl/bcpl` and `cg`,
plus `bootstrap-host.bcpl` and `cambridge-options.txt`
are tracked as well.

Combined with the previously inspected `make-demoted.py`,
`make-mr10-trn-large-names.py`,
`build-mr10-trni-large-names.sh` and
`jcl/build-cambridge-resident.jcl`, this identifies a
**Git-governed source and build graph** for all known initial
MR10/Cambridge inputs consumed by the BLIB compiler.

**Gate A accepted as a provenance inventory**, not as a successful
clean-checkout rebuild or bytewise comparison. Gate B must validate
the actual generated sources/INTCODE under controlled staging,
including the ignored workarea files, and identify any undeclared
runtime or utility requirements revealed by execution.

## Gate B — bootstrap preparation driver staged

Git now tracks `tools/native/prepare-bootstrap`, a single orchestrator of
existing historical transformations. It requires only the checked-in
source paths for a `--check-inputs` preflight. The default run executes
`make-demoted.py` and `make-mr10-trn-large-names.py`, rebuilding
the disposable demoted Cambridge files and MR10 TRN source derivatives
under ignored `workarea/bootstrap-cambridge/`. It emits a SHA-256
inventory at `workarea/bootstrap-cambridge/prepare-bootstrap-manifest.json`
for the 18 checked input paths and 24 generated source files.
The manifest is diagnostic evidence, not a signed release or an
MVS-resident equality check.

Usage:

```sh
python3 tools/native/prepare-bootstrap --check-inputs
python3 tools/native/prepare-bootstrap
```

Full translator INTCODE generation is **opt-in** because it launches
the existing MVS-backed `tools/mr10/compile-and-run` workflow:

```sh
python3 tools/native/prepare-bootstrap --with-trnilrg
```

That optional mode runs the existing
`build-mr10-trni-large-names.sh` and additionally inventories
`trni-large-names.int`. No mode runs `dspal put`, submits CAMBBLD,
or writes OBJ/DEVOBJ. The default source-generation mode **does**
replace generated files in ignored `workarea/`; it must not be
mistaken for a read-only command. Use `--check-inputs` for a
strictly read-only check.

Gate B is **not accepted yet**: driver is staged in Git, but a real
operator generation run and digest/output review are needed. No
claim of resident member equality or clean-checkout MVS run yet.

## Gate B — host generator execution evidence (13 October 2026)

After pulling Git through `54c6930`, the operator ran
`python3 tools/native/prepare-bootstrap --check-inputs`, reporting
**18/18 required paths present** without file writes. The default
`python3 tools/native/prepare-bootstrap` then successfully executed the
tracked `make-demoted.py` and `make-mr10-trn-large-names.py`
generators, reporting **24 generated outputs** and a SHA-256
inventory at
`workarea/bootstrap-cambridge/prepare-bootstrap-manifest.json`.

Reported output sizes agree with the earlier operator directory
listing for the generated source files (including BLIB 14,134
bytes and MR10 TRN0 2,400 bytes). This establishes working
regeneration and file presence; it does **not** prove matching SHA-256
digests against the previous contents or resident MVS members.
`--with-trnilrg` was not executed. All operations remained on
the host and did not modify MVS datasets.

**Gate B status: source-preparation subsection accepted; full
TRNILRG generation/equivalence still pending.**

## Gate B — full bootstrap preparation accepted (13 October 2026)

The operator pulled commit `544ce37` and ran
`python3 tools/native/prepare-bootstrap --with-trnilrg`.
Both tracked source generators completed, followed by the opt-in
`build-mr10-trni-large-names.sh`. The MVS-backed
`tools/mr10/compile-and-run` submitted **JOB 936** and reported saved
INTCODE files for TRN0–TRN6. The concatenated
`workarea/bootstrap-cambridge/trni-large-names.int` was
**20,885 bytes**, agreeing with the previously reported file size.
The bootstrap driver inventoried **25 generated outputs** in its
SHA-256 manifest and reported no MVS dataset changes.

**Gate B accepted:** the preparation chain has been executed end
to end from tracked historical and transformation inputs through
the MVS-backed INTCODE generator. Neither raw JOB 936 return codes
nor a before/after SHA-256 equality comparison were supplied, so
this acceptance does not claim independently verified step codes
or bytewise resident equivalence. Gate C will address controlled
resident source/JCL synchronization separately.

## Gate C — explicit member replacement verification policy

The operator suggested a controlled **delete–compress–rebuild–list**
test for Git-to-MVS synchronization:

```sh
tools/datasets/dspal rm SOURCE <explicit-approved-member>
tools/datasets/dspal compress SOURCE
# Stage replacement from the corresponding Git mapping, e.g.
tools/datasets/dspal put SOURCE <member> <mapped-host-file>
tools/datasets/dspal ls SOURCE
```

Use exact member names and the mapped source filenames; do **not**
delete all members or indiscriminately delete resident bootstrap
prerequisites. Inventory proves that expected names were restored,
not that source bytes were equivalent. Follow with readback or
appropriate normalized text comparison where feasible. For binary
libraries, use MVS-native operations and binary-safe verification;
never use `dspal put` on OBJ/DEVOBJ. Apply a destructive replacement
only after documenting the affected members and confirming all host
replacement files exist. Production OBJ remains out of scope without
separate operator authorization.

## Gate C — controlled resident synchronization: operator plan

**Boundary:** only the specified text members in
`HERC02.BCPL.SOURCE` and `HERC02.BCPL.JCL`.
Do not delete or replace `LOAD(ICINT19)`,
`INTCODE(CAMBCOMP)`, or any OBJ/DEVOBJ member in this
synchronization step. The independently rebuilt
`trni-large-names.int` can be staged in a subsequent, explicitly
identified bootstrap-input step; rebuilding CAMBCOMP is not needed
to validate the five existing runtime build jobs.

**Preflight:** `git pull --ff-only`; then
`python3 tools/native/prepare-bootstrap --check-inputs`. All mapped host
files below must exist before *any* resident deletion.

| PDS | Member | Authoritative host input |
| --- | --- | --- |
| SOURCE | BCPLMAIN | asm/bcplmain.asm |
| SOURCE | BCPLMEM | asm/bcplmem.asm |
| SOURCE | BCPLBYTE | asm/bcplbyte.asm |
| SOURCE | BCPLAPT | asm/bcplapt.asm |
| SOURCE | BLIB | workarea/bootstrap-cambridge/demoted/blib |
| JCL | BLDDEVN | jcl/build-dev-bcplmain.jcl |
| JCL | BLDDEVM | jcl/build-dev-bcplmem.jcl |
| JCL | BLDDEVB | jcl/build-dev-bcplbyte.jcl |
| JCL | BLDDEVA | jcl/build-dev-bcplapt.jcl |
| JCL | BLDDEVL | jcl/build-dev-blib.jcl |

Begin with `tools/datasets/dspal ls SOURCE` and `tools/datasets/dspal ls JCL`
for the original inventories. For each selected PDS use explicit
`dspal rm` for **only** the mapped members above, followed by
one `dspal compress` for that PDS, then explicit
`dspal put PDS MEMBER HOSTFILE` for each replacement.
Check each command's completion and stop immediately on any
nonzero exit or unanticipated inventory.

Finish with `tools/datasets/dspal ls SOURCE` and
`tools/datasets/dspal ls JCL`, and verify the ten selected names all
reappear. Before claiming content equivalence, independently
read each text member back using `dspal get` and compare under
the configured UTF-8 ↔ CP037 FB80 round-trip normalization;
raw host bytes and resident FB80 records are not necessarily
identical. Readback can be scoped to a focused subset first;
an inventory alone proves names, not contents.

**Then**, only after the ten-member text sync is accepted,
submit the five independent `BLDDEV*` jobs to DEVOBJ and
inspect their assembler/compile/install step codes. This is
part of Gate C's integrated build proof and feeds Gate D's
focused regression execution. Production OBJ remains unchanged.

## Gate C — SOURCE/JCL replacement and inventory evidence (13 October 2026)

The operator pulled Git through `9789399`, passed the
`prepare-bootstrap --check-inputs` preflight (18 inputs), and
verified the ten mapped host files existed. Original SOURCE and
JCL inventories included all five intended members in each.

**SOURCE:** exact member deletions BCPLMAIN, BCPLMEM, BCPLBYTE,
BCPLAPT, BLIB succeeded in JOBs **939–943**; IEBCOPY compression
JOB **944** succeeded; explicit host-file transfers completed
in JOBs **945–949**, and the final SOURCE inventory contained
all five names and the other existing source members.

**JCL:** exact member deletions BLDDEVN, BLDDEVM, BLDDEVB,
BLDDEVA, BLDDEVL succeeded in JOBs **951–955**; compression
JOB **956** succeeded; Git-mapped job bodies were installed
in JOBs **957–961**. Final JCL inventory contained all five
names and the other previously present job members.

**Gate C subsection accepted: controlled ten-member text staging
and restored inventories.** Byte/semantic readback and the five
independent DEVOBJ builds remain outstanding, so the *whole* Gate C
is not yet closed. Production OBJ, LOAD(ICINT19), CAMBCOMP and
TRNILRG were outside the operation's scope.

## Gate C — BLIB readback blocked by false job-summary ABEND

The operator's ten-member normalized readback check passed
SOURCE(BCPLMAIN), SOURCE(BCPLMEM), SOURCE(BCPLBYTE),
SOURCE(BCPLAPT), JOBs **963–966**. The fifth `dspal get`
of SOURCE(BLIB), JOB **967**, exited nonzero because
`tools/mvs/job-summary` reported `ABEND: detected`
despite IEBGENER COPY RC=0000.

The operator supplied JOB 967's complete JES report:
`IEF142I` confirmed COND CODE 0000, `IEF404I` ended
the job and `$HASP395` confirmed normal completion.
The job's SYSOUT included BLIB source lines
`STEP ABEND USER CODE` and `STEP ABEND SYSTEM CODE`.
Audit of `tools/mvs/job-summary` found its previous generic
`ABEND_RE` scanning all SYSOUT lines, explaining the
false-positive classification. The detector has been
constrained to genuine IEF/IEA diagnostic message IDs,
and a targeted check was added at
`tools/checks/check-job-summary-abend.py`.

**Not yet retested on the host.** JOB 967 is correctly
understood as a successful IEBGENER copy, but the content
comparison did not execute for BLIB, and the five JCL
comparisons were not reached. No SOURCE member was
modified by this readback.

## Gate C — all ten text readbacks verified (13 October 2026)

The operator first compared the canonical SOURCE assembler members,
all four matching. The first BLIB comparison detected only two
additional trailing blank lines in the generated host file, and
the fail-fast script stopped before the JCL cases.

The operator then used a shell `dspal cat` + `diff -u` check with
normalization removing trailing spaces on each line and terminal
blank lines. **SOURCE(BLIB) and JCL(BLDDEVN), JCL(BLDDEVM),
JCL(BLDDEVB), JCL(BLDDEVA), JCL(BLDDEVL) all passed.**
Combined with the prior four assembler SOURCE matches, this
establishes **10/10 normalized text-member equality** against
the Git-controlled mappings. This is logical record equivalence,
not raw EBCDIC FB80 byte equivalence.

The next Gate C action is independently building all five DEVOBJ
components from these installed SOURCE/JCL members. No production
OBJ mutation is authorized.

## Gate C — independent DEVOBJ rebuild accepted (13 October 2026)

After pulling Git through `48d3e5a`, the operator submitted
all five previously synchronized resident build-job bodies.
Each job completed successfully:

| Member | Payload job | Compiler/assembler | Install |
| --- | --- | --- | --- |
| BCPLMAIN | 982 | ASMMMAIN IFOX00 RC=0000 | PUTMAIN IEBGENER RC=0000 |
| BCPLMEM | 985 | ASMMEM IFOX00 RC=0000 | PUTMEM IEBGENER RC=0000 |
| BCPLBYTE | 988 | ASMCOMP IFOX00 RC=0000 | PUTCOMP IEBGENER RC=0000 |
| BCPLAPT | 991 | ASMCOMP IFOX00 RC=0000 | PUTCOMP IEBGENER RC=0000 |
| BLIB | 994 | COMP ICINT19, PREPASM IFOX00, PREPLK IEWL, FIXASM, ASMBLIB IFOX00, all RC=0000 | INSTALL IEBGENER RC=0000 |

All five jobs reported highest RC=0000, zero flagged
assembler statements and highest assembler severity zero.
The operator's `tools/datasets/dspal ls DEVOBJ` inventory showed exactly
BCPLAPT, BCPLBYTE, BCPLMAIN, BCPLMEM, BLIB.

**Gate C accepted:** the ten synchronized and text-verified
resident SOURCE/JCL inputs independently produced the complete
five-member DEVOBJ runtime. No production OBJ write was involved.
Gate D now requires focused application linkage and execution
using that newly rebuilt DEVOBJ runtime; do not run the full
panel until final Gate F.

## Gate D — focused rebuilt DEVOBJ execution accepted (13 October 2026)

After pulling Git through `e216ac4`, the operator ran
`BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ
tools/native/run-regression <test> --show-output` separately for
04 (string output), 25 (separately compiled BCPL library),
26 (separately assembled native through G), 27 (GETVEC),
069 (independent BLIB object), 091 (nested APTOVEC),
and 123 (FREEBASE auto-publication).

Each invocation reported **PASS 1, FAIL 0, SKIP 0,
TOTAL 1**, for an aggregate **7 PASS, 0 FAIL, 0 SKIP**.
This supplies focused application execution evidence for
the independently rebuilt five-member DEVOBJ runtime.
No full panel was run as part of Gate D.

**Gate D accepted.** Gate E production alignment remains
optional and requires separate explicit operator authorization.
Gate F is the single final full regression panel, with the
object-library target to be identified explicitly.

## Constraints and acceptance evidence

The M1.7 DEVOBJ 00–123 panel passed 123, failed 0 and skipped 083;
that is the accepted **resident baseline**, not a clean-checkout
reconstruction proof. Do not use `dspal put` on binary OBJ or DEVOBJ:
it performs text conversion. The existing IFOX and IEBGENER jobs
produce binary FB80 objects on MVS. Do not overwrite production OBJ.

Next: verify the tracked BLIB generator and source provenance,
trace ICINT19/CAMBCOMP resident bootstrap provenance, then implement
safe, explicit staging and build instructions. No new operator MVS
commands are yet required for the provenance audit.

## Gate F — full rebuilt DEVOBJ panel accepted (13 October 2026)

After pulling Git through `b71e81c`, the operator ran:

```sh
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ tools/native/run-regression
```

The single full native regression panel enumerated cases 00 through 123
(124 total): **123 PASS, 0 FAIL, 1 expected SKIP**. Case 083 is the
source-only instrumentation experiment, not an executable regression.
The panel exercised the independently rebuilt DEVOBJ set, with the
same runtime library selection used for Gate D. All executable cases
passed. The operator's output explicitly reported `NATIVE REGRESSION
COMPLETE / PASS 123 / FAIL 0 / SKIP 1 / TOTAL 124`.

**Gate F accepted. M1.8 closed.** The Git-controlled reconstruction,
resident SOURCE/JCL synchronization and readback, independent DEVOBJ
builds, focused checks and the final panel are accepted as a complete
reproducible candidate-runtime workflow. Optional Gate E (production
OBJ alignment) is intentionally **deferred and not authorized**; this
closure does not claim that production OBJ was changed or is identical
to DEVOBJ. DEVOBJ remains the development candidate library, OBJ the
stable ordinary-application linkage library. Any future promotion must
be separately authorized and recorded with Git revision, member
inventory and acceptance evidence.
