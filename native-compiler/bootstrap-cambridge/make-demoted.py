#!/usr/bin/env python3
"""Generate MR10-hostable Cambridge compiler units.

The bootstrap derivative is deliberately mechanical:

- split historical source containers at SECTION boundaries;
- omit SECTION wrappers from resulting compilation units;
- rewrite Cambridge '~=' as token-separated older 'NE';
- map historical member-style GET names to MVS-DD-friendly names;
- split LEX packed reserved-word strings to fit MR10's 255-character limit;
- replace LEX READFLOAT with an explicit bootstrap-only fatal stub because
  MR10 cannot parse Cambridge FLOAT/# floating arithmetic;
- rewrite TRNB's one unary ABS source expression as equivalent older BCPL;
- omit the BCPL master's leading NEEDS "$LOAD$" dependency directive for the
  interpreted all-modules-loaded bootstrap image.

Historical sources remain untouched.  Unexpected source drift fails loudly.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
OUT = ROOT.parent.parent / "workarea" / "bootstrap-cambridge" / "demoted"
DIAG_OUT = ROOT.parent.parent / "workarea" / "bootstrap-cambridge" / "demoted-diag"
HIST = ROOT.parent.parent / "richards-bcpltape" / "bcplib" / "bcpl"


def split_container(path: Path, first_name: str, second_name: str):
    text = path.read_text(encoding="utf-8")
    first_header = f'SECTION "{first_name}"\n'
    second_marker = f'\n.\nSECTION "{second_name}"\n'
    if not text.startswith(first_header):
        raise SystemExit(f"{path}: expected leading {first_header!r}")
    if text.count(second_marker) != 1:
        raise SystemExit(
            f"{path}: expected exactly one boundary {second_marker!r}, "
            f"found {text.count(second_marker)}"
        )
    first, second = text[len(first_header):].split(second_marker, 1)
    return first, second


def split_sections(path: Path, names):
    """Split a historical multi-SECTION container into named bodies."""
    text = path.read_text(encoding="utf-8")
    first_header = f'SECTION "{names[0]}"\n'
    if not text.startswith(first_header):
        raise SystemExit(f"{path}: expected leading {first_header!r}")
    rest = text[len(first_header):]
    units = []
    for name in names[1:]:
        marker = f'\n.\nSECTION "{name}"\n'
        if rest.count(marker) != 1:
            raise SystemExit(
                f"{path}: expected exactly one boundary {marker!r}, "
                f"found {rest.count(marker)}"
            )
        body, rest = rest.split(marker, 1)
        units.append(body)
    units.append(rest)
    return units


def demote(text: str) -> str:
    # NE is alphabetic in the MR10 syntax.  Surround it with whitespace so
    # adjacent Cambridge spelling such as SHIFT~=0 cannot become SHIFTNE0.
    text = text.replace("~=", " NE ")
    text = text.replace('GET "HEADERS(SYNHDR)"', 'GET "SYNHDR"')
    text = text.replace('GET "HEADERS(TRNHDR)"', 'GET "TRNHDR"')
    text = text.replace('GET "HEADERS(CGHDR)"', 'GET "CGHDR"')
    return text


def demote_lex_word_table(text: str) -> str:
    first = '''       D("AND/ABS/*
         *BE/BREAK/BY/*
         *CASE/*
         *DO/DEFAULT/*
         *EQ/EQV/ELSE/ENDCASE/*
         *FALSE/FOR/FINISH/FLOAT/FIX/*
         *GOTO/GE/GR/GLOBAL/GET/*
         *IF/INTO/*
         *LET/LV/LE/LS/LOGOR/LOGAND/LOOP/LSHIFT//")'''
    first_replacement = '''       D("AND/ABS/BE/BREAK/BY/CASE/DO/DEFAULT//")
       D("EQ/EQV/ELSE/ENDCASE/FALSE/FOR/FINISH/FLOAT/FIX//")
       D("GOTO/GE/GR/GLOBAL/GET/IF/INTO//")
       D("LET/LV/LE/LS/LOGOR/LOGAND/LOOP/LSHIFT//")'''
    second = '''       D("MANIFEST/*
         *NE/NOT/NEQV/NEEDS/*
         *OF/OR/*
         *RESULTIS/RETURN/REM/RSHIFT/RV/*
         *REPEAT/REPEATWHILE/REPEATUNTIL/*
         *SWITCHON/STATIC/SLCT/SECTION/*
         *TO/TEST/TRUE/THEN/TABLE/*
         *UNTIL/UNLESS/*
         *VEC/VALOF/*
         *WHILE/*
         *$//")'''
    second_replacement = '''       D("MANIFEST/NE/NOT/NEQV/NEEDS/OF/OR//")
       D("RESULTIS/RETURN/REM/RSHIFT/RV//")
       D("REPEAT/REPEATWHILE/REPEATUNTIL//")
       D("SWITCHON/STATIC/SLCT/SECTION//")
       D("TO/TEST/TRUE/THEN/TABLE/UNTIL/UNLESS//")
       D("VEC/VALOF/WHILE/$//")'''
    if text.count(first) != 1:
        raise SystemExit(f"LEX: expected one first packed word table, found {text.count(first)}")
    if text.count(second) != 1:
        raise SystemExit(f"LEX: expected one second packed word table, found {text.count(second)}")
    return text.replace(first, first_replacement, 1).replace(second, second_replacement, 1)


def demote_lex_readfloat(text: str) -> str:
    original = '''AND READFLOAT() BE

$(  LET EXP, N = 0, 0
    LET FLTEN = FLOAT 10
    DECVAL := FLOAT DECVAL; SYMB := S.NUMBER
    IF CH='.' THEN
    $(  RCH(); N := VALUE(CH)
        IF N>=10 THEN BREAK
        EXP := EXP-1
        DECVAL := DECVAL #* FLTEN #+ FLOAT N
    $) REPEAT
    IF CH='E' | CH='e' THEN
    $(  LET NEG = FALSE
        RCH(); IF CH='+' | CH='-' THEN  $( NEG := CH='-'; RCH()  $)
        N := DECVAL
        READNUMBER(10)
        TEST NEG THEN EXP := EXP - DECVAL
                   OR EXP := EXP + DECVAL
        DECVAL := N
    $)
    WHILE EXP NE 0 DO
    $(  TEST EXP<0
        THEN  $(  DECVAL := DECVAL #/ FLTEN; EXP := EXP + 1  $)
          OR  $(  DECVAL := DECVAL #* FLTEN; EXP := EXP - 1  $)
    $)
$)'''
    replacement = '''AND READFLOAT() BE
$(  || BOOTSTRAP ONLY: MR10 CANNOT COMPILE CAMBRIDGE FLOAT/# OPERATORS.
    || FAIL RATHER THAN PRODUCE AN INCORRECT FLOATING CONSTANT.
    CAEREPORT(-33)
$)'''
    if text.count(original) != 1:
        raise SystemExit(f"LEX: expected one READFLOAT body, found {text.count(original)}")
    return text.replace(original, replacement, 1)


def demote_trnb_ocode_host_width(text: str) -> str:
    """Write bootstrap OCODE using the MR10 host's two-byte word layout.

    The Cambridge LIBHDR correctly says BYTESPERWORD=4 for System/370, but
    the resident bootstrap executes with the MR10 GETBYTE/PUTBYTE runtime,
    which stores two bytes per interpreted BCPL word.  WRBYTE must therefore
    advance OBUFP after two host bytes or adjacent OCODE groups overlap.
    """
    old = """AND WRBYTE(N) BE $( PUTBYTE(OBUFP, OBUFB, N)
                    OBUFB := OBUFB+1
                    IF OBUFB=BYTESPERWORD THEN
                         OBUFP, OBUFB := OBUFP+1, 0
                    CHECKWORKSPACE()
                 $)"""
    new = """AND WRBYTE(N) BE $( PUTBYTE(OBUFP, OBUFB, N)
                    OBUFB := OBUFB+1
                    || BOOTSTRAP HOST: MR10 STORES TWO BYTES PER WORD.
                    IF OBUFB=2 THEN
                         OBUFP, OBUFB := OBUFP+1, 0
                    CHECKWORKSPACE()
                 $)"""
    if text.count(old) != 1:
        raise SystemExit(f"TRNB: expected one WRBYTE host-width block, found {text.count(old)}")
    return text.replace(old, new, 1)


def demote_trnb_abs(text: str) -> str:
    original = '            CASE S.ABS: RESULTIS ABS EVALCONST(H2X)'
    replacement = '''            CASE S.ABS:
            $(  LET E = EVALCONST(H2X)
                RESULTIS E<0 -> -E, E
            $)'''
    if text.count(original) != 1:
        raise SystemExit(f"TRNB: expected one unary ABS expression, found {text.count(original)}")
    return text.replace(original, replacement, 1)


def demote_master(text: str) -> str:
    prefix = 'SECTION "BCPL"\nNEEDS "$LOAD$"\n\n'
    if not text.startswith(prefix):
        raise SystemExit("bcpl master: expected SECTION BCPL followed by NEEDS $LOAD$")

    text = demote(text[len(prefix):])

    # Historical CODEA translates native System/370 EBCDIC character codes to
    # ASCII for cross-compilation away from the 370.  The bootstrap runs the
    # Cambridge compiler under the MR10 ASCII host while CG370 still targets
    # System/370, so the required direction is the inverse: ASCII -> EBCDIC.
    #
    # The historical table maps both EBCDIC NL (X'15') and LF (X'25') to ASCII
    # newline.  Choose X'25', matching the target representation expected by
    # the surviving compiler and the factorial probe.
    marker = "   IF ASCII THEN CHARCODE := CODEA\n"
    if text.count(marker) != 1:
        raise SystemExit(
            "bcpl master: expected one CHARCODE/CODEA selection point, "
            f"found {text.count(marker)}"
        )

    target_charcode = r"""AND CODE370(CH) = VALOF
