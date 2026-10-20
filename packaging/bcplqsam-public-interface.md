# BCPLQSAM — Public Interface Specification

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implementation of QSAM  
**March:** Q.0 — Reconnaissance & contract  
**Target:** IBM System/370, MVS 3.8J under Hercules  
**Package:** BCPLQSAM  
**Public global:** `QSAMSVC:200`  
**API:** Version 1 public interface — Q.0 reviewed design baseline  
**Status:** Public version-1 numeric contract reviewed; standalone ABI/QSAM jobs 2157, 2159–2163, 2165–2170 and 2172–2174 passed at their tested parameters. JOB 2171 demonstrated an unrecovered S013-20 on an incompatible QSAM OPEN. JOB 2172 confirmed non-opening JFCB geometry checks, JOB 2173 empty-dataset persistent EOF, and JOB 2174 static-stage pending-record retry. Production BCPLQSAM and R.0 registration remain unimplemented
**Provenance:** Based on the Project Source `BCPLQSAM — Public Interface Specification`, dated October 19, 2026.

---

## 1. Purpose

BCPLQSAM provides native BCPL programs with direct access to MVS QSAM sequential logical-record I/O.

It allows BCPL applications to open, read, write, and close JCL-allocated datasets without converting them into character streams.

Its central requirements are:

- Exact preservation of eight-bit record data.
- Support for fixed-length and variable-length logical records.
- Separation of logical records from physical disk blocks.
- Explicit buffer capacity, record length, and operation status.
- Support for multiple concurrently open datasets.
- Integration with the project's optional Runtime Extensions architecture.

BCPLQSAM is a new MVS-specific System Extension. It is not claimed to reproduce a historical Cambridge BCPL QSAM interface.

## 2. Relationship to the existing runtime

The existing Core Runtime and `BCPLIO` character-stream interfaces remain unchanged.

| Facility | Responsibility |
|---|---|
| BCPLMAIN | Program startup, global-vector construction, and core runtime coordination |
| BCPLIO | Historical BCPL character-stream operations |
| BCPLMEM | BCPL vector allocation and reclamation |
| BCPLBYTE | Machine-dependent byte access |
| BLIB | Historical BCPL Base Library |
| BCPLQSAM | Optional MVS sequential logical-record operations |

A BCPL program may use both BCPLIO and BCPLQSAM.

Neither interface depends on the other.

BCPLQSAM does not introduce compiler changes and is not a prerequisite for native Cambridge compiler reconstruction.

## 3. Logical-record model

**BCPLQSAM operates on logical records, never physical blocks.**

One successful READ returns one logical record. One successful WRITE supplies one logical record.

MVS QSAM remains responsible for blocking, deblocking, physical buffering, and the access-method operations.

For example, FB80 datasets with physical block sizes of 800 and 8000 bytes produce the same sequence of 80-byte logical records.

BCPLQSAM does not expose physical disk blocks, channel programs, or QSAM internal control structures through its public API.

### Binary fidelity

The complete data portion of a logical record is preserved.

BCPLQSAM must not:

- Trim trailing EBCDIC blanks.
- Insert or remove newlines.
- Translate between ASCII and EBCDIC.
- Treat binary zero as a string terminator.
- Silently truncate or pad application data.
- Interpret records as character strings.

A record containing arbitrary hexadecimal byte values from `00` through `FF` must be transferred unchanged.

## 4. Public global-vector interface

BCPLQSAM occupies one permanent BCPL global-vector entry:

```bcpl
GLOBAL $(
    QSAMSVC:200
$)
```

Global 200 is assigned to BCPLQSAM in the project's Global Number Registry.

The public entry is an opcode dispatcher:

```text
QSAMSVC(operation, request, result)
```

Except for QUERY, `request` and `result` are caller-owned BCPL word vectors.

The API uses the existing native BCPL calling convention:

- A BCPL word is 32 bits.
- BCPL pointers are word addresses.
- The first three arguments are passed in registers R7, R8, and R9.
- R7 contains the function result.
- The extension must preserve the native BCPL runtime's required register and workspace invariants.

