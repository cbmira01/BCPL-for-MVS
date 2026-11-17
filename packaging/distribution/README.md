# MVS tape distribution

This directory contains the source-controlled materials for a future self-contained Cambridge BCPL Programming System distribution on AWS virtual tape.

- [docs/](docs/) — source text for distribution documentation PDS members; release-specific content must describe the exact tape.
- [manifest/](manifest/) — authoritative release selection, position-based `BCPL.BTnnnn` aliases, dataset mapping and sequence (schema pending).
- [create-tape/](create-tape/) — development-host tools and MVS JCL for building and verifying tape media.
- [install-from-tape/](install-from-tape/) — MVS-resident JCL and installation materials intended to be distributed on tape.

## TA.0 architecture and approved scoped releases

- [Release without the native compiler](release-without-native-compiler-decision-20261116.md) — owner decision and conditional TA.6 gate.
- [TA.0 release architecture and inventory](manifest/ta0-release-architecture-and-inventory.md) — curated member selections, mappings, dependencies and incomplete compiler artifacts.
- [Manifest schema v1 design](manifest/schema-v1-design.md) — canonical inventory, validation and consistency requirements.
- [Design-stage selected-member YAML inventory](manifest/ta0-inventory.yaml) and [read-only validator](../../tools/distribution/validate-manifest.py) — 20 proposed logical datasets, 127 members; not a release candidate.
- [TA.0 provenance and recipient-JCL dependency audit](manifest/ta0-provenance-and-dependency-audit.md) — 110 Git-backed selections, 2 generated, 15 MVS binaries, ten JCL adaptation blockers; none release-accepted.

**TA.0 is in progress; no march is closed.** No tape or publication is authorized.

## Release identity and VOLSER tracking

- [Version and VOLSER registry design (8 November 2026)](release-version-and-volser-registry-decisions-20261108.md) — one proposed Git-controlled registry for cross-release version and VOLSER allocation; per-release manifests remain authoritative for tape dataset order. No registry is implemented.

## Governing Tape artifact release milestone

- [Tape artifact release](../milestones/tape-artifact-release/milestone-tape-artifact-release.md) — nine owner-approved marches **TA.0–TA.8**; **TA.0 ready for kickoff**, no completed release or tape authorization.
- [Owner-approved MR10 regression reporting and human MVS verification](mr10-regression-exp-manual-verification-decision-20261116.md) — the 12 standard cases print literal `EXP:` next to actual `RP:`; MVS recipient verification is documented human review, **not** an automatic MVS semantic comparator. WSL automated `RP:`/`CODE=` checks remain.

## Expanded release payload decisions (16 November 2026)

- [Approved release scope expansion](release-payload-scope-decision-20261116.md) - include native Coroutine Support, `BCPLDEMO`, `BCPLTIME`, `BCPLQSAM`, and the independently usable MR10 Kit Compiler with all 11 language demos, 17 BCPL demos, and its 12-case panel. MVS-only **human-reviewed** golden-result verification of the panel is an **unmet release gate**, not a completed feature (subsequent owner decision above). No tape release has been accepted.

## Native Cambridge Compiler release and tape naming decisions

- [Owner-approved distribution decisions (8 November 2026)](native-cambridge-compiler-distribution-decisions-20261108.md) — initial native Cambridge Compiler product scope, position-based `BCPL.BTnnnn` dataset aliases, canonical source-to-tape-to-install mapping, self-documenting bootstrap and release lifecycle. This remains a design direction, not a completed installer or release.

## Reconstruction automation decision and distribution research

**Owner-approved direction and documented implementation status:**

- [Clean-room reconstruction automation decision (4 November 2026)](clean-room-reconstruction-automation-decision-20261104.md) — full purge and restart from zero, one scoped approval, independently runnable tools, optional console progress, and regression tests separate from reconstruction.
- [Clean-room batch-population improvement closure (9 November 2026)](clean-room-batch-reconstruction-closure-20261109.md) — operator-reported 12m46s reconstruction and separate passing full six-suite regression; `--batch-populate` remains opt-in, and the guarded controller remains separate.
- [Step 3 safety-hardening closure and JOB 357 evidence (5 November 2026)](clean-room-reconstruction-step3-closure-20261105.md) — real-MVS ACTIVE/BLOCKED and CLEAR acceptance; live reconstruction remains disabled.
- [Next automation phase: guarded live integration (5 November 2026)](clean-room-reconstruction-live-integration-plan-20261105.md) — single-TK5 integration planning; no destructive-run authorization.
- [Single-TK5 JES submission-control candidate (5 November 2026)](clean-room-reconstruction-submission-control-design-20261105.md) — cooperative project submission lock, explicit lease delegation, and offline tests.

**Historical research and unimplemented proposals:**

- [Tape operations and practice](tape-operations-design-discussion-20261103.md) — attachment versus mounting, MVS read/write exercises, safeguards and proof of tape round trips.
- [Earlier clean-room automation discussion](clean-room-automation-design-discussion-20261103.md) — historical checkpoint/resume proposal, now superseded.
- [Distribution tape production automation](tape-production-automation-design-discussion-20261103.md) — manifest-driven JCL, controlled tape writing, independent installation and release gates.
- [Multi-dataset tape and append experiment (deferred, 8 November 2026)](multi-dataset-tape-and-append-experiment-20261108.md) — observed automatic unmount after one-dataset write; outstanding retention, positioning, standard-label sequence, and safe append/recovery tests.

GitHub `main` remains the source authority. Tape creation, restoration, labeling, bootstrap file ordering, and dataset overwrite policies require design, MVS 3.8J verification, and separate operational authorization.

This layout is still production-distribution scaffolding: no full distribution tape or executable installation package has been accepted. On 8 November 2026 MVS verified both the [seven-member documentation-PDS round trip](create-tape/scratch-pds-roundtrip-acceptance-20261108.md) and the [eight-member relocatable object-library round trip, including native linkage and execution](create-tape/object-library-tape-roundtrip-acceptance-20261108.md).

## Tape inspection and verified scratch experiment

- [Scratch tape round-trip acceptance (8 November 2026)](create-tape/scratch-pds-roundtrip-acceptance-20261108.md) — four real JES jobs; IEBCOPY unload and restore; IEBCOMPR RC 0. This is not yet a distribution installation.
- [Object-library tape round-trip acceptance (8 November 2026)](create-tape/object-library-tape-roundtrip-acceptance-20261108.md) — four real JES jobs, verified BTO001 tape, binary IEBCOMPR RC 0, and native regressions 00/03 PASS using the restored eight-member object PDS.
- [Tape inspection capability](tape-inspection-capabilities-20261108.md) — Hercules `hetmap` already maps standard labels, physical files and datasets; requirements for a more detailed read-only report remain a future decision.
