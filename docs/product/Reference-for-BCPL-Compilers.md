# Reference for BCPL Compilers

*Cambridge BCPL Programming System for MVS 3.8J*

**Status:** DR.5 reconciliation in progress. Existing compiler documentation and accepted contracts retain their authority pending reconciliation and explicit owner approval. This manual distinguishes source-observed behavior, accepted target evidence, and unsupported or unverified operation. It does not certify every historical switch.

See the [compiler explanation](Explanation-of-BCPL-Compilers.md) for architecture and the [language reference](Reference-for-the-BCPL-Language.md) for syntax.

## 1. Applicable environments and release/development boundaries

| Environment | Invocation / implementation | Scope |
| --- | --- | --- |
| MR10 Kit Compiler | ICINT19 running SYNI/TRNI and CGI | Released compiler; interpreted applications |
| Interpreter-hosted demoted Cambridge Compiler | ICINT19 running BOOT_INTCODE(CAMBCOMP) | Development compiler; native applications through textual CODE, IFOX, IEWL |
| Native-running Cambridge Compiler | Historical PGM=BCPL interface, intended native load module | Unfinished reconstruction; historical interface only |

RC4 (BCPL-0.1.0-rc4, volume BC0004) includes the MR10 Kit Compiler, ICINT19, sources, JCL, library and tests in the MR10 and COMBINED profiles. It does not include CAMBCOMP or a usable native-running compiler. Native components are supplied as work in progress. The [RC4 companion guide](../../packaging/distribution/publication/RC4-README.md) and frozen release manifest govern that distribution.

Dataset names such as MR10_LOAD, BOOT_INTCODE and BOOT_SOURCE in this manual are development manifest keys, not literal JCL DDs or DSNs. Consult [dataset configuration](../../config/dspal.yaml) for development mappings. Release datasets instead use the installed site namespace and the release manifest.

## 2. MR10 Kit Compiler

### 2.1 Inputs and outputs

The installed phases are described in the [MR10 INTCODE inventory](../../mr10-kit-compiler/source/README.md).

| Stage | INTIN decks | Input | Output |
| --- | --- | --- | --- |
| Compile | SYNI, TRNI, BLIBI, ICLIB | SYSIN BCPL source; OPTIONS if supplied; GET inputs when required | OCODE; SYSPRINT diagnostics |
| Generate | CGI, BLIBI, ICLIB | SYSIN containing OCODE | INTCODE; SYSPRINT diagnostics |
| Execute | Generated application deck(s) and required support decks | Application-specific DDs | Application output; SYSPRINT and interpreted CODE |

The [MRLANGDM JCL](../../mr10-kit-compiler/jcl/run-language-demos.jcl) stages the phase PDS members as sequential FB80 datasets before concatenating them on INTIN; this avoids the observed end-of-member issue. C/G/R steps distinguish compile, generate and run. OCODE and INTCODE outputs in these jobs are FB80 records, not binary IBM object decks. Historical SYN and CG fall back to SYSPRINT if their named output stream is absent; that is unsuitable for a normal downstream compilation pipeline.

### 2.2 Option transport and defaults

Historical SYN START reads FINDINPUT("OPTIONS"), first record up to newline or end-of-stream; absent OPTIONS selects defaults. It echoes the record with OPTIONS as prefix. No slash separator or separate CG370 option phase exists. CGI START reads SYSIN and INTCODE, not OPTIONS. MVS EXEC PARM is not this parser's option source.

| Setting | Source default |
| --- | --- |
| TREESIZE | 5500 BCPL words |
| SAVESPACESIZE | 2 words |
| OPTION!0 through OPTION!20 | FALSE |
| PPTRACE / PRSOURCE | FALSE |
| CHARCODE | Identity conversion |
| REPORTMAX | 20 (fixed, not a switch) |

The [MR10 options inventory](../../mr10-kit-compiler/docs/compiler-options.md) and historical [SYN](../../richards-bcpltape/mr10/bcplkit/syn), [TRN](../../richards-bcpltape/mr10/bcplkit/trn) and [CG](../../richards-bcpltape/mr10/bcplkit/cg) are the evidence for the following table.

