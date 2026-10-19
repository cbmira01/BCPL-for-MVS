# Complete LIBHDR G1–G99 reconciliation — source evidence checkpoint

**Status:** Static source audit, no machine-code changes. Examined on 11 October 2026 against repository `main`. Accepted baseline remains 119/119 installed-object and 120/120 mixed-mode.

## Evidence and scope

* `richards-bcpltape/sys3/bcpl/libhdr`: authoritative **names/numbers for this comparison**, not proof of implementation.
* `richards-bcpltape/bcplib/bcpl/blib`: surviving historical portable library **source definitions**. 21 named LIBHDR entries have top-level `LET`/`AND` definitions. This is not an independent symbol-table or installed-PDS export dump.
* `asm/bcplmain-wip/10-bootstrap-and-system.asmfrag`: startup **direct assignments** to the global vector (R12), including the conditional G76 fallback. Five objects installed in accepted MVS PDS: BCPLMAIN, BCPLBYTE, BCPLAPT, BCPLMEM, BLIB.
* `native-compiler/regression/37-multiple-exported-globals/source.bcpl` and startup `GINST` loop: application-defined globals are imported from the compiler's global trailer; G1 START is an example.

**Classification:** "Unresolved" means no matching BLIB routine definition and no direct BCPLMAIN startup write found **in these inspected sources**. It does not imply unimplemented or prove absent from other runtime sources, alternate library versions, or application exports. Source definitions are not proof of successful object export. Test-specific functionality requires independent evidence. Numeric cell G0 is global-vector metadata, outside LIBHDR G1–G99.

## Per-slot reconciliation

