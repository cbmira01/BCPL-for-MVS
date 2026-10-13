# M1.8 — Reproducible Runtime Builds and MVS Synchronization

Status: **ACTIVE — Gate A provenance inventory accepted; Gate B next. No OBJ promotion authorized.**

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
`python3 native-compiler/bootstrap-cambridge/make-demoted.py --blib-only`.
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
`native-compiler/bootstrap-cambridge/build-mr10-trni-large-names.sh`
first runs
`native-compiler/bootstrap-cambridge/make-mr10-trn-large-names.py`.
The Python generator splits tracked historical
`richards-bcpltape/mr10/bcplkit/trn`, increasing the TRN0
declaration-vector capacity from 1200 to 2400 words with strict
anchors. The shell script compiles its generated TRN units under
`asm/icintv19.asm` with `tools/compile-and-run --save-intcode`,
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
`native-compiler/bootstrap-cambridge/options-large-tree.txt`
option file. The Cambridge demotion inputs
`native-compiler/bootstrap-cambridge/source/syn`,
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

Git now tracks `tools/prepare-bootstrap`, a single orchestrator of
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
python3 tools/prepare-bootstrap --check-inputs
python3 tools/prepare-bootstrap
```

Full translator INTCODE generation is **opt-in** because it launches
the existing MVS-backed `tools/compile-and-run` workflow:

```sh
python3 tools/prepare-bootstrap --with-trnilrg
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
`python3 tools/prepare-bootstrap --check-inputs`, reporting
**18/18 required paths present** without file writes. The default
`python3 tools/prepare-bootstrap` then successfully executed the
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
