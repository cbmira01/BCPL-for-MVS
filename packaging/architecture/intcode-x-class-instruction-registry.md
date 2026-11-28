# INTCODE X-class Instruction Registry

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Cambridge Compiler Bootstrap Restoration  
**March:** CBR.0 — Architecture and Dependency Reconciliation  
**Date:** 28 November 2026 EST  
**Review baseline:** `12336b3d9802dacd8416b08190ad9d6d6c0e078f`  
**Status:** Owner-approved governing registry, 28 November 2026 EST. Existing assignments are recorded, not newly allocated. No additional assignment is made by this record.

## 1. Scope and authority

The X-class is INTCODE machine function 7 (execute operation). Its effective operand D selects an operation. X-class instruction numbers are independent of BCPL GLOBAL numbers, OCODE operators, System/370 opcodes and BCEX/BCRG package-local opcodes.

The historical basic machine defines X1–X23. The historical interpreter appendix and hand-written ICLIB define the existing implementation-dependent X24–X37. The registry preserves these meanings for the project; ICINT19 remains the independent accepted interpreter baseline. ICINT20 may change implementation details needed for its word representation and host interfaces without repurposing these assignments. Behavior changes must be documented and verified, not inferred from an allocation.

Authoritative source references (relative to the repository location `packaging/architecture/intcode-x-class-instruction-registry.md`):

- [Historical INTCODE specification and interpreter appendix](../../richards-bcpltape/mr10/text/intcode).
- [Historical bootstrap design](../../richards-bcpltape/mr10/text/bstrbcpl).
- [ICINT19 assembler](../../mr10-kit-compiler/asm/icintv19.asm), especially OP7, X1–X37, ICGETBY, ICPUTBY and INTERROR.
- [Canonical hand-written ICLIB](../../mr10-kit-compiler/source/iclib.int).
- [Global Number Registry](global-number-registry.md).
- [Approved CBR design discussion](cambridge-compiler-bootstrap-restoration-design-discussion-20261128.md), decisions 9–11.
- [Governing CBR milestone](../milestones/cambridge-compiler-bootstrap-restoration/milestone-cambridge-compiler-bootstrap-restoration.md).

## 2. Basic machine instructions — historical, retained

A and B are the interpreted accumulators; P is the interpreted frame pointer; C is the interpreted sequence control register; D is the effective instruction operand. `M[n]` denotes the interpreted word at address n. Unless explicitly described otherwise, the interpreter resumes instruction fetch. The table identifies operation semantics, not every exceptional case or internal register side effect.

| X-class | Operation | Effect |
| --- | --- | --- |
| X1 | Indirect load | A := M[A] |
| X2 | Negate | A := −A |
| X3 | Complement | A := bitwise NOT A |
| X4 | Return | C := M[P+1]; P := M[P]; A retains the function result |
| X5 | Multiply | A := B × A |
| X6 | Divide | A := B / A (integer quotient) |
| X7 | Remainder | A := B REM A |
| X8 | Add | A := B + A |
| X9 | Subtract | A := B − A |
| X10 | Equal | A := B = A |
| X11 | Not equal | A := B not equal to A |
| X12 | Less than | A := B < A |
| X13 | Greater than or equal | A := B >= A |
| X14 | Greater than | A := B > A |
| X15 | Less than or equal | A := B <= A |
| X16 | Left shift | A := B LSHIFT A; zero-filled |
| X17 | Right shift | A := B RSHIFT A; zero-filled |
| X18 | Logical AND | A := B LOGAND A |
| X19 | Logical OR | A := B LOGOR A |
| X20 | Not equivalent | A := B NEQV A (exclusive OR) |
| X21 | Equivalent | A := B EQV A (complement of exclusive OR) |
| X22 | Finish | Terminate interpreted execution with result zero |
| X23 | SWITCHON | Select C from the switch table beginning at C, using A as selector; default target if no match |

ICINT19 comparison operations return −1 for true and 0 for false. The X23 table layout is count, default target, then case-value/target pairs. Numeric overflow, division exceptions, shift-count boundaries, malformed tables and invalid addresses require separate behavioral verification; the registry does not certify them.

## 3. Existing implementation-dependent instructions — historical, retained

These assignments are used by hand-written ICLIB. The documented inputs refer to interpreted registers and stack cells, not host System/370 registers. A dash in the result column means no BCPL value is specified by this registry, not a preservation promise for every register. Wrappers may perform X4 after the service; operations that replace P/C or terminate execution have their own control transfer.

| X-class | ICLIB service | BCPL GLOBAL (MR10 ICLIB) | Input | Result / effect |
| --- | --- | ---: | --- | --- |
| X24 | SELECTINPUT | 11 | A = stream | Select current input |
| X25 | SELECTOUTPUT | 12 | A = stream | Select current output |
| X26 | RDCH | 13 | Current input | A = translated ASCII character, or −1 at end of stream |
| X27 | WRCH | 14 | A = character | Translate ASCII to host text encoding and write to selected output |
| X28 | FINDINPUT | 42 | A = interpreted counted string address | A = host input stream handle or failure result |
| X29 | FINDOUTPUT | 41 | A = interpreted counted string address | A = host output stream handle or failure result |
| X30 | STOP | 30 | A = interpreted stop value | Terminate interpreted execution with A as result |
| X31 | LEVEL | 31 | P = current ICLIB call frame | A = M[P] (caller frame pointer) |
| X32 | LONGJUMP | 32 | A = target P; B = target C | P := A; C := B; resume fetch at target |
| X33 | ENDREAD | 46 | Current input | Close selected input |
| X34 | ENDWRITE | 47 | Current output | Close selected output |
| X35 | APTOVEC | 40 | A = procedure entry; B = vector upper bound | Construct new frame at D := P+B+1; M[D..D+3] := M[P], M[P+1], P, B; P := D; C := A |
| X36 | GETBYTE | 85 | A = word address; B = byte index | A = unsigned byte |
| X37 | PUTBYTE | 86 | A = word address; B = byte index; M[P+4] = byte | Store byte at indexed location |

