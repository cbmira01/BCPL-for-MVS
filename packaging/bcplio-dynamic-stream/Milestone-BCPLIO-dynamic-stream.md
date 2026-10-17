# BCPLIO dynamic streams — milestone history

**Status: CLOSED and ACCEPTED, 17 October 2026.** This is a concise,
current navigation record, not a replay of the superseded execution journal.
The full chronological notes remain in Git history at
[pre-reorganization baseline](https://github.com/cbmira01/BCPL-for-MVS/blob/2164a4ef163c9d757c5b2f5d37c95481839287c5/docs/Milestone-BCPLIO-dynamic-stream.md).

## Accepted result

The DEVOBJ candidate consists of independently linked BCPLM6 and BCPLIO,
with BCPLBYTE and BCPLAPT from DEVOBJ and BCPLMEM/BLIB from NATIVE_OBJ.
The Cambridge compiler remains INTCODE run by ICINT19. No production
NATIVE_OBJ promotion was authorized.

The fresh native 00..145 run at `57c7354` completed with
**145 PASS, zero FAIL and expected SKIP 083**; an independent auditor
checked **145/145 fresh case logs**. JOB 8184 demonstrated distinct
class A/Z formatted-printer routing; JOB 8185 verified separate
QSAM FB132 sequential datasets by full 132-byte EBCDIC comparisons
including padding, order/count and EOF; JOB 8186 intentionally altered
an expected padding byte and the verifier rejected it with RC0012.
This does **not** establish raw JES2 spool-byte identity.

A later duplicate runner invocation overwrote the normal transcript
and some per-case logs after successful verification. The owner
accepted the contemporaneous evidence; the original receipt and
matching TSV are archived under
[verification evidence](../bcplio-dynamic-stream-evidence/).
The milestone is not reopened by that later overwrite.

See the [formal acceptance record](Milestone-BCPLIO-dynamic-stream-final-acceptance.md)
for exact claims and limitations.

## Durable engineering outcomes

- [Design rationale](design-rationale.md): accepted M0 stream lifetime,
  DD-name, duplicate FIND and error-handling decisions.
- [Runtime contract](BCPLIO-dynamic-runtime-contract.md): current
  programmer-visible character streams mapped to MVS QSAM.
- [JCL/QSAM responsibility boundary](BCPLIO-JCL-QSAM-stream-contract.md):
  MVS owns actual dataset validation and errors that do not return control.
- [Clean-room reconstruction runbook](../clean-room-mvs-reconstruction.md):
  rebuild MVS resident compiler and runtime from tracked sources.

## Historical technical records worth retaining

| March | Durable result |
|---|---|
| M0 | Stable handles, duplicate FIND identity and returned-control failure contract |
| M1–M2 | Dynamic input DD discovery; multiple simultaneous streams, including 16 concurrent inputs |
| M3 | Independent output and mixed streams |
| [M4.2](Milestone-BCPLIO-dynamic-stream-M4.2-plan.md) | OPEN-failure boundary; real failing SVC19 was not demonstrated |
| [M4.3](Milestone-BCPLIO-dynamic-stream-M4.3-plan.md) | Returned-control resource accounting under test-only instrumentation |
| [M5.1](Milestone-BCPLIO-dynamic-stream-M5.1-plan.md) | QSAM FB132 physical dataset readback and printer-class routing |
| [M5.2](Milestone-BCPLIO-dynamic-stream-M5.2-plan.md) | Fail-closed padding-byte negative verifier |
| [M5.3](Milestone-BCPLIO-dynamic-stream-M5.3-review.md) | Permanent regression coverage reconciliation |
| [M5.5](Milestone-BCPLIO-dynamic-stream-M5.5-plan.md) | Final fresh-panel audit and evidence caveat |

M4.4 full-panel intermediate acceptance, M5.0's original stricter JES2
spool proposal, and other dated progress journals were superseded.
Their full text is available in the Git baseline linked above and related
historical commits; none remains an active march.
