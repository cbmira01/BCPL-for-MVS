# How to Create a Release Candidate

**Audience:** Project maintainers.  
**Status:** Working draft, DR.3 — Project Documentation; source reviewed at `a07fe5290c507c575269b2acd1e1ac7914a35704`.

Use this manual to plan, review and conduct a privately verified tape candidate of the **Cambridge BCPL Programming System for MVS 3.8J**. The [canonical execution guide](../../tools/distribution/How-to-Create-a-Release-Candidate.md) remains the single operative step-by-step command procedure. Follow its linked steps at each gate below. This manual adds the review and acceptance context around that procedure; it does not create a second independently executable recipe, relocate the existing guide or transfer its authority. DR.5 will review dependencies before any authority transfer.

The new [create-release driver](../../tools/distribution/create-release) and extracted helpers are implemented and offline-tested, but have not passed a live MVS run. The earlier private BC0005 integration used a different, now retired harness. Nothing in this manual authorizes a new candidate, MVS operation, installation, registry change or publication.

[Documentation catalog](../README.md) | [Project tools reference](Reference-for-Project-Tools.md) | [Reconstruct from source](How-to-Reconstruct-BCPL-from-Source.md)

## 1. Confirm scope, prerequisites and authorization

Decide what is to be released before reserving an identity. Distinguish these three activities:

| Activity | Source and result |
| --- | --- |
| Development reconstruction | Rebuild the project programming environment from Git and verify its supported tests on MVS. Not a release selection or tape. |
| Private tape candidate | Freeze a selected payload, produce a standard-labeled AWS, install and verify its supported profiles, package and seal evidence. |
| Public release | Publish the exact privately accepted bytes after a separate owner decision and provenance review. |

The first driver implementation supports only the frozen RC4 layout: 21 logical datasets, one standard-labeled AWS volume, three profiles, MR10 Kit Compiler and ICINT19, native runtime/libraries and optional System Extensions, and selected historical Cambridge Compiler source. The native-running Cambridge Compiler is absent. The driver pins the RC4 template checksum and refuses changes to its dataset selection, profiles or other unsupported fields. The separately reconstructed interpreter-hosted CAMBCOMP is not a released native-running compiler; the RC4 program payload does not include CAMBCOMP.

Consult the [manifest index](../../packaging/distribution/manifest/README.md), [distribution index](../../packaging/distribution/README.md) and [formal Tape artifact release closure](../../packaging/milestones/tape-artifact-release/ta8-formal-qualified-closure-and-milestone-completion-20261124.md). The accepted prerelease is RC4 / BC0004, published 24 November 2026. BC0005 is a permanently used private tool-integration volume, not RC5. Do not modify RC4 or earlier accepted media, frozen manifests, reservation entries, tag or evidence. Do not replay consumed historical operations.

