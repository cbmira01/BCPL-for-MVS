# Milestone Decimal Arithmetic

**Status:** Proposed, not started (2026-10-15). Optional native BCPL runtime extension; independent of M4 and Milestone QSAM.

## Objective and scope

Give programs compiled with the existing native System/370 BCPL compiler accurate, base-ten, fixed-point arithmetic suitable for amounts, counters, and fields found in COBOL-style business records. Implement the substantial machine-dependent work in a separately assembled module, provisionally `BCPLDEC`, with a small BCPL-facing declaration/wrapper module. This is a **new extension**, not an assertion that historical Cambridge BCPL provided this API.

System/370 has packed-decimal operations such as ZAP, AP, SP, CP, MP, DP and SRP. Operand limits and scaling matter: up to 16 packed bytes (31 decimal digits and a sign); multiplication and division have stricter operand-layout/length conditions. Do **not** presume every 31-digit operation can be implemented as one instruction. Confirm hardware limits, exceptions and IFOX syntax against contemporary System/370 documentation before implementation.

**Included:** signed packed decimal; fixed-point scale; load/format; compare; add/subtract; multiply/divide with explicit scale/rounding; packed-field import/export; clear error/status reporting; checked bounds/overflow; examples and regressions.

**Excluded:** binary/IEEE floating point; arbitrary precision; locale/currency policy; automatic compiler operators/types; COBOL PICTURE compiler; VSAM/QSAM integration beyond buffer interoperability; dynamic global-vector changes to the compiler.

## Representation and contracts (provisional)

- An application-owned, fixed-size **decimal descriptor**, provisionally `VEC 7` (eight BCPL words), contains implementation-managed value, precision/scale and validity metadata. Its concrete layout is **undecided** until the ABI review. Do not directly dereference it in application code.
- Default capacity target is **31 significant decimal digits**, with an explicitly declared **scale** (number of digits after the decimal point). Scale range and descriptor storage must be settled in D.0.
- The decimal point is **not stored as a character in the packed numeric field**; the descriptor's scale supplies its interpretation. Preserve sign and distinguish +0/-0 policy.
- No aliasing of output and operands unless explicitly tested and approved; initial version may require distinct descriptors. Check destination capacity and rounding before mutation; failed operations should leave destination unchanged.
- Distinguish **success (0)** from errors such as invalid numeric input, invalid scale, overflow, divide by zero, invalid packed nibble/sign, insufficient destination space and unrepresentable rounding.
- BCPL strings and byte arrays have different representations. Formatting/parsing wrappers must follow the actual native compiler string ABI. Define counts, trailing blanks, EBCDIC encoding and null-termination policy, if any. Packed import/export uses **raw byte buffers** with explicit capacity and field length.
- Entry points are allocated documented global-vector slots only after the present runtime's registration convention is investigated. Linking an object alone must not be presumed to install global addresses.

## Provisional BCPL interface

| Procedure | Meaning |
| --- | --- |
| `DECINIT(d, scale)` | Initialize caller-owned decimal descriptor to zero at scale |
| `DECPARSE(d, text)` | Parse signed decimal text into descriptor at its chosen scale; explicit rounding/rejection policy |
| `DECFORMAT(d, text, capacity)` | Format value into BCPL-compatible text destination |
| `DECCOPY(dst, src)` | Copy value/scale under documented compatibility rule |
| `DECCMP(a, b)` | Return -1, 0, +1, or separate error status |
| `DECADD(dst, a, b)` | Exact addition with scale normalization or error |
| `DECSUB(dst, a, b)` | Exact subtraction with scale normalization or error |
| `DECMUL(dst, a, b)` | Multiply and round to destination scale |
| `DECDIV(dst, a, b)` | Divide and round to destination scale; report zero divisor |
| `DECRESCALE(dst, src, mode)` | Explicit scale conversion and rounding |
| `DECUNPACK(d, bytes, len, scale)` | Decode an external packed-decimal field |
| `DECPACK(d, bytes, capacity, len)` | Encode packed decimal for a record field |
| `DECSTATUS()` | Diagnostic for the most recent operation, if status not already in its return |

Specify status precedence, compare error behavior, format return length, numeric grammar, and rounding modes (initially reject-inexact or round-half-up; other policies optional) in D.0. These names are **proposals**, not allocated exports.

## Illustrative BCPL (not yet compiled)

```bcpl
// Proposed interface; string and output-buffer ABI await D.0.
LET START() BE
$(
    LET PRICE = VEC 7
    LET TAX   = VEC 7
    LET TOTAL = VEC 7
    LET TEXT  = VEC 31

    DECINIT(PRICE, 2)
    DECINIT(TAX,   2)
    DECINIT(TOTAL, 2)

    IF DECPARSE(PRICE, "123.45") ~= 0 RETURN
    IF DECPARSE(TAX,   "8.64")   ~= 0 RETURN
    IF DECADD(TOTAL, PRICE, TAX) ~= 0 RETURN
    IF DECFORMAT(TOTAL, TEXT, 128) < 0 RETURN

    WRITES(TEXT)       // Intended result: 132.09
    NEWLINE()
$)
```

The text buffer, return convention and functions `WRITES`/`NEWLINE` must be reconciled with the installed native compiler/runtime before using this as an executable test. The example conveys intended **client usage**, not established interface compatibility.

## Marches and gates

| March | Scope | Exit gate |
| --- | --- | --- |
| **D.0 — ABI and decimal contract** | Inventory runtime, globals, existing numeric routines and packed-decimal constraints; approve descriptor, scales, status/rounding, string and raw-byte ABI | Contract and test matrix committed; no assumptions left implicit |
| **D.1 — Representation and conversion** | DECINIT, parse, format, import/export, nibble validation | Round trips for positive, negative, zero, max-length, and invalid packed fields |
| **D.2 — Arithmetic core** | Compare, copy, add, subtract; overflow and scale tests | Independent expected-value tests run on MVS; no regression |
| **D.3 — Advanced arithmetic** | Multiply, divide, rescale and rounding, exception safety | Large operands, divide by zero, half-way cases and capacity boundaries verified |
| **D.4 — Application and release** | Record-field demonstration, optional link-edit, rebuild recipe and user documentation | Clean rebuild from Git, native regression panel, acceptance and object-promotion decision |

## Engineering discipline

Keep `BCPLDEC` optional and separately assembled, ideally with one cohesive source module per major facility only where the existing runtime pattern supports it. Do not modify `BCPLIO`, `BCPLMAIN`, the compiler, or historical libraries simply to make the API convenient. Candidate objects belong in `NATIVE_DEVOBJ` until explicit acceptance; do not promote or migrate binaries. Use `config/dspal.yaml` and actual `tools/datasets/dspal` conventions. Record observed JES output/condition codes, examples, test data, and gate acceptance in Git under `packaging/`. This milestone must neither delay M4 nor depend on QSAM.

**Primary technical references to verify during D.0:** IBM System/370 *Principles of Operation*, decimal-instruction definitions and operands; MVS 3.8 assembler/linkage environment. Modern COBOL documentation is comparative background, not evidence of an MVS 3.8 compiler contract.
