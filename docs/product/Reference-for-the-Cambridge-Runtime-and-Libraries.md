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

GETVEC uses conditional GETMAIN and links only successful allocations; FREEVEC searches the live list before dereferencing allocation metadata, unlinks and frees with the recorded length. These are source-observed protections, not a guarantee of arbitrary pointer safety or recovery from an MVS abend. BCPLBYTE uses R7 pointer/result, R8 byte offset, R9 store value; the source uses R14 as scratch and restores R4 from the current frame. No bounds checking is performed. The allocator and streams use static state and are not reentrant. Normal cleanup of outstanding allocations is supported at tested scope; skipped case 083 does not establish measured complete resource reclamation.

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
| 11 | SELECTINPUT(H) | Select a live input or PARM handle; invalid, wrong-direction or closed QSAM handles leave selection unchanged |
| 12 | SELECTOUTPUT(H) | Select a live output handle; invalid, wrong-direction or closed handles leave selection unchanged |
| 13 | RDCH() | Next character, synthesized 10 at record boundary, -1 at EOF |
| 14 | WRCH(CH) | Append to selected output; 10 emits record |
| 15 | UNRDCH() | One-character replay in selected input, including tested EOF |
| 16 | INPUT() | Current input handle |
| 17 | OUTPUT() | Current output handle |
| 33 | WRAPOUTPUT() | Provisional; flush selected open built-in BCPALT even if empty; no effect on primary or dynamic output |
| 39 | FINDPARM() | Dedicated EXEC PARM memory stream, not DD allocation |
| 41 | FINDOUTPUT(NAME) | Live opaque output handle, or 0 on returned-control failure |
| 42 | FINDINPUT(NAME) | Live opaque input handle, or 0 on returned-control failure |
| 46 | ENDREAD() | Close selected QSAM input, clear selection; retire dynamic handle or reset PARM cursor |
| 47 | ENDWRITE() | Flush/close selected nonprimary output, restore SYSPRINT; no-op for primary |

### 4.1 Discovery, selection and lifetime

The corrected built-in and dynamic name paths accept a readable counted string of 1–8 characters: EBCDIC alphabetic or @/#/$ initially, and digits also after the first character. IONORM uppercases lowercase EBCDIC and blank-pads the name to eight bytes; invalid/empty/overlength names are rejected without truncation. FIND does not dynamically allocate a DD and does not change selection. The dynamic lookup key is normalized name plus direction. An existing live dynamic handle is returned before RDJFCB or another OPEN; close/reopen produces a new handle, with retired identities retained until final drain. Cases 127, 131, 132 and 134 establish this for dynamic DDs. Sixteen concurrent dynamic inputs were tested (130). Do not assume unlimited resources.

Normalization precedes built-in dispatch. Case-equivalent names identify the same built-in within its direction; the legacy built-in paths still differ from the dynamic path in lifetime and OPEN handling:

| Name or facility | Actual source behavior and use |
| --- | --- |
| SYSPRINT | Opened by IOINIT; ordinary selected output; fixed handle; IOFIN owns final flush/CLOSE |
| BCPALT | Opened lazily by normalized FINDOUTPUT; fixed handle; ENDWRITE flushes nonempty data, closes and selects SYSPRINT |
| BCPIN, BCPINB | Opened lazily by normalized FINDINPUT; fixed independent input handles/cursors; ENDREAD closes and clears selection |
| FINDPARM() | Fixed memory-stream handle; capture original EXEC PARM address, clamp length to 100 bytes, deliver bytes without right trimming, one logical newline and then EOF; ENDREAD resets cursor and clears selection |

The FINDPARM details beyond case 108's first-character probe are source-observed. The fixed handle is not a dynamically allocated stable identity. Reopening a built-in reuses its fixed handle; a closed built-in QSAM input or output cannot be selected until reopened. Do not use a saved handle as proof of a distinct open lifetime, or assume a general rewind capability. The input selection starts at zero; RDCH with no selection returns -1. ENDREAD does not automatically select another input. Output selection persists until explicitly changed or a nonprimary ENDWRITE restores primary.