The R7/R8/R9 argument and R7 result registers and BCPL word-pointer representation agree with existing runtime source and focused regressions. A separately assembled test-only Q0DISP dispatcher passed the G!200 calling-convention probe on MVS 3.8J (JOB 2157, RC=0000, output 42). That verifies the exercised entry, result-vector and return paths; unexercised register preservation, actual QSAM calls, and production extension registration still require verification. See [Q.0 ABI evidence](qsam-q0-dispatcher-abi-evidence-20261019.md).

### Optional wrappers

BCPL source-level wrappers may eventually provide convenient operations such as:

```text
QSOPEN(...)
QSREAD(...)
QSWRITE(...)
QSCLOSE(...)
QSINFO(...)
```

These wrappers call QSAMSVC. They do not require additional global-vector entries.

## 5. Operation numbers

The proposed version 1 operation table is:

| Opcode | Operation | Purpose |
|---|---|---|
| 0 | QUERY | Discover interface version and supported capabilities |
| 1 | OPEN | Open a JCL-allocated dataset |
| 2 | READ | Read one logical record |
| 3 | WRITE | Write one logical record |
| 4 | CLOSE | Close a dataset |
| 5 | INFO | Return effective dataset characteristics |

Operation numbers belong to BCPLQSAM's package-local opcode namespace. The Q.0 numeric assignments above are part of this reviewed **design baseline**. Once implemented and published as an accepted API, the meaning of an opcode must remain stable across compatible versions.

## 6. Request and result vectors

For ordinary operations, version 1 uses a four-word request vector and an eight-word result vector.

In BCPL:

```bcpl
LET REQUEST = VEC 3
LET RESULT  = VEC 7
```

### Request vector

| Word | Meaning |
|---|---|
| `request!0` | DD-name pointer for OPEN; otherwise an opaque dataset handle |
| `request!1` | OPEN mode or record-buffer pointer |
| `request!2` | Record-buffer capacity or data length, in bytes |
| `request!3` | Reserved; set to zero |

### Result vector

| Word | Meaning |
|---|---|
| `result!0` | Completion status |
| `result!1` | Handle, actual record length, required capacity, or other operation-specific value |
| `result!2` | Additional diagnostic information when available |
| `result!3` | Reserved |
| `result!4` | INFO: effective record format |
| `result!5` | INFO: effective logical record length |
| `result!6` | INFO: effective block size |
| `result!7` | INFO: maximum supported logical data length |

The dispatcher returns the operation completion status as its ordinary BCPL function result. `result!0` contains the same status.

Unused result fields are initialized to zero on normal returns. The values of any fields not defined for an operation must not be interpreted.

All vector fields are 32-bit BCPL words, not byte arrays.

Version 1 callers must supply the documented vector sizes. **Request and result allocation bounds are a caller obligation:** the ordinary dispatcher receives only two BCPL word pointers, not verified vector capacities. It cannot generally prove that either points to four/eight accessible words; an incorrectly sized or invalid vector can corrupt storage. `request!3` must be zero; a nonzero value is `QS_ERR_ARGUMENT`. For valid result vectors, all eight result words are set deterministically on ordinary returns: unassigned fields are zero. QUERY writes only its separate capability vector, not the ordinary result vector.

The declared record-data capacity is in **bytes** and is enforceable assuming the caller really owns that amount of writable storage. Future compatible versions may add opcodes or versioned descriptors but must not change the size or interpretation of these existing fixed layouts. An extension that needs bigger ordinary request/result vectors requires a distinct opcode or an incompatible interface generation.

## 7. QUERY — opcode 0

QUERY follows the proposed shared Runtime Extensions convention.

```text
QSAMSVC(0, info_vector, capacity_words)
```

This is intentionally a special case of the dispatcher signature.

A size inquiry is performed with:

```text
QSAMSVC(0, 0, 0)
```

It returns the required descriptor size in 32-bit words without allocating storage or changing I/O state.

### Initial capability descriptor

The proposed version 1 descriptor contains six words.

| Word | Contents |
|---|---|
| `info!0` | Shared query descriptor format version |
| `info!1` | BCPLQSAM API major version |
| `info!2` | BCPLQSAM API minor version |
| `info!3` | Required descriptor size in words |
| `info!4` | Bitmap of supported operation numbers |
| `info!5` | Package capability flags |

