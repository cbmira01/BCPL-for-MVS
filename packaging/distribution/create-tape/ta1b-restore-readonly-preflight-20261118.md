# TA.1 — Track B independent restore read-only preflight PASS

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.1 — Multi-Dataset Tape Mechanics  
**Date:** 18 November 2026, 19:24 EST / 19 November 2026, 00:24 UTC  
**Disposition:** Live read-only preflight **PASS**. **No restore or executable GO was performed**.

## Authoritative operator-reported result

GitHub `main`: `52c128ca4dac2b82549114976f4f4eee807aa9d6`.

Invoked from repository root, **without `--run`**:

    packaging/distribution/create-tape/scripts/run-ta1-track-b-restore

The owner supplied the exact output:

    BTA102 JOB 9120 write receipt and immutable SHA-256 PASS; drive empty.
    TA.1 Track B restore preflight PASS (new DASD PDS still absent).
    No remount, new DASD dataset, restore, IEHLIST or GO executed.
    Evidence: workarea/ta1b-operations/BTA102-track-b-restore-20261119T002435Z-10407

The runner checks the original write attempt receipt, JOB 9120
IEBCOPY `UNLOAD RC=0000` summary, SL labels and filemarks, current
AWS SHA-256, source load library and member inventory, intended
DASD target absence, catalog status of uncataloged tape DSN,
other AWS image VOLSERs and Hercules 0480/MVS tape unit status.
That is the committed source contract, supported by the reported PASS.
The assistant has not independently read the private evidence folder.

**Immutability pin:** BTA102 virtual tape
`mvs-state/tape/bcpl-ta1-b-20261117-01.aws`,
SHA-256 `c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.

## Next distinct owner authorization gate

The approved Track B design calls for independent IEBCOPY
`TA1BREST`, reading the **uncataloged**
`BCPL.BT0001`, `VOL=SER=BTA102`, `LABEL=(1,SL)`,
from the existing original image, and creating/cataloging **only**
new DASD `HERC02.BCPL.TA1B.LOAD`, `PO/U/0/6144`.
The image itself is never initialized, rewritten or replaced.
The guarded `scripts/run-ta1-track-b-restore --run` repeats
read-only checks, obtains a typed restore authorization, creates
an irreversible no-retry attempt marker before conditional mount
or JES submission, and asks separately before exactly one
`TA1BREST` submission.

**This record is NOT stateful approval.** Do not run `--run`
without distinct owner authorization. The independent IEHLIST
source-versus-restored directory comparison, observed member
entry/attributes, and the eight-step MRREGRES scalar/vector GO
with all ICINT19 STEPLIB DDs targeting the restored library
remain subsequent, distinct verification gates.

**TA.1 state:** Track A PASS (qualified); Track B unload WRITE
PASS (qualified) and restore read-only preflight PASS;
Track B restore, directory comparison, and restored executable
test PENDING. TA.1 remains IN PROGRESS.

## Subsequently authorized and completed restoration (18 November 2026)

After explicit separate authorization the owner executed the exact
one-shot restore. `TA1BREST` JOB **9136** returned IEBCOPY RC=0000,
`HERC02.BCPL.TA1B.LOAD(ICINT19)` was verified on TSO002 as
PO/U/0/6144, and the original BTA102 SHA-256 was unchanged.
The ignored evidence is in
`workarea/ta1b-operations/BTA102-track-b-restore-20261119T021135Z-10863/`.
This supersedes the preceding preflight-only status, but does not
assert directory equality or executable proof. See
[the next verification gate](ta1b-restore-evidence-and-directory-gate-20261118.md).
