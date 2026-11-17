# TA.0 — FB80 object-member readback experiment and evidence gate

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Tape artifact release
**March:** TA.0 — Release Architecture, Inventory, and Manifest
**State:** IEBPTPCH-first method approved by owner. Static JCL renderer validated offline; no live MVS readback or binary provenance yet.

## Scope and authority

The one authoritative design selection is packaging/distribution/manifest/ta0-inventory.yaml. Only the 14 selected FB80 object members in MR10_OBJ (1), BOOT_OBJ (10) and EXT_OBJ (3) are eligible for this pilot mechanism. MR10_LOAD(ICINT19) is a PO/U load module and is **not** an FB80 object member.

The read-only renderer tools/distribution/prepare-iebptpch-readback.py checks the selected member, the source mapping from config/dspal.yaml and the expected PO/FB/80/800 record characteristics. It emits an IEBPTPCH JOB **body** without a JOB card or credentials. It neither submits JES nor modifies DASD, tape or object members.

The supported period reference is IBM *OS/VS2 MVS Utilities*, Release 3.8, GC26-3902-1 (second edition, September 1983), chapter 11, especially pages 11-1 through 11-5:
https://bitsavers.org/pdf/ibm/370/OS_VS2/Release_3.8_1978/GC26-3902-1_OS_VS2_MVS_Utilities_Rel_3.8_Sep83.pdf

IEBPTPCH supports PRINT TYPORG=PO,TOTCONV=XE,MAXNAME=1 followed by MEMBER NAME=member. The standard print format groups characters and can split a converted 80-byte record over multiple output lines. Input-record delimiters, block delimiters, JES spool carriage control and printer pagination must be examined on the **actual MVS 3.8J system**. Never infer input records from output text line breaks alone.

## Proposed MVS-only pilot: EXT_OBJ(BCPLDEMO)

Use the renderer to produce a private JCL job body with dataset key EXT_OBJ and member BCPLDEMO. Prepend a site-authorized JOB card. The generated step is:

    //TA0HEX   EXEC PGM=IEBPTPCH
    //SYSPRINT DD SYSOUT=*
    //SYSUT1   DD DSN=HERC02.BCPL.EXT.OBJ,DISP=SHR
    //SYSUT2   DD SYSOUT=*
    //SYSIN    DD *
             PRINT TYPORG=PO,TOTCONV=XE,MAXNAME=1
             MEMBER NAME=BCPLDEMO
    /*

HERC02 identifies the current development source only. There is no recipient-site dependency and no output dataset except JES SYSOUT. The pilot must not be run on MR10_LOAD or on tape. A normal authorized JES submission is a separate operator action; no silent retry is permitted.

## Required actual evidence

1. Before submission: save source dataset member listing and raw TSO LISTDS LABEL report showing the actual source DCB. Record the Git revision as an operator **claim**, not proven ancestry.
2. Capture the exact submitted deck securely, printer stream, launcher and payload JES job identities, job-summary and complete dump-report-for-job results. Protect credential-bearing source material. Preserve raw printer bytes, length and SHA-256 before any report parsing; a human must associate the spool window with this specific submitted job.
3. Demand IEBPTPCH step RC=0000, correct selected member and both SYSUT2 and SYSPRINT evidence. Even a clean RC does not prove exact bytes.
4. Inspect one complete record (80 bytes = 160 hexadecimal characters) and subsequent records for wrapping, record/block separators, page breaks, ASA controls, leading zeros, X'00', X'FF', and trailing spaces. Do not drop nonprintable data or trim padding.
5. Only after a real pilot has established the grammar should a fail-closed host decoder be designed and implemented. It must prove per-record 80-byte length, record count, exact byte stream, integrity hash and independent comparison; test corrupted/truncated/duplicated/reordered output.
6. Extend successful readback to the other 13 FB80 members. Keep byte fingerprints distinct from source-to-binary ancestry and redistribution permission.

The existing tools/distribution/audit-mvs-build-evidence.py consumes an unchanged 20-attachment retained evidence index. The new pilot output is **separate**, not automatically accepted by that inspector. No second authoritative release manifest is created.

## Separate load-module track

MR10_LOAD(ICINT19) uses PO/U/0/6144 and requires a separate load-library structure/content and actual execution path. AMBLIST can provide structural information, but neither AMBLIST nor a successful GO alone proves exact binary content. The accepted single PDS IEBCOPY/IEBCOMPR FB80 tape experiment is not a RECFM=U acceptance and not TA.1 authorization. The candidate load-library approach requires a separately reviewed exact-content technique and later separately authorized TA.1 restoration/executable-use experiment.

## Build lineage and rights

The offline build-chain map identifies 15 objects/load members but not their current resident byte identities. BOOT_OBJ(BLIB) still requires historical/generated source lineage through development-only BLIBBLD and interpreter-hosted compilation. BOOT_OBJ(COROUTIN) requires verified generated BOOT_ASM(COROUTIN) inputs and exact source-to-assembler-to-object correspondence. MR10_OBJ(ICINT19) and MR10_LOAD(ICINT19) require separate IFOX/IEWL evidence. Git path matches, JES success and old CO.5 qualified results do not confer new release-candidate binary identity or redistribution approval.

## Local offline checkpoint

The proposed renderer and its 20 synthetic unit tests were executed in the assistant's isolated workspace on 17 November 2026: **20/20 PASS**. Python syntax check also passed. These are not actual MVS evidence; the wider 73-case TA.0 suite has not been rerun in this isolated workspace. GitHub main remains source authority. MVS/JES/IFOX/IEWL remain execution authority.

**TA.0 remains IN PROGRESS.** No TA.1 tape write, recipient installation, new VOLSER, release candidate or publication is authorized by this note. Only BT0001 and BT0002 tape roles are fixed; later positions remain proposals.
