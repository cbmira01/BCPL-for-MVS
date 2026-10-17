# 132 — Reopen same dynamically allocated input DD, preserve handle identity

**Status: STAGED AS AN MVS EXPLORATORY GATE; NOT YET EXECUTED.**

Compiled Cambridge BCPL tests the accepted M0 stable-handle contract
for **dynamic input**, complementing output regression 131. JCL gives
DD01 (two FB80 records A, B) and DD02 (Q, R), each as separate
instream DD DATA. It opens both, reads A from DD01, ENDREADs the
first lifetime, confirms old-handle selection rejection, then reads
Q from the still-active DD02.

It attempts `FINDINPUT("dd01")` on the same DD01 allocation.
Successful reopen is required to return a **new nonzero word handle**
different from either prior handle, without reviving the retired
one. A duplicate FINDINPUT("DD01") must return the new identity;
selecting the old handle must not disturb the current selected input.
DD02's cursor must remain intact (newline, then R). Both reopened
and second streams are closed, and their retired identities rejected.

**Crucial restriction:** this test deliberately does not call RDCH
on reopened DD01. It tests QSAM CLOSE/OPEN and BCPL identity/lifecycle,
not whether instream DD DATA can rewind or where its file position is.
A disk-backed sequential dataset would be needed to test a stronger
repositioning guarantee. If OPEN itself cannot be repeated against
DD DATA, first capture the MVS job's IEC/IEF messages and investigate;
do not silently weaken the requirement or change runtime source.

Normal GO RC0000 plus exact primary `BCPL INPUT REOPEN OK` is PASS;
assertion failures call STOP(8). A QSAM abend, compiler/assembler/link
failure, or unexpected GO result is a genuine failed exploratory gate
requiring diagnosis. This test does not cover storage accounting
or lossless per-DD attribution.

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 132 --show-output
```
