# Clean-room MVS PDS reconstruction — MR10 through native BCPL

**Scope:** reconstruct the complete **M3 executable stack**, then reproduce the **M5.4 DEVOBJ(BCPLM6+BCPLIO)** candidate described in section 10, starting from a clean host `workarea/`. This document is the single operator runbook for the reconstruction sequence. It is not an M4 native Cambridge compiler build.

**Status:** M3 stages and its earlier 00–123 suite were demonstrated on TK5 (15 October 2026); the independent DEVOBJ dynamic-stream candidate later passed M4.4 (00–145, 145 PASS/0 FAIL/expected SKIP 083) and M5.1/M5.2 focused evidence on 17 October. **This full destructive purge-to-DEVOBJ sequence has not been run anew as one clean-room acceptance exercise**. Record its results when executed. The final M3 panel demonstrated **123 PASS / 0 FAIL / 1 expected SKIP (083)**.

## Authorities, scope, and precautions

- Run commands from the repository root on the machine that hosts Hercules/TK5. Use a clean checkout at a **recorded Git commit**, or `git pull --ff-only` with a clean tree.
- Git holds canonical source code and build JCL. `config/dspal.yaml` alone defines **24 managed PDS/load datasets**: **9 MR10**, **9 reserved CAMB**, **6 NATIVE**. It currently has **151 mapped text members**; unpopulated products are generated later.
- `CAMB_*` is **reserved for M4**. M3 rebuilds use only `MR10_*` and `NATIVE_*`. A full manifest `initbcpl` still allocates the reserved CAMB datasets; do not populate them with compiler artifacts or submit CAMB jobs.
- `config/dspal.local.yaml` provides local credentials and runtime overrides; keep it secret and **out of Git**. If local overrides change the HLQ, examine the build JCL: several authoritative jobs intentionally contain the canonical `HERC02` DSNs.
- **Destructive boundary:** `purgebcpl` removes **every dataset named in the manifest, including MR10/NATIVE binaries and the empty/reserved CAMB datasets**. This is not a general MVS reset. Protect anything not reproducible before invoking it. It does not delete retired unlisted PDSes.
- Clean **only** the disposable host `workarea/`, not `mvs-state/`, TK5 DASD, local configuration, historical evidence, or checked-in source. Do not migrate prior PDS INTCODE/OBJ/LOAD images.
- Allow each command to finish successfully before progressing. `dspal submit` prints the **launcher** and **payload** jobs; inspect the **payload** summary.

## The complete workflow at a glance

**Historical gates 0–9 are the M3 base, not the current dynamic candidate.** The additional candidate build and fresh 00–145 run are documented below in **section 10**; use both parts when reconstructing the current BCPLIO runtime.

| Gate | Rebuild action | Input authority | MVS result / evidence |
| --- | --- | --- | --- |
| 0 | Preflight TK5, manifest and Git | `config/dspal.yaml`, local override | Status, `git rev-parse HEAD` |
| 1 | Remove disposable `workarea/`; regenerate demoted sources | Historical tracked sources and `tools/native/prepare-bootstrap` | 24 generated host outputs and SHA-256 manifest; no PDS writes |
| 2 | Purge explicit managed PDS set; initialize clean set | `dspal purgebcpl`, `initbcpl` | Manifest-defined PDS/load libraries; **all old binaries discarded** |
| 3 | Populate Git-backed text members | `dspal populate all` | MR10 source, ASM, JCL, tests, demos and native ASM/JCL/headers |
| 4 | Build ICINT19 | `MR10_JCL(IC19BLD)` | `MR10_LOAD(ICINT19)`, `MR10_OBJ(ICINT19)` |
| 5 | Execute MR10 interpreted tests and demos | MR10 kit sources and installed interpreter | 11 language demos, 17 BCPL demos, 12 regressions (MVS jobs) |
| 6 | Rebuild enlarged MR10 translator | `prepare-bootstrap --with-trnilrg` | `NATIVE_INTCODE(TRNILRG)` |
| 7 | Stage demoted Cambridge BCPL and options | `tools/native/stage-bootstrap` | `NATIVE_SOURCE` demoted units, BLIB, headers and options |
| 8 | Build resident Cambridge compiler image | `NATIVE_JCL(CAMBBLD)` | `NATIVE_INTCODE(CAMBCOMP)` and compiler INTCODE units |
| 9 | Rebuild production runtime | `NATIVE_JCL(BLDBMAIN)`, `NATIVE_JCL(BLIBBLD)` | `NATIVE_OBJ(BCPLMAIN,BCPLMEM,BLIB)` |
| 10 | Rebuild development service modules | `NATIVE_JCL(BLDDEVA,BLDDEVB,BLDDEVI)` | `NATIVE_DEVOBJ(BCPLAPT,BCPLBYTE,BCPLIO)` |
| 11 | Native compile smoke and full regression | `tools/native/compile-mvs`, `tools/native/run-regression` | Actual IFOX/IEWL/GO; target 123/0/1 |
| 12 | Save checks and closure evidence | Git commit, MVS JOB summaries, dataset inventories | Reproducibility record; no migration |

