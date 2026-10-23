# Rebuild BCPL for MVS from source

> **Core Runtime installation hold (R.5):** The revised seven-assembler-
> object `BLDBMAIN` and the production linker recipe implement the
> approved registration-enabled eight-member `BOOT_OBJ` design.
> Design and source approval does **not** authorize installation.
> Do not submit `BLDBMAIN` to update `BOOT_OBJ` until the owner
> separately approves those permanent MVS writes and reviews the
> reconstruction/recovery procedure. `BOOT_DEVOBJ` remains untouched.
> See `bootstrap-toolchain/asm/README.md`.

**Operator guide — Hercules / MVS 3.8J / TK5**

This guide shows how to rebuild the BCPL tools and native runtime on a working
MVS 3.8 system. Follow the steps in order. Check each result before moving on.

**What you will get:** a working BCPL interpreter, the demoted Cambridge
bootstrap compiler running under that interpreter, eight production object
members, and a tested system. The bootstrap compiler generates System/370
assembler; it does not execute as native machine code.

**Scope:** this guide rebuilds the interpreter-hosted bootstrap toolchain in
`bootstrap-toolchain/`. It does **not** build the separate native Cambridge
compiler being developed in `cambridge-compiler/`.

**Important:** this is a clean rebuild of the **BCPL project data sets inside
MVS**. It is not a guide to installing Linux, Docker, Hercules, or TK5 from
nothing. Those must already be set up.

## Before you begin

### What the names mean

| Term | Plain meaning |
| --- | --- |
| **BCPL** | The programming language we are rebuilding. |
| **MVS** | The IBM operating system that runs inside Hercules. |
| **Hercules / TK5** | The emulator and MVS 3.8J system used for this project. |
| **PDS** | An MVS data set that holds named members, much like files in a folder. |
| **JCL** | Instructions that tell MVS which programs or build steps to run. |
| **JES job** | A batch job sent to MVS. Each job has a number and a result. |
| **`dspal`** | Our tool for creating, filling, listing, and deleting the BCPL PDSes. |
| **`ICINT19`** | The interpreter that runs the early BCPL compiler's INTCODE. |
| **INTCODE** | The intermediate code used during the BCPL bootstrap. |
| **`TRNILRG`** | A larger-name translator image needed to build the demoted Cambridge bootstrap compiler. |
| **Demoted Cambridge compiler** | The interpreter-hosted bootstrap compiler that generates native System/370 assembler. |
| **`CAMBCOMP`** | The demoted Cambridge compiler image, stored as INTCODE and executed by `ICINT19`. |
| **Native Cambridge compiler** | The separate target in `cambridge-compiler/`: a compiler that itself executes as a native MVS program. This guide does not build it. |
| **`BOOT_OBJ`** | The PDS that holds the six finished, native object modules. |
| **RC / CODE** | A job step's return code / the BCPL interpreter's own completion code. Check both. |

### What is kept, and what is erased?

This process **deletes data**. Read this table first.

| Area | What happens | What you must know |
| --- | --- | --- |
| `workarea/` on Linux | Its contents are deleted | Save any build logs or evidence you need first. |
| `workarea/.gitignore` | **Kept** | Git tracks this file so `workarea/` exists after a fresh clone. |
| 28 BCPL PDSes listed in `config/dspal.yaml` | **Deleted and rebuilt** | Any personal files in these managed PDSes will be lost. |
| `BOOT_OBJ` | Recreated empty, then rebuilt | Do not copy old binary objects into it. |
| `BOOT_DEVOBJ` | Recreated empty | Leave it empty during the production rebuild. |
| `mvs-state/`, DASD images, TK5 system files | **Kept** | Never erase these as part of this guide. |
| Git source, `docker/`, `config/dspal.local.yaml` | **Kept** | The local config may contain credentials. Never paste them into logs or commits. |

The purge command works only on the data sets named in the **effective**
`dspal` configuration. First check the high-level qualifier (HLQ) and the
full delete list. It does **not** erase IBM system data sets or the whole
MVS disk.

### One source of truth for PDS content

