# TA.7 — RC4 clean-namespace technical acceptance — 24 November 2026 EST

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Tape artifact release
**March:** TA.7 — Clean-Target Integration and Release Acceptance
**Disposition:** Technical PASS (qualified); ready for explicit owner closure.
**Candidate:** BCPL-0.1.0-rc4 / BC0004
**Implementation:** 6038fe025caef1bb5a73cba4a8416d1dd0cddd20

## Actual MVS results reported by the owner

The owner supplied console output from the guarded TA.7 controller.
Preflight JOB 9423 verified all 42 target PDSes absent and tape drive EMPTY.
The owner confirmed the single installation and functional campaign.

| Profile | Namespace | PDSes | Members | Result |
| --- | --- | ---: | ---: | --- |
| MR10 | HERC02.BCPL.T7MR | 11 | 94 | PASS |
| NATIVE | HERC02.BCPL.T7NT | 11 | 71 | PASS |
| COMBINED | HERC02.BCPL.T7CB | 20 | 150 | PASS |
| Total | | 42 | 315 | PASS |

The controller gates each installation result on actual tape-resident
profile execution, ordered IEF142I RC0000 steps, and exact MVS catalog,
DCB and PDS member directory checks against the RC4 manifest.
NATIVE and COMBINED each include all eight native-group PDSes and 41
native-group members, plus the 15 selected Cambridge source members.

| Functional suite | MR10 JOB | COMBINED JOB | Cases per profile | Steps per job |
| --- | ---: | ---: | ---: | ---: |
| MRLANGDM | 9431 | 9447 | 11 | 38 |
| MRBCDEMO | 9433 | 9449 | 17 | 62 |
| MRREGRES | 9435 | 9451 | 12 | 63 |

Both MR10-capable profiles passed all 40 cases independently:
56 demonstrations and 24 automatic regression verdicts in total,
with 326 required functional JES steps. Each regression verdict
requires TEST identity, fixed EXP and evaluated RP against the
independent golden records, and interpreted CODE=0. Human per-case
signatures are not required. Installed JCL was read back through MVS
before retargeting to the corresponding namespace. No interpreter
rebuild or native functional test was required or performed by the
controller. TA.4 rebuild acceptance remains preserved.

Final owner-reported console result:

```text
TA.7 PASS: 42 PDSes / 315 members; 24 regressions, 56 demos; RC4 unchanged.
Evidence: workarea/ta7-clean-namespace/20261124T133036Z-41593
```

## Evidence and qualification

Private original evidence:
`workarea/ta7-clean-namespace/20261124T133036Z-41593`.

Consumed one-shot marker:
`workarea/ta7-clean-namespace/BC0004-ta7-no-retry.json`.

The controller seals its per-job reports and result JSON with SHA256SUMS
before reporting PASS. The assistant reviewed the committed controller and
the owner's reported output, but did not directly open the private raw
reports, seal, local checkout identity or marker. Job numbers not printed
by the owner are not inferred. The reported final PASS includes the
controller's before/after checks of RC4 and original RC3 media checksums.

RC4 SHA-256:
`7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`.

Acceptance is qualified to fresh namespaces on the existing MVS 3.8J
system, as explicitly directed by the owner in
[the superseding TA.7 decision](ta7-clean-namespace-decision-20261124.md).
It does not establish independent-system IPL, alternate account/HLQ
portability, byte-for-byte comparison of every restored native member,
or native compiler/runtime functional certification. The native compiler
is absent; TA.6 remains N/A. Native components are distributed as work
in progress.

## Disposition

All owner-approved revised TA.7 technical gates are satisfied on
owner-reported actual MVS evidence. TA.7 is ready for formal qualified
closure; the owner has not yet explicitly directed that closure.
Do not rerun the consumed TA.7 operation or modify any accepted
namespace, tape, marker or prior evidence. TA.8 — Release Audit and
Controlled Publication remains pending. Publication is not authorized.
