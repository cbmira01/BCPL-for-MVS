# Tutorial on System Extensions

*Cambridge BCPL Programming System for MVS 3.8J*

Learn to select a package, discover its capabilities, retrieve data and handle a controlled capacity error using BCPLDEMO, the permanent supported reference System Extension. This tutorial uses existing accepted native regression applications, not a newly invented build procedure.

## 1. Prepare an eligible development environment

Use the established MVS 3.8J development installation: ICINT19, interpreter-hosted demoted Cambridge Compiler (CAMBCOMP), IFOX00, IEWL, native Core Runtime/Base Library, BCPLRGS, BCX selection macros and BCPLDEMO. For installed-mode exercises use the verified resident objects and macros. See the [clean-room guide](../Rebuild-BCPL-for-MVS-from-source.md) if reconstruction is necessary; do not overwrite working datasets just to learn.

RC4 does not include CAMBCOMP or a usable native-running Cambridge Compiler. Native components are work in progress in RC4. These exercises require the development environment and authorization to submit real MVS jobs; they do not install permanent objects. The exact accepted regression fixtures below remain unchanged. DR.5 corrected the native *N/NEWLINE() incompatibility with BCPLIO's numeric-10 delimiter. JOB 9504 independently verified record boundaries with rebuilt CAMBCOMP and BLIB. Older objects retain former behavior. A short message flushed by FINISH alone does not establish a newline boundary. See the [runtime reference](Reference-for-the-Cambridge-Runtime-and-Libraries.md).

## 2. Discover BCPLDEMO and its header

Read [bcpldemo.h](../../system-extensions/bcpldemo/bcpldemo.h): DEMOSVC:203, DEMO_QUERY=0 and DEMO_GETVALUES=1. One global dispatches multiple operations. A header does not link code or register the global. QUERY must not be used to discover an absent package.

## 3. Write a client and perform QUERY

Here is the complete accepted [regression 148](../../tests/runtime-extensions/148-bcpldemo-query-fields/source.bcpl). It explicitly declares the global because extension-header GET transport is not exercised by this example.


```bcpl
// R.5 NATIVE BCPL REGRESSION 148.
GLOBAL $( START:1; STOP:30; WRITES:60; NEWLINE:63;
          DEMOSVC:203 $)
LET START() BE
$(1
    LET INFO = VEC 6
    IF DEMOSVC(0,INFO,6) NE 6 DO STOP(8)
    IF INFO!0 NE 1 | INFO!1 NE 1 DO STOP(8)
    IF INFO!2 NE 0 | INFO!3 NE 6 DO STOP(8)
    IF INFO!4 NE 1 | INFO!5 NE 0 DO STOP(8)
    WRITES("R5 EXT 148 PASS")
    NEWLINE()
    FINISH
$)1
```

VEC 6 allocates seven words; this client advertises six. QUERY returns a word count, not status zero. Its fields describe format 1, API 1.0, length 6, bitmap 1 and flags 0. Bit zero advertises opcode 1.

## 4. Select, compile, assemble, link and run

The [selection file](../../tests/runtime-extensions/148-bcpldemo-query-fields/extension-selection.asm) contains:


```asm
         BCXREQ BCPLDEMO
```

The runner compiles under ICINT19/CAMBCOMP, assembles the application and registry through IFOX, includes the required runtime and selected package through IEWL, and executes native GO. BCXREQ selects the package and records its requirement in BCPLREG.

From the development repository root use the existing MVS-facing runner:


```sh
tools/bootstrap/run-installed-r5-t1-regression 148
```

This is read-only installed-package linkage with temporary job outputs. The source-mode alternative is tools/bootstrap/run-production-regression 148. Keep receipts for the two modes distinct.

## 5. Inspect returned values and expected output

The [expected record](../../tests/runtime-extensions/148-bcpldemo-query-fields/expected.txt) is:


```text
R5 EXT 148 PASS
```

Require actual runner PASS, successful relevant JES steps and an IEWL MAP consistent with BCPLREG and DMODISP/descriptor inclusion. A successful RC alone is not sufficient. The compiler executes interpreted code, but the application executes native System/370 instructions. R.5 evidence establishes these exercises; this drafting increment has not rerun them.

## 6. Modify and rerun; learn from a controlled failure

Use [case 151](../../tests/runtime-extensions/151-bcpldemo-getvalues/source.bcpl) to call GETVALUES and check the guard word beyond the advertised capacity:


```bcpl
// R.5 NATIVE BCPL REGRESSION 151.
GLOBAL $( START:1; STOP:30; WRITES:60; NEWLINE:63;
          DEMOSVC:203 $)
LET START() BE
$(1
    LET VALUES = VEC 3
    VALUES!3 := 777
    IF DEMOSVC(1,VALUES,3) NE 3 DO STOP(8)
    IF VALUES!0 NE 10 | VALUES!1 NE 20 DO STOP(8)
    IF VALUES!2 NE 30 | VALUES!3 NE 777 DO STOP(8)
    WRITES("R5 EXT 151 PASS")
    NEWLINE()
    FINISH
$)1
```

Use [case 149](../../tests/runtime-extensions/149-bcpldemo-query-short/source.bcpl) to learn the controlled short-buffer response:


```bcpl
// R.5 NATIVE BCPL REGRESSION 149.
GLOBAL $( START:1; STOP:30; WRITES:60; NEWLINE:63;
          DEMOSVC:203 $)
LET START() BE
$(1
    LET INFO = VEC 6
    INFO!0 := 777
    INFO!1 := 888
    INFO!6 := 999
    IF DEMOSVC(0,INFO,5) NE -1 DO STOP(8)
    IF INFO!0 NE 777 | INFO!1 NE 888 DO STOP(8)
    IF INFO!6 NE 999 DO STOP(8)
    WRITES("R5 EXT 149 PASS")
    NEWLINE()
    FINISH
$)1
```

Run the existing cases, including case 150 for invalid arguments:


```sh
tools/bootstrap/run-installed-r5-t1-regression 149 151
```

Expected records for 149 and 151, in that order:


```text
R5 EXT 149 PASS
R5 EXT 151 PASS
```

The negative package status in 149 is intended; the application must still pass. In a separate private exercise, predict what would happen if the capacity were changed from 5 to 6: return 6 and changed descriptor words, so the original assertions would no longer apply. This modification is untested. Do not alter the accepted regression or its oracle.

## 7. Next steps — time, record I/O and shared references

Try the [BCPLTIME direct caller](../../system-extensions/bcpltime/test.bcpl) and the [BCPLQSAM fixed-record example](../../tests/system-extensions/bcplqsam/168-qsam-fixed-full/README.md). The latter includes independent MVS record verification.

Use [How to Use System Extensions](How-to-Use-System-Extensions.md) for practical selection and I/O, [Explanation of System Extensions](Explanation-of-System-Extensions.md) for architecture, and [Reference for System Extensions](Reference-for-System-Extensions.md) for numerical interfaces.
