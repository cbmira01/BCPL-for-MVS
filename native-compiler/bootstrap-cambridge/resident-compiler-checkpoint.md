# Cambridge Resident Compiler Checkpoint

This checkpoint records the first successful interpreted run of the complete resident Cambridge BCPL compiler far enough to parse a BCPL source file and emit OCODE under ICINT V19.

It is deliberately phrased in terms of architectural boundaries rather than JES job numbers. JES numbers are useful diagnostics, not durable project state.

## Resident image

The resident compiler image is built from the Cambridge master and implementation sections in this load order:

1. `bcpl`
2. `syn`
3. `lex`
4. `trna`
5. `trnb`
6. `cga`
7. `cgb`
8. `cgc`
9. `cgd`
10. `cge`
11. `bootstrap-host.bcpl`
12. MR10 `BLIBI`
13. MR10 `ICLIB`

All Cambridge implementation units compile under the MR10 bootstrap path and rendezvous through one shared global vector. Representative populated globals include the master entry at G!1, compiler services in the 100-400 range, the System/370 code generator entry at G!450, and code-generator globals through G!699.

Because the resident image supplies `CODEGEN`, the historical overlay path is dormant for this bootstrap configuration.

## Host boundary discoveries

Bringing up the resident compiler exposed host services in a useful sequence.

### WRAPOUTPUT

The first missing host global was `WRAPOUTPUT` at G!33. `bootstrap-host.bcpl` supplies the minimal state-preserving implementation needed by the Cambridge master.

### FINDPARM

The next missing host global was `FINDPARM` at G!39. The bootstrap implementation maps this to the dedicated `CAMBPARM` DDNAME rather than reusing the MR10 `OPTIONS` stream.

### CAMBPARM record semantics

The compiler option readers treat `/` as the option terminator. On MVS, the in-stream file is presented as FB80 records, so a short host record such as `//` is blank padded and the code-generator option reader continues into those blanks.

The bootstrap parameter file therefore contains one complete 80-character record of `/` characters. This causes every reader of the parameter stream to encounter terminators throughout the full FB80 record.

### Final-run SYSIN

The resident compiler must see the BCPL source as `SYSIN` during the final interpreted execution. The ordinary `compile-and-run --dd` facility cannot do this because `SYSIN` is already owned by the MR10 compiler phases earlier in the same job.

A local experiment proved that supplying a DD only on the final RUN step is sufficient. This is a generic staging capability and may remain useful in the MR10 tool, but Cambridge compilation should not continue to accumulate special cases inside `compile-and-run`.

### STACKBASE and STACKEND

The Cambridge `LIBHDR` contract uses:

- G!54 `STACKBASE`: first BCPL word available for stack/workspace;
- G!55 `STACKEND`: first BCPL word beyond the stack region.

ICINT already knows both quantities after loading INTCODE:

- `STKBASE` is the final value of P after the resident image is loaded;
- `PROGWORD + PROGCNT` is the first word beyond PROGVEC.

ICINT V19 therefore publishes:

- G!54 = `STKBASE`;
- G!55 = `PROGWORD + 40001`.

With a resident program size of 26967 BCPL words, the compiler reported a stack size of 13034 words, exactly `40001 - 26967`.

## Proven execution boundary

With the parameter stream, final-run SYSIN, and stack globals supplied, the resident compiler reached:

```text
INTCODE SYSTEM ENTERED, PROGRAM SIZE = 26967

BCPL 5th Mar 81  Stacksize = 13034  Parm =
Tree size 422
OCODE size = 33

NO SYSGO

EXECUTION CYCLES = 81330, CODE = 8
```

This establishes several facts at once:

- the complete resident image loads;
- the shared-global rendezvous is coherent enough to execute the master compiler;
- parameter parsing works;
- source discovery through `SYSIN` works;
- stack/workspace discovery works;
- syntax analysis completes for the probe source;
- translation completes far enough to report a tree;
- OCODE generation completes and reports a non-zero OCODE size;
- execution reaches the native code-generation/output boundary.

`NO SYSGO` is the next host boundary, not evidence that the preceding compiler phases failed.

## Why SYSGO must be supplied

The historical master defaults deck generation on. Its relevant behavior is conceptually:

```text
if DECK:
    SYSPCH := FINDOUTPUT("SYSGO")
    if SYSPCH = 0:
        write "NO SYSGO"
        stop(8)
```

The `N` option suppresses deck generation, but doing so would bypass exactly the native System/370 object-deck path that this reconstruction is intended to exercise. The bootstrap should therefore provide `SYSGO`, not disable it.

## Tooling decision

`tools/compile-and-run` remains the MR10 bootstrap tool. Its architecture is intentionally:

```text
BCPL source
  -> SYNI/TRNI
  -> OCODE
  -> CGI
  -> INTCODE
  -> concatenate modules with BLIBI/ICLIB
  -> execute under ICINT
```

The Cambridge resident compiler has a different lifecycle:

```text
build ICINT
  -> build/load resident Cambridge compiler image
  -> supply CAMBPARM, source and historical headers/services
  -> execute Cambridge compiler
  -> capture CODE / SYSGO / diagnostics
```

Do not keep extending `compile-and-run` with Cambridge-specific output handling. Introduce a separate Cambridge-oriented tool (working name `tools/cambridge-compile`) whose first-class outputs include the historical compiler's `CODE` and `SYSGO` streams.

A generic facility for injecting named input DDs only into the final RUN step may still be appropriate in `compile-and-run`; that capability is not Cambridge-specific. In contrast, allocating and recovering Cambridge native-output streams belongs in the new Cambridge tool.

## ICINT V19 status

ICINT V19 is checkpointed, not promoted.

The V19 generator now reproduces byte-for-byte the tested `asm/icintv19.asm` candidate. The candidate includes:

- G!0..G!699 global-vector capacity;
- reachable literal-pool handling for the enlarged static image;
- far-address MAPSTORE message loads through `=A(...)` literals;
- Cambridge G!54/G!55 stack-bound publication.

Do not change `config/CURRENT` to V19 or call V19 settled without an explicit review. One known review item is the old MAPSTORE program-vector diagnostic bound inherited from the earlier 20,001-word PROGVEC configuration.

## Next engineering boundary

The next bootstrap objective is to provide and capture the Cambridge native output streams, especially `SYSGO`, then observe CG370 consuming the 33-word probe OCODE and emitting System/370 output.

That work should proceed through the dedicated Cambridge compiler driver rather than by further Cambridge-specific expansion of the MR10 `compile-and-run` interface.
