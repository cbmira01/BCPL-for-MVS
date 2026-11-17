# TA.0 — Release Architecture, Inventory, and Manifest: formal qualified closure

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.0 — Release Architecture, Inventory, and Manifest  
**Owner decision:** **ACCEPTED AND CLOSED (qualified)**  
**Decision date:** 17 November 2026  
**Evidence/source checkpoint:** GitHub `main` `f1999d59ab1b473bd4cbe670ca232ffdee2af13c`  
**Next march:** TA.1 — Multi-Dataset Tape Mechanics (**READY FOR DESIGN/PREFLIGHT; no tape-write approval**)

## Owner direction and bounded acceptance

The owner directed: **“Move to TA.0 closure without delay. Give me a handoff prompt for TA.1.”** Treat this as authorization to close TA.0 **on a qualified architecture and inventory basis**, not as authorization to write tape, reserve release identity, approve redistribution, or declare a release candidate.

TA.0 established the approved release boundary, selected dataset/member ownership and source mapping, design-stage single-manifest schema, bootstrap labels, dependency checks and retained development-system evidence. It **did not** prove every production candidate input or complete the tape producer, load-library transfer, recipient installer or publication.

## Accepted design baseline

- **Product:** Cambridge BCPL Programming System for MVS 3.8J on a standard-labeled Hercules AWS virtual tape. A release declaring `native_compiler: absent` is allowed; the native-running Cambridge Compiler remains unfinished. `CAMBCOMP` does not substitute for it.
- **Selection:** one design inventory at `packaging/distribution/manifest/ta0-inventory.yaml` describing 20 proposed logical tape datasets, including two reserved bootstrap positions and 18 selected PDSes with **127 members** (**79 MR10**). The positions after `BT0002` are **design proposals**, not a frozen release.
- **Bootstrap:** `BCPL.BT0001` = EBCDIC FB80 readable instructions; `BCPL.BT0002` = MVS-only installer PDS unload; contiguous `BCPL.BTnnnn` aliases reflect **logical** 1-based MVS dataset sequence and `LABEL=(n,SL)`, not Hercules physical-file indices.
- **Profiles:** MR10-only, native-components-only (not a native BCPL compiler), combined; keep Coroutine Support distinct from historical `BLIB`, and three System Extensions distributed but optional at IEWL application link time.
- **Manifest:** one Git-controlled per-release manifest and one cross-release release/VOLSER registry; `config/dspal.yaml` is only a development dataset map. Candidate identities, site HLQ, JCL, integrity, provenance, rights and producer/recipient dependencies remain fail-closed.
- **DCB / transfer direction:** FB80 PDS `PO/FB/80/800`, `MR10_LOAD` `PO/U/0/6144`, bootstrap sequential FB80; IEBCOPY **sequential unload DCB is distinct from PDS source/restored DCB** and must be proven for each content class by TA.1/TA.2. Never assume a single prior `V/816/820` unload instance applies universally.

See the [governing milestone](milestone-tape-artifact-release.md), [TA.0 architecture](../../distribution/manifest/ta0-release-architecture-and-inventory.md), [schema](../../distribution/manifest/schema-v1-design.md), [nomenclature](../../architecture/runtime-and-library-nomenclature.md), and [approved scoped-release decision](../../distribution/release-without-native-compiler-decision-20261116.md).

## Actual development-MVS verification retained

The owner reported a successful, no-JES-resubmission, SHA-256-pinned [TA.0 binary reconciliation](../../distribution/manifest/ta0-binary-evidence-reconciliation-20261117.md):

| Observation | Qualified result |
| --- | --- |
| Selected FB80 relocatable objects | 14/14: 3 `EXT_OBJ`, 1 `MR10_OBJ`, 10 `BOOT_OBJ` |
| Printer decoded records/bytes | 902 FB80 records, 72,160 bytes, each member reconciled to saved pinned evidence |
| Historical decoder schema | Exactly two pre-pagination receipts reconciled without rewriting original evidence |
| `MR10_LOAD(ICINT19)` directory | JOB 9060, formatted entry `000000`, attributes `02E2` |
| Development `ICINT19` executable use | JOB 9061, eight original scalar/vector `MRREGRES` steps, RC=0000, interpreted `CODE=0`, expected `RP:` output; twice reverified without JES resubmission |

The private printer reports, binaries and receipt index reside under ignored `workarea/ta0-mvs-evidence-20261117/`, not in Git. The above are the owner's observed tool outputs; the raw private report bytes were not independently available in the assistant's workspace. This **does not** establish original DASD-byte identity or that a tape-restored `ICINT19` runs.

Existing accepted **single-dataset** scratch PDS/object tape round trips from 8 November are retained as bounded background evidence. They do not satisfy TA.1's **two logical datasets on one volume** requirement.

## Explicit exclusions and follow-on gates

**Not accepted by closing TA.0:**

1. Source-to-resident-object provenance, Git-to-MVS revision binding, the eight historical IFOX/IEWL build-job report sets, and generated `BLIB`/`COROUTIN` build ancestry. The source/build dependency mapping exists, but it is not proof of binary derivation. Validate candidate inputs before release production (TA.2, TA.4/TA.5, TA.7/TA.8 as applicable).
2. Per-member author/license/redistribution clearance; the audit's 127 `UNREVIEWED` statuses remain unresolved. Mandatory before release production/publication under TA.8.
3. Tested load-library `RECFM=U` IEBCOPY unload/restore, restored GO, exact unload DCB, multi-dataset SL label sequencing, volume retention, filemarks and failure handling: **TA.1**.
4. Final manifest and version/source SHA/VOLSER reservation, deterministic producer, artifact integrity: **TA.2**; site-independent MVS-only bootstrap/installation, allocation/JCL and no-overwrite policy: **TA.3**.
5. Full 12-case MR10 `TEST:/EXP:/RP:/CODE=` human review, 11+17 demos and installed MR10 independence: **TA.4/TA.7**; native Core Runtime, `BLIB`, Coroutine Support and System Extensions installed verification: **TA.5/TA.7**.
6. A native-running Cambridge Compiler is **absent** in the approved scoped-release design; TA.6 is **N/A only for a candidate explicitly declaring `native_compiler: absent`**, never a generic PASS. Complete release including that compiler requires TA.6.

No production AWS tape, release candidate, unique VOLSER reservation, completed release manifest, tape-write permission, dataset overwrite or publication follows from this closure. Preserve all unresolved findings instead of marking them PASS. Do not reopen TA.0 without a demonstrated architecture/inventory defect.

## Formal disposition and transition

**TA.0 — Release Architecture, Inventory, and Manifest: CLOSED (qualified), owner directed 17 November 2026.**

**TA.1 — Multi-Dataset Tape Mechanics: READY FOR DESIGN/PREFLIGHT**. Prepare and review a fresh-scratch-media plan and JCL/host guards; obtain **separate explicit owner authorization** for any new media initialization, mount/write, guest dataset creation or other state change. A ready plan is not authority to execute. See [TA.1 kickoff](ta1-kickoff-20261117.md).

**TA.2–TA.8:** NOT STARTED by this decision. The complete milestone **Tape artifact release** remains IN PROGRESS.
