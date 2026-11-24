# Cambridge BCPL Programming System for MVS 3.8J — 0.1.0-rc4

Release candidate 0.1.0-rc4; standard-labeled AWS virtual tape BC0004.

## Included

- Independently usable MR10 Kit Compiler with ICINT19, libraries, build JCL, demonstrations and regressions.
- Native Core Runtime, Base Library (historical BLIB), Coroutine Support Library, System Extensions and historical Cambridge Compiler sources as work in progress.

The native-running Cambridge Compiler and CAMBCOMP are not included. Native functional acceptance is not claimed.

## Verification

All three installation profiles passed on MVS 3.8J in fresh dataset namespaces on the existing system: 42 PDSes and 315 restored member entries. MR10 and COMBINED passed 56 demonstrations and 24 semantic regressions, 80/80 total. Independent-system IPL and alternate HLQ verification were not performed. Native components are installation/inventory accepted only.

## Installation

Download and extract `BCPL-0.1.0-rc4-BC0004.zip`. Read RC4-README.md before installing. This guide supersedes the older BT0003 draft notes. Keep the accompanying manifest, license and historical attribution files with the tape.

## Copyright and preservation

Original project work is MIT-licensed. Historical material retains its original authorship and copyright status. Historical redistribution rights remain unresolved; the project claims no new rights over that material. See the included LICENSE.md, THIRD-PARTY-NOTICES.md and historical archival notes.

## Exact artifact identity

- Frozen program-source revision: `e910de51c19c09698be139e33084a90401511cc9`. RC4 includes separately generated bootstrap/installer material.
- Archive SHA-256: `a3d47d7a3591c3f8fa826c205729a9488423f31a3a7e0c10ed87357d3404e80e`
- Extracted AWS SHA-256: `7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`
