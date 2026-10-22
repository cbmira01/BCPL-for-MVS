# R2TESTB — test-only second Runtime Extensions dispatcher

**Status:** R.2 development fixture, not a distributed or permanently
numbered Cambridge package. **MVS execution has not been verified.**

R2TESTB is extension B of the R.2 — Selective interoperability matrix.
It occupies **test-local G!299** (name `R2BSVC`) only in these probes.
G!299 was also a temporary R.0 query fixture; it is **not** a new entry
in the Global Number Registry. Do not ship this header/global assignment
as an application API. **G!203 remains permanently BCPLDEMO's.**

| Item | Test-only contract |
| --- | --- |
| Package ID | `R2TESTB` (`CL8`, space padded) |
| Assembler entry | `R2BDISP` |
| BCEX span | `R2BBEG` through `R2BEND` |
| Public test global | `R2BSVC:299` |
| QUERY opcode 0 | 8-word format-1 descriptor, API 3.2, bitmap 5, flags 0 |
| QUERY additional words | 77, 99 (test fixture values, not shared ABI fields) |
| Opcode 1 | Return 201 |
| Opcode 3 | Return 203 |
| Other opcodes | Return -2 |
| QUERY failure | -1 insufficient capacity, -3 invalid arguments |
| Dependencies, initializer, finalizer | None |

The dispatcher follows native R7/R8/R9 argument/result conventions. QUERY
checks the complete eight-word capacity before copying and does not write
on an error. Source and tests are under the R.2 interoperability probe;
use its [matrix instructions](../../probes/r2-interoperability/README.md).

The fixture intentionally differs from BCPLDEMO in its version,
descriptor size and opcode bitmap, exercising the **shared QUERY prefix**
without presenting its two appended words as a permanent shared contract.
No runtime or accepted MVS library object is altered.
