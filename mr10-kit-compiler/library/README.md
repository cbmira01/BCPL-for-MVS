# Reconstructed BCPL library

The `library/` directory contains portable BCPL routines intended to be compiled alongside an application as additional compilation units.  There is no requirement that these routines be packaged as one monolithic object library.

The normal model is:

```sh
tools/compile-and-run --results \
    "$(tools/current-icint)" \
    main-program.bcpl \
    +library/module-one.bcpl \
    +library/module-two.bcpl
```

Each application declares the GLOBAL names it uses with the assignments documented in [`GLOBALS.md`](GLOBALS.md).  The separately compiled modules rendezvous through the common BCPL global vector.

## General-purpose modules

### `random.bcpl`

Deterministic Park-Miller pseudo-random number support:

```text
SRAND(N)       seed the generator
RAND()         next value in 1..2147483646
RANDRANGE(N)   value in 0..N-1; 0 when N<=0
RANDSEED(N)    compatibility spelling for SRAND
```

The algorithm uses Schrage's method and therefore does not rely on signed 32-bit multiplication overflow.  It is for programs, demonstrations, randomized algorithms, and reproducible tests; it is not cryptographic.

### `integer-utils.bcpl`

```text
ABS(N)
MIN(A,B)
MAX(A,B)
SIGN(N)
GCD(A,B)
IPOW(BASE,EXP)
```

`IPOW` is integer exponentiation.  A negative exponent returns 0; exponent zero returns 1.

### `string-utils.bcpl`

Utilities for ordinary packed BCPL strings:

```text
STRLEN(S)
STRCMP(A,B)
STRCPY(DST,SRC)
STRCAT(DST,SRC)
STRCHR(S,CH)
```

BCPL strings carry their byte length in byte zero.  `STRCPY` and `STRCAT` do not allocate storage or perform bounds checking; the caller must supply a writable destination large enough for the result.  `STRCHR` returns the one-based character position, or 0 if no match is found.

### `memory-utils.bcpl`

Byte-oriented operations:

```text
MEMCPY(DST,SRC,N)
MEMSET(DST,VALUE,N)
MEMCMP(A,B,N)
```

and word-vector operations:

```text
VECCOPY(DST,SRC,N)
VECCLEAR(V,N)
```

`MEM*` counts bytes from byte offset zero.  `VEC*` counts BCPL words from word offset zero.  `MEMCPY` currently has ordinary forward-copy semantics and is not specified for overlapping regions.

### `numeric-conversion.bcpl`

```text
ATOI(S)
ITOA(N,S)
HEXTOI(S)
ITOHEX(N,S)
```

`ITOA` and `ITOHEX` write into caller-provided packed-string storage.  `ATOI` accepts an optional leading sign and stops at the first non-decimal digit.  `HEXTOI` accepts upper- or lower-case hexadecimal digits and stops at the first non-hexadecimal character.  `ITOHEX` currently accepts non-negative integers.

### `char-utils.bcpl`

```text
ISDIGIT(CH)
ISALPHA(CH)
ISSPACE(CH)
TOUPPER(CH)
TOLOWER(CH)
```

These operate on the bootstrap BCPL character model.  `ISSPACE` recognizes space, tab, and newline.

### `line-io.bcpl`

```text
READLINE(S,MAX)
WRITELINE(S)
```

`READLINE` reads from the currently selected input stream, stores at most `MAX` characters in `S`, and consumes the rest of an overlong input line through newline.  It returns the number of stored characters, or `-1` for immediate end-of-stream.  `WRITELINE` writes a packed string to the currently selected output stream followed by newline.

A named MVS input DD can therefore be used with the ordinary historical stream interface:

```bcpl
S := FINDINPUT("INPUT")
SELECTINPUT(S)
N := READLINE(BUF, 80)
ENDREAD()
```

with a host invocation such as:

```sh
tools/compile-and-run --results \
    --dd INPUT=input.txt \
    "$(tools/current-icint)" \
    main.bcpl \
    +library/line-io.bcpl
```

## Runtime-oriented modules

### `getvec-freevec.bcpl`

Provides the reconstruction allocator:

```text
GETVEC:87
FREEVEC:88
HEAPINIT:89
FREEHEAD:90
```

`HEAPINIT(BASE, WORDS)` installs an already BCPL-addressable arena. `GETVEC(N)` returns storage for a BCPL `VEC N`, and `FREEVEC(V)` reinserts and coalesces the block.  The allocator deliberately keeps BCPL storage inside ICINT's existing word-address space.

### `coroutines.bcpl`

Provides the portable coroutine layer:

```text
CREATECO:91
DELETECO:92
CALLCO:93
COWAIT:94
RESUMECO:95
```

It depends on historical runtime state `CHANGECO:6`, `CURRCO:7`, `COLIST:8` and on `GETVEC`/`FREEVEC`.  `CHANGECO` remains machine-dependent; the portable coroutine interface does not depend on how the backend performs the actual context switch.

## GLOBAL convention

The shared global vector is the linkage ABI.  New reusable routines must not pick numbers independently in demonstrations or tests.  The current project convention is documented in [`GLOBALS.md`](GLOBALS.md):

```text
through 86   historical/bootstrap assignments
87..95       reconstruction runtime assignments
96..159      reconstruction general-library assignments
```

The 96..159 assignments are reconstruction-local pending eventual reconciliation with a consolidated historical/runtime header.

## Regression coverage

The regression panel includes focused `standard-library` cases covering:

- deterministic random generation;
- integer utilities;
- character classification and case conversion;
- packed-string operations;
- byte memory and word-vector operations;
- decimal and hexadecimal conversion;
- line input/output through a named DD stream;
- the pre-existing historical basic library surface.

Run all standard-library regressions with:

```sh
tools/run-regression-panel --category standard-library
```

The allocator and coroutine layers remain covered by their `storage` and `coroutines` regression categories.
