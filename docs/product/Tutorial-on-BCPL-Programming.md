# Tutorial on BCPL Programming

*Cambridge BCPL Programming System for MVS 3.8J — MR10 Kit Compiler*

This tutorial teaches BCPL by running and modifying existing programs. Use the MR10 or COMBINED installation of release candidate BCPL-0.1.0-rc4. The MR10 Kit Compiler and its applications execute as INTCODE under ICINT19. The interpreter-hosted demoted Cambridge Compiler generates native System/370 application code in the reconstruction environment; it and the unfinished native-running Cambridge Compiler are not distributed as usable compilers in RC4.

Before starting, have an installed system, access to JES output, an authorized JOB card and a working copy of the supplied suite JCL. Follow the [RC4 companion guide](../../packaging/distribution/publication/RC4-README.md) for installation and site substitutions. The [language reference](Reference-for-the-BCPL-Language.md) describes syntax and dialect boundaries.

**How to use the examples:** run the unmodified installed examples first. The complete repository examples linked below are the exercises; snippets are extracts, not additional standalone programs. Predicted output for demonstrations is derived from the source; regression output is taken from independent golden files. RC4 acceptance covers the unchanged suites. Your modifications need their own runs. The tutorial exercises use MR10. The corrected native development compiler and rebuilt BLIB also use logical newline 10 (JOB 9504); older builds had an incompatible mapping of 37. See the [runtime reference](Reference-for-the-Cambridge-Runtime-and-Libraries.md) before adapting examples for native execution.

## 1. Your first BCPL program

Open the [integer-arithmetic regression](../../mr10-kit-compiler/tests/00-regression-panel/calculation/integer-arithmetic.bcpl). Here is its executable source, with introductory comments omitted:


```bcpl
GLOBAL $( START:1; WRITEF:76 $)

LET START() BE
$(
 LET A = 17
   AND B = 5
   WRITEF("TEST: Integer arithmetic and remainder*N")
   WRITEF("EXP: ARITH 22 12 85 3 2*N")
   WRITEF("RP: ARITH %N %N %N %N %N*N",
          A+B, A-B, A*B, A/B, A REM B)
   FINISH
$)
```

GLOBAL associates START with slot 1 and WRITEF with slot 76. START is the application's entry routine. LET introduces local words, WRITEF writes formatted text (%N prints an integer; *N is a newline in this MR10 environment) and FINISH terminates the application.

Run the supplied MRREGRES member of MR10KIT.JCL. Copy it to a submission deck, replace the development prefix HERC02.BCPL.MR10KIT. with your installed prefix (e.g. HERC02.BCPL.R4MR.MR10KIT.), and add your authorized JOB card. The original must remain intact. The job stages the compiler and library INTCODE, compiles source to OCODE (C steps), generates INTCODE (G steps), then runs applications (R steps).

Inspect the case's TEST, EXP and RP records and compare with [the expected record](../../mr10-kit-compiler/tests/00-regression-panel/calculation/integer-arithmetic.expected):


```text
RP: ARITH 22 12 85 3 2
```

Require zero JES step return codes, zero interpreted CODE values and matching results. A successful MVS step alone is insufficient. To experiment, copy the source to an authorized scratch member and adapt a copy of the corresponding compile/generate/run sequence in [MRREGRES source](../../mr10-kit-compiler/jcl/run-regression-tests.jcl); do not overwrite shipped members or change the regression oracle. Change A from 17 to 18 and predict the new result before running it (23, 13, 90, 3, 3).

The MRLANGDM and MRBCDEMO members similarly run the language and application examples below. See [suite jobs](../../mr10-kit-compiler/jcl/README-SUITES.md) for development-checkout usage; its installation commands are not required on a restored RC4 system.

## 2. Constants, variables and declarations

Run [declarations](../../mr10-kit-compiler/language-demo/declarations/declarations.bcpl) using MRLANGDM. Local A, B and C are initialized to 10, 20 and 30. A nested block introduces another B with value 200; the outer B remains 20 after the block. D is calculated inside the inner block. Observe the printed outer and inner values.


```bcpl
LET A = 10
AND B = 20
AND C = 30
```

LET declarations precede executable commands within a block. A subsequent assignment uses := rather than =. MANIFEST introduces compile-time constants; try [manifest-global](../../mr10-kit-compiler/language-demo/manifest-global/manifest-global.bcpl) and observe ANSWER=42 and TIMESCALE(7)=21. Change the SCALE constant in a scratch copy and predict the output. Use numeric constants or previously bound MANIFEST names with simple arithmetic. The MR10 compile-time evaluator is narrower than its ordinary expression evaluator; see the language reference.

