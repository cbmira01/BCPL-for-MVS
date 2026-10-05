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

## CGA exposes an MR10 translator-capacity boundary

Job 899 is the first CGA bootstrap probe.  ICINT V19 assembled and linked
cleanly, but the MR10 compile phase returned code 8 after reaching:

```text
TREE SIZE 11089
REPORT:   TOO MANY NAMES DECLARED
COMMANDS COMPILED 0
```

The saved OCODE contains only `STACK 2`, and CGI therefore reports program
length zero.  These are failure artifacts and must not be treated as a partial
CGA success.

The diagnostic is MR10 TRN report 143.  In the historical translator source,
`COMPILEAE` allocates `A = VEC 1200` and initializes `DVECT` to 1200.  `ADDNAME`
stores three words per declaration `(name, class, value)` and reports 143 when
`DVECS>=DVECT`.  The effective historical capacity is therefore about 400
simultaneously visible names.  CGA exceeds that limit.

This is a bootstrap-capacity issue, not a Cambridge syntax incompatibility and
not an ICINT PROGVEC/global-vector issue.

`make-mr10-trn-large-names.py` now creates a source-derived MR10 TRN variant by
splitting the historical `mr10/bcplkit/trn` container and changing only TRN0:

```text
VEC 1200 -> VEC 2400
DVECT 1200 -> DVECT 2400
```

The historical source remains untouched.  `build-mr10-trni-large-names.sh`
compiles the generated TRN sections with the proven MR10 compiler/CGI pipeline,
saves each generated INTCODE section, and concatenates them into:

```text
native-compiler/bootstrap-cambridge/trni-large-names.int
```

Do not replace the tracked default `intcode/trni.int` permanently until this
variant has compiled CGA successfully and ordinary regression tests remain
stable.

## Phase change

The bootstrap problem is now no longer whether the Cambridge SYN/TRN sources or
master can cross the MR10 dialect boundary.  The next objective is to provide
the MR10 translator enough declaration capacity for CGA, then continue through
all five native S/370 code-generator sections and build the complete interpreted
compiler image.

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

First build the larger-name MR10 translator derivative:

```sh
bash native-compiler/bootstrap-cambridge/build-mr10-trni-large-names.sh
```

That should produce `native-compiler/bootstrap-cambridge/trni-large-names.int`.
For the first proof only, substitute it locally for `intcode/trni.int`, run the
same CGA probe, then restore the tracked file immediately.  Once the variant is
proven, add a permanent compiler-phase override to the tooling rather than
continuing to swap files.

The CGA success criterion is nonempty saved OCODE and a CGI-produced INTCODE
image.  The isolated final RUN is not meaningful for a CG section.

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
