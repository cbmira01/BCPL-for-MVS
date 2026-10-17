# BCPLIO dynamic streams — current DEVOBJ runtime contract

**M5.4 documentation baseline: 17 October 2026.** Scope: native Cambridge-compiled
BCPL on System/370, MVS 3.8J/TK5, linked against the **DEVOBJ(BCPLM6 +
BCPLIO)** candidate. This is the *current* dynamic-stream contract. The
[early fixed-DD contract](../../native-compiler/regression/native-stream-contract.md)
records an older predecessor and should not be read as a description of
the present candidate. The [M4.2 JCL/QSAM responsibility note]
(BCPLIO-JCL-QSAM-stream-contract.md) remains authoritative on recoverable
failure versus MVS abend. This project reconstructs a historical interface;
it does not claim complete identity with the original IBM/370 BCPL runtime.

## 1. What BCPLIO provides (and what it does not)

The application sees *character streams* through historical BCPL globals.
The implementation maps those streams onto MVS **QSAM fixed-record I/O**.
A program does not see the QSAM DCB, JFCB, GET/PUT record operation,
RECFM or BLKSIZE through this core character-stream API.

| Layer | Obligation |
|---|---|
| BCPL application | Supply a valid allocated DD name, select a stream, use ordinary BCPL input/output/close operations; handle unsuccessful FIND |
| Job author / dataset allocation | Provide a compatible named DD allocation and record attributes, with suitable input data or output destination |
| BCPLIO | Normalize the DD name, validate/locate an allocation, manage stream descriptors/handles/DCBs and buffers, call relevant MVS QSAM services, and translate supported records to/from BCPL characters |
| MVS QSAM | Apply actual dataset attributes and validate or carry out OPEN/GET/PUT/CLOSE; may issue a normal failure indication or an unrecovered abend |
| JES2 (for SYSOUT DDs) | Own spool representation, class/device routing and onward output handling after QSAM accepts output |

The [M5.1 acceptance record]
(Milestone-BCPLIO-dynamic-stream-M5.1-plan.md) explicitly **does not**
require BCPLIO to independently verify internal JES2 spool bytes.
Its responsibility is the QSAM-facing record contract. A separate
application-facing QSAM or VSAM record library belongs outside this
core character-stream API.

## 2. Programmer-visible operations

These are the tested historical BCPL global assignments; G-numbers are
not changed for dynamic streams.

| G | Operation | Documented native effect |
|---:|---|---|
| 11 | SELECTINPUT(handle) | Select a valid live input handle; invalid or retired handle does not replace current selection |
| 12 | SELECTOUTPUT(handle) | Select a valid live output handle; invalid or retired handle leaves output selection intact |
| 13 | RDCH() | Return the next character, a synthesized line feed (10) at a fixed-record boundary, or -1 at EOF |
| 14 | WRCH(ch) | Append character to selected output's pending record; ch=10 emits one full 132-byte record |
| 15 | UNRDCH() | One-character pushback/repeat behavior in the *currently selected* input stream, including tested EOF behavior |
| 16 | INPUT() | Return the current input handle |
| 17 | OUTPUT() | Return the current output handle |
| 30 | STOP(code) | Terminate with requested BCPL status; tested dynamic pending-output flush under STOP(8) |
| 33 | WRAPOUTPUT() | Historical provisional wrap interface; retain tested alternate-output behavior, not a general QSAM block operation |
| 39 | FINDPARM() | PARM-related memory-backed pseudo-stream; not a named QSAM DD and not a new file allocation |
| 41 | FINDOUTPUT(name) | Return live opaque output handle for a supported existing JCL DD, otherwise zero under ordinary returned-control failures |
| 42 | FINDINPUT(name) | Return live opaque input handle for a supported existing JCL DD, otherwise zero under ordinary returned-control failures |
| 46 | ENDREAD() | Close and retire the selected input lifetime; do not presume an MVS DD DATA rewind on later FIND |
| 47 | ENDWRITE() | Flush pending output, close/retire selected output lifetime, restore ordinary output selection per tested cases |

BCPL global 40 (APTOVEC) and G85/G86 byte functions belong to
*other* modular runtime components, not a BCPLIO interface expansion.
BLIB routines such as WRITES are compiled library services using the
stream primitives; they are not additional QSAM operations.

**Examples of supported calls** (not new syntax):

