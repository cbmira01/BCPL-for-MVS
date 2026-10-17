# Clean-room MVS reconstruction — full native OBJ runtime

**Current objective (17 October 2026):** rebuild the *entire project-managed*
MVS PDS environment from Git and historical source, starting with an empty
ignored `workarea/`, then assemble **all five canonical runtime modules
and freshly compiled BLIB into `NATIVE_OBJ`**. The result is intended to
run the entire native regression panel **00..145 from OBJ alone**.

**Authority:** the owner explicitly requested an all-OBJ rebuild with the
latest canonical source. This supersedes the historical pre-D6 production
source hold. The complete source-based production reconstruction was accepted
on 17 October 2026 against baseline commit 04c74af8b07b5cdc2aaec44d79f020a848cb7e65,
with 145 PASS, 0 FAIL, and 1 expected SKIP (083).

**Procedure revision:** the manifest-driven two-pass population sequence below
replaces the procedure used for that acceptance run. The historical acceptance
record remains valid, but this revised sequence has not yet been executed
end-to-end on a freshly purged MVS environment.

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
| 1 | Safely empty disposable `workarea/` | Clean host build directory; tracked placeholder retained |
| 2 | Purge, initialize and run first manifest population | Tracked sources installed; missing generated sources reported with nonzero status |
| 3 | Assemble/link ICINT19 from MR10 source | `MR10_LOAD(ICINT19)` |
| 4 | Verify MR10 interpreted examples | Compiler and interpreter sanity |
| 5 | Generate all bootstrap artifacts and repeat manifest population | Demoted Cambridge sources and `NATIVE_INTCODE(TRNILRG)` installed |
| 6 | Build CAMBCOMP from populated source and INTCODE | `NATIVE_INTCODE(CAMBCOMP)` |
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

## 1. Clean only disposable host-generated files

```sh
# Requires typing DELETE; preserves the Git-tracked workarea/.gitignore.
tools/clean-workarea
```

Do not delete the workarea placeholder: Git tracks `workarea/.gitignore`
to create the directory on a fresh clone. The clean-room compiler artifacts
will be generated after rebuilding the interpreter in stage 3. Retain any
prior host-side evidence needed for review *before* authorizing cleanup.

## 2. Purge, initialize, and populate currently ready managed sources

```sh
# INSPECT THE EXACT DELETE DECK BEFORE AUTHORIZING DELETION.
tools/datasets/dspal purgebcpl --show-jcl
tools/datasets/dspal purgebcpl    # requires explicit YES

tools/datasets/dspal initbcpl --show-jcl
tools/datasets/dspal initbcpl
tools/datasets/dspal stat
tools/datasets/dspal populate all --dry-run  # expected RC=2: generated files missing
tools/datasets/dspal populate all            # expected RC=2: tracked members installed
tools/datasets/dspal ls
```

**The first population is intentionally incomplete and returns RC=2.** Unlike
ordinary preflight failures, *missing generated sources* are reported after
the available tracked members have been populated. Confirm the summary says
the expected generated files are missing, and verify that the tracked MR10
and native source/JCL members exist. Do not suppress or ignore other error
messages: invalid mappings, missing tracked sources, malformed FB80 records,
or stale generated-file hashes stop population before writes. A failed JES
installation is also a hard failure and must be investigated.

The initial binary libraries (including `MR10_LOAD`, `MR10_OBJ`,
`NATIVE_OBJ`, `NATIVE_DEVOBJ`, and `NATIVE_INTCODE`) remain empty.
No old binary images may be copied into them. The manifest lists **24
managed datasets**; both tracked and generated member mappings reside in
`config/dspal.yaml`. The first pass installs the tracked mappings only.

**Do not chain the first population to subsequent commands with `&&` or
use a blanket `set -e` wrapper.** Its nonzero status is deliberate and
must be inspected, not disguised as a successful complete population.

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

## 5. Regenerate all bootstrap inputs and populate them through dspal

```sh
tools/native/prepare-bootstrap --with-trnilrg
cat workarea/bootstrap-cambridge/prepare-bootstrap-manifest.json
tools/datasets/dspal populate all --dry-run
tools/datasets/dspal populate all
tools/datasets/dspal ls NATIVE_SOURCE
tools/datasets/dspal ls NATIVE_INTCODE
```

The single `prepare-bootstrap --with-trnilrg` invocation generates all
11 demoted Cambridge sources, five diagnostic demotions, the enlarged
MR10 translator sections, and the assembled `TRNILRG` INTCODE image
using freshly installed `MR10_LOAD(ICINT19)`.

The second `dspal populate all` must complete **RC=0**, restoring the
tracked member mappings and installing the 11 demoted Cambridge members
into `NATIVE_SOURCE` plus `NATIVE_INTCODE(TRNILRG)`. Generated source
integrity is checked against the preparation SHA-256 inventory, including
its tracked inputs. A missing or stale generated artifact is an error.
There is no separate `stage-bootstrap` operation or manual `dspal put`
for `TRNILRG`.

## 6. Build CAMBCOMP from the manifest-populated sources

```sh
python3 tools/checks/check-native-bootstrap-jcl.py
tools/datasets/dspal submit NATIVE_JCL CAMBBLD
tools/datasets/dspal ls NATIVE_INTCODE
```

`CAMBBLD` and the three tracked bootstrap inputs `BOOTHOST`,
`OPTIONS` and `CAMBPARM` are already populated through the manifest.
The resident build `native-compiler/jcl/cambbld.jcl` uses
`MR10_LOAD(ICINT19)`, `MR10_SOURCE`, `NATIVE_INTCODE(TRNILRG)`
and `NATIVE_SOURCE`. It contains 22 interpreter executions plus a
PACKCOMP step. Require `CODE=0` for **all 22** interpreted phases
(not merely each step's `RC=0000`) and verify `NATIVE_INTCODE(CAMBCOMP)`
and its constituent units. No `CAMB_*` library is used.

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

**Measured on 17 October 2026 on the new OBJ build:**
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

The **complete purge-to-OBJ procedure was executed and verified
end-to-end on 17 October 2026**. See the
[acceptance record](clean-room-mvs-reconstruction-acceptance-2026-10-17.md). The previously accepted
[BCPLIO dynamic-stream milestone](bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream-final-acceptance.md)
documents the earlier DEVOBJ results, not the new production result.
