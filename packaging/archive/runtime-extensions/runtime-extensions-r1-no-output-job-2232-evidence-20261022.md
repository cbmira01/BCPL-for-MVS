# Milestone Runtime Extensions — R.1 no-output JOB 2232 evidence

**MVS execution:** 22 October 2026 (reported by TK5).
**Disposition:** **PASS** — normal FINISH with no BCPL application output.
This is an isolation result; it does not accept integrated diagnostic 1001
or close R.1.

## Source and job

The demoted Cambridge compiler built
`bootstrap-toolchain/probes/r1-registration/no-output.bcpl` in JOB 2231,
producing `workarea/runtime-extensions-r1/no-output.s370.asm`.
The compiled `START` contains `FINISH` only (no WRITES/NEWLINE).
`make-jobs.py no-output` linked it with the genuine empty BCPLREG,
temporary R.1 BCPLMAIN adaptation, RGINIT/RGFINI, and the accepted
Core Runtime components read-only from BOOT_OBJ.

The execution job was **JOB 2232 R1NOOUT** (the separately returned
JOB 2231 was the compiler job).

| Step | Program | JES result |
| --- | --- | --- |
| ASMA | IFOX00 | RC=0000 |
| ASMN | IFOX00 | RC=0000 |
| ASMR | IFOX00 | RC=0000 |
| ASMG | IFOX00 | RC=0000 |
| LKED | IEWL | RC=0000 |
| GO | Linked temporary load module | **RC=0000** |

IFOX flagged **zero** statements, highest severity zero.
GO used `TIME=(,2)` and completed normally with 0.00 seconds
reported GO CPU time. The job summary reported SUCCESS,
highest RC=0000. No BCPL application output was expected or emitted.
The JES report shows `BOOT_OBJ` accessed as `DISP=SHR`.

## Interpretation and narrower hypothesis

The R1NOOUT result disproves the proposed broad explanation
that BCPLIO cannot close SYSPRINT when no application record
has been written. JOBs 2229 and 2230 therefore point to a
**registration-rejection-specific** error path.

Source review identifies a concrete register-protocol defect in the
temporary R.1 BCPLMAIN adapter:

- `IOFIN` sets **R10** to its private code base and does not
  preserve the caller's R10. The normal `FINEXIT` path explicitly
  uses `LR 9,10` before calling IOFIN and `LR 10,9` after return.
- The R.1 `R1BAD` rejection path lacked these two instructions,
  then executed `BAL 14,RELMEM`, assembled using R10 as the base
  register for the target instruction address.
- Thus, after IOFIN returns, the rejection branch can reach the
  wrong address. This is a **source-confirmed contract violation**
  and a strong explanation for the repeatable S322, but the precise
  causal chain still needs MVS retesting.

The narrow candidate fix saves and restores R10 through R9 around
IOFIN in both rejection and test-only leakage cleanup paths.
It deliberately **does not** reorder IOINIT and RGINIT,
change accepted BCPLMAIN/BCPLIO/BOOT_OBJ, or raise GO CPU limits.

**Next required MVS evidence:** regenerate and submit R1N1001.
Require diagnostic `BCPLREG 1001`, no START output, no partial
G!298/G!299 publication, and GO **RC=0012**. Do not count
any host-only checks as this MVS acceptance.
