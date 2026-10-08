# Native BLIB object-library foundation — Stage A and resident build verified

**Stage A is VERIFIED:** user-run JOB 2396 on 2026-10-08 completed ASMBLIB,
INSTALL, ASMRUN and LKED at RC=0000. IEWL explicitly included
`HERC02.BCPL.OBJ(BLIB)` and resolved its external BCPLMAIN reference.
See [stage-a-checkpoint.md](stage-a-checkpoint.md) for ESD, RLD,
link map and exact acceptance evidence. The linked module was not run.

The **Stage A linkage probe** was isolated and non-executing. Subsequent
packaging work on this experiment branch extends `config/dspal.yaml`, but
does not modify regression 000–068, canonical historical BLIB, the static
combiner, or `BCPLMAIN-wip`.

## Prerequisites

1. Regenerate the complete demoted BLIB using
   `native-compiler/bootstrap-cambridge/make-demoted.py --blib-only`.
2. Run the existing separately compiled BLIB regression 067 far enough to
   obtain its `library-generated.s370.asm` artifact. The currently established
   path is `workarea/native-regression/067-full-historical-blib-link/library-generated.s370.asm`
   (verify the file exists; do not substitute combined application assembly).
3. Inspect `HERC02.BCPL.OBJ` using `tools/dspal stat HERC02.BCPL.OBJ --raw`.
   **Only if missing**, generate an authenticated allocation JCL using
   `make-obj-allocation-job.py`; submit it and check RC=0000. Do not replace
   an existing dataset. The proposed DCB is DSORG=PO, RECFM=FB, LRECL=80,
   BLKSIZE=800, directory blocks=20. These attributes were verified under TK5 by the Stage A allocation
   and `dspal stat` jobs.
4. Provide `mvs.batch_password` for `HERC02` through the gitignored
   `config/dspal.local.yaml`, as documented in `config/README.md`.
   Generated JCL files contain a batch password: keep them local, do not
   display or commit their contents, and delete them after use.

## Generate and submit

From repository root, allocate the object PDS **only if it does not exist**:

```sh
python3 native-compiler/object-library/make-obj-allocation-job.py \
  workarea/blib-object-allocate.jcl
tools/submit-jcl workarea/blib-object-allocate.jcl
# Check allocation job summary before proceeding.
```

Then generate and submit the probe:

```sh
python3 native-compiler/object-library/make-blib-object-job.py \
  workarea/native-regression/067-full-historical-blib-link/library-generated.s370.asm \
  asm/bcplmain-wip.asm \
  workarea/blib-object-probe.jcl

tools/submit-jcl workarea/blib-object-probe.jcl
# Inspect both jobs, then remove generated credential-bearing JCL:
# rm -f workarea/blib-object-allocate.jcl workarea/blib-object-probe.jcl
```

The generator checks the standalone unnamed generated CSECT and EXTRN
BCPLMAIN, changes only its name to `BLIB`, and applies the single known
signed-minimum assembler constant repair (if present). It leaves the
historical wrapper, exported-global trailer, and all source code intact.

The job:

1. Assembles **BLIB alone** through IFOX to an FB/80 temporary object deck.
2. Uses IEBGENER to copy object **records without host text conversion** to
   `HERC02.BCPL.OBJ(BLIB)`.
3. Separately assembles the unchanged `BCPLMAIN-wip` source to another
   temporary object deck, solely to satisfy BLIB's external reference.
4. Runs IEWL with `INCLUDE OBJ(BLIB)` and `ENTRY BLIB`, writing a
   temporary load module but **never running it**.

Both jobs authenticate with the same `dspal` batch credentials used by
other managed dataset operations. The experiment does not use `dspal put`
or `populate`, since those operate on text. It does not assume BCPLMAIN can initialize independently linked
sections. The object member may be overwritten on later experimental runs;
use a dedicated library and inspect its existing contents first.

## Evidence and acceptance