`config/dspal.yaml` says which host file goes into each MVS PDS member.
It has two kinds of input:

| Kind | Example | When it exists |
| --- | --- | --- |
| Git-tracked | `mr10-kit-compiler/asm/icintv19.asm` | Right after clone |
| Generated | `workarea/bootstrap-cambridge/demoted/syn` or `trni-large-names.int` | After we run the bootstrap generator |

We run **`dspal populate all` twice**. On the first pass it installs what
already exists. On the second pass it adds the files we generated. The same
manifest controls both passes.

There is **no `stage-bootstrap` step** and no manual `dspal put` for
`TRNILRG` or `CAMBBLD` in this rebuild.

### Build map

| Step | Task | Good result |
| --- | --- | --- |
| 0 | Check Git, MVS, and settings | Ready to start |
| 1 | Clean `workarea/` | Empty except for `.gitignore` |
| 2 | Purge and recreate the BCPL PDSes; first populate | Tracked source installed; generated files still missing |
| 3 | Build `ICINT19` | Installed, working interpreter |
| 4 | Run the MR10 examples and tests | All resident suites pass |
| 5 | Generate demoted Cambridge bootstrap sources and `TRNILRG`; second populate | All mapped members installed |
| 6 | Build and test interpreted `CAMBCOMP` | Bootstrap compiler produces System/370 assembler |
| 7 | Assemble six Core Runtime modules and empty BCPLREG | Seven members in `BOOT_OBJ` |
| 8 | Compile and assemble `BLIB` | Eight members in `BOOT_OBJ` |
| 9 | Run native regression tests | 145 PASS, 0 FAIL, 1 expected SKIP |
| 10 | Save the evidence | Results and limits recorded |

> **Status:** A full clean-room rebuild was accepted on **17 October 2026**
> using source baseline `04c74af8b07b5cdc2aaec44d79f020a848cb7e65`.
> See the [acceptance record](clean-room-mvs-reconstruction-acceptance-2026-10-17.md).
> The *two-pass manifest procedure in this guide* was added **after** that
> acceptance. It has **not yet passed a new end-to-end clean-room test**.
> Do not claim it has until that test is done.

## Step 0 — Check the system

Open a shell on the Linux host. Work from the repository root.

```sh
cd ~/Source/Repos/BCPL-for-MVS

git status --short
git pull --ff-only
git rev-parse HEAD

tools/mvs/start-tk5 --detached
tools/datasets/dspal status --probe
tools/datasets/dspal info
tools/bootstrap/prepare-bootstrap --check-inputs
```

**Check before going on:**

- Git has no unexpected changes. Note the full commit ID.
- Docker/Hercules and the JES card reader are ready.
- The `dspal` settings point to the **right** MVS system and HLQ.
- The input check finds the tracked source files.
- The private `config/dspal.local.yaml` has the needed MVS login settings.
  Never print the password in a public report.

A command error must be understood before you continue.

## Step 1 — Clean the host work area

This deletes generated files and earlier test logs, **not** Git source or
MVS data sets.

```sh
# Review the items shown. Type DELETE only if you want to erase them.
bash tools/clean-workarea

git status --short
```

The tool is interactive. It shows what will be removed, requires the exact
word `DELETE`, and keeps `workarea/.gitignore`. It refuses to run if
other tracked files are under `workarea/`.

**Check:** `workarea/` still exists, and `workarea/.gitignore` is still
there. The Git working tree has no new changes.

Do **not** use `rm -rf workarea`. That removes the tracked file that makes
this directory appear in a fresh clone.

## Step 2 — Rebuild the managed PDS layout

### 2A. Review and purge the BCPL data sets

```sh
# Show the proposed delete job. This does not delete anything.
tools/datasets/dspal purgebcpl --show-jcl

# The real purge asks you to type YES.
tools/datasets/dspal purgebcpl
```

**Stop and read the list before typing `YES`.** The purge removes the
managed BCPL PDSes and their contents. Do not run it if any of them holds
data you still need.

**Check:** the purge reports which data sets were deleted and the JES job
number. Save the result.

### 2B. Create new empty PDSes