The shared descriptor format is **1**; the initial BCPLQSAM API version is **1.0**, and `info!3` initially equals **6**. `QSAMSVC(0,0,0)` returns 6 without touching memory. With a sufficient capacity, QUERY copies the entire descriptor and returns its required word count (not status zero). With insufficient capacity, it returns `QS_ERR_CAPACITY=-1` and copies **no** descriptor words; invalid combinations return `QS_ERR_ARGUMENT=-3`. If a compatible future descriptor appends fields, the required-size probe reports the larger size; an undersized caller must allocate accordingly.

For version 1, `info!5` capability flags are: `QS_CAP_FIXED=1` (tested F/FB support), `QS_CAP_VARIABLE=2` (tested V/VB support), and `QS_CAP_CARRIAGE=4` (tested carriage-control support). Unassigned bits are zero. `info!4` lists **currently implemented** supported opcodes, not anticipated Q.2–Q.4 features.

Bit 0 of `info!4` represents opcode 1, bit 1 represents opcode 2, and so forth.

An insufficient descriptor buffer must not be partially modified.

QUERY is side-effect-free: it does not open a dataset, perform I/O, allocate a dataset buffer, or alter an existing handle.

QUERY cannot be used safely to discover an extension that was never linked or registered. The shared registration mechanism must establish package availability before application execution.

## 8. OPEN — opcode 1

OPEN creates a QSAM logical-record handle for a dataset already allocated through JCL.

### Request

| Field | Contents |
|---|---|
| `request!0` | BCPL pointer to a length-prefixed DD-name string |
| `request!1` | Input or output mode |
| `request!2` | Zero |
| `request!3` | Zero |

The DD name is **not stored directly in the 32-bit request word**.

`request!0` contains a BCPL word address pointing to a normal length-prefixed BCPL string, such as `"MYINPUT"`.

BCPLQSAM reads the string, validates its contents, normalizes permitted lowercase letters to uppercase, and copies the name into its own eight-byte, EBCDIC blank-padded DDNAME field.

The original string remains owned by the caller.

### DD-name rules

The initial naming rules follow the current BCPLIO implementation:

- Length from 1 to 8 characters.
- First character alphabetic or `@`, `#`, or `$`.
- Subsequent characters may also include decimal digits.
- Permitted lowercase alphabetic characters are normalized.
- Invalid names are rejected.
- The DD name must refer to an allocation provided by JCL.

BCPLQSAM does not dynamically allocate datasets.

### OPEN modes

Version 1 supports:

- INPUT — sequential logical-record reading.
- OUTPUT — sequential logical-record writing.

APPEND, UPDATE, and direct-access modes are excluded.

The public mode constants are `QS_INPUT=1` and `QS_OUTPUT=2`. Other values return `QS_ERR_ARGUMENT` without acquiring a handle.

### Successful OPEN

A successful OPEN returns status zero and a positive opaque handle in `result!1`.

The handle identifies a BCPLQSAM-managed dataset, not a raw DCB or machine-storage address.

An unsuccessful OPEN returns an error when MVS permits control to return to the extension.

The extension releases resources acquired during an unsuccessful, recoverable OPEN.

A valid DD allocation does not guarantee that QSAM OPEN will succeed.

## 9. Dataset handles

Version 1 supports at least 16 concurrently open datasets.

Handles have these properties:

- Positive integer representation.
- Opaque to the application.
- Independent of DD names.
- Associated with an input or output mode.
- Valid until successfully closed or otherwise invalidated.
- Checked against the extension's active-handle state.

A closed handle must not become valid accidentally merely because its internal table slot has been reused.

An application may hold several handles simultaneously and interleave operations among them.

Whether a particular DD allocation may be opened more than once is subject to MVS/QSAM compatibility and documented restrictions; the API does not promise that every duplicate OPEN succeeds.

The initial implementation may use private nonreentrant state.

## 10. READ — opcode 2

READ returns one complete logical record.

### Request

| Field | Contents |
|---|---|
| `request!0` | Open input handle |
| `request!1` | BCPL word pointer to writable buffer |
| `request!2` | Buffer capacity in bytes |
| `request!3` | Zero |

### Successful READ

On success:

- The dispatcher returns status zero.
- `result!0` is zero.
- `result!1` contains the actual logical data length.
- Exactly that many bytes are copied into the caller's buffer.
- No terminator, newline, padding, or translation is added.

