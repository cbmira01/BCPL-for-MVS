# BCPL library

Library modules are BCPL files compiled alongside an application. They share the BCPL global vector. Slot assignments are in [GLOBALS.md](GLOBALS.md).

| File | Functions or purpose |
| --- | --- |
| `random.bcpl` | SRAND, RAND, RANDRANGE, RANDSEED |
| `integer-utils.bcpl` | ABS, MIN, MAX, SIGN, GCD, IPOW |
| `char-utils.bcpl` | ISDIGIT, ISALPHA, ISSPACE, TOUPPER, TOLOWER |
| `string-utils.bcpl` | STRLEN, STRCMP, STRCPY, STRCAT, STRCHR |
| `memory-utils.bcpl` | MEMCPY, MEMSET, MEMCMP, VECCOPY, VECCLEAR |
| `numeric-conversion.bcpl` | ATOI, ITOA, HEXTOI, ITOHEX |
| `line-io.bcpl` | READLINE, WRITELINE |
| `getvec-freevec.bcpl` | HEAPINIT, GETVEC, FREEVEC |
| `coroutines.bcpl` | CREATECO, DELETECO, CALLCO, COWAIT, RESUMECO |

## Compile with a program

```sh
tools/mr10/compile-and-run --results \
  "$(tools/mr10/current-icint)" \
  mr10-kit-compiler/bcpl-demo/quicksort/quicksort.bcpl \
  +mr10-kit-compiler/library/random.bcpl
```

## Important limits

| Area | Rule |
| --- | --- |
| Strings | Packed BCPL strings store their length in byte zero. The caller must provide enough destination space. |
| Memory | `MEM*` sizes count bytes. `VEC*` sizes count words. Overlapping MEMCPY areas are not supported. |
| Random | Deterministic Park-Miller generator; not for security use. `RANDRANGE(N)` returns 0 when `N<=0`. |
| Numbers | `IPOW` returns 0 for negative powers; `ITOHEX` accepts non-negative numbers. |
| Lines | `READLINE` returns -1 for end of input and truncates overlong lines to the supplied limit. |
| Storage | Call `HEAPINIT` before `GETVEC`. Free storage with `FREEVEC`. |
| Coroutines | Depends on the allocator and on the machine-specific `CHANGECO` service. |

The historical global slots run through 86. Reconstructed runtime services use 87–95; other project library functions use 96–159. See `GLOBALS.md` before assigning a new slot.

Run library tests with `tools/mr10/run-regression-panel --category standard-library`; the allocator and coroutine tests are in the storage and coroutines categories.