```sh
tools/datasets/dspal initbcpl --show-jcl
tools/datasets/dspal initbcpl
tools/datasets/dspal stat
```

**Check:** all **28** managed data sets exist with the expected record
formats. The binary libraries start empty. The MVS system data sets and
the host's DASD images are unchanged.

### 2C. First population: install the Git-tracked files

```sh
# Preview the ready files. No PDS writes.
tools/datasets/dspal populate all --dry-run

# Install the available files into MVS.
tools/datasets/dspal populate all

# Look at the new member lists.
tools/datasets/dspal ls MR10_SOURCE
tools/datasets/dspal ls MR10_JCL
tools/datasets/dspal ls MR10_ASM
tools/datasets/dspal ls BOOT_SOURCE
tools/datasets/dspal ls BOOT_JCL
tools/datasets/dspal ls EXT_MAC
tools/datasets/dspal ls EXT_ASM
tools/datasets/dspal ls EXT_SOURCE
tools/datasets/dspal ls EXT_OBJ
```

**R.5 extension check:** `EXT_MAC` contains `BCXPRE`, `BCXCAT`, and
`BCXPOST`; `EXT_ASM` contains `BCPLDEMO`; and `EXT_SOURCE` contains
`DEMOHDR`. `EXT_OBJ` must still be empty at this stage: its binary
`BCPLDEMO` object is built and installed separately on MVS, not by
`dspal populate all`.

**The first population is meant to end with RC=2.** That does **not** mean
it installed nothing. At this point, the 11 demoted Cambridge sources and
`TRNILRG` do not exist yet, so the tool reports **12 missing generated
members** after writing the ready tracked members.

Check the output carefully:

| Output | Meaning | Action |
| --- | --- | --- |
| `populate completed: ... ready member(s) written` and 12 `MISSING GENERATED` entries | Expected first pass | Check that the tracked members are in MVS, then continue |
| Missing Git-tracked source, bad record length, duplicate member, stale hash | Real preflight problem | Fix it; do not continue |
| JES job failed, a required data set is absent, or a member was not written | Real installation problem | Fix it; do not continue |
| RC=0 on a fresh, empty workarea | Unexpected for this stage | Check whether old generated files remain or the manifest has changed |

**Important:** verify the **reason** for RC=2. Do not automatically treat
every RC=2 as success. Do not run this stage in a shell chain that requires
each command to return zero, such as one long `&&` chain or `set -e` script.

The finished first pass must leave the interpreter's tracked assembler,
JCL, and input files ready. It must **not** restore old INTCODE, object, or
load modules from another machine.

## Step 3 — Rebuild the interpreter

```sh
tools/datasets/dspal submit MR10_JCL IC19BLD
tools/datasets/dspal ls MR10_LOAD
tools/datasets/dspal ls MR10_OBJ
```

This builds `ICINT19` from assembler source, then installs it. The build
uses IBM assembler and link-edit tools.

**Check:** the job steps `ASM`, `LKED`, and `SAVEOBJ` all finish with
`RC=0000`. Both `MR10_LOAD` and `MR10_OBJ` contain `ICINT19`.

Now make sure the newly installed interpreter can run a BCPL program:

```sh
tools/mr10/compile-and-run --installed-icint MR10_LOAD --results \
  mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.bcpl
```

**Check:** the program's output is correct and the interpreter reports
`CODE=0`. A good JES step RC by itself is not enough.

### How to read an MVS job report

`dspal submit` runs a short **launcher job** and then the real **payload
job**. It prints both job numbers. The payload is the one to inspect.

Use the payload number shown on your machine in place of `NNNN`:

```sh
tools/mvs/job-summary NNNN
tools/mvs/dump-report-for-job NNNN
```

Check the steps and their RC values. In the full report, also look for
interpreter `CODE=0` messages and the program's actual output. Do not
assume that the launcher completing means that the real job passed.

## Step 4 — Test the new interpreter

The project includes three groups of test and example programs. These
jobs run inside MVS using the installed interpreter.

```sh
tools/datasets/dspal submit MR10_JCL MRLANGDM
tools/datasets/dspal submit MR10_JCL MRBCDEMO
tools/datasets/dspal submit MR10_JCL MRREGRES
```

