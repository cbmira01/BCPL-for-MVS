# BLIB object-library experiment (Stage A, verified)

**Stage A is VERIFIED:** user-run JOB 2396 on 2026-10-08 completed ASMBLIB,
INSTALL, ASMRUN and LKED at RC=0000. IEWL explicitly included
`HERC02.BCPL.OBJ(BLIB)` and resolved its external BCPLMAIN reference.
See [stage-a-checkpoint.md](stage-a-checkpoint.md) for ESD, RLD,
link map and exact acceptance evidence. The linked module was not run.

This is an **isolated, non-executing** probe. It does not modify regression
000–068, canonical `richards-bcpltape/bcplib/bcpl/blib`, the static
combiner, `config/dspal.yaml`, or `BCPLMAIN-wip`.

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
   BLKSIZE=800, directory blocks=20. These attributes remain to be verified
   under TK5.
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


## Managed BLIB rebuild (MVS-resident pipeline, pending TK5 run)

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
offline regression test requires the names to agree. A rerun on TK5 is
still required to verify execution and subsequent object installation.
The earlier `OBJ(BLIB)` directory entry was from JOB 2396 and should
**not** be cited as an outcome of failed JOB 2408.

The original four-step **Stage A object-linkage probe** remains in the earlier
section of this document. Its success is not evidence that this new six-step
build has passed. The first run of this stored MVS job must be checked and
documented; it has **not** yet been executed under TK5.

To submit the already deployed source/job body without host orchestration:

```sh
tools/dspal submit JCL BLIBBLD --wait
```

This will overwrite `OBJ(BLIB)` when successful. It does **not** link-edit
BLIB with an application or execute independently linked BCPL sections.
Those are separately tested, and Stage B global-vector initialization is
still deferred. Keep the 69 passing static native regressions unchanged.

## Next boundary

Once this is verified, design a typed `OBJ` manifest entry and
binary-preserving install path in `dspal`. That is separate from Stage B:
loading BLIB's exported globals into the runtime global vector and executing
multiple independently linked BCPL sections.
