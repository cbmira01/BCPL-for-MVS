# Regression 138 — M4.2 synthetic DQOPEN denial before SVC 19

**Status: STAGED ONLY; not yet assembled, linked, or run under MVS.**

Candidate-only compiled BCPL verification of the **DQOPEN failure
cleanup branch**, using the same isolated, inline-assembled, temporary
BCPLIO object mechanism that passed M4.1 regressions 135–137.
The canonical source and all installed OBJ/DEVOBJ members are untouched.

`tools/checks/prepare-bcplio-m42-open.py` takes the canonical
`native-compiler/asm/bcplio.asm`, locates the unique `SVC 19`
in `DQOPEN`, and adds a private three-state counter:

- First DQOPEN (DD01): perform real MVS SVC 19.
- Second DQOPEN (DD02): return R15=8 through `DQBAD`
  **without issuing SVC 19 for this DD**.
- Third DQOPEN (retry DD02): perform real MVS SVC 19.

The BCPL program must observe zero for the failed DD02 FIND,
retain the selected DD01 handle and read cursor, successfully
reopen DD02 on retry, read both streams and ENDREAD both.
The primary expected record is `BCPL OPEN BRANCH OK`.

**Critical limit:** This is **not** a real unsuccessful MVS
QSAM OPEN test. No failing SVC 19 is issued on the second
call; it proves only BCPLIO's recovery/cleanup when DQOPEN
returns nonzero. The canonical source routes `DIFCLEAN`
to `DREL` without CLOSE in that case because the DCB
was never opened. Actual MVS failure behavior may include
IEC messages, recoverable unopened DCBs or an S013 abend.
A separate M4.2 MVS diagnostic probe is required before
promising graceful recovery from incompatible allocated DDs.

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
python3 tools/checks/check-bcplio-m42-open.py
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 138 --show-output
```

Expected only when run: source-only transformer check PASS,
then **PASS 138**, GO expected `BCPL OPEN BRANCH OK`.
Preserve exact ASMFIO/LKED/GO job diagnostics if failing.
The full native regression panel remains owner-deferred.
