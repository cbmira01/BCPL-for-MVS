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
- [ ] Verify remaining module prologues and developer navigation
      identify authoritative accepted candidate versus baseline.
- [ ] Review and explicitly document inter-CSECT linkage/register,
      reentrancy and exceptional-exit assumptions; distinguish
      proven MVS evidence from inference.
- [ ] Ensure documentation clearly records Git authority and DEVOBJ
      staging; no unapproved production OBJ mutation.
- [ ] Re-stage and assemble comment-only updated BCPLIO/BCPLAPT/
      BCPLBYTE to DEVOBJ if accepting their updated resident sources,
      inspect RCs and linkage before final Gate F acceptance.
- [ ] Formally record Gate E acceptance or remaining bounded deferrals.

## Next gate

Gate F, per charter, is final candidate acceptance against the M1.9
contract and complete installed DEVOBJ regression panel. Existing D6
full-panel evidence is valid and should be reused where nothing has
changed; any new source/object build must be identified explicitly.

**Gate E remains OPEN; M2.0 remains OPEN.**
