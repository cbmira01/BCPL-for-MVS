# Clean-room MVS reconstruction — full native OBJ runtime

**Current objective (17 October 2026):** rebuild the *entire project-managed*
MVS PDS environment from Git and historical source, starting with an empty
ignored `workarea/`, then assemble **all five canonical runtime modules
and freshly compiled BLIB into `NATIVE_OBJ`**. The result is intended to
run the entire native regression panel **00..145 from OBJ alone**.

**Authority:** the owner explicitly requested an all-OBJ rebuild with the
latest canonical source. This supersedes the historical pre-D6 production
source hold. It is *not* a claim that the new production build or regression
has already passed. Only the earlier DEVOBJ(BCPLM6) dynamic-stream panel
has measured 145 PASS, 0 FAIL, 1 expected SKIP (083).

## Scope and destructive boundary

- `dspal purgebcpl` removes **the 24 datasets explicitly managed by
  `config/dspal.yaml`**, not SYS1 system datasets, TK5 installation files,
  all MVS DASD volumes, or any other guest datasets. Review its exact list
  before responding `YES`. This also deletes user-created content in
  managed PDSes, so inspect anything worth retaining first.
- Remove only repository-root `workarea/` (ignored generated artifacts);
  preserve any uncommitted evidence before deleting it.
  **Never delete `mvs-state/`, the DASD images, `docker/`,
  historical Git source, or `config/dspal.local.yaml`.**
- A new `NATIVE_OBJ` begins empty and is rebuilt *from source*.
  No `SEEDDEV`, copying old FB80 objects, importing INTCODE,
  or migrating previous load libraries.
- `NATIVE_DEVOBJ` remains part of the managed dataset inventory
  but is intentionally unused and empty after the clean rebuild.
- Run the commands from the repository root on the host with
  Hercules/TK5 and JES available. Inspect every **payload** JES job
  and step RC, not only the outer `dspal submit` launcher.
- Ensure a clean Git checkout at a recorded revision, a correct MVS HLQ,
  and a functioning local JES reader before the destructive operation.
  Local overrides and MVS credentials are private.

## Ordered reconstruction

| Stage | Work | Expected result |
|---|---|---|
| 0 | Check Git, TK5, source inputs and build contracts | Validated starting point |
| 1 | Remove disposable `workarea/`, regenerate inputs | Fresh host-generated demotions |
| 2 | Purge, initialize and repopulate managed PDSes | Empty binary libraries; tracked text staged |
| 3 | Assemble/link ICINT19 from MR10 source | `MR10_LOAD(ICINT19)` |
| 4 | Verify MR10 interpreted examples | Compiler and interpreter sanity |
| 5 | Rebuild enlarged translator INTCODE | `NATIVE_INTCODE(TRNILRG)` |
| 6 | Stage demoted Cambridge sources, build CAMBCOMP | `NATIVE_INTCODE(CAMBCOMP)` |
| 7 | Assemble all five latest canonical runtime modules | Five `NATIVE_OBJ` members |
| 8 | Compile and assemble BLIB from BCPL source | `NATIVE_OBJ(BLIB)` |
| 9 | Run production-only 00..145 regression panel | Target 145 PASS/0 FAIL/1 SKIP |

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
python3 tools/checks/check-native-production-build.py
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

The host-side stage regenerates demoted `blib`, `bcpl`, `syn`, `lex`, `trna`, `trnb`, `cga`–`cge`, the diagnostic demotions, and seven large-name MR10 translator sections plus their header (24 generated output files total). This **reconstructs source inputs**, not an executable resident compiler. The enlarged `TRNILRG` INTCODE image is built **after** ICINT19 is available. Retain the generated SHA-256 manifest as host-side provenance.

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
  native-compiler/jcl/cambbld.jcl
tools/datasets/dspal submit NATIVE_JCL CAMBBLD
tools/datasets/dspal ls NATIVE_INTCODE
```

`stage-bootstrap` puts 14 members: `BLIB`, 10 demoted Cambridge compiler units, `BOOTHOST`, `OPTIONS`, and `CAMBPARM`. Headers (`LIBHDR`, `SYNHDR`, `TRNHDR`, `CGHDR`) were populated from Git in gate 2. The authoritative resident build is `native-compiler/jcl/cambbld.jcl`; it uses `MR10_LOAD(ICINT19)`, `MR10_SOURCE`, `NATIVE_INTCODE(TRNILRG)`, and `NATIVE_SOURCE`. It contains 22 interpreter executions plus a PACKCOMP step. Require `CODE=0` for **all 22** interpreted phases (not merely each step's `RC=0000`) and verify `NATIVE_INTCODE(CAMBCOMP)` and the constituent units. No `CAMB_*` library is used.

Smoke-test compilation using the resident image:

```sh
tools/native/compile-mvs \
  native-compiler/regression/00-most-degenerate-bcpl-program/source.bcpl \
  --output workarea/m3-clean-smoke.s370.asm
test -s workarea/m3-clean-smoke.s370.asm
```

Look for generated `CSECT`, `EXTRN BCPLMAIN`, and `END` cards. `compile-mvs` verifies interpreted execution code.

## 7. Build all five canonical assembler modules into NATIVE_OBJ

The authoritative source-to-member mapping is `config/dspal.yaml`.
After `dspal populate all`, `NATIVE_ASM` must contain exactly:
`BCPLMAIN`, `BCPLIO`, `BCPLMEM`, `BCPLBYTE`, `BCPLAPT`.
These map to `native-compiler/asm/<lowercase-member>.asm` with no
versioned or historical source aliases. The canonical BCPLMAIN is
the D6/M5.5 source accepted in the dynamic-stream milestone.

**This is a deliberate source-based production build**. The previous
DEVOBJ-only policy no longer applies to this new clean-room target.

```sh
python3 tools/checks/check-native-production-build.py
tools/datasets/dspal ls NATIVE_ASM
tools/datasets/dspal ls NATIVE_JCL
tools/datasets/dspal ls NATIVE_OBJ

