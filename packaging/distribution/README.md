# MVS tape distribution

This directory contains the source-controlled materials for a future self-contained Cambridge BCPL Programming System distribution on AWS virtual tape.

- [docs/](docs/) — source text for distribution documentation PDS members; release-specific content must describe the exact tape.
- [manifest/](manifest/) — tape file inventory, dataset attributes, sequence, and release identity (design and schema pending).
- [create-tape/](create-tape/) — development-host tools and MVS JCL for building and verifying tape media.
- [install-from-tape/](install-from-tape/) — MVS-resident JCL and installation materials intended to be distributed on tape.

## Research and design discussions (3 November 2026)

These are proposals and study plans, not approved production procedures:

- [Tape operations and practice](tape-operations-design-discussion-20261103.md) — attachment versus mounting, MVS read/write exercises, safeguards and proof of tape round trips.
- [Clean-room reconstruction automation](clean-room-automation-design-discussion-20261103.md) — existing stage map, explicit operator checkpoints, resumability and JES evidence requirements.
- [Distribution tape production automation](tape-production-automation-design-discussion-20261103.md) — manifest-driven JCL, controlled tape writing, independent installation and release gates.

GitHub `main` remains the source authority. Tape creation, restoration, labeling, bootstrap file ordering, and dataset overwrite policies require design, MVS 3.8J verification, and separate operational authorization.

This layout is scaffolding only. No tape image, executable installer, or verified unload/restore procedure is supplied yet.
