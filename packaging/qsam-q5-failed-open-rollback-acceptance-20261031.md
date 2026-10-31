# Milestone QSAM — Q.5 failed-OPEN rollback acceptance

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **Q.5 — Hardening & release** (IN PROGRESS)  
**Owner decision:** **ACCEPTED 31 October 2026** — owner explicitly directed "Step 1, accept. Proceed with step 2".  
**Scope:** Only the corrected, test-only failed-OPEN rollback experiment; not Q.5 or Milestone QSAM closure, nor promotion of any installed object.

## Native evidence and interpretation

- **Q5RFCOMP JOB 8144:** resident demoted Cambridge compilation of the corrected BCPL application with an explicit terminal `FINISH`; ICINT19 and recovery steps RC=0000. Recovered 311-line assembler SHA-256 `f68e03ea2cdc8bc9a25a8f4df49c8c8cc1fd4b54056eed1a858be952b207d4ed`.
- **Q5RBFIN JOB 8145:** owner-authorized one-shot test-only 4,154-card deck SHA-256 `e315f22394c9a0fa7118abfaf330c73869936406cebe2e1f8ae4acc7306e4b70`; **all ten IFOX/IEWL/WGO/GO steps RC=0000**, JES SUCCESS and highest RC=0000, zero assembler flagged statements/severity, and one exact `BCPLQSAM Q5 OPEN ROLLBACK PASS` BCPL record.
- The first Q01 OPEN really completed before the *test-only* injected refusal of the subsequent private-stage allocation. The native rollback used the real `QSMCLS1` CLOSE path. Surviving Q00 operations, fresh Q01 OPEN, handle validation, explicit CLOSE and normal BCPL `FINISH` were exercised.
- The console and MVS hardcopy each recorded `E L P R T X P`. Final `X` counters are five zero fullwords. The seventh `P` is explained by the *actual assembled diagnostic overlay*: after `QFPEX` `SVC 35` at `0010CA`, execution falls into `Q5RPST` at `0010CC`. This is a test-only WTO fall-through, not evidence of a second rollback; no production `bcplqsam.asm` change.
- Initial evidence harvesting returned `console.rc=1` and `evidence.rc=1` due to a literal one-space JES `STARTED/ENDED` test, despite original two-space Hercules lines. These collector failures are preserved and **are not the native GO status**. The later dedicated `check-q5-rollback-finish.py` contains strict JOB 8145 evidence/provenance tests. The original WSL evidence files were not rewritten.

## Acceptance boundary

This validates the **injected post-OPEN stage-refusal and successful returned-control rollback CLOSE**, not actual MVS GETMAIN exhaustion, returned exceptional CLOSE, recovery from an MVS abend, or all DCB/device geometries. Historical GO S0C1 failures JOBs 8142–8143 remain unmodified evidence. Accepted `BOOT_OBJ` and installed MVS datasets were not changed.

**Next bounded Q.5 activity:** test the approved returned-CLOSE `QS_ERR_CLOSE=-14` / uncertain-ownership quarantine policy using an explicitly distinguished **test-only post-CLOSE R15 override**, with no claim that MVS returned an error. Any native JES submission requires separate approval. Further geometry/resource, packaging, full regression, clean-from-Git reconstruction and promotion reviews remain outstanding.

**Source of evidence:** [Q.5 experiment record](qsam-q5-open-rollback-experiment-20261030.md), preserved operator JOB 8144/8145 output and original Hercules console/hardcopy logs.