## 0. Establish a reproducible operator session

```sh
cd ~/Source/Repos/BCPL-for-MVS
git status --short
git pull --ff-only
git rev-parse HEAD
tools/mvs/start-tk5 --detached
tools/datasets/dspal status --probe
tools/datasets/dspal info
tools/native/prepare-bootstrap --check-inputs
python3 tools/checks/check-native-bootstrap-jcl.py
```

Do not continue after an unexpected Git modification, unavailable JES card reader, or incorrect target HLQ. Confirm the password is configured in `config/dspal.local.yaml`; do **not** paste credentials into a report. Starting an already-running container should not be treated as a demand to recreate its DASD.

## 1. Clean only host-generated files; regenerate demoted sources

```sh
# DESTRUCTIVE TO DISPOSABLE HOST BUILD OUTPUTS ONLY.
# Check for anything worth preserving in workarea/ before removal.
rm -rf -- workarea
mkdir -p workarea
tools/native/prepare-bootstrap
cat workarea/bootstrap-cambridge/prepare-bootstrap-manifest.json
```

The non-live stage regenerates demoted `blib`, `bcpl`, `syn`, `lex`, `trna`, `trnb`, `cga`–`cge`, the diagnostic demotions, and seven large-name MR10 translator sections plus their header (24 generated output files total). This **reconstructs source inputs**, not an executable resident compiler. The enlarged `TRNILRG` INTCODE image is built **after** ICINT19 is available. Retain the generated SHA-256 manifest as host-side provenance.

## 2. Purge, initialize, and populate managed PDSes

```sh
# INSPECT THE EXACT DELETE DECK BEFORE AUTHORIZING DELETION.
tools/datasets/dspal purgebcpl --show-jcl
tools/datasets/dspal purgebcpl    # requires explicit YES

tools/datasets/dspal initbcpl --show-jcl
tools/datasets/dspal initbcpl
tools/datasets/dspal stat
tools/datasets/dspal populate all --dry-run
tools/datasets/dspal populate all
tools/datasets/dspal ls
```

The purge includes `MR10_LOAD`, `MR10_OBJ`, `NATIVE_INTCODE`, `NATIVE_OBJ` and `NATIVE_DEVOBJ`; they are **empty after initialization by design**. Do not copy modules from old pre-M3 libraries. Text population intentionally excludes derived binary members and generated Cambridge demotions, which are staged later.

The manifest lists **24 managed datasets**. Check the current number of mapped source members with `dspal info`; historical counts are not a reliable validation after source reorganization.

## 3. Rebuild the MR10 version-19 interpreter

```sh
tools/datasets/dspal submit MR10_JCL IC19BLD
tools/datasets/dspal ls MR10_LOAD
tools/datasets/dspal ls MR10_OBJ
```

