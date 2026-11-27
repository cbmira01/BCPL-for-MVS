"""Adapt validated source QSAM decks to read-only installed-object linkage."""
import re

PRIVATE = ("ASMN", "ASMR", "ASMQ")
SECTIONS = ("QSMDESC", "QSMDISP", "QSMCORE", "QSMCLS1", "QSMIO",
            "QSMFIN", "QSMCTRL", "QSMDCBS")
STEP = re.compile(r"^//([A-Z0-9]{1,8})\s+EXEC\s")
DSN = re.compile(r"[A-Z@$#][A-Z0-9@$#]{0,7}(?:\.[A-Z@$#][A-Z0-9@$#]{0,7})+")
ENTRY = re.compile(r"(?im)^[ \t\f]*[01+]?[ \t\f]*ENTRY[ \t]+ADDRESS[ \t]+"
                   r"([0-9A-F]{1,8})[ \t]*$")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def installed_steps(steps):
    return tuple(s for s in steps if s not in PRIVATE)


def application_links(kind):
    return ("LKED", "LKRD") if kind == "full" else ("LKED",)


def macro_invocations(rows):
    """Return executable cards outside IFOX MACRO/MEND definitions."""
    result = []
    in_macro = False
    for row in rows:
        if not row.strip() or row.startswith("*"):
            continue
        if row.strip() == "MACRO":
            require(not in_macro, "nested BCX macro definition")
            in_macro = True
        elif row.strip() == "MEND":
            require(in_macro, "unmatched BCX MEND")
            in_macro = False
        elif not in_macro:
            result.append(row)
    require(not in_macro, "unterminated BCX macro definition")
    return result


def transform(deck, kind, steps, obj, ext, mac):
    """Keep application/independent I/O steps and DDs byte-for-byte unchanged."""
    require(len({obj, ext, mac}) == 3 and all(len(d) <= 44 and DSN.fullmatch(d)
            for d in (obj, ext, mac)), "invalid/colliding installed PDS DSNs")
    rows = deck.splitlines()
    starts = [(i, STEP.match(x).group(1)) for i, x in enumerate(rows) if STEP.match(x)]
    require(tuple(s for _, s in starts) == tuple(steps), "unexpected source step order")
    result = rows[:starts[0][0]] + ["//* INSTALLED QSAM: BOOT_OBJ, EXT_OBJ, EXT_MAC READ ONLY"]
    apps = application_links(kind)
    selection = ["         BCXREQ BCPLQSAM"]
    if kind == "mix":
        selection.append("         BCXREQ BCPLDEMO")
    for index, (start, step) in enumerate(starts):
        end = starts[index + 1][0] if index + 1 < len(starts) else len(rows)
        block = rows[start:end]
        if step in PRIVATE:
            require(block.count("/*") == 1 and block[-1] == "/*", "private step boundary")
            continue
        if step == "ASMG":
            anchor = "//SYSIN    DD  *"
            require(block.count(anchor) == 1 and block.count("/*") == 1
                    and block[-1] == "/*", "unexpected macro stream")
            at = block.index(anchor)
            require(macro_invocations(block[at+1:-1]) == selection + [
                        "         BCXEND", "         END   BCPLREG"],
                    "unexpected BCX invocation sequence")
            block = block[:at] + [
                f"//SYSIN    DD  DSN={mac}(BCXPRE),DISP=SHR",
                f"//         DD  DSN={mac}(BCXCAT),DISP=SHR",
                "//         DD  *", *selection, "/*",
                f"//         DD  DSN={mac}(BCXPOST),DISP=SHR",
            ]
        if step in apps:
            qsm = "//QSMOBJ   DD  DSN=&&Q1QSOBJ,DISP=(OLD,PASS)"
            extdd = f"//EXTLIB   DD  DSN={ext},DISP=SHR"
            require(block.count(qsm) == 1 and
                    block.count(f"//OBJ      DD  DSN={obj},DISP=SHR") == 1,
                    "unexpected application object DDs")
            require(block.count(extdd) == int(kind == "mix"), "unexpected EXTLIB DD")
            if kind == "mix":
                block.remove(qsm)
            else:
                block[block.index(qsm)] = extdd
            for temp in ("Q1NMOBJ", "Q1RGOBJ"):
                dd = f"//         DD  DSN=&&{temp},DISP=(OLD,PASS)"
                require(block.count(dd) == 1, "missing private object DD: " + temp)
                block.remove(dd)
            anchor = " INCLUDE OBJ(BCPLIO)"
            require(block.count(anchor) == 1, "missing runtime INCLUDE anchor")
            at = block.index(anchor)
            block[at:at] = [" INCLUDE OBJ(BCPLMAIN)", " INCLUDE OBJ(BCPLRGS)"]
        result += block
    require(tuple(STEP.match(x).group(1) for x in result if STEP.match(x)) ==
            installed_steps(steps), "installed step order mismatch")
    for row in result:
        require(row.isascii() and len(row) <= 71 and "\t" not in row, "invalid JCL card")
        require(not any(x in row for x in ("&&Q1NMOBJ", "&&Q1RGOBJ", "&&Q1QSOBJ",
                    "//QSMOBJ", "CATLG", "DISP=MOD")), "private object or permanent write")
        if row.startswith("//") and not row.startswith("//*") and "DSN=" in row:
            d = row.split("DSN=", 1)[1].split(",", 1)[0]
            require(d.startswith("&&") or row.endswith(",DISP=SHR"),
                    "non-temporary DD must be read-only")
    return "\n".join(result) + "\n"


