# TA.4 — MR10 automatic acceptance: owner-reported evidence and closure readiness

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.4 — MR10 Kit Compiler Distribution and Verification  
**Date:** 23 November 2026 EST / 24 November UTC  
**Disposition:** **All TA.4 technical acceptance gates PASS (owner-reported and previously documented); READY FOR FORMAL OWNER CLOSURE**  
**Candidate:** `BCPL-0.1.0-rc4` / `BC0004`

## Actual automated acceptance

The owner ran the source-controlled, read-only
`packaging/distribution/install-from-tape/scripts/ta4-mr10-automatic-acceptance`
from GitHub `main` after commit
`145da0e3f0306cf0573216cffa8f1e6d5b37029e`.

Reported terminal result:

```text
TA.4 AUTOMATED ACCEPTANCE PASS: 12/12 MRREGRES; 11+17 demos; rebuilt ICINT19.
Evidence: workarea/ta4-mr10-automatic-acceptance/accept-20261124T003512Z-40183
```

This program validates the original JOB **9369** sealed BC0003
63-step/12-case MVS `TEST:` / literal `EXP:` / calculated `RP:` /
interpreted `CODE=0` data against independently retained golden
records, and the separate RC4 sealed five-job results:

| Actual MVS job | Scope | Accepted result |
| --- | --- | --- |
| **9418** | Nine installed MR10 PDSes and two fresh-target absences | Preflight PASS |
| **9419** | Isolated IFOX/IEWL interpreter rebuild | Four steps PASS |
| **9420** | Rebuilt `ICINT19` SCALVEC semantic execution | Eight steps PASS |
| **9421** | Language demonstrations | 11 cases, 38 steps PASS |
| **9422** | BCPL demonstrations | 17 cases, 62 steps PASS |

Original completed verification:
`workarea/ta4-mr10-verification/20261123T212347Z-39337`.
Original RC3 JOB 9369 verification:
`workarea/ta2-rc3-installed-mr10-continuation/20261123T000015Z-32502`.

The unchanged host-side `tools/mr10/run-regression-panel` was already
reported by the owner on **22 November 2026** as **12 PASS /
0 FAIL / 12 total / RC=0**, after all 23 literal `EXP:` records
were added to the canonical sources. This is documented in
[the milestone's 22 November regression checkpoint](milestone-tape-artifact-release.md)
and satisfies the separate unchanged WSL `RP:`/`CODE=` test
requirement without executing it again.

The owner superseded all per-case human verdicts and `SIGN`
requirements on 23 November 2026. The automated verifier,
not JES RC0000 alone, supplies twelve separately checked per-case
decisions; any divergence refuses acceptance. See
[the TA.4 automated semantic acceptance decision](ta4-automatic-semantic-acceptance-decision-20261123.md).

## Qualification and decision boundary

The reported PASS comes from actual execution of the source-controlled
saved-evidence reviewer against private, SHA256-sealed local MVS
artifacts. These private files were **not directly opened by the
assistant**; do not describe the supplied transcript as independent
assistant file inspection. The result is accepted as an
**owner-reported technical checkpoint**, with its evidence preserved
under the owner's ignored repository `workarea/` directory.

No MVS job, image production, restore or regression job is to be
replayed for administrative acceptance. No new tape, no alteration
to the accepted `R4MR` installation or `TA4R1` object/load targets,
no modification of prior seals, and no release publication occurred
during the read-only acceptance.

**TA.4 technical gates are satisfied. Formal march closure remains
an explicitly recorded owner decision**, as in the TA.0–TA.3
transitions; this record is not itself a purported owner instruction
to close the march.

After that decision, proceed to **TA.5 — Native Runtime,
Libraries, and Extensions Distribution** within the same
**Tape artifact release** milestone, using separate, guarded native
acceptance on existing installed `R4NT`/`R4CB` libraries.
TA.6 is N/A because the candidate declares
`native_compiler: absent`. TA.7 and TA.8 remain independent,
and controlled publication is not authorized.
