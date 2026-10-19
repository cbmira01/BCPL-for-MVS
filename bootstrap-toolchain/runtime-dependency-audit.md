# Native compiler runtime dependency audit

Status: **INITIAL SOURCE-TRACED INVENTORY — executable changes not authorized**
Date: 2026-10-09. Entry native regression baseline: operator-confirmed
**90 PASS / 0 FAIL (000–089)**.

## Decision and purpose

The target is **native execution of the historical Cambridge compiler**
before general-purpose native extension-library work. Audit all known
historical contracts, but distinguish **bootstrap blockers** from optional
historical facilities and source references. Preserve the canonical BLIB
object-resource architecture and the already validated BCPLMAIN runtime.

Evidence examined in this checkpoint:

- `richards-bcpltape/sys3/bcpl/libhdr` — historical global-number map
- `richards-bcpltape/bcplib/bcpl/{bcpl,syn,trn,cg,blib}` — master,
  SYN/LEX, TRNA/TRNB, CGA–CGE, historical BLIB
- `richards-bcpltape/bcplib/bcpl/{cghdr,synhdr,trnhdr}`
- `asm/bcplmain-wip.asm` — current runtime responsibilities and code
- `native-compiler/bootstrap-cambridge/{bootstrap-host.bcpl,
  native-codegen-checkpoint.md,compiler-image-next.md}`
- `native-compiler/regression/runtime-stream-io-march.md` and
  closed `runtime-exit-semantics-march.md`

### Evidence quality

The detailed inventory below counts **lexical mentions** in the
four compiler containers (BCPL master / SYN+LEX / TRNA+TRNB / CGA–CGE).
Counts can include comments, declarations, local names, and unrelated
identifiers. **They are leads, not proof of a runtime call.**
Specific bootstrap requirements below are supported by inspected
call sites, conditional branches, and existing executable checkpoints.
The inventory is complete for *named historical LIBHDR entries*, not
a proof that every unnamed/internal BCPLMAIN service is identified.

## 1. Compiler phase topology and external resources

- The historical compiler master `bcpl` is `SECTION "BCPL"`;
  `syn` contains sections SYN and LEX; `trn` contains TRNA/TRNB;
  `cg` contains CGA–CGE. These are **ten** sections.
- The master evaluates `OVERLAYING := CODEGEN < 0`. If the
  code generator is already available in the global vector, the
  compiler follows its **resident** path; otherwise it calls
  LOADSEG for SYN/TRN/CG, which ultimately calls `LOAD(S,0)`.
  The resident configuration is an **architectural choice to avoid
  overlay dependencies initially**, not evidence that LOAD/UNLOAD
  have been fully reconstructed.
- Master input/output DDs: `FINDPARM()` supplies compiler options;
  `FINDINPUT("SYSIN")` supplies BCPL source; `FINDOUTPUT("SYSPRINT")`
  supplies diagnostics, `FINDOUTPUT("OCODE")` and
  `FINDOUTPUT("CODE")` choose intermediate and assembler streams.
  `FINDOUTPUT("SYSGO")` is required only if `DECK` is true.
- `N` codegen option sets `DECK:=FALSE`; the bootstrap's
  `/N/` options fixture intentionally disables binary deck output.
  A future production compiler still needs native binary object
  output or an explicitly supported assembler-source workflow.
- The master performs `SELECTINPUT/SELECTOUTPUT`, `RDCH`,
  `UNRDCH`, `ENDREAD/ENDWRITE`, WRAPOUTPUT, INPUT/OUTPUT
  and BLIB formatting. LEX calls `FINDINPUT` for GET sources,
  switches input streams, and closes them.
- CG370 calls DATE for the module header; its CGD `WRCARD`
  calls `WRITEREC(V,80)` only if DECK is true.
  For textual output this particular binary-record dependency
  is not on the initial critical path.

## 2. Runtime readiness, gaps, and ownership

