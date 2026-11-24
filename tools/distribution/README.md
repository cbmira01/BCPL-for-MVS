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

## Reusable MVS helpers

[`mvs_release.py`](mvs_release.py) extracts the established MVS operations from the BC0005-tested historical path: staging and bootstrap JCL, tape-unit-480/VOL1 checks, exact installed JCL readback, ordered PROC return-code verification, DSPAL catalog and member/DCB checks, MR10 suite binding and demo verification, JES submission/evidence capture and exclusive evidence sealing. It is a Python library with no standalone live execution command. Use the existing MVS and DSPAL transport; do not bypass authorization, catalog/VTOC and media preflight, exclusive intent or no-retry controls. The module is verified by 13 focused offline tests; its new parameterized interfaces have not yet been exercised in another actual MVS run.

Offline tests for both modules: `python3 -B -m unittest discover -s tools/distribution -p 'test_*release.py' -v`.

## Private end-to-end integration exercise — completed

The [exact consumed integration harness](https://github.com/cbmira01/BCPL-for-MVS/blob/7d8f1e9a8a94901ca4cdb4c895fbb0838cb12bc2/tools/distribution/integration.py) passed actual MVS on 24 November 2026: BC0005, 21 datasets/64 tape files, 42 installed PDSes/315 members, 24 regressions and 56 demonstrations. Preserve the test tape, marker and `workarea/release-integration/20261124T205914Z-45447`. Do not rerun. BC0005 is permanently recorded as used in the registry and is not RC5.

The fixed-candidate harness and RC2–RC4 production/recipient orchestration, dedicated tests and obsolete installer JCL are retired from active main; the [pre-retirement revision](https://github.com/cbmira01/BCPL-for-MVS/tree/bacf928f0364d24d89c6fa2ed3f88e2ff53fd9fc) preserves them and their dependency graph. The RC4 exact-byte publication reviewer and source preparation/fidelity tools remain. No new generic live producer, source reconstruction or full restored-record-byte verification is implied. See the [audit](../../packaging/distribution/post-release-audit-20261124.md).
