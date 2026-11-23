# TA.4 — RC4 MR10 Kit Compiler MVS technical verification checkpoint

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.4 — MR10 Kit Compiler Distribution and Verification  
**Date:** 23 November 2026 EST  
**Disposition:** **MVS interpreter-rebuild and 11+17 demonstration technical gates PASS (qualified, owner-reported)**; **TA.4 IN PROGRESS**, human sign-off outstanding.

## Candidate, recipient and non-replay scope

- Candidate: `BCPL-0.1.0-rc4`; tape VOLSER `BC0004`.
- Accepted AWS SHA-256: `7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`.
- Installed MR10 inputs: `HERC02.BCPL.R4MR.MR10KIT.*`; accepted installation was not replaced.
- Fresh build outputs: `HERC02.BCPL.TA4R1.OBJ`, `HERC02.BCPL.TA4R1.LOAD`.
- Verification implementation at GitHub `main` commit `2520e2e4478a59e795029b5e9c900d7c317148c0` (preflight RC correction).
- New sealed private MVS evidence reported at `workarea/ta4-mr10-verification/20261123T212347Z-39337`.
- The original read-only preflight refusal evidence `workarea/ta4-mr10-verification/20261123T211811Z-39250` remains preserved.

## Owner-reported actual MVS 3.8J execution

| MVS JOB | Runner stage | Actual steps | Reported result |
| --- | --- | ---: | --- |
| **9418** | `T4R1PRE` — `LISTDS LABEL` on nine installed MR10 PDSes and two absent fresh targets | Read-only inquiry | PASS |
| **9419** | `T4R1BLD` — isolated IFOX00 assembler, IEWL link, object save and allocation | 4 | PASS |
| **9420** | `T4R1GO` — rebuilt-load SCALVEC compiler/generator/execute | 8 | PASS |
| **9421** | `T4R1LNG` — all 11 selected language demonstrations | 38 | PASS |
| **9422** | `T4R1BCD` — all 17 selected BCPL demonstrations | 62 | PASS |

The reported successful runner enforces exact ordered JES/IEF142I step
completion RC0000 for each stateful job, matches the rebuilt-interpreter
SCALVEC `TEST:`/`EXP:`/`RP:` and interpreted `CODE=0`, and checks
the language and BCPL demonstrations for required `DEMO:` output and
zero interpreted codes. It seals planned/source JCL, actual MVS reports
and semantic receipts before returning success. The provided terminal
transcript ends:

```text
TA.4 MVS REBUILD + DEMONSTRATIONS PASS; JOB 9369 preserved; 12-case human sign-off remains separate.
Evidence: workarea/ta4-mr10-verification/20261123T212347Z-39337
```

**Evidence qualification:** The owner supplied the MVS runner terminal
output; the private sealed `workarea` artifacts were not directly opened
by the assistant. This is an owner-reported actual-MVS checkpoint, not a
claim of independently read JES datasets. The successful, marker-consumed
`TA4R1` operation must **never** be rerun solely for additional proof.

## Remaining TA.4 acceptance gate

The accepted earlier **JOB 9369** under `BCPL-0.1.0-rc3`/`BC0003`
remains the predecessor full 63-step `MRREGRES` evidence with
12/12 automated `TEST:`/`EXP:`/`RP:`/`CODE=0` PASS.
That job must not be repeated for administrative sign-off.

Formal human review still needs a **sealed receipt** containing twelve
individually reviewed PASS/FAIL verdicts, the reviewer identifier,
and explicit final `SIGN` confirmation. The approved read-only
`packaging/distribution/create-tape/scripts/ta2-rc3-human-review --signoff`
replays saved original MVS evidence without any MVS submission, tape
operation, or dataset modification. A human FAIL blocks acceptance.
Previous twelve PASS selections with reviewer `cm` did not generate a
receipt because the final confirmation was not accepted.

**Status:** TA.4 technical MVS gates PASS (qualified); formal TA.4
acceptance and closure **PENDING** the identified human sign-off and owner
decision. TA.5, TA.7 and TA.8 retain their independent gates; TA.6 is
N/A for this candidate because the native Cambridge Compiler is absent.
No release publication is authorized.
