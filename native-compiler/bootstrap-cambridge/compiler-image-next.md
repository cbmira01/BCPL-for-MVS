# Cambridge compiler-image bootstrap phase

## Milestone reached

Jobs 885, 888, 889, and 892 established successful MR10 bootstrap compilation
of all four Cambridge frontend/translator implementation sections:

```text
SYN   -> OCODE -> CGI -> INTCODE
LEX   -> OCODE -> CGI -> INTCODE
TRNA  -> OCODE -> CGI -> INTCODE
TRNB  -> OCODE -> CGI -> INTCODE
```

The isolated final RUN faults are expected: these sections are not complete
START programs by themselves.

Job 892 is the first successful TRNB result after demoting its one later unary
`ABS` source expression to equivalent older BCPL integer logic.

## Phase change

The bootstrap problem is now no longer whether the Cambridge SYN/TRN sources can
cross the MR10 dialect boundary.  The next objective is to build the complete
interpreted compiler image.

Historical components still required are:

```text
bcplib/bcpl/bcpl       master/START section BCPL
bcplib/bcpl/cg         native S/370 generator sections CGA..CGE
```

`make-demoted.py` now generates:

```text
demoted/bcpl
demoted/cga
demoted/cgb
demoted/cgc
demoted/cgd
demoted/cge
```

in addition to the four already-proven SYN/TRN units.

## Bootstrap-only transformations

For the master `BCPL` section:

- omit the `SECTION "BCPL"` wrapper;
- omit the leading `NEEDS "$LOAD$"` object dependency directive;
- retain the actual `LOADSEG`/`UNLOAD` code unchanged.

The omitted `NEEDS` directive belongs to the native object/linkage environment.
The interpreted bootstrap will load all compiler units together.  When
`CODEGEN` is already populated through the global vector, the historical master
sets `OVERLAYING` false and the overlay-loading paths remain dormant.

For CGA..CGE:

- split the historical `cg` container at its five SECTION boundaries;
- omit the wrappers and inter-section `.` delimiters;
- map `GET "HEADERS(CGHDR)"` to `GET "CGHDR"` for MVS DDNAME use;
- rewrite Cambridge `~=` to MR10 `NE`.

No code-generator semantics have otherwise been changed.

## Next controlled experiment

Compile only the demoted master first:

```sh
tools/compile-and-run --results --save-ocode \
    --dd OPTIONS=native-compiler/bootstrap-cambridge/options-large-tree.txt \
    --dd LIBHDR=richards-bcpltape/sys3/bcpl/libhdr \
    asm/icintv18.asm \
    native-compiler/bootstrap-cambridge/demoted/bcpl
```

The success criterion is nonempty saved OCODE.  A standalone final RUN is not
expected to work because the master depends on globals supplied by SYN, TRN,
CG, and runtime support.

If the master compiles, probe CGA next with both `LIBHDR` and `CGHDR` exposed.
Continue one section at a time so every additional source-dialect accommodation
is evidence-driven.

## Intended assembled image

Once BCPL and CGA..CGE also cross the MR10 bootstrap boundary, load these
INTCODE units together under ICINT v18:

```text
BCPL
SYN
LEX
TRNA
TRNB
CGA
CGB
CGC
CGD
CGE
BLIBI / host runtime support
```

The global vector is the rendezvous mechanism.  The first integrated test should
compile a very small BCPL source through the Cambridge frontend and native CG370,
with output directed to a host-visible CODE stream.  That test, not isolated
section execution, will establish a runnable Cambridge compiler under
interpretation.