# All five modules: one MVS job, five IFOX assemblies and five
# gated IEBGENER FB80 object installs. No host-side object copying.
tools/datasets/dspal submit NATIVE_JCL BLDBMAIN
tools/datasets/dspal ls NATIVE_OBJ
```

The canonical `native-compiler/jcl/bldbmain.jcl` installs these
objects **only after each preceding assembly and installation
succeeded with RC=0000**:

| Git source | Assembler step | Production member |
|---|---|---|
| `bcplmain.asm` | ASMMMAIN | `NATIVE_OBJ(BCPLMAIN)` |
| `bcplmem.asm` | ASMMMEM | `NATIVE_OBJ(BCPLMEM)` |
| `bcplbyte.asm` | ASMMBYTE | `NATIVE_OBJ(BCPLBYTE)` |
| `bcplapt.asm` | ASMMAPT | `NATIVE_OBJ(BCPLAPT)` |
| `bcplio.asm` | ASMMIO | `NATIVE_OBJ(BCPLIO)` |

Check all five assembly RCs and all five binary-install RCs.
Stop if any step failed; the job is **not transactionally atomic**.
Before going on, prove five members actually exist and were installed
in `NATIVE_OBJ`, not the old retired `HERC02.BCPL.OBJ` or `DEVOBJ`.

## 8. Build the current BLIB from source into NATIVE_OBJ

```sh
tools/datasets/dspal submit NATIVE_JCL BLIBBLD
tools/datasets/dspal ls NATIVE_OBJ
```

The canonical `native-compiler/jcl/blibbld.jcl` uses resident
`ICINT19` and `CAMBCOMP` to translate demoted BCPL `BLIB`
source into native System/370 code, applies the narrow documented
CG370 card repairs, assembles it with IFOX and uses IEBGENER
to install **`NATIVE_OBJ(BLIB)`**.

Inspect the payload steps `COMP`, `PREPASM`, `PREPLK`,
`FIXASM`, `ASMBLIB` and `INSTALL`. Require each expected
RC=0000 and interpreted `CODE=0` where applicable. Do not treat
a successful assembler alone as proof of the BLIB build.

The final production object inventory must contain **all six**:
`BCPLMAIN`, `BCPLIO`, `BCPLMEM`, `BCPLBYTE`,
`BCPLAPT`, and `BLIB`. No old binary is copied into that set.

## 9. Run the complete native regression against NATIVE_OBJ

The regression launcher has an explicit full-production profile:
`tools/native/run-production-regression` sets
`BCPL_RUNTIME_PDS=1`, `BCPL_RUNTIME_LIBRARY=OBJ`, and disables
all versioned candidate-member selectors. It causes IEWL to
`INCLUDE OBJ(...)` for the five runtime modules **and BLIB**.
The historical `DEVOBJ(BCPLM6)` profile remains available for
comparison but is not used in this rebuild.

The newer dynamic-stream tests (124..145) are permitted in
this **full-OBJ profile**. Private fault-instrumented BCPLIO is
assembled only inside the corresponding GO job, without writing
back to the canonical `BCPLIO` object. D6-controlled failures
in cases 052 and 093 continue to expect GO RC0000, not the
different historical D7 RC0012.

```sh
# Static; does not submit MVS jobs:
python3 tools/checks/check-native-production-build.py
env -u BCPL_RUNTIME_CANDIDATE_MEMBER \
    BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=OBJ \
    BCPL_RUNTIME_CANDIDATE=0 \
    python3 tools/checks/check-m44-compatibility.py --production
tools/native/run-production-regression --check-numbering

# MVS compile, assemble, link and GO proof:
tools/native/run-production-regression 0 --show-output
tools/native/run-production-regression 52
tools/native/run-production-regression 93
tools/native/run-production-regression 124 --show-output
tools/native/run-production-regression 139 145

# Run the complete, inclusive 146-case panel:
tools/native/run-production-regression 0 145

# Independently audit saved per-case JES outcome logs:
python3 tools/checks/check-m44-full-panel-logs.py
```

**Target, not yet measured on the new OBJ build:**
145 PASS / 0 FAIL / one source-only SKIP 083 among
146 numbered cases. Case 048 is deliberately compile-only
but counts as PASS when compilation succeeds.
The log audit expects 145 independently PASS case logs, correct
GO return codes, successful IFOX/IEWL, and no unresolved ABEND
signatures. A named class/routing receipt from M5.5 is evidence
of the older DEVOBJ milestone, not a substitute for this new run.

## 10. Capture the new clean-room acceptance record

Record the Git commit and effective `dspal.yaml`, the inspected
deletion inventory, the purge/allocate/populate payload JOBs,
recreated `MR10_LOAD(ICINT19)`, fresh TRNILRG and CAMBCOMP,
interpreted CODE=0 checks, the ten BLDBMAIN and six BLIBBLD
payload step RCs, the six-member `NATIVE_OBJ` inventory,
each focused regression result, the full-panel summary and its
145/145 log audit. Protect credentials and raw MVS data.

The **new complete purge-to-OBJ procedure has not yet been executed
or verified end-to-end**. Do not mark it accepted solely because
this source-and-tooling commit exists. The previously accepted
[BCPLIO dynamic-stream milestone](bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream-final-acceptance.md)
documents the earlier DEVOBJ results, not the new production result.
