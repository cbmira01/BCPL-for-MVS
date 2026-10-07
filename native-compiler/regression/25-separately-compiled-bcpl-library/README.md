# 25 - Separately compiled BCPL library routine through G

This regression proves that an application compilation unit can call a
routine generated from a separate BCPL compilation unit through the global
vector.

The application declares but does not define `ADD`:

```bcpl
GLOBAL $( START:1; DEBUGINT:150; ADD:151 $)

LET START () BE
$(1
    LET X = ADD(17,25)

    DEBUGINT(X)
    FINISH
$)1
```

The library is compiled independently:

```bcpl
GLOBAL $( ADD:151 $)

LET ADD(A,B) = A+B
```

Expected output:

```text
42
```

## Purpose

Test 24 proved a callable user global when the definition and caller were in
the same generated module. Test 25 separates those BCPL compilation units.

The intended path is:

```text
source.bcpl  --------> independent CG370 output --+
                                                   |
                                                   +--> regression static combiner
                                                   |       |
library.bcpl --------> independent CG370 output --+       v
                                                     one native test module
                                                           |
                                                           v
                                                   BCPLMAIN installs G!151
                                                           |
                                                           v
                                                   START calls ADD through G
```

The library's generated local labels are renamed by the regression harness
before combination so they cannot collide with labels from the application
compilation unit. Its exported-global trailer entries are merged into the
application module trailer.

## Important scope boundary

The static combiner is test scaffolding, not the final BCPL linker or loader.

The current WIP `BCPLMAIN` scans only the trailer belonging to the one
generated module that entered it. The historical multi-section LOAD/UNLOAD
mechanism has not yet been reconstructed. Consequently, two independently
generated BCPL modules cannot yet be linked unchanged and have both trailers
registered automatically.

This test deliberately proves the narrower contract needed now:

- application and library BCPL are compiled independently;
- ADD's machine code comes from the library compilation, not the application;
- the library export is installed as G!151;
- START reaches ADD through the global vector;
- ordinary BCPL argument and result conventions survive the compilation-unit
  boundary.

A later loader/linkage regression must remove the static-combiner
accommodation and exercise independently loadable native BCPL sections.

## Acceptance criteria

A successful run must:

- compile `source.bcpl` and `library.bcpl` in two separate Cambridge
  compiler invocations;
- generate independent System/370 assembler for each unit;
- combine them without recompiling either BCPL source;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show START loading G!151 at byte displacement 604 from R12 and calling it;
- show G!151's installed address naming code derived from `library.bcpl`;
- show the library ADD receiving R7/R8 and returning its sum in R7.

## Status

PENDING.
