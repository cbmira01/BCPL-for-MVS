# Reference for the Cambridge Runtime and Libraries

*Cambridge BCPL Programming System for MVS 3.8J*

**Status:** DR.2 working reference. Existing contracts retain authority pending individual reconciliation, validation and owner approval. This is a supported-domain synopsis, not a complete historical LIBHDR implementation or a replacement for private assembler interfaces.

## 1. Scope, terminology and compiler-specific interfaces

Core Runtime plus historical Base Library (BLIB) constitute the Cambridge Runtime Library. Coroutine Support Library is separate from BLIB; optional System Extensions, Standard Libraries and User/Site Libraries retain their own roles. See [nomenclature](../../packaging/architecture/runtime-and-library-nomenclature.md) and the [runtime explanation](Explanation-of-the-Cambridge-Runtime-and-Libraries.md).

| Domain | Application execution | Evidence boundary |
| --- | --- | --- |
| MR10 Kit Compiler | ICINT19 executing INTCODE with BLIBI/ICLIB and selected modules | RC4 supported, MR10 and COMBINED profiles |
| Interpreter-hosted demoted Cambridge Compiler | Native System/370 after CG370, IFOX and IEWL | Accepted development profiles; RC4 native inventory only |
| Native-running Cambridge Compiler | Intended native applications | Compiler reconstruction unfinished |

Source-observed means inspected implementation, not a fresh MVS test. Accepted results are limited to the named profile, source and oracle. The [RC4 companion](../../packaging/distribution/publication/RC4-README.md), [CO.5 closure](../../packaging/milestones/coroutines/co5-formal-acceptance-and-closure-20261116.md) and [CO.6 closure](../../packaging/milestones/coroutines/co6-formal-acceptance-and-closure-20261116.md) supply release/development distinctions.

The [runtime interface conventions](../../packaging/architecture/runtime-interface-conventions-and-contracts.md) distinguish declaration, behavior and execution ABI. The [Global Number Registry](../../packaging/architecture/global-number-registry.md) owns allocations, including historical reserved slots that lack implementations. The following tables describe selected facilities without making new allocations.

## 2. Core Runtime — startup, exports, globals, registers, calls and stack

### 2.1 Components and startup

| Module | Role |
| --- | --- |
| [BCPLMAIN](../../bootstrap-toolchain/asm/bcplmain.asm) | Startup, global import, stack/system vector, STOP/FINISH and cleanup orchestration |
| [BCPLIO](../../bootstrap-toolchain/asm/bcplio.asm) | Character streams and private I/O helpers |
| [BCPLMEM](../../bootstrap-toolchain/asm/bcplmem.asm) | Native vectors and private allocation tracking |
| [BCPLBYTE](../../bootstrap-toolchain/asm/bcplbyte.asm) | GETBYTE/PUTBYTE |
| [BCPLAPT](../../bootstrap-toolchain/asm/bcplapt.asm) | Temporary callback vectors and active limit |
| [BCPLRGS](../../bootstrap-toolchain/asm/bcplrgs.asm) and application BCPLREG | Optional package registration and finalization; exactly one application table, including the empty-table case |
| [BCPLCO](../../bootstrap-toolchain/asm/bcplco-production.asm) | Native coroutine context bridge, with COROUTIN |

BCPLMAIN imports the application and independently compiled BLIB export trailers (relocated address/global byte-offset pairs), installs machine-dependent globals, and uses the G!1 START entry. A declaration or object member alone is not an export. The source tracks actual global ownership for optional registration. Application trailer capacity is G!0–699; the BLIB import has its own restricted offset check. Do not infer a general arbitrary-module import ABI from these two imports.

| Native register | Generated-code role |
| --- | --- |
| R4 | Callee entry/code base; restored from 0(R5) on ordinary BCPL return |
| R5 | Current BCPL workspace/frame byte address |
| R6 | BCPL return linkage |
| R7–R10 | Early arguments; R7 result |
| R11 | System-vector byte base |
| R12 | Global-vector byte base |
| R15 | Incoming/new workspace byte address |

This describes native BCPL linkage, not a universal preservation mask. Private R14-linked interfaces and MVS save-area linkage have separate conventions. See [compiler reference](Reference-for-BCPL-Compilers.md) for generated entry paths.

### 2.2 Selected globals and stack

