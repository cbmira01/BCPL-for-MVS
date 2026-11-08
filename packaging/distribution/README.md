# MVS tape distribution

This directory contains the source-controlled materials for a future self-contained Cambridge BCPL Programming System distribution on AWS virtual tape.

- [docs/](docs/) — source text for distribution documentation PDS members; release-specific content must describe the exact tape.
- [manifest/](manifest/) — tape file inventory, dataset attributes, sequence, and release identity (design and schema pending).
- [create-tape/](create-tape/) — development-host tools and MVS JCL for building and verifying tape media.
- [install-from-tape/](install-from-tape/) — MVS-resident JCL and installation materials intended to be distributed on tape.

## Reconstruction automation decision and distribution research

**Owner-approved direction and documented implementation status:**

- [Clean-room reconstruction automation decision (4 November 2026)](clean-room-reconstruction-automation-decision-20261104.md) — full purge and restart from zero, one scoped approval, independently runnable tools, optional console progress, and regression tests separate from reconstruction.
- [Step 3 safety-hardening closure and JOB 357 evidence (5 November 2026)](clean-room-reconstruction-step3-closure-20261105.md) — real-MVS ACTIVE/BLOCKED and CLEAR acceptance; live reconstruction remains disabled.
- [Next automation phase: guarded live integration (5 November 2026)](clean-room-reconstruction-live-integration-plan-20261105.md) — single-TK5 integration planning; no destructive-run authorization.
- [Single-TK5 JES submission-control candidate (5 November 2026)](clean-room-reconstruction-submission-control-design-20261105.md) — cooperative project submission lock, explicit lease delegation, and offline tests.

**Historical research and unimplemented proposals:**

- [Tape operations and practice](tape-operations-design-discussion-20261103.md) — attachment versus mounting, MVS read/write exercises, safeguards and proof of tape round trips.
- [Earlier clean-room automation discussion](clean-room-automation-design-discussion-20261103.md) — historical checkpoint/resume proposal, now superseded.
- [Distribution tape production automation](tape-production-automation-design-discussion-20261103.md) — manifest-driven JCL, controlled tape writing, independent installation and release gates.

GitHub `main` remains the source authority. Tape creation, restoration, labeling, bootstrap file ordering, and dataset overwrite policies require design, MVS 3.8J verification, and separate operational authorization.

This layout is still production-distribution scaffolding: no full distribution tape or executable installation package has been accepted. On 8 November 2026 MVS verified both the [seven-member documentation-PDS round trip](create-tape/scratch-pds-roundtrip-acceptance-20261108.md) and the [eight-member relocatable object-library round trip, including native linkage and execution](create-tape/object-library-tape-roundtrip-acceptance-20261108.md).

## Tape inspection and verified scratch experiment

- [Scratch tape round-trip acceptance (8 November 2026)](create-tape/scratch-pds-roundtrip-acceptance-20261108.md) — four real JES jobs; IEBCOPY unload and restore; IEBCOMPR RC 0. This is not yet a distribution installation.
- [Object-library tape round-trip acceptance (8 November 2026)](create-tape/object-library-tape-roundtrip-acceptance-20261108.md) — four real JES jobs, verified BTO001 tape, binary IEBCOMPR RC 0, and native regressions 00/03 PASS using the restored eight-member object PDS.
- [Tape inspection capability](tape-inspection-capabilities-20261108.md) — Hercules `hetmap` already maps standard labels, physical files and datasets; requirements for a more detailed read-only report remain a future decision.