Before any production preparation, review the [canonical prerequisites](../../tools/distribution/How-to-Create-a-Release-Candidate.md#1-confirm-scope-and-prerequisites):

- Clean, tracked `main` checkout at the authoritative origin HEAD; Python 3.11 or later with PyYAML, established WSL/Docker/TK5 and authenticated DSPAL configuration.
- Dedicated, quiescent MVS environment, with no competing JES, tape, dataset, reconstruction or release work. HERC02 site and batch user, TSO002 DASD, unit 480 empty, reader 3505, HTTP 8038 and expected printer and Docker tape bind.
- Accessible RC3, RC4, BC0005 and every later registry-protected verified tape with matching hashes. Preserve private reports, sealed folders, markers and original packages in protected storage.
- Reviewed source preparation and lineage, exact selected member inventory/DCB, allocation evidence, and preservation/provenance policy.

The driver's clean-main check explicitly ignores untracked files; it checks tracked cleanliness, branch, approved origin URL and live remote HEAD. Inspect untracked files and local configuration independently where relevant. Mutating driver invocations take a nonblocking exclusive host file lock under `workarea/create-release/`; this is not a lock on all MVS jobs or external operations.

A prior successful reconstruction or release is evidence at its tested scope, not authorization for this invocation. Discuss changes to payload or format before implementation. The current driver does not support expanded selections, multiple tape volumes, final versions, arbitrary producer sites, inaccessible/off-site protected media or automatic source preparation. Do not try to work around these restrictions.

## 2. Preview identity and VOLSER

Use [canonical Step 2](../../tools/distribution/How-to-Create-a-Release-Candidate.md#2-preview-the-next-identity). The default invocation of `create-release` reads the registry and proposes an unused prerelease version and monotonically allocated BCnnnn serial. `--version` may explicitly select an unused supported prerelease in plan or preparation mode; it is not accepted with reserve, run or record. The proposal performs no reservation, JES submission or tape write.

The [registry](../../packaging/distribution/registry/releases.yaml) is the only cross-release authority. It contains three distinct classes of record:

| Registry field | Purpose |
| --- | --- |
| `candidates` | Original identity, version, frozen source commit, VOLSER and manifest SHA-256 reservation |
| `lifecycle` | Later technical, private-verification and publication annotations; preserve original reservations |
| `integration_tests` | Permanently used private integration identities and VOLSERs, excluded from future allocation |

At the reviewed baseline, BC0001–BC0004 are reserved and BC0005 is recorded as used. Thus the expected next proposal is `BCPL-0.1.0-rc5 / BC0006`, not an assigned identity. Read actual output and registry again before approval; this example must not become a fixed future reservation. A newer reserved or used serial advances the next proposal; gaps are not permission to reuse a serial. Exhausting BC9999 blocks allocation.

Check for duplicate identity or version, the source selection decision, and whether the candidate name and serial are the intended next allocation. Physical tape-name/VOL1 collision checks are a later live preflight; the offline proposal alone is not proof that media is absent.

## 3. Reserve identity and freeze manifest/registry

Use [canonical Step 3](../../tools/distribution/How-to-Create-a-Release-Candidate.md#3-prepare-a-reservation-and-frozen-manifest) after reviewing the input preparation requirements in Chapter 4. The driver separates preparation, reservation and production.

1. Select exactly one input mode: explicit `--reuse-rc4` or `--inputs FILE`. Generate a sealed reservation draft with the canonical preparation command; review its printed identity, track budget, frozen manifest, proposed registry and `base-head.txt`.
2. Inspect the draft against the frozen RC4 template and actual source receipt. Confirm the selected profile/member set, program revision, allocation and evidence bindings, and the exact reservation append. A candidate's program-source commit and producer-tool commit need not be the same.
3. Apply the reviewed draft locally using the canonical reserve operation. It verifies the seal, source receipt, draft base, current registry and availability, requires interactive confirmation, and refuses an existing target manifest.
4. Review and obtain authorization for a single commit containing the new manifest and registry append on GitHub `main`. Synchronize the operator checkout with the authoritative committed result before production.

The draft lives at the actual printed path `workarea/create-release/<candidate>-<volser>-reservation`. Preparation does not edit tracked files; applying the reservation writes local tracked files, but never commits or pushes. Local file creation and registry replacement are separate operations, not a cross-file transaction. If interrupted, preserve and reconcile the exact local changes before proceeding. A partial or uncommitted reservation cannot pass the run gate.

The new manifest is based on [frozen RC4](../../packaging/distribution/manifest/releases/BCPL-0.1.0-rc4.yaml), retaining its layout/selection with the new identity, program source and `producer_inputs` binding. Record the new manifest SHA-256 in the corresponding reservation. Do not alter any earlier candidate manifest or reservation to fit a new build. A changed main or stale draft cannot be forced through the guard; obtain a freshly reviewed draft against the new authoritative base. Do not overwrite an existing draft or manually bypass a collision.

The [manifest validator](../../tools/distribution/validate-manifest.py) is structural/read-only by default; the run invokes it with the selected manifest, without `--release`. Its strict release gate requires complete inventory and rights evidence. Do not describe the qualified RC4 or a structurally validated new candidate as satisfying strict rights validation. The [schema and manifest index](../../packaging/distribution/manifest/README.md) retain authority.

## 4. Prepare source, documentation and installation payloads

Prepare the approved payload before reservation. Distinguish the program inputs, freshly generated tape materials and actual MVS staging.

### Program-source selection

For a documentation/installer successor, explicit RC4 reuse binds BT0004–BT0021 to the accepted `HERC02.BCPL.TA2R3S.BTnnnn` PDSs and the prior sealed production evidence at `workarea/ta3-rc4-production/20261123T130731Z-36363`. The frozen RC4 source commit is `e910de51c19c09698be139e33084a90401511cc9`. Reuse does not incorporate later program changes. If those PDSs or their evidence are unavailable, the driver refuses; do not invent a substitute receipt.

For new program inputs of the same layout, reconstruct and verify the needed components using the [existing clean-room runbook](../../docs/Rebuild-BCPL-for-MVS-from-source.md), with separate authorization for destructive work. Independently prepare the exact selected PDSs, establish source/build provenance, readback fidelity and allocation evidence. The [retained staging index](../../packaging/distribution/create-tape/README.md) and [historical source selection index](../../packaging/distribution/compiler-source/README.md) describe the reusable functions and historical encoding/transport evidence. The old one-shot staging operations and approvals are not transferable to a new candidate. A fully generalized source-preparation workflow remains unverified; stop if the prepared inputs cannot be independently established.

The new input receipt must have exactly these fields (see canonical Step 3 for the binding contract):

| Field | Review requirement |
| --- | --- |
| `mode` | prepared |
| `source_commit` | Full Git SHA, ancestor of authoritative main |
| `sources` | String sequence keys 4–21; 18 distinct safe PDS DSNs under HERC02.BCPL.* |
| `allocations` | String keys 3–21; three positive integer quantities per entry: primary tracks, secondary tracks, directory blocks, each at most 10000 in the current parser |
| `evidence` | Relative path to private, non-symlink workarea directory |
| `evidence_seal_sha256` | SHA-256 of that directory's SHA256SUMS |

The sealed folder contains `prepared-inputs.json` with exactly the first four fields and the reviewed evidence. The driver checks all immediate evidence files against the flat seal, rejects duplicate/missing/linked members, checks the frozen source is an ancestor and compares the entire `mr10-kit-compiler` Git subtree to current HEAD. Consequently a change anywhere in that subtree can block use of a prior payload even when a narrow source comparison might pass. Do not weaken this guard or forge a receipt. The checksum seal binds saved bytes, not proof of substantive source lineage, binary fidelity or rights. The actual MVS preflight requires 135 members across the 18 prepared program PDSs on TSO002 with exact expected names/DCBs.

### Fresh tape materials

For either input mode, the driver regenerates BT0001–BT0003 from the new identity, source revision and frozen selection, not from stale RC4 documentation.

| Sequence | Material |
| --- | --- |
| BT0001 | FB80 bootstrap and example BT0002 restore instructions |
| BT0002 | Installer PDS with MR10, NATIVE, COMBINED, INSTALL, DATASETS, RELEASE, RESTORE and COPY |
| BT0003 | Documentation PDS: README, INSTALL, DATASETS, COMPILE, VERIFY, RELEASE, LICENSE |
| BT0004–BT0021 | Independently prepared or explicitly reused program payloads, including historical source selection |

Inspect generated installer defaults, site-specific namespaces and dataset allocation parameters. Preserve FB80 record structure and binary-object/load-module handling. Do not normalize historical raw record material indiscriminately; see the [BT0021 acceptance](../../packaging/distribution/create-tape/ta2-bt0021-qualified-acceptance-20261121.md) and [encoding decision](../../packaging/distribution/compiler-source/rc2-job9330-reconciliation-acceptance-and-encoding-decision-20261120.md). The new tape's LICENSE incorporates the project MIT text and preservation/provenance qualification, without relicensing historical sources. The fresh companion and bootstrap decks match the new identity. This does not amend RC4; its mandatory external companion still supersedes its own stale BT0003.

## 5. Produce and verify on MVS — guarded staging, tape write and readback

Only after the reviewed reservation is committed, prepared inputs verified and actual run scope approved, follow [canonical Step 4](../../tools/distribution/How-to-Create-a-Release-Candidate.md#4-produce-and-verify-the-candidate-on-mvs). The canonical command is the one orchestration entry point, not a series of independently replayable stage commands. Do not substitute retired RC2–RC4 or BC0005 harnesses.

The driver first verifies the unused committed reservation, source receipt and frozen template. It checks protected media, exact runtime transport, Docker running state/tape bind/UID and GID, HETINIT support, empty unit 480 on both guest and emulator, physical volume collisions, actual source PDS attributes and directories, fresh target and tape-alias absence, VTOC and reported free tracks. Some of these read-only live inquiries submit real JES jobs; no persistent candidate write is intended before approval.

For RC4 reuse, the plan is 45 new DASD datasets and 1954 planning tracks. Free tracks must be at least twice the calculated budget; available total does not prove contiguous extents. The actual plan and receipts control, not the example. Review all preflight output, confirm the correct reservation, empty drive, intended stage and install targets and absence of independent work. A refusal or ambiguity blocks production.

The exact interactive run confirmation is a separate one-shot decision. After confirmation the driver rechecks authoritative HEAD, empty drive, protected images and absent new image; it creates an exclusive `workarea/create-release/<VOLSER>-no-retry.json` marker before staging. That consumes the intent, even if no tape is subsequently written. The driver lock does not make arbitrary external activity safe.

| Stage | Required evidence |
| --- | --- |
| CRSTAGE / CRDOCS | Expected IEBGENER/IEFBR14 steps, zero required RCs, actual bootstrap DCB, installer/doc directories and exact printed documentation |
| Initialize and mount | Fresh exclusive image, correct serial, empty-drive and ready-media checks |
| CRWRITE | 21 ordered write steps: IEBGENER for BT0001 and IEBCOPY for BT0002–BT0021 |
| Physical review | HETMAP labels and physical files against manifest: 21 logical datasets, 64 physical files, correct volume/sequence |
| Independent readback | New tape checksum recorded; MVS CRBOOT reads actual BT0001 and checks card content; BT0002 restored per profile in Chapter 6 |

Use the actual saved writer deck and reports. Host tape structure review is not a substitute for MVS restore or full record-byte comparison. Require new-image and protected-image digests to remain unchanged through verification. Do not manually manipulate tape position, allocation or queue in response to an uncertain result without a separate reviewed investigation. Stop on any failed gate. The current driver owns the consolidated operation; Chapter 6 describes the continuation and required evidence, not a standalone recovery sequence.

## 6. Install in fresh namespaces and verify supported functions

The consolidated run continues with fresh namespaces derived from the allocated VOLSER. For BC0006 the example sites are R0006ST (staging), R0006MR, R0006NT and R0006CB under HERC02.BCPL. Do not choose these names independently of the reserved serial. All 45 targets must have passed absence checks before writes; do not reuse an accepted installation.

For each profile the driver restores BT0002 using IEBCOPY (CRBT2), reads the actual tape-restored profile and COPY member (CRVIEW), compares to the generated canonical card sequence, submits the restored profile (CRREST) and verifies ordered required PROC steps and exact actual PDS DCBs and member names. It reads all fresh BT0003 documentation back in each profile and compares card content. Require full receipts, not only a successful launcher or a printed PASS.

| Profile | PDSes | Member entries | Functional scope |
| --- | ---: | ---: | --- |
| MR10 | 11 | 94 | 11 language demonstrations, 17 BCPL demonstrations, 12 semantic regressions |
| NATIVE | 11 | 71 | Installation and inventory only |
| COMBINED | 20 | 150 | Independent repeat of all 40 MR10 cases |
| Total | 42 | 315 | 56 demonstrations and 24 semantic regressions |

The functional path reads installed MRLANGDM, MRBCDEMO and MRREGRES JCL through MVS, validates exact card content, retargets only to the selected installed namespace, submits and checks the actual payload. Per MR10-capable profile the three suites require 38, 62 and 63 JES steps, respectively (326 functional steps across both profiles). Require zero required JES/ICINT19 codes; for the regressions the independent TEST identity, EXP, RP and CODE checks must all pass. The native profile has no native functional acceptance. Do not use a development-system regression result to extend this release's actual verification scope.

The [TA.7 acceptance](../../packaging/milestones/tape-artifact-release/ta7-clean-namespace-acceptance-20261124.md) records these counts for RC4 in fresh namespaces on existing MVS. The later BC0005 private exercise matched those counts but was not RC5 and did not validate the newly extracted driver's orchestration. The accepted TA.4 isolated ICINT19 rebuild remains earlier evidence; the new driver does not itself rebuild ICINT19 from source.

At the end of the consolidated run require tape unmounted, unit empty, new tape digest unchanged and all protected images unchanged. The fresh staging and installation datasets remain intact. A PASS is qualified to this layout, existing MVS and the actual verified profiles; it is not an independent IPL, alternative account portability, all restored-member byte fidelity, native compiler certification or proof of all current source provenance.

## 7. Review private evidence, checksums and package consistency

The driver prints the actual evidence directory beneath `workarea/create-release/`. Use [canonical Step 5](../../tools/distribution/How-to-Create-a-Release-Candidate.md#5-review-the-output-and-record-private-verification) to review evidence before any record operation. Inspect the full saved evidence, not just the final console result.

| Evidence | Required review |
| --- | --- |
| Frozen manifest and producer-head.txt | Exact reservation, frozen program-source and producing tool revisions |
| Preflight and job reports | Intended source/target inventory and allocation, actual job identity and every required step/RC |
| tape-review.json and readback reports | Standard labels, physical sequence and actual restored content checks |
| Per-profile checkpoints and semantic verdicts | Correct member counts, all six functional suite receipts, independent output/completion results |
| result.json | Status PRIVATE_CANDIDATE_VERIFIED_QUALIFIED, correct identity, source/producer commits and AWS/archive digests; publication_authorized false |
| proposed-lifecycle.json | Exact proposed qualified private-verification annotation |
| SHA256SUMS | Full private evidence seal; verify all saved files |
| VOLSER no-retry marker | Exclusive consumed intent, matching candidate, producer HEAD and evidence path |

The private package contains the exact AWS, candidate manifest, freshly generated README.md companion, BOOT.jcl, BT2.jcl, VERIFICATION.json, LICENSE.md, THIRD-PARTY-NOTICES.md, README.Nordier, README.orig.Yap and INDEX; internal SHA256SUMS covers its other members. The driver checks the AWS hash before packaging, creates the ZIP exclusively, reopens it, checks exact entry names, ZIP integrity and bytes against inputs, and writes external ARCHIVE.sha256. The private result adds the archive name and digest after packaging; the internal VERIFICATION.json describes the verified inputs before that archive self-digest exists. Do not expect the archive to contain its own SHA-256.

Compare exact private package bytes with the saved digest, manifest and accepted AWS; preserve the complete sealed folder and no-retry marker. The archive excludes private raw JES reports and authentication configuration. Keep those separate, redact any shared extracts and protect private reports. A package seal cannot establish untested source lineage, independent MVS installation or rights approval. Do not claim fresh verification of a saved digest without reading the actual bytes.

The [RC4 private package acceptance](../../packaging/milestones/tape-artifact-release/ta8-private-package-acceptance-20261124.md) and [exact RC4 reviewer](../../packaging/distribution/publication/scripts/ta8-rc4-review) are historical exact-candidate evidence, not tools for a new arbitrary candidate. The new driver supplies its own candidate-specific seal and byte review. Retain both sets of records.

## 8. Record acceptance and separate publication authorization; stop/recovery rules

After review, use the canonical record operation in Step 5 with the actual printed evidence directory. It requires a current authoritative clean main and verifies the seal, unused lifecycle reservation, qualified result status, profile and functional counts, consumed intent, artifact digests and exact proposed annotation. After a new interactive confirmation, it writes the lifecycle annotation locally. It does not commit or push. Review and obtain authorization for the registry-only commit. A refusal leaves the existing registry unchanged.

The resulting state is `verified-qualified-pending-owner-review` with publication_authorized false. This is not formal owner acceptance, permission to publish or a public release. Present the source revision, producing revision, candidate/VOLSER, exact archive/AWS digests, actual MVS receipts and qualifications, and the requested acceptance decision. Owner approval must explicitly address the tested scope and provenance/rights status. Original project work is MIT under its stated terms; historical authors' rights remain unresolved. The current preservation policy is not blanket redistribution permission.

For public distribution, require a separate owner decision specifying exact accepted bytes, intended tag and release type, provenance/notices, companion and checksum publication. The driver never creates a release tag, uploads or publishes. Preserve the reviewed private package and verify public metadata and asset digest against it; distinguish server-reported digest from independent downloaded-byte verification. The [RC4 publication authorization](../../packaging/milestones/tape-artifact-release/ta8-rc4-publication-authorization-20261124.md) and [formal closure](../../packaging/milestones/tape-artifact-release/ta8-formal-qualified-closure-and-milestone-completion-20261124.md) provide the recorded historical example, not a reusable publication approval. RC4 remains unchanged.

| Outcome | Required response |
| --- | --- |
| Preview or preparation refused | Diagnose source, registry or input evidence; no run authorized |
| Reservation local write interrupted | Preserve/reconcile both intended files; no run with partial/uncommitted reservation |
| Live preflight refusal before intent | Inspect actual read-only inquiries and outstanding jobs, correct cause, renew review before any attempt |
| Declined run | May return RC=0 and seal DECLINED_NO_WRITE; not a verification pass |
| Consumed intent, failure or ambiguous submission | **NO RETRY**. Freeze writes, preserve marker, media, allocated namespaces and evidence; inspect actual MVS state. |
| Successful private result, record declined | Preserve verified private evidence; registry remains unchanged, no publication |
| Publication not authorized | Retain private package; do not create tag or upload |

If intent has been consumed, the VOLSER stays unavailable even if no image exists. Do not delete marker or tape, reuse identities, replay individual write/restore operations, or run historical one-shot tools as a recovery shortcut. Record a failed disposition through a separate reviewed registry change; a subsequent attempt requires new identity, VOLSER and scope approval. Do not assume a complete seal can always be written after a failure; preserve whatever actual evidence exists. Refer to the canonical stop/recovery rules, and preserve original failure evidence even if a later attempt succeeds.

Before changes to the driver or helper interfaces, use its canonical offline test procedure. The [release tool guide](../../tools/distribution/README.md) describes the simulated success, decline and write failure checks and retained helpers. Mock transport tests do not replace actual MVS acceptance. A future independently authorized candidate must establish the new driver's live verification before it is represented as accepted.

DR.3 documentation drafting does not reopen the Tape artifact release milestone or authorize production. Existing canonical instructions, frozen source records, manifest, registry, evidence and independent oracles retain their authority.