| Option | Source-observed action |
| --- | --- |
| P | OPTION!1: token/symbol debugging walk; stops on S.END, not an ordinary compilation |
| T | OPTION!2: print AE tree using PLIST(A,0,20) |
| C | OPTION!3: suppress COMPILEAE and ordinary OCODE output |
| M | OPTION!4: MAPSTORE after compiler workspace processing |
| N | OPTION!5: suppress GET inclusions after consuming requested filename |
| A | Set CHARCODE to EBCDICTOASCII for single-character literal conversion; not a general stream or target switch |
| S | PRSOURCE: echo top-level source, excluding nested GET input |
| E | PPTRACE: print lexer character at NEXTSYMB entry |
| L followed by decimal number | Set TREESIZE via READN; terminator is reprocessed |
| 3 | Set SAVESPACESIZE to 3, affecting translator workspace/save-space offsets |

The scanner maintains a mutable flag index initially zero. P/T/C/M/N set it; every processed character reaching the common assignment sets OPTION!N true. A/S/E/L/3 have additional side effects. Unknown characters are not reliably rejected. Acceptance by the scanner is not a supported-option guarantee. The historical source and the preserved executable SYNI image have not been exhaustively compared behaviorally. All five tracked MR10 INTCODE inputs (SYNI, TRNI, CGI, BLIBI, ICLIB) match the RC4 frozen program-source revision e910de51c19c09698be139e33084a90401511cc9 by blob SHA. That establishes tracked input identity, not source-to-deck regeneration equivalence or independent verification of every option.

### 2.3 Supplying options

The tracked [large-tree record](../../bootstrap-toolchain/bootstrap-cambridge/options-large-tree.txt) contains L12000 and is used when MR10 builds the Cambridge sources. A development host driver can bind this file via its --dd OPTIONS=PATH argument; the argument belongs to the driver, not the BCPL compiler. The corresponding MVS JCL can provide an OPTIONS DD alongside SYSIN. The [CAMBBLD job](../../bootstrap-toolchain/jcl/cambbld.jcl) provides actual examples. Do not replace the RC4 defaults or change workspace/save-space conventions indiscriminately.

### 2.4 GET inputs

