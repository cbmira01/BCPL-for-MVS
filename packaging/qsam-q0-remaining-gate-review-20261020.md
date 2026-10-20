# Milestone QSAM — Q.0 remaining-gate review (2026-10-20)

**March:** Q.0 — Reconnaissance & contract. **Not closed.**
**Next March:** Q.1 — Linkage & OPEN/CLOSE skeleton (**not started**).
This is an evidence inventory and risk register; the owner approved
the Q.0 conservative error policy, shared Runtime Extensions R.0
architectural/finalization model, and 16-DCB experiment on
2026-10-20. This does not approve any new public opcode or change
the separately accepted 1024-byte private-stage ceiling.
The authorities are `packaging/milestone-qsam.md`,
`packaging/bcplqsam-public-interface.md`, the Q.0 approved staging
record, and `packaging/milestone-runtime-extensions.md`.

## Mechanisms already demonstrated on MVS/TK5

| Area | Evidence | Scope / limit |
| --- | --- | --- |
| BCPL-to-assembler dispatcher ABI | JOB 2157 | Test-only G!200 binding, not generic R.0 registration |
| QSAM sequential FB/V/VB | JOBs 2159–2162 | Selected formats/lengths, not full size ceilings |
| Fixed-record boundaries | JOBs 2163, 2165–2167 | Specific tested F/FB sizes |
| Zero-data-length V/VB | JOBs 2168–2169 | Successful RDW-only logical records |
| Non-opening DDNAME inquiry | JOB 2170 | Tested present/missing DD, not universal error recovery |
| Incompatible OPEN | JOB 2171 | S013-20 abend demonstrates a nonrecoverable path |
| Non-opening geometry / empty EOF | JOBs 2172–2173 | Tested JFCB FB offsets, sticky EOF policy |
| Staged pending READ retry | JOB 2174 | Single statically staged FB80 reader |
| Conditional storage ownership | JOB 2175 | Real GETMAIN/FREEMAIN; injected explicit rollback |
| Shared rollback handler | JOB 2176 | Real small allocations, injected failure through handler |
| Real conditional allocation refusal | JOB 2177 | Single 1 MiB GETMAIN returned R15=4 under REGION=256K; recovered |
| Post-OPEN V/VB INFO attributes | JOBs 2178–2179 | DCB RECFM, LRECL=100, BLKSIZE=104/404, enum 3/4, data maximum 96 |
| V/VB initial stage boundary | JOBs 2180–2181 | Effective LRECL=1024; 4/16/1024 RDW-inclusive lengths, 1020-byte data and binary sentinels |
| Sixteen concurrent stage allocations | JOB 2182 | **Sixteen** independent 1024-byte GETMAIN areas acquired, checked and freed; no DCB OPEN |
| Concurrent live QSAM DCBs | **JOBs 2183–2186** | F1024 1/3/8/16 simultaneously OPEN DCBs, private stage per DCB, two interleaved records, REGION=256K; all six steps RC=0000 in each |

## Remaining questions before owner accepts Q.0

1. **Real conditional allocation refusal — resolved for tested case.**
   [JOB 2177](qsam-q0-real-getmain-refusal-evidence-20261020.md)
   observed actual R15=4, rollback and later successful allocation after
   one bounded 1 MiB GETMAIN under REGION=256K. No general guarantee
   of abend recovery or record-size support follows.
2. **Initial record-stage ceiling — design decision approved.**
   [JOBs 2180–2182](qsam-q0-1024-byte-stage-evidence-20261020.md)
   passed, and the owner approved a **1024-byte total private stage per
   BCPLQSAM handle** (F/FB up to 1024 data; V/VB up to 1020).
   The isolated [JOBs 2183–2186](qsam-q0-concurrent-dcb-evidence-20261020.md)
   have **passed on MVS**, including **16 simultaneously OPEN F1024
   QSAM DCBs and sixteen 1024-byte stages at GO REGION=256K**.
   This closes the **standalone concurrency experiment**, not the
   production BCPLQSAM handle-table or complete BCPL
   runtime/application budget. The 512K fallback was not needed.
   Production over-limit rejection and end-to-end resource accounting
   remain to be tested.
3. **Effective INFO attributes — V/VB test geometry confirmed.**
   [JOBs 2178/2179](qsam-q0-post-open-info-evidence-20261020.md)
   verified post-OPEN RECFM/LRECL/BLKSIZE at LRECL=100; JOBs 2180/2181
   checked effective attributes at LRECL=1024. The owner approved
   `INFO.result!7` as the dataset-specific application-data maximum:
   F/FB=LRECL; V/VB=LRECL minus four. Actual BCPL `QSAMSVC` INFO,
   exceptional formats and negative geometry remain unverified.
4. **Error semantics — design approved, failure evidence still open.**
   The [owner-approved Q.0 policy](qsam-q0-error-and-r0-design-decisions-20261020.md)
   preserves the v1 numeric codes, uses reliable pre-OPEN validation,
   and marks a returned CLOSE failure unusable with **uncertain
   resource ownership**, rather than blindly retrying or freeing
   live structures. JOB 2171 still proves an S013-20 abend path;
   no generic MVS abend recovery is promised. SYNAD/GET/PUT and
   exceptional CLOSE behavior still require targeted MVS evidence.
5. **Shared optional-module lifecycle — model approved; R.0 in progress.**
   The owner approved linker-selected bounded `BCPLREG`,
   duplicate/missing package rejection before START, optional
   descriptor-carried finalizers called once in reverse order
   **before BCPLIO.IOFIN and BCPLMEM.MEMDRAIN**. `STOP(n)` retains n;
   a returned finalizer failure on ordinary `FINISH` emits a
   diagnostic and sets **RC=8**. The **exact assembler layout,
   register ABI and error report format** still need R.0 evidence,
   testing and further approval. The
   [candidate R.0 binary layout review](runtime-extensions-r0-candidate-binary-abi-20261020.md)
   distinguishes source-supported facts from **new, unapproved**
   byte offsets, package IDs and finalizer register conventions.
   No generic finalizer is implemented.
6. **Owner Q.0 gate review.** Reconcile the accepted version-1
   BCPLQSAM Public Interface Specification with supported evidence,
   record permitted deferrals, and explicitly approve Q.0 before Q.1.
   A run of standalone assembler probes does not close Q.0 by itself.

**Production BCPLQSAM remains unimplemented.** Neither BOOT_OBJ nor the
accepted core BCPL runtime was changed by the Q.0 resource tests.
