# Native regression 124 — dynamic DD selected output

This is a **candidate-only** native-compiled BCPL regression. It invokes
historical BCPL global slots (FINDOUTPUT G41, SELECTOUTPUT G12, OUTPUT G17,
WRCH G14, ENDWRITE G47) and historical BLIB WRITES G60. The test exercises
REPORT and REPORT2, including interleaved writes, newline recordization,
partially filled last record, ENDWRITE, rejected stale selection, missing-DD
failure, and primary SYSPRINT reselection.

The existing runner compiles this source with the resident Cambridge compiler,
assembles its output under IFOX, links only the modular development runtime
candidate BCPLM6 and BCPLIO from DEVOBJ (other production services remain
in OBJ), and executes under MVS. The GO JCL receives explicitly declared
FB132 REPORT and REPORT2 DDs from fixture files.

Run only after **verifying or rebuilding DEVOBJ(BCPLM6)**, separate from the
already verified DEVOBJ(BCPLIO). No production OBJ installation:

```sh
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 124 --show-output
```

Expected normal exit, compiler/IFOX/IEWL/GO RC0 and these actual GO records:

- SYSPRINT: `BCPL DYNAMIC OK`
- REPORT: `BCPL REPORT A`, `BCPL REPORT B`
- REPORT2: `BCPL REPORT2 PART`

Combined JES record matching identifies logical records *after* link-edit but
**does not prove physical DD ownership**. Dedicated JES spool DD extraction
remains a later milestone gate. Test 124 is skipped by the ordinary
production-default regression panel, preserving the 00..123 baseline.
