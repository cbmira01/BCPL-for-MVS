# Historical BLIB integration — completed march and next boundary

**Recorded:** 2026-10-08  
**Repository:** `cbmira01/BCPL-for-MVS`  
**Status:** **COMPLETE — static native integration phase**

## Verified checkpoint

The user ran the entire native regression panel on the TK5 MVS 3.8
system:

```text
tools/run-native-regression 0 68 --show-output
NATIVE REGRESSION COMPLETE
PASS  69
FAIL  0
TOTAL 69
```

This is an **observed host execution result**, not a claim that
independent object-module linkage or all BLIB procedures are complete.

Tests 065–068 all compile against the same **whole historical BLIB**,
not individually extracted BCPL routines:

| Test | Verification | Exact observed output |
| --- | --- | --- |
| 065 | Historical `WRITES` at G!60 | `HELLO` |
| 066 | Historical `WRITEN` at G!62, including `WRITED` | `42 -17 0` |
| 067 | Full BLIB compilation, static merge and native execution | `BLIB 42` |
| 068 | `WRITEX` G!74, `WRITEOCT` G!77, `NEWLINE` G!63, `WRITEF` G!76 | Four records: `HEX 0000002A`, `OCT 052`, `FORMAT 42`, `DONE` |

Historical evidence is
`richards-bcpltape/bcplib/bcpl/blib`, which should remain untouched.
`native-compiler/bootstrap-cambridge/make-demoted.py --blib-only`
produces `workarea/bootstrap-cambridge/demoted/blib`, removing the
unsupported `SECTION "BLIB"` directive and changing the two `~=`
tokens to MR10-compatible `NE`. The original `GET "LIBHDR"` and
library procedures are retained. The regression `library-source.txt`
files select this generated source.

### The exact present linkage mechanism

```text
regression source.bcpl          historical BLIB source
        |                               |
 resident Cambridge compiler     reproducible demotion
        |                               |
   application CG370 output      resident compiler / CG370
        |                               |
        +------------+------------------+
                     |
 native-compiler/regression/combine-separate-bcpl.py
                     |
     one joined generated assembly CSECT
           + BCPLMAIN-wip CSECT
                     |
                  IFOX00
                     |
            MVS object stream
                     |
                   IEWL
                     |
             executable load module
```

The application and BLIB **are separately compiled as BCPL**, but
**are not separately assembled into object modules**. The combiner
renames BLIB-local `Lnnn` labels to `Qnnn`, retains the application
entry wrapper, removes BLIB's standalone entry wrapper, appends BLIB
code/constants, and merges export/global-initialization trailer
pairs. `asm/bcplmain-wip.asm` is appended as its own CSECT. IEWL
therefore links the combined application+BLIB CSECT with BCPLMAIN;
it does not retrieve BLIB from an object PDS.

Two narrow combiner repairs were needed for the complete BLIB:
preserving a `Q999` origin reference after wrapper removal and
replacing the malformed historical signed-minimum 32-bit
`DC F'-./,),(-*,('` with `DC X'80000000'`. The repair belongs to
the current generated-assembly transport/combination scaffolding,
not a change to canonical BLIB source. Independently generated
BLIB object compilation must be checked on its own merits.

The first 067 output was `BLIB�42` where a vertical bar was
requested. Tests 066–068 use predictable output characters instead.
The vertical-bar output/transport discrepancy remains **unresolved**,
not proven to be a BLIB defect.

## Architectural conclusions and decisions

1. **Close this march.** It achieved whole historical BLIB native
   compilation and execution and a clean 69/69 regression sweep.
2. **Keep canonical BLIB intact.** It is expected to be stable, but
   regenerating its **object** could be necessary if compiler or module
   ABI conventions change.
3. **Production target:** separately compile and assemble the
   application, BLIB, and BCPLMAIN; let MVS IEWL combine their
   relocatable object modules. BCPL's global-vector initialization
   is distinct from MVS external-symbol resolution.
