# How to Compile and Run BCPL Programs

*Cambridge BCPL Programming System for MVS 3.8J*

This guide separates recipient MVS application JCL from development-host automation. Use the [language tutorial](Tutorial-on-BCPL-Programming.md) for learning BCPL and the [compiler reference](Reference-for-BCPL-Compilers.md) for options and ABI details. The worked examples reproduce tracked, accepted sources and selected JCL; a new adapted job requires its own verification.

## 1. Choose compiler and verify installation scope

| Environment | Compilation | Execution |
| --- | --- | --- |
| RC4 MR10 or COMBINED | SYNI/TRNI then CGI under installed ICINT19 | Application INTCODE under ICINT19 |
| RC4 NATIVE | No supported compiler | Inventory/source study |
| Reconstructed development system | Interpreter-hosted demoted Cambridge Compiler (CAMBCOMP) | Generated native System/370 through IFOX/IEWL |
| Native-running Cambridge Compiler | Unfinished | Not a supported workflow |

RC4 does not include CAMBCOMP or a usable native-running Cambridge Compiler. The native development pipeline is not an RC4 functional acceptance claim. See [Explanation of BCPL Compilers](Explanation-of-BCPL-Compilers.md).

## 2. Prepare source members, headers and DDs

Use valid BCPL for the chosen compiler. In the MR10 examples a program declares START:1 and the library globals it uses; local declarations precede executable commands. Use authorized user/scratch source members rather than editing shipped samples. Preserve FB80 transport and the source record shape. Include headers via supported GET/named input arrangements or declare the appropriate globals explicitly. Do not mix native LIBHDR and MR10-local declarations or assume every header transport is identical.

For MR10 compile steps SYSIN is BCPL source, INTIN contains SYNI/TRNI/BLIBI/ICLIB, OCODE is output. Generation reads OCODE via SYSIN, runs CGI/BLIBI/ICLIB and writes INTCODE. Execution INTIN starts with generated application decks and includes support decks. OPTIONS DD is the historical MR10 option-record input (not EXEC PARM). Use the [compiler reference](Reference-for-BCPL-Compilers.md) for switch meanings; do not alter default workspace conventions casually.

## 3. Compile and run an MR10 program with installed ICINT19

Begin with the installed MRREGRES body in your MR10KIT.JCL, or the original [tracked body](../../mr10-kit-compiler/jcl/run-regression-tests.jcl). Run the complete supplied job as described in the [operation guide](How-to-Operate-the-BCPL-Programming-System.md). For a focused standalone job, the following is an exact selection of its five staging steps, C01A/G01A and R01. The extracted subset has not been independently resubmitted as a new deck for this manual.

The example source is the installed TESTS(SCALVEC), from [scalar-vector.bcpl](../../mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.bcpl):


```bcpl
// ======================================================================
// SCALAR VECTOR: BCPL REGRESSION TEST
// ======================================================================
// Regression: scalar assignment and vector load/store.
// --- Global slots ---
GLOBAL $( START:1; WRITEF:76 $)

// --- Test entry and result ---
LET START() BE
$(
 LET A = 17
   AND B = 42
   AND V = VEC 3

   WRITEF("TEST: Scalar assignments and vector load/store*N")
   WRITEF("EXP: SCALAR 17 42*N")
   WRITEF("EXP: VECTOR 5 10 15 20*N")
   V!0 := 5
   V!1 := 10
   V!2 := 15
   V!3 := 20

   WRITEF("RP: SCALAR %N %N*N", A, B)
   WRITEF("RP: VECTOR %N %N %N %N*N", V!0, V!1, V!2, V!3)
   FINISH
$)
```

Copy the following sections in order to a working deck, add your authorized JOB card, replace all HERC02.BCPL.MR10KIT. prefixes with the actual installed site prefix (for example HERC02.BCPL.R4MR.MR10KIT.), preserve card columns, and use the site's normal end-of-job handling. Do not submit any section alone.

**Stage five sequential phase decks:** PDS-member copying before concatenation is intentional. These temporary datasets are passed to the later compiler/application steps.


