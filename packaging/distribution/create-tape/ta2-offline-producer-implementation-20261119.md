# TA.2 — Initial manifest-driven producer: offline and read-only implementation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 19 November 2026  
**State:** Initial offline implementation and host-only read-only preflight. **No release candidate or MVS tape production authorized.**

## Authority and acceptance scope

The owner approved the five TA.2 architectural directions: frozen Git inputs, one cross-release identity registry, separate MVS staging, ordered generated JCL and terminal no-retry failure behavior. This document records the resulting **first implementation**, not TA.2 acceptance or authorization to reserve a production version/VOLSER. TA.0 and TA.1 remain **CLOSED (qualified)**. Subsequent TA.3–TA.8 names and gates are unchanged.

## Implemented and reusable components

`packaging/distribution/create-tape/scripts/ta2-offline` reuses the **existing** `tools/distribution/validate-manifest.py` loader and exact TA.0 selection checks. It adds these strictly offline checks, without modifying the TA.0 validator:

- Default: read-only design inventory check; it accepts the proposed `ta0-inventory.yaml` **only as design**, prints one compact line, and never renders production JCL.
- `--candidate`: accepts only an exact `manifest/releases/<candidate-id>.yaml` with a frozen source Git SHA that is an ancestor of the clean current checkout, plus exact unchanged selected source blobs. The canonical `registry/releases.yaml` must exist and contain the same candidate identity, version, source SHA, unique VOLSER and SHA-256 of the exact manifest bytes, in state `reserved`. Repository tracked files must be clean and referenced frozen Git blobs available. The registry and release-specific manifest are **not created by this march**.
- All 20 producer source/staging DSNs must be declared explicitly and unique. Each dataset must include distinct source/restored DCB and (for PDS unloads) a verified sequential IEBCOPY unload DCB. Only the first dataset is generated as a sequential FB80 bootstrap; others use IEBCOPY selective unloads.
- Every source/staging dataset needs SHA-256-pinned *existing* read-only `dspal stat` evidence; PDSes also need `dspal ls` evidence with **exactly the curated members** in staging. The declared DASD volume and `DSORG/RECFM/LRECL/BLKSIZE` must match. Evidence paths must be safe under this repository's `workarea/`; the tool **does not collect or create** evidence.
- For all 127 selected members, the canonical validator checks presence/membership and per-member rights/source declarations; the new offline gate also enforces rights/source references. The reported evidence does **not** independently establish object-deck bytes, native code ancestry, or legal approval.
- Candidate JCL is generated entirely from the validated manifest with contiguous `BCPL.BTnnnn`, `LABEL=(n,SL)`, explicit `VOL=(PRIVATE,...SER=...)`, guarded next steps (`COND=(0,NE)`), `IEBGENER` for `BT0001`, and `IEBCOPY` for all subsequent PDSes. The final step releases `RETAIN`. One SELECT card per member avoids oversized lists and does not select development members beyond the manifest. The JCL is a JOB-less body, requiring the existing controlled submission facility **after separate authorization**.
- The generator never adds a PDS `RECFM=U` DCB override to the sequential tape unload DD, never catalogs tape aliases, never uses `DISP=MOD`, and never initializes, mounts, writes or restores an AWS image.

## Strict candidate input contract (not instantiated)

In addition to the accepted schema-v1 release fields, the offline gate requires on each dataset:

- `producer_source_dsn`: exact MVS source/staging DSN, independently verified before any use.
- `producer_source_volume`: six-or-fewer-character DASD VOLSER observed in the pinned MVS stat.
- `source_dcb`, `target_dcb`: exact separate `dsorg`, `recfm`, `lrecl`, `blksize` maps; initially must match.
- `unload_dcb`: **for each PDS**, the distinct observed IEBCOPY sequential unload DCB; this is NOT added as a JCL output override.
- `mvs_inventory_receipt`: `stat: {path,sha256}` and, for PDSes, `ls: {path,sha256}`, of saved, exact UTF-8 read-only MVS inquiries under `workarea/`.