Verify the **payload** ASM (IFOX), LKED (IEWL), and SAVEOBJ (IEBGENER) each returned `RC=0000`, and that both libraries contain `ICINT19`. The job-body source is `mr10-kit-compiler/jcl/build-icintv19.jcl`. Never use a preexisting load module to satisfy this gate.

For an independent interpreted smoke test using the newly installed interpreter:

```sh
tools/mr10/compile-and-run --installed-icint MR10_LOAD --results \
  mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.bcpl
```

Require interpreted `EXECUTION CYCLES=...,CODE=0` and expected output; JES `RC=0000` alone does not establish semantic success.

## 4. Exercise all MR10 language demos, BCPL demos, and regressions

The three authoritative **MVS-resident suites** are already manifest-mapped into `MR10_JCL` and depend on the freshly populated `MR10_*` test/source PDSes:

```sh
tools/datasets/dspal submit MR10_JCL MRLANGDM
tools/datasets/dspal submit MR10_JCL MRBCDEMO
tools/datasets/dspal submit MR10_JCL MRREGRES
```

| Member | MVS job-body file | Programs | Interpretation |
| --- | --- | ---: | --- |
| `MRLANGDM` | `mr10-kit-compiler/jcl/run-language-demos.jcl` | 11 | BCPL language constructs |
| `MRBCDEMO` | `mr10-kit-compiler/jcl/run-bcpl-demos.jcl` | 17 | Application demonstrations |
| `MRREGRES` | `mr10-kit-compiler/jcl/run-regression-tests.jcl` | 12 | MR10 kit regression programs |

Each includes compile, code-generation and program-run steps; the regression suite does **not** perform host-side exact comparison against checked-in `.expected` files. Inspect `CODE=0`, `RP:` lines, and error markers in the full payload reports. Details: `mr10-kit-compiler/jcl/README-SUITES.md`.

For stricter **host-verified expected-output comparison**, additionally run:

```sh
tools/mr10/run-regression-panel
tools/mr10/run-language-demos
tools/mr10/run-demo-suite
```

These legacy host suite runners currently use `tools/mr10/current-icint` (assembler source) and may assemble/link their own interpreter per test; they are **additional tests, not proof that each case ran through the newly installed `MR10_LOAD(ICINT19)`**. The installed-interpreter smoke test above and the resident MVS suites supply that proof. Do not misstate the distinction.

## 5. Recreate enlarged TRNI INTCODE

```sh
tools/native/prepare-bootstrap --with-trnilrg
tools/datasets/dspal put NATIVE_INTCODE TRNILRG \
  workarea/bootstrap-cambridge/trni-large-names.int
tools/datasets/dspal ls NATIVE_INTCODE
```

This reruns the demotions and compiles seven generated MR10 translator pieces through the **installed** interpreter, then assembles their INTCODE into `trni-large-names.int`. Require successful interpreted compilation, the host manifest's `trnilrg_rebuilt: true`, and `TRNILRG` in the target PDS. The installed member is rebuildable; it is not migrated from an old library.

## 6. Stage demoted Cambridge sources and rebuild CAMBCOMP

```sh
tools/native/stage-bootstrap --dry-run
tools/native/stage-bootstrap
tools/datasets/dspal ls NATIVE_SOURCE
python3 tools/checks/check-native-bootstrap-jcl.py
tools/datasets/dspal put NATIVE_JCL CAMBBLD \
  native-compiler/jcl/build-cambridge-resident.jcl
tools/datasets/dspal submit NATIVE_JCL CAMBBLD
tools/datasets/dspal ls NATIVE_INTCODE
```