| Job member | What it tests | Programs |
| --- | --- | ---: |
| `MRLANGDM` | Basic BCPL language features | 11 |
| `MRBCDEMO` | Complete BCPL example programs | 17 |
| `MRREGRES` | MR10 compiler/runtime regression cases | 12 |

**Check:** inspect the **payload** reports. Check step return codes,
`CODE=0` lines, output, and error messages. All three suites must pass
before you build the demoted Cambridge bootstrap compiler.

**Limit:** these resident suites do **not** automatically compare their
output with every checked-in `.expected` file. Other host-side test runners
can make those comparisons, but they may build an interpreter from source
rather than use the installed `ICINT19`. These are different kinds of
evidence; do not treat them as the same test.

See `mr10-kit-compiler/jcl/README-SUITES.md` for more about the suites.

## Step 5 — Make the demoted Cambridge bootstrap files

The full `TRNILRG` image needs a running `ICINT19`. That is why this step
comes **after** Steps 3 and 4, not before the first population.

### 5A. Generate all bootstrap inputs in one pass

```sh
tools/bootstrap/prepare-bootstrap --with-trnilrg
cat workarea/bootstrap-cambridge/prepare-bootstrap-manifest.json
```

This one command makes:

- 11 demoted Cambridge BCPL source units, including `BLIB`.
- Five *diagnostic* code-generator source units (saved for optional work).
- The split MR10 translator source units.
- One compiled translator image: `trni-large-names.int`, for `TRNILRG`.
- A JSON inventory with SHA-256 file hashes.

The diagnostic units are **not** part of the normal compiler or its
production object build.

**Check:** the generator finishes successfully. The JSON manifest says
`"trnilrg_rebuilt": true`, and the compiled image exists and is not
empty. Inspect the interpreted jobs for success and `CODE=0`.

### 5B. Second population: install the generated files

```sh
tools/datasets/dspal populate all --dry-run
tools/datasets/dspal populate all

tools/datasets/dspal ls BOOT_SOURCE
tools/datasets/dspal ls BOOT_INTCODE
```

**This pass must return RC=0.** It installs every mapped source file
again, plus the generated members that were missing the first time.

| PDS | What should now be there |
| --- | --- |
| `BOOT_SOURCE` | Four headers, `BOOTHOST`, `OPTIONS`, `CAMBPARM`, and 11 demoted Cambridge source units |
| `BOOT_INTCODE` | `TRNILRG`; the compiler will be added next |
| `BOOT_JCL` | The Git-tracked `CAMBBLD` build job, already present from the first pass |

`dspal` checks generated files against the saved hashes and checks the
tracked inputs used to make them. If a file is missing, changed, or not
listed in the inventory, correct the source or rerun the generator.
Do **not** copy an old image from another PDS.

There is no second installation map in Python: `config/dspal.yaml` is the
only source-to-PDS map for this stage.

## Step 6 — Build the demoted Cambridge bootstrap compiler

```sh
tools/datasets/dspal submit BOOT_JCL CAMBBLD
tools/datasets/dspal ls BOOT_INTCODE
```

This job uses `ICINT19` and `TRNILRG` to compile the demoted Cambridge
source. It installs the interpreter-hosted bootstrap compiler `CAMBCOMP` and
its 11 compiler units in `BOOT_INTCODE`. `CAMBCOMP` generates native
System/370 assembler, but runs as INTCODE under `ICINT19`.

This step does **not** build the native Cambridge compiler in
`cambridge-compiler/`.

**Check:** there are **22 interpreter phases** (compile and code generation
for each unit) plus a `PACKCOMP` step. Every interpreted phase must report
`CODE=0`. Review the JES step RCs as well. The final PDS must contain
`CAMBCOMP` and the expected units.

### Test that the compiler writes assembler

```sh
tools/bootstrap/compile-mvs \
  bootstrap-toolchain/regression/00-most-degenerate-bcpl-program/source.bcpl \
  --output workarea/m3-clean-smoke.s370.asm

test -s workarea/m3-clean-smoke.s370.asm
```