**DR.5 BCPLIO correction — verified:** Source revision `a0efe9a204e1f3f3968b60cb8c7065e9b423bce7` normalizes names before fixed-name dispatch, guards built-in QSAM input open state and dynamic output direction/open state, and defensively checks dynamic output write/close paths. Private candidate JOB 363, BLDIOFIX JOB 366 (including installed-object IEBCOMPR) and permanent Bootstrap case 193 passed. The full supported production campaign reported 212 PASS and one expected SKIP (083). Case 193 verifies mixed-case built-in identity and input cursor preservation, wrong-direction selection rejection, closed built-in input rejection and normal output/close behavior. It deliberately avoids actual wrong-mode I/O or GET on a closed DCB; the private defensive guards are source-observed rather than separately fault-injected. Fixed-handle identity reuse and the PARM reset behavior remain unchanged. Older uncorrected objects, including those distributed before the correction, do not acquire these guarantees automatically. The [migration ledger](../../packaging/milestones/documentation-refactoring/dr2-runtime-library-manual-migration-20261125.md) retains the original discrepancies and exact evidence.

### 4.2 Record and replay semantics

| Direction | Supported contract |
| --- | --- |
| Input | Sequential text-oriented FB80; trim right EBCDIC X'40' padding, synthesize 10, return -1 at EOF |
| Output | Sequential text-oriented FB132; independent pending record per output; 10 emits 132 bytes padded X'40'; blank lines emit blank records |
| Maximum line | 132 characters before newline; 133rd triggers STOP(12) |
| Closure | Nonprimary ENDWRITE and normal FINISH/STOP flush pending nonempty data at tested scope; no extra empty record on close |

The native replay implementation has an independent last-value, seen and pending flag for each input. UNRDCH schedules one repeat of the last RDCH result (including newline or EOF), not a multi-character stack or physical rewind. The source does nothing before a value has been seen on that input; repeated requests before another RDCH set the same pending flag. This is distinct from the compiler-host UNRDCH wrapper introduced in DR.5. Cases 097 and 099 verify built-in character/newline/EOF replay; dynamic input uses equivalent private state. Output newline compares the complete argument word with 10; ordinary bytes use the low eight bits. No automatic continuation or general character-code translation is performed.

**DR.5 logical newline correction:** The accepted BCPLIO delimiter remains 10. Older CAMBCOMP emitted X'25' (37) for *N; JOBS 9491/9493 failed with RC=12, and JOB 9495 verified 37 and passed with explicit WRCH(10). Owner-approved CODE370 correction at `828cf88dcd080868d7f126267f3650613571951d` preserves logical 10. CAMBCOMP/BLIB rebuilds (9498/9500) and JOBS 9502/9504 verified the correction. In the rebuilt development environment, *N, WRCH(10), BLIB NEWLINE() and RDCH synthetic boundaries agree. JOB 9504 independently compared all six FB132 sequential-dataset records including padding and EOF; EBCDIC A=193 also passed. Older objects require regeneration. The subsequent eight-suite supported regression campaign passed 208 cases, with one expected SKIP (083), zero failures and zero blocked cases. Neither campaign establishes raw JES spool-byte fidelity. See the [DR.5 candidate evidence](../../packaging/milestones/documentation-refactoring/candidates/language-verification/README.md).

An ordinary stream cannot preserve significant trailing FB80 blanks. No arbitrary binary/VB, PDS traversal, VSAM, dynamic allocation or general DCB validation is promised. DD attributes must be compatible; QSAM/MVS resolves actual effective attributes. BCPLIO's private templates do not explicitly set all RECFM/LRECL/BLKSIZE values.

### 4.3 Ownership, errors and evidence

For dynamic names the source sequence is normalize, live-handle lookup, RDJFCB allocation inquiry, allocate descriptor and DCB/buffer, OPEN, allocate stable handle. Descriptor (32 bytes), DCB/buffer region (268 bytes) and handle record (16 bytes) are private implementation details, not public layout. A failed second allocation frees the first; a returned OPEN failure releases the unopened descriptor; a handle allocation failure after successful OPEN takes CLOSE then release. Normal close retires the handle before freeing the descriptor; IOFIN/IODRAIN frees both live and retired handle records at termination.

Invalid/absent dynamic names, conditional allocation failure and detected recoverable OPEN failure return zero if control returns, preserving selection. The normalized built-in shortcuts use their own OPEN paths without the dynamic RDJFCB/conditional-failure sequence; do not assume the dynamic zero-return contract for a missing built-in allocation. The source checks a field at DCB+48 after SVC19 in DQOPEN; this is not independently verified as a universal OPEN-success oracle. Synthetic GETMAIN/DQOPEN tests 134–145 and private accounting establish bounded returned-control recovery, not actual arbitrary SVC19 failure or full MVS storage-exhaustion recovery. Exploratory jobs 7874–7876 did not demonstrate unsuccessful real OPEN. No general public GET/PUT/CLOSE error-status or recovery API is supplied; system abends may bypass cleanup. Test-only resource counters are not installed BCPL globals and do not establish independent physical storage accounting.

