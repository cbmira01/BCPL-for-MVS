# TA.3 — BC0003 three-profile MVS installation results (23 November 2026 EST)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.3 — MVS Bootstrap and Installation (**IN PROGRESS**)  
**Source of result:** Owner-supplied WSL operator console output, not independently retrieved JES reports.  
**Candidate:** `BCPL-0.1.0-rc3`, VOLSER `BC0003`, immutable SHA-256
`6c54c4df2b75020a698110061c4f8003b09adbe21f738848dcaed3da495d81e1`.

## Accepted first recipient: MR10-only

The owner previously reported `HERC02.BCPL.TA3N1.*` installation and
installed `ICINT19` SCALVEC execution successful on actual MVS JOBS
9370–9377. The preserved operator result is
[TA3N1 MVS report](ta3-rc3-n1-operator-result-20261122.md).
No TA3N1 allocation, job, or tape write was repeated.

## Remaining profiles: native-only and combined

After the corrected prior-receipt filename gate was committed to
GitHub `main`, the owner ran:
`packaging/distribution/install-from-tape/scripts/ta3-rc3-remaining-profiles --run`,
approved the single `[y/N]` prompt, and reported these exact outcomes:

```text
TA.3 PROFILE PREFLIGHT PASS: JOB 9378; 31 absent targets, BC0003 intact, drive EMPTY.
Install native-only TA3N2 and combined TA3N3 ONCE? [y/N]: y
TA.3 NATIVE-ONLY PASS: 11 PDSes, 67 members; no native compiler claimed.
TA.3 COMBINED PASS: 20 PDSes, 146 members; installed SCALVEC TEST/EXP/RP/CODE PASS.
TA.3 PROFILES PASS: native-only and combined install; BC0003 unchanged.
Evidence: workarea/ta3-rc3-remaining-profiles/20261123T050551Z-34032
```

The successful runner assertions, as reported by the owner, encompass
actual MVS `IEBGENER` BT0001 reading, `IEBCOPY` BT0002 installer
restoration and four-member reading, independent
`TA3NATV` and `TA3BOTH` IEBCOPY restoration, per-dataset
`LISTDS` DCB/volume verification and per-PDS member-directory
comparison, JES/IEF142I RC0000 checks, combined-profile installed
`ICINT19` compile/generate/execute, and `TEST:`/`EXP:`/`RP:`/
`CODE=0` semantics. The runner verifies the original BC0003 AWS
SHA-256 again upon completion.

| Profile | Isolated recipient namespace | New installed PDSes, including BT0002 installer | Expected/verified members | Installed program use |
| --- | --- | ---: | ---: | --- |
| MR10-only | `HERC02.BCPL.TA3N1` | 11 | 90 / 90 | Installed SCALVEC PASS |
| Native-only | `HERC02.BCPL.TA3N2` | 11 | 67 / 67 | Inventory proof; no native compiler claimed |
| Combined | `HERC02.BCPL.TA3N3` | 20 | 146 / 146 | Installed SCALVEC PASS |

For the second invocation the owner reported only the preflight job
number, **9378**. No later JES job numbers are inferred or invented.
Its sealed JES evidence and checksums reside **in the owner's
repository** at the supplied `workarea` location. Those files have
not been independently opened from GitHub; this record is a faithful
representation of the supplied successful console results.

## Prior preflight diagnostic is resolved

The first invocation of the remaining-profiles runner halted before any
new stateful operation because its TA3N1 prior-evidence check requested
`directory-report.txt` instead of the actual
`inventory-report.txt`. The source code was corrected, acceptance/
tamper refusal tests were added, and the successful invocation above
then proceeded past that checkpoint. The earlier failed preflight did
not consume the one-shot stateful marker and is **not** an MVS failure.

## TA.3 acceptance boundary

**Qualified technical result: all three isolated-profile restoration,
catalog/directory and applicable installed-MR10-use checks PASS as
owner-reported from actual MVS 3.8J.** These are separated, previously
absent dataset namespaces **on the existing development MVS system**,
not a newly IPL'd independent MVS recipient.

The frozen tape's original `BT0002(RESTORE)` is still a 19-step
site-substitution **template**, not a directly operable,
profile-selectable MVS job. The three operational profiles demonstrated
above used separately source-controlled, MVS-only JCL job bodies and
a host-side submission/evidence orchestrator. Thus the strict
milestone language “`BT0002` yields operable MVS-only installation
jobs” requires an explicit qualified interpretation or a new separately
approved candidate with a revised tape-resident installer. Do not
silently assert this gate has unqualified PASS.

No native Cambridge Compiler is distributed or executable in the scoped
candidate; `native_compiler: absent` remains correct. The native-only
profile was verified for installation/inventory, **not** standalone
native application link/execution (separate TA.5 proof).
No TA.7 independent clean-MVS system gate, TA.4 full MR10 suite,
redistribution-rights acceptance, or release publication is claimed.

**Disposition:** TA.3 IN PROGRESS pending owner decision on qualified
acceptance of the source-controlled external JCL profile mechanism
versus new-candidate tape-resident installer work. Preserve BC0003,
all TA.2/TA.3 receipts, all existing recipient datasets, and consumed
one-shot markers. Do not rerun previously accepted jobs.
