# Tape artifact release — post-release inventory and retirement audit

**Date:** 24 November 2026 EST. **Scope:** owner-directed housekeeping following qualified milestone closure; no new milestone. **Audited baseline:** `9f382203fcd6a5424cd916f304e3210c0f650212`. Compared with pre-milestone revision `f57428423a5112746e7764049f4c5e880f3ebdc7` using complete Git trees.

## Findings

354 added files, 21 changed files, no deletions (includes the subsequent Diátaxis discussion record). Of 375 changed paths, 339 are in packaging, 23 in tools, 12 MR10 regression sources, one config. The MR10 changes add literal EXP records; retain them and their independent expected-result data. The config change defines the historical CAMB_SOURCE population; retain it. No code changes are part of this housekeeping.

| Area | Tracked files at audit baseline | Markdown | Disposition |
| --- | ---: | ---: | --- |
| distribution/create-tape | 190 | 66 | Keep producer dependencies; retire consumed experiments after dependency proof |
| distribution/install-from-tape | 41 | 11 | Keep installer/semantic verification dependencies; retire trial wrappers |
| distribution/compiler-source | 39 | 13 | Keep selected source and encoding/fidelity evidence; retire consumed staging wrappers |
| distribution/manifest | 48 | 19 | Keep manifests/schema/evidence and tests |
| distribution/publication | 3 | 2 | Keep exact RC4 companion, notes and saved-evidence packager |
| distribution/docs | 7 | 0 | Keep frozen BT0003 inputs; replace with coherent generated documentation for a future candidate only |
| distribution/registry | 1 | 0 | Keep reservations and lifecycle records |
| milestones/tape-artifact-release | 32 | 32 | Keep authoritative closures and all historical records; current indexes should link to closure, not replay history |
| tools/distribution | 23 | 1 | Keep validator and useful evidence functions; review historical pilot/migration entry points |

There are 92 script/code files in the scoped distribution script directories and tools/distribution (excluding tests, JCL and assembly), many specific to one candidate or one incident. The create-tape README alone had 902 lines. The milestone document had over 2,200 lines. Current-facing README replacements link to the prior immutable Git revision rather than repeating historical instructions.

## Keep, retire, delete

**Keep permanently:** published RC4 archive/tape/tag, RC3 tape, all frozen manifests and registry reservations, RC4 companion and notices, historical sources and encoding decisions, all accepted closure/evidence records, private MVS receipts/seals/no-retry markers, MR10 source EXP changes and independent goldens, config/dspal.yaml, existing build and regression machinery. Never apply a new cleanup to the published release or its tag.

**Keep as current reusable capability:** manifest validation, JCL generation and dependency checks, standard-label AWS structure and tape inspection, source-to-PDS mapping, MVS IEBCOPY/IEBGENER install logic, exact MR10 semantic comparison, publication integrity checks. Preserve corresponding tests. A future implementation should derive candidate and target parameters from a manifest, not from a march name or old receipt timestamp.

**Keep temporarily at existing paths, but retire as operator entry points:** RC4 production and recipient/continuation, TA.4 verification, TA.7 clean-namespace runner, TA.8 exact-byte reviewer, RC2/RC3 production/readback/recipient and source staging helpers. Their work is accepted or superseded; they are not general release commands. Do not replay consumed operations. Retain the publication reviewer specifically for review of saved RC4 evidence; do not treat it as a generic publisher.

**Proposed removal from active checkout after verification:** historical scratch tape and TA.1 one-shot submission/restore/GO runners and their tightly coupled tests/JCL; TA.0 pilot execution/recovery/relocation wrappers; RC2/RC3 incident-specific orchestration and approval handling once reusable functions have been extracted and no current imports, test or workflow references remain. Preserve release-era source by immutable Git revision, preserve historical records and references. Do not delete tests that establish a retained contract. Do not move files merely to hide complexity: imports use hard-coded paths.

**Clear deletion candidates:** the six zero-byte .gitkeep placeholders under create-tape/{jcl,scripts,tests} and install-from-tape/{jcl,scripts,tests}; those directories contain tracked files. No file deletion is performed in this documentation housekeeping; confirm no references and remove with an approved cleanup.

## Demonstrated dependencies that prevent bulk deletion

- ta3-rc4-installer loads ta2-offline and reads RC3/RC4 manifests, registry and the TA.2 stage-space proposal.
- ta3-rc4-production loads ta3-rc4-installer, ta2-rc3-consolidated, ta2-rc2-produce-once, ta2-rc2-media-preflight and ta2-rc2-aws-review.
- ta2-rc3-consolidated loads RC2 producer preview, readback plan, bootstrap generator, offline renderer and installation acceptance/review helpers.
- ta2-rc2-produce-once loads rc2-bt0021-stage-once.py, which in turn loads the BT0021 preflight, staging draft, readiness, QSAM fidelity/reconciliation and target inspection/review helpers.
- ta7-clean-namespace loads ta3-rc4-recipient, ta4-mr10-verification, ta4-mr10-automatic-acceptance, ta2-rc2-mr10-review and earlier media/install helpers. TA.4 and TA.3 load RC3 and RC2 modules.
- ta8-rc4-review pins original tape SHA values, frozen manifest and the four accepted workarea evidence locations. This is a historical exact-candidate verifier, not a generic packaging workflow.

This is direct source inspection of central producer/installer/acceptance paths, not a complete transitive call graph or full line-by-line review of all 92 scripts. No runtime testing, private receipt review or local checkout was possible in this read-only GitHub audit; network access from the assistant workspace did not permit a clone.

## Recommended next cleanup

First, maintain short current README indexes and preserve historical versions. Next, agree on a small manifest-driven production/verification interface, extract common functions (including MVS/JES operations through existing tools), test them offline against retained fixtures and on an independently approved new MVS candidate when needed, then retire redundant executable wrappers with a verified dependency audit. Do not open another milestone or rewrite RC4 to achieve housekeeping.

TA.5 was already formally closed (qualified) on 23 November; the authoritative [closure](../milestones/tape-artifact-release/ta5-formal-qualified-closure-and-ta7-transition-20261123.md) remains unchanged. TA.6 remains N/A for RC4. The [final closure](../milestones/tape-artifact-release/ta8-formal-qualified-closure-and-milestone-completion-20261124.md) governs the release. Historical redistribution rights remain unresolved.
