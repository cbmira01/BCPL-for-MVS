# 132 — Reopen same dynamically allocated input DD, preserve handle identity

**Status: ACCEPTED — candidate-only compiled-BCPL regression PASS 132 (2026-10-17).**
The operator pulled repository main through `9486824` and ran
`tools/native/run-regression 132 --show-output` using
`BCPL_RUNTIME_PDS=1`, `BCPL_RUNTIME_LIBRARY=DEVOBJ`,
`BCPL_RUNTIME_CANDIDATE=1`, and
`BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6`. The runner reported
**PASS 132 / PASS 1 / FAIL 0 / SKIP 0 / TOTAL 1**.

The output validates a new nonzero input handle distinct from the
retired DD01 handle and still-live DD02 handle, active duplicate FIND
identity, rejection of the retired handle after reopening, and an
unchanged DD02 cursor. The reopening and closing operations succeeded
under MVS in this test, but it deliberately did not call RDCH on the
reopened DD01 and thus proves **nothing about DD DATA rewind or
post-reopen read position**. The last full candidate panel remains
00..131 (131 PASS / 0 FAIL / expected SKIP 083); 00..132 has not
yet been rerun. The BCPLIO runtime source and DEVOBJ objects were
not rebuilt or modified for this acceptance.

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
A disk-backed sequential dataset would be suitable for a
separate stronger repositioning test, if that behavior is wanted.
Repeated OPEN itself was successful in this regression; no
assumption about a repeat GET is justified.

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
