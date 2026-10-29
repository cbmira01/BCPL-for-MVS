# Q2MIX — BCPLQSAM + installed BCPLDEMO native interoperability

**Milestone QSAM; Q.2 — Fixed logical records remains OPEN.**

Q2MIX is an intentionally source-controlled, temporary-only native MVS
campaign derived from the already executed Q2STOP template. It confirms
that two independent required BCEX v1 packages register at G!200
(QSAMSVC) and G!203 (DEMOSVC) in one native BCPL load module.

## Content and native ownership

- test-q2-mix.bcpl: Cambridge source compiled by tools/bootstrap/compile-mvs.
  It alternates the two dispatchers before/after OPEN, INFO and PUT.
  DEMOSVC's GETVALUES returns 10,20,30 while the FB80 handle is open.
- q2-mix-catalog.asm / q2-mix-selection.asm: private BCXCAT mapping
  BCPLQSAM to temporary QSMOBJ and BCPLDEMO to installed read-only
  EXT_OBJ(BCPLDEMO). Both are required by BCXREQ. Registry is 60 bytes.
- q2-mix-verify.asm: an independently linked assembler reader which
  compares one physical FB80 record byte-for-byte, detects extra records
  and requires EODAD. Returns VGO RC=0000 only after success.
- prepare-q2-mix.py: reuses the accepted Q2STOP IFOX/IEWL/BGO/VGO job.
  It does not submit JES or modify permanent PDSes. JCL is kept
  exclusively under workarea/bcplqsam-q2/mix-demo/q2mix.jcl.
- check-q2-mix-evidence.py: validates native steps, two exact markers,
  and IEWL MAP cross references for both BCEX descriptors and
  one BCPLREG of length 60. This checker itself never submits.

BOOT_OBJ and EXT_OBJ are manifest-resolved read-only input PDSes.
QPOST is an FB80/800 temporary DASD dataset passed from BGO to VGO.
No BCPLQSAM or BCPLDEMO installation/promotion is performed.

## Commands (repository root; after an approved GitHub pull)

Run local checks:

    python3 -m unittest discover -s bootstrap-toolchain/extensions/bcplqsam -p 'test_*q2_mix*.py' -v
    python3 bootstrap-toolchain/extensions/bcplqsam/prepare-q2-mix.py --check

Compile the Q2MIX caller on MVS using the established driver, job
Q2MCOMP; save assembler to:

    workarea/bcplqsam-q2/mix-demo/generated.asm

Prepare JCL using:

    python3 bootstrap-toolchain/extensions/bcplqsam/prepare-q2-mix.py --generated workarea/bcplqsam-q2/mix-demo/generated.asm

Submit the generated Q2MIX job once with tools/mvs/submit-jcl.
Retrieve tools/mvs/job-summary and dump-report-for-job; evaluate:

    python3 bootstrap-toolchain/extensions/bcplqsam/check-q2-mix-evidence.py --summary workarea/bcplqsam-q2/mix-demo/summary.txt --report workarea/bcplqsam-q2/mix-demo/report.txt

Expected ten steps: ASMA ASMV ASMN ASMR ASMQ ASMG LKED LKVR
BGO VGO. All are RC=0000 except BGO RC=0008 for deliberate
STOP(8). Two exact output records:

    Q2 MIX BCPLQSAM BCPLDEMO WRITTEN PASS
    Q2 MIX BCPLQSAM BCPLDEMO FB80 EXACT PASS

Success proves the tested link/registration/interleaving and
independent output readback, not all possible mixed-extension cases,
not physical DD attribution from a combined printer report and not
independent 16-handle close accounting. Q.2 remains OPEN until
explicit acceptance.
