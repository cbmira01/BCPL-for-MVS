# Global Number Registry

**Project:** BCPL for MVS 3.8 Reconstruction
**Effective date:** 2026-10-22
**Authority:** Official repository record of BCPL GLOBAL-number ownership.
**Status:** Historical and existing project slots inventoried; G!200–G!202 are assigned to System Extensions, and **G!203 is permanently assigned to the BCPLDEMO reference optional extension** (owner approval 22 October 2026). Allocation does **not** imply successful MVS execution or deployment.

## Rules and interpretation

- A BCPL `GLOBAL` number identifies a 32-bit global-vector word. Native S/370 code addresses `G!N` at global-base byte offset `4*N`.
- The reconstructed runtimes presently allocate globals **G!0–G!699**; capacity is an implementation limit, not a license to reuse historical numbers. `G!0` contains vector-extent metadata.
- The **historical `LIBHDR`** table below reserves its names and positions, including services not implemented in the reconstructed runtime. Do not silently change original assignments.
- The historical **Cambridge compiler `CGHDR`** also declares globals. Compiler-internal slots matter when assembling the full compiler; do not treat unlisted gaps as universally available.
- **MR10-local interpreted-library** slots are catalogued separately. These overlap historical names; their allocation scope must not be confused with native Cambridge compatibility.
- One publicly assigned slot normally names one **optional-package dispatcher**, not every package opcode. Package-local opcodes live in each package's contract.
- A public GLOBAL declaration, IEWL inclusion of an object, and runtime global-vector registration are three distinct operations. These new allocations do **not** install implementations.
- When a slot is retired, keep a tombstone. Future allocations and any User/Site Library ranges require recorded collision review; unlisted does not automatically mean free.
- Collision checking for a real executable must inspect its **effective combined** source/header/registration set. No universal User/Site Library range is assigned yet.

**R.0 ownership decision E (approved):** This document allocates
public slots; the per-executable owner ledger must separately verify
actual application, BLIB, native and optional writers before any
optional registration. Preserve only verified historical precedence
and reject new optional overwrites transactionally. See
[owner ABI decisions A–H](runtime-extensions-r0-owner-abi-decisions.md).

## Project-approved optional package allocations

| Global | Public name | Owner | Allocation | Implementation |
|---:|---|---|---|---|
| **200** | **`QSAMSVC`** | **BCPLQSAM**, MVS QSAM logical-record I/O | **Assigned** | Q.0 design; not implemented |
| **201** | Public name to be chosen | **BCPLTIME**, date/time services | **Assigned** | Proposed; not implemented |
| **202** | Public name to be chosen | **BCPLDEC**, decimal arithmetic | **Assigned** | Proposed; not implemented |
| **203** | **`DEMOSVC`** | **BCPLDEMO**, project-maintained teaching/reference extension | **Permanently assigned** (22 Oct 2026) | R.2 source candidate; MVS verification pending |

G!200 belongs exclusively to BCPLQSAM. Prior `TIMESVC:200` examples in design documents were illustrative and are superseded; any illustrative BCPLTIME dispatcher is associated with its new assignment **G!201**. Neither BCPLTIME nor BCPLDEC has an approved public dispatcher spelling yet.

**G!203 / `DEMOSVC` belongs exclusively to BCPLDEMO.** Its fixed slot is deliberately permanent so the example demonstrates real compile-time `GLOBAL` declarations, IEWL relocation of a `BCEX` dispatcher entry, and subsequent `BCPLREG` startup installation. [Owner decision and R.2 boundary](runtime-extensions-r2-bcpldemo-decision-20261022.md). Other applications and extensions must not reuse G!203. The package does not bypass ordinary R.1 per-executable collision and missing-package validation.

## Specific existing positions and conflicts

