# Cambridge bootstrap investigations — historical

The files below are retained for evidence and provenance, **not** as current
build instructions. They describe early interpreted compiler experiments:
old tool paths, next steps and provisional conclusions can be superseded.
Use the [current bootstrap guide](../../../bootstrap-toolchain/bootstrap-cambridge/README.md)
and [clean-room reconstruction guide](../../../docs/Rebuild-BCPL-for-MVS-from-source.md)
for the operative procedure.

- [JOB 883 capacity](job-883-capacity.md) — initial SYN workspace limit
- [JOB 893 master global capacity](job-893-master-global-capacity.md) — ICINT global bound
- [Jobs 898–906](checkpoint-jobs-898-906.md) — compilation of Cambridge sections
- [Resident-image probe](resident-image-probe.md) — initial all-resident experiment
- [Resident compiler checkpoint](resident-compiler-checkpoint.md) — initial integrated compiler execution
- [Early demotion specification](demotion.patch) — not an applicable patch or current transformation contract

The native CG370 code-generation checkpoint is kept separately in
[evidence](../../evidence/bootstrap-cambridge/native-codegen-checkpoint.md).
The current source generator is
[`make-demoted.py`](../../../bootstrap-toolchain/bootstrap-cambridge/make-demoted.py).

Additional early bootstrap records:

- [Pre-M3 BLIB object-library foundation](object-library/README.md) — Stage A and resident BLIB build evidence (original generators retired)
- [Historical BLIB integration march](blib-integration-march-checkpoint.md)
- [Interpreter capacity investigation](bootstrap-capacity-notes.md)
- [Early kit-compiler strategy discussion](kit-compiler-strategy.md)
- [Former bootstrap overview](bootstrap-toolchain-legacy-readme.md) — preserved before operational overview rewrite

- [Early MVS-resident compiler workflow](mvs-resident-cambridge-early-workflow.md) — superseded pre-reconstruction dataset names and commands; consult the current rebuild runbook instead
