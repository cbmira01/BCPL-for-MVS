# MVS deployment and reconstruction

The canonical MVS dataset manifest is [`config/dspal.yaml`](../config/dspal.yaml) and its operator interface is `tools/datasets/dspal`. All tracked source files and build JCL reside in Git; MVS libraries hold deployed sources and rebuildable outputs.

## Complete reconstruction

**[Clean-room MR10-to-native MVS reconstruction runbook](clean-room-mvs-reconstruction.md)** is the single chronological procedure for emptying `workarea/`, inspecting and purging the manifest-defined PDS set, reinitialization, text population, ICINT19 rebuilding, MR10 demos/tests, demoted Cambridge bootstrap, runtime object rebuilding, and the complete native regression panel.

[Accepted M3 evidence](m3-native-reconstruction-acceptance-20261015.md) records the demonstrated component builds and **123 PASS / 0 FAIL / 1 expected SKIP** for the full native regression panel. The single combined destructive procedure still requires one-run verification.

## Proposed optional native I/O milestone

[Milestone QSAM](milestone-qsam.md) defines a separately gated Q.0–Q.5 roadmap for a native BCPL QSAM record-I/O extension. It is **proposed, not started**, and is not a dependency of M4. Candidate object builds must remain separate from accepted runtime objects.

## Proposed optional numeric and clock milestones

- [Milestone Decimal Arithmetic](milestone-decimal-arithmetic.md): packed-decimal fixed-point arithmetic and business-record interoperability, proposed D.0–D.4.
- [Milestone Date and Time Services](milestone-date-and-time-services.md): Gregorian calendar helpers and MVS clock adapter, proposed T.0–T.4.

Both are optional, proposed, and independent of M4 and Milestone QSAM.

## Dataset ownership

| Namespace | Current status | Authority |
| --- | --- | --- |
| `MR10_*` (9 datasets) | Reconstructed historical kit interpreter, tests, demos | `mr10-kit-compiler/` and manifest |
| `NATIVE_*` (6 datasets) | Reconstructed resident compiler INTCODE, native runtime ASM/JCL, objects | `native-compiler/` and manifest |
| `CAMB_*` (9 datasets) | Reserved for M4; **not used for M3 compiler reconstruction** | Manifest allocation only |

`NATIVE_OBJ` contains the accepted BCPLMAIN, BCPLMEM, and BLIB objects. `NATIVE_DEVOBJ` contains independently assembled BCPLAPT, BCPLBYTE, and BCPLIO candidates. No binary migration or implicit object promotion is permitted.

A successful `dspal populate` updates explicitly mapped text members without pruning unlisted members. `dspal purgebcpl` is destructive to **all 24 manifest-managed datasets**; it does not delete datasets outside the manifest and prompts for explicit confirmation. Generated sources and binary outputs must be rebuilt after a purge. Keep local credentials in the ignored `config/dspal.local.yaml`.

## Historical design and evidence

The older proposal and milestone records elsewhere under `packaging/` preserve decisions and rationale as of their stated dates. In particular, previous `HERC02.BCPL.OBJ` proposals and old `SOURCE/JCL/DEVOBJ` commands are historical, **not current installation guidance**.

Useful further references: [Git/MVS source authority](git-mvs-authority.md), [M3 namespace migration log](m3-dspal-namespace-migration.md), and [M2.1 runtime acceptance](m2-1-gate-f-final-runtime-acceptance.md).