| G | LIBHDR declaration | Observed source owner / installation | Evidence or limitation |
|---:|---|---|---|
| 1 | START | Unresolved | No direct startup write or BLIB definition found |
| 2 | SETPM | Unresolved | No direct startup write or BLIB definition found |
| 3 | ABORT | BLIB source | Definition: ABORT |
| 4 | BACKTRACE | BLIB source | Definition: BACKTRACE |
| 5 | ERRORMESSAGE | BLIB source | Definition: ERRORMESSAGE |
| 6 | SAVEAREA | BCPLMAIN | R13 word pointer (provisional) |
| 7 | UNLOADALL | Unresolved | No direct startup write or BLIB definition found |
| 8 | LOADFORT | Unresolved | No direct startup write or BLIB definition found |
| 9 | UNLOAD | Unresolved | No direct startup write or BLIB definition found |
| 10 | LOAD | Unresolved | No direct startup write or BLIB definition found |
| 11 | SELECTINPUT | BCPLMAIN | SELINP |
| 12 | SELECTOUTPUT | BCPLMAIN | SELOUT |
| 13 | RDCH | BCPLMAIN | RDCHENT |
| 14 | WRCH | BCPLMAIN | WRCH |
| 15 | UNRDCH | BCPLMAIN | UNRDCHEN |
| 16 | INPUT | BCPLMAIN | INPENT |
| 17 | OUTPUT | BCPLMAIN | OUTENT |
| 18 | INCONTROL | Unresolved | No direct startup write or BLIB definition found |
| 19 | OUTCONTROL | Unresolved | No direct startup write or BLIB definition found |
| 20 | TRIMINPUT | Unresolved | No direct startup write or BLIB definition found |
| 21 | SETWINDOW | Unresolved | No direct startup write or BLIB definition found |
| 22 | BINARYINPUT | Unresolved | No direct startup write or BLIB definition found |
| 23 | READREC | Unresolved | No direct startup write or BLIB definition found |
| 24 | WRITEREC | Unresolved | No direct startup write or BLIB definition found |
| 25 | WRITESEG | Unresolved | No direct startup write or BLIB definition found |
| 26 | SKIPREC | Unresolved | No direct startup write or BLIB definition found |
| 27 | TIMEOFDAY | Unresolved | No direct startup write or BLIB definition found |
| 28 | TIME | Unresolved | No direct startup write or BLIB definition found |
| 29 | DATE | Unresolved | No direct startup write or BLIB definition found |
| 30 | STOP | BCPLMAIN | STOPENT |
| 31 | LEVEL | Unresolved | No direct startup write or BLIB definition found |
| 32 | LONGJUMP | Unresolved | No direct startup write or BLIB definition found |
| 33 | WRAPOUTPUT | BCPLMAIN | WRAPENT |
| 34 | BINWRCH | Unresolved | No direct startup write or BLIB definition found |
| 35 | REWIND | Unresolved | No direct startup write or BLIB definition found |
| 36 | FINDLOG | Unresolved | No direct startup write or BLIB definition found |
| 37 | WRITETOLOG | Unresolved | No direct startup write or BLIB definition found |
| 38 | FINDTERMINAL | Unresolved | No direct startup write or BLIB definition found |
| 39 | FINDPARM | BCPLMAIN | PARMENT |
| 40 | APTOVEC | BCPLAPT | BCPLAPT |
| 41 | FINDOUTPUT | BCPLMAIN | FINDOUT |
| 42 | FINDINPUT | BCPLMAIN | FINDINP |
| 43 | FINDLIBRARY | Unresolved | No direct startup write or BLIB definition found |
| 44 | INPUTMEMBER | Unresolved | No direct startup write or BLIB definition found |
| 45 | PARMS | Unresolved | No startup assignment; distinguish from G39 FINDPARM |
| 46 | ENDREAD | BCPLMAIN | ENDRDENT |
| 47 | ENDWRITE | BCPLMAIN | ENDWENT |
| 48 | CLOSELIBRARY | Unresolved | No direct startup write or BLIB definition found |
| 49 | OUTPUTMEMBER | Unresolved | No direct startup write or BLIB definition found |
| 50 | (reserved/unnamed) | Unresolved | Not declared as routine in LIBHDR |
| 51 | ENDTOINPUT | Unresolved | No direct startup write or BLIB definition found |
| 52 | LOADPOINT | BCPLMAIN | MODBASE (provisional) |
| 53 | ENDPOINT | BCPLMAIN | MODEND (provisional) |
| 54 | STACKBASE | BCPLMAIN | DYNWORK |
| 55 | STACKEND | BCPLMAIN | DYNEND |
| 56 | STACKHWM | BLIB source | Definition: STACKHWM; BLIB STACKHWM depends on stack initialization pattern |
| 57 | OS/CMS marker (unnamed) | Unresolved | LIBHDR comment; no startup write observed |
| 58 | INPROGRAM | BLIB source | Definition: INPROGRAM |
| 59 | VALIDPOINTER | BLIB source | Definition: VALIDPOINTER |
| 60 | WRITES | BLIB source | Definition: WRITES |
| 61 | COMPAREBYTES | Unresolved | No direct startup write or BLIB definition found |
| 62 | WRITEN | BLIB source | Definition: WRITEN |
| 63 | NEWLINE | BLIB source | Definition: NEWLINE |
| 64 | NEWPAGE | BLIB source | Definition: NEWPAGE |
| 65 | WRITEO | BLIB source | Definition: WRITEO |
| 66 | PACKSTRING | BLIB source | Definition: PACKSTRING |
| 67 | UNPACKSTRING | BLIB source | Definition: UNPACKSTRING |
| 68 | WRITED | BLIB source | Definition: WRITED |
| 69 | WRITEARG | BLIB source | Definition: WRITEARG |
| 70 | READN | BLIB source | Definition: READN |
| 71 | TERMINATOR | Unresolved | No direct startup write or BLIB definition found |
| 72 | SCANBLOCKFILE | Unresolved | No direct startup write or BLIB definition found |
| 73 | (reserved/unnamed) | Unresolved | Not declared as routine in LIBHDR |
| 74 | WRITEX | BLIB source | Definition: WRITEX |
| 75 | WRITEHEX | BLIB source | Definition: WRITEHEX |
| 76 | WRITEF | BCPLMAIN + BLIB source | WRITEST only if BLIB unset; Definition: WRITEF |
| 77 | WRITEOCT | BLIB source | Definition: WRITEOCT |
| 78 | MAPSTORE | BLIB source | Definition: MAPSTORE |
| 79 | USERPOSTMORTEM | Unresolved | No direct startup write or BLIB definition found |
| 80 | CALLIFORT | Unresolved | No direct startup write or BLIB definition found |
| 81 | CALLRFORT | Unresolved | No direct startup write or BLIB definition found |
| 82 | SETBREAK | Unresolved | No direct startup write or BLIB definition found |
| 83 | ISBREAK | Unresolved | No direct startup write or BLIB definition found |
| 84 | ERRORRESET | Unresolved | No direct startup write or BLIB definition found |
| 85 | GETBYTE | BCPLBYTE | BCPLBYTE |
| 86 | PUTBYTE | BCPLBYTE | BCPLBYTE |
| 87 | GETVEC | BCPLMEM | BCPLMEM |
| 88 | FREEVEC | BCPLMEM | BCPLMEM |
| 89 | RANDOM | Unresolved | No direct startup write or BLIB definition found |
| 90 | MULDIV | Unresolved | No direct startup write or BLIB definition found |
| 91 | RESULT2 | Unresolved | No direct startup write or BLIB definition found |
| 92 | BLOCKSIZE | Unresolved | No direct startup write or BLIB definition found |
| 93 | CREATEBLOCKFILE | Unresolved | No direct startup write or BLIB definition found |
| 94 | OPENBLOCKFILE / UPDATEBLOCKFILE | Unresolved | Two LIBHDR names share G94 |
| 95 | CLOSEBLOCKFILE | Unresolved | No direct startup write or BLIB definition found |
| 96 | READBLOCK | Unresolved | No direct startup write or BLIB definition found |
| 97 | WRITEBLOCK | Unresolved | No direct startup write or BLIB definition found |
| 98 | WRNEXTBLOCK | Unresolved | No direct startup write or BLIB definition found |
| 99 | MOVEBYTES | Unresolved | No direct startup write or BLIB definition found |

