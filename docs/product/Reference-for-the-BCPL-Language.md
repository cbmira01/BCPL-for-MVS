# Reference for the BCPL Language

*Cambridge BCPL Programming System for MVS 3.8J*

**Status:** DR.2 working reference; not yet a replacement normative authority. Existing contracts retain authority until individually reconciled and approved.

**Scope:** MR10 Kit Compiler and its interpreted applications are the released baseline (BCPL-0.1.0-rc4). The interpreter-hosted demoted Cambridge Compiler is a separate development compiler producing native System/370 applications; the native-running Cambridge Compiler remains unfinished. Neither CAMBCOMP nor a usable native-running compiler is supplied by RC4. Historical Cambridge source recognition is not proof that a feature works in a reconstructed executable.

Evidence descriptions distinguish **release-tested** (unchanged RC4 examples/regressions), **source-observed** (historical implementation examined), and **unverified** (no sufficient target evidence yet). Release acceptance is recorded in the [RC4 companion](../../packaging/distribution/publication/RC4-README.md). The [tutorial](Tutorial-on-BCPL-Programming.md) teaches these facilities through programs.

## 1. Lexical structure

The MR10 historical SYN lexer recognizes names beginning with an uppercase letter, followed by uppercase letters, digits or periods. Use uppercase identifiers in portable examples; lowercase handling by a source transport or reconstructed input path is a separate question. The historical Cambridge lexer additionally recognizes lowercase letters and underscores within names and has a FORCEUPPERCASE path.

| Category | MR10 forms (source-observed unless tested) |
| --- | --- |
| Integer literals | Decimal digits; # followed by octal digits; #B binary, #O octal, #X hexadecimal |
| Character literal | Single quoted character, e.g. 'A' |
| String literal | Double quotes, e.g. "BCPL"; historical lexer bounds the character count at 255 |
| Escape | Asterisk conventions, e.g. `*N` newline, `*S` space, `*T` tab, `**` asterisk |
| Comments | `//` and `\|\|` to end of line; `/* ... */` |
| Block brackets | $( and $), optionally tagged |
| Expression grouping | Parentheses; historical lexer also recognizes [ and ] as parenthesis tokens |
| Assignment | :=; historical lexer also recognizes underscore |
| Statement separator | Semicolon and applicable line boundaries |

Reserved names in historical MR10 SYN (DECLSYSWORDS): AND, BE, BREAK, BY, CASE, DO, DEFAULT, EQ, EQV, ELSE, ENDCASE, FALSE, FOR, FINISH, GOTO, GE, GR, GLOBAL, GET, IF, INTO, LET, LV, LE, LS, LOGOR, LOGAND, LOOP, LSHIFT, MANIFEST, NE, NOT, NEQV, OR, RESULTIS, RETURN, REM, RSHIFT, RV, REPEAT, REPEATWHILE, REPEATUNTIL, SWITCHON, STATIC, TO, TEST, TRUE, THEN, TABLE, UNTIL, UNLESS, VEC, VALOF, WHILE. THEN is an alias of DO and ELSE of OR in this lexer. This is a source-derived inventory, not a target-tested token-by-token promise.

Use the actual compiler-input character mapping and MVS source card constraints. Do not assume UTF-8 source bytes or modern brace syntax are accepted directly. See historical [MR10 SYN](../../richards-bcpltape/mr10/bcplkit/syn), NEXTSYMB, RDTAG and DECLSYSWORDS, and [Cambridge SYN](../../richards-bcpltape/bcplib/bcpl/syn).

## 2. Syntax and grammar

This is a descriptive grammar synopsis, not a complete formal grammar. Name, expression, command and constant expression denote syntactic categories. Angle brackets below denote placeholders; square brackets in this synopsis denote optional material, not literal source tokens.


```text
declaration  ::= LET definition { AND definition }
               | MANIFEST $( name = constant ... $)
               | GLOBAL   $( name : constant ... $)
               | STATIC   $( name = constant ... $)
definition   ::= name-list = expression-list
               | name = VEC constant
               | name ( [name-list] ) = expression
               | name ( [name-list] ) BE command
block        ::= $( declarations commands $)
assignment   ::= expression-list := expression-list
call         ::= expression ( [expression-list] )
conditional  ::= expression -> expression , expression
```

The braces in this synopsis mean repetition, not BCPL braces. A block's declarations precede its command sequence; local LET after a command is not accepted by the MR10 suite. AND connects definitions, not Boolean operands. In MR10 SYN, RDBLOCKBODY, RDEF, REXP and RCOM are the primary evidence. Newlines can affect expression continuation; use grouping and established source layout. Full production grammar, tagged bracket matching, continuation rules and malformed-input diagnostics remain to be reconciled.

## 3. Data representation