The operand ordering follows actual ICLIB: `LIP3 LIP2` sets B from the second BCPL argument and A from the first. X37 obtains its third argument from M[P+4]. X35 and X32 do not have a trailing X4 in the canonical wrappers. The canonical CHANGECO global 6 wrapper also uses X32; it does not have its own X-class assignment. The experimental `ICLIBC` candidate changes coroutine frame handling without introducing an X-class number; it is not the canonical ICLIB.

### ICINT19 representation and behavior qualifications

- X36/X37 address two interpreted bytes per fullword-backed word; the byte offset uses index/2, with bytes in the low halfword. X-class numbers do not prescribe the underlying packing. ICINT20's four-byte packing, including assembler C directives, string conversion and all affected library routines, must be verified together.
- X26/X27 and X28/X29 currently perform character encoding conversion at the host interface. ICINT20 must preserve ASCII internal text and distinguish raw binary operations from these text services.
- X30 propagates the interpreted result to the interpreter's return path. ICINT19's outer MVS main routine currently returns RC=0; do not interpret X30 as a guarantee that the MVS step RC equals A.
- X32/X35 are control-transfer mechanisms; their allocation does not imply that all stack, coroutine, bounds or exceptional behavior has been verified.
- X0 and every number greater than 37 fall through OP7 to INTERROR in ICINT19, which records diagnostics and exits interpreted execution with −1. This is not a claim of a nonzero JES step RC.

## 4. Unallocated instructions and CBR.3 candidates

| Number | Status | Proposed use / qualification |
| --- | --- | --- |
| X0 | Unsupported in ICINT19; no assignment | Do not allocate casually or treat as a no-op |
| X38 | Unassigned; provisional candidate only | Historical READREC (GLOBAL 23), subject to interface and allocation approval |
| X39 | Unassigned; provisional candidate only | Historical WRITEREC (GLOBAL 24), subject to interface and allocation approval |
| X40 and above | Unassigned in inspected dispatchers | No advance reservation or blanket availability guarantee |

No instruction is allocated by this table. The order X38 READREC / X39 WRITEREC is a proposal, not an approved ABI. Their argument and result conventions are not defined by this record. CBR.3 must reconcile historical contracts, actual compiler callers, stream state, logical-record length, EOF and errors before approval. The historical CGD WRCARD calls `WRITEREC(V,80)` for the object-deck output stream; that establishes a real caller, not a complete READREC/WRITEREC specification. Preserve historical BCPL globals 23 and 24 independently of opcode selection. These services are not aliases for the optional BCPLQSAM dispatcher and must not require its registration.

## 5. Allocation and implementation control — approved governing rules

1. Retain the historical meanings of X1–X37. Never repurpose an assigned operation or silently alter its ABI. Preserve ICINT19, original kit decks and canonical MR10 ICLIB.
2. Introduce an implementation-dependent operation only for a demonstrated machine or host service that cannot reasonably be supplied in ordinary BCPL. Prefer a maintained BCPL library when practical. Do not preallocate floating-point or other speculative services.
3. Before assigning a number, inspect this registry, historical and active interpreter dispatchers, hand-written INTCODE, relevant generated decks, compiler emission paths and tests. Record exact evidence scope and unresolved limitations. An unsupported number in one version is not alone evidence of availability everywhere.
4. Document owner/service, proposed number, applicable interpreter versions, interpreted A/B/P/C and stack operands, units, return value, changes to registers/stream state, error and termination behavior, encoding/packing, BCPL wrapper and GLOBAL linkage, source paths, compatibility impact and independent test oracle. Obtain owner approval of the number and contract before implementation; record the decision here and any linked Global Number Registry update.
5. Distinguish assigned, implemented, independently verified, and promoted status. An allocation is not acceptance of code; keep evidence linked by source revision. Check IFOX and IEWL, actual JES/interpreter results and independent semantic oracles as applicable. Explicitly verify unsupported-operation rejection at the accepted scope.
6. Use separately named ICINT20 candidates and corresponding ICLIB/BLIBI until promotion is separately authorized. Verify preserved X1–X37 behavior, changed representation-dependent services, and unaffected MR10/ICINT19 baselines. Record any retired instruction as a tombstone; require an explicit compatibility decision for reuse.

## 6. Reconciliation evidence and limits

Read-only inspection at the review baseline:

- Historical INTCODE description and appendix: basic X1–X23 and implementation-dependent X24–X37 agree with the current operation names and wrappers.
- ICINT19 OP7: all 37 entries confirmed, with corresponding handler inspection; no dispatch above X37.
- Retained assembler variants `icintv12.asm` through `icintv19.asm` and `icintv14-trace.asm`: direct `BE Xn` dispatch scan found X1–X37 in each, with no higher direct branch target. This is a dispatch-shape scan, not a semantic audit of all historical variants.
- Canonical `iclib.int` and experimental `iclib-co0-candidate.int`: inspected in full; no new instruction allocation.
- `syni.int`, `trni.int`, `cgi.int` and `blibi.int`: scan for whitespace-delimited direct Xn tokens found none greater than 37. Compact/modified forms, all archive fragments, all application decks and computed operation values were not exhaustively scanned. Before new allocation, a whole-tree and generated-deck search remains required. No claim of complete repository-wide vacancy.
- No MVS job, compiler invocation, assembly, link-edit, live regression or installation was performed for this registry. Existing acceptance evidence is preserved at its original scope. No code, global allocation, interpreter implementation or march status is changed.
