# Explanation of BCPL Compilers

*Cambridge BCPL Programming System for MVS 3.8J*

This manual explains the relationships between the surviving BCPL compilers, their intermediate languages and the MVS reconstruction. For invocation interfaces and option meanings, see the [compiler reference](Reference-for-BCPL-Compilers.md); for programming, see the [BCPL tutorial](Tutorial-on-BCPL-Programming.md) and [language reference](Reference-for-the-BCPL-Language.md).

## 1. BCPL origins and surviving compiler materials

BCPL originated in Martin Richards's work on a portable systems programming language derived from CPL. A major goal was to make compiler construction and porting practical by separating the language front end from machine-dependent code generation. A compiler written largely in BCPL could then be transported using a relatively small interpreter or target-specific back end.

The [historical transport tape index](../../richards-bcpltape/INDEX) distinguishes two especially important collections:

| Collection | Contents and role |
| --- | --- |
| MR10.BCPLKIT | BCPL sources SYN, TRN, CG, ICINT and BLIB, and compiled INTCODE phases SYNI, TRNI, CGI and BLIBI; a portable bootstrap kit |
| BCPLIB.BCPL | Cambridge compiler master BCPL, SYN, TRN, CG and their headers; historical BLIB, IOS, PM and EDITMAIN |
| BCPLIB.JCL and SYS1.USERPROC | Historical object/load-library construction and compile/link/go procedures |
| KM10.BCPLMAC | Machine-dependent runtime macro evidence |

The original BCPLMAIN assembler member and the listed historical compiler and library object modules are missing from this archive. Recovering BCPL sources is therefore not equivalent to recovering a runnable native compiler. The reconstruction supplies missing machine-dependent facilities and validates them on MVS 3.8J under Hercules/TK5.

The preserved [historical materials](../../richards-bcpltape/) remain primary evidence; the [history briefing](../BCPL-history-and-porting.md) provides broader context. Historical authorship and redistribution qualifications are recorded in [third-party notices](../../THIRD-PARTY-NOTICES.md). Modern BCPL systems and dialects are not the same compiler as either collection.

## 2. Source translation — SYN, TRN and OCODE

SYN (including lexical analysis) reads BCPL source and constructs the applicative-expression (AE) tree. TRN resolves names and declarations, assigns storage and labels, and translates the tree into OCODE, a machine-independent, stack-oriented intermediate language. OCODE describes operations such as loading a local/global word, evaluating arithmetic, making calls, branching and describing data.


```text
BCPL source -> lexer/parser (SYN) -> AE tree
            -> translator (TRN) -> OCODE
```

For example, a source expression that reads two local words and adds them is represented in OCODE by load operations and an addition operation. The back end decides how to realize those operations; the source front end need not prescribe System/370 registers or instructions.

The MR10 compiler exposes a textual OCODE stream as the interface to its separate code generator. The Cambridge master retains OCODE in a workspace buffer for direct consumption by CG370 and can also list it. These are related intermediate representations, not a promise that any OCODE deck is interchangeable between compiler versions. See [MR10 TRN](../../richards-bcpltape/mr10/bcplkit/trn) and [Cambridge TRN](../../richards-bcpltape/bcplib/bcpl/trn).

## 3. Back ends — CGI to INTCODE and CG370 to System/370 assembler

OCODE is the branching point, not INTCODE.


```text
                         +-> CGI -> INTCODE -> ICINT -> execution
BCPL -> SYN/TRN -> OCODE |
                         +-> CG370 -> CODE -> IFOX -> object deck
                                   -> SYSGO (historical direct deck)
```

The [MR10 CG source](../../richards-bcpltape/mr10/bcplkit/cg), compiled as CGI, lowers OCODE into a compact register-oriented virtual-machine instruction stream. ICINT executes those virtual instructions on the host.

The [historical Cambridge CG](../../richards-bcpltape/bcplib/bcpl/cg), called CG370 here to distinguish its target, instead consumes Cambridge OCODE. It models the evaluation stack, keeps useful values in registers, spills others into workspace, normalizes System/370 addresses and resolves internal labels. It can produce symbolic System/370 assembler and historically also builds binary ESD, TXT, RLD and END records itself. The current demoted toolchain deliberately uses textual CODE and IFOX rather than claiming a byte-preserving direct object-deck path.

