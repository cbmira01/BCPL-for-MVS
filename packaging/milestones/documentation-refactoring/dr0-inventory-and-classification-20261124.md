# DR.0 — Inventory and Classification — initial census

**Status:** IN PROGRESS; preliminary census, not a completed semantic inventory or accepted disposition plan.  
**Date:** 24 November 2026 EST  
**Baseline:** GitHub main `ed0f8066859ed4e1a310bbb91520d0d629c5dca3`  
**Method:** Read-only recursive Git tree inspection and review of the handoff's governing documentation. Tree response was not truncated. No local full checkout, full document content review, dependency scan or MVS execution is claimed.

## Census

2,577 tracked blobs, 3,014 total tree entries; 857 paths ending in .md (case-insensitive), including ten empty files. These are path counts, not manual counts or semantic classification.

| Location | Markdown files |
| --- | ---: |
| Root | 4 |
| bootstrap-toolchain | 21 |
| cambridge-compiler | 2 |
| config | 1 |
| docker | 1 |
| docs | 27 |
| mr10-kit-compiler | 29 |
| packaging | 554 |
| richards-bcpltape | 1 |
| standard-library | 1 |
| system-extensions | 13 |
| tests | 192 |
| tools | 11 |
| Total | 857 |

Within packaging: root index 1, applications 2, architecture 11, archive 175, distribution 130, evidence 5, milestones 209, operations 21. Within tests: root index 1, bootstrap 147, coroutines 13, runtime-extensions 13, system-extensions 18. These groups are physical locations, not dispositions.

Seven additional .txt files in packaging/distribution/docs/ are frozen draft BT0003 inputs (README, INSTALL, DATASETS, COMPILE, VERIFY, RELEASE, LICENSE). Preserve unchanged. Original historical documentation and embedded comments, manifests and JCL require separate scope review beyond the extension count.

## Preliminary classification and audit leads

| Source / area | Information class / authority | Candidate action (not authorized) |
| --- | --- | --- |
| Root README | Navigation and current product/project status | Revise after reconciliation; link to authoritative manuals |
| LICENSE.md, THIRD-PARTY-NOTICES.md, PUBLIC-RELEASE-AUDIT.md | Legal/provenance and release audit | Preserve; review references without altering rights claims |
| docs/README.md and educational briefings | Primarily explanations; secondary educational material | Review by subject; consolidate where useful |
| docs/Rebuild-BCPL-for-MVS-from-source.md | Canonical operational reconstruction how-to | Retain authority; review alongside manual rebuild |
| docs/Manual-Rebuild-BCPL-for-MVS.md | Maintenance/reconstruction instructions | Inspect distinct manual tasks and overlap |
| docs/Guide-to-*.md (ten zero-byte paths) | Unfilled placeholders | Removal candidates after dependency and architecture review |
| packaging/architecture/runtime-and-library-nomenclature.md | Normative vocabulary mixed with prior proposals | Reconcile accepted status against closure records without changing terms |
| packaging/architecture/global-number-registry.md | Normative assignment registry | Preserve assignments and authority |
| packaging/architecture/runtime-contract-v1.md, stack-check-contract.md | Technical contracts | Preserve authority; review reference integration |
| packaging/milestones/qsam/bcplqsam-public-interface.md | Public interface contract | Preserve authority; consider approved reference integration |
| system-extensions/bcplqsam/README.md and Q.1/Q.2 runbooks | Component documentation and development-era procedures | Inspect status and dependencies; separate active guidance from evidence |
| packaging/milestones/, packaging/archive/, packaging/evidence/, tests/ | Mixed governance, engineering evidence, instructions | Classify individually or by demonstrably homogeneous series; retain accepted records |
| config/dspal.yaml | Machine-readable development dataset map | Preserve separate authority |
| packaging/distribution/manifest/, registry/releases.yaml | Release manifests and identity/lifecycle authority | Preserve frozen entries and registry semantics |
| packaging/distribution/publication/, distribution/docs/ | RC4 companion and frozen input documentation | Preserve unchanged; companion supersedes BT0003 |
| tools/distribution/How-to-Create-a-Release-Candidate.md | Active how-to with verification qualification | Retain status: new driver offline-tested, actual MVS run not established |
| richards-bcpltape/ | Historical primary material | Preserve; do not apply Diátaxis or rewrite |

Large files are review leads, not defects: IFOX briefing 67,412 bytes; MVS 3.8 briefing 54,991 bytes; bootstrap regression README 59,261 bytes; Tape artifact release governing document 176,965 bytes. Accepted records are not targets for shortening.

## Next inventory work

1. Review reader-facing and operational documents for content, intended audience, Diátaxis type, authority, duplication and stale status.
2. Identify authoritative contracts and historical/accepted records; classify recurring evidence families with explicit exceptions.
3. Map references from Markdown, configuration, source, tests and release tooling, including frozen paths and generated documentation. Record exact scope and unresolved dependencies.
4. Propose dispositions and consolidation candidates; record open questions for DR.1, not a physical architecture decision.
5. Present completed inventory for owner review before closure or transition.

No files moved, deleted or rewritten during this census. No MVS operation or release production authorized. No separately named charter was located in the recursive path review; the approved handoff and governing discussion supply the objectives.
