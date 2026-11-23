# TA.3 — BC0003 isolated MR10 recipient: reported MVS PASS

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **TA.3 — MVS Bootstrap and Installation** (IN PROGRESS)  
**Candidate:** `BCPL-0.1.0-rc3`; VOLSER `BC0003`  
**Original AWS SHA-256:** `6c54c4df2b75020a698110061c4f8003b09adbe21f738848dcaed3da495d81e1`

## Owner-supplied MVS result

On 22 November 2026 EST / 23 November 2026 UTC, after pulling GitHub
`main`, the owner ran the source-controlled
`packaging/distribution/install-from-tape/scripts/ta3-rc3-recipient --run`,
received and answered its single stateful `[y/N]` confirmation, and
supplied the console report:

```text
TA.3 PREFLIGHT PASS: JOB 9370; all 11 PDS targets absent; BC0003 verified, drive empty.
TA.3 ISOLATED MR10 PASS: BT0001 printed; BT0002 installer restored; 10/10 PDS restores; 90/90 members; SCALVEC TEST/EXP/RP/CODE PASS.
MVS JOBS: absence_preflight=9370, boot=9371, installer_restore=9372, installer_view=9373, profile_restore=9374, catalog=9375, directory=9376, installed_go=9377
Evidence: workarea/ta3-rc3-recipient/20261123T014830Z-33002
```

The owner console output reports:

- **9370**: all 11 fresh `HERC02.BCPL.TA3N1.*` PDS targets
  absent; original BC0003 image verified; drive empty;
- **9371–9373**: actual MVS `BT0001` IEBGENER, `BT0002`
  IEBCOPY, and four-member installer print;
- **9374**: MR10-only release payload IEBCOPY restore, 10/10;
- **9375–9376**: recipient LISTDS DCB and directory verification,
  11 PDSes and 90 expected members;
- **9377**: eight-step installed `ICINT19` scalar/vector
  compile, INTCODE generation and execution, with
  `TEST:`/`EXP:`/`RP:`/`CODE=0` reported PASS.

The per-job JES reports and sealed receipt are retained **on the
owner's machine** under the indicated repository `workarea` directory.
This repository document records the supplied successful console result;
it does **not** claim independent access to or manual review of those
local JES evidence files.

## TA.3 scope consequence

**Isolated MR10-only recipient path: PASS, qualified by owner output.**
Do not repeat these jobs or use `TA3N1` as the destination for later
profile trials.

Remaining TA.3 gates: native-only and combined profile installation
on new absent namespaces; exact MVS DCB/member verification and installed
BCPL proof where applicable; evaluation of the frozen tape-resident
`BT0002` RESTORE template's site-parametric usability. This remains
a same-MVS-system namespace-isolation trial, not independent recipient
IPL qualification. `native_compiler: absent` remains accurate.

No media reinitialization, original `BC0003` rewrite, TA.2
stateful replay, release publication, or formal TA.3 closure is
authorized by this reported result.
