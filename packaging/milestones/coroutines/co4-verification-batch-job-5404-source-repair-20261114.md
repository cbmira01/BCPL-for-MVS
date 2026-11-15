# CO.4 — First batch attempt JOB 5404 FAIL and reviewed source repair

**Project:** BCPL for MVS 3.8 Reconstruction
**March:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)
**Original source revision:** `6d6ee095b68253ecd175055fdaa2218a6eba0298`
**Report:** Owner-operated MVS batch, 14 November 2026 local (15 November UTC)
**Evidence classification:** **OWNER-REPORTED COMPILER FAILURE; NOT NATIVE-MVS-TESTED**

## Preserved original failure

The owner performed an exact-revision guarded pull and ran
`python3 -B tools/coroutines/run-co4-verification-batch.py --run`.
Observed console output:

```text
CO.3 first lifecycle FAIL: CO3ACMP compiler RC=2, jobs=['5404']
CO.4 STACK FAIL
CO.4 batch FAIL (0/3)
CO.4 batch evidence: /home/calvin/Source/Repos/BCPL-for-MVS/workarea/co4-verification-batch/20261115T022139Z-4ygdp7hr
CO.4 batch RC=1
```

The first Cambridge **application** compilation failed. No successful
IFOX/IEWL/GO evidence was produced for STACK, and the CHURN and BUSY
cases were **not attempted**. The source compiler job is JOB **5404**.
The reason for host compiler RC=2, including any nonzero compiler
execution code or underlying Cambridge diagnostic, **has not been
independently retrieved from the owner's MVS JES listing**.

## Source investigation and candidate correction

Review of the committed STACK fixture found a second `LET GUARD=...`
declaration after the executable `IF END-BASE ...` statement in the
same `CHECK` block. Cambridge BCPL blocks use their initial declaration
group before commands. This violates the reconstructed source layout
and is a plausible cause of the compilation failure. All local CHECK
variables are now declared in one initial `LET ... AND ...` group before
the first `IF`.

For consistency, local variable `END` is renamed `TOP` in the three
new batch fixtures; this removes an unverified identifier choice
without changing the computed extent. No accepted CO.3 library source,
assembler, public slots, stack geometry, or worker count is changed.

The native batch runner now records the inherited failure `reason` and
prints one bounded, filtered compiler diagnostic when available in
`CO3ACMP.log` or `CO3LCMP.log`; it never dumps full printer SYSOUT.
Regression tests explicitly reject the previous late-declaration
layout and cover bounded error extraction.

## Host verification of repaired source

Performed in an isolated assistant workspace with the accepted CO.3
library, CO3DROP and `/CN` compiler parameter bytes pinned to their
unchanged Git blob identities:

- `run-co4-verification-batch.py --check`: **PASS**.
- `python3 -W error -B -m unittest discover -s tools/coroutines -p test_run_co4_verification_batch.py`: **15 PASS**, 0 FAIL.
- Both Python modules compile with `python -W error -m py_compile`: **PASS**.
- All three repaired BCPL sources satisfy ASCII, <=80 columns,
  source-contract and strict per-case oracle checks: **PASS**.

**Limit:** Host checks do **not** establish that JOB 5404's compiler
failed for precisely this reason, and they cannot substitute for real
Cambridge/IFOX/IEWL/MVS execution. The next operator MVS batch rerun
must be recorded independently; no previous FAIL is overwritten or
reclassified as PASS. This source repair does not close CO.4 or start
CO.5.