## 3. Expressions and operators

Return to integer-arithmetic. Evaluate addition, subtraction, multiplication, integer division and remainder. The positive calculation 17/5 gives 3 and 17 REM 5 gives 2.

Run [boolean-operators](../../mr10-kit-compiler/language-demo/boolean-operators/boolean-operators.bcpl). Compare `A<B`, `A=B`, and `A\=B`; combine conditions using `/\` and `\/`. The backslash prefix negates a logical value. Parenthesize mixed expressions to make intent clear. BCPL words can represent integers, bit patterns or logical values; do not import the Boolean rules of another language.

Exercise: predict which comparisons in the example are true, then change B to 7 in your scratch copy. Compare the numeric truth representations printed by WRITEF. Use TRUE/FALSE or a comparison as a condition, rather than an arbitrary nonzero integer. Logical operators used to produce a word are not the same as the compiler's conditional branching path; do not depend on short circuit in a value expression. Sequence calls with observable side effects in separate commands.

## 4. Conditional execution and iteration

Run [repeat-forms](../../mr10-kit-compiler/language-demo/repeat-forms/repeat-forms.bcpl). Each loop prints 1, 2, 3. REPEATWHILE tests after executing its body, REPEATUNTIL stops when its test becomes true, and REPEAT with BREAK leaves the loop explicitly.


```bcpl
FOR I = 1 TO 4 DO S := S+I
```

This fragment from [branches-loops](../../mr10-kit-compiler/tests/00-regression-panel/control/branches-loops.bcpl) sums four integers to 10. Its SWITCHON chooses among numbered cases and a DEFAULT. Run [switchon](../../mr10-kit-compiler/language-demo/switchon/switchon.bcpl) to see ENDCASE and grouped case labels. Try changing the loop bound to 5; predict S=15. If you use BY, use a compile-time constant, not a variable step. Avoid zero steps. These exercises use the increasing-loop domain already demonstrated by the suite. Inspect [TEST/THEN/OR](../../mr10-kit-compiler/language-demo/test-then-or/test-then-or.bcpl) for a two-way decision.

## 5. Functions and routines

Run the [nested-recursion regression](../../mr10-kit-compiler/tests/00-regression-panel/calls/nested-recursion.bcpl):


```bcpl
GLOBAL $( START:1; WRITEF:76 $)

LET ADD3(A,B,C) = A+B+C

AND FACT(N) = N=0 -> 1, N*FACT(N-1)

