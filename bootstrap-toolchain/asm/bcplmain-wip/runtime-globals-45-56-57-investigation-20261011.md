# Runtime globals G45, G56, G57 — historical contract and consumers

**Status:** Evidence-only checkpoint (11 October 2026). No executable,
LIBHDR, or PDS changes. Keep the accepted 119/119 production-object and
120/120 mixed-mode regression baselines unchanged.

## Evidence inspected

* `richards-bcpltape/sys3/bcpl/libhdr`
* `richards-bcpltape/bcplib/bcpl/blib`
* `asm/bcplmain-wip/10-bootstrap-and-system.asmfrag`
* `asm/bcplmain-wip/00-contract.asmfrag`
* `docs/stack-check-contract.md`
* `bootstrap-toolchain/bootstrap-cambridge/compiler-options-and-parm.md`
* `bootstrap-toolchain/regression/108-findparm-stream/README.md`

This is a targeted source/document examination, **not an exhaustive
repository-wide consumer scan** or an installed-object symbol dump.
A lack of observed uses below must not be treated as proof of no use.

## Comparison

| Global | Historical interface evidence | Actual observed consumer / producer | Present reconstruction | Missing proof |
| --- | --- | --- | --- | --- |
| **G45 PARMS** | SYS3 LIBHDR declares `PARMS:45`. Compiler options documentation says second-phase `G...` copies remaining option record into `PARMS`. | The compiler options parser consumes the parameter pseudo-stream via `SELECTINPUT(FINDPARM())`; this is **G39**, not evidence that G45 is the pseudo-stream. Documentation mentions a compiler-side `PARMS` destination, but its binding to LIBHDR G45 is **not verified**. | No G45 startup store identified. G39 is installed as `PARMENT`, currently mapped to a prepared input DD for regression 108. | Determine whether historical G45 is a writable pointer, parameter buffer, runtime string or a compiler-local/global shadow; locate defining use and exact storage/lifetime. |
| **G56 STACKHWM** | SYS3 LIBHDR declares `STACKHWM:56`; surviving BLIB implements `STACKHWM()`. It examines `STACKEND-1` and `STACKEND-2`, `STACKBASE`, and sentinel words `#X5C40E2E3` and `#XC3D2405C`; comments name results OVERFLOW=0, UNSET=1. | BLIB `MAPSTORE` invokes `STACKHWM()` to report stack utilization. This is a **confirmed historical consumer**, not merely a declaration. | BCPLMAIN installs G54 STACKBASE and G55 STACKEND, but source inspected shows no initial stack-pattern fill contract or G56 installation by BCPLMAIN. The BLIB source has G56 definition; installed member export/result not independently verified by this audit. | Verify actual installed BLIB G56 export and stack-marker initialization/word-address layout; avoid claiming stack high-water accuracy from existing stack-limit regressions. |
| **G57 OS/CMS** | SYS3 LIBHDR comment: `GLOBAL 57 IS SET TO 'OS' OR 'CMS'`. No named declaration for G57. | No concrete G57 reader was established in the targeted source set. The comment is evidence of intent, not of data encoding or operational consumer. | No G57 startup store identified; MVS runtime environment is OS, not CMS. | Determine whether value is BCPL string pointer, packed word, or another representation; check consumers and historical initialization before assigning a value. |

## Critical distinctions

* **PARMS != FINDPARM.** The parameter stream G39 has a well-supported
  historical connection to the MVS EXEC PARM field, but the meaning
  and ownership of G45 require separate proof.
* **G56 implementation exists in BLIB source**, yet the function depends
  on the runtime's initialization discipline. Adding another assembler
  STACKHWM implementation would duplicate likely library ownership.
* **G57 is a data value**, not automatically a callable service. Do not
  guess its representation from the quoted two/three-letter strings.

## Decision and next bounded gate

**First candidate: G57 environment marker**, chosen solely because
it should require minimal machine-dependent behavior *after* its value
representation and consumer contract are established. Do not yet write
a constant or add a new global assignment.

1. Search the surviving historical SYS3 sources and relevant macros
   explicitly for accesses to global **57** and OS/CMS marker
   initialization; determine value encoding/word-vs-string semantics.
2. If proven, introduce a single startup global assignment (BCPLMAIN
   ownership; no new object required for a constant) and a narrow
   regression that observes the actual representation and never assumes
   a decoded pointer by guesswork.
3. If still ambiguous, defer G57 rather than fabricating an ABI; next
   investigate G45 producer/storage contract, then G56's BLIB export
   and historical marker initialization.

No implementation is authorized by this evidence checkpoint alone.
