# Milestone QSAM — Q.1 JOB 6620 explicit-GO-DCB evidence (2026-10-26)

**March:** Q.1 — Linkage & OPEN/CLOSE skeleton.
**Disposition:** **PASS for the tested three-DD explicit-DCB configuration; Q.1 remains OPEN and NOT ACCEPTED.**

## Configuration and evidence custody

JOB 6620 (`Q13DD`) exercised the opt-in temporary JCL variant from [commit e37477c](https://github.com/cbmira01/BCPL-for-MVS/commit/e37477cb644c0c2eb987c73ccd4e54ecbbe6a466). On the **GO reader** DDs Q00, Q01 and Q02 it supplied `DCB=(RECFM=F,LRECL=1024,BLKSIZE=1024)`. WGO had already written temporary F1024 datasets with corresponding DCB attributes. GO ran at `REGION=256K`.

The original Q.1 generator, `bcplqsam.asm`, public interface, and installed MVS datasets were not modified for this test. The operator's ignored workarea retains:

- `workarea/bcplqsam-q1/q13dd-go-dcb-6620-summary.txt`
- `workarea/bcplqsam-q1/q13dd-go-dcb-6620-report.txt`

The outcomes below are owner-reported from those preserved JES files. Their full contents were not committed or independently reacquired for this record.

## Observed JOB 6620 result

| Step | Observed result |
| --- | --- |
| ASMWR | RC=0000 |
| LKWR | RC=0000 |
| ASMA | RC=0000 |
| ASMN | RC=0000 |
| ASMR | RC=0000 |
| ASMQ | RC=0000 |
| ASMG | RC=0000 |
| LKED | RC=0000 |
| WGO | RC=0000 |
| **GO** | **RC=0000** |

**JOB RESULT: SUCCESS.** Assembler statements flagged: **0**; highest assembler severity: **0**.

All three non-opening JFCB preflights reported `R3=00000080`, `R5=00000400`, `R6=00000400` (tested F1024 geometry). Three independent OPEN calls issued handles **1, 2, 3**. INFO validated geometry; CLOSE operations succeeded; repeated CLOSE of a retired handle returned expected `QS_ERR_HANDLE=-7`. The native application printed **`BCPLQSAM Q1 THREE DD PASS`**.

## Relationship to previous evidence

- **JOB 6617:** first OPEN returned `QS_ERR_OPEN=-6`; GO RC=0008.
- **JOB 6618:** `Q1O:PREFORM` located pre-OPEN `QCVFORM` rejection.
- **JOB 6619:** RDJFCB succeeded and DDs were allocated, but raw R3/R5/R6 were all zero in GO without reader `DCB=`.
- **Q.0 JOB 2172:** successful non-opening JFCB preflight used explicit DD geometry on the step issuing RDJFCB. See [Q.0 evidence](qsam-q0-geometry-empty-eof-evidence-20261020.md).
- **Q.1 JOB 6620:** repeating F1024 attributes on the three GO reader DDs supplied nonzero preflight geometry and the native OPEN/INFO/CLOSE path passed.

This supports the specific explanation that missing **GO-step JCL geometry** caused the observed Q.1 preflight rejection. WGO's geometry alone did not fill the tested GO JFCB fields. It does **not** establish that explicit JCL DCB is mandatory for production.

## Contract, safety and remaining gates

The approved [public API](bcplqsam-public-interface.md) exposes OPEN by an already allocated DDNAME; it does not currently require an explicit JCL `DCB=` operand. A production policy for existing datasets with omitted DD geometry therefore needs owner review. Q.0 [JOB 2171](qsam-q0-open-incompatible-evidence-20261020.md) showed unrecovered **S013-20** on an invalid FB80/801 OPEN; [approved error policy](qsam-q0-error-and-r0-design-decisions-20261020.md) requires rejecting known unsafe geometry before OPEN and does not promise universal abend recovery. Do not bypass the guard because RDJFCB returned success with empty geometry.

JOB 6620 does **not** verify omitted-DCB existing datasets, non-DASD devices, other record formats, the full native 16-handle campaign, 17th-handle refusal/slot reuse, failed-OPEN rollback and resource accounting, returned-CLOSE failures, generic FINISH/STOP(8) finalization, or native regression. It does not authorize changes to `bcplqsam.asm`, permanent MVS datasets, JES runs or the public contract.

**Q.1 — Linkage & OPEN/CLOSE skeleton remains OPEN and NOT ACCEPTED. Do not begin Q.2.**