```jcl
//SSYNI    EXEC PGM=IEBGENER
//SYSPRINT DD  DUMMY
//SYSIN    DD  DUMMY
//SYSUT1   DD  DSN=HERC02.BCPL.MR10KIT.SOURCE(SYNI),
//             DISP=SHR
//SYSUT2   DD  DSN=&&SYNI,UNIT=SYSDA,
//             SPACE=(80,(1000,500)),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=80),
//             DISP=(NEW,PASS)
//*
//STRNI    EXEC PGM=IEBGENER
//SYSPRINT DD  DUMMY
//SYSIN    DD  DUMMY
//SYSUT1   DD  DSN=HERC02.BCPL.MR10KIT.SOURCE(TRNI),
//             DISP=SHR
//SYSUT2   DD  DSN=&&TRNI,UNIT=SYSDA,
//             SPACE=(80,(1000,500)),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=80),
//             DISP=(NEW,PASS)
//*
//SCGI     EXEC PGM=IEBGENER
//SYSPRINT DD  DUMMY
//SYSIN    DD  DUMMY
//SYSUT1   DD  DSN=HERC02.BCPL.MR10KIT.SOURCE(CGI),
//             DISP=SHR
//SYSUT2   DD  DSN=&&CGI,UNIT=SYSDA,
//             SPACE=(80,(1000,500)),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=80),
//             DISP=(NEW,PASS)
//*
//SBLIBI   EXEC PGM=IEBGENER
//SYSPRINT DD  DUMMY
//SYSIN    DD  DUMMY
//SYSUT1   DD  DSN=HERC02.BCPL.MR10KIT.SOURCE(BLIBI),
//             DISP=SHR
//SYSUT2   DD  DSN=&&BLIBI,UNIT=SYSDA,
//             SPACE=(80,(1000,500)),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=80),
//             DISP=(NEW,PASS)
//*
//SICLIB   EXEC PGM=IEBGENER
//SYSPRINT DD  DUMMY
//SYSIN    DD  DUMMY
//SYSUT1   DD  DSN=HERC02.BCPL.MR10KIT.SOURCE(ICLIB),
//             DISP=SHR
//SYSUT2   DD  DSN=&&ICLIB,UNIT=SYSDA,
//             SPACE=(80,(1000,500)),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=80),
//             DISP=(NEW,PASS)
//*
```

**Compile and generate SCALVEC:**


```jcl
//C01A     EXEC PGM=ICINT19,REGION=1024K,COND=(4,LT)
//STEPLIB  DD  DSN=HERC02.BCPL.MR10KIT.LOAD,DISP=SHR
//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
//INTIN    DD  DSN=&&SYNI,DISP=(OLD,PASS)
//         DD  DSN=&&TRNI,DISP=(OLD,PASS)
//         DD  DSN=&&BLIBI,DISP=(OLD,PASS)
//         DD  DSN=&&ICLIB,DISP=(OLD,PASS)
//SYSIN    DD  DSN=HERC02.BCPL.MR10KIT.TESTS(SCALVEC),
//             DISP=SHR
//OCODE    DD  DSN=&&O01A,UNIT=SYSDA,
//             SPACE=(80,(1000,500)),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=80),
//             DISP=(NEW,PASS)
//SYSUDUMP DD  DUMMY
//*
//* G01A GENERATE SCALVEC
//G01A     EXEC PGM=ICINT19,REGION=1024K,COND=(4,LT)
//STEPLIB  DD  DSN=HERC02.BCPL.MR10KIT.LOAD,DISP=SHR
//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
//INTIN    DD  DSN=&&CGI,DISP=(OLD,PASS)
//         DD  DSN=&&BLIBI,DISP=(OLD,PASS)
//         DD  DSN=&&ICLIB,DISP=(OLD,PASS)
//INTCODE  DD  DSN=&&I01A,UNIT=SYSDA,
//             SPACE=(80,(1000,500)),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=80),
//             DISP=(NEW,PASS)
//SYSIN    DD  DSN=&&O01A,DISP=(OLD,DELETE)
//SYSUDUMP DD  DUMMY
//*
```

**Execute generated INTCODE:**


```jcl
//R01      EXEC PGM=ICINT19,REGION=1024K,COND=(4,LT)
//STEPLIB  DD  DSN=HERC02.BCPL.MR10KIT.LOAD,DISP=SHR
//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
//INTIN    DD  DSN=&&I01A,DISP=(OLD,DELETE)
//         DD  DSN=&&BLIBI,DISP=(OLD,PASS)
//         DD  DSN=&&ICLIB,DISP=(OLD,PASS)
//SYSUDUMP DD  DUMMY
//*
```