CG370 divides native code into sections. Its four approximately 4 KB address windows accommodate System/370's 12-bit RX displacement. A procedure inside a section does not create an independent CSECT. The historical generator diagnoses an oversized section; the intended remedy is to split the source into sections, not to treat the limit as the maximum size of an entire program. See [CG370 architecture notes](../../packaging/architecture/cg370-architecture-notes.md).

## 4. MR10 Kit Compiler — ICINT19 and interpreted execution

The MR10 Kit Compiler is the independently usable compiler in RC4. The installed compiler is not an MVS load module called SYNI: the MVS load module is ICINT19, an assembler implementation of the INTCODE interpreter. SYNI, TRNI, CGI and BLIBI are preserved INTCODE decks; ICLIB supplies reconstructed host support.


```text
MVS ICINT19 running SYNI + TRNI + BLIBI + ICLIB
    BCPL source -> OCODE
MVS ICINT19 running CGI + BLIBI + ICLIB
    OCODE -> application INTCODE
MVS ICINT19 running application INTCODE + required libraries
    application -> results
```

The same interpreter can run both the compiler phases and compiled applications. The MR10 compiler obtains OPTIONS and named GET inputs through its stream interface; the compiler driver supplies MVS DD allocations, not host include-path semantics. MR10's option N suppresses GET, unlike either Cambridge N switch. The compiler reference describes the distinct transports. Compilation and execution are still distinct jobs or steps with distinct input and output artifacts.

The [MR10 source inventory](../../mr10-kit-compiler/source/README.md) identifies the phase decks, and [suite JCL](../../mr10-kit-compiler/jcl/README-SUITES.md) demonstrates their staging and use. The [ICINT19 build instructions](../../mr10-kit-compiler/jcl/README-ICINT19.md) describe assembly, link-edit and installation of the interpreter, not regeneration of the compiler phases.

## 5. Interpreter-hosted demoted Cambridge Compiler — bootstrap, CAMBCOMP and native application output

A later compiler may recognize constructs that the older kit cannot compile. That does not mean the later compiler's implementation needs to use every construct it recognizes. The project adapts the Cambridge implementation source to the older kit dialect instead of extending MR10 until it becomes Cambridge.

The [bootstrap build](../../bootstrap-toolchain/bootstrap-cambridge/README.md) derives source units using make-demoted.py, prepares a larger-name MR10 translator TRNILRG, and builds the resident CAMBCOMP INTCODE image using [CAMBBLD](../../bootstrap-toolchain/jcl/cambbld.jcl). Source transformations include splitting SECTION containers, adjusting header and operator spellings, splitting large packed lexer literals, and explicitly disabling floating-literal parsing where the bootstrap cannot implement it. The tracked demoted directory is an earlier snapshot, not the current generator's output. Distinguish syntax used to implement the compiler from syntax it recognizes in applications: for example, the generator rewrites an ABS expression in the compiler's EVALCONST implementation for MR10 without deleting the corresponding Cambridge constant-expression case. The fatal READFLOAT replacement, by contrast, explicitly removes a usable floating-literal parser in this bootstrap. Neither fact establishes native execution of every historically recognized operator. The generator's removal of SECTION wrappers and the master's NEEDS "$LOAD$" is also an adaptation of the compiler's own source. Its application parser still recognizes SECTION and NEEDS and its translator emits the corresponding OCODE metadata; successful native dependency resolution must be established separately.

There are also host/target representation accommodations. ICINT19 uses fullword storage but GETBYTE/PUTBYTE expose two packed bytes per interpreted word. Native System/370 BCPL uses four bytes per word. The generated TRN advances its OCODE buffer after two host bytes, whereas CG370 uses a private PK370 helper at target-packing sites. The bootstrap defaults to CODE370 character translation for the ASCII host to EBCDIC target direction. Its FINDPARM shim reads CAMBPARM rather than a native runtime parameter pseudo-stream.


```text
Historical Cambridge compiler source
    -> controlled source derivation -> MR10 compilation -> CAMBCOMP INTCODE

Application BCPL source
    -> CAMBCOMP running under ICINT19
    -> Cambridge OCODE -> CG370 -> System/370 assembler
    -> IFOX -> IEWL -> native application
```

