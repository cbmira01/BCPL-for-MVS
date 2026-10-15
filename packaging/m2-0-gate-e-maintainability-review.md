# M2.0 Gate E — Linkage and Maintainability Review

**Status: OPEN — source and documentation audit underway (14 October 2026).**
**Predecessor:** Gate D closed, commit 2900113; accepted DEVOBJ(BCPLM6)
with 123 PASS, 0 FAIL, 1 expected SKIP in full 00-123 panel.

## Charter and acceptance boundary

The M2.0 architecture defines Gate E as a source-header, provenance,
symbol-boundary, base-register, independent object-build and navigation
review. It also requires BCPLMAIN to remain an intelligible bootstrap
and coordinator. Gate E is **not** permission to add BCPLSTACK or new
historical functionality or to promote production OBJ.

## Established architecture and evidence

- BCPLMAIN D6 is an independent CSECT, length X'0C00' in JOB 2393.
  It initializes MVS linkage, storage, G and SYSV, publishes services,
  invokes START, coordinates IOFIN, MEMDRAIN and MVS release.
- BCPLIO is an independent CSECT, X'0FF8' in JOB 2393. Its input
  and output services are resolved from BCPLMAIN's external refs.
  Input and output DCBs/cursors/saves are not locally duplicated.
- BCPLAPT G40/APLIMIT is distinct, accepted at Gate B.
- BCPLBYTE G85/G86 and BCPLMEM G87/G88/private teardown are distinct,
  accepted at Gate C.
- DEVOBJ-only D6 assembly JOB 2389 IFOX00/IEBGENER RC=0000,
  IEWL JOB 2393 RC=0000, 084-119 36 PASS, full 00-123
  123 PASS, 0 FAIL, expected source-only SKIP 083.
- Production `HERC02.BCPL.OBJ` is not promoted or modified.

## Findings and dispositions

1. **Header drift, correct without machine-instruction changes:**
   `asm/bcplio.asm` began with an obsolete D2 output-only,
   unintegrated-candidate warning despite accepted input integration;
   `asm/bcplbyte.asm` claimed not to be used by normal regressions;
   `asm/bcplapt.asm` stated object acceptance was pending. The three
   source prologues have been corrected to reflect Gates B/C/D.
2. **Traceability:** source labels and EXTRN/ENTRY cross-reference are
   supported by JOB 2393 IEWL map, independently of source-only
   claims. Explicit public versus private contracts are needed in
   headers; detailed BCPLIO native-private behavior is documented in
   `packaging/m2-0-d3-bcplio-linkage-contract.md`, whose dated
   candidate statements must not override Gate D closure.
3. **BCPLMAIN readability:** D6 has 1,543 source records,
   approximately 583 of them a historical evidence/provenance
   preamble. That narrative is valuable; moving or condensing it would
   be an independent review with risk of lost provenance. Do not
   mechanically delete historical evidence merely to shorten a file.
   Provisional WRITEST and DEBUGINT remain deliberately local.
4. **Register/base scope:** documented R10 private bases and R5/R6/R7
   BCPL ABI remain critical. Independently successful IFOX/IEWL
   builds and regressions support existing implementation but do not
   prove reentrancy or all untested register/error paths.
5. **Build navigation:** Gate D established separate `BCPLIO`,
   `BCPLM6` SOURCE/DEVOBJ workflows and explicit candidate selection.
   Review whether generic developer instructions point to the D6
   candidate unambiguously, rather than imply the production
   `asm/bcplmain.asm` or production OBJ was overwritten.

## Gate E exit checklist

- [x] Review Gate A-D module ownership and candidate IEWL evidence.
- [x] Correct the three obsolete module-level acceptance headers.
- [x] Verify remaining module prologues and developer navigation
      identify authoritative accepted candidate versus baseline.
- [x] Review and explicitly document inter-CSECT linkage/register,
      reentrancy and exceptional-exit assumptions; distinguish
      proven MVS evidence from inference.
- [x] Ensure documentation clearly records Git authority and DEVOBJ
      staging; no unapproved production OBJ mutation.
- [x] Re-stage and assemble comment-only updated BCPLIO/BCPLAPT/
      BCPLBYTE to DEVOBJ; verify RCs and integrated IEWL linkage.
- [x] Formally record Gate E acceptance with bounded post-rebuild execution deferral to Gate F.

## Next gate

Gate F, per charter, is final candidate acceptance against the M1.9
contract and complete installed DEVOBJ regression panel. Existing D6
full-panel evidence is valid and should be reused where nothing has
changed; any new source/object build must be identified explicitly.

**Superseded by Gate E closure decision at the end of this document; M2.0 remains OPEN.**

## Gate E contract and navigation audit complete — MVS refresh pending

