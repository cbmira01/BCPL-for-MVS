# Runtime interface conventions and contracts: MR10 and Cambridge

Status: **architectural note; source-grounded, not a complete historical specification** (2026-10-09).

## Interface declarations versus runtime contracts

Both BCPL systems have a central source-level **LIBHDR**. A declaration such as `APTOVEC:40` binds a service name to a numbered position in the BCPL global vector. It does **not**, by itself, specify number and meaning of arguments, results, storage ownership, errors, or machine linkage.

Three kinds of agreement need to be distinguished:

1. **Name/slot convention:** the `GLOBAL` declarations in LIBHDR map symbols to global-vector slots.
2. **Behavioral contract:** callers and implementations agree on procedure arguments, results, state changes, lifetime and failure behavior. Recover these from manuals, compiler call sites, BLIB and machine-dependent code.
3. **Execution ABI:** startup, global-vector initialization, generated procedure call/return, register roles, workspace/stack layout and operating-system services. LIBHDR does not comprehensively specify this.

A runtime implementation must honor all three. LIBHDR is an interface declaration, **not a full behavioral specification**.

## MR10 INTCODE compiler kit

Evidence in the repository:
- `richards-bcpltape/mr10/bcplkit/blib` begins with a section labelled `// LIBHDR`, ends that section with `.`, and then supplies `BLIB` source using `GET "LIBHDR"`.
- `richards-bcpltape/mr10/bcplkit/{syn,trn,cg,icint}` all use `GET "LIBHDR"`.
- `richards-bcpltape/mr10/b/bcplhdr` uses `GET "LIBHDR"` and adds compiler-specific globals. **BCPLHDR is not LIBHDR**.

Representative MR10 declarations: `START:1`, `SELECTINPUT:11`, `RDCH:13`, `WRCH:14`, `STOP:30`, `LEVEL:31`, `LONGJUMP:32`, `REWIND:35`, `APTOVEC:40`, `FINDOUTPUT:41`, `FINDINPUT:42`, `ENDREAD:46`, `ENDWRITE:47`, `WRITES:60`, `WRITEN:62`, `WRITEF:76`, `GETBYTE:85`, `PUTBYTE:86`.

MR10's header has `ENDSTREAMCH=-1` and `BYTESPERWORD=2`. This describes kit-target assumptions, not the word size of every historical BCPL. Its `icint` source describes an assembler/interpreter for a 16-bit EBCDIC machine and notes testing on IBM 370.

**What is established:** the compiler phases, interpreter and BLIB share an agreed global namespace. The supplied BLIB implements some, but not all, declared services. The inspected MR10 kit does not furnish a complete central behavioral specification or complete source implementation of all runtime services. **This does not prove that no contemporary external manual or fuller implementation existed.** The MR10 INTCODE bootstrap architecture must also be distinguished from Cambridge native object-module linkage.

## Cambridge System/370 BCPL

Evidence: `richards-bcpltape/sys3/bcpl/libhdr` and `richards-bcpltape/bcplib/bcpl/{bcpl,syn,trn,cg,blib}` and compiler headers. Consult `native-compiler/runtime-dependency-audit.md` for source-traced compiler dependencies; `asm/bcplmain-wip.asm` is our reconstruction, **not historical specification**.

Cambridge keeps key global slots including `START:1`, `RDCH:13`, `WRCH:14`, `STOP:30`, `APTOVEC:40`, `FINDINPUT:42`, `WRITEF:76`, `GETBYTE:85`, and `PUTBYTE:86`. It expands the interface to module loading, diagnostics, richer streams and dataset I/O, time/date, parameters, stack bounds, byte/word utilities, allocation, FORTRAN bridging and block-file operations. Some globals are runtime **data**, not procedures.

Cambridge's header specifies `BYTESPERWORD=4`, `BITSPERWORD=32`, `BITSPERBYTE=8`, `MAXSTRLENGTH=255`, and `FIRSTFREEGLOBAL=150`. The latter describes the conventional beginning of application/compiler-specific global slots, **not** a maximum global-vector capacity.

**LIBHDR is the public interface to the complete runtime system, not an extension library layered over BLIB.** BLIB implements a set of largely BCPL-coded facilities; BCPLMAIN and other native modules provide machine-dependent/OS facilities. The header does not prescribe a one-to-one implementation-module boundary.

Cambridge's distinct native **execution ABI** has been established through CG370 output and probes: R4 is callee entry/code base, R5 current workspace, R6 return linkage, R7 onward early arguments (R7 also result), R11 system-vector base, R12 global-vector base, and R15 new workspace. These details are additional to LIBHDR.

## APTOVEC demonstrates the distinction

Both LIBHDRs declare `APTOVEC:40`. The behavior recovered for Cambridge is conceptually `APTOVEC(F,N)`: construct temporary stack storage for `VEC N` (N+1 BCPL words), call `F(V,N)`, propagate its result, and reclaim the workspace when the call unwinds. Unlike GETVEC/FREEVEC, the vector does not persist as an independent heap allocation.

**The common global number alone proves none of those semantics and does not imply binary compatibility** between the MR10 16-bit kit and Cambridge's 32-bit System/370 environment.

Current **reconstruction** evidence: native regressions 091 (small nested call), 092 (N=9000; 36,004-byte vector) and 093 (controlled overflow diagnostic) were operator-reported PASS under TK5. This proves only those tested behaviors of the present BCPLMAIN, not historical completeness. The full native panel remains a separate acceptance gate.

## Conclusions and reconstruction discipline

- **Established:** both systems used a central declarative LIBHDR runtime interface, with substantial continuity of global slot assignments.
- **Established:** LIBHDR covers services beyond BLIB; the implementations involve machine-dependent runtime facilities as well.
- **Established:** source modules depended on shared behavioral and execution conventions beyond LIBHDR's declarations.
- **Not established:** that the inspected MR10 kit includes a complete behavioral contract, or that no such specification existed elsewhere.
- **Not established:** that same-numbered global services have identical semantics or representation between target systems.
- **Project practice:** for every required runtime service record its global number, historical provenance, signatures, data representation, ownership, side effects, errors, register/workspace effects, executable test evidence, and unresolved questions. Label claims **DECLARED**, **SOURCE-OBSERVED**, **TESTED**, or **INFERRED**.

For native Cambridge bootstrap, implement the runtime demanded by its compiler's actual observed calls and its LIBHDR, rather than assuming that either MR10's header or BLIB alone constitutes the system.
