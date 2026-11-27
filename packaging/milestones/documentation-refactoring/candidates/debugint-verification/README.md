# DR.5 — DEBUGINT negative-operand correction

**Status:** Owner-approved correction candidate; native verification pending.
The [owner decision](../../dr5-core-runtime-authority-transfer-acceptance-20261127.md)
authorizes focused native reproduction and correction, not a new numbered
regression or expansion of the provisional G!150 allocation.

Canonical BCPLMAIN previously called DBGAPND to write the minus sign before
CVD, losing R7 to the append helper. The candidate saves R7 in R8 and restores
it after DBGAPND; that helper does not use R8 and DBGCVT subsequently
overwrites R8. The two LR cards are the only executable changes. Positive
behavior, IODIAG primary routing/truncation policy, G!150, and all other
source and oracles remain unchanged. No historical FORMTREE conflict resolution.

The [source](source.bcpl) emits six ordered values via DEBUGINT and explicit
WRCH(10), with prefixes via historical BLIB WRITES. The [exact oracle](expected.txt)
is independent decimal text covering zero, positive 42, signed maximum,
negative 1 and 42, and signed minimum. The compiler-generated application is
reused unchanged for all three execution paths. The baseline must have all
three nonnegative controls correct and a signed numeric mismatch in the
negative group, with successful compiler/IFOX/IEWL/GO receipts. Its semantic
failure remains FAIL, not a regression PASS. If the defect is not reproduced
or the baseline shape is unexpected, stop without installation.

The [driver](../../../../../tools/checks/run-dr5-debugint-verification.py)
uses the established native deck generator to assemble canonical BCPLMAIN
privately and remove its installed INCLUDE; the remaining runtime and BLIB
objects are read-only. Require exact ordered records before any writes.
In explicit rebuild mode, after another JES idle check and source/revision
guard, stage only BOOT_ASM(BCPLMAIN), compare text readback, and install
only BOOT_OBJ(BCPLMAIN) with the adapted previously verified IFOX,
IEBGENER, independent readback and IEBCOMPR sequence. The identical installed
application must then match all six records. The private naming parameter
906 is not a suite identity. No release or other PDS member change, no
automatic retry or rollback. Preserve workarea/dr5-debugint/ and the
writes-started marker; do not replay a partially completed operation.

Precommit host checks: the driver passed Python compilation and synthetic
positive/negative tests for the baseline, private deck and scoped installation
gates. The exact tested driver Git blob is
a2110eedeabdd9606ebd3bdb96f904bc9bde8f0d. The assembler change is two
additional LR cards, with ASCII/column-71 checks. Local Git DNS remains
unavailable; full helper integration and IFOX/IEWL/GO must be verified on MVS.
No target result or installed binary identity is claimed. An aggregate
post-correction regression and reconstruction remain separate gates.