## Findings and next gate

1. **Historical BLIB source** defines 21 LIBHDR-named routines: WRITES, UNPACKSTRING, PACKSTRING, WRITEF, ABORT, ERRORMESSAGE, STACKHWM, MAPSTORE, INPROGRAM, VALIDPOINTER, BACKTRACE, WRITEARG, WRITED, WRITEN, NEWLINE, NEWPAGE, READN, WRITEOCT, WRITEHEX, WRITEO, WRITEX. BLIB `PRINTWIDTH` is a private helper; other nested local functions are not necessarily exported.
2. **BCPLMAIN startup** assigns the named globals G6, G11–G17, G30, G33, G39–G42, G46–G47, G52–G55, G76 (conditionally), G85–G88; plus non-LIBHDR G150 diagnostic. G1 START is imported from application exports rather than supplied as a BCPLMAIN routine. G0 is runtime vector metadata.
3. **Externalized machine primitives**: G40 BCPLAPT; G85–G86 BCPLBYTE; G87–G88 BCPLMEM. Startup's source labels are not a substitute for IEWL proof of the installed members; acceptance tests furnish behavior evidence.
4. **Deliberate uncertainties**: G45 PARMS is not G39 FINDPARM; G56 STACKHWM's BLIB routine relies on historical stack markers; G57 lacks a declared symbol but LIBHDR says OS/CMS; G94 aliases OPENBLOCKFILE and UPDATEBLOCKFILE in this specific surviving header.
5. **Application exports** are variable per compiled module. The compiler global trailer / `GINST` startup import is proven as a mechanism, not a universal static list of application-defined G numbers.

**Next bounded investigation (no implementation yet):** trace live consumers and exact expected semantics of G45, G56, G57; separately cross-check the installed BLIB object's global export trailer/listing against the surviving source before calling the 21 definitions verified installed exports. Preserve existing regressions and modular ownership.