| Slot | Facility |
| --- | --- |
| G!0 | Global-vector extent metadata |
| G!1 | START |
| G!6 | SAVEAREA, published word pointer with limited tested consumers |
| G!30 | STOP |
| G!40 | APTOVEC, independent BCPLAPT in current production |
| G!52–55 | LOADPOINT, ENDPOINT, STACKBASE, STACKEND |
| G!56 | STACKHWM (BLIB) |
| G!85–88 | GETBYTE, PUTBYTE, GETVEC, FREEVEC |
| G!150 | Provisional DEBUGINT; conflict with historical compiler FORMTREE:150 remains unresolved |

Current BCPLMAIN obtains 68,592 bytes: 700 global words (2,800 bytes), 16,384 usable stack words (65,536 bytes), 256 bytes reserved clearance. STACKBASE and STACKEND publish word addresses of allocated extent; STKLIM is a private safe byte limit, not STACKEND. Initial stack markers support BLIB STACKHWM (bounded evidence only). BCPLMAIN initializes independent BCPLAPT APLIMIT; native coroutine switching updates active limits.

Checked entry at R11+60 consumes inline full-frame size in bytes and checks incoming frame end against STKLIM. Caller workspace advancement is not necessarily the full callee requirement. Invalid frame metadata has a separate exceptional path. R11+20 counting is skip-only; R11+80 combined checked/counting currently skips just one fullword and does not establish the frame or enforce the limit. Do not execute combined checked/counting output against that handler. CO.1 compile-only /CKN and /CPN evidence does not prove runtime operation.

The [v1 contract](../../packaging/architecture/runtime-contract-v1.md) describes M1.9's five-component candidate with internal APTOVEC; [v2](../../packaging/archive/core-runtime/m2-1-runtime-contract-v2.md) applies only to M2.1 D7. The [historical stack checkpoint](../../packaging/architecture/stack-check-contract.md) does not recover the original STKCK body. These profile distinctions are intentional.

## 3. Core Runtime — storage, allocation, vectors, byte access and termination

### 3.1 Native storage and bytes

| Interface | Inputs / result | Ownership and restrictions |
| --- | --- | --- |
| GETVEC(N), G!87 | Last index N; returns word pointer or 0 | N+1 words; source rejects negative or excessive N (upper bound 4,194,299); returned GETMAIN failure gives 0 |
| FREEVEC(V), G!88 | Exact returned word pointer; routine | Unlinks and releases known live allocation. Zero/unknown pointers ignored by native source; not stale-pointer/ABA protection |
| APTOVEC(F,N), G!40 | Calls F(V,N), propagates result | Temporary N+1 words; caller must not retain pointer after return. Current source upper bound 16380 plus active stack/clearance check; invalid/exhausted case enters overflow path |
| GETBYTE(S,I), G!85 | Word pointer S, byte offset I; 0–255 | Native byte address 4*S+I; caller supplies readable extent |
| PUTBYTE(S,I,B), G!86 | Stores low eight bits of B | Caller supplies writable extent; no bounds or character conversion guarantee |

BCPLMEM's current implementation allocates 4(N+1)+12 bytes, with a private descriptor containing returned pointer, allocation length and list link. Memory is not promised zero-initialized. MEMDRAIN and MEMBIND are private startup/cleanup interfaces, not public BCPL calls. MEMBIND publishes the allocation-list head for the limited SAVEAREA/BLIB consumers (G!6!48). MEMSTAT uses R1 pointing to four writable fullwords: current and peak live block counts, current and peak allocated bytes including private headers. It is private R14 linkage, R10 scratch, quiescent singleton only; not total task memory or a BCPL API.

The allocator and streams use static state and are not reentrant. Normal cleanup of outstanding allocations is supported at tested scope; skipped case 083 does not establish measured complete resource reclamation.

### 3.2 Termination

| Current source path | MVS completion / qualification |
| --- | --- |
| FINISH | Normally 0 |
| STOP(N) | Requested N |
| Character-output overflow | STOP(12) |
| Checked-stack or APTOVEC exhaustion | STACK OVERFLOW diagnostic, then FINIMPL; normally 0 in current source/profile |
| Oversize global export / missing START / initial GETMAIN failure | Source paths 16 / 20 / 24 respectively |
| Invalid checked-frame metadata / unexpected START return | Source paths 36; exceptional cleanup differs |