M5.1/M5.2 evidence distinguishes class-separated physical writer routing (8184), exact sequential dataset FB132 readback (8185) and the intentional verifier RC12 for a wrong 132nd padding byte (8186). None is raw JES2 spool-byte proof. [M5.5 final acceptance](../../packaging/milestones/bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream-final-acceptance.md) records 145 PASS plus expected SKIP 083 under DEVOBJ; the earlier DR.5 production campaign reported 211 PASS plus expected SKIP. The post-BCPLIO-correction DR.5 campaign reported 212 PASS plus expected SKIP, with case 193 passing. The earlier runs remain historical evidence. The [fixed-DD predecessor](../../packaging/archive/core-runtime/regression/native-stream-contract.md) preserves the earlier built-in behavior. The existing contracts remain operative pending reconciliation and explicit owner-approved transfer. Use BCPLQSAM for application logical-record I/O, not an undocumented stream-mode switch.

## 5. Base Library (BLIB) — supported formatting, strings, conversions and other routines

The [historical source](../../richards-bcpltape/bcplib/bcpl/blib) and [LIBHDR](../../richards-bcpltape/sys3/bcpl/libhdr) are primary evidence. Native BLIB is independently compiled and its exports imported. The preserved historical assignments are not a blanket support declaration. At DR.5, matching the 22 top-level BLIB definitions to LIBHDR identifies 21 global-numbered procedure candidates: the 13 ordinary routines below and eight diagnostic routines (G!3 ABORT, G!4 BACKTRACE, G!5 ERRORMESSAGE, G!56 STACKHWM, G!58 INPROGRAM, G!59 VALIDPOINTER, G!69 WRITEARG, G!78 MAPSTORE). PRINTWIDTH is an unnumbered helper; G!71 TERMINATOR is data, not a procedure, and G!79 USERPOSTMORTEM is a referenced hook, not a BLIB definition. The [generator](../../bootstrap-toolchain/bootstrap-cambridge/make-demoted.py) removes SECTION and rewrites two inequality tokens; [BLIBBLD](../../bootstrap-toolchain/jcl/blibbld.jcl) compiles and prepares the separate native object. The [historical R.0 JOB 2197 census](../../packaging/archive/runtime-extensions/runtime-extensions-r0-trailer-job-2197-evidence-20261021.md) independently observed exactly these 21 procedure slots in the then-installed BLIB, with neither G!71 nor G!79 among its exports. This is not a census of the subsequently rebuilt resident object; DR.5 prepares a fresh read-only check. The following calls have focused evidence for selected cases; other details are source-observed.

| Global | Signature | Behavior |
| --- | --- | --- |
| 60 | WRITES(S) | Write counted string characters using WRCH |
| 62 | WRITEN(N) | Signed decimal via WRITED(N,0) |
| 63 | NEWLINE() | Historical BLIB calls WRCH('*N'); rebuilt BLIB emits a record using logical 10 (JOB 9504; chapter 4) |
| 64 | NEWPAGE() | WRCH page character; no universal MVS page/device behavior established |
| 65 | WRITEO(N) | WRITEOCT(N,11) |
| 66 | PACKSTRING(V,S) | V!0 length (low 8 bits), subsequent words characters; packs into S; native result N/4, in-place V=S tested |
| 67 | UNPACKSTRING(S,V) | Copy length and each character to separate vector words |
| 68 | WRITED(N,D) | Decimal formatting with width |
| 70 | READN() | Read optional sign and decimal digit sequence; consumed terminator in G!71 (see below) |
| 74 | WRITEX(N) | WRITEHEX(N,8) |
| 75 | WRITEHEX(N,D) | Hexadecimal formatting with width |
| 76 | WRITEF(FORMAT,...) | Format and argument cursor; native historical formal parameters A–K after FORMAT |
| 77 | WRITEOCT(N,D) | Octal formatting with width |

Strings are counted, maximum length 255 in historical LIBHDR. Supply sufficient readable/writable storage (including length byte); unpacked vector requires length+1 words. PACKSTRING masks V!0 to eight bits, clears the final packed word and returns N/4 (integer division), the last word index, not character count. Its explicit saved-word handling supports exact V=S; case 071 verifies five characters in place. Do not generalize to arbitrary overlapping buffers. UNPACKSTRING copies byte zero as well as characters.

