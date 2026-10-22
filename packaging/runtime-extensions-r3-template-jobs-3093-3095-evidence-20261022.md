# Runtime Extensions — R.3 developer-template MVS evidence (JOBs 3093–3095)

**Milestone:** Runtime Extensions  
**March:** R.3 — Packaging and acceptance (**ACTIVE**)  
**Execution date:** 22 October 2026, MVS 3.8J TK5 under Hercules  
**Source baseline:** [GitHub `main` commit `424463a`](https://github.com/cbmira01/BCPL-for-MVS/commit/424463af43925214887110aa1db06ce8c2d3b3f0)  
**Disposition:** **PASS for the two developer-template variants tested**; not R.3
closure, installed-object approval, or a fresh native regression.

## Evidence and review basis

The operator supplied the terminal transcript and complete printable
JES reports for **JOB 3094 (`R3TNFIN`)** and **JOB 3095 (`R3TFIN`)**.
The combined ASCII capture is 555,960 bytes, SHA-256:

```
cfc4a781275912e9627d27a218bae25e4b46a967fbb84d70e0baeb0c7e13995d
```

This source report was reviewed directly, including the step condition
codes, IEWL MAP/XREF, application output, and finalizer witness. It is
**not** a committed repository file or a source-controlled evidence
artifact. The capture includes ordinary operator/JES headers; do not
commit it wholesale. The operator-local generated artifacts and
credentials remain outside Git under ignored `workarea/`.

The operator pulled `424463a`, and the template's eight host unit
tests all reported `ok`. `tools/bootstrap/compile-mvs` reported
**JOB 3093** and saved generated Cambridge CODE as
`workarea/runtime-extensions-r3/template/client.s370.asm`.
The supplied transcript does not contain JOB 3093's full JES report or
its per-step condition codes; compilation is evidenced here by the
produced source and the subsequent assembled/executed BCPL caller,
**not** by an independently reviewed JOB 3093 job log.

## Test preparation and execution

The operator instantiated the source templates under
`workarea/runtime-extensions-r3/template/`, replacing:

| Template token | Test-local value |
| --- | --- |
| `@PACKAGE@` | `R3TMPL` |
| `@GLOBAL@` | `299` (**test-only; no permanent allocation**) |
| `@SERVICE@` | `TMSVC` |
| `@FINADR@` in `R3TNFIN` | `F'0'` |
| `@FINADR@` in `R3TFIN` | `A(TMFIN)`, with `EXTRN TMFIN` |

Only the finalizer-equipped variant includes `finalizer.asm`, with
a temporary `WTO 'R3 TEMPLATE FINALIZER CALLED'` inserted immediately
before its successful R15 return. This **test-only instrumentation**
does not change the tracked template.

The existing R.1 `make-jobs.py` infrastructure was reused to construct
the two authenticated JCL decks with overridden application-specific
`BCPLREG` and separate BCEX/dispatcher objects. Although that helper
labels the generated decks `R.1 EMPTY BCPLREG CANDIDATE`, **both**
actual jobs contain the selected 44-byte `BCPLREG` instance, not the
28-byte empty registry. The objects/load modules were MVS temporary
`&&` datasets. The JCL reads manifest-defined
`HERC02.BCPL.BOOT.OBJ` with `DISP=SHR`, including `BCPLIO`,
`BCPLMEM`, `BCPLBYTE`, `BCPLAPT`, and `BLIB`.

Operator submission produced JOB **3094** for
`workarea/runtime-extensions-r3/template/no.jcl` and JOB **3095**
for `workarea/runtime-extensions-r3/template/fin.jcl`.
Both use the same source `BCPLMAIN` and `BCPLRGS` registrar; each
job independently assembles temporary copies. **These two jobs do
not demonstrate one reused BCPLMAIN object across multiple links**;
that separate four-link property is established in R.2.

## Observed JES condition codes and run markers

| Step or check | JOB 3094 — `R3TNFIN` | JOB 3095 — `R3TFIN` |
| --- | --- | --- |
| `ASMA` BCPL application | IFOX RC=0000 | IFOX RC=0000 |
| `ASMN` BCPLMAIN | IFOX RC=0000 | IFOX RC=0000 |
| `ASMR` registrar | IFOX RC=0000 | IFOX RC=0000 |
| `ASMG` selected BCPLREG | IFOX RC=0000 | IFOX RC=0000 |
| `ASMD` BCEX descriptor | IFOX RC=0000 | IFOX RC=0000 |
| `ASMS` dispatcher | IFOX RC=0000 | IFOX RC=0000 |
| `ASMF` finalizer | Not selected | IFOX RC=0000 |
| `LKED` IEWL | RC=0000 | RC=0000 |
| `GO` | RC=0000 | RC=0000 |
| `R3 TEMPLATE CLIENT PASS` | Present | Present |
| `R3 TEMPLATE FINALIZER CALLED` | Absent | Present once as live WTO |

Both jobs reached `$HASP395` normal completion. The compiled BCPL
client checks the six-word QUERY return and version, a short-buffer
`-1` result without writes to its sentinels, the three GETVALUES
words `10/20/30`, an unknown-opcode `-2` result, and untouched
sentinels. Its displayed PASS marker and GO RC=0000 support the
combined successful client verdict, not separate independently logged
assertion-level outcomes.

## Independently inspected IEWL MAP/XREF

Both link-edits used `PARM='NCAL,LIST,XREF,MAP'`, entry `R0APP`
and distinct temporary load module names. The MAP excerpts give
hexadecimal origins/lengths:

| CSECT | JOB 3094 | JOB 3095 |
| --- | --- | --- |
| `R0APP` | `0000 / 02C0` | `0000 / 02C0` |
| `BCPLMAIN` | `02C0 / 1048` | `02C0 / 1048` |
| `RGINIT` | `1308 / 0A20` | `1308 / 0A20` |
| `RGFINI` | `1D28 / 0100` | `1D28 / 0100` |
| `BCPLREG` | `1E28 / 002C` (44 bytes) | `1E28 / 002C` |
| `TMDSC` | `1E58 / 0038` (56 bytes) | `1E58 / 0038` |
| `TMDISP` | `1E90 / 00B8` | `1E90 / 00B8` |
| `TMFIN` | **Absent** | `1F48 / 0094` |

The cross-reference entries explicitly associate `BCRGBEG` and
`BCRGEND` with `BCPLREG`; `TMBEG` and `TMEND` with `TMDSC`;
and the dispatcher relocation with `TMDISP`. In JOB 3095,
the relocation at `1E7C` resolves `TMFIN`. There is no `TMFIN`
entry in JOB 3094's IEWL map. These observations establish that
optional-finalizer selection is determined by the source/link table
rather than merely by a public BCPL `GLOBAL` declaration.

## Limits and outstanding R.3 obligations

- This is an actual MVS verification of the template's assembler
  descriptor, registry, dispatcher, **compiled BCPL caller**, and
  optional successful finalizer path. It is **not** a compiled BCPL
  *extension implementation/export*; the extension dispatcher is
  assembler.
- The optional finalizer's **FINISH success** execution is witnessed
  once; this run does not separately test STOP reasons/codes,
  nonzero return handling, reverse ordering, or two finalizers.
  R.1 holds earlier accepted lifecycle coverage for those cases.
- These two jobs do not rerun the complete R.2 0/A/B/A+B selection
  matrix or its 21 negative/dependency scenarios.
- The instantiation and JCL-preparation snippets were executed
  interactively, with results under ignored `workarea/`. A single
  source-controlled R.3 operator runner and clean-from-Git rebuild
  evidence remain separate future work.
- No new native 00..145 regression panel was run for this evidence;
  R.3 still requires **145 PASS / 0 FAIL / 1 expected SKIP 083**.
- No installed library was written or promoted: `BOOT_OBJ` was a
  read-only JCL input, `BOOT_DEVOBJ` was not an output target,
  and object and load outputs were temporary. No public G!299
  allocation is implied.
- R.3 remains **ACTIVE**. No object-PDS installation decision or
  owner-approved milestone closure follows from this record.

## Related project sources

- [R.3 kickoff and requirements](runtime-extensions-r3-kickoff-20261022.md)
- [R.3 linkage/declaration guide](runtime-extensions-r3-linkage-guide.md)
- [Reusable developer template](../bootstrap-toolchain/extensions/template/README.md)
- [R.1 accepted lifecycle evidence](runtime-extensions-r1-closure-20261022.md)
- [R.2 interoperability closure](runtime-extensions-r2-closure-20261022.md)
