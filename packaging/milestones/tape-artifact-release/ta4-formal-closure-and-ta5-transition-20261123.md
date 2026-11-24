# TA.4 formal closure and TA.5 transition — 23 November 2026 EST

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**Owner direction:** “Close TA4, proceed to TA5. Give me a handoff prompt.”  
**TA.4 — MR10 Kit Compiler Distribution and Verification:** **FORMALLY CLOSED**  
**TA.5 — Native Runtime, Libraries, and Extensions Distribution:** **OPEN / IN PROGRESS**  
**Candidate:** `BCPL-0.1.0-rc4` / `BC0004`  
**Authoritative repository:** `https://github.com/cbmira01/BCPL-for-MVS`, `main`

## Formal TA.4 acceptance

The owner explicitly directs formal closure after all four accepted TA.4
gates succeeded. The governing 23 November decision replaced the
prior per-case human-signature procedure with a **twelve-case,
read-only, automatically sealed semantic comparison**, not a
JES-RC-only pass.

The owner reported successful actual MVS verification:

| MVS JOB | Accepted gate | Result |
| --- | --- | --- |
| **9369** (historical `BC0003`) | 63 ordered steps, 12 `MRREGRES` `TEST:`/`EXP:`/`RP:`/`CODE=0` cases | 63/63 step RC0000; 12/12 semantic PASS |
| **9418** (`BC0004`) | Nine installed MR10 PDSes and two absent fresh targets | Read-only preflight PASS |
| **9419** (`BC0004`) | Fresh isolated IFOX/IEWL `ICINT19` rebuild | 4 steps PASS |
| **9420** (`BC0004`) | Rebuilt interpreter SCALVEC | 8 steps and semantic PASS |
| **9421** (`BC0004`) | Eleven MR10 language demonstrations | 11/11, 38 steps PASS |
| **9422** (`BC0004`) | Seventeen BCPL demonstrations | 17/17, 62 steps PASS |

The original, unchanged `tools/mr10/run-regression-panel` was
reported on **22 November 2026** as **12 PASS, 0 FAIL, RC=0**,
following addition of the 23 literal `EXP:` records. This
fulfills the separate unchanged WSL regression requirement.

The owner then ran the Git-controlled
`ta4-mr10-automatic-acceptance` read-only reviewer,
which independently rechecked the sealed JOB 9369 regression
and RC4 rebuild/demo receipts, and reported:

```text
TA.4 AUTOMATED ACCEPTANCE PASS: 12/12 MRREGRES; 11+17 demos; rebuilt ICINT19.
Evidence: workarea/ta4-mr10-automatic-acceptance/accept-20261124T003512Z-40183
```

The source-controlled check was committed at
`145da0e3f0306cf0573216cffa8f1e6d5b37029e`;
its accepted evidence and readiness record were committed at
`ccbc118f7abc267d0e6269ad2a9514b8a8864daa`.
The interactive human-review/signature gate is **superseded**;
there are no remaining TA.4 sign-off prompts.

## Evidence and preservation

The private, SHA-256-sealed evidence is retained on the
owner's repository working system, including:

- `workarea/ta2-rc3-installed-mr10-continuation/20261123T000015Z-32502`
- `workarea/ta4-mr10-verification/20261123T212347Z-39337`
- `workarea/ta4-mr10-automatic-acceptance/accept-20261124T003512Z-40183`

The assistant has not directly inspected these private receipts;
the owner-reported PASS is accepted through the source-controlled
reviewer and preserved actual MVS evidence. Do not repeat
JOB 9369, JOBS 9418–9422, any accepted TA.2/TA.3 production,
tape readback or installation, or consumed no-retry operations.

The `BC0004` tape candidate is unchanged with AWS SHA-256
`7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`.
`BC0003` remains preserved and immutable.

## Formal disposition and boundaries

**TA.4 is formally CLOSED by owner direction.** Its closure
does not assert native Core Runtime, `BLIB`, Coroutine Support,
or optional System Extension linkage/execution from RC4; this is
the distinct **TA.5** acceptance scope. It does not establish an
independently clean-target system (TA.7), legal/provenance
clearance or controlled publication (TA.8). The candidate declares
`native_compiler: absent`, so **TA.6 is N/A**, not PASS.
No release publication is authorized.

## TA.5 opening

**TA.5 — Native Runtime, Libraries, and Extensions Distribution is
formally OPEN / IN PROGRESS.** Its first action is a **read-only
Git-backed inventory and accepted-evidence audit** of the RC4
NATIVE and COMBINED installation, historical build/source lineage,
native linkage and `BCEX/BCRG v1` tests, followed by design
review before any new stateful MVS operation.

Read the [TA.5 kickoff](ta5-kickoff-20261123.md) and
[TA.5 source/provenance entry audit](ta5-entry-audit-and-design-preparation-20261123.md)
before writing or submitting new JCL. Use fresh targets and
separate authorization for any new MVS state change.