The application may examine individual bytes using the existing `GETBYTE` primitive.

### End of file

EOF is a distinct positive status.

At EOF:

- No new record is returned.
- The destination buffer remains unchanged.
- The actual returned data length is zero.
- Repeated READ calls continue reporting EOF until the dataset is closed.

A successful zero-length variable record, where supported by the actual QSAM format and implementation, is **not EOF**. It is a successful READ with a data length of zero.

### Insufficient-buffer behavior — accepted decision

If the next record is larger than the caller's capacity:

1. READ returns BUFFER_TOO_SMALL.
2. `result!1` reports the complete required record length.
3. The caller's buffer remains unchanged.
4. BCPLQSAM retains the entire logical record privately.
5. The application may retry READ with a larger buffer.
6. A successful retry returns the retained record without performing another QSAM GET.

The pending record belongs to its original input handle.

Repeated undersized retries leave it pending.

CLOSE discards any pending record belonging to that handle.

This requires private record staging storage. The extension must report resource failures rather than silently discard oversized data. The approved [Q.0 staging and resource-management decision](qsam-q0-staging-resource-design-decision.md) selects checked per-handle allocation before the first GET/PUT, with an explicit pending-record state and no second GET on an undersized retry. The implementation and limits have not yet been MVS-tested.

There is no fixed public limit of 80 or 132 bytes. The applicable limits come from MVS dataset attributes, QSAM capabilities, and the extension's documented supported maximum.

## 11. WRITE — opcode 3

WRITE submits one logical record for output.

### Request

| Field | Contents |
|---|---|
| `request!0` | Open output handle |
| `request!1` | BCPL word pointer to readable data |
| `request!2` | Number of data bytes to write |
| `request!3` | Zero |

### Fixed-length output

For F or FB datasets, the requested length must equal the effective logical record length.

BCPLQSAM must not silently pad a shorter record or truncate a longer record.

An invalid length is rejected before QSAM PUT.

### Variable-length output

For V or VB datasets, the caller supplies the actual data length.

BCPLQSAM constructs or maintains the required QSAM record-control information internally.

The caller does not include an RDW or BDW in the data buffer.

Lengths outside the supported bounds are rejected.

### Completion

A successful WRITE means the record was accepted by the applicable QSAM operation.

It does not guarantee that all physical output has reached its final destination.

CLOSE failures must be observable separately when MVS returns an error.

On successful WRITE, `result!1` is always the accepted data byte length.

## 12. CLOSE — opcode 4

CLOSE ends use of a dataset handle.

### Request

| Field | Contents |
|---|---|
| `request!0` | Open handle |
| `request!1–3` | Zero |

On successful CLOSE:

- QSAM CLOSE has completed.
- Associated private buffers and descriptors are released.
- The handle becomes invalid.
- Further READ, WRITE, INFO, or CLOSE operations using that handle fail.

Closing an invalid or previously closed handle is an error.

A CLOSE error must be reported if MVS returns control with an identifiable failure.

The exact handle and resource disposition following exceptional CLOSE failure requires an explicitly tested implementation policy; it must not be represented as successful cleanup without evidence.

On normal BCPL `FINISH` and `STOP(n)`, a *linked* BCPLQSAM instance must attempt to close every outstanding handle and safely release extension-owned resources before final program memory reclamation. This is an approved design requirement, not implemented functionality. The intended mechanism is a **generic termination/finalization hook** from [Milestone Runtime Extensions](milestone-runtime-extensions.md), not a QSAM-specific permanent BCPLMAIN edit. Preserve the requested `STOP(n)` code. Normal termination cleanup does not guarantee recovery from unrecovered MVS abends, and the diagnostic/exit policy for an implicit CLOSE failure remains to be verified. See [Q.0 decision](qsam-q0-staging-resource-design-decision.md).

## 13. INFO — opcode 5

INFO returns the effective characteristics of an open dataset.

### Request

| Field | Contents |
|---|---|
| `request!0` | Open handle |
| `request!1–3` | Zero |

### Result

On success, the result vector provides:

- Effective record format.
- Effective logical record length (LRECL).
- Effective block size (BLKSIZE).
- Maximum supported logical data length.

