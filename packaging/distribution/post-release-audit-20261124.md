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

## Approved consolidation and first retirement

The owner approved the consolidation and removal plan. Baseline `52850c4c21b6b10db3174304f5cc778bc95283fe` preserves the exact pre-cleanup source.

- Static inspection covered all 92 original scoped distribution scripts, 83 retained Python test files and 15 retained distribution JCL files for references to the TA.1 Track A/B executable family. No literal dependency on the retired runners, tests or decks was found outside that family. Scratch VOLSER exclusions remain in the later code. This is a bounded filename/job-name scan, not proof of every possible dynamically constructed path or a whole-repository test run.
- Remove 11 TA.1 runners/helpers, 11 dedicated test files, six TA.1 experiment JCL decks and six empty .gitkeep placeholders: 34 files total. Earlier scratch/object experiments are outside this retirement; all TA.1 Markdown and closure records are retained unchanged. The [pre-cleanup source tree](https://github.com/cbmira01/BCPL-for-MVS/tree/52850c4c21b6b10db3174304f5cc778bc95283fe/packaging/distribution/create-tape) resolves historic source references.
- Add [tools/distribution/release.py](../../tools/distribution/release.py), an offline, manifest-driven interface for writer JCL, three recipient PROC profiles, HETMAP structure review and the MR10 TEST/RP/EXP/CODE comparator. It takes explicit candidate source DSNs, allocations and site parameters. It does not perform a live release or replace operational safety gates.
- Ten focused offline unit tests passed on the assistant workspace, including a frozen RC4 writer and all three profile rendering digests derived by comparing the historical rendering logic against the actual RC4 selection and allocation fields retrieved from GitHub. The workspace could not clone GitHub; the RC4 fixture used those reconstructed fields, not a full repository checkout or original tape bytes. Exact Git blob hashes of both tested Python files were verified before commit.
- The remaining legacy RC2–RC4 execution chain is kept intact. In particular the TA.2 strict candidate check pins its producer SHA, and accepted orchestration and private receipt paths are candidate-specific. Do not redirect them or remove their shared functions until the generic replacement has been verified against actual MVS on a new approved candidate. No legacy test or actual MVS execution is claimed here.
- Retained issue: an older TA.2 offline renderer test expects Q00001 for a BC0001 fixture while the production VOLSER contract explicitly rejects Q00001. This is a source-inspection finding, not a test executed in this workspace. Keep historical tests unchanged until their retained contract is migrated.

This is a first verified retirement and reusable offline core, not a completed replacement of the live producer, staging, installation/evidence sealing and packaging workflow. No new milestone or MVS operation is opened. Published RC4, frozen manifests, registry, private receipts, historical records and operational safety markers remain untouched.

## Owner-reported offline and saved-MVS-evidence verification

24 November 2026: owner executed the committed ten-test unit suite and both new reviewer commands against sealed RC4 evidence. All ten tests passed (0.034 s), including frozen RC4 writer and three profile rendering digests. The original production and TA.7 evidence seals passed. The tape reviewer reported BC0004, 21 logical datasets, 64 physical files; the MR10 and COMBINED reviewers each reported EXP_RP_CODE_COMPARISON_PASS, twelve cases. Retain `workarea/release-offline-NyCWhxj7` and `workarea/release-evidence-rd1y0aWu`. These owner-reported actual results supersede the earlier unsubstantiated assistant-workspace ten-test execution assertion; private raw files were not directly inspected by the assistant.

## Owner-approved consolidated private MVS integration exercise

Owner authorized one new private tape production, installation and verification exercise and associated commits. The test identity is BCPL-0.1.0-tooltest1 / BC0005 (not RC5, not a public release). The single registry reserves BC0005 permanently under integration_tests, distinct from the four frozen candidate records. Future VOLSER allocation must exclude both lists. The older candidate-only checks do not yet enforce this additional test-volume map; they remain historical, not an authorization path.

The temporary [integration harness](../../tools/distribution/integration.py) uses release.py for writer and installer generation, HETMAP inspection and MR10 semantic comparison. It derives a private manifest from SHA-256-pinned RC4 selection and the established allocation budget; BT0001/2 are newly staged at HERC02.BCPL.X5ST; BT0003–21 reuse the existing accepted TA2R3S input PDSes. BT0003 remains the historical documentation payload, explicitly superseded by the private bootstrap; this is not a redistributable candidate. Native components are inventory-only.

Preflight requires original RC3/RC4 checksums, clean main, unused tape identity, idle/known media, exact 19 source PDS DCBs and 142 members, catalog and formatted VTOC absence for 44 new DASD targets, and sufficient IEHLIST-reported planning space. The 1,887-track allowance must not exceed half the reported free tracks; this does not prove extent contiguity. One interactive confirmation and an exclusive no-retry marker precede the two new stage allocations and tape initialization. No accepted dataset, tape image, marker, manifest or tag is modified; an idle accepted tape may be unmounted to free unit 480. The test volume is left unmounted on success, with all new PDSes and evidence retained. Use a quiescent MVS environment; no concurrent tape or dataset operations.

Acceptance: MVS staging/write RC0000; 21 SL datasets/64 physical AWS files; MVS bootstrap and on-tape installer readback; exact 11/11/20 PDS and 94/71/150 member inventories at X5MR/X5NT/X5CB; six functional jobs covering 80 MR10 cases (24 regression and 56 demonstrations) with actual installed JCL, exact EXP/RP/TEST/CODE for regressions and retained demo checks; accepted tape and new test image checksum stability. All jobs and receipts are saved in workarea/release-integration and sealed; no automatic retry, scratch or publication. This is verification on fresh namespaces of the existing MVS, not independent IPL or complete record-byte comparison.

Assistant compiled the exact new harness locally and exercised its offline plan and synthetic drive guards in an isolated fixture using blob-verified RC4 manifest and allocation data, reconstructed registry, and copied release renderer functions. The plan produced 44 targets and 1,887 planning tracks, with profile counts and VOLSER checks passing. Full repository import and actual MVS execution cannot be performed in the assistant workspace. The harness intentionally reuses established historical transport, stage/restore and evidence helpers, including a scoped in-memory allowlist adaptation for the pure suite-deck helper. It is a temporary verification harness, not a generic live producer or justification for deletion of these dependencies. Actual MVS evidence is pending; no new milestone or reopening of TA.5.

## Private MVS integration result — PASS (24 November 2026)

The owner executed the committed integration harness at `7d8f1e9a8a94901ca4cdb4c895fbb0838cb12bc2`, approved the single guarded operation after read-only preflight, and reported successful completion. No retry is authorized. The private BC0005 reservation is now consumed.

- Preflight JOBS 9452/9453/9454/9455: 44 absent targets; 7,493 IEHLIST-reported free tracks versus 1,887 planning tracks; drive EMPTY.
- Stage JOB 9456: new BT0001/BT0002.
- Write JOB 9460: 21 logical datasets, 64 physical tape files; BC0005 SHA-256 `10ff1f489b280f1d20a7ec6725aad3a4f3cb21292f310b3121468ddbfb8272e3`.
- MR10 install JOB 9464: 11 PDSes, 94 members; language JOB 9468 (11 cases), BCPL JOB 9470 (17 cases), regression JOB 9472 (12 cases).
- NATIVE install JOB 9475: 11 PDSes, 71 members; inventory only.
- COMBINED install JOB 9480: 20 PDSes, 150 members; language JOB 9484 (11 cases), BCPL JOB 9486 (17 cases), regression JOB 9488 (12 cases).
- Final console result: `INTEGRATION PASS: 42 PDSes/315 members; 24 regressions/56 demos; accepted tapes unchanged.`

Private evidence: `workarea/release-integration/20261124T205914Z-45447`. Preserve this directory, the exclusive no-retry marker, the BC0005 image, and installed test namespaces until separately authorized disposition. The harness reports final success only after checking the original tapes and test image and sealing the evidence directory. The assistant has reviewed the owner-supplied console transcript and the committed acceptance logic, not independently inspected the private raw files or recomputed the image digest.

All four release.py functions have passed offline tests, saved RC4 evidence checks and actual MVS integration. This establishes the tested RC4-layout production and installation path using reused accepted payload inputs. It does not establish a fresh source reconstruction, arbitrary manifest/layout support, record-byte fidelity of all restored members, native functional acceptance, independent IPL, or a general live release producer independent of historical transport helpers. The integration harness is consumed; do not rerun it. Future consolidation should extract the demonstrated reusable MVS transport and verification functions before retiring dependencies, and maintain exclusion of used private VOLSERs. No new milestone or RC5; no publication authorization.
