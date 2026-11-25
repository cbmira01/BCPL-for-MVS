# DR.3 — Release candidate manual: migration and evidence

**Date:** 25 November 2026 EST  
**Baseline:** `a07fe5290c507c575269b2acd1e1ac7914a35704`  
**Status:** Eight-chapter working draft; owner review and commit authorization pending. DR.3 remains IN PROGRESS.

Destination: [How to Create a Release Candidate](../../../docs/project/How-to-Create-a-Release-Candidate.md).

**Boundary:** The [canonical execution guide](../../../tools/distribution/How-to-Create-a-Release-Candidate.md) remains at its existing path and retains the exact runnable sequence. The new manual is a review-oriented how-to with direct section links, decision gates, input/evidence contracts and qualifications, not a second command recipe. No path moves, authority transfer, release modification or retired-tool replay.

| Source / authority | Destination | Reconciliation |
| --- | --- | --- |
| [Canonical guide](../../../tools/distribution/How-to-Create-a-Release-Candidate.md), [driver](../../../tools/distribution/create-release), [distribution tool guide](../../../tools/distribution/README.md) | 1–8 | Retain existing execution authority; inspect actual plan/prepare/reserve/run/record, frozen template, per-operation effects and guards. New driver offline-tested only. |
| [Registry](../../distribution/registry/releases.yaml), [RC4 manifest](../../distribution/manifest/releases/BCPL-0.1.0-rc4.yaml), [manifest index](../../distribution/manifest/README.md), [validator](../../../tools/distribution/validate-manifest.py) | 1–4, 8 | Candidate vs lifecycle vs integration identities, expected next proposal not a reservation, append-only prior records, structural validation distinct from strict release rights gate. |
| [Source preparation index](../../distribution/create-tape/README.md), [compiler source](../../distribution/compiler-source/README.md), [BT0021 acceptance](../../distribution/create-tape/ta2-bt0021-qualified-acceptance-20261121.md), [encoding decision](../../distribution/compiler-source/rc2-job9330-reconciliation-acceptance-and-encoding-decision-20261120.md) | 4 | Explicit RC4 reuse versus new independently prepared PDSs; exact receipt schema, source subtree equality and seal; preserve historical encoding and provenance; no generalized source preparation claim. |
| [Driver](../../../tools/distribution/create-release), [release interface](../../../tools/distribution/release.py), [MVS helper](../../../tools/distribution/mvs_release.py) | 5–7 | Preflight submits query JES, single intent, 45 new targets, 135 prepared members, 21 write steps, 64 physical files, actual BT0001/BT0002 readback and three profile checks. |
| [TA.7 acceptance](../tape-artifact-release/ta7-clean-namespace-acceptance-20261124.md), [distribution index](../../distribution/README.md), [post-release audit](../../distribution/post-release-audit-20261124.md) | 1, 5–6, 8 | Historical actual owner-reported RC4 and BC0005 evidence; 42 PDSes/315 entries, 24 regressions/56 demos; NATIVE inventory only, no replay or new driver live claim. |
| [Private package acceptance](../tape-artifact-release/ta8-private-package-acceptance-20261124.md), [RC4 reviewer](../../distribution/publication/scripts/ta8-rc4-review), [publication authorization](../tape-artifact-release/ta8-rc4-publication-authorization-20261124.md), [formal closure](../tape-artifact-release/ta8-formal-qualified-closure-and-milestone-completion-20261124.md) | 7–8 | Exact accepted private bytes and separate publication decision, historical server-reported asset digest versus actual rehash. New package and registry result are private only. |

## Additional source-observed qualifications

- The driver's tracked clean-main gate uses --untracked-files=no; do not present it as checking every untracked file. It checks live remote main. A nonblocking local file lock covers stateful driver invocations but is not a system-wide MVS submission lock.
- Reserve writes the manifest exclusively and atomically replaces the registry via a pending file; the pair is not a cross-file transaction. Production requires committed authoritative reservation. Seal checks bind immediate evidence files and exact prepared-inputs.json; they do not prove provenance or rights.
- The driver compares the whole mr10-kit-compiler Git subtree to the frozen source revision and enforces allocation quantities 1–10000. Strict --release validation is not invoked during the ordinary structural gate. Historical qualified rights status is unchanged.
- Read-only live preflight submits query jobs; the marker precedes all persistent production writes and remains consumed on failure. A declined run can return zero. The driver may not succeed in writing a complete failure seal, so preserve all available evidence.
- The package's internal VERIFICATION.json is created before adding the archive name/digest to private result.json. It does not include a circular archive self-digest. The external ARCHIVE.sha256 and private result bind the package bytes.
- No fresh target job, release plan/reservation, registry edit, tape manipulation, raw private evidence reopening, asset rehash or actual repository unit test execution was performed during this draft. The owner-reported historical acceptance remains at its recorded scope.

DR.0 dependency qualifications persist. DR.5 must reconcile current instructions, anchor/dependency references and clause-level authority, including the existing canonical release how-to, before migration or retirement. The catalog will identify the new manual as a working draft and explicitly link the existing operational authority. No release state changed.
