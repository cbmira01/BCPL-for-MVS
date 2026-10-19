# Native BCPL library

This directory stages **BCPL source extension modules** for the native
Cambridge-to-System/370 compiler pipeline. It is separate from the
historical BLIB runtime.

## Historical BLIB is not duplicated here

The original BLIB lives at
`richards-bcpltape/bcplib/bcpl/blib`. The generated MR10-compatible
whole-BLIB compilation unit is at
`workarea/bootstrap-cambridge/demoted/blib` and is produced by
`native-compiler/bootstrap-cambridge/make-demoted.py --blib-only`.
Do **not** maintain another derivative of historical BLIB here.
The tested native packaging strategy makes BLIB available as a
link-edit object resource in `HERC02.BCPL.OBJ(BLIB)`.

## Staged native extension sources

The following portable helper modules have been **copied unchanged**
from the reconstruction's MR10-oriented `library/` source directory:

| Source | Exports (GLOBAL numbers) | Dependency |
| --- | --- | --- |
| `integer-utils.bcpl` | ABS 101; MIN 102; MAX 103; SIGN 104; GCD 105; IPOW 106 | BCPL arithmetic |
| `string-utils.bcpl` | STRLEN 107; STRCMP 108; STRCPY 109; STRCAT 110; STRCHR 111 | G85 GETBYTE, G86 PUTBYTE |
| `memory-utils.bcpl` | MEMCPY 112; MEMSET 113; MEMCMP 114; VECCOPY 115; VECCLEAR 116 | G85 GETBYTE, G86 PUTBYTE for byte routines |

Source provenance: `library/{integer-utils,string-utils,memory-utils}.bcpl`.
These are **native-candidate source files**, not a confirmed resident
object library, and copying them does not establish native compile,
link or runtime acceptance.

The chosen G101–G116 assignments are reconstruction-local, inherited
from `library/GLOBALS.md`; retain them for compatible applications
until a checked consolidated native ABI map is established. They do
not replace or override the historical BLIB global assignments.
String operations assume ordinary length-prefixed BCPL byte strings.
Callers must supply sufficiently large destination storage.
MEMCPY has forward-copy semantics; overlapping ranges are unsupported.

## Intended usage and packaging

Compile each source as a separately compiled native BCPL module, then
link it with an application at native link-edit time. Once successfully
validated, stage the resulting load/object artifacts in a separately
named extension PDS member, not in the historical BLIB member.
Keep the library modular; applications should only link needed objects.

A first validation rung should compile `integer-utils.bcpl` with a
small BCPL application exercising G101/G105/G106; a second should
exercise `string-utils.bcpl` and `memory-utils.bcpl` with the
existing native G85/G86 byte primitives. Confirm actual independent
object linking rather than relying solely on concatenation of sources.

## Deferred ports

- `line-io.bcpl`: postpone runtime validation until native RDCH
  (G13), EOF and newline semantics are established; the new stream
  I/O march tracks that work.
- `char-utils.bcpl`: review the bootstrap ASCII assumptions against
  the native EBCDIC character model before using classification or
  case conversion.
- `numeric-conversion.bcpl`: review minimum signed integer,
  string conversion, and native machine-code generation behavior.
- `random.bcpl`: review long-integer arithmetic portability and
  expected deterministic sequence under the native target.
- `getvec-freevec.bcpl`: **do not port** the MR10 arena allocator
  as G87/G88; canonical BCPLMAIN already provides GETVEC/FREEVEC
  with MVS GETMAIN/FREEMAIN.
- `coroutines.bcpl`: requires a separate native context-switch
  implementation and global ABI reconciliation.

## Validation state

Entry native regression baseline: **90/90 PASS** (000–089).
The three staged extension modules are not yet native-regression
validated. Their promotion to resident object members is contingent
on focused TK5 tests and a full native regression sweep.