```bcpl
LET R = FINDOUTPUT("REPORT")
IF R=0 DO FINISH
SELECTOUTPUT(R)
WRITES("Hello")
WRCH(10)
ENDWRITE()
```

The application requests **DD name REPORT**; the job must supply
`//REPORT DD ...` with compatible attributes. FIND is not an
MVS dynamic-allocation request: there must already be an allocation.
Ordinary built-ins are still **BCPIN**, **BCPINB**, **SYSPRINT**
and **BCPALT**. These are not names for new public global slots.

## 3. DD normalization and stream identity

- Input is a BCPL counted string containing **1–8 valid DD-name
  characters**. The runtime uppercases EBCDIC lowercase letters
  and compares space-padded eight-byte normalized names. It
  rejects empty, overlength and invalid names **without truncation**.
  An allocated DD must be present; it is not discovered by
  enumerating arbitrary datasets.
- FINDINPUT and FINDOUTPUT are separate *directions*. A second
  FIND of an already **open** normalized DD in the same direction
  returns the **same live handle** and does not duplicate OPEN.
- A successful FIND returns an opaque **BCPL word-address
  handle**, not an MVS DCB address, a DD index or an exposed
  descriptor pointer. Compiled BCPL must not inspect its storage.
- ENDREAD/ENDWRITE retire the handle. A subsequent FIND of the
  same DD establishes a new lifetime with a **different** handle.
  Selecting an old handle has no effect on the new selection.
  Handles are not recycled during a run; dead small handle
  records are reclaimed at final cleanup.
- Ordinary stream count is governed by available MVS resources,
  not a fixed 12-channel table. Regression 130 exercised
  **16 concurrently open dynamic input DDs**. This is evidence
  for tested capacity, **not** an unlimited-capacity guarantee.

Core runtime keeps normalized DD descriptors, independent selected
input/output state, record buffers, cursor/EOF/pushback state, dynamic
DCB regions and durable handle identities. Canonical ownership and
QSAM code are in [BCPLIO assembler]
(../../native-compiler/asm/bcplio.asm); [BCPLM6]
(../../native-compiler/asm/bcplmain-d6-candidate.asm) owns bootstrap,
globals, FINISH/STOP orchestration and linkage to other components.
They are independently linked rather than pasted into one assembly source.

## 4. Supported record transformation

| Direction | Supported stream shape | Translation |
|---|---|---|
| Input | Sequential text-oriented fixed **FB80** QSAM allocations | GET supplies a record; right-hand EBCDIC X'40' padding is trimmed, then BCPL newline code **10** is synthesized. RDCH returns **-1** at EOF. Per-stream UNRDCH and independent cursors are preserved. |
| Output | Sequential text-oriented fixed **FB132** QSAM allocations | Characters collect independently per output. A BCPL newline code **10** emits a record, blank padded through byte 132 with EBCDIC **X'40'**. A blank logical line emits an empty/blank-padded physical record; a partly filled final record is emitted by ENDWRITE or accepted termination. |
| Output limit | Up to **132** characters before newline | Regression 112 exercises exactly 132; the 133rd character follows the documented **STOP(12)** overflow policy (regression 113). |

These are **application-level translation rules**, not a claim that
BCPLIO checks all after-OPEN DCB attributes or corrects incompatible
JCL. The private copied dynamic QSAM DCB templates identify
`DSORG=PS` and MACRF (input GM, output PM), but do not
themselves hardcode every record attribute; MVS resolves effective
attributes during OPEN. Both **FB80** and **FB132** describe the
supported fixture/data contract, not unrestricted QSAM facility
support.

Important intentional limitation: **significant trailing blanks on
FB80 input cannot be distinguished from padding** by this stream
translation. The BCPL programmer gets right-trimmed characters and
synthetic newlines, not an exact 80-byte record image. Use a
separate record API for exact source records.

Not part of this milestone: VB/variable records, PDS traversal,
VSAM, arbitrary binary I/O, dataset creation/dynamic allocation,
direct S/370 inline code from BCPL, or runtime QSAM data-structure
exposure. Neither an optional QSAM library nor any new global
extension dispatcher has been introduced.

## 5. Lifecycle and returned-control failures

- **Normal closure:** ENDREAD/ENDWRITE close and retire the selected
  owned dynamic stream; pending output must be flushed as tested.
  FINISH and STOP(8) invoke the runtime's IOFIN/IODRAIN path,
  draining live dynamic streams including two simultaneously
  partial output records (cases 128 and 129).