$(  IF CH=0 RESULTIS 0
    IF CH=10 RESULTIS #45
    FOR I = 0 TO 255 IF CODEA(I)=CH RESULTIS I
    RESULTIS 0
$)

   || BOOTSTRAP ONLY: MR10 supplies ASCII source character codes while
   || historical CG370 emits native System/370 data.
   CHARCODE := CODE370

"""

    return text.replace(marker, target_charcode + marker, 1)


def demote_cg_target_pack(text: str, section: str) -> str:
    """Use 4-byte target packing only where CG370 constructs target words.

    Both historical target PACKSTRING calls are in section CGA.  The bootstrap
    executes under the MR10 two-bytes-per-word string runtime, while CG370
    expects four 8-bit characters per 32-bit target word.
    """
    if section != "CGA":
        return text

    replacements = (
        ("        PACKSTRING(W, N)",
         "        PK370(W, N)"),
        ("        L := PACKSTRING(V, NAMET+2)",
         "        L := PK370(V, NAMET+2)"),
    )
    for old, new in replacements:
        if text.count(old) != 1:
            raise SystemExit(
                f"CGA: expected one target PACKSTRING call {old!r}, "
                f"found {text.count(old)}"
            )
        text = text.replace(old, new, 1)

    helper = r"""

AND PK370(V, S) = VALOF
$(  || BOOTSTRAP ONLY: pack an unpacked character vector using the
    || System/370 target convention: four 8-bit bytes per 32-bit word.
    LET N = V!0 & #XFF
    LET LAST = N/4

    FOR I = 0 TO LAST DO S!I := 0

    FOR I = 0 TO N DO
    $(  LET J = I/4
        LET SH = 24 - (I&3)*8
        S!J := S!J | ((V!I & #XFF) << SH)
    $)

    RESULTIS LAST
$)
"""

    # CGA contains two independent top-level LET/AND declaration groups:
    # CG370... and SCAN....  Each target PACKSTRING call is in a different
    # group, so each group needs its own private PK370 declaration.
    scan_marker = "\nLET SCAN() BE"
    if text.count(scan_marker) != 1:
        raise SystemExit(
            f"CGA: expected one SCAN declaration boundary, "
            f"found {text.count(scan_marker)}"
        )
    text = text.replace(scan_marker, helper + scan_marker, 1)
    return text + helper



def instrument_cg(text: str, section: str) -> str:
    """Add listing-only diagnostics without changing generated object code.

    Every diagnostic assembler line begins with '* CG370-DIAG:' and is emitted
    only when CG370 is producing a listing.  No TXTP/BINING state is changed.
    Unexpected source drift fails loudly at every insertion point.
    """
    if section == "CGA":
        replacements = (
            (
                '     SW: IF CGTRACE DO WRITEF("*NOP = %N  ", OP)\n',
                '''     SW: IF CGTRACE DO WRITEF("*NOP = %N  ", OP)
         IF LISTING DO
         $(  WRCH(42)
             WRITEF(" CG370-DIAG: OCODE OP=%N SSP=%N*N", OP, SSP)
         $)
''',
                "SCAN OCODE dispatch",
            ),
        )
        for old, new, label in replacements:
            if text.count(old) != 1:
                raise SystemExit(
                    f"CGA diagnostic: expected one {label}, "
                    f"found {text.count(old)}"
                )
            text = text.replace(old, new, 1)

    if section == "CGB":
        replacements = (
            (
                '''    GENLAB(M, " ENTRY TO ")
    IF LISTING DO
''',
                '''    IF LISTING DO
    $(  WRCH(42)
        WRITEF(" CG370-DIAG: ENTRY LABEL=L%N NAMELEN=%N*N", M, N)
    $)
    GENLAB(M, " ENTRY TO ")
    IF LISTING DO
''',
                "CGENTRY label",
            ),
            (
                '''AND CGSAVE(N) BE
    $( LET A = R.A1 + N - 4
       IF A > R.A4 DO A := R.A4
       GENRS(F.STM, R.B, A, R.W, 0)
''',
                '''AND CGSAVE(N) BE
    $( LET A = R.A1 + N - 4
       IF A > R.A4 DO A := R.A4
       IF LISTING DO
       $(  WRCH(42)
           WRITEF(" CG370-DIAG: SAVE N=%N SSP=%N STKCK=%N*N",
                  N, SSP, STKCKING)
       $)
       GENRS(F.STM, R.B, A, R.W, 0)
''',
                "CGSAVE entry",
            ),
            (
                '''    IF RMIN<R.A1 DO RMIN := R.A1
    IF RMAX>R.A4 DO RMAX := R.A4

    STORE(K+7, SSP-2) || Store args 5,6,... into stack
''',
                '''    IF RMIN<R.A1 DO RMIN := R.A1
    IF RMAX>R.A4 DO RMAX := R.A4

    IF LISTING DO
    $(  WRCH(42)
        TEST OP=C.FNAP
          THEN WRITEF(" CG370-DIAG: FNAP OP=%N K=%N WOFF=%N SSP=%N*N",
                      OP, K, 4*K, SSP)
          OR WRITEF(" CG370-DIAG: RTAP OP=%N K=%N WOFF=%N SSP=%N*N",
                    OP, K, 4*K, SSP)
    $)

    STORE(K+7, SSP-2) || Store args 5,6,... into stack
''',
                "CGAPPLY setup",
            ),
            (
                '''        LET SAFEFRAME = K+7
        IF BASEFRMSIZE<SAFEFRAME DO BASEFRMSIZE:=SAFEFRAME
''',
                '''        LET SAFEFRAME = K+7
        IF LISTING DO
        $(  WRCH(42)
            WRITEF(" CG370-DIAG: CALL SAFEFRAME=%N BASEFRAME=%N*N",
                   SAFEFRAME, BASEFRMSIZE)
        $)
        IF BASEFRMSIZE<SAFEFRAME DO BASEFRMSIZE:=SAFEFRAME
''',
                "CGAPPLY safe frame",
            ),
        )
        for old, new, label in replacements:
            if text.count(old) != 1:
                raise SystemExit(
                    f"CGB diagnostic: expected one {label}, "
                    f"found {text.count(old)}"
                )
            text = text.replace(old, new, 1)

    if section == "CGE":
        replacements = (
            (
                '''AND GENSTKCK1() BE
$(
    IF LISTING DO WRITEF("*SDC*SA(L%N) STACK FRAME SIZE*N", BASEFRMLAB)
''',
                '''AND GENSTKCK1() BE
$(
    IF LISTING DO
    $(  WRCH(42)
        WRITEF(" CG370-DIAG: STKCK SLOT L%N AT BYTE %N*N",
               BASEFRMLAB, TXTP)
        WRITEF("*SDC*SA(L%N) STACK FRAME SIZE*N", BASEFRMLAB)
    $)
''',
                "GENSTKCK1",
            ),
            (
                '''AND GENSTKCK2() BE
$(
    IF LISTING DO WRITEF("L%N*SEQU*S%N STACK FRAME SIZE*N",
                                 BASEFRMLAB, BASEFRMSIZE*4)
''',
                '''AND GENSTKCK2() BE
$(
    IF LISTING DO
    $(  WRCH(42)
        WRITEF(" CG370-DIAG: STKCK FINAL L%N WORDS=%N BYTES=%N*N",
               BASEFRMLAB, BASEFRMSIZE, BASEFRMSIZE*4)
        WRITEF("L%N*SEQU*S%N STACK FRAME SIZE*N",
               BASEFRMLAB, BASEFRMSIZE*4)
    $)
''',
                "GENSTKCK2",
            ),
        )
        for old, new, label in replacements:
            if text.count(old) != 1:
                raise SystemExit(
                    f"CGE diagnostic: expected one {label}, "
                    f"found {text.count(old)}"
                )
            text = text.replace(old, new, 1)

    return text


def write_unit(name: str, historical_section: str, text: str, extra_banner=(), out_dir=OUT) -> None:
    text = demote(text)
    if historical_section == "LEX":
        text = demote_lex_word_table(text)
        text = demote_lex_readfloat(text)
    if historical_section == "TRNB":
        text = demote_trnb_abs(text)
        text = demote_trnb_ocode_host_width(text)

    banner = [
        f'|| BOOTSTRAP DERIVATIVE OF CAMBRIDGE SECTION "{historical_section}".',
        '|| SECTION wrapper omitted for MR10 source-dialect compilation.',
        '|| Historical HEADERS(...) GET names mapped to MVS DDNAMEs.',
    ]
    if historical_section == "LEX":
        banner += [
            '|| Packed reserved-word strings split to fit MR10 literal limits.',
            '|| READFLOAT is a fatal bootstrap stub; floating literals unsupported.',
        ]
    if historical_section == "TRNB":
        banner += [
            '|| Unary ABS implementation spelling demoted for MR10 compatibility.',
            '|| OCODE WRBYTE advances after two MR10 host bytes per word.',
        ]
    banner += list(extra_banner)
    (out_dir / name).write_text("\n".join(banner) + "\n" + text, encoding="utf-8")


def main() -> None:
    syn_text = (SOURCE / "syn").read_text(encoding="utf-8")
    trn_text = (SOURCE / "trn").read_text(encoding="utf-8")
    master_text = (HIST / "bcpl").read_text(encoding="utf-8")
    cg_text = (HIST / "cg").read_text(encoding="utf-8")

    if syn_text.count("~=") != 1:
        raise SystemExit(f"source/syn: expected one '~=', found {syn_text.count('~=')}")
    if trn_text.count("~=") != 1:
        raise SystemExit(f"source/trn: expected one '~=', found {trn_text.count('~=')}")
    if syn_text.count('GET "HEADERS(SYNHDR)"') != 2:
        raise SystemExit('source/syn: expected exactly two GET "HEADERS(SYNHDR)" occurrences')
    if trn_text.count('GET "HEADERS(TRNHDR)"') != 2:
        raise SystemExit('source/trn: expected exactly two GET "HEADERS(TRNHDR)" occurrences')
    if cg_text.count('GET "HEADERS(CGHDR)"') != 5:
        raise SystemExit('historical cg: expected exactly five GET "HEADERS(CGHDR)" occurrences')

    syn, lex = split_container(SOURCE / "syn", "SYN", "LEX")
    trna, trnb = split_container(SOURCE / "trn", "TRNA", "TRNB")
    cga, cgb, cgc, cgd, cge = split_sections(HIST / "cg", ["CGA", "CGB", "CGC", "CGD", "CGE"])

    OUT.mkdir(parents=True, exist_ok=True)
    DIAG_OUT.mkdir(parents=True, exist_ok=True)
    write_unit("syn", "SYN", syn)
    write_unit("lex", "LEX", lex)
    write_unit("trna", "TRNA", trna)
    write_unit("trnb", "TRNB", trnb)

    master = demote_master(master_text)
    master_banner = (
        '|| BOOTSTRAP DERIVATIVE OF CAMBRIDGE SECTION "BCPL".',
        '|| SECTION wrapper omitted for MR10 source-dialect compilation.',
        '|| NEEDS "$LOAD$" omitted: bootstrap loads all compiler units together.',
    )
    (OUT / "bcpl").write_text("\n".join(master_banner) + "\n" + master, encoding="utf-8")

    for name, section, body in (
        ("cga", "CGA", cga), ("cgb", "CGB", cgb), ("cgc", "CGC", cgc),
        ("cgd", "CGD", cgd), ("cge", "CGE", cge),
    ):
        body = demote_cg_target_pack(body, section)
        extra_banner = ()
        if section == "CGA":
            extra_banner = (
                "|| Target PACKSTRING calls use a private 4-byte/word packer;",
                "|| the MR10 host runtime remains two bytes per word.",
            )
        write_unit(name, section, body, extra_banner=extra_banner)

        diag = instrument_cg(body, section)
        diag_banner = extra_banner + (
            "|| DIAGNOSTIC DERIVATIVE: listing-only CG370 commentary enabled.",
            "|| Every injected assembler comment begins '* CG370-DIAG:'.",
            "|| Removing those lines must reproduce ordinary CG370 listing output.",
        )
        write_unit(
            name,
            section,
            diag,
            extra_banner=diag_banner,
            out_dir=DIAG_OUT,
        )

    names = ("syn", "lex", "trna", "trnb", "bcpl", "cga", "cgb", "cgc", "cgd", "cge")
    print("generated:")
    for name in names:
        p = OUT / name
        print(f"  {p.relative_to(ROOT.parent.parent)}  {p.stat().st_size} bytes")
    for name in ("cga", "cgb", "cgc", "cgd", "cge"):
        p = DIAG_OUT / name
        print(f"  {p.relative_to(ROOT.parent.parent)}  {p.stat().st_size} bytes")


if __name__ == "__main__":
    main()