INFO uses the project-defined numeric enum `QS_FMT_F=1`, `QS_FMT_FB=2`, `QS_FMT_V=3`, `QS_FMT_VB=4`, `QS_FMT_FBA=5`, and `QS_FMT_VBA=6`. These are **not raw DCB RECFM bit encodings**. FBA/VBA may not be reported as supported until Q.4 verifies their treatment.

On success `result!1=0`, `result!2=0`, `result!3=0`, `result!4` is the enum, `result!5` is the effective **DCB LRECL**, `result!6` the effective **DCB BLKSIZE**, and `result!7` the maximum **application data bytes** per logical record allowed by both the dataset and the supported implementation. For F/FB, this data length equals LRECL. For V/VB, DCB LRECL includes the four-byte RDW, so the data maximum is no greater than LRECL minus four. QSAM BDWs are never included in the BCPL record buffer or length. Record-size/device limits must be checked on MVS 3.8.

INFO reports attributes established by the actual OPEN processing, not merely values copied from source JCL.

For variable records, the public maximum data length must distinguish application data bytes from internal MVS record-control bytes.

INFO does not expose mutable DCB structures or permit the application to change dataset attributes.

The caller can use INFO to size record buffers before beginning I/O.

## 14. Completion and error reporting

The status scheme is:

| Status class | Meaning |
|---|---|
| Zero | Success |
| Positive EOF status | End of input |
| Negative status | Error |

The symbolic error categories include:

- Invalid operation code.
- Invalid argument or request vector.
- Invalid DD name.
- Unallocated DD.
- OPEN failure.
- Invalid or stale handle.
- Operation incompatible with open mode.
- Unsupported record format.
- Buffer too small.
- Invalid output record length.
- Memory or handle resource exhaustion.
- READ/GET failure.
- WRITE/PUT failure.
- CLOSE failure.

The shared Runtime Extensions proposal already identifies provisional common query errors `-1`, `-2`, and `-3`.

The concrete Q.0 error-number assignments are in section 24. These values are part of the reviewed design baseline; validate before an accepted public header ships.

The result vector provides application-level status independently of JES messages.

Because no tested, stable MVS diagnostic encoding has been established, `result!2` is **zero** in this version 1 public contract. A future documented extension must specify the meaning of any new diagnostic value; ordinary status codes remain authoritative.

**Limits of error recovery:** MVS may issue an unrecovered abend during OPEN, GET, PUT, or CLOSE. BCPLQSAM does not promise to convert every system abend into an ordinary negative return code.

## 15. Buffer ownership and storage protection

The BCPL application owns the public request, result, and record-data buffers.

BCPLQSAM owns:

- QSAM DCBs and work areas.
- Handle table entries.
- Internal record buffers.
- Pending records retained for READ retries.
- Any other private MVS control structures.

The extension must not retain a public record-buffer pointer beyond the active operation.

All declared **record-data** byte capacities are enforced for valid caller-provided storage; the caller must separately ensure the fixed request/result word vectors contain the required words.

A BCPL pointer is a word address. The extension converts it into a System/370 byte address using the established runtime convention.

An accessible buffer of sufficient real storage is a caller obligation. The extension does not claim general protection against arbitrary invalid machine addresses or dishonest capacity declarations.

The initial extension is not required to be reentrant or thread-safe.

## 16. Dataset organizations and formats

| Format | Planned support | Milestone |
|---|---|---|
| F | Sequential fixed logical records | Q.2 |
| FB | Blocked fixed logical records | Q.2 |
| V | Variable logical records | Q.3 |
| VB | Blocked variable logical records | Q.3 |
| FBA | Fixed records with printer carriage control | Q.4 |
| VBA | Variable records with printer carriage control | Q.4, subject to verified MVS rules |
| U | Undefined-length records | Excluded initially |
| VS/VBS | Spanned variable records | Excluded initially |

For FBA/VBA, the API must explicitly document carriage-control treatment before acceptance. It must not silently remove or synthesize a control character.

Selected PDS members may be used through suitable JCL DD allocations where QSAM permits sequential processing. PDS directory maintenance is outside this interface.

## 17. Application integration and registration

BCPLQSAM is an optional package.

Application integration requires three separate steps:

1. The BCPL source declares `QSAMSVC:200` through the package's public header.
2. The application link-edit includes the BCPLQSAM object module.
3. The shared Runtime Extensions startup registration mechanism installs the dispatcher's entry address into G!200.