| Global | Evidence | Disposition |
|---:|---|---|
| 0 | `BCPLMAIN`: global-vector extent | Runtime metadata, not callable |
| 1 | `LIBHDR`: `START` | Historical global, application entry |
| 50 | No named `LIBHDR` declaration | Historical gap; preserve pending deliberate allocation |
| 57 | `LIBHDR`: OS/CMS marker comment | Historical data slot; representation unresolved |
| 73 | `LIBHDR`: explicitly spare | Historical spare, do not silently allocate |
| 94 | `LIBHDR`: `OPENBLOCKFILE` **and** `UPDATEBLOCKFILE` | **Duplicate historical assignment**; document, do not change evidence |
| 150 | Bootstrap `BCPLMAIN` startup DEBUGINT conflicts with historical full Cambridge compiler `FORMTREE:150` in `cambridge-compiler/source/bcpl.bcpl` and `synhdr.bcpl` | **Known cross-component conflict; unresolved**; see [G!150 review](runtime-extensions-r0-g150-startup-ownership-review-20261021.md) |
| 699 | `HIGHMARK` in native regression 090 | Test-local assignment; not a permanent public package slot |

Historical `LIBHDR` also declares `FIRSTFREEGLOBAL=150`. That is **not** a current vacancy guarantee. The Cambridge compiler's `CGHDR` uses compiler globals in the 100s and above; the reconstructed runtime has an existing G!150 diagnostic collision.

## Historical runtime GLOBAL declarations (LIBHDR)

**Source authority:** [`richards-bcpltape/sys3/bcpl/libhdr`](../richards-bcpltape/sys3/bcpl/libhdr).
This table reproduces all explicit named numeric GLOBAL declarations in that source, not a claim that all are installed and working.

