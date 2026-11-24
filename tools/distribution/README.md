# Distribution tools

The Tape artifact release milestone is formally CLOSED (qualified). [RC4](../../packaging/distribution/README.md) is the published candidate. This directory contains the manifest validator and TA.0 evidence/inventory tools; it does not contain a general-purpose release producer.

## Reusable functionality to retain

- [validate-manifest.py](validate-manifest.py) — read-only schema/selection validation, used by the later producer. The default input is the TA.0 design inventory; explicitly select the intended manifest.
- [audit-jcl-dependencies.py](audit-jcl-dependencies.py), [audit-binary-build-chain.py](audit-binary-build-chain.py), [audit-mvs-build-evidence.py](audit-mvs-build-evidence.py) — candidate input and saved evidence analysis; historical TA.0 assumptions need review before generalization.
- IEBPTPCH decoding/page framing, IEHLIST directory review, ICINT19 execution verification and inventory collection — potentially reusable MVS evidence functions; retain tests and extract only demonstrated reusable code.

The validator's strict --release mode requires complete inventory and rights evidence. It is not a substitute for the actual qualified RC4 acceptance or legal permission.

## Historical TA.0 tools

The pilot submission/recovery, failed-pilot inspection, evidence reconciliation, relocation and compatibility utilities are retained for historical evidence and possible dependencies. They are not routine operator procedures; some submit JES jobs or move private evidence. Do not replay historical operations.

See the [manifest and tests](../../packaging/distribution/manifest/README.md) and [post-release audit](../../packaging/distribution/post-release-audit-20261124.md). [Previous TA.0 README](https://github.com/cbmira01/BCPL-for-MVS/blob/9f382203fcd6a5424cd916f304e3210c0f650212/tools/distribution/README.md) preserves the original commands and limitations.