A declaration alone does not include executable code.

An IEWL INCLUDE alone does not install a BCPL global.

Normal RUN JCL supplies the DD allocations used by the already-linked application; it does not dynamically select optional packages.

The implementation must use the common Runtime Extensions registration mechanism rather than adding a QSAM-specific startup protocol.

Until registration is implemented and verified, this section describes the required architecture, not an available facility.

## 18. Illustrative BCPL usage

The following is schematic version 1 BCPL showing the intended calling pattern, not validated executable source.

```bcpl
GLOBAL $(
    START:1
    QSAMSVC:200
    GETBYTE:85
$)

MANIFEST $(
    QS_OPEN=1
    QS_READ=2
    QS_CLOSE=4
    QS_INPUT=1
$)

LET START() BE
$(1
    LET REQUEST = VEC 3
    LET RESULT = VEC 7
    LET BUFFER = VEC 199

    REQUEST!0 := "OBJECT"
    REQUEST!1 := QS_INPUT
    REQUEST!2 := 0
    REQUEST!3 := 0

    LET RC = QSAMSVC(QS_OPEN, REQUEST, RESULT)

    IF RC=0
    $(2
        LET HANDLE = RESULT!1

        REQUEST!0 := HANDLE
        REQUEST!1 := BUFFER
        REQUEST!2 := 800
        REQUEST!3 := 0

        RC := QSAMSVC(QS_READ, REQUEST, RESULT)

        // On success, RESULT!1 is the byte length.
        // BUFFER contains exactly that many data bytes.

        REQUEST!0 := HANDLE
        REQUEST!1 := 0
        REQUEST!2 := 0

        QSAMSVC(QS_CLOSE, REQUEST, RESULT)
    $)2

    FINISH
$)1
```

The example assumes an 800-byte destination and does not demonstrate the full retry loop or detailed error checks. A production example must handle those conditions and must use the final public manifest constants.

## 19. Principal acceptance demonstration

The principal Q.2 demonstration is a reversible binary-object conversion.

Input:

```text
BOOT_OBJ(BLIB)
    FB80 binary object records
```

BCPL reads each 80-byte logical record and encodes every byte as two hexadecimal characters.

Output:

```text
FB160 sequential dataset
    160 EBCDIC hexadecimal characters per record
```

A separate BCPL decoder converts each hexadecimal record back into 80 binary bytes.

An independent MVS verification step compares the reconstructed FB80 records against the original object member byte-for-byte.

Acceptance requires:

- Identical record count.
- Identical logical record lengths.
- Exact preservation of binary zeros.
- Exact preservation of nonprintable data.
- Exact preservation of significant trailing bytes.
- No silent data transformation.

The test should include both blocked and unblocked fixed datasets.

## 20. March roadmap

| March | Responsibility |
|---|---|
| **Q.0 — Reconnaissance & contract** | Verify ABI, public contracts, dataset limits, error semantics, and registration requirements |
| **Q.1 — Linkage & OPEN/CLOSE skeleton** | Independent module, dispatcher integration, OPEN/CLOSE, 16 handles, cleanup |
| **Q.2 — Fixed logical records** | F/FB READ/WRITE, exact binary fidelity, buffer retry, object-deck round trip |
| **Q.3 — Variable logical records** | V/VB support, actual record lengths, RDW handling and boundary tests |
| **Q.4 — SYSOUT devices** | SYSOUT, printer carriage control, card-punch record demonstrations |
| **Q.5 — Hardening & release** | Full verification, reproducible build and installation, optional-link demonstration, documentation and acceptance |

Q.0 is a specification and investigation march. Functional implementation begins only after the relevant design and shared registration prerequisites have been approved.

## 21. Exclusions

The initial milestone excludes:

- VSAM.
- BSAM and EXCP.
- Physical-block access.
- Random positioning or keyed access.
- Dynamic dataset allocation.
- PDS directory management, member creation, and STOW.
- Undefined-length and spanned-record formats.
- Compiler front-end or code-generator modifications.
- Replacement of BCPLIO character streams.
- Unverified general recovery from MVS system abends.

These may be considered as future system extensions.

## 22. Remaining Q.0 verification

The following items remain open before declaring Q.0 complete:

1. Extend the passed test-only G!200 ABI probe (JOB 2157) to verify actual production dispatcher register preservation, system-service calls and argument bounds.
2. Verify the explicit public mode, record-format and error constants proposed in sections 5, 8, 13 and 24 with native test callers.
3. Extend standalone QSAM evidence from JOBs 2159–2162 to the remaining actual MVS record-size limits, OPEN/DCB failure paths, V/VB zero-data-length and boundary cases, and retrievable diagnostics.
4. Verify the per-handle pending-record mechanism for an undersized READ.
5. Validate the explicit INFO fields and QUERY version rules against effective DCB attributes and a native capability-query probe.
6. Verify the common Runtime Extensions registration mechanism and its error handling.
7. Produce complete positive and negative test cases and validated BCPL caller examples.

The Global Number Registry owns the approved G!200 allocation. The package specification owns the BCPLQSAM operation-number namespace.

**The standalone ABI and QSAM probes passed; no production BCPLQSAM assembly, link-edit, or MVS execution is claimed.** See [Q.0 DASD evidence](qsam-q0-dasd-evidence-20261020.md) and the [Q.0 design review](qsam-q0-design-review-20261020.md).

---

## 23. Governing project references

- `packaging/milestone-qsam.md`
- `packaging/milestone-runtime-extensions.md`
- `packaging/runtime-and-library-nomenclature.md`
- `packaging/global-number-registry.md`
- `richards-bcpltape/sys3/bcpl/libhdr`
- `richards-bcpltape/bcplib/bcpl/cghdr`
- `bootstrap-toolchain/asm/bcplmain.asm`
- `bootstrap-toolchain/asm/bcplbyte.asm`
- `bootstrap-toolchain/asm/bcplio.asm`

GitHub is authoritative for the reviewed specification. The Project Source from October 19, 2026 supplies the base text. The decisions above and the enumerated constants below are Q.0 design outcomes. **Test-only IFOX/IEWL/MVS probes passed in JOBs 2157 and 2159–2162; no BCPLQSAM implementation, Runtime Extensions registration or regression acceptance is claimed, and Q.0 is not closed.**

## 24. Version 1 numeric interface assignments and operation results

### Operation, mode, success and capability constants

| BCPL manifest name | Value | Purpose |
|---|---:|---|
| `QS_QUERY` | 0 | Capability query |
| `QS_OPEN` | 1 | Open an allocated DD |
| `QS_READ` | 2 | Read a logical record |
| `QS_WRITE` | 3 | Write a logical record |
| `QS_CLOSE` | 4 | Close a handle |
| `QS_INFO` | 5 | Inspect effective dataset attributes |
| `QS_INPUT` | 1 | OPEN for input |
| `QS_OUTPUT` | 2 | OPEN for output |
| `QS_OK` | 0 | Ordinary operation success |
| `QS_EOF` | 1 | End of input (READ only) |
| `QS_CAP_FIXED` | 1 | Support for F/FB, when validated |
| `QS_CAP_VARIABLE` | 2 | Support for V/VB, when validated |
| `QS_CAP_CARRIAGE` | 4 | Supported printer control semantics, when validated |

### Numeric error codes

| BCPL manifest name | Value | Defined meaning |
|---|---:|---|
| `QS_ERR_CAPACITY` | -1 | QUERY vector too short, or READ buffer too small |
| `QS_ERR_OPCODE` | -2 | Unknown/unimplemented operation |
| `QS_ERR_ARGUMENT` | -3 | Invalid scalar, mode, QUERY pairing, reserved field or detectably invalid pointer |
| `QS_ERR_DDNAME` | -4 | DD-name spelling/length invalid |
| `QS_ERR_NO_DD` | -5 | DD not allocated, when reliably determined |
| `QS_ERR_OPEN` | -6 | Recoverable failure while opening |
| `QS_ERR_HANDLE` | -7 | Invalid, closed or stale handle |
| `QS_ERR_DIRECTION` | -8 | READ on output or WRITE on input |
| `QS_ERR_RECFM` | -9 | Unsupported effective dataset record format |
| `QS_ERR_LENGTH` | -10 | Output length invalid for dataset |
| `QS_ERR_RESOURCE` | -11 | Handle, storage or staging resource unavailable |
| `QS_ERR_READ` | -12 | Recoverable GET/READ failure |
| `QS_ERR_WRITE` | -13 | Recoverable PUT/WRITE failure |
| `QS_ERR_CLOSE` | -14 | Recoverable CLOSE failure |

