# TA.0 — MR10_LOAD(ICINT19) directory acceptance and executable-use pilot

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone / march:** Tape artifact release / TA.0 — Release Architecture, Inventory, and Manifest  
**Status:** JOB 9060 formatted directory verified by owner, 17 November 2026; one-case ICINT19 execution pilot implemented and mocked; **execution not yet demonstrated by this pilot**. TA.0 remains IN PROGRESS.

## Live MVS directory observation

The owner ran the already-committed `verify-iehlist-load-directory.py` against
its original, SHA-256-pinned JOB 9060 evidence directory. The resulting
saved-report interpretation printed:

    TA.0 LOAD DIRECTORY JOB 9060: ICINT19 observed, entry=000000 attr=02E2
    Directory evidence only; no load bytes or executable-use verified.

This advances the single selected `MR10_LOAD(ICINT19)` member to
**formatted IEHLIST PDS directory observed**. The development library is
`HERC02.BCPL.MR10KIT.LOAD`, `PO/U/0/6144`; the operation confirmed the
non-alias member and directory attributes, not execution or byte identity.
The actual private JOB 9060 report was validated by the operator's tool;
its raw bytes have not been examined in the assistant's workspace.

## Bounded executable-use check (next live MVS gate)

`tools/distribution/verify-icint19-executable.py` first revalidates the
original pinned JOB 9060 `IEHLIST` attachments, reloads and parses the
original directory and byte-compares the facts with the previously saved
`directory-review.json`. It compares the active `MR10_LOAD` DCB and DSN to the
reviewed development library; it refuses a changed directory entry or source
mapping. It also verifies the *Git blob identity* of the approved source JCL
`mr10-kit-compiler/jcl/run-regression-tests.jcl` before extracting **exactly
8 existing steps** from the standard MR10 regression job:

| Steps | Original installed-MR10 behavior |
| --- | --- |
| SSYNI, STRNI, SCGI, SBLIBI, SICLIB | Stage existing MR10 INTCODE source members with read-only PDS input and `&&` temporary sequential outputs |
| C01A | Execute `ICINT19` via reviewed `STEPLIB` to compile `MR10_TESTS(SCALVEC)` to temporary OCODE |
| G01A | Execute `ICINT19` via reviewed `STEPLIB` to generate temporary INTCODE |
| R01 | Execute `ICINT19` via reviewed `STEPLIB` to run scalar/vector regression |

The tool prepends the site-authorized authenticated JOB card **in memory**
and submits one cursor-scoped JES job named `TA0ICEX`. It never stages or
changes a persistent MVS dataset, creates no permanent data set, performs no
assembly/link edit, and performs no tape operation. It does allocate the
same temporary `&&` work data sets as the existing `MRREGRES` JCL. It does
not invent a new test, recompile ICINT19, or run the whole 12-case panel.

A positive result must include JES START/END identity, exactly the eight
expected programs/steps at RC=0000, matching successful `IEF142I`,
interpreted `CODE=0` records, and **exact** `RP:` records matching the retained
scalar-vector golden fixture:

    RP: SCALAR 17 42
    RP: VECTOR 5 10 15 20

This confirms **the installed development load module was executable in a
known existing MR10 workload**, not that its raw `RECFM=U` records match the
reconstructed source/object, or that an unloaded/restored copy executes.
A `CODE=` mismatch or any semantic mismatch fails even if JES RC=0000.
The `EXP:`/`RP:` human-review requirement for all 12 standard tests belongs
to TA.4 and remains outstanding. No TA.4 acceptance is claimed.

The tool writes private cursor, redacted body, JES summary, report, original
printer window and SHA-256 receipt under one **new** external directory.
Possible JOB-card credentials remain confined to private MVS output; the
console prints a brief status only. It never retries an ambiguous failure.
All existing JOB 9060 directory evidence remains unchanged and outside Git.

## Offline verification and gating

19 new isolated, non-submitting tests validate the exact eight-step extraction,
source blob/golden pinning, input/STEPLIB bindings, simulated successful
execution, private file hashes and permissions, failed preflight, JES identity,
all eight RC/IEF142I messages, interpreted `CODE=`, semantic output, duplicate
records, ABEND rejection and no-retry preservation. The existing 24
IEHLIST inspector tests and these 19 tests were run together: **43/43 PASS**.
Python compilation succeeded. These are host-side mock tests, not real
System/370 execution. New binary source ancestry and redistribution review
are still required.

## Out of scope

This work performs no `IEBCOPY` unload/restore or scratch AWS tape write;
TA.1 requires separately accepted new scratch media and a readback/GO test
from the restored `PO/U` member. Likewise eight historical build-job receipts,
valid source-to-MVS revision binding, rights checks, clean recipient install,
version/VOLSER registry and release acceptance remain open. **Do not close
TA.0, authorize TA.1 writes or publish a release from this pilot alone.**
