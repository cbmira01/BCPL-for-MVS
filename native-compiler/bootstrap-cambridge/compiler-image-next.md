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

The Cambridge master also crosses the MR10 bootstrap boundary.  Job 893 saved
nonempty `bcpl.ocode`; its standalone execution then exposed the historical
master's larger global-vector requirement (`TOPGLOB:699`).

ICINT V19 was therefore derived from V18 as a capacity/layout-only bootstrap
candidate:

- enlarge the global vector from 401 to 700 words, supporting G!0..G!699;
- move all matching OP1/GUSED/MAPSTORE bounds with it;
- retain the V18 40,001-word PROGVEC;
- place the executable-code literal pool explicitly at the code/data boundary;
- load the two MAPSTORE messages that now lie just above x'2FFF' through
  reachable address literals rather than consuming another permanent base.

Jobs 894-897 isolated and corrected the resulting IFOX layout/addressability
issues.  Job 898 is the first complete V19 master probe: ICINT assembled and
linked, the Cambridge master again produced nonempty OCODE, CGI generated a
2953-word INTCODE image, and the master actually entered execution.

Job 898's standalone execution stopped after 43 cycles because the other
Cambridge compiler sections were not loaded.  Its MAPSTORE shows the key
rendezvous globals absent, including `FORMTREE` (G!150), `COMPILEAE` (G!245),
and `CODEGEN` (G!390).

Do not infer from that result that ICINT should initialize unused globals to a
negative sentinel.  The historical MR10 ICINT assembler can leave unresolved
global entries at zero.  The Cambridge master's `CODEGEN < 0` overlay test
belongs to its original host/linkage environment.  Our bootstrap design avoids
that path by loading all compiler sections together so these globals are real
addresses.

## Phase change

The bootstrap problem is now no longer whether the Cambridge SYN/TRN sources or
master can cross the MR10 dialect boundary.  The next objective is to bootstrap
all five native S/370 code-generator sections and then build the complete
interpreted compiler image.

Historical components still required are:

```text
bcplib/bcpl/cg         native S/370 generator sections CGA..CGE
```

`make-demoted.py` generates:

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
`CODEGEN` is populated through the global vector by CGA, the historical master
sets `OVERLAYING` false and the overlay-loading paths remain dormant.

For CGA..CGE:

- split the historical `cg` container at its five SECTION boundaries;
- omit the wrappers and inter-section `.` delimiters;
- map `GET "HEADERS(CGHDR)"` to `GET "CGHDR"` for MVS DDNAME use;
- rewrite Cambridge `~=` to MR10 `NE`.

No code-generator semantics have otherwise been changed.

## Next controlled experiment

Probe CGA next with the V19 interpreter and both headers exposed:

```sh
tools/compile-and-run --results --save-ocode \
    --dd OPTIONS=native-compiler/bootstrap-cambridge/options-large-tree.txt \
    --dd LIBHDR=richards-bcpltape/sys3/bcpl/libhdr \
    --dd CGHDR=richards-bcpltape/bcplib/bcpl/cghdr \
    asm/icintv19.asm \
    native-compiler/bootstrap-cambridge/demoted/cga
```

The success criterion is nonempty saved OCODE and a CGI-produced INTCODE image.
The isolated final RUN is not meaningful for a CG section.

Continue CGA through CGE one section at a time so every additional
source-dialect accommodation remains evidence-driven.

## Intended assembled image

Once CGA..CGE also cross the MR10 bootstrap boundary, load these INTCODE units
together under ICINT V19:

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