| Global | Historical name(s) | Ownership |
|---:|---|---|
| 1 | `START` | Historical LIBHDR |
| 2 | `SETPM` | Historical LIBHDR |
| 3 | `ABORT` | Historical LIBHDR |
| 4 | `BACKTRACE` | Historical LIBHDR |
| 5 | `ERRORMESSAGE` | Historical LIBHDR |
| 6 | `SAVEAREA` | Historical LIBHDR |
| 7 | `UNLOADALL` | Historical LIBHDR |
| 8 | `LOADFORT` | Historical LIBHDR |
| 9 | `UNLOAD` | Historical LIBHDR |
| 10 | `LOAD` | Historical LIBHDR |
| 11 | `SELECTINPUT` | Historical LIBHDR |
| 12 | `SELECTOUTPUT` | Historical LIBHDR |
| 13 | `RDCH` | Historical LIBHDR |
| 14 | `WRCH` | Historical LIBHDR |
| 15 | `UNRDCH` | Historical LIBHDR |
| 16 | `INPUT` | Historical LIBHDR |
| 17 | `OUTPUT` | Historical LIBHDR |
| 18 | `INCONTROL` | Historical LIBHDR |
| 19 | `OUTCONTROL` | Historical LIBHDR |
| 20 | `TRIMINPUT` | Historical LIBHDR |
| 21 | `SETWINDOW` | Historical LIBHDR |
| 22 | `BINARYINPUT` | Historical LIBHDR |
| 23 | `READREC` | Historical LIBHDR |
| 24 | `WRITEREC` | Historical LIBHDR |
| 25 | `WRITESEG` | Historical LIBHDR |
| 26 | `SKIPREC` | Historical LIBHDR |
| 27 | `TIMEOFDAY` | Historical LIBHDR |
| 28 | `TIME` | Historical LIBHDR |
| 29 | `DATE` | Historical LIBHDR |
| 30 | `STOP` | Historical LIBHDR |
| 31 | `LEVEL` | Historical LIBHDR |
| 32 | `LONGJUMP` | Historical LIBHDR |
| 33 | `WRAPOUTPUT` | Historical LIBHDR |
| 34 | `BINWRCH` | Historical LIBHDR |
| 35 | `REWIND` | Historical LIBHDR |
| 36 | `FINDLOG` | Historical LIBHDR |
| 37 | `WRITETOLOG` | Historical LIBHDR |
| 38 | `FINDTERMINAL` | Historical LIBHDR |
| 39 | `FINDPARM` | Historical LIBHDR |
| 40 | `APTOVEC` | Historical LIBHDR |
| 41 | `FINDOUTPUT` | Historical LIBHDR |
| 42 | `FINDINPUT` | Historical LIBHDR |
| 43 | `FINDLIBRARY` | Historical LIBHDR |
| 44 | `INPUTMEMBER` | Historical LIBHDR |
| 45 | `PARMS` | Historical LIBHDR |
| 46 | `ENDREAD` | Historical LIBHDR |
| 47 | `ENDWRITE` | Historical LIBHDR |
| 48 | `CLOSELIBRARY` | Historical LIBHDR |
| 49 | `OUTPUTMEMBER` | Historical LIBHDR |
| 51 | `ENDTOINPUT` | Historical LIBHDR |
| 52 | `LOADPOINT` | Historical LIBHDR |
| 53 | `ENDPOINT` | Historical LIBHDR |
| 54 | `STACKBASE` | Historical LIBHDR |
| 55 | `STACKEND` | Historical LIBHDR |
| 56 | `STACKHWM` | Historical LIBHDR |
| 58 | `INPROGRAM` | Historical LIBHDR |
| 59 | `VALIDPOINTER` | Historical LIBHDR |
| 60 | `WRITES` | Historical LIBHDR |
| 61 | `COMPAREBYTES` | Historical LIBHDR |
| 62 | `WRITEN` | Historical LIBHDR |
| 63 | `NEWLINE` | Historical LIBHDR |
| 64 | `NEWPAGE` | Historical LIBHDR |
| 65 | `WRITEO` | Historical LIBHDR |
| 66 | `PACKSTRING` | Historical LIBHDR |
| 67 | `UNPACKSTRING` | Historical LIBHDR |
| 68 | `WRITED` | Historical LIBHDR |
| 69 | `WRITEARG` | Historical LIBHDR |
| 70 | `READN` | Historical LIBHDR |
| 71 | `TERMINATOR` | Historical LIBHDR |
| 72 | `SCANBLOCKFILE` | Historical LIBHDR |
| 74 | `WRITEX` | Historical LIBHDR |
| 75 | `WRITEHEX` | Historical LIBHDR |
| 76 | `WRITEF` | Historical LIBHDR |
| 77 | `WRITEOCT` | Historical LIBHDR |
| 78 | `MAPSTORE` | Historical LIBHDR |
| 79 | `USERPOSTMORTEM` | Historical LIBHDR |
| 80 | `CALLIFORT` | Historical LIBHDR |
| 81 | `CALLRFORT` | Historical LIBHDR |
| 82 | `SETBREAK` | Historical LIBHDR |
| 83 | `ISBREAK` | Historical LIBHDR |
| 84 | `ERRORRESET` | Historical LIBHDR |
| 85 | `GETBYTE` | Historical LIBHDR |
| 86 | `PUTBYTE` | Historical LIBHDR |
| 87 | `GETVEC` | Historical LIBHDR |
| 88 | `FREEVEC` | Historical LIBHDR |
| 89 | `RANDOM` | Historical LIBHDR |
| 90 | `MULDIV` | Historical LIBHDR |
| 91 | `RESULT2` | Historical LIBHDR |
| 92 | `BLOCKSIZE` | Historical LIBHDR |
| 93 | `CREATEBLOCKFILE` | Historical LIBHDR |
| 94 | `OPENBLOCKFILE` / `UPDATEBLOCKFILE` | Historical LIBHDR |
| 95 | `CLOSEBLOCKFILE` | Historical LIBHDR |
| 96 | `READBLOCK` | Historical LIBHDR |
| 97 | `WRITEBLOCK` | Historical LIBHDR |
| 98 | `WRNEXTBLOCK` | Historical LIBHDR |
| 99 | `MOVEBYTES` | Historical LIBHDR |

**G!94 is intentionally shown with both original names.** Resolve its ambiguity only through a separate documented historical-contract decision. G!50/G!57/G!73 appear in the special-cases table because they lack ordinary named declarations.

## Historical Cambridge compiler GLOBAL declarations (CGHDR)

**Source authority:** [`richards-bcpltape/bcplib/bcpl/cghdr`](../richards-bcpltape/bcplib/bcpl/cghdr).
Every numeric `GLOBAL` declaration from this header is listed. `MANIFEST` constants are not global slots.