READN skips leading '*S', '*T' and '*N', accepts one optional sign, and accumulates consecutive decimal digits. The first character outside the digit range is consumed and left in G!71 TERMINATOR, including EOF (-1). With no digits, the source returns zero, so zero is not a reliable parse-success indicator. Whitespace after the sign is not skipped again; no explicit numeric overflow check or automatic unread is implemented. The [DR.5 native READN candidate](../../packaging/milestones/documentation-refactoring/candidates/readn-verification/README.md) passed all twelve exact value/terminator assertions using installed BLIB (compiler JOB 1301, native JOB 1302). This verifies leading blanks and logical newline, both signs, zero, nondigits, consumed punctuation, sign without digits, blank after sign and repeated EOF at the fixture scope. Tab input, overflow and complete installed export-trailer identity remain unverified. The compiler-host option tests exercise a separate interpreted reader and must not be used as native G!70 proof.

WRITED pads on the left with spaces to a minimum width including any minus sign; it never intentionally truncates a longer decimal representation. WRITEHEX and WRITEOCT emit the requested number of digit positions, with leading zeroes where needed within the ordinary supported widths. WRITEX fixes width 8, WRITEO width 11. Arbitrary widths, signed shift edge cases and full-range decimal behavior are not independently certified.

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

Width is one character decoded as digit or alphabetic value (EBCDIC-specific implementation), not an arbitrary decimal width string. The source folds the type with X'40' before dispatch; an unknown type emits the original character without advancing the argument cursor. Historical WRITEF uses an argument cursor based on @A and declares eleven argument words after FORMAT. It does not check the number supplied or guard a dangling percent or missing width byte. Use complete formats and enough arguments; do not assume unlimited variadic arguments. Source recognition and individual formatting cases do not establish every width, signed edge case or malformed format. Ordinary format example from native [075](../../tests/bootstrap/075-blib-writef-mixed-object/README.md):

```bcpl
WRITEF("C:%C S:%S N:%N", 'Z', "HI", 42)
```

Expected `C:Z S:HI N:42`. The original failure and later G!76 binding correction are retained; bootstrap WRITEST is fallback only when historical WRITEF is absent. Tests [069](../../tests/bootstrap/069-independent-blib-object/README.md), [070](../../tests/bootstrap/070-blib-unpackstring-object/README.md), [071](../../tests/bootstrap/071-blib-packstring-inplace-object/README.md), [072](../../tests/bootstrap/072-blib-writed-width-object/README.md), [073](../../tests/bootstrap/073-blib-writehex-width-object/README.md), [074](../../tests/bootstrap/074-blib-writeo-object/README.md) and 075–081 give independent-object and calling evidence. Earlier bootstrap formatter cases must not be conflated with the historical BLIB object.

Diagnostic BLIB routines have additional dependencies (historical ABORT and ERRORMESSAGE reference FINDLOG/WRITETOLOG; BACKTRACE references LEVEL, and ABORT may invoke USERPOSTMORTEM): STACKHWM G!56 returns a word address or sentinel 0 (overflow) / 1 (unset); test [120](../../tests/bootstrap/120-stackhwm-initialized/README.md) checks a bounded result, not exact peak measurement. INPROGRAM G!58 and VALIDPOINTER G!59 use published extents and selected list metadata; tests 121–123 do not establish arbitrary-address safety. ABORT, ERRORMESSAGE, BACKTRACE, WRITEARG, MAPSTORE and USERPOSTMORTEM have only partially reconstructed support; see chapter 9.

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

The [MR10 GLOBALS map](../../mr10-kit-compiler/library/GLOBALS.md) retains local allocation authority subject to the registry. Compile the corresponding module with the application; these routines are not all built into ICLIB. The following signatures and restrictions are source-observed in the [library modules](../../mr10-kit-compiler/library/README.md), with ordinary-domain evidence from the MR10 Regression Panel (library-scalars, library-strings and library-line-io). They are not native BLIB contracts.