AND START() BE
$(
   WRITEF("TEST: Arguments nested calls and recursive factorial*N")
   WRITEF("EXP: CALLS 9 120*N")
 WRITEF("RP: CALLS %N %N*N", ADD3(2,3,4), FACT(5))
   FINISH
$)
```

A function defined with = supplies a value; a routine defined with BE executes commands. AND joins definitions. The conditional expression selects one of two expressions; FACT stops recursively calling itself when N=0. Expected result: RP: CALLS 9 120. Try FACT(6), which should yield 720, not an unlimited-precision value.

Study [VALOF/RESULTIS](../../mr10-kit-compiler/language-demo/valof-resultis/valof-resultis.bcpl) to compute a function result using a command block, and [function values](../../mr10-kit-compiler/language-demo/function-values/function-values.bcpl) to pass SQUARE or DOUBLE to APPLY. Its two calls with 7 produce 49 and 14. Do not assume nested procedures provide modern closures.

## 6. Vectors, pointers and indirection

Run [pointer-idioms](../../mr10-kit-compiler/language-demo/pointer-idioms/pointer-idioms.bcpl):


```bcpl
LET V = VEC 4
LET P = V
```

VEC 4 reserves five words, indexed 0 through 4. Its bound is a compile-time constant; use the library allocation operation for a size computed at runtime. P copies the word address, not the contents. When swapping two words, use a temporary word rather than assuming that comma-separated assignment evaluates every right-hand side before storing. The example fills V with 10, 20, 30, 40, 50, then assigns P!2 := 99 and observes V!2=99. Do not dereference outside the allocated extent. @ obtains an address; ! reads or writes a word through an address. See the [scalar/vector regression](../../mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.bcpl) and [TABLE/vector demonstration](../../mr10-kit-compiler/language-demo/table-vector/table-vector.bcpl). Exercise: modify the fourth element through P and print it through V.

## 7. Strings and character manipulation

Run [strings-bytes](../../mr10-kit-compiler/language-demo/strings-bytes/strings-bytes.bcpl). A string is packed into words with a length byte at offset 0. GETBYTE(S,0) for "BCPL" returns 4. GETBYTE(S,1) through GETBYTE(S,4) return character codes. Do not assume the codes are ASCII. WRITEF("%S*N", S) prints the string followed by a newline.

The [bytes regression](../../mr10-kit-compiler/tests/00-regression-panel/data-movement/bytes.bcpl) writes and reads numeric byte values 65, 66, 67, 68. It tests byte preservation, not the spelling of these characters. PUTBYTE modifies caller-owned storage. Never assume a string literal can be modified safely. Exercise: change the demonstration string in a scratch source to "MVS" and observe length 3.

## 8. Global variables and separate compilation

Read [main](../../mr10-kit-compiler/tests/00-regression-panel/modules/main.bcpl) and [helper](../../mr10-kit-compiler/tests/00-regression-panel/modules/helper.bcpl). Both declare HELPER:180. The helper defines the function; the main calls it. The MRREGRES job compiles the modules separately and supplies both generated decks to the interpreter. Its expected result is RP: MODULE 43.

A GLOBAL declaration describes a slot in the shared vector; it is not an implementation or a request to allocate a new number. Slot 180 here belongs to this isolated regression example, not an allocation for a new package. Reusable MR10 library assignments are in [GLOBALS.md](../../mr10-kit-compiler/library/GLOBALS.md); the project [Global Number Registry](../../packaging/architecture/global-number-registry.md) retains its own allocation authority. Exercise: in scratch copies change the helper formula and rerun the two-module program.

## 9. Dynamic memory management

Run the [GETVEC/FREEVEC regression](../../mr10-kit-compiler/tests/00-regression-panel/storage/getvec-reuse.bcpl). In this MR10 implementation the caller provides an arena to HEAPINIT. The example uses VEC 100 (101 words), initializes the arena, allocates GETVEC(5) (six payload words), frees it and allocates again. Expected result: RP: GETVEC 0 11 13. The zero is the address difference in this specific reuse test, not a portable guarantee.

Inspect the [allocator source](../../mr10-kit-compiler/library/getvec-freevec.bcpl). GETVEC returns zero on failure; check it before accessing storage. FREEVEC releases an owned allocation; never free a local vector, free twice, or access storage after release. Keep the arena alive while its allocations exist. The small regression assumes allocation succeeds; production code must check failure. Native memory management is a separate implementation.

## 10. Data structures and algorithms

Run [binary-search](../../mr10-kit-compiler/bcpl-demo/binary-search/binary-search.bcpl) in MRBCDEMO. It fills a 16-word vector with squares, then searches for five keys. Expected observations: 49, 81, 100 and 169 at indices 7, 9, 10 and 13; 250 not found. Understand why the midpoint comparison discards half the remaining range. A sorted input is essential.

Next inspect [quicksort](../../mr10-kit-compiler/bcpl-demo/quicksort/quicksort.bcpl) (with its additional random module), [linked-list](../../mr10-kit-compiler/bcpl-demo/linked-list/linked-list.bcpl) and [binary-tree](../../mr10-kit-compiler/bcpl-demo/binary-tree/binary-tree.bcpl). Use the supplied suite to provide dependencies. Draw the vector or node links, then follow a small example by hand. In a scratch binary-search copy, replace an unsuccessful key with 225 and predict index 15. Verify with execution.

## 11. Coroutines

Run the [MR10 coroutine generator](../../mr10-kit-compiler/bcpl-demo/coroutines/coroutines.bcpl). It explicitly initializes an MR10 arena and root descriptor, creates a worker, transfers control repeatedly and deletes the inactive worker:


```bcpl
GLOBAL $(
START:1
CURRCO:7
COLIST:8
WRITEF:76
HEAPINIT:89
CREATECO:91
DELETECO:92
CALLCO:93
COWAIT:94
$)

LET GENERATOR(IGNORED) = VALOF
$( FOR N = 1 TO 5 DO
   $( WRITEF("  GENERATOR YIELDS %N*N", N)
      COWAIT(N)
   $)

   COWAIT(-1)
   RESULTIS 0
$)

