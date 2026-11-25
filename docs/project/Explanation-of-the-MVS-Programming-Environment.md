# Explanation of the MVS Programming Environment

**Audience:** Programmers, operators and developers.  
**Status:** DR.3 working explanation; reviewed at `f111b92ff7fb8805c4f62bde46d8249752b5740b`.

BCPL on MVS involves several distinct layers: the language and its execution conventions, the compiler or interpreter, System/370, the MVS operating system, JES and the Hercules emulated devices. Knowing which layer owns an address, symbol, record or failure makes the reconstruction easier to modify, reconstruct, test and release.

This explanation consolidates the existing programmer briefings. It is neither a complete machine or macro reference nor a replacement for the runtime contracts. The original briefings and authoritative sources remain available during migration. Worked examples are explanatory; excerpts of real code are identified by their source and are not new MVS executions.

[Documentation catalog](../README.md) | [Develop and test BCPL for MVS](How-to-Develop-and-Test-BCPL-for-MVS.md) | [Reference for Project Tools](Reference-for-Project-Tools.md)

## 1. System/370 architecture — registers, addressing, instructions and PSW

System/370 is a machine architecture, not MVS. Different hardware models implement its facilities; Hercules emulates the programmer-visible machine. Storage is byte-addressed; the sixteen general-purpose registers R0–R15 each contain 32 bits. The target architectural addresses are 24 bits, giving a 16 MiB address range, not an entitlement to allocate that much storage.

The instruction format defines how operands are encoded. RR denotes register-to-register, RX register and indexed storage, RS register and storage, SI storage and immediate, and SS storage-to-storage. For RX addressing, the effective address is the sum of base and index address components and a 12-bit unsigned displacement. A zero base or index field contributes zero, not the contents of R0. Thus with R12=X'00100000', R3=X'00000014' and displacement X'028', the resulting address is X'0010003C'. The displacement alone covers 0–4095. Larger areas require suitable base relationships or address computation. Addressability and valid allocated storage are separate questions.

| Instruction | Interpretation |
| --- | --- |
| LR 3,4 | Copy R4 into R3 |
| L 3,VALUE / ST 3,VALUE | Load/store a fullword |
| LA 3,VALUE | Form an address, not load its contents |
| LH 3,HALF / STH 3,HALF | Load signed halfword with extension/store low halfword |
| AR 3,4 / SR 3,4 | Fixed-point register addition/subtraction |
| XR 3,3 | Clear R3 |
| MVC TARGET(20),SOURCE | Move 20 bytes in storage |
| C 3,VALUE | Compare signed fullwords |

The PSW includes an instruction address, a two-bit condition code, protection key, masks and execution-control fields. Condition codes depend on the instruction that produced them: comparison can indicate equal/low/high; arithmetic can indicate zero/negative/positive/overflow. Branch mnemonics such as BE and BH select conditions. Register pairs in multiply, divide and double-length shifts have instruction-specific restrictions. Consult the instruction definition rather than extrapolating from modern CPU behavior.

Interruptions transfer control through the architecture's PSW mechanism. Program, supervisor-call, I/O, external, machine-check and restart interruptions are distinct. The old PSW need not identify the exact faulting instruction; instruction length and the interruption's definition matter. DAT and protection connect these machine operations to MVS. No general register is a hardware-defined stack pointer; MVS and native BCPL impose different software conventions.

