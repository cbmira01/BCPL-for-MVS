# How to Create a Release Candidate

This procedure creates a privately verified tape candidate of the **Cambridge BCPL Programming System for MVS 3.8J**. Use the `create-release` command from the repository root. It coordinates the reusable `release.py` and `mvs_release.py` helpers, DSPAL, MVS JES, IEBGENER, IEBCOPY and IEHLIST. The release registry is the only cross-release authority for versions and VOLSERs.

**Implementation status:** offline-tested, including simulated end-to-end success, decline and write failure. The new driver and the extracted MVS helper interfaces have not yet passed an actual MVS run. The earlier BC0005 private integration passed on actual MVS; it is not verification of this new orchestration. This guide does not authorize another release, publish an artifact, reopen a milestone or change the accepted RC4 release.

## 1. Confirm scope and prerequisites

The first implementation supports the established single-volume, standard-labeled RC4 layout: 21 logical datasets, MR10/NATIVE/COMBINED profiles, the MR10 Kit Compiler, ICINT19, native runtime and libraries, System Extensions and historical Cambridge Compiler source. The native-running Cambridge Compiler is absent. The tool refuses an expanded or changed payload selection instead of silently certifying an untested compiler or layout.

Use the clean, committed authoritative `main` checkout synchronized with GitHub `origin/main`, Python 3.11 or newer with PyYAML, the established WSL/Docker/TK5 environment and authenticated DSPAL configuration. Start with unit 480 empty, DASD volume TSO002 available, and no concurrent MVS, tape, dataset or release operations. Preserve the accepted images, private evidence and no-retry markers. The existing BC0003, BC0004 and BC0005 images, and every later registry-tracked verified image, must be accessible under `mvs-state/tape/` with matching checksums. This implementation does not handle archived/off-site media or alternative producer sites.

The command does not purge, repopulate or rebuild the development environment. Prepare new program payloads using the [canonical clean-room reconstruction procedure](../../docs/Rebuild-BCPL-for-MVS-from-source.md) and the retained source-selection, encoding, staging and fidelity tools. Independently establish their source/build lineage, exact prepared PDS membership and allocation evidence. A reconstruction pass alone does not establish a complete release input receipt.

## 2. Preview the next identity

```sh
tools/distribution/create-release
```

The command reads [releases.yaml](../../packaging/distribution/registry/releases.yaml), considers **both** `candidates` and `integration_tests`, and proposes the next unused candidate version and the next monotonically allocated BCnnnn VOLSER. After BC0005 the expected proposal is `BCPL-0.1.0-rc5 / BC0006`. This is a proposal, not an assignment. Nothing is reserved or written to MVS. Use `--version 0.2.0-rc1` (for example) to select an explicit unused prerelease version instead of the automatic increment. Final-version and multi-volume releases are not supported by this implementation.

## 3. Prepare a reservation and frozen manifest

For a documentation/installer successor with the same prepared RC4 program payload, explicitly select:

```sh
tools/distribution/create-release --prepare --reuse-rc4
```

The source revision remains the frozen RC4 program-source SHA, not the current tool revision. BT0004–BT0021 come from the accepted TA2R3S prepared PDSes; the old sealed production evidence is checked. This is an explicit decision to reuse those inputs, not an assertion that they contain later source changes. BT0001, BT0002 and BT0003 are freshly generated for the new candidate. The on-tape LICENSE includes the original MIT text and preservation/provenance qualification. The companion guide and external bootstrap JCL will match the new identity; the RC4 stale-documentation workaround is not carried forward.

For newly prepared program payloads of the same layout, use `--prepare --inputs FILE`. The input JSON must contain exactly these fields:

| Field | Required content |
| --- | --- |
| `mode` | `prepared` |
| `source_commit` | Full Git SHA of the reviewed program-source revision, an ancestor of main |
| `sources` | Object mapping string keys `4` through `21` to 18 distinct prepared project PDS DSNs under `HERC02.BCPL.*` |
| `allocations` | Object mapping string keys `3` through `21` to `[primary_tracks, secondary_tracks, directory_blocks]` for each recipient PDS |
| `evidence` | Relative path to a sealed private workarea directory containing reviewed source preparation/build evidence |
| `evidence_seal_sha256` | SHA-256 of that directory's `SHA256SUMS` |

The evidence directory must contain `prepared-inputs.json` with the exact `mode`, `source_commit`, `sources` and `allocations` fields; it and every other evidence file must be covered by the seal. The input JSON additionally specifies the directory path and seal hash. The tool checks these bindings and ensures the current MR10 reference sources, suite decks and independent goldens match the frozen Git tree. The operator remains responsible for the evidence's substantive source/binary lineage and rights review. An arbitrary self-created seal is not proof of a successful reconstruction or record fidelity. All 18 PDSes must reside on TSO002, have exactly the selected members and expected DCBs; the command refuses extra or absent members.

The preparation command writes a checksum-sealed draft under `workarea/create-release/<candidate>-<volser>-reservation`. It does not edit tracked files. Review the selection, source revision, allocations, provenance and exact proposed reservation. The following separate step applies the draft to the local checkout after confirmation:

```sh
tools/distribution/create-release --reserve workarea/create-release/BCPL-0.1.0-rc5-BC0006-reservation
```