| Global | Compiler name | Ownership |
|---:|---|---|
| 110 | `PRSOURCE` | Compiler CGHDR |
| 129 | `QUIET` | Compiler CGHDR |
| 320 | `SYSOPT` | Compiler CGHDR |
| 321 | `SYSIPT` | Compiler CGHDR |
| 322 | `SYSPCH` | Compiler CGHDR |
| 323 | `CODESTREAM` | Compiler CGHDR |
| 326 | `DIAGNOSTICS` | Compiler CGHDR |
| 331 | `REPORTCOUNT` | Compiler CGHDR |
| 332 | `REPORTMAX` | Compiler CGHDR |
| 334 | `MEMBERNAMEING` | Compiler CGHDR |
| 336 | `SECTIONNAME` | Compiler CGHDR |
| 350 | `WORKBASE` | Compiler CGHDR |
| 351 | `WORKTOP` | Compiler CGHDR |
| 353 | `OBUFB` | Compiler CGHDR |
| 355 | `CGWORKVEC` | Compiler CGHDR |
| 370 | `GETBYTES` | Compiler CGHDR |
| 390 | `CODEGEN` | Compiler CGHDR |
| 401 | `BINING` | Compiler CGHDR |
| 403 | `LISTING` | Compiler CGHDR |
| 405 | `DECK` | Compiler CGHDR |
| 406 | `CGTRACE` | Compiler CGHDR |
| 407 | `LISTDECK` | Compiler CGHDR |
| 410 | `SEQNUMB` | Compiler CGHDR |
| 412 | `INCODE` | Compiler CGHDR |
| 415 | `COUNTFLAG` | Compiler CGHDR |
| 416 | `CALLCOUNTING` | Compiler CGHDR |
| 417 | `COUNTING` | Compiler CGHDR |
| 418 | `STINDRET` | Compiler CGHDR |
| 419 | `STKCKING` | Compiler CGHDR |
| 430 | `READOP` | Compiler CGHDR |
| 431 | `READN` | Compiler CGHDR |
| 432 | `READL` | Compiler CGHDR |
| 433 | `READGN` | Compiler CGHDR |
| 450 | `CG370` | Compiler CGHDR |
| 451 | `CGREPORT` | Compiler CGHDR |
| 452 | `CGMESSAGE` | Compiler CGHDR |
| 455 | `NEXTPARAM` | Compiler CGHDR |
| 456 | `INITSTACK` | Compiler CGHDR |
| 457 | `LOAD` | Compiler CGHDR |
| 460 | `LOSE` | Compiler CGHDR |
| 461 | `STACK` | Compiler CGHDR |
| 462 | `STORE` | Compiler CGHDR |
| 465 | `STORET` | Compiler CGHDR |
| 466 | `USING` | Compiler CGHDR |
| 467 | `NEXTR` | Compiler CGHDR |
| 468 | `FREEREG` | Compiler CGHDR |
| 470 | `TEMPV` | Compiler CGHDR |
| 471 | `TEMPT` | Compiler CGHDR |
| 472 | `SSP` | Compiler CGHDR |
| 475 | `ARG1` | Compiler CGHDR |
| 476 | `ARG2` | Compiler CGHDR |
| 477 | `LABV` | Compiler CGHDR |
| 478 | `PARAMNUMBER` | Compiler CGHDR |
| 480 | `ENDLAB` | Compiler CGHDR |
| 481 | `HLAB` | Compiler CGHDR |
| 482 | `FLAB` | Compiler CGHDR |
| 483 | `SLAB` | Compiler CGHDR |
| 487 | `MAXGN` | Compiler CGHDR |
| 488 | `MAXL` | Compiler CGHDR |
| 490 | `SCAN` | Compiler CGHDR |
| 491 | `OP` | Compiler CGHDR |
| 500 | `CGSWITCH` | Compiler CGHDR |
| 501 | `LABVECSWITCH` | Compiler CGHDR |
| 502 | `BINTREESWITCH` | Compiler CGHDR |
| 505 | `CASEK` | Compiler CGHDR |
| 506 | `CASEL` | Compiler CGHDR |
| 510 | `CGENTRY` | Compiler CGHDR |
| 511 | `CGSAVE` | Compiler CGHDR |
| 512 | `CGENDPROC` | Compiler CGHDR |
| 513 | `CGAPPLY` | Compiler CGHDR |
| 520 | `CGSTIND` | Compiler CGHDR |
| 521 | `CGMULT` | Compiler CGHDR |
| 522 | `CGPLUS` | Compiler CGHDR |
| 523 | `CGASSOP` | Compiler CGHDR |
| 525 | `CGRELOP` | Compiler CGHDR |
| 526 | `CONDITION` | Compiler CGHDR |
| 527 | `CGSHIFT` | Compiler CGHDR |
| 528 | `CGLOGOP` | Compiler CGHDR |
| 529 | `CGBYTEAP` | Compiler CGHDR |
| 530 | `CGSTRING` | Compiler CGHDR |
| 531 | `CGGLOBAL` | Compiler CGHDR |
| 532 | `GENDATA` | Compiler CGHDR |
| 535 | `DATA` | Compiler CGHDR |
| 536 | `SDATA` | Compiler CGHDR |
| 537 | `FDATA` | Compiler CGHDR |
| 538 | `HDATA` | Compiler CGHDR |
| 540 | `FREF` | Compiler CGHDR |
| 541 | `HREF` | Compiler CGHDR |
| 542 | `XREF` | Compiler CGHDR |
| 545 | `INITDATALISTS` | Compiler CGHDR |
| 546 | `MAP1` | Compiler CGHDR |
| 547 | `MAP2` | Compiler CGHDR |
| 550 | `DP` | Compiler CGHDR |
| 551 | `DATAP` | Compiler CGHDR |
| 552 | `DATALIST` | Compiler CGHDR |
| 553 | `XREFP` | Compiler CGHDR |
| 554 | `XREFLIST` | Compiler CGHDR |
| 555 | `SDATAP` | Compiler CGHDR |
| 556 | `SDATALIST` | Compiler CGHDR |
| 557 | `STRINGADDR` | Compiler CGHDR |
| 558 | `NEEDSP` | Compiler CGHDR |
| 559 | `NEEDSLIST` | Compiler CGHDR |
| 560 | `FDATAP` | Compiler CGHDR |
| 561 | `FDATALIST` | Compiler CGHDR |
| 562 | `HDATAP` | Compiler CGHDR |
| 563 | `HDATALIST` | Compiler CGHDR |
| 565 | `FREFP` | Compiler CGHDR |
| 566 | `FREFLIST` | Compiler CGHDR |
| 567 | `HREFP` | Compiler CGHDR |
| 568 | `HREFLIST` | Compiler CGHDR |
| 570 | `NAMING` | Compiler CGHDR |
| 571 | `NAMEL` | Compiler CGHDR |
| 572 | `NAMET` | Compiler CGHDR |
| 574 | `NAMES` | Compiler CGHDR |
| 578 | `BLOCKLABEL` | Compiler CGHDR |
| 579 | `PROCLABEL` | Compiler CGHDR |
| 580 | `COMPILE` | Compiler CGHDR |
| 581 | `MOVETOANYCR` | Compiler CGHDR |
| 582 | `MOVETOANYR` | Compiler CGHDR |
| 585 | `MOVETOR` | Compiler CGHDR |
| 586 | `CLASS` | Compiler CGHDR |
| 590 | `GENRHFK` | Compiler CGHDR |
| 591 | `GENRHF` | Compiler CGHDR |
| 592 | `GENRF` | Compiler CGHDR |
| 593 | `SETRTOK` | Compiler CGHDR |
| 600 | `GENRXA` | Compiler CGHDR |
| 601 | `ADJUSTADDR` | Compiler CGHDR |
| 602 | `GENRXL` | Compiler CGHDR |
| 603 | `GENSIA` | Compiler CGHDR |
| 605 | `GENRS` | Compiler CGHDR |
| 606 | `GENRR` | Compiler CGHDR |
| 607 | `JUMP` | Compiler CGHDR |
| 608 | `CONDJUMP` | Compiler CGHDR |
| 610 | `GENLAB` | Compiler CGHDR |
| 611 | `GENDCF` | Compiler CGHDR |
| 612 | `GENDCA` | Compiler CGHDR |
| 613 | `GENDCAX` | Compiler CGHDR |
| 615 | `GENDCH` | Compiler CGHDR |
| 616 | `GENDCAL2` | Compiler CGHDR |
| 617 | `GENDCX` | Compiler CGHDR |
| 618 | `CSECTN1` | Compiler CGHDR |
| 619 | `CSECTN2` | Compiler CGHDR |
| 620 | `CNOP` | Compiler CGHDR |
| 621 | `INSERTCOUNT` | Compiler CGHDR |
| 622 | `CGSTART` | Compiler CGHDR |
| 623 | `CGEND` | Compiler CGHDR |
| 624 | `CSECTFLAG` | Compiler CGHDR |
| 625 | `FNHREF` | Compiler CGHDR |
| 626 | `FNFREF` | Compiler CGHDR |
| 627 | `PUTHW` | Compiler CGHDR |
| 628 | `PUTFW` | Compiler CGHDR |
| 630 | `TXTV` | Compiler CGHDR |
| 631 | `TXTP` | Compiler CGHDR |
| 632 | `TP` | Compiler CGHDR |
| 633 | `LEFTHW` | Compiler CGHDR |
| 635 | `BASE` | Compiler CGHDR |
| 636 | `BASELAB` | Compiler CGHDR |
| 637 | `BASEADDR` | Compiler CGHDR |
| 638 | `BASEFRMLAB` | Compiler CGHDR |
| 639 | `BASEFRMADDR` | Compiler CGHDR |
| 640 | `BASEFRMSIZE` | Compiler CGHDR |
| 641 | `BASEOVRFLW` | Compiler CGHDR |
| 642 | `GENSTKCK1` | Compiler CGHDR |
| 643 | `GENSTKCK2` | Compiler CGHDR |
| 644 | `OPCODE` | Compiler CGHDR |
| 645 | `WRCARD` | Compiler CGHDR |
| 646 | `BINTOX` | Compiler CGHDR |
| 647 | `CARDWORD` | Compiler CGHDR |
| 648 | `DECKOUT` | Compiler CGHDR |
| 649 | `CW` | Compiler CGHDR |
| 650 | `USINGF` | Compiler CGHDR |
| 651 | `NEXTFR` | Compiler CGHDR |
| 652 | `FREEFREG` | Compiler CGHDR |
| 653 | `MOVETOFR` | Compiler CGHDR |
| 654 | `MOVETOANYFR` | Compiler CGHDR |
| 655 | `GENFRHF` | Compiler CGHDR |
| 660 | `CGFLOAT` | Compiler CGHDR |
| 661 | `FLOATL` | Compiler CGHDR |
| 662 | `CGFIX` | Compiler CGHDR |
| 663 | `FIXL` | Compiler CGHDR |
| 665 | `CGFSYM` | Compiler CGHDR |
| 666 | `CGFASYM` | Compiler CGHDR |
| 671 | `CGSLCTST` | Compiler CGHDR |
| 675 | `DISCARDREGS` | Compiler CGHDR |
| 676 | `DISCARDREG` | Compiler CGHDR |
| 677 | `DISCARDADDRESS` | Compiler CGHDR |
| 678 | `LOADADDRESS` | Compiler CGHDR |
| 679 | `MOVESTOR` | Compiler CGHDR |
| 680 | `MOVERTOR` | Compiler CGHDR |
| 681 | `STORER` | Compiler CGHDR |
| 682 | `PRINTREGLIST` | Compiler CGHDR |
| 684 | `DEBUG` | Compiler CGHDR |
| 685 | `REGLIST` | Compiler CGHDR |
| 688 | `LOOKFOR` | Compiler CGHDR |
| 690 | `LOCK` | Compiler CGHDR |
| 691 | `UNLOCK` | Compiler CGHDR |
| 692 | `LOCKED` | Compiler CGHDR |