These preserve the tentative shared Runtime Extensions meanings of `-1` (capacity), `-2` (opcode), and `-3` (invalid query arguments), while consistently reusing those codes for ordinary operations. `QS_EOF=1` is returned **only by READ**; a successful zero-byte variable record (if supported on the target) has `QS_OK=0`.

`QS_ERR_CAPACITY` on READ sets `result!1` to the exact pending record's required **data** byte count and leaves the user's data buffer unchanged. QUERY on capacity failure writes **nothing** into its capability vector; callers use the size probe. A failed OPEN distinguishes proven missing allocation (`QS_ERR_NO_DD`) from other failures (`QS_ERR_OPEN`). For ordinary errors, all result fields other than `result!0` and explicitly documented supplementary fields are zero.

### Ordinary operation result contract

| Operation | On `QS_OK`, `result!1` | Additional defined words |
|---|---|---|
| OPEN | Positive opaque handle | All other unused words zero |
| READ | Actual data byte count | EOF: `result!1=0`; too small: required size |
| WRITE | Accepted data byte count | Other unused words zero |
| CLOSE | Zero | Other unused words zero |
| INFO | Zero | `result!4` format code; `!5` effective LRECL; `!6` BLKSIZE; `!7` max data bytes |

READ retries are per-handle: after `QS_ERR_CAPACITY`, the record remains privately staged until a sufficiently large READ on that handle succeeds or CLOSE discards it. Repeated inadequate retries must not issue another QSAM GET. The extension should stage up to the supported maximum before advancing the record cursor, or fail recoverably without losing a record; Q.0 implementation verification must establish resource bounds.

For version 1 QUERY, the six-word capability descriptor is: format=1, API major=1, minor=0, required words=6, actual implemented-opcode bitmap, capability flags. Its return value is required words, **not** ordinary operation status.

### Public record-format constants

| BCPL manifest | Value | Record format |
|---|---:|---|
| `QS_FMT_F` | 1 | F |
| `QS_FMT_FB` | 2 | FB |
| `QS_FMT_V` | 3 | V |
| `QS_FMT_VB` | 4 | VB |
| `QS_FMT_FBA` | 5 | FBA (Q.4) |
| `QS_FMT_VBA` | 6 | VBA (Q.4, pending verification) |

These numbers are stable design-baseline declarations, **not** MVS DCB flags. Unimplemented formats must be reported unsupported rather than simulated.

### Limits of verification and follow-on gates

- Current runtime evidence supports the native first-three-argument convention, global-vector access through G!N, length-prefixed BCPL strings, and byte address conversion. A test-only G!200 Q0DISP dispatcher was assembled and executed in JOB 2157; the production BCPLQSAM dispatcher has not been implemented.
- The existing `BCPLIO` handles DD-name normalization and MVS QSAM internally; BCPLQSAM will reuse validated concepts but not the text-stream semantics.
- IBM's later [data-record overview](https://www.ibm.com/docs/en/zos-basic-skills?topic=set-data-record-formats), [QSAM DCB specification](https://www.ibm.com/docs/en/zos/3.2.0?topic=descriptions-dcbconstruct-data-control-block-qsam), and [QSAM GET reference](https://www.ibm.com/docs/en/zos/3.2.0?topic=descriptions-getobtain-next-logical-record-qsam) explain RDW, LRECL and move-mode behavior. They are **not** evidence that all modern details are available in MVS 3.8J.
- The test-only G!200 dispatcher ABI probe passed in JOB 2157. Standalone QSAM tests passed for FB80 JCL DD DATA/SYSOUT (JOB 2159), blocked FB80 DASD (JOB 2160), V (JOB 2161) and VB (JOB 2162). See [fixed SYSOUT evidence](qsam-q0-fb80-evidence-20261020.md) and [DASD execution evidence](qsam-q0-dasd-evidence-20261020.md). Q.0 still requires additional boundary/error tests, a validated pending-record strategy and reconciliation with shared Runtime Extensions R.0. This document records **specification decisions**, not milestone gate acceptance.