- **Ownership:** one dynamic descriptor (32 bytes), one
  associated 268-byte QSAM DCB/record region and one
  stable-handle record (16 bytes) are allocated per new
  stream lifetime; closed descriptor/DCB resources are
  released, while small retired handles remain until
  final drain to prevent stale-address aliasing.
- **Returned failures:** invalid or missing DD names, conditional
  GETMAIN denial, and a detected recoverable OPEN failure
  lead to FIND returning zero while preserving the currently
  selected stream; test-only denial paths and cleanup/retry
  are covered by 134–145. This says what BCPLIO does **if
  it regains control**, not that every failed SVC19 does so.
- **Unrecoverable host errors:** a real MVS OPEN/GET/PUT/CLOSE
  failure may abend or bypass BCPLIO's recoverable branch.
  BCPLIO does **not** claim to catch all S013, storage or I/O
  abends, to reinterpret all effective DCB values, or to
  continue after arbitrary MVS failure. Exploratory jobs
  7874–7876 did **not** produce an unsuccessful real OPEN.
- **Accounting scope:** M4.3 private, test-only assembler
  variants counted successful GETMAIN/FREEMAIN and SVC19/20
  calls on returned-control paths, including terminal drain
  and synthetic denials. These counters are **not** a new
  BCPL G service, not installed in canonical BCPLIO,
  and not independent proof of underlying MVS physical
  storage reclamation. See [M4.3 accounting record]
  (Milestone-BCPLIO-dynamic-stream-M4.3-plan.md).

## 6. Evidence and acceptance limits

| Gate | Observed operator evidence | Meaning |
|---|---|---|
| M4.4 | DEVOBJ candidate native 00–145: **145 PASS**, zero unexpected FAIL, expected SKIP 083; **145/145 saved logs audited** | Existing compiled BCPL runtime, ordinary BLIB/compiler and stream regression compatibility under the tested profile |
| M5.1.1 | **JOB 8184** AT114R, assembly/link/GO RC0000; class A PRINTER1 and class Z PRINTER2 observed separately | Physical writer route for two **built-in** output DDs, not raw spool bytes |
| M5.1.2 | **JOB 8185** M5D124B, six steps RC0000, VCHK independently compares GET buffers by CLC(132), exact order/EOF | Exact QSAM **sequential-dataset** FB132 record bytes for dynamic REPORT (2 records) and REPORT2 (1 record) |
| M5.2 | **JOB 8186** M52PAD, first five steps RC0000, VCHK intentional **RC0012** | Real MVS checker rejects an incorrect **132nd padding byte**; job-summary FAILURE is expected here |
| M5.3 | Source-to-test matrix and above accepted run evidence | Coverage accepted without re-running cases; not a claim that all cases were separately byte-verified |

Printer images can trim padding. **The dataset-backed byte proof
does not demonstrate untouched JES2 spool bytes**, and the
class-separated route proof does not byte-check every SYSOUT
record. M5.1 was deliberately closed at the QSAM responsibility
boundary, and M5.3 closed within that agreed scope.

## 7. Rebuild, test and current status

The **single** clean-room procedure is
[Clean-room MVS PDS reconstruction]
(../clean-room-mvs-reconstruction.md).
Follow its base M3 MR10/ICINT19/CAMBCOMP/BLIB rebuild **and**
its M5.4 DEVOBJ(BCPLM6+BCPLIO) addendum. Never migrate
derived .OBJ/.LOAD/INTCODE binaries as if they were source.

The isolated M5.1/M5.2 experimental JCL and checkers under
`tools/checks/` remain useful diagnostic aids; they
are **not** automatically incorporated into the standard
`tools/native/run-regression` runner. Any future
integration is a separate maintenance decision.
**M5.4 documentation completed. M5.5 fresh native 00..145 candidate regression and independent audit PASSED and were formally accepted by the owner on 2026-10-17; the BCPLIO dynamic-stream milestone is CLOSED.** The accepted final evidence and post-success interrupted duplicate are recorded in the [final acceptance note](Milestone-BCPLIO-dynamic-stream-final-acceptance.md). Production NATIVE_OBJ promotion remains a separate explicit decision.
Production NATIVE_OBJ promotion is a separate explicit decision.