Use the actual draft path printed by preparation. This writes only the new candidate manifest and a registry append, preserving all previous entries. Have both files reviewed and committed to GitHub `main` together by the authorized project operator; neither the command nor the driver commits or pushes. Synchronize the checkout after the authorized commit. A candidate cannot run with an uncommitted reservation, a stale checkout, a mismatched manifest checksum or an existing lifecycle record. If another reservation has been committed, regenerate a draft against the new main; never reuse a used or reserved VOLSER.

## 4. Produce and verify the candidate on MVS

After the reservation commit is authoritative and the owner has approved the proposed operation:

```sh
tools/distribution/create-release --run BCPL-0.1.0-rc5
```

Supply the actual reserved identity. The command begins with read-only checks of the registry, frozen input evidence, manifest structural validator, Docker identity/tape bind, protected media hashes, guest and emulator drive status, physical media VOLSER collision, source directories/DCBs, new DASD target and tape-alias catalog absence, formatted VTOC and reported DASD capacity. The planning allowance includes staging BT0001–BT0003 and all three installations. The available-track total must be at least twice the allowance; this is not proof of contiguous extents. For the RC4 reuse budget, the plan is 45 new DASD datasets and 1,954 tracks.

Only after a successful preflight and one interactive confirmation does the command create an exclusive no-retry marker and begin stateful operations. The marker is consumed even if an operation later fails. The driver:

1. Stages new bootstrap, installer and documentation datasets using IEBGENER and IEFBR14; verifies directories, DCBs and printed documentation.
2. Initializes and writes a new AWS tape with the manifest-driven IEBGENER/IEBCOPY deck. Checks JES return codes, HETMAP standard-label sequence, physical files and image checksum.
3. Restores BT0001 and BT0002 on MVS. Reads the actual tape-restored profile JCL, verifies its expected card sequence and COPY control, then submits that profile in its fresh namespace.
4. Verifies exact PDS names, DCBs and member directories; reads the new BT0003 documentation back in each profile.
5. Reads installed MR10 JCL and binds it to the installed namespace. Runs the 11 language demonstrations, 17 BCPL demonstrations and 12 semantic regressions in MR10 and COMBINED. Requires zero JES/ICINT19 codes and independent TEST/EXP/RP/CODE comparison for the regressions. NATIVE is installation/inventory only.
6. Unmounts the new tape after success, checks its digest and all protected tape digests, and packages the exact verified image.

Expected: 21 logical datasets / 64 physical tape files; 42 installed PDSes / 315 member entries; 80 functional MR10 cases (24 semantic regressions, 56 demonstrations). The run leaves fresh staging and installed datasets intact. A new namespace is derived from the allocated serial (e.g. `R0006ST`, `R0006MR`, `R0006NT`, `R0006CB` for BC0006).

## 5. Review the output and record private verification

The command prints the evidence directory under `workarea/create-release/`. On success it contains the private candidate ZIP, external `ARCHIVE.sha256`, the exact manifest, actual generated decks, MVS reports, semantic verdicts, `result.json`, `proposed-lifecycle.json` and a complete evidence `SHA256SUMS`. The ZIP contains the exact AWS, manifest, fresh companion guide, external bootstrap/BT0002 JCL, verification summary, complete project license and historical provenance notices/archival notes, and an internal checksum list. The driver reopens the ZIP, verifies every member byte-for-byte against its inputs and records its SHA-256. It does not include private raw JES reports or authentication configuration.

After reviewing the actual evidence, use `tools/distribution/create-release --record EVIDENCE_DIRECTORY` with the printed relative directory path. It verifies the seal, consumed intent, identity, expected profile/case counts, and archive and AWS digests. After confirmation it appends a proposed qualified private-verification annotation to the registry in the local checkout, preserving prior entries. Commit the reviewed registry change separately. The recorded state remains `verified-qualified-pending-owner-review`; publication is false. Keep the candidate tape, ZIP, checksum, reports and marker. Publication of the exact accepted bytes requires a separate owner decision, including licensing/provenance review and release/tag association. The command never creates a tag or uploads a release.

If a run halts after intent creation, **do not retry**. Preserve the image, marker, evidence and allocated namespaces; inspect the actual MVS failure. Record failed disposition through a separate reviewed registry change. The reserved VOLSER remains unavailable even if no tape was written. The next attempt needs a new candidate identity and VOLSER, not an overwrite. A preflight refusal or declined confirmation before intent creation has performed no stateful production operation; investigate before attempting again.

## Verification limits and development testing

The result is qualified: current layout only; fresh namespaces on the existing MVS system, not a separate IPL or independently installed system; no fresh ICINT19 source rebuild or native functional acceptance; no full restored record-byte identity or automatic proof of current source/binary provenance. Historical redistribution rights remain unresolved. The driver does not yet automate complete new program source preparation, accept a native-running Cambridge Compiler, or publish a release. Those require independently verified scope and inputs.

Run the offline suite from the repository root:

```sh
python3 -B -m unittest discover -s tools/distribution -p 'test_*release.py' -v
```

This exercises the existing release renderer/reviewers, MVS helper contracts, registry and seal handling, fresh documentation, archive integrity, refusal cases, and the simulated driver success/decline/failure paths. Mock transport tests are not actual MVS verification. On a future owner-approved candidate, verify the new driver against MVS before treating it as an accepted live release procedure.