| Interface / subsystem | Historical owner / evidence | Current reconstructed state | Native compiler priority |
| --- | --- | --- | --- |
| MVS entry and CG370 register ABI | BCPLMAIN; CGHDR, generated prefix | Working across native panel | Keep invariant |
| Global merge, START and shared globals | BCPLMAIN + compiled module trailers | Working for linked/resident modules; not general dynamic loader | **Critical**: prove full compiler image G slots |
| Global/stack GETMAIN, GETVEC/FREEVEC | BCPLMAIN, BCPLMAC | Working with tested teardown; finite fixed G!0..200 | **Critical**: capacity audit before resident compiler |
| System-vector return / FINISH / stack check | CGHDR, BCPLMAIN | Implemented in exercised subsets; COUNT placeholder and floating workspace contract outstanding | Critical for ordinary code; deeper calls conditional |
| STOP(N), output CLOSE | BCPLMAIN, Richards 1974 | Verified production termination (90-test baseline) | Keep invariant |
| Historical BLIB formatting / byte helpers | BLIB object; G85/G86 BCPLMAIN | BLIB object linked successfully, GETBYTE/PUTBYTE working | **Critical** |
| FINDPARM and compiler-option input | Master directly calls FINDPARM, RDCH | Bootstrap host shim uses `FINDINPUT("CAMBPARM")`; native interface not installed | **Critical** |
| FINDINPUT, selected input, RDCH, UNRDCH | Master and LEX calls, LIBHDR | Native RDCH and stream selection absent | **Critical — first implementation march** |
| FINDOUTPUT, SELECTOUTPUT, OUTPUT | Master, CG, BLIB | Bootstrap-only narrow WRCH/SYSPRINT; general selected streams absent | **Critical — same I/O march** |
| ENDREAD/ENDWRITE, stream status, multi-DD | Master, LEX, BLIB | No complete native stream descriptor or per-DD closure | **Critical** |
| Newline, record boundary and multi-record WRCH | Master/BLIB, LIBHDR | WRCH is currently 132-byte single-record buffer | **Critical** for compiler listing/text CODE |
| WRAPOUTPUT | Master calls; bootstrap host shim | Native behavior not supplied | **Critical** (may begin as faithful minimal state) |
| DATE | CGA call; bootstrap host shim | Native DATE missing | **Critical** for generated module header |
| APTOVEC and workspace sizing | Master calls APTOVEC(COMP,size) | Historical G40 not implemented in native runtime | **Critical**; must recover calling/storage semantics |
| STACKBASE/STACKEND | Master sizes compiler workspace | Published in WIP; stack-clearance policy imperfect | Critical, test capacity/values |
| Dynamic LOAD/UNLOAD | Master overlay branch, LIBHDR | Not implemented | Conditional; defer if full resident image proves |
| WRITEREC and SYSGO object deck | CGD under DECK | Native absent | Required for full object output, deferred on /N/ |
| READREC and raw-record/binary input | LIBHDR; master contains conditional comments / path | No native record interface | Medium; conditional compiler modes |
| TIME + diagnostics | Master WRTIME under TIMING | Not reconstructed | Conditional |
| PARMS/PARM/SETPM, execution options | LIBHDR and BCPLMAC | Native PARM grammar not recovered | Distinguish MVS entry PARM from FINDPARM stream |
| Recovery STAE/SPIE, ABORT bridge | BCPLMAC and BLIB | Not reconstructed | Compatibility/reliability; not initial successful compile |
| Floating point and R13 FWSP area | CGHDR/BCPLMAIN note, LEX READFLOAT demotion | Incomplete | Required for full language support, not initial integer-only probe |
| LIBHDR G89–G99 extended facilities | LIBHDR | Not established in BCPLMAIN | Historical compatibility; must classify per source |
| General native extension modules | `native-compiler/library/` | Sources staged only; no native object validation | **After native compiler bootstrap** |

### Concrete capacity warning

The current BCPLMAIN provides a finite G!0..G!200 implementation.
The earlier **resident INTCODE** compiler required a 700-word
global vector and used at least `FORMTREE G!150`,
`COMPILEAE G!245`, `CODEGEN G!390`,
`CG370 G!450`, and `CGSTART G!622`
(recorded in `compiler-image-next.md`).

Those are **INTCODE-host bootstrap observations**, not a completed
audit of the native linked compiler. Nevertheless, they make
the **native global-vector size and module trailer limits an immediate
potential blocker**. Do not attempt a large native compiler image
under the current 201-word global vector without a capacity plan.

### Memory/workspace warning

The compiler master measures `STACKEND-STACKBASE`, reserves
`FREESTACKSIZE` (default 3000), and passes an address/size to
`APTOVEC(COMP, WORKSPACESIZE)`. This is not interchangeable
with the current native GETVEC, and the present stack/global
allocation sizes were chosen for ordinary regression programs.
The exact APTOVEC control-transfer contract must be reconstructed
before a compiler bootstrap attempt.

## 3. Historical LIBHDR global inventory (all named assignments)

Mentions column lists source occurrences in **master / SYN+LEX /
TRNA+TRNB / CGA–CGE**, respectively. It is a conservative discovery
aid, not a link map. Slot 94 is intentionally assigned twice in
historical LIBHDR (OPENBLOCKFILE/UPDATEBLOCKFILE), and does not
justify inventing separate slots.