BCPL has a word-oriented, not a statically typed, data model. A word in this system is 32 bits; the meaning is determined by its use. Integer arithmetic is finite-word arithmetic, not arbitrary precision. A word may be a number, a pointer, a bit mask, a function value or a logical value.

Word pointers index BCPL words, not bytes. On the native System/370 path the Core Runtime and generated code interpret word pointers through their byte-address conversion; INTCODE uses its own execution representation. Never transfer internal pointer values between execution environments.

Packed strings contain a length byte followed by characters; the offset for the first character is 1. GETBYTE and PUTBYTE access byte offsets in BCPL storage. The released bytes regression checks preservation of four numeric byte values. Character codes and stream transformations depend on the applicable MVS/interpreter interface; ASCII is not presumed.

TRUE and FALSE are BCPL logical constants; the conventional representation is all one bits (-1) and zero respectively. MR10 TRN translates these constants and branches on them. The Boolean demonstration exercises their use, but numeric bit-pattern truth and noncanonical condition behavior require explicit oracle verification before normative transfer. Do not treat all nonzero integers as interchangeable Boolean values.

The expression ? is recognized by MR10 SYN/TRN. Its use as an unspecified value is not a guarantee of zero-initialized storage. Division by zero, overflow, out-of-range shifts and arbitrary invalid addresses are not covered by the positive arithmetic regression.

## 4. Declarations and scope

| Form | Meaning |
| --- | --- |
| LET A = E | Introduce and initialize a local name |
| LET A,B = E,F | Introduce names with corresponding initial values |
| AND | Join definitions in a declaration group |
| MANIFEST $( A = C $) | Compile-time constant binding |
| GLOBAL $( F:76 $) | Associate a name with a numbered global-vector slot |
| STATIC $( A = C $) | Static storage declaration, source-observed in historical MR10 SYN/TRN |

Local names are scoped to their block; an inner binding can hide an outer name. The declarations example exercises nesting. Initializers in a declaration group must not be assumed to execute as sequential assignments; use a separate LET for dependent initialization when necessary. Function and routine names can appear in the same AND group (see the recursion regression). MANIFEST values and global slot numbers use the compiler's constant-expression evaluator, which is more restricted in historical MR10 TRN than ordinary expressions.

Historical MR10 TRN emits a data label and constant initializer for STATIC; native development case 40 also verifies a static scalar changed by a routine. Detailed MR10 target evidence for static lifetime and initializer constraints, scope restrictions on non-global nested routines, and duplicate-name diagnostics remains to be reconciled. Do not assume automatic zero initialization of uninitialized words.

## 5. Expressions and operator precedence

The following precedence is derived from historical MR10 SYN REXP and RBEXP, from strongest to weakest. Binding powers describe the actual parser, not a modern language's precedence table.