These internal compiler assignments extend through G!692. Source headers inspected show no declarations for G!200, G!201, or G!202; that scoped negative finding does not prove that arbitrary other historical/application modules never used those numbers.

## Separate MR10 interpreted-library global declarations

**Source authority:** [`mr10-kit-compiler/library/GLOBALS.md`](../mr10-kit-compiler/library/GLOBALS.md).
This is an independent, reconstruction-local numbering convention. It has numeric overlaps with historical `LIBHDR` and is **not** a second compatible namespace within the same native executable.

| Global | MR10-local name | Scope |
|---:|---|---|
| 87 | `GETVEC` | MR10 interpreted library |
| 88 | `FREEVEC` | MR10 interpreted library |
| 89 | `HEAPINIT` | MR10 interpreted library |
| 90 | `FREEHEAD` | MR10 interpreted library |
| 91 | `CREATECO` | MR10 interpreted library |
| 92 | `DELETECO` | MR10 interpreted library |
| 93 | `CALLCO` | MR10 interpreted library |
| 94 | `COWAIT` | MR10 interpreted library |
| 95 | `RESUMECO` | MR10 interpreted library |
| 96 | `SRAND` | MR10 interpreted library |
| 97 | `RAND` | MR10 interpreted library |
| 98 | `RANDRANGE` | MR10 interpreted library |
| 99 | `RANDSTATE` | MR10 interpreted library |
| 100 | `RANDSEED` | MR10 interpreted library |
| 101 | `ABS` | MR10 interpreted library |
| 102 | `MIN` | MR10 interpreted library |
| 103 | `MAX` | MR10 interpreted library |
| 104 | `SIGN` | MR10 interpreted library |
| 105 | `GCD` | MR10 interpreted library |
| 106 | `IPOW` | MR10 interpreted library |
| 107 | `STRLEN` | MR10 interpreted library |
| 108 | `STRCMP` | MR10 interpreted library |
| 109 | `STRCPY` | MR10 interpreted library |
| 110 | `STRCAT` | MR10 interpreted library |
| 111 | `STRCHR` | MR10 interpreted library |
| 112 | `MEMCPY` | MR10 interpreted library |
| 113 | `MEMSET` | MR10 interpreted library |
| 114 | `MEMCMP` | MR10 interpreted library |
| 115 | `VECCOPY` | MR10 interpreted library |
| 116 | `VECCLEAR` | MR10 interpreted library |
| 117 | `ATOI` | MR10 interpreted library |
| 118 | `ITOA` | MR10 interpreted library |
| 119 | `HEXTOI` | MR10 interpreted library |
| 120 | `ITOHEX` | MR10 interpreted library |
| 121 | `ISDIGIT` | MR10 interpreted library |
| 122 | `ISALPHA` | MR10 interpreted library |
| 123 | `ISSPACE` | MR10 interpreted library |
| 124 | `TOUPPER` | MR10 interpreted library |
| 125 | `TOLOWER` | MR10 interpreted library |
| 126 | `READLINE` | MR10 interpreted library |
| 127 | `WRITELINE` | MR10 interpreted library |