Collect the job number, IFOX assembly condition codes, the IFOX ESD/RLD
listing for BLIB, IEBGENER condition code, and IEWL MAP/XREF output including
resolved `BCPLMAIN` and included `BLIB` section. Verify the installed
member through MVS listing/usage; **do not** read it via `dspal get` or
`cat` as text.

The results of JOB 2396 are documented in the verified checkpoint. If the
historical CG370 output has assembler defects beyond the known constant,
record them explicitly and repair only in generated transport. Stage A is complete for independently assembled object storage and IEWL
inclusion; Stage B execution remains unproven.


## Managed BLIB rebuild (MVS-resident pipeline, verified)

This production-style packaging workflow follows the **same pattern as the
demoted compiler**: position source, position a stored JCL job body, invoke it.
It does not depend on regression 067 or host-recovered CG370 assembly.

The `dspal` manifest maps `SOURCE(BLIB)` to
`workarea/bootstrap-cambridge/demoted/blib` and `JCL(BLIBBLD)` to
`jcl/build-blib-object.jcl`. The managed `OBJ` dataset is a PO FB/80
BLKSIZE=800 PDS with `content_type: object` and `populate: false`.
`dspal put/get/cat/submit` reject OBJ as a text dataset, but `stat` and
`ls` support it; `initbcpl` can allocate it if missing.

The normal host command is:

```sh
tools/build-blib-object --dry-run
tools/build-blib-object
```

After verifying dataset attributes, the command performs exactly:

1. Regenerate the demoted BLIB text from the untouched historic source.
2. `dspal put SOURCE BLIB workarea/bootstrap-cambridge/demoted/blib`
3. `dspal put JCL BLIBBLD jcl/build-blib-object.jcl`
4. `dspal submit JCL BLIBBLD --wait`
5. Check all six job steps for RC=0000 and inventory `OBJ(BLIB)`.

Inside the stored MVS job:

| Step | Program | Work |
| --- | --- | --- |
| COMP | ICINT19 | Resident `CAMBCOMP` reads `SOURCE(BLIB)`, writes CG370 `&&CODE` |
| PREPASM | IFOX00 | Assemble an in-stream, narrow FB80 card-repair utility |
| PREPLK | IEWL | Link that temporary utility only; no BLIB linking |
| FIXASM | Temporary PREPLK module | Name unnamed BLIB CSECT and fix signed-minimum DC card |
| ASMBLIB | IFOX00 | Assemble independent BLIB relocatable object records |
| INSTALL | IEBGENER | Copy unchanged FB80 object records to `OBJ(BLIB)` |

The in-stream FIXASM utility is intentionally small, not a general-purpose
assembler preprocessor. It recognizes exactly two whitespace presentations
of each known problematic line: the unnamed `CSECT` and the emitted
`DC F'-./,),(-*,('`. It substitutes `BLIB CSECT` and `DC X'80000000'`,
respectively. It **requires exactly one of each transformation** and
returns RC=8 otherwise. This prevents an empty compiler result or an
unexpected code-generator change from silently replacing the object member.
The following assembly/install steps run only if the earlier work completes
successfully. The canonical BLIB, CG370 compiler, and BCPLMAIN are unchanged.

### First resident build attempt: JOB 2408 (2026-10-08)

This is a **failed** resident-build checkpoint, distinct from the successful
Stage A JOB 2396 probe. The user reported that the resident compiler printed
`COMPILATION SUCCESSFUL` and `EXECUTION CYCLES = 9009776, CODE = 0`;
COMP, PREPASM and PREPLK each returned RC=0000. FIXASM abended
`S806-4` with `IEA703I ... MODULE ACCESSED PREP`. The original PREPLK
`SYSLMOD` DD named its temporary PDS member `PREP`, whereas the
linkage editor installed `BLIBPREP` through `NAME BLIBPREP(R)`.
The JCL now uses `&&PREPLD(BLIBPREP)` so the module requested by
`EXEC PGM=*.PREPLK.SYSLMOD` matches the IEWL module name. An
offline regression test requires the names to agree. A rerun on TK5 was completed successfully as JOB 2413; see the
next checkpoint below.
The earlier `OBJ(BLIB)` directory entry was from JOB 2396 and should
**not** be cited as an outcome of failed JOB 2408.

