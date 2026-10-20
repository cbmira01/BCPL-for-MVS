# Milestone QSAM — Q.0 concurrent QSAM DCB execution evidence

**March:** Q.0 — Reconnaissance & contract (**open**).
**Execution date:** 20 October 2026, MVS 3.8J/TK5.
**Scope:** test-only System/370 assembler programs; not a working
BCPLQSAM service or a full BCPL executable.

The owner ran the tracked
[1/3/8/16-DCB generator](../bootstrap-toolchain/probes/q0-qsam-16-dcb-probes/README.md)
on Morkies and supplied the returned JES job numbers, all six
step-condition-code summaries and actual reader QOUT markers.

## Results observed

| Profile | JOB | Simultaneously open QSAM DCBs | WGO/RGO region | ASMWR | ASMRD | LKWR | LKRD | WGO | RGO | Actual QOUT |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| `one` | **2183 / Q0H1** | 1 | 256K | 0000 | 0000 | 0000 | 0000 | 0000 | 0000 | `Q0 01 DCB F1024 2 RECORDS PASS` |
| `three` | **2184 / Q0H3** | 3 | 256K | 0000 | 0000 | 0000 | 0000 | 0000 | 0000 | `Q0 03 DCB F1024 2 RECORDS PASS` |
| `eight` | **2185 / Q0H8** | 8 | 256K | 0000 | 0000 | 0000 | 0000 | 0000 | 0000 | `Q0 08 DCB F1024 2 RECORDS PASS` |
| `sixteen` | **2186 / Q0H16** | 16 | 256K | 0000 | 0000 | 0000 | 0000 | 0000 | 0000 | `Q0 16 DCB F1024 2 RECORDS PASS` |

Each profile used a *separately assembled and linked writer and reader*
with temporary `&&Q0Hnn` QSAM DASD datasets,
`RECFM=F,LRECL=1024,BLKSIZE=1024`.
In both GO steps the program maintained one checked, private,
1024-byte `GETMAIN RC` stage per OPEN DCB. The writer issued two
interleaved passes of PUTs across all the DCBs; the reader checked
both complete 1024-byte records for each dataset, the dataset-specific
header, binary final-byte sentinel, and EODAD; both programs CLOSEd
DCBs in reverse order and released their stages. The successful
return code and marker are the observed evidence for these intended
success paths, not a separate storage-leak measurement.

Generator-only `--check` validation also passed:
`one` 278 cards, `three` 474 cards, `eight` 964 cards,
`sixteen` 1748 cards, `sixteen-512` 1748 cards. The
generator's initial exact-delete-check error was corrected in commit
`76a262d`; the subsequent jobs compiled, linked and executed
successfully.

The user's final Git status was clean for JOBs 2183, 2184, 2185,
and 2186. Printer reports are under the owner's ignored
`workarea/qsam-q0-16-dcb/job-NNNN.txt` and MVS JES output, **not
committed to Git**. This record is based on owner-provided step
summaries and QOUT lines; it does not assert that full raw JES listings
were independently archived or audited.

## What is established and what remains

- **Established:** In standalone assembler WGO and RGO programs,
  sixteen simultaneously open F1024 QSAM DCBs plus sixteen separate
  1024-byte stages worked within **GO REGION=256K** on the tested
  MVS/TK5 system. Interleaved logical record I/O, EODAD and normal
  reverse-order cleanup were verified for the test.
- **No need to run the prepared `sixteen-512` fallback** for this
  successful configuration. The 256K value is an observed job
  parameter, not a general minimum or guaranteed ceiling.
- **Not established:** the full BCPLQSAM handle table,
  G!200 dispatcher and request/result vectors, shared
  `BCPLREG` registration, finalizer, actual BCPL program/runtime
  memory budget, error/abend recovery, or a universal 16-handle
  budget across record formats, BLKSIZEs and devices.

**Q.0 standalone concurrency investigation is complete for
F1024 on MVS/TK5. Q.0 remains open; Q.1 not started.**
Next work is the separate
[Milestone Runtime Extensions R.0 ABI review](runtime-extensions-r0-evidence-and-contract-20261020.md)
and outstanding exceptional QSAM error cases.
