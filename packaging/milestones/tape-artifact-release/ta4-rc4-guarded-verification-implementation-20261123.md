# TA.4 — RC4 MR10 rebuild and demonstration verification implementation

**Milestone:** Tape artifact release  
**March:** TA.4 — MR10 Kit Compiler Distribution and Verification  
**Status:** IN PROGRESS; no new MVS execution claimed  
**Candidate:** `BCPL-0.1.0-rc4` / `BC0004`  
**Baseline source commit:** `e910de51c19c09698be139e33084a90401511cc9`

## Preserved evidence

TA.3 is CLOSED (qualified). Preserve the accepted RC4 MR10-only installation
`HERC02.BCPL.R4MR.MR10KIT.*`, RC4 AWS SHA-256
`7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`,
and the earlier BC0003 JOB 9369 63-step/12-case semantic PASS. The final
individual human `SIGN` receipt remains outstanding. Do not replay JOB 9369
or any accepted producer, restorer, or installer.

## Tracked implementation

`install-from-tape/scripts/ta4-mr10-verification` reuses the existing
repository JES submission and immutable evidence helpers.

- No argument: source-controlled offline JCL plan; no MVS operations.
- `--preflight`: validate pinned Git/release source and RC4 media; submit only
  a read-only MVS `LISTDS LABEL` inquiry; check nine installed MR10 PDS DCBs
  and absence of both verification targets; seal the preflight record.
- `--run`: repeat the complete preflight, ask one explicit `[y/N]` approval,
  then consume a no-replay marker and submit guarded MVS jobs.
- Rebuild: allocate only `HERC02.BCPL.TA4R1.OBJ` (PO/FB/80/800) and
  `HERC02.BCPL.TA4R1.LOAD` (PO/U/0/6144); assemble distributed
  `ASM(ICINT19)` using IFOX00, link using IEWL and save the relocatable object.
- Rebuilt execution: use a rebuilt-load `STEPLIB` for all three SCALVEC
  compiler/generator/execute steps; compare `TEST:`, `EXP:`, `RP:` and
  interpreted `CODE=0` through the existing semantic reviewer.
- Language and BCPL demonstrations: independently use the installed
  `R4MR` load library, 11 selected `MRLANGDM` cases (38 steps) and
  17 selected `MRBCDEMO` cases (62 steps); require full ordered JES/IEF142I
  RC0000, interpreted zero codes and program `DEMO:` evidence.
- Store full submitted JCL, JES summary/report, semantic JSON, one-shot
  marker and sealed outcomes under `workarea/ta4-mr10-verification/`.

The script never stages/writes/remounts tape or changes the accepted
`R4MR` installation. Any post-approval failure is a no-retry incident;
investigate the saved MVS evidence before authorizing a new isolated target.

## Local verification and boundaries

The isolated assistant workspace ran 18 positive/negative Python tests
successfully and checked the generated JCL contract against the actual
canonical GitHub sources. Actual MVS IFOX, IEWL, SCALVEC and 11+17 demonstration
results remain **PENDING**, not PASS. Human sign-off is a separate,
read-only, owner-performed review of sealed JOB 9369 evidence through
`create-tape/scripts/ta2-rc3-human-review --signoff`; it requires twelve
individual PASS/FAIL verdicts, a reviewer identifier and exact uppercase
`SIGN`. No new MRREGRES job is required merely for sign-off.

**TA.4 cannot close until all remaining actual MVS and human gates pass.**

## 23 November — first TA.4 preflight refusal; tested RC contract repair

The owner reported:

```text
TA.4 VERIFICATION HALTED: T4R1PRE: actual MVS step list/RC differs
Evidence: workarea/ta4-mr10-verification/20261123T211811Z-39250
```

This occurred within the **read-only** TSO `LISTDS LABEL` preflight,
before the `[y/N]` prompt and before any no-retry marker or build allocation.
The original private `workarea` JES report is retained on the owner's system;
its exact observed RC has **not** been independently inspected in the
assistant workspace. No IFOX, IEWL, compiler, demo or signed review result
is claimed.

The source defect was identified in the runner: it invoked the shared
`ta3-rc3-recipient.mvs_job` with `max_rc=8` while also passing
`expected=[('STAT','IKJEFT01')]`. That helper demands exactly RC0000 for
each supplied expected step, contradicting the accepted return-code range
for a `LISTDS` inquiry of two intentionally nonexistent target PDSes.

The correction calls that shared helper with `expected=None` for this
preflight only, then independently requires the single exact
`STAT/IKJEFT01` JES step at RC0000/0004/0008 and a matching, unique
`IEF142I` MVS completion. It continues to reject system abends and to
verify *every* installed dataset's exact PDS/DCB plus both build targets'
nonexistence. **Successful overall preflight requires all these checks**;
accepting RC0008 does not by itself assert success.

The assistant executed **21/21** isolated local unit tests for the revised
runner, including RC0000/0004/0008 successes, RC0012, wrong job/step,
duplicate MVS completion, JES/IEF142I disagreement, abend refusals, and
the separate per-dataset checks. Both new Git blob contents were checked
against the tested local files' Git object IDs. Actual amended MVS
preflight and state-changing verification remain outstanding.

Since the first operation never reached owner confirmation, the original
one-shot marker should remain absent. The guarded runner may be invoked
again after updating GitHub `main`; it performs another **read-only**
preflight and requests a fresh `[y/N]` confirmation before changing MVS
state. Preserve the first refusal evidence and do not replay any earlier
accepted producer, installer, or regression operation.
