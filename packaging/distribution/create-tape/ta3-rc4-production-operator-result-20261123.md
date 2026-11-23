# TA.3 — BC0004 MVS tape production: operator-reported PASS (23 November 2026 EST)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.3 — MVS Bootstrap and Installation, **IN PROGRESS**  
**Candidate:** `BCPL-0.1.0-rc4` / VOLSER `BC0004`  
**Immutable new AWS image:** `mvs-state/tape/bcpl-0.1.0-rc4-BC0004.aws`  
**Owner-reported SHA-256:** `7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`

## Actual MVS 3.8J execution

After the pre-stateful source validation defect was corrected,
the owner pulled GitHub `main` and ran
`packaging/distribution/create-tape/scripts/ta3-rc4-production --run`.
The owner explicitly approved the one-shot stage/write operation:

```text
TA.3 RC4 PREFLIGHT PASS: JOB 9393; 19 accepted RC3 sources; 2 new stage targets absent; BC0004 unused; drive EMPTY.
Stage 2 new PDSes and write new BC0004 tape ONCE? [y/N]: y
TA.3 RC4 STAGING PASS: JOB 9394; new BT0001/BT0002; DCB JOB 9395; 8 installer members JOB 9396.
TA.3 RC4 TAPE PASS: MVS JOB 9397; 21 SL datasets; 64 physical files; SHA256 7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1.
Evidence: workarea/ta3-rc4-production/20261123T130731Z-36363
```

The runner required exact MVS JES/IEF142I checks, independently
queried the staged DCBs and eight-member PDS directory, and used the
established HETMAP structure auditor to validate the `BC0004`
standard-label volume (21 logical tape datasets, 64 physical files).
The original BC0003 SHA-256 was guarded before and after the write.
Only the new `HERC02.BCPL.TA3R4S.BT0001` and `BT0002` were staged;
the remaining 19 accepted RC3 PDSes were producer inputs.

The corresponding sealed files remain in the owner's ignored
`workarea/` directory. **The assistant has not independently
retrieved or re-read those local JES/hetmap receipts**; all exact MVS
job numbers and tape SHA-256 above are owner-reported, not inferred.

## Acceptance and next operation

**Technical production: PASS (operator reported).**
The one-shot RC4 stage/write marker has been consumed;
**do not repeat RC4 staging or tape writing**. Preserve both
`BC0003` and `BC0004`, their original SHA-256 values, original
source PDSes and all accepted TA.2/TA.3 receipts.

This result does not establish that a recipient has used
`BT0002(MR10)`, `BT0002(NATIVE)` or `BT0002(COMBINED)`.
The next TA.3 gate must independently restore **the new BC0004**
`BT0001`/`BT0002` on fresh MVS recipient namespaces, verify
the eight on-tape installer members, and execute installation
jobs read from the restored MVS PDS. The combined profile must
execute an installed MR10 demonstration (`ICINT19`), verifying
`TEST:`/`EXP:`/`RP:`/`CODE=0` on actual MVS.
No native Cambridge Compiler is claimed (`native_compiler: absent`).

**TA.3 remains IN PROGRESS; TA.7 clean-system and other milestone
acceptance gates are not implied by this producer result.**
