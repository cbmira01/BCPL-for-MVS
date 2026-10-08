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


## Managed BLIB rebuild (packaging follow-on, awaiting Hercules verification)

The Stage A experiment above remains preserved as evidence. The new managed
rebuild path is **not** the same job and has **not yet been exercised on TK5**.

The `dspal` manifest now includes the mappings:

| Dataset | Member | Source / purpose |
| --- | --- | --- |
| SOURCE | BLIB | `workarea/bootstrap-cambridge/demoted/blib` |
| JCL | BLIBBLD | `jcl/build-blib-object.jcl` (stored JCL body) |
| OBJ | BLIB | Relocatable binary object records, **not text-populated** |

The manifest defines OBJ as a managed PO, FB/80, BLKSIZE=800 PDS, with
`content_type: object` and `populate: false`. The binary member is created
only by native IFOX assembly + IEBGENER. For safety, `dspal put`, `cat`,
`get`, and `submit` reject the managed OBJ dataset; `ls` and `stat` work.
`dspal initbcpl` recognizes the OBJ definition and can allocate the PDS
if missing, without replacing an existing one.

From the repository root, with Hercules and the resident compiler installed:

```sh
python3 tools/build-blib-object --dry-run
python3 tools/build-blib-object
```

The host command performs these operations:

1. Preflight all managed datasets, including OBJ, refusing unexpected DCB or
   missing datasets; never silently allocate or purge a PDS.
2. Regenerate demoted BLIB from the **unchanged historical source**, using
   the drift-checked `make-demoted.py --blib-only`.
3. Deploy the text source as `HERC02.BCPL.SOURCE(BLIB)` using `dspal put`.
4. Compile the local demoted source through resident `CAMBCOMP` using
   `tools/cambridge-compile-mvs`. Recover S/370 assembler to
   `workarea/blib-object-build/blib-generated.s370.asm`.
5. Normalize recovered assembly cards with the verified Stage A logic:
   name the BLIB CSECT, normalize non-ASCII printer artifacts in comments,
   and repair the known signed-minimum constant.
6. Deploy **text** to `HERC02.BCPL.ASM(BLIB)` and deploy
   `HERC02.BCPL.JCL(BLIBBLD)` using `dspal put`.
7. Submit `dspal submit JCL BLIBBLD --wait`. IFOX produces temporary
   FB/80 **binary object records**; IEBGENER installs those records
   directly in `HERC02.BCPL.OBJ(BLIB)` without host conversion. INSTALL is
   bypassed unless IFOX returns **RC=0000**.
8. Require both `ASMBLIB` and `INSTALL` at RC=0000 and verify `BLIB` in OBJ.

`BLIBBLD` itself contains only the **ASMBLIB** and **INSTALL** MVS steps.
It **does not link-edit or execute** BLIB. It consumes prepared ASM(BLIB),
so it is not a JCL-only build from SOURCE(BLIB). That stronger workflow is
not yet implemented, because CG370 emits an unnamed section and one malformed
signed-minimum constant; preparation currently takes place on the host.

To repeat *only* the stored IFOX assembly and installation when ASM(BLIB)
has already been prepared and deployed:

```sh
tools/dspal submit JCL BLIBBLD --wait
```

If OBJ was lost, provision it first with `tools/dspal initbcpl` and verify
attributes. If the resident compiler or the other managed libraries were
also lost, restore those prerequisites before running the rebuild.

The first managed-build run on Hercules must still verify both job steps,
PDS member presence, and the object/linkage evidence. No managed-build
job has been run yet. Existing 69 passing native regressions and their static
combiner remain unchanged, as do the canonical historical source and
BCPLMAIN-wip. Independent BCPL section execution is **Stage B**, not part of
this packaging milestone.


## Next boundary

Once this is verified, design a typed `OBJ` manifest entry and
binary-preserving install path in `dspal`. That is separate from Stage B:
loading BLIB's exported globals into the runtime global vector and executing
multiple independently linked BCPL sections.
