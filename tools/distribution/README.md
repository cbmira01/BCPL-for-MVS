# Distribution tools

The Tape artifact release milestone is formally CLOSED (qualified). [RC4](../../packaging/distribution/README.md) is the published candidate. This directory contains the manifest validator, reusable offline JCL/evidence functions, and retained TA.0 evidence/inventory tools. No generic live producer has been accepted yet.

## Reusable offline release interface

[`release.py`](release.py) is the candidate-independent interface to the established tape JCL and saved-evidence operations. It never submits JES jobs, allocates or deletes datasets, mounts or writes tape, reserves VOLSERs, or publishes a release.

| Subcommand | Inputs | Output |
| --- | --- | --- |
| `write-jcl` | `--manifest`, `--source-map`, `--unit` | JOB-less SL write deck using IEBGENER and IEBCOPY |
| `install-jcl` | `--manifest`, `--allocations`, `--profile`, `--hlq`, `--site`, `--tape-unit`, `--dasd-unit`, `--dasd-vol` | JOB-less in-stream PROC for the selected profile, after BT0002 is restored |
| `review-tape` | `--manifest`, `--labels`, `--files` | JSON comparison of saved HETMAP -l and -f reports to manifest sequence/volume |
| `review-mr10` | `--report`, optional `--root` | JSON comparison of ordered TEST, RP, EXP and interpreted CODE against independent MR10 goldens |

Run with Python 3 and PyYAML (manifest commands); see each subcommand's `--help`. Source-map JSON maps decimal sequence strings (e.g. "1") to explicit, already-staged source DSNs and must cover all logical datasets. Allocation JSON maps each payload sequence (3 onward) to three positive integers: primary tracks, secondary tracks and directory blocks. Use the approved manifest and allocation evidence for the intended candidate, never reuse an old staging namespace or approval automatically.

The generated installer uses the accepted RC4 layout (BT0001 FB80 bootstrap, BT0002 PDS COPY control member, FB80/800 and U/6144 recipient PDSes). It refuses unsupported layouts and DCBs. The interface is offline only: it does not establish source lineage, registry or rights approval, catalog absence, free space, JES completion, record fidelity or release acceptance. Before any new live operation, use the canonical manifest validator and obtain the separately approved MVS preflight and operational scope. For historical RC4 use the published companion guide rather than regenerating or replaying it.

Offline test command (from the repository root): `python3 -B -m unittest discover -s tools/distribution -p test_release.py -v`. The tests include frozen RC4 writer and three profile rendering digests. Saved evidence comparisons are not a substitute for fresh actual MVS verification.

## Reusable functionality to retain

- [validate-manifest.py](validate-manifest.py) — read-only schema/selection validation, used by the later producer. The default input is the TA.0 design inventory; explicitly select the intended manifest.
- [audit-jcl-dependencies.py](audit-jcl-dependencies.py), [audit-binary-build-chain.py](audit-binary-build-chain.py), [audit-mvs-build-evidence.py](audit-mvs-build-evidence.py) — candidate input and saved evidence analysis; historical TA.0 assumptions need review before generalization.
- IEBPTPCH decoding/page framing, IEHLIST directory review, ICINT19 execution verification and inventory collection — potentially reusable MVS evidence functions; retain tests and extract only demonstrated reusable code.

The validator's strict --release mode requires complete inventory and rights evidence. It is not a substitute for the actual qualified RC4 acceptance or legal permission.

## Historical TA.0 tools

The pilot submission/recovery, failed-pilot inspection, evidence reconciliation, relocation and compatibility utilities are retained for historical evidence and possible dependencies. They are not routine operator procedures; some submit JES jobs or move private evidence. Do not replay historical operations.

See the [manifest and tests](../../packaging/distribution/manifest/README.md) and [post-release audit](../../packaging/distribution/post-release-audit-20261124.md). [Previous TA.0 README](https://github.com/cbmira01/BCPL-for-MVS/blob/9f382203fcd6a5424cd916f304e3210c0f650212/tools/distribution/README.md) preserves the original commands and limitations.

## Private end-to-end integration exercise

The owner-approved [integration harness](integration.py) verifies the four offline release functions with a fresh private test tape and actual MVS jobs. BC0005 is permanently reserved for this test in the release registry; this is not RC5. Default invocation plans only; `--run` performs read-only preflight and requests one interactive approval before any new staging/tape/installation changes. The fixed namespaces X5ST/X5MR/X5NT/X5CB must be absent and the accepted RC3/RC4 tapes unchanged. Never retry a consumed marker. Run without concurrent MVS tape or dataset operations; preserve all test evidence and media. The historical transport helpers remain dependencies until verified consolidation. See the [audit](../../packaging/distribution/post-release-audit-20261124.md) for scope and limitations.

**Result, 24 November 2026:** The BC0005 one-shot exercise passed on actual MVS: 21 datasets/64 tape files, 42 installed PDSes/315 members, 24 regressions and 56 demonstrations. The test is consumed; do not use `--run` again. Preserve the private evidence at `workarea/release-integration/20261124T205914Z-45447` and see the audit for qualifications. All four release.py operations are verified for the exercised RC4 layout, but the historical transport dependencies remain.
