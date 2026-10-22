# BCPLDEMO — example optional extension

**Status:** R.2 development candidate. **First actual MVS execution PASS: JOB 3075 (22 October 2026).** The complete R.2 matrix remains pending.
**Owner-approved:** Permanent `DEMOSVC:203` global; package `BCPLDEMO`.

BCPLDEMO is a maintained, deliberately simple reference example for people
building their own System Extension, Standard Library, or User/Site Library.
It is not a special case in BCPLMAIN and is never linked automatically.
The same `BCPLREG` and `BCEX` rules apply to real packages.

## Distinguish the three names

- **`BCPLDEMO`** is the eight-byte package identity in BCEX/BCRG.
- **`DMODISP`** is the assembler `ENTRY` symbol relocated by IEWL.
- **`DEMOSVC`** is the name assigned to **G!203** in the BCPL header.
  Calling `DEMOSVC(op,vector,capacity)` calls the registered dispatcher.

A `GLOBAL` declaration reserves a compiled numeric reference. It **does not**
select an object, install its address, or discover an absent package.
The application-specific `BCPLREG` includes an explicit requirement for
`BCPLDEMO` and lists its `BCEX` extent; the link-editor includes the actual
objects. The R.1 registrar validates everything before calling `START`.

## Published teaching API (version 1.0 candidate)

| Opcode | BCPL call | Successful result | Errors |
| --- | --- | --- | --- |
| 0 | `DEMOSVC(0, info, capacity_words)` | 6; writes the six-word QUERY v1 descriptor | -1 short; -3 bad arguments |
| 0 | `DEMOSVC(0, 0, 0)` | 6; no write | — |
| 1 | `DEMOSVC(1, values, capacity_words)` | 3; writes fullwords `10, 20, 30` | -1 short; -3 null/negative |
| Other | `DEMOSVC(op, 0, 0)` | — | -2 unsupported opcode |

`info` and `values` are **BCPL word pointers**, not byte addresses.
Their capacity is counted in 32-bit fullwords. The caller owns both vectors.
Both supported operations check for insufficient capacity before writing;
no partial buffer is returned. `QUERY` reports `(format=1, major=1,
minor=0, length=6, opcode_bitmap=1, capability_flags=0)`, with bit zero
advertising opcode 1. All other bits are zero. Both operations are stateless;
there is no initializer or finalizer. As in any native BCPL ABI, genuinely
accessible caller storage must be supplied; arbitrary fabricated pointers
cannot be made safe through this interface.

## Physical source files

| File | Purpose |
| --- | --- |
| `bcpldemo.h` | Public BCPL declaration and package-local opcode constants |
| `descriptor.asm` | Linker-relocatable `BCEX` export of G!203, no dependencies |
| `dispatcher.asm` | Assembler implementation and the two example opcodes |
| `../../probes/r2-interoperability/registry-demo.asm` | Application-selected registration example (see actual path below) |

The executable BCPL demonstration currently repeats the header's GLOBAL
number explicitly because the demoted Cambridge compiler's input header
handling is not yet part of this example's exercised build procedure.
The canonical number remains the [Global Number Registry](../../../packaging/global-number-registry.md).

## Test-only MVS job (R.2 extension A)

Run from repository root after the bootstrap/toolchain environment is built:

```sh
python3 -m unittest discover -s \
  bootstrap-toolchain/probes/r2-interoperability -p 'test_*.py' -v
python3 bootstrap-toolchain/probes/r2-interoperability/make-job.py --check

tools/bootstrap/compile-mvs \
  bootstrap-toolchain/probes/r2-interoperability/demo.bcpl \
  --job-name R2DCOMP \
  --output workarea/r2-demo.s370.asm

python3 bootstrap-toolchain/probes/r2-interoperability/make-job.py \
  --generated workarea/r2-demo.s370.asm

bash tools/mvs/submit-jcl workarea/runtime-extensions-r2/r2-demo.jcl
```

Then inspect the real JES job using `tools/mvs/job-summary` and
`tools/mvs/dump-report-for-job`. Expected GO condition code **0000**, and
exactly one live application output marker:

```
R2 BCPLDEMO G203 PASS
```

This result was **observed exactly once in MVS JOB 3075**. All six IFOX
steps, IEWL, and GO returned 0000. The real MAP shows `BCPLREG`,
`DMOBEG`, `DMOEND`, and `DMODISP`, with no application-trailer G!203
registration. See [the reviewed JOB 3075 evidence](../../../packaging/runtime-extensions-r2-bcpldemo-job-3075-evidence-20261022.md).
Further R.2 acceptance tests remain pending.
All assembled candidates and the load module use temporary `&&` datasets;
`BOOT_OBJ` is read-only and `BOOT_DEVOBJ` is not modified. The generator
writes authenticated JCL only under ignored `workarea/` with mode 0600.
Do not commit generated decks or operator credentials.

## Learning path and next acceptance gates

1. Examine the header and notice that only **one global slot** is public.
2. Examine `descriptor.asm`: its `F'203',A(DMODISP)` is relocated by IEWL.
3. Examine the BCRG in the R.2 probe directory: it explicitly selects
   this package and declares the application requirement.
4. Examine the dispatcher argument registers, capacity checks, QUERY
   six-word prefix, and caller-owned `GETVALUES` result.
5. Run the stand-alone demonstration and read the IEWL MAP.
6. In the full R.2 matrix, try absent and independently selected packages.

To adapt the example for a new package, **do not reuse G!203**. Obtain an
appropriate allocation, change the package identity and dispatcher/header
names, publish an ABI, update selected BCEX/BCRG tables, and add collision,
absence, and independent-linkage tests. A site-private slot is not a
portable, universally reserved number. R.3 will provide the polished
end-user tutorial and distribution recipe after R.2 acceptance.
