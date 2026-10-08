# BLIB object-library experiment (Stage A, unverified)

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
3. Inspect `HERC02.BCPL.OBJ` using existing MVS tools. Submit
   `allocate-blib-obj.jcl` **only if the DSN is missing**. Do not replace
   an existing dataset. The proposed DCB is DSORG=PO, RECFM=FB, LRECL=80,
   BLKSIZE=800, directory blocks=20. These attributes remain to be verified
   under TK5.

## Generate and submit

From repository root:

```sh
python3 native-compiler/object-library/make-blib-object-job.py \
  workarea/native-regression/067-full-historical-blib-link/library-generated.s370.asm \
  asm/bcplmain-wip.asm \
  workarea/blib-object-probe.jcl

tools/submit-jcl workarea/blib-object-probe.jcl
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

The experiment does not use `dspal put` or `populate`, since those operate
on text. It does not assume BCPLMAIN can initialize independently linked
sections. The object member may be overwritten on later experimental runs;
use a dedicated library and inspect its existing contents first.

## Evidence and acceptance

Collect the job number, IFOX assembly condition codes, the IFOX ESD/RLD
listing for BLIB, IEBGENER condition code, and IEWL MAP/XREF output including
resolved `BCPLMAIN` and included `BLIB` section. Verify the installed
member through MVS listing/usage; **do not** read it via `dspal get` or
`cat` as text.

Expected step outcomes are **hypotheses**, not observed results. If the
historical CG370 output has assembler defects beyond the known constant,
record them explicitly and repair only in generated transport. Do not claim
Stage A completed until the MVS job logs prove object-member inclusion and
successful IEWL completion without unresolved symbols.

## Next boundary

Once this is verified, design a typed `OBJ` manifest entry and
binary-preserving install path in `dspal`. That is separate from Stage B:
loading BLIB's exported globals into the runtime global vector and executing
multiple independently linked BCPL sections.