**Check:** the output file has System/370 assembler statements such as
`CSECT`, `EXTRN BCPLMAIN`, and `END`. The compiler runner must report
interpreted completion `CODE=0`.

**Note:** the `CAMB_*` data sets are reserved for the separate native
Cambridge compiler effort and are not used by this reconstruction. The
interpreter-hosted bootstrap compiler lives in `BOOT_INTCODE`.

## Step 7 — Build the six Core Runtime modules and empty BCPLREG

The runtime provides the low-level services that native BCPL programs
need. Its assembler sources are tracked in Git and mapped to `BOOT_ASM`
by `config/dspal.yaml`.

First check the source and object libraries:

```sh
tools/datasets/dspal ls BOOT_ASM
tools/datasets/dspal ls BOOT_JCL
tools/datasets/dspal ls BOOT_OBJ
```

Before the build, `BOOT_OBJ` must be empty.

**Installation authorization:** The source/JCL correction does not, by
itself, authorize persistent object-library writes. The installation
hold at the start of this guide remains effective until the owner
explicitly approves installation into `BOOT_OBJ`.

Then build and install the runtime:

```sh
tools/datasets/dspal submit BOOT_JCL BLDBMAIN
tools/datasets/dspal ls BOOT_OBJ
```

| Source in Git | PDS object member |
| --- | --- |
| `bootstrap-toolchain/asm/bcplmain.asm` | `BCPLMAIN` |
| `bootstrap-toolchain/asm/bcplmem.asm` | `BCPLMEM` |
| `bootstrap-toolchain/asm/bcplbyte.asm` | `BCPLBYTE` |
| `bootstrap-toolchain/asm/bcplapt.asm` | `BCPLAPT` |
| `bootstrap-toolchain/asm/bcplio.asm` | `BCPLIO` |
| `bootstrap-toolchain/asm/bcplrgs.asm` | `BCPLRGS` |
| `bootstrap-toolchain/asm/bcplreg-empty.asm` | `BCPLREG` |

**Check:** the job has seven assembler steps and seven object-install
steps. All fourteen must return `RC=0000`. The final `BOOT_OBJ` must
contain these seven members and no old objects. `BCPLRGS` supplies
`RGINIT`/`RGFINI`; `BCPLREG` supplies the default empty registry.
An executable must link exactly one application registration table.

The install job is **not all-or-nothing**. If a step fails, stop and find
the cause; do not claim all five were installed.

The canonical `BCPLIO` is the uninstrumented production I/O module.
Fault-test instrumentation used by some regression cases is separate.

## Step 8 — Build BLIB, the sixth native object

`BLIB` is BCPL library code. This stage uses the rebuilt demoted Cambridge
bootstrap compiler (`CAMBCOMP`) to generate System/370 assembler. It then
applies the known assembler-card fixes, assembles the code, and installs
the resulting native object.

```sh
tools/datasets/dspal submit BOOT_JCL BLIBBLD
tools/datasets/dspal ls BOOT_OBJ
tools/datasets/dspal ls BOOT_DEVOBJ
```

**Check:** all six job steps finish with `RC=0000`:

| Step | Job |
| --- | --- |
| `COMP` | Compile BCPL library source |
| `PREPASM` | Prepare assembler cards |
| `PREPLK` | Prepare link/card content |
| `FIXASM` | Apply the known card fixes |
| `ASMBLIB` | Assemble BLIB |
| `INSTALL` | Save the native BLIB object |

The interpreted `CAMBCOMP` run must also report `CODE=0`.

The final production PDS must have **exactly eight** object members:

```text
BCPLMAIN  BCPLMEM  BCPLBYTE  BCPLAPT  BCPLIO  BCPLRGS  BCPLREG  BLIB
```

`BOOT_DEVOBJ` must remain empty. Do not use it to fill any gap in
`BOOT_OBJ`.

## Step 9 — Install BCPLDEMO and run the native production tests

