# TA.8 — Private RC4 package technical acceptance — 24 November 2026 EST

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.8 — Release Audit and Controlled Publication  
**Status:** Private package technical PASS (qualified); awaiting separate publication approval.  
**Implementation:** 72352864d136b7c1ee8386e6e0830d2bdaa3b50c

## Owner-reported actual saved-evidence result

```text
TA.8 PRIVATE PACKAGE PASS: 4 MVS evidence seals; 326 functional steps; RC4 exact bytes.
Archive SHA256: a3d47d7a3591c3f8fa826c205729a9488423f31a3a7e0c10ed87357d3404e80e
Evidence: workarea/ta8-rc4-20261124T151859675204Z
```

The committed `packaging/distribution/publication/scripts/ta8-rc4-review --prepare` verifies the pinned four saved acceptance receipts and their complete checksum seals, the 326 functional JES steps and saved semantic verdicts, the RC4 and RC3 tape digests, and frozen RC4 manifest digest. It packages the unchanged AWS, frozen manifest, RC4 companion guide, full MIT license, third-party notices, original archive README files and INDEX, and internal SHA256SUMS. It verifies each archived entry against its source before reporting PASS. The reviewer uses existing semantic verdicts; it does not rerun MVS or independently recompute every golden comparison.

Private archive: `workarea/ta8-rc4-20261124T151859675204Z/BCPL-0.1.0-rc4-BC0004.zip`  
Archive SHA-256: `a3d47d7a3591c3f8fa826c205729a9488423f31a3a7e0c10ed87357d3404e80e`  
Accepted AWS SHA-256: `7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`.

The owner supplied the successful actual local output. The assistant has not opened the private archive, receipt JSON or raw evidence directly. The registry's original reservation entries remain unchanged; its lifecycle mapping now records the owner-reported verified private package.

## Publication decision

Under the owner's preservation-first decision, the complete companion package must accompany the historical tape. Unresolved historical redistribution rights remain disclosed; this is not legal clearance. The companion guide supersedes stale BT0003 prose; native components remain work in progress and TA.6 is N/A. The release identity must remain 0.1.0-rc4 / BC0004 and publication must not change the accepted bytes. Recommend a GitHub prerelease using tag v0.1.0-rc4 (subject to confirmation that it is unused), associated with the release-preparation commit containing the companion materials, and explicitly recording the frozen program-source revision e910de51c19c09698be139e33084a90401511cc9. Attach the exact verified ZIP and publish its SHA-256; verify the uploaded/downloaded asset against the recorded digest before declaring public delivery complete.

Separate explicit owner publication approval is still required. The current connected GitHub tools do not expose release creation or binary asset upload and cannot access the owner's local workarea. Publication therefore requires an authorized transfer route, such as the owner's GitHub release UI. No release/tag/asset was created by this record. No further MVS operation is required. TA.8 remains open; formal closure and milestone completion follow actual publication verification and owner direction.
