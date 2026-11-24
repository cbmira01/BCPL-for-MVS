# TA.8 formal qualified closure and milestone completion — 24 November 2026 EST

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release — FORMALLY CLOSED (qualified)  
**TA.8 — Release Audit and Controlled Publication:** FORMALLY CLOSED (qualified)  
**Owner direction:** “Close TA8, and give me a prompt for a post-milestone discussion.”

## Accepted published release

[Cambridge BCPL Programming System for MVS 3.8J — 0.1.0-rc4](https://github.com/cbmira01/BCPL-for-MVS/releases/tag/v0.1.0-rc4)

Direct GitHub metadata inspection confirms release ID 457049551,
published 2026-11-24T16:42:17Z (11:42:17 EST), draft false,
prerelease true, tag v0.1.0-rc4 resolved to
5fca3d6b83b7db6a29cd863e1c977c12a21876f2. The tag is the release preparation checkpoint,
distinct from frozen program-source revision
e910de51c19c09698be139e33084a90401511cc9.

Uploaded asset ID 787993716: BCPL-0.1.0-rc4-BC0004.zip,
254181 bytes, state uploaded. GitHub's SHA-256 digest exactly
matches the accepted private package:
a3d47d7a3591c3f8fa826c205729a9488423f31a3a7e0c10ed87357d3404e80e.
The archive contains the accepted BC0004 image with AWS SHA-256
7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1.
The assistant verified metadata and the server-reported asset digest,
not an independent download and rehash. The release is not immutable;
preserve the tag and asset bytes. External SHA256SUMS was not attached;
the release description supplies the correct archive digest instead.
The accepted private package contains internal SHA256SUMS and the
required companion documentation and notices. Keep private review
receipts and the original archive backed up.

## Final acceptance

TA.0–TA.3 CLOSED (qualified); TA.4 CLOSED; TA.5 CLOSED (qualified);
TA.6 N/A for RC4 (not PASS); TA.7 CLOSED (qualified); TA.8 CLOSED
(qualified). The milestone is complete under its owner-approved
revised scope.

The released standard-labeled AWS contains 21 logical datasets
and 64 physical files. Actual MVS acceptance restored all three
profiles, 42 PDSes / 315 member entries across fresh namespaces
on the existing system. MR10 and COMBINED passed 56 demonstrations
and 24 semantic regressions (80/80 functional cases, 326 JES steps).
TA.4 also accepted the isolated ICINT19 rebuild. The final private
review reported four saved MVS evidence seals verified, with exact
RC4 bytes preserved. The assistant did not independently inspect
the owner-local raw receipts.

The MR10 Kit Compiler is independently usable. Native runtime,
libraries, extensions and Cambridge Compiler sources are distributed
as work in progress; native compiler absent, no native functional
acceptance or alternate HLQ/independent IPL certification claimed.
Historical redistribution rights remain unresolved under the
owner-approved preservation-first policy; no new legal permission
is asserted. Mandatory RC4 companion guide supersedes stale BT0003
notes. Broader semantic documentation refactoring is explicitly
deferred to a separate future milestone.

Preserve RC4, RC3, all accepted evidence and consumed markers,
frozen manifests and reservation entries, and the public release
tag. No new MVS execution or candidate is needed. Do not reopen
accepted work without a demonstrated defect.

## Post-milestone discussion

Review the completed project stage and lessons learned, including
ease of modification, reconstruction, testing and release.
Discuss semantic documentation refactoring as a prospective
separate milestone; evaluate other project priorities including
native compiler reconstruction. No new milestone, march number,
implementation, repository refactoring or MVS action is authorized
by this closure. Agree on scope and priorities with the owner first.