def map_issues(report, kind, steps):
    """Validate each real IEWL map, including independent IFOX-only links."""
    links = [s for s in steps if s.startswith("LK")]
    chunks = report.split("CROSS REFERENCE TABLE")
    if len(chunks) != len(links) + 1:
        return ["wrong installed IEWL map count"]
    errors = []
    for name, chunk in zip(links, chunks[1:]):
        if "LOCATION  REFERS TO SYMBOL" not in chunk:
            errors.append(name + ": missing XREF boundary")
            continue
        mapping = chunk.split("LOCATION  REFERS TO SYMBOL", 1)[0]
        found = {}
        for symbol, size in re.findall(
                r"(?m)^  ([A-Z0-9@$#]{1,8})\s+[0-9A-F]{1,8}\s+([0-9A-F]{1,8})\s*$", mapping):
            found.setdefault(symbol, []).append(int(size, 16))
        selected = name in application_links(kind)
        demo = selected and kind == "mix"
        for symbol in SECTIONS:
            if len(found.get(symbol, [])) != int(selected):
                errors.append(name + ": wrong QSAM CSECT " + symbol)
        if selected:
            for symbol in ("R0APP", "BCPLMAIN", "RGINIT", "RGFINI"):
                if len(found.get(symbol, [])) != 1:
                    errors.append(name + ": missing/duplicate " + symbol)
            for symbol, size in (("QSMDESC", 56), ("BCPLREG", 60 if demo else 44)):
                if found.get(symbol) != [size]:
                    errors.append(name + ": wrong " + symbol + " length")
            for symbol in ("QSMBEG", "QSMEND"):
                if not re.search(r"\b" + symbol + r"\b", mapping):
                    errors.append(name + ": missing " + symbol)
        for symbol in ("DMODESC", "DMODISP"):
            if len(found.get(symbol, [])) != int(demo):
                errors.append(name + ": wrong DEMO CSECT " + symbol)
        if any(symbol in found for symbol in ("TIMDESC", "TIMDISP")):
            errors.append(name + ": unexpected BCPLTIME")
    if not re.search(r"\bINCLUDE\s+EXTLIB\s*\(\s*BCPLQSAM\s*\)", report):
        errors.append("missing installed BCPLQSAM INCLUDE evidence")
    if bool(re.search(r"\bINCLUDE\s+EXTLIB\s*\(\s*BCPLDEMO\s*\)", report)) != (kind == "mix"):
        errors.append("wrong installed BCPLDEMO INCLUDE evidence")
    addresses = ENTRY.findall(report)
    if len(addresses) != len(links):
        errors.append("wrong IEWL entry count")
    else:
        for name, address in zip(links, addresses):
            if name in application_links(kind) and int(address, 16) != 0:
                errors.append(name + ": nonzero application entry")
    return errors