The manifest's `generation.producer_sha256` and `generation.canonical_validator_sha256` additionally pin the exact generator and canonical validator bytes. Candidate source commit identity is deliberately independent of the later commit containing the candidate manifest/registry; their Git commit hashes cannot safely be self-referential.

The cross-release registry has `schema_version: 1` and an ordered `candidates` list, whose entries carry `candidate_id`, `state`, `version`, `source_commit`, `volser`, `manifest_sha256`. `prepared` alone may have no VOLSER; a **new unbuilt `reserved`** entry is required to render JCL. Historical rejected/failed/built/published allocations permanently retain their distinct VOLSERs. Earlier scratch `BTA101`, `BTA102`, `BTO001` and `BTP001` are forbidden as new candidate identities. No registry file or candidate manifest has been created or reserved.

The same release manifest must drive the future MVS installer and verification expectations, not a second tape map. The registry records cross-release identity history only.

## Intentional qualification and next MVS gates

The generated 20-dataset JCL is an **offline proposal**, not proven JES-acceptable or multi-IEBCOPY-successful on the target MVS 3.8J. The `RETAIN`/step sequencing extends the bounded two-dataset TA.1 result, not 20-dataset observed behavior. `SYSUT3/SYSUT4 SPACE=(TRK,(10,5))` is a provisional explicit generation parameter requiring real MVS capacity and utility review. The saved `dspal stat/ls` evidence check is **not** an actual MVS query and does not compare staged member contents. A full media preflight must also check actual connected Hercules drive state, existing AWS volume-label collisions (including outside the registry), MVS catalog and allocations, and current source/volume identity. The TA.1 operator safety mechanisms are the starting point, but no generalized stateful producer exists yet.

Before any media operation, obtain fresh owner approval of the **exact** frozen source SHA, candidate ID/version, never-used VOLSER, media filename, selected member inventory, validated producer JCL, and stateful one-shot safety boundary. Production must stop rather than retry after an ambiguous mount/position/JES event. Preserve BTA101/BTA102. On authorization, MVS/JES/IEBCOPY/IEHLIST/GO and independent AWS structure/restore checks decide acceptance. No byte-identical `RECFM=U` load-member assertion follows from the accepted TA.1 evidence.

## Offline verification

Run in the assistant workspace, without MVS/Docker/JES calls:

`python3 -B -m unittest discover -s packaging/distribution/create-tape/tests -p 'test_ta2_offline.py' -v`

**First implementation:** 35 isolated synthetic success/refusal tests. They exercise tape positions, selectable members, duplicate registry IDs/VOLSERs, forbidden TA.1 scratch identities, state transitions, SHA-pinned saved MVS evidence, staging DCB/volume/member discrepancies, Git freeze gate invocation, and JCL column widths. A local synthetic test run cannot replace current-source MVS evidence or production acceptance.

## Read-only MVS source inventory extension

The separately reviewed `scripts/ta2-source-preflight` implements a
consolidated **read-only live MVS** preflight for the 18 development-source
PDSes selected by the TA.0 manifest. Its default invocation is host-only
planning; only `--live` invokes existing `dspal stat` and `dspal ls`
inquiries. It verifies dataset identity, DASD volume, expected DCB, and
presence of selected members, while separately reporting *unselected*
development members. It preserves original query output, private JSON
summary, and SHA-256 digests exclusively under ignored
`workarea/ta2-source-preflight/`. An inquiry failure or inconsistent
attributes causes a refusal, never a dataset rewrite.

**Offline verification:** 11 additional synthetic parser/refusal checks,
for **46 focused TA.2 tests** across the two tools. Live MVS results have
not yet been supplied; these tests do not establish binary equality,
rights clearance, or any production candidate. The read-only MVS inquiry
still requires execution by the owner on the actual TK5 system.

Do not substitute raw development member inventories for the exact
candidate-specific isolated staging required by the frozen producer.
