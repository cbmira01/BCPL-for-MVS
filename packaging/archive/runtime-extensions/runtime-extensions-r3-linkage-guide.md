# Runtime Extensions — R.3 application linkage guide (steps 1–3)

**March:** R.3 — Packaging and acceptance (ACTIVE). This guide covers
only the owner-approved developer template, declaration convention and
link-edit examples. It does **not** accept deployment or close R.3.

## Three independent responsibilities

| Concern | Owner of the decision | Effect |
| --- | --- | --- |
| BCPL `GLOBAL` | Application source/header | Compiled `G!N` reference; no code |
| IEWL selection | Application link-edit | Includes objects; fixes load module |
| `BCPLREG` | Application-selected BCRG table | Requires packages; registers exports before START |

The application selects extension code **at link time**, not in RUN
JCL. Every application links **exactly one** BCRG object, even if empty.
Its external symbols are `BCRGBEG` and `BCRGEND`; each selected BCEX
exports an independently relocated begin/end pair. The generic
`RGINIT`/`RGFINI` code checks dependencies, ownership and versions
before exposing the requested global addresses.

## Existing concrete demonstration: four link-edits

R.2 supplies an actual source-based four-link generator at
`bootstrap-toolchain/probes/r2-interoperability/make-matrix.py`. It
uses these identical Core Runtime and Base Library components in all
links: `BCPLMAIN` (once assembled and reused), `RGINIT`/`RGFINI`
(once assembled and reused), `BCPLIO`, `BCPLMEM`, `BCPLBYTE`,
`BCPLAPT`, and the historical Base Library `BLIB`.

| Profile | App | BCPLREG bytes | Selected descriptor / dispatcher |
| --- | --- | ---: | --- |
| 0 | `zero.bcpl` | 28 | none |
| A | `demo.bcpl` | 44 | `DMODESC` / `DMODISP` (`BCPLDEMO`, G!203) |
| B | `onlyb.bcpl` | 44 | `R2BDSC` / `R2BDISP` (`R2TESTB`, **test-only** G!299) |
| A+B | `both.bcpl` | 60 | both, in registered order A then B |

The generator assembles four **different applications** and four
**different BCRG tables**. It assembles just one candidate BCPLMAIN
object and one registrar object for all four IEWL links. It assembles
both optional descriptors and dispatchers only once. The test-only B
module must not be distributed as a permanent G!299 assignment.

## IEWL: what each link actually selects

The tested generator emits equivalent per-link IEWL control records:

```
 INCLUDE OBJ(BCPLIO)
 INCLUDE OBJ(BCPLMEM)
 INCLUDE OBJ(BCPLBYTE)
 INCLUDE OBJ(BCPLAPT)
 INCLUDE OBJ(BLIB)
 ENTRY R0APP
 NAME <load-module-name>(R)
```

Before the instream IEWL control statements, the JCL supplies these
object modules as **concatenated SYSLIN DDs**:

| Profile | Required temporary SYSLIN objects |
| --- | --- |
| 0 | app, candidate `BCPLMAIN`, generic registrar, empty BCRG |
| A | app, same core/registrar, A BCRG, A BCEX, A dispatcher |
| B | app, same core/registrar, B BCRG, B BCEX, B dispatcher |
| A+B | app, same core/registrar, A+B BCRG, A BCEX, A dispatcher, B BCEX, B dispatcher |

`//OBJ DD DSN=<BOOT_OBJ>,DISP=SHR` is an **input** object PDS and the
`INCLUDE OBJ(...)` records select its mandatory members. `<BOOT_OBJ>`
means the concrete manifest-resolved dataset name, not a literal JCL
value. The temporary `&&` objects are concatenated to `SYSLIN` with
`DISP=(OLD,PASS)`, and each separate load module is also temporary.
See the generator for executable, properly authenticated JCL cards,
continuation rules, and DD/step names; do not paste pseudocode
placeholders directly into JES input.

## Reproduce the demonstrated selection jobs

At repository root, after constructing the documented bootstrap
environment, the *existing* source-controlled workflow is:

```sh
python3 -m unittest discover -s \
  bootstrap-toolchain/probes/r2-interoperability -p 'test_*.py' -v
python3 bootstrap-toolchain/probes/r2-interoperability/make-matrix.py --check
python3 tools/bootstrap/run-r2-acceptance --execute
```

The historical R.2 evidence records JOB 3080 and JOB 3091 positive
matrix PASS, and JOB 3092 negative campaign PASS on tested revision
`7141907`. This is **not** an R.3 acceptance execution, and its
limitations are recorded in `packaging/runtime-extensions-r2-closure-20261022.md`.
Do not run a new MVS job or claim a new verified result without actual
operator execution and JES/IEWL review.

## Required IEWL MAP/XREF inspection

For each of the **four** links, require successful IEWL and GO return
codes, actual BCPL markers, a real `BCPLMAIN`, `RGINIT`, `BCPLREG`,
and precisely these symbol presences:

| IEWL symbol/CSECT | 0 | A | B | A+B |
| --- | :---: | :---: | :---: | :---: |
| `DMODESC`, `DMODISP` | absent | present | absent | present |
| `R2BDSC`, `R2BDISP` | absent | absent | present | present |

Verify actual relocated `DMOBEG`/`DMOEND` and `R2BBEG`/`R2BEND`
references through IEWL MAP/XREF as applicable, rather than assuming
that matching source names prove linkage. Excluded objects must not
appear in the resolved load module. A standalone declaration or
object INCLUDE without matching BCRG registration does not satisfy
the pre-START package requirement.

## Safety and acceptance boundary

The core and registrar are not rebuilt differently for each selection;
only app, BCRG and optional-object composition varies by link.
Do not modify `BOOT_OBJ` or `BOOT_DEVOBJ`, change BCPLMAIN source,
change public ABI, allocate a global number, or implement BCPLQSAM,
BCPLTIME or BCPLDEC for this guide. Initial proof uses temporary
`&&` data sets and ignored `workarea/` files. The full fresh
145 PASS / 0 FAIL / 1 expected SKIP 083 native regression, clean
rebuild, object-PDS decision and final acceptance remain R.3 steps
4–7 and require separate owner direction.