- BCPLMAIN candidate source is asm/bcplmain-d6-candidate.asm; object member is DEVOBJ(BCPLM6). asm/bcplmain.asm and bcplmain-wip.asm are not interchangeable with it.
- BCPLMAIN owns MVS entry, G/SYSV, global/stack allocation, START invocation, STOP code and teardown. IOINIT receives the MVS PARM pointer; IOFIN precedes MEMDRAIN, MEMBIND(0) and FREEMAIN.
- BCPLIO is a static nonreentrant owner of input/output QSAM DCBs, private buffers, cursors, EODAD, PARM pseudo-stream and stream cleanup. Its BCPL-facing services use R5 frame/R6 return; native-private IOINIT/IOFIN/IOBIND/IODIAG/IOREPL/IOPMGET use their separately documented R14 native contracts. R10 is a private base and is clobbered.
- BCPLAPT owns G40 APTOVEC with exported APLIMIT data initialized by BCPLMAIN from STKLIM; its failure transfer branches to BCPLMAIN STKOVFL. BCPLBYTE owns G85/G86, preserves generated permanent registers and restores R4. BCPLMEM owns G87/G88, static allocation state and private MEMBIND/MEMDRAIN/MEMSTAT; publication passes a G6!48 slot address.
- BLIB is a compiled BCPL object whose exported G76 WRITEF takes priority over bootstrap WRITEST. DEBUGINT and WRITEST remain provisional local BCPLMAIN code.
- Gate B/C and D6 JOB 2393 link maps plus successful native execution support these ownership claims. They do not prove recursive reentrancy, every untested error path, or complete original Cambridge compatibility.
- asm/README.md now directs contributors to the accepted D6 candidate and its link-edit workflow. Git is the source authority; SOURCE and DEVOBJ are MVS build state. Production OBJ is not to be changed without explicit separate authorization.

## Operator verification needed before Gate E acceptance

Comment-only updated BCPLAPT, BCPLBYTE and BCPLIO files require synchronization and independent DEVOBJ reassembly to verify reproducibility. From the repository root after git pull --ff-only:

```sh
tools/datasets/dspal put SOURCE BCPLAPT asm/bcplapt.asm
tools/datasets/dspal put SOURCE BCPLBYTE asm/bcplbyte.asm
tools/datasets/dspal put SOURCE BCPLIO asm/bcplio.asm
tools/datasets/dspal put JCL BLDDEVA jcl/build-dev-bcplapt.jcl
tools/datasets/dspal put JCL BLDDEVB jcl/build-dev-bcplbyte.jcl
tools/datasets/dspal put JCL BLDDEVI jcl/build-dev-bcplio.jcl
tools/datasets/dspal submit JCL BLDDEVA
tools/datasets/dspal submit JCL BLDDEVB
tools/datasets/dspal submit JCL BLDDEVI
```

Require each assembler and binary-safe object installation step RC=0000, zero flagged source statements. Then submit existing JCL(D6LINK) and require IEWL RC=0000 and unchanged object boundaries. A smoke run against DEVOBJ(BCPLM6) should follow, then Gate F full-panel candidate acceptance. No production OBJ promotion. Gate E remains OPEN pending MVS evidence.

## Resident MVS rebuild and linkage acceptance — 14 October 2026

Operator synchronized updated source prologues to SOURCE(BCPLAPT), SOURCE(BCPLBYTE), SOURCE(BCPLIO) through staging JOBs **2714, 2715, 2716**; refreshed resident JCL in JOBs **2717–2719**. Independent DEVOBJ builds:

- **JOB 2722 BLDDEVA**: ASMCOMP IFOX00 RC=0000, PUTCOMP IEBGENER RC=0000; zero flagged statements/severity.
- **JOB 2725 BLDDEVB**: ASMCOMP IFOX00 RC=0000, PUTCOMP IEBGENER RC=0000; zero flagged statements/severity.
- **JOB 2728 BLDDEVI**: ASMIO IFOX00 RC=0000, PUTIO IEBGENER RC=0000; zero flagged statements/severity.
- **JOB 2731 D6LINK**: integrated IEWL LKED RC=0000 using existing D6 control.

The committed assembler changes were comments only. These jobs establish updated SOURCE and DEVOBJ object builds and successful integration, not a newly observed post-rebuild GO. No evidence of production OBJ write. To close Gate E, run DEVOBJ(BCPLM6) native regression 00 as smoke and record result; Gate F owns final full 00–123 acceptance.

## Gate E closure / transition to Gate F — 14 October 2026

**Gate E ACCEPTED AND CLOSED for the architectural and maintainability scope.** The source/interface/provenance/navigation audit is complete; all three comment-only changed modules were re-staged and rebuilt independently with IFOX00 and IEBGENER RC=0000, zero flagged statements (JOBs 2722, 2725, 2728); integrated IEWL passed RC=0000 (JOB 2731). **Bounded deferral:** no post-rebuild GO result was supplied. Rather than represent this as verified, transfer runtime smoke and final complete DEVOBJ(BCPLM6) panel to Gate F, whose charter expressly governs candidate execution acceptance. A final execution failure will reopen the implementation issue and prevent Gate F/M2.0 closure. No production OBJ promotion.