## Allocation control

1. Compare the historical `LIBHDR` and compiler `CGHDR` tables, active native runtime symbols, any MR10-local symbols participating in the actual link, and existing project assignments.
2. For each new package, record its owner, public dispatcher spelling, slot number, compatibility, and status here **before** publishing a header or code that exports it.
3. Reject duplicate or unauthorized GLOBAL assignments. Never silently overwrite historical, runtime, compiler, or separately linked application globals.
4. The **Global Number Registry** assigns numbers; a future optional **Module Registration Table** (provisionally `BCPLREG`) selects and installs dispatcher addresses into each linked application.
5. Validate the target runtime's global-vector capacity, registration and missing-module behavior during Milestone Runtime Extensions **R.0–R.3**. A declared number alone is not usable service code.
6. Maintain retired assignments as tombstones; do not recycle slots without an explicit breaking-ABI decision. Document a User/Site Library allocation and collision policy before adopting one.

## Scope limitations and reference order

This is a source-grounded inventory of the preserved `LIBHDR`, `CGHDR`, the separate MR10-local map, the observed G!150 conflict, the three assigned System Extension slots, and the permanently assigned BCPLDEMO G!203 reference slot. It is **not an exhaustive scan** of arbitrary GLOBAL declarations in every application or historical fragment. An application's own GLOBAL exports may occupy additional slots.

- **Historical name/number evidence:** `richards-bcpltape/sys3/bcpl/libhdr`; `richards-bcpltape/bcplib/bcpl/cghdr`.
- **MR10-local library contract:** `mr10-kit-compiler/library/GLOBALS.md`.
- **Runtime implementation evidence:** `bootstrap-toolchain/asm/bcplmain.asm`; `cambridge-compiler/asm/bcplmain.asm`; `bootstrap-toolchain/regression/090-high-global-capacity/source.bcpl`.
- **Optional registration design:** [Milestone Runtime Extensions](milestone-runtime-extensions.md).
- **Related terminology and I/O design:** [Runtime and Library Nomenclature](runtime-and-library-nomenclature.md); [Milestone QSAM](milestone-qsam.md).

The **new slot allocations above are authoritative for this project** even though their implementation and optional registration mechanism have not been completed.
