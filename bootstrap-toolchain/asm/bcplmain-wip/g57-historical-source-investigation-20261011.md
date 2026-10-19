# G57 OS/CMS marker — historical source investigation

**Status:** Negative evidence / contract unresolved. No runtime edits.
2026-10-11. Continuation of `runtime-globals-45-56-57-investigation-20261011.md`.

## Source coverage

The recursive repository tree lists **only**
`richards-bcpltape/sys3/bcpl/libhdr` beneath `richards-bcpltape/sys3/`.
There is no SYS3 BCPLMAIN implementation or SYS3 assembler macro body
in this checkout to inspect for setting or reading G57.

Inspected the surviving assembler macro collections
`richards-bcpltape/km10/bcplmac` and
`richards-bcpltape/km10/comacro`, specifically their global equates
and GETGLOB/SETGLOB machinery, and searched for references to 57,
the OS/CMS marker, and global-vector access syntax. These macros
provide generic access mechanisms (`GETGLOB`, `SETGLOB`,
`4*&GLOB.(G)`, `4*&NUM.(G)`) but **no observed explicit G57
initializer or consumer**. Their presence does not mean an expanded
calling module cannot use literal 57.

## Evidence table

| Evidence | What it establishes | What it does not establish |
| --- | --- | --- |
| SYS3 LIBHDR line 22: `GLOBAL 57 IS SET TO 'OS' OR 'CMS'` | Intended discriminator and possible symbolic values | Whether text denotes a BCPL string, packed word, pointer, literal name, or runtime encoding |
| SYS3 repository tree | Only SYS3 LIBHDR survives in this checkout | No proof of absence from historical systems outside the repo |
| KM10 BCPLMAC and COMACRO global-name tables | G45 PARMS explicitly called `PARAMETER STRING`; no analogous G57 equate identified | G57's physical representation |
| KM10 generic GETGLOB/SETGLOB macros | Mechanism can read/write any numbered global | Evidence of an actual G57 read or write |
| WIP startup `10-bootstrap-and-system.asmfrag` | No observed store to byte offset 228 (G57) | Whether future/other runtime modules initialize it |

## Important adjacent finding: G45

Both KM10 macro sets explicitly have `PARMS EQU 45` annotated
`PARAMETER STRING`. This **strengthens**, but does not complete,
the G45 contract: it identifies a parameter-string global, without
establishing the pointer representation, allocation, lifetime, or
relationship between native EXEC PARM and compiler-local options.

## Decision

**Do not implement G57 yet.** Its presence is documented but the
representation is not recoverable from the searched surviving SYS3
material, and no reader was identified. Assigning `'OS'`, an encoded
integer, or a fabricated string pointer would invent an ABI.

A productive next bounded task is G45: trace concrete PARMS reads,
writes, storage allocation, and its relationship to `FINDPARM` in
the actual KM10 assembler/routines and Cambridge compiler sources.
If G57 remains desirable, first obtain an additional historical
BCPLMAIN or usage source showing G57 storage or read semantics.

No regressions were run; executable baseline unchanged.