4. **Investigate CG370's existing module envelope first:** its entry
   wrapper, `EXTRN BCPLMAIN`, export/global table, and relocation
   semantics. Do not assume the current static merge proves
   independently compiled module initialization works.
5. **Stage A — native object-library foundation:** independently
   assemble whole BLIB without the combiner; inspect IFOX external
   symbol dictionary and relocation data; store an object member in
   an MVS PDS; demonstrate IEWL can explicitly include that member.
   This does **not** require BCPLMAIN to be finished or native
   execution to pass.
6. **Stage B — true section runtime linkage:** build an application
   object, BLIB object and BCPLMAIN object independently, link under
   IEWL, and teach/verify the evolving BCPLMAIN section and
   global-vector initialization contract. Use regression 067 as the
   initial behavioral acceptance check.
7. **Preserve regressions 000–068 unchanged as the established
   reference baseline** until a parallel object-link test proves the
   new path. Do not replace or silently weaken the static combiner.

### MVS library planning — verify before changing configuration

The established deployment authority is `tools/dspal` using
`config/dspal.yaml`. The repository is authoritative; MVS datasets
are reproducibly deployed/build artifacts.

As of this checkpoint, the manifest defines `BCPL.LOAD` as an MVS
load-module PDS but **has no `OBJ` dataset entry yet**. The planned
object library name is `HERC02.BCPL.OBJ` (the manifest uses
`hlq: HERC02` plus the dataset suffix `BCPL.*`). Its record
format/BLKSIZE, allocation rules, object-deck transport, and member
population/install operation must be designed and tested; do not
copy `FB/80` source-library text conversion or assume the load-library
format is appropriate for relocatable object decks.

Proposed members: `BLIB` initially and perhaps `BCPLMAIN` later,
with a deliberately explicit IEWL `INCLUDE` from the object PDS.
Check the external names and `SYSLIN` concatenation/inclusion syntax
against TK5's actual IEWL behavior. Using `NCAL` suppresses
automatic library search but does not replace an explicit link
strategy. Do not assert the illustrative IEWL JCL is already tested.

## Next march — proposed order, not yet performed

- Inspect and document a standalone CG370 BLIB assembly module and
  the current assembler/link-job generation.
- Determine whether it assembles independently, including all
  historical constants and global trailer information.
- Extend `dspal`'s manifest and tooling to create/manage the object
  PDS with correct **object-deck semantics** and strict safety
  boundaries; preserve current deployed libraries.
- Build and install BLIB as a relocatable PDS member, inspect ESD/RLD,
  and demonstrate explicit IEWL inclusion.
- Only then experiment with BCPLMAIN initialization of multiple
  linked BCPL sections, in parallel with existing passing tests.

**Non-goals for the completed march:** production object packaging,
BCPL multi-section loader, complete BCPLMAIN ABI, dynamic library
loading, and comprehensive verification of all historical BLIB
services.

## Handoff prompt

> Resume the BCPL-for-MVS project from the completed historical BLIB
> static-integration march, documented in
> `native-compiler/blib-integration-march-checkpoint.md`. The user
> executed `tools/run-native-regression 0 68 --show-output` under
> MVS 3.8J TK5 with **69 PASS, 0 FAIL**. Tests 065–068 use the
> complete demoted Cambridge BLIB. **Do not restart this march or
> change the passing regressions.** The next architectural objective
> is a **Native Object Library Foundation**: evaluate independent
> CG370/IFOX BLIB assembly, object-deck storage in a proposed
> `HERC02.BCPL.OBJ(BLIB)` PDS via existing `dspal` infrastructure,
> and explicit IEWL inclusion. `config/dspal.yaml` currently has a
> LOAD library but no OBJ entry. BCPLMAIN-wip is still evolving; do
> not presume multi-section global-vector initialization is ready.
> First inspect existing CG370 module wrappers, IFOX object-deck
> generation and dspal contracts. Plan changes narrowly, preserve
> canonical `richards-bcpltape/bcplib/bcpl/blib`, and keep all
> existing regressions passing. Discuss or implement the first
> object-library experiment with the user.