| G! | Name | Working ownership area | Compiler textual mentions |
| ---: | --- | --- | --- |
| 1 | START | startup | 2 / — / — / — |
| 2 | SETPM | startup | — / — / — / — |
| 3 | ABORT | exit | 5 / — / — / — |
| 4 | BACKTRACE | exit | 1 / — / — / — |
| 5 | ERRORMESSAGE | exit | — / — / — / — |
| 6 | SAVEAREA | startup | — / — / — / — |
| 7 | UNLOADALL | loader | — / — / — / — |
| 8 | LOADFORT | loader | — / — / — / — |
| 9 | UNLOAD | loader | 3 / — / — / — |
| 10 | LOAD | loader | 2 / — / 33 / 15 |
| 11 | SELECTINPUT | stream | 2 / 2 / — / — |
| 12 | SELECTOUTPUT | stream | 10 / — / 2 / 11 |
| 13 | RDCH | stream | 4 / 1 / — / — |
| 14 | WRCH | stream | 5 / 3 / 3 / 5 |
| 15 | UNRDCH | stream | 5 / — / — / — |
| 16 | INPUT | stream | 2 / — / — / — |
| 17 | OUTPUT | stream | 1 / — / — / 1 |
| 18 | INCONTROL | stream | — / — / — / — |
| 19 | OUTCONTROL | stream | — / — / — / — |
| 20 | TRIMINPUT | stream | — / — / — / — |
| 21 | SETWINDOW | stream | — / — / — / — |
| 22 | BINARYINPUT | stream | — / — / — / — |
| 23 | READREC | stream | 1 / — / — / — |
| 24 | WRITEREC | stream | — / — / — / 1 |
| 25 | WRITESEG | stream | — / — / — / — |
| 26 | SKIPREC | stream | — / 1 / — / — |
| 27 | TIMEOFDAY | mvs | — / — / — / — |
| 28 | TIME | mvs | 2 / — / — / — |
| 29 | DATE | mvs | — / — / — / 1 |
| 30 | STOP | exit | 13 / 1 / 2 / 4 |
| 31 | LEVEL | loader | — / 4 / — / — |
| 32 | LONGJUMP | loader | — / 1 / — / — |
| 33 | WRAPOUTPUT | stream | 2 / — / — / — |
| 34 | BINWRCH | stream | — / — / — / — |
| 35 | REWIND | stream | — / — / — / — |
| 36 | FINDLOG | stream | — / — / — / — |
| 37 | WRITETOLOG | stream | 2 / — / — / — |
| 38 | FINDTERMINAL | stream | — / — / — / — |
| 39 | FINDPARM | stream | 1 / — / — / — |
| 40 | APTOVEC | mvs | 1 / — / — / 1 |
| 41 | FINDOUTPUT | stream | 5 / — / — / — |
| 42 | FINDINPUT | stream | 1 / 1 / — / — |
| 43 | FINDLIBRARY | stream | — / — / — / — |
| 44 | INPUTMEMBER | stream | — / — / — / — |
| 45 | PARMS | startup | 4 / — / — / — |
| 46 | ENDREAD | stream | 2 / 2 / — / — |
| 47 | ENDWRITE | stream | 4 / — / — / — |
| 48 | CLOSELIBRARY | stream | — / — / — / — |
| 49 | OUTPUTMEMBER | stream | — / — / — / — |
| 51 | ENDTOINPUT | stream | — / — / — / — |
| 52 | LOADPOINT | startup | — / — / — / — |
| 53 | ENDPOINT | startup | — / — / — / — |
| 54 | STACKBASE | startup | 1 / — / — / — |
| 55 | STACKEND | startup | 1 / — / — / — |
| 56 | STACKHWM | startup | — / — / — / — |
| 58 | INPROGRAM | startup | — / — / — / — |
| 59 | VALIDPOINTER | startup | — / — / — / — |
| 60 | WRITES | blib | 19 / 14 / 5 / 8 |
| 61 | COMPAREBYTES | blib | — / — / — / — |
| 62 | WRITEN | blib | — / 3 / 1 / — |
| 63 | NEWLINE | blib | 1 / 5 / 3 / 8 |
| 64 | NEWPAGE | blib | — / — / — / — |
| 65 | WRITEO | blib | — / — / — / — |
| 66 | PACKSTRING | blib | — / 3 / — / 2 |
| 67 | UNPACKSTRING | blib | — / — / 3 / 1 |
| 68 | WRITED | blib | — / — / — / — |
| 69 | WRITEARG | blib | — / — / — / — |
| 70 | READN | blib | 4 / — / — / 37 |
| 71 | TERMINATOR | blib | — / — / — / — |
| 72 | SCANBLOCKFILE | blib | — / — / — / — |
| 74 | WRITEX | blib | — / — / — / 1 |
| 75 | WRITEHEX | blib | — / — / — / — |
| 76 | WRITEF | blib | 11 / 8 / 4 / 26 |
| 77 | WRITEOCT | blib | — / — / — / — |
| 78 | MAPSTORE | exit | 2 / — / — / — |
| 79 | USERPOSTMORTEM | exit | — / — / — / — |
| 80 | CALLIFORT | special | — / — / — / — |
| 81 | CALLRFORT | special | — / — / — / — |
| 82 | SETBREAK | special | — / — / — / — |
| 83 | ISBREAK | special | — / — / — / — |
| 84 | ERRORRESET | exit | — / — / — / — |
| 85 | GETBYTE | mvs | 3 / 3 / 4 / 4 |
| 86 | PUTBYTE | mvs | 4 / 1 / 4 / 2 |
| 87 | GETVEC | mvs | — / — / — / — |
| 88 | FREEVEC | mvs | — / — / — / — |
| 89 | RANDOM | blib | — / — / — / — |
| 90 | MULDIV | blib | — / — / — / — |
| 91 | RESULT2 | blib | — / — / — / — |
| 92 | BLOCKSIZE | mvs | — / — / — / — |
| 93 | CREATEBLOCKFILE | special | — / — / — / — |
| 94 | OPENBLOCKFILE | special | — / — / — / — |
| 94 | UPDATEBLOCKFILE | special | — / — / — / — |
| 95 | CLOSEBLOCKFILE | special | — / — / — / — |
| 96 | READBLOCK | special | — / — / — / — |
| 97 | WRITEBLOCK | special | — / — / — / — |
| 98 | WRNEXTBLOCK | special | — / — / — / — |
| 99 | MOVEBYTES | blib | — / — / — / — |

