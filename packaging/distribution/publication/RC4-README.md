# Cambridge BCPL Programming System for MVS 3.8J

## Release candidate BCPL-0.1.0-rc4 — BC0004

This companion guide is authoritative for RC4 and supersedes the older
draft notes in the tape's DIST.DOCS PDS (BT0003). The tape itself is unchanged.
Keep this guide and all accompanying copyright and provenance files with
the tape. The executable installation profiles in BT0002 remain applicable.

**Included:** the independently usable MR10 Kit Compiler, INTCODE
interpreter ICINT19, library, sources, build JCL, demonstrations and
regressions. Native Core Runtime, Base Library (historical BLIB),
Coroutine Support Library, System Extensions and historical Cambridge
Compiler sources are supplied as work in progress.

**Not included:** a native-running Cambridge Compiler or CAMBCOMP.
Native components are installation/inventory accepted, not functionally
certified by this release. Native compilation/self-compilation is not
a supported RC4 workflow.

## Media and acceptance

- AWS: `bcpl-0.1.0-rc4-BC0004.aws`
- SHA-256: `7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`
- Standard labels; VOLSER BC0004; 21 logical datasets; 64 AWS physical files.
- Frozen program-source revision: `e910de51c19c09698be139e33084a90401511cc9`.
- RC4 uses the accepted RC3 program payload (BT0003–BT0021) and
  separately generated RC4 bootstrap and installer (BT0001–BT0002).
- Exact selection and DCBs: accompanying `BCPL-0.1.0-rc4.yaml`.

Verify the AWS SHA-256 after extracting it. The accepted tests installed
all three profiles (42 restored PDSes / 315 member entries across the
three installations) in fresh namespaces on the existing MVS 3.8J
system. MR10 and COMBINED each passed 11 language demonstrations,
17 BCPL demonstrations and 12 semantic regressions (80/80 total).
The installed interpreter was used; an isolated source rebuild was
also accepted in TA.4. Independent IPL and alternate site/HLQ testing
were not performed. Native object byte identity and native functional
acceptance are not claimed.

## Install using MVS

Use an existing MVS 3.8J system with JES, IEBGENER and IEBCOPY, available
DASD, an authorized JOB card and an AWS-compatible virtual tape drive.
Attach the extracted tape read-only. Select one installation profile
and a fresh namespace `<HLQ>.BCPL.<SITE>`. Do not overwrite existing
PDSes, scratch a previous installation or blindly restart a failed job.

| BT0002 member | Default SITE | PDSes | Members |
| --- | --- | ---: | ---: |
| MR10 | R4MR | 11 | 94 |
| NATIVE | R4NT | 11 | 71 |
| COMBINED | R4CB | 20 | 150 |

The supplied defaults are HLQ HERC02, tape unit 480, DASD unit SYSDA
and volume TSO002. These are examples from the tested system. Choose
an authorized local HLQ, site, units and volume. Verify every destination
is absent before restoring.

Read the bootstrap with an authorized JOB card followed by this body
(adapt unit 480 to your drive):

```jcl
//BOOTREAD EXEC PGM=IEBGENER,REGION=256K
//SYSPRINT DD SYSOUT=*
//SYSIN DD DUMMY
//SYSUT1 DD DSN=BCPL.BT0001,UNIT=480,
//            VOL=(PRIVATE,RETAIN,SER=BC0004),
//            LABEL=(1,SL),DISP=OLD
//SYSUT2 DD SYSOUT=*
//
```

Restore BT0002 to the selected fresh installer PDS. Example for
MR10 at HERC02.BCPL.R4MR; change the destination and DASD/tape values
for your chosen profile and site. Add your authorized JOB card.

```jcl
//BT2REST EXEC PGM=IEBCOPY,REGION=512K
//SYSPRINT DD SYSOUT=*
//INTAPE DD DSN=BCPL.BT0002,UNIT=480,
//            VOL=(PRIVATE,RETAIN,SER=BC0004),
//            LABEL=(2,SL),DISP=OLD
//OUTPDS DD DSN=HERC02.BCPL.R4MR.DIST.INST,
//            DISP=(NEW,CATLG,DELETE),UNIT=SYSDA,
//            VOL=SER=TSO002,SPACE=(TRK,(20,5,10)),
//            DCB=(DSORG=PO,RECFM=FB,LRECL=80,BLKSIZE=800)
//SYSUT3 DD UNIT=SYSDA,SPACE=(TRK,(10,5))
//SYSUT4 DD UNIT=SYSDA,SPACE=(TRK,(10,5))
//SYSIN DD *
 COPY OUTDD=OUTPDS,INDD=INTAPE
/*
//
```

Inspect the restored INSTALL, DATASETS, RELEASE, RESTORE and COPY
members. Copy the selected profile JCL to a submission deck, add your
JOB card and, if required, override HLQ, SITE, TU, DU and DV on its
final GO EXEC. The SITE and HLQ must match the restored installer PDS.
Do not change tape positions or use an older BC0003 restore procedure.

Require all IEBCOPY steps RC0000; compare LISTDS LABEL and LISTDS MEMBERS
against the manifest for the chosen profile, including DIST.INST itself.
The manifest's target templates omit the additional SITE qualifier;
insert it immediately after BCPL. Only the MR10 load PDS uses RECFM=U,
BLKSIZE=6144; other PDSes use FB80/800.

## Use and verify MR10

Within the MR10 or COMBINED namespace, the MR10KIT.SOURCE library
contains the INTCODE phases SYNI, TRNI, CGI, BLIBI and support ICLIB.
BCPL source is translated through these phases into INTCODE and
executed by MR10KIT.LOAD(ICINT19), rather than compiled into native MVS
machine code.

The MR10KIT.JCL members MRLANGDM, MRBCDEMO and MRREGRES are the
working compile/execute examples. Copy each to a submission deck,
replace the development prefix HERC02.BCPL.MR10KIT. with the installed
site prefix (for example HERC02.BCPL.R4MR.MR10KIT.), preserve JCL card
columns and add an authorized JOB card. Leave the installed originals
unchanged. Check the 11, 17 and 12 cases respectively; all JES steps
must return zero, all interpreted CODE values must be zero, and each
MRREGRES TEST identity, literal EXP and computed RP must agree with
the independent expected records in MR10KIT.TESTS. The installed
ICINT19 is ready to use. IC19BLD is the source rebuild JCL; adapt its
permanent output datasets to fresh separate object/load targets, never
overwrite the supplied module. Native-only recipients should verify
the installation inventory and should not run MR10 or native compiler tests.

## Copyright and preservation

Original project work: Copyright (c) 2026 Calvin Miracle, MIT licensed
unless marked otherwise. See the accompanying complete LICENSE.md.
Historical material is not relicensed by that license. Martin Richards
and other original authors retain their respective authorship and
copyright status; Ken Yap archived the transport tape and Robert
Nordier corrected character mappings and organized the archive.
The accompanying original archival notes, INDEX and
THIRD-PARTY-NOTICES.md preserve these acknowledgments.

The repository and this tape follow the same preservation-first policy.
The historical MR10 compiler files, historical BLIB and headers,
Cambridge source collection and historical derivatives retain their
original provenance. No blanket license covering the entire historical
tape has been established. Historical redistribution rights remain
unresolved; the project claims no new rights over this material.
This notice is not a grant of historical rights.

Hercules, TK5 and MVS themselves are not supplied by this package.

Repository and acceptance records:
https://github.com/cbmira01/BCPL-for-MVS