FINEXIT calls selected finalizers before IOFIN and MEMDRAIN; a failed finalizer on FINISH can change status to 8, while explicit STOP status is preserved. Normal release unbinds and frees root storage. Early return and abend paths do not promise normal stream flush, finalizers or explicit cleanup.

**Do not apply D7's RC12 stack-overflow contract to current production.** STKOVFL calls IOREPL with the diagnostic then branches to FINIMPL (which clears STOPRC). Test [52](../../tests/bootstrap/52-controlled-stack-overflow/README.md) and [093](../../tests/bootstrap/093-aptovec-stack-overflow/README.md) preserve different candidate-specific return oracles; the D6-compatible oracle is [0000](../../tests/bootstrap/52-controlled-stack-overflow/expected-go-rc-bcplm6.txt). Output overflow and stack exhaustion are distinct. The historical BLIB ABORT/STOP(100) path is not automatically reproduced. Controlled root-stack overflow evidence does not authorize deliberate worker-overflow or arbitrary abend recovery.

## 4. Core Runtime — character streams, selection, translation, errors and cleanup

Native BCPLIO implements the [dynamic runtime contract](../../packaging/milestones/bcplio-dynamic-stream/BCPLIO-dynamic-runtime-contract.md), originally documented for DEVOBJ(BCPLM6+BCPLIO). The older v1/v2 fixed-DD limitation is not the current dynamic-name implementation. The [JCL/QSAM contract](../../packaging/milestones/bcplio-dynamic-stream/BCPLIO-JCL-QSAM-stream-contract.md) governs the boundary between returned failure and MVS abend.

| Global | Call | Effect |
| --- | --- | --- |
| 11 | SELECTINPUT(H) | Select valid live input; invalid/retired handle leaves selection unchanged |
| 12 | SELECTOUTPUT(H) | Corresponding output selection |
| 13 | RDCH() | Next character, synthesized 10 at record boundary, -1 at EOF |
| 14 | WRCH(CH) | Append to selected output; 10 emits record |
| 15 | UNRDCH() | One-character replay in selected input, including tested EOF |
| 16 | INPUT() | Current input handle |
| 17 | OUTPUT() | Current output handle |
| 33 | WRAPOUTPUT | Provisional historical interface; tested alternate-output flushing, not general QSAM control |
| 39 | FINDPARM() | EXEC PARM-related memory stream, not DD allocation |
| 41 | FINDOUTPUT(NAME) | Live opaque output handle, or 0 on returned-control failure |
| 42 | FINDINPUT(NAME) | Live opaque input handle, or 0 on returned-control failure |
| 46 | ENDREAD() | Close/retire selected input lifetime; no general rewind promise |
| 47 | ENDWRITE() | Flush pending output, close/retire, restore ordinary selection as tested |

NAME is a counted BCPL string of 1–8 valid DD-name characters; lowercase EBCDIC letters normalized to uppercase and names blank-padded for lookup. Reject invalid, empty or overlength names rather than truncate. DD must already be allocated. Built-ins include BCPIN, BCPINB, SYSPRINT and BCPALT. FIND is separate from selection. Repeated FIND of an open normalized DD in the same direction returns the same live handle, without another OPEN; input/output directions are separate. Reopening after close obtains a new lifetime/handle. Treat handles as opaque, not DCB addresses. Dynamic retired handle identities are retained until drain; do not assume unlimited streams. Sixteen concurrently open dynamic inputs were tested (130).

| Direction | Supported contract |
| --- | --- |
| Input | Sequential text-oriented FB80; trim right EBCDIC X'40' padding, synthesize 10, return -1 at EOF |
| Output | Sequential text-oriented FB132; independent pending record per output; 10 emits 132 bytes padded X'40'; blank lines emit blank records |
| Maximum line | 132 characters before newline; 133rd triggers STOP(12) |
| Closure | ENDWRITE and normal FINISH/STOP flush pending data at tested scope |