## 4. BCPLMAIN internal contracts that LIBHDR does not enumerate

- MVS caller save-area choreography, entry linkage, R13 private work,
  and R14/R15 return behavior; R0 permanent zero, R1..R3 anchor
  constants, generated-code registers R4–R12/R15.
- S-vector: return +0, COUNT +20, FINISH +40, STACKCK +60,
  STACKCKCOUNT +80; verify each handler's exact effects, especially
  counters and floating-point R13 workspace.
- Runtime sizing/options: BCPLMAC HNUM, GNUM, KNUM, DFLG, TNUM, INUM;
  PARM grammar is still unknown. Startup must honor documented
  contracts without replacing historical options with guesswork.
- Global-vector initial sentinels, exported-global trailer scanning,
  section entry/return bookkeeping, static/resident module metadata.
- MVS GETMAIN/FREEMAIN ownership; explicit vector descriptors;
  output DCBs/record buffers; final cleanup; stack exhaustion.
- STAE/SPIE recovery and linkage into BLIB ABORT's
  `(CODE, ADDR, OLDSTACK, DATA)` signature.
- Character representation: native S/370 EBCDIC BCPL string bytes,
  32-bit 4-byte words vs MR10/ICINT host 2-byte words.
- Native object output: assembler textual CODE and binary SYSGO
  are **different record/transport contracts**.

## 5. Work plan and gates

**Gate A — contract/capacity deepening (no executable change):**
Trace native global counts and exports for all ten sections, map
BCPLMAIN's 201-word current limit against the compiler requirements,
and reconstruct APTOVEC plus the required size/stack discipline.
Extract detailed stream semantics from the historical manual,
BCPLMAC DCB structures and compiler call sites.

**Gate B — selected stream I/O:**
Provide DD-discovered input, FINDPARM, RDCH, UNRDCH, SELECTINPUT,
INPUT, EOF/newline; then named output, SELECTOUTPUT, OUTPUT,
multi-record WRCH, ENDREAD/ENDWRITE, and WRAPOUTPUT. Keep existing
SYSPRINT behavior and termination cleanup tested throughout.

**Gate C — resident compiler linkage proof:**
Compile/link required sections, verify exported global indices and
actual cross-module calls. Validate DATE and APTOVEC contracts,
compiler workspace capacity, and use /N/ for textual assembly.
Do not claim native self-hosting until a compiler running as native
S/370 code successfully compiles a BCPL input.

**Gate D — full behavior and historical coverage:**
Binary SYSGO deck records, overlay LOAD/UNLOAD where required,
runtime options, diagnostics/recovery, floating-point, optional
record/block I/O, and any additional services proved necessary.

After each executable rung: run focused TK5 tests, then the complete
native panel at a march boundary. **No current test or runtime
implementation is modified by this audit.**

## 6. Explicit unknowns / source coverage limits

- Historical ownership of every LIBHDR routine between BCPLMAIN,
  BLIB, IOS/PM, and optional subsystems has not yet been proven
  from assembler definitions alone; the ownership column is a
  **working classification**, not a verified symbol map.
- Lexical mentions are not a program-flow reachability analysis;
  error, tracing and overlay branches need targeted inspection.
- Compiler frontend `GET` include files and output settings may
  require additional DDs; only named resources observed above are
  asserted.
- Real MVS PARM format and historically precise input record
  trimming/newline/EOF rules remain to be established.
- Native full-compiler aggregate storage and addressing pressure
  must be measured instead of extrapolated solely from ICINT V19.