### Verified resident build: JOB 2413 (2026-10-08)

After the corrected JCL was positioned in `JCL(BLIBBLD)` by JOB 2410,
the user submitted it through `dspal submit`. JES launcher JOB 2412
submitted payload **JOB 2413**. Every step completed at **RC=0000**:

```text
COMP    ICINT19      RC=0000
PREPASM IFOX00       RC=0000
PREPLK  IEWL         RC=0000
FIXASM  PGM=*.DD     RC=0000
ASMBLIB IFOX00       RC=0000
INSTALL IEBGENER     RC=0000
JOB RESULT: SUCCESS
HIGHEST RC: 0000
```

No assembler statements were flagged; highest severity was zero.
This establishes compilation of positioned `SOURCE(BLIB)` by resident
Cambridge, execution of the MVS card-fixer, independent IFOX assembly,
and binary object installation in `OBJ(BLIB)`.
The original four-step **Stage A object-linkage probe** remains separately
verified as JOB 2396. See [resident-build-checkpoint.md](resident-build-checkpoint.md)
for the observed jobs, error/fix chronology, and precise limitations.

The user exercised the stored `dspal` build path directly; the convenience
wrapper's single-command full execution has not yet been independently
observed.

To submit the already deployed source/job body without host orchestration:

```sh
tools/dspal submit JCL BLIBBLD --wait
```

This will overwrite `OBJ(BLIB)` when successful. It does **not** link-edit
BLIB with an application or execute independently linked BCPL sections.
Those are separately tested, and Stage B global-vector initialization is
still deferred. Keep the 69 passing static native regressions unchanged.

## Separate-job object consumer probe — ready, not yet executed

The new **`BLIBLINK`** JCL member is an independent, non-executing
consumer of the object installed by resident **JOB 2413**. It cannot
recompile or overwrite BLIB. It performs:

1. `ASMRUN`: IFOX-assemble unmodified `asm/bcplmain-wip.asm` from
   the managed `HERC02.BCPL.ASM(BCMWIP)` member.
2. `LKED`: IEWL explicit `INCLUDE OBJ(BLIB)` from read-only
   `HERC02.BCPL.OBJ`; use `ENTRY BLIB`, `NAME BLIBCHK(R)`,
   and a temporary `SYSLMOD`; do **not** run the result.

From the experiment branch, run offline packaging tests and position
the two text members:

```sh
git pull --ff-only
python3 native-compiler/object-library/test_packaging.py
tools/dspal put ASM BCMWIP asm/bcplmain-wip.asm
tools/dspal put JCL BLIBLINK jcl/probe-blib-object-consumer.jcl
tools/dspal submit JCL BLIBLINK --wait
```

The exact acceptance result is `ASMRUN RC=0000` and `LKED RC=0000`,
plus a control-section map containing separately linked `BCPLMAIN` and
`BLIB`, `INCLUDE OBJ(BLIB)` in IEWL control-card echo, and the
`BCPLMAIN` external relocation resolved. Inspect the JES report rather
than treating IEWL RC alone as complete evidence. Do **not** treat this
as proof of runtime initialization; there is no `GO` step.
The earlier Stage A JOB 2396 proved linkage only when source object
installation was in the same job; this checks **separate-job reuse**
of persistent `OBJ(BLIB)` built by the resident compiler.

No execution evidence for BLIBLINK is recorded as of this note.
Regressions 067 and 068 remain unchanged and continue to statically
combine BLIB. Potential object-linked execution tests 069/070 are
**future Stage B proposals**, not implemented regressions.

## Next boundary

The `OBJ` manifest entry and binary-preserving IFOX/IEBGENER installation
are now implemented and the resident job verified. The next distinct
architectural problem is **Stage B**: loading BLIB's exported globals into
the runtime global vector and executing multiple independently linked BCPL
sections. Preserve the passing static regression reference path until
that runtime-linkage behavior is demonstrated.
