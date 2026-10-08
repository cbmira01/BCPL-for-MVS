# Native Object Library Foundation — Stage A verified checkpoint

**Recorded:** 2026-10-08  
**Repository:** `cbmira01/BCPL-for-MVS`  
**Branch:** `experiment/blib-object-pds`  
**Status:** **STAGE A COMPLETE — independent BLIB object assembly and PDS inclusion**

## Verified Hercules / MVS 3.8J TK5 evidence

- Previous static BLIB integration march remains the accepted baseline:
  **69 PASS, 0 FAIL** on native regressions 000–068.
- Regression 067 was **rerun** before this experiment and passed, printing
  `BLIB 42`. The complete 69-test panel was **not rerun** during Stage A.
- `HERC02.BCPL.OBJ` allocation: **JOB 2394**, `BLIBALOC ALLOC IEFBR14 RC=0000`.
  The `dspal stat` check in JOB 2395 reported:
  `VOL=TSO003, DSORG=PO, RECFM=FB, LRECL=80, BLKSIZE=800`.
- Stage A experimental job: **JOB 2396**, submitted and executed by the user
  on 2026-10-08.

| JOB 2396 step | Program | Observed result |
| --- | --- | --- |
| ASMBLIB | IFOX00 | RC=0000 |
| INSTALL | IEBGENER | RC=0000 |
| ASMRUN | IFOX00 | RC=0000 |
| LKED | IEWL | RC=0000 |

BLIB standalone IFOX ESD:

```text
SYMBOL    TYPE  ID    ADDR    LENGTH
BLIB      SD    0001  000000  001BB0
BCPLMAIN  ER    0002
```

- BLIB is a separately assembled relocatable section of `X'1BB0'`
  = 7,088 bytes; BCPLMAIN is unresolved *at BLIB assembly time*, as intended.
- The IFOX assembler flagged **zero** statements, severity **0**.
- IFOX emitted **132 object records** for BLIB.
- The BLIB RLD includes `POS.ID 0001, REL.ID 0002, FLAGS 0C,
  ADDRESS 00000C`: the external BCPLMAIN address in BLIB's section wrapper.
- Installation used IEBGENER to copy the IFOX binary FB/80 object records
  from a temporary dataset directly into `HERC02.BCPL.OBJ(BLIB)`.
  `tools/dspal ls HERC02.BCPL.OBJ` listed member `BLIB`.
- IEWL received an explicit `INCLUDE OBJ(BLIB)` with `OBJ` allocated to
  `HERC02.BCPL.OBJ`; `NCAL` did not prevent this explicit include.
  Its control-card echo and map confirmed:

```text
IEW0000     INCLUDE OBJ(BLIB)
IEW0000     ENTRY BLIB
IEW0000     NAME BLIBCHK(R)

CONTROL SECTION  ORIGIN  LENGTH
BCPLMAIN         000000  004D18
BLIB             004D18  001BB0

LOCATION  REFERS TO SYMBOL  IN CONTROL SECTION
004D24    BCPLMAIN         BCPLMAIN

ENTRY ADDRESS   004D18
TOTAL LENGTH    0068C8
```

`X'4D24' = X'4D18' + X'000C'` ties IEWL's resolved reference to
BLIB's assembler-reported external relocation. This establishes not just
successful IEWL completion, but actual extraction of the stored PDS member
and resolution of its external symbol to a separately assembled BCPLMAIN.

The experiment generated a **temporary link-edited load module** and
**did not execute it**. Thus it does **not** prove that BCPLMAIN can
initialize or use BLIB as an independently linked BCPL section.

## Work implemented (isolated branch)

`native-compiler/object-library/make-obj-allocation-job.py` generates
an authenticated one-time allocation deck using the existing `dspal`
configuration. An earlier static unauthenticated allocation deck failed
as **JOB 2393** due to RAKF denying the default `PROD` identity.
The corrected authenticated job succeeded as JOB 2394.

`native-compiler/object-library/make-blib-object-job.py`:
- accepts the independently generated BLIB assembler source from the
  established regression-067 Cambridge compilation path;
- normalizes non-ASCII printer-recovery bytes in generated assembler
  comments, as the existing static combiner does, and repairs only the
  known malformed historical signed-minimum constant if present;
- assigns the generated, previously unnamed CSECT the name `BLIB`;
- retains the complete standalone entry wrapper, BCPL export trailer,
  and external `BCPLMAIN` symbol;
- performs standalone IFOX assembly, direct object-record PDS
  installation, separate IFOX assembly of unchanged BCPLMAIN-wip,
  and explicit IEWL inclusion;
- uses authenticated batch job cards from `dspal`, saving generated
  credential-bearing JCL with restricted owner permissions.

## Architectural conclusions

1. The historical Cambridge CG370 section wrapper is compatible with
   independently assembled relocatable IFOX object decks.
2. An FB/80 PDS member containing object **records**, not ordinary text,
   is compatible with IEWL explicit `INCLUDE` on TK5.
3. The BCPL global-initialization trailer is a runtime contract and is
   **not** MVS ESD linkage. IEWL has resolved `BCPLMAIN` but has not
   installed BLIB's BCPL globals into the runtime global vector.
4. The working static combiner remains authoritative for executing
   regressions 065–068. No existing regression, canonical historical
   BLIB source, `BCPLMAIN-wip`, or `config/dspal.yaml` was changed.
5. The object PDS member persists across jobs, but a **separate-job**
   reuse test and full deploy/rebuild automation remain available
   hardening tasks. Stage A acceptance was inclusion from the PDS,
   not execution of independently linked sections.

## Next boundary: Stage B

Do **not** interpret Stage A as a successful multiple-section BCPL
runtime. A Stage B test will separately assemble an application, BLIB,
and BCPLMAIN, link through IEWL, and then reconstruct/test
the global-vector section initialization contract. Begin with the
behavior of regression 067 as a parallel acceptance test.

Do not replace the 69 passing regressions or remove
`native-compiler/regression/combine-separate-bcpl.py` before that
behavior is demonstrated. Treat changes to `dspal` object-library
manifest/deployment semantics as a separate, narrowly scoped packaging
task, not a reason to redesign BCPLMAIN prematurely.
