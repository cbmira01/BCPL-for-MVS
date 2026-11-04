# MR10 development probe 05-named-dd — initial acceptance

**Project:** BCPL for MVS 3.8 Reconstruction
**Case:** `05-named-dd`
**Owner decision:** ACCEPTED on 4 November 2026; limited to this initial golden-output baseline
**Source Git revision:** `eab7b8ce9f5f160678bf2802cb0628cd27e23f99`
**Target:** MVS 3.8J / TK5, MR10 compiler under `icintv19.asm`

## Execution identity

- JES JOB 9543, job name DP018361, 04 NOV 26, 19:09:06–19:09:07 MVS job time.
- Host runner: `tools/mr10/run-dev-probes --run --case 05-named-dd`.
- Main source: `mr10-kit-compiler/tests/05-named-dd/main.bcpl`.
- Named DD `EXTRA`: `mr10-kit-compiler/tests/05-named-dd/extra.bcpl` (`XVAL = 12345`).
- Initial runner result OBSERVED, RC=3, before owner acceptance.
- Operator-local evidence: `workarea/mr10-probes/20261104T180906Z-28361-3pazfpy9/`.
- The supplied `summary.json`, `05-named-dd.log` and extracted `05-named-dd-jes-report.txt` reside on the operator workstation; they are not Git-tracked.

## MVS/JES verification

| Step | Program | JES RC |
| --- | --- | --- |
| ASM | IFOX00 | 0000 |
| LKED | IEWL | 0000 |
| STGSYNI | IEBGENER | 0000 |
| STGTRNI | IEBGENER | 0000 |
| STGCGI | IEBGENER | 0000 |
| STGBLIB | IEBGENER | 0000 |
| STGICLIB | IEBGENER | 0000 |
| COMP | RUNMOD | 0000 |
| CG | RUNMOD | 0000 |
| RUN | RUNMOD | 0000 |

`tools/mvs/job-summary 9543 --max-rc 0` returned RC=0, job result SUCCESS and highest RC=0000.
The extracted JES report identified DP018361 and confirmed the ten executed steps without a reported ABEND.
The COMP, CG and RUN phases each completed at interpreted `CODE=0` (89,627, 19,785 and 891 execution cycles, respectively).

Final program output, excluding ICINT metadata:

```text
VALUE FROM EXTRA = 12345
```

## Scope and qualification

The owner accepted this execution as the initial golden-output baseline. The accepted
program-output record is stored in `05-named-dd.expected`. Future PASS results
must match the golden output, ten JES RC=0000 steps and three interpreted CODE=0 phases.
The revised runner still requires its own fresh live MVS verification.
The other 16 development probes remain UNVERIFIED, and the existing 12-case
MR10 Regression Panel and project regression coordinator remain unchanged.