**DR.5 newline representation discrepancy:** The current BCPLIO contract recognizes numeric 10, and native regression 110/111 uses WRCH(10). The compiler adaptation CODE370 deliberately maps host newline 10 to X'25' (37); JOB 9490 emitted that byte in *N strings. Two native candidates (JOBS 9491/9493) ended with RC=12 after output accounting consistent with 132 accumulated bytes rather than individual physical records. Cambridge JOB 9494 and native JOB 9495 subsequently passed all ten records using explicit WRCH(10); GETBYTE("*N",1) and '*N' both returned 37, confirming the representation mismatch. Historical BLIB WRITES/WRITEF pass literal bytes to WRCH and NEWLINE uses the character literal '*N'. Do not assume embedded *N or NEWLINE() is equivalent to WRCH(10) in the current native environment. Use explicit WRCH(10) for the established record delimiter pending reconciliation; RDCH synthesizes 10 at input record boundaries, so compare it with numeric 10 rather than '*N' in the current native environment. See the [DR.5 candidate evidence](../../packaging/milestones/documentation-refactoring/candidates/language-verification/README.md); no raw record attribution, installed-image identity or production fix is established.

An ordinary stream cannot preserve significant trailing FB80 blanks. No arbitrary binary/VB, PDS traversal, VSAM, dynamic allocation or general DCB validation is promised. DD attributes must be compatible; QSAM/MVS resolves actual effective attributes. BCPLIO's private templates do not explicitly set all RECFM/LRECL/BLKSIZE values.

The dynamic contract records 32-byte descriptors, 268-byte DCB/record regions and 16-byte stable-handle records. These are private implementation details, not a public layout. Closing releases owned descriptor/DCB resources; retired handle records remain until final drain. Invalid/absent names and conditional allocation or recoverable OPEN failure return zero if control returns, preserving selection. Synthetic GETMAIN/DQOPEN tests 134–145 and private accounting establish bounded returned-control recovery, not actual arbitrary SVC19 failure or full MVS storage-exhaustion recovery. Exploratory OPEN jobs did not demonstrate unsuccessful real OPEN. System abends may bypass cleanup.

M5.1/M5.2 evidence distinguishes class-separated physical writer routing, exact sequential dataset FB132 readback, and an intentionally rejected padding-byte mismatch. None is a raw JES2 spool-byte proof. See the original dynamic contract for exact job identities, conditions and preserved negative tests. Use BCPLQSAM for application logical-record I/O, not an undocumented stream-mode switch.

## 5. Base Library (BLIB) — supported formatting, strings, conversions and other routines

The [historical source](../../richards-bcpltape/bcplib/bcpl/blib) and [LIBHDR](../../richards-bcpltape/sys3/bcpl/libhdr) are primary evidence. Native BLIB is independently compiled and its exports imported. The preserved historical assignments are not a blanket support declaration. The following source-observed calls have focused evidence for selected cases; exact argument domains and negative cases remain subject to reconciliation.

| Global | Signature | Behavior |
| --- | --- | --- |
| 60 | WRITES(S) | Write counted string characters using WRCH |
| 62 | WRITEN(N) | Signed decimal via WRITED(N,0) |
| 63 | NEWLINE() | Historical BLIB calls WRCH('*N'); see newline representation qualification in chapter 4 |
| 64 | NEWPAGE() | WRCH page character; no universal MVS page/device behavior established |
| 65 | WRITEO(N) | WRITEOCT(N,11) |
| 66 | PACKSTRING(V,S) | V!0 length (low 8 bits), subsequent words characters; packs into S; native result N/4, in-place V=S tested |
| 67 | UNPACKSTRING(S,V) | Copy length and each character to separate vector words |
| 68 | WRITED(N,D) | Decimal formatting with width |
| 70 | READN() | Historical numeric reader, TERMINATOR G!71; complete lexical/error contract pending |
| 74 | WRITEX(N) | WRITEHEX(N,8) |
| 75 | WRITEHEX(N,D) | Hexadecimal formatting with width |
| 76 | WRITEF(FORMAT,...) | Format and argument cursor; native historical formal parameters A–K after FORMAT |
| 77 | WRITEOCT(N,D) | Octal formatting with width |

Strings are counted, maximum length 255 in historical LIBHDR. Supply sufficient readable/writable storage (including length byte); unpacked vector requires length+1 words. PACKSTRING's native return is last word index, not character count; this differs from a two-byte interpreted packing computation. Do not generalize tested exact in-place operation to arbitrary overlapping buffers.

