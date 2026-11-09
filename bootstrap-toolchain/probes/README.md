# Active and dependency-retained native probes

This directory contains **isolated test fixtures still referenced by current
host-side preparation, acceptance or regression tools**, plus two unresolved
historical investigations. These fixtures are not normal compiler/library
product modules. Use the authoritative acceptance runbooks before submitting
any JES job.

| Directory | Why it remains here |
| --- | --- |
| [`m42-real-open/`](m42-real-open/README.md) | M4.2 source and input fixtures consumed by three MVS job preparers |
| [`q0-integrated-16-dcb/`](q0-integrated-16-dcb/README.md) | Corrected integrated 16-DCB test needs separate verification; uses adjacent 16-DCB generator |
| [`q0-qsam-16-dcb-probes/`](q0-qsam-16-dcb-probes/README.md) | Dependency of the integrated Q.0 generator |
| [`r0-export-trailer-probe/`](r0-export-trailer-probe/README.md) | Consumed by R.3 acceptance and R.5 regression preparation |
| [`r0-g150-startup-probe/`](r0-g150-startup-probe/README.md) | Source-probe MVS verification was pending in its dated record |
| [`r1-registration/`](r1-registration/README.md) | R.1/R.3 acceptance and host checks |
| [`r2-interoperability/`](r2-interoperability/README.md) | R.2/R.3 acceptance tests |
| [`r4-bcx-macros/`](r4-bcx-macros/README.md) | R.5 packaging and native regression fixture |

**Historical research relocated without loss of underlying sources:**

- [Q.0 QSAM probes](../../packaging/archive/qsam/probes/README.md)
- [R.0 and IEWL research probes](../../packaging/archive/runtime-extensions/probes/README.md)
- [M4.2 exploratory OPEN notes](../../packaging/archive/core-runtime/probes/README.md)

A closed march is not an authorization to submit archived experimental JCL.
Archive scripts may use a historical dataset layout and require deliberate
review before any execution.