AND START() BE
$( LET ROOT = VEC 2
   AND ARENA = VEC 400
   AND GEN = 0
   AND VALUE = 0
   AND DONE = FALSE

   WRITEF("DEMO: Coroutine generator with COWAIT and CALLCO*N")
   HEAPINIT(ARENA, 401)

   CURRCO := ROOT
   ROOT!0 := 0
   ROOT!1 := -1
   ROOT!2 := 0
   COLIST := ROOT

   WRITEF("COROUTINE GENERATOR DEMO*N")

   GEN := CREATECO(GENERATOR, 100)
   IF GEN = 0 DO
   $( WRITEF("CREATECO FAILED*N")
      FINISH
   $)

   WRITEF("ROOT CREATED GENERATOR*N")

   UNTIL DONE DO
   $( VALUE := CALLCO(GEN, 0)
      TEST VALUE = -1
      THEN DONE := TRUE
      OR WRITEF("ROOT RECEIVED %N*N", VALUE)
   $)

   WRITEF("GENERATOR FINISHED*N")

   TEST DELETECO(GEN)
   THEN WRITEF("GENERATOR DELETED*N")
   OR WRITEF("DELETECO FAILED*N")

   FINISH
$)
```

Expected sequence: the generator yields 1 through 5, the root receives each value, and the final -1 sentinel ends the root loop before deletion. COWAIT suspends the worker rather than starting a new thread; local FOR state survives each transfer. The regression panel separately checks RP: COROUTINE 77 1.

Keep this example's MR10 setup; do not transplant its globals or descriptor layout into native programs. The [accepted common coroutine contract](../../packaging/milestones/coroutines/co6-common-coroutine-contract-20261116.md) describes a bounded common domain; the native implementation has at most two live workers and fixed checked 1024-word worker stacks. An original manually constructed MR10 fixed-stack example genuinely fails under canonical ICINT19; the supported generator is not that fixture. See [qualified closure](../../packaging/milestones/coroutines/co6-formal-acceptance-and-closure-20261116.md). Exercise: predict the sequence if the upper bound changes to 3, then test only the scratch variant.

## 12. Writing a substantial BCPL application

Build on the [word-count demonstration](../../mr10-kit-compiler/bcpl-demo/word-count/word-count.bcpl). The supplied MRBCDEMO job provides the TEXT DD from the [input fixture](../../mr10-kit-compiler/bcpl-demo/word-count/input.txt). Study how the program uses a Boolean state to recognize the beginning of a word, counts line boundaries, and closes the input stream.


```bcpl
GLOBAL $(
START:1
SELECTINPUT:11
RDCH:13
FINDINPUT:42
ENDREAD:46
WRITEF:76
$)

MANIFEST $( ENDSTREAMCH=-1 $)

LET SPACE(CH) = CH='*S' \/ CH='*T' \/ CH='*N'

AND START() BE
$( LET S = FINDINPUT("TEXT")
   LET CHARS = 0
   AND WORDS = 0
   AND LINES = 0
   AND INWORD = FALSE

   WRITEF("DEMO: Count characters, words, and lines from TEXT*N")
   IF S=0 DO
   $( WRITEF("TEXT DD NOT FOUND*N")
      FINISH
   $)

   SELECTINPUT(S)
   $( LET CH = RDCH()
      IF CH=ENDSTREAMCH BREAK
      CHARS := CHARS+1
      IF CH='*N' DO LINES := LINES+1
      TEST SPACE(CH)
         THEN INWORD := FALSE
         OR UNLESS INWORD DO
            $( WORDS := WORDS+1
               INWORD := TRUE
            $)
   $) REPEAT
   ENDREAD()

   WRITEF("CHARACTERS = %N*N", CHARS)
   WRITEF("WORDS      = %N*N", WORDS)
   WRITEF("LINES      = %N*N", LINES)
   FINISH
$)
```

Run the unchanged program. Confirm the reported counts against the stream delivered by ICINT19; do not equate host file byte count with the interpreted logical character count. In a scratch job, supply a small TEXT input of two lines, containing "ONE TWO" and "THREE". Predict three words and observe how the stream supplies end-of-line and trailing record blanks. Then extend the scratch program to count occurrences of a selected character. Declare counters before commands, check FINDINPUT, and preserve end-of-stream handling.

Keep your source, input, expected output and actual JES evidence together. To finish, rerun the unchanged reference example and compare the result; a modified program is not a regression pass until its own expected result is defined and checked.

## Further reading

The [language example catalog](../../mr10-kit-compiler/language-demo/README.md), [application example catalog](../../mr10-kit-compiler/bcpl-demo/README.md) and [regression panel](../../mr10-kit-compiler/tests/00-regression-panel/README.md) contain additional exercises. The RC4 companion records 11 language demonstrations, 17 application demonstrations and 12 semantic regressions passing in each of the MR10 and COMBINED installations. The tutorial does not claim fresh execution of its proposed modifications.