Step 8 must have produced eight production object members (six Core
Runtime, default empty `BCPLREG`, and Base Library `BLIB`) in `BOOT_OBJ`. The runtime source packaging hold at the top of
this guide remains in force until separately resolved; this section does
not authorize or bypass the `BLDBMAIN` installation hold.

### Install the optional extension object

The first `dspal populate all` installed the Git-controlled text members
in `EXT_MAC`, `EXT_ASM`, and `EXT_SOURCE`. It did **not** populate
`EXT_OBJ`: binary object records must be assembled on MVS. Check the
required members before installing:

```sh
tools/datasets/dspal ls EXT_MAC
tools/datasets/dspal ls EXT_ASM
tools/datasets/dspal ls EXT_SOURCE
tools/datasets/dspal ls EXT_OBJ
```

Require `BCXPRE`, `BCXCAT`, `BCXPOST`, `BCPLDEMO` (assembler source),
and `DEMOHDR` in their respective text libraries. On a new clean-room
build, `EXT_OBJ` must still be empty. The approved installation target
is `HERC02.BCPL.EXT.OBJ(BCPLDEMO)` (FB80 relocatable object records);
the tracked assembler input is `HERC02.BCPL.EXT.ASM(BCPLDEMO)`. Check
the effective HLQ before using this site-specific installation deck.

**Permanent PDS write:** Obtain the required owner authorization before
running the install job. The job's only permanent write is the
`PUTDEMO` installation of `EXT_OBJ(BCPLDEMO)`. The project treats
optional package objects as disposable, reproducible build products;
there is no backup or member-level rollback PDS. Consult
[the R.5 installation design](runtime-extensions-r5-installation-design.md).

The committed `bootstrap-toolchain/extensions/bcpldemo/install-bcpldemo.jcl`
is a JOB-body deck without an authenticated JOB card. Prepare a
private, untracked copy from the configured batch credentials:

```sh
python3 - <<'PY'
import importlib.util
from pathlib import Path

path = Path("tools/datasets/dspal-core.py")
spec = importlib.util.spec_from_file_location("clean_room_dspal", path)
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

config = core.load_config()
card = core.authenticated_job_card(config, "R5DINST", "R5 BCPLDEMO", False)
source = Path(
    "bootstrap-toolchain/extensions/bcpldemo/install-bcpldemo.jcl"
).read_text(encoding="ascii")

output = Path("workarea/runtime-extensions-r5/install-bcpldemo.jcl")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text("\n".join(card) + "\n" + source, encoding="ascii")
output.chmod(0o600)
print("Prepared:", output)
PY
```

Submit the deck, recording the actual JES job number:

```sh
tools/mvs/submit-jcl workarea/runtime-extensions-r5/install-bcpldemo.jcl
```

Use the returned integer job number with `tools/mvs/job-summary` and
`tools/mvs/dump-report-for-job`. **Do not enter a literal placeholder**
in place of the number. Verify all four steps on the real MVS report:

| Step | Program | Required result |
| --- | --- | --- |
| `ASMDEMO` | IFOX00 | RC=0000; no assembler diagnostics |
| `PUTDEMO` | IEBGENER | RC=0000; binary object member installed |
| `READBACK` | IEBGENER | RC=0000; installed records copied back |
| `VERIFY` | IEBCOMPR | RC=0000; all object records match |

Then confirm the installed member:

```sh
tools/datasets/dspal ls EXT_OBJ
```

It must contain `BCPLDEMO`. Do not begin installed-mode regression
if assembly, installation, read-back, comparison, or membership fails.
Never transfer binary object records using `dspal put` or a text
encoding conversion.

### Run the complete production panel

Check the production build and compiler-driver paths:

```sh
python3 tools/checks/check-native-production-build.py
```

This is a host-side check; it does not submit MVS jobs. For ordinary
tests 00–145 the production linker explicitly includes installed
`BOOT_OBJ(BCPLRGS)` and `BOOT_OBJ(BCPLREG)`. Tests 146–158 instead
assemble their application-specific registry and temporary registrar;
they must not link the default `BCPLREG` as a second table.
Set the optional-extension installed-mode inputs and invoke the established
production launcher:

```sh
export BCPL_R5_EXTENSION_MODE=installed
export BCPL_R5_EXTENSION_DSN=HERC02.BCPL.EXT.OBJ
export BCPL_R5_MACRO_DSN=HERC02.BCPL.EXT.MAC

tools/bootstrap/run-production-regression 0 158
```

The production launcher selects the accepted `BOOT_OBJ` Core
Runtime/Base Library objects (`BCPL_RUNTIME_PDS=1`,
`BCPL_RUNTIME_LIBRARY=OBJ`, `BCPL_RUNTIME_CANDIDATE=0`).
It does **not** select the historical `MIXED` or `DEVOBJ`
profile. The extension settings independently direct cases 146–158
to the installed read-only `EXT_OBJ` and resident `EXT_MAC` libraries.
The interpreted `CAMBCOMP` compiles each BCPL client; IFOX, IEWL,
and GO run on MVS.

**Target result:**

| Result | Count | Meaning |
| --- | ---: | --- |
| PASS | **158** | Every executed regression passed |
| FAIL | **0** | No failed regressions |
| SKIP | **1** | Case 083 needs source-only instrumentation |
| TOTAL | **159** | Numbered cases 00 through 158 |

A few cases are special:

| Case | Expected behavior |
| --- | --- |
| `048` | Compile-only test; successful compile counts as PASS |
| `052` and `093` | In the production D6 profile, GO RC should be 0000 |
| `124`–`145` | Dynamic-stream and fault/accounting cases use all-OBJ production objects |
| `139`–`145` | Private test-only accounting does not replace production `BCPLIO` |
| `146` and `158` | BCPLDEMO excluded from the linked module |
| `147`–`157` | Installed BCPLDEMO selection, registration, and dispatcher behavior |

Each case saves its log in `workarea/native-regression/logs/`.
Inspect the saved report for any failure, including the actual
compiler, IFOX, IEWL MAP/XREF, and GO results. Re-run a single case,
for example `tools/bootstrap/run-production-regression 147 --show-output`.
Record the full-panel console summary and relevant JES job numbers.
Do not use `set -e` in the interactive operator shell: a failing
command should not terminate that shell.

### Audit the saved test reports

The historical `tools/checks/check-m44-full-panel-logs.py` audits
**00–145 only** and writes
`workarea/native-regression/m44-00-145-jobs.tsv`. Its current corpus
check requires the highest regression number to be 145; it therefore
**rejects the expanded 00–158 corpus** and is **not an R.5
acceptance gate**. Do not report it as an audit of tests 146–158.
For R.5, retain the full 00–158 runner result, each case's saved log,
and representative JES/IFOX/IEWL/GO evidence for the installed
extension. A harness log does not independently verify every physical
MVS DD record.

## Step 10 — Save what you proved

For every new clean-room rebuild, keep a short acceptance record.
A passing command is not enough if no one can tell which sources,
PDS members, and jobs were used.

| Record | What to save |
| --- | --- |
| Source | Full Git commit ID and the effective `dspal` settings (without passwords) |
| Erase/recreate | Deleted PDS list; purge and allocation job numbers |
| First population | Member summary; 12 expected missing generated members; evidence tracked sources were installed |
| Interpreter | Build payload job, `ASM`/`LKED`/`SAVEOBJ` RCs, smoke-test `CODE=0` |
| MR10 tests | Payload job numbers, suite pass results, output checked, comparison limits |
| Bootstrap | Source and output hash inventory, `TRNILRG` compile result, second population RC=0 |
| Demoted Cambridge bootstrap | `CAMBBLD` payload job, all 22 interpreted `CODE=0` results, `CAMBCOMP` smoke test |
| Runtime | Seven assembly and seven install RCs; eight final `BOOT_OBJ` members including BCPLRGS, BCPLREG, and BLIB |
| Optional extension | `EXT_MAC`/`EXT_ASM`/`EXT_SOURCE` membership; `EXT_OBJ(BCPLDEMO)` install job; `ASMDEMO`, `PUTDEMO`, `READBACK`, and `VERIFY` RCs; binary comparison and IEWL MAP/XREF evidence |
| Native tests | Full installed-mode 00–158 result (158 PASS, 0 FAIL, expected SKIP 083); case logs and JES job numbers; historical 00–145 audit limitation recorded |
| Boundaries | Any checks not run, warnings, and generated evidence that was not saved |