| Form | Binding / association |
| --- | --- |
| Calls F(A), grouping | Calls attached by REXP; parentheses group |
| V!I | 40, left associative |
| Prefix @, ! (LV, RV) | Operand parsed at 35 |
| `*`, `/`, REM | 35, left associative |
| Unary +, - | Operand parsed at 34 (includes multiplication) |
| Binary +, - | 34, left associative |
| `=`, `\=`, `<`, `>`, `<=`, `>=` (EQ, NE, LS, GR, LE, GE) | 30; chains form conjunctions of adjacent comparisons |
| `<<`, `>>` (LSHIFT, RSHIFT) | Left binding 25, right operand parsed at 30 |
| Prefix `\` or NOT | Operand parsed at 24 |
| `/\`, `&`, LOGAND | 23, left associative |
| `\/`, `\|`, LOGOR | 22, left associative |
| EQV, NEQV | 21, left associative |
| C -> E,F | 13, branches parsed as expressions |

A logical operator in value context can operate on word bit patterns; TRN has a separate JUMPCOND path for control expressions. Do not assume value-context short circuit or single evaluation of a middle operand in chained comparisons: the source constructs multiple adjacent comparisons. Use explicit commands or a conditional expression for intentional conditional evaluation.

Positive integer arithmetic is release-tested: 17+5=22, 17-5=12, 17*5=85, 17/5=3, 17 REM 5=2. Negative division/remainder, overflow and exact shift semantics need further evidence. Conditional expressions and VALOF/RESULTIS are exercised by the recursion, GCD and language demonstrations. TABLE provides a word table from its elements; see the TABLE/vector demonstration. Parenthesize unfamiliar combinations.

## 6. Commands and control structures

| Form | Meaning |
| --- | --- |
| A := E | Assign through a writable destination |
| A,B := E,F | Multiple assignment (historical parser/translator; evaluation details pending) |
| IF C DO S | Execute S when C holds |
| UNLESS C DO S | Execute S when C does not hold |
| TEST C THEN S OR T | Select one of two commands |
| WHILE C DO S | Pre-test repetition while C holds |
| UNTIL C DO S | Pre-test repetition until C holds |
| S REPEAT | Unconditional repetition |
| S REPEATWHILE C / S REPEATUNTIL C | Post-test repetition |
| FOR I = A TO B [BY D] DO S | Counted repetition; default step 1, inclusive end in the demonstrated increasing case |
| BREAK / LOOP | Leave / continue enclosing repetition |
| SWITCHON E INTO $( CASE K: ... DEFAULT: ... $) | Select a constant case or default |
| ENDCASE | Leave SWITCHON |
| label: S / GOTO E | Label and transfer (source-observed; target restrictions pending) |
| RETURN / FINISH | Return from a routine / terminate program |
| RESULTIS E | Produce the result of the enclosing VALOF expression |

DO is optional where historical RCOM ignores its token; use explicit DO for readability. SWITCHON cases are not implicitly separated by a break; use ENDCASE to avoid unintended continuation, or RESULTIS when returning a VALOF result. The switch demonstration includes grouped case labels. The historical translator diagnoses out-of-context BREAK, LOOP, RESULTIS and CASE constructs. Exact FOR bound/step evaluation, negative steps, nonlocal transfer and error behavior are not completely target-reconciled.

The release-tested control regression expects RP: CONTROL 10 1 10 30. The repeat-forms and TEST/THEN/OR demonstrations cover further positive forms.

## 7. Functions and routines

A function definition LET F(A,B) = E computes an expression value. A routine definition LET R(A) BE S executes a command. VALOF S computes an expression using RESULTIS to supply its value. RETURN exits a routine; do not substitute it for RESULTIS in a value-producing block.

Arguments and return values are BCPL words. Passing a pointer copies the address and permits access to the referenced object. Procedure values can be passed and called indirectly, as shown by APPLY in the function-values demonstration. The recursion regression checks a three-argument call and factorial (RP: CALLS 9 120). Recursion consumes implementation-specific workspace; no unlimited depth is promised. Exact argument evaluation order, mismatched arity, callable-address validity and closure-like capture are not guaranteed by these tests. The machine calling convention is a runtime/compiler contract rather than a language syntax rule.

## 8. Storage and addressing

VEC N reserves N+1 words, indexed 0 through N, in its enclosing local storage. Historical MR10 TRN (TRANSDYNDEFS) evaluates N using EVALCONST at translation time: do not use a run-time size in a VEC declaration. V!I denotes the word at address V+I; prefix ! dereferences a word address; @ obtains the address of a suitable location. Assigning a pointer does not copy the storage. TABLE yields a pointer to a word table. Historical MR10 TRN emits each table element using EVALCONST; use constant expressions. Treat literal/static table storage separately from local vectors; do not assume literal mutability or particular placement.

Keep local-vector pointers within their live scope. Do not use pointers after return or deallocation. Bounds are the programmer's responsibility; neither historical syntax nor a passing valid-domain test guarantees general address protection. Byte offsets are not word indices.

GETVEC and FREEVEC are library operations, not declaration syntax. The MR10 reconstruction uses caller-initialized arena allocation (HEAPINIT); GETVEC(N) provides N+1 payload words or zero on failure. The release test checks one reuse sequence. Native allocation has separate contracts and must not be described by MR10's private allocator layout. See [MR10 allocator](../../mr10-kit-compiler/library/getvec-freevec.bcpl) and [existing memory briefing](../BCPL-memory-management.md).

## 9. Program structure and separate compilation

A BCPL compilation unit defines procedures and declarations. GET imports source declarations using the compiler's source-input mechanism; historical MR10 and Cambridge SYN have PERFORMGET implementations. Actual search order, header naming and MVS dataset conventions belong to compiler interfaces, and are not inferred from modern include behavior. Historical MR10 source uses a period between sections; historical Cambridge uses SECTION and NEEDS tokens. Exact section and dependency semantics are compiler-specific.

The system enters an application through START at global slot 1. Independently compiled MR10 units use matching GLOBAL numbers and their INTCODE decks are provided together with the applicable library. The module regression binds HELPER:180 in both units and expects RP: MODULE 43. This local example does not establish a public slot assignment. See [MR10 global map](../../mr10-kit-compiler/library/GLOBALS.md) and [Global Number Registry](../../packaging/architecture/global-number-registry.md).

Native application generation, assembly, IEWL link-edit, and global installation form a different workflow. A header is not executable code and an object library is not the Base Library as a logical facility. See [runtime and library nomenclature](../../packaging/architecture/runtime-and-library-nomenclature.md). Compiler options and runtime ABI are outside the language reference.

## 10. Language dialects and implementation differences

| Facility | MR10 Kit Compiler / ICINT19 | Historical Cambridge SYN/TRN and reconstruction |
| --- | --- | --- |
| Basic integer expressions, LET, control, recursion, vector and byte operations | Release-tested examples and regressions | Historical common constructs; native application evidence is separate |
| Identifier spelling | Historical uppercase/digits/periods | Historical lexer additionally permits lowercase and internal underscore, with case option |
| Byte access | GETBYTE/PUTBYTE library interface tested | Historical SYN recognizes % (BYTEAP); TRN translates to GETBYTE/byte assignment machinery; reconstructed feature coverage not established here |
| Floating operators, FLOAT/FIX/ABS, selectors (SLCT) | Not in historical MR10 parser in these forms | Historical Cambridge syntax/translation present; do not claim working native floating point or selectors merely from that source |
| SECTION / NEEDS | Not reserved by historical MR10 lexer | Historical Cambridge source recognizes them; exact behavior not reconciled here |
| Coroutine lifecycle | MR10-specific globals and setup; supported tests | Bounded native common-domain contract accepted in development, not RC4 native functional certification |
| Modern BCPL additions | Not presumed supported | Not presumed supported |

The [historical Cambridge SYN](../../richards-bcpltape/bcplib/bcpl/syn) and [TRN](../../richards-bcpltape/bcplib/bcpl/trn) contain additional syntax compared with [MR10 SYN](../../richards-bcpltape/mr10/bcplkit/syn) and [MR10 TRN](../../richards-bcpltape/mr10/bcplkit/trn). This is a preliminary source-based contrast, not an exhaustive supported-feature matrix. The [MR10 compiler INTCODE inventory](../../mr10-kit-compiler/source/README.md) identifies the actual historical SYNI/TRNI/CGI decks used on MVS. The [demoted Cambridge build documentation](../../bootstrap-toolchain/bootstrap-cambridge/README.md) identifies its current input containers `source/syn` and `source/trn`, the `make-demoted.py` generator, and the generated compiler units. The tracked `demoted/` directory is an earlier snapshot, not the current clean-room build input. The source containers include the same additional BYTEAP, floating-operator and selector parsing/translation branches described above; those branches alone do not establish supported output behavior. Exact generated front-end and backend coverage must be traced separately.

### Accepted native application examples (development only)

The [CO.6 closure](../../packaging/milestones/coroutines/co6-formal-acceptance-and-closure-20261116.md) records 145 PASS and one expected SKIP (083) for the native bootstrap suite. The following six cases and their source, README and expected-output blobs match the tested revision 216b6707c404a91c796ed8f1419a99ef172b184a. Each expects the diagnostic output value 42. These are native applications generated by the interpreter-hosted demoted Cambridge Compiler, not evidence of a native-running compiler or RC4 native certification.

| Case | Verified positive example |
| --- | --- |
| [08](../../tests/bootstrap/08-local-vector-store-load/source.bcpl) | Store and reload a word through a local vector |
| [18](../../tests/bootstrap/18-recursion/source.bcpl) | Recursive function and conditional expression |
| [22](../../tests/bootstrap/22-signed-arithmetic/source.bcpl) | Unary negation and signed subtraction |
| [34](../../tests/bootstrap/34-valof-resultis/source.bcpl) | VALOF/RESULTIS in a local initializer |
| [38](../../tests/bootstrap/38-putbyte-getbyte-roundtrip/source.bcpl) | Byte store and reload through library calls |
| [40](../../tests/bootstrap/40-static-scalar-persistence/source.bcpl) | STATIC scalar changed by a separate routine |

These cases are deliberately small and do not establish all semantics of the corresponding constructs. The suite manifest and independent expected outputs remain authoritative.

The accepted [common coroutine behavioral contract](../../packaging/milestones/coroutines/co6-common-coroutine-contract-20261116.md) covers valid cooperative transfers, preserved locals, and bounded deletion/reuse with one root and up to two workers in the common domain. Native stacks are checked 1024-word stacks; MR10 and native global numbers and internal descriptors differ. The original manually constructed fixed-stack MR10 fixture remains a genuine failure under canonical ICINT19, as documented in [CO.6 qualified closure](../../packaging/milestones/coroutines/co6-formal-acceptance-and-closure-20261116.md). Coroutines are library/runtime services, not additional syntax. No transfer of that contract's authority is effected here.

### Evidence and verification boundaries

The [MR10 language demonstrations](../../mr10-kit-compiler/language-demo/README.md), [application demonstrations](../../mr10-kit-compiler/bcpl-demo/README.md) and [12-case semantic panel](../../mr10-kit-compiler/tests/00-regression-panel/README.md) support positive examples. RC4 accepts these suites in two installed profiles; MVS RC, interpreted CODE and exact semantic results are separate checks. Source analysis alone does not establish edge cases or error semantics. The [DR.2 migration ledger](../../packaging/milestones/documentation-refactoring/dr2-language-manual-migration-20261125.md) records remaining reconciliation and preservation requirements.
