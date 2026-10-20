# Milestone QSAM — Q.0 V/VB effective DCB INFO observations

**Status:** JOBs **2178** (`QS0INFV`) and **2179** (`QS0INFVB`) PASS on
MVS 3.8J/TK5, 20 October 2026. This is standalone assembler evidence;
`QSAMSVC:200` / public `QS_INFO=5` remains unimplemented.

The owner supplied complete JES, IFOX and IEWL listings and QOUT reports.
Both jobs completed six steps at RC=0000:
ASMWR, ASMRD, LKWR, LKRD, WGO, RGO.

| Field checked **after OPEN** | JOB 2178, V | JOB 2179, VB |
| --- | --- | --- |
| Raw DCB `RECFM` (DCB+36) | `X'40'` | `X'50'` |
| Effective LRECL (DCB+82) | 100 | 100 |
| Effective BLKSIZE (DCB+62) | 104 | 404 |
| Project public format enum (local mapping) | 3, `QS_FMT_V` | 4, `QS_FMT_VB` |
| Dataset payload maximum, LRECL - 4 RDW | 96 bytes | 96 bytes |
| Records read and checked, then EODAD | 15 | 15 |

The actual QOUT records were:

```text
Q0 INFO V OPEN DCB ENUM3 DATA96 PASS
Q0 INFO VB OPEN DCB ENUM4 DATA96 PASS
```

The readers verified the post-OPEN DCB fields, mapped the format byte
to the project's **already specified** numeric enum, computed
100 - 4 = 96, and read all 15 test logical records. The writer and
reader used temporary `&&Q0DISK`; the data set was deleted, and no
production object library was changed. The owner's `git status`
showed the checkout was clean after the experiment.

**Limits:** Neither program populated a BCPL `QSINFO` result vector,
created a production handle, verified arbitrary DCB geometry, or
established a 1024-byte V/VB record. The dataset's 96-byte payload
bound is **not** a globally approved BCPLQSAM size ceiling.

The next isolated profiles are described in
[Q.0 candidate 1024-byte stage probes](../bootstrap-toolchain/probes/q0-qsam-ceiling-probes/README.md).

**Q.0 remains open; Q.1 has not started.**