| WRITEF syntax | Historical native BLIB meaning |
| --- | --- |
| %S | Packed string |
| %C | Character |
| %N | Decimal number, width 0 |
| %I followed by width character | Decimal field |
| %X followed by width character | Hexadecimal field |
| %O followed by width character | Octal field |
| %$ | Advance argument cursor without printing |
| Other conversion | Source default writes conversion character |

Width is one character decoded as digit or alphabetic value (EBCDIC-specific implementation), not an arbitrary decimal width string. Historical WRITEF uses an argument cursor based on @A; do not assume unlimited variadic arguments. Source recognition and individual formatting cases do not establish every width, signed edge case or malformed format. Ordinary format example from native [075](../../tests/bootstrap/075-blib-writef-mixed-object/README.md):

```bcpl
WRITEF("C:%C S:%S N:%N", 'Z', "HI", 42)
```

Expected `C:Z S:HI N:42`. The original failure and later G!76 binding correction are retained; bootstrap WRITEST is fallback only when historical WRITEF is absent. Tests [069](../../tests/bootstrap/069-independent-blib-object/README.md), [070](../../tests/bootstrap/070-blib-unpackstring-object/README.md), [071](../../tests/bootstrap/071-blib-packstring-inplace-object/README.md), [072](../../tests/bootstrap/072-blib-writed-width-object/README.md), [073](../../tests/bootstrap/073-blib-writehex-width-object/README.md), [074](../../tests/bootstrap/074-blib-writeo-object/README.md) and 075–081 give independent-object and calling evidence. Earlier bootstrap formatter cases must not be conflated with the historical BLIB object.

Diagnostic BLIB routines have additional dependencies: STACKHWM G!56 returns a word address or sentinel 0 (overflow) / 1 (unset); test [120](../../tests/bootstrap/120-stackhwm-initialized/README.md) checks a bounded result, not exact peak measurement. INPROGRAM G!58 and VALIDPOINTER G!59 use published extents and selected list metadata; tests 121–123 do not establish arbitrary-address safety. ABORT, ERRORMESSAGE, BACKTRACE, WRITEARG, MAPSTORE and USERPOSTMORTEM have only partially reconstructed support; see chapter 9.

## 6. Coroutine Support Library — creation, activation, transfer, deletion, limits and common behavior

Native [COROUTIN source](../../bootstrap-toolchain/library/coroutines.bcpl), [COHDR declarations](../../bootstrap-toolchain/library/coroutines.h) and [BCPLCO](../../bootstrap-toolchain/asm/bcplco-production.asm) are production source. See [CO.5 promotion](../../packaging/milestones/coroutines/co5-production-promotion-20261115.md), [CO.5 qualified closure](../../packaging/milestones/coroutines/co5-formal-acceptance-and-closure-20261116.md) and [CO.6 common contract](../../packaging/milestones/coroutines/co6-common-coroutine-contract-20261116.md).

| Native global | Call | Bounded behavior / source-visible result |
| --- | --- | --- |
| 289 | CO3INIT() | Initialize root once; returns root or 0 |
| 290 | CREATECO(FN,SIZE) | Root creates worker; SIZE must equal 1024; returns worker or 0 |
| 291 | DELETECO(C) | Root-only deletion of known-live inactive registered worker; TRUE on success, FALSE on rejected lifecycle conditions |
| 292 | CALLCO(C,A) | Set worker parent to caller, transfer A, return value upon resumption; source rejects self/busy with -2 |
| 293 | COWAIT(A) | Clear parent association, yield A to parent; resumed call returns value; source rejects root/no-parent with -3 |
| 294 | RESUMECO(C,A) | Transfer to valid inactive worker with caller's parent; root/no-parent -3, invalid selection/busy -998 within defined source checks |

G!295–297 (CO3CURR, CO3ROOT, CO3LIST) are state; G!298–300 (CO2INIT, CHANGECO, CO3DROP) are machine-dependent bridge entries. Applications must not manipulate their private state or synthesize contexts. Header, IEWL inclusion of BCPLCO/COROUTIN, and native global registration must all agree. Use the accepted installed-only application referenced by CO.5 for a complete example, not MR10's descriptor initialization.