Require all eight steps RC0000, and all three interpreted CODE results zero. The application should print the scalar/vector TEST identity, literal EXP records and actual RP records matching [independent expected](../../mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.expected):


```text
RP: SCALAR 17 42
RP: VECTOR 5 10 15 20
```

When adapting to your own program, use the actual source member and required DDs, keep temporary deck lifetimes consistent, and define an independent expected result. A complete supplied suite was accepted; the extracted/retargeted single job needs a fresh run in your environment.

## 4. Compile separately and combine MR10 modules where supported

The accepted MRREGRES case 06 is a two-unit example. Both modules declare HELPER:180 (test-local, not a generally allocated library slot). Only main declares START. [Main source](../../mr10-kit-compiler/tests/00-regression-panel/modules/main.bcpl):


```bcpl
// ======================================================================
// MAIN: BCPL REGRESSION TEST
// ======================================================================
// Regression: separate compilation and GLOBAL-vector linkage.
// --- Global slots ---
GLOBAL $( START:1; WRITEF:76; HELPER:180 $)

// --- Test entry and result ---
LET START() BE
$(
   WRITEF("TEST: Separate compilation and GLOBAL linkage*N")
   WRITEF("EXP: MODULE 43*N")
 WRITEF("RP: MODULE %N*N", HELPER(14))
   FINISH
$)
```

[Helper source](../../mr10-kit-compiler/tests/00-regression-panel/modules/helper.bcpl):


```bcpl
// ======================================================================
// HELPER: BCPL REGRESSION TEST
// ======================================================================
// Regression helper module.
// --- Global slots ---
GLOBAL $( HELPER:180 $)

LET HELPER(N) = N*3+1
```

Use C06A/G06A and C06B/G06B in the original MRREGRES to compile/generate separately, after the same five staging steps. R06 concatenates both generated INTCODE units before BLIBI/ICLIB:


```jcl
//R06      EXEC PGM=ICINT19,REGION=1024K,COND=(4,LT)
//STEPLIB  DD  DSN=HERC02.BCPL.MR10KIT.LOAD,DISP=SHR
//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
//INTIN    DD  DSN=&&I06A,DISP=(OLD,DELETE)
//         DD  DSN=&&I06B,DISP=(OLD,DELETE)
//         DD  DSN=&&BLIBI,DISP=(OLD,PASS)
//         DD  DSN=&&ICLIB,DISP=(OLD,PASS)
//SYSUDUMP DD  DUMMY
//*
```

The independent [expected result](../../mr10-kit-compiler/tests/00-regression-panel/modules/separate-module.expected) is:


```text
RP: MODULE 43
```

Do not concatenate OCODE as a substitute for the tested independent generation/linkage arrangement. MR10-local helpers (allocator, integer/string/memory, random and coroutine modules) are selected by adding their BCPL compilation units; consult the [library README](../../mr10-kit-compiler/library/README.md) and [GLOBALS map](../../mr10-kit-compiler/library/GLOBALS.md). Header declarations alone install no executable definitions.

On the development host, the existing installed-interpreter automation equivalent for a single scalar-vector case is documented in [MR10 tools](../../tools/mr10/README.md):


```sh
tools/mr10/compile-and-run --installed-icint MR10_LOAD --results \
  mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.bcpl
```

This submits real MVS jobs and resolves the development manifest, not a recipient site prefix; do not use it blindly against RC4 libraries.

## 5. Compile native applications on the development system — CAMBCOMP, IFOX, IEWL and GO

Prerequisites: installed ICINT19, resident BOOT_INTCODE(CAMBCOMP), appropriate BOOT_SOURCE headers and CAMBPARM, accepted production BOOT_OBJ and MVS IFOX/IEWL. The [bootstrap guide](../../bootstrap-toolchain/bootstrap-cambridge/README.md) explains the compiler image. This is a development workflow, not supported RC4 recipient use.

Use [native regression 075](../../tests/bootstrap/075-blib-writef-mixed-object/source.bcpl) as a complete known application:


```bcpl
GLOBAL $( START:1; WRITEF:76 $)

LET START () BE
$(1
    WRITEF("C:%C S:%S N:%N", 'Z', "HI", 42)
    FINISH
$)1
```