Further reading: [System/370 briefing](../System_370-briefing.md); IBM [System/370 Principles of Operation, GA22-7000-4, September 1975](https://bitsavers.org/pdf/ibm/370/princOps/GA22-7000-4_370_Principles_Of_Operation_Sep75.pdf). Indexed primary-source text was consulted for base/index/displacement addressing; individual instruction and model-option verification remains outside this orientation.

## 2. IBM data — words, bytes, EBCDIC, binary/decimal and records

Storage contains bytes, not language types. Interpretation follows the instruction and interface. A halfword is two bytes, a fullword four, a doubleword eight. Binary values are big-endian: X'12345678' appears as bytes 12, 34, 56, 78 in ascending addresses. Signed integers use two's complement. X'FFFFFFFF' is -1 when interpreted as a signed fullword, not in every data representation. Alignment depends on the instruction; DS 0F and DS 0D can align the assembler location counter.

Illustrative assembler definitions:

```asm
BYTE     DC    X'F1'
HALF     DC    H'1234'
FULL     DC    F'123456'
TEXT     DC    C'HELLO'
DECIMAL  DC    PL4'1234567'
FLOAT    DC    D'123.456'
```

X specifies exact bits, H/F binary integer constants, C target character bytes, PL packed decimal and D double-precision hexadecimal floating point, not a doubleword integer. IBM hexadecimal floating point is not IEEE-754. Zoned decimal holds a digit per byte with zone/sign information. Packed decimal holds digit nibbles and a final sign nibble: positive 1234567 with sign C can be represented as X'1234567C'. An arbitrary binary integer or ASCII digit sequence is not automatically valid packed decimal. Check defined bit numbering and preserve unrelated flag bits.

EBCDIC is the normal target character encoding. In CP037, A is X'C1', a blank X'40', digit 1 X'F1'. Character collating order differs from ASCII and punctuation mappings differ across code pages. The tracked text transport policy is in [DSPAL configuration](../../config/dspal.yaml). Historical BCPL source encoding and its accepted qualifications remain in the [BT0021 encoding reconciliation](../../packaging/distribution/compiler-source/rc2-job9330-reconciliation-acceptance-and-encoding-decision-20261120.md).

Fixed-length fields, counted BCPL strings and C NUL-terminated strings are different. MVS record boundaries do not depend on a universal newline character. An 80-byte record can contain source text or binary object information; never apply host text normalization to binary FB80 or load-module records.

Native BCPL uses 32-bit words and word-addressed data pointers, while System/370 addresses bytes. For a valid native word pointer X'00040000', scaling by four yields byte address X'00100000'; a byte offset of 3 selects X'00100003'. Reverse conversion requires suitable alignment. Do not apply this rule to every MVS parameter or historical interpreted representation. Chapter 12 shows the real bridge.

Further reading: [IBM data briefing](../IBM-data-representation.md), GA22-7000-4, [Reference for the BCPL Language](../product/Reference-for-the-BCPL-Language.md).

## 3. MVS architecture — address spaces, tasks, program state and storage

MVS (Multiple Virtual Storage) runs above System/370. Dynamic Address Translation (DAT) allows virtual addresses in different address spaces to denote different real storage. Each address space has private and common/system mappings; exact layouts depend on configuration. Real frames and paging backing storage are managed by MVS. A virtual page need not be continuously resident.

```text
virtual address in an address space
          |
    DAT and protection
          |
     real storage
```

REGION describes a private virtual-storage constraint subject to MVS rules, not dedicated physical RAM. Allocation failure can reflect region/subpool limits, fragmentation, excessive request size or a leak. The nucleus, CSA (Common Service Area) and SQA (System Queue Area) are system facilities, not ordinary application workspace.

An address space is a storage context; a task is an execution context within it. Tasks can share private storage subject to ownership and protection. MVS dispatches eligible tasks and can suspend them for events/I/O. ATTACH creates subordinate task execution; BCPL coroutine switching does not create an MVS task.

The PSW distinguishes problem and supervisor states. Privileged instructions are restricted; problem programs use defined system interfaces. Storage keys participate in protection. MVS authorization is a separate constraint from CPU state. An assembler program does not gain arbitrary privilege merely by issuing an SVC.

GETMAIN and FREEMAIN obtain and release MVS-managed storage. Length, location, subpool, ownership and lifetime are service contracts. A numerical address alone does not establish who may free the storage. A save area preserves linkage state, whereas a language stack supports language invocation state. Reentrant programs must manage invocation-specific writable state; marking a module reentrant does not make unsafe shared static data safe.

Further reading: [MVS overview](../MVS-3_8-briefing.md), [storage and addressing](../MVS-storage-and-addressing.md), IBM *OS/VS2 MVS Overview* GC28-0984 and the applicable supervisor documentation. Detailed release-specific layout and control blocks require further verification.

## 4. System interfaces — supervisor services and macros

A macro is source generation by the assembler. It can expand to instructions, parameter lists, branches, declarations and an SVC where required. SVC is a machine instruction that causes a supervisor-call interruption; not every system macro is one SVC. The documented service and its actual expansion govern registers, storage and errors.

| Interface | Role |
| --- | --- |
| GETMAIN / FREEMAIN | Storage allocation/release |
| LOAD / DELETE | Obtain/release logical use of a loadable module |
| LINK / XCTL | Invoke with return / transfer without return to transferring program |
| ATTACH | Establish subordinate task |
| WAIT / POST | Event synchronization with documented ECB conventions |
| ENQ / DEQ | Named resource serialization |
| TIME and interval services | Time or interval functions |
| STAE and recovery facilities | Defined abnormal-condition recovery |
| ABEND | Request abnormal termination |
| OPEN / CLOSE / GET / PUT | Access-method operations |

WAIT/POST concerns events and task readiness; ENQ/DEQ concerns resource ownership. Neither should be confused with a host-side release-driver lock. Control blocks describe system state; mapping macros and DSECTs describe field offsets. Use documented fields, lengths, flags and interface versions. Visibility in a dump is not permission to modify internal storage.

Actual [BCPLMEM](../../bootstrap-toolchain/asm/bcplmem.asm) computes GETVEC(N)'s byte length from N+1 words and its private header, then uses `GETMAIN EC,LV=(8),A=GVRADDR,SP=0` and checks R15. It links only a successful allocation into its list. FREEVEC unlinks a known live allocation before using `FREEMAIN R,LV=(4),A=(1)` with the saved byte length. This is source-observed behavior, not a generic allocation template or proof of all failure cases. Its private allocator is nonreentrant.

Channel Command Words describe device operations; EXCP offers a lower-level MVS path to execute a channel program. It requires more programmer responsibility than an access method, including device and completion conventions. Most sequential BCPL I/O should use the runtime or relevant documented record interface, not direct channel programming.

Further reading: [system interfaces briefing](../MVS-system-programming-interfaces.md); IBM [OS/VS2 MVS Supervisor Services and Macro Instructions, GC28-0683-3, September 1983](https://bitsavers.trailing-edge.com/pdf/ibm/370/OS_VS2/Release_3.7_1976/GC28-0683-3_OS_VS2_MVS_Supervisor_Services_and_Macros_Rel_3.7_Sep83.pdf). This later revision of the manual family was consulted for conventional linkage; exact target macro forms need the installed macro definitions and applicable release documentation.

## 5. Datasets and access methods — sequential/PDS, DCB and QSAM

An MVS data set has a name, organization, allocation and record characteristics. The catalog helps locate it; it is not its data. Names are dot-separated qualifiers, normally up to eight characters each. A physical sequential data set (PS) holds sequential records; a partitioned data set (PO/PDS) holds named members and a directory. DSN(MEMBER) is a member selection, not a filesystem path. PDS directory space and data extents are distinct; replacement can leave unused gaps, and IEBCOPY compression is a persistent reorganization. Temporary names begin with &&. Indexed and direct organizations have different access contracts.

A DCB (Data Control Block) describes the access-method interface. OPEN reconciles program intent, DD allocation, data-set characteristics and defaults, establishing access and buffers. CLOSE finalizes that processing. The program can use a logical DDNAME while JCL binds it to the actual data set, in-stream input or JES output.

| RECFM | Meaning |
| --- | --- |
| F / FB | Fixed-length, unblocked / blocked |
| V / VB | Variable-length, unblocked / blocked |
| FBA | Fixed blocked with ASA carriage-control byte |
| U | Undefined-format records; used for load modules and specialized data |

LRECL is the logical record length (maximum including descriptor for ordinary V/VB); BLKSIZE describes the physical block length or maximum as applicable. FB80/800 permits ten records per full block. An ordinary unspanned variable record has a four-byte RDW whose length includes the RDW. Its block has a four-byte BDW including itself. A three-byte payload can have RDW X'00070000'; a block containing only that record can have BDW X'000B0000'. These are illustrative descriptor values, not a block-building API. Spanned record conventions differ. The FBA carriage-control byte is part of the record and is interpreted by the appropriate output processing.

QSAM buffers logical records and supplies GET/PUT; move and locate modes have different buffer contracts. EODAD specifies the end-of-data exit rather than assuming GET returns a C-like EOF value. BSAM gives more explicit block control through READ/WRITE/CHECK. BPAM supports partitioned organization/member access. Device independence has limits.

The actual [BLIBBLD job](../../bootstrap-toolchain/jcl/blibbld.jcl) uses a BLIBPREP helper. Selected excerpt, intervening logic omitted:

```asm
         OPEN  (INDCB,(INPUT))
         OPEN  (OUTDCB,(OUTPUT))
READLOOP GET   INDCB,CARD
*        ... card transformation omitted ...
WRREC    PUT   OUTDCB,CARD
         B     READLOOP
EOF      CLOSE (INDCB)
         CLOSE (OUTDCB)
*        ... return processing omitted ...
CARD     DS    CL80
INDCB    DCB   DDNAME=RAW,DSORG=PS,MACRF=GM,EODAD=EOF
OUTDCB   DCB   DDNAME=READY,DSORG=PS,MACRF=PM
```

RAW and READY bind temporary compiler output and prepared FB80 source in FIXASM. The program processes CARD, not a host filename. The complete source and macro contract govern behavior.

BCPLIO's character streams differ from optional BCPLQSAM logical records. BCPLQSAM hides RDW/BDW from the caller's variable payload and has a 1024-byte private staging ceiling; it supports a qualified subset including FBA. These are project limits, not MVS-wide restrictions. A successful PUT or CLOSE is not proof of final physical printer/punch delivery.

Further reading: [access-method briefing](../MVS-access-methods.md); IBM [OS/VS Data Management Services Guide, GC26-3783-5, November 1975](https://bitsavers.org/pdf/ibm/370/OS_VS/dms/GC26-3783-5_OS_VS_Data_Management_Services_Guide_197511.pdf), consulted for organization and ordinary RDW/BDW; [BCPLQSAM public specification](../../packaging/milestones/qsam/bcplqsam-public-interface.md).

## 6. JCL and JES — jobs, steps, DDs, allocation, spool and codes

JCL describes the execution environment, not application code. JOB identifies the job, EXEC specifies a program or procedure step, DD defines that step's resources. JES2 reads and queues jobs, processes spool and routes output; MVS initiators and allocation/program-management services execute the work.

```text
reader -> JES input/queue -> conversion/scheduling
       -> initiator -> allocation and step execution
       -> JES output spool -> selected writer/device
```

DSN, DISP, UNIT, VOL, SPACE, DCB and SYSOUT define allocation and routing. DISP=(NEW,PASS,DELETE) creates a data set, passes it to subsequent steps on normal completion and deletes it after abnormal completion. OLD requests exclusive use; SHR permits shared use under applicable rules; MOD has organization-dependent modification/append or allocation semantics. DD DUMMY supplies a dummy interface; DD * supplies in-stream records. Concatenation presents compatible inputs or libraries to a single DD. JOBLIB/STEPLIB are load-library definitions, distinct from assembler macro and IEWL object-library DDs. Procedure symbolic parameters affect expansion; EXEC PARM supplies input to the executing program.

Actual selected [BLDCORCO](../../bootstrap-toolchain/jcl/bldcorco.jcl) job-body records (not an independent runnable deck):

```jcl
//SYSGO    DD DSN=&&COOBJ,UNIT=SYSDA,
//             SPACE=(80,(300,100)),DISP=(NEW,PASS),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
//SYSIN    DD DSN=HERC02.BCPL.BOOT.ASM(BCPLCO),DISP=SHR
//* BLOCK INSTALL UNLESS IFOX RETURNS ZERO.
//PUTCOR   EXEC PGM=IEBGENER,COND=(0,NE,ASMCOR)
//SYSPRINT DD SYSOUT=*
//SYSIN    DD DUMMY
//SYSUT1   DD DSN=&&COOBJ,DISP=(OLD,PASS)
//SYSUT2   DD DSN=HERC02.BCPL.BOOT.OBJ(BCPLCO),DISP=OLD
```

ASMCOR creates temporary binary object output. PUTCOR writes a permanent member; COND expresses a bypass test, so a nonzero ASMCOR code bypasses PUTCOR. Subsequent RDCOR/VFCOR read and compare the result. Assembling and installing are distinct actions.

A DSPAL stored-body submission creates a launcher and actual payload. Read the actual payload job report. Names and numbers can be reused; identify the fresh run and the specific step/procedure step/DD. SYSOUT routes to spool, not necessarily immediately to a device. JES writer state and Hercules attachment are separate.

CPU condition code, JES step RC, assembler severity, ICINT CODE, GO RC and independent semantic output are not synonyms. Nonzero normal RC is utility-specific, ABEND denotes abnormal termination, and bypassed steps did not perform their intended work. Do not assume RC4 is harmless.

Further reading: [JCL briefing](../JCL-for-the-programmer.md), the applicable IBM OS/VS2 MVS JCL/JES2 manuals, and [Reference for Project Tools](Reference-for-Project-Tools.md).

## 7. IFOX assembler — source cards, directives, macros, CSECTs and bases

IFOX00 assigns section-relative locations, translates machine instructions, evaluates symbols, expands macros and literals, and emits object and diagnostic information. IEWL is a separate step.

Card-oriented source separates name, operation, operands, comments, continuation and sequence fields. The maintained hand-written source uses ASCII host text, no tabs or trailing whitespace, source through column 71, at most eight-character labels, and column-1 full-line comments. These project hygiene rules do not replace the historical assembler's complete continuation syntax. [check-asm-source.py](../../tools/checks/check-asm-source.py) is not an assembler.

| Construct | Function |
| --- | --- |
| CSECT / START | Establish section/location context |
| EQU | Assign assembly-time symbol value |
| DC / DS | Define constants / reserve or align storage |
| DSECT | Describe a layout without allocating runtime storage |
| USING / DROP | Declare/revoke assembler base assumptions |
| LTORG | Place pending literals |
| ENTRY / EXTRN | External definitions/references |
| COPY / macro invocation | Include source / expand source |
| END | End module; applicable entry information |

A literal such as =F'1' denotes a constant placed in a literal pool. It must be addressable. An absolute value differs from a section-relative symbol; a DSECT requires an actual storage address established separately.

BALR 12,0 followed by USING *,12 is a conventional base-establishment idiom: BALR sets the next-instruction address component of R12 without branching to the second register, and USING informs the assembler of the corresponding location. USING does not load R12; a wrong runtime value can survive assembly and fail execution. Additional bases must be initialized as well as declared.

In BLDCORCO, SYSIN supplies the source and SYS1.MACLIB supplies system macros via SYSLIB. SYSGO receives temporary FB80 object output, SYSPRINT the listing. PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD' requests object output, not a punched deck, and extensive symbol/relocation listing information. Inspect flagged statements, severity and macro expansions; macros may change registers according to their own contracts.

Further reading: [IFOX briefing](../IFOX-assembler-toolchain-briefing.md); IBM [OS/VS-DOS/VSE-VM/370 Assembler Language, GC33-4010-5, March 1979](https://www.bitsavers.org/pdf/ibm/370/OS_VS/assembler/GC33-4010-5_OS_VS_DOS_VSE_VM_370_Assembler_Language_Mar79.pdf), consulted for USING/DROP. Verify the actual IFOX dialect.

## 8. Object modules and IEWL — symbols, relocation, maps and libraries

The assembler cannot know the final positions of separately compiled modules. A CSECT is an independently relocatable unit; the assembler supplies bytes and information needed to resolve external references and adjust address-sensitive fields.

| Traditional object record | Purpose |
| --- | --- |
| ESD | External Symbol Dictionary: sections, external definitions/references |
| TXT | Generated instructions and data |
| RLD | Relocation Dictionary: address-sensitive fields |
| END | Object module termination and applicable entry information |

Object modules commonly use binary FB80 records. TXT alone is not necessarily an executable image. IEWL chooses sections, resolves external references, processes relocation, selects the entry and creates a load module; loading subsequently makes it usable at its assigned address. A load module is not the same object deck in a new member, and U-format load libraries are not source text.

Source PDSes supply text; macro libraries supply assembler definitions; object PDSes supply relocatable modules; load PDSes supply executable members to program management. INCLUDE identifies a member and the relevant DD; automatic library search follows its own IEWL rules. A member name, CSECT, exported label and selected entry can be different. The linker's placement map and assembler listing are complementary.

The actual BLIBBLD PREPLK step consumes &&PREPOBJ and uses:

```text
 ENTRY BLIBPREP
 NAME BLIBPREP(R)
```

It writes the temporary load module via SYSLMOD. FIXASM executes PGM=*.PREPLK.SYSLMOD. ASMBLIB subsequently creates the BLIB object and INSTALL writes BOOT_OBJ(BLIB). The preparation helper is executed, not BLIB itself as a standalone application.

The [historical paired runtime promotion record](../../packaging/operations/runtime-object-promotion.md) shows that a missing SYSLIB/OBJ DD and unresolved STKOVFL are distinct link defects. Its dated pre-M3 paths are preserved evidence, not current procedures. A successful link with the wrong provider may still be a semantic failure.

Further reading: [object and load module briefing](../S370-object-and-load-modules.md), [IFOX briefing](../IFOX-assembler-toolchain-briefing.md), IBM *OS/VS Linkage Editor and Loader* GC28-6451. Precise object card and load-module layouts require release-specific study.

## 9. Program execution — loading, linkage, save areas and return

MVS program fetch locates a load module and makes it available for execution; the selected entry receives control. EXEC PGM identifies a loadable program, not an unlinked CSECT. Program management is distinct from assembly and link-edit.

Traditional MVS linkage assigns R1 parameter information (often an address list), R13 the caller's save area, R14 return linkage and R15 entry address or return status. Other roles depend on the interface. A conventional save area is 18 fullwords (72 bytes), with back and forward chain fields at offsets 4 and 8. A called routine preserves the required caller state, establishes addressability, obtains/chains a save area if needed, does its work and restores the environment.

Actual BLIBPREP source in BLIBBLD:

```asm
BLIBPREP CSECT
         STM   14,12,12(13)
         LR    12,15
         USING BLIBPREP,12
         LA    3,SAVEAREA
         ST    13,4(3)
         ST    3,8(13)
         LR    13,3
```

The STM range wraps from R14 through R15 and R0–R12. The new save area points backward to the caller, the caller forward to the new area. Its normal return path:

```asm
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
```

R15 is cleared after the restore that would otherwise overwrite the return code. This helper uses a static save area in its one-invocation context; it is not a reentrant template. SAVE/RETURN macros implement software conventions. R1 address lists may contain interface-specific flags/terminators. EXEC PARM is not a C argc/argv; APTOVEC adapts the relevant MVS parameter structure for the native BCPL environment.

BAL/BALR or macro CALL performs ordinary linkage. LOAD obtains module availability; LINK invokes a managed program with return, XCTL transfers without return to the transferring program, ATTACH establishes another task. Their lifetime/release contracts differ. Native BCPL's private frame and return register convention is not the MVS ABI.

Further reading: [program execution briefing](../MVS-program-execution.md), GC28-0683 Linkage Conventions and Program Management. Indexed IBM manual text confirms the save-area chain and register-return distinction; use the installed macro and service documentation for exact interfaces.

## 10. Debugging — listings, maps, dumps, abends and evidence

Find the first failed layer before inspecting an application dump. A JCL/allocation failure may prevent IFOX running; an assembly/link error may prevent GO; a normally completed JES job may still contain a failed interpreted CODE or application oracle.

| Evidence | Diagnostic question |
| --- | --- |
| JES, IEF/IEC messages | Which actual job, step and DD failed or was bypassed? |
| IFOX listing | First substantive error, source, machine bytes, severity and bases |
| IEWL map/XREF | Correct modules, symbols, placement and entry? |
| ABEND/dump | Actual interruption, PSW, registers and relevant storage |
| Access-method messages | DD, DCB, length, device, EOF and allocation? |
| CODE / application oracle | Exact expected and observed results, including zero-RC failures |

S0C1 denotes operation exception; S0C4 is protection or translation-related; S0C5 addressing exception; S0C7 data exception, commonly invalid decimal data. An invalid pointer can yield different failures according to address and state. A corrupted return address may branch into data. An overlay may damage a save area or DCB long before the observed crash. Do not infer cause from the code alone.

For an illustrative RX address, base X'00200000', index X'00000008', displacement X'034' yield X'0020003C'. Check the intended allocation and ownership. Trace the relevant PSW and interruption definition to the load address and IEWL map, then the same-build IFOX listing and source. Do not blindly subtract an instruction length from every PSW. Save-area chains assist traceback but can be corrupted.

Real [native case 075](../../tests/bootstrap/075-blib-writef-mixed-object/README.md) originally returned C:Z S:HI N:2 instead of C:Z S:HI N:42 even with zero step return codes; a later G!76 binding correction passed focused tests. This demonstrates why linking does not prove correct global bindings or variadic arguments. Preserve its original failure. [CO.6 closure](../../packaging/milestones/coroutines/co6-formal-acceptance-and-closure-20261116.md) likewise preserves the Bootstrap 117 IEWL SB2D and historical MR10 fixed-stack CODE=-1 incidents.

Retain revision, exact input and configuration, job identity, required steps, listings, map, completion records and independent oracle. Reused job numbers require fresh evidence attribution; use the appropriate printer-window mechanism and separately verify physical output devices. A failure is not authority to retry a guarded operation, flush unrelated queues, overwrite installed objects or purge. See [development and testing](How-to-Develop-and-Test-BCPL-for-MVS.md).

Further reading: [debugging briefing](../MVS-debugging.md), applicable IBM system-code/service-aids manuals and actual MVS reports.

## 11. Hercules and TK5 — emulated machine, devices and host/guest boundaries

Hercules emulates System/370 processors, storage, channels, interrupts and devices. TK5 supplies the MVS 3.8J environment. Hercules is not the guest OS, JES2, IFOX or IEWL. The guest executes emulated machine instructions, not a translation of BCPL into a host program.

```text
Host Linux / WSL
  Docker Compose container
    Hercules / TK5 virtual machine
      MVS 3.8J, JES2 and guest utilities
        ICINT19 or native BCPL application
```

Hercules configuration maps virtual device addresses/types to host resources. Guest device definitions must correspond. Starting Hercules constructs the machine; IPL boots MVS; guest and JES initialization follow. A running container does not establish reader readiness or successful execution.

The tracked [Compose file](../../docker/compose.yaml) defines service mvs, container mvs38j, image mvs38j-tk5:local and these mappings:

| Port or persistent host location | Role |
| --- | --- |
| 3270 | Terminal |
| 3505 | JES socket reader |
| 8038 | Hercules HTTP |
| mvs-state/dasd.usr | User/development DASD |
| mvs-state/tape | Tape image media |
| mvs-state/prt and pch | Printer/punch output |
| mvs-state/log | Emulator/TK5 logs |
| Git checkout | Read-only /workspace exposure inside container |

These are configuration, not a live inventory. Host pathname, Hercules device address, guest DSN, DD and JES class are different identities. AWS/HET media represents virtual tape; the guest observes tape files, labels and tape marks. Mounting in Hercules does not prove guest allocation/release. The accepted release layout contains 21 logical datasets and 64 physical tape files, not 21 host files.

Emulator console commands target Hercules; MVS/JES2 commands target the guest. The [console guide](../../tools/mvs/mvs-console-README.md) specifies routing, safety and display limitations. HTTP success does not prove guest command completion; async messages may be unrelated. A guest writer can be stopped while a virtual device exists. Preserve state, quiesce work before orderly shutdown, and do not reinitialize a device to bypass an allocation or media guard. Record the actual emulator version/configuration for machine-level investigations.

Further reading: [Hercules briefing](../Hercules-briefing.md), upstream [configuration](https://sdl-hercules-390.github.io/html/hercconf.html) and [installation/operation](https://sdl-hercules-390.github.io/html/hercinst.html) documentation. Use the installed-version reference rather than assuming every upstream feature is present.

## 12. Putting it together — BCPL, assembly, linkage, execution and I/O

The historical compiler's execution model must be distinguished from its output application's execution model.

```text
MR10 Kit Compiler:
  BCPL source -> SYNI/TRNI -> OCODE -> CGI -> INTCODE
  INTCODE + interpreted libraries -> ICINT19 under MVS

Demoted Cambridge Compiler development path:
  resident CAMBCOMP INTCODE under ICINT19
  BCPL source -> generated S/370 assembler
  IFOX00 -> relocatable application object
  IEWL + selected runtime/libraries -> load module
  MVS program fetch / GO -> native System/370 instructions
```

The native-running Cambridge Compiler is separate unfinished work. Native application execution does not establish a native-running compiler. RC4 includes the MR10 Kit Compiler, native components and selected historical Cambridge source; it does not contain the development CAMBCOMP image or a native-running compiler. See [compiler explanation](../product/Explanation-of-BCPL-Compilers.md) and [distribution index](../../packaging/distribution/README.md).

BCPLMAIN coordinates startup, global/system vectors and root workspace. The Core Runtime and independently compiled Base Library form the Cambridge Runtime Library; Coroutine Support Library and optional System Extensions are distinct. Use the [approved nomenclature](../../packaging/architecture/runtime-and-library-nomenclature.md). A global declaration, link-editor inclusion and executable-address registration are separate. Select exactly one application BCPLREG table; do not infer all optional packages are mandatory.

Actual [BCPLBYTE](../../bootstrap-toolchain/asm/bcplbyte.asm) implements:

```asm
GETBYTE  LR    14,7
         SLL   14,2
         AR    14,8
         SR    7,7
         IC    7,0(14)
         L     4,0(5)
         BCR   15,6
```

R7 begins as a BCPL word pointer and becomes the result; R8 contains a byte offset, R5 is the frame byte address, and R6 is return linkage. SLL scales the pointer, AR adds the byte offset, SR clears R7 and IC inserts the byte. The final instructions restore the base convention and return. This is not an MVS R1/R14 call, does not translate characters, and does not protect arbitrary pointers.

GETVEC(N) allocates N+1 words. BCPLMEM translates this into MVS byte allocation including private bookkeeping, returns a word pointer and uses FREEMAIN on known live allocations. Native coroutine support is separately qualified to a root and at most two live registered workers with checked 1024-word worker stacks and known-live lifecycle. It does not implement MVS task scheduling or every historical coroutine behavior. See [runtime reference](../product/Reference-for-the-Cambridge-Runtime-and-Libraries.md) and [memory-management research](../BCPL-memory-management.md).

The actual [case 075 BCPL source](../../tests/bootstrap/075-blib-writef-mixed-object/source.bcpl) is:

```bcpl
GLOBAL $( START:1; WRITEF:76 $)

LET START () BE
$(1
    WRITEF("C:%C S:%S N:%N", 'Z', "HI", 42)
    FINISH
$)1
```

Its independent [oracle](../../tests/bootstrap/075-blib-writef-mixed-object/expected.txt) is:

```text
C:Z S:HI N:42
```

The native compile path generates assembler for global calls. IFOX emits object records; IEWL resolves selected runtime/library symbols; MVS loads the result. Startup binds G!76 to the historical BLIB formatter. Output passes through the runtime character-stream service, QSAM, DD binding and JES spool to the appropriate output. A valid object, link and GO are necessary but not sufficient for the specified output, as Chapter 10 demonstrates.

Controlled reconstruction derives artifacts from Git; target evidence verifies the resulting behavior; a release separately freezes and verifies the actual selected payload. The [historical porting briefing](../BCPL-history-and-porting.md) remains useful background. The other project manuals own operational procedures and tool interfaces; product manuals explain the supported BCPL system.

The draft draws on existing briefings, actual source/JCL and selected IBM primary-source text. Scanned page-image requests failed; full exact-edition and clause-level technical reconciliation remains for DR.5. No new MVS execution is claimed. No historical contract or normative authority is transferred.