The accepted domain has one root, no more than two live registered workers, fixed independently checked 1024-word worker stacks and known-live lifecycle. Creation primes a valid first-activation frame. A worker may suspend at distinct sites with nested locals retained. Busy-target rejection preserves the original parent. Deletion rejects active or parent-reachable workers, revokes registration before freeing worker stack and descriptor, and allows bounded reuse. The 24-word context representation and larger private lifecycle allocation in source are not a public descriptor size.

Natural return can lead to FN being invoked again on a later call (source-observed CO3BOOT/COBOOT); a dedicated paired natural-return oracle is not claimed here. The common domain is observable application behavior; MR10 and native representations/return codes need not match. No generalized worker count/size, stale/freed/ABA-safe pointers, actual GETMAIN exhaustion, deliberate overflow recovery, cancellation/abend recovery, preemption or reentrancy is promised. In particular, source checks that dereference C assume a valid known-live argument; do not treat a rejection result as general pointer validation.

## 7. MR10 interpreted runtime and libraries — separate ABI, slots and services

MR10 uses ICINT19, BLIBI and ICLIB. Its compiler and application INTCODE use their own global domain and interpreter frame convention. Fullword-backed storage has two packed logical bytes per word, as ICINT19's ICGETBY/ICPUTBY show. Historical kit LIBHDR uses BYTESPERWORD=2; do not copy native four-byte packing formulas into MR10. The current [interpreter source](../../mr10-kit-compiler/asm/icintv19.asm) and [phase inventory](../../mr10-kit-compiler/source/README.md) describe implementation.

| MR10-local slots | Facility |
| --- | --- |
| 6–8 | CHANGECO, CURRCO, COLIST |
| 87–90 | GETVEC, FREEVEC, HEAPINIT, FREEHEAD |
| 91–95 | CREATECO, DELETECO, CALLCO, COWAIT, RESUMECO |
| 96–100 | SRAND, RAND, RANDRANGE, RANDSTATE (private), RANDSEED |
| 101–106 | ABS, MIN, MAX, SIGN, GCD, IPOW |
| 107–111 | STRLEN, STRCMP, STRCPY, STRCAT, STRCHR |
| 112–116 | MEMCPY, MEMSET, MEMCMP, VECCOPY, VECCLEAR |
| 117–120 | ATOI, ITOA, HEXTOI, ITOHEX |
| 121–125 | ISDIGIT, ISALPHA, ISSPACE, TOUPPER, TOLOWER |
| 126–127 | READLINE, WRITELINE |

The [MR10 GLOBALS map](../../mr10-kit-compiler/library/GLOBALS.md) retains local allocation authority subject to the registry. Compile the corresponding module with the application; these routines are not all built into ICLIB. The [library README](../../mr10-kit-compiler/library/README.md) identifies modules and existing contracts: strings require adequate caller storage, MEM sizes are bytes, VEC sizes words, overlapping MEMCPY unsupported; deterministic Park-Miller random is not for security, RANDRANGE(N) gives 0 for N<=0; negative IPOW gives 0; ITOHEX nonnegative; READLINE truncates to supplied limit and returns -1 at end of input. Full individual routine signatures and corner cases remain to be reconciled against source and tests before authority transfer.

[MR10 allocator](../../mr10-kit-compiler/library/getvec-freevec.bcpl) requires HEAPINIT(BASE,WORDS) on an existing arena, GETVEC(N) returns N+1 words or zero; FREEVEC releases owned storage. This is not MVS GETMAIN/FREEMAIN. [MR10 coroutines](../../mr10-kit-compiler/library/coroutines.bcpl) use the allocator, CHANGECO and explicit root setup; source CALLCO busy result -999 differs from native -2. The [generator demonstration](../../mr10-kit-compiler/bcpl-demo/coroutines/coroutines.bcpl) is the applicable complete example. Retain canonical first-activation frame preconditions; the original historical manually constructed fixed-stack fixture still fails with CODE=-1. The supported valid-frame variant and common CO.6 oracles do not erase that failure.

## 8. Optional libraries and extensions — linkage, deferred facilities and user/site libraries

| Facility | Current scope |
| --- | --- |
| BCPLDEMO | G!203 DEMOSVC, supported reference System Extension |
| BCPLTIME | G!201 TIMESVC, accepted native development System Extension |
| BCPLQSAM | G!200 QSAMSVC, accepted qualified native logical-record facility |
| BCPLDEC | G!202 allocated, public dispatcher spelling and implementation not established |
| Native helper source staging | Integer/string/memory candidate modules, not accepted native object packages |
| BCPL Standard Library | Proposed design, not approved API/implementation/release |
| User/Site Libraries | No universal allocated global range or arbitrary-module registration guarantee |