For the full compile/assemble/link/GO workflow with installed production runtime objects, use the existing bounded native runner:


```sh
tools/bootstrap/run-production-regression 75
```

Its expected record is [075 golden](../../tests/bootstrap/075-blib-writef-mixed-object/expected.txt):


```text
C:Z S:HI N:42
```

The runner compiles the BCPL source on MVS under ICINT19/CAMBCOMP, assembles recovered System/370 CODE with IFOX, link-edits with IEWL and runs native GO. It checks actual output; the [075 evidence](../../tests/bootstrap/075-blib-writef-mixed-object/README.md) preserves an earlier wrong-output run and the subsequent G!76 binding correction.

For a separate compilation step (does not assemble/link/run the recovered application), the existing [compile-mvs driver](../../tools/bootstrap/compile-mvs) accepts a source path and disposable output path. Example invocation, not a newly executed job:


```sh
tools/bootstrap/compile-mvs \
  tests/bootstrap/075-blib-writef-mixed-object/source.bcpl \
  --job-name BCPL075 --output workarea/bcpl075.s370.asm
```

Use an unused disposable output path: the driver removes a pre-existing output before building the deck, including on its --show-jcl preview path. The driver submits an ICINT19 compiler job, obtains textual FB80 CODE, and validates/reconstructs assembler output. The current CAMBPARM starts /N/ with slash-fill to 80 columns; N suppresses direct binary SYSGO. Do not remove N or substitute the historical EXEC PARM interface. See [compiler reference](Reference-for-BCPL-Compilers.md).

## 6. Link runtime, libraries and optional packages

For the native development pipeline, assemble the recovered CODE with IFOX, using actual required macros and object-deck DDs. Link with IEWL using accepted production runtime/BLIB objects, exactly one application BCPLREG (empty when no packages) and explicit application ENTRY. Use the regression runner's generated JCL and MAP as the concrete model; it is not an unrestricted general-purpose link editor recipe for arbitrary modules.

BCPL globals are registered from actual exports and selected package descriptors, not just source declarations. The [runtime/library reference](Reference-for-the-Cambridge-Runtime-and-Libraries.md) gives current roles and boundaries. Optional System Extensions use BCXSEL/BCXREQ and BCEX/BCRG; see [How to Use System Extensions](How-to-Use-System-Extensions.md). COROUTIN and BCPLCO supply bounded native coroutine support with separate lifecycle/registration requirements. Do not assume all arbitrary BCPL library objects use the same import mechanism. Do not link unverified candidates or override global ownership.

## 7. Inspect JES output, return codes and application results

For MR10 require each staging/compile/generate/run step, zero JES RC and interpreted CODE, correct TEST identity and literal EXP/evaluated RP versus independent golden. A compile diagnostic must be addressed even if G/R steps run. For a new program define input, expected results and required records before execution.

For native compilation require the compiler/interpreter result, valid generated assembler, actual IFOX RC/severity, IEWL RC/MAP/XREF and native GO result. Compare exact records and expected condition code. Native GO is not an ICINT CODE result. A zero step RC alone cannot prove behavior: case 075 originally emitted N:2 rather than N:42 with zero step RCs. Preserve original failures and subsequent corrected results.

## 8. Diagnose compilation, assembly, linkage and execution failures

| Stage | Inspect |
| --- | --- |
| Compile | First diagnostic, dialect, GET inputs, options, source and interpreted CODE |
| Generate | OCODE, CGI or CG370 options, emitted INTCODE or CODE completeness |
| Assemble | Actual IFOX listing, symbols, card columns, macro expansion and severity |
| Link | Object selection, unresolved externals, application ENTRY, global registration, MAP/XREF |
| Execute | Actual input DD, stack/storage, expected records, CODE or GO RC/abend |
| Submission/transport | Known job identity, full JES output and actual state before retry |

Use the [operation guide](How-to-Operate-the-BCPL-Programming-System.md) for evidence preservation. Do not change a golden result just to produce PASS, overwrite installed libraries, or promote runtime candidates as part of application troubleshooting. For unsupported compiler/extension behaviors consult their qualified reference and accepted milestone evidence. No new MVS execution or new compilation guarantee follows from these extracted examples.