The compiler remains interpreted. The resulting application is native; it does not use ICINT19 to execute its generated System/370 instructions. The [first native code-generation checkpoint](../../packaging/evidence/bootstrap-cambridge/native-codegen-checkpoint.md) records the factorial probe and the host/target packing correction. The current normal parameter record is /N/ followed by slash fill; the earlier A/N/ experiment was not the correct character-translation direction.

## 6. Native-running Cambridge Compiler — recovered design and unfinished reconstruction

The historical native Cambridge compiler was itself a System/370 program. Its master could use separately loaded compiler segments (SYN, TRN, CG and PROGRAM), or use a resident generator. The historical [MAKEOBJ](../../richards-bcpltape/bcplib/jcl/makeobj) and [MAKELIB](../../richards-bcpltape/bcplib/jcl/makelib) describe object and load libraries, including COMPBLIB with its special ABORT assignment, the BCPL root segment, and separate compiler segments.

The historical design also includes native runtime parameter processing and direct object-deck generation. The reconstructed application Core Runtime and the compiler's own required runtime services overlap, but successful application execution does not establish that all services needed by a native compiler are implemented.

The project reserves [cambridge-compiler](../../cambridge-compiler/) for this unfinished subsystem. Its copied MAKEOBJ/MAKELIB jobs are historical evidence, not an accepted installation procedure; they refer to original site resources and include deletion steps. Do not submit them as current jobs.

The eventual native-running compiler must execute as an MVS load module and generate valid native programs, including a demonstrated native compiler rebuild/self-compilation where required by its acceptance. No such completion or release is claimed by this manual.

## 7. Assembly, link-edit, runtime and application relationships

The textual native path separates three jobs of work: generating assembler, assembling a relocatable object, and linking objects into an executable load module. IFOX00 translates System/370 assembler; IEWL resolves control-section references and relocations and constructs the load module. Neither tool translates BCPL source.

The historical factorial listing begins with these records (excerpt from the accepted checkpoint):


```asm
 CSECT
 EXTRN BCPLMAIN
 USING 4096,1,2,3
```

BCPLMAIN participates in startup, global-vector construction and transfer to the application's START. Ordinary native applications use the Cambridge Runtime Library (Core Runtime plus historical Base Library, BLIB), supplemented by the Coroutine Support Library or selected optional System Extensions as required. A declaration header publishes names/numbers; it is not linked code. A GLOBAL number must agree with the selected implementation and the applicable registry. The [runtime nomenclature](../../packaging/architecture/runtime-and-library-nomenclature.md) distinguishes logical libraries from physical object and load library PDSes.

A successful compiler run proves neither IFOX acceptance of the generated listing nor IEWL resolution nor execution of the resulting application. All are separate verification boundaries.

## 8. Compatibility and evidence — shared and distinct execution domains

| Environment | Compiler executes as | Application executes as | Status |
| --- | --- | --- | --- |
| MR10 Kit Compiler | INTCODE under ICINT19 | INTCODE under ICINT19 | Independently usable, distributed in RC4 |
| Interpreter-hosted demoted Cambridge Compiler | CAMBCOMP INTCODE under ICINT19 | System/370 machine code after IFOX/IEWL | Verified development toolchain; CAMBCOMP not distributed in RC4 |
| Native-running Cambridge Compiler | Intended System/370 MVS load module | Intended System/370 machine code | Unfinished; historical sources and native components distributed as work in progress |

The [RC4 companion](../../packaging/distribution/publication/RC4-README.md) records 80/80 functional cases across MR10 and COMBINED installations. Native-only installation acceptance is inventory acceptance, not native functional certification. No independent IPL or alternate HLQ/site test is claimed.

The [CO.6 qualified closure](../../packaging/milestones/coroutines/co6-formal-acceptance-and-closure-20261116.md) records 208 supported development passes and one expected skip, including two paired interpreted/native coroutine oracles. It retains a genuine failure in the original manually constructed MR10 fixed-stack fixture. Passing the common application behavior does not imply matching internal ABIs, pointer values, stack layouts, packed bytes or compiler dialect coverage. Historical options that produce assembler do not necessarily have working runtime support.

Choose the execution environment first, then the corresponding language subset, library contracts, compilation workflow and test evidence. Neither compiler self-compilation nor a finite regression panel alone can establish complete historical compatibility.
