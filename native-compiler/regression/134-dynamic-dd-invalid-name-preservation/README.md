# 134 — M4.0 invalid DD names, no selection side effects

**Status: STAGED, NOT YET EXECUTED ON MVS OR ACCEPTED.**

This permanent candidate-only compiled Cambridge BCPL regression
tests ordinary failing FINDINPUT and FINDOUTPUT without altering
either live selection. The two allocated DDs are input DD01
(two FB80 records A and B) and output REPORT (FB132 SYSOUT).

The test opens both streams, selects each, reads the first
input character, then performs *both* FINDINPUT and FINDOUTPUT
for each of five deliberately failing DD names:

| Name | Expected reason for failure |
|---|---|
| `""` | zero-length counted string |
| `"ABCDEFGHI"` | nine-character name (MVS limit eight) |
| `"1BAD"` | invalid initial numeric DDNAME character |
| `"AB-C"` | invalid hyphen within name |
| `"NOFILE"` | syntactically valid, deliberately unallocated DD |

Every failure must return zero and leave both INPUT() and OUTPUT()
equal to their prior live handles. Afterwards lowercase duplicate
FIND of allocated DD01/REPORT must return the original live
identities. The existing input cursor resumes at synthetic
newline then B, proving unsuccessful FIND did not destroy
it. The REPORT output contains `NEGATIVE DD OK`; primary
SYSPRINT outputs `BCPL DD FAILURES OK`. Any assertion STOP(8)
is a failing regression.

The test does not claim real OPEN failure or GETMAIN exhaustion,
which require later M4 fault gates. The current combined JES
checker does not prove physical REPORT DD attribution.
No BCPLIO/runtime/compiler or JCL harness modifications were
made to stage this test.

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 134 --show-output
```