| Module | Calls and results | Caller obligations and boundaries |
| --- | --- | --- |
| [random](../../mr10-kit-compiler/library/random.bcpl) | SRAND(N), RANDSEED(N) seed; RAND() next value; RANDRANGE(N) returns remainder or 0 for N<=0 | Seed before use; deterministic Park-Miller state, not security randomness; no unbiased-range guarantee |
| [integer-utils](../../mr10-kit-compiler/library/integer-utils.bcpl) | ABS(N), MIN(A,B), MAX(A,B), SIGN(N) (-1/0/1), GCD(A,B), IPOW(BASE,EXP) | Negative exponent returns 0; exponent 0 returns 1; no explicit overflow handling or minimum-signed-integer guarantee |
| [char-utils](../../mr10-kit-compiler/library/char-utils.bcpl) | ISDIGIT(CH), ISALPHA(CH), ISSPACE(CH), TOUPPER(CH), TOLOWER(CH) | ASCII character ranges; ISSPACE recognizes space/tab/newline; not native EBCDIC classification |
| [string-utils](../../mr10-kit-compiler/library/string-utils.bcpl) | STRLEN(S); STRCMP(A,B) (-1/0/1); STRCPY(DST,SRC), STRCAT(DST,SRC) return DST; STRCHR(S,CH) returns first one-based index or 0 | Counted strings, sufficient destination; concatenated length must fit one byte (255), no overlap or overflow checks |
| [memory-utils](../../mr10-kit-compiler/library/memory-utils.bcpl) | MEMCPY(DST,SRC,N), MEMSET(DST,VALUE,N), MEMCMP(A,B,N); VECCOPY(DST,SRC,N), VECCLEAR(V,N) | MEM sizes bytes, VEC sizes words; copies/fills return destination, comparison -1/0/1; nonpositive count performs no element access; forward copies are not overlap-safe |
| [numeric-conversion](../../mr10-kit-compiler/library/numeric-conversion.bcpl) | ATOI(S), HEXTOI(S); ITOA(N,S), ITOHEX(N,S) return S on supported input | Parse digit prefix without a separate error indicator; no overflow detection. ITOHEX rejects negative input with 0; minimum signed input to ITOA not established; caller supplies storage |
| [line-io](../../mr10-kit-compiler/library/line-io.bcpl) | READLINE(S,MAX) returns stored length or -1 on immediate EOF; WRITELINE(S) emits string and newline | MAX is character capacity excluding length byte; keep 0–255 and supply storage. Negative MAX becomes zero; excess input is consumed through newline or EOF; partial final line returned before EOF |

These source-level limits are not exhaustive negative tests. In particular, string/line length overflow, arbitrary overlap and numeric overflow must not be advertised as safe.

[MR10 allocator](../../mr10-kit-compiler/library/getvec-freevec.bcpl) requires HEAPINIT(BASE,WORDS) on an existing arena of at least three words; it resets FREEHEAD and must not be used to reinitialize an arena with live allocations. GETVEC(N) returns a pointer to at least N+1 payload words or zero, using first fit, a two-word private header and splitting only when at least three words remain. FREEVEC(0) is a no-op; nonzero V must be an exact live allocation pointer. The source reinserts by address and coalesces adjacent blocks without native-style live-list validation. Do not pass foreign, stale or duplicate pointers. No explicit arithmetic overflow check for N+3 is provided. This is not MVS GETMAIN/FREEMAIN. [MR10 coroutines](../../mr10-kit-compiler/library/coroutines.bcpl) use the allocator, CHANGECO and explicit root setup; source CALLCO busy result -999 differs from native -2. The [generator demonstration](../../mr10-kit-compiler/bcpl-demo/coroutines/coroutines.bcpl) is the applicable complete example. Retain canonical first-activation frame preconditions; the original historical manually constructed fixed-stack fixture still fails with CODE=-1. The supported valid-frame variant and common CO.6 oracles do not erase that failure.

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
| DR.5 compiler corrections | [211 supported passes](../../packaging/milestones/documentation-refactoring/candidates/compiler-verification/README.md), expected SKIP 083; corrected compiler host and native newline behavior |
| DR.5 BCPLIO correction | [212 supported passes](../../packaging/milestones/documentation-refactoring/dr2-runtime-library-manual-migration-20261125.md), expected SKIP 083; installed BCPLIO and stream guards verified, not an exhaustive runtime or library boundary matrix |
| RC4 | 80/80 MR10/COMBINED functional cases; native installation/inventory only |

MVS RC alone is not proof of semantic success: compare interpreted CODE and exact application records where applicable, verify native compiler/IFOX/IEWL/GO individually, and respect profile-specific negative oracles. CO.5 Bootstrap 117's earlier IEWL SB2D remains a genuine incident despite later successful reruns. No complete historical source/binary compatibility or all-exception recovery follows from passing finite panels.

This reference retains the original [v1](../../packaging/architecture/runtime-contract-v1.md), [D7 v2](../../packaging/archive/core-runtime/m2-1-runtime-contract-v2.md), [dynamic stream contract](../../packaging/milestones/bcplio-dynamic-stream/BCPLIO-dynamic-runtime-contract.md) and [CO.6 contract](../../packaging/milestones/coroutines/co6-common-coroutine-contract-20261116.md) authorities and evidence. See the [migration ledger](../../packaging/milestones/documentation-refactoring/dr2-runtime-library-manual-migration-20261125.md) for outstanding reconciliation. No new MVS execution is claimed by this drafting increment.