Keep credentials out of committed files. `workarea/` is ignored by Git;
its generated logs, images, and manifests will **not** be saved by a
normal `git commit`.

The [17 October 2026 acceptance record](clean-room-mvs-reconstruction-acceptance-2026-10-17.md)
proves the **earlier** accepted procedure. When this revised two-pass
procedure is tested end-to-end, record that result separately. Do not
change the old record to make it look as if the new procedure was used.

## When something goes wrong

| Symptom | First thing to check |
| --- | --- |
| First `populate all` exits 2 | Is the **only** issue the 12 missing generated members? Were tracked members installed? |
| A tracked member is missing | Git checkout and the member mapping in `config/dspal.yaml` |
| `prepare-bootstrap --with-trnilrg` fails | Is the newly built `MR10_LOAD(ICINT19)` working? Read the interpreter payload reports |
| Second `populate all` exits nonzero | Generated inventory, missing files, source hashes, or JES installation failures |
| `CAMBBLD` fails | Interpreter `CODE=0`, `TRNILRG`, source members, and the payload job |
| Runtime assembly fails | Full IFOX listing and exact step RC; do not install an old object |
| Native regression fails | That case's saved log and its compiler, assembler, link, and GO jobs |
| Printer report is missing | Check `mvs-state/prt/prt00e.txt` and the actual payload job number |

Fix failures at the stage where they occur. Do not hide an unexpected
error code with `|| true` and continue to a later step.

## Developer checks — not part of a routine rebuild

These checks protect the **build tools and test harness** while someone
is editing them. They do not rebuild BCPL or run MVS. Use them when you
change the related scripts or JCL, or when you are investigating a problem.

| Command | What it checks |
| --- | --- |
| `python3 tools/checks/test-dspal-generated-population.py` | Offline tests for first/second population behavior |
| `python3 tools/checks/check-native-bootstrap-jcl.py` | Expected `CAMBBLD` job structure and PDS names |
| `python3 tools/checks/check-native-production-build.py` | Canonical native build source and JCL contracts |
| `tools/bootstrap/run-production-regression --check-numbering` | Test numbering and expected range |
| `check-m44-compatibility.py --production` | Harness fixtures, production linkage, and test-only fault settings |

For the last check, the required production environment is:

```sh
env -u BCPL_RUNTIME_CANDIDATE_MEMBER \
  BCPL_RUNTIME_PDS=1 \
  BCPL_RUNTIME_LIBRARY=OBJ \
  BCPL_RUNTIME_CANDIDATE=0 \
  python3 tools/checks/check-m44-compatibility.py --production
```

**Why these checks are optional here:** the JCL, manifest, and runner are
Git-tracked. We do not expect them to change during a routine rebuild.
Successful MVS builds and the full regression panel give stronger proof
that the rebuilt system works. Static checks remain useful when the
*tools themselves* are being changed.

## Optional historical and diagnostic tools

| Item | Current status |
| --- | --- |
| `BOOT_DEVOBJ` and historical `BCPLM6` candidate | Kept for development/history; **not used** in the production rebuild |
| `CAMB_*` PDSes | Managed, but **not used** for the resident bootstrap above |
| Instrumented `CG370D` compiler | Its generator and `BOOT_JCL(CG370DB)` build job are still in Git; **not part of the normal build** |

`make-demoted.py` still generates the five instrumented code-generator
sources in `workarea/bootstrap-cambridge/demoted-diag/`.
`bootstrap-toolchain/jcl/cg370db.jcl` can build the separate
`BOOT_INTCODE(CG370D)` image. At present those five diagnostic sources
(`CGAD`–`CGED`) still need **explicit staging** into `BOOT_SOURCE`:
they are not in the normal `dspal populate all` mapping.
Building `CG370D` does **not** replace `CAMBCOMP`.

Do not restore or run those optional tools just to complete this guide.