Historical SYN PERFORMGET reads a quoted name and invokes FINDINPUT; N bypasses the open. ICINT19 FINDIN checks its fixed stream table before dynamic DD discovery; MAKENAME accepts a counted name of 1–8 bytes and blank-pads it. The dynamic path uses the allocated DD rather than a filesystem search. The current [MR10 driver](../../tools/mr10/compile-and-run-core.py) uppercases and validates --dd names, rejects reserved or duplicate names, reads ASCII records and supplies those named inputs to compilation and final execution. Provide the required DD explicitly and use uppercase names in source. Historical MR10 error 96 prints NO INPUT with the requested name, and error 97 reports STRING OR NUMBER EXPECTED. CAEREPORT increments REPORTCOUNT, stops immediately only when it exceeds REPORTMAX, otherwise attempts token synchronization and LONGJUMP recovery. START checks the accumulated errors before normal translation and completion. This is not a promise of safe recovery from a missing DD (the source has already changed SOURCESTREAM). The VEC 10 frame storage permits three complete three-word saved frames by layout, but the historical MR10 PERFORMGET has no extent check. No arbitrary nesting, duplicate-open or malformed-input safety is certified. See the [language reference](Reference-for-the-BCPL-Language.md#9-program-structure-and-separate-compilation) for the parser's source-derived behavior.

## 3. Interpreter-hosted demoted Cambridge Compiler

### 3.1 Inputs and transport

The [bootstrap compiler build guide](../../bootstrap-toolchain/bootstrap-cambridge/README.md) and [compiler driver](../../tools/bootstrap/compile-mvs) define the current workflow. CAMBCOMP is a packed compiler INTCODE image in BOOT_INTCODE. The current driver runs PGM=ICINT19, normally REGION=256K and TIME=(,30), with the following DD roles:

| DD | Role |
| --- | --- |
| STEPLIB | Installed ICINT19 load library |
| INTIN | CAMBCOMP image |
| SYSIN | Application BCPL source |
| CAMBPARM | Bootstrap option record, normally BOOT_SOURCE(CAMBPARM) |
| LIBHDR, SYNHDR, TRNHDR, CGHDR | Named header inputs supplied by driver |
| OPTIONS | Also allocated by the driver; not the resident Cambridge option parser's input |
| CODE | Textual assembler output, temporary FB80 |
| SYSGO | DUMMY in the current textual path |
| SYSPRINT | Compiler/interpreter diagnostics, FB132 in current driver |
| SYSUDUMP | DUMMY in current driver |

The exact [bootstrap host source](../../bootstrap-toolchain/bootstrap-cambridge/bootstrap-host.bcpl) supplies:


```bcpl
LET FINDPARM() = FINDINPUT("CAMBPARM")
```

This is a bootstrap accommodation, not a redefinition of the historical native FINDPARM contract. The driver accepts --cambridge-parm PATH for an alternate record and --show-jcl for a preview. **Preview is not side-effect-free on the host:** the current driver creates the output parent directory and unlinks an existing selected assembler output before the preview branch. Use a distinct scratch output path. Executing the driver normally submits MVS jobs. The driver's built-in GET bindings are the four header DDs listed above; it does not expose the MR10 driver's general --dd option. Other inputs require an explicitly arranged MVS allocation or separately authorized tooling work; do not infer a host include-file search. Cambridge PERFORMGET saves three words per frame in VEC 10 and rejects a fourth simultaneous inclusion before saving it (CAEREPORT(-87), GETs too deeply nested); missing input is fatal CAEREPORT(-88), Input ... not provided for GET. A negative diagnostic number sets REPORTMAX to zero, and CAEREPORT stops when REPORTCOUNT >= REPORTMAX. Within included files LINECOUNT starts at 10001; CAERRWRITE displays line number modulo 10000 and identifies a GET file. These details are source-observed, not independent target verification of nesting or failure recovery.

### 3.2 Option grammar and default record

The [historical Cambridge master](../../richards-bcpltape/bcplib/bcpl/bcpl) reads two consecutive phases from FINDPARM. The first slash separates compiler/front-end switches from generator switches. Newline or end-of-stream also terminates the respective loops. Extra slashes in the second phase are ignored. Options are uppercased by the master. Unknown first-phase options are reported and ignored (READN followed by UNRDCH consumes a numeric suffix and makes the terminating character available again); unknown second-phase options stop compilation with STOP(8).


```text
front-end-options / code-generator-options
/N/
```

The [current CAMBPARM file](../../bootstrap-toolchain/bootstrap-cambridge/cambridge-options.txt) is exactly one 80-character record: slash, N, then 78 slash characters. Slash fill prevents FB80 blank padding from becoming invalid options. The leading slash selects no front-end option; generator N suppresses direct binary SYSGO output. Do not remove N with the present driver.

The earlier A/N/ experiment selected the historical EBCDIC-to-ASCII conversion, the wrong direction for an ASCII interpreter host targeting System/370 EBCDIC. The generated bootstrap master installs private CODE370 target conversion by default. The option A retains its historical meaning; it is not a generic cross-compilation flag. Prior CODE370 mapped host newline 10 to X'25' (37), verified by JOB 9495. The owner-approved DR.5 correction preserves logical 10; ordinary target character conversion is unchanged. Rebuilt CAMBCOMP and BLIB passed JOBS 9502/9504, including both literal representations and exact FB132 records. Historical CODEA, option A, MR10 and external encoding policies remain unchanged. See the [runtime reference](Reference-for-the-Cambridge-Runtime-and-Libraries.md). The subsequent eight-suite supported regression campaign passed 208 cases, with one expected SKIP (083), zero failures and zero blocked cases in the rebuilt development installation.

### 3.3 First-phase switches

These are source-recognized historical switches, not a promise of independent bootstrap verification. Source: [compiler option and parameter transport note](../../bootstrap-toolchain/bootstrap-cambridge/compiler-options-and-parm.md) and historical master COMPILE.

| Option | Action |
| --- | --- |
| A | ASCII := TRUE; install historical CODEA EBCDIC-to-ASCII conversion |
| B | BACKVEC := TRUE |
| C | FORCEUPPERCASE := FALSE |
| F | ABORT := STANDARDABORT |
| H | HARD := TRUE; stop on reported errors at phase boundaries |
| N | NUMOCODE := TRUE; fall through to O and enable OCODE output |
| O | OCODE := TRUE |
| Pnnn | FREESTACKSIZE := decimal value |
| Q | QUIET := TRUE |
| Rnnn | ERRORMAX := decimal value |
| S | PRSOURCE := TRUE |
| W | WRCH redirected through WRITEUPPERCASE for SYSOPT output |
| X | TIMING := TRUE |
| Z | NOCG := TRUE; skip generator |
| 1 through 9 | Set SAVESPACESIZE to that digit |

Defaults include SAVESPACESIZE=3; BACKVEC, NOGET, LEXTEST, PPTRACE, TREE, OCODE, NUMOCODE, PRSOURCE and QUIET false; FORCEUPPERCASE true; static ERRORMAX=30. FREESTACKSIZE defaults to 3000 if zero. A, B, N/O, Z and the digit cases fall into the source's cross-compilation warning path (N reports its original option character).

Commented-out cases E (PPTRACE), M (MAPPING), T (TREE), V (LEXTEST) and Y (NOTRN) are inactive in the surviving parser. Do not import MR10 switch meanings into this phase.

### 3.4 Second-phase switches

| Option | Action |
| --- | --- |
| C | STKCKING := TRUE |
| G followed by remainder | LOADGO := TRUE; copies the remaining characters verbatim through newline/end-of-stream into PARMS, sets its length byte and terminates option parsing; must be last |
| Hnnn | NAMING := TRUE; size NAMES from decimal value, default 600 if zero |
| K | CALLCOUNTING := TRUE |
| L | LISTING := TRUE |
| M | MEMBERNAMEING := TRUE |
| N | DECK := FALSE; suppress direct object deck |
| P | CALLCOUNTING and COUNTING := TRUE |
| / | Ignore additional slash |

Defaults: DECK and BINING true; LISTDECK, LISTING, CGTRACE, STKCKING, CALLCOUNTING, COUNTING, MEMBERNAMEING and NAMING false; NAMES=0. An allocated CODE stream makes LISTING true; without CODE, listing output is directed to SYSOPT when enabled. D (LISTDECK) and T (CGTRACE) remain commented-out cases.

The decimal readers for P/R in phase one and H in phase two call UNRDCH after READN so the following option character can be processed. G historically loads and enters the generated code; it is not an accepted current bootstrap execution option. Other source-observed switches can require unreconstructed services. In particular, the historical combined C/K or C/P entry path is not safe merely because the compiler emits its instructions (see chapter 6).

**N is phase-sensitive:** first-phase N requests numeric OCODE and enables OCODE; second-phase N disables binary object-deck output. MR10 N instead disables GET.

## 4. Native-running Cambridge Compiler

### 4.1 Recovered historical parameter interface

The surviving [BCPLCLG procedure](../../richards-bcpltape/sys1/userproc/bcplclg) contains the following exact EXEC fragment:


```jcl
//BCPL    EXEC PGM=BCPL,REGION=&REGC,
//             PARM='$0T&IOSPACE.$&LISTC.&PARMC',
//             TIME=(&MINC,&SECC),COND=(&CONDC)
```

Defaults include IOSPACE=60K, LISTC empty and PARMC='/CK', producing conceptually $0T60K.$/CK. The prefix belongs to native runtime parameter processing. The compiler consumes a pseudo-input stream through SELECTINPUT(FINDPARM()); [BCPLMAC](../../richards-bcpltape/km10/bcplmac) describes PARMAREA and PARMFLD. CAMBPARM is not the historical native transport.

The historical procedure supplies STEPLIB, SYSPRINT, LIBHDR and SYSGO (FB80, BLKSIZE=2480), then passes SYSGO's dataset to IEWL via SYSLIN, with SYSLIB and SYSLMOD, and executes GO with separate run parameters. Source SYSIN is provided by the invoking job. Historical MAKEOBJ uses /C for compiler components BCPL, SYN, TRN, CG and COMPBLIB, and empty PARMC for BLIB, IOS, PM. These are historical site-specific interfaces, not a currently supported RC4 compile procedure.

### 4.2 Implementation status

The intended native option grammar is the historical two-phase grammar in chapter 3. Restoration of the native parameter pseudo-stream, compiler runtime services, direct object deck generation and native compiler execution must be established separately. Historical /CK is not the current demoted compiler default. The copied [MAKEOBJ](../../cambridge-compiler/jcl/makeobj.jcl) and [MAKELIB](../../cambridge-compiler/jcl/makelib.jcl) are not runnable reconstruction instructions and contain destructive historical steps. No supported native compiler installation, self-compilation, or comprehensive switch certification is claimed.

## 5. Output and intermediate artifacts

| Artifact | Producer | Consumer / meaning |
| --- | --- | --- |
| AE tree | SYN | TRN; compiler workspace structure |
| OCODE | TRN | CGI (MR10 textual stream) or CG370 (Cambridge internal representation, optional listing) |
| INTCODE | CGI | ICINT19 interpreter; not native IBM object code |
| CODE | CG370 | System/370 assembler text for IFOX00 in current bootstrap |
| SYSGO | Historical CG370 or IFOX | Binary relocatable object records; producer determines meaning |
| Load module | IEWL | MVS executable; not a source or object deck |

The historical master finds OCODE and CODE output streams, defaults to SYSOPT when absent, and enables the corresponding listing if a stream is supplied. With DECK true it requires SYSGO; CG370's DECKOUT calls WRITEREC(V,80) for binary records. With N after the slash the deck path is disabled. The present compiler driver writes CODE FB80 to a temporary dataset, copies it via IEBGENER into marked SYSOUT between @@BCPL-CODE-BEGIN@@ and @@BCPL-CODE-END@@, then recovers nonempty assembler. This is textual transport, not a byte-preserving object-deck capture.

Separate IFOX/IEWL steps are needed to construct native load modules from CODE. The historical CG370 direct object output and the assembler's object output are both relocatable object decks; an IEWL load module is a different artifact. The historical [CG source](../../richards-bcpltape/bcplib/bcpl/cg) and [architecture notes](../../packaging/architecture/cg370-architecture-notes.md) describe section/label handling and object records.

## 6. Diagnostics and constraints

### 6.1 Compiler and interpreter limits

| Limit / diagnostic | Scope and qualification |
| --- | --- |
| MR10 tree 5500 words default | Historical source; L option changes allocation; L12000 is tracked bootstrap setting |
| MR10 REPORTMAX=20 | Historical SYN; phase reports errors and STOP(8) paths |
| ICINT19 PROGCNT=40001; GLOBCNT=700 | Current assembler source capacity; loaded code consumes part of program/workspace; not 40001 free stack words |
| Cambridge default free stack 3000 words | Historical master; workspace = STACKEND - STACKBASE - FREESTACKSIZE; requires at least 5000 workspace words or STOP(8) |
| Cambridge ERRORMAX=30 default | Historical master; R option changes maximum |
| CG370 generated section about 16 KB | Source-derived section size restriction (four 4095-byte windows in limit calculation); not total program limit |
| Floating literals | Explicitly unsupported in demoted compiler: generated READFLOAT fatal stub |
| Binary SYSGO output | Not supported by current textual bootstrap transport; retain second-phase N |
| Native runtime service requirements | Depend on code generator switches, selected Core Runtime and libraries |

The [ICINT19 assembler](../../mr10-kit-compiler/asm/icintv19.asm) defines the program/global capacities and supplies G!54/G!55 stack boundaries for the Cambridge host. Its ICGETBY/ICPUTBY use two logical bytes per fullword-backed interpreted slot, unlike four-byte native word packing. The [demotion generator](../../bootstrap-toolchain/bootstrap-cambridge/make-demoted.py) adjusts OCODE host packing and target packing separately. Its main routine reads the maintained SYN/TRN source containers and historical master/CG, splits SYN/LEX, TRNA/TRNB and CGA–CGE, checks expected header/spelling occurrence counts, derives the master and emits separate ordinary and diagnostic units. At the DR.5 pre-correction checkpoint all five selected input blobs matched CO.6 tested revision 216b6707c404a91c796ed8f1419a99ef172b184a. At 0de748ebef72965497dd1ac40330a99a33f56cae, four still match (SYN, TRN, bootstrap host, default parameters); make-demoted.py differs by the verified DR.5 logical-newline correction. CAMBBLD 9498 and the later supported regression campaign establish current execution at their reported scope. Blob identity does not establish installed binary identity or every nondefault configuration.

### 6.2 Checked and counted native procedure entry

The historical CG370 second-phase flags select distinct system-vector calls (source-observed [CO.1 option matrix](../../packaging/milestones/coroutines/co1-cg370-checked-entry-option-matrix-20261112.md)).

| Generator switches (N retained for bootstrap) | Entry path | Inline data | Evidence boundary |
| --- | --- | --- | --- |
| /N | Ordinary frame setup | None | Accepted development applications |
| /KN | +20 counting call | One counter fullword | Source-observed; no functional counting claim |
| /CN | +60 checked call | One full frame-size word | Reported production baseline cases 49–52 pass |
| /CKN | +80 combined call | Counter and full frame-size words | Compiler-only probe, not safe native GO |
| /CPN | +80 plus additional +20 sites | Respective metadata | Compiler-only probe, not functional counting |

The [CK-C result](../../packaging/milestones/coroutines/co1-ck-c-jes-5342-compile-only-result-20261112.md) records two +80 entries for its source, and the [CK-D result](../../packaging/milestones/coroutines/co1-ck-d-counting-jes-5343-compile-only-result-20261112.md) two +80 and five +20 sites. They are operator-reported compile-only results; no IFOX, IEWL or GO was run in these probes. The current [BCPLMAIN assembler](../../bootstrap-toolchain/asm/bcplmain.asm) still has STKCIMP advancing by just four bytes and returning. That cannot consume both metadata words, establish the frame or enforce its limit. Do not run combined checked/counting output against this handler. Counting behavior is not established by emission alone. The [CK-B record](../../packaging/milestones/coroutines/co1-ck-b-native-checked-stack-production-baseline-20261112.md) distinguishes the checked-only baseline from combined mode.

### 6.3 Interpreting results

JES RC0000 by itself is insufficient. For MR10, verify all required compile/generate/run steps, interpreted CODE=0 and independent expected output; examine SYNTAX ERROR, INTCODE ERROR, MAPSTORE and missing/invalid generated artifacts. For the resident Cambridge compiler, require successful compiler execution and recovered assembler, then separately inspect IFOX, IEWL and GO results and applicable regression oracles. Negative tests can have an explicitly different expected outcome; do not replace their oracles with a universal zero-RC rule.

Historical compiler diagnostics include COMPILATION FAILED, INSUFFICIENT REGION SIZE, NO SYSIN, NO SYSGO, and code-generator unknown-option errors. Cambridge HARD checks accumulated phase errors after SYN and TRN; without HARD the source may continue through translation or generation but reports COMPILATION FAILED and STOP(8) at the final ERRORS check. Fatal negative CAEREPORT codes stop earlier regardless of HARD. MR10 SYN uses REPORTCOUNT > REPORTMAX for its immediate abort, unlike Cambridge's >= test, and checks nonzero report count before normal translation. These are source control-flow observations, not guarantees of a particular JES RC, artifact absence, or safe continuation after every malformed program. Compiler success messages are not substitutes for JES/ICINT/assembly/link/execute evidence. The [RC4 guide](../../packaging/distribution/publication/RC4-README.md) records the released positive suites; the [CO.6 closure](../../packaging/milestones/coroutines/co6-formal-acceptance-and-closure-20261116.md) records qualified development results, including one expected native skip and the separate historical coroutine failure.

## 7. Comparison tables

| Property | MR10 Kit Compiler | Demoted Cambridge Compiler | Native-running Cambridge Compiler |
| --- | --- | --- | --- |
| Compiler host | ICINT19 | ICINT19 | Intended MVS native load module |
| Option transport | OPTIONS DD | CAMBPARM DD via shim | Historical EXEC PARM pseudo-stream |
| Option grammar | Single record | Two phases, slash boundary | Historical two-phase grammar |
| Source input | SYSIN | SYSIN | Historical SYSIN |
| Intermediate | Textual OCODE | In-memory Cambridge OCODE | Historical in-memory OCODE |
| Normal output | INTCODE | Textual CODE | Historical SYSGO object deck and optional CODE |
| Application execution | ICINT19 | Native after IFOX/IEWL | Intended native |
| RC4 status | Supported | CAMBCOMP absent | Unfinished |

| Spelling | MR10 | Cambridge front end | Cambridge generator |
| --- | --- | --- | --- |
| C | Parse without OCODE | Disable forced uppercase | Stack-check generation |
| N | Suppress GET | Numeric OCODE and OCODE listing | Suppress binary deck |
| P | Token debug | Pnnn free stack | Call and other counting |
| T | AE tree | Inactive case | Inactive case |
| M | MAPSTORE | Inactive case | Member naming |
| L | Lnnn tree allocation | Not recognized | Listing |
| A | Character-literal conversion | Historical EBCDIC-to-ASCII | Not recognized |

These differences are not aliases. Source recognition and emitted instructions are not equivalent to verified functional support. Consult the applicable source, installed revision, release guide and test evidence before selecting nondefault modes. DR.5 comparison of the option inventories with the historical source confirms their recognized switches and inactive cases within source-observed scope. The Cambridge note's early A/N/ wording describes the superseded experiment; the current /N/ record is controlling for the bootstrap. This working manual does not supersede the [MR10 option inventory](../../mr10-kit-compiler/docs/compiler-options.md) or [Cambridge option transport note](../../bootstrap-toolchain/bootstrap-cambridge/compiler-options-and-parm.md); the [migration ledger](../../packaging/milestones/documentation-refactoring/dr2-compiler-manual-migration-20261125.md) records their reconciliation.