`stage-bootstrap` puts 14 members: `BLIB`, 10 demoted Cambridge compiler units, `BOOTHOST`, `OPTIONS`, and `CAMBPARM`. Headers (`LIBHDR`, `SYNHDR`, `TRNHDR`, `CGHDR`) were populated from Git in gate 2. The authoritative resident build is `native-compiler/jcl/build-cambridge-resident.jcl`; it uses `MR10_LOAD(ICINT19)`, `MR10_SOURCE`, `NATIVE_INTCODE(TRNILRG)`, and `NATIVE_SOURCE`. It contains 22 interpreter executions plus a PACKCOMP step. Require `CODE=0` for **all 22** interpreted phases (not merely each step's `RC=0000`) and verify `NATIVE_INTCODE(CAMBCOMP)` and the constituent units. No `CAMB_*` library is used.

Smoke-test compilation using the resident image:

```sh
tools/native/compile-mvs \
  native-compiler/regression/00-most-degenerate-bcpl-program/source.bcpl \
  --output workarea/m3-clean-smoke.s370.asm
test -s workarea/m3-clean-smoke.s370.asm
```

Look for generated `CSECT`, `EXTRN BCPLMAIN`, and `END` cards. `compile-mvs` verifies interpreted execution code.

## 7. Rebuild runtime objects without copying any earlier OBJ

**PRODUCTION-CHANGE HOLD (canonical-source update, October 2026).**
The commands below document the former M3 procedure. The manifest now
populates the accepted **D6 development source** into
`NATIVE_ASM(BCPLMAIN)`. Submitting `BLDBMAIN` below would replace
the existing production `NATIVE_OBJ(BCPLMAIN)` with D6.
**Do not run that job or the full destructive clean-room sequence
without explicit production promotion approval.** For exact historical
M3 reconstruction, the former pre-D6 source remains in
`native-compiler/asm/history/bcplmain-pre-d6-production.asm`.
Until a separate production policy is accepted, the clean-room
runbook is an engineering reference, not authorization to deploy D6.

```sh
tools/datasets/dspal ls NATIVE_ASM

tools/datasets/dspal put NATIVE_JCL BLDBMAIN \
  native-compiler/jcl/build-bcplmain-objects.jcl
tools/datasets/dspal put NATIVE_JCL BLIBBLD \
  native-compiler/jcl/build-blib-object.jcl
tools/datasets/dspal put NATIVE_JCL BLDDEVA \
  native-compiler/jcl/build-dev-bcplapt.jcl
tools/datasets/dspal put NATIVE_JCL BLDDEVB \
  native-compiler/jcl/build-dev-bcplbyte.jcl
tools/datasets/dspal put NATIVE_JCL BLDDEVI \
  native-compiler/jcl/build-dev-bcplio.jcl

tools/datasets/dspal submit NATIVE_JCL BLDBMAIN
tools/datasets/dspal submit NATIVE_JCL BLIBBLD
tools/datasets/dspal submit NATIVE_JCL BLDDEVA
tools/datasets/dspal submit NATIVE_JCL BLDDEVB
tools/datasets/dspal submit NATIVE_JCL BLDDEVI

tools/datasets/dspal ls NATIVE_OBJ
tools/datasets/dspal ls NATIVE_DEVOBJ
```

| Object library | Required members | How rebuilt |
| --- | --- | --- |
| `NATIVE_OBJ` | `BCPLMAIN`, `BCPLMEM` | `BLDBMAIN`: IFOX assembler + IEBGENER |
| `NATIVE_OBJ` | `BLIB` | `BLIBBLD`: resident compiler + card repair + IFOX + IEBGENER |
| `NATIVE_DEVOBJ` | `BCPLAPT`, `BCPLBYTE`, `BCPLIO` | `BLDDEVA`, `BLDDEVB`, `BLDDEVI`: IFOX + IEBGENER |

**Do not promote** development objects into the accepted library for convenience, and **do not run `SEEDDEV`** on the clean-room path. It is an older five-member copy job with a prerequisite not present in the newly rebuilt accepted library.

**Installed JCL synchronization warning:** after editing checked-in job bodies, re-install them into `NATIVE_JCL` before submission. On 15 October, an old `BLDDEVA` member assembled and wrote to retired `HERC02.BCPL.SOURCE/DEVOBJ` with `RC=0000`; the new library remained unchanged until the corrected JCL was reinstalled. Always verify final PDS inventories, not just return codes.

## 8. Run the full native panel

```sh
tools/native/run-regression 0 --show-output
tools/native/run-regression 0 9
tools/native/run-regression
```

The installed-object regression linker reads `BCPLMAIN`, `BCPLMEM`, and `BLIB` from `NATIVE_OBJ` while resolving `BCPLAPT` and `BCPLBYTE` from `NATIVE_DEVOBJ`. There is **no object promotion**. The current complete panel spans **00–123**:

| Expected result | Count |
| --- | ---: |
| PASS | 123 |
| FAIL | 0 |
| SKIP | 1 (`083-instrumented-storage-reclamation`) |
| TOTAL | 124 |

Regression 083 is intentionally skipped in installed-object mode because its memory reclamation instrumentation is source-only. This is not a blanket assertion of full historical Cambridge/BCPL compatibility. Review failures and captured `workarea/native-regression/logs/` before making code changes.

## 9. Record complete clean-room evidence

Record the exact Git commit, TK5/MVS date, effective `dspal info` dataset list (redact secrets), operator machine, each payload JOB number and step RC, the ICINT `CODE` values, the member inventories (`MR10_LOAD`, `MR10_OBJ`, `NATIVE_INTCODE`, `NATIVE_ASM`, `NATIVE_SOURCE`, `NATIVE_OBJ`, `NATIVE_DEVOBJ`), the demotion SHA-256 manifest, and the final three regression summary counts.

The baseline stage-by-stage acceptance and representative historical JOB numbers are recorded in `packaging/m3-native-reconstruction-acceptance-20261015.md`. JES job IDs will differ on a fresh run and can wrap.

**Stop condition:** all required members present; no stale retired dataset allocation; all interpreter programs return the expected interpreted status; all assembly/link/install steps complete; native panel 123/0/1. Until the complete sequence is exercised in one clean-room run, consider this a consolidated, source-audited procedure rather than independent proof of one-run reproducibility.

---

## 10. M5.4 addendum — reproduce the accepted dynamic BCPLIO candidate

**Status (17 October 2026): source-documented extension to the
historical M3 clean-room procedure above.** It is **not** a claim
that the *entire* purge-to-candidate sequence has been newly
executed end-to-end. Source and live-stage outcomes are recorded
separately in [M4.4]
(bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream.md),
[M5.1]
(bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream-M5.1-plan.md),
[M5.2]
(bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream-M5.2-plan.md)
and [the current runtime contract]
(bcplio-dynamic-stream/BCPLIO-dynamic-runtime-contract.md).

**This section extends, not replaces, gates 0–9 above.** Gates 0–9
still explain the whole disposable MR10/ICINT19, demoted Cambridge
compiler, production OBJ, BLIB and service-module bootstrap.
The original gate 8 expected 123/0/1 was the **older M3
acceptance result**, not the current candidate acceptance target.
After following those gates, also do the following.

### A. Know which objects are canonical vs candidate

**Canonical Git source and MVS object status are separate.** The
canonical D6 `native-compiler/asm/bcplmain.asm` maps only to
`NATIVE_ASM(BCPLMAIN)`. Historical source variants are not mapped.
The optional D6 build JCL reads this canonical source and installs
`NATIVE_DEVOBJ(BCPLM6)`; its object member retains that historical
name for accepted regression compatibility. **BLDBMAIN also reads
BCPLMAIN source and now constitutes a production promotion if run.**

| Manifest alias | Relevant members | Authority |
|---|---|---|
| NATIVE_ASM | BCPLMAIN, BCPLIO, BCPLMEM, BCPLBYTE, BCPLAPT | Exactly five canonical Git `.asm` sources |
| NATIVE_JCL | BLDDEVI and optional BLDDEVM6 | BLDDEVI manifest-mapped; historical BLDDEVM6 is staged explicitly, not manifest-populated |
| NATIVE_OBJ | BCPLMAIN, BCPLMEM, BLIB | Rebuild using BLDBMAIN and BLIBBLD in base gates; **no copying old object records** |
| NATIVE_DEVOBJ | BCPLM6, BCPLIO, BCPLBYTE, BCPLAPT | Build through the resident IFOX/IEBGENER jobs; no PROD OBJ promotion |

The candidate regression linker includes **BCPLM6 and BCPLIO
from NATIVE_DEVOBJ**, **BCPLMEM and BLIB from NATIVE_OBJ**
and **BCPLBYTE and BCPLAPT from NATIVE_DEVOBJ**.
This mixed object resolution is intentional: the DEVOBJ flag
names the candidate runtime *library profile*, not an instruction
to migrate all accepted OBJ members.

### B. Build and verify the two candidate modules in the clean PDS

Only after the complete base compiler/runtime stack has been
rebuilt as above, use the Git-controlled sources and job bodies:

```sh
# Review the checked-in source and target dataset identities first:
git rev-parse HEAD
tools/datasets/dspal info
tools/datasets/dspal ls NATIVE_ASM
tools/datasets/dspal ls NATIVE_JCL

# Install source text (not binary object records):
tools/datasets/dspal put NATIVE_ASM BCPLMAIN \
  native-compiler/asm/bcplmain.asm
tools/datasets/dspal put NATIVE_ASM BCPLIO \
  native-compiler/asm/bcplio.asm

# Explicitly install the current, approved build JCL bodies:
tools/datasets/dspal put NATIVE_JCL BLDDEVM6 \
  native-compiler/jcl/build-dev-bcplm6.jcl
tools/datasets/dspal put NATIVE_JCL BLDDEVI \
  native-compiler/jcl/build-dev-bcplio.jcl

tools/datasets/dspal submit NATIVE_JCL BLDDEVM6
tools/datasets/dspal submit NATIVE_JCL BLDDEVI
tools/datasets/dspal ls NATIVE_DEVOBJ
```

**For BLDDEVM6:** require *payload* ASMMMAIN (IFOX)
RC0000, PUTMAIN (IEBGENER) RC0000 and DEVOBJ(BCPLM6).
**For BLDDEVI:** require *payload* ASMIO (IFOX)
RC0000, PUTIO (IEBGENER) RC0000 and DEVOBJ(BCPLIO).
Confirm zero flagged assembler errors, inspect the
submitted job's real PDS source/output DSNs and do not
accept a good RC from a stale job targeting retired
libraries. Launcher job completion is not sufficient.

The job sources write only **NATIVE_DEVOBJ**, not NATIVE_OBJ.
Verify that `NATIVE_OBJ(BCPLMAIN,BCPLMEM,BLIB)` remains
the base accepted runtime; never reassemble or silently
promote BCPLM6 into NATIVE_OBJ at this gate.

### C. Candidate preflight, focused smoke, and complete panel

```sh
export BCPL_RUNTIME_PDS=1
export BCPL_RUNTIME_LIBRARY=DEVOBJ
export BCPL_RUNTIME_CANDIDATE=1
export BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6

# Does not submit MVS jobs:
python3 tools/checks/check-m44-compatibility.py --candidate
python3 tools/checks/check-bcplio-m43-account.py
tools/native/run-regression --check-numbering

# Actual MVS execution; verify the resulting job reports:
tools/native/run-regression 124 --show-output
tools/native/run-regression 128 129
tools/native/run-regression 131 133

# M5.5: run only when the final full-panel gate is authorized:
tools/native/run-regression 0 145
python3 tools/checks/check-m44-full-panel-logs.py
```

The `0 145` runner range is inclusive, covering
146 numbered cases, of which 083 is a deliberate
source-only skip and 048 is compile-only. The accepted
M4.4 **historical measured result** was **145 PASS /
0 FAIL / one expected SKIP 083**, and 145/145 saved
logs passed the corrected read-only audit. Under the
BCPLM6/D6 candidate, 052 and 093 have separate
`expected-go-rc-bcplm6.txt` fixtures because
their intended GO RC0000 differs from the D7 profile.
Case 129 and case 141 use intentional nonzero STOP
termination statuses; the harness determines acceptance
against each case's profile, **not by demanding every
GO step RC0000**.

**Neither the documented commands nor the preceding
M5.3 review counts as a fresh M5.5 run.** A newly
performed full sweep must include its own JES job IDs,
step RC and saved report/log evidence before M5.5 closes.

### D. Physical QSAM proof and experimental JCL (existing results)

The ordinary regression runner uses combined JES
reports for *logical* fixture comparisons; this is
not an exact byte-level observation of individual
QSAM output datasets. The separate limited experiments
verified the boundary once without adding an API:

| Probe | Input and physical output | Actual evidence |
|---|---|---|
| M5.1.1 | Native case 114 and split SYSOUT A/Z classes | JOB 8184: two observed printer routes, RC0 |
| M5.1.2 | Native case 124 linked to separate temporary REPORT and REPORT2 FB132 datasets, followed by assembler QSAM GET/CLC(132) | JOB 8185: all six steps RC0000, complete records/count/EOF |
| M5.2 | Exact positive case-124 JCL with only one wrong **verifier expectation** at EBCDIC pad offset 131 | JOB 8186: first five steps RC0000, VCHK **RC0012 intentionally** |

The source and offline review commands remain in
`tools/checks/m51-fb132-dataset-probe.py` and
`tools/checks/m52-padding-negative.py`
and their plans. They generate files under
`workarea/native-regression/124-dynamic-dd-selected-output/`;
**never submit a negative probe without verifying
its intended nonzero RC and JOB name**. Do not
rerun the three already accepted jobs to count
M5.4 as complete. Their experimental JCL is not
part of the ordinary regression runner by default.

### E. Capture a new full reconstruction or M5.5 acceptance record

At minimum, keep the Git commit, effective manifest
mapping (no secrets), whether workarea/PDS purging was
actually performed, generated bootstrap SHA-256,
ICINT19/MR10 suite JOB evidence, TRNILRG and
CAMBCOMP rebuild and interpreted CODE=0 checks,
BLIB and runtime build payload JOBs and RCs,
DEVOBJ(BCPLM6/BCPLIO) member inventory,
candidate environment, compiler/IFOX/IEWL/GO
results, native test summary, 145/145 log audit,
and known limitations.

**Do not claim from-scratch completeness merely
because a normal incremental rebuild works.**
The base runbook's destructive purge has *not*
been newly exercised as an M5.4 proof. In normal
development **do not run purgebcpl** or delete
`workarea/` just to validate documentation.
When a truly clean-room reconstruction is desired,
the operator must explicitly authorize and protect
any non-reproducible managed PDS content first.
M5.4 changes only documentation; M5.5 is the
fresh candidate execution/final acceptance gate.


## 11. M5.5 final fresh full panel (operator execution required)

For the precise non-destructive final acceptance procedure, follow
[M5.5 final acceptance gate]
(bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream-M5.5-plan.md).
Unlike the historical M4.4 log auditor alone, the
M5.5 check snapshots prior logs **before** the full
run and requires 145 new case logs plus an exact
145 PASS / 0 FAIL / 1 expected SKIP 083 transcript.
**M5.5 accepted and CLOSED by the project owner on 2026-10-17** after a fresh 145 PASS / 0 FAIL / expected SKIP 083 DEVOBJ run and successful 145/145 log audit. See the [final milestone acceptance record](bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream-final-acceptance.md) for the important subsequent interrupted-repeat/evidence caveat. This accepted incremental run does **not** mean the complete destructive clean-room purge/rebuild procedure in this document has been executed as one new end-to-end experiment. No clean-room PDS purge, OBJ promotion, or new runtime/JCL build is implied.
