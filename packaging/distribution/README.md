# MVS tape distribution

This directory contains the source-controlled materials for a future self-contained Cambridge BCPL Programming System distribution on AWS virtual tape.

- [docs/](docs/) — source text for distribution documentation PDS members; release-specific content must describe the exact tape.
- [manifest/](manifest/) — tape file inventory, dataset attributes, sequence, and release identity (design and schema pending).
- [create-tape/](create-tape/) — development-host tools and MVS JCL for building and verifying tape media.
- [install-from-tape/](install-from-tape/) — MVS-resident JCL and installation materials intended to be distributed on tape.

GitHub `main` remains the source authority. Tape creation, restoration, labeling, bootstrap file ordering, and dataset overwrite policies require design, MVS 3.8J verification, and separate operational authorization.

This layout is scaffolding only. No tape image, executable installer, or verified unload/restore procedure is supplied yet.
