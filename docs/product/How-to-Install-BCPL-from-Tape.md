# How to Install BCPL from Tape

*Cambridge BCPL Programming System for MVS 3.8J*

This guide explains how an MVS operator installs a distributed release into a fresh namespace. The worked release is **BCPL-0.1.0-rc4 / BC0004**. Its [mandatory companion guide](../../packaging/distribution/publication/RC4-README.md) and [frozen manifest](../../packaging/distribution/manifest/releases/BCPL-0.1.0-rc4.yaml) govern the exact bytes, tape positions, profiles and supported operations. For another release use that release's own companion and manifest; do not reuse RC4 positions by assumption.

## 1. Identify release, media, checksum and target

Obtain the [published RC4 prerelease](https://github.com/cbmira01/BCPL-for-MVS/releases/tag/v0.1.0-rc4). Preserve the archive, companion, manifest, internal checksums and copyright/provenance notices together.

| Item | RC4 identity |
| --- | --- |
| Archive | BCPL-0.1.0-rc4-BC0004.zip |
| Archive SHA-256 | a3d47d7a3591c3f8fa826c205729a9488423f31a3a7e0c10ed87357d3404e80e |
| Extracted image | bcpl-0.1.0-rc4-BC0004.aws |
| AWS SHA-256 | 7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1 |
| Format | AWS, standard labels (SL), volume BC0004 |
| Inventory | 21 logical datasets, 64 AWS physical files |
| Frozen program source | e910de51c19c09698be139e33084a90401511cc9 |

Check archive and extracted image digests with your site's SHA-256 utility; compare accompanying checksum records. Stop on any mismatch. The release is a prerelease, not a claim of complete Cambridge compiler reconstruction. Hercules, TK5 and MVS are not included. Historical rights remain unresolved; preserve all supplied notices and do not treat the project's MIT license as a grant covering historical material.

Target: existing MVS 3.8J with JES, IEBGENER, IEBCOPY, authorized JOB card, available DASD, AWS-compatible tape drive and access to catalog/member listings. TA.7 verified fresh namespaces on the existing system, not an independent IPL or alternate HLQ/site.

## 2. Review manifest, HLQ, storage and profile prerequisites

Use a fresh namespace `<HLQ>.BCPL.<SITE>`; insert SITE immediately after BCPL in the manifest's target templates. Select exactly one profile. The tested examples use HLQ=HERC02, TU=480, DU=SYSDA and DV=TSO002. They are not universal site defaults.

| BT0002 member | Manifest profile | Default SITE | PDSes | Member entries |
| --- | --- | --- | ---: | ---: |
| MR10 | mr10-only | R4MR | 11 | 94 |
| NATIVE | native-only | R4NT | 11 | 71 |
| COMBINED | combined | R4CB | 20 | 150 |

MR10 and COMBINED include an independently usable MR10 Kit Compiler. NATIVE and COMBINED carry native Core Runtime, Base Library, Coroutine Support Library, System Extensions and historical Cambridge Compiler source as work in progress. Neither includes CAMBCOMP or a usable native-running Cambridge Compiler.

Plan all destination DSNs, DASD units, volumes, tracks and directory blocks before submitting anything. Inspect the profile's allocation statements, check free space and catalog/VTOC as appropriate to your site; verify every target absent, including DIST.INST. Do not assume a missing catalog entry proves a physically allocated dataset absent. Keep existing installations untouched. The selected tape positions are:

| Logical tape files | Group / purpose |
| --- | --- |
| BT0001 | Sequential FB80 bootstrap text; not a restored PDS |
| BT0002 | Common installer PDS, DIST.INST |
| BT0003 | Common DIST.DOCS, older draft notes |
| BT0004–BT0012 | MR10Kit libraries (nine PDSes) |
| BT0013–BT0020 | Native BOOT and EXT libraries (eight PDSes) |
| BT0021 | CAMBRIDG.SOURCE, selected historical/reconstructed source inventory |

Consult the full frozen manifest for every member and DCB; do not infer physical AWS file indexes from logical label sequence.

## 3. Mount media and restore bootstrap/installer

Attach the verified AWS image read-only using the site's Hercules/tape procedure. Confirm the intended drive and VOLSER, not a similarly named image or an older BC0003 candidate. Do not initialize or write the tape.

The following two JOB-card-less decks are reproduced exactly from the RC4 companion. Supply the authorized JOB card and adapt the documented site fields in a working copy, preserving card columns. First read the sequential bootstrap into JES output:


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

Check IEBGENER RC0000 and actual bootstrap text for the intended release. Then restore the installer PDS. The companion example uses the MR10 namespace:


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

This is a real allocating job, not a read-only check. Verify BT0002's IEBCOPY result, DCB and exact eight-member directory: INSTALL, DATASETS, RELEASE, RESTORE, COPY, MR10, NATIVE, COMBINED. For another profile substitute its intended installer DSN before the restore; do not overwrite a prior installer.

## 4. Select and install applicable MR10, NATIVE or COMBINED profile

Read INSTALL, DATASETS, RELEASE and RESTORE in the restored DIST.INST; inspect COPY and the chosen profile. The profile members are complete JOB-card-less bodies containing an in-stream PROC, PEND and a final GO EXEC. They require no host Python, Git or dspal in the recipient environment.

Copy the selected profile to a submission deck, supply the JOB card and override HLQ, SITE, TU, DU and DV on its final GO EXEC as needed. HLQ and SITE must agree with the previously restored DIST.INST because every IEBCOPY step reads its SYSIN from that PDS's COPY member. Keep the PROC and its symbolic substitution intact; do not replace them with modern SET/JCLLIB or inline data inside PROC.

Verify all remaining targets absent immediately before submission. Submit once, then monitor the actual job. Each payload destination uses DISP=(NEW,CATLG,DELETE). MR10 and NATIVE have ten IEBCOPY steps after BT0002; COMBINED has nineteen. Require the expected ordered step results with RC0000. Do not rely only on a shell/reader return or job-submission confirmation.

## 5. Verify inventory, directory/DCB and members

Use MVS LISTDS LABEL and LISTDS MEMBERS for each target, including DIST.INST. Compare actual catalog/volume, DSORG, RECFM, LRECL, BLKSIZE and exact member identities against the selected frozen manifest and profile. Count entries, but also check each name; counts alone cannot establish the inventory.

Only MR10KIT.LOAD has DSORG=PO, RECFM=U, LRECL=0, BLKSIZE=6144. The other restored PDSes use PO/FB/80/800. BT0001 is sequential text, not a PDS. Object FB80 members contain binary data and must not undergo text translation. Do not edit or transfer them as source.

The accepted TA.3 and TA.7 checks covered 42 PDSes and 315 member entries across three distinct fresh installations. See [TA.3 results](../../packaging/distribution/install-from-tape/ta3-rc4-all-profiles-accepted-20261123.md) and [TA.7 results](../../packaging/milestones/tape-artifact-release/ta7-clean-namespace-acceptance-20261124.md). These are inventory/DCB/member checks, not byte-for-byte proof of every restored native object.

## 6. Run supported functional verification

For MR10 or COMBINED use the installed MR10KIT.LOAD(ICINT19), not a rebuilt interpreter. Copy the three MR10KIT.JCL members to local submission decks; retarget the development prefix HERC02.BCPL.MR10KIT. to the installed site prefix, preserve card columns and add the authorized JOB card.

| Job member | Cases | Required steps |
| --- | ---: | ---: |
| MRLANGDM | 11 | 38 |
| MRBCDEMO | 17 | 62 |
| MRREGRES | 12 | 63 |

Require all intended JES steps RC0000 and all interpreted CODE values zero. Check actual demonstration results, and every regression TEST identity, literal EXP and calculated RP against the independent expected records in MR10KIT.TESTS. See [operation guide](How-to-Operate-the-BCPL-Programming-System.md) and [compile/run guide](How-to-Compile-and-Run-BCPL-Programs.md).

TA.7 accepted 80/80 cases across MR10 and COMBINED. NATIVE-only installations verify inventory only; do not run MR10 or native compiler tests there. An ICINT19 source rebuild was separately accepted in TA.4; not a required installation step. The on-tape IC19BLD writes object/load members and must only be adapted to fresh separate targets if explicitly needed.

## 7. Recover from incomplete installation without overwriting existing installations

If a job fails, stop further allocation and preserve the tape, exact submission deck, catalog/DCB/member listings and full JES evidence. A timeout or a failed reviewer does not prove that a submitted job did not run. Establish actual completed steps and surviving datasets. DISP=(NEW,CATLG,DELETE) is not a transaction across the entire job.

Do not blindly resubmit the profile, delete partial PDSes or overwrite an existing installation. A fresh independently checked namespace is the preferred clean alternative if recovery is required; a partial continuation needs an exact inventory and separately reviewed authorized plan. TA.3 recovered its first MR10 installation without replay after a reviewer halt; that historical controller is retired and not a recipient tool.

Follow the [RC4 companion](../../packaging/distribution/publication/RC4-README.md) rather than stale DIST.DOCS/BT0003 or RC3 procedures. [TA.8 formal closure](../../packaging/milestones/tape-artifact-release/ta8-formal-qualified-closure-and-milestone-completion-20261124.md) preserves release qualification, private receipt limitations and historical rights notices. No new installation, media writing, release or native functional certification is implied by this guide.
