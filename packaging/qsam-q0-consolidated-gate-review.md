# Milestone QSAM — Q.0 consolidated gate matrix

**Disposition: Q.0 — Reconnaissance & contract IN PROGRESS; Q.1 — Linkage & OPEN/CLOSE skeleton NOT STARTED.** This is an owner-approved **preparation** of remaining test-only evidence work, not a new execution report or Q.0 closure. The GitHub baseline was `5b993fa41547c50555fe3680bc6d65585be50267` (25 October 2026). Preserve the official Q.0–Q.5 numbering and titles.

| Q.0 requirement | Proven or approved | Remaining verification / boundary |
|---|---|---|
| Native R7/R8/R9, G!200, BCPL vectors | JOB 2157 test-only dispatcher | Production BCPLQSAM ABI in Q.1 |
| F/FB/V/VB QSAM and binary records | JOBs 2159–2169, 2180–2181 | Production READ/WRITE Q.2/Q.3; no unlimited record-size claim |
| Non-opening DD inquiry, geometry, empty EOF | JOBs 2170–2173 | Preflight only prevents known hazards, not every abend; JOB 2171 S013-20 remains unrecovered |
| Staged retry, independent records, zero-byte V/VB | JOBs 2168–2169, 2174 | Public BUFFER_TOO_SMALL and EOF/zero-data semantics in Q.2/Q.3 |
| Checked allocations, rollback, real refusal | JOBs 2175–2177, 2182 | Transactional OPEN and actual handle accounting in Q.1 |
| Post-OPEN INFO/DCB mapping | JOBs 2178–2179 | Public INFO result vectors in appropriate implementation gate |
| 16 simultaneously OPEN QSAM DCBs/stages | JOBs 2183–2186: standalone 256K | Full native BCPL/coexisting process resource test below |
| BCEX/BCRG v1, registration/finalization | Accepted Runtime Extensions R.0/R.1, including JOBs 2760–2783 | QSAM finalizer implements approved R1 ABI; no new registrar |
| Optional source/installed selection | Accepted R.2–R.5; BCPLDEMO and BCPLTIME T.0–T.1 | QSAM-specific packaging later, without touching accepted references |
| Full native BCPL process with 16 staged DCBs and finalizer | `q0-integrated-16-dcb` batch prepared | **MVS NOT YET RUN:** FINISH and STOP(8) JES IDs, IFOX/IEWL/GO RCs, MAP, GO markers, cleanup |
| Returned-CLOSE error ownership and exceptional MVS outcomes | Approved conservative `qsam-q0-error-and-r0-design-decisions-20261020.md` | Returned CLOSE failure remains unverified in QSAM. Decide explicitly at Q.0 gate whether to defer implementation-specific tests to Q.1/Q.5 |
| Public QUERY, modes, formats, errors | `bcplqsam-public-interface.md` approved design | Native BCPL caller/examples and production status vector tests after Q.0 approval, in Q.1–Q.3 |

## New batch acceptance and evidence checklist

For `Q0NFIN` and `Q0NSTP`, preserve the generated JCL, actual returned JES payload job IDs, step RCs, IFOX severity, actual IEWL MAP/XREF with selected `BCEX` export and 44-byte BCRG, WGO/GO output, and all failure messages. Check stage/DCB counts as exercised by the private finalizer. Both execute from **accepted installed Core Runtime and BLIB** using temporary test-only object code. The STOP case's GO RC=8 must reflect the caller's requested STOP(8), not a returned finalizer failure. For FINISH, GO RC=0 and no `BCPLREG 2001` diagnostic.

Success under GO REGION=256K establishes one native-process configuration, **not** a region-size guarantee for fully implemented BCPLQSAM handles, arbitrary record formats or devices. The approved 1024-byte **total** stage bound per handle remains unchanged: F/FB up to 1024 data bytes, V/VB up to 1020 data bytes with four RDW bytes private.

## Exit decision still required

Q.0 is an evidence-backed *contract* march, not a production installation. At the explicit owner gate review, identify which originally open requirements have been discharged by accepted Runtime Extensions R.0–R.5 and which belong to production Q.1–Q.5. The owner must specifically accept or defer exceptional returned-CLOSE error testing, and review any unsuccessful 256K/512K MVS runs without suppressing abends. No speculative CLOSE recovery, automatic Q.1 start, Q.0 closure, or new status codes are authorized by this batch.

**Rollbacks:** No pre-existing MVS PDS modifications; temporary `&&` resources are disposed of by job lifecycle (and normal finalizer for private stage allocations). No production `QSAMSVC:200`, no compiler changes, no new regressions numbered 163+, and no reopened Runtime Extensions or BCPLTIME marches.