Allocation authority: [Global Number Registry](../../packaging/architecture/global-number-registry.md). Its dated implementation labels are not necessarily current; later [Q.5 closure](../../packaging/milestones/qsam/qsam-q5-closure-20261101.md), [T.1 closure](../../packaging/milestones/bcpltime/bcpltime-t1-closure-20261024.md) and [R.5 closure](../../packaging/milestones/runtime-extensions/runtime-extensions-r5-closure-20261024.md) establish acceptance within their scopes. The native extension BCEX/BCRG registration/finalization contract and package-local APIs belong in the System Extensions reference. Declaration, link selection and registration are distinct; no transitive auto-selection or dynamic loading promise.

The [native library staging README](../../bootstrap-toolchain/library/README.md) lists G101–116 source candidates; their native collision and verification gates are unresolved. Its old coroutine deferral is superseded by the explicit CO.5 entry. Do not use the MR10 allocator as the native G87/G88 provider. See [BSL design](../../packaging/architecture/bsl-scope-and-module-design-20261103.md) for proposed independent-module selection; it does not authorize allocations or imply registration through the System Extension dispatcher mechanism.

## 9. Compatibility, diagnostics, restrictions and verification scope

Historical LIBHDR declares many unimplemented or only partially implemented services. LEVEL G!31, LONGJUMP G!32, general loading/overlays, logging, terminal/block/library/record and FORTRAN interfaces, and automatic ABORT/BACKTRACE/postmortem are not established as a complete native contract. Historical DATE in the compiler bootstrap is a separate host accommodation; BCPLTIME does not automatically implement G!29. G!94 historically duplicates OPENBLOCKFILE and UPDATEBLOCKFILE: preserve that evidence without silently renumbering.

DEBUGINT G!150 is a provisional project diagnostic, not a historical BLIB API or an available compiler slot. Historical FORMTREE also uses 150; no resolution or native-running compiler compatibility is claimed. FIRSTFREEGLOBAL=150 is not a current vacancy guarantee. MAPSTORE, USERPOSTMORTEM, STACKHWM and VALIDPOINTER are not automatic exhaustive telemetry or fault interception. Native assembler services and private diagnostic counters are not BCPL globals unless explicitly installed.

| Evidence | Scope |
| --- | --- |
| M1.8/v1 and M2.1 D7/v2 | Earlier candidate panels 123 PASS, expected skip 083; profile-specific APTOVEC/stream/overflow behavior |
| M4.4/M5 dynamic streams | 145 PASS plus expected skip; returned-control recovery, separate record byte and printer routing evidence |
| CO.5 | Ten-member production BOOT_OBJ reconstruction, installed-only coroutine IFOX/IEWL/GO and 21-record oracle; 201 supported post-rebuild passes, skip 083 |
| CO.6 | 208 supported passes, expected skip 083; two paired coroutine oracles; original historical MR10 failure separately retained |
| RC4 | 80/80 MR10/COMBINED functional cases; native installation/inventory only |

MVS RC alone is not proof of semantic success: compare interpreted CODE and exact application records where applicable, verify native compiler/IFOX/IEWL/GO individually, and respect profile-specific negative oracles. CO.5 Bootstrap 117's earlier IEWL SB2D remains a genuine incident despite later successful reruns. No complete historical source/binary compatibility or all-exception recovery follows from passing finite panels.

This reference retains the original [v1](../../packaging/architecture/runtime-contract-v1.md), [D7 v2](../../packaging/archive/core-runtime/m2-1-runtime-contract-v2.md), [dynamic stream contract](../../packaging/milestones/bcplio-dynamic-stream/BCPLIO-dynamic-runtime-contract.md) and [CO.6 contract](../../packaging/milestones/coroutines/co6-common-coroutine-contract-20261116.md) authorities and evidence. See the [migration ledger](../../packaging/milestones/documentation-refactoring/dr2-runtime-library-manual-migration-20261125.md) for outstanding reconciliation. No new MVS execution is claimed by this drafting increment.
